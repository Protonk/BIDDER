"""
q_lattice_direct_angular.py - angular spectrum of the raw lattice.

No FFT. No iteration. Just compute lag correlations directly on slog
of the (n, k) Q-lattice at 16 angles, L = 1, 2, 4. Compare against the
distribution of angular spectra from multiple constgauss seeds at the
same probe.

The hypothesis: the FFT-mag-log iteration was imposing strong angular
structure of its own, masking substrate signal. Removing the iteration
gives the raw lattice's spatial-correlation structure directly.

What we want from the result: clear separation of original from
constgauss distribution. Substantively elevated correlations in some
angles (above the constgauss distribution's range), with sharp peaks
or clean directional preference.

If we DON'T see clean signal here, we have a problem: the lattice has
visible structure (we have rendered images of it), but spatial
correlations at small lags don't pick it up. That would suggest the
"structure" we see in renders is more about value-magnitude than
positional correlation.

Either result is informative.
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


def angular_corrs(img):
    """Return per-angle, per-lag correlation array (shape: 16 x 3)."""
    out = np.zeros((len(DIRECTIONS), len(LAGS)))
    for i, (dy_u, dx_u) in enumerate(DIRECTIONS):
        for j, L in enumerate(LAGS):
            out[i, j] = lag_corr(img, dy_u * L, dx_u * L)
    return out


def angular_sums(img):
    out = angular_corrs(img)
    return np.abs(out).sum(axis=1)


def main():
    cache = os.path.join(HERE, 'q_lattice_4000.npy')
    print('Loading lattice...')
    grid = np.load(cache).astype(np.float64)

    print('\nComputing angular spectrum of slog(original lattice)...')
    t0 = time.time()
    img_orig = slog(grid).astype(np.float32)
    sums_orig = angular_sums(img_orig)
    corrs_orig = angular_corrs(img_orig)
    print(f'  {time.time() - t0:.1f}s')

    # Constgauss baseline distribution
    N_SEEDS = 12
    seeds = list(range(2000, 2000 + N_SEEDS))
    print(f'\nConstgauss baseline ({N_SEEDS} seeds)...')
    cg_sums = np.zeros((N_SEEDS, len(DIRECTIONS)))
    for i, seed in enumerate(seeds):
        t0 = time.time()
        g = constgauss_input(grid, seed)
        img_cg = slog(g).astype(np.float32)
        cg_sums[i] = angular_sums(img_cg)
        print(f'  seed {seed}: total |corr|={cg_sums[i].sum():.5f}  '
              f'[{time.time() - t0:.1f}s]')

    # ----- Per-angle comparison -----
    print('\n=== Direct angular spectrum: original vs constgauss ===')
    print(f'{"angle°":>8}  {"(dy, dx)":>10}  {"original":>10}  '
          f'{"cg mean":>10}  {"cg std":>10}  {"z(orig)":>10}')
    cg_mean = cg_sums.mean(axis=0)
    cg_std = cg_sums.std(axis=0)
    for i, (dy, dx) in enumerate(DIRECTIONS):
        ang = degrees(atan2(dy, dx))
        z = (sums_orig[i] - cg_mean[i]) / max(cg_std[i], 1e-12)
        marker = ''
        if abs(z) > 5: marker = '   ***'
        elif abs(z) > 3: marker = '   **'
        elif abs(z) > 2: marker = '   *'
        print(f'{ang:>8.1f}  {str((dy, dx)):>10}  '
              f'{sums_orig[i]:>10.5f}  {cg_mean[i]:>10.5f}  '
              f'{cg_std[i]:>10.5f}  {z:>+10.2f}{marker}')

    # Sort by z
    print('\n=== Sorted by z (most-elevated angles first) ===')
    rows = sorted(
        enumerate(DIRECTIONS),
        key=lambda kv: -((sums_orig[kv[0]] - cg_mean[kv[0]]) /
                          max(cg_std[kv[0]], 1e-12)),
    )
    for i, (dy, dx) in rows:
        ang = degrees(atan2(dy, dx))
        z = (sums_orig[i] - cg_mean[i]) / max(cg_std[i], 1e-12)
        print(f'  angle {ang:>7.1f}°  z = {z:>+8.2f}  '
              f'(orig {sums_orig[i]:.5f} vs cg {cg_mean[i]:.5f} ± {cg_std[i]:.5f})')

    # Total budget
    print(f'\n=== total |corr| budget across 16 angles × 3 lags ===')
    cg_totals = cg_sums.sum(axis=1)
    print(f'  original:                  {sums_orig.sum():.5f}')
    print(f'  constgauss mean:           {cg_totals.mean():.5f}')
    print(f'  constgauss std:            {cg_totals.std():.5f}')
    print(f'  z(original vs cg total):   '
          f'{(sums_orig.sum() - cg_totals.mean()) / max(cg_totals.std(), 1e-12):+.2f}')

    # Per-lag breakdown for the highest-z angle
    top_idx = max(range(len(DIRECTIONS)),
                  key=lambda i: (sums_orig[i] - cg_mean[i]) /
                                 max(cg_std[i], 1e-12))
    dy, dx = DIRECTIONS[top_idx]
    ang = degrees(atan2(dy, dx))
    print(f'\n=== Per-lag breakdown at peak angle ({ang:.1f}°, '
          f'(dy, dx) = {(dy, dx)}) ===')
    print(f'{"L":>4}  {"original":>10}  {"sample cg":>10}')
    for j, L in enumerate(LAGS):
        c_o = corrs_orig[top_idx, j]
        # Estimate cg mean per-lag from one realization
        g_sample = constgauss_input(grid, seeds[0])
        c_c = lag_corr(slog(g_sample).astype(np.float32),
                       dy * L, dx * L)
        print(f'  L={L:>2}  {c_o:>+10.5f}  {c_c:>+10.5f}')


if __name__ == '__main__':
    main()
