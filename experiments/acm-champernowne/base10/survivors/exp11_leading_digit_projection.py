"""
exp11_leading_digit_projection.py — derive the L1-gap triangles
from the closed-form K_pair lattice.

EXP05 established that the triangular fingers in the l1_grid heatmap
are NOT in κ (which is smooth) but in the leading-digit projection of
the survivor set. With the closed-form lattice now in hand
(LATTICE-CLOSED-FORM.md), we can compute the same gap heatmap
analytically (no resolution averaging) and decompose its structure
into lattice contributions.

Three observables, all at unit (n_0, K) resolution:

  GAP(K, n_0) = |p_S − u|_1 − |p_B − u|_1
    where p_B = bundle leading-digit dist over W·K atoms,
          p_S = survivor leading-digit dist over the singletons,
          u = uniform-9.
    This is the static endpoint of the l1_grid's running quantity.

  L1_CULL(K, n_0) = |p_C − u|_1
    where p_C = leading-digit dist of culled atoms (weighted by mult),
                = (bundle_ld − surv_ld) / N_C.
    This isolates the lens-side bias: how non-uniform are the
    leading digits of the atoms removed by collisions.

  LATTICE(K, n_0) = Λ_W(K, n_0) (from EXP10) for overlay.

Output:
    exp11_leading_digit_projection.png
    exp11_static_gap.npz         (cached for downstream)
"""

from __future__ import annotations

import os
import time
import math
from itertools import combinations

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'exp11_leading_digit_projection.png')
CACHE = os.path.join(HERE, 'exp11_static_gap.npz')

W = 10
N0_MIN, N0_MAX = 10, 300
K_MAX = 300


def n_primes_vec(n: int, k: int) -> np.ndarray:
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


