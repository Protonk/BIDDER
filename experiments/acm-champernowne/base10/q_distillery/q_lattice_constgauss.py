"""
q_lattice_constgauss.py - constant-marginal Gaussianization test.

Replace every cell of the lattice with an independent draw from a single
Gaussian matched to the global mean and std. This:

  - preserves the global first two moments
  - destroys per-row mean/std coherence between adjacent n
  - destroys all spatial structure
  - leaves an i.i.d. Gaussian field with the correct overall scale

If the conservation budget at iter_5 collapses to ~Gaussian baseline
(0.00338), then the entire residual after rowgauss was row-mean/std
coherence between adjacent rows.

If the budget stays elevated, there's a layer below row marginals
that even total Gaussianization doesn't reach. Most likely culprit:
the FFT iteration itself produces baseline isotropic correlations
from any input — call that the operator's intrinsic correlation level.

Either way the result narrows the structural budget's location.
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


def main():
    cache = os.path.join(HERE, 'q_lattice_4000.npy')
    print('Loading original lattice...')
    grid = np.load(cache)
    glob_m = float(grid.mean())
    glob_s = float(grid.std())
    print(f'  shape {grid.shape}  '
          f'global mean {glob_m:.4f}  global std {glob_s:.4f}')

    print(f'\nGlobal Gaussianizing all cells (seed {SEED})...')
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    grid_c = rng.normal(loc=glob_m, scale=glob_s,
                        size=grid.shape).astype(grid.dtype)
    print(f'  generate: {time.time() - t0:.2f}s')
    print(f'  result:    mean {grid_c.mean():.4f}  '
          f'std {grid_c.std():.4f}')

    # Sanity: per-row stats should now NOT match original (this is the point).
    for i in [0, 100, 1000, 3000]:
        m_o = grid[i].mean()
        s_o = grid[i].std()
        m_c = grid_c[i].mean()
        s_c = grid_c[i].std()
        print(f'  row {i+2}:  orig (m={m_o:+.3f}, s={s_o:.3f})  '
              f'constgauss (m={m_c:+.3f}, s={s_c:.3f})')

    np.save(os.path.join(HERE, 'q_lattice_constgauss.npy'), grid_c)

    # FFT iteration
    print('\nIterating FFT-mag-log to iter_5...')
    t0 = time.time()
    img = slog(grid_c).astype(np.float32)
    for i in range(1, 6):
        img = fft_log_mag(img)
    iter5 = img
    np.save(os.path.join(HERE, 'q_lattice_constgauss_iter05.npy'), iter5)
    print(f'  iter_5: {time.time() - t0:.1f}s   '
          f'mean {iter5.mean():.4f}  std {iter5.std():.4f}')

    # Anisotropy test
    rng2 = np.random.default_rng(42)
    gauss = rng2.normal(loc=iter5.mean(), scale=iter5.std(),
                        size=iter5.shape).astype(np.float32)

    lags = [1, 2, 4, 8, 16, 32]
    directions = [
        ('x       (0, +L)', 0, 1),
        ('y       (+L, 0)', 1, 0),
        ('+diag  (+L, +L)', 1, 1),
        ('-diag  (+L, -L)', 1, -1),
    ]
    n_eff = (iter5.shape[0] - 1) * (iter5.shape[1] - 1)
    print(f'\nnoise floor ~= {1 / np.sqrt(n_eff):.2e}')

    print('\n=== iter_5 CONSTGAUSS lag correlations ===')
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

    # Conservation summary
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
    rowgauss_sums = {
        'x       (0, +L)': 0.00097,
        'y       (+L, 0)': 0.00160,
        '+diag  (+L, +L)': 0.00266,
        '-diag  (+L, -L)': 0.00103,
    }

    total_orig = sum(orig_sums.values())
    total_taurand = sum(taurand_sums.values())
    total_rowgauss = sum(rowgauss_sums.values())
    total_re = sum(sums_re.values())
    total_g = sum(sums_g.values())

    print('\n=== budget conservation ladder ===')
    print(f'  original lattice:    sum |corr| = {total_orig:.5f}  '
          f'({total_orig/total_g:.2f}x Gaussian)')
    print(f'  tau-randomized:      sum |corr| = {total_taurand:.5f}  '
          f'({total_taurand/total_g:.2f}x Gaussian)')
    print(f'  rowgauss:            sum |corr| = {total_rowgauss:.5f}  '
          f'({total_rowgauss/total_g:.2f}x Gaussian)')
    print(f'  constgauss:          sum |corr| = {total_re:.5f}  '
          f'({total_re/total_g:.2f}x Gaussian)')
    print(f'  matched Gaussian:    sum |corr| = {total_g:.5f}  '
          f'(1.00x by definition)')

    if total_re < 1.10 * total_g:
        print('\n  -> CONSTGAUSS COLLAPSED TO BASELINE.')
        print('     Row mean/std coherence was carrying the entire residual budget.')
    elif total_re < 1.30 * total_g:
        print('\n  -> CONSTGAUSS dropped substantially toward baseline.')
        print('     Most of the residual was row-marginal coherence; small layer remains.')
    else:
        print('\n  -> CONSTGAUSS still elevated above baseline.')
        print('     A layer below row marginals continues to carry budget.')

    print('\n=== direction-by-direction comparison ===')
    print(f'{"direction":>20}  {"original":>10}  {"taurand":>10}  '
          f'{"rowgauss":>10}  {"constgauss":>11}  {"gauss":>10}')
    for name in sums_re:
        print(f'{name:>20}  '
              f'{orig_sums[name]:>10.5f}  '
              f'{taurand_sums[name]:>10.5f}  '
              f'{rowgauss_sums[name]:>10.5f}  '
              f'{sums_re[name]:>11.5f}  '
              f'{sums_g[name]:>10.5f}')


if __name__ == '__main__':
    main()
