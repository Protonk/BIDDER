"""
h2_cell_resolved.py — cell-resolved h=2 multiplication-table predictor
=======================================================================

The (B) move per H2-RESULT-N1E8.md and the cross-thread critique:
the bare count M_n(N) washes Q_n into Ford's universal κ_F. To
exercise Q_n's value at h=2 explicitly, we decompose M_n(N) by
`d(k) = d(m/n²)`, the payload divisor count. At each cell:

    Q_n(n²k) = 1 − d(k)/2

is a universal identity (Q-FORMULAS.md). So binning distinct products
by `d(k)` gives a partition of M_n(N) on which Q_n's local algebra
acts.

This script:

1. Enumerates distinct products at h=2 for prime n in the panel.
2. Builds a divisor sieve `d_sieve[k] = d(k)` for k ≤ N/n².
3. Bins distinct products by `d(k)` and records bin count + log-sum.
4. Computes the Λ_n-weighted sum

       S_n(N) := Σ_{m ∈ M_n^{(2)}(N)} Q_n(m) · log(m)
              = Σ_D (1 − D/2) · L_n(D, N)

   where L_n(D, N) = Σ_{m ∈ bin D} log(m).

5. Computes per-bin relative frequencies f_n(D, N) = bin/M_n(N) and
   compares across n. If the c-shift from N=10^8 enumeration is
   driven by the d-distribution shift on coprime-to-n integers, we
   should see bin distributions that differ predictably with n —
   specifically, coprime-to-n biases bin distribution because
   restricting prime support changes the d distribution.

Output:
  h2_cell_resolved.csv         per-(n, N, D) table
  h2_cell_resolved_summary.txt human-readable per-(n, N) bin tables
                                and Q-weighted sums

Usage:
    python3 h2_cell_resolved.py
"""

import csv
import math
import os
import time
from math import gcd, log

import numpy as np


HERE = os.path.dirname(os.path.abspath(__file__))

PANEL_NS = [2, 3, 5, 7]  # primes for clean rank-2 only structure
ENUMERATION_NS = [10**5, 10**6, 10**7]
MAX_BIN_DISPLAY = 12  # d(k) values up to this; rest aggregated


# ---- divisor sieve ----

def divisor_sieve(K):
    """d_sieve[k] = d(k) for k ∈ [0, K]. Numpy-vectorized inner loop."""
    d = np.zeros(K + 1, dtype=np.int32)
    for i in range(1, K + 1):
        d[i::i] += 1
    return d


# ---- cell-resolved enumeration ----

def coprime_below(c_max, n):
    return [c for c in range(1, c_max + 1) if gcd(c, n) == 1]


def cell_resolved(n, N, verbose=True):
    """Enumerate distinct products in M_n^{(2)}(N), bin by d(k).

    Returns (M_n, bin_counts, bin_log_sums, log_M_n_total) where:
      bin_counts[D] = #{distinct products with d(k) = D}
      bin_log_sums[D] = Σ log(n²k) over distinct products in bin D
      log_M_n_total = Σ log(n²k) over all distinct products
    """
    K = N // (n * n)
    c_max = math.isqrt(K)
    cs = coprime_below(c_max, n)

    if verbose:
        print(f'    n={n}, N={N:>10}: K={K}, c_max={c_max}, '
              f'|coprime|={len(cs)}', flush=True)

    t0 = time.time()
    d_sieve = divisor_sieve(K)
    sieve_time = time.time() - t0

    t0 = time.time()
    products = set()
    for i, c1 in enumerate(cs):
        for c2 in cs[i:]:
            products.add(c1 * c2)
    enum_time = time.time() - t0

    t0 = time.time()
    bin_counts = {}
    bin_log_sums = {}
    log_total = 0.0
    log_n2 = 2 * math.log(n)
    for k in products:
        D = int(d_sieve[k])
        log_m = log_n2 + math.log(k)
        bin_counts[D] = bin_counts.get(D, 0) + 1
        bin_log_sums[D] = bin_log_sums.get(D, 0) + log_m
        log_total += log_m
    bin_time = time.time() - t0

    if verbose:
        print(f'      sieve={sieve_time:.2f}s, enum={enum_time:.2f}s, '
              f'bin={bin_time:.2f}s, M_n={len(products)}', flush=True)

    return len(products), bin_counts, bin_log_sums, log_total


# ---- aggregate ----

def Q_at_D(D):
    """Q_n at the rank-2 cell with d(k) = D (universal across prime n)."""
    return 1 - D / 2


