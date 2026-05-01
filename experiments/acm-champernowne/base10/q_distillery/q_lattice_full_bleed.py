"""
q_lattice_full_bleed.py - two full-bleed images, no chrome.

Image 1: 2x2 mosaic of the (n, k) Q lattice at sizes [60, 120, 240, 480],
shared color scale, no axes / labels / titles.

Image 2: single 2000 x 2000 grid, full bleed.

Both render Q_n(n^h * k) at h = 5 via the general master expansion
(handles gcd(k, n) > 1 by extending exact height to h + nu_n(k)).
Diverging colormap with pure black at Q = 0.
"""

import os
import time
from functools import lru_cache
from math import comb

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


HERE = os.path.dirname(os.path.abspath(__file__))
H = 5


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


def q_general(n, h, k):
    n_facts = factor_tuple(n)
    if not n_facts:
        return 0.0
    k_facts = factor_tuple(k)
    k_dict = dict(k_facts)
    nu_n_k = min((k_dict.get(p, 0) // a) for p, a in n_facts)
    h_eff = h + nu_n_k
    n_prime_set = set(p for p, _ in n_facts)
    Q = 0.0
    for j in range(1, h_eff + 1):
        tau = 1
        for p, a in n_facts:
            e_p = k_dict.get(p, 0)
            exp_in_x = (h - j) * a + e_p
            tau *= comb(exp_in_x + j - 1, j - 1)
        for kp, ke in k_facts:
            if kp not in n_prime_set:
                tau *= comb(ke + j - 1, j - 1)
        sign = 1 if j % 2 == 1 else -1
        Q += sign * tau / j
    return Q


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


def make_grid(n_max, k_max, h=H):
    n_rows = n_max - 1
    grid = np.zeros((n_rows, k_max), dtype=float)
    for ni, n in enumerate(range(2, n_max + 1)):
        for ki, k in enumerate(range(1, k_max + 1)):
            grid[ni, ki] = q_general(n, h, k)
    return grid


def render_mosaic(sizes, out_path, fig_inches=20, dpi=200):
    grids = []
    for s in sizes:
        t0 = time.time()
        g = make_grid(s, s)
        print(f'  mosaic size={s}: compute {time.time() - t0:.2f}s   '
              f'Q in [{g.min():.3g}, {g.max():.3g}]')
        grids.append(g)

    smax = max(float(np.abs(slog(g)).max()) for g in grids)
    cmap = make_cmap()

    fig = plt.figure(figsize=(fig_inches, fig_inches),
                     dpi=dpi, facecolor='black')

    # 2x2 layout, each subplot fills its quadrant exactly.
    positions = [
        (0.0, 0.5, 0.5, 0.5),  # top-left   (60)
        (0.5, 0.5, 0.5, 0.5),  # top-right  (120)
        (0.0, 0.0, 0.5, 0.5),  # bot-left   (240)
        (0.5, 0.0, 0.5, 0.5),  # bot-right  (480)
    ]

    for grid, pos in zip(grids, positions):
        ax = fig.add_axes(pos)
        ax.imshow(slog(grid), origin='lower', aspect='auto',
                  cmap=cmap, vmin=-smax, vmax=smax,
                  interpolation='nearest')
        ax.set_axis_off()

    fig.savefig(out_path, facecolor='black', dpi=dpi, pad_inches=0)
    plt.close(fig)


def render_full(grid, out_path, fig_inches=24, dpi=200):
    smax = float(max(np.abs(slog(grid)).max(), 1.0))
    cmap = make_cmap()

    fig = plt.figure(figsize=(fig_inches, fig_inches),
                     dpi=dpi, facecolor='black')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(slog(grid), origin='lower', aspect='auto',
              cmap=cmap, vmin=-smax, vmax=smax,
              interpolation='nearest')
    ax.set_axis_off()
    fig.savefig(out_path, facecolor='black', dpi=dpi, pad_inches=0)
    plt.close(fig)


def main():
    # Image 1: 2x2 mosaic.
    print('Image 1: mosaic [60, 120, 240, 480]')
    out1 = os.path.join(HERE, 'q_lattice_mosaic.png')
    t0 = time.time()
    render_mosaic([60, 120, 240, 480], out1)
    print(f'  total: {time.time() - t0:.2f}s   '
          f'-> {os.path.basename(out1)}  '
          f'({os.path.getsize(out1) / 1024:.0f} KB)')
    print()

    # Image 2: full 2000 x 2000.
    print('Image 2: full-bleed 2000 x 2000')
    t0 = time.time()
    grid = make_grid(2000, 2000)
    print(f'  compute: {time.time() - t0:.2f}s   '
          f'Q in [{grid.min():.3g}, {grid.max():.3g}]   '
          f'zero cells: {int((np.abs(grid) < 1e-9).sum())} '
          f'/ {grid.size} ({100 * int((np.abs(grid) < 1e-9).sum()) / grid.size:.2f}%)')

    out2 = os.path.join(HERE, 'q_lattice_2000.png')
    t0 = time.time()
    render_full(grid, out2)
    print(f'  render: {time.time() - t0:.2f}s   '
          f'-> {os.path.basename(out2)}  '
          f'({os.path.getsize(out2) / 1024:.0f} KB)')


if __name__ == '__main__':
    main()
