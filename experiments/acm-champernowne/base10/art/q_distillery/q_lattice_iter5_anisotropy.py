"""
q_lattice_iter5_anisotropy.py - same lag-correlation test as
q_lattice_iter_anisotropy.py, applied to iter_5 rather than iter_10.

If the fixed-point attractor is fully settled by iter 3 (as the
iteration stats suggest), iter_5 should be statistically
indistinguishable from iter_10. Any difference would indicate the
"settled" claim is approximate, not exact.
"""

import os
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


def main():
    cache = os.path.join(HERE, 'q_lattice_4000.npy')
    grid = np.load(cache)

    img = slog(grid).astype(np.float32)
    print('Iterating to iter_5...')
    for i in range(1, 6):
        img = fft_log_mag(img)
    iter5 = img.copy()
    np.save(os.path.join(HERE, 'q_lattice_iter_05.npy'), iter5)

    print(f'iter_5: shape {iter5.shape}  '
          f'mean {iter5.mean():.4f}  std {iter5.std():.4f}  '
          f'range [{iter5.min():.3f}, {iter5.max():.3f}]')

    # Same RNG seed as iter_10 control for direct comparability.
    rng = np.random.default_rng(42)
    gauss = rng.normal(
        loc=iter5.mean(), scale=iter5.std(), size=iter5.shape,
    ).astype(np.float32)

    lags = [1, 2, 4, 8, 16, 32]
    directions = [
        ('x       (0, +L)', 0, 1),
        ('y       (+L, 0)', 1, 0),
        ('+diag  (+L, +L)', 1, 1),
        ('-diag  (+L, -L)', 1, -1),
    ]

    n_eff = (iter5.shape[0] - 1) * (iter5.shape[1] - 1)
    print(f'\nnoise floor (1/sqrt(N_overlap)) ~= {1.0 / np.sqrt(n_eff):.2e}\n')

    print('=== iter_5 lag correlations ===')
    print(f'{"":>20} ' + ' '.join(f'{f"L={L}":>11}' for L in lags))
    iter5_sums = {}
    for name, dy_unit, dx_unit in directions:
        row = []
        s = 0.0
        for L in lags:
            c = lag_corr(iter5, dy_unit * L, dx_unit * L)
            row.append(f'{c:>+11.5f}')
            s += abs(c)
        iter5_sums[name] = s
        print(f'{name:>20} ' + ' '.join(row))

    print('\n=== matched Gaussian (control, same seed as iter_10 run) ===')
    print(f'{"":>20} ' + ' '.join(f'{f"L={L}":>11}' for L in lags))
    gauss_sums = {}
    for name, dy_unit, dx_unit in directions:
        row = []
        s = 0.0
        for L in lags:
            c = lag_corr(gauss, dy_unit * L, dx_unit * L)
            row.append(f'{c:>+11.5f}')
            s += abs(c)
        gauss_sums[name] = s
        print(f'{name:>20} ' + ' '.join(row))

    print('\n=== sum |corr| across lags  (direction excess vs Gaussian) ===')
    print(f'{"direction":>20}  {"iter_5":>10}  {"Gaussian":>10}  '
          f'{"ratio":>8}')
    for name in iter5_sums:
        ratio = iter5_sums[name] / max(gauss_sums[name], 1e-12)
        print(f'{name:>20}  {iter5_sums[name]:>10.5f}  '
              f'{gauss_sums[name]:>10.5f}  {ratio:>8.2f}x')


if __name__ == '__main__':
    main()
