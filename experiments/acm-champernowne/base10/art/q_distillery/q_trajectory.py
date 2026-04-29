"""
q_trajectory.py - k-trajectories through n-space.

For each payload k coprime to lcm(panel-n's) = 12, at each rank h in 1..5,
draw a polyline through the four points (n_index, Q_n(n^h * k)) for
n in {2, 4, 6, 12}. One panel per h. The polyline shape is the
hierarchy claim made into a visual primitive.

The visual story across the 5 panels:

  - h=1: all polylines flat at y=1 (Q_n is identically 1 - no hierarchy
    to show).
  - h=2: all polylines flat at y = 1 - d(k)/2 (the formula is
    n-independent at h=2 - hierarchy is null).
  - h=3+: polylines fan out by n type. k modulates the shape -
    sometimes monotone descent (hierarchy honored), sometimes
    step-shaped (primes/prime-powers cluster, squarefree/mixed
    cluster), sometimes sign-flips between adjacent n (hierarchy
    inverts).

Polylines are colored by the sign-flip count along (Q_2, Q_4, Q_6, Q_12):
  - 0 flips: faint cool (hierarchy honored, possibly inverted but
    consistent in sign).
  - 1 flip: orange (clean violation - the polyline crosses zero once).
  - 2+ flips: red (severe violation - sign oscillates).

A few canonical k are highlighted explicitly: k=1 (empty payload),
k=5 (single prime), k=25 (prime squared), k=35 (two distinct primes).
The median trajectory across all k is overlaid in white as the
"central tendency" the hierarchy would predict.
"""

import os
from functools import lru_cache
from math import comb, gcd, lcm

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'q_trajectory.png')

PANEL_NS = [2, 4, 6, 12]
H_VALUES = [1, 2, 3, 4, 5]
K_MAX = 300

DARK = '#0a0a0a'
GRID = (0.30, 0.34, 0.38, 0.18)
TICK_COLOR = (0.85, 0.88, 0.92, 0.85)
LABEL_COLOR = (0.95, 0.97, 1.00, 0.92)


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


def q_coprime(n, h, k):
    """Q_n(n^h * k) for k coprime to n. Master expansion with all t_i = 0."""
    factors = factor_tuple(n)
    total = 0.0
    for j in range(1, h + 1):
        coeff = 1
        for (_p, a) in factors:
            coeff *= comb(a * (h - j) + j - 1, j - 1)
        sign = 1 if j % 2 == 1 else -1
        total += sign * coeff * tau(j, k) / j
    return total


def panel_lcm():
    L = 1
    for n in PANEL_NS:
        L = lcm(L, n)
    return L


def collect_trajectories():
    L = panel_lcm()  # = 12
    payloads = [k for k in range(1, K_MAX + 1) if gcd(k, L) == 1]
    traj = {}
    for h in H_VALUES:
        rows = np.array([
            [q_coprime(n, h, k) for n in PANEL_NS] for k in payloads
        ])
        traj[h] = rows
    return payloads, traj


def sign_flip_count(row):
    flips = 0
    for i in range(len(row) - 1):
        a = row[i]
        b = row[i + 1]
        if a == 0 or b == 0:
            continue  # zero crossings counted only when sign actually flips
        if (a > 0) != (b > 0):
            flips += 1
    return flips


def draw_panel(ax, h, payloads, Y, is_top, is_bottom):
    n_payloads = len(payloads)
    x_positions = np.arange(len(PANEL_NS))

    flip_counts = np.array([sign_flip_count(Y[r]) for r in range(n_payloads)])

    # Plot order: 0-flip first (background), then 1-flip, then 2+-flip on top.
    order_buckets = [
        (0, (0.50, 0.72, 1.00, 0.42), 0.85),  # cool blue, more visible
        (1, (1.00, 0.65, 0.30, 0.65), 1.20),  # orange
    ]

    for fc_value, color, lw in order_buckets:
        mask = flip_counts == fc_value
        for r in np.where(mask)[0]:
            ax.plot(x_positions, Y[r], color=color, lw=lw, zorder=2 + fc_value,
                    solid_capstyle='round')

    # 2+ flips on top.
    mask = flip_counts >= 2
    for r in np.where(mask)[0]:
        ax.plot(x_positions, Y[r], color=(1.00, 0.36, 0.36, 0.80),
                lw=1.50, zorder=4, solid_capstyle='round')

    # Median trajectory.
    median = np.median(Y, axis=0)
    ax.plot(x_positions, median, color=(1.0, 1.0, 1.0, 0.85),
            lw=2.2, ls='--', zorder=6, marker='o', ms=6,
            markerfacecolor=(1.0, 1.0, 1.0, 0.95),
            markeredgecolor=(0.20, 0.22, 0.25, 1.0),
            markeredgewidth=0.8)

    # Highlight a few canonical k.
    canon = [
        (1,  '$k{=}1$',         (1.00, 0.84, 0.30)),  # gold
        (5,  '$k{=}5$',         (0.50, 1.00, 0.70)),  # mint
        (25, '$k{=}25$',        (0.95, 0.55, 1.00)),  # magenta
        (35, '$k{=}5{\\cdot}7$', (0.40, 0.85, 1.00)), # cyan
    ]
    for k_canon, label, color in canon:
        if k_canon not in payloads:
            continue
        idx = payloads.index(k_canon)
        ax.plot(x_positions, Y[idx],
                color=(*color, 0.95), lw=1.9, zorder=7,
                marker='o', ms=7,
                markerfacecolor=(*color, 1.0),
                markeredgecolor=(0.05, 0.05, 0.07, 1.0),
                markeredgewidth=0.6,
                label=label if is_top else None)

    # Zero line.
    ax.axhline(0, color=(0.85, 0.88, 0.92, 0.30), lw=0.7, ls='-', zorder=1)

    # Y scale: symlog so sign + magnitude both legible.
    ymax = max(abs(Y.max()), abs(Y.min()), 1.0)
    if ymax < 2:
        ax.set_yscale('linear')
        ax.set_ylim(-1.5 * ymax - 0.2, 1.5 * ymax + 0.2)
    else:
        ax.set_yscale('symlog', linthresh=1.0)
        ax.set_ylim(-2.0 * ymax, 2.0 * ymax)

    # Axes cosmetics.
    for spine in ax.spines.values():
        spine.set_color((0.45, 0.50, 0.55, 0.50))
        spine.set_linewidth(0.8)
    ax.tick_params(axis='both', colors=TICK_COLOR, labelsize=11)
    ax.grid(True, color=GRID[:3], alpha=GRID[3], lw=0.5)
    ax.set_facecolor(DARK)

    ax.set_xticks(x_positions)
    if is_bottom:
        ax.set_xticklabels(
            [f'n={n}\n({label})' for n, label in zip(
                PANEL_NS, ['prime', 'prime power', 'squarefree', 'mixed']
            )],
            fontsize=11, color=TICK_COLOR,
        )
    else:
        ax.set_xticklabels([])

    # h label on the left, in figure coords so it's positioned absolutely
    # rather than relative to the axes box.
    bbox = ax.get_position()
    fig_x = bbox.x0 - 0.015
    fig_y = (bbox.y0 + bbox.y1) * 0.5
    ax.figure.text(
        fig_x, fig_y, f'h = {h}',
        fontsize=28, fontweight='bold', color=LABEL_COLOR,
        ha='right', va='center', zorder=10,
    )

    # Annotation per panel describing the regime.
    regime = {
        1: 'flat at $Q_n=1$  -  no hierarchy',
        2: 'flat at $1-d(k)/2$  -  hierarchy null (n-independent formula)',
        3: 'fan emerges  -  hierarchy concedes structure',
        4: 'step-shaped clusters  -  primes $\\sim$ prime-powers,'
           ' squarefree $\\sim$ mixed',
        5: 'tangled  -  k structure swamps n hierarchy',
    }
    ax.text(0.99, 0.96, regime[h],
            transform=ax.transAxes, fontsize=11, ha='right', va='top',
            color=(0.80, 0.85, 0.92, 0.75), style='italic')


