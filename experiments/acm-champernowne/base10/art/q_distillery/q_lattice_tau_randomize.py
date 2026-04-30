"""
q_lattice_tau_randomize.py - tau-signature randomization test.

For each row (fixed n), apply an independent random permutation of the
k-axis. This preserves row-marginal value distribution but destroys:
  - the (shape x tau-sig) -> Q functional dependence
  - gcd-vein periodicities (gcd>1 cells no longer at specific k positions)
  - prime-harmonic grid structure that iter_1 would normally produce

Then iterate FFT-magnitude-log to iter_5 and run the anisotropy test.
Compare against:
  - original iter_5: x=0.00204, y=0.00132, +diag=0.00147, -diag=0.00292
  - relabeled iter_5: identical to original (sigma is null transform)

Hypothesis: tau-randomization breaks the class structure that the
relabeling test confirmed is the entire content of the lattice. iter_5
anisotropy should drop substantially. If anti-diagonal preference
survives, it's about row-marginal distributions rather than
(shape x tau-sig) classification.

Also save iter_1 PNG of the randomized lattice for visual comparison
to the original prime-harmonic plaid.
"""

import os
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


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


def randomize_within_rows(grid, seed):
    rng = np.random.default_rng(seed)
    out = np.empty_like(grid)
    n_rows, n_cols = grid.shape
    for i in range(n_rows):
        perm = rng.permutation(n_cols)
        out[i] = grid[i, perm]
    return out


def make_cmap():
    colors = [
        (0.00, (0.55, 1.00, 1.00)),
        (0.18, (0.30, 0.55, 0.95)),
        (0.38, (0.20, 0.25, 0.45)),
        (0.50, (0.04, 0.04, 0.05)),
        (0.62, (0.42, 0.28, 0.14)),
        (0.82, (1.00, 0.55, 0.20)),
        (1.00, (1.00, 0.92, 0.45)),
    ]
    return LinearSegmentedColormap.from_list('q_div', colors, N=512)


def render_signed(img, out_path, fig_inches=15, dpi=150):
    sgrid = slog(img)
    smax = float(max(np.abs(sgrid).max(), 1.0))
    cmap = make_cmap()
    fig = plt.figure(figsize=(fig_inches, fig_inches), dpi=dpi, facecolor='black')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(sgrid, origin='lower', aspect='auto',
              cmap=cmap, vmin=-smax, vmax=smax,
              interpolation='nearest')
    ax.set_axis_off()
    fig.savefig(out_path, facecolor='black', dpi=dpi, pad_inches=0)
    plt.close(fig)


def render_inferno(img, out_path, fig_inches=15, dpi=150):
    lo = float(np.percentile(img, 2))
    hi = float(np.percentile(img, 99))
    fig = plt.figure(figsize=(fig_inches, fig_inches), dpi=dpi, facecolor='black')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(img, origin='lower', aspect='auto',
              cmap='inferno', vmin=lo, vmax=hi,
              interpolation='nearest')
    ax.set_axis_off()
    fig.savefig(out_path, facecolor='black', dpi=dpi, pad_inches=0)
    plt.close(fig)


def main():
    cache = os.path.join(HERE, 'q_lattice_4000.npy')
    print('Loading original lattice...')
    grid = np.load(cache)
    print(f'  shape {grid.shape}  '
          f'mean {grid.mean():.4f}  std {grid.std():.4f}')

    print(f'\nRandomizing within rows (seed {SEED})...')
    t0 = time.time()
    grid_re = randomize_within_rows(grid, SEED)
    print(f'  permute: {time.time() - t0:.2f}s')

    # Sanity: row marginals should be identical (just permuted columns)
    for i in [0, 100, 1000, 3000]:
        same = np.allclose(np.sort(grid[i]), np.sort(grid_re[i]))
        print(f'  row {i+2}: sorted values identical = {same}')

    # Global value distribution should also match (it's just rearranged).
    print(f'  global mean preserved: '
          f'{grid_re.mean():.4f} == {grid.mean():.4f}: '
          f'{np.isclose(grid_re.mean(), grid.mean())}')

    np.save(os.path.join(HERE, 'q_lattice_taurand.npy'), grid_re)

    # Render the randomized lattice itself (compare to original 'plaid').
    print('\nRendering randomized lattice (signed slog)...')
    out_lat = os.path.join(HERE, 'q_lattice_taurand.png')
    render_signed(grid_re, out_lat)
    print(f'  -> {os.path.basename(out_lat)} '
          f'({os.path.getsize(out_lat) / 1024 / 1024:.1f} MB)')

    # iter_1 of randomized lattice
    print('\nFFT-iterating randomized lattice...')
    t0 = time.time()
    img = slog(grid_re).astype(np.float32)
    iter1 = fft_log_mag(img)
    out_it1 = os.path.join(HERE, 'q_lattice_taurand_iter01.png')
    render_inferno(iter1, out_it1)
    print(f'  iter_1: {time.time() - t0:.2f}s   '
          f'-> {os.path.basename(out_it1)} '
          f'({os.path.getsize(out_it1) / 1024 / 1024:.1f} MB)')

    # Continue to iter_5
    img = iter1
    for i in range(2, 6):
        img = fft_log_mag(img)
    iter5 = img
    np.save(os.path.join(HERE, 'q_lattice_taurand_iter05.npy'), iter5)
    print(f'  iter_5 (taurand): mean {iter5.mean():.4f}  '
          f'std {iter5.std():.4f}')

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

    print('\n=== iter_5 TAURAND lag correlations ===')
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

    orig_sums = {
        'x       (0, +L)': 0.00204,
        'y       (+L, 0)': 0.00132,
        '+diag  (+L, +L)': 0.00147,
        '-diag  (+L, -L)': 0.00292,
    }

    print(f'\n=== comparison: ORIGINAL vs TAURAND iter_5 (sum |corr|) ===')
    print(f'{"direction":>20}  {"original":>10}  {"taurand":>10}  '
          f'{"gauss":>10}   {"orig/g":>10}  {"taurand/g":>10}')
    for name in sums_re:
        print(f'{name:>20}  '
              f'{orig_sums[name]:>10.5f}  '
              f'{sums_re[name]:>10.5f}  '
              f'{sums_g[name]:>10.5f}   '
              f'{orig_sums[name]/sums_g[name]:>10.2f}x  '
              f'{sums_re[name]/sums_g[name]:>10.2f}x')


if __name__ == '__main__':
    main()
