"""
Pre-flight cross-validation reference regen.

Produces small-scope deterministic artifacts that can be diffed across
architectures (ARM M1 ↔ x86 beef box) to confirm libm trig/log
differences and PCG64 stream determinism are not silently changing the
load-bearing observables. Both machines run this same script and
emit architecture-tagged output files; the diff is post-hoc.

Two sub-runs (mirroring `EXPENSIVE-BEEF-BOX-SIM.md` Step 0.1 and 0.3):

  A. M1+B1+B2 kernel at reduced scope (N = 10⁶, n = 100), seed
     0xBADC0DE1, IC = +√2, symmetric BS(1,2).
     Tests bit-stability of the L₁ trajectory and ĥ(1, n) under
     normal float64 step / Fourier code paths.

  B. R2 kernel (rational restart) at reduced scope (N = 10⁵, n = 50),
     seed 0xC0FFEE33 (= ROOT-TWO-CHECKS base ^ ord('2')), IC = +1.
     Tests bit-stability of the integer zero-hit count, the one
     observable where last-bit float differences could in principle
     change a discrete count.

Output (in `beef_box/`):
  - preflight_m1_b1_b2_ref_<arch>.npz
  - preflight_r2_ref_<arch>.npz

where `<arch>` is `platform.machine()` (e.g. `x86_64`, `arm64`).

Diff procedure (post-hoc, after both machines have run):
  python -c "import numpy as np; \
             a=np.load('preflight_m1_b1_b2_ref_x86_64.npz'); \
             b=np.load('preflight_m1_b1_b2_ref_arm64.npz'); \
             print('max |ΔL₁| =', np.max(np.abs(a['l1']-b['l1']))); \
             print('max |Δĥ(1)| =', np.max(np.abs(a['h_full'][:,0]-b['h_full'][:,0])))"

Acceptance criteria (per the plan):
  - max relative L₁ / ĥ(1) divergence ≲ 10⁻¹² (libm last-bit budget)
  - R2 zero-hit count agreement within ≲ 1% (~25,000 expected at N=10⁵)

Cost: ~30 sec total (sub-run A ~25 sec, sub-run B ~5 sec).

Run: sage -python run_preflight_reference.py
"""

import math
import os
import platform
import time
import numpy as np


# --- Common config ----------------------------------------------------

E_THRESH = 20
E_R = 3

MODES = np.array([1, 2, 3, 4, 5], dtype=np.int32)

LOG10_2 = math.log10(2.0)
LOG10_SQRT2 = 0.5 * LOG10_2

FOURIER_BATCH = 10**7

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
ARCH = platform.machine()


# --- Step kernel (identical to M1/M3/M4) ------------------------------

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
    """M1 / M3 standard b-step (no zero handling)."""
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


def step_b_r2(m, E, sign, mask, delta):
    """R2 b-step: exact-zero restart at (m=0, E=0, sign=sign(delta)).
    Returns count of exact-zero events for this sub-step."""
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


# --- Statistics -------------------------------------------------------

def compute_l1(m, n_bins):
    n = m.shape[0]
    hist, _ = np.histogram(m, bins=n_bins, range=(0.0, 1.0))
    freq = hist.astype(np.float64) / n
    return float(np.sum(np.abs(freq - 1.0 / n_bins)))


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


# --- Sub-run A: M1+B1+B2 small reference ------------------------------

