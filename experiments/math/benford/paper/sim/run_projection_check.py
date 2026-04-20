"""
Projection check: recompute sub-sampling slowdown r on ℤ² and H_3
under multiple projections of the state space, to test whether
lower-dimensional observables wash out the ~2× slowdown we see on
the full state.

Predictions:
- ℤ² full 2D gives r ≈ 2.0 (confirms existing measurement).
- ℤ² 1D-x marginal should give r ≈ 1.0 (since full and alt both
  give the x-marginal the same number of updates on average at
  matched n).
- H_3 full 3D gives r ≈ 2.0.
- H_3 (a,b) 2D projection = the abelianized (ℤ²-like) view; probably
  r ≈ 2.0 again.
- H_3 a-only 1D: predicted r ≈ 1.0 by same argument as ℤ².
- H_3 c-only 1D: wildcard. c evolves through a·b interactions; not
  obvious what r will be.

Runs full and alt walks on each group at N = 10⁶, n_max = 2000, L
matching the previous runs (ℤ² L=31, H_3 L=15). Saves one L₁ array
per projection per (group, walk) in a combined npz.

Run: sage -python run_projection_check.py
"""

import math
import os
import time
import numpy as np


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SIM_DIR, 'projection_check_results')
os.makedirs(OUT_DIR, exist_ok=True)

N_WALKERS = 10**6
N_MAX = 2000
SAMPLE_TIMES = np.arange(10, N_MAX + 1, 10, dtype=np.int32)

SEED_BASE = 0x9502EC71  # distinct from other runs


# --- ℤ² torus --------------------------------------------------------

L_Z2 = 31

def init_z2(n):
    return np.zeros(n, dtype=np.int32), np.zeros(n, dtype=np.int32)


def step_z2_full(x, y, rng, step_index):
    choice = rng.integers(0, 4, size=x.shape[0], dtype=np.int8)
    # 0: x+=1, 1: x-=1, 2: y+=1, 3: y-=1
    x += (choice == 0).astype(np.int32) - (choice == 1).astype(np.int32)
    x %= L_Z2
    y += (choice == 2).astype(np.int32) - (choice == 3).astype(np.int32)
    y %= L_Z2


def step_z2_alt(x, y, rng, step_index):
    if step_index % 2 == 1:
        choice = rng.integers(0, 2, size=x.shape[0], dtype=np.int8)
        x += (choice == 0).astype(np.int32) - (choice == 1).astype(np.int32)
        x %= L_Z2
    else:
        choice = rng.integers(0, 2, size=x.shape[0], dtype=np.int8)
        y += (choice == 0).astype(np.int32) - (choice == 1).astype(np.int32)
        y %= L_Z2


def z2_projections(x, y):
    """Return dict of L₁ values under different projections."""
    n = x.shape[0]
    out = {}

    # Full 2D
    idx2d = x.astype(np.int64) * L_Z2 + y.astype(np.int64)
    h2d = np.bincount(idx2d, minlength=L_Z2 * L_Z2)
    out['full_2d'] = float(np.sum(np.abs(h2d.astype(np.float64) / n - 1.0 / (L_Z2 * L_Z2))))

    # 1D x
    hx = np.bincount(x, minlength=L_Z2)
    out['x_1d'] = float(np.sum(np.abs(hx.astype(np.float64) / n - 1.0 / L_Z2)))

    # 1D y
    hy = np.bincount(y, minlength=L_Z2)
    out['y_1d'] = float(np.sum(np.abs(hy.astype(np.float64) / n - 1.0 / L_Z2)))

    return out


# --- H_3(ℤ/L) -------------------------------------------------------

L_H3 = 15


def init_h3(n):
    return (np.zeros(n, dtype=np.int32),
            np.zeros(n, dtype=np.int32),
            np.zeros(n, dtype=np.int32))


def step_h3_full(a, b, c, rng, step_index):
    choice = rng.integers(0, 4, size=a.shape[0], dtype=np.int8)
    y_plus = choice == 2
    y_minus = choice == 3
    c_delta = np.where(y_plus, a, 0) + np.where(y_minus, -a, 0)
    c += c_delta
    c %= L_H3
    b += y_plus.astype(np.int32) - y_minus.astype(np.int32)
    b %= L_H3
    a += (choice == 0).astype(np.int32) - (choice == 1).astype(np.int32)
    a %= L_H3


def step_h3_alt(a, b, c, rng, step_index):
    if step_index % 2 == 1:
        choice = rng.integers(0, 2, size=a.shape[0], dtype=np.int8)
        a += (choice == 0).astype(np.int32) - (choice == 1).astype(np.int32)
        a %= L_H3
    else:
        choice = rng.integers(0, 2, size=a.shape[0], dtype=np.int8)
        y_plus = choice == 0
        y_minus = choice == 1
        c_delta = np.where(y_plus, a, 0) + np.where(y_minus, -a, 0)
        c += c_delta
        c %= L_H3
        b += y_plus.astype(np.int32) - y_minus.astype(np.int32)
        b %= L_H3


