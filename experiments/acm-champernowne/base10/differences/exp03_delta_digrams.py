"""
exp03_delta_digrams.py — pair correlations (digrams) of δ's overlap region.

EXP01 found single-digit frequencies in δ's overlap region with a
distinctive 0-and-9 spike (the subtraction-with-borrows signature).
This experiment goes one rank up: look at consecutive digit pairs
(d_i, d_{i+1}) and ask whether the borrow signature has internal
structure beyond what single-digit frequencies predict.

If the digrams are independent (P(d, d') = P(d) · P(d')), then the
single-digit view captures everything. If they're not, δ carries
*pair-level* structure that single-digit views averaged out — and
the user's intuition was right: the transducer was only mostly
destructive, with residual content pushed into pair correlations.

Bundle's own overlap-region digrams are a control: if δ has digrams
that bundle doesn't, those are subtraction-specific.

Run: sage -python experiments/acm-champernowne/base10/differences/exp03_delta_digrams.py
"""

from __future__ import annotations

import math
import os
import sys
from collections import Counter
from fractions import Fraction

sys.set_int_max_str_digits(1_000_000)

import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = HERE
for _ in range(4):
    REPO = os.path.dirname(REPO)
sys.path.insert(0, os.path.join(REPO, 'core'))
sys.path.insert(0, os.path.join(REPO, 'experiments', 'acm-champernowne',
                                'base10', 'survivors'))

from survivors_core import bundle_atoms, survival_mask  # noqa: E402


N0, N1, K = 2, 10, 400

BG = '#fafafa'
FG = '#1a1a2e'
GUIDE = '#aaaaaa'


def digits_to_real(s: str) -> Fraction:
    if not s:
        return Fraction(1)
    return Fraction(1) + Fraction(int(s), 10 ** len(s))


def expand_digits(r: Fraction, n: int) -> list[int]:
    assert 0 <= r < 1, f'expected r in [0, 1), got {float(r)}'
    digits = []
    cur = r
    for _ in range(n):
        cur *= 10
        d = int(cur)
        digits.append(d)
        cur -= d
    return digits


def joint_distribution(digit_seq):
    """10x10 matrix of P(d_i, d_{i+1}) frequencies."""
    counts = np.zeros((10, 10), dtype=np.int64)
    for i in range(len(digit_seq) - 1):
        counts[digit_seq[i], digit_seq[i + 1]] += 1
    total = counts.sum()
    return counts / total, counts, total


def independence_deviation(joint, marginals):
    """joint - marginals[i]*marginals[j]."""
    indep = np.outer(marginals, marginals)
    return joint - indep, indep


def mutual_information(joint):
    """I(X;Y) = sum_{i,j} p(i,j) log(p(i,j) / (p(i)p(j)))."""
    p_x = joint.sum(axis=1)
    p_y = joint.sum(axis=0)
    info = 0.0
    for i in range(10):
        for j in range(10):
            if joint[i, j] > 0 and p_x[i] > 0 and p_y[j] > 0:
                info += joint[i, j] * math.log2(joint[i, j] / (p_x[i] * p_y[j]))
    return info


def chi_squared_independence(counts, total):
    """Standard chi-squared statistic for the 10x10 contingency table."""
    p_x = counts.sum(axis=1) / total
    p_y = counts.sum(axis=0) / total
    expected = total * np.outer(p_x, p_y)
    mask = expected > 0
    return float(np.sum((counts[mask] - expected[mask]) ** 2 / expected[mask]))


