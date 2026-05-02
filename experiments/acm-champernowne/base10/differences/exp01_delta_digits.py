"""
exp01_delta_digits.py — first reading of δ = C_Bundle − C_Surv.

Compute the difference of the two reals at the Two Tongues panel
parameters (Survivors §"Proposal 2"), expand |δ| to many decimal
digits, plot the digit-frequency histogram against the uniform-1/10
baseline. The L1 work in survivors/ measures frequency divergence
between bundle and survivor; this measures POSITIONAL divergence.

If δ's digits look uniform/random, the L1-tracking story is the
whole story. If δ exhibits Benford-like, anti-Benford-like, or
anomalous structure, the relation has a residual that the L1 view
averages.

Run: sage -python experiments/acm-champernowne/base10/differences/exp01_delta_digits.py
"""

from __future__ import annotations

import os
import sys
from collections import Counter
from fractions import Fraction

# Python 3.11+ caps int<->str conversion at 4300 digits by default.
# C_Bundle here is ~13k digits; raise the limit for this experiment.
sys.set_int_max_str_digits(1_000_000)

import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
# differences -> base10 -> acm-champernowne -> experiments -> BIDDER
REPO = HERE
for _ in range(4):
    REPO = os.path.dirname(REPO)
sys.path.insert(0, os.path.join(REPO, 'core'))
sys.path.insert(0, os.path.join(REPO, 'experiments', 'acm-champernowne',
                                'base10', 'survivors'))

from survivors_core import bundle_atoms, survival_mask  # noqa: E402


# Two Tongues panel parameters
N0, N1, K = 2, 10, 400

# Visual palette — analytic register, matching cabinet light emblems
BG = '#fafafa'
FG = '#1a1a2e'
BAR_DEFAULT = '#3a5a7a'
BAR_HIGH = '#c0392b'
BAR_LOW = '#1f4e79'
GUIDE = '#aaaaaa'
BENFORD = '#b8860b'


def digits_to_real(s: str) -> Fraction:
    """Return 1 + 0.<s> as a Fraction (the C_Bundle / C_Surv form)."""
    if not s:
        return Fraction(1)
    return Fraction(1) + Fraction(int(s), 10 ** len(s))


def expand_digits(r: Fraction, n: int) -> list[int]:
    """Expand 0 <= r < 1 to n decimal digits."""
    assert 0 <= r < 1, f'expected r in [0, 1), got {float(r)}'
    digits = []
    cur = r
    for _ in range(n):
        cur *= 10
        d = int(cur)
        digits.append(d)
        cur -= d
    return digits


