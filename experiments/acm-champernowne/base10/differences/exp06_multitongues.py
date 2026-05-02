"""
exp06_multitongues.py — multiplicity-bucketed Two Tongues.

Tests the optimizer reading (DIFFERENCING-AS-TRANSDUCER.md, follow-up
discussion): survivors are atoms with H(stream | integer) = 0 — the
output of an information-theoretic optimizer. Doubletons (m=2),
triples (m=3), and higher multiplicities have H > 0; their leading-
digit content might be biased, breaking the L1 tracking.

Extends Two Tongues from {bundle, survivors} to {bundle, m=1, m=2,
m=3, m≥4}. Computes running leading-digit L1 deviation for each
along bundle's atom-axis.

Prediction (optimizer reading):
  - m=1 (survivors) tracks bundle (existing finding).
  - m=2, 3, ≥4 diverge from bundle — their leading-digit content
    has source-bias.

Falsifier (Benford-robustness reading):
  - All multiplicities track bundle. The L1 tracking is just a
    feature of how integers in this number range distribute their
    leading digits, regardless of selection rule.

Run: sage -python experiments/acm-champernowne/base10/differences/exp06_multitongues.py
"""

from __future__ import annotations

import os
import sys
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = HERE
for _ in range(4):
    REPO = os.path.dirname(REPO)
sys.path.insert(0, os.path.join(REPO, 'core'))
sys.path.insert(0, os.path.join(REPO, 'experiments', 'acm-champernowne',
                                'base10', 'survivors'))

from survivors_core import bundle_atoms  # noqa: E402

N0, N1, K = 2, 10, 400

# Visual palette
BG = '#fafafa'
FG = '#1a1a2e'
GUIDE = '#aaaaaa'

PALETTE = {
    'bundle': '#1f4e79',  # navy
    'm=1':    '#c0392b',  # crimson — survivors (the optimizer's output)
    'm=2':    '#2ca02c',  # green — doubletons
    'm=3':    '#ff7f0e',  # orange — triples
    'm≥4':    '#9467bd',  # purple — quads+
}


