"""
h2_cell_fixedK.py — controlled cell-resolved experiment
=========================================================

Addresses three critiques of `h2_cell_resolved.py`:

(Q1) Cell-occupancy shift ≠ c-shift without per-cell c_D variation.
     Measure N_D(K) / K · Φ(K) per (n, D, K) and fit per-cell deficit
     exponent. If c_D varies with D, re-weighting cells by n shifts
     the dominant c. If c_D is constant in D, occupancy shift is a
     prefactor effect, not a c-shift mechanism.

(Q2) Fixed-N comparison confounds three n-dependent variables
     (residue density α_n, cofactor box √K, image size). To isolate
     the residue effect, hold K fixed and vary n. N = K · n² varies.

(Q3) Whether n=7 is a plateau or a reversal — at fixed N, K shrinks
     with n, conflating residue and K effects. Fixed-K resolves this.

This script:

1. For K ∈ {10^4, 10^5, 10^6, 10^7} and n ∈ {2, 3, 5, 7, 11, 13}:
   - Build divisor sieve of size K.
   - Enumerate distinct cofactor products c_1·c_2 with c_i ⊥ n,
     c_i ≤ √K. Bin by d(k).
2. Fixed-K analysis (Q2/Q3): at each K, compare mean d(k) and bin
   distributions across n.
3. Per-cell deficit fit (Q1): for each (n, D), regress log(N_D/K)
   on log(log K) across the K values. Slope = −c_D(n). Test if
   c_D varies with D.

Outputs:
  h2_cell_fixedK.csv           per-(n, K, D) table
  h2_cell_fixedK_summary.txt   fixed-K cross-n comparisons,
                                per-(n, D) deficit fits

Usage:
    sage -python h2_cell_fixedK.py
"""

import csv
import math
import os
import time
from collections import defaultdict
from math import gcd, log

import numpy as np


HERE = os.path.dirname(os.path.abspath(__file__))

PANEL_NS = [2, 3, 5, 7, 11, 13]
K_VALUES = [10**4, 10**5, 10**6, 10**7]
MAX_BIN_DISPLAY = 12


def divisor_sieve(K):
    d = np.zeros(K + 1, dtype=np.int32)
    for i in range(1, K + 1):
        d[i::i] += 1
    return d


def coprime_below(c_max, n):
    return [c for c in range(1, c_max + 1) if gcd(c, n) == 1]


def cell_resolved_at_K(n, K, d_sieve, verbose=False):
    """Enumerate distinct cofactor products c_1·c_2 ≤ K with c_i ⊥ n,
    c_i ≤ √K. Bin by d(k). Returns (M_n_K, bins, log_sums)."""
    c_max = math.isqrt(K)
    cs = coprime_below(c_max, n)

    if verbose:
        print(f'    n={n}, K={K}: c_max={c_max}, |coprime|={len(cs)}, '
              f'pairs={len(cs)**2}', flush=True)

    products = set()
    for i, c1 in enumerate(cs):
        for c2 in cs[i:]:
            products.add(c1 * c2)

    bins = defaultdict(int)
    log_sums = defaultdict(float)
    for k in products:
        D = int(d_sieve[k])
        bins[D] += 1
        log_sums[D] += math.log(k)

    return len(products), dict(bins), dict(log_sums)


