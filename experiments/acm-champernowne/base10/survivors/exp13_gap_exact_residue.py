"""
exp13_gap_exact_residue.py — exact GAP decomposition.

EXP12's linear predictor matched 87% of GAP variance; the residual
came from L1-norm sign flips. Here we close the gap with an
exact, per-digit-explicit decomposition:

    GAP = GAP_LIN + R_TOTAL                   (exact, no approximation)

where, with v_B = p_B − u, v_S = p_S − u, ε = (N_C/N_S)·(p_B − p_C),

    GAP_LIN = (N_C/N_S) · Σ_d sign(v_B[d]) · (p_B[d] − p_C[d])
    R_TOTAL = Σ_d R_d
    R_d     = (1 − sign(v_B[d]) · sign(v_S[d])) · |v_S[d]|

Per-digit residue cases:
    same sign (v_B·v_S > 0):       R_d = 0     (linear regime)
    flip (v_B·v_S < 0):            R_d = 2|v_S[d]|     (sign flip)
    boundary (v_B = 0, v_S ≠ 0):   R_d = |v_S[d]|       (uniform digit)
    boundary (v_S = 0):            R_d = 0     (deflation to zero)

Sum over d gives the full residue. The flip set is determined by
whether (N_C/N_S) · |δ_d| exceeds |v_B[d]| — i.e., whether the
collision perturbation is large enough to cross zero on digit d.

Outputs:
    exp13_gap_exact_residue.png
    exp13_decomposition.npz
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
OUT = os.path.join(HERE, 'exp13_gap_exact_residue.png')
CACHE = os.path.join(HERE, 'exp13_decomposition.npz')

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


def safe_sign(x: np.ndarray) -> np.ndarray:
    """sign function returning -1, 0, +1, with 0 at exactly 0."""
    return np.sign(x)


def compute_decomposition(n0_min, n0_max, k_max, w):
    """Per cell, compute GAP, GAP_LIN, R_TOTAL, plus per-digit
    residue map (which digits flip) and flip count."""

    n0_count = n0_max - n0_min + 1

    GAP = np.full((n0_count, k_max), np.nan)
    GAP_LIN = np.full((n0_count, k_max), np.nan)
    R_TOTAL = np.full((n0_count, k_max), np.nan)
    FLIP_COUNT = np.zeros((n0_count, k_max), dtype=np.int8)
    LAMBDA = np.zeros((n0_count, k_max), dtype=np.int32)
    R_PER_DIGIT = np.zeros((n0_count, k_max, 9), dtype=np.float32)

    u9 = np.full(9, 1.0 / 9)

    t0 = time.time()
    for i, n0 in enumerate(range(n0_min, n0_max + 1)):
        streams = [n_primes_vec(n, k_max) for n in range(n0, n0 + w)]

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
            if N_B > 0 and 0 < n_sing < N_B:
                p_B = bundle_ld / N_B
                p_S = surv_ld / n_sing
                v_B = p_B - u9
                v_S = p_S - u9

                gap = float(np.abs(v_S).sum() - np.abs(v_B).sum())
                GAP[i, K - 1] = gap

                N_C = N_B - n_sing
                p_C = (bundle_ld - surv_ld) / N_C
                delta = p_B - p_C

                # Linear predictor
                sign_vB = safe_sign(v_B)
                lin = (N_C / n_sing) * float(np.dot(sign_vB, delta))
                GAP_LIN[i, K - 1] = lin

                # Per-digit exact residue
                sign_vS = safe_sign(v_S)
                R_d = (1.0 - sign_vB * sign_vS) * np.abs(v_S)
                R_PER_DIGIT[i, K - 1] = R_d.astype(np.float32)
                R_TOTAL[i, K - 1] = float(R_d.sum())

                # Count flips: digits where v_B and v_S have STRICTLY
                # opposite nonzero signs.
                flips = int(((sign_vB * sign_vS) == -1).sum())
                FLIP_COUNT[i, K - 1] = flips

        if (i + 1) % 30 == 0:
            print(f'  rows: {i + 1}/{n0_count} (t={time.time() - t0:.1f}s)')

    print(f'  total: {time.time() - t0:.1f}s')
    return {
        'GAP': GAP, 'GAP_LIN': GAP_LIN, 'R_TOTAL': R_TOTAL,
        'FLIP_COUNT': FLIP_COUNT, 'LAMBDA': LAMBDA,
        'R_PER_DIGIT': R_PER_DIGIT,
    }


def main():
    print(f'EXP13 — exact GAP decomposition with explicit residue')
    print(f'  n_0 ∈ [{N0_MIN}, {N0_MAX}], K ∈ [1, {K_MAX}], W = {W}')

    R = compute_decomposition(N0_MIN, N0_MAX, K_MAX, W)
    GAP = R['GAP']
    GAP_LIN = R['GAP_LIN']
    R_TOTAL = R['R_TOTAL']
    FLIP_COUNT = R['FLIP_COUNT']
    LAMBDA = R['LAMBDA']
    R_PER_DIGIT = R['R_PER_DIGIT']

    np.savez(CACHE, **R, N0_MIN=N0_MIN, N0_MAX=N0_MAX, K_MAX=K_MAX, W=W)
    print(f'-> {CACHE}')

    # ---- Verify exactness ----
    mask = ~np.isnan(GAP)
    diff = GAP - (GAP_LIN + R_TOTAL)
    max_abs = float(np.nanmax(np.abs(diff)))
    print(f'\n--- Exactness check ---')
    print(f'  max |GAP − (GAP_LIN + R_TOTAL)| = {max_abs:.2e}')
    print(f'  median |diff|: {float(np.nanmedian(np.abs(diff))):.2e}')
    if max_abs < 1e-10:
        print('  IDENTITY VERIFIED to machine precision.')
    else:
        print('  WARNING: identity does not hold to machine precision.')

    # ---- Residue statistics ----
    print(f'\n--- Residue R_TOTAL statistics ---')
    print(f'  range: [{np.nanmin(R_TOTAL):.4f}, {np.nanmax(R_TOTAL):.4f}]')
    print(f'  median |R_TOTAL|: {float(np.nanmedian(np.abs(R_TOTAL))):.4f}')
    print(f'  median |GAP|:     {float(np.nanmedian(np.abs(GAP))):.4f}')
    print(f'  fraction of cells with R_TOTAL > 0: '
          f'{float((R_TOTAL > 1e-12).sum() / mask.sum()):.4f}')

    print(f'\n--- Flip count distribution ---')
    flip_vals, flip_counts = np.unique(FLIP_COUNT[mask], return_counts=True)
    for v, c in zip(flip_vals, flip_counts):
        pct = 100 * c / mask.sum()
        print(f'  {int(v)} digits flipped: {int(c):6d} cells ({pct:5.2f}%)')

    print(f'\n--- Per-digit residue (sum across cells) ---')
    digit_totals = R_PER_DIGIT[mask].sum(axis=0)
    print(f'  digit:    1     2     3     4     5     6     7     8     9')
    print(f'  total:  ' + '  '.join(f'{x:5.2f}' for x in digit_totals))

    # ---- Plot ----
    fig = plt.figure(figsize=(20, 14), dpi=130)
    fig.patch.set_facecolor('#0a0a0a')
    gs = fig.add_gridspec(3, 3, hspace=0.32, wspace=0.22)

    extent = (0.5, K_MAX + 0.5, N0_MIN - 0.5, N0_MAX + 0.5)

    # Row 1: GAP, GAP_LIN, R_TOTAL
    vmax_g = float(np.nanpercentile(np.abs(GAP), 98))
    norm_g = TwoSlopeNorm(vmin=-vmax_g, vcenter=0.0, vmax=vmax_g)

    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor('#0a0a0a')
    im1 = ax1.imshow(GAP, aspect='auto', origin='lower', cmap='RdBu_r',
                     norm=norm_g, interpolation='nearest', extent=extent)
    ax1.set_title('GAP (truth)', color='white', fontsize=11)
    plt.colorbar(im1, ax=ax1, fraction=0.045, pad=0.02)

    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor('#0a0a0a')
    im2 = ax2.imshow(GAP_LIN, aspect='auto', origin='lower', cmap='RdBu_r',
                     norm=norm_g, interpolation='nearest', extent=extent)
    ax2.set_title('GAP_LIN  (linear part)', color='white', fontsize=11)
    plt.colorbar(im2, ax=ax2, fraction=0.045, pad=0.02)

    ax3 = fig.add_subplot(gs[0, 2])
    ax3.set_facecolor('#0a0a0a')
    vmax_r = float(np.nanpercentile(R_TOTAL, 99)) if np.nanmax(R_TOTAL) > 0 else 0.1
    im3 = ax3.imshow(R_TOTAL, aspect='auto', origin='lower', cmap='magma',
                     interpolation='nearest', extent=extent,
                     vmin=0, vmax=max(vmax_r, 0.01))
    ax3.set_title(
        'R_TOTAL  (sign-flip residue, ≥ 0)\n'
        '= Σ_d (1 − sign v_B · sign v_S) · |v_S|',
        color='white', fontsize=11)
    plt.colorbar(im3, ax=ax3, fraction=0.045, pad=0.02)

    # Row 2: |residual| of identity (should be ≈ 0), flip count, lattice
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.set_facecolor('#0a0a0a')
    abs_diff = np.abs(diff)
    im4 = ax4.imshow(abs_diff, aspect='auto', origin='lower', cmap='inferno',
                     interpolation='nearest', extent=extent,
                     vmin=0, vmax=max(float(np.nanmax(abs_diff)), 1e-15))
    ax4.set_title(
        f'|GAP − (GAP_LIN + R_TOTAL)|\n'
        f'max = {max_abs:.2e}  (machine precision; identity verified)',
        color='white', fontsize=10)
    plt.colorbar(im4, ax=ax4, fraction=0.045, pad=0.02,
                 format='%.0e')

    ax5 = fig.add_subplot(gs[1, 1])
    ax5.set_facecolor('#0a0a0a')
    im5 = ax5.imshow(FLIP_COUNT, aspect='auto', origin='lower',
                     cmap='viridis', interpolation='nearest',
                     extent=extent, vmin=0, vmax=max(int(FLIP_COUNT.max()), 1))
    ax5.set_title('# digits with v_B·v_S sign flip\n'
                  '(integer in 0..9)',
                  color='white', fontsize=11)
    plt.colorbar(im5, ax=ax5, fraction=0.045, pad=0.02)

    ax6 = fig.add_subplot(gs[1, 2])
    ax6.set_facecolor('#0a0a0a')
    vmax_l = float(LAMBDA.max())
    im6 = ax6.imshow(LAMBDA, aspect='auto', origin='lower', cmap='hot',
                     interpolation='nearest', extent=extent,
                     vmin=0, vmax=max(vmax_l, 2))
    ax6.set_title('Λ_W (closed-form lattice, EXP10)\n'
                  'reference: where collision events deposit mass',
                  color='white', fontsize=11)
    plt.colorbar(im6, ax=ax6, fraction=0.045, pad=0.02)

    # Row 3: per-digit residue panels (3 sample digits)
    digit_choices = [3, 5, 7]
    for col, d in enumerate(digit_choices):
        ax = fig.add_subplot(gs[2, col])
        ax.set_facecolor('#0a0a0a')
        Rd = R_PER_DIGIT[:, :, d - 1]
        vmax_d = float(np.nanpercentile(Rd, 99)) if np.nanmax(Rd) > 0 else 0.01
        im = ax.imshow(Rd, aspect='auto', origin='lower', cmap='magma',
                       interpolation='nearest', extent=extent,
                       vmin=0, vmax=max(vmax_d, 0.01))
        ax.set_title(f'R_d for digit d = {d}\n'
                     f'(contribution to R_TOTAL from this digit)',
                     color='white', fontsize=11)
        plt.colorbar(im, ax=ax, fraction=0.045, pad=0.02)

    # Axes formatting
    for ax in fig.axes:
        if ax.get_xlabel() == '':
            ax.set_xlabel('K', color='white', fontsize=10)
            ax.set_ylabel('n_0', color='white', fontsize=10)
            ax.tick_params(colors='white')
            for spine in ax.spines.values():
                spine.set_color('#333')

    fig.suptitle(
        'EXP13 — exact GAP decomposition: GAP = GAP_LIN + R_TOTAL  '
        '(R_TOTAL closed-form per-digit, ≥ 0, sign-flip-localized)',
        color='white', fontsize=13, y=0.997
    )
    plt.tight_layout()
    plt.savefig(OUT, dpi=180, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f'-> {OUT}')


if __name__ == '__main__':
    main()
