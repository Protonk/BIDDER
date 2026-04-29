"""
q_merger_h5.py - merger D restricted to h = 5.

Combines q_trajectory.py and q_towers.py in one panel:

  - x-axis: four n positions (n in {2, 4, 6, 12}), each given a small
    horizontal range so payloads can spread within the column.
  - y-axis: signed mass on symlog scale.
  - Per (n, k=k_i, h=5): a vertical tower from -N to +P, warm above 0,
    cool below 0. The tower height (P + N) is the pre-cancellation
    mass at that cell.
  - Per k: a polyline connecting Q_n(n^5 k) at the four n positions.
    The polyline literally threads through the towers.

Bulk (~100 k coprime to 12): faint towers and faint polylines, drawn
as a "fog" of cancellation context.

Highlighted k (canonical anchors): bright towers, bright Q dots,
bright polyline. Each highlighted k tells a structural story:

  - k = 1 (simple payload): towers small at n=2 / n=4 (primes/p-powers
    side); larger at n=6 / n=12. Polyline shape mirrors q_trajectory's
    h=5 panel.
  - k = 5 (single prime): same shape, scaled.
  - k = 25 = 5^2 (prime square): bigger towers because tau_j growth.
  - k = 35 = 5*7 (the dramatic violation): towers tall everywhere,
    polyline traces 0 -> -3 -> -24 -> +60 - the cancellation flips
    the surviving sign at n=12 even as towers stay roughly comparable.
  - k = 49 = 7^2 and k = 121 = 11^2: more prime-square structure.

The visual claim is: hierarchy reads as TOWER GROWTH (warm + cool
extent), the polyline is where the residual lands within those
towers. A polyline punching DEEP into a tower (Q_n far from 0
relative to P + N) is rare structure; a polyline hugging the
midline (Q_n ~ 0 relative to P + N) is heavy cancellation.
"""

import os
from functools import lru_cache
from math import comb, gcd, lcm

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection


HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'q_merger_h5.png')

PANEL_NS = [2, 4, 6, 12]
N_TYPES = ['prime', 'prime power', 'squarefree', 'mixed']
H = 5
K_MAX = 300

DARK = '#0a0a0a'
WARM = (1.00, 0.66, 0.30)
COOL = (0.45, 0.78, 1.00)
TICK_COLOR = (0.85, 0.88, 0.92, 0.85)
LABEL_COLOR = (0.95, 0.97, 1.00, 0.95)


@lru_cache(maxsize=None)
def factor_tuple(n):
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


@lru_cache(maxsize=None)
def tau(j, x):
    if j == 1:
        return 1
    prod = 1
    for _p, e in factor_tuple(x):
        prod *= comb(e + j - 1, j - 1)
    return prod


def pn_q(n, h, k):
    factors = factor_tuple(n)
    P = 0.0
    N = 0.0
    for j in range(1, h + 1):
        coeff = 1
        for (_p, a) in factors:
            coeff *= comb(a * (h - j) + j - 1, j - 1)
        magnitude = coeff * tau(j, k) / j
        if j % 2 == 1:
            P += magnitude
        else:
            N += magnitude
    return P, N, P - N


def panel_lcm():
    L = 1
    for n in PANEL_NS:
        L = lcm(L, n)
    return L


def slog(y, lt=1.0):
    return np.sign(y) * np.log10(1.0 + np.abs(y) / lt)