def main():
    print('h2_cell_fixedK.py — fixed-K cell-resolved + per-cell c_D fit\n',
          flush=True)
    print(f'panel n: {PANEL_NS}', flush=True)
    print(f'K values: {K_VALUES}\n', flush=True)

    # Pre-build sieves (one per K). Largest sieve dominates time/memory.
    sieves = {}
    for K in K_VALUES:
        t0 = time.time()
        sieves[K] = divisor_sieve(K)
        print(f'  built sieve K={K} in {time.time()-t0:.2f}s '
              f'({(K+1)*4/1024/1024:.1f} MB)', flush=True)

    # Run all (n, K) cells.
    results = {}  # (n, K) -> (M, bins, log_sums)
    print('\n=== Enumerating cells ===', flush=True)
    for K in K_VALUES:
        for n in PANEL_NS:
            t0 = time.time()
            M, bins, log_sums = cell_resolved_at_K(n, K, sieves[K])
            elapsed = time.time() - t0
            results[(n, K)] = (M, bins, log_sums)
            print(f'  n={n:>2}, K={K:>10}: M={M:>9}, '
                  f'mean d(k)={sum(D*c for D, c in bins.items())/M:.3f}  '
                  f'({elapsed:.1f}s)', flush=True)

    # ---- Q2/Q3: fixed-K mean d(k) comparison ----
    summary_lines = ['Brief 4 / Phase 4 (B′) — fixed-K cell-resolved test',
                     '',
                     'Q2 fix: hold K constant across n to isolate residue effect.',
                     'Q3 fix: fixed-K removes the K-shrinkage confound.',
                     '',
                     '=== Mean d(k) on image at fixed K ===',
                     '']
    summary_lines.append(
        '  n  | ' + ' | '.join(f'K=10^{int(math.log10(K))}'.rjust(11)
                                for K in K_VALUES)
    )
    summary_lines.append(
        '  ---+' + '+'.join(['-' * 13] * len(K_VALUES))
    )
    print('\n=== Mean d(k) at fixed K ===', flush=True)
    print('  ' + ' | '.join([f'{"n":>3}'] + [f'K=10^{int(math.log10(K))}'.rjust(11)
                                              for K in K_VALUES]), flush=True)
    for n in PANEL_NS:
        parts = [f'  {n:>2} ']
        for K in K_VALUES:
            M, bins, _ = results[(n, K)]
            mean_d = sum(D * c for D, c in bins.items()) / M if M else 0
            parts.append(f'{mean_d:>11.4f}')
        line = '|'.join(parts) + '|'
        summary_lines.append(line)
        print(line, flush=True)

    # ---- Per-cell deficit fit (Q1) ----
    summary_lines.append('')
    summary_lines.append('=== Per-cell deficit fit: log(N_D/K) vs log(log K) ===')
    summary_lines.append('')
    summary_lines.append(
        '  Slope ≈ -c_D for that cell; if c_D varies with D, re-weighting')
    summary_lines.append(
        '  cells across n produces a c-shift. If c_D ≈ const in D, the')
    summary_lines.append(
        '  c-shift mechanism needs an extra ingredient.')
    summary_lines.append('')
    summary_lines.append(
        '  We require N_D(K) ≥ 30 at every K in the fit to reduce noise.')
    summary_lines.append('')

    log_log_K = [math.log(math.log(K)) for K in K_VALUES]
    summary_lines.append(
        f'  log log K values: {[f"{x:.3f}" for x in log_log_K]}'
    )
    summary_lines.append('')

    csv_rows = [(
        'n', 'K', 'D', 'N_D', 'log_N_D_over_K', 'M_n', 'frac',
    )]

    # Track per-(n, D) data for slope fit.
    per_cell = defaultdict(list)  # (n, D) -> list of (log_log_K, log(N_D/K))

    for K in K_VALUES:
        for n in PANEL_NS:
            M, bins, _ = results[(n, K)]
            for D in sorted(bins):
                N_D = bins[D]
                frac = N_D / M if M else 0
                log_ratio = math.log(N_D / K)
                csv_rows.append((n, K, D, N_D, f'{log_ratio:.6f}', M,
                                 f'{frac:.6f}'))
                per_cell[(n, D)].append((math.log(math.log(K)), log_ratio, N_D))

    # Fit slopes per (n, D).
    summary_lines.append('  Per-(n, D) deficit fits (slope = -c_D(n)):')
    summary_lines.append('')
    summary_lines.append(
        f'  {"n":>3} {"D":>4} {"# K":>4} {"slope":>10} {"intercept":>12} '
        f'{"R²":>7}'
    )
    summary_lines.append(
        '  ----+------+-----+----------+------------+-------'
    )

    fit_results = {}  # (n, D) -> (slope, intercept, r2, n_points)
    for n in PANEL_NS:
        for D in sorted(set(D for (nn, D) in per_cell if nn == n)):
            data = per_cell[(n, D)]
            # Require ≥ 3 K values with N_D ≥ 30 (reduce noise floor).
            qualifying = [(x, y) for (x, y, ND) in data if ND >= 30]
            if len(qualifying) < 3:
                continue
            xs = np.array([x for x, _ in qualifying])
            ys = np.array([y for _, y in qualifying])
            # OLS fit y = slope·x + intercept.
            slope, intercept = np.polyfit(xs, ys, 1)
            ys_pred = slope * xs + intercept
            ss_res = np.sum((ys - ys_pred) ** 2)
            ss_tot = np.sum((ys - ys.mean()) ** 2)
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float('nan')
            fit_results[(n, D)] = (float(slope), float(intercept),
                                    float(r2), len(qualifying))
            summary_lines.append(
                f'  {n:>3} {D:>4} {len(qualifying):>4} '
                f'{slope:>+10.4f} {intercept:>+12.4f} {r2:>7.4f}'
            )
        summary_lines.append('')

    # ---- Cross-D table: c_D inferred per (n, D), at-a-glance ----
    summary_lines.append('=== c_D estimates at-a-glance (= -slope) ===')
    summary_lines.append('')
    all_Ds = sorted(set(D for (n, D) in fit_results))
    truncated_Ds = [D for D in all_Ds if D <= MAX_BIN_DISPLAY]
    summary_lines.append(
        '  ' + ' '.join([f'{"n":>3}'] + [f'D={D:>2}'.rjust(8) for D in truncated_Ds])
    )
    summary_lines.append(
        '  ' + ' '.join(['-' * 3] + ['-' * 8 for _ in truncated_Ds])
    )
    for n in PANEL_NS:
        row = [f'{n:>3}']
        for D in truncated_Ds:
            if (n, D) in fit_results:
                slope, _, r2, _ = fit_results[(n, D)]
                row.append(f'{-slope:>+8.3f}')
            else:
                row.append(f'{"-":>8}')
        summary_lines.append('  ' + ' '.join(row))
    summary_lines.append('')

    # ---- Verdict ----
    summary_lines.append('=== Verdict on Q1 ===')
    summary_lines.append('')
    summary_lines.append('Compute spread of c_D across D for each n.')
    summary_lines.append('Large spread → c_D varies → bin shift CAN cause c-shift.')
    summary_lines.append('Small spread → c_D ≈ const → bin shift gives prefactor only.')
    summary_lines.append('')
    summary_lines.append(
        f'  {"n":>3} | spread (max c_D − min c_D) | range of c_D | comment'
    )
    summary_lines.append(
        '  ----+------------------------------+-----------------+------'
    )
    for n in PANEL_NS:
        Ds_with_fit = [D for D in all_Ds if (n, D) in fit_results]
        if len(Ds_with_fit) < 2:
            summary_lines.append(f'  {n:>3} | (insufficient cells fit)')
            continue
        c_Ds = [-fit_results[(n, D)][0] for D in Ds_with_fit]
        spread = max(c_Ds) - min(c_Ds)
        summary_lines.append(
            f'  {n:>3} | {spread:>+28.4f} | '
            f'[{min(c_Ds):+.3f}, {max(c_Ds):+.3f}]'
        )

    csv_path = os.path.join(HERE, 'h2_cell_fixedK.csv')
    with open(csv_path, 'w', newline='') as f:
        csv.writer(f).writerows(csv_rows)
    print(f'\nwrote {csv_path}', flush=True)

    summary_path = os.path.join(HERE, 'h2_cell_fixedK_summary.txt')
    with open(summary_path, 'w') as f:
        f.write('\n'.join(summary_lines) + '\n')
    print(f'wrote {summary_path}', flush=True)


if __name__ == '__main__':
    main()
