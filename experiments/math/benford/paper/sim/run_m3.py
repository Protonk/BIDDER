"""
M3 — Initial-condition robustness.

Runs three nontrivial ICs on the M1 sampling schedule. Purpose: check
that the rate classification is not an artifact of the √2 IC used in M1.

ICs:
  (a) m ~ Uniform[0, 1), E = 0, sign = +1
  (b) m = log₁₀√2, E ~ Uniform{−5, …, 5}, sign = +1
  (c) m ~ Uniform[0, 1), E ~ Uniform{−5, …, 5}, sign = +1

(b) and (c) use log₁₀√2 instead of m = 0 because the orbit-exclusion-of-0
argument (see `run_m1_b1_b2.py`) requires √2 in the shifted value to keep
the b-step's x = 0 case algebraically impossible. The qualitative purpose
of (b) and (c) — spread over nontrivial E — is preserved.

Per-IC output: L₁(n) on the M1 sample grid, ensemble Fourier ĥ(r, n) for
r ∈ {1..5}, cohort sizes, and ‖h‖_{L²}. No conditional-by-return-count
data (M1 already has that at the sharper IC).

N = 10⁷ per IC (10× less than M1) — M3's thresholds are coarse (within
15% of M1's c, slope ratio and residual sign), so the resulting 1/√N
noise inflation (θ_N ≈ 8.6×10⁻³ vs. M1's 2.72×10⁻³) is acceptable on
the [20, 200] fit window where L₁ is O(10⁻¹ → 10⁻²).

Run: sage -python run_m3.py
"""

import math
import os
import time
import numpy as np


# --- Config -----------------------------------------------------------

N_WALKERS = 10**7
N_STEPS = 600
N_BINS = 1000
SEED_BASE = 0xEE1C3A11

E_THRESH = 20
E_R = 3

MODES = np.array([1, 2, 3, 4, 5], dtype=np.int32)

SAMPLE_TIMES = np.concatenate([
    np.arange(1, 201, dtype=np.int32),
    np.arange(205, 601, 5, dtype=np.int32),
])

FOURIER_BATCH = 10**7

LOG10_2 = math.log10(2.0)
LOG10_SQRT2 = 0.5 * LOG10_2

E_INIT_RANGE = 5  # uniform on {−5, …, 5} for ICs (b) and (c)

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(SIM_DIR, 'm3_results.npz')


# --- IC initializers --------------------------------------------------

def initialize_a(n, rng):
    """IC (a): m ~ U[0,1), E = 0, sign = +1."""
    m = rng.random(n, dtype=np.float64)
    E = np.zeros(n, dtype=np.int32)
    sign = np.ones(n, dtype=np.int8)
    return m, E, sign


def initialize_b(n, rng):
    """IC (b): m = log₁₀√2, E ~ U{−5, …, 5}, sign = +1."""
    m = np.full(n, LOG10_SQRT2, dtype=np.float64)
    E = rng.integers(-E_INIT_RANGE, E_INIT_RANGE + 1, size=n, dtype=np.int32)
    sign = np.ones(n, dtype=np.int8)
    return m, E, sign


def initialize_c(n, rng):
    """IC (c): m ~ U[0,1), E ~ U{−5, …, 5}, sign = +1."""
    m = rng.random(n, dtype=np.float64)
    E = rng.integers(-E_INIT_RANGE, E_INIT_RANGE + 1, size=n, dtype=np.int32)
    sign = np.ones(n, dtype=np.int8)
    return m, E, sign


INITIALIZERS = {
    'a': ('m~U[0,1), E=0', initialize_a),
    'b': ('m=log10√2, E~U{-5..5}', initialize_b),
    'c': ('m~U[0,1), E~U{-5..5}', initialize_c),
}


# --- Step kernel (identical to M1) ------------------------------------

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


# --- Per-IC run ------------------------------------------------------

def run_ic(ic_key, rng, verbose=True):
    desc, init_fn = INITIALIZERS[ic_key]
    print(f'\n=== IC ({ic_key}): {desc} ===')
    print(f'  N = {N_WALKERS:_}, steps = {N_STEPS}')

    t0 = time.time()
    m, E, sign = init_fn(N_WALKERS, rng)
    print(f'  init: {time.time()-t0:.2f}s')

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

            if verbose and (sample_idx % 50 == 0 or step == N_STEPS):
                dt = time.time() - t_start
                rate = step / max(dt, 1e-9)
                eta = (N_STEPS - step) / max(rate, 1e-9)
                print(f'  n={step:4d}  L₁={l1_arr[sample_idx]:.5f}  '
                      f'|ĥ(1)|={abs(h[0]):.4f}  '
                      f'({rate:.1f} steps/s, ETA {eta:.0f}s)', flush=True)
            sample_idx += 1

    total = time.time() - t_start
    print(f'  Walk time: {total:.1f}s = {total/60:.2f} min')
    return dict(
        l1=l1_arr,
        h_full=h_full,
        l2_norm=l2_norm,
    )


def main():
    print(f'M3 — IC robustness')
    print(f'Seed base: {SEED_BASE:#x}; per-IC seed = base ^ ord(ic)')

    results = {}
    for ic_key in ['a', 'b', 'c']:
        seed = SEED_BASE ^ ord(ic_key)
        rng = np.random.default_rng(seed)
        r = run_ic(ic_key, rng)
        r['seed'] = seed
        results[ic_key] = r

    # Save results
    out = dict(
        sample_times=SAMPLE_TIMES,
        modes=MODES,
        meta_N=np.int64(N_WALKERS),
        meta_steps=np.int32(N_STEPS),
        meta_bins=np.int32(N_BINS),
        meta_E_R=np.int32(E_R),
        meta_E_THRESH=np.int32(E_THRESH),
        meta_seed_base=np.int64(SEED_BASE),
    )
    for ic_key in ['a', 'b', 'c']:
        r = results[ic_key]
        out[f'ic_{ic_key}_l1'] = r['l1']
        out[f'ic_{ic_key}_h_full'] = r['h_full']
        out[f'ic_{ic_key}_l2_norm'] = r['l2_norm']
        out[f'ic_{ic_key}_seed'] = np.int64(r['seed'])

    np.savez_compressed(OUT_PATH, **out)
    print(f'\n-> {OUT_PATH}')


if __name__ == '__main__':
    main()