def run_a():
    N_WALKERS = 10**6
    N_STEPS = 100
    N_BINS = 1000
    SEED = 0xBADC0DE1   # matches run_m1_b1_b2.py exactly

    print(f'\n=== A. M1+B1+B2 reference (N = {N_WALKERS:_}, n = {N_STEPS}) ===')
    print(f'  seed = {SEED:#x}, IC = +√2, modes = {MODES.tolist()}')

    rng = np.random.default_rng(SEED)
    m = np.full(N_WALKERS, LOG10_SQRT2, dtype=np.float64)
    E = np.zeros(N_WALKERS, dtype=np.int32)
    sign = np.ones(N_WALKERS, dtype=np.int8)

    l1_arr = np.zeros(N_STEPS, dtype=np.float64)
    h_full = np.zeros((N_STEPS, MODES.size), dtype=np.complex128)

    t0 = time.time()
    for step in range(1, N_STEPS + 1):
        choice = rng.integers(0, 4, size=N_WALKERS, dtype=np.int8)
        step_a(m, E, choice == 0)
        step_a_inv(m, E, choice == 1)
        step_b(m, E, sign, choice == 2, +1)
        step_b(m, E, sign, choice == 3, -1)

        h = compute_fourier(m, MODES)
        l1_arr[step - 1] = compute_l1(m, N_BINS)
        h_full[step - 1] = h

    dt = time.time() - t0
    print(f'  walk time: {dt:.2f}s')
    print(f'  L₁(100) = {l1_arr[-1]:.10e}')
    print(f'  |ĥ(1, 100)| = {abs(h_full[-1, 0]):.10e}')

    out_path = os.path.join(SIM_DIR, f'preflight_m1_b1_b2_ref_{ARCH}.npz')
    np.savez_compressed(
        out_path,
        sample_times=np.arange(1, N_STEPS + 1, dtype=np.int32),
        l1=l1_arr,
        h_full=h_full,
        modes=MODES,
        meta_N=np.int64(N_WALKERS),
        meta_steps=np.int32(N_STEPS),
        meta_bins=np.int32(N_BINS),
        meta_seed=np.int64(SEED),
        meta_arch=ARCH,
        meta_numpy_version=np.__version__,
    )
    print(f'  -> {out_path}')


# --- Sub-run B: R2 small reference -----------------------------------

def run_b():
    N_WALKERS = 10**5
    N_STEPS = 50
    N_BINS = 1000
    SEED = 0xC0FFEE01 ^ ord('2')   # matches run_root_two_checks.py R2 exactly

    print(f'\n=== B. R2 (rational restart) reference (N = {N_WALKERS:_}, n = {N_STEPS}) ===')
    print(f'  seed = {SEED:#x}, IC = +1, exact-zero restart')

    rng = np.random.default_rng(SEED)
    m = np.zeros(N_WALKERS, dtype=np.float64)
    E = np.zeros(N_WALKERS, dtype=np.int32)
    sign = np.ones(N_WALKERS, dtype=np.int8)

    l1_arr = np.zeros(N_STEPS, dtype=np.float64)
    h_full = np.zeros((N_STEPS, MODES.size), dtype=np.complex128)
    zero_hits_per_step = np.zeros(N_STEPS + 1, dtype=np.int64)

    t0 = time.time()
    for step in range(1, N_STEPS + 1):
        choice = rng.integers(0, 4, size=N_WALKERS, dtype=np.int8)
        step_a(m, E, choice == 0)
        step_a_inv(m, E, choice == 1)
        zh_pos = step_b_r2(m, E, sign, choice == 2, +1)
        zh_neg = step_b_r2(m, E, sign, choice == 3, -1)
        zero_hits_per_step[step] = zh_pos + zh_neg

        l1_arr[step - 1] = compute_l1(m, N_BINS)
        h_full[step - 1] = compute_fourier(m, MODES)

    dt = time.time() - t0
    total_hits = int(zero_hits_per_step.sum())
    print(f'  walk time: {dt:.2f}s')
    print(f'  total exact-zero hits: {total_hits:_} (≈ {total_hits/N_WALKERS:.4f} per walker)')
    print(f'  L₁(50) = {l1_arr[-1]:.10e}')

    out_path = os.path.join(SIM_DIR, f'preflight_r2_ref_{ARCH}.npz')
    np.savez_compressed(
        out_path,
        sample_times=np.arange(1, N_STEPS + 1, dtype=np.int32),
        l1=l1_arr,
        h_full=h_full,
        modes=MODES,
        zero_hits_per_step=zero_hits_per_step,
        total_zero_hits=np.int64(total_hits),
        meta_N=np.int64(N_WALKERS),
        meta_steps=np.int32(N_STEPS),
        meta_bins=np.int32(N_BINS),
        meta_seed=np.int64(SEED),
        meta_arch=ARCH,
        meta_numpy_version=np.__version__,
    )
    print(f'  -> {out_path}')


def main():
    print('Pre-flight reference regen for cross-architecture validation')
    print(f'Architecture tag: {ARCH}')
    print(f'NumPy version:    {np.__version__}')
    run_a()
    run_b()
    print('\nDone. Push these alongside the beef-box results so the M1 can')
    print('produce its own architecture-tagged copies after pulling and diff.')


if __name__ == '__main__':
    main()
