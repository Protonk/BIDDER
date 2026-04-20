"""
Test A of CONDITIONAL-DECAY-PLAN.md — analytic computation of the
hypothesis H's prediction for BS(1,2) mantissa Fourier coefficients.

Under H (b-steps don't move m conditional on a-count K, which is
Binomial(n, 1/2)):

    c_k^H(n) = e^{-2πi k m₀} · ((1 + cos(2π k α)) / 2)^n
    |c_k^H(n)| = cos²(π k α)^n

where α = log₁₀ 2, m₀ = log₁₀ √2.

Computes:
  - |c_k^H(n)| for a grid of k, n; identifies slow modes.
  - TV^H(n) from inverse-FFT to a fine m-grid: ∫ |ρ^H - 1| dm.
  - L²^H(n) via Parseval: sqrt(2 · Σ_{k ≥ 1} |c_k^H(n)|²).
  - Fits both to C · exp(-c · n^γ) over n ∈ [30, 3000], reports γ.

No simulation; runtime is seconds.

Run: sage -python run_conditional_a.py
"""

import math
import os
import numpy as np


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SIM_DIR, 'conditional_decay_results')
os.makedirs(OUT_DIR, exist_ok=True)

ALPHA = math.log10(2.0)
M0 = 0.5 * math.log10(2.0)  # log10(√2)

K_MAX = 500
N_GRID_M = 10000  # m-grid resolution for TV integration
N_VALUES = np.array([10, 30, 100, 300, 1000, 3000, 10000, 30000], dtype=np.int64)
# Dense n grid for shape fitting
N_DENSE = np.unique(np.concatenate([
    np.arange(10, 101, 5, dtype=np.int64),
    np.arange(100, 1001, 20, dtype=np.int64),
    np.arange(1000, 10001, 200, dtype=np.int64),
])).astype(np.int64)


def per_step_magnitude(k):
    """|c_k per step under H| = (1 + cos(2π k α))/2 = cos²(π k α)."""
    return (1.0 + math.cos(2.0 * math.pi * k * ALPHA)) / 2.0


def c_k_H(k, n):
    """Complex coefficient c_k^H(n). |value| = per_step^n."""
    mag = per_step_magnitude(k) ** n
    phase = math.cos(-2.0 * math.pi * k * M0) + 1j * math.sin(-2.0 * math.pi * k * M0)
    return phase * mag


def density_H(n, k_max, m_grid):
    """Reconstruct ρ^H(n, m) = 1 + 2 Σ_{k≥1} |c_k^H(n)| cos(2πk(m - m₀))."""
    rho = np.ones_like(m_grid)
    for k in range(1, k_max + 1):
        mag = per_step_magnitude(k) ** n
        if mag < 1e-300:
            continue
        rho += 2.0 * mag * np.cos(2.0 * math.pi * k * (m_grid - M0))
    return rho


def TV_H(n, k_max=K_MAX, n_grid=N_GRID_M):
    """TV = 0.5 ∫ |ρ - 1| dm, using half-step midpoint grid."""
    m = (np.arange(n_grid) + 0.5) / n_grid
    rho = density_H(n, k_max, m)
    return 0.5 * float(np.mean(np.abs(rho - 1.0)))


def L1_H(n, k_max=K_MAX, n_grid=N_GRID_M):
    """L¹ = ∫ |ρ - 1| dm. Comparable to histogram L₁ statistic in paper."""
    m = (np.arange(n_grid) + 0.5) / n_grid
    rho = density_H(n, k_max, m)
    return float(np.mean(np.abs(rho - 1.0)))


def L2_H(n, k_max=K_MAX):
    """L² from Parseval: sqrt(2 · Σ_{k≥1} |c_k|²)."""
    s = 0.0
    for k in range(1, k_max + 1):
        mag = per_step_magnitude(k) ** n
        if mag < 1e-300:
            continue
        s += mag ** 2
    return math.sqrt(2.0 * s)


def fit_stretched(n_arr, y_arr, n_range=(30, 3000), gammas=None):
    """Fit y = C · exp(-c · n^γ) over n in n_range. Grid-search γ."""
    if gammas is None:
        gammas = np.linspace(0.1, 1.2, 111)
    mask = (n_arr >= n_range[0]) & (n_arr <= n_range[1]) & (y_arr > 1e-300)
    n_fit = n_arr[mask].astype(float)
    y_fit = y_arr[mask]
    logy = np.log(y_fit)
    best = {'gamma': None, 'c': None, 'logC': None, 'rss': np.inf, 'r2': None}
    for g in gammas:
        x = n_fit ** g
        xb = x.mean()
        yb = logy.mean()
        den = ((x - xb) ** 2).sum()
        if den <= 0:
            continue
        slope = ((x - xb) * (logy - yb)).sum() / den
        if slope >= 0:
            continue  # want exp(-c·n^γ) so slope on logy vs n^γ should be negative
        intercept = yb - slope * xb
        pred = slope * x + intercept
        rss = ((logy - pred) ** 2).sum()
        if rss < best['rss']:
            tss = ((logy - yb) ** 2).sum()
            r2 = 1.0 - rss / tss if tss > 0 else float('nan')
            best = {'gamma': float(g), 'c': float(-slope), 'logC': float(intercept),
                    'rss': float(rss), 'r2': float(r2), 'n_fit': int(n_fit.size)}
    return best


