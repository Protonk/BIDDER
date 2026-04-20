"""
PARITY-MODE FALSIFIER: test whether the near-parity Fourier mode
is the mechanism for r = 4 on 1D and r = 2 on 2D in the projection
check (`projection_check_SUMMARY.md`).

Two new walks:

(A) lazy-alt on ℤ² torus at L = 31 (odd).
    At each calendar step, with prob ε = 1/2 hold; else execute the
    alt schedule step (x±1 on odd, y±1 on even).
    Predicted r vs existing z2_full.npz:
      2D full state: r ≈ 1.00
      x_1d marginal: r ≈ 2.00
    Contrast with measured r for pure alt (2.00, 4.00).

(B) alt and full on ℤ² torus at L = 30 (even).
    On even L, alt preserves an exact x-parity (x stays on one
    parity class of Z/30 forever). Predicted x_1d L₁(alt) plateaus
    at ≈ 1.0; L₁(full) mixes normally.

Run: sage -python run_parity_falsifier.py
"""

import math
import os
import time
import numpy as np


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SIM_DIR, 'parity_falsifier_results')
os.makedirs(OUT_DIR, exist_ok=True)

N_WALKERS = 10**6
N_MAX = 2000
SAMPLE_TIMES = np.arange(10, N_MAX + 1, 10, dtype=np.int32)



# --- step kernels ---------------------------------------------------

def step_z2_full(x, y, rng, step_index, L):
    choice = rng.integers(0, 4, size=x.shape[0], dtype=np.int8)
    x += (choice == 0).astype(np.int32) - (choice == 1).astype(np.int32)
    x %= L
    y += (choice == 2).astype(np.int32) - (choice == 3).astype(np.int32)
    y %= L


def step_z2_alt(x, y, rng, step_index, L):
    if step_index % 2 == 1:
        choice = rng.integers(0, 2, size=x.shape[0], dtype=np.int8)
        x += (choice == 0).astype(np.int32) - (choice == 1).astype(np.int32)
        x %= L
    else:
        choice = rng.integers(0, 2, size=x.shape[0], dtype=np.int8)
        y += (choice == 0).astype(np.int32) - (choice == 1).astype(np.int32)
        y %= L


def step_z2_lazy_alt(x, y, rng, step_index, L, eps=0.5):
    hold = rng.random(size=x.shape[0]) < eps
    active = ~hold
    n_active = int(active.sum())
    if n_active == 0:
        return
    choice = rng.integers(0, 2, size=n_active, dtype=np.int8)
    delta = (choice.astype(np.int32) * 2 - 1)
    if step_index % 2 == 1:
        x[active] = (x[active] + delta) % L
    else:
        y[active] = (y[active] + delta) % L


# --- observable -----------------------------------------------------

def projections_z2(x, y, L):
    n = x.shape[0]
    out = {}
    idx2d = x.astype(np.int64) * L + y.astype(np.int64)
    h2d = np.bincount(idx2d, minlength=L * L)
    out['full_2d'] = float(np.sum(np.abs(h2d.astype(np.float64) / n - 1.0 / (L * L))))
    hx = np.bincount(x, minlength=L)
    out['x_1d'] = float(np.sum(np.abs(hx.astype(np.float64) / n - 1.0 / L)))
    hy = np.bincount(y, minlength=L)
    out['y_1d'] = float(np.sum(np.abs(hy.astype(np.float64) / n - 1.0 / L)))
    return out


# --- runner ---------------------------------------------------------

def run(walk_name, step_fn, seed, L, out_path, extra_kwargs=None):
    print(f'\n=== ℤ² {walk_name}  L={L}  N={N_WALKERS:_}  seed={seed} ===')
    rng = np.random.default_rng(seed)
    x = np.zeros(N_WALKERS, dtype=np.int32)
    y = np.zeros(N_WALKERS, dtype=np.int32)
    proj_names = ['full_2d', 'x_1d', 'y_1d']
    l1_by_proj = {p: np.zeros(SAMPLE_TIMES.size, dtype=np.float64) for p in proj_names}
    sample_set = set(SAMPLE_TIMES.tolist())
    sample_idx = 0
    extra = extra_kwargs or {}
    t0 = time.time()
    for step in range(1, N_MAX + 1):
        step_fn(x, y, rng, step, L, **extra)
        if step in sample_set:
            proj = projections_z2(x, y, L)
            for p in proj_names:
                l1_by_proj[p][sample_idx] = proj[p]
            if sample_idx % 40 == 0 or step == N_MAX:
                dt = time.time() - t0
                print(f'  n={step:5d}  2D={proj["full_2d"]:.4e}  '
                      f'x1D={proj["x_1d"]:.4e}  '
                      f'({step/max(dt,1e-9):.1f} s/s)', flush=True)
            sample_idx += 1
    print(f'  wall: {time.time()-t0:.1f}s')
    np.savez_compressed(out_path,
                        sample_times=SAMPLE_TIMES,
                        **{f'l1_{p}': l1_by_proj[p] for p in proj_names},
                        meta_L=np.int32(L),
                        meta_N=np.int64(N_WALKERS),
                        meta_seed=np.int64(seed),
                        meta_walk=np.str_(walk_name))
    print(f'  -> {out_path}')


def main():
    print('PARITY FALSIFIER: lazy-alt (L=31) and even-L (L=30) tests')

    seed_base = 0xB1D3_0FFF  # distinct from projection check

    # Part A: lazy-alt at L=31
    run('lazy_alt_eps0.5', step_z2_lazy_alt, seed_base + 1, 31,
        os.path.join(OUT_DIR, 'z2_lazy_alt_L31.npz'),
        extra_kwargs={'eps': 0.5})

    # Part B: even-L test at L=30
    run('full_L30', step_z2_full, seed_base + 2, 30,
        os.path.join(OUT_DIR, 'z2_full_L30.npz'))
    run('alt_L30', step_z2_alt, seed_base + 3, 30,
        os.path.join(OUT_DIR, 'z2_alt_L30.npz'))

    print('\n=== parity falsifier sim complete ===')


if __name__ == '__main__':
    main()
