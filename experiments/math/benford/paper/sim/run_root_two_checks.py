"""
ROOT-TWO-CHECKS: R1 (IC = φ), R2 (IC = 1 + exact-zero restart),
R3 (IC = 1 + exact-zero absorb).

See `ROOT-TWO-CHECKS-SIM.md` for the rationale and decision matrix.

All three runs share the M3-style kernel (symmetric BS(1,2) step,
E_THRESH = 20 frozen, |E| < −20 near-zero shortcut) but differ in
(a) the initial condition and (b) how an active-branch exact-zero
event on a b-step is handled:

- R1: IC is x = +φ. Active-branch exact zero is algebraically
  impossible on this orbit; if it ever fires, we assert.
- R2: IC is x = +1. On active-branch x_new = 0, restart the walker
  at (m=0, E=0, sign=sign(delta)), matching the existing E < −20
  shortcut's convention. Track zero-hit counts per step.
- R3: IC is x = +1. On active-branch x_new = 0, mark the walker
  dead and exclude it from all L₁ / Fourier computations going
  forward. Track survival trajectory.

Each run: N = 10⁷ walkers, n_max = 600, M1-style sampling (every
step [1, 200], every 5 steps [205, 600]). Per-run output goes to
r{1,2,3}_*_results.npz.

Run: sage -python run_root_two_checks.py
"""

import math
import os
import time
import numpy as np


# --- Config -----------------------------------------------------------

N_WALKERS = 10**7
N_STEPS = 600
N_BINS = 1000
SEED_BASE = 0xC0FFEE01

E_THRESH = 20

MODES = np.array([1, 2, 3, 4, 5], dtype=np.int32)

SAMPLE_TIMES = np.concatenate([
    np.arange(1, 201, dtype=np.int32),
    np.arange(205, 601, 5, dtype=np.int32),
])

FOURIER_BATCH = 10**7

LOG10_2 = math.log10(2.0)
LOG10_PHI = math.log10((1.0 + math.sqrt(5.0)) / 2.0)  # ≈ 0.2090

SIM_DIR = os.path.dirname(os.path.abspath(__file__))


# --- IC initializers --------------------------------------------------

def initialize_phi(n):
    """R1: x = +φ. m = log₁₀φ, E = 0, sign = +1."""
    m = np.full(n, LOG10_PHI, dtype=np.float64)
    E = np.zeros(n, dtype=np.int32)
    sign = np.ones(n, dtype=np.int8)
    return m, E, sign


def initialize_one(n):
    """R2/R3: x = +1. m = 0, E = 0, sign = +1."""
    m = np.zeros(n, dtype=np.float64)
    E = np.zeros(n, dtype=np.int32)
    sign = np.ones(n, dtype=np.int8)
    return m, E, sign


# --- Step kernels -----------------------------------------------------

def step_a(m, E, mask):
    if not mask.any():
        return
    idx = np.where(mask)[0]
    m_new = m[idx] + LOG10_2
    carry = m_new >= 1.0
    m[idx] = np.where(carry, m_new - 1.0, m_new)
    E[idx] += carry.astype(np.int32)


def step_a_inv(m, E, mask):
    if not mask.any():
        return
    idx = np.where(mask)[0]
    m_new = m[idx] - LOG10_2
    borrow = m_new < 0.0
    m[idx] = np.where(borrow, m_new + 1.0, m_new)
    E[idx] -= borrow.astype(np.int32)


