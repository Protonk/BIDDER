"""
Q Distillery, n=2 - one enlarged finite-rank pane.

This is the single-vessel version of q_distillery.py. It keeps only
n=2 and spends the whole canvas on the prime case, so the alternating
structure/residue handoff is easier to read.
"""

import os
from math import log

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.path import Path
from matplotlib.patches import PathPatch

from q_distillery import (
    DARK,
    NEG_A,
    NEG_B,
    POS_A,
    POS_B,
    blend,
    contribution_color,
    layer_terms,
    n_type,
    normalize_logs,
)


HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'q_distillery_n2.png')

N = 2
H_MAX = 8
K_SAMPLES = 430
K_MAX = 32000

IMG_W = 3000
IMG_H = 2300


def payloads_for_single_n():
    raw = np.unique(np.round(np.geomspace(1, K_MAX, K_SAMPLES * 5)).astype(int))
    vals = [int(k) for k in raw if k % N != 0]
    if len(vals) < K_SAMPLES:
        seen = set(vals)
        k = 1
        while len(vals) < K_SAMPLES:
            if k % N != 0 and k not in seen:
                vals.append(k)
                seen.add(k)
            k += 1
        vals.sort()
    return vals[:K_SAMPLES]


def collect_records(payloads):
    records = []
    for h in range(1, H_MAX + 1):
        for idx, k in enumerate(payloads):
            terms = layer_terms(N, h, k)
            q_value = sum(t['term'] for t in terms)
            for term in terms:
                rec = dict(term)
                rec.update({
                    'n': N,
                    'h': h,
                    'k': k,
                    'payload_idx': idx,
                    'q': q_value,
                })
                records.append(rec)
    return records


def draw_vessel(ax):
    left = 185.0
    bottom = 130.0
    width = 2630.0
    height = 2025.0
    cx = left + width * 0.5
    y0 = bottom + height * 0.045
    y1 = bottom + height * 0.955
    half = width * 0.465
    neck = width * 0.365

    verts = [
        (cx - neck, y1),
        (cx - half, y1 - height * 0.13),
        (cx - half, y0 + height * 0.14),
        (cx - neck, y0),
        (cx + neck, y0),
        (cx + half, y0 + height * 0.14),
        (cx + half, y1 - height * 0.13),
        (cx + neck, y1),
        (cx - neck, y1),
    ]
    codes = [
        Path.MOVETO,
        Path.CURVE3,
        Path.CURVE3,
        Path.CURVE3,
        Path.LINETO,
        Path.CURVE3,
        Path.CURVE3,
        Path.CURVE3,
        Path.CLOSEPOLY,
    ]
    ax.add_patch(PathPatch(
        Path(verts, codes),
        facecolor=(0.018, 0.023, 0.026, 0.18),
        edgecolor=(0.55, 0.66, 0.70, 0.28),
        linewidth=1.25,
        zorder=1,
    ))

    ax.text(
        left + width * 0.055,
        bottom + height * 0.948,
        f'n={N}  {n_type(N)}',
        color=(1.0, 1.0, 1.0, 0.30),
        fontsize=22,
        ha='left',
        va='center',
        zorder=8,
    )

    return left, bottom, width, height


