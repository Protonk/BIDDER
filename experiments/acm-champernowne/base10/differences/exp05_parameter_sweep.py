"""
exp05_parameter_sweep.py — does the survivor's z-score from random
hold across (n_0, W, k) parameters?

EXP04 found z = +2.21 (L1) and +2.53 (χ²) at the Two Tongues panel
[n_0=2, W=9, k=400]. The result is meaningful but doesn't tell us
whether the signal is robust across panels or specific to this one.

Three sweeps around the Two Tongues center:
  - Vary k ∈ {100, 200, 400, 800} at (n_0=2, W=9)
  - Vary n_0 ∈ {2, 10, 30, 100} at (W=9, k=400)
  - Vary W ∈ {3, 9, 15, 21} at (n_0=2, k=400)

20 random seeds per panel; compute z-score of survivor relative to
random distribution. Plot z vs each axis. If z stays near ~+2, the
signal is robust. If it varies systematically, the variation localises
where the survivor filter's signature is strongest.

Run: sage -python experiments/acm-champernowne/base10/differences/exp05_parameter_sweep.py
"""

from __future__ import annotations

import math
import os
import random
import sys
from collections import Counter
from fractions import Fraction

sys.set_int_max_str_digits(2_000_000)

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

N_SEEDS = 20
SEED_BASE = 0xACAC00

# Sweep grids (Two Tongues center: n_0=2, W=9, k=400)
K_VALUES = [100, 200, 400, 800]
N0_VALUES = [2, 10, 30, 100]
W_VALUES = [3, 9, 15, 21]

BG = '#fafafa'
FG = '#1a1a2e'
PRIM = '#1f4e79'
ACCENT = '#c0392b'
NEUTRAL = '#7e7e9e'
HILIGHT = '#b8860b'
GUIDE = '#aaaaaa'


def digits_to_real(s: str) -> Fraction:
    if not s:
        return Fraction(1)
    return Fraction(1) + Fraction(int(s), 10 ** len(s))


def expand_digits(r: Fraction, n: int) -> list[int]:
    assert 0 <= r < 1
    digits = []
    cur = r
    for _ in range(n):
        cur *= 10
        d = int(cur)
        digits.append(d)
        cur -= d
    return digits


def digit_stats(digits):
    counts = Counter(digits)
    n = len(digits)
    if n == 0:
        return None, None, None
    freq = np.array([counts[d] / n for d in range(10)])
    chi2 = float(np.sum((np.array([counts[d] for d in range(10)]) - n / 10) ** 2 / (n / 10)))
    l1 = float(np.abs(freq - 0.1).sum())
    return freq, chi2, l1


def measure_panel(n_0, W, k):
    n_1 = n_0 + W - 1
    atoms = bundle_atoms(n_0, n_1, k)
    mask = survival_mask(atoms)
    n_bundle = len(atoms)
    n_surv = sum(mask)
    if n_surv == 0:
        return None

    bundle_str = ''.join(str(m) for _, m in atoms)
    surv_str = ''.join(str(m) for (_, m), keep in zip(atoms, mask) if keep)
    L_bundle = len(bundle_str)
    L_surv = len(surv_str)

    c_bundle = digits_to_real(bundle_str)
    c_surv = digits_to_real(surv_str)
    delta = c_bundle - c_surv
    abs_d = delta if delta > 0 else -delta
    if abs_d == 0:
        return None

    surv_full = expand_digits(abs_d, L_bundle)
    surv_overlap = surv_full[:L_surv]
    _, surv_chi2, surv_l1 = digit_stats(surv_overlap)

    rand_l1s = []
    rand_chi2s = []
    for s in range(N_SEEDS):
        rng = random.Random(SEED_BASE + s)
        keep_idx = sorted(rng.sample(range(n_bundle), n_surv))
        kept = [atoms[i] for i in keep_idx]
        rand_str = ''.join(str(m) for _, m in kept)
        L_rand = len(rand_str)
        c_rand = digits_to_real(rand_str)
        d_rand = c_bundle - c_rand
        abs_r = d_rand if d_rand > 0 else -d_rand
        if abs_r == 0:
            continue
        rand_full = expand_digits(abs_r, L_bundle)
        rand_overlap = rand_full[:L_rand]
        _, rchi2, rl1 = digit_stats(rand_overlap)
        if rchi2 is not None:
            rand_l1s.append(rl1)
            rand_chi2s.append(rchi2)

    if len(rand_l1s) < 5:
        return None

    rand_l1_mean = float(np.mean(rand_l1s))
    rand_l1_std = float(np.std(rand_l1s))
    rand_chi2_mean = float(np.mean(rand_chi2s))
    rand_chi2_std = float(np.std(rand_chi2s))

    z_l1 = (surv_l1 - rand_l1_mean) / rand_l1_std if rand_l1_std > 0 else 0.0
    z_chi2 = (surv_chi2 - rand_chi2_mean) / rand_chi2_std if rand_chi2_std > 0 else 0.0

    return {
        'n_0': n_0, 'W': W, 'k': k,
        'n_bundle': n_bundle, 'n_surv': n_surv,
        'survival_rate': n_surv / n_bundle,
        'L_surv': L_surv, 'L_bundle': L_bundle,
        'surv_l1': surv_l1, 'surv_chi2': surv_chi2,
        'rand_l1_mean': rand_l1_mean, 'rand_l1_std': rand_l1_std,
        'rand_chi2_mean': rand_chi2_mean, 'rand_chi2_std': rand_chi2_std,
        'z_l1': z_l1, 'z_chi2': z_chi2,
    }


