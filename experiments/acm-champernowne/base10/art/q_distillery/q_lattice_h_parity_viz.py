"""
q_lattice_h_parity_viz.py - direct visualisation of the h-parity
alternation in the substrate's angular spectrum.

Three panels designed to show the parity flip directly rather than
imply it via overlay:

  1. (n, k)-style heatmap of the 4×16 spectra. Rows = h ∈ {5, 6, 7, 8},
     columns = 16 angles. Color = sum|corr|. Even-row vs odd-row
     pattern reveals the alternation as banded structure.
  2. Polar overlay: even-h average (orange) vs odd-h average (blue),
     shown as filled polygons. The two shapes differ in axial
     emphasis, visible directly as different lobe-magnitudes at 0°
     vs 90°.
  3. Polar signed difference: (even avg) − (odd avg) at each angle.
     Positive directions (even-dominated) filled warm, negative
     directions (odd-dominated) filled cool. Shows the parity
     alternation's direction-by-direction pattern.

Uses cached lattices (q_lattice_4000_h{5,6,7,8}.npy).
"""

import os
import time
from math import atan2, degrees

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


HERE = os.path.dirname(os.path.abspath(__file__))
H_VALUES = [5, 6, 7, 8]


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


DIRECTIONS = [
    (0, 1), (1, 3), (1, 2), (2, 3), (1, 1), (3, 2), (2, 1), (3, 1),
    (1, 0), (3, -1), (2, -1), (3, -2), (1, -1), (2, -3), (1, -2), (1, -3),
]
LAGS = [1, 2, 4]


def angular_sums(img):
    out = np.zeros(len(DIRECTIONS))
    for i, (dy_u, dx_u) in enumerate(DIRECTIONS):
        s = 0.0
        for L in LAGS:
            s += abs(lag_corr(img, dy_u * L, dx_u * L))
        out[i] = s
    return out


