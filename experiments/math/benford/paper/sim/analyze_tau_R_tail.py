"""
Analyze τ_R tail sim: compute empirical survival function, fit
polynomial and stretched-exp, compare first-excursion to pooled
subsequent-excursion distributions.

Run: sage -python analyze_tau_R_tail.py
"""

import math
import os
import numpy as np


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SIM_DIR, 'tau_R_tail_results')


def survival_from_hist(bin_edges, hist):
    """Given left-inclusive bin_edges and counts in each bin, return
    (bin_edges, S) where S[i] = P(τ > bin_edges[i]) = sum of counts
    with duration > bin_edges[i] divided by total counts."""
    total = hist.sum()
    if total == 0:
        return bin_edges, np.ones_like(bin_edges, dtype=float)
    # For each edge e, P(τ > e) = fraction of counts with duration > e.
    # If durations binned at edges as in searchsorted("right") - 1, the bin
    # with index i contains durations in [bin_edges[i], bin_edges[i+1]).
    # P(τ > bin_edges[i]) = sum of hist[j] for j s.t. bin_edges[j] > bin_edges[i]
    # ≈ sum of hist[i+1:] if we interpret bin_edges[i+1] > bin_edges[i].
    cum = np.concatenate([np.array([0]), np.cumsum(hist)])
    S = 1.0 - cum / total
    # S has length len(bin_edges) + 1 (survival at each edge + one past)
    # Align: S[i] = P(τ ≥ bin_edges[i]) approximately. Use S[:n_edges].
    return bin_edges, S[:bin_edges.size]


def fit_powerlaw(n_vals, y_vals, n_range=(50, 5000)):
    """Fit log y = a + b * log n. Return b (slope; would be ~ -0.5 for
    null-recurrent SRW tail; steeper negative means faster decay)."""
    mask = (n_vals >= n_range[0]) & (n_vals <= n_range[1]) & (y_vals > 0)
    if mask.sum() < 3:
        return None
    x = np.log(n_vals[mask].astype(float))
    y = np.log(y_vals[mask])
    xb = x.mean()
    yb = y.mean()
    den = ((x - xb) ** 2).sum()
    if den <= 0:
        return None
    slope = ((x - xb) * (y - yb)).sum() / den
    intercept = yb - slope * xb
    pred = slope * x + intercept
    rss = ((y - pred) ** 2).sum()
    tss = ((y - yb) ** 2).sum()
    r2 = 1.0 - rss / tss if tss > 0 else float('nan')
    return {'slope': float(slope), 'intercept': float(intercept),
            'r2': float(r2), 'n_points': int(mask.sum())}


