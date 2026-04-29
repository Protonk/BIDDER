"""
Cancellation Furnace, h=3 - signed Q_n mass as opposing streams.

For h=3 the finite-rank stack is

    Q_n(n^3 k) = T1 - |T2| + T3.

This render fixes h=3 and changes n across the Phase 1 panel. Warm
positive mass descends, cool negative mass rises, and the central burn
line shows how much structure cancels before the residual Q_n remains.
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
    layer_terms,
    n_type,
)
from q_distillery_h3_ns import (
    H,
    PANEL_NS,
    coprime_samples,
    group_specs,
    payload_from_overlap,
)


HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'q_cancellation_furnace_h3_ns.png')

IMG_W = 3300
IMG_H = 2200


def collect_records():
    records = []
    for n in PANEL_NS:
        groups = group_specs(n)
        for group_idx, (overlaps, label, count) in enumerate(groups):
            for within_idx, k_prime in enumerate(coprime_samples(n, count)):
                k = payload_from_overlap(n, overlaps, k_prime)
                terms = layer_terms(n, H, k)
                if len(terms) != 3:
                    raise RuntimeError(f'expected three terms for h=3, got {len(terms)}')
                t1, t2, t3 = [term['term'] for term in terms]
                positive = sum(max(term['term'], 0.0) for term in terms)
                negative = sum(max(-term['term'], 0.0) for term in terms)
                q_value = positive - negative
                total = positive + negative
                cancellation = 0.0 if total <= 0.0 else 1.0 - abs(q_value) / total
                cancellation = max(0.0, min(1.0, cancellation))
                records.append({
                    'n': n,
                    'k': k,
                    'k_prime_sample': k_prime,
                    'group_idx': group_idx,
                    'group_count': len(groups),
                    'group_label': label,
                    'within_idx': within_idx,
                    'within_count': count,
                    't1': t1,
                    't2_abs': -t2,
                    't3': t3,
                    'positive': positive,
                    'negative': negative,
                    'q': q_value,
                    'total': total,
                    'cancellation': cancellation,
                })
    return records


def log_norm(values):
    logs = [log(v + 1.0) for v in values]
    return max(max(logs), 1e-9)


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
    y0 = bottom + height * 0.105
    y1 = bottom + height * 0.895
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
        facecolor=(0.018, 0.023, 0.026, 0.15),
        edgecolor=(0.55, 0.66, 0.70, 0.20),
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


def build_art(records):
    pos_norm = log_norm([r['positive'] for r in records])
    neg_norm = log_norm([r['negative'] for r in records])
    t1_norm = log_norm([abs(r['t1']) for r in records])
    t3_norm = log_norm([abs(r['t3']) for r in records])
    q_norm_denom = log_norm([abs(r['q']) for r in records])
    total_norm = log_norm([r['total'] for r in records])

    panel_by_n = {n: i for i, n in enumerate(PANEL_NS)}

    pos1_segments = []
    pos1_colors = []
    pos1_widths = []
    pos3_segments = []
    pos3_colors = []
    pos3_widths = []
    neg_segments = []
    neg_colors = []
    neg_widths = []
    glow_segments = []
    glow_colors = []
    glow_widths = []

    burn_x = []
    burn_y = []
    burn_sizes = []
    burn_colors = []
    core_x = []
    core_y = []
    core_sizes = []
    core_colors = []
    q_x = []
    q_y = []
    q_sizes = []
    q_colors = []

    for rec in records:
        n = rec['n']
        left, bottom, panel_w, panel_h = panel_geometry(panel_by_n[n])
        x_base = group_x_position(left, panel_w, rec)
        y_top = bottom + panel_h * 0.765
        y_mid = bottom + panel_h * 0.505
        y_bottom = bottom + panel_h * 0.255
        y_residue = bottom + panel_h * 0.122

        pos_n = log(rec['positive'] + 1.0) / pos_norm
        neg_n = log(rec['negative'] + 1.0) / neg_norm
        t1_n = log(abs(rec['t1']) + 1.0) / t1_norm
        t3_n = log(abs(rec['t3']) + 1.0) / t3_norm
        q_n = log(abs(rec['q']) + 1.0) / q_norm_denom
        total_n = log(rec['total'] + 1.0) / total_norm
        cancel = rec['cancellation']

        phase = 0.012 * rec['k_prime_sample'] + 0.43 * n + 0.71 * rec['group_idx']
        plume = np.sin(phase) + 0.45 * np.sin(0.47 * phase + 1.2)
        drift = 13.0 * plume + 28.0 * (cancel - 0.5)
        x_collision = x_base + drift

        x_t1 = x_base - 22.0 + 16.0 * np.sin(0.55 * phase)
        x_t3 = x_base + 20.0 + 22.0 * (t3_n - 0.5)
        x_neg = x_base + 8.0 + 16.0 * np.sin(0.63 * phase + 2.0)

        pos1_segments.append([(x_t1, y_top), (x_collision - 5.0, y_mid)])
        pos3_segments.append([(x_t3, bottom + panel_h * 0.700), (x_collision + 7.0, y_mid)])
        neg_segments.append([(x_neg, y_bottom), (x_collision, y_mid)])

        warm1 = blend(POS_A, POS_B, 0.18 + 0.45 * cancel)
        warm3 = blend(np.array([1.0, 0.92, 0.56]), POS_B, 0.30 + 0.50 * t3_n)
        cool = blend(NEG_A, NEG_B, 0.22 + 0.58 * cancel)

        pos1_alpha = np.clip(0.12 + 0.36 * t1_n + 0.14 * pos_n, 0.10, 0.68)
        pos3_alpha = np.clip(0.10 + 0.42 * t3_n + 0.18 * pos_n, 0.08, 0.78)
        neg_alpha = np.clip(0.12 + 0.50 * neg_n + 0.22 * cancel, 0.10, 0.86)

        pos1_colors.append((*np.clip(warm1, 0.0, 1.0), pos1_alpha))
        pos3_colors.append((*np.clip(warm3, 0.0, 1.0), pos3_alpha))
        neg_colors.append((*np.clip(cool, 0.0, 1.0), neg_alpha))

        pos1_widths.append(0.18 + 2.0 * t1_n + 1.1 * pos_n)
        pos3_widths.append(0.14 + 2.2 * t3_n + 1.3 * pos_n)
        neg_widths.append(0.16 + 2.8 * neg_n + 1.8 * cancel)

        # A broad white-hot halo around heavy collisions.
        if cancel > 0.18:
            glow_segments.append([(x_collision - 9.0, y_mid), (x_collision + 9.0, y_mid)])
            glow_colors.append((1.0, 0.92, 0.72, 0.05 + 0.24 * cancel * total_n))
            glow_widths.append(7.0 + 30.0 * cancel * total_n)

        burn_x.append(x_collision)
        burn_y.append(y_mid)
        burn_sizes.append(6.0 + 138.0 * cancel * total_n)
        burn_colors.append((0.0, 0.0, 0.0, 0.10 + 0.55 * cancel))

        core_x.append(x_collision)
        core_y.append(y_mid)
        core_sizes.append(2.0 + 54.0 * cancel * total_n)
        core_colors.append((1.0, 0.95, 0.75, 0.07 + 0.35 * cancel * total_n))

        q_x.append(x_collision + 10.0 * np.sin(phase + 1.7))
        q_y.append(y_residue)
        if abs(rec['q']) < 1e-12:
            q_sizes.append(6.0 + 30.0 * cancel)
            q_colors.append((0.98, 0.95, 0.82, 0.24 + 0.28 * cancel))
        elif rec['q'] > 0:
            q_rgb = blend(POS_A, POS_B, 0.55)
            q_sizes.append(4.0 + 78.0 * q_n)
            q_colors.append((*np.clip(q_rgb * (0.76 + 0.72 * q_n), 0.0, 1.0),
                             0.14 + 0.50 * q_n))
        else:
            q_rgb = blend(NEG_A, NEG_B, 0.68)
            q_sizes.append(4.0 + 78.0 * q_n)
            q_colors.append((*np.clip(q_rgb * (0.76 + 0.72 * q_n), 0.0, 1.0),
                             0.14 + 0.50 * q_n))

    fig = plt.figure(figsize=(16.5, 11), dpi=200, facecolor=DARK, frameon=False)
    ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    ax.set_axis_off()
    ax.set_facecolor(DARK)
    fig.add_axes(ax)

    for i, n in enumerate(PANEL_NS):
        left, bottom, panel_w, panel_h = panel_geometry(i)
        draw_panel_shell(ax, left, bottom, panel_w, panel_h, n)
        groups = group_specs(n)

        for frac, alpha, lw in [(0.765, 0.08, 0.55), (0.505, 0.14, 0.78),
                                (0.255, 0.08, 0.55), (0.122, 0.08, 0.55)]:
            ax.plot(
                [left + panel_w * 0.07, left + panel_w * 0.93],
                [bottom + panel_h * frac, bottom + panel_h * frac],
                color=(0.62, 0.68, 0.70, alpha),
                lw=lw,
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
                    [bottom + panel_h * 0.105, bottom + panel_h * 0.785],
                    color=(0.66, 0.70, 0.72, 0.07),
                    lw=0.55,
                    zorder=2,
                )
            ax.text(
                gx + group_w * 0.5,
                bottom + panel_h * 0.095,
                label,
                color=(1.0, 1.0, 1.0, 0.17),
                fontsize=8,
                ha='center',
                va='center',
                zorder=8,
            )

    if glow_segments:
        ax.add_collection(LineCollection(
            glow_segments,
            colors=glow_colors,
            linewidths=glow_widths,
            capstyle='round',
            joinstyle='round',
            antialiased=True,
            zorder=3,
        ))

    for segments, colors, widths, z in [
        (pos1_segments, pos1_colors, pos1_widths, 4),
        (pos3_segments, pos3_colors, pos3_widths, 5),
        (neg_segments, neg_colors, neg_widths, 6),
    ]:
        ax.add_collection(LineCollection(
            segments,
            colors=[(r, g, b, a * 0.18) for r, g, b, a in colors],
            linewidths=[w * 5.2 for w in widths],
            capstyle='round',
            joinstyle='round',
            antialiased=True,
            zorder=z,
        ))
        ax.add_collection(LineCollection(
            segments,
            colors=colors,
            linewidths=widths,
            capstyle='round',
            joinstyle='round',
            antialiased=True,
            zorder=z + 1,
        ))

    ax.scatter(burn_x, burn_y, s=burn_sizes, c=burn_colors,
               marker='o', linewidths=0, zorder=10)
    ax.scatter(core_x, core_y, s=core_sizes, c=core_colors,
               marker='o', linewidths=0, zorder=11)
    ax.scatter(q_x, q_y, s=q_sizes, c=q_colors,
               marker='o', linewidths=0, zorder=12)

    # Shared center-burn guides connect the family panels.
    for frac in [0.505, 0.122]:
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
    print('Collecting h=3 cancellation records...')
    records = collect_records()
    print(f'Rendering {len(records)} furnace columns...')
    build_art(records)
    print(f'-> {OUT}')


if __name__ == '__main__':
    main()
