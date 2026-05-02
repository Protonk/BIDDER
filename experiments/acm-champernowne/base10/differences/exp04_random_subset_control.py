"""
exp04_random_subset_control.py — random-subset control for δ.

The cabinet's Two Tongues curiosity hangs on one question:
*does the survivor filter's L1-tracking property generalise to any
37%-thinning of the bundle, or is it specific to the survivor
construction?*

EXP01-03 characterised δ = C_Bundle − C_Surv directly: the digit-
frequency view returned a borrow signature; the CF view returned
generic; the digram view returned a weak residual. None of those
results separates "the survivor filter is special" from "any
random thinning would look like this."

This experiment computes δ_random for many random subsets matching
the survivor's atom count (1338 of 3600 atoms, preserving bundle
read-order), and compares the digit-frequency signature to δ_surv's.

If random and survivor produce the same signature, the survivor
filter is no more special than a uniform-random selection at this
observable. If they differ, the survivor filter has a digit-level
fingerprint.

Run: sage -python experiments/acm-champernowne/base10/differences/exp04_random_subset_control.py
"""

from __future__ import annotations

import math
import os
import random
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
N_SEEDS = 50
SEED_BASE = 0xACAC00

BG = '#fafafa'
FG = '#1a1a2e'
PRIM = '#1f4e79'
ACCENT = '#c0392b'
RAND = '#7e7e9e'
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


def digit_freq(digits):
    counts = Counter(digits)
    n = len(digits)
    freq = np.array([counts[d] / n for d in range(10)])
    chi2 = float(np.sum((np.array([counts[d] for d in range(10)]) - n / 10) ** 2
                        / (n / 10)))
    l1 = float(np.abs(freq - 0.1).sum())
    return freq, chi2, l1