def main():
    print('h2_cell_resolved.py — bin distinct products by d(k); '
          'compute Q-weighted sum\n', flush=True)
    print(f'panel n: {PANEL_NS}', flush=True)
    print(f'N values: {ENUMERATION_NS}\n', flush=True)

    csv_rows = [(
        'n', 'N', 'd_k', 'Q_n_at_cell',
        'bin_count', 'bin_log_sum',
        'M_n_total', 'log_M_n_total',
        'bin_count_frac', 'bin_log_frac',
        'cell_contribution_to_S_n',
    )]

    summary_lines = ['Brief 4 / Phase 4 (B) — h=2 cell-resolved table',
                     '',
                     'Per cell: Q_n(n²k) = 1 - d(k)/2 (universal across prime n).',
                     'Empirical: bin distinct products m = n²k by d(k).',
                     'S_n(N) = Σ Q_n(m) · log(m) = Σ_D (1 - D/2) · log_sum(D).',
                     '',
                     ]

    all_results = {}  # (n, N) -> (M_n, bins, log_sums, total)

    print('=== Per-(n, N) bin tables ===', flush=True)
    for N in ENUMERATION_NS:
        print(f'\n--- N = {N:>10} ---', flush=True)
        for n in PANEL_NS:
            M_n, bins, log_sums, log_total = cell_resolved(n, N)
            all_results[(n, N)] = (M_n, bins, log_sums, log_total)

            # Compute Q-weighted sum S_n(N) = Σ_D (1 - D/2) · log_sums[D]
            S_n = sum((1 - D / 2) * log_sums[D] for D in log_sums)

            summary_lines.append('')
            summary_lines.append(f'  n = {n}, N = {N:>10}: '
                                 f'M_n = {M_n}, S_n = {S_n:.4f}, '
                                 f'log_total = {log_total:.4f}')
            summary_lines.append(
                '    D   Q_n@D    bin_cnt   bin_frac    bin_log_sum    '
                '  log_frac   cell·Q_n·log'
            )
            summary_lines.append(
                '    --  ------  --------  ----------  ------------  '
                '----------  ---------------'
            )
            for D in sorted(bins.keys()):
                cnt = bins[D]
                lsum = log_sums[D]
                Q = Q_at_D(D)
                cnt_frac = cnt / M_n if M_n else 0
                log_frac = lsum / log_total if log_total else 0
                contrib = Q * lsum
                summary_lines.append(
                    f'    {D:>2}  {Q:>+5.1f}   {cnt:>8}  {cnt_frac:>10.6f}  '
                    f'{lsum:>12.4f}  {log_frac:>10.6f}  {contrib:>+15.4f}'
                )
                csv_rows.append((
                    n, N, D, Q, cnt, f'{lsum:.6f}',
                    M_n, f'{log_total:.6f}',
                    f'{cnt_frac:.8f}', f'{log_frac:.8f}',
                    f'{contrib:.6f}',
                ))

    # ---- Q-weighted sum table ----
    summary_lines.append('')
    summary_lines.append('=== Λ_n-weighted sum S_n(N) per (n, N) ===')
    summary_lines.append('')
    summary_lines.append('  S_n(N) = Σ Q_n(m) · log(m), summed over distinct')
    summary_lines.append('  products in M_n^{(2)}(N). Q_n(n²k) = 1 - d(k)/2.')
    summary_lines.append('')
    summary_lines.append(
        '  n  | ' + ' | '.join(f'N=10^{int(math.log10(N))}'.rjust(15) for N in ENUMERATION_NS)
    )
    summary_lines.append(
        '  ---+' + '+'.join(['-' * 17] * len(ENUMERATION_NS))
    )
    for n in PANEL_NS:
        parts = [f'  {n:>2} ']
        for N in ENUMERATION_NS:
            _, _, log_sums, _ = all_results[(n, N)]
            S_n = sum((1 - D / 2) * log_sums[D] for D in log_sums)
            parts.append(f'{S_n:>15.4f}')
        summary_lines.append('|'.join(parts) + '|')

    # ---- Bin-fraction comparison across n ----
    summary_lines.append('')
    summary_lines.append('=== Bin-count fraction f_n(D, N) at largest N ===')
    summary_lines.append('')
    summary_lines.append('  Predicts: shift toward higher D for restricted')
    summary_lines.append('  d-distribution on coprime-to-n integers.')
    summary_lines.append('')

    N_max = ENUMERATION_NS[-1]
    summary_lines.append(f'  N = {N_max:>10}, all values are bin_count(n, D) / M_n(N)')
    summary_lines.append('')
    all_Ds = sorted(set(D for n in PANEL_NS for D in all_results[(n, N_max)][1]))
    truncated_Ds = [D for D in all_Ds if D <= MAX_BIN_DISPLAY]
    if any(D > MAX_BIN_DISPLAY for D in all_Ds):
        truncated_Ds.append('≥' + str(MAX_BIN_DISPLAY + 1))

    header = '   D ' + ''.join(f'  n={n:>2}      ' for n in PANEL_NS)
    summary_lines.append(header)
    summary_lines.append('  ---' + ''.join(' ----------- ' for n in PANEL_NS))
    for D in all_Ds[:MAX_BIN_DISPLAY]:
        row = f'  {D:>2} '
        for n in PANEL_NS:
            _, bins, _, _ = all_results[(n, N_max)]
            M_n = all_results[(n, N_max)][0]
            cnt = bins.get(D, 0)
            frac = cnt / M_n if M_n else 0
            row += f'  {frac:>10.6f}'
        summary_lines.append(row)
    if any(D > MAX_BIN_DISPLAY for D in all_Ds):
        row = f'  ≥{MAX_BIN_DISPLAY + 1:<2}'
        for n in PANEL_NS:
            _, bins, _, _ = all_results[(n, N_max)]
            M_n = all_results[(n, N_max)][0]
            cnt_total = sum(c for D, c in bins.items() if D > MAX_BIN_DISPLAY)
            frac = cnt_total / M_n if M_n else 0
            row += f'  {frac:>10.6f}'
        summary_lines.append(row)

    # ---- Mean d(k) on the multiplication-table image, by n ----
    summary_lines.append('')
    summary_lines.append('=== Mean d(k) on M_n^{(2)}(N) image, by n ===')
    summary_lines.append('')
    summary_lines.append(
        '  n  | ' + ' | '.join(f'N=10^{int(math.log10(N))}'.rjust(11) for N in ENUMERATION_NS)
    )
    summary_lines.append(
        '  ---+' + '+'.join(['-' * 13] * len(ENUMERATION_NS))
    )
    for n in PANEL_NS:
        parts = [f'  {n:>2} ']
        for N in ENUMERATION_NS:
            M_n, bins, _, _ = all_results[(n, N)]
            mean_d = sum(D * c for D, c in bins.items()) / M_n if M_n else 0
            parts.append(f'{mean_d:>11.4f}')
        summary_lines.append('|'.join(parts) + '|')

    # ---- Mean Q_n on M_n^{(2)}(N) image (not log-weighted) ----
    summary_lines.append('')
    summary_lines.append('=== Mean Q_n on M_n^{(2)}(N) image, by n ===')
    summary_lines.append('')
    summary_lines.append('  Mean Q_n = (1/M_n) Σ Q_n(m) = 1 - mean_d(k)/2.')
    summary_lines.append(
        '  n  | ' + ' | '.join(f'N=10^{int(math.log10(N))}'.rjust(11) for N in ENUMERATION_NS)
    )
    summary_lines.append(
        '  ---+' + '+'.join(['-' * 13] * len(ENUMERATION_NS))
    )
    for n in PANEL_NS:
        parts = [f'  {n:>2} ']
        for N in ENUMERATION_NS:
            M_n, bins, _, _ = all_results[(n, N)]
            mean_Q = sum((1 - D / 2) * c for D, c in bins.items()) / M_n if M_n else 0
            parts.append(f'{mean_Q:>+11.4f}')
        summary_lines.append('|'.join(parts) + '|')

    # ---- Write outputs ----
    csv_path = os.path.join(HERE, 'h2_cell_resolved.csv')
    with open(csv_path, 'w', newline='') as f:
        csv.writer(f).writerows(csv_rows)
    print(f'\nwrote {csv_path}', flush=True)

    summary_path = os.path.join(HERE, 'h2_cell_resolved_summary.txt')
    with open(summary_path, 'w') as f:
        f.write('\n'.join(summary_lines) + '\n')
    print(f'wrote {summary_path}', flush=True)

    # Print headlines.
    print('\n=== Mean d(k) at N=10^7 ===', flush=True)
    for n in PANEL_NS:
        M_n, bins, _, _ = all_results[(n, ENUMERATION_NS[-1])]
        mean_d = sum(D * c for D, c in bins.items()) / M_n if M_n else 0
        print(f'  n = {n}: mean d(k) = {mean_d:.4f}', flush=True)

    print('\n=== Mean Q_n at N=10^7 ===', flush=True)
    for n in PANEL_NS:
        M_n, bins, _, _ = all_results[(n, ENUMERATION_NS[-1])]
        mean_Q = sum((1 - D / 2) * c for D, c in bins.items()) / M_n if M_n else 0
        print(f'  n = {n}: mean Q_n = {mean_Q:+.4f}', flush=True)

    print('\n=== S_n(N) at N=10^7 ===', flush=True)
    for n in PANEL_NS:
        _, _, log_sums, _ = all_results[(n, ENUMERATION_NS[-1])]
        S_n = sum((1 - D / 2) * log_sums[D] for D in log_sums)
        print(f'  n = {n}: S_n = {S_n:+.4f}', flush=True)


if __name__ == '__main__':
    main()