def build_legend_axis(ax):
    ax.set_facecolor(DARK)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()

    swatches = [
        ((0.45, 0.65, 0.95, 0.55), 'no sign flips along (Q_2, Q_4, Q_6, Q_12)'),
        ((1.00, 0.65, 0.30, 0.85), '1 sign flip - clean hierarchy violation'),
        ((1.00, 0.36, 0.36, 0.85), '2+ sign flips - severe / non-monotone'),
        ((1.0, 1.0, 1.0, 0.95),    'white dashed: median trajectory'),
    ]
    for i, (color, label) in enumerate(swatches):
        x = 0.04 + (i % 2) * 0.50
        y = 0.75 - (i // 2) * 0.45
        ax.plot([x, x + 0.04], [y, y], color=color, lw=2.0,
                ls='--' if 'median' in label else '-')
        ax.text(x + 0.06, y, label, color=(0.85, 0.90, 0.95, 0.85),
                fontsize=11, va='center')

    canon = [
        ('$k{=}1$',          (1.00, 0.84, 0.30)),
        ('$k{=}5$',          (0.50, 1.00, 0.70)),
        ('$k{=}25$',         (0.95, 0.55, 1.00)),
        ('$k{=}5{\\cdot}7$', (0.40, 0.85, 1.00)),
    ]
    for i, (label, color) in enumerate(canon):
        x = 0.04 + i * 0.24
        y = 0.18
        ax.plot([x], [y], 'o', color=color, ms=8,
                markeredgecolor=(0.05, 0.05, 0.07, 1.0), markeredgewidth=0.6)
        ax.text(x + 0.02, y, label,
                color=(0.85, 0.90, 0.95, 0.85), fontsize=11, va='center')


def main():
    payloads, traj = collect_trajectories()
    print(f'Collected {len(payloads)} k-trajectories coprime to {panel_lcm()}.')

    fig = plt.figure(
        figsize=(14, 18), dpi=180,
        facecolor=DARK,
    )
    gs = fig.add_gridspec(
        nrows=len(H_VALUES) + 1, ncols=1,
        height_ratios=[1.0] * len(H_VALUES) + [0.32],
        hspace=0.22, left=0.13, right=0.97, top=0.95, bottom=0.05,
    )

    axes = []
    for i, h in enumerate(H_VALUES):
        ax = fig.add_subplot(gs[i, 0])
        axes.append(ax)
        draw_panel(
            ax, h, payloads, traj[h],
            is_top=(i == 0),
            is_bottom=(i == len(H_VALUES) - 1),
        )

    # Title.
    fig.text(
        0.5, 0.985,
        'k-trajectories through n-space',
        ha='center', va='top', color=(1.0, 1.0, 1.0, 0.95),
        fontsize=22, fontweight='bold',
    )
    fig.text(
        0.5, 0.964,
        'each line: $Q_n(n^h k)$ across $n \\in \\{2, 4, 6, 12\\}$ '
        'for one fixed payload $k$ coprime to 12',
        ha='center', va='top', color=(0.80, 0.85, 0.92, 0.65),
        fontsize=12, style='italic',
    )

    legend_ax = fig.add_subplot(gs[-1, 0])
    build_legend_axis(legend_ax)

    plt.savefig(OUT, facecolor=DARK)
    plt.close()
    print(f'-> {OUT}')


if __name__ == '__main__':
    main()
