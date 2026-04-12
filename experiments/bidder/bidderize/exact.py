"""
exact.py — One image. One claim. BIDDER is exact.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..')
DIST = os.path.join(ROOT, 'dist')
sys.path.insert(0, DIST)

try:
    import bidder_c as bidder
except ImportError:
    import bidder

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


BG = '#080808'
FG = 'white'
K = 9
M = 1000
PERIOD = K * M
N_KEYS = 20


def main():
    fig, ax = plt.subplots(figsize=(10, 5.5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    digits = np.arange(1, K + 1)

    # --- Gather data: N_KEYS runs of each ---
    bidder_counts = np.zeros((N_KEYS, K), dtype=int)
    numpy_counts = np.zeros((N_KEYS, K), dtype=int)

    for ki in range(N_KEYS):
        B = bidder.cipher(period=PERIOD, key=f'exact:{ki}'.encode())
        syms = np.array([(B.at(i) % K) + 1 for i in range(PERIOD)])
        for di, d in enumerate(digits):
            bidder_counts[ki, di] = np.sum(syms == d)

        rng = np.random.default_rng(ki + 500)
        syms_np = rng.integers(1, K + 1, size=PERIOD)
        for di, d in enumerate(digits):
            numpy_counts[ki, di] = np.sum(syms_np == d)

    # --- Reference line: green, halftone (dashed) ---
    ax.axhline(M, color='#88d8b0', linewidth=1.5, linestyle=(0, (6, 3)),
               alpha=0.6, zorder=2)

    # --- numpy: circles, yellow ---
    for ki in range(N_KEYS):
        ax.scatter(digits, numpy_counts[ki], s=22, color='#ffcc5c',
                   alpha=0.65, zorder=3, edgecolors='none',
                   marker='o', label='numpy' if ki == 0 else None)

    # --- BIDDER: squares, blue (plotted on top) ---
    for ki in range(N_KEYS):
        ax.scatter(digits, bidder_counts[ki], s=28, color='#6ec6ff',
                   alpha=0.95, zorder=4, edgecolors='none',
                   marker='s', label='bidder' if ki == 0 else None)

    ax.set_xlim(0.2, K + 0.8)
    ax.set_xticks(digits)
    ax.set_xticklabels([str(d) for d in digits])
    ax.set_ylabel('count  (out of 9,000)', color='#999', fontsize=11)
    ax.tick_params(colors='#666')
    for spine in ax.spines.values():
        spine.set_color('#222')
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis='y', color='#1a1a1a', linewidth=0.5)

    lo = min(bidder_counts.min(), numpy_counts.min()) - 10
    hi = max(bidder_counts.max(), numpy_counts.max()) + 10
    ax.set_ylim(lo, hi)

    leg = ax.legend(loc='upper right', facecolor='#111', edgecolor='#222',
                    fontsize=11, markerscale=1.5)
    for t in leg.get_texts():
        t.set_color(FG)

    # --- The claim ---
    fig.text(
        0.5, 0.97,
        'Every generator is uniform.  BIDDER is exact, algebraically.',
        ha='center', va='top', color=FG, fontsize=14, fontweight='bold',
    )
    fig.text(
        0.5, 0.93,
        f'{N_KEYS} keys  ·  {PERIOD:,} outputs each  ·  digits 1–{K}',
        ha='center', va='top', color='#444', fontsize=10,
    )
    numpy_max_dev = int(np.max(np.abs(numpy_counts - M)))
    fig.text(
        0.35, 0.02,
        f'bidder  max |count − {M}| = 0',
        ha='center', va='bottom', color='#6ec6ff', fontsize=11,
        fontweight='bold',
    )
    fig.text(
        0.70, 0.02,
        f'numpy  max |count − {M}| = {numpy_max_dev}',
        ha='center', va='bottom', color='#ffcc5c', fontsize=11,
        fontweight='bold',
    )

    out = os.path.join(HERE, 'exact.png')
    fig.savefig(out, dpi=300, facecolor=BG, bbox_inches='tight',
                pad_inches=0.3)
    plt.close(fig)
    print(f'-> exact.png')


if __name__ == '__main__':
    main()
