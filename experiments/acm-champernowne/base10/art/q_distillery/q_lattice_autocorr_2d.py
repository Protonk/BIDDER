"""
q_lattice_autocorr_2d.py - 2D autocorrelation maps for h = 5, 6, 7, 8.

For each rank, compute the full 2D autocorrelation of slog(lattice) via
FFT, extract the central window (lag dy, dx in [-31, 31]), and render
as a 4-panel grid. Every (dy, dx) is its own pixel — no angular or
radial discretization. Whatever structure the substrate has at small
lags is visible at single-pixel resolution.

If the parity alternation we saw in the 16-angle probe is the whole
story, the 4 panels should split into two visual classes (odd-row
shape vs even-row shape) by gross morphology and not show any finer
structure inside.

If there is finer structure — rays of correlation at off-axial angles,
periodic spots from gcd structures, anomalous diagonals — the 2D maps
will show them as features the angular probe was averaging over.

Uses cached lattices.
"""

import os
import time

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


HERE = os.path.dirname(os.path.abspath(__file__))
H_VALUES = [5, 6, 7, 8]
WINDOW = 31  # show lags from -31 to +31


def slog(arr, lt=1.0):
    arr = np.asarray(arr, dtype=float)
    return np.sign(arr) * np.log10(1.0 + np.abs(arr) / lt)


def autocorr_2d(img):
    """Pearson autocorrelation map via FFT, fftshifted so zero-lag at
    center."""
    img = img.astype(np.float64)
    img = img - img.mean()
    var = (img * img).sum()
    if var == 0:
        return np.zeros_like(img)
    F = np.fft.fft2(img)
    autocorr = np.real(np.fft.ifft2(np.abs(F) ** 2)) / var
    return np.fft.fftshift(autocorr)


def make_div_cmap():
    return LinearSegmentedColormap.from_list('q_div', [
        (0.00, (0.55, 1.00, 1.00)),
        (0.18, (0.30, 0.55, 0.95)),
        (0.38, (0.20, 0.25, 0.45)),
        (0.50, (0.04, 0.04, 0.05)),
        (0.62, (0.42, 0.28, 0.14)),
        (0.82, (1.00, 0.55, 0.20)),
        (1.00, (1.00, 0.92, 0.45)),
    ], N=512)