def h3_projections(a, b, c):
    n = a.shape[0]
    out = {}

    # Full 3D
    idx3d = (a.astype(np.int64) * (L_H3 * L_H3) +
             b.astype(np.int64) * L_H3 +
             c.astype(np.int64))
    h3d = np.bincount(idx3d, minlength=L_H3 ** 3)
    out['full_3d'] = float(np.sum(np.abs(h3d.astype(np.float64) / n - 1.0 / (L_H3 ** 3))))

    # 2D (a, b) — abelianized
    idx_ab = a.astype(np.int64) * L_H3 + b.astype(np.int64)
    h_ab = np.bincount(idx_ab, minlength=L_H3 ** 2)
    out['ab_2d'] = float(np.sum(np.abs(h_ab.astype(np.float64) / n - 1.0 / (L_H3 ** 2))))

    # 1D a
    h_a = np.bincount(a, minlength=L_H3)
    out['a_1d'] = float(np.sum(np.abs(h_a.astype(np.float64) / n - 1.0 / L_H3)))

    # 1D b
    h_b = np.bincount(b, minlength=L_H3)
    out['b_1d'] = float(np.sum(np.abs(h_b.astype(np.float64) / n - 1.0 / L_H3)))

    # 1D c (the commutator coordinate)
    h_c = np.bincount(c, minlength=L_H3)
    out['c_1d'] = float(np.sum(np.abs(h_c.astype(np.float64) / n - 1.0 / L_H3)))

    return out


# --- Runner ---------------------------------------------------------

def run_z2(walk_name, step_fn, seed, out_path):
    print(f'\n=== ℤ² {walk_name}  L={L_Z2}  N={N_WALKERS:_}  seed={seed} ===')
    rng = np.random.default_rng(seed)
    x, y = init_z2(N_WALKERS)
    proj_names = ['full_2d', 'x_1d', 'y_1d']
    l1_by_proj = {p: np.zeros(SAMPLE_TIMES.size, dtype=np.float64) for p in proj_names}
    sample_set = set(SAMPLE_TIMES.tolist())
    sample_idx = 0
    t0 = time.time()
    for step in range(1, N_MAX + 1):
        step_fn(x, y, rng, step)
        if step in sample_set:
            proj = z2_projections(x, y)
            for p in proj_names:
                l1_by_proj[p][sample_idx] = proj[p]
            if sample_idx % 40 == 0 or step == N_MAX:
                dt = time.time() - t0
                print(f'  n={step:5d}  2D={proj["full_2d"]:.4e}  x1D={proj["x_1d"]:.4e}  '
                      f'({step/max(dt,1e-9):.1f} s/s)', flush=True)
            sample_idx += 1
    print(f'  wall: {time.time()-t0:.1f}s')
    np.savez_compressed(out_path,
                        sample_times=SAMPLE_TIMES,
                        **{f'l1_{p}': l1_by_proj[p] for p in proj_names},
                        meta_L=np.int32(L_Z2),
                        meta_N=np.int64(N_WALKERS),
                        meta_seed=np.int64(seed),
                        meta_walk=np.str_(walk_name),
                        meta_group=np.str_('z2'))
    print(f'  -> {out_path}')


def run_h3(walk_name, step_fn, seed, out_path):
    print(f'\n=== H_3 {walk_name}  L={L_H3}  N={N_WALKERS:_}  seed={seed} ===')
    rng = np.random.default_rng(seed)
    a, b, c = init_h3(N_WALKERS)
    proj_names = ['full_3d', 'ab_2d', 'a_1d', 'b_1d', 'c_1d']
    l1_by_proj = {p: np.zeros(SAMPLE_TIMES.size, dtype=np.float64) for p in proj_names}
    sample_set = set(SAMPLE_TIMES.tolist())
    sample_idx = 0
    t0 = time.time()
    for step in range(1, N_MAX + 1):
        step_fn(a, b, c, rng, step)
        if step in sample_set:
            proj = h3_projections(a, b, c)
            for p in proj_names:
                l1_by_proj[p][sample_idx] = proj[p]
            if sample_idx % 40 == 0 or step == N_MAX:
                dt = time.time() - t0
                print(f'  n={step:5d}  3D={proj["full_3d"]:.4e}  a1D={proj["a_1d"]:.4e}  '
                      f'c1D={proj["c_1d"]:.4e}  ({step/max(dt,1e-9):.1f} s/s)', flush=True)
            sample_idx += 1
    print(f'  wall: {time.time()-t0:.1f}s')
    np.savez_compressed(out_path,
                        sample_times=SAMPLE_TIMES,
                        **{f'l1_{p}': l1_by_proj[p] for p in proj_names},
                        meta_L=np.int32(L_H3),
                        meta_N=np.int64(N_WALKERS),
                        meta_seed=np.int64(seed),
                        meta_walk=np.str_(walk_name),
                        meta_group=np.str_('h3'))
    print(f'  -> {out_path}')


def main():
    print('Projection check: ℤ² and H_3 under multiple projections')
    # ℤ²
    run_z2('full', step_z2_full, SEED_BASE + 1,
           os.path.join(OUT_DIR, 'z2_full.npz'))
    run_z2('alt', step_z2_alt, SEED_BASE + 2,
           os.path.join(OUT_DIR, 'z2_alt.npz'))
    # H_3
    run_h3('full', step_h3_full, SEED_BASE + 3,
           os.path.join(OUT_DIR, 'h3_full.npz'))
    run_h3('alt', step_h3_alt, SEED_BASE + 4,
           os.path.join(OUT_DIR, 'h3_alt.npz'))
    print('\n=== projection check sim complete ===')


if __name__ == '__main__':
    main()
