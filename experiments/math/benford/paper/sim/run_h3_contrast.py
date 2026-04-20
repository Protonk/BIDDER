"""
H3-CONTRAST-SIM: Heisenberg H_3(ℤ/L) walks, fourth data point in the
sub-sampling slowdown comparison across groups.

H_3 group law: (a, b, c) · (a', b', c') = (a+a', b+b', c+c' + a·b').
Generators x = (1, 0, 0), y = (0, 1, 0). The commutator [x, y] =
(0, 0, 1) = z is central.

Actions on walker state (a, b, c) ∈ (ℤ/L)³:
  x    : a ← a + 1
  x⁻¹  : a ← a − 1
  y    : b ← b + 1, c ← c + a
  y⁻¹  : b ← b − 1, c ← c − a

All arithmetic mod L (L odd to avoid bipartite pathology).

Two walks:
  - full:    step uniform on {x, x⁻¹, y, y⁻¹}
  - alt:     odd step uniform on {x, x⁻¹}; even step uniform on {y, y⁻¹}

Observable: L₁ to uniform on the L³-cell state space.

Run: sage -python run_h3_contrast.py
"""

import math
import os
import time
import numpy as np


# --- Config -----------------------------------------------------------

L = 15                      # odd — no bipartite pathology
N_MAX = 2000
SAMPLE_TIMES = np.arange(10, N_MAX + 1, 10, dtype=np.int32)

SEED_BASE = 0xDE7A3333
WALK_IDX = {'full': 0, 'alt': 1}

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SIM_DIR, 'h3_contrast_results')
os.makedirs(OUT_DIR, exist_ok=True)


# --- Walker init ------------------------------------------------------

def init_walkers(n):
    a = np.zeros(n, dtype=np.int32)
    b = np.zeros(n, dtype=np.int32)
    c = np.zeros(n, dtype=np.int32)
    return a, b, c


# --- Step kernels (fully vectorized, in-place) -----------------------

def step_full(a, b, c, rng, step_index):
    """choice 0: x (a+=1); 1: x⁻¹ (a-=1); 2: y (b+=1, c+=a); 3: y⁻¹
    (b-=1, c-=a). IMPORTANT: c depends on CURRENT a, so update c
    before mutating a."""
    choice = rng.integers(0, 4, size=a.shape[0], dtype=np.int8)
    y_plus = choice == 2
    y_minus = choice == 3

    # c-update (uses current a, done first)
    c_delta = np.where(y_plus, a, 0) + np.where(y_minus, -a, 0)
    c += c_delta
    c %= L

    # b-update
    b += y_plus.astype(np.int32) - y_minus.astype(np.int32)
    b %= L

    # a-update
    a += (choice == 0).astype(np.int32) - (choice == 1).astype(np.int32)
    a %= L


def step_alt(a, b, c, rng, step_index):
    """Alternating: odd step picks from {x, x⁻¹}, even from {y, y⁻¹}."""
    if step_index % 2 == 1:
        # odd: x-type only (choice 0: x, 1: x⁻¹)
        choice = rng.integers(0, 2, size=a.shape[0], dtype=np.int8)
        a += (choice == 0).astype(np.int32) - (choice == 1).astype(np.int32)
        a %= L
    else:
        # even: y-type only (choice 0: y, 1: y⁻¹)
        choice = rng.integers(0, 2, size=a.shape[0], dtype=np.int8)
        y_plus = choice == 0
        y_minus = choice == 1
        c_delta = np.where(y_plus, a, 0) + np.where(y_minus, -a, 0)
        c += c_delta
        c %= L
        b += y_plus.astype(np.int32) - y_minus.astype(np.int32)
        b %= L


# --- Statistic -------------------------------------------------------

def compute_l1(a, b, c):
    n = a.shape[0]
    # Flatten (a, b, c) into single cell index in [0, L³)
    idx = (a.astype(np.int64) * (L * L) +
           b.astype(np.int64) * L +
           c.astype(np.int64))
    hist = np.bincount(idx, minlength=L**3)
    freq = hist.astype(np.float64) / n
    return float(np.sum(np.abs(freq - 1.0 / (L**3))))


# --- Seeding ---------------------------------------------------------

def compute_seed(walk, N, seed_idx=0):
    log_N = int(round(math.log10(N)))
    return SEED_BASE + WALK_IDX[walk] * 10**6 + log_N * 10**4 + seed_idx


# --- Runner ----------------------------------------------------------

def run_walk(walk_name, step_fn, N, seed_idx=0):
    seed = compute_seed(walk_name, N, seed_idx)
    log_N = int(round(math.log10(N)))
    out_path = os.path.join(OUT_DIR, f'{walk_name}_N1e{log_N}.npz')

    print(f'\n=== {walk_name}  N={N:_}  seed={seed} ===')
    rng = np.random.default_rng(seed)
    a, b, c = init_walkers(N)
    l1_arr = np.zeros(SAMPLE_TIMES.size, dtype=np.float64)
    sample_set = set(SAMPLE_TIMES.tolist())
    sample_idx = 0
    t0 = time.time()

    for step in range(1, N_MAX + 1):
        step_fn(a, b, c, rng, step)
        if step in sample_set:
            l1_arr[sample_idx] = compute_l1(a, b, c)
            if sample_idx % max(1, SAMPLE_TIMES.size // 8) == 0 or step == N_MAX:
                dt = time.time() - t0
                print(f'  n={step:5d}  L₁={l1_arr[sample_idx]:.4e}  '
                      f'({step/max(dt,1e-9):.1f} s/s)', flush=True)
            sample_idx += 1

    total = time.time() - t0
    print(f'  wall: {total:.1f}s')

    np.savez_compressed(
        out_path,
        sample_times=SAMPLE_TIMES,
        l1=l1_arr,
        meta_N=np.int64(N),
        meta_L=np.int32(L),
        meta_steps=np.int32(N_MAX),
        meta_seed=np.int64(seed),
        meta_walk=np.str_(walk_name),
    )
    print(f'  -> {out_path}')


def main():
    print(f'H3-CONTRAST-SIM  (Heisenberg H_3(ℤ/{L}))')
    print(f'  state space = L³ = {L**3}')
    print(f'  N_MAX = {N_MAX}')

    for N in [10**5, 10**6, 10**7]:
        for walk_name, step_fn in [('full', step_full), ('alt', step_alt)]:
            run_walk(walk_name, step_fn, N)

    print('\n=== H3-CONTRAST complete ===')


if __name__ == '__main__':
    main()
