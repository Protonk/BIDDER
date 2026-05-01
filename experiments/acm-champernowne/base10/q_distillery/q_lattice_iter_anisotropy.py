"""
q_lattice_iter_anisotropy.py - lag-correlation test for the iter_10 attractor.

Computes Pearson correlation of iter_10 with itself shifted by lag L in
four directions (x, y, +diag, -diag), for L in {1, 2, 4, 8, 16, 32}.

Compared against a matched Gaussian (same mean / std). With ~16 M
elements, the per-lag noise floor is ~2.5e-4, so correlations above
that are real spatial structure.

Anisotropy check: do different directions disagree at the same lag?
"""

import os
import numpy as np


HERE = os.path.dirname(os.path.abspath(__file__))


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
    iter10 = np.load(os.path.join(HERE, 'q_lattice_iter_10.npy'))
    print(f'iter_10: shape {iter10.shape}  '
          f'mean {iter10.mean():.4f}  std {iter10.std():.4f}')

    rng = np.random.default_rng(42)
    gauss = rng.normal(
        loc=iter10.mean(), scale=iter10.std(), size=iter10.shape,
    ).astype(np.float32)

    lags = [1, 2, 4, 8, 16, 32]
    directions = [
        ('x       (0, +L)', 0, 1),
        ('y       (+L, 0)', 1, 0),
        ('+diag  (+L, +L)', 1, 1),
        ('-diag  (+L, -L)', 1, -1),
    ]

    n_eff = (iter10.shape[0] - 1) * (iter10.shape[1] - 1)
    noise_floor = 1.0 / np.sqrt(n_eff)
    print(f'\nnoise floor (1/sqrt(N_overlap)) ~= {noise_floor:.2e}\n')

    print('=== iter_10 lag correlations ===')
    print(f'{"":>20} ' + ' '.join(f'{f"L={L}":>11}' for L in lags))
    for name, dy_unit, dx_unit in directions:
        row = []
        for L in lags:
            c = lag_corr(iter10, dy_unit * L, dx_unit * L)
            row.append(f'{c:>+11.5f}')
        print(f'{name:>20} ' + ' '.join(row))

    print('\n=== matched Gaussian (control) ===')
    print(f'{"":>20} ' + ' '.join(f'{f"L={L}":>11}' for L in lags))
    for name, dy_unit, dx_unit in directions:
        row = []
        for L in lags:
            c = lag_corr(gauss, dy_unit * L, dx_unit * L)
            row.append(f'{c:>+11.5f}')
        print(f'{name:>20} ' + ' '.join(row))


if __name__ == '__main__':
    main()
