"""
exactness.py — Digit-count exactness over one period.

BIDDER gives each of k symbols exactly m times. Numpy jitters around m.
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


BG = '#0a0a0a'
FG = 'white'
SPINE = '#333'
K = 9
M = 1000
PERIOD = K * M
N_KEYS = 10


def main():
    fig, axes = plt.subplots(2, 2, figsize=(16, 10),
                             gridspec_kw={'height_ratios': [1, 1.8]})
    fig.patch.set_facecolor(BG)

    for ax in axes.ravel():
        ax.set_facecolor(BG)
        ax.tick_params(colors=FG)
        for spine in ax.spines.values():
            spine.set_color(SPINE)

    digits = np.arange(1, K + 1)
    bar_width = 0.35

    # --- Top row: single period ---
    ax_b = axes[0, 0]
    B = bidder.cipher(period=PERIOD, key=b'exactness-single')
    symbols = np.array([(B.at(i) % K) + 1 for i in range(PERIOD)])
    counts_b = np.array([np.sum(symbols == d) for d in digits])
    ax_b.bar(digits, counts_b, color='#6ec6ff', edgecolor='none')
    ax_b.axhline(M, color='#88d8b0', linestyle='--', linewidth=1.0, alpha=0.7)
    ax_b.set_title('BIDDER cipher  (1 period)', color=FG, fontsize=12)
    ax_b.set_ylabel('count', color=FG)
    ax_b.set_xticks(digits)
    ax_b.set_ylim(M - 80, M + 80)

    ax_n = axes[0, 1]
    rng = np.random.default_rng(42)
    symbols_np = rng.integers(1, K + 1, size=PERIOD)
    counts_n = np.array([np.sum(symbols_np == d) for d in digits])
    ax_n.bar(digits, counts_n, color='#ffcc5c', edgecolor='none')
    ax_n.axhline(M, color='#88d8b0', linestyle='--', linewidth=1.0, alpha=0.7)
    ax_n.set_title('numpy PRNG  (1 period)', color=FG, fontsize=12)
    ax_n.set_xticks(digits)
    ax_n.set_ylim(M - 80, M + 80)

    # Annotate max deviation
    dev_b = max(abs(counts_b - M))
    dev_n = max(abs(counts_n - M))
    ax_b.text(0.97, 0.95, f'max |count − {M}| = {dev_b}',
              color=FG, fontsize=10, ha='right', va='top',
              transform=ax_b.transAxes)
    ax_n.text(0.97, 0.95, f'max |count − {M}| = {dev_n}',
              color=FG, fontsize=10, ha='right', va='top',
              transform=ax_n.transAxes)

    # --- Bottom row: 10 independent periods ---
    ax_bm = axes[1, 0]
    all_counts_b = np.zeros((N_KEYS, K), dtype=int)
    for ki in range(N_KEYS):
        B = bidder.cipher(period=PERIOD, key=f'exactness-k{ki}'.encode())
        syms = np.array([(B.at(i) % K) + 1 for i in range(PERIOD)])
        for di, d in enumerate(digits):
            all_counts_b[ki, di] = np.sum(syms == d)

    x = np.arange(N_KEYS)
    for di in range(K):
        offset = (di - K / 2 + 0.5) * 0.08
        ax_bm.bar(x + offset, all_counts_b[:, di], width=0.07,
                  color=plt.cm.twilight_shifted(di / K), edgecolor='none')
    ax_bm.axhline(M, color='#88d8b0', linestyle='--', linewidth=1.0, alpha=0.7)
    ax_bm.set_title(f'BIDDER cipher  ({N_KEYS} keys)', color=FG, fontsize=12)
    ax_bm.set_xlabel('key index', color=FG)
    ax_bm.set_ylabel('count', color=FG)
    ax_bm.set_xticks(x)
    ax_bm.set_ylim(M - 80, M + 80)

    ax_nm = axes[1, 1]
    all_counts_n = np.zeros((N_KEYS, K), dtype=int)
    for ki in range(N_KEYS):
        rng_k = np.random.default_rng(ki + 100)
        syms_np = rng_k.integers(1, K + 1, size=PERIOD)
        for di, d in enumerate(digits):
            all_counts_n[ki, di] = np.sum(syms_np == d)

    for di in range(K):
        offset = (di - K / 2 + 0.5) * 0.08
        ax_nm.bar(x + offset, all_counts_n[:, di], width=0.07,
                  color=plt.cm.twilight_shifted(di / K), edgecolor='none')
    ax_nm.axhline(M, color='#88d8b0', linestyle='--', linewidth=1.0, alpha=0.7)
    ax_nm.set_title(f'numpy PRNG  ({N_KEYS} seeds)', color=FG, fontsize=12)
    ax_nm.set_xlabel('seed index', color=FG)
    ax_nm.set_xticks(x)
    ax_nm.set_ylim(M - 80, M + 80)

    fig.suptitle(f'Symbol counts over one period  (k={K}, m={M}, period={PERIOD})',
                 color=FG, fontsize=14, y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out = os.path.join(HERE, 'exactness.png')
    fig.savefig(out, dpi=250, facecolor=BG, bbox_inches='tight')
    plt.close(fig)
    print(f'-> exactness.png')


if __name__ == '__main__':
    main()