def step_b_r1(m, E, sign, mask, delta):
    """R1: asserts no exact-zero. Otherwise standard kernel."""
    if not mask.any():
        return
    idx = np.where(mask)[0]
    E_local = E[idx]
    frozen = E_local > E_THRESH
    snap = E_local < -E_THRESH
    active = ~(frozen | snap)

    snap_idx = idx[snap]
    if snap_idx.size > 0:
        m[snap_idx] = 0.0
        E[snap_idx] = 0
        sign[snap_idx] = np.int8(1 if delta > 0 else -1)

    if active.any():
        act_idx = idx[active]
        log_mag = E[act_idx].astype(np.float64) + m[act_idx]
        x = sign[act_idx].astype(np.float64) * np.power(10.0, log_mag)
        x_new = x + float(delta)

        # R1 guard: φ orbit should never produce exact zero.
        if (x_new == 0.0).any():
            n_zero = int((x_new == 0.0).sum())
            raise AssertionError(
                f'R1 hit x_new = 0 ({n_zero} walkers); φ orbit should exclude 0. '
                f'This indicates either a float64 coincidence or a kernel bug.'
            )

        abs_x = np.abs(x_new)
        log_abs = np.log10(abs_x)
        new_E = np.floor(log_abs).astype(np.int32)
        new_m = log_abs - new_E.astype(np.float64)
        new_sign = np.where(x_new > 0.0, np.int8(1), np.int8(-1))
        m[act_idx] = new_m
        E[act_idx] = new_E
        sign[act_idx] = new_sign


def step_b_r2(m, E, sign, mask, delta):
    """R2: exact-zero restart at (m=0, E=0, sign=sign(delta)).
    Returns number of exact-zero events this substep."""
    if not mask.any():
        return 0
    idx = np.where(mask)[0]
    E_local = E[idx]
    frozen = E_local > E_THRESH
    snap = E_local < -E_THRESH
    active = ~(frozen | snap)

    snap_idx = idx[snap]
    if snap_idx.size > 0:
        m[snap_idx] = 0.0
        E[snap_idx] = 0
        sign[snap_idx] = np.int8(1 if delta > 0 else -1)

    n_zero = 0
    if active.any():
        act_idx = idx[active]
        log_mag = E[act_idx].astype(np.float64) + m[act_idx]
        x = sign[act_idx].astype(np.float64) * np.power(10.0, log_mag)
        x_new = x + float(delta)

        is_zero = x_new == 0.0
        n_zero = int(is_zero.sum())

        if n_zero > 0:
            zero_idx = act_idx[is_zero]
            m[zero_idx] = 0.0
            E[zero_idx] = 0
            sign[zero_idx] = np.int8(1 if delta > 0 else -1)

        nonzero_mask = ~is_zero
        if nonzero_mask.any():
            nz_idx = act_idx[nonzero_mask]
            x_nz = x_new[nonzero_mask]
            abs_x = np.abs(x_nz)
            log_abs = np.log10(abs_x)
            new_E = np.floor(log_abs).astype(np.int32)
            new_m = log_abs - new_E.astype(np.float64)
            new_sign = np.where(x_nz > 0.0, np.int8(1), np.int8(-1))
            m[nz_idx] = new_m
            E[nz_idx] = new_E
            sign[nz_idx] = new_sign

    return n_zero


def step_b_r3(m, E, sign, alive, mask, delta):
    """R3: exact-zero absorb. Walkers hitting 0 are marked dead in `alive`
    and no longer participate. Returns number of newly-absorbed walkers."""
    if not mask.any():
        return 0
    idx = np.where(mask)[0]
    E_local = E[idx]
    frozen = E_local > E_THRESH
    snap = E_local < -E_THRESH
    active = ~(frozen | snap)

    snap_idx = idx[snap]
    if snap_idx.size > 0:
        m[snap_idx] = 0.0
        E[snap_idx] = 0
        sign[snap_idx] = np.int8(1 if delta > 0 else -1)

    n_absorbed = 0
    if active.any():
        act_idx = idx[active]
        log_mag = E[act_idx].astype(np.float64) + m[act_idx]
        x = sign[act_idx].astype(np.float64) * np.power(10.0, log_mag)
        x_new = x + float(delta)

        is_zero = x_new == 0.0
        n_absorbed = int(is_zero.sum())

        if n_absorbed > 0:
            alive[act_idx[is_zero]] = False

        nonzero_mask = ~is_zero
        if nonzero_mask.any():
            nz_idx = act_idx[nonzero_mask]
            x_nz = x_new[nonzero_mask]
            abs_x = np.abs(x_nz)
            log_abs = np.log10(abs_x)
            new_E = np.floor(log_abs).astype(np.int32)
            new_m = log_abs - new_E.astype(np.float64)
            new_sign = np.where(x_nz > 0.0, np.int8(1), np.int8(-1))
            m[nz_idx] = new_m
            E[nz_idx] = new_E
            sign[nz_idx] = new_sign

    return n_absorbed