def main():
    print(f'building bundle for [{N0}, {N1}], k = {K} ...')
    atoms = bundle_atoms(N0, N1, K)
    mask = survival_mask(atoms)
    n_bundle = len(atoms)
    n_surv = sum(mask)
    print(f'  {n_bundle} atoms, {n_surv} survivors '
          f'({100 * n_surv / n_bundle:.1f}%)')

    bundle_digits_str = ''.join(str(m) for _, m in atoms)
    surv_digits_str = ''.join(str(m) for (_, m), keep in zip(atoms, mask) if keep)
    print(f'  C_Bundle: {len(bundle_digits_str):,} digits')
    print(f'  C_Surv:   {len(surv_digits_str):,} digits')

    c_bundle = digits_to_real(bundle_digits_str)
    c_surv = digits_to_real(surv_digits_str)
    delta = c_bundle - c_surv
    sign = 1 if delta > 0 else (-1 if delta < 0 else 0)
    abs_delta = delta if sign >= 0 else -delta

    print(f'\n  C_Bundle  ≈ {float(c_bundle):.12f}')
    print(f'  C_Surv    ≈ {float(c_surv):.12f}')
    print(f'  δ         ≈ {float(delta):+.6e}   (sign: {sign:+d})')

    # Expand |δ| to L_b digits — the full meaningful range.
    n_digits = len(bundle_digits_str)
    overlap_n = len(surv_digits_str)
    tail_n = n_digits - overlap_n
    print(f'\n  expanding |δ| to {n_digits:,} decimal digits ...')
    delta_digits = expand_digits(abs_delta, n_digits)
    head = ''.join(str(d) for d in delta_digits[:80])
    print(f'  first 80 digits of |δ|: {head}')

    # Structural split: since C_Surv contributes zero after digit L_s,
    # the last (L_b − L_s) digits of δ are just bundle's last
    # (L_b − L_s) digits. The substantive subtraction lives in the
    # first L_s digits.
    overlap_digits = delta_digits[:overlap_n]
    tail_digits = delta_digits[overlap_n:]
    print(f'  overlap region (first {overlap_n:,} digits): bundle vs survivor')
    print(f'  tail (last {tail_n:,} digits): identical to bundle\'s tail '
          f'(C_Surv contributes 0 there)')

    def freq_of(digit_list):
        counts = Counter(digit_list)
        total = len(digit_list)
        return (np.array([counts[d] / total for d in range(10)]),
                counts, total)

    full_freq, full_counts, full_total = freq_of(delta_digits)
    over_freq, over_counts, over_total = freq_of(overlap_digits)
    tail_freq, tail_counts, tail_total = freq_of(tail_digits)

    def chi2_of(counts, total):
        exp = total / 10
        return float(np.sum((np.array([counts[d] for d in range(10)]) - exp) ** 2
                            / exp))

    full_l1 = float(np.abs(full_freq - 0.1).sum())
    over_l1 = float(np.abs(over_freq - 0.1).sum())
    tail_l1 = float(np.abs(tail_freq - 0.1).sum())
    full_chi2 = chi2_of(full_counts, full_total)
    over_chi2 = chi2_of(over_counts, over_total)
    tail_chi2 = chi2_of(tail_counts, tail_total)

    print(f'\n  region          | digits   | L1 vs 1/10 | χ² (9 dof)')
    print(f'  ----------------+----------+------------+-----------')
    print(f'  full δ          | {full_total:>7,}  | {full_l1:.4f}     | {full_chi2:>7.2f}')
    print(f'  overlap (first) | {over_total:>7,}  | {over_l1:.4f}     | {over_chi2:>7.2f}')
    print(f'  tail (last)     | {tail_total:>7,}  | {tail_l1:.4f}     | {tail_chi2:>7.2f}')

    # Plot — three panels stacked: full, overlap, tail
    fig, axes = plt.subplots(1, 3, figsize=(15, 6), facecolor=BG)

    panels = [
        ('full δ', full_freq, full_total, full_l1, full_chi2),
        (f'overlap (first {over_total:,} digits)', over_freq, over_total, over_l1, over_chi2),
        (f'tail (last {tail_total:,} digits)', tail_freq, tail_total, tail_l1, tail_chi2),
    ]

    digits = np.arange(10)
    for ax, (label, freq, total, l1, chi2) in zip(axes, panels):
        ax.set_facecolor(BG)
        bar_colors = [BAR_HIGH if freq[d] > 0.105
                      else BAR_LOW if freq[d] < 0.095
                      else BAR_DEFAULT for d in range(10)]
        ax.bar(digits, freq, color=bar_colors, edgecolor=FG,
               linewidth=0.5, width=0.7, zorder=3)
        ax.axhline(0.1, color=GUIDE, linewidth=1.0, linestyle='--', zorder=2)
        for d in digits:
            ax.text(d, freq[d] + 0.002, f'{freq[d]:.3f}',
                    ha='center', va='bottom', color=FG, fontsize=8)
        for side in ('top', 'right'):
            ax.spines[side].set_visible(False)
        for side in ('bottom', 'left'):
            ax.spines[side].set_color(FG)
            ax.spines[side].set_alpha(0.4)
        ax.tick_params(colors=FG, which='both')
        ax.set_xticks(digits)
        ax.set_xlabel('digit', color=FG, fontsize=10)
        ax.set_ylim(0, max(freq.max() + 0.018, 0.16))
        ax.set_title(label, color=FG, fontsize=11, pad=8)
        caption = f'L1 = {l1:.4f}\nχ² = {chi2:.1f}'
        ax.text(0.97, 0.97, caption, transform=ax.transAxes,
                color=FG, fontsize=9, va='top', ha='right',
                family='monospace',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#f0f0f0',
                          edgecolor=GUIDE, alpha=0.9))

    axes[0].set_ylabel('frequency', color=FG, fontsize=11)

    sign_str = 'positive' if sign > 0 else ('negative' if sign < 0 else 'zero')
    fig.suptitle(
        f'EXP01 — digit frequency of |δ = C_Bundle − C_Surv|  '
        f'at [{N0}, {N1}], k = {K}    '
        f'(δ ≈ {float(delta):+.3e}, {sign_str})',
        color=FG, fontsize=13, fontweight='semibold', y=0.98,
    )

    fig.text(0.5, 0.02,
             f'(C_Bundle has {len(bundle_digits_str):,} digits; '
             f'C_Surv has {len(surv_digits_str):,}. The last '
             f'{tail_n:,} digits of δ are bundle\'s tail — '
             f'C_Surv contributes zero there.)',
             color=GUIDE, fontsize=8.5, ha='center', style='italic')

    fig.tight_layout(rect=[0, 0.05, 1, 0.94])
    out = os.path.join(HERE, 'exp01_delta_digits.png')
    fig.savefig(out, dpi=150, facecolor=BG)
    print(f'\n-> {out}')


if __name__ == '__main__':
    main()
