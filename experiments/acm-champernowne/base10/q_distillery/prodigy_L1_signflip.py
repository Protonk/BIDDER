"""
prodigy_L1_signflip.py — emblem render for wonders/prodigy-L1-cliff-n2-h8.md.

Single-panel bar chart of the vertical L=1 autocorrelation across h.
"Vertical L=1" = mean Pearson correlation between row_n and row_{n+1}
of the (n, k) lattice at fixed h, where row_n is k → Q_n(n^h · k).

Published values in ATTRACTOR-AND-MIRAGE.md:612-615 cover h ∈ {5, 6, 7, 8}
and report ≈ +0.25 at odd h and ≈ −0.14 at even h. This emblem extends
to h ∈ {3..10} to show whether the alternation continues. Computation
is analytic via algebra/predict_q.q_general; no lattice required.

Note. The grid here (n ∈ [2, 50], k ∈ [1, 200]) is smaller than the
published lattice (n_max ≈ 3999, K = 4000). The sign pattern is
structural (first-order reading: master expansion's (-1)^(j-1) at
deepest rank j = h) and should reproduce; the magnitudes will shift
by a few percent from the published ~+0.25 / ~−0.14.

Run: sage -python experiments/acm-champernowne/base10/q_distillery/prodigy_L1_signflip.py
"""

from __future__ import annotations

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
# q_distillery -> base10 -> acm-champernowne -> experiments -> BIDDER
REPO = HERE
for _ in range(4):
    REPO = os.path.dirname(REPO)
sys.path.insert(0, os.path.join(REPO, 'algebra'))

from predict_q import q_general  # noqa: E402


H_VALUES = (4, 5, 6, 7, 8, 9, 10)
N_RANGE = (2, 50)   # inclusive
K_MAX = 200
PUBLISHED_HS = {5, 6, 7, 8}

BG = '#fafafa'
FG = '#1a1a2e'
POS = '#c0392b'
NEG = '#1f4e79'
GUIDE = '#aaaaaa'
PUB = '#888888'


def vertical_l1_at_h(h: int) -> float:
    """Mean Pearson correlation between row_n and row_{n+1}
    for n ∈ [N_RANGE[0], N_RANGE[1]-1], where row_n[k] = Q_n(n^h * (k+1)).

    Computed on raw Q values (no slog). At smaller (n_max, K) than the
    published lattice, magnitudes are smaller than the
    ATTRACTOR-AND-MIRAGE.md figures (~+0.25 / ~−0.14 at h ∈ {5,6,7,8})
    but the sign pattern survives cleanly.
    """
    n_lo, n_hi = N_RANGE
    n_count = n_hi - n_lo + 1
    grid = np.zeros((n_count, K_MAX))
    for ni, n in enumerate(range(n_lo, n_hi + 1)):
        for ki, k in enumerate(range(1, K_MAX + 1)):
            grid[ni, ki] = float(q_general(n, h, k))
    correlations = []
    for ni in range(n_count - 1):
        a = grid[ni]
        b = grid[ni + 1]
        a_centered = a - a.mean()
        b_centered = b - b.mean()
        denom = np.sqrt((a_centered ** 2).sum() * (b_centered ** 2).sum())
        if denom == 0:
            continue
        correlations.append((a_centered * b_centered).sum() / denom)
    return float(np.mean(correlations))


def render():
    print(f'computing vertical L=1 across h ∈ {H_VALUES}, '
          f'n ∈ [{N_RANGE[0]}, {N_RANGE[1]}], K = {K_MAX} ...')
    values = []
    for h in H_VALUES:
        v = vertical_l1_at_h(h)
        values.append(v)
        marker = '   <- ATTRACTOR' if h in PUBLISHED_HS else ''
        print(f'  h = {h:2d}:  vertical L=1 = {v:+.4f}{marker}')

    fig, ax = plt.subplots(figsize=(10, 6), facecolor=BG)
    ax.set_facecolor(BG)

    x_pos = np.arange(len(H_VALUES))
    bar_colors = [POS if v > 0 else NEG for v in values]

    bars = ax.bar(x_pos, values, color=bar_colors, edgecolor=FG,
                  linewidth=0.6, width=0.7, zorder=3)

    # zero line
    ax.axhline(0, color=FG, linewidth=0.8, alpha=0.5, zorder=2)

    # value labels above/below each bar
    for x, v in zip(x_pos, values):
        offset = 0.012 if v > 0 else -0.012
        va = 'bottom' if v > 0 else 'top'
        ax.text(x, v + offset, f'{v:+.3f}', ha='center', va=va,
                color=FG, fontsize=9.5, zorder=4)

    # published-vs-extension distinction: faint underline on published h's
    y_min = min(min(values), 0) - 0.12
    for x, h in zip(x_pos, H_VALUES):
        if h in PUBLISHED_HS:
            ax.scatter([x], [y_min + 0.015], marker='s', s=18,
                       color=PUB, alpha=0.9, zorder=2)

    ax.text(len(H_VALUES) - 0.5, y_min + 0.015,
            ' ▪ marker: h-values cited in ATTRACTOR-AND-MIRAGE.md:612-615',
            color=PUB, fontsize=8.5, ha='right', va='center', alpha=0.85)

    # axes / spines
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('bottom', 'left'):
        ax.spines[side].set_color(FG)
        ax.spines[side].set_alpha(0.4)
    ax.tick_params(colors=FG, which='both')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f'h = {h}' for h in H_VALUES], color=FG)
    ax.set_ylabel('vertical L=1 autocorrelation\n(mean Pearson over adjacent n-rows)',
                  color=FG, fontsize=10.5)
    ax.set_title(
        'Prodigy: The L=1 Sign-Flip Across h-Parity — vertical autocorrelation by height',
        color=FG, fontsize=13.5, pad=12, fontweight='semibold',
    )
    ax.set_ylim(y_min, max(max(values), 0) * 1.18)
    ax.set_xlim(-0.6, len(H_VALUES) - 0.4)

    # Footnote
    fig.text(0.5, 0.02,
             f'(n ∈ [{N_RANGE[0]}, {N_RANGE[1]}], K = {K_MAX}; '
             f'analytic from algebra/predict_q.q_general — no lattice required)',
             color=GUIDE, fontsize=8.5, ha='center', style='italic')

    fig.tight_layout(rect=[0, 0.04, 1, 1])

    out = os.path.join(HERE, 'prodigy_L1_signflip.png')
    fig.savefig(out, dpi=150, facecolor=BG)
    print(f'-> {out}')


if __name__ == '__main__':
    render()
