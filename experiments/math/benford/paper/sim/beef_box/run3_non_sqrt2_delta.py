"""
Run 3 — NON-SQRT2-DELTA.

Beef-box pressure-test of M3 IC (b) for hidden √2-specific structure.
The IC (b) recipe fixes m at log₁₀√2 = ½ · log₁₀ 2 — a *rational*
multiple of the walk's rotation quantum log₁₀ 2. If that rational
relationship is producing the clean α̂ ≈ 0.525 signal as an arithmetic
artifact (rather than as a generic consequence of sharp m + spread E),
substituting other m-values should shift α̂.

Three substitutions, all keeping the M3 IC (b) shell (sharp delta in m,
E ~ Uniform{−5, …, 5}, sign = +1) and the M3 horizon n_max = 600:

| label          | m value            | x analog | class                |
|:---------------|:-------------------|:---------|:---------------------|
| pi             | log₁₀ π            | π        | transcendental       |
| seven_fifths   | log₁₀(7/5)         | 7/5      | non-dyadic rational  |
| sqrt3          | log₁₀√3            | √3       | algebraic ≠ √2       |

Each orbit excludes x = 0 by an analogous orbit-arithmetic argument
(π and √3 by irrationality; 7/5 because 2^k · 7 ≡ 0 mod 5 has no
solution). In float64 the round-trip through log10/floor could in
principle still produce an exact zero, so the plan calls for the
R2-style defensive restart (restart at (m=0, E=0, sign=sign(delta))
if x_new == 0.0). Zero hits are tracked and expected to stay at 0.

Per-IC output: L₁(n), ensemble ĥ(r, n) for r = 1..5, l2_norm(n) on
the M3 sample grid (every step [1, 200], every 5 from 205 to 600).

N = 10⁷ per IC. Cost (beef box): ~5 min per IC, ~15 min total + overhead.

Run: sage -python run3_non_sqrt2_delta.py
"""

import math
import os
import time
import numpy as np


# --- Config -----------------------------------------------------------

N_WALKERS = 10**7
N_STEPS = 600
N_BINS = 1000
SEED_BASE = 0xBEE8B0AC

E_THRESH = 20
E_R = 3
E_INIT_RANGE = 5  # matches M3 IC (b)

MODES = np.array([1, 2, 3, 4, 5], dtype=np.int32)

SAMPLE_TIMES = np.concatenate([
    np.arange(1, 201, dtype=np.int32),
    np.arange(205, 601, 5, dtype=np.int32),
])

FOURIER_BATCH = 10**7

LOG10_2 = math.log10(2.0)

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SIM_DIR, 'run3_non_sqrt2_delta')


# --- IC catalog ------------------------------------------------------

# Each entry: (m_init_value, x_analog_str, class_str, seed_tag).
# m_init values are all in [0, 1), so no mod-1 reduction is needed.
ICS = {
    'pi':            (math.log10(math.pi),                    'π',           'transcendental',      ord('p')),
    'seven_fifths':  (math.log10(7.0 / 5.0),                  '7/5',         'non-dyadic rational', ord('7')),
    'sqrt3':         (0.5 * math.log10(3.0),                  '√3',          'algebraic ≠ √2',      ord('s')),
}


# --- Step kernel (identical to M1/M3) --------------------------------

def initialize(n, m_value, rng):
    """m = m_value (delta), E ~ Uniform{−5, …, 5}, sign = +1."""
    m = np.full(n, m_value, dtype=np.float64)
    E = rng.integers(-E_INIT_RANGE, E_INIT_RANGE + 1, size=n, dtype=np.int32)
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


def step_b_restart(m, E, sign, mask, delta):
    """Symmetric b-step with defensive exact-zero restart (R2 convention).
    Returns count of exact-zero events; expected to be 0 for these ICs
    by orbit arithmetic, but tracked as a safety check."""
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