def main():
    L = panel_lcm()
    payloads = [k for k in range(1, K_MAX + 1) if gcd(k, L) == 1]
    print(f'{len(payloads)} payloads coprime to {L}.')

    # Per-k data: tuple keyed by n.
    data = {k: {n: pn_q(n, H, k) for n in PANEL_NS} for k in payloads}

    # x-positions for each (n_idx, k_idx).
    n_centers = np.arange(len(PANEL_NS), dtype=float) * 1.6
    column_half_width = 0.55
    log_ks = np.log(np.array(payloads))
    lk_min, lk_max = log_ks.min(), log_ks.max()
    lk_norm = (log_ks - lk_min) / (lk_max - lk_min) if lk_max > lk_min else np.zeros_like(log_ks)

    def x_pos(n_idx, k_idx):
        return n_centers[n_idx] - column_half_width + 2 * column_half_width * lk_norm[k_idx]

    fig, ax = plt.subplots(figsize=(15, 11), dpi=180, facecolor=DARK)
    ax.set_facecolor(DARK)

    # ---- background fog: 100 k towers and Q polylines, very faint ----

    bg_warm_segs = []
    bg_cool_segs = []
    bg_poly_segs = []
    bg_q_x = []
    bg_q_y = []

    for k_idx, k in enumerate(payloads):
        poly_xs = []
        poly_ys = []
        for n_idx, n in enumerate(PANEL_NS):
            P, N, Q = data[k][n]
            x = x_pos(n_idx, k_idx)
            bg_warm_segs.append([(x, 0.0), (x, slog(P))])
            bg_cool_segs.append([(x, 0.0), (x, -slog(N))])
            poly_xs.append(x)
            poly_ys.append(slog(Q))
            bg_q_x.append(x)
            bg_q_y.append(slog(Q))
        for i in range(len(poly_xs) - 1):
            bg_poly_segs.append([(poly_xs[i], poly_ys[i]),
                                  (poly_xs[i + 1], poly_ys[i + 1])])

    ax.add_collection(LineCollection(
        bg_warm_segs, colors=[(*WARM, 0.10)], linewidths=0.55,
        zorder=2,
    ))
    ax.add_collection(LineCollection(
        bg_cool_segs, colors=[(*COOL, 0.10)], linewidths=0.55,
        zorder=2,
    ))
    ax.add_collection(LineCollection(
        bg_poly_segs, colors=[(0.92, 0.95, 1.00, 0.07)], linewidths=0.6,
        zorder=3,
    ))
    ax.scatter(bg_q_x, bg_q_y, s=2.2, c=[(1.0, 1.0, 1.0, 0.18)],
               zorder=4, linewidths=0)

    # ---- foreground: highlighted canonical k ----

    highlights = [
        (1,   'k=1',    (1.00, 0.84, 0.30)),  # gold
        (5,   'k=5',    (0.50, 1.00, 0.70)),  # mint
        (25,  'k=25',   (0.95, 0.55, 1.00)),  # magenta
        (35,  'k=5·7',  (0.40, 0.85, 1.00)),  # cyan
        (49,  'k=7²',   (1.00, 0.55, 0.55)),  # red-pink
        (125, 'k=5³',   (1.00, 0.85, 0.55)),  # peach (cube, distinct shape)
    ]

    annotations = []
    for k_canon, label, color in highlights:
        if k_canon not in data:
            continue
        k_idx = payloads.index(k_canon)
        poly_xs = []
        poly_ys = []
        for n_idx, n in enumerate(PANEL_NS):
            P, N, Q = data[k_canon][n]
            x = x_pos(n_idx, k_idx)
            ax.plot([x, x], [0, slog(P)], color=(*WARM, 0.92),
                    lw=3.4, solid_capstyle='round', zorder=5)
            ax.plot([x, x], [0, -slog(N)], color=(*COOL, 0.92),
                    lw=3.4, solid_capstyle='round', zorder=5)
            poly_xs.append(x)
            poly_ys.append(slog(Q))

        ax.plot(poly_xs, poly_ys,
                color=(*color, 0.95), lw=2.4, zorder=7,
                solid_capstyle='round', label=label)
        ax.scatter(poly_xs, poly_ys,
                   s=120, c=[(*color, 1.0)],
                   edgecolors=[(0.0, 0.0, 0.0, 0.95)], linewidths=1.2,
                   zorder=8)

        # Collect for collision-resolved annotation pass below.
        last_idx = len(PANEL_NS) - 1
        annotations.append({
            'x': poly_xs[last_idx],
            'y_orig': poly_ys[last_idx],
            'Q': data[k_canon][PANEL_NS[last_idx]][2],
            'color': color,
        })

    # Annotate Q values at the rightmost (n=12) endpoint with collision
    # resolution: sort by y descending, enforce a minimum vertical
    # separation, and draw a thin leader line back to the original Q dot.
    annotations.sort(key=lambda d: -d['y_orig'])
    min_sep = 0.13  # in slog units
    for i, a in enumerate(annotations):
        a['y'] = a['y_orig']
    for i in range(1, len(annotations)):
        prev_y = annotations[i - 1]['y']
        if annotations[i]['y'] > prev_y - min_sep:
            annotations[i]['y'] = prev_y - min_sep
    for a in annotations:
        Q = a['Q']
        label_text = f'{Q:+.0f}' if abs(Q) >= 1 else f'{Q:+.2f}'
        if abs(a['y'] - a['y_orig']) > 1e-3:
            ax.plot(
                [a['x'] + 0.04, a['x'] + 0.13],
                [a['y_orig'], a['y']],
                color=(*a['color'], 0.45), lw=0.6, zorder=8.5,
            )
        ax.text(
            a['x'] + 0.16, a['y'],
            label_text,
            color=(*a['color'], 0.98), fontsize=11, ha='left', va='center',
            fontweight='bold', zorder=9,
            bbox=dict(facecolor=(0.05, 0.06, 0.07, 0.78),
                      edgecolor=(*a['color'], 0.50), linewidth=0.8, pad=1.5,
                      boxstyle='round,pad=0.3'),
        )

    # Zero line.
    ax.axhline(0.0, color=(0.95, 0.97, 1.00, 0.40), lw=0.8, zorder=1)

    # ---- axes cosmetics ----

    ax.set_xticks(n_centers)
    ax.set_xticklabels(
        [f'n = {n}\n({t})' for n, t in zip(PANEL_NS, N_TYPES)],
        fontsize=12, color=TICK_COLOR,
    )
    ax.tick_params(axis='x', length=0)
    ax.set_xlim(n_centers[0] - 1.0, n_centers[-1] + 1.4)

    # symlog y ticks at -1000, -100, -10, -1, 0, 1, 10, 100, 1000.
    tick_values = [-1000, -100, -10, -1, 0, 1, 10, 100, 1000]
    tick_locs = [slog(v) for v in tick_values]
    tick_labels = [f'{v:+d}' if v != 0 else '0' for v in tick_values]
    ax.set_yticks(tick_locs)
    ax.set_yticklabels(tick_labels, fontsize=10, color=TICK_COLOR)
    ax.set_ylim(slog(-2500), slog(2500))

    for spine in ax.spines.values():
        spine.set_color((0.40, 0.45, 0.50, 0.45))
        spine.set_linewidth(0.8)
    ax.grid(True, axis='y', color=(0.30, 0.34, 0.38), alpha=0.18, lw=0.5)

    # Column dividers (faint).
    for i in range(len(PANEL_NS) - 1):
        x_div = (n_centers[i] + n_centers[i + 1]) * 0.5
        ax.axvline(x_div, color=(0.30, 0.34, 0.40, 0.30),
                   lw=0.7, ls=':', zorder=0.5)

    # Title and subtitle.
    fig.text(
        0.5, 0.965,
        'Q_n at h = 5 — towers and trajectories',
        ha='center', va='top', color=(1.0, 1.0, 1.0, 0.95),
        fontsize=22, fontweight='bold', family='serif',
    )
    fig.text(
        0.5, 0.940,
        'tower at (n, k):  Σ|term_j| split warm (j odd) above, cool (j even) below.   '
        'polyline:  Q_n(n^5·k) across n = 2, 4, 6, 12 at fixed k.',
        ha='center', va='top', color=(0.80, 0.85, 0.92, 0.62),
        fontsize=11, fontstyle='italic',
    )

    # Legend.
    leg = ax.legend(
        loc='lower left', fontsize=10, framealpha=0.85,
        facecolor=(0.05, 0.06, 0.08, 0.85),
        edgecolor=(0.30, 0.36, 0.42, 0.50),
        labelcolor=(0.92, 0.95, 1.00, 1.0),
        ncol=3,
    )

    # Reading hint, parked in the upper-right where the data is sparsest.
    ax.text(
        0.985, 0.975,
        'tall tower → lots of cancellation mass.\n'
        'polyline far from 0 within tower → residual escapes.\n'
        'polyline pinned to 0 → full cancellation.',
        transform=ax.transAxes, fontsize=9.5,
        color=(0.78, 0.85, 0.92, 0.62), fontstyle='italic',
        ha='right', va='top',
        linespacing=1.35,
    )

    plt.subplots_adjust(left=0.06, right=0.97, top=0.91, bottom=0.07)
    plt.savefig(OUT, facecolor=DARK)
    plt.close()
    print(f'-> {OUT}')


if __name__ == '__main__':
    main()