def main():
    path = os.path.join(OUT_DIR, 'tau_R_tail.npz')
    d = np.load(path, allow_pickle=True)
    bin_edges = d['bin_edges']
    dur_hist_all = d['dur_hist_all']
    dur_hist_post = d['dur_hist_post_first']
    first_exit = d['first_exit_t']
    first_return = d['first_return_t']
    censored_durs = d['censored_durs']
    N = int(d['meta_N'])
    n_max = int(d['meta_n_max'])
    E0 = int(d['meta_E0'])

    print(f'τ_R tail analysis')
    print(f'  N = {N:_}, n_max = {n_max}, E₀ = {E0}')

    total_all = int(dur_hist_all.sum())
    total_post = int(dur_hist_post.sum())
    n_censored = int(censored_durs.size)
    print(f'  Completed excursions (all): {total_all:_}')
    print(f'  Completed excursions (post-first per walker): {total_post:_}')
    print(f'  Ongoing (censored) excursions at n_max: {n_censored:_}')
    print()

    # --- First-excursion distribution ---
    print('=== First-excursion τ_R distribution (IC-specific) ===')
    first_complete = (first_exit != -1) & (first_return != -1)
    first_incomplete = (first_exit != -1) & (first_return == -1)
    never_exited = (first_exit == -1)
    print(f'  walkers with first exit and first return: '
          f'{first_complete.sum():_} ({first_complete.mean():.3%})')
    print(f'  walkers with first exit, no first return by n_max: '
          f'{first_incomplete.sum():_} ({first_incomplete.mean():.3%})')
    print(f'  walkers that never exited: '
          f'{never_exited.sum():_} ({never_exited.mean():.3%})')
    if first_complete.sum() > 0:
        durs_first = (first_return[first_complete] -
                      first_exit[first_complete]).astype(np.int64)
        print(f'  first-excursion durations: '
              f'min/median/mean/max = {durs_first.min()} / '
              f'{int(np.median(durs_first))} / {durs_first.mean():.1f} / '
              f'{durs_first.max()}')

    # Empirical survival S(n) = P(τ_R first > n | first exit occurred)
    # Use all walkers that had a first exit; those without return give τ > n_max.
    has_first_exit = ~never_exited
    if has_first_exit.sum() > 0:
        print('\n  Empirical survival S(n) for first-excursion τ_R '
              '(condition: had first exit):')
        # For each n in a log-spaced grid, P(first τ_R > n | had first exit)
        grid = np.unique(np.round(np.logspace(0, math.log10(n_max),
                                              30)).astype(np.int64))
        surv = []
        for ng in grid:
            # τ_R > ng means: (first_return - first_exit > ng) OR first_return == -1
            # (both conditional on first_exit != -1).
            fe = first_exit[has_first_exit]
            fr = first_return[has_first_exit]
            greater = (fr == -1) | ((fr - fe) > ng)
            surv.append(float(greater.mean()))
        surv = np.array(surv)
        for ng, s in zip(grid, surv):
            print(f'    n = {int(ng):>6d}:  S(n) = {s:.5e}')

        fit = fit_powerlaw(grid, surv, n_range=(50, 10000))
        if fit:
            print(f'\n  Power-law fit on n ∈ [50, 10000]: '
                  f'slope = {fit["slope"]:.3f}  R² = {fit["r2"]:.4f}  '
                  f'({fit["n_points"]} points)')
            print(f'    (SRW reference slope for P(τ > n): -0.5)')

    # --- Pooled-excursion distribution (from histograms) ---
    print('\n=== All-excursions pooled τ_R survival ===')
    if total_all > 0:
        # Compute survival on the log bin grid
        edges, S = survival_from_hist(bin_edges, dur_hist_all)
        # Print a spaced-out subset
        grid = np.unique(np.round(np.logspace(0, math.log10(n_max),
                                              30)).astype(np.int64))
        print(f'  {"n":>6s}  {"S_all(n)":>12s}  {"S_post(n)":>12s}')
        edges_post, S_post = survival_from_hist(bin_edges, dur_hist_post)
        for ng in grid:
            idx = int(np.searchsorted(bin_edges, ng, side='right') - 1)
            idx = min(max(idx, 0), bin_edges.size - 1)
            print(f'  {int(ng):>6d}  {S[idx]:>12.5e}  '
                  f'{S_post[idx]:>12.5e}')
        # Power-law fit on the pooled survival
        surv_grid = np.array([S[min(max(int(np.searchsorted(bin_edges, ng,
                                                              side='right') - 1),
                                       0), bin_edges.size - 1)]
                              for ng in grid])
        fit_all = fit_powerlaw(grid, surv_grid, n_range=(50, 10000))
        if fit_all:
            print(f'\n  Pooled-all survival power-law fit, n ∈ [50, 10000]: '
                  f'slope = {fit_all["slope"]:.3f}  R² = {fit_all["r2"]:.4f}')

    # --- Tail mass / never-returners ---
    print('\n=== Censored (ongoing) excursions at n_max ===')
    if n_censored > 0:
        print(f'  count = {n_censored:_} '
              f'({n_censored / N:.3%} of walkers)')
        cd = censored_durs
        print(f'  ongoing durations: min/median/mean/max = '
              f'{cd.min()} / {int(np.median(cd))} / {cd.mean():.1f} / '
              f'{cd.max()}')


if __name__ == '__main__':
    main()