def step_walkers(m, E, sign, rng):
    """Returns total exact-zero events this step (expected: 0)."""
    choice = rng.integers(0, 4, size=m.shape[0], dtype=np.int8)
    step_a(m, E, choice == 0)
    step_a_inv(m, E, choice == 1)
    n_zero_pos = step_b_restart(m, E, sign, choice == 2, +1)
    n_zero_neg = step_b_restart(m, E, sign, choice == 3, -1)
    return n_zero_pos + n_zero_neg


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


# --- Per-IC driver ---------------------------------------------------

def run_one(label, m_value, x_str, class_str, seed):
    print(f'\n=== IC {label}: m = log₁₀({x_str}) = {m_value:.6f}  [{class_str}] ===')
    print(f'  N = {N_WALKERS:_}, n_max = {N_STEPS}, seed = {seed:#x}')

    rng = np.random.default_rng(seed)

    t0 = time.time()
    m, E, sign = initialize(N_WALKERS, m_value, rng)
    print(f'  init: {time.time()-t0:.2f}s')

    n_sample = SAMPLE_TIMES.size
    l1_arr = np.zeros(n_sample, dtype=np.float64)
    h_full = np.zeros((n_sample, MODES.size), dtype=np.complex128)
    l2_norm = np.zeros(n_sample, dtype=np.float64)
    zero_hits_per_step = np.zeros(N_STEPS + 1, dtype=np.int64)

    sample_set = set(SAMPLE_TIMES.tolist())
    sample_idx = 0
    t_start = time.time()

    for step in range(1, N_STEPS + 1):
        n_zero = step_walkers(m, E, sign, rng)
        zero_hits_per_step[step] = n_zero
        if step in sample_set:
            h = compute_fourier(m, MODES)
            l1_arr[sample_idx] = compute_l1(m)
            h_full[sample_idx] = h
            l2_norm[sample_idx] = float(np.sqrt(np.sum(np.abs(h) ** 2)))

            if (sample_idx % 50 == 0) or step == N_STEPS:
                dt = time.time() - t_start
                rate = step / max(dt, 1e-9)
                eta = (N_STEPS - step) / max(rate, 1e-9)
                print(f'  n={step:4d}  L₁={l1_arr[sample_idx]:.5f}  '
                      f'|ĥ(1)|={abs(h[0]):.4f}  '
                      f'({rate:.1f} steps/s, ETA {eta:.0f}s)', flush=True)
            sample_idx += 1

    total = time.time() - t_start
    total_zero = int(zero_hits_per_step.sum())
    print(f'  walk time: {total:.1f}s = {total/60:.2f} min')
    print(f'  total exact-zero hits: {total_zero:_} '
          f'(expected 0 by orbit arithmetic)')

    out_path = os.path.join(OUT_DIR, f'{label}_results.npz')
    np.savez_compressed(
        out_path,
        sample_times=SAMPLE_TIMES,
        l1=l1_arr,
        h_full=h_full,
        l2_norm=l2_norm,
        modes=MODES,
        zero_hits_per_step=zero_hits_per_step,
        meta_N=np.int64(N_WALKERS),
        meta_steps=np.int32(N_STEPS),
        meta_bins=np.int32(N_BINS),
        meta_E_R=np.int32(E_R),
        meta_E_THRESH=np.int32(E_THRESH),
        meta_E_INIT_RANGE=np.int32(E_INIT_RANGE),
        meta_seed=np.int64(seed),
        meta_m_init=np.float64(m_value),
        meta_x_analog=x_str,
        meta_class=class_str,
    )
    print(f'  -> {out_path}')


def main():
    print('Run 3 — NON-SQRT2-DELTA (M3 IC (b) substitutions: π, 7/5, √3)')
    print(f'Seed base: {SEED_BASE:#x}; per-IC seed = base ^ tag')

    os.makedirs(OUT_DIR, exist_ok=True)

    for label, (m_value, x_str, class_str, tag) in ICS.items():
        seed = SEED_BASE ^ tag
        run_one(label, m_value, x_str, class_str, seed)

    print('\nAll three ICs complete.')


if __name__ == '__main__':
    main()