def main():
    print(f'building bundle for [{N0}, {N1}], k = {K} ...')
    atoms = bundle_atoms(N0, N1, K)
    mask = survival_mask(atoms)

    bundle_str = ''.join(str(m) for _, m in atoms)
    surv_str = ''.join(str(m) for (_, m), keep in zip(atoms, mask) if keep)
    L_bundle = len(bundle_str)
    L_surv = len(surv_str)
    print(f'  C_Bundle: {L_bundle:,} digits')
    print(f'  C_Surv:   {L_surv:,} digits')

    c_bundle = digits_to_real(bundle_str)
    c_surv = digits_to_real(surv_str)
    delta = c_bundle - c_surv
    abs_delta = delta if delta > 0 else -delta

    # Overlap region: first L_surv digits — where the genuine subtraction lives.
    overlap_n = L_surv
    print(f'\n  expanding |δ| to {L_bundle:,} digits, taking first {overlap_n:,} as overlap ...')
    delta_digits_full = expand_digits(abs_delta, L_bundle)
    delta_digits = delta_digits_full[:overlap_n]

    # Bundle digit sequence (control) — first overlap_n digits of bundle's stream
    bundle_digits = [int(c) for c in bundle_str[:overlap_n]]

    # Joint distributions
    delta_joint, delta_counts, delta_total = joint_distribution(delta_digits)
    bundle_joint, bundle_counts, bundle_total = joint_distribution(bundle_digits)

    # Marginals (averaging over both axes)
    delta_marg = (delta_joint.sum(axis=0) + delta_joint.sum(axis=1)) / 2
    bundle_marg = (bundle_joint.sum(axis=0) + bundle_joint.sum(axis=1)) / 2

    # Deviations from independence
    delta_dev, delta_indep = independence_deviation(delta_joint, delta_joint.sum(axis=0))
    bundle_dev, bundle_indep = independence_deviation(bundle_joint, bundle_joint.sum(axis=0))

    # Statistics
    delta_chi2 = chi_squared_independence(delta_counts, delta_total)
    bundle_chi2 = chi_squared_independence(bundle_counts, bundle_total)
    delta_mi = mutual_information(delta_joint)
    bundle_mi = mutual_information(bundle_joint)

    print(f'\n  pair-frequency stats over overlap region ({overlap_n - 1:,} pairs):')
    print(f'    δ:       χ²(81 dof) = {delta_chi2:>8.2f}, MI = {delta_mi:.5f} bits')
    print(f'    bundle:  χ²(81 dof) = {bundle_chi2:>8.2f}, MI = {bundle_mi:.5f} bits')

    # Top anomalous pairs in δ (signed deviation from independence)
    flat = [(i, j, delta_dev[i, j]) for i in range(10) for j in range(10)]
    flat_sorted = sorted(flat, key=lambda x: -abs(x[2]))
    print(f'\n  top 10 anomalous digit pairs in δ (deviation from independence):')
    print(f'    pair (d_i, d_{{i+1}})  joint freq  indep pred  deviation')
    for i, j, d in flat_sorted[:10]:
        joint = delta_joint[i, j]
        indep = delta_indep[i, j]
        print(f'    ({i}, {j})              {joint:.5f}     {indep:.5f}    {d:+.5f}')

    # Plot — 2x2: δ joint, δ deviation, bundle deviation, stats text
    fig = plt.figure(figsize=(13, 11), facecolor=BG)
    gs = fig.add_gridspec(2, 2, hspace=0.32, wspace=0.32)

    def draw_heatmap(ax, matrix, title, cmap, vmin=None, vmax=None,
                     fmt='.4f', annotate=True):
        ax.set_facecolor(BG)
        if vmax is None:
            vmax = max(abs(matrix.min()), abs(matrix.max()))
            vmin = -vmax if matrix.min() < 0 else 0
        im = ax.imshow(matrix, cmap=cmap, vmin=vmin, vmax=vmax,
                       origin='upper', aspect='equal')
        if annotate:
            for i in range(10):
                for j in range(10):
                    val = matrix[i, j]
                    color = (FG if abs(val) < 0.5 * max(abs(vmin), abs(vmax))
                             else 'white')
                    ax.text(j, i, f'{val:{fmt}}', ha='center', va='center',
                            color=color, fontsize=7)
        ax.set_xticks(range(10))
        ax.set_yticks(range(10))
        ax.set_xlabel('$d_{i+1}$', color=FG, fontsize=10)
        ax.set_ylabel('$d_i$', color=FG, fontsize=10)
        ax.set_title(title, color=FG, fontsize=11, pad=8)
        ax.tick_params(colors=FG)
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    # TL: δ joint
    ax1 = fig.add_subplot(gs[0, 0])
    draw_heatmap(ax1, delta_joint,
                 f'δ joint frequency  P($d_i$, $d_{{i+1}}$)',
                 cmap='Blues', vmin=0, vmax=delta_joint.max())

    # TR: δ deviation
    ax2 = fig.add_subplot(gs[0, 1])
    dev_max = max(abs(delta_dev.min()), abs(delta_dev.max()))
    draw_heatmap(ax2, delta_dev,
                 f'δ deviation from independence  (max |dev| = {dev_max:.4f})',
                 cmap='RdBu_r', vmin=-dev_max, vmax=dev_max)

    # BL: bundle deviation (control)
    ax3 = fig.add_subplot(gs[1, 0])
    bdev_max = max(abs(bundle_dev.min()), abs(bundle_dev.max()))
    draw_heatmap(ax3, bundle_dev,
                 f'bundle deviation (control)  (max |dev| = {bdev_max:.4f})',
                 cmap='RdBu_r', vmin=-bdev_max, vmax=bdev_max)

    # BR: stats and top pairs
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_facecolor(BG)
    ax4.axis('off')
    lines = [
        f'overlap region: {overlap_n:,} digits, {overlap_n - 1:,} pairs',
        '',
        f'              χ² (81 dof)    MI (bits)',
        f'  δ          {delta_chi2:>8.2f}    {delta_mi:.5f}',
        f'  bundle     {bundle_chi2:>8.2f}    {bundle_mi:.5f}',
        '',
        f'top 10 most anomalous pairs in δ:',
        f'  (d_i, d_{{i+1}})   joint     indep    deviation',
        '  ' + '-' * 44,
    ]
    for i, j, d in flat_sorted[:10]:
        joint = delta_joint[i, j]
        indep = delta_indep[i, j]
        sign = '+' if d > 0 else '−'
        lines.append(
            f'  ({i}, {j})            {joint:.4f}   {indep:.4f}   {sign}{abs(d):.4f}'
        )
    ax4.text(0.04, 0.97, '\n'.join(lines), transform=ax4.transAxes,
             color=FG, fontsize=10, va='top', ha='left',
             family='monospace')
    ax4.set_title('statistics and anomalous pairs',
                  color=FG, fontsize=11, pad=8)

    fig.suptitle(
        f'EXP03 — digit-pair correlations of |δ = C_Bundle − C_Surv|  '
        f'overlap region, [{N0}, {N1}], k = {K}',
        color=FG, fontsize=13, fontweight='semibold', y=0.995,
    )

    out = os.path.join(HERE, 'exp03_delta_digrams.png')
    fig.savefig(out, dpi=130, facecolor=BG, bbox_inches='tight')
    print(f'\n-> {out}')


if __name__ == '__main__':
    main()