def main():
    print(f'building bundle for [{N0}, {N1}], k = {K} ...')
    atoms = bundle_atoms(N0, N1, K)
    n_atoms = len(atoms)
    print(f'  {n_atoms} atoms')

    integer_counts = Counter(m for _, m in atoms)

    # Bundle per-atom leading digits
    leading_digits = np.array([int(str(m)[0]) for _, m in atoms])
    ld_per_atom = np.zeros((n_atoms, 9), dtype=np.int64)
    ld_per_atom[np.arange(n_atoms), leading_digits - 1] = 1

    # Per-bucket: count each unique integer once, at its first appearance
    buckets = ['m=1', 'm=2', 'm=3', 'm≥4']
    ld_buckets = {b: np.zeros((n_atoms, 9), dtype=np.int64) for b in buckets}
    counts_per_bucket = {b: 0 for b in buckets}
    seen = set()

    for i, (n, m) in enumerate(atoms):
        if m in seen:
            continue
        seen.add(m)
        mult = integer_counts[m]
        if mult == 1:
            key = 'm=1'
        elif mult == 2:
            key = 'm=2'
        elif mult == 3:
            key = 'm=3'
        else:
            key = 'm≥4'
        leading = leading_digits[i]
        ld_buckets[key][i, leading - 1] = 1
        counts_per_bucket[key] += 1

    print(f'\n  multiplicity decomposition:')
    print(f'    bundle (every atom):        {n_atoms} atoms')
    for b in buckets:
        print(f'    {b}: {counts_per_bucket[b]:>5} unique integers')
    print(f'    total unique integers:      {sum(counts_per_bucket.values())}')

    # Cumulative counts
    cum_bundle = np.cumsum(ld_per_atom, axis=0)
    cum_buckets = {b: np.cumsum(ld_buckets[b], axis=0) for b in buckets}

    total_bundle = cum_bundle.sum(axis=1)
    total_buckets = {b: cum_buckets[b].sum(axis=1) for b in buckets}

    uniform = np.full(9, 1.0 / 9)

    def l1_dev(cum, total):
        out = np.full(len(total), np.nan)
        valid = total > 0
        p = cum[valid] / total[valid, None]
        out[valid] = np.abs(p - uniform).sum(axis=1)
        return out

    l1_bundle = l1_dev(cum_bundle, total_bundle)
    l1_buckets_curves = {b: l1_dev(cum_buckets[b], total_buckets[b]) for b in buckets}

    end_l1 = {'bundle': float(l1_bundle[-1])}
    end_count = {'bundle': n_atoms}
    for b in buckets:
        end_l1[b] = float(l1_buckets_curves[b][-1])
        end_count[b] = counts_per_bucket[b]

    print(f'\n  end-of-stream leading-digit L1 (vs uniform-1/9):')
    print(f'    bundle: {end_l1["bundle"]:.4f}  ({end_count["bundle"]:,} atoms)')
    for b in buckets:
        delta = end_l1[b] - end_l1['bundle']
        print(f'    {b}:    {end_l1[b]:.4f}  ({end_count[b]:>5} integers)   '
              f'Δ from bundle: {delta:+.4f}')

    # Per-bucket leading-digit distribution at end of stream
    print(f'\n  end-of-stream leading-digit distributions:')
    print(f'    digit | bundle  |   m=1   |   m=2   |   m=3   |  m≥4')
    print(f'    ------+---------+---------+---------+---------+--------')
    for d in range(9):
        bundle_p = cum_bundle[-1, d] / total_bundle[-1]
        bucket_ps = {}
        for b in buckets:
            t = total_buckets[b][-1]
            bucket_ps[b] = cum_buckets[b][-1, d] / t if t > 0 else float('nan')
        row = f'      {d+1}   | {bundle_p:.4f}'
        for b in buckets:
            row += f'  | {bucket_ps[b]:.4f}'
        print(row)

    # Plot — 2x2: tongues curves, end-L1 bars, end leading-digit histogram, stats
    fig = plt.figure(figsize=(14, 10), facecolor=BG)
    gs = fig.add_gridspec(2, 2, hspace=0.32, wspace=0.28)

    # TL: tongues (running L1 over bundle position)
    ax = fig.add_subplot(gs[0, :])
    ax.set_facecolor(BG)
    x = np.arange(1, n_atoms + 1)
    ax.semilogy(x, l1_bundle, color=PALETTE['bundle'], linewidth=2.0,
                label=f'bundle ({n_atoms} atoms)', alpha=0.95, zorder=5)
    for b in buckets:
        if counts_per_bucket[b] >= 2:  # skip empty/near-empty buckets
            ax.semilogy(x, l1_buckets_curves[b], color=PALETTE[b],
                        linewidth=1.4, alpha=0.85,
                        label=f'{b}  ({counts_per_bucket[b]} ints)',
                        zorder=4)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('bottom', 'left'):
        ax.spines[side].set_color(FG)
        ax.spines[side].set_alpha(0.4)
    ax.tick_params(colors=FG)
    ax.set_xlabel('bundle atoms processed', color=FG, fontsize=10)
    ax.set_ylabel('L1 deviation from uniform-1/9', color=FG, fontsize=10)
    ax.set_title(
        f'multi-tongue: leading-digit L1 by multiplicity, [{N0}, {N1}], k = {K}',
        color=FG, fontsize=12, pad=8,
    )
    ax.legend(loc='upper right', facecolor='#f0f0f0', fontsize=9, framealpha=0.95)

    # BL: end-of-stream L1 bars
    ax = fig.add_subplot(gs[1, 0])
    ax.set_facecolor(BG)
    labels = ['bundle'] + buckets
    values = [end_l1[k] for k in labels]
    colors = [PALETTE[k] for k in labels]
    ax.bar(labels, values, color=colors, edgecolor=FG, linewidth=0.5)
    for x_pos, (lbl, v) in enumerate(zip(labels, values)):
        ax.text(x_pos, v + 0.002, f'{v:.4f}', ha='center', va='bottom',
                color=FG, fontsize=9)
    ax.axhline(end_l1['bundle'], color=GUIDE, linewidth=0.8, linestyle='--',
               alpha=0.6, label='bundle level')
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('bottom', 'left'):
        ax.spines[side].set_color(FG)
        ax.spines[side].set_alpha(0.4)
    ax.tick_params(colors=FG)
    ax.set_ylabel('end-of-stream L1 deviation', color=FG, fontsize=10)
    ax.set_title('end-of-stream L1 by multiplicity', color=FG, fontsize=11, pad=8)
    ax.legend(loc='upper left', facecolor='#f0f0f0', fontsize=9)

    # BR: per-digit leading-digit distribution at end of stream
    ax = fig.add_subplot(gs[1, 1])
    ax.set_facecolor(BG)
    digits = np.arange(1, 10)
    width = 0.15
    bundle_dist = (cum_bundle[-1] / total_bundle[-1]).flatten()
    ax.bar(digits - 2 * width, bundle_dist, width=width, color=PALETTE['bundle'],
           edgecolor=FG, linewidth=0.4, label='bundle', zorder=3)
    for j, b in enumerate(buckets):
        if counts_per_bucket[b] < 2:
            continue
        bdist = cum_buckets[b][-1] / total_buckets[b][-1]
        ax.bar(digits + (j - 1) * width, bdist, width=width, color=PALETTE[b],
               edgecolor=FG, linewidth=0.4, label=b, zorder=3)
    ax.axhline(1.0/9, color=GUIDE, linewidth=0.8, linestyle='--',
               alpha=0.6, label='uniform 1/9')
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('bottom', 'left'):
        ax.spines[side].set_color(FG)
        ax.spines[side].set_alpha(0.4)
    ax.tick_params(colors=FG)
    ax.set_xticks(digits)
    ax.set_xlabel('leading digit (1–9)', color=FG, fontsize=10)
    ax.set_ylabel('frequency at end of stream', color=FG, fontsize=10)
    ax.set_title('end leading-digit distribution by multiplicity',
                 color=FG, fontsize=11, pad=8)
    ax.legend(loc='upper right', facecolor='#f0f0f0', fontsize=9)

    fig.suptitle(
        'EXP06 — does the L1 tracking generalise across multiplicity buckets?',
        color=FG, fontsize=14, fontweight='semibold', y=0.995,
    )

    out = os.path.join(HERE, 'exp06_multitongues.png')
    fig.savefig(out, dpi=130, facecolor=BG, bbox_inches='tight')
    print(f'\n-> {out}')


if __name__ == '__main__':
    main()
