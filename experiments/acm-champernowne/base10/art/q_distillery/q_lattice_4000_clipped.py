"""
q_lattice_4000_clipped.py - re-render the cached 4000 x 4000 grid with
percentile-clipped color scaling.

Loads the .npy cache from q_lattice_4000.py. Clips slog(Q) at the
specified percentile of |slog Q| (excluding exact zeros). Bulk dynamic
range gets the full diverging palette; rare extremes saturate at tips.

Renders three variants (p90, p95, p99) for comparison.
"""

import os
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


HERE = os.path.dirname(os.path.abspath(__file__))
FIG_INCHES = 40.0
DPI = 200


def slog(arr, lt=1.0):
    arr = np.asarray(arr, dtype=float)
    return np.sign(arr) * np.log10(1.0 + np.abs(arr) / lt)


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


def render_clipped(sgrid, out_path, threshold,
                   fig_inches=FIG_INCHES, dpi=DPI):
    cmap = make_cmap()
    fig = plt.figure(figsize=(fig_inches, fig_inches),
                     dpi=dpi, facecolor='black')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(sgrid, origin='lower', aspect='auto',
              cmap=cmap, vmin=-threshold, vmax=threshold,
              interpolation='nearest')
    ax.set_axis_off()
    fig.savefig(out_path, facecolor='black', dpi=dpi, pad_inches=0)
    plt.close(fig)


def main():
    cache_path = os.path.join(HERE, 'q_lattice_4000.npy')
    if not os.path.exists(cache_path):
        print(f'No cache at {cache_path}; run q_lattice_4000.py first.')
        return

    print('Loading cached grid...')
    t0 = time.time()
    grid = np.load(cache_path)
    print(f'  shape {grid.shape}, '
          f'Q in [{grid.min():.3g}, {grid.max():.3g}], '
          f'loaded in {time.time() - t0:.1f}s')

    sgrid = slog(grid)
    abs_slog = np.abs(sgrid)
    nonzero = abs_slog[abs_slog > 1e-9]
    smax_full = float(abs_slog.max())
    print(f'  full |slog| range: 0 .. {smax_full:.3f}')

    for p in [80]:
        threshold = float(np.percentile(nonzero, p))
        ratio = smax_full / threshold
        print(f'\nRendering p{p}: threshold = {threshold:.3f} '
              f'(clipping {ratio:.2f}x of dynamic range)')

        out = os.path.join(HERE, f'q_lattice_4000_p{p}.png')
        t0 = time.time()
        render_clipped(sgrid, out, threshold)
        print(f'  render: {time.time() - t0:.1f}s   '
              f'{os.path.getsize(out) / 1024 / 1024:.1f} MB   '
              f'-> {os.path.basename(out)}')


if __name__ == '__main__':
    main()
