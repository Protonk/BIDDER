"""
S0 — Mittag-Leffler index test.

Post-processing on m1_b1_b2_results.npz (hist_return_counts at the
M1 checkpoints). No new sim required.

Two measurements at each n ∈ {100, 200, 500} (plus 150, 300 as
cross-checks):

1. Tail exponent β via log-log regression of P(N_n ≥ k) on k over
   k ∈ [⌈√n/4⌉, ⌊2√n⌋], clipped to observed support. Poisson
   parametric bootstrap gives the 95% CI.
2. Empirical Laplace transform L̂(λ) = E[exp(−λ · N_n / √n)] for
   λ ∈ {0.1, 0.5, 1, 2, 5} vs ML(1/2): E_{1/2}(−λ·c) = exp((λc)²)
   erfc(λc). Scale c fit by least squares on log L̂.

The M1 summary flagged a large zero-mass fraction (e.g. P(N=0) =
0.33 at n=500). We therefore report **both** unconditional and
conditional-on-(N ≥ 1) fits. The plan's decision rule is stated
on the unconditional fit; the conditional version is a diagnostic
for whether the mixture of "stuck-at-origin" and "excursion"
walkers biases the β̂ estimate.

Run: sage -python run_s0.py
"""

import math
import os
import numpy as np
from scipy.special import erfc
from scipy.optimize import minimize_scalar


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
M1_PATH = os.path.join(SIM_DIR, 'm1_b1_b2_results.npz')
OUT_PATH = os.path.join(SIM_DIR, 's0_results.npz')

BOOT_REPS = 2000
BOOT_SEED = 0xDEADBEEF

CHECKPOINTS_PRIMARY = [100, 200, 500]
CHECKPOINTS_ALL = [25, 50, 100, 150, 200, 300, 500]

LAMBDAS = np.array([0.1, 0.5, 1.0, 2.0, 5.0])


def ml_half_laplace(lam):
    """Mittag-Leffler (α=1/2) Laplace transform: E_{1/2}(-λ) = exp(λ²) erfc(λ)."""
    return np.exp(lam * lam) * erfc(lam)


def fit_tail_exponent(hist, N_total, conditional=False):
    """Fit log P(N ≥ k) = a − β log k over the plan's k range.
    Returns (beta, a, k_lo, k_hi, fit_k, fit_logP)."""
    h = hist.astype(np.float64).copy()
    if conditional:
        h[0] = 0.0
    N = h.sum()
    if N <= 0:
        return None
    # P(N ≥ k) via reverse cumulative
    tail = np.cumsum(h[::-1])[::-1]   # tail[k] = count at k or above
    prob_tail = tail / N

    max_nz = int(np.where(h > 0)[0][-1])
    # Use the length n implied by hist position — we pass n explicitly below.
    return prob_tail, max_nz


