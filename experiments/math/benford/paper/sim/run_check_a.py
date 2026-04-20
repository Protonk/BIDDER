"""
CHECK A: Markov-type-correlation walk on ℤ² torus and H_3(ℤ/L).

Tests whether the 2× slowdown of alternating vs full is a continuous
function of type-choice correlation, or a threshold effect.

At each step, walker type (x or y) is chosen by a Markov chain with
switching probability p_switch:
  - p_switch = 0.5: independent types per step → full walk (r = 1)
  - p_switch = 1.0: strictly alternating → current purple (r = 2)
  - p_switch = 0.75: intermediate

Run on ℤ² (L=31) and H_3(ℤ/15) at N = 10⁶, n_max = 2000.
Compare hit-times to existing full and alt data in
f2_contrast_results/torus/ and h3_contrast_results/.

Run: sage -python run_check_a.py
"""

import math
import os
import time
import numpy as np


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SIM_DIR, 'check_a_results')
os.makedirs(OUT_DIR, exist_ok=True)

N_WALKERS = 10**6
N_MAX = 2000
SAMPLE_TIMES = np.arange(10, N_MAX + 1, 10, dtype=np.int32)

P_SWITCH = 0.75
SEED_BASE = 0xA_75_00


def precompute_type_schedule(n_max, p_switch, rng):
    """Global Markov chain on type (0 = x-type, 1 = y-type)."""
    types = np.zeros(n_max + 1, dtype=np.int8)  # 1-indexed
    types[1] = 0 if rng.random() < 0.5 else 1
    for i in range(2, n_max + 1):
        if rng.random() < p_switch:
            types[i] = 1 - types[i-1]
        else:
            types[i] = types[i-1]
    return types


# --- ℤ² torus ---------------------------------------------------------

L_Z2 = 31


def init_z2(n):
    x = np.zeros(n, dtype=np.int32)
    y = np.zeros(n, dtype=np.int32)
    return x, y


def step_z2(x, y, rng, type_at_step):
    """type_at_step ∈ {0 = x-type, 1 = y-type}."""
    choice = rng.integers(0, 2, size=x.shape[0], dtype=np.int8)
    delta = choice.astype(np.int32) * 2 - 1  # 0→-1, 1→+1
    if type_at_step == 0:
        x += delta
        x %= L_Z2
    else:
        y += delta
        y %= L_Z2


def l1_z2(x, y):
    n = x.shape[0]
    idx = x.astype(np.int64) * L_Z2 + y.astype(np.int64)
    hist = np.bincount(idx, minlength=L_Z2 * L_Z2)
    freq = hist.astype(np.float64) / n
    return float(np.sum(np.abs(freq - 1.0 / (L_Z2 * L_Z2))))


def run_z2_markov(p_switch, seed, out_path):
    print(f'\n=== Z² Markov p={p_switch}  N={N_WALKERS:_}  seed={seed} ===')
    rng = np.random.default_rng(seed)
    type_sched = precompute_type_schedule(N_MAX, p_switch, rng)
    x, y = init_z2(N_WALKERS)
    l1_arr = np.zeros(SAMPLE_TIMES.size, dtype=np.float64)
    sample_set = set(SAMPLE_TIMES.tolist())
    sample_idx = 0
    t0 = time.time()
    for step in range(1, N_MAX + 1):
        step_z2(x, y, rng, int(type_sched[step]))
        if step in sample_set:
            l1_arr[sample_idx] = l1_z2(x, y)
            if sample_idx % 40 == 0 or step == N_MAX:
                dt = time.time() - t0
                print(f'  n={step:5d}  L₁={l1_arr[sample_idx]:.4e}  '
                      f'({step/max(dt,1e-9):.1f} s/s)', flush=True)
            sample_idx += 1
    print(f'  wall: {time.time()-t0:.1f}s')
    np.savez_compressed(out_path,
                        sample_times=SAMPLE_TIMES, l1=l1_arr,
                        meta_N=np.int64(N_WALKERS),
                        meta_L=np.int32(L_Z2),
                        meta_p_switch=np.float64(p_switch),
                        meta_seed=np.int64(seed),
                        meta_walk=np.str_('markov'))
    print(f'  -> {out_path}')


# --- H_3 ℤ/L ---------------------------------------------------------

L_H3 = 15


def init_h3(n):
    a = np.zeros(n, dtype=np.int32)
    b = np.zeros(n, dtype=np.int32)
    c = np.zeros(n, dtype=np.int32)
    return a, b, c


def step_h3(a, b, c, rng, type_at_step):
    """type_at_step: 0 = x-type (a±1), 1 = y-type (b±1, c±=a)."""
    choice = rng.integers(0, 2, size=a.shape[0], dtype=np.int8)
    delta = choice.astype(np.int32) * 2 - 1  # ±1
    if type_at_step == 0:
        a += delta
        a %= L_H3
    else:
        c += delta * a  # c ± a
        c %= L_H3
        b += delta
        b %= L_H3


def l1_h3(a, b, c):
    n = a.shape[0]
    idx = (a.astype(np.int64) * (L_H3 * L_H3) +
           b.astype(np.int64) * L_H3 +
           c.astype(np.int64))
    hist = np.bincount(idx, minlength=L_H3 ** 3)
    freq = hist.astype(np.float64) / n
    return float(np.sum(np.abs(freq - 1.0 / (L_H3 ** 3))))


def run_h3_markov(p_switch, seed, out_path):
    print(f'\n=== H_3 Markov p={p_switch}  N={N_WALKERS:_}  seed={seed} ===')
    rng = np.random.default_rng(seed)
    type_sched = precompute_type_schedule(N_MAX, p_switch, rng)
    a, b, c = init_h3(N_WALKERS)
    l1_arr = np.zeros(SAMPLE_TIMES.size, dtype=np.float64)
    sample_set = set(SAMPLE_TIMES.tolist())
    sample_idx = 0
    t0 = time.time()
    for step in range(1, N_MAX + 1):
        step_h3(a, b, c, rng, int(type_sched[step]))
        if step in sample_set:
            l1_arr[sample_idx] = l1_h3(a, b, c)
            if sample_idx % 40 == 0 or step == N_MAX:
                dt = time.time() - t0
                print(f'  n={step:5d}  L₁={l1_arr[sample_idx]:.4e}  '
                      f'({step/max(dt,1e-9):.1f} s/s)', flush=True)
            sample_idx += 1
    print(f'  wall: {time.time()-t0:.1f}s')
    np.savez_compressed(out_path,
                        sample_times=SAMPLE_TIMES, l1=l1_arr,
                        meta_N=np.int64(N_WALKERS),
                        meta_L=np.int32(L_H3),
                        meta_p_switch=np.float64(p_switch),
                        meta_seed=np.int64(seed),
                        meta_walk=np.str_('markov'))
    print(f'  -> {out_path}')


def main():
    print(f'CHECK A: Markov-type walk at p_switch = {P_SWITCH}')
    run_z2_markov(P_SWITCH, SEED_BASE + 1,
                  os.path.join(OUT_DIR, f'z2_markov_p075_N1e6.npz'))
    run_h3_markov(P_SWITCH, SEED_BASE + 2,
                  os.path.join(OUT_DIR, f'h3_markov_p075_N1e6.npz'))
    print('\n=== CHECK A complete ===')


if __name__ == '__main__':
    main()