# --- Statistics (on a passed view of m) -------------------------------

def compute_l1(m):
    n = m.shape[0]
    if n == 0:
        return float('nan')
    hist, _ = np.histogram(m, bins=N_BINS, range=(0.0, 1.0))
    freq = hist.astype(np.float64) / n
    return float(np.sum(np.abs(freq - 1.0 / N_BINS)))


def compute_fourier(m_arr, modes):
    n = m_arr.shape[0]
    R = modes.shape[0]
    if n == 0:
        return np.zeros(R, dtype=np.complex128)
    cos_sum = np.zeros(R, dtype=np.float64)
    sin_sum = np.zeros(R, dtype=np.float64)
    two_pi_modes = (2.0 * np.pi * modes.astype(np.float64))[:, None]
    for start in range(0, n, FOURIER_BATCH):
        end = min(start + FOURIER_BATCH, n)
        chunk = m_arr[start:end][None, :]
        arg = two_pi_modes * chunk
        cos_sum += np.cos(arg).sum(axis=1)
        sin_sum -= np.sin(arg).sum(axis=1)
    cos_sum /= n
    sin_sum /= n
    return cos_sum + 1j * sin_sum


# --- Per-run drivers --------------------------------------------------

def run_r1(seed):
    """R1: IC = φ."""
    print(f'\n=== R1: IC = φ, N = {N_WALKERS:_} ===')
    rng = np.random.default_rng(seed)
    m, E, sign = initialize_phi(N_WALKERS)
    n_sample = SAMPLE_TIMES.size
    l1_arr = np.zeros(n_sample, dtype=np.float64)
    h_full = np.zeros((n_sample, MODES.size), dtype=np.complex128)
    l2_norm = np.zeros(n_sample, dtype=np.float64)
    sample_set = set(SAMPLE_TIMES.tolist())
    sample_idx = 0
    t0 = time.time()

    for step in range(1, N_STEPS + 1):
        choice = rng.integers(0, 4, size=N_WALKERS, dtype=np.int8)
        step_a(m, E, choice == 0)
        step_a_inv(m, E, choice == 1)
        step_b_r1(m, E, sign, choice == 2, +1)
        step_b_r1(m, E, sign, choice == 3, -1)

        if step in sample_set:
            h = compute_fourier(m, MODES)
            l1_arr[sample_idx] = compute_l1(m)
            h_full[sample_idx] = h
            l2_norm[sample_idx] = float(np.sqrt(np.sum(np.abs(h) ** 2)))
            if sample_idx % 50 == 0 or step == N_STEPS:
                dt = time.time() - t0
                rate = step / max(dt, 1e-9)
                print(f'  n={step:4d}  L₁={l1_arr[sample_idx]:.5e}  '
                      f'|ĥ(1)|={abs(h[0]):.4e}  ({rate:.2f} steps/s)', flush=True)
            sample_idx += 1

    total = time.time() - t0
    print(f'  wall time: {total:.1f}s = {total/60:.2f} min')

    out_path = os.path.join(SIM_DIR, 'r1_phi_results.npz')
    np.savez_compressed(
        out_path,
        sample_times=SAMPLE_TIMES,
        l1=l1_arr,
        h_full=h_full,
        l2_norm=l2_norm,
        modes=MODES,
        meta_N=np.int64(N_WALKERS),
        meta_steps=np.int32(N_STEPS),
        meta_bins=np.int32(N_BINS),
        meta_seed=np.int64(seed),
        meta_m_init=np.float64(LOG10_PHI),
    )
    print(f'  -> {out_path}')


