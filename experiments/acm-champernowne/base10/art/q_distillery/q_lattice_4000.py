"""
q_lattice_4000.py - 4000 x 4000 full-bleed (n, k) Q lattice at h = 5.

Image: 8000 x 8000 px (2 px/cell), no chrome.
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
N_MAX = 4000
K_MAX = 4000
FIG_INCHES = 40.0
DPI = 200


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
    grid = np.zeros((n_rows, k_max), dtype=np.float32)
    log_every = max(1, n_rows // 20)
    t0 = time.time()
    for ni, n in enumerate(range(2, n_max + 1)):
        for ki, k in enumerate(range(1, k_max + 1)):
            grid[ni, ki] = q_general(n, h, k)
        if (ni + 1) % log_every == 0:
            elapsed = time.time() - t0
            frac = (ni + 1) / n_rows
            eta = elapsed * (1 / frac - 1)
            print(f'  row {ni + 1}/{n_rows}  '
                  f'{100 * frac:5.1f}%   {elapsed:6.1f}s elapsed   '
                  f'ETA {eta:6.1f}s', flush=True)
    return grid


def render_full(grid, out_path, fig_inches=FIG_INCHES, dpi=DPI):
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
    cache_path = os.path.join(HERE, 'q_lattice_4000.npy')

    if os.path.exists(cache_path):
        print(f'Loading cached grid from {os.path.basename(cache_path)}...')
        grid = np.load(cache_path)
        print(f'  shape {grid.shape}   '
              f'Q in [{grid.min():.3g}, {grid.max():.3g}]')
    else:
        print(f'Computing {N_MAX} x {K_MAX} grid at h = {H}...')
        t0 = time.time()
        grid = make_grid(N_MAX, K_MAX)
        print(f'compute total: {time.time() - t0:.1f}s   '
              f'Q in [{grid.min():.3g}, {grid.max():.3g}]')
        np.save(cache_path, grid)
        print(f'  cached -> {os.path.basename(cache_path)}')

    zeros = int((np.abs(grid) < 1e-9).sum())
    print(f'  zeros: {zeros} / {grid.size} '
          f'({100 * zeros / grid.size:.2f}%)')

    px = int(FIG_INCHES * DPI)
    print(f'Rendering at {FIG_INCHES}" x {DPI} dpi -> {px} x {px} px...')
    out = os.path.join(HERE, 'q_lattice_4000.png')
    t0 = time.time()
    render_full(grid, out)
    print(f'render: {time.time() - t0:.1f}s   '
          f'{os.path.getsize(out) / 1024 / 1024:.1f} MB   '
          f'-> {os.path.basename(out)}')


if __name__ == '__main__':
    main()