def regression(k_arr, logP_arr):
    """OLS log P ~ a − β log k. Returns (beta, a, R²)."""
    x = np.log(k_arr)
    y = logP_arr
    A = np.vstack([x, np.ones_like(x)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    m, b = coef
    beta = -m
    yhat = A @ coef
    ss_res = np.sum((y - yhat) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return float(beta), float(b), float(r2)


def bootstrap_beta(hist, n, N_total, rng, reps, conditional):
    """Poisson parametric bootstrap on bin counts. Returns β̂ samples."""
    sqrt_n = math.sqrt(float(n))
    k_lo_plan = int(math.ceil(sqrt_n / 4.0))
    k_hi_plan = int(math.floor(2.0 * sqrt_n))

    betas = np.empty(reps, dtype=np.float64)
    for rep in range(reps):
        # Resample each bin: Poisson around observed count (total preserved only in mean).
        resampled = rng.poisson(hist).astype(np.float64)
        if conditional:
            resampled[0] = 0.0
        N_r = resampled.sum()
        if N_r <= 0:
            betas[rep] = np.nan
            continue
        tail = np.cumsum(resampled[::-1])[::-1] / N_r
        max_nz = int(np.where(resampled > 0)[0][-1]) if (resampled > 0).any() else 0
        k_hi = min(k_hi_plan, max_nz)
        if k_hi <= k_lo_plan:
            betas[rep] = np.nan
            continue
        ks = np.arange(k_lo_plan, k_hi + 1)
        probs = tail[ks]
        good = probs > 0
        if good.sum() < 3:
            betas[rep] = np.nan
            continue
        beta, _, _ = regression(ks[good].astype(np.float64), np.log(probs[good]))
        betas[rep] = beta
    return betas


def laplace_fit(hist, n, conditional=False):
    """Empirical Laplace E[exp(-λ · N/√n)] and best-fit scale c for ML(1/2)."""
    h = hist.astype(np.float64).copy()
    if conditional:
        h[0] = 0.0
    N = h.sum()
    ks = np.arange(h.size).astype(np.float64)
    x = ks / math.sqrt(float(n))   # rescaled

    L_emp = np.array([float(np.sum(h * np.exp(-lam * x)) / N) for lam in LAMBDAS])

    # Fit c by matching ML(1/2)(λ c) on log scale.
    def loss(c):
        pred = ml_half_laplace(LAMBDAS * c)
        return float(np.sum((np.log(L_emp) - np.log(pred)) ** 2))

    # Search c ∈ (0, 5).
    res = minimize_scalar(loss, bounds=(1e-3, 5.0), method='bounded',
                          options=dict(xatol=1e-5))
    c_fit = float(res.x)
    L_pred = ml_half_laplace(LAMBDAS * c_fit)
    resid_log = np.log(L_emp) - np.log(L_pred)
    return L_emp, c_fit, L_pred, resid_log


def analyze_n(n, hist, rng, conditional=False):
    """Full S0 analysis at a single checkpoint n."""
    label = 'conditional (N≥1)' if conditional else 'unconditional'
    print(f'\n=== n = {n}  [{label}] ===')

    N_total = hist.sum()
    if conditional:
        N_eff = N_total - hist[0]
    else:
        N_eff = N_total
    print(f'  N_walkers = {int(N_total):_}  effective = {int(N_eff):_}  P(N=0) = {hist[0]/N_total:.4f}')

    h = hist.astype(np.float64).copy()
    if conditional:
        h[0] = 0.0
    tail = np.cumsum(h[::-1])[::-1] / N_eff

    # Mean of N on effective subpopulation
    ks_arr = np.arange(h.size).astype(np.float64)
    mean_N = float((ks_arr * h).sum() / max(N_eff, 1))
    print(f'  E[N_n{" | N≥1" if conditional else ""}]/√n = {mean_N / math.sqrt(n):.4f}')

    sqrt_n = math.sqrt(float(n))
    k_lo = int(math.ceil(sqrt_n / 4.0))
    max_nz = int(np.where(h > 0)[0][-1]) if (h > 0).any() else 0
    k_hi = min(int(math.floor(2.0 * sqrt_n)), max_nz)
    if k_hi <= k_lo:
        print(f'  Fit window [{k_lo}, {k_hi}] empty or inverted — skipping.')
        return None
    ks = np.arange(k_lo, k_hi + 1)
    probs = tail[ks]
    good = probs > 0
    if good.sum() < 3:
        print(f'  Fit window has too few nonzero bins.')
        return None

    beta, a, r2 = regression(ks[good].astype(np.float64), np.log(probs[good]))
    print(f'  β̂ = {beta:.3f}   intercept = {a:.3f}   R² = {r2:.4f}   '
          f'fit range k ∈ [{k_lo}, {k_hi}]  ({good.sum()} points)')

    # Bootstrap CI
    boot = bootstrap_beta(hist, n, N_total, rng, BOOT_REPS, conditional)
    boot = boot[~np.isnan(boot)]
    lo, hi = np.percentile(boot, [2.5, 97.5]) if boot.size > 10 else (np.nan, np.nan)
    print(f'  β̂ bootstrap 95% CI: [{lo:.3f}, {hi:.3f}]   (width {hi-lo:.3f}, {len(boot)}/{BOOT_REPS} valid)')

    # Laplace
    L_emp, c_fit, L_pred, resid = laplace_fit(hist, n, conditional=conditional)
    print(f'  Laplace fit c = {c_fit:.4f}')
    print(f'  λ      L̂(λ)         ML(1/2)(λc)   resid(log)')
    for lam, Le, Lp, r in zip(LAMBDAS, L_emp, L_pred, resid):
        print(f'  {lam:>4.2f}   {Le:.5f}     {Lp:.5f}     {r:+.4f}')

    return dict(n=n, conditional=conditional, beta=beta, intercept=a, r2=r2,
                k_lo=k_lo, k_hi=k_hi, boot_lo=lo, boot_hi=hi,
                L_emp=L_emp, c_fit=c_fit, L_pred=L_pred, resid=resid,
                mean_N_eff_over_sqrt_n=mean_N/math.sqrt(n),
                P_N_zero=hist[0]/N_total)


def decision(beta, lo, hi):
    """Plan's decision rule on the unconditional β̂."""
    width = hi - lo
    in_range = (0.45 <= beta <= 0.55)
    tight_95 = (lo >= 0.45 and hi <= 0.55)
    loose = (width >= 0.05)
    if tight_95 and width < 0.05:
        return 'ML(1/2) holds — proceed'
    if (hi < 0.45 or lo > 0.55) and width < 0.05:
        return 'ML(1/2) rejected — halt + reformulate'
    if loose:
        return 'CI too loose — extend data'
    return 'boundary — β̂ consistent-ish; extend data before committing'


def main():
    print('S0 — Mittag-Leffler index test')
    print(f'Source: {M1_PATH}')

    d = np.load(M1_PATH)
    hck = d['hist_checkpoints']
    hrc = d['hist_return_counts']
    N_total = int(d['meta_N'])
    print(f'N = {N_total:_}; checkpoints = {hck.tolist()}')

    rng = np.random.default_rng(BOOT_SEED)

    all_results = []
    for n_target in CHECKPOINTS_ALL:
        j = int(np.where(hck == n_target)[0][0])
        hist = hrc[j]
        for conditional in [False, True]:
            r = analyze_n(int(n_target), hist, rng, conditional=conditional)
            if r is not None:
                all_results.append(r)

    # Summary / decision on primary checkpoints
    print('\n\n=== Decision summary ===')
    print('  Plan rule operates on UNCONDITIONAL β̂.')
    for r in all_results:
        if (not r['conditional']) and (r['n'] in CHECKPOINTS_PRIMARY):
            verdict = decision(r['beta'], r['boot_lo'], r['boot_hi'])
            print(f'  n={r["n"]:4d}  β̂={r["beta"]:.3f}  CI=[{r["boot_lo"]:.3f}, {r["boot_hi"]:.3f}]  → {verdict}')

    # Save numerics
    def pack(results):
        out = {}
        for i, r in enumerate(results):
            tag = f'{"cond" if r["conditional"] else "uncond"}_n{r["n"]}'
            out[f'{tag}_beta'] = np.float64(r['beta'])
            out[f'{tag}_intercept'] = np.float64(r['intercept'])
            out[f'{tag}_r2'] = np.float64(r['r2'])
            out[f'{tag}_ci'] = np.array([r['boot_lo'], r['boot_hi']])
            out[f'{tag}_L_emp'] = r['L_emp']
            out[f'{tag}_L_pred'] = r['L_pred']
            out[f'{tag}_c_fit'] = np.float64(r['c_fit'])
            out[f'{tag}_resid'] = r['resid']
            out[f'{tag}_mean_N_eff_over_sqrt_n'] = np.float64(r['mean_N_eff_over_sqrt_n'])
            out[f'{tag}_P_N_zero'] = np.float64(r['P_N_zero'])
        return out

    np.savez_compressed(OUT_PATH, lambdas=LAMBDAS, **pack(all_results))
    print(f'\n-> {OUT_PATH}')


if __name__ == '__main__':
    main()