def main():
    print('Loading cached lattices and computing angular spectra...')
    spectra = {}
    for h in H_VALUES:
        cache = os.path.join(HERE, f'q_lattice_4000_h{h}.npy')
        if not os.path.exists(cache):
            print(f'  no cache for h={h}; skipping')
            continue
        t0 = time.time()
        grid = np.load(cache)
        img = slog(grid).astype(np.float32)
        spectra[h] = angular_sums(img)
        print(f'  h={h}: {time.time() - t0:.1f}s   '
              f'total={spectra[h].sum():.4f}')

    angles_rad = np.array([np.arctan2(dy, dx) for dy, dx in DIRECTIONS])
    angles_deg = np.array([degrees(np.arctan2(dy, dx)) for dy, dx in DIRECTIONS])

    odd_avg = (spectra[5] + spectra[7]) / 2.0
    even_avg = (spectra[6] + spectra[8]) / 2.0
    diff = even_avg - odd_avg

    print('\nodd-avg per angle:    ', odd_avg.round(4))
    print('even-avg per angle:   ', even_avg.round(4))
    print('diff (even - odd):    ', diff.round(4))

    fig = plt.figure(figsize=(16, 10), facecolor='#0a0a0a', dpi=180)

    # ---------- Panel 1: heatmap of (h, angle) ----------
    ax_heat = fig.add_axes([0.04, 0.58, 0.92, 0.36],
                           facecolor='#0a0a0a')
    # Sort columns by angle ascending for visual order
    order = np.argsort(angles_deg)
    sorted_angles = angles_deg[order]
    matrix = np.array([spectra[h][order] for h in H_VALUES])

    cmap_heat = LinearSegmentedColormap.from_list('heat', [
        (0.05, 0.06, 0.08),
        (0.20, 0.25, 0.45),
        (0.55, 0.30, 0.95),
        (1.00, 0.45, 0.30),
        (1.00, 0.92, 0.45),
    ], N=512)

    im = ax_heat.imshow(matrix, aspect='auto', cmap=cmap_heat,
                        origin='lower', interpolation='nearest',
                        vmin=0, vmax=matrix.max())
    ax_heat.set_yticks(range(len(H_VALUES)))
    ax_heat.set_yticklabels(
        [f'h = {h}  ({"even" if h % 2 == 0 else "odd"})' for h in H_VALUES],
        color=(0.92, 0.95, 1.00, 0.95), fontsize=11,
    )
    ax_heat.set_xticks(range(len(sorted_angles)))
    ax_heat.set_xticklabels(
        [f'{a:.0f}°' for a in sorted_angles],
        color=(0.78, 0.82, 0.88, 0.85), fontsize=9, rotation=0,
    )
    ax_heat.set_xlabel('lag-direction angle',
                       color=(0.85, 0.88, 0.92, 0.92), fontsize=11)
    ax_heat.set_title(
        'spectrum heatmap   ·   rows = h   ·   cols = angle   ·   '
        'cell = sum|corr| over L = 1, 2, 4',
        color=(0.96, 0.97, 1.00, 0.95), fontsize=12, pad=10,
    )
    for spine in ax_heat.spines.values():
        spine.set_color((0.40, 0.45, 0.50, 0.40))

    # Annotate cell values
    for i, h in enumerate(H_VALUES):
        for j in range(len(sorted_angles)):
            v = matrix[i, j]
            txt_color = (0.05, 0.05, 0.06) if v > 1.4 else (0.95, 0.97, 1.00)
            ax_heat.text(j, i, f'{v:.2f}',
                         color=(*txt_color, 0.92), ha='center', va='center',
                         fontsize=8, family='monospace')

    cbar = fig.colorbar(im, ax=ax_heat, fraction=0.025, pad=0.02)
    cbar.set_label('sum |corr|', color=(0.85, 0.88, 0.92, 0.85))
    cbar.ax.tick_params(colors=(0.78, 0.82, 0.88, 0.85), labelsize=8)

    # Highlight 0° (col index where angle is closest to 0) and 90°
    col_0 = int(np.argmin(np.abs(sorted_angles - 0)))
    col_90 = int(np.argmin(np.abs(sorted_angles - 90)))
    for col in [col_0, col_90]:
        ax_heat.axvline(col, color=(1.0, 1.0, 1.0, 0.15), lw=0.6)

    # ---------- Panel 2: polar overlay (odd vs even avg) ----------
    ax_pol1 = fig.add_axes([0.04, 0.05, 0.40, 0.45], polar=True,
                           facecolor='#0a0a0a')
    ax_pol1.set_theta_zero_location('E')
    ax_pol1.set_theta_direction(1)

    def close_polar(angles, vals):
        full_a = np.concatenate([angles, angles + np.pi])
        full_v = np.concatenate([vals, vals])
        order = np.argsort(full_a)
        full_a = full_a[order]
        full_v = full_v[order]
        return (np.concatenate([full_a, [full_a[0] + 2 * np.pi]]),
                np.concatenate([full_v, [full_v[0]]]))

    ang_full, odd_full = close_polar(angles_rad, odd_avg)
    _, even_full = close_polar(angles_rad, even_avg)

    ax_pol1.fill(ang_full, even_full, color=(1.00, 0.66, 0.30, 0.30))
    ax_pol1.plot(ang_full, even_full, color=(1.00, 0.66, 0.30, 0.95),
                 lw=2.2, label='even h avg (h=6, 8)')

    ax_pol1.fill(ang_full, odd_full, color=(0.45, 0.78, 1.00, 0.30))
    ax_pol1.plot(ang_full, odd_full, color=(0.45, 0.78, 1.00, 0.95),
                 lw=2.2, label='odd h avg (h=5, 7)')

    ax_pol1.scatter(angles_rad, even_avg, s=60,
                    c=[(1.00, 0.84, 0.30, 1.0)],
                    edgecolors=[(0.0, 0.0, 0.0, 0.85)], linewidths=0.8,
                    zorder=5)
    ax_pol1.scatter(angles_rad + np.pi, even_avg, s=60,
                    c=[(1.00, 0.84, 0.30, 1.0)],
                    edgecolors=[(0.0, 0.0, 0.0, 0.85)], linewidths=0.8,
                    zorder=5)
    ax_pol1.scatter(angles_rad, odd_avg, s=60,
                    c=[(0.55, 0.85, 1.00, 1.0)],
                    edgecolors=[(0.0, 0.0, 0.0, 0.85)], linewidths=0.8,
                    zorder=5)
    ax_pol1.scatter(angles_rad + np.pi, odd_avg, s=60,
                    c=[(0.55, 0.85, 1.00, 1.0)],
                    edgecolors=[(0.0, 0.0, 0.0, 0.85)], linewidths=0.8,
                    zorder=5)

    ax_pol1.set_xticks(np.deg2rad([0, 45, 90, 135, 180, 225, 270, 315]))
    ax_pol1.set_xticklabels(['0°', '45°', '90°', '135°', '180°',
                              '225°', '270°', '315°'],
                             color=(0.92, 0.95, 1.00, 0.92), fontsize=10)
    ax_pol1.tick_params(colors=(0.78, 0.82, 0.88, 0.78), labelsize=8)
    ax_pol1.grid(True, color=(0.30, 0.34, 0.38), alpha=0.30, lw=0.5)
    ax_pol1.set_title(
        'odd-h avg vs even-h avg   ·   linear radial scale',
        color=(0.96, 0.97, 1.00, 0.92), fontsize=11, pad=18,
    )
    ax_pol1.legend(loc='lower center', bbox_to_anchor=(0.5, -0.13),
                   fontsize=9, frameon=False,
                   labelcolor=(0.92, 0.95, 1.00, 1.0), ncol=2)

    # ---------- Panel 3: polar signed difference ----------
    ax_pol2 = fig.add_axes([0.55, 0.05, 0.40, 0.45], polar=True,
                           facecolor='#0a0a0a')
    ax_pol2.set_theta_zero_location('E')
    ax_pol2.set_theta_direction(1)

    diff_full_a, diff_full = close_polar(angles_rad, diff)

    diff_pos = np.where(diff_full > 0, diff_full, 0)
    diff_neg = np.where(diff_full < 0, -diff_full, 0)

    ax_pol2.fill(diff_full_a, diff_pos, color=(1.00, 0.66, 0.30, 0.55),
                 label='even − odd > 0  (even-dominated)')
    ax_pol2.fill(diff_full_a, diff_neg, color=(0.45, 0.78, 1.00, 0.55),
                 label='odd − even > 0  (odd-dominated)')

    # Outer outline of |diff|
    ax_pol2.plot(diff_full_a, np.abs(diff_full),
                 color=(0.96, 0.97, 1.00, 0.85), lw=1.4)

    # Mark sign at each measured angle
    for ang, d in zip(angles_rad, diff):
        col = (1.00, 0.66, 0.30) if d > 0 else (0.45, 0.78, 1.00)
        ax_pol2.scatter([ang, ang + np.pi], [abs(d), abs(d)],
                        s=70, c=[col], zorder=5,
                        edgecolors=[(0.0, 0.0, 0.0, 0.85)], linewidths=0.8)

    ax_pol2.set_xticks(np.deg2rad([0, 45, 90, 135, 180, 225, 270, 315]))
    ax_pol2.set_xticklabels(['0°', '45°', '90°', '135°', '180°',
                              '225°', '270°', '315°'],
                             color=(0.92, 0.95, 1.00, 0.92), fontsize=10)
    ax_pol2.tick_params(colors=(0.78, 0.82, 0.88, 0.78), labelsize=8)
    ax_pol2.grid(True, color=(0.30, 0.34, 0.38), alpha=0.30, lw=0.5)
    ax_pol2.set_title(
        '|even-avg − odd-avg|  ·  warm: even>odd  ·  cool: odd>even',
        color=(0.96, 0.97, 1.00, 0.92), fontsize=11, pad=18,
    )
    ax_pol2.legend(loc='lower center', bbox_to_anchor=(0.5, -0.13),
                   fontsize=9, frameon=False,
                   labelcolor=(0.92, 0.95, 1.00, 1.0), ncol=1)

    # ---------- super-title ----------
    fig.text(0.5, 0.98,
             'h-parity alternation in substrate spatial-correlation shape',
             ha='center', va='top', fontsize=14, fontweight='bold',
             color=(1.0, 1.0, 1.0, 0.95), family='serif')
    fig.text(0.5, 0.955,
             'odd h: roughly axial-balanced  ·  '
             'even h: horizontal-dominant, vertical-suppressed  ·  '
             'diagonals weakest at all h',
             ha='center', va='top', fontsize=10, fontstyle='italic',
             color=(0.85, 0.88, 0.92, 0.65))

    out = os.path.join(HERE, 'q_lattice_h_parity.png')
    plt.savefig(out, facecolor='#0a0a0a', dpi=180,
                bbox_inches='tight', pad_inches=0.15)
    plt.close()
    sz = os.path.getsize(out) / 1024
    print(f'\n-> {os.path.basename(out)}  ({sz:.0f} KB)')


if __name__ == '__main__':
    main()
