"""
q_towers.py - pre-cancellation towers.

For each (n, h, k) coprime to lcm(panel-n's) = 12, decompose the
master Mercator sum into:

    P = sum of |term_j| for j odd  (positive mass before cancellation)
    N = sum of |term_j| for j even (negative mass before cancellation)
    Q_n(n^h k) = P - N             (the signed surviving residual)

Each (n, h, k) is rendered as a vertical bar from y = -N to y = +P,
with the warm region above y = 0 and cool region below. A white dot
marks y = Q_n - the actual survivor of the cancellation.

The visual claim: hierarchy reads as tower height (P + N), not as
the final Q_n. Cells with rich payloads have enormous P and N that
nearly cancel. Cells with simple payloads have small P, N that
don't cancel much. The "violation" of n-hierarchy emerges when a
prime cell at rich k has taller towers than a mixed cell at simple
k - the complexity is in the cancellation, not in the surviving
value.

Reading the grid:

  - h = 1 row: trivial. P = 1, N = 0 always. Towers are unit-height
    warm spikes; Q_n dot sits at the top. No cancellation.
  - h = 2 row: small towers (P = 1, N = d(k)/2). Q_n at top of warm
    region or in cool region depending on d(k).
  - h = 3+ rows: towers grow rapidly with both n and k. The white
    dots stay close to y = 0 - showing that Q_n is a sliver of the
    pre-cancellation mass.

Per-row y-axis is shared across the four n columns so tower heights
compare directly across n at fixed h.
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
OUT = os.path.join(HERE, 'q_towers.png')

PANEL_NS = [2, 4, 6, 12]
N_TYPES = ['prime', 'prime power', 'squarefree', 'mixed']
H_VALUES = [1, 2, 3, 4, 5]
K_MAX = 300

DARK = '#0a0a0a'
WARM = (1.00, 0.66, 0.30)   # positive contributions
COOL = (0.45, 0.78, 1.00)   # negative contributions
WHITE = (0.98, 0.98, 1.00)
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


def pn_masses(n, h, k):
    """For Q_n(n^h k) with k coprime to n, return (P, N) the positive
    and negative pre-cancellation mass."""
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
    return P, N


def panel_lcm():
    L = 1
    for n in PANEL_NS:
        L = lcm(L, n)
    return L


def collect():
    L = panel_lcm()
    payloads = [k for k in range(1, K_MAX + 1) if gcd(k, L) == 1]
    cells = {}
    for n in PANEL_NS:
        for h in H_VALUES:
            data = []
            for k in payloads:
                P, N = pn_masses(n, h, k)
                data.append((k, P, N, P - N))
            cells[(n, h)] = data
    return payloads, cells


def symlog_transform(y, linthresh=1.0):
    """Manual symlog so we can plot bars segment-by-segment."""
    return np.sign(y) * np.log10(1.0 + np.abs(y) / linthresh)


def draw_cell(ax, n, h, data, y_max_row, is_top_row, is_left_col,
              n_label, n_subtype):
    """Render one (n, h) cell with ~100 vertical bars."""
    # Sort by k for a stable x-axis.
    data = sorted(data, key=lambda r: r[0])
    ks = np.array([r[0] for r in data])
    Ps = np.array([r[1] for r in data])
    Ns = np.array([r[2] for r in data])
    Qs = np.array([r[3] for r in data])

    # x = log(k); spread across cell.
    log_ks = np.log(ks)
    x_lo, x_hi = log_ks.min(), log_ks.max()
    if x_hi == x_lo:
        x_norm = np.zeros_like(log_ks)
    else:
        x_norm = (log_ks - x_lo) / (x_hi - x_lo)

    # Symlog the y values so all rows can share a scale shape.
    P_t = symlog_transform(Ps)
    N_t = symlog_transform(-Ns)  # negative direction
    Q_t = symlog_transform(Qs)

    # Bar segments: warm from (x, 0) to (x, +P_t); cool from (x, 0) to (x, -N_t).
    warm_segs = [[(x, 0.0), (x, p)] for x, p in zip(x_norm, P_t)]
    cool_segs = [[(x, 0.0), (x, n_)] for x, n_ in zip(x_norm, N_t)]

    # Bar widths scale with k spacing - thin enough to see ~100 bars.
    bar_lw = max(0.8, min(2.4, 240.0 / len(ks)))

    ax.add_collection(LineCollection(
        warm_segs, colors=[(*WARM, 0.85)], linewidths=bar_lw,
        capstyle='butt', zorder=3,
    ))
    ax.add_collection(LineCollection(
        cool_segs, colors=[(*COOL, 0.85)], linewidths=bar_lw,
        capstyle='butt', zorder=3,
    ))

    # White Q_n dots: the sliver that survives. Drawn larger so the
    # cancellation residual is the most prominent feature.
    ax.scatter(
        x_norm, Q_t,
        s=22.0, c=[(*WHITE, 0.98)],
        marker='o', linewidths=0.6,
        edgecolors=[(0.05, 0.05, 0.06, 0.9)],
        zorder=6,
    )

    # Median total-mass curve: P + N median across this cell, drawn as
    # a horizontal line so the cell's "characteristic tower height"
    # reads at a glance.
    median_total = float(np.median(Ps + Ns))
    median_y = symlog_transform(median_total)
    ax.axhline(median_y, color=(*WARM, 0.30), lw=1.0, ls='--', zorder=2)
    ax.axhline(-median_y, color=(*COOL, 0.30), lw=1.0, ls='--', zorder=2)

    # Annotate the median total mass and the median |Q_n| in the cell
    # corner so the cancellation ratio is readable.
    median_q = float(np.median(np.abs(Qs)))
    if median_total > 0:
        cancel_ratio = 1.0 - median_q / median_total
    else:
        cancel_ratio = 0.0
    ax.text(
        0.97, 0.04,
        f'P+N med  {median_total:.2g}\n'
        f'|Q|  med  {median_q:.2g}\n'
        f'cancel    {cancel_ratio*100:.0f}%',
        transform=ax.transAxes, ha='right', va='bottom',
        fontsize=10, color=(0.85, 0.92, 1.00, 0.85),
        family='monospace',
        bbox=dict(facecolor=(0.05, 0.06, 0.07, 0.65),
                  edgecolor=(0.30, 0.36, 0.42, 0.40),
                  linewidth=0.5, pad=3.5,
                  boxstyle='round,pad=0.3'),
        zorder=7,
    )

    # Zero line.
    ax.axhline(0.0, color=(0.95, 0.97, 1.00, 0.40), lw=0.7, zorder=1)

    # Cosmetics.
    ax.set_facecolor(DARK)
    for spine in ax.spines.values():
        spine.set_color((0.40, 0.45, 0.50, 0.45))
        spine.set_linewidth(0.8)

    ax.set_xlim(-0.04, 1.04)
    # Per-row y-limits: based on max P+N across the row.
    y_limit = symlog_transform(y_max_row * 1.15)
    ax.set_ylim(-y_limit, y_limit)
    ax.set_xticks([])

    # y-tick marks: choose 3 symlog levels per row.
    tick_values = []
    for v in [1, 10, 100, 1000, 10000]:
        if v <= y_max_row * 1.5:
            tick_values.append(v)
    tick_locs = [symlog_transform(v) for v in tick_values]
    tick_locs += [-t for t in tick_locs]
    tick_labels = [f'+{v}' for v in tick_values] + [f'-{v}' for v in tick_values]
    if is_left_col:
        ax.set_yticks(tick_locs)
        ax.set_yticklabels(tick_labels, fontsize=7,
                           color=TICK_COLOR)
    else:
        ax.set_yticks(tick_locs)
        ax.set_yticklabels([])

    # Column header (top of column).
    if is_top_row:
        ax.text(
            0.5, 1.18, f'n = {n_label}',
            transform=ax.transAxes, fontsize=18, fontweight='bold',
            color=LABEL_COLOR, ha='center', va='bottom',
        )
        ax.text(
            0.5, 1.04, n_subtype,
            transform=ax.transAxes, fontsize=11, fontstyle='italic',
            color=(0.78, 0.84, 0.92, 0.80), ha='center', va='bottom',
        )


def build():
    payloads, cells = collect()
    print(f'Computed P, N, Q across {len(payloads)} payloads and '
          f'{len(PANEL_NS) * len(H_VALUES)} (n, h) cells.')

    # Per-row max(P + N) for shared y-scale within each h row.
    row_max = {}
    for h in H_VALUES:
        m = 0.0
        for n in PANEL_NS:
            for (_, P, N, _) in cells[(n, h)]:
                m = max(m, P + N)
        row_max[h] = m

    fig = plt.figure(figsize=(14, 17), dpi=180, facecolor=DARK)
    gs = fig.add_gridspec(
        nrows=len(H_VALUES), ncols=len(PANEL_NS),
        wspace=0.10, hspace=0.32,
        left=0.10, right=0.97, top=0.88, bottom=0.06,
    )

    cat_subtitles = dict(zip(PANEL_NS, N_TYPES))

    for h_idx, h in enumerate(H_VALUES):
        for n_idx, n in enumerate(PANEL_NS):
            ax = fig.add_subplot(gs[h_idx, n_idx])
            draw_cell(
                ax, n, h, cells[(n, h)],
                y_max_row=row_max[h],
                is_top_row=(h_idx == 0),
                is_left_col=(n_idx == 0),
                n_label=str(n),
                n_subtype=cat_subtitles[n],
            )

        # Row label "h = N" outside leftmost cell.
        bbox = fig.axes[h_idx * len(PANEL_NS)].get_position()
        fig.text(
            bbox.x0 - 0.020, (bbox.y0 + bbox.y1) * 0.5,
            f'h = {h}',
            fontsize=24, fontweight='bold',
            color=LABEL_COLOR, ha='right', va='center',
        )

    # Title and subtitle.
    fig.text(
        0.5, 0.985,
        'pre-cancellation towers',
        ha='center', va='top', color=(1.0, 1.0, 1.0, 0.95),
        fontsize=22, fontweight='bold',
    )
    fig.text(
        0.5, 0.964,
        'each bar: one payload k coprime to 12. '
        'warm above 0 = $\\Sigma|term_j|$ for j odd; '
        'cool below 0 = $\\Sigma|term_j|$ for j even. '
        'white dot = $Q_n$, the sliver that survives.',
        ha='center', va='top', color=(0.80, 0.85, 0.92, 0.65),
        fontsize=11, fontstyle='italic',
    )

    # Footer legend.
    fig.text(
        0.5, 0.020,
        'corner stats per cell: median(P+N), median(|Q|), '
        'and cancellation % = 1 - median(|Q|) / median(P+N). '
        'high % = lots of cancellation, small surviving residual. '
        'dashed lines: $\\pm$median(P+N) per cell.',
        ha='center', va='bottom', color=(0.78, 0.85, 0.92, 0.55),
        fontsize=10, fontstyle='italic',
    )

    plt.savefig(OUT, facecolor=DARK)
    plt.close()
    print(f'-> {OUT}')


if __name__ == '__main__':
    build()
