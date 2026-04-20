"""
ℤ³ torus (L = 15) full and alt walks.

Extends the parity-mode mechanism test to 3D. Predictions from the
spectral calculation:
  - 3D full state: r = 3 (alt has axis-parity modes at 1/3 cal rate;
    full has diagonal-parity mode at full rate)
  - 2D (a, b) marginal: r = 4
  - 1D (a only) marginal: r = 4

Alt cycles type through {x, y, z} by step_index mod 3.

Run: sage -python run_z3_torus.py
"""

import math
import os
import time
import numpy as np


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SIM_DIR, 'z3_torus_results')
os.makedirs(OUT_DIR, exist_ok=True)

N_WALKERS = 10**6
N_MAX = 2000
SAMPLE_TIMES = np.arange(10, N_MAX + 1, 10, dtype=np.int32)
L = 15
SEED_BASE = 0xCC33_FF15


def init_z3(n):
    return (np.zeros(n, dtype=np.int32),
            np.zeros(n, dtype=np.int32),
            np.zeros(n, dtype=np.int32))


def step_z3_full(a, b, c, rng, step_index):
    choice = rng.integers(0, 6, size=a.shape[0], dtype=np.int8)
    # 0:a+, 1:a-, 2:b+, 3:b-, 4:c+, 5:c-
    a += (choice == 0).astype(np.int32) - (choice == 1).astype(np.int32)
    a %= L
    b += (choice == 2).astype(np.int32) - (choice == 3).astype(np.int32)
    b %= L
    c += (choice == 4).astype(np.int32) - (choice == 5).astype(np.int32)
    c %= L


def step_z3_alt(a, b, c, rng, step_index):
    """Cycle through {a, b, c} by step_index mod 3."""
    choice = rng.integers(0, 2, size=a.shape[0], dtype=np.int8)
    delta = choice.astype(np.int32) * 2 - 1
    kind = (step_index - 1) % 3
    if kind == 0:
        a += delta
        a %= L
    elif kind == 1:
        b += delta
        b %= L
    else:
        c += delta
        c %= L


def projections(a, b, c):
    n = a.shape[0]
    out = {}
    idx3d = (a.astype(np.int64) * (L * L) +
             b.astype(np.int64) * L +
             c.astype(np.int64))
    h3d = np.bincount(idx3d, minlength=L ** 3)
    out['full_3d'] = float(np.sum(np.abs(h3d.astype(np.float64) / n - 1.0 / (L ** 3))))

    for pair, name in [((a, b), 'ab_2d'), ((a, c), 'ac_2d'), ((b, c), 'bc_2d')]:
        u, v = pair
        idx = u.astype(np.int64) * L + v.astype(np.int64)
        h = np.bincount(idx, minlength=L * L)
        out[name] = float(np.sum(np.abs(h.astype(np.float64) / n - 1.0 / (L * L))))

    for coord, name in [(a, 'a_1d'), (b, 'b_1d'), (c, 'c_1d')]:
        h = np.bincount(coord, minlength=L)
        out[name] = float(np.sum(np.abs(h.astype(np.float64) / n - 1.0 / L)))

    return out


def run(walk_name, step_fn, seed, out_path):
    print(f'\n=== ℤ³ {walk_name}  L={L}  N={N_WALKERS:_}  seed={seed} ===')
    rng = np.random.default_rng(seed)
    a, b, c = init_z3(N_WALKERS)
    proj_names = ['full_3d', 'ab_2d', 'ac_2d', 'bc_2d',
                  'a_1d', 'b_1d', 'c_1d']
    l1 = {p: np.zeros(SAMPLE_TIMES.size, dtype=np.float64) for p in proj_names}
    sample_set = set(SAMPLE_TIMES.tolist())
    sample_idx = 0
    t0 = time.time()
    for step in range(1, N_MAX + 1):
        step_fn(a, b, c, rng, step)
        if step in sample_set:
            proj = projections(a, b, c)
            for p in proj_names:
                l1[p][sample_idx] = proj[p]
            if sample_idx % 40 == 0 or step == N_MAX:
                dt = time.time() - t0
                print(f'  n={step:5d}  3D={proj["full_3d"]:.4e}  '
                      f'ab2D={proj["ab_2d"]:.4e}  a1D={proj["a_1d"]:.4e}  '
                      f'({step/max(dt,1e-9):.1f} s/s)', flush=True)
            sample_idx += 1
    print(f'  wall: {time.time()-t0:.1f}s')
    np.savez_compressed(out_path,
                        sample_times=SAMPLE_TIMES,
                        **{f'l1_{p}': l1[p] for p in proj_names},
                        meta_L=np.int32(L),
                        meta_N=np.int64(N_WALKERS),
                        meta_seed=np.int64(seed),
                        meta_walk=np.str_(walk_name))
    print(f'  -> {out_path}')


def main():
    print(f'ℤ³ torus full vs alt at L={L}')
    run('full', step_z3_full, SEED_BASE + 1,
        os.path.join(OUT_DIR, 'z3_full.npz'))
    run('alt', step_z3_alt, SEED_BASE + 2,
        os.path.join(OUT_DIR, 'z3_alt.npz'))
    print('\n=== ℤ³ torus sim complete ===')


if __name__ == '__main__':
    main()