def main():
    print('Test A (analytic): hypothesis H Fourier predictions')
    print(f'α = log₁₀ 2 = {ALPHA:.10f}')
    print(f'm₀ = log₁₀ √2 = {M0:.10f}')
    print(f'K_max = {K_MAX}, m-grid = {N_GRID_M}')
    print()

    # ---- Slow-mode hierarchy ----
    print('Slow-mode per-step magnitudes (1 + cos(2π k α))/2:')
    per_step = np.array([per_step_magnitude(k) for k in range(1, K_MAX + 1)])
    slow_order = np.argsort(per_step)[::-1]  # largest = slowest decay
    print(f'  {"k":>4s}  {"per-step":>10s}  {"rate":>10s}  {"kα mod 1":>10s}')
    for idx in slow_order[:12]:
        k = idx + 1
        ps = per_step[idx]
        rate = -math.log(max(ps, 1e-300))
        kmod = (k * ALPHA) % 1.0
        kmod_signed = min(kmod, 1.0 - kmod)
        print(f'  {k:>4d}  {ps:>10.7f}  {rate:>10.6f}  {kmod_signed:>10.7f}')

    # ---- |c_k^H(n)| at representative k, n ----
    print('\n|c_k^H(n)| at representative (k, n):')
    print(f'  {"k":>4s} |' + ''.join(f' {int(n):>10d}' for n in N_VALUES))
    for k in [1, 3, 10, 20, 50, 93, 196, 485]:
        row = [per_step_magnitude(k) ** n for n in N_VALUES]
        print(f'  {k:>4d} |' + ''.join(f' {v:>10.3e}' for v in row))

    # ---- TV and L² shape fitting ----
    print('\nComputing TV^H(n), L1^H(n), L²^H(n) on dense n grid...')
    tv = np.array([TV_H(int(n)) for n in N_DENSE])
    l1 = np.array([L1_H(int(n)) for n in N_DENSE])
    l2 = np.array([L2_H(int(n)) for n in N_DENSE])

    print('\nRepresentative values:')
    print(f'  {"n":>6s}  {"TV^H":>12s}  {"L1^H":>12s}  {"L²^H":>12s}')
    for n_val in N_VALUES:
        idx = int(np.argmin(np.abs(N_DENSE - n_val)))
        print(f'  {N_DENSE[idx]:>6d}  {tv[idx]:>12.4e}  {l1[idx]:>12.4e}  {l2[idx]:>12.4e}')

    # ---- Stretched-exp fits ----
    print('\n--- Stretched-exp fits (y ~ C exp(-c n^γ)) on n ∈ [30, 3000] ---')
    for name, y in [('TV^H', tv), ('L1^H (≈ paper φ histogram L₁)', l1),
                    ('L²^H', l2)]:
        fit = fit_stretched(N_DENSE, y)
        if fit['gamma'] is None:
            print(f'  {name}: no fit converged')
            continue
        print(f'  {name}: γ = {fit["gamma"]:.3f}  c = {fit["c"]:.4f}  '
              f'logC = {fit["logC"]:.3f}  R² = {fit["r2"]:.4f}  '
              f'n_pts = {fit["n_fit"]}')

    # ---- Compare against M1 measured c ≈ 0.498 at γ = 0.5 ----
    print('\n--- Comparison at fixed γ = 0.5 (paper fit shape) ---')
    print('Paper M1 sharp IC: c ≈ 0.498 (T1B-EVIDENCE-MAP.md)')
    for name, y in [('TV^H', tv), ('L1^H', l1), ('L²^H', l2)]:
        fit = fit_stretched(N_DENSE, y, gammas=np.array([0.5]))
        if fit['gamma'] is not None:
            print(f'  {name} at γ=0.5: c = {fit["c"]:.4f}  '
                  f'R² = {fit["r2"]:.4f}')

    # ---- Save ----
    np.savez_compressed(os.path.join(OUT_DIR, 'analytic_H.npz'),
                        n_dense=N_DENSE, tv=tv, l1=l1, l2=l2,
                        per_step=per_step,
                        alpha=ALPHA, m0=M0, k_max=np.int32(K_MAX))
    print(f"\n-> {os.path.join(OUT_DIR, 'analytic_H.npz')}")


if __name__ == '__main__':
    main()
