"""
q_lattice_4000_h_regen.py — regenerate q_lattice_4000_h{5,6,7,8}.npy
using the exact-rational evaluator algebra/predict_q.q_general
(Fraction → float64 only at write time).

Replaces the float-arithmetic generation that suffers cancellation
loss at high-h boundary cells. Empirically, h=8 boundary cells
(Ω(k') = h_eff at single-prime cofactors q^e) drift ~2e-12 from
their exact value 1/9, ~80,000 ULP — the master expansion
alternating sum has individual terms reaching 10^5 in magnitude
and cancels to 10^-1, and float64 cannot hold that contract.

Output dtype is float64 to match the existing cache. Other dtypes
(float32, bfloat16, custom software floats) are a single line
change at the np.array(..., dtype=...) call site if needed for
regularization probes.

Usage:
    sage -python q_lattice_4000_h_regen.py

Requires numpy (available via sage per AGENTS.md).
"""

import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
# HERE = .../q_distillery; walk up to BIDDER root.
REPO = HERE
for _ in range(4):  # q_distillery -> base10 -> acm-champernowne -> experiments -> BIDDER
    REPO = os.path.dirname(REPO)
sys.path.insert(0, os.path.join(REPO, 'algebra'))

from predict_q import q_general  # noqa: E402

N_MAX = 4000
K_MAX = 4000
HEIGHTS = (5, 6, 7, 8)
OUT_DTYPE = np.float64


def regenerate_grid(h: int, n_max: int = N_MAX, k_max: int = K_MAX,
                    out_dtype=OUT_DTYPE) -> np.ndarray:
    """Compute the (n=2..n_max, k=1..k_max) grid at height h via q_general
    in exact Fraction, converting to out_dtype at the final assignment."""
    n_rows = n_max - 1
    grid = np.zeros((n_rows, k_max), dtype=out_dtype)
    t0 = time.time()
    log_every = max(1, n_rows // 20)
    for ni, n in enumerate(range(2, n_max + 1)):
        for ki, k in enumerate(range(1, k_max + 1)):
            grid[ni, ki] = float(q_general(n, h, k))
        if (ni + 1) % log_every == 0:
            elapsed = time.time() - t0
            frac = (ni + 1) / n_rows
            eta = elapsed * (1 / frac - 1)
            print(f'  row {ni + 1}/{n_rows}  '
                  f'{100 * frac:5.1f}%   {elapsed:6.1f}s elapsed   '
                  f'ETA {eta:6.1f}s', flush=True)
    return grid


def main():
    for h in HEIGHTS:
        path = os.path.join(HERE, f'q_lattice_4000_h{h}.npy')
        bak = os.path.join(HERE, f'q_lattice_4000_h{h}.float_buggy.bak.npy')
        if os.path.exists(path) and not os.path.exists(bak):
            os.rename(path, bak)
            print(f'h={h}: backed up existing -> {os.path.basename(bak)}')

        print(f'h={h}: regenerating {N_MAX - 1} x {K_MAX} grid '
              f'(dtype={OUT_DTYPE.__name__}) via q_general...')
        t0 = time.time()
        grid = regenerate_grid(h)
        elapsed = time.time() - t0

        zeros = int((grid == 0).sum())
        print(f'  total: {elapsed:.1f}s   '
              f'Q in [{grid.min():.3g}, {grid.max():.3g}]   '
              f'zeros: {zeros} / {grid.size} ({100 * zeros / grid.size:.2f}%)')

        np.save(path, grid)
        print(f'  saved -> {os.path.basename(path)} '
              f'({os.path.getsize(path) / 1e6:.1f} MB)')
        print()


if __name__ == '__main__':
    main()
