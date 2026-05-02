"""
exp07_source_stream_stratification.py — survivors stratified by source stream.

EXP06 found that survivors over-represent digit 3 (20.4%) vs the
bundle's 12.4%, but couldn't localise where this comes from. Each
survivor c has a unique source stream d ∈ [n_0..n_1] (the only
window-divisor with c/d coprime to d). Stratifying by source stream
asks whether the aggregate's digit-3 spike traces to one or two
specific streams.

Build:
  - For each d ∈ [n_0..n_1], the set S_d of survivors with source stream d.
  - Per-stream leading-digit distribution P_d.
  - The aggregate decomposed as Σ_d (|S_d|/|Surv|) · P_d.

Plot:
  - Per-stream leading-digit distributions.
  - Stream populations.
  - Aggregate distribution stacked by source-stream contribution.
  - Digit-3 specific analysis.

Run: sage -python experiments/acm-champernowne/base10/differences/exp07_source_stream_stratification.py
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

BG = '#fafafa'
FG = '#1a1a2e'
GUIDE = '#aaaaaa'
HIGHLIGHT_DIGIT = 3   # digit-3 is the EXP06 anomaly

# tab10-ish palette for streams
STREAM_PALETTE = {
    2: '#1f77b4',   # blue
    3: '#ff7f0e',   # orange
    4: '#2ca02c',   # green
    5: '#d62728',   # red
    6: '#9467bd',   # purple
    7: '#8c564b',   # brown
    8: '#e377c2',   # pink
    9: '#7f7f7f',   # gray
    10: '#bcbd22',  # olive
}


def leading_digit(m):
    return int(str(m)[0])


def main():
    print(f'building bundle for [{N0}, {N1}], k = {K} ...')
    atoms = bundle_atoms(N0, N1, K)
    n_atoms = len(atoms)
    print(f'  {n_atoms} atoms')

    # Identify survivors and their source streams
    counts = Counter(m for _, m in atoms)
    survivors_by_stream = {n: [] for n in range(N0, N1 + 1)}
    seen = set()
    for n, m in atoms:
        if counts[m] == 1 and m not in seen:
            seen.add(m)
            survivors_by_stream[n].append(m)

    n_surv_total = sum(len(s) for s in survivors_by_stream.values())
    print(f'  {n_surv_total} survivors total')

    # First pass: compute per-stream stats
    stream_sizes = {}
    stream_dists = {}
    for d in range(N0, N1 + 1):
        S_d = survivors_by_stream[d]
        size = len(S_d)
        stream_sizes[d] = size
        if size == 0:
            stream_dists[d] = np.zeros(9)
            continue
        digits = [leading_digit(m) for m in S_d]
        ld_counts = Counter(digits)
        dist = np.array([ld_counts.get(j, 0) / size for j in range(1, 10)])
        stream_dists[d] = dist

    total_digit3_contrib = sum(
        (stream_sizes[d] / n_surv_total) * stream_dists[d][HIGHLIGHT_DIGIT - 1]
        for d in range(N0, N1 + 1) if stream_sizes[d] > 0
    )

    print(f'\n  per-stream survivor populations and digit-{HIGHLIGHT_DIGIT} share:')
    print(f'    d  | |S_d|  | share | P_d(3)  | digit-3 contrib (% of total)')
    print(f'    ---+--------+-------+---------+----------------------------')
    for d in range(N0, N1 + 1):
        size = stream_sizes[d]
        if size == 0:
            print(f'    {d:>2} | {size:>5} | {0.0:.3f} |   ---   |   ---')
            continue
        share = size / n_surv_total
        p_d_3 = stream_dists[d][HIGHLIGHT_DIGIT - 1]
        contrib = share * p_d_3
        pct = 100 * contrib / total_digit3_contrib if total_digit3_contrib > 0 else 0.0
        print(f'    {d:>2} | {size:>5} | {share:.3f} | {p_d_3:.4f}  | '
              f'{contrib:.4f}  ({pct:>5.1f}%)')

    # Aggregate distribution
    aggregate = np.zeros(9)
    for d in range(N0, N1 + 1):
        if stream_sizes[d] == 0:
            continue
        share = stream_sizes[d] / n_surv_total
        aggregate += share * stream_dists[d]

    print(f'\n  aggregate survivor leading-digit distribution:')
    print(f'    digit | freq')
    for j in range(1, 10):
        print(f'      {j}   | {aggregate[j-1]:.4f}')
    print(f'    digit-{HIGHLIGHT_DIGIT} freq: {aggregate[HIGHLIGHT_DIGIT-1]:.4f}')

    # Bundle baseline (every atom)
    bundle_digits = Counter(leading_digit(m) for _, m in atoms)
    bundle_dist = np.array([bundle_digits.get(j, 0) / n_atoms for j in range(1, 10)])
    print(f'\n  bundle leading-digit distribution (control):')
    print(f'    digit-3 freq: {bundle_dist[HIGHLIGHT_DIGIT-1]:.4f}')
    print(f'    aggregate − bundle at digit 3: '
          f'{aggregate[HIGHLIGHT_DIGIT-1] - bundle_dist[HIGHLIGHT_DIGIT-1]:+.4f}')

    # Per-stream contribution to aggregate digit-3
    print(f'\n  digit-{HIGHLIGHT_DIGIT} excess decomposition:')
    print(f'  aggregate digit-3 = Σ_d (|S_d|/|Surv|) · P_d(3)')
    excess_total = aggregate[HIGHLIGHT_DIGIT-1] - bundle_dist[HIGHLIGHT_DIGIT-1]
    print(f'  total excess vs bundle: {excess_total:+.4f}')
    for d in range(N0, N1 + 1):
        if stream_sizes[d] == 0:
            continue
        share = stream_sizes[d] / n_surv_total
        contrib = share * stream_dists[d][HIGHLIGHT_DIGIT-1]
        # how much above the "bundle baseline" share would expect
        baseline_contrib = share * bundle_dist[HIGHLIGHT_DIGIT-1]
        d_excess = contrib - baseline_contrib
        print(f'    d={d:>2}: contrib = {contrib:.4f}   '
              f'baseline = {baseline_contrib:.4f}   '
              f'Δ = {d_excess:+.4f}   '
              f'({100*d_excess/excess_total if excess_total != 0 else 0:>5.1f}% of total excess)')

    # PLOT — 2x2 grid
    fig = plt.figure(figsize=(14, 10), facecolor=BG)
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.25)

    # TL: aggregate distribution stacked by source stream
    ax = fig.add_subplot(gs[0, 0])
    ax.set_facecolor(BG)
    digits = np.arange(1, 10)
    bottom = np.zeros(9)
    for d in range(N0, N1 + 1):
        if stream_sizes[d] == 0:
            continue
        share = stream_sizes[d] / n_surv_total
        contrib = share * stream_dists[d]  # contribution to each digit
        ax.bar(digits, contrib, bottom=bottom, color=STREAM_PALETTE[d],
               edgecolor=FG, linewidth=0.3, label=f'd={d} ({stream_sizes[d]})',
               zorder=3)
        bottom += contrib
    # bundle reference
    ax.plot(digits, bundle_dist, marker='_', color=FG, linewidth=0,
            markersize=18, markeredgewidth=2.4, zorder=5,
            label='bundle (per-atom)')
    ax.axhline(1/9, color=GUIDE, linewidth=0.8, linestyle='--', zorder=2,
               label='uniform 1/9')
    # digit-3 highlight
    ax.axvspan(HIGHLIGHT_DIGIT - 0.5, HIGHLIGHT_DIGIT + 0.5, alpha=0.05,
               color='black', zorder=0)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('bottom', 'left'):
        ax.spines[side].set_color(FG)
        ax.spines[side].set_alpha(0.4)
    ax.tick_params(colors=FG)
    ax.set_xticks(digits)
    ax.set_xlabel('leading digit', color=FG, fontsize=10)
    ax.set_ylabel('aggregate survivor frequency', color=FG, fontsize=10)
    ax.set_title('aggregate survivor digit-distribution, stacked by source stream',
                 color=FG, fontsize=11, pad=8)
    ax.legend(loc='upper right', facecolor='#f0f0f0', fontsize=8.5, ncol=2)

    # TR: per-stream leading-digit distributions
    ax = fig.add_subplot(gs[0, 1])
    ax.set_facecolor(BG)
    width = 0.09
    for i, d in enumerate(range(N0, N1 + 1)):
        if stream_sizes[d] == 0:
            continue
        offset = (i - 4) * width
        ax.bar(digits + offset, stream_dists[d], width=width,
               color=STREAM_PALETTE[d], edgecolor=FG, linewidth=0.2,
               label=f'd={d}', zorder=3)
    ax.axhline(1/9, color=GUIDE, linewidth=0.8, linestyle='--', zorder=2)
    ax.axvspan(HIGHLIGHT_DIGIT - 0.5, HIGHLIGHT_DIGIT + 0.5, alpha=0.05,
               color='black', zorder=0)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('bottom', 'left'):
        ax.spines[side].set_color(FG)
        ax.spines[side].set_alpha(0.4)
    ax.tick_params(colors=FG)
    ax.set_xticks(digits)
    ax.set_xlabel('leading digit', color=FG, fontsize=10)
    ax.set_ylabel('per-stream survivor frequency P_d', color=FG, fontsize=10)
    ax.set_title('per-stream leading-digit distributions',
                 color=FG, fontsize=11, pad=8)
    ax.legend(loc='upper right', facecolor='#f0f0f0', fontsize=8, ncol=2)

    # BL: stream populations
    ax = fig.add_subplot(gs[1, 0])
    ax.set_facecolor(BG)
    streams = list(range(N0, N1 + 1))
    sizes = [stream_sizes[d] for d in streams]
    colors = [STREAM_PALETTE[d] for d in streams]
    bars = ax.bar(streams, sizes, color=colors, edgecolor=FG, linewidth=0.4)
    for x, sz in zip(streams, sizes):
        ax.text(x, sz + 5, str(sz), ha='center', va='bottom', color=FG, fontsize=9)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('bottom', 'left'):
        ax.spines[side].set_color(FG)
        ax.spines[side].set_alpha(0.4)
    ax.tick_params(colors=FG)
    ax.set_xticks(streams)
    ax.set_xlabel('source stream d', color=FG, fontsize=10)
    ax.set_ylabel('|S_d| — survivor count from stream d', color=FG, fontsize=10)
    ax.set_title(f'survivor population per source stream (total {n_surv_total})',
                 color=FG, fontsize=11, pad=8)

    # BR: digit-3 contribution per stream — survivor's vs bundle-baseline
    ax = fig.add_subplot(gs[1, 1])
    ax.set_facecolor(BG)
    excess_per_stream = []
    contribs_per_stream = []
    baselines_per_stream = []
    for d in streams:
        if stream_sizes[d] == 0:
            excess_per_stream.append(0)
            contribs_per_stream.append(0)
            baselines_per_stream.append(0)
            continue
        share = stream_sizes[d] / n_surv_total
        contrib = share * stream_dists[d][HIGHLIGHT_DIGIT - 1]
        baseline = share * bundle_dist[HIGHLIGHT_DIGIT - 1]
        excess_per_stream.append(contrib - baseline)
        contribs_per_stream.append(contrib)
        baselines_per_stream.append(baseline)
    width = 0.4
    ax.bar([s - width/2 for s in streams], baselines_per_stream, width=width,
           color=GUIDE, edgecolor=FG, linewidth=0.3,
           label='if survivors had bundle digit-3 freq', zorder=3, alpha=0.7)
    ax.bar([s + width/2 for s in streams], contribs_per_stream, width=width,
           color=[STREAM_PALETTE[d] for d in streams], edgecolor=FG, linewidth=0.3,
           label='actual contribution', zorder=3)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('bottom', 'left'):
        ax.spines[side].set_color(FG)
        ax.spines[side].set_alpha(0.4)
    ax.tick_params(colors=FG)
    ax.set_xticks(streams)
    ax.set_xlabel('source stream d', color=FG, fontsize=10)
    ax.set_ylabel(f'contribution to aggregate digit-{HIGHLIGHT_DIGIT}', color=FG, fontsize=10)
    ax.set_title(f'where the digit-{HIGHLIGHT_DIGIT} excess comes from',
                 color=FG, fontsize=11, pad=8)
    ax.legend(loc='upper right', facecolor='#f0f0f0', fontsize=9)

    fig.suptitle(
        f'EXP07 — survivors stratified by source stream, [{N0}, {N1}], k = {K}',
        color=FG, fontsize=13, fontweight='semibold', y=0.995,
    )

    out = os.path.join(HERE, 'exp07_source_stream_stratification.png')
    fig.savefig(out, dpi=130, facecolor=BG, bbox_inches='tight')
    print(f'\n-> {out}')


if __name__ == '__main__':
    main()