def run_r2(seed):
    """R2: IC = 1 with exact-zero restart."""
    print(f'\n=== R2: IC = 1, exact-zero restart, N = {N_WALKERS:_} ===')
    rng = np.random.default_rng(seed)
    m, E, sign = initialize_one(N_WALKERS)
    n_sample = SAMPLE_TIMES.size
    l1_arr = np.zeros(n_sample, dtype=np.float64)
    h_full = np.zeros((n_sample, MODES.size), dtype=np.complex128)
    l2_norm = np.zeros(n_sample, dtype=np.float64)

    zero_hits_per_step = np.zeros(N_STEPS + 1, dtype=np.int64)
    first_hit_step = np.full(N_WALKERS, -1, dtype=np.int32)  # -1 = not yet hit

    sample_set = set(SAMPLE_TIMES.tolist())
    sample_idx = 0
    t0 = time.time()

    for step in range(1, N_STEPS + 1):
        # Snapshot pre-step m to detect which walkers got restarted this step
        # (so first_hit_step can be populated correctly)
        # We'll detect "was restarted" as any walker whose active-branch step
        # zero'd; we only track this by aggregate count, not per-walker, to
        # save memory. first_hit_step needs a per-walker marker: do it by
        # comparing (E, m) before and after the zero branch... simpler is to
        # track inline. We'll just track the total count here; first_hit_step
        # is populated by detecting that a walker's (m, E, sign) matches the
        # restart state immediately after a b-step that produced zero.
        #
        # For simplicity we only record zero_hits_per_step as aggregate.

        choice = rng.integers(0, 4, size=N_WALKERS, dtype=np.int8)
        step_a(m, E, choice == 0)
        step_a_inv(m, E, choice == 1)
        zh_pos = step_b_r2(m, E, sign, choice == 2, +1)
        zh_neg = step_b_r2(m, E, sign, choice == 3, -1)
        zero_hits_per_step[step] = zh_pos + zh_neg

        if step in sample_set:
            h = compute_fourier(m, MODES)
            l1_arr[sample_idx] = compute_l1(m)
            h_full[sample_idx] = h
            l2_norm[sample_idx] = float(np.sqrt(np.sum(np.abs(h) ** 2)))
            if sample_idx % 50 == 0 or step == N_STEPS:
                dt = time.time() - t0
                rate = step / max(dt, 1e-9)
                total_zh = int(zero_hits_per_step[:step+1].sum())
                print(f'  n={step:4d}  L₁={l1_arr[sample_idx]:.5e}  '
                      f'|ĥ(1)|={abs(h[0]):.4e}  '
                      f'zero hits cum={total_zh:_}  '
                      f'({rate:.2f} steps/s)', flush=True)
            sample_idx += 1

    total = time.time() - t0
    total_hits = int(zero_hits_per_step.sum())
    print(f'  wall time: {total:.1f}s = {total/60:.2f} min')
    print(f'  total exact-zero hits: {total_hits:_} '
          f'({total_hits/N_WALKERS:.3f} per walker)')

    out_path = os.path.join(SIM_DIR, 'r2_rational_restart_results.npz')
    np.savez_compressed(
        out_path,
        sample_times=SAMPLE_TIMES,
        l1=l1_arr,
        h_full=h_full,
        l2_norm=l2_norm,
        modes=MODES,
        zero_hits_per_step=zero_hits_per_step,
        total_zero_hits=np.int64(total_hits),
        meta_N=np.int64(N_WALKERS),
        meta_steps=np.int32(N_STEPS),
        meta_bins=np.int32(N_BINS),
        meta_seed=np.int64(seed),
    )
    print(f'  -> {out_path}')