def main():
    print(f'building bundle for [{N0}, {N1}], k = {K} ...')
    atoms = bundle_atoms(N0, N1, K)
    mask = survival_mask(atoms)
    n_bundle = len(atoms)
    n_surv = sum(mask)
    print(f'  {n_bundle} atoms, {n_surv} survivors '
          f'({100 * n_surv / n_bundle:.1f}%)')

    bundle_str = ''.join(str(m) for _, m in atoms)
    surv_str = ''.join(str(m) for (_, m), keep in zip(atoms, mask) if keep)
    L_bundle = len(bundle_str)
    L_surv = len(surv_str)
    print(f'  C_Bundle: {L_bundle:,} digits')
    print(f'  C_Surv:   {L_surv:,} digits')

    c_bundle = digits_to_real(bundle_str)
    c_surv = digits_to_real(surv_str)
    delta_surv = c_bundle - c_surv
    abs_delta_surv = delta_surv if delta_surv > 0 else -delta_surv

    # Survivor's overlap-region digits
    surv_full_digits = expand_digits(abs_delta_surv, L_bundle)
    surv_overlap_digits = surv_full_digits[:L_surv]
    surv_freq, surv_chi2, surv_l1 = digit_freq(surv_overlap_digits)
    print(f'\n  δ_survivor overlap signature: L1 = {surv_l1:.4f}, χ²(9 dof) = {surv_chi2:.2f}')

    # Random-subset controls
    print(f'\n  running {N_SEEDS} random-subset controls (size {n_surv} '
          f'of {n_bundle}, preserving order) ...')
    random_freqs = []
    random_chi2s = []
    random_l1s = []
    random_overlap_lens = []

    for s in range(N_SEEDS):
        rng = random.Random(SEED_BASE + s)
        keep_idx = sorted(rng.sample(range(n_bundle), n_surv))
        kept_atoms = [atoms[i] for i in keep_idx]
        rand_str = ''.join(str(m) for _, m in kept_atoms)
        L_rand = len(rand_str)
        random_overlap_lens.append(L_rand)

        c_rand = digits_to_real(rand_str)
        delta_rand = c_bundle - c_rand
        abs_delta_rand = delta_rand if delta_rand > 0 else -delta_rand
        # Could be 0 in extremely rare degenerate cases
        if abs_delta_rand == 0:
            continue

        rand_full_digits = expand_digits(abs_delta_rand, L_bundle)
        rand_overlap_digits = rand_full_digits[:L_rand]
        rfreq, rchi2, rl1 = digit_freq(rand_overlap_digits)
        random_freqs.append(rfreq)
        random_chi2s.append(rchi2)
        random_l1s.append(rl1)

    random_freqs = np.array(random_freqs)
    rand_freq_mean = random_freqs.mean(axis=0)
    rand_freq_std = random_freqs.std(axis=0)
    rand_chi2_mean = float(np.mean(random_chi2s))
    rand_chi2_std = float(np.std(random_chi2s))
    rand_l1_mean = float(np.mean(random_l1s))
    rand_l1_std = float(np.std(random_l1s))

    print(f'\n  random subset distributions ({len(random_l1s)} successful seeds):')
    print(f'    overlap length: mean = {np.mean(random_overlap_lens):,.0f}, '
          f'std = {np.std(random_overlap_lens):.0f}')
    print(f'    L1 from uniform-1/10:  {rand_l1_mean:.4f} ± {rand_l1_std:.4f}')
    print(f'    χ²(9 dof):             {rand_chi2_mean:.2f} ± {rand_chi2_std:.2f}')

    # Z-scores for the survivor relative to the random distribution
    z_l1 = (surv_l1 - rand_l1_mean) / rand_l1_std if rand_l1_std > 0 else float('nan')
    z_chi2 = (surv_chi2 - rand_chi2_mean) / rand_chi2_std if rand_chi2_std > 0 else float('nan')
    print(f'\n  survivor vs random:')
    print(f'    survivor L1   = {surv_l1:.4f}, random {rand_l1_mean:.4f} ± {rand_l1_std:.4f}    z = {z_l1:+.2f}')
    print(f'    survivor χ²   = {surv_chi2:.2f},  random {rand_chi2_mean:.2f} ± {rand_chi2_std:.2f}    z = {z_chi2:+.2f}')

    # Per-digit comparison
    print(f'\n  per-digit comparison (survivor vs random mean):')
    print(f'    digit | surv freq | rand mean ± std       | z-score')
    print(f'    ------+-----------+-----------------------+---------')
    z_per_digit = np.zeros(10)
    for d in range(10):
        z = ((surv_freq[d] - rand_freq_mean[d]) / rand_freq_std[d]
             if rand_freq_std[d] > 0 else float('nan'))
        z_per_digit[d] = z
        print(f'      {d}   |  {surv_freq[d]:.4f}   |  {rand_freq_mean[d]:.4f} ± {rand_freq_std[d]:.4f}    | {z:+.2f}')

    # Plot — 2x2 layout
    fig = plt.figure(figsize=(13, 9), facecolor=BG)
    gs = fig.add_gridspec(2, 2, hspace=0.32, wspace=0.28)

    # TL: per-digit frequency comparison
    ax = fig.add_subplot(gs[0, 0])
    ax.set_facecolor(BG)
    digits = np.arange(10)
    width = 0.36
    ax.bar(digits - width/2, surv_freq, width=width, color=ACCENT,
           edgecolor=FG, linewidth=0.4, label='δ_survivor (overlap)', zorder=3)
    ax.bar(digits + width/2, rand_freq_mean, width=width, color=RAND,
           edgecolor=FG, linewidth=0.4,
           label=f'δ_random mean ({len(random_l1s)} seeds)', zorder=3,
           yerr=rand_freq_std, capsize=3, ecolor=FG, error_kw={'linewidth': 0.8})
    ax.axhline(0.1, color=GUIDE, linewidth=1.0, linestyle='--', zorder=2,
               label='uniform: 1/10')
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('bottom', 'left'):
        ax.spines[side].set_color(FG)
        ax.spines[side].set_alpha(0.4)
    ax.tick_params(colors=FG)
    ax.set_xticks(digits)
    ax.set_xlabel('digit', color=FG, fontsize=10)
    ax.set_ylabel('frequency', color=FG, fontsize=10)
    ax.set_title('δ digit frequency: survivor vs random subset',
                 color=FG, fontsize=11, pad=8)
    ax.legend(loc='upper right', facecolor='#f0f0f0', fontsize=9)

    # TR: L1 distribution histogram
    ax = fig.add_subplot(gs[0, 1])
    ax.set_facecolor(BG)
    ax.hist(random_l1s, bins=20, color=RAND, edgecolor=FG, linewidth=0.4,
            alpha=0.85, label='δ_random L1 (seeds)', zorder=3)
    ax.axvline(surv_l1, color=ACCENT, linewidth=2.2, linestyle='-',
               label=f'δ_survivor L1 = {surv_l1:.4f}', zorder=4)
    ax.axvline(rand_l1_mean, color=PRIM, linewidth=1.2, linestyle='--',
               label=f'random mean = {rand_l1_mean:.4f}', zorder=4)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('bottom', 'left'):
        ax.spines[side].set_color(FG)
        ax.spines[side].set_alpha(0.4)
    ax.tick_params(colors=FG)
    ax.set_xlabel('L1 from uniform-1/10', color=FG, fontsize=10)
    ax.set_ylabel('count', color=FG, fontsize=10)
    ax.set_title(f'L1 distribution: survivor at z = {z_l1:+.2f}',
                 color=FG, fontsize=11, pad=8)
    ax.legend(loc='upper right', facecolor='#f0f0f0', fontsize=9)

    # BL: per-digit z-scores
    ax = fig.add_subplot(gs[1, 0])
    ax.set_facecolor(BG)
    bar_colors = [ACCENT if abs(z) > 2 else RAND for z in z_per_digit]
    ax.bar(digits, z_per_digit, color=bar_colors, edgecolor=FG,
           linewidth=0.4, zorder=3)
    ax.axhline(0, color=FG, linewidth=0.6, alpha=0.5, zorder=2)
    for thresh, color, label in [(2.0, '#888', '±2σ'), (3.0, '#444', '±3σ')]:
        ax.axhline(thresh, color=color, linewidth=0.7, linestyle=':', alpha=0.6)
        ax.axhline(-thresh, color=color, linewidth=0.7, linestyle=':', alpha=0.6)
    for d in digits:
        ax.text(d, z_per_digit[d] + (0.15 if z_per_digit[d] >= 0 else -0.15),
                f'{z_per_digit[d]:+.2f}',
                ha='center', va='bottom' if z_per_digit[d] >= 0 else 'top',
                color=FG, fontsize=9)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('bottom', 'left'):
        ax.spines[side].set_color(FG)
        ax.spines[side].set_alpha(0.4)
    ax.tick_params(colors=FG)
    ax.set_xticks(digits)
    ax.set_xlabel('digit', color=FG, fontsize=10)
    ax.set_ylabel('z-score (survivor vs random)', color=FG, fontsize=10)
    ax.set_title('per-digit z-score: survivor digit freq relative to random distribution',
                 color=FG, fontsize=11, pad=8)

    # BR: stats text
    ax = fig.add_subplot(gs[1, 1])
    ax.set_facecolor(BG)
    ax.axis('off')
    lines = [
        f'panel parameters: [{N0}, {N1}], k = {K}',
        f'bundle atoms:  {n_bundle}',
        f'subset size:   {n_surv} (survivor count)',
        f'random seeds:  {len(random_l1s)}',
        '',
        f'digit-frequency stats (overlap region):',
        f'',
        f'                    survivor      random mean ± std    z',
        f'  L1 from 1/10:     {surv_l1:.4f}        {rand_l1_mean:.4f} ± {rand_l1_std:.4f}      {z_l1:+.2f}',
        f'  χ² (9 dof):      {surv_chi2:>7.2f}        {rand_chi2_mean:>7.2f} ± {rand_chi2_std:.2f}      {z_chi2:+.2f}',
        '',
        f'per-digit z-score:',
    ]
    for d in range(10):
        flag = ' *' if abs(z_per_digit[d]) > 2 else '  '
        lines.append(f'    {d}: {z_per_digit[d]:+.2f}{flag}')
    lines.append('')
    lines.append('* = |z| > 2  (significantly different from random control)')
    ax.text(0.02, 0.98, '\n'.join(lines), transform=ax.transAxes,
            color=FG, fontsize=9.5, va='top', ha='left',
            family='monospace')

    fig.suptitle(
        f'EXP04 — random-subset control for δ  ([{N0}, {N1}], k = {K}, '
        f'subset size = survivor count, {N_SEEDS} seeds)',
        color=FG, fontsize=13, fontweight='semibold', y=0.995,
    )

    out = os.path.join(HERE, 'exp04_random_subset_control.png')
    fig.savefig(out, dpi=130, facecolor=BG, bbox_inches='tight')
    print(f'\n-> {out}')


if __name__ == '__main__':
    main()
