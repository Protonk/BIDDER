"""
SUBSET-STEP-BUDDIES sim: BS(1,2) full walk and alternating walk at
matched walker counts N ∈ {10⁴, 10⁵, 10⁶, 10⁷}, for the cross-N
sub-sampling comparison figure.

See `fig/SUBSET-STEP-BUDDIES-PLAN.md` for rationale and
`sim/SUBSET-THEOREM.md` for the theory this empirically checks.

Key design points:
- Stateless `step_alternating` (parity from explicit step_index),
  no closure state that could leak across runs.
- Deterministic arithmetic seeds (no Python hash salting).
- Shared kernel with `run_comparison_walks.py`.

Run: sage -python run_step_buddies.py
"""

import math
import os
import time
import numpy as np

# Reuse kernels from comparison-walks module.
from run_comparison_walks import (
    initialize,
    step_a,
    step_a_inv,
    step_b,
    compute_l1,
    N_BINS,
    E_THRESH,
    LOG10_2,
    LOG10_SQRT2,
)


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SIM_DIR, 'comparison_walks_results', 'step_buddies')
os.makedirs(OUT_DIR, exist_ok=True)


# --- Stateless step dispatchers -------------------------------------

def step_bs12(m, E, sign, rng, step_index):
    """Full BS(1,2) walk. step_index is ignored (included for uniform
    signature with step_alternating)."""
    choice = rng.integers(0, 4, size=m.shape[0], dtype=np.int8)
    step_a(m, E, choice == 0)
    step_a_inv(m, E, choice == 1)
    step_b(m, E, sign, choice == 2, +1)
    step_b(m, E, sign, choice == 3, -1)


def step_alternating(m, E, sign, rng, step_index):
    """Alternating walk: odd step_index → random {a, a⁻¹}, even
    step_index → random {b, b⁻¹}. No internal state; parity is read
    from the caller-passed step_index."""
    if step_index % 2 == 1:
        choice = rng.integers(0, 2, size=m.shape[0], dtype=np.int8)
        step_a(m, E, choice == 0)
        step_a_inv(m, E, choice == 1)
    else:
        choice = rng.integers(0, 2, size=m.shape[0], dtype=np.int8)
        step_b(m, E, sign, choice == 0, +1)
        step_b(m, E, sign, choice == 1, -1)


# --- Seeding --------------------------------------------------------

SEED_BASE = 0x51DE51DE

WALK_IDX = {'bs12': 0, 'alt': 1}


def compute_seed(walk, N, seed_idx):
    """Deterministic, interpreter-salt-free seed."""
    log_N = int(round(math.log10(N)))
    return SEED_BASE + WALK_IDX[walk] * 10**6 + log_N * 10**4 + seed_idx


# --- Run configuration ----------------------------------------------

N_MAX = 500
SAMPLE_TIMES = np.unique(np.concatenate([
    np.arange(1, 101, dtype=np.int32),
    np.arange(105, N_MAX + 1, 5, dtype=np.int32),
]))

# (N, seeds): how many independent seeds to run at each N.
CONFIGS = [
    (10**4, 3),
    (10**5, 3),
    (10**6, 1),
    (10**7, 1),
]

WALKS = [
    ('bs12', step_bs12),
    ('alt',  step_alternating),
]


# --- Runner ---------------------------------------------------------

def run_walk(walk_name, step_fn, N, seed_idx):
    seed = compute_seed(walk_name, N, seed_idx)
    out_path = os.path.join(OUT_DIR, f'{walk_name}_N1e{int(round(math.log10(N)))}_s{seed_idx}.npz')

    print(f'\n=== {walk_name}  N={N:_}  seed_idx={seed_idx}  seed={seed} ===')
    rng = np.random.default_rng(seed)
    m, E, sign = initialize(N)
    l1_arr = np.zeros(SAMPLE_TIMES.size, dtype=np.float64)
    sample_set = set(SAMPLE_TIMES.tolist())
    sample_idx = 0
    t0 = time.time()

    for step in range(1, N_MAX + 1):
        step_fn(m, E, sign, rng, step)
        if step in sample_set:
            l1_arr[sample_idx] = compute_l1(m)
            if sample_idx % max(1, SAMPLE_TIMES.size // 6) == 0 or step == N_MAX:
                dt = time.time() - t0
                print(f'  n={step:4d}  L₁={l1_arr[sample_idx]:.4e}  ({step/max(dt,1e-9):.1f} s/s)',
                      flush=True)
            sample_idx += 1

    total = time.time() - t0
    print(f'  wall: {total:.1f}s')

    np.savez_compressed(
        out_path,
        sample_times=SAMPLE_TIMES,
        l1=l1_arr,
        meta_N=np.int64(N),
        meta_steps=np.int32(N_MAX),
        meta_bins=np.int32(N_BINS),
        meta_seed=np.int64(seed),
        meta_walk=np.str_(walk_name),
        meta_seed_idx=np.int32(seed_idx),
    )
    print(f'  -> {out_path}')
    return out_path


def main():
    print('SUBSET-STEP-BUDDIES sim')
    print(f'  N_MAX = {N_MAX}, B = {N_BINS}, E_THRESH = {E_THRESH}')
    print(f'  configs = {CONFIGS}')
    print(f'  walks = {[w[0] for w in WALKS]}')
    print(f'  sample times: {SAMPLE_TIMES.size}')

    total_runs = sum(2 * seeds for (_, seeds) in CONFIGS)
    print(f'  total runs = {total_runs}')

    for (N, n_seeds) in CONFIGS:
        for (walk_name, step_fn) in WALKS:
            for seed_idx in range(n_seeds):
                run_walk(walk_name, step_fn, N, seed_idx)

    print('\n=== SUBSET-STEP-BUDDIES complete ===')


if __name__ == '__main__':
    main()
