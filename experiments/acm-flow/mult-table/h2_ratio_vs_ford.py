"""
h2_ratio_vs_ford.py — disambiguator: M_n(K) / M_Ford(K) vs α_n²
=================================================================

Per the cross-thread agent's recommendation: before proposing any
analytic question, run a control that disambiguates which question
is live.

The disambiguator. BRIEF4-h2's prediction is

    M_n(K) ~ ((n−1)/n)² · K · κ_F · (log K)^{−c} · (log log K)^{−3/2}
    M_Ford(K) ~                 K · κ_F · (log K)^{−c} · (log log K)^{−3/2}

So the ratio cancels Ford's universal Φ(K) exactly:

    M_n(K) / M_Ford(K)  →  α_n² = ((n−1)/n)²    (uniformly in K)

Three diagnostic outcomes per the agent:

  Outcome 1 — ratio settles at α_n² across the K panel.
              → BRIEF4-h2 prediction holds; the apparent c-shift in
                M_n · Φ(N) / N is finite-N correction in Φ itself
                (also present in unrestricted Ford). Next: (γ) with
                finite-N Φ correction as analytic target.

  Outcome 2 — ratio drifts upward toward α_n.
              → Anatomy invariance fails for coprime-to-n; the
                conditional balance probability P(m balanced | m ⊥ n)
                differs from 1/Φ(K). Next: (α′) targeting that
                conditional probability.

  Outcome 3 — ratio drifts in some other n-dependent way.
              → Reframe; possibly Meisner-style residue-class
                deficit shift.

Cost: one extra unrestricted Ford enumeration per K. Very cheap
(bytearray-based).

Also computes the Q-weighted sum S_n(N) = Σ_{m ∈ M_n^{(2)}(N)}
Q_n(m) · log(m) on the same enumeration. This is the Q_n-explicit
observable the agent flagged earlier; it weights the count by Q_n's
sign at h=2, exposing rank-2 finite-rank structure that the bare
count and the cell-binning don't.

Outputs:
  h2_ratio_vs_ford.csv         per-(n, K) ratios and S_n
  h2_ratio_vs_ford_summary.txt diagnostic tables and verdict

Usage:
    sage -python h2_ratio_vs_ford.py
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


def divisor_sieve(K):
    d = np.zeros(K + 1, dtype=np.int32)
    for i in range(1, K + 1):
        d[i::i] += 1
    return d


def M_Ford(K, verbose=False):
    """Unrestricted Ford balanced-product count:
    |{k ≤ K : k = c_1·c_2, 1 ≤ c_1 ≤ c_2 ≤ √K}|.
    Bytearray-based for memory efficiency."""
    c_max = math.isqrt(K)
    seen = bytearray(K + 1)
    for c1 in range(1, c_max + 1):
        for c2 in range(c1, c_max + 1):
            seen[c1 * c2] = 1
    return seen.count(1)


def M_n_and_bins(n, K, d_sieve):
    """Coprime-to-n distinct products + bin counts for S_n.
    Returns (M_n, S_n, bins)."""
    c_max = math.isqrt(K)
    cs = [c for c in range(1, c_max + 1) if gcd(c, n) == 1]
    products = set()
    for i, c1 in enumerate(cs):
        for c2 in cs[i:]:
            products.add(c1 * c2)
    bins = defaultdict(int)
    log_sums = defaultdict(float)
    log_n2 = 2 * math.log(n)
    for k in products:
        D = int(d_sieve[k])
        bins[D] += 1
        log_sums[D] += log_n2 + math.log(k)
    S_n = sum((1 - D / 2) * log_sums[D] for D in log_sums)
    return len(products), S_n, dict(bins)


def main():
    print('h2_ratio_vs_ford.py — disambiguator M_n(K) / M_Ford(K) vs α_n²\n',
          flush=True)
    print(f'panel n: {PANEL_NS}', flush=True)
    print(f'K values: {K_VALUES}\n', flush=True)

    # ---- 1. Unrestricted Ford counts ----
    print('=== Unrestricted Ford M_Ford(K) ===', flush=True)
    M_Ford_results = {}
    for K in K_VALUES:
        t0 = time.time()
        M = M_Ford(K)
        elapsed = time.time() - t0
        M_Ford_results[K] = M
        print(f'  K = {K:>10}: M_Ford = {M:>10}  ({elapsed:.2f}s)', flush=True)

    # ---- 2. Sieves for d(k) ----
    print('\n=== Building divisor sieves ===', flush=True)
    sieves = {}
    for K in K_VALUES:
        t0 = time.time()
        sieves[K] = divisor_sieve(K)
        print(f'  K = {K:>10}: sieve built in {time.time()-t0:.2f}s', flush=True)

    # ---- 3. Coprime-to-n counts and S_n ----
    print('\n=== Coprime-to-n M_n(K) and S_n(N=K·n²) ===', flush=True)
    M_n_results = {}
    S_n_results = {}
    for K in K_VALUES:
        for n in PANEL_NS:
            t0 = time.time()
            M, S_n, _ = M_n_and_bins(n, K, sieves[K])
            elapsed = time.time() - t0
            M_n_results[(n, K)] = M
            S_n_results[(n, K)] = S_n
            print(f'  n={n:>2}, K={K:>10}: M_n = {M:>9}, '
                  f'S_n = {S_n:>+15.4f}  ({elapsed:.1f}s)', flush=True)

    # ---- 4. Ratio test ----
    print('\n=== Ratio M_n(K) / M_Ford(K) vs predicted α_n² ===', flush=True)
    K_labels = [f'K=10^{int(math.log10(K))}' for K in K_VALUES]

    summary_lines = [
        'Brief 4 / Phase 4 (B″) — ratio test M_n(K) / M_Ford(K)',
        '',
        'Disambiguator: BRIEF4-h2 predicts M_n(K) / M_Ford(K) → α_n² = ((n-1)/n)²',
        'uniformly in K. The ratio cancels Ford\'s Φ(K) exactly.',
        '',
        '  Outcome 1 (ratio settles at α_n²):  drift in M_n · Φ(N)/N is finite-N',
        '                                       correction in Φ; (γ) is the path.',
        '  Outcome 2 (ratio drifts toward α_n): anatomy invariance fails;',
        '                                       (α′) targets P(balanced | k⊥n).',
        '  Outcome 3 (other shape):             reframe; possibly Meisner-style',
        '                                       residue-class deficit shift.',
        '',
        '=== Predicted: α_n² = ((n-1)/n)² ===',
        '',
    ]
    pred_table = '  ' + '  '.join([f'{"n":>3}', f'{"α_n²":>11}', f'{"α_n":>11}'])
    summary_lines.append(pred_table)
    summary_lines.append('  ' + '  '.join(['---'.rjust(3)] + ['-' * 11] * 2))
    for n in PANEL_NS:
        alpha = (n - 1) / n
        a2 = alpha ** 2
        summary_lines.append(f'  {n:>3}  {a2:>11.6f}  {alpha:>11.6f}')

    summary_lines.append('')
    summary_lines.append('=== Empirical M_n(K) / M_Ford(K) ===')
    summary_lines.append('')
    header = '  ' + '  '.join([f'{"n":>3}'] + [f'{label:>11}' for label in K_labels])
    summary_lines.append(header)
    summary_lines.append('  ' + '  '.join(['---'.rjust(3)] + ['-' * 11] * len(K_VALUES)))
    print('  ' + '  '.join([f'{"n":>3}', f'{"α_n²":>11}']
                            + [f'{label:>11}' for label in K_labels]), flush=True)
    print('  ' + '  '.join(['---'.rjust(3), '-' * 11] + ['-' * 11] * len(K_VALUES)),
          flush=True)
    for n in PANEL_NS:
        a2 = ((n - 1) / n) ** 2
        ratios = []
        for K in K_VALUES:
            r = M_n_results[(n, K)] / M_Ford_results[K]
            ratios.append(r)
        row = f'  {n:>3}  ' + '  '.join(f'{r:>11.6f}' for r in ratios)
        summary_lines.append(row)
        full_row = (f'  {n:>3}  {a2:>11.6f}'
                    + '  '.join([''] + [f'{r:>11.6f}' for r in ratios]))
        print(full_row, flush=True)

    # ---- 5. Verdict per (n, K) ----
    summary_lines.append('')
    summary_lines.append('=== Verdict at K = 10^7 ===')
    summary_lines.append('')
    summary_lines.append('  ratio compared to predictions α_n² and α_n')
    summary_lines.append('  closer to α_n² → outcome 1; closer to α_n → outcome 2')
    summary_lines.append('')
    summary_lines.append(
        f'  {"n":>3} | {"α_n²":>11} | {"α_n":>11} | {"ratio":>11} | '
        f'{"diff α_n²":>11} | {"diff α_n":>11} | reading'
    )
    summary_lines.append(
        '  ----+-------------+-------------+-------------+-------------+-------------+--------'
    )
    print('\n=== Verdict at K = 10^7 ===', flush=True)
    print(f'  {"n":>3} | {"α_n²":>11} | {"α_n":>11} | {"ratio":>11} | '
          f'{"diff α_n²":>11} | {"diff α_n":>11} | reading', flush=True)
    for n in PANEL_NS:
        alpha = (n - 1) / n
        a2 = alpha ** 2
        ratio = M_n_results[(n, 10**7)] / M_Ford_results[10**7]
        diff_a2 = ratio - a2
        diff_a = ratio - alpha
        if abs(diff_a2) < abs(diff_a):
            verdict = 'closer to α_n² (outcome 1)'
        else:
            verdict = 'closer to α_n (outcome 2)'
        line = (f'  {n:>3} | {a2:>11.6f} | {alpha:>11.6f} | {ratio:>11.6f} | '
                f'{diff_a2:>+11.6f} | {diff_a:>+11.6f} | {verdict}')
        print(line, flush=True)
        summary_lines.append(line)

    # ---- 6. Drift across K (does ratio converge?) ----
    summary_lines.append('')
    summary_lines.append('=== Drift of ratio across K ===')
    summary_lines.append('')
    summary_lines.append('  ratio change per decade of K, log scale')
    summary_lines.append('  small change → converging; large change → still drifting')
    summary_lines.append('')
    summary_lines.append(
        f'  {"n":>3} | ' + ' | '.join(f'{label:>13}' for label in K_labels)
        + ' | per-decade drift'
    )
    summary_lines.append(
        '  ----+' + '+'.join(['-' * 15] * len(K_VALUES))
        + '+------------'
    )
    for n in PANEL_NS:
        a2 = ((n - 1) / n) ** 2
        ratios = [M_n_results[(n, K)] / M_Ford_results[K] for K in K_VALUES]
        # Drift per decade: change of log ratio per log K
        drifts = []
        for i in range(1, len(ratios)):
            d_log_r = math.log(ratios[i] / ratios[i - 1])
            d_log_K = math.log(K_VALUES[i] / K_VALUES[i - 1])  # = log(10)
            drift_per_decade = d_log_r / (d_log_K / math.log(10))
            drifts.append(drift_per_decade)
        ratio_str = ' | '.join(f'{r:>13.6f}' for r in ratios)
        drift_summary = ' / '.join(f'{d:>+5.4f}' for d in drifts)
        summary_lines.append(f'  {n:>3} | {ratio_str} | {drift_summary}')

    # ---- 7. S_n table ----
    summary_lines.append('')
    summary_lines.append('=== Q-weighted sum S_n(N) per (n, K), N = K·n² ===')
    summary_lines.append('')
    summary_lines.append('  S_n(N) = Σ_{m ∈ M_n^(2)(N)} Q_n(m) · log(m)')
    summary_lines.append('         = Σ_D (1 − D/2) · log_sum(D)')
    summary_lines.append('')
    summary_lines.append(
        f'  {"n":>3} | ' + ' | '.join(f'{label:>15}' for label in K_labels)
    )
    summary_lines.append(
        '  ----+' + '+'.join(['-' * 17] * len(K_VALUES))
    )
    for n in PANEL_NS:
        parts = [f'  {n:>3}']
        for K in K_VALUES:
            parts.append(f'{S_n_results[(n, K)]:>15.4f}')
        summary_lines.append(' | '.join(parts) + ' |')

    # S_n / N normalization (where N = K·n²)
    summary_lines.append('')
    summary_lines.append('=== S_n(N) / N normalized per (n, K) ===')
    summary_lines.append('')
    summary_lines.append('  Stable asymptote in N → rank-2 finite-rank test passes.')
    summary_lines.append('')
    summary_lines.append(
        f'  {"n":>3} | ' + ' | '.join(f'{label:>13}' for label in K_labels)
    )
    summary_lines.append(
        '  ----+' + '+'.join(['-' * 15] * len(K_VALUES))
    )
    for n in PANEL_NS:
        parts = [f'  {n:>3}']
        for K in K_VALUES:
            N = K * n * n
            S_over_N = S_n_results[(n, K)] / N
            parts.append(f'{S_over_N:>13.6f}')
        summary_lines.append(' | '.join(parts) + ' |')

    # ---- Output ----
    csv_path = os.path.join(HERE, 'h2_ratio_vs_ford.csv')
    csv_rows = [(
        'n', 'K', 'M_Ford', 'M_n', 'ratio', 'alpha_n2', 'alpha_n',
        'diff_from_alpha_n2', 'diff_from_alpha_n',
        'S_n', 'N_eq_K_times_n2', 'S_n_over_N',
    )]
    for K in K_VALUES:
        for n in PANEL_NS:
            alpha = (n - 1) / n
            a2 = alpha ** 2
            ratio = M_n_results[(n, K)] / M_Ford_results[K]
            S_n = S_n_results[(n, K)]
            N = K * n * n
            csv_rows.append((
                n, K, M_Ford_results[K], M_n_results[(n, K)],
                f'{ratio:.6f}', f'{a2:.6f}', f'{alpha:.6f}',
                f'{ratio - a2:+.6f}', f'{ratio - alpha:+.6f}',
                f'{S_n:.6f}', N, f'{S_n / N:.6f}',
            ))
    with open(csv_path, 'w', newline='') as f:
        csv.writer(f).writerows(csv_rows)
    print(f'\nwrote {csv_path}', flush=True)

    summary_path = os.path.join(HERE, 'h2_ratio_vs_ford_summary.txt')
    with open(summary_path, 'w') as f:
        f.write('\n'.join(summary_lines) + '\n')
    print(f'wrote {summary_path}', flush=True)


if __name__ == '__main__':
    main()
