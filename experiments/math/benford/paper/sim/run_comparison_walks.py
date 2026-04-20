"""
Comparison sim: pure-multiplicative vs pure-additive walks, both from
x = √2, for the "why BS(1,2) is in the Goldilocks zone" figure.

Pure-mul: only {a, a⁻¹}, equivalent to irrational rotation on T by
  ±log₁₀ 2. Converges exponentially fast.
Pure-add: only {b, b⁻¹}. Walker stays on √2 + ℤ. Magnitude |x| grows
  like √n; log-mantissa distribution sees O(log n) decades, so L₁
  decays like 1/log n.

Same kernel and IC as M1 (√2, symmetric) but with step probabilities
reduced to the relevant subset. Used alongside M1's L₁(n) for a
3-walk comparison figure.

Run: sage -python run_comparison_walks.py
"""

import math
import os
import time
import numpy as np


N_BINS = 1000
E_THRESH = 20
LOG10_2 = math.log10(2.0)
LOG10_SQRT2 = 0.5 * LOG10_2

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SIM_DIR, 'comparison_walks_results')
os.makedirs(OUT_DIR, exist_ok=True)


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


def step_pure_mul(m, E, sign, rng):
    """Only a, a⁻¹. choice ∈ {0, 1} with equal probability."""
    choice = rng.integers(0, 2, size=m.shape[0], dtype=np.int8)
    step_a(m, E, choice == 0)
    step_a_inv(m, E, choice == 1)


def step_pure_add(m, E, sign, rng):
    """Only b, b⁻¹. choice ∈ {0, 1} with equal probability."""
    choice = rng.integers(0, 2, size=m.shape[0], dtype=np.int8)
    step_b(m, E, sign, choice == 0, +1)
    step_b(m, E, sign, choice == 1, -1)


def step_alternating_factory():
    """Returns a step function that alternates mul-step and add-step by
    (global) step parity: odd steps pick from {a, a⁻¹}, even steps pick
    from {b, b⁻¹}. Random sign within each class. All walkers share the
    same parity schedule, so the alternation is 'forced' at ensemble
    level and sign is the only randomness per step."""
    state = {'step_count': 0}
    def step_alt(m, E, sign, rng):
        state['step_count'] += 1
        if state['step_count'] % 2 == 1:
            # odd step: mul
            choice = rng.integers(0, 2, size=m.shape[0], dtype=np.int8)
            step_a(m, E, choice == 0)
            step_a_inv(m, E, choice == 1)
        else:
            # even step: add
            choice = rng.integers(0, 2, size=m.shape[0], dtype=np.int8)
            step_b(m, E, sign, choice == 0, +1)
            step_b(m, E, sign, choice == 1, -1)
    return step_alt


def compute_l1(m):
    n = m.shape[0]
    hist, _ = np.histogram(m, bins=N_BINS, range=(0.0, 1.0))
    freq = hist.astype(np.float64) / n
    return float(np.sum(np.abs(freq - 1.0 / N_BINS)))


def run_walk(label, step_fn, N, n_steps, sample_times, seed, out_path):
    print(f'\n=== {label}: N = {N:_}, n_max = {n_steps} ===')
    rng = np.random.default_rng(seed)
    m, E, sign = initialize(N)
    l1_arr = np.zeros(sample_times.size, dtype=np.float64)
    sample_set = set(sample_times.tolist())
    sample_idx = 0
    t0 = time.time()
    for step in range(1, n_steps + 1):
        step_fn(m, E, sign, rng)
        if step in sample_set:
            l1_arr[sample_idx] = compute_l1(m)
            if sample_idx % max(1, sample_times.size // 10) == 0 or step == n_steps:
                dt = time.time() - t0
                rate = step / max(dt, 1e-9)
                eta = (n_steps - step) / max(rate, 1e-9)
                print(f'  n={step:7d}  L₁={l1_arr[sample_idx]:.4e}  '
                      f'({rate:.1f} s/s, ETA {eta:.0f}s)', flush=True)
            sample_idx += 1
    print(f'  wall: {time.time()-t0:.1f}s')
    np.savez_compressed(out_path,
                        sample_times=sample_times,
                        l1=l1_arr,
                        meta_N=np.int64(N),
                        meta_steps=np.int32(n_steps),
                        meta_bins=np.int32(N_BINS),
                        meta_seed=np.int64(seed),
                        meta_label=np.str_(label))
    print(f'  -> {out_path}')


def main():
    # Pure multiplicative: horizon long enough to see bin-filling regime
    # and the subsequent Fourier-type decay. L₁ with B=1000 bins from a
    # delta IC is bounded below by ~(1 − support_size/B) until support
    # grows to cover all bins, which for pure-mul takes O(B) steps.
    N_mul = 10**6
    n_mul = 2000
    sample_mul = np.unique(np.concatenate([
        np.arange(1, 101, dtype=np.int32),
        np.arange(105, 1001, 5, dtype=np.int32),
        np.arange(1010, n_mul + 1, 20, dtype=np.int32),
    ]))
    run_walk('pure_multiplicative',
             step_pure_mul, N_mul, n_mul, sample_mul,
             seed=0xCA1C0FFEE & 0xFFFFFFFF,
             out_path=os.path.join(OUT_DIR, 'pure_mul_results.npz'))

    # Pure additive: slow convergence, long horizon.
    N_add = 10**6
    n_add = 10**4
    sample_add = np.unique(np.concatenate([
        np.arange(1, 101, dtype=np.int32),
        np.arange(105, 1001, 5, dtype=np.int32),
        np.arange(1010, n_add + 1, 50, dtype=np.int32),
    ]))
    run_walk('pure_additive',
             step_pure_add, N_add, n_add, sample_add,
             seed=0xADDAD0DE & 0xFFFFFFFF,
             out_path=os.path.join(OUT_DIR, 'pure_add_results.npz'))

    # Alternating add/mul (forced alternation, random sign per step).
    # Same N and horizon as BS(1,2) M1 for direct comparison.
    N_alt = 10**6
    n_alt = 1000
    sample_alt = np.unique(np.concatenate([
        np.arange(1, 201, dtype=np.int32),
        np.arange(205, n_alt + 1, 5, dtype=np.int32),
    ]))
    run_walk('alternating',
             step_alternating_factory(), N_alt, n_alt, sample_alt,
             seed=0xA17E4AA7 & 0xFFFFFFFF,
             out_path=os.path.join(OUT_DIR, 'alternating_results.npz'))

    print('\n=== Comparison walks complete ===')


if __name__ == '__main__':
    main()
