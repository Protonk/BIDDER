"""
Q Distillery, h=3 - fixed height across the Phase 1 n-panel.

At height h=3 the master expansion has exactly three layers:

    + structure_1 * tau_1(k')
    - structure_2 * tau_2(k') / 2
    + structure_3 * tau_3(k') / 3

This render keeps h fixed and changes n. Payloads are grouped by their
overlap exponents relative to the prime factors of n, so the prime,
prime-power, and squarefree cases separate into visibly different
cancellation geometries.
"""

import os
from math import gcd, log

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
    factor_tuple,
    layer_terms,
    n_type,
    normalize_logs,
)


HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'q_distillery_h3_ns.png')

PANEL_NS = [2, 3, 5, 4, 6, 10]
H = 3
KPRIME_MAX = 60000
GROUP_SAMPLES = {
    'prime': 310,
    'prime_power': 150,
    'squarefree': 86,
}

IMG_W = 3300
IMG_H = 2200


def coprime_samples(n, count):
    raw = np.unique(np.round(np.geomspace(1, KPRIME_MAX, count * 7)).astype(int))
    vals = [int(k) for k in raw if gcd(int(k), n) == 1]
    if len(vals) < count:
        seen = set(vals)
        k = 1
        while len(vals) < count:
            if gcd(k, n) == 1 and k not in seen:
                vals.append(k)
                seen.add(k)
            k += 1
        vals.sort()
    return vals[:count]


def group_specs(n):
    kind = n_type(n)
    factors = factor_tuple(n)
    if kind == 'prime':
        return [((0,), 'coprime', GROUP_SAMPLES['prime'])]
    if kind == 'prime_power':
        a = factors[0][1]
        return [
            ((t,), f't={t}', GROUP_SAMPLES['prime_power'])
            for t in range(a)
        ]
    if kind == 'squarefree' and len(factors) == 2:
        p, q = factors[0][0], factors[1][0]
        return [
            ((0, 0), '00', GROUP_SAMPLES['squarefree']),
            ((1, 0), f'{p}', GROUP_SAMPLES['squarefree']),
            ((3, 0), f'{p}^3', GROUP_SAMPLES['squarefree']),
            ((0, 1), f'{q}', GROUP_SAMPLES['squarefree']),
            ((0, 3), f'{q}^3', GROUP_SAMPLES['squarefree']),
        ]
    raise ValueError(f'unexpected n for h=3 panel: {n}')


def payload_from_overlap(n, overlaps, k_prime):
    factors = factor_tuple(n)
    k = k_prime
    for (p, _a), t in zip(factors, overlaps):
        k *= p ** t
    return k


def collect_records():
    records = []
    for n in PANEL_NS:
        groups = group_specs(n)
        for group_idx, (overlaps, label, count) in enumerate(groups):
            for within_idx, k_prime in enumerate(coprime_samples(n, count)):
                k = payload_from_overlap(n, overlaps, k_prime)
                terms = layer_terms(n, H, k)
                q_value = sum(t['term'] for t in terms)
                for term in terms:
                    rec = dict(term)
                    rec.update({
                        'n': n,
                        'h': H,
                        'k': k,
                        'k_prime_sample': k_prime,
                        'group_idx': group_idx,
                        'group_count': len(groups),
                        'group_label': label,
                        'within_idx': within_idx,
                        'within_count': count,
                        'q': q_value,
                    })
                    records.append(rec)
    return records


def panel_geometry(panel_index):
    col = panel_index % 3
    row = panel_index // 3
    panel_w = 960.0
    panel_h = 820.0
    gap_x = 95.0
    gap_y = 230.0
    left = 130.0 + col * (panel_w + gap_x)
    bottom = 180.0 + (1 - row) * (panel_h + gap_y)
    return left, bottom, panel_w, panel_h


def draw_panel_shell(ax, left, bottom, width, height, n):
    cx = left + width * 0.5
    y0 = bottom + height * 0.11
    y1 = bottom + height * 0.89
    half = width * 0.47
    neck = width * 0.36
    verts = [
        (cx - neck, y1),
        (cx - half, y1 - height * 0.12),
        (cx - half, y0 + height * 0.12),
        (cx - neck, y0),
        (cx + neck, y0),
        (cx + half, y0 + height * 0.12),
        (cx + half, y1 - height * 0.12),
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
        facecolor=(0.018, 0.023, 0.026, 0.16),
        edgecolor=(0.55, 0.66, 0.70, 0.22),
        linewidth=1.05,
        zorder=1,
    ))
    ax.text(
        left + width * 0.055,
        bottom + height * 0.925,
        f'n={n}  {n_type(n)}',
        color=(1.0, 1.0, 1.0, 0.30),
        fontsize=15,
        ha='left',
        va='center',
        zorder=8,
    )


def group_x_position(left, width, rec):
    group_count = rec['group_count']
    group_idx = rec['group_idx']
    within_idx = rec['within_idx']
    within_count = rec['within_count']
    usable_left = left + width * 0.075
    usable_width = width * 0.85
    group_w = usable_width / group_count
    return (
        usable_left
        + group_w * group_idx
        + group_w * (0.08 + 0.84 * within_idx / max(within_count - 1, 1))
    )


