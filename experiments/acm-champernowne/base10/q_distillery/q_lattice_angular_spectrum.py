"""
q_lattice_angular_spectrum.py - finer angular probe of the iter_5
anti-diagonal partial closure.

Tests 16 directions covering 0°-180° at lag magnitudes 1, 2, 4 (each
unit vector multiplied by L). For each direction, sums |corr| across
the three lags. Compares the original lattice's iter_5 against one
realisation of constgauss iter_5 as baseline.

Question: is the anti-diagonal partial closure at 135° a sharp peak
in the angular spectrum, a broad bump centred there, or part of a
broader elevation?
"""

import os
import time
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
    (0, 1),   # 0°
    (1, 3),   # 18.43°
    (1, 2),   # 26.57°
    (2, 3),   # 33.69°
    (1, 1),   # 45°
    (3, 2),   # 56.31°
    (2, 1),   # 63.43°
    (3, 1),   # 71.57°
    (1, 0),   # 90°
    (3, -1),  # 108.43°
    (2, -1),  # 116.57°
    (3, -2),  # 123.69°
    (1, -1),  # 135°  (anti-diagonal — the partial closure direction)
    (2, -3),  # 146.31°
    (1, -2),  # 153.43°
    (1, -3),  # 161.57°
]

LAGS = [1, 2, 4]


def angle_deg(dy, dx):
    return degrees(atan2(dy, dx))


def angular_sums(img):
    sums = []
    for dy_u, dx_u in DIRECTIONS:
        s = 0.0
        for L in LAGS:
            c = lag_corr(img, dy_u * L, dx_u * L)
            s += abs(c)
        sums.append(s)
    return sums


def main():
    cache = os.path.join(HERE, 'q_lattice_4000.npy')
    print('Loading lattice cache...')
    grid = np.load(cache)

    print('\nComputing iter_5 of original lattice...')
    t0 = time.time()
    iter5_orig = iter_5_from_input(grid)
    print(f'  {time.time() - t0:.1f}s')

    print('\nComputing iter_5 of constgauss (seed 1729) as baseline...')
    t0 = time.time()
    grid_cg = constgauss_input(grid, 1729)
    iter5_cg = iter_5_from_input(grid_cg)
    print(f'  {time.time() - t0:.1f}s')

    print('\nComputing angular spectrum...')
    t0 = time.time()
    sums_orig = angular_sums(iter5_orig)
    sums_cg = angular_sums(iter5_cg)
    print(f'  {time.time() - t0:.1f}s')

    print('\n=== Angular spectrum at iter_5 (sum |corr| across L = 1, 2, 4) ===')
    print(f'{"angle°":>8}  {"(dy, dx)":>10}  {"original":>10}  '
          f'{"constgauss":>12}  {"orig - cg":>12}')
    for (dy, dx), s_o, s_c in zip(DIRECTIONS, sums_orig, sums_cg):
        ang = angle_deg(dy, dx)
        diff = s_o - s_c
        tag = ''
        if abs(ang - 135) < 0.5:
            tag = '   <- anti-diagonal partial closure'
        elif abs(ang - 45) < 0.5:
            tag = '   (+ diag)'
        elif abs(ang - 90) < 0.5:
            tag = '   (vertical)'
        elif abs(ang - 0) < 0.5:
            tag = '   (horizontal)'
        print(f'{ang:>8.1f}  {str((dy, dx)):>10}  '
              f'{s_o:>10.5f}  {s_c:>12.5f}  {diff:>+12.5f}{tag}')

    # Sort by excess to see the shape of the spectrum
    print('\n=== Sorted by (orig - constgauss) descending ===')
    rows = sorted(zip(DIRECTIONS, sums_orig, sums_cg),
                  key=lambda x: -(x[1] - x[2]))
    print(f'{"rank":>4}  {"angle°":>8}  {"(dy, dx)":>10}  '
          f'{"orig - cg":>12}  {"ratio":>8}')
    for rank, ((dy, dx), s_o, s_c) in enumerate(rows, 1):
        ang = angle_deg(dy, dx)
        ratio = s_o / max(s_c, 1e-9)
        print(f'{rank:>4}  {ang:>8.1f}  {str((dy, dx)):>10}  '
              f'{s_o - s_c:>+12.5f}  {ratio:>8.2f}x')

    # Summary statistics: where do the elevations cluster?
    excess = np.array(sums_orig) - np.array(sums_cg)
    angles = np.array([angle_deg(dy, dx) for dy, dx in DIRECTIONS])

    print(f'\n=== Excess summary ===')
    print(f'  mean excess across all 16 angles: {excess.mean():+.5f}')
    print(f'  std  excess across all 16 angles:  {excess.std():.5f}')
    print(f'  max  excess: {excess.max():+.5f} at angle {angles[excess.argmax()]:.1f}°')
    print(f'  min  excess: {excess.min():+.5f} at angle {angles[excess.argmin()]:.1f}°')

    # Cluster check: is excess positive for angles near 135°?
    near_135 = np.abs(angles - 135) < 25  # angles within 25° of anti-diagonal
    print(f'\n  angles within 25° of 135°: {angles[near_135]}')
    print(f'    mean excess: {excess[near_135].mean():+.5f}')
    print(f'    n above zero: {int((excess[near_135] > 0).sum())} / {int(near_135.sum())}')

    far = ~near_135
    print(f'  angles outside ±25° of 135°: {angles[far]}')
    print(f'    mean excess: {excess[far].mean():+.5f}')
    print(f'    n above zero: {int((excess[far] > 0).sum())} / {int(far.sum())}')


if __name__ == '__main__':
    main()