def main():
    print('Loading lattices and computing 2D autocorrelations...')
    autocorrs = {}
    centers = {}
    windows = {}
    for h in H_VALUES:
        cache = os.path.join(HERE, f'q_lattice_4000_h{h}.npy')
        if not os.path.exists(cache):
            print(f'  no cache for h={h}; skipping')
            continue
        t0 = time.time()
        grid = np.load(cache)
        img = slog(grid).astype(np.float64)
        ac = autocorr_2d(img)
        cy, cx = ac.shape[0] // 2, ac.shape[1] // 2
        win = ac[cy - WINDOW:cy + WINDOW + 1,
                 cx - WINDOW:cx + WINDOW + 1].copy()
        autocorrs[h] = ac
        centers[h] = (cy, cx)
        windows[h] = win
        # Some statistics
        print(f'  h={h}: {time.time() - t0:.1f}s   '
              f'center value = {ac[cy, cx]:.4f}   '
              f'window range = [{win.min():.3f}, {win.max():.3f}]')

    # ---- Render 4-panel grid ----
    cmap = make_div_cmap()

    fig = plt.figure(figsize=(15, 14), facecolor='#0a0a0a', dpi=180)

    # Determine shared color scale (excluding center pixel which is 1.0)
    # Use 99th percentile of |off-center| values for vmax
    all_off_center = []
    for h, win in windows.items():
        cy, cx = win.shape[0] // 2, win.shape[1] // 2
        masked = win.copy()
        masked[cy, cx] = 0
        all_off_center.append(np.abs(masked).ravel())
    pooled = np.concatenate(all_off_center)
    vmax = float(np.percentile(pooled, 99.5))
    print(f'\n  shared color vmax = {vmax:.3f} (p99.5 of off-center |corr|)')

    panel_positions = [
        (0.05, 0.55, 0.42, 0.40),
        (0.53, 0.55, 0.42, 0.40),
        (0.05, 0.08, 0.42, 0.40),
        (0.53, 0.08, 0.42, 0.40),
    ]

    for h, (left, bot, w, hgt) in zip(H_VALUES, panel_positions):
        if h not in windows:
            continue
        ax = fig.add_axes([left, bot, w, hgt], facecolor='#0a0a0a')
        win = windows[h]
        cy, cx = win.shape[0] // 2, win.shape[1] // 2
        im = ax.imshow(
            win, origin='lower',
            extent=[-WINDOW - 0.5, WINDOW + 0.5,
                    -WINDOW - 0.5, WINDOW + 0.5],
            cmap=cmap, vmin=-vmax, vmax=vmax,
            interpolation='nearest', aspect='equal',
        )
        # Center marker
        ax.plot(0, 0, marker='+', ms=10,
                markeredgecolor=(1.0, 1.0, 1.0, 0.55),
                markeredgewidth=1.0)
        # Concentric reference circles at radii 4, 8, 16, 31
        for r in [4, 8, 16, 31]:
            theta = np.linspace(0, 2 * np.pi, 200)
            ax.plot(r * np.cos(theta), r * np.sin(theta),
                    color=(1.0, 1.0, 1.0, 0.10), lw=0.5)
        # Cardinal axis lines
        ax.axhline(0, color=(1.0, 1.0, 1.0, 0.10), lw=0.5)
        ax.axvline(0, color=(1.0, 1.0, 1.0, 0.10), lw=0.5)

        ax.set_xlim(-WINDOW - 0.5, WINDOW + 0.5)
        ax.set_ylim(-WINDOW - 0.5, WINDOW + 0.5)
        ax.set_title(
            f'h = {h}  ({"even" if h % 2 == 0 else "odd"})',
            color=(0.96, 0.97, 1.00, 0.95), fontsize=13, pad=8,
        )
        ax.set_xlabel('lag dx', color=(0.85, 0.88, 0.92, 0.85),
                      fontsize=10)
        ax.set_ylabel('lag dy', color=(0.85, 0.88, 0.92, 0.85),
                      fontsize=10)
        ax.tick_params(colors=(0.78, 0.82, 0.88, 0.78), labelsize=8)
        for spine in ax.spines.values():
            spine.set_color((0.40, 0.45, 0.50, 0.40))

    # Shared colorbar
    cbar_ax = fig.add_axes([0.97, 0.10, 0.012, 0.80],
                           facecolor='#0a0a0a')
    fig.colorbar(im, cax=cbar_ax)
    cbar_ax.set_ylabel('Pearson autocorrelation',
                       color=(0.85, 0.88, 0.92, 0.85), fontsize=9)
    cbar_ax.tick_params(colors=(0.78, 0.82, 0.88, 0.85), labelsize=8)

    fig.text(0.5, 0.99,
             '2D autocorrelation maps  ·  central window dy, dx ∈ [−31, +31]',
             ha='center', va='top', fontsize=14, fontweight='bold',
             color=(1.0, 1.0, 1.0, 0.95), family='serif')
    fig.text(0.5, 0.965,
             'no angular discretization  ·  every (dy, dx) is one pixel  ·  '
             'reference rings at r = 4, 8, 16, 31',
             ha='center', va='top', fontsize=10, fontstyle='italic',
             color=(0.85, 0.88, 0.92, 0.65))

    out = os.path.join(HERE, 'q_lattice_autocorr_2d.png')
    plt.savefig(out, facecolor='#0a0a0a', dpi=180, bbox_inches='tight',
                pad_inches=0.15)
    plt.close()
    sz = os.path.getsize(out) / 1024
    print(f'\n-> {os.path.basename(out)}  ({sz:.0f} KB)')


if __name__ == '__main__':
    main()
