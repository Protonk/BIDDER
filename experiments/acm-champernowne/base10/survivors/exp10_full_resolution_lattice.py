"""
exp10_full_resolution_lattice.py — render Λ_W at unit resolution.

EXP07 computed `∂κ/∂K` (= COLL up to multi-share corrections) at 10×10
heatmap cells, averaging out the K_pair lattice. With Theorem 1 we
can now compute Λ_W in closed form at every (n_0, K) point — no
empirical walk, no resolution averaging — and see the fan
decomposition explicitly.

What this script renders:

  Panel 1 — full-resolution Λ_W at unit (n_0, K) cells.
    The slope-1 (r=1, g=1) family lives on K = a, NOT K = n_0 + 1
    (the off-by-one reference line that EXP07's annotation drew).
    Slope-1/d rays for d = 2, …, W-1 spread out below.

  Panel 2 — zoom on small n_0 to make individual rays visible.

  Panel 3 — side-by-side comparison to EXP07's downsampled version,
    same coordinates, to show what averaging hid.

Sanity check: Λ_W summed over rows should equal C(W, 2) per n_0.

Outputs:
    exp10_full_resolution_lattice.png
"""

from __future__ import annotations

import os
import math
import time
from itertools import combinations

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'exp10_full_resolution_lattice.png')

W = 10
N0_MIN, N0_MAX = 10, 1000
K_MIN, K_MAX = 1, 1000
ZOOM_N0 = (50, 200)
ZOOM_K = (1, 220)