def main():
    # Build the grid of unique (n_0, W, k) to compute
    panels = set()
    for k in K_VALUES:
        panels.add((2, 9, k))
    for n0 in N0_VALUES:
        panels.add((n0, 9, 400))
    for w in W_VALUES:
        panels.add((2, w, 400))

    print(f'unique panels to compute: {len(panels)}')
    print(f'random seeds per panel: {N_SEEDS}')
    print()

    results = {}
    for i, (n0, w, k) in enumerate(sorted(panels)):
        print(f'  [{i+1}/{len(panels)}] n_0={n0}, W={w}, k={k} ...', flush=True)
        res = measure_panel(n0, w, k)
        if res is None:
            print(f'    (skipped — degenerate)')
            continue
        results[(n0, w, k)] = res
        print(f'    n_bundle={res["n_bundle"]}, n_surv={res["n_surv"]} '
              f'({100*res["survival_rate"]:.1f}%), '
              f'L1: surv={res["surv_l1"]:.4f} rand={res["rand_l1_mean"]:.4f}±{res["rand_l1_std"]:.4f}  '
              f'z_L1={res["z_l1"]:+.2f}, z_χ²={res["z_chi2"]:+.2f}')

    # Build sweep series
    k_sweep = [(k, results[(2, 9, k)]) for k in K_VALUES if (2, 9, k) in results]
    n0_sweep = [(n0, results[(n0, 9, 400)]) for n0 in N0_VALUES if (n0, 9, 400) in results]
    w_sweep = [(w, results[(2, w, 400)]) for w in W_VALUES if (2, w, 400) in results]

    print(f'\n  k sweep (at n_0=2, W=9):')
    for k, r in k_sweep:
        print(f'    k = {k:>4}: z_L1 = {r["z_l1"]:+.2f}, z_χ² = {r["z_chi2"]:+.2f}, '
              f'surv_rate = {100*r["survival_rate"]:.1f}%')
    print(f'\n  n_0 sweep (at W=9, k=400):')
    for n0, r in n0_sweep:
        print(f'    n_0 = {n0:>3}: z_L1 = {r["z_l1"]:+.2f}, z_χ² = {r["z_chi2"]:+.2f}, '
              f'surv_rate = {100*r["survival_rate"]:.1f}%')
    print(f'\n  W sweep (at n_0=2, k=400):')
    for w, r in w_sweep:
        print(f'    W = {w:>2}: z_L1 = {r["z_l1"]:+.2f}, z_χ² = {r["z_chi2"]:+.2f}, '
              f'surv_rate = {100*r["survival_rate"]:.1f}%')

    # Plot — 2x2 panels
    fig = plt.figure(figsize=(13, 9), facecolor=BG)
    gs = fig.add_gridspec(2, 2, hspace=0.32, wspace=0.28)

    def setup_axes(ax, xlabel, title):
        ax.set_facecolor(BG)
        for side in ('top', 'right'):
            ax.spines[side].set_visible(False)
        for side in ('bottom', 'left'):
            ax.spines[side].set_color(FG)
            ax.spines[side].set_alpha(0.4)
        ax.tick_params(colors=FG)
        ax.axhline(0, color=FG, linewidth=0.6, alpha=0.5)
        ax.axhline(2, color=GUIDE, linewidth=0.7, linestyle=':',
                   alpha=0.6, label='|z| = 2')
        ax.axhline(-2, color=GUIDE, linewidth=0.7, linestyle=':', alpha=0.6)
        ax.set_xlabel(xlabel, color=FG, fontsize=10)
        ax.set_ylabel('z-score (survivor vs random)', color=FG, fontsize=10)
        ax.set_title(title, color=FG, fontsize=11, pad=8)

    def plot_sweep(ax, sweep, xlabel, title, xscale='linear'):
        if not sweep:
            ax.text(0.5, 0.5, '(no data)', transform=ax.transAxes,
                    ha='center', va='center', color=FG)
            return
        xs = [x for x, _ in sweep]
        z_l1 = [r['z_l1'] for _, r in sweep]
        z_chi2 = [r['z_chi2'] for _, r in sweep]
        ax.plot(xs, z_l1, marker='o', color=ACCENT, linewidth=1.6,
                markersize=8, label='z (L1)', zorder=4)
        ax.plot(xs, z_chi2, marker='s', color=PRIM, linewidth=1.6,
                markersize=7, label='z (χ²)', zorder=4)
        # Mark the Two Tongues center
        for x, r in sweep:
            if (r['n_0'], r['W'], r['k']) == (2, 9, 400):
                ax.scatter([x], [r['z_l1']], s=180, facecolor='none',
                           edgecolor=HILIGHT, linewidth=1.8, zorder=5)
                ax.annotate('Two Tongues', xy=(x, r['z_l1']),
                            xytext=(8, 14), textcoords='offset points',
                            color=HILIGHT, fontsize=8.5, ha='left')
        for side in ('top', 'right'):
            ax.spines[side].set_visible(False)
        for side in ('bottom', 'left'):
            ax.spines[side].set_color(FG)
            ax.spines[side].set_alpha(0.4)
        ax.tick_params(colors=FG)
        ax.axhline(0, color=FG, linewidth=0.6, alpha=0.5)
        ax.axhline(2, color=GUIDE, linewidth=0.7, linestyle=':', alpha=0.6)
        ax.axhline(-2, color=GUIDE, linewidth=0.7, linestyle=':', alpha=0.6)
        ax.set_xlabel(xlabel, color=FG, fontsize=10)
        ax.set_ylabel('z-score (survivor vs random)', color=FG, fontsize=10)
        ax.set_title(title, color=FG, fontsize=11, pad=8)
        if xscale == 'log':
            ax.set_xscale('log')
        ax.set_xticks(xs)
        ax.set_xticklabels([str(x) for x in xs])
        ax.legend(loc='best', facecolor='#f0f0f0', fontsize=9)

    ax_k = fig.add_subplot(gs[0, 0])
    plot_sweep(ax_k, k_sweep, 'k (per-stream truncation)',
               f'sweep k at n_0=2, W=9', xscale='log')

    ax_n0 = fig.add_subplot(gs[0, 1])
    plot_sweep(ax_n0, n0_sweep, 'n_0 (window start)',
               f'sweep n_0 at W=9, k=400', xscale='log')

    ax_w = fig.add_subplot(gs[1, 0])
    plot_sweep(ax_w, w_sweep, 'W (window width)',
               f'sweep W at n_0=2, k=400')

    # Stats panel
    ax_stats = fig.add_subplot(gs[1, 1])
    ax_stats.set_facecolor(BG)
    ax_stats.axis('off')
    lines = ['parameter sweep summary',
             f'{N_SEEDS} random seeds per panel',
             '']
    lines.append('  axis    value    n_bundle  n_surv    z_L1     z_χ²')
    lines.append('  ' + '-' * 48)
    lines.append('  k sweep (n_0=2, W=9):')
    for k, r in k_sweep:
        lines.append(f'    k =   {k:>4}  {r["n_bundle"]:>6}    {r["n_surv"]:>6}    '
                     f'{r["z_l1"]:+5.2f}    {r["z_chi2"]:+5.2f}')
    lines.append('  n_0 sweep (W=9, k=400):')
    for n0, r in n0_sweep:
        lines.append(f'    n_0 = {n0:>4}  {r["n_bundle"]:>6}    {r["n_surv"]:>6}    '
                     f'{r["z_l1"]:+5.2f}    {r["z_chi2"]:+5.2f}')
    lines.append('  W sweep (n_0=2, k=400):')
    for w, r in w_sweep:
        lines.append(f'    W =     {w:>2}  {r["n_bundle"]:>6}    {r["n_surv"]:>6}    '
                     f'{r["z_l1"]:+5.2f}    {r["z_chi2"]:+5.2f}')
    ax_stats.text(0.02, 0.98, '\n'.join(lines), transform=ax_stats.transAxes,
                  color=FG, fontsize=9, va='top', ha='left',
                  family='monospace')
    ax_stats.set_title('summary table', color=FG, fontsize=11, pad=8)

    fig.suptitle(
        'EXP05 — parameter sweep: does z ≈ +2.2 hold across (n_0, W, k)?',
        color=FG, fontsize=13, fontweight='semibold', y=0.995,
    )

    out = os.path.join(HERE, 'exp05_parameter_sweep.png')
    fig.savefig(out, dpi=130, facecolor=BG, bbox_inches='tight')
    print(f'\n-> {out}')


if __name__ == '__main__':
    main()
