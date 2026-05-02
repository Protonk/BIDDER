"""
marvel_row_ogf_cliff.py — emblem render for wonders/marvel-row-ogf-cliff.md.

Small-multiples stem plot of Q_p(p^h · q^e) for p = 2, q = 3,
e ∈ {2, 3, 4, 6}. Each panel shows the row
F(x; p, q^e) = (1 − (1−x)^e)/e terminating at degree exactly e — the
"cliff". Coefficients computed exactly via algebra/predict_q.row_polynomial.

The visual: e nonzero stems, then a cliff (vertical guide at h = e + 0.5),
then a band of faint absence markers indicating the zero coefficients
that the master expansion is structurally forced to produce. Repeated
four times, with e = 2, 3, 4, 6.

Run:
    python3 experiments/acm-champernowne/base10/q_distillery/marvel_row_ogf_cliff.py
"""

from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
# q_distillery -> base10 -> acm-champernowne -> experiments -> BIDDER
REPO = HERE
for _ in range(4):
    REPO = os.path.dirname(REPO)
sys.path.insert(0, os.path.join(REPO, 'algebra'))

from predict_q import row_polynomial  # noqa: E402


E_VALUES = (2, 3, 4, 6)
P, Q = 2, 3
H_MAX = 10

BG = '#fafafa'
FG = '#1a1a2e'
POS = '#c0392b'
NEG = '#1f4e79'
GUIDE = '#aaaaaa'


def render():
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5), facecolor=BG)
    axes = axes.flatten()

    for ax, e in zip(axes, E_VALUES):
        coefs = [float(c) for c in row_polynomial(P, Q ** e)]
        h_values = list(range(1, len(coefs) + 1))

        # cliff zone (h > e) — faint shading to show the absence
        ax.axvspan(e + 0.5, H_MAX + 0.7, alpha=0.06, color='black', zorder=0)

        # stems
        for h, c in zip(h_values, coefs):
            col = POS if c > 0 else NEG
            ax.vlines(h, 0, c, colors=col, linewidth=2.0, zorder=3)
            ax.scatter([h], [c], color=col, s=42, zorder=4,
                       edgecolors=BG, linewidths=0.6)

        # zero line
        ax.axhline(0, color=FG, linewidth=0.6, alpha=0.5, zorder=1)

        # post-cliff absence markers
        for h in range(e + 1, H_MAX + 1):
            ax.scatter([h], [0], color=GUIDE, s=14, marker='o',
                       alpha=0.55, zorder=2)

        # vertical guide at the cliff edge
        ax.axvline(e + 0.5, color=GUIDE, linewidth=0.8, linestyle='--',
                   alpha=0.6, zorder=1)

        ax.set_xlim(0.3, H_MAX + 0.7)
        cmin = min(coefs + [0])
        cmax = max(coefs + [0])
        pad = max(abs(cmin), abs(cmax)) * 0.18
        ax.set_ylim(cmin - pad, cmax + pad)

        ax.set_facecolor(BG)
        for side in ('top', 'right'):
            ax.spines[side].set_visible(False)
        for side in ('bottom', 'left'):
            ax.spines[side].set_color(FG)
            ax.spines[side].set_alpha(0.4)
        ax.tick_params(colors=FG, which='both')
        ax.set_xticks(list(range(1, H_MAX + 1)))
        ax.set_xlabel('h', color=FG)
        ax.set_ylabel(r'$Q_p(p^h \cdot q^e)$', color=FG)
        ax.set_title(
            rf'$e = {e}$:  $F(x; 2, 3^{e}) = (1 - (1-x)^{e})/{e}$',
            color=FG, fontsize=11,
        )

    fig.suptitle(
        'Marvel: The Row-OGF Cliff — termination at degree exactly Ω(k′)',
        color=FG, fontsize=13.5, y=0.99, fontweight='semibold',
    )
    fig.tight_layout(rect=[0, 0, 1, 0.96])

    out = os.path.join(HERE, 'marvel_row_ogf_cliff.png')
    fig.savefig(out, dpi=150, facecolor=BG)
    print(f'-> {out}')


if __name__ == '__main__':
    render()