def k_pair_formula(a: int, b: int) -> int:
    """Closed-form K_pair (window regime). General form, valid for
    a < b with a² ∤ b: max(b/g − ⌊b/(g·a)⌋, a/g − ⌊a/(g·b)⌋)."""
    g = math.gcd(a, b)
    pos_a = (b // g) - (b // (g * a))
    pos_b = (a // g) - (a // (g * b))
    return max(pos_a, pos_b)


def build_lambda_grid(n0_min: int, n0_max: int, k_min: int, k_max: int,
                      w: int) -> np.ndarray:
    """Λ_W at unit resolution. Rows index n_0 (n0_min..n0_max),
    columns index K (k_min..k_max)."""
    n0_count = n0_max - n0_min + 1
    k_count = k_max - k_min + 1
    L = np.zeros((n0_count, k_count), dtype=np.int32)
    t0 = time.time()
    for i, n0 in enumerate(range(n0_min, n0_max + 1)):
        for a, b in combinations(range(n0, n0 + w), 2):
            K = k_pair_formula(a, b)
            if k_min <= K <= k_max:
                L[i, K - k_min] += 1
        if (i + 1) % 200 == 0:
            print(f'  rows: {i + 1}/{n0_count} (t={time.time() - t0:.1f}s)')
    print(f'  total: {time.time() - t0:.1f}s')
    return L


def build_lambda_downsampled(n0_min: int, n0_max: int, k_min: int,
                             k_max: int, w: int, step_n0: int = 10,
                             step_k: int = 10) -> np.ndarray:
    """For comparison with EXP07: average Λ_W over step_n0 × step_k
    cells, mimicking the downsampled view. We sum (not average) so
    each cell counts the integral over the box.
    """
    n0_count = (n0_max - n0_min + 1) // step_n0
    k_count = (k_max - k_min + 1) // step_k
    L = np.zeros((n0_count, k_count), dtype=np.int32)
    for i, n0_lo in enumerate(range(n0_min, n0_min + n0_count * step_n0,
                                     step_n0)):
        for n0 in range(n0_lo, n0_lo + step_n0):
            for a, b in combinations(range(n0, n0 + w), 2):
                K = k_pair_formula(a, b)
                if k_min <= K <= k_max:
                    j = (K - k_min) // step_k
                    if 0 <= j < k_count:
                        L[i, j] += 1
    return L


def main():
    print(f'Building full-resolution lattice: '
          f'n_0 ∈ [{N0_MIN}, {N0_MAX}], K ∈ [{K_MIN}, {K_MAX}], W = {W}')
    LAMBDA = build_lambda_grid(N0_MIN, N0_MAX, K_MIN, K_MAX, W)

    # Sanity check
    n_pairs = W * (W - 1) // 2
    row_sums = LAMBDA.sum(axis=1)
    print(f'  expected pairs per row: C(W, 2) = {n_pairs}')
    print(f'  observed: min={row_sums.min()}, max={row_sums.max()}, '
          f'mean={row_sums.mean():.1f}')
    if row_sums.min() < n_pairs:
        # Some pairs have K_pair > K_MAX — verify this is expected
        n_outside = n_pairs - row_sums.min()
        print(f'  note: {n_outside} pair(s) per row land outside [K_MIN, K_MAX]')

    # Build downsampled version for the comparison panel
    print('Building downsampled (10×10) version for EXP07-comparison panel')
    LAMBDA_DS = build_lambda_downsampled(N0_MIN, N0_MAX, K_MIN, K_MAX, W,
                                          step_n0=10, step_k=10)

    # ---- Plot ----
    fig = plt.figure(figsize=(20, 14), dpi=130)
    fig.patch.set_facecolor('#0a0a0a')

    gs = fig.add_gridspec(2, 2, height_ratios=[1.1, 1.0],
                          hspace=0.22, wspace=0.18)

    ax_full = fig.add_subplot(gs[0, :])
    ax_zoom = fig.add_subplot(gs[1, 0])
    ax_ds = fig.add_subplot(gs[1, 1])

    for ax in [ax_full, ax_zoom, ax_ds]:
        ax.set_facecolor('#0a0a0a')

    # === Panel 1: full-resolution Λ_W ===
    extent_full = (K_MIN - 0.5, K_MAX + 0.5, N0_MIN - 0.5, N0_MAX + 0.5)
    # Use full multiplicity range so trailing-edge cells (where g=1
    # sub-rays superimpose) show their max value cleanly.
    vmax_full = float(LAMBDA.max())
    im_full = ax_full.imshow(LAMBDA, aspect='auto', origin='lower',
                              cmap='hot', interpolation='nearest',
                              extent=extent_full,
                              vmin=0, vmax=vmax_full)
    ax_full.set_title(
        f'Λ_W(K, n_0) at full unit resolution  '
        f'(W = {W}, every cell = one (n_0, K) point; closed-form, no walk)',
        color='white', fontsize=13, pad=10)
    cbar = plt.colorbar(im_full, ax=ax_full, fraction=0.025, pad=0.01,
                        label='# pairs at this (K, n_0); '
                              'leading edge = 1, trailing edge ≤ W − 1')
    cbar.ax.yaxis.label.set_color('white')
    cbar.ax.tick_params(colors='white')

    # Reference rays
    n_grid = np.linspace(N0_MIN, N0_MAX, 800)
    # Leading and trailing edge of the slope-1 g=1 band.
    ax_full.plot(n_grid, n_grid, color='#00ffff', linewidth=0.8,
                 alpha=0.85,
                 label='K = a   (band leading edge, r=1 g=1, mult 1)')
    ax_full.plot(n_grid + (W - 2), n_grid, color='#ffcc00', linewidth=0.8,
                 alpha=0.85,
                 label=f'K = a + {W-2}   (band trailing edge, '
                       f'mult up to W−1)')
    # Old EXP07 reference (one step into the band)
    ax_full.plot(n_grid + 1, n_grid, color='#ff66ff', linewidth=0.7,
                 alpha=0.55, linestyle='--',
                 label='K = n_0 + 1   (EXP07 guide; sits inside the band, '
                       'not at edge)')
    # Slope-1/d rays for d = 2, ..., W-1
    for d in range(2, W):
        col = plt.cm.viridis(0.25 + 0.7 * (d - 2) / (W - 3))
        lab = f'K = n_0 / {d}   (g = {d} ray)' if d <= 5 else None
        ax_full.plot(n_grid / d, n_grid, color=col, linewidth=0.75,
                     alpha=0.6, label=lab)

    ax_full.set_xlim(K_MIN - 0.5, K_MAX + 0.5)
    ax_full.set_ylim(N0_MIN - 0.5, N0_MAX + 0.5)
    ax_full.set_xlabel('K', color='white', fontsize=11)
    ax_full.set_ylabel(f'n_0  (window=[n_0, n_0+{W-1}])', color='white',
                        fontsize=11)
    ax_full.tick_params(colors='white')
    for spine in ax_full.spines.values():
        spine.set_color('#333')
    ax_full.legend(loc='lower right', fontsize=9, framealpha=0.6,
                   labelcolor='white', facecolor='#1a1a1a')

    # === Panel 2 (bottom-left): zoom on small n_0 ===
    z0_n0, z1_n0 = ZOOM_N0
    z0_K, z1_K = ZOOM_K
    i0 = z0_n0 - N0_MIN
    i1 = z1_n0 - N0_MIN + 1
    j0 = z0_K - K_MIN
    j1 = z1_K - K_MIN + 1
    LAMBDA_ZOOM = LAMBDA[i0:i1, j0:j1]
    extent_zoom = (z0_K - 0.5, z1_K + 0.5, z0_n0 - 0.5, z1_n0 + 0.5)
    nonzero_z = LAMBDA_ZOOM[LAMBDA_ZOOM > 0]
    vmax_zoom = float(nonzero_z.max()) if nonzero_z.size else 1.0
    im_zoom = ax_zoom.imshow(LAMBDA_ZOOM, aspect='auto', origin='lower',
                              cmap='hot', interpolation='nearest',
                              extent=extent_zoom,
                              vmin=0, vmax=vmax_zoom)
    ax_zoom.set_title(
        f'Zoom: n_0 ∈ [{z0_n0}, {z1_n0}], K ∈ [{z0_K}, {z1_K}]\n'
        f'slope-1 band has width W−1; multiplicity grows from 1 (left) '
        f'to up to W−1 (right)',
        color='white', fontsize=11)
    plt.colorbar(im_zoom, ax=ax_zoom, fraction=0.045, pad=0.02,
                 label='# pairs')
    n_grid_z = np.linspace(z0_n0, z1_n0, 200)
    ax_zoom.plot(n_grid_z, n_grid_z, color='#00ffff', linewidth=0.7,
                 alpha=0.75, label='K = a   (leading)')
    ax_zoom.plot(n_grid_z + (W - 2), n_grid_z, color='#ffcc00',
                 linewidth=0.7, alpha=0.75,
                 label=f'K = a+{W-2}  (trailing)')
    ax_zoom.plot(n_grid_z + 1, n_grid_z, color='#ff66ff', linewidth=0.5,
                 alpha=0.45, linestyle='--', label='K = n_0+1')
    for d in range(2, 6):
        col = plt.cm.viridis(0.2 + 0.7 * (d - 2) / 3)
        ax_zoom.plot(n_grid_z / d, n_grid_z, color=col, linewidth=0.6,
                     alpha=0.6, label=f'K = n_0/{d}' if d <= 4 else None)
    ax_zoom.set_xlim(z0_K - 0.5, z1_K + 0.5)
    ax_zoom.set_ylim(z0_n0 - 0.5, z1_n0 + 0.5)
    ax_zoom.set_xlabel('K', color='white', fontsize=10)
    ax_zoom.set_ylabel('n_0', color='white', fontsize=10)
    ax_zoom.tick_params(colors='white')
    for spine in ax_zoom.spines.values():
        spine.set_color('#333')
    ax_zoom.legend(loc='upper right', fontsize=8, framealpha=0.5,
                   labelcolor='white', facecolor='#1a1a1a')

    # === Panel 3 (bottom-middle): EXP07-style downsampled ===
    extent_ds = (K_MIN - 5, K_MIN + LAMBDA_DS.shape[1] * 10 - 5,
                 N0_MIN - 5, N0_MIN + LAMBDA_DS.shape[0] * 10 - 5)
    nonzero_ds = LAMBDA_DS[LAMBDA_DS > 0]
    vmax_ds = float(np.percentile(nonzero_ds, 99)) if nonzero_ds.size else 1.0
    im_ds = ax_ds.imshow(LAMBDA_DS, aspect='auto', origin='lower',
                          cmap='hot', interpolation='nearest',
                          extent=extent_ds,
                          vmin=0, vmax=max(vmax_ds, 2))
    ax_ds.set_title('EXP07-style 10×10 downsample\n'
                    '(sums in 10×10 boxes; rays visible but blurred)',
                    color='white', fontsize=11)
    plt.colorbar(im_ds, ax=ax_ds, fraction=0.045, pad=0.02,
                 label='Σ pairs in 10×10 cell')
    ax_ds.set_xlim(K_MIN - 5, N0_MAX + 5)
    ax_ds.set_ylim(N0_MIN - 5, N0_MAX + 5)
    ax_ds.set_xlabel('K (10-cell bins)', color='white', fontsize=10)
    ax_ds.set_ylabel('n_0 (10-cell bins)', color='white', fontsize=10)
    ax_ds.tick_params(colors='white')
    for spine in ax_ds.spines.values():
        spine.set_color('#333')

    fig.suptitle(
        'EXP10 — full-resolution K_pair lattice via closed-form Theorem 1.  '
        'Slope-1 band has explicit width W−1 with multiplicity growing '
        'left→right; slope-1/d rays for d=2..W−1 fan out below.',
        color='white', fontsize=13, y=0.998
    )
    plt.tight_layout()
    plt.savefig(OUT, dpi=180, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f'-> {OUT}')

    # Numerical summary of fan structure
    print('\n--- Fan statistics ---')
    print(f'Total nonzero (n_0, K) cells in [{N0_MIN}..{N0_MAX}, '
          f'{K_MIN}..{K_MAX}]: {int((LAMBDA > 0).sum())}')
    print(f'Total pair-events (sum Λ): {int(LAMBDA.sum())}')
    print(f'Cells with Λ ≥ 2 (multiple rays overlapping): '
          f'{int((LAMBDA >= 2).sum())}')
    print(f'Max Λ per cell: {int(LAMBDA.max())}')
    if LAMBDA.max() > 0:
        max_idx = np.unravel_index(LAMBDA.argmax(), LAMBDA.shape)
        max_n0 = max_idx[0] + N0_MIN
        max_K = max_idx[1] + K_MIN
        print(f'  achieved at: n_0 = {max_n0}, K = {max_K}')
        # which pairs land there?
        pairs_at_max = []
        for a, b in combinations(range(max_n0, max_n0 + W), 2):
            if k_pair_formula(a, b) == max_K:
                pairs_at_max.append((a, b, math.gcd(a, b - a)))
        print(f'  pairs (a, b, g): {pairs_at_max}')


if __name__ == '__main__':
    main()
