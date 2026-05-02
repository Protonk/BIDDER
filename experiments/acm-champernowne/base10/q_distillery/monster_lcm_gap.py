"""
monster_lcm_gap.py — emblem render for wonders/monster-lcm-not-factorial.md.

Two curves over h ∈ [1, 20], log-y:
  - h! (warm crimson, dashed): the naive expectation.
  - lcm(1, ..., h) (navy, solid): the actual bound the construction forces.

The shaded region between them is the "constitutively unattainable" gap.
A scatter of empirical Q denominators (over a sample of (n, h, k) cells)
overlays the curves; every point lands on or below the lcm curve, never
in the gap.

Computation: lcm and factorial in pure Python; denominators from
algebra/predict_q.q_general (exact Fraction).

Run: sage -python experiments/acm-champernowne/base10/q_distillery/monster_lcm_gap.py
"""

from __future__ import annotations

import os
import sys
from math import factorial, gcd

import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
# q_distillery -> base10 -> acm-champernowne -> experiments -> BIDDER
REPO = HERE
for _ in range(4):
    REPO = os.path.dirname(REPO)
sys.path.insert(0, os.path.join(REPO, 'algebra'))

from predict_q import q_general, n_adic_height  # noqa: E402


H_MAX = 20

# Sample cells to scatter
N_VALUES = (2, 3, 5, 6, 10)
K_VALUES = (1, 2, 3, 6, 12, 30)

BG = '#fafafa'
FG = '#1a1a2e'
CEILING = '#c0392b'      # warm — h!, the naive expectation
BOUND = '#1f4e79'        # cool — lcm, the actual bound
GAP = '#d96440'          # warm desaturated for shading
SCATTER = '#3a3a4a'      # slate gray
GUIDE = '#aaaaaa'


def lcm(a, b):
    return a * b // gcd(a, b)


def lcm_range(h):
    out = 1
    for i in range(1, h + 1):
        out = lcm(out, i)
    return out


def main():
    h_axis = np.arange(1, H_MAX + 1)
    factorials = np.array([factorial(h) for h in h_axis], dtype=object)
    lcms = np.array([lcm_range(h) for h in h_axis], dtype=object)

    print('h | h!                       | lcm(1..h)              | ratio')
    for h, f, l in zip(h_axis, factorials, lcms):
        ratio = float(f) / float(l)
        print(f'{h:>2} | {int(f):>22d} | {int(l):>22d} | {ratio:>10.2f}')

    # Empirical Q denominators
    print('\nsampling Q denominators ...')
    scatter_h = []
    scatter_d = []
    for n in N_VALUES:
        for h in h_axis:
            for k in K_VALUES:
                m = (n ** int(h)) * k
                # use the true height including overlap
                h_eff = n_adic_height(n, m)
                if h_eff > H_MAX:
                    continue
                q = q_general(n, int(h), k)
                scatter_h.append(int(h_eff))
                scatter_d.append(int(q.denominator))
    scatter_h = np.array(scatter_h)
    scatter_d = np.array(scatter_d)
    print(f'  sampled {len(scatter_d)} cells')
    print(f'  denom range: [{scatter_d.min()}, {scatter_d.max()}]')

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=BG)
    ax.set_facecolor(BG)

    # convert to plottable numerics
    fact_y = np.array([float(x) for x in factorials])
    lcm_y = np.array([float(x) for x in lcms])

    # shaded gap region (between lcm and h!)
    ax.fill_between(h_axis, lcm_y, fact_y, color=GAP, alpha=0.13, zorder=1,
                    label='h!/lcm gap — constitutively unattainable')

    # h! curve (warm, dashed — predicted not realised)
    ax.plot(h_axis, fact_y, color=CEILING, linewidth=2.0, linestyle='--',
            alpha=0.9, zorder=3, label='h!  (naive expectation)')
    ax.scatter(h_axis, fact_y, color=CEILING, s=22, zorder=4,
               edgecolors=BG, linewidths=0.6)

    # lcm curve (cool, solid — actual bound)
    ax.plot(h_axis, lcm_y, color=BOUND, linewidth=2.0, alpha=0.95,
            zorder=3, label='lcm(1, …, h)  (actual bound)')
    ax.scatter(h_axis, lcm_y, color=BOUND, s=22, zorder=4,
               edgecolors=BG, linewidths=0.6)

    # empirical Q denominators
    ax.scatter(scatter_h, scatter_d, color=SCATTER, s=14, alpha=0.45,
               zorder=2, marker='o', edgecolors='none',
               label=f'denom(Q_n(n^h · k))  ({len(scatter_d)} cells)')

    ax.set_yscale('log')
    ax.set_xticks(list(h_axis))
    ax.set_xlim(0.5, H_MAX + 0.5)

    # annotations: gap callouts
    ax.annotate(
        f'h = 8:  lcm = {lcm_range(8)},  h! = {factorial(8):,}\n'
        f'         h!/lcm = {factorial(8) // lcm_range(8)}× tighter',
        xy=(8, lcm_range(8)), xytext=(11.5, 200),
        color=FG, fontsize=9.5,
        arrowprops=dict(arrowstyle='->', color=GUIDE, alpha=0.7,
                        connectionstyle='arc3,rad=0.2'),
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#f0f0f0',
                  edgecolor=GUIDE, alpha=0.85),
    )
    ratio_20 = factorial(20) / lcm_range(20)
    ax.annotate(
        f'h = 20:  h!/lcm ≈ {ratio_20:.1e}',
        xy=(20, lcm_range(20)), xytext=(13.5, 1e15),
        color=FG, fontsize=9.5,
        arrowprops=dict(arrowstyle='->', color=GUIDE, alpha=0.7,
                        connectionstyle='arc3,rad=-0.2'),
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#f0f0f0',
                  edgecolor=GUIDE, alpha=0.85),
    )

    # axes / spines
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('bottom', 'left'):
        ax.spines[side].set_color(FG)
        ax.spines[side].set_alpha(0.4)
    ax.tick_params(colors=FG, which='both')
    ax.set_xlabel('h', color=FG, fontsize=11)
    ax.set_ylabel('denominator (log)', color=FG, fontsize=11)
    ax.set_title(
        'Monster: The lcm-not-Factorial Denominator — the gap the construction forces',
        color=FG, fontsize=13, pad=12, fontweight='semibold',
    )
    ax.legend(loc='upper left', facecolor='#f0f0f0', edgecolor=GUIDE,
              fontsize=9.5, framealpha=0.9)

    fig.tight_layout()
    out = os.path.join(HERE, 'monster_lcm_gap.png')
    fig.savefig(out, dpi=150, facecolor=BG)
    print(f'-> {out}')


if __name__ == '__main__':
    main()
