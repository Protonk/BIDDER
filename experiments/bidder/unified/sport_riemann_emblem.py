"""
sport_riemann_emblem.py — emblem render for wonders/sport-riemann-sum-identity.md.

Single-panel convergence-event image. 25 keys, each producing a running
MC estimate of ∫₀¹ sin(πx) dx via bidder.cipher(P=2000, key); plot the
estimates over sample size N on a linear y-axis. The 25 trajectories
wiggle differently across the parameter space and all land on the same
single point at N = P, exactly. The emblem's caption is the spread
across the 25 keys at N = P (≈ machine ε; functionally zero).

Companion to the four-panel diagnostic in riemann_proof.py; this is the
emblem extracted from Panel 1, larger and tighter.

Run: sage -python experiments/bidder/unified/sport_riemann_emblem.py
"""

from __future__ import annotations

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, REPO)

import bidder  # noqa: E402


P = 2000
N_KEYS = 25
F_NAME = 'sin(πx)'
F_FUNC = lambda x: np.sin(np.pi * x)
F_TRUE = 2.0 / np.pi

BG = '#0a0a0a'
FG = '#ffffff'
DIM = '#666666'
RIEMANN_COL = '#ffcc5c'
TRUE_COL = '#ff6f61'
PALETTE = plt.cm.viridis(np.linspace(0.1, 0.95, N_KEYS))


def main():
    # Compute trajectories
    sample_sizes = np.unique(np.geomspace(10, P, num=200).astype(int))
    sample_sizes = np.concatenate([sample_sizes, [P]])
    sample_sizes = np.unique(sample_sizes)

    print(f'computing {N_KEYS} trajectories over P = {P}, f(x) = {F_NAME} ...')
    trajectories = []
    final_estimates = []
    for k in range(N_KEYS):
        key = f'sport-emblem-{k}'.encode()
        B = bidder.cipher(period=P, key=key)
        full = np.array([F_FUNC(B.at(i) / P) for i in range(P)])
        cumsum = np.cumsum(full)
        estimates = cumsum[sample_sizes - 1] / sample_sizes
        trajectories.append(estimates)
        final_estimates.append(cumsum[-1] / P)
    final_estimates = np.array(final_estimates)

    riemann_sum = float(np.mean([F_FUNC(k / P) for k in range(P)]))
    spread = float(final_estimates.max() - final_estimates.min())

    print(f'  Riemann sum = {riemann_sum:.12f}')
    print(f'  true int    = {F_TRUE:.12f}')
    print(f'  spread @ N=P = {spread:.3e}')

    # Render
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=BG)
    ax.set_facecolor(BG)

    # horizontal guide at the Riemann sum (the convergence value)
    ax.axhline(riemann_sum, color=RIEMANN_COL, linewidth=1.2, alpha=0.7,
               linestyle='--', zorder=2)
    ax.text(P * 1.03, riemann_sum,
            f' R = {riemann_sum:.6f}\n true ∫ = 2/π (gap = {abs(F_TRUE - riemann_sum):.1e})',
            color=RIEMANN_COL, fontsize=9, va='center')

    # 25 trajectories
    for k, traj in enumerate(trajectories):
        ax.plot(sample_sizes, traj, color=PALETTE[k], linewidth=0.9,
                alpha=0.55, zorder=3)

    # convergence-point marker
    ax.scatter([P], [riemann_sum], color=RIEMANN_COL, s=80, zorder=5,
               edgecolors=BG, linewidths=1.2)

    # vertical guide at N = P
    ax.axvline(P, color=DIM, linewidth=1.0, linestyle=':', alpha=0.6,
               zorder=1)
    ax.text(P, ax.get_ylim()[1] * 0.99, f' N = P = {P}',
            color=DIM, fontsize=9, va='top', ha='left')

    # caption: the spread
    spread_text = (
        f'{N_KEYS} keys → one point\n'
        f'spread at N = P:  {spread:.2e}\n'
        f'(machine ε; functionally zero)'
    )
    ax.text(0.02, 0.97, spread_text, transform=ax.transAxes,
            color=FG, fontsize=10, va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='#1a1a1a',
                      edgecolor='#333', alpha=0.85))

    # axes / spines
    for spine in ax.spines.values():
        spine.set_color('#333')
    ax.tick_params(colors=FG, which='both')
    ax.set_xlabel('sample size N', color=FG, fontsize=11)
    ax.set_ylabel(f'MC estimate of ∫ {F_NAME} dx', color=FG, fontsize=11)
    ax.set_title(
        f'Sport: The N=P Riemann-Sum Identity — {N_KEYS} keys, one destination',
        color=FG, fontsize=13.5, pad=12, fontweight='semibold',
    )

    # zoom y-axis to the relevant region (final estimates ± modest pad)
    y_lo = min(min(t.min() for t in trajectories), F_TRUE, riemann_sum) - 0.04
    y_hi = max(max(t.max() for t in trajectories), F_TRUE, riemann_sum) + 0.04
    ax.set_ylim(y_lo, y_hi)
    ax.set_xlim(5, P * 1.15)
    ax.set_xscale('log')

    fig.tight_layout()
    out = os.path.join(HERE, 'sport_riemann_emblem.png')
    fig.savefig(out, dpi=150, facecolor=BG)
    print(f'-> {out}')


if __name__ == '__main__':
    main()