def k_pair_formula(a: int, b: int) -> int:
    g = math.gcd(a, b)
    pos_a = (b // g) - (b // (g * a))
    pos_b = (a // g) - (a // (g * b))
    return max(pos_a, pos_b)


def leading_digit(n: int) -> int:
    while n >= 10:
        n //= 10
    return n


def compute_gap_grids(n0_min: int, n0_max: int, k_max: int, w: int):
    """Incrementally compute GAP_STATIC, L1_CULL, LATTICE at unit
    resolution. For each n_0, walk K = 1..k_max; at each step add W
    new atoms; update bundle / survivor leading-digit distributions
    via the multiplicity counter."""

    n0_count = n0_max - n0_min + 1
    GAP = np.full((n0_count, k_max), np.nan, dtype=np.float64)
    L1C = np.full((n0_count, k_max), np.nan, dtype=np.float64)
    L1B = np.full((n0_count, k_max), np.nan, dtype=np.float64)
    L1S = np.full((n0_count, k_max), np.nan, dtype=np.float64)
    BENFORD_EXCESS = np.full((n0_count, k_max), np.nan, dtype=np.float64)
    LAMBDA = np.zeros((n0_count, k_max), dtype=np.int32)

    u9 = np.full(9, 1.0 / 9, dtype=np.float64)

    t0 = time.time()
    for i, n0 in enumerate(range(n0_min, n0_max + 1)):
        streams = [n_primes_vec(n, k_max) for n in range(n0, n0 + w)]

        # Lattice via closed form (one pass per n_0)
        for a, b in combinations(range(n0, n0 + w), 2):
            K = k_pair_formula(a, b)
            if 1 <= K <= k_max:
                LAMBDA[i, K - 1] += 1

        counts: dict[int, int] = {}
        bundle_ld = np.zeros(9, dtype=np.int64)
        surv_ld = np.zeros(9, dtype=np.int64)
        n_sing = 0

        for K in range(1, k_max + 1):
            for ni in range(w):
                atom = int(streams[ni][K - 1])
                ld = leading_digit(atom)
                old_c = counts.get(atom, 0)
                counts[atom] = old_c + 1
                bundle_ld[ld - 1] += 1
                if old_c == 0:
                    surv_ld[ld - 1] += 1
                    n_sing += 1
                elif old_c == 1:
                    surv_ld[ld - 1] -= 1
                    n_sing -= 1

            N_B = w * K
            if N_B > 0 and n_sing > 0:
                p_B = bundle_ld / N_B
                p_S = surv_ld / n_sing
                l_b = float(np.abs(p_B - u9).sum())
                l_s = float(np.abs(p_S - u9).sum())
                L1B[i, K - 1] = l_b
                L1S[i, K - 1] = l_s
                GAP[i, K - 1] = l_s - l_b

                N_C = N_B - n_sing
                if N_C > 0:
                    p_C = (bundle_ld - surv_ld) / N_C
                    L1C[i, K - 1] = float(np.abs(p_C - u9).sum())
                    # Benford excess: small-digit mass minus large-digit
                    # mass. + ⇒ culled atoms heavy on digits 1-3
                    # (Benford-like); − ⇒ heavy on digits 7-9.
                    BENFORD_EXCESS[i, K - 1] = float(
                        p_C[0] + p_C[1] + p_C[2]
                        - p_C[6] - p_C[7] - p_C[8]
                    )

        if (i + 1) % 30 == 0:
            print(f'  rows: {i + 1}/{n0_count} (t={time.time() - t0:.1f}s)')

    print(f'  total: {time.time() - t0:.1f}s')
    return GAP, L1C, L1B, L1S, LAMBDA, BENFORD_EXCESS


def main():
    print(f'EXP11 — leading-digit projection at unit resolution')
    print(f'  n_0 ∈ [{N0_MIN}, {N0_MAX}], K ∈ [1, {K_MAX}], W = {W}')

    GAP, L1C, L1B, L1S, LAMBDA, BENFORD_EXCESS = compute_gap_grids(
        N0_MIN, N0_MAX, K_MAX, W)

    np.savez(CACHE, GAP=GAP, L1C=L1C, L1B=L1B, L1S=L1S, LAMBDA=LAMBDA,
             BENFORD_EXCESS=BENFORD_EXCESS,
             N0_MIN=N0_MIN, N0_MAX=N0_MAX, K_MAX=K_MAX, W=W)
    print(f'-> {CACHE}')

    print(f'\nStatic gap range: [{np.nanmin(GAP):+.4f}, {np.nanmax(GAP):+.4f}]')
    print(f'  median |gap|: {np.nanmedian(np.abs(GAP)):.4f}')
    print(f'  median bundle L1 distance: {np.nanmedian(L1B):.4f}')
    print(f'  median surv L1 distance:   {np.nanmedian(L1S):.4f}')
    print(f'  median culled L1 distance: {np.nanmedian(L1C):.4f}')

    # ---- Plot ----
    fig = plt.figure(figsize=(20, 14), dpi=130)
    fig.patch.set_facecolor('#0a0a0a')
    gs = fig.add_gridspec(2, 3, hspace=0.30, wspace=0.20)

    ax_gap = fig.add_subplot(gs[0, 0])
    ax_cull = fig.add_subplot(gs[0, 1])
    ax_lat = fig.add_subplot(gs[0, 2])
    ax_overlay = fig.add_subplot(gs[1, 0])
    ax_l1b = fig.add_subplot(gs[1, 1])
    ax_l1s = fig.add_subplot(gs[1, 2])

    for ax in [ax_gap, ax_cull, ax_lat, ax_overlay, ax_l1b, ax_l1s]:
        ax.set_facecolor('#0a0a0a')

    extent = (0.5, K_MAX + 0.5, N0_MIN - 0.5, N0_MAX + 0.5)

    # === GAP heatmap (diverging) ===
    vmax_g = float(np.nanpercentile(np.abs(GAP), 98))
    norm_g = TwoSlopeNorm(vmin=-vmax_g, vcenter=0.0, vmax=vmax_g)
    im_g = ax_gap.imshow(GAP, aspect='auto', origin='lower', cmap='RdBu_r',
                          norm=norm_g, interpolation='nearest', extent=extent)
    ax_gap.set_title('GAP = |p_S − u|₁ − |p_B − u|₁  (unit resolution)\n'
                      '+ ⇒ survivor MORE non-uniform than bundle',
                      color='white', fontsize=11)
    plt.colorbar(im_g, ax=ax_gap, fraction=0.045, pad=0.02)

    # === Culled-atom Benford excess (signed) ===
    vmax_be = float(np.nanpercentile(np.abs(BENFORD_EXCESS), 98))
    norm_be = TwoSlopeNorm(vmin=-vmax_be, vcenter=0.0, vmax=vmax_be)
    im_c = ax_cull.imshow(BENFORD_EXCESS, aspect='auto', origin='lower',
                           cmap='PuOr_r', norm=norm_be,
                           interpolation='nearest', extent=extent)
    ax_cull.set_title('Benford excess of culled atoms:  '
                      'p_C[1-3] − p_C[7-9]\n'
                      '+ ⇒ culled small-digit-heavy (Benford-like); '
                      '− ⇒ large-digit-heavy',
                      color='white', fontsize=11)
    plt.colorbar(im_c, ax=ax_cull, fraction=0.045, pad=0.02)

    # === Lattice Λ_W ===
    vmax_l = float(LAMBDA.max())
    im_l = ax_lat.imshow(LAMBDA, aspect='auto', origin='lower', cmap='hot',
                          interpolation='nearest', extent=extent,
                          vmin=0, vmax=max(vmax_l, 2))
    ax_lat.set_title('Λ_W(K, n_0)  (closed form, EXP10)\n'
                      'fan of slope-1 band + slope-1/d rays',
                      color='white', fontsize=11)
    plt.colorbar(im_l, ax=ax_lat, fraction=0.045, pad=0.02)

    # === GAP overlaid with lattice rays ===
    im_o = ax_overlay.imshow(GAP, aspect='auto', origin='lower',
                              cmap='RdBu_r', norm=norm_g,
                              interpolation='nearest', extent=extent,
                              alpha=0.95)
    ax_overlay.set_title('GAP with lattice rays overlaid:\n'
                          'finger boundaries align with K = a and K = n_0/d rays',
                          color='white', fontsize=11)
    plt.colorbar(im_o, ax=ax_overlay, fraction=0.045, pad=0.02)
    n_grid = np.linspace(N0_MIN, N0_MAX, 400)
    ax_overlay.plot(n_grid, n_grid, color='#00ffff', linewidth=0.6,
                     alpha=0.5, label='K = a')
    ax_overlay.plot(n_grid + (W - 2), n_grid, color='#ffcc00',
                     linewidth=0.6, alpha=0.5,
                     label=f'K = a + {W - 2}')
    for d in range(2, 6):
        ax_overlay.plot(n_grid / d, n_grid, color='#88ff88',
                         linewidth=0.5, alpha=0.4,
                         label=f'K = n_0/{d}' if d <= 3 else None)
    ax_overlay.legend(loc='upper right', fontsize=8, framealpha=0.4,
                       labelcolor='white', facecolor='#1a1a1a')

    # === Bundle L1 distance ===
    vmax_b = float(np.nanpercentile(L1B, 98))
    im_b = ax_l1b.imshow(L1B, aspect='auto', origin='lower', cmap='viridis',
                          interpolation='nearest', extent=extent,
                          vmin=0, vmax=vmax_b)
    ax_l1b.set_title('|p_B − u|₁  — bundle leading-digit anomaly',
                      color='white', fontsize=11)
    plt.colorbar(im_b, ax=ax_l1b, fraction=0.045, pad=0.02)

    # === Survivor L1 distance ===
    vmax_s = float(np.nanpercentile(L1S, 98))
    im_s = ax_l1s.imshow(L1S, aspect='auto', origin='lower', cmap='viridis',
                          interpolation='nearest', extent=extent,
                          vmin=0, vmax=vmax_s)
    ax_l1s.set_title('|p_S − u|₁  — survivor leading-digit anomaly',
                      color='white', fontsize=11)
    plt.colorbar(im_s, ax=ax_l1s, fraction=0.045, pad=0.02)

    # Reference lines on all panels
    for ax in [ax_gap, ax_cull, ax_lat, ax_l1b, ax_l1s]:
        ax.plot(n_grid, n_grid, color='#00ffff', linewidth=0.5, alpha=0.4)
        ax.plot(n_grid + (W - 2), n_grid, color='#ffcc00', linewidth=0.5,
                alpha=0.4)
        for d in range(2, 6):
            ax.plot(n_grid / d, n_grid, color='#88ff88', linewidth=0.4,
                    alpha=0.35)

    # Axis labels
    for ax in [ax_gap, ax_cull, ax_lat, ax_overlay, ax_l1b, ax_l1s]:
        ax.set_xlabel('K', color='white', fontsize=10)
        ax.set_ylabel('n_0', color='white', fontsize=10)
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#333')
        ax.set_xlim(0.5, K_MAX + 0.5)
        ax.set_ylim(N0_MIN - 0.5, N0_MAX + 0.5)

    fig.suptitle(
        f'EXP11 — leading-digit projection of the K_pair lattice  '
        f'(W = {W}, unit resolution)',
        color='white', fontsize=13, y=0.995
    )
    plt.tight_layout()
    plt.savefig(OUT, dpi=180, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f'-> {OUT}')

    # Numerical correlations
    mask = ~np.isnan(GAP) & ~np.isnan(L1C)
    if mask.any():
        corr_gap_cull = float(np.corrcoef(GAP[mask], L1C[mask])[0, 1])
        print(f'\nCorrelations (over valid cells):')
        print(f'  corr(GAP, |p_C − u|₁)        = {corr_gap_cull:+.4f}  '
              f'(magnitude of culled bias)')
        mask_b = ~np.isnan(GAP) & ~np.isnan(L1B)
        corr_gap_lb = float(np.corrcoef(GAP[mask_b], L1B[mask_b])[0, 1])
        print(f'  corr(GAP, |p_B − u|₁)        = {corr_gap_lb:+.4f}  '
              f'(bundle non-uniformity)')
        mask_be = ~np.isnan(GAP) & ~np.isnan(BENFORD_EXCESS)
        corr_gap_be = float(np.corrcoef(
            GAP[mask_be], BENFORD_EXCESS[mask_be])[0, 1])
        print(f'  corr(GAP, Benford excess)    = {corr_gap_be:+.4f}  '
              f'(SIGNED — directional bias of culled atoms)')
        gap_flat = GAP[mask].astype(np.float64)
        lat_flat = LAMBDA[mask].astype(np.float64)
        if gap_flat.std() > 0 and lat_flat.std() > 0:
            corr_gap_lat = float(np.corrcoef(gap_flat, lat_flat)[0, 1])
            print(f'  corr(GAP, Λ count)           = {corr_gap_lat:+.4f}  '
                  f'(should be ~0; gap is leading-digit, not multiplicity)')


if __name__ == '__main__':
    main()
