"""
q_merger_345.py - Q_n towers and trajectories across h in {3, 4, 5}.

Three stacked panels. Each panel: faint background towers per (n, k)
showing pre-cancellation mass, with highlighted-k polylines connecting
Q_n through those towers across the four n positions, ordered by
(omega(n), Omega(n)) - prime-structure of n, which is the actual axis
the master expansion responds to.

h=1 (trivially Q_n=1) and h=2 (n-independent formula 1 - d(k)/2)
are dropped - they don't reward the canvas space.

Highlighted k's labelled by tau-signature so structural identities
are visible: k=25 [p^2] and k=49 [p^2] produce identical Q at every
(n, h) - they are the same point in the visualisation, not two
points coincidentally aligned.

At every prime n at h=5, the coefficient pattern (+1, -2, +2, -1,
+1/5) annihilates polynomials of degree 1..4 in j. Since tau_j(p^e)
is degree e in j, Q_p(p^5 k) = 0 for any k coprime to p with
Omega(k) in [1, 4]. The n=2 column at h=5 shows five highlighted
k's stacked on the zero line for this reason - a stated identity,
not a clustering coincidence. The same identity does NOT hold at
h=3 or h=4 (different coefficient patterns) - hence the qualitative
shape difference between the three panels.
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
OUT = os.path.join(HERE, 'q_merger_345.png')

PANEL_NS = [2, 4, 6, 12]
H_VALUES = [3, 4, 5]
K_MAX = 300

DARK = '#0a0a0a'
WARM = (1.00, 0.66, 0.30)
COOL = (0.45, 0.78, 1.00)
TICK_COLOR = (0.78, 0.82, 0.88, 0.75)
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

    data = {}
    for h in H_VALUES:
        data[h] = {k: {n: pn_q(n, h, k) for n in PANEL_NS} for k in payloads}

    n_centers = np.arange(len(PANEL_NS), dtype=float) * 1.6
    column_half_width = 0.58
    log_ks = np.log(np.array(payloads))
    lk_min, lk_max = log_ks.min(), log_ks.max()
    lk_norm = (
        (log_ks - lk_min) / (lk_max - lk_min)
        if lk_max > lk_min else np.zeros_like(log_ks)
    )

    def x_pos(n_idx, k_idx):
        return (
            n_centers[n_idx]
            - column_half_width
            + 2 * column_half_width * lk_norm[k_idx]
        )

    # k labelled by tau-signature in the legend below.
    highlights = [
        (1,   (1.00, 0.84, 0.30)),  # gold
        (5,   (0.50, 1.00, 0.70)),  # mint
        (25,  (0.95, 0.55, 1.00)),  # magenta
        (35,  (0.40, 0.85, 1.00)),  # cyan
        (49,  (1.00, 0.55, 0.55)),  # red-pink
        (125, (1.00, 0.85, 0.55)),  # peach
    ]

    fig = plt.figure(figsize=(14, 18), dpi=180, facecolor=DARK)
    gs = fig.add_gridspec(
        nrows=len(H_VALUES) + 1, ncols=1,
        height_ratios=[1.0] * len(H_VALUES) + [0.08],
        hspace=0.08, left=0.10, right=0.97, top=0.97, bottom=0.04,
    )

    for h_idx, h in enumerate(H_VALUES):
        ax = fig.add_subplot(gs[h_idx, 0])
        ax.set_facecolor(DARK)

        # Background towers (no background polylines - too noisy).
        bg_warm = []
        bg_cool = []
        for k_idx, k in enumerate(payloads):
            for n_idx, n in enumerate(PANEL_NS):
                P, N, _ = data[h][k][n]
                x = x_pos(n_idx, k_idx)
                bg_warm.append([(x, 0.0), (x, slog(P))])
                bg_cool.append([(x, 0.0), (x, -slog(N))])

        ax.add_collection(LineCollection(
            bg_warm, colors=[(*WARM, 0.10)], linewidths=0.55, zorder=2,
        ))
        ax.add_collection(LineCollection(
            bg_cool, colors=[(*COOL, 0.10)], linewidths=0.55, zorder=2,
        ))

        # Foreground: highlighted k's only.
        for k_canon, color in highlights:
            if k_canon not in data[h]:
                continue
            k_idx = payloads.index(k_canon)
            poly_xs = []
            poly_ys = []
            for n_idx, n in enumerate(PANEL_NS):
                P, N, Q = data[h][k_canon][n]
                x = x_pos(n_idx, k_idx)
                ax.plot([x, x], [0, slog(P)],
                        color=(*WARM, 0.92), lw=3.2,
                        solid_capstyle='round', zorder=5)
                ax.plot([x, x], [0, -slog(N)],
                        color=(*COOL, 0.92), lw=3.2,
                        solid_capstyle='round', zorder=5)
                poly_xs.append(x)
                poly_ys.append(slog(Q))

            ax.plot(poly_xs, poly_ys,
                    color=(*color, 0.95), lw=2.2, zorder=7,
                    solid_capstyle='round')
            ax.scatter(poly_xs, poly_ys,
                       s=95, c=[(*color, 1.0)],
                       edgecolors=[(0.0, 0.0, 0.0, 0.95)], linewidths=1.0,
                       zorder=8)

        # Zero line.
        ax.axhline(0.0, color=(0.95, 0.97, 1.00, 0.30), lw=0.7, zorder=1)

        # Per-panel y range.
        all_pn = [
            max(data[h][k][n][0], data[h][k][n][1])
            for k in payloads for n in PANEL_NS
        ]
        max_mag = max(all_pn)
        ax.set_ylim(-slog(max_mag * 1.5), slog(max_mag * 1.5))

        # Minimal y-ticks: just 3 levels per panel.
        if max_mag <= 15:
            tick_values = [10, 1]
        elif max_mag <= 150:
            tick_values = [100, 10, 1]
        else:
            tick_values = [1000, 100, 10, 1]
        tick_locs = [slog(v) for v in tick_values] + [0] + [-slog(v) for v in tick_values]
        tick_labels = (
            [f'+{v}' for v in tick_values]
            + ['0']
            + [f'-{v}' for v in tick_values]
        )
        ax.set_yticks(tick_locs)
        ax.set_yticklabels(tick_labels, fontsize=9, color=TICK_COLOR)

        # Faint horizontal gridlines tied to the symlog tick locations,
        # so the reader can pick a value off without a per-panel title
        # to anchor scale; explicit zorder keeps them under the data.
        ax.grid(
            True, axis='y',
            color=(0.30, 0.34, 0.40), alpha=0.16, lw=0.4, zorder=0.4,
        )

        # X-axis: ticks only on bottom panel. Annotated with Omega(n)
        # (total prime exponent) to name the ordering principle of the
        # polylines explicitly - the polyline is a path along
        # (omega, Omega) of n, the structural axis of the master
        # expansion.
        omega_str = lambda n: str(sum(e for _p, e in factor_tuple(n)))
        ax.set_xticks(n_centers)
        if h_idx == len(H_VALUES) - 1:
            ax.set_xticklabels(
                [f'n = {n}\nΩ = {omega_str(n)}' for n in PANEL_NS],
                fontsize=14, color=LABEL_COLOR,
            )
        else:
            ax.set_xticklabels([])
        ax.tick_params(axis='x', length=0)
        ax.set_xlim(n_centers[0] - 0.85, n_centers[-1] + 0.85)

        for spine in ax.spines.values():
            spine.set_color((0.35, 0.40, 0.45, 0.40))
            spine.set_linewidth(0.7)

    # h-labels in figure coords.
    for h_idx, h in enumerate(H_VALUES):
        bbox = fig.axes[h_idx].get_position()
        fig.text(
            bbox.x0 - 0.018,
            (bbox.y0 + bbox.y1) * 0.5,
            f'h = {h}',
            fontsize=34, fontweight='bold',
            color=LABEL_COLOR, ha='right', va='center',
        )

    # Bottom legend strip.
    leg_ax = fig.add_subplot(gs[-1, 0])
    leg_ax.set_facecolor(DARK)
    leg_ax.set_xlim(0, 1)
    leg_ax.set_ylim(0, 1)
    leg_ax.set_axis_off()

    # tau-signature in brackets after each k makes structural
    # equivalences readable from the legend alone: k=25 and k=49 are
    # both [p^2], hence identical Q at every (n, h).
    canon_labels = [
        'k=1  [const]',
        'k=5  [p]',
        'k=25 [p²]',
        'k=5·7 [pq]',
        'k=7² [p²]',
        'k=5³ [p³]',
    ]
    canon_colors = [c for _, c in highlights]
    legend_x_step = 0.155
    legend_x_start = (1 - (len(canon_labels) - 1) * legend_x_step) * 0.5 - 0.04
    for i, (label, color) in enumerate(zip(canon_labels, canon_colors)):
        x = legend_x_start + i * legend_x_step
        leg_ax.scatter([x], [0.5], s=140, c=[(*color, 1.0)],
                       edgecolors=[(0.0, 0.0, 0.0, 0.95)], linewidths=1.0)
        leg_ax.text(x + 0.020, 0.5, label,
                    color=(0.85, 0.92, 1.00, 0.92),
                    fontsize=13, va='center')

    plt.savefig(OUT, facecolor=DARK)
    plt.close()
    print(f'-> {OUT}')


if __name__ == '__main__':
    main()
