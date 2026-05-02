"""
wonder_cost_ladder.py — emblem render for wonders/wonder-cost-ladder.md.

Three curves over h ∈ [1, 12], log-y:

  - Numerical (crimson):   median log10(max(numerator, denominator)) of
                           q_general(n, h, k) — the bignum width.
  - Combinatorial (navy):  median wall-clock μs per q_general call —
                           proxy for arithmetic operations.
  - Cognitive (gold):      partition count p(h) — proxy for
                           (shape × tau_sig) classes at height h.

If the three track on log-y, the wonder is one rate. If they diverge,
the ladder is three ladders. The emblem records which.

This emblem doubles as the wonder's first instrumentation pass per
the entry's provocation #1.

Run: sage -python experiments/acm-champernowne/base10/q_distillery/wonder_cost_ladder.py
"""

from __future__ import annotations

import os
import sys
import time
from fractions import Fraction

import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
# q_distillery -> base10 -> acm-champernowne -> experiments -> BIDDER
REPO = HERE
for _ in range(4):
    REPO = os.path.dirname(REPO)
sys.path.insert(0, os.path.join(REPO, 'algebra'))

from predict_q import q_general  # noqa: E402


H_MAX = 12
N_VALUES = list(range(2, 16))     # 14 values
K_VALUES = list(range(1, 31)) + [
    # boundary-y cells with higher Ω, to expose the bignum-width tail
    2 * 3, 2 * 3 * 5, 2 * 3 * 5 * 7, 2 * 3 * 5 * 7 * 11,
    2 * 3 * 5 * 7 * 11 * 13, 2 * 3 * 5 * 7 * 11 * 13 * 17,
    2 ** 4, 3 ** 4, 5 ** 4, 7 ** 4,
]
TIMING_REPS = 5

BG = '#fafafa'
FG = '#1a1a2e'
NUM = '#c0392b'    # crimson — numerical
COMB = '#1f4e79'   # navy — combinatorial
COG = '#b8860b'    # dark goldenrod — cognitive
GUIDE = '#aaaaaa'


def partition_count(n: int) -> int:
    """Number of integer partitions of n. Standard recurrence by
    bounded part size: p(n, k) = p(n, k-1) + p(n-k, k)."""
    if n < 0:
        return 0
    if n == 0:
        return 1
    # iterative DP
    table = [0] * (n + 1)
    table[0] = 1
    for k in range(1, n + 1):
        for j in range(k, n + 1):
            table[j] += table[j - k]
    return table[n]


def bignum_width(q: Fraction) -> float:
    """log10(max(|numerator|, |denominator|)). Returns 0 for q = 0."""
    if q == 0:
        return 0.0
    a = abs(q.numerator)
    b = q.denominator
    return float(np.log10(max(a, b)))


def measure_h(h: int):
    """Return (max_bignum_width, median_micros_per_call, partition_count).

    Numerical coordinate uses *max* across cells, not median: the wonder
    is in the heavy-tail boundary cells where the master expansion's
    alternating terms reach huge magnitudes before cancelling. Median is
    dominated by typical cells and misses the climb.
    """
    widths = []
    timings = []
    cells = 0
    for n in N_VALUES:
        for k in K_VALUES:
            # bignum width
            q = q_general(n, h, k)
            widths.append(bignum_width(q))
            # wall-clock
            t0 = time.perf_counter()
            for _ in range(TIMING_REPS):
                q_general(n, h, k)
            t1 = time.perf_counter()
            timings.append((t1 - t0) * 1e6 / TIMING_REPS)
            cells += 1
    bw = float(np.max(widths))
    tm = float(np.median(timings))
    pc = partition_count(h)
    return bw, tm, pc, cells


def main():
    print(f'sampling {len(N_VALUES) * len(K_VALUES)} cells per h, '
          f'h ∈ [1, {H_MAX}], {TIMING_REPS} timing reps each ...')
    print()
    print(f'{"h":>3}  {"max bignum w.":>14}  {"μs/call":>10}  {"p(h)":>8}')
    print(f'{"-"*3}  {"-"*14}  {"-"*10}  {"-"*8}')

    h_values = list(range(1, H_MAX + 1))
    bw_arr = []
    tm_arr = []
    pc_arr = []
    for h in h_values:
        bw, tm, pc, _cells = measure_h(h)
        bw_arr.append(bw)
        tm_arr.append(tm)
        pc_arr.append(pc)
        print(f'{h:>3}  {bw:>14.3f}  {tm:>10.2f}  {pc:>8}')

    fig, ax = plt.subplots(figsize=(10, 6), facecolor=BG)
    ax.set_facecolor(BG)

    h_x = np.array(h_values)

    # numerical: 10^bignum_width
    num_y = 10.0 ** np.array(bw_arr)
    # combinatorial: μs per call
    comb_y = np.array(tm_arr)
    # cognitive: p(h)
    cog_y = np.array(pc_arr, dtype=float)

    ax.plot(h_x, num_y, color=NUM, linewidth=2.0, marker='o', markersize=6,
            label='numerical: max(|num|, denom) of Q across cells', zorder=4)
    ax.plot(h_x, comb_y, color=COMB, linewidth=2.0, marker='s', markersize=5.5,
            label='combinatorial: μs per q_general call', zorder=4)
    ax.plot(h_x, cog_y, color=COG, linewidth=2.0, marker='D', markersize=5.5,
            label='cognitive: p(h) = partitions of h', zorder=4)

    ax.set_yscale('log')
    ax.set_xticks(h_values)
    ax.set_xlim(0.5, H_MAX + 0.5)

    # subtle "three rates, or one?" annotation
    ax.text(0.015, 0.97, 'three rates, or one?',
            transform=ax.transAxes, color=FG, fontsize=11,
            va='top', ha='left', style='italic',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#f0f0f0',
                      edgecolor=GUIDE, alpha=0.85))

    # axes / spines
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('bottom', 'left'):
        ax.spines[side].set_color(FG)
        ax.spines[side].set_alpha(0.4)
    ax.tick_params(colors=FG, which='both')
    ax.set_xlabel('h (height)', color=FG, fontsize=11)
    ax.set_ylabel('coordinate value (log)', color=FG, fontsize=11)
    ax.set_title(
        'Wonder: The Cost Ladder — three coordinates of climb',
        color=FG, fontsize=13, pad=12, fontweight='semibold',
    )
    ax.legend(loc='lower right', facecolor='#f0f0f0', edgecolor=GUIDE,
              fontsize=9.5, framealpha=0.9)

    # footer
    fig.text(0.5, 0.02,
             f'(median over {len(N_VALUES)}×{len(K_VALUES)} = '
             f'{len(N_VALUES)*len(K_VALUES)} cells per h, '
             f'{TIMING_REPS} timing reps; single-machine measurement)',
             color=GUIDE, fontsize=8.5, ha='center', style='italic')

    fig.tight_layout(rect=[0, 0.04, 1, 1])
    out = os.path.join(HERE, 'wonder_cost_ladder.png')
    fig.savefig(out, dpi=150, facecolor=BG)
    print(f'\n-> {out}')


if __name__ == '__main__':
    main()
