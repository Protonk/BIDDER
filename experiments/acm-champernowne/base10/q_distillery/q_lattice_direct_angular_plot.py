"""
q_lattice_direct_angular_plot.py - render the direct angular spectrum.

Polar plot showing the raw lattice's 16-angle sum|corr| profile against
constgauss baseline. Plus an inset showing the per-lag (L = 1, 2, 4)
breakdown at the dominant 0° direction, which has the L=1 < L=4
anomaly worth flagging visually.

Dark background, warm = original, cool = constgauss, log radial scale
so both are simultaneously visible despite ~1000x magnitude gap.
"""

import os
import time
from math import atan2, degrees

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


HERE = os.path.dirname(os.path.abspath(__file__))


def slog(arr, lt=1.0):
    arr = np.asarray(arr, dtype=float)
    return np.sign(arr) * np.log10(1.0 + np.abs(arr) / lt)


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


def constgauss_input(grid, seed):
    rng = np.random.default_rng(seed)
    glob_m = float(grid.mean())
    glob_s = float(grid.std())
    return rng.normal(loc=glob_m, scale=glob_s,
                      size=grid.shape).astype(grid.dtype)


DIRECTIONS = [
    (0, 1), (1, 3), (1, 2), (2, 3), (1, 1), (3, 2), (2, 1), (3, 1),
    (1, 0), (3, -1), (2, -1), (3, -2), (1, -1), (2, -3), (1, -2), (1, -3),
]
LAGS = [1, 2, 4]


def angular_corrs(img):
    out = np.zeros((len(DIRECTIONS), len(LAGS)))
    for i, (dy_u, dx_u) in enumerate(DIRECTIONS):
        for j, L in enumerate(LAGS):
            out[i, j] = lag_corr(img, dy_u * L, dx_u * L)
    return out


