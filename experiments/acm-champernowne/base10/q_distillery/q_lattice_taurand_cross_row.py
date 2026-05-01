"""
q_lattice_taurand_cross_row.py - test hypothesis 1 from the web agent.

Within-row tau-randomization permuted each row of the (n, k) lattice
independently. If same-shape rows still carry pairwise correlation
above the independent-permutation baseline, there's cross-row coherence
within shape classes that doesn't go through tau-signature alignment.

Test: compute pairwise Pearson correlation between rows of the
tau-randomized lattice. Stratify by:
  - same shape vs different shape
  - row distance (adjacent vs further)

Compare against a Gaussian-noise control (each row independent
random; pair correlations should center on 0 with std ~ 1/sqrt(K)).

If same-shape pairs are elevated above different-shape pairs by more
than baseline noise, shape-class identity carries arithmetic content
beyond categorical-functional dependence.
"""

import os
import time
from functools import lru_cache
from itertools import combinations

import numpy as np


HERE = os.path.dirname(os.path.abspath(__file__))


@lru_cache(maxsize=None)
def factor_tuple(n):
    if n < 1:
        raise ValueError(f'n must be >= 1, got {n}')
    if n == 1:
        return ()
    out = []
    r = n
    p = 2
    while p * p <= r:
        if r % p == 0:
            e = 0
            while r % p == 0:
                e += 1
                r //= p
            out.append((p, e))
        p += 1 if p == 2 else 2
    if r > 1:
        out.append((r, 1))
    return tuple(out)


def shape(n):
    return tuple(sorted([e for _p, e in factor_tuple(n)], reverse=True))


def pearson_row(a, b):
    """Pearson correlation of two 1D arrays."""
    a = a.astype(np.float64)
    b = b.astype(np.float64)
    a = a - a.mean()
    b = b - b.mean()
    norm = np.sqrt(np.dot(a, a) * np.dot(b, b))
    if norm == 0:
        return 0.0
    return float(np.dot(a, b) / norm)


def main():
    cache = os.path.join(HERE, 'q_lattice_taurand.npy')
    print('Loading tau-randomized lattice...')
    grid = np.load(cache)
    n_rows, n_cols = grid.shape
    print(f'  shape {grid.shape}')

    # Build shape -> list of row indices map.
    # Row i in the array corresponds to n = i + 2.
    shape_to_rows = {}
    for i in range(n_rows):
        s = shape(i + 2)
        shape_to_rows.setdefault(s, []).append(i)

    # Print shape class sizes.
    print('\nshape class sizes (top 10 by count):')
    sorted_shapes = sorted(shape_to_rows.items(),
                           key=lambda kv: -len(kv[1]))
    for s, rows in sorted_shapes[:10]:
        print(f'  {str(s):>20}: {len(rows):>4} rows')

    # ----- adjacent-pair test -----
    print('\n=== Adjacent pair (n, n+1) correlations ===')
    same_shape_corrs = []
    diff_shape_corrs = []
    for i in range(n_rows - 1):
        row_a = grid[i]
        row_b = grid[i + 1]
        c = pearson_row(row_a, row_b)
        if shape(i + 2) == shape(i + 3):
            same_shape_corrs.append(c)
        else:
            diff_shape_corrs.append(c)

    print(f'  same-shape adjacent  pairs: {len(same_shape_corrs):>4}  '
          f'mean corr = {np.mean(same_shape_corrs):+.5f}  '
          f'std = {np.std(same_shape_corrs):.5f}')
    print(f'  diff-shape adjacent  pairs: {len(diff_shape_corrs):>4}  '
          f'mean corr = {np.mean(diff_shape_corrs):+.5f}  '
          f'std = {np.std(diff_shape_corrs):.5f}')

    # ----- random-pair-within-shape test -----
    print('\n=== Random within-shape pair correlations ===')
    rng = np.random.default_rng(42)
    print(f'  {"shape":>20}  {"n_pairs":>8}  {"mean":>10}  {"std":>10}')
    same_shape_pool = []
    for s, rows in sorted_shapes:
        if len(rows) < 2:
            continue
        # Sample up to 200 pairs per shape class.
        all_pairs = list(combinations(rows, 2))
        if len(all_pairs) > 200:
            idx = rng.choice(len(all_pairs), 200, replace=False)
            pairs = [all_pairs[i] for i in idx]
        else:
            pairs = all_pairs
        cs = [pearson_row(grid[i], grid[j]) for i, j in pairs]
        same_shape_pool.extend(cs)
        if len(rows) >= 3:
            print(f'  {str(s):>20}  {len(pairs):>8}  '
                  f'{np.mean(cs):>+10.5f}  {np.std(cs):>10.5f}')

    # Random different-shape pairs (control).
    print('\n=== Random different-shape pair correlations (control) ===')
    diff_shape_pool = []
    n_samples = 1000
    while len(diff_shape_pool) < n_samples:
        i, j = rng.integers(0, n_rows, size=2)
        if i == j:
            continue
        if shape(i + 2) != shape(j + 2):
            diff_shape_pool.append(pearson_row(grid[i], grid[j]))
    print(f'  n_pairs = {len(diff_shape_pool)}  '
          f'mean corr = {np.mean(diff_shape_pool):+.5f}  '
          f'std = {np.std(diff_shape_pool):.5f}')

    # ----- summary -----
    print('\n=== summary ===')
    print(f'  same-shape pool:  n = {len(same_shape_pool):>5}  '
          f'mean = {np.mean(same_shape_pool):+.5f}  '
          f'std = {np.std(same_shape_pool):.5f}')
    print(f'  diff-shape pool:  n = {len(diff_shape_pool):>5}  '
          f'mean = {np.mean(diff_shape_pool):+.5f}  '
          f'std = {np.std(diff_shape_pool):.5f}')

    # Statistical test: is same-shape mean significantly different from
    # diff-shape mean?
    diff = np.mean(same_shape_pool) - np.mean(diff_shape_pool)
    se = np.sqrt(np.var(same_shape_pool) / len(same_shape_pool) +
                 np.var(diff_shape_pool) / len(diff_shape_pool))
    z = diff / se if se > 0 else 0
    print(f'\n  same - diff = {diff:+.5f}   SE = {se:.5f}   z = {z:.2f}')
    if abs(z) > 3:
        print('  -> SIGNIFICANT separation: shape carries cross-row info '
              'beyond categorical-functional dependence')
    elif abs(z) > 2:
        print('  -> marginal separation (2-3 sigma)')
    else:
        print('  -> not significantly different from independent-permutation '
              'baseline')


if __name__ == '__main__':
    main()
