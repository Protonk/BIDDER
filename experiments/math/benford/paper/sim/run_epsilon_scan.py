"""
ε-scan of lazy-alt on ℤ² torus, L = 31.

Tests the U-shaped r(ε) prediction from the parity-mode mechanism.
At ε = 0 (pure alt), the (k = 15) near-parity mode dominates and
r_1D = 4, r_2D = 2. As ε increases, the parity mode is dampened
and at crossover ε ≈ 0.008 the (k = 1) mode overtakes it; at that
point r_1D = 1 and r_2D = 0.5 (lazy-alt is FASTER than full on 2D).
For ε > crossover, r rises back toward r_1D = 2, r_2D = 1 at ε =
0.5.

ε ∈ {0, 0.001, 0.003, 0.005, 0.008, 0.01, 0.03, 0.1, 0.3, 0.5}.

Run: sage -python run_epsilon_scan.py
"""

import math
import os
import time
import numpy as np


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SIM_DIR, 'epsilon_scan_results')
os.makedirs(OUT_DIR, exist_ok=True)

N_WALKERS = 10**6
N_MAX = 2500
SAMPLE_TIMES = np.arange(10, N_MAX + 1, 10, dtype=np.int32)
L = 31

EPSILONS = [0.0, 0.001, 0.003, 0.005, 0.008, 0.01, 0.03, 0.1, 0.3, 0.5]
SEED_BASE = 0xE951_1C00


def step_lazy_alt(x, y, rng, step_index, eps):
    """ε = 0 is pure alt; ε = 0.5 is lazy-alt-half."""
    if eps > 0:
        hold = rng.random(size=x.shape[0]) < eps
        active = ~hold
    else:
        active = np.ones(x.shape[0], dtype=bool)
    n_active = int(active.sum())
    if n_active == 0:
        return
    choice = rng.integers(0, 2, size=n_active, dtype=np.int8)
    delta = choice.astype(np.int32) * 2 - 1
    if step_index % 2 == 1:
        x[active] = (x[active] + delta) % L
    else:
        y[active] = (y[active] + delta) % L


def projections(x, y):
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


def run_one(eps, seed, out_path):
    print(f'\n=== lazy-alt ε={eps}  L={L}  N={N_WALKERS:_}  seed={seed} ===')
    rng = np.random.default_rng(seed)
    x = np.zeros(N_WALKERS, dtype=np.int32)
    y = np.zeros(N_WALKERS, dtype=np.int32)
    proj_names = ['full_2d', 'x_1d', 'y_1d']
    l1 = {p: np.zeros(SAMPLE_TIMES.size, dtype=np.float64) for p in proj_names}
    sample_set = set(SAMPLE_TIMES.tolist())
    sample_idx = 0
    t0 = time.time()
    for step in range(1, N_MAX + 1):
        step_lazy_alt(x, y, rng, step, eps)
        if step in sample_set:
            proj = projections(x, y)
            for p in proj_names:
                l1[p][sample_idx] = proj[p]
            if sample_idx % 50 == 0 or step == N_MAX:
                dt = time.time() - t0
                print(f'  n={step:5d}  2D={proj["full_2d"]:.4e}  '
                      f'x1D={proj["x_1d"]:.4e}  '
                      f'({step/max(dt,1e-9):.1f} s/s)', flush=True)
            sample_idx += 1
    print(f'  wall: {time.time()-t0:.1f}s')
    np.savez_compressed(out_path,
                        sample_times=SAMPLE_TIMES,
                        **{f'l1_{p}': l1[p] for p in proj_names},
                        meta_L=np.int32(L),
                        meta_N=np.int64(N_WALKERS),
                        meta_seed=np.int64(seed),
                        meta_eps=np.float64(eps))
    print(f'  -> {out_path}')


def main():
    print(f'ε-scan of lazy-alt on ℤ²/{L}²')
    for i, eps in enumerate(EPSILONS):
        tag = f'eps{eps:.3f}'.replace('.', 'p')
        path = os.path.join(OUT_DIR, f'z2_lazy_alt_{tag}.npz')
        run_one(eps, SEED_BASE + i + 1, path)
    print('\n=== ε-scan complete ===')


if __name__ == '__main__':
    main()
