"""
exp12_gap_predictor.py — closed-form predictor for GAP.

EXP11 found corr(GAP, signed Benford excess of culled) = -0.40, a
moderate correlation that gives the SIGN of the gap but not its
magnitude. Here we derive the LINEAR predictor from first principles
and check how tight it gets.

Setup: at each (K, n_0) cell, with N_B = W·K, N_S = #singletons,
N_C = N_B − N_S, and 9-vectors p_B, p_S, p_C (leading-digit dists),

    p_S = (N_B p_B − N_C p_C) / N_S = p_B + (N_C/N_S) (p_B − p_C).

So with v_B = p_B − u, v_S = p_S − u, δ = p_B − p_C,

    v_S = v_B + (N_C/N_S) δ.

L1 norm: |x + ε|₁ ≈ |x|₁ + ⟨sign(x), ε⟩ for small ε (no sign flips).
This gives the LINEAR PREDICTOR

    GAP_lin := (N_C / N_S) · ⟨sign(v_B), δ⟩
            = (N_C / N_S) · Σ_d sign(p_B[d] − 1/9) · (p_B[d] − p_C[d]).

We also try:
- GAP_exact_dot := ⟨sign(v_B), v_S − v_B⟩ (= GAP_lin; sanity check)
- GAP_2 := exact L1 difference rebuilt from p_B, p_C, N_C, N_S
           (should match GAP up to numerical precision; full circle)
- GAP_be := signed Benford excess of culled atoms (EXP11's predictor)
- GAP_lvb := |v_B|₁ alone

Compute on the EXP11 cache and report correlations + scatter plots.

Output:
    exp12_gap_predictor.png
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
OUT = os.path.join(HERE, 'exp12_gap_predictor.png')

W = 10
N0_MIN, N0_MAX = 10, 300
K_MAX = 300


def n_primes_vec(n: int, k: int) -> np.ndarray:
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


def leading_digit(n: int) -> int:
    while n >= 10:
        n //= 10
    return n


def compute_predictors(n0_min, n0_max, k_max, w):
    """For each (K, n_0) cell, compute GAP plus all predictors and
    the relevant per-cell 9-vectors."""

    n0_count = n0_max - n0_min + 1

    GAP = np.full((n0_count, k_max), np.nan)
    GAP_LIN = np.full((n0_count, k_max), np.nan)
    GAP_BE = np.full((n0_count, k_max), np.nan)
    GAP_LVB = np.full((n0_count, k_max), np.nan)
    GAP_RECON = np.full((n0_count, k_max), np.nan)
    NC_OVER_NS = np.full((n0_count, k_max), np.nan)
    LVB = np.full((n0_count, k_max), np.nan)

    u9 = np.full(9, 1.0 / 9)

    t0 = time.time()
    for i, n0 in enumerate(range(n0_min, n0_max + 1)):
        streams = [n_primes_vec(n, k_max) for n in range(n0, n0 + w)]
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
            if N_B > 0 and n_sing > 0 and n_sing < N_B:
                p_B = bundle_ld / N_B
                p_S = surv_ld / n_sing
                v_B = p_B - u9
                v_S = p_S - u9
                lvb = float(np.abs(v_B).sum())
                lvs = float(np.abs(v_S).sum())
                gap = lvs - lvb
                GAP[i, K - 1] = gap
                LVB[i, K - 1] = lvb

                N_C = N_B - n_sing
                p_C = (bundle_ld - surv_ld) / N_C
                delta = p_B - p_C
                NC_OVER_NS[i, K - 1] = N_C / n_sing

                # Linear predictor: ⟨sign(v_B), (N_C/N_S) δ⟩
                sign_vB = np.sign(v_B)
                gap_lin = (N_C / n_sing) * float(np.dot(sign_vB, delta))
                GAP_LIN[i, K - 1] = gap_lin

                # Reconstruction using p_C: should match GAP exactly
                v_S_recon = v_B + (N_C / n_sing) * delta
                gap_recon = float(np.abs(v_S_recon).sum()) - lvb
                GAP_RECON[i, K - 1] = gap_recon

                # Benford excess of culled atoms (EXP11's predictor)
                be = (p_C[0] + p_C[1] + p_C[2]
                      - p_C[6] - p_C[7] - p_C[8])
                GAP_BE[i, K - 1] = be
                GAP_LVB[i, K - 1] = lvb

        if (i + 1) % 30 == 0:
            print(f'  rows: {i + 1}/{n0_count} (t={time.time() - t0:.1f}s)')

    print(f'  total: {time.time() - t0:.1f}s')
    return {
        'GAP': GAP,
        'GAP_LIN': GAP_LIN,
        'GAP_BE': GAP_BE,
        'GAP_LVB': GAP_LVB,
        'GAP_RECON': GAP_RECON,
        'NC_OVER_NS': NC_OVER_NS,
        'LVB': LVB,
    }


def main():
    print(f'EXP12 — closed-form GAP predictor at unit resolution')
    print(f'  n_0 ∈ [{N0_MIN}, {N0_MAX}], K ∈ [1, {K_MAX}], W = {W}')

    R = compute_predictors(N0_MIN, N0_MAX, K_MAX, W)
    GAP = R['GAP']
    GAP_LIN = R['GAP_LIN']
    GAP_BE = R['GAP_BE']
    GAP_LVB = R['GAP_LVB']
    GAP_RECON = R['GAP_RECON']

    # --- Correlation table ---
    mask = ~np.isnan(GAP)
    print(f'\nCorrelations (n = {mask.sum()} valid cells):')

    def corr(x, y, mask):
        m = mask & ~np.isnan(x) & ~np.isnan(y)
        if m.sum() < 2:
            return float('nan')
        return float(np.corrcoef(x[m], y[m])[0, 1])

    rows = [
        ('Benford excess of culled (EXP11)', 'GAP_BE'),
        ('|v_B|₁ alone', 'GAP_LVB'),
        ('linear: (N_C/N_S)⟨sign(v_B), δ⟩', 'GAP_LIN'),
        ('recon: |v_B + (N_C/N_S)δ|₁ − |v_B|₁ (sanity)', 'GAP_RECON'),
    ]
    for desc, key in rows:
        c = corr(GAP, R[key], mask)
        print(f'  corr(GAP, {desc:<48}) = {c:+.4f}')

    # Multivariate: best linear combo of (BE, LVB)
    m = mask & ~np.isnan(GAP_BE) & ~np.isnan(GAP_LVB)
    X = np.column_stack([GAP_BE[m], GAP_LVB[m]])
    y = GAP[m]
    # Least squares fit GAP ≈ a·BE + b·LVB + c
    A = np.column_stack([X, np.ones(X.shape[0])])
    coefs, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coefs
    r2 = 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    print(f'\nLinear regression GAP ≈ {coefs[0]:+.3f}·BE + '
          f'{coefs[1]:+.3f}·|v_B|₁ + {coefs[2]:+.4f}')
    print(f'  R² = {r2:.4f}')

    # --- Plot: scatter for each predictor + heatmap of residuals ---
    fig = plt.figure(figsize=(20, 12), dpi=130)
    fig.patch.set_facecolor('#0a0a0a')
    gs = fig.add_gridspec(2, 3, hspace=0.32, wspace=0.25)

    # Scatter helpers
    def scatter_panel(ax, x, y, title, xlabel='predictor'):
        ax.set_facecolor('#0a0a0a')
        m = mask & ~np.isnan(x) & ~np.isnan(y)
        ax.scatter(x[m], y[m], s=1.5, alpha=0.18, color='#88ccff')
        c = float(np.corrcoef(x[m], y[m])[0, 1])
        # Diagonal y = x for the linear/recon predictors
        if 'linear' in title.lower() or 'recon' in title.lower():
            xs = np.linspace(x[m].min(), x[m].max(), 100)
            ax.plot(xs, xs, color='#ff66aa', linewidth=0.8, alpha=0.6,
                    linestyle='--', label='y = x')
        ax.axhline(0, color='#444', linewidth=0.6, alpha=0.7)
        ax.axvline(0, color='#444', linewidth=0.6, alpha=0.7)
        ax.set_title(f'{title}\n(corr = {c:+.4f})',
                     color='white', fontsize=11)
        ax.set_xlabel(xlabel, color='white', fontsize=10)
        ax.set_ylabel('GAP', color='white', fontsize=10)
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#333')
        if 'linear' in title.lower() or 'recon' in title.lower():
            ax.legend(loc='upper left', fontsize=8, framealpha=0.5,
                      labelcolor='white', facecolor='#1a1a1a')

    ax1 = fig.add_subplot(gs[0, 0])
    scatter_panel(ax1, GAP_BE, GAP, 'GAP vs Benford excess (EXP11)',
                  xlabel='BE = p_C[1-3] − p_C[7-9]')

    ax2 = fig.add_subplot(gs[0, 1])
    scatter_panel(ax2, GAP_LVB, GAP, 'GAP vs |v_B|₁',
                  xlabel='|v_B|₁')

    ax3 = fig.add_subplot(gs[0, 2])
    scatter_panel(ax3, GAP_LIN, GAP,
                  'GAP vs linear predictor: '
                  '(N_C/N_S)⟨sign v_B, δ⟩',
                  xlabel='GAP_LIN')

    # Bottom row: residuals
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.set_facecolor('#0a0a0a')
    extent = (0.5, K_MAX + 0.5, N0_MIN - 0.5, N0_MAX + 0.5)
    vmax_g = float(np.nanpercentile(np.abs(GAP), 98))
    norm_g = TwoSlopeNorm(vmin=-vmax_g, vcenter=0.0, vmax=vmax_g)
    im4 = ax4.imshow(GAP, aspect='auto', origin='lower', cmap='RdBu_r',
                     norm=norm_g, interpolation='nearest', extent=extent)
    ax4.set_title('GAP (truth)', color='white', fontsize=11)
    plt.colorbar(im4, ax=ax4, fraction=0.045, pad=0.02)

    ax5 = fig.add_subplot(gs[1, 1])
    ax5.set_facecolor('#0a0a0a')
    im5 = ax5.imshow(GAP_LIN, aspect='auto', origin='lower', cmap='RdBu_r',
                     norm=norm_g, interpolation='nearest', extent=extent)
    ax5.set_title('GAP_LIN (linear predictor)',
                  color='white', fontsize=11)
    plt.colorbar(im5, ax=ax5, fraction=0.045, pad=0.02)

    ax6 = fig.add_subplot(gs[1, 2])
    ax6.set_facecolor('#0a0a0a')
    residual = GAP - GAP_LIN
    vmax_r = float(np.nanpercentile(np.abs(residual), 98))
    norm_r = TwoSlopeNorm(vmin=-vmax_r, vcenter=0.0, vmax=vmax_r)
    im6 = ax6.imshow(residual, aspect='auto', origin='lower',
                     cmap='RdBu_r', norm=norm_r, interpolation='nearest',
                     extent=extent)
    ax6.set_title(f'Residual: GAP − GAP_LIN  '
                  f'(scale ≈ ±{vmax_r:.3f})',
                  color='white', fontsize=11)
    plt.colorbar(im6, ax=ax6, fraction=0.045, pad=0.02)

    for ax in [ax4, ax5, ax6]:
        ax.set_xlabel('K', color='white', fontsize=10)
        ax.set_ylabel('n_0', color='white', fontsize=10)
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#333')

    fig.suptitle(
        'EXP12 — closed-form linear predictor for GAP from (p_B, p_C, N_C, N_S)',
        color='white', fontsize=13, y=0.995
    )
    plt.tight_layout()
    plt.savefig(OUT, dpi=180, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f'-> {OUT}')


if __name__ == '__main__':
    main()
