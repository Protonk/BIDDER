"""
q_lattice_rowgauss.py - per-row Gaussianization test.

For each row of the lattice, replace its 4000 values with independent
Gaussian draws matched to that row's mean and std. This:

  - preserves each row's first two moments (mean, std)
  - destroys distribution SHAPE (skewness, kurtosis, quantization)
  - destroys all positional structure within the row (independent draws)

The harder question this targets: is the conserved structural budget
just row-marginal mean/std, or does the bounded non-Gaussian shape of
the original Q distribution carry information?

Compare iter_5 sum |corr| against:
  - original lattice iter_5: 0.00775
  - tau-randomized iter_5:    0.00703
  - matched Gaussian baseline: ~0.00337

If rowgauss budget collapses to Gaussian baseline (~0.0034), then the
specific Q distribution shape beyond first two moments is the
load-bearer of the surviving correlation budget.

If rowgauss budget stays high (~0.007 or so), then row mean/std alone
suffice and we keep peeling.
"""

import os
import time
import numpy as np


HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 1729


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


def gaussianize_rows(grid, seed):
    rng = np.random.default_rng(seed)
    out = np.empty_like(grid)
    n_rows, n_cols = grid.shape
    for i in range(n_rows):
        m = float(grid[i].mean())
        s = float(grid[i].std())
        out[i] = rng.normal(loc=m, scale=s, size=n_cols).astype(grid.dtype)
    return out


def main():
    cache = os.path.join(HERE, 'q_lattice_4000.npy')
    print('Loading original lattice...')
    grid = np.load(cache)
    print(f'  shape {grid.shape}  '
          f'mean {grid.mean():.4f}  std {grid.std():.4f}')

    print(f'\nGaussianizing rows (seed {SEED})...')
    t0 = time.time()
    grid_g = gaussianize_rows(grid, SEED)
    print(f'  gaussianize: {time.time() - t0:.2f}s')

    # Sanity: per-row means/stds match between original and rowgauss.
    for i in [0, 100, 1000, 3000]:
        m_o = grid[i].mean()
        s_o = grid[i].std()
        m_g = grid_g[i].mean()
        s_g = grid_g[i].std()
        print(f'  row {i+2}:  orig (m={m_o:+.3f}, s={s_o:.3f})  '
              f'rowgauss (m={m_g:+.3f}, s={s_g:.3f})')

    np.save(os.path.join(HERE, 'q_lattice_rowgauss.npy'), grid_g)

    # FFT iteration
    print('\nIterating FFT-mag-log to iter_5...')
    t0 = time.time()
    img = slog(grid_g).astype(np.float32)
    for i in range(1, 6):
        img = fft_log_mag(img)
    iter5 = img
    np.save(os.path.join(HERE, 'q_lattice_rowgauss_iter05.npy'), iter5)
    print(f'  iter_5: {time.time() - t0:.1f}s   '
          f'mean {iter5.mean():.4f}  std {iter5.std():.4f}')

    # Anisotropy test
    rng2 = np.random.default_rng(42)
    gauss = rng2.normal(
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
    print(f'\nnoise floor ~= {1 / np.sqrt(n_eff):.2e}')

    print('\n=== iter_5 ROWGAUSS lag correlations ===')
    print(f'{"":>20} ' + ' '.join(f'{f"L={L}":>11}' for L in lags))
    sums_re = {}
    for name, dy_unit, dx_unit in directions:
        row = []
        s = 0.0
        for L in lags:
            c = lag_corr(iter5, dy_unit * L, dx_unit * L)
            row.append(f'{c:>+11.5f}')
            s += abs(c)
        sums_re[name] = s
        print(f'{name:>20} ' + ' '.join(row))

    print('\n=== matched Gaussian (control) ===')
    print(f'{"":>20} ' + ' '.join(f'{f"L={L}":>11}' for L in lags))
    sums_g = {}
    for name, dy_unit, dx_unit in directions:
        row = []
        s = 0.0
        for L in lags:
            c = lag_corr(gauss, dy_unit * L, dx_unit * L)
            row.append(f'{c:>+11.5f}')
            s += abs(c)
        sums_g[name] = s
        print(f'{name:>20} ' + ' '.join(row))

    # Conservation comparison.
    orig_sums = {
        'x       (0, +L)': 0.00204,
        'y       (+L, 0)': 0.00132,
        '+diag  (+L, +L)': 0.00147,
        '-diag  (+L, -L)': 0.00292,
    }
    taurand_sums = {
        'x       (0, +L)': 0.00175,
        'y       (+L, 0)': 0.00194,
        '+diag  (+L, +L)': 0.00197,
        '-diag  (+L, -L)': 0.00137,
    }

    total_orig = sum(orig_sums.values())
    total_taurand = sum(taurand_sums.values())
    total_re = sum(sums_re.values())
    total_g = sum(sums_g.values())

    print('\n=== budget conservation across transforms ===')
    print(f'  original lattice iter_5:   sum |corr| = {total_orig:.5f}  '
          f'(ratio to gauss = {total_orig/total_g:.2f}x)')
    print(f'  tau-rand iter_5:           sum |corr| = {total_taurand:.5f}  '
          f'(ratio to gauss = {total_taurand/total_g:.2f}x)')
    print(f'  rowgauss iter_5:           sum |corr| = {total_re:.5f}  '
          f'(ratio to gauss = {total_re/total_g:.2f}x)')
    print(f'  matched Gaussian:          sum |corr| = {total_g:.5f}')

    print('\n=== direction-by-direction comparison ===')
    print(f'{"direction":>20}  {"original":>10}  {"taurand":>10}  '
          f'{"rowgauss":>10}  {"gauss":>10}')
    for name in sums_re:
        print(f'{name:>20}  '
              f'{orig_sums[name]:>10.5f}  '
              f'{taurand_sums[name]:>10.5f}  '
              f'{sums_re[name]:>10.5f}  '
              f'{sums_g[name]:>10.5f}')


if __name__ == '__main__':
    main()
