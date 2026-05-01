"""
exp07_kappa_derivative.py — does ∂κ/∂K reveal the K_pair lattice?

κ(K, n_0) is smooth (EXP05); the question is whether its K-derivative
isolates the discrete pair-collision events. At each K_pair(n_a, n_b),
two streams' K-th atoms are equal — a "collision event" — and the
singleton count S takes a step-down. Between events, S grows by W
per K-step (every new atom is a fresh singleton). So:

    dS/dK = W - 2 · (#collision events at this K-step)

A heatmap of `(W - dS/dK)/2` should show the K_pair lattice as
sharp bright cells, with zero background.

Implementation: incremental K-walk per n_0. For each new atom m,
update its count and singleton-count delta. O(W*K_max) per n_0.

Outputs:
    exp07_kappa_derivative.png
"""

from __future__ import annotations

import os
import sys
import time

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

OUT = os.path.join(HERE, 'exp07_kappa_derivative.png')

W = 10
N0_VALUES = np.arange(10, 1001, 10)   # step 10, matching l1_grid axis
K_MAX = 1000                            # finer step (every K)


def n_primes_vec(n: int, k: int) -> np.ndarray:
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


def collision_events_curve(n0: int, w: int, k_max: int):
    """For each K = 1..k_max, count the number of collision events that
    happen at step K-1 → K (atoms in the W new atoms that duplicate
    something already in the bundle, OR collide with another new atom
    in the same step). Returns array of length k_max.

    A "collision event" reduces dS/dK by 2 vs the no-collision baseline
    of dS/dK = W.
    """
    streams = [n_primes_vec(n, k_max) for n in range(n0, n0 + w)]
    counts = {}
    n_singletons = 0
    coll = np.zeros(k_max, dtype=np.int32)
    S = np.zeros(k_max, dtype=np.int64)
    for K in range(1, k_max + 1):
        prev_S = n_singletons
        for ni in range(w):
            m = int(streams[ni][K - 1])
            old_c = counts.get(m, 0)
            counts[m] = old_c + 1
            if old_c == 0:
                n_singletons += 1
            elif old_c == 1:
                n_singletons -= 1
            # else (old_c >= 2): no change
        # Collision events at this step = W - dS = W - (n_singletons - prev_S)
        # Each collision event is one atom that didn't become a fresh
        # singleton (either it duplicated an existing singleton, killing
        # both, or it duplicated an existing duplicate, doing nothing
        # but still not becoming a singleton).
        # Note: "two streams add the same atom in the same step" counts
        # as 2 collision events here (each contributes -1 to dS).
        coll[K - 1] = w - (n_singletons - prev_S)
        S[K - 1] = n_singletons
    return coll, S


def main():
    print(f'Computing collision events: {len(N0_VALUES)} n_0 × {K_MAX} K')
    t0 = time.time()
    COLL = np.zeros((len(N0_VALUES), K_MAX), dtype=np.int32)
    S_GRID = np.zeros((len(N0_VALUES), K_MAX), dtype=np.int64)
    for i, n0 in enumerate(N0_VALUES):
        coll, S = collision_events_curve(int(n0), W, K_MAX)
        COLL[i] = coll
        S_GRID[i] = S
        if (i + 1) % 20 == 0:
            print(f'  rows: {i + 1}/{len(N0_VALUES)} (t={time.time() - t0:.1f}s)')
    print(f'Total: {time.time() - t0:.1f}s')

    print(f'Collision events per cell: max = {COLL.max()}, mean = {COLL.mean():.3f}')
    n_nonzero = int((COLL > 0).sum())
    print(f'Non-zero cells: {n_nonzero} of {COLL.size} '
          f'({100 * n_nonzero / COLL.size:.2f}%)')

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(20, 10), dpi=130)
    fig.patch.set_facecolor('#0a0a0a')
    for ax in axes:
        ax.set_facecolor('#0a0a0a')

    # Extent: K on x (every 1), n_0 on y (every 10).
    extent = (0.5, K_MAX + 0.5, N0_VALUES[0] - 5, N0_VALUES[-1] + 5)

    # Panel 1: collision events (the main result)
    ax = axes[0]
    # Use log color scale — events are sparse. Cap vmax to avoid wash-out.
    vmax = float(np.percentile(COLL[COLL > 0], 99)) if (COLL > 0).any() else 1.0
    im1 = ax.imshow(COLL, aspect='auto', origin='lower', cmap='hot',
                    interpolation='nearest', extent=extent,
                    vmin=0, vmax=max(vmax, 2))
    ax.set_title('collision events per K-step\n'
                 '(W − dS/dK; bright = pair-collision activation)',
                 color='white', fontsize=12)
    plt.colorbar(im1, ax=ax, fraction=0.040, pad=0.02,
                 label='events at this K-step')

    # Panel 2: cumulative collision count (= culled atoms count)
    # equivalent: W*K - S
    K_arr = np.arange(1, K_MAX + 1)
    culled = W * K_arr[None, :] - S_GRID
    im2 = ax2 = axes[1]
    im2 = ax2.imshow(culled, aspect='auto', origin='lower', cmap='magma',
                     interpolation='nearest', extent=extent)
    ax2.set_title('cumulative culled count\n(= W·K − S; smooth — same info as κ)',
                  color='white', fontsize=12)
    plt.colorbar(im2, ax=ax2, fraction=0.040, pad=0.02)

    # Reference curves on both panels
    n_grid = np.linspace(N0_VALUES[0], N0_VALUES[-1], 400)
    for ax in axes:
        ax.plot(n_grid + 1, n_grid, color='#00ffff', linewidth=0.7,
                alpha=0.6, label='K = n_0 + 1')
        ax.plot(n_grid / 2, n_grid, color='#88ff88', linewidth=0.7,
                alpha=0.5, label='K = n_0 / 2')
        ax.plot(n_grid / 3, n_grid, color='#ffff88', linewidth=0.7,
                alpha=0.4, label='K = n_0 / 3')
        ax.set_xlim(0.5, K_MAX + 0.5)
        ax.set_ylim(N0_VALUES[0] - 5, N0_VALUES[-1] + 5)
        ax.set_xlabel('K (atoms per stream)', color='white', fontsize=11)
        ax.set_ylabel(f'n_0 (window=[n_0, n_0+{W-1}])', color='white', fontsize=11)
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#333')

    axes[0].legend(loc='upper right', fontsize=9, framealpha=0.4,
                   labelcolor='white', facecolor='#1a1a1a')

    fig.suptitle(
        '∂κ/∂K reveals the lattice: collision events at each K-step (left), '
        'vs the smooth integral (right)',
        color='white', fontsize=13, y=0.995
    )

    plt.tight_layout()
    plt.savefig(OUT, dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f'-> {OUT}')


if __name__ == '__main__':
    main()