def build_art(records, payloads, norms):
    left = 185.0
    bottom = 130.0
    panel_w = 2630.0
    panel_h = 2025.0

    segments = []
    colors = []
    widths = []
    glow_colors = []
    glow_widths = []
    residue_x = []
    residue_y = []
    residue_sizes = []
    residue_colors = []
    q_x = []
    q_y = []
    q_sizes = []
    q_colors = []

    payload_count = len(payloads)

    for rec in records:
        h = rec['h']
        j = rec['j']
        idx = rec['payload_idx']
        x_base = left + panel_w * (0.065 + 0.87 * idx / max(payload_count - 1, 1))
        band_h = panel_h * 0.086
        band_gap = panel_h * 0.021
        band_bottom = bottom + panel_h * 0.075 + (h - 1) * (band_h + band_gap)

        layer_y = band_bottom + band_h * (0.10 + 0.80 * (j - 0.5) / h)
        next_y = band_bottom + band_h * (0.10 + 0.80 * (min(j + 1, h + 0.82) - 0.5) / h)

        coeff_norm = log(rec['coeff'] + 1.0) / norms['coeff']
        residue_norm = log(rec['residue'] + 1.0) / norms['residue']
        term_norm = log(abs(rec['term']) + 1.0) / norms['term']
        q_norm = log(abs(rec['q']) + 1.0) / norms['q']

        phase = 0.0105 * rec['k'] + 1.52 * j + 0.71 * h
        plume = np.sin(phase) + 0.55 * np.sin(0.31 * phase + 1.4)
        drift = (
            34.0 * plume
            + 38.0 * (residue_norm - 0.5)
            + 18.0 * (j - (h + 1) / 2.0)
        )
        x0 = x_base + drift
        x1 = x_base + 0.54 * drift + 58.0 * (coeff_norm - 0.48)

        sign = 1 if rec['term'] >= 0 else -1
        rgb = contribution_color(sign, residue_norm, term_norm)
        alpha = np.clip(0.13 + 0.52 * term_norm + 0.16 * residue_norm, 0.10, 0.90)
        width = 0.16 + 2.65 * coeff_norm + 1.75 * term_norm

        segments.append([(x0, layer_y), (x1, next_y)])
        colors.append((*rgb, alpha))
        widths.append(width)
        glow_colors.append((*rgb, alpha * 0.17))
        glow_widths.append(width * (4.0 + 2.2 * term_norm))

        if j < h:
            residue_x.append(x1)
            residue_y.append(next_y)
            residue_sizes.append(1.3 + 26.0 * residue_norm * (0.38 + term_norm))
            residue_colors.append((*np.clip(rgb + 0.18, 0.0, 1.0), 0.08 + 0.30 * residue_norm))

        if j == h:
            q_x.append(x1)
            q_y.append(band_bottom - band_h * 0.18)
            q_sizes.append(5.0 + 82.0 * q_norm)
            q_rgb = blend(POS_A, POS_B, 0.54) if rec['q'] >= 0 else blend(NEG_A, NEG_B, 0.58)
            q_colors.append((*np.clip(q_rgb * (0.76 + 0.72 * q_norm), 0.0, 1.0), 0.15 + 0.50 * q_norm))

    fig = plt.figure(figsize=(15, 11.5), dpi=200, facecolor=DARK, frameon=False)
    ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    ax.set_axis_off()
    ax.set_facecolor(DARK)
    fig.add_axes(ax)

    draw_vessel(ax)

    for h in range(1, H_MAX + 1):
        band_h = panel_h * 0.086
        band_gap = panel_h * 0.021
        y = bottom + panel_h * 0.075 + (h - 1) * (band_h + band_gap)
        x0 = left + panel_w * 0.06
        x1 = left + panel_w * 0.94
        ax.plot([x0, x1], [y - band_h * 0.17, y - band_h * 0.17],
                color=(0.66, 0.72, 0.74, 0.08), lw=0.65, zorder=2)
        ax.text(left + panel_w * 0.955, y + band_h * 0.42, str(h),
                color=(1.0, 1.0, 1.0, 0.20), fontsize=13,
                ha='center', va='center', zorder=8)

    ax.add_collection(LineCollection(
        segments,
        colors=glow_colors,
        linewidths=glow_widths,
        capstyle='round',
        joinstyle='round',
        antialiased=True,
        zorder=3,
    ))
    ax.add_collection(LineCollection(
        segments,
        colors=colors,
        linewidths=widths,
        capstyle='round',
        joinstyle='round',
        antialiased=True,
        zorder=4,
    ))

    ax.scatter(residue_x, residue_y, s=residue_sizes, c=residue_colors,
               marker='.', linewidths=0, zorder=5)
    ax.scatter(q_x, q_y, s=q_sizes, c=q_colors,
               marker='o', linewidths=0, zorder=6)

    # A faint condenser curve makes the single pane feel like one object.
    t = np.linspace(0.0, 1.0, 900)
    arc_x = left + panel_w * (0.075 + 0.85 * t)
    arc_y = bottom + panel_h * (0.915 + 0.020 * np.sin(2.0 * np.pi * t))
    ax.plot(arc_x, arc_y, color=(0.38, 0.52, 0.56, 0.10), lw=1.1, zorder=0)

    ax.set_xlim(0, IMG_W)
    ax.set_ylim(0, IMG_H)
    ax.set_aspect('equal')

    fig.canvas.draw()
    rgba = np.asarray(fig.canvas.buffer_rgba()).astype(np.float64) / 255.0
    bg = np.array([10, 10, 10], dtype=np.float64) / 255.0
    rgb_out = rgba[:, :, :3] * rgba[:, :, 3:4] + bg * (1.0 - rgba[:, :, 3:4])
    plt.imsave(OUT, np.clip(rgb_out, 0.0, 1.0))
    plt.close(fig)


def main():
    print('Collecting n=2 finite-rank layers...')
    payloads = payloads_for_single_n()
    records = collect_records(payloads)
    print(f'Rendering {len(records)} signed layers...')
    norms = normalize_logs(records)
    build_art(records, payloads, norms)
    print(f'-> {OUT}')


if __name__ == '__main__':
    main()