def main():
    cache = os.path.join(HERE, 'q_lattice_4000.npy')
    print('Loading lattice...')
    grid = np.load(cache).astype(np.float64)

    print('Computing angular correlations on slog(original)...')
    t0 = time.time()
    img_orig = slog(grid).astype(np.float32)
    corrs_orig = angular_corrs(img_orig)
    sums_orig = np.abs(corrs_orig).sum(axis=1)
    print(f'  {time.time() - t0:.1f}s')

    print('Computing constgauss baseline (seed 1729)...')
    t0 = time.time()
    grid_cg = constgauss_input(grid, 1729)
    img_cg = slog(grid_cg).astype(np.float32)
    corrs_cg = angular_corrs(img_cg)
    sums_cg = np.abs(corrs_cg).sum(axis=1)
    print(f'  {time.time() - t0:.1f}s')

    angles_rad = np.array([np.arctan2(dy, dx) for dy, dx in DIRECTIONS])
    angles_deg = np.degrees(angles_rad)

    # Mirror to 360° so the polar plot looks full (lag corr is sign-symmetric:
    # corr(img, dy, dx) = corr(img, -dy, -dx), so each angle θ also has signal
    # at θ + 180°).
    angles_full = np.concatenate([angles_rad, angles_rad + np.pi])
    sums_orig_full = np.concatenate([sums_orig, sums_orig])
    sums_cg_full = np.concatenate([sums_cg, sums_cg])

    # Sort by angle for a clean closed curve.
    order = np.argsort(angles_full)
    angles_full = angles_full[order]
    sums_orig_full = sums_orig_full[order]
    sums_cg_full = sums_cg_full[order]
    # Close the curve by repeating the first point.
    angles_full = np.concatenate([angles_full, [angles_full[0] + 2 * np.pi]])
    sums_orig_full = np.concatenate([sums_orig_full, [sums_orig_full[0]]])
    sums_cg_full = np.concatenate([sums_cg_full, [sums_cg_full[0]]])

    # --- figure ---
    fig = plt.figure(figsize=(15, 9), facecolor='#0a0a0a', dpi=180)

    # Main polar plot (log radial)
    ax_pol = fig.add_axes([0.04, 0.05, 0.55, 0.90], polar=True,
                          facecolor='#0a0a0a')
    ax_pol.set_theta_zero_location('E')
    ax_pol.set_theta_direction(1)

    # Use log scale on r by transforming
    log_orig = np.log10(sums_orig_full + 1e-6)
    log_cg = np.log10(sums_cg_full + 1e-6)

    ax_pol.plot(angles_full, log_orig, color=(1.00, 0.66, 0.30, 0.95),
                lw=2.2, label='original lattice')
    ax_pol.fill(angles_full, log_orig,
                color=(1.00, 0.66, 0.30, 0.18))
    ax_pol.plot(angles_full, log_cg, color=(0.45, 0.78, 1.00, 0.95),
                lw=2.0, label='constgauss baseline (seed 1729)')
    ax_pol.fill(angles_full, log_cg,
                color=(0.45, 0.78, 1.00, 0.18))

    # Markers at each measured angle for original
    ax_pol.scatter(angles_rad, np.log10(sums_orig + 1e-6),
                   s=80, c=[(1.00, 0.84, 0.30, 1.0)],
                   edgecolors=[(0.0, 0.0, 0.0, 0.9)], linewidths=1.0,
                   zorder=5)
    ax_pol.scatter(angles_rad + np.pi, np.log10(sums_orig + 1e-6),
                   s=80, c=[(1.00, 0.84, 0.30, 1.0)],
                   edgecolors=[(0.0, 0.0, 0.0, 0.9)], linewidths=1.0,
                   zorder=5)

    # Set radial ticks (log scale)
    r_ticks = [-3, -2, -1, 0]
    r_tick_labels = [r'$10^{-3}$', r'$10^{-2}$', r'$10^{-1}$', r'$10^{0}$']
    ax_pol.set_yticks(r_ticks)
    ax_pol.set_yticklabels(r_tick_labels, color=(0.78, 0.82, 0.88, 0.88),
                           fontsize=9)
    ax_pol.set_ylim(-3.5, 0.5)

    # Angular ticks at canonical angles
    ax_pol.set_xticks(np.deg2rad([0, 45, 90, 135, 180, 225, 270, 315]))
    ax_pol.set_xticklabels(['0°', '45°', '90°', '135°', '180°',
                             '225°', '270°', '315°'],
                            color=(0.92, 0.95, 1.00, 0.92),
                            fontsize=11)

    ax_pol.tick_params(colors=(0.78, 0.82, 0.88, 0.78))
    ax_pol.grid(True, color=(0.30, 0.34, 0.38), alpha=0.30, lw=0.5)

    leg = ax_pol.legend(loc='lower center',
                        bbox_to_anchor=(0.5, -0.11),
                        ncol=2, fontsize=10, frameon=False,
                        labelcolor=(0.92, 0.95, 1.00, 1.0))

    ax_pol.set_title(
        '16-angle spatial correlation spectrum — slog(Q lattice), no FFT\n'
        r'$\sum|\mathrm{corr}|$ at lags $L \in \{1, 2, 4\}$  ·  log radial scale',
        color=(0.96, 0.97, 1.00, 0.95), fontsize=12, pad=22,
    )

    # --- right panel: lag-decay at 0° and 90° ---
    ax_lag = fig.add_axes([0.66, 0.55, 0.31, 0.38],
                          facecolor='#0a0a0a')
    # Original at 0° (idx 0) and 90° (idx 8)
    ax_lag.plot(LAGS, corrs_orig[0], 'o-',
                color=(1.00, 0.66, 0.30, 0.95), lw=2.0, ms=9,
                label='original 0° (horizontal)')
    ax_lag.plot(LAGS, corrs_orig[8], 's-',
                color=(1.00, 0.50, 0.20, 0.95), lw=2.0, ms=9,
                label='original 90° (vertical)')
    ax_lag.plot(LAGS, corrs_cg[0], 'o-',
                color=(0.45, 0.78, 1.00, 0.95), lw=1.5, ms=7,
                label='constgauss 0°')
    ax_lag.plot(LAGS, corrs_cg[8], 's-',
                color=(0.30, 0.55, 0.95, 0.95), lw=1.5, ms=7,
                label='constgauss 90°')
    ax_lag.axhline(0, color=(0.95, 0.97, 1.00, 0.30), lw=0.7)
    ax_lag.set_xlabel('lag L', color=(0.85, 0.88, 0.92, 0.92), fontsize=10)
    ax_lag.set_ylabel('Pearson corr', color=(0.85, 0.88, 0.92, 0.92), fontsize=10)
    ax_lag.set_xticks(LAGS)
    ax_lag.tick_params(colors=(0.78, 0.82, 0.88, 0.85), labelsize=9)
    for spine in ax_lag.spines.values():
        spine.set_color((0.40, 0.45, 0.50, 0.40))
    ax_lag.grid(True, color=(0.30, 0.34, 0.38), alpha=0.18, lw=0.4)
    ax_lag.legend(loc='upper left', fontsize=8.5, frameon=False,
                  labelcolor=(0.92, 0.95, 1.00, 1.0))
    ax_lag.set_title(
        'lag profile at axial directions — note the rise with L',
        color=(0.96, 0.97, 1.00, 0.92), fontsize=10, pad=8,
    )

    # --- bottom-right summary ---
    ax_summary = fig.add_axes([0.66, 0.05, 0.31, 0.42],
                              facecolor='#0a0a0a')
    ax_summary.set_axis_off()

    summary_lines = [
        '[ angular sum|corr| over L = 1, 2, 4 ]',
        '',
        '  total budget',
        f'    original     {sums_orig.sum():.4f}',
        f'    constgauss   {sums_cg.sum():.4f}',
        f'    ratio        {sums_orig.sum() / sums_cg.sum():.0f}x',
        '',
        '  peak angles (largest sum|corr|)',
        f'    {"90.0°":>6}  {sums_orig[8]:.4f}  (vertical)',
        f'    {"0.0°":>6}  {sums_orig[0]:.4f}  (horizontal)',
        f'    {"56.3°":>6}  {sums_orig[5]:.4f}',
        f'    {"123.7°":>6}  {sums_orig[11]:.4f}',
        '',
        '  weakest near-axial angles',
        f'    {"45.0°":>6}  {sums_orig[4]:.4f}  (+diag)',
        f'    {"135.0°":>6}  {sums_orig[12]:.4f}  (-diag)',
        '',
        '  the diagonals are weakest;',
        '  iter_5 saw -diag as the partial closure.',
        '  the FFT iteration inverted the substrate\'s',
        '  natural axial preference.',
    ]
    for i, line in enumerate(summary_lines):
        ax_summary.text(
            0.02, 0.97 - i * 0.045, line,
            transform=ax_summary.transAxes,
            color=(0.85, 0.92, 1.00, 0.92),
            fontsize=9.5, family='monospace',
            verticalalignment='top',
        )

    out = os.path.join(HERE, 'q_lattice_direct_angular.png')
    plt.savefig(out, facecolor='#0a0a0a', dpi=180,
                bbox_inches='tight', pad_inches=0.15)
    plt.close()
    sz = os.path.getsize(out) / 1024
    print(f'-> {os.path.basename(out)}  ({sz:.0f} KB)')


if __name__ == '__main__':
    main()
