"""
Run 1 — FULL-M4.

Beef-box extension of M4 to the originally-planned n_max = 20,000 on the
√2 IC. M4 capped at n = 3000 for ARM-M1 cost reasons; the longer horizon
is what's needed to pin down whether the late-window α stabilizes near
1/2 directly on the natural √2 IC, or keeps drifting.

Spec (per `EXPENSIVE-BEEF-BOX-SIM.md`):
    N = 10⁸ walkers
    Symmetric measure
    IC: x = +√2  (m = log₁₀√2, E = 0, sign = +1)
    Time range: n = 0 to 20,000
    Sampling: every 10 steps to 3000 (overlaps M4 exactly), then sparse
        tail checkpoints {5000, 7000, 10000, 14000, 20000}
    Output: L₁(n), ensemble ĥ(r, n) for r = 1..5, l2_norm(n)

Checkpoint frequency: save partial results every 1000 sim steps to
`run1_full_m4_results.npz.partial` so a crash at hour N doesn't lose
everything.

Cost estimate (beef box ≳ 5×10⁷ walker-steps/s): 2×10¹² walker-steps
≈ 11 hrs walk time + sampling/Fourier overhead → 15–20 hrs total.

Run: sage -python run1_full_m4.py
"""

import math
import os
import time
import numpy as np


# --- Config -----------------------------------------------------------

N_WALKERS = 10**8
N_STEPS = 20000
N_BINS = 1000
SEED = 0xCACA0DE4  # same as M4, so the [1, 3000] sub-trajectory is bit-comparable

E_THRESH = 20
E_R = 3

MODES = np.array([1, 2, 3, 4, 5], dtype=np.int32)

# Sampling per plan: every 10 to 3000 (matches M4 grid exactly), then
# sparse tail at the listed checkpoints.
SAMPLE_TIMES = np.concatenate([
    np.arange(10, 3001, 10, dtype=np.int32),
    np.array([5000, 7000, 10000, 14000, 20000], dtype=np.int32),
])

FOURIER_BATCH = 10**7

LOG10_2 = math.log10(2.0)
LOG10_SQRT2 = 0.5 * LOG10_2

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(SIM_DIR, 'run1_full_m4_results.npz')

CHECKPOINT_EVERY = 1000


# --- Step kernel (identical to M1/M4) --------------------------------

def initialize(n):
    m = np.full(n, LOG10_SQRT2, dtype=np.float64)
    E = np.zeros(n, dtype=np.int32)
    sign = np.ones(n, dtype=np.int8)
    return m, E, sign


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


def step_b(m, E, sign, mask, delta):
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
        abs_x = np.abs(x_new)
        log_abs = np.log10(abs_x)
        new_E = np.floor(log_abs).astype(np.int32)
        new_m = log_abs - new_E.astype(np.float64)
        new_sign = np.where(x_new > 0.0, np.int8(1), np.int8(-1))
        m[act_idx] = new_m
        E[act_idx] = new_E
        sign[act_idx] = new_sign


def step_walkers(m, E, sign, rng):
    choice = rng.integers(0, 4, size=m.shape[0], dtype=np.int8)
    step_a(m, E, choice == 0)
    step_a_inv(m, E, choice == 1)
    step_b(m, E, sign, choice == 2, +1)
    step_b(m, E, sign, choice == 3, -1)


# --- Statistics -------------------------------------------------------

def compute_l1(m):
    n = m.shape[0]
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


# --- Main -------------------------------------------------------------

def main():
    print('Run 1 — FULL-M4 (long-horizon √2 IC)')
    print(f'  N = {N_WALKERS:_}, n_max = {N_STEPS}, B = {N_BINS}, modes = {MODES.tolist()}')
    print(f'  sample count = {SAMPLE_TIMES.size}  '
          f'(dense [10, 3000] + tail {SAMPLE_TIMES[-5:].tolist()})')
    print(f'  seed = {SEED:#x}  (matches M4 for [1, 3000] cross-check)')
    print()

    rng = np.random.default_rng(SEED)

    t0 = time.time()
    m, E, sign = initialize(N_WALKERS)
    print(f'  init: {time.time()-t0:.2f}s, state ~{(m.nbytes + E.nbytes + sign.nbytes) / 1e9:.2f} GB')

    n_sample = SAMPLE_TIMES.size
    l1_arr = np.zeros(n_sample, dtype=np.float64)
    h_full = np.zeros((n_sample, MODES.size), dtype=np.complex128)
    l2_norm = np.zeros(n_sample, dtype=np.float64)

    sample_set = set(SAMPLE_TIMES.tolist())
    sample_idx = 0
    t_start = time.time()

    for step in range(1, N_STEPS + 1):
        step_walkers(m, E, sign, rng)
        if step in sample_set:
            h = compute_fourier(m, MODES)
            l1_arr[sample_idx] = compute_l1(m)
            h_full[sample_idx] = h
            l2_norm[sample_idx] = float(np.sqrt(np.sum(np.abs(h) ** 2)))

            if (sample_idx % 30 == 0) or step == N_STEPS:
                dt = time.time() - t_start
                rate = step / max(dt, 1e-9)
                eta = (N_STEPS - step) / max(rate, 1e-9)
                print(f'  n={step:6d}  L₁={l1_arr[sample_idx]:.5e}  '
                      f'|ĥ(1)|={abs(h[0]):.4e}  '
                      f'({rate:.2f} steps/s, ETA {eta/60:.0f} min)',
                      flush=True)
            sample_idx += 1

        if step % CHECKPOINT_EVERY == 0 and step > 0:
            np.savez_compressed(
                OUT_PATH + '.partial',
                sample_times=SAMPLE_TIMES[:sample_idx],
                l1=l1_arr[:sample_idx],
                h_full=h_full[:sample_idx],
                l2_norm=l2_norm[:sample_idx],
                modes=MODES,
                meta_N=np.int64(N_WALKERS),
                meta_steps=np.int32(step),
                meta_bins=np.int32(N_BINS),
                meta_E_R=np.int32(E_R),
                meta_E_THRESH=np.int32(E_THRESH),
                meta_seed=np.int64(SEED),
                checkpoint_step=np.int32(step),
            )

    total_time = time.time() - t_start
    print(f'\nTotal walk time: {total_time:.1f}s = {total_time/3600:.2f} hrs')
    print(f'Throughput: {N_WALKERS * N_STEPS / total_time:.2e} walker-steps/s')

    print()
    print('=== L₁ at key times ===')
    for target in [10, 100, 500, 1000, 3000, 5000, 7000, 10000, 14000, 20000]:
        if target in sample_set:
            i = np.argmin(np.abs(SAMPLE_TIMES - target))
            print(f'  n={int(SAMPLE_TIMES[i]):6d}  L₁={l1_arr[i]:.4e}')

    np.savez_compressed(
        OUT_PATH,
        sample_times=SAMPLE_TIMES,
        l1=l1_arr,
        h_full=h_full,
        l2_norm=l2_norm,
        modes=MODES,
        meta_N=np.int64(N_WALKERS),
        meta_steps=np.int32(N_STEPS),
        meta_bins=np.int32(N_BINS),
        meta_E_R=np.int32(E_R),
        meta_E_THRESH=np.int32(E_THRESH),
        meta_seed=np.int64(SEED),
    )

    partial = OUT_PATH + '.partial'
    if os.path.exists(partial):
        os.remove(partial)

    print(f'\n-> {OUT_PATH}')


if __name__ == '__main__':
    main()