def build_art(records, norms):
    panel_by_n = {n: i for i, n in enumerate(PANEL_NS)}

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

    layer_frac = {1: 0.72, 2: 0.50, 3: 0.285}
    next_frac = {1: 0.50, 2: 0.285, 3: 0.125}

    for rec in records:
        n = rec['n']
        left, bottom, panel_w, panel_h = panel_geometry(panel_by_n[n])
        j = rec['j']

        x_base = group_x_position(left, panel_w, rec)
        y0 = bottom + panel_h * layer_frac[j]
        y1 = bottom + panel_h * next_frac[j]

        coeff_norm = log(rec['coeff'] + 1.0) / norms['coeff']
        residue_norm = log(rec['residue'] + 1.0) / norms['residue']
        term_norm = log(abs(rec['term']) + 1.0) / norms['term']
        q_norm = log(abs(rec['q']) + 1.0) / norms['q']

        phase = 0.012 * rec['k_prime_sample'] + 1.61 * j + 0.37 * n
        plume = np.sin(phase) + 0.42 * np.sin(0.39 * phase + rec['group_idx'])
        drift = (
            12.0 * plume
            + 21.0 * (residue_norm - 0.5)
            + 16.0 * (coeff_norm - 0.5)
        )
        x0 = x_base + drift
        x1 = x_base + 0.55 * drift + 25.0 * (j - 2.0) + 18.0 * (coeff_norm - 0.45)

        sign = 1 if rec['term'] >= 0 else -1
        rgb = contribution_color(sign, residue_norm, term_norm)
        alpha = np.clip(0.13 + 0.50 * term_norm + 0.18 * residue_norm, 0.10, 0.88)
        width = 0.16 + 2.65 * coeff_norm + 1.85 * term_norm

        segments.append([(x0, y0), (x1, y1)])
        colors.append((*rgb, alpha))
        widths.append(width)
        glow_colors.append((*rgb, alpha * 0.17))
        glow_widths.append(width * (4.2 + 2.4 * term_norm))

        if j < H:
            residue_x.append(x1)
            residue_y.append(y1)
            residue_sizes.append(1.2 + 22.0 * residue_norm * (0.35 + term_norm))
            residue_colors.append((*np.clip(rgb + 0.16, 0.0, 1.0), 0.07 + 0.28 * residue_norm))

        if j == H:
            q_x.append(x1)
            q_y.append(y1 - panel_h * 0.030)
            if abs(rec['q']) < 1e-12:
                q_sizes.append(7.0)
                q_colors.append((0.92, 0.90, 0.78, 0.22))
            else:
                q_sizes.append(5.0 + 76.0 * q_norm)
                q_rgb = blend(POS_A, POS_B, 0.55) if rec['q'] > 0 else blend(NEG_A, NEG_B, 0.62)
                q_colors.append((*np.clip(q_rgb * (0.75 + 0.74 * q_norm), 0.0, 1.0),
                                 0.14 + 0.50 * q_norm))

    fig = plt.figure(figsize=(16.5, 11), dpi=200, facecolor=DARK, frameon=False)
    ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    ax.set_axis_off()
    ax.set_facecolor(DARK)
    fig.add_axes(ax)

    for i, n in enumerate(PANEL_NS):
        left, bottom, panel_w, panel_h = panel_geometry(i)
        draw_panel_shell(ax, left, bottom, panel_w, panel_h, n)
        groups = group_specs(n)

        for frac, a in [(layer_frac[1], 0.10), (layer_frac[2], 0.08), (layer_frac[3], 0.08)]:
            ax.plot(
                [left + panel_w * 0.07, left + panel_w * 0.93],
                [bottom + panel_h * frac, bottom + panel_h * frac],
                color=(0.62, 0.68, 0.70, a),
                lw=0.55,
                zorder=2,
            )

        usable_left = left + panel_w * 0.075
        usable_width = panel_w * 0.85
        group_w = usable_width / len(groups)
        for group_idx, (_overlaps, label, _count) in enumerate(groups):
            gx = usable_left + group_w * group_idx
            if group_idx > 0:
                ax.plot(
                    [gx, gx],
                    [bottom + panel_h * 0.115, bottom + panel_h * 0.765],
                    color=(0.66, 0.70, 0.72, 0.07),
                    lw=0.55,
                    zorder=2,
                )
            ax.text(
                gx + group_w * 0.5,
                bottom + panel_h * 0.105,
                label,
                color=(1.0, 1.0, 1.0, 0.18),
                fontsize=8,
                ha='center',
                va='center',
                zorder=8,
            )

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

    # Shared layer guides across the panel family.
    for frac in [layer_frac[1], layer_frac[2], layer_frac[3], next_frac[3] - 0.030]:
        xs = []
        ys = []
        for i in range(len(PANEL_NS)):
            left, bottom, panel_w, panel_h = panel_geometry(i)
            xs.append(left + panel_w * 0.5)
            ys.append(bottom + panel_h * frac)
        ax.plot(xs, ys, color=(0.36, 0.47, 0.50, 0.045), lw=0.9, zorder=0)

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
    print('Collecting h=3 Q layers across n...')
    records = collect_records()
    print(f'Rendering {len(records)} signed layers...')
    norms = normalize_logs(records)
    build_art(records, norms)
    print(f'-> {OUT}')


if __name__ == '__main__':
    main()