def run_r3(seed):
    """R3: IC = 1 with exact-zero absorb."""
    print(f'\n=== R3: IC = 1, exact-zero absorb, N = {N_WALKERS:_} ===')
    rng = np.random.default_rng(seed)
    m, E, sign = initialize_one(N_WALKERS)
    alive = np.ones(N_WALKERS, dtype=bool)

    n_sample = SAMPLE_TIMES.size
    l1_arr = np.zeros(n_sample, dtype=np.float64)
    h_full = np.zeros((n_sample, MODES.size), dtype=np.complex128)
    l2_norm = np.zeros(n_sample, dtype=np.float64)
    n_alive_arr = np.zeros(n_sample, dtype=np.int64)

    absorbed_per_step = np.zeros(N_STEPS + 1, dtype=np.int64)
    n_alive_per_step = np.zeros(N_STEPS + 1, dtype=np.int64)
    n_alive_per_step[0] = N_WALKERS

    sample_set = set(SAMPLE_TIMES.tolist())
    sample_idx = 0
    t0 = time.time()

    for step in range(1, N_STEPS + 1):
        choice = rng.integers(0, 4, size=N_WALKERS, dtype=np.int8)
        # Dead walkers don't participate in step_a/step_a_inv either (keeps their state frozen).
        # But since L₁/Fourier are computed on m[alive] only, dead walkers evolving doesn't
        # hurt. To save per-step cost, mask dead out of the step choice:
        active_step_mask = alive & (choice == 0)
        step_a(m, E, active_step_mask)
        active_step_mask = alive & (choice == 1)
        step_a_inv(m, E, active_step_mask)
        active_step_mask = alive & (choice == 2)
        ab_pos = step_b_r3(m, E, sign, alive, active_step_mask, +1)
        active_step_mask = alive & (choice == 3)
        ab_neg = step_b_r3(m, E, sign, alive, active_step_mask, -1)
        absorbed_per_step[step] = ab_pos + ab_neg
        n_alive_per_step[step] = int(alive.sum())

        if step in sample_set:
            m_alive = m[alive]
            h = compute_fourier(m_alive, MODES)
            l1_arr[sample_idx] = compute_l1(m_alive)
            h_full[sample_idx] = h
            l2_norm[sample_idx] = float(np.sqrt(np.sum(np.abs(h) ** 2)))
            n_alive_arr[sample_idx] = int(alive.sum())
            if sample_idx % 50 == 0 or step == N_STEPS:
                dt = time.time() - t0
                rate = step / max(dt, 1e-9)
                surv = n_alive_arr[sample_idx] / N_WALKERS
                print(f'  n={step:4d}  L₁={l1_arr[sample_idx]:.5e}  '
                      f'|ĥ(1)|={abs(h[0]):.4e}  '
                      f'alive={n_alive_arr[sample_idx]:_} (survival={surv:.4f})  '
                      f'({rate:.2f} steps/s)', flush=True)
            sample_idx += 1

    total = time.time() - t0
    final_surv = float(alive.sum()) / N_WALKERS
    print(f'  wall time: {total:.1f}s = {total/60:.2f} min')
    print(f'  final survival fraction: {final_surv:.4f}  ({int(alive.sum()):_} / {N_WALKERS:_})')

    out_path = os.path.join(SIM_DIR, 'r3_rational_absorb_results.npz')
    np.savez_compressed(
        out_path,
        sample_times=SAMPLE_TIMES,
        l1=l1_arr,
        h_full=h_full,
        l2_norm=l2_norm,
        modes=MODES,
        n_alive=n_alive_arr,
        absorbed_per_step=absorbed_per_step,
        n_alive_per_step=n_alive_per_step,
        meta_N=np.int64(N_WALKERS),
        meta_steps=np.int32(N_STEPS),
        meta_bins=np.int32(N_BINS),
        meta_seed=np.int64(seed),
    )
    print(f'  -> {out_path}')


def main():
    print('ROOT-TWO-CHECKS sim (R1 + R2 + R3)')
    print(f'N = {N_WALKERS:_}, n_max = {N_STEPS}, B = {N_BINS}')
    print(f'sample count = {SAMPLE_TIMES.size}')

    run_r1(seed=SEED_BASE ^ ord('1'))
    run_r2(seed=SEED_BASE ^ ord('2'))
    run_r3(seed=SEED_BASE ^ ord('3'))

    print('\nAll three runs complete.')


if __name__ == '__main__':
    main()
