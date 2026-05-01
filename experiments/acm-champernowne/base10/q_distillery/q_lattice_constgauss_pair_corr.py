"""
q_lattice_constgauss_pair_corr.py - the Mobius-result control.

Generate N constgauss inputs with different seeds. Run iter_5 on each.
Compute the 16-angle excess vector for each (against a fixed reference
constgauss baseline, seed 1729 — same as used in the Mobius test).

Then compute pairwise correlations between excess vectors across the
constgauss seeds. The resulting distribution of pair correlations is
the operator's intrinsic angular-shape correlation between two
random-input runs.

The Mobius test reported corr(orig - cg, mu - cg) = +0.703.
If the median pair correlation between two constgauss seeds is
near 0, the +0.703 is informative.
If the median is near +0.6+, the +0.703 is not informative — the
operator produces partly-correlated angular spectra for similar
inputs regardless of substrate content.
"""

import os
import time
from itertools import combinations
from math import atan2, degrees

import numpy as np


HERE = os.path.dirname(os.path.abspath(__file__))


def slog(arr, lt=1.0):
    arr = np.asarray(arr, dtype=float)
    return np.sign(arr) * np.log10(1.0 + np.abs(arr) / lt)


def fft_log_mag(img):
    centered = img - img.mean()
    F = np.fft.fftshift(np.fft.fft2(centered))
    return np.log10(np.abs(F) + 1.0).astype(np.float32)


def lag_corr(img, dy, dx):
    h, w = img.shape
    y_start_a = max(0, -dy)
    y_end_a = h + min(0, -dy)
    y_start_b = max(0, dy)
    y_end_b = h + min(0, dy)
    x_start_a = max(0, -dx)
    x_end_a = w + min(0, -dx)
    x_start_b = max(0, dx)
    x_end_b = w + min(0, dx)
    a = img[y_start_a:y_end_a, x_start_a:x_end_a].ravel().astype(np.float64)
    b = img[y_start_b:y_end_b, x_start_b:x_end_b].ravel().astype(np.float64)
    a = a - a.mean()
    b = b - b.mean()
    norm = np.sqrt(np.dot(a, a) * np.dot(b, b))
    if norm == 0:
        return 0.0
    return float(np.dot(a, b) / norm)


def iter_5_from_input(input_grid):
    img = slog(input_grid).astype(np.float32)
    for _ in range(5):
        img = fft_log_mag(img)
    return img


def constgauss_input(grid, seed):
    rng = np.random.default_rng(seed)
    glob_m = float(grid.mean())
    glob_s = float(grid.std())
    return rng.normal(loc=glob_m, scale=glob_s,
                      size=grid.shape).astype(grid.dtype)


DIRECTIONS = [
    (0, 1), (1, 3), (1, 2), (2, 3), (1, 1), (3, 2), (2, 1), (3, 1),
    (1, 0), (3, -1), (2, -1), (3, -2), (1, -1), (2, -3), (1, -2), (1, -3),
]
LAGS = [1, 2, 4]


def angular_sums(img):
    sums = []
    for dy_u, dx_u in DIRECTIONS:
        s = 0.0
        for L in LAGS:
            s += abs(lag_corr(img, dy_u * L, dx_u * L))
        sums.append(s)
    return np.array(sums)


def main():
    cache = os.path.join(HERE, 'q_lattice_4000.npy')
    print('Loading lattice...')
    grid = np.load(cache).astype(np.float64)

    # Reference constgauss with the same seed used in the Mobius test.
    print('\nReference constgauss (seed 1729) — used as baseline...')
    t0 = time.time()
    grid_ref = constgauss_input(grid, 1729)
    iter5_ref = iter_5_from_input(grid_ref)
    sums_ref = angular_sums(iter5_ref)
    print(f'  iter_5 + angles: {time.time() - t0:.1f}s')

    # Generate N constgauss runs with different seeds.
    N = 12  # 12 seeds (different from the 1729 reference)
    seeds = list(range(2000, 2000 + N))
    print(f'\nGenerating {N} test constgauss seeds and computing '
          f'angular excess vectors...')

    excess_vectors = []
    for i, seed in enumerate(seeds):
        t0 = time.time()
        g = constgauss_input(grid, seed)
        iter5 = iter_5_from_input(g)
        sums = angular_sums(iter5)
        excess = sums - sums_ref
        excess_vectors.append(excess)
        print(f'  seed {seed}: total |corr|={sums.sum():.5f}  '
              f'excess norm={np.linalg.norm(excess):.5f}  '
              f'[{time.time() - t0:.1f}s]')

    # Pairwise correlations between excess vectors.
    print(f'\nComputing pairwise correlations among {N} excess vectors '
          f'({N * (N - 1) // 2} pairs)...')
    pair_corrs = []
    for i, j in combinations(range(N), 2):
        a = excess_vectors[i]
        b = excess_vectors[j]
        if a.std() > 0 and b.std() > 0:
            c = float(np.corrcoef(a, b)[0, 1])
            pair_corrs.append(c)
    pair_corrs = np.array(pair_corrs)

    # Also: each excess vector vs its own self (sanity = 1.0)
    print(f'\n=== Pairwise correlation distribution ===')
    print(f'  n_pairs:  {len(pair_corrs)}')
    print(f'  mean:     {pair_corrs.mean():+.4f}')
    print(f'  median:   {np.median(pair_corrs):+.4f}')
    print(f'  std:      {pair_corrs.std():.4f}')
    print(f'  min:      {pair_corrs.min():+.4f}')
    print(f'  max:      {pair_corrs.max():+.4f}')
    print(f'  quartiles: '
          f'25%={np.percentile(pair_corrs, 25):+.4f}  '
          f'75%={np.percentile(pair_corrs, 75):+.4f}')

    print(f'\n=== Comparison ===')
    print(f'  Mobius vs original (single seed):     +0.703')
    print(f'  constgauss seed-pair median:          {np.median(pair_corrs):+.4f}')
    print(f'  constgauss seed-pair max:             {pair_corrs.max():+.4f}')

    if pair_corrs.max() < 0.4:
        print(f'\n  -> Mobius +0.703 is well above the random-input '
              f'pair-correlation distribution.')
        print(f'     Mobius preserved real angular shape that two '
              f'random-input runs do NOT share.')
    elif np.median(pair_corrs) > 0.5:
        print(f'\n  -> Two random-input runs typically correlate '
              f'highly. The +0.703 is likely operator-bias.')
    else:
        print(f'\n  -> Mobius +0.703 sits in the upper tail of the '
              f'random-input pair distribution.')
        print(f'     Suggestive but not decisive without '
              f'multi-seed Mobius bracketing.')


if __name__ == '__main__':
    main()
