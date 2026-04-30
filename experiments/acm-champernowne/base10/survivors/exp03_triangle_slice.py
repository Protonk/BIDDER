"""
exp03_triangle_slice.py — vertical slice through the n_0 = 290 triangle.

Hypothesis (from EXP02-style analysis of l1_grid_zoom.png): the
triangular fingers along the K = n_0 diagonal are constant-character
regions of the survivor filter, separated by sharp transitions at the
pair-collision thresholds K_pair(n_a, n_b) for pairs in the window.

Test: compute gap(K) at fixed n_0 = 290 for dense K, overlay the 45
K_pair values for window [290..299]. If the hypothesis holds, gap(K)
should show plateaus between consecutive K_pair values and step-jumps
at each threshold.

Outputs:
    exp03_triangle_slice.png  — gap(K) at n_0=290 with thresholds
"""

import os
import sys
import time
import math

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..', 'core'))

from pair_thresholds import all_k_pairs

OUT = os.path.join(HERE, 'exp03_triangle_slice.png')

W = 10
N0 = 290
K_MIN = 30
K_MAX = 500
K_STEP = 1
WARMUP_FRAC = 0.25

u9 = np.full(9, 1.0 / 9)


def n_primes_vec(n: int, k: int) -> np.ndarray:
    """First k n-primes as int64."""
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


def gap_signed(n0: int, k: int, w: int = W) -> float:
    """Mean post-warmup of (surv_l1 - bundle_l1) for leading-digit
    distribution from uniform on {1..9}."""
    parts = [n_primes_vec(n, k) for n in range(n0, n0 + w)]
    m_arr = np.concatenate(parts)
    n_atoms = m_arr.size

    _, inverse, counts = np.unique(m_arr, return_inverse=True, return_counts=True)
    mask = (counts[inverse] == 1).astype(np.int64)

    log_floor = np.floor(np.log10(m_arr)).astype(np.int64)
    leading = (m_arr // 10 ** log_floor).astype(np.int64)

    ld = np.zeros((n_atoms, 9), dtype=np.int64)
    ld[np.arange(n_atoms), leading - 1] = 1

    ld_b = np.cumsum(ld, axis=0)
    ld_s = np.cumsum(ld * mask[:, None], axis=0)
    tot_b = ld_b.sum(axis=1)
    tot_s = ld_s.sum(axis=1)

    valid = (tot_b > 0) & (tot_s > 0)
    pb = ld_b[valid] / tot_b[valid, None]
    ps = ld_s[valid] / tot_s[valid, None]
    l1_b = np.abs(pb - u9).sum(axis=1)
    l1_s = np.abs(ps - u9).sum(axis=1)

    n_valid = l1_b.size
    start = int(WARMUP_FRAC * n_valid)
    if start >= n_valid:
        return float('nan')
    return float(np.mean(l1_s[start:] - l1_b[start:]))


def main():
    print(f'Computing gap(K) slice at n_0 = {N0}, window W = {W}')
    print(f'K in [{K_MIN}, {K_MAX}] step {K_STEP}')
    print()

    t0 = time.time()
    Ks = np.arange(K_MIN, K_MAX + 1, K_STEP)
    gaps = np.zeros(len(Ks))
    for i, K in enumerate(Ks):
        gaps[i] = gap_signed(N0, int(K))
        if (i + 1) % 50 == 0:
            print(f'  K = {K}, gap = {gaps[i]:+.4f}  (t={time.time() - t0:.1f}s)')
    print(f'Total: {time.time() - t0:.1f}s')

    # Pair thresholds for window [N0..N0+W-1]
    thresholds = sorted(set(all_k_pairs(N0, W)))
    print(f'\nPair-collision thresholds (W={W}, {len(thresholds)} unique):')
    print(' ', thresholds)

    # Plot
    fig, ax = plt.subplots(figsize=(14, 7), dpi=140)
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')

    # Color thresholds by their position in the sorted list (early=blue, late=red).
    cmap = plt.get_cmap('plasma')
    for i, kp in enumerate(thresholds):
        if K_MIN <= kp <= K_MAX:
            color = cmap(i / max(1, len(thresholds) - 1))
            ax.axvline(kp, color=color, linewidth=0.7, alpha=0.55, zorder=1)

    # The gap curve
    ax.plot(Ks, gaps, color='#ffcc5c', linewidth=1.4, zorder=3,
            label=f'gap(K) at n_0 = {N0}')
    ax.axhline(0, color='#666', linewidth=0.6, zorder=2)

    # Annotate clusters
    cluster_bounds = [(50, 100), (140, 160), (285, 300)]
    for lo, hi in cluster_bounds:
        kps_in_cluster = [kp for kp in thresholds if lo <= kp <= hi]
        if kps_in_cluster:
            mid = sum(kps_in_cluster) / len(kps_in_cluster)
            ax.text(mid, ax.get_ylim()[1] * 0.92 if ax.get_ylim()[1] > 0 else 0.04,
                    f'{len(kps_in_cluster)} pairs',
                    ha='center', va='top', color='#ddd', fontsize=9,
                    bbox=dict(facecolor='#1a1a1a', edgecolor='none',
                              alpha=0.7, pad=2))

    ax.set_xlabel('K  (atoms per stream)', color='white', fontsize=12)
    ax.set_ylabel('gap = mean (surv_L1 − bundle_L1), post-warmup',
                  color='white', fontsize=12)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#333')
    ax.grid(True, alpha=0.15, color='#888')

    title = (f'Triangle slice: gap(K) at n_0 = {N0}, W = {W}\n'
             f'vertical lines = pair-collision thresholds K_pair(n_a, n_b) '
             f'for pairs in [{N0}..{N0 + W - 1}]')
    ax.set_title(title, color='white', fontsize=12)
    ax.legend(loc='upper left', fontsize=10, framealpha=0.4,
              labelcolor='white', facecolor='#1a1a1a')

    # Mark cluster regions on x-axis
    ax.set_xlim(K_MIN, K_MAX)

    plt.tight_layout()
    plt.savefig(OUT, dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f'\n-> {OUT}')

    # Quick numerical summary: gap value just before/after each threshold cluster
    print('\nGap behavior across threshold clusters:')
    print(f'  K < first threshold ({thresholds[0]}):  '
          f'mean gap in [{K_MIN}, {thresholds[0] - 1}] = '
          f'{gaps[(Ks >= K_MIN) & (Ks < thresholds[0])].mean():+.4f}')
    cluster_ranges = [
        ('first cluster (≈99)', 100, 145),
        ('second cluster (≈149)', 150, 285),
        ('third cluster (290-298)', 299, K_MAX),
    ]
    for name, lo, hi in cluster_ranges:
        mask = (Ks >= lo) & (Ks <= hi)
        if mask.any():
            print(f'  {name}: mean gap in [{lo}, {hi}] = {gaps[mask].mean():+.4f}')


if __name__ == '__main__':
    main()
