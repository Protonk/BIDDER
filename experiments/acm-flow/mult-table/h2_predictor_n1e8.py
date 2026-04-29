"""
h2_predictor_n1e8.py — Brief 4 / Phase 4 (A): push to N = 10^8
=================================================================

Extends `h2_predictor.py` to N = 10^8 using a memory-efficient
bytearray-based direct enumeration. Disambiguates the open question
from `BRIEF4-h2.md`:

    Is the empirical M_n(N)·Φ(N)/N drift away from the simple
    Ford-flat prediction (n−1)²/n⁴ a (a) prefactor correction or
    (b) deficit exponent shift c → c(n) > c?

Plateau at a constant value of `M_n / M_2` ⇒ prefactor correction.
Continued logarithmic decay of `M_n / M_2` ⇒ c-shift.

Method:

For each (n, N), enumerate distinct products c_1·c_2 with c_1, c_2
coprime to n and c_1, c_2 ≤ √(N/n²). Each product k ≤ N/n² is
recorded in a bytearray of size N/n² + 1; bytearray.count(1) gives
M_n(N).

Memory at N = 10^8: max 25 MB (n = 2). Time: a few minutes total.
Pair-iteration is restricted to c_1 ≤ c_2 (half the work; bytearray
dedupes regardless of iteration order).

Panel extended to n ∈ {2, 3, 5, 7, 11, 13} — the prime panel. Each
n is computed independently; bytearray for n is freed before the
next n.

Output:

    h2_predictor_n1e8.csv         per-(n, N) data table
    h2_predictor_n1e8_summary.txt human-readable convergence analysis

Usage:
    python3 h2_predictor_n1e8.py
"""

import csv
import math
import os
import sys
import time
from math import gcd, log


HERE = os.path.dirname(os.path.abspath(__file__))

PANEL_NS = [2, 3, 5, 7, 11, 13]
ENUMERATION_NS = [10**4, 10**5, 10**6, 10**7, 10**8]
FORD_C = 1 - (1 + math.log(math.log(2))) / math.log(2)


# ---- predicted constants ----

def C_predicted(n):
    """C(n) = (n−1)² / n⁴, the prefactor of κ_F in the asymptotic
    M_n(N) · Φ(N) / N → κ_F · C(n)."""
    return (n - 1) ** 2 / n ** 4


def Phi(N):
    """Ford's Φ(N) = (log N)^c · (log log N)^{3/2}."""
    lN = log(N)
    llN = log(lN)
    return lN ** FORD_C * llN ** 1.5


# ---- bytearray-based enumeration ----

def coprime_below(c_max, n):
    """Integers c with 1 ≤ c ≤ c_max and gcd(c, n) = 1."""
    return [c for c in range(1, c_max + 1) if gcd(c, n) == 1]


def M_n_enumerate(n, N, verbose=True):
    """Memory-efficient direct enumeration of M_n(N).

    M_n(N) = |{distinct c_1·c_2 ≤ N/n² : c_i coprime to n, c_i ≤ √(N/n²)}|.

    Uses bytearray of size N/n² + 1 to deduplicate products.
    Inner loop iterates c_1 ≤ c_2 (saves a factor of 2 on iterations;
    bytearray writes are idempotent so this is safe)."""
    K = N // (n * n)
    c_max = math.isqrt(K)
    cs = coprime_below(c_max, n)
    if verbose:
        bytearray_mb = (K + 1) / 1024 / 1024
        n_pairs = len(cs) * (len(cs) + 1) // 2
        print(f'    n={n}, N={N:>11}: K={K}, c_max={c_max}, '
              f'|coprime|={len(cs)}, unordered pairs={n_pairs}, '
              f'bytearray={bytearray_mb:.2f} MB', flush=True)
    seen = bytearray(K + 1)
    t0 = time.time()
    for i, c1 in enumerate(cs):
        for c2 in cs[i:]:
            seen[c1 * c2] = 1
    elapsed = time.time() - t0
    M = seen.count(1)
    if verbose:
        print(f'      done in {elapsed:.2f}s; M_n(N) = {M}', flush=True)
    return M


# ---- main ----

def main():
    print('h2_predictor_n1e8.py — extended Brief 4 h=2 panel\n', flush=True)
    print(f'panel n: {PANEL_NS}', flush=True)
    print(f'N values: {ENUMERATION_NS}', flush=True)
    print(f'Ford c = {FORD_C:.10f}\n', flush=True)

    # ---- predicted constants ----
    print('=== Predicted constants C(n) = (n−1)² / n⁴ ===', flush=True)
    print(f'  {"n":>3} | {"C(n)":>12} | {"C(n)/C(2)":>12}', flush=True)
    print(f'  ----+--------------+--------------', flush=True)
    C_panel = {}
    for n in PANEL_NS:
        c = C_predicted(n)
        C_panel[n] = c
        ratio = c / C_panel[2] if 2 in C_panel else 1
        print(f'  {n:>3} | {c:>12.6f} | {ratio:>12.6f}', flush=True)
    print('', flush=True)

    # ---- empirical enumeration ----
    print('=== Empirical M_n(N) by direct enumeration (bytearray) ===',
          flush=True)
    M_results = {}

    csv_rows = [(
        'n', 'N', 'M_n', 'M_n_phi_over_N',
        'ratio_to_n_eq_2', 'predicted_ratio',
        'diff_from_predicted_ratio',
    )]

    # Iterate by N then n so we can compare ratios at fixed N as we go.
    for N in ENUMERATION_NS:
        print(f'\n  --- N = {N:>11} ---', flush=True)
        for n in PANEL_NS:
            M_n = M_n_enumerate(n, N)
            M_results[(n, N)] = M_n
            m_phi_over_N = M_n * Phi(N) / N

            ratio_to_2 = ''
            pred_ratio = C_panel[n] / C_panel[2]
            diff = ''
            if (2, N) in M_results and M_results[(2, N)] > 0:
                M_2 = M_results[(2, N)]
                r = M_n / M_2
                ratio_to_2 = f'{r:.6f}'
                diff = f'{r - pred_ratio:+.6f}'

            csv_rows.append((
                n, N, M_n, f'{m_phi_over_N:.6f}',
                ratio_to_2, f'{pred_ratio:.6f}', diff,
            ))

    csv_path = os.path.join(HERE, 'h2_predictor_n1e8.csv')
    with open(csv_path, 'w', newline='') as f:
        csv.writer(f).writerows(csv_rows)
    print(f'\nwrote {csv_path}', flush=True)

    # ---- convergence analysis ----
    print('\n=== Ratio convergence: M_n / M_2 vs predicted (n−1)²·16/n⁴ ===',
          flush=True)
    print(f'  Plateau at constant value ⇒ prefactor correction.',
          flush=True)
    print(f'  Continued decay with N ⇒ deficit exponent shift c → c(n).\n',
          flush=True)

    summary_lines = ['Brief 4 / Phase 4 (A) — h=2 prime-n mult-table — N up to 10^8',
                     '',
                     f'Ford c = {FORD_C:.6f}',
                     f'panel n: {PANEL_NS}',
                     f'N values: {ENUMERATION_NS}',
                     '',
                     '=== Ratio M_n / M_2 across N (predicted: (n−1)²·16/n⁴) ===',
                     '']

    header = f'  n  | predicted | ' + ' | '.join(f'N=10^{int(math.log10(N))}'.rjust(11) for N in ENUMERATION_NS)
    print(header, flush=True)
    summary_lines.append(header)
    sep = f'  ---+-----------+' + '+'.join(['-' * 13] * len(ENUMERATION_NS))
    print(sep, flush=True)
    summary_lines.append(sep)

    for n in PANEL_NS:
        if n == 2:
            continue
        pred = C_panel[n] / C_panel[2]
        row_parts = [f'  {n:>2} | {pred:>9.6f} ']
        for N in ENUMERATION_NS:
            r = M_results[(n, N)] / M_results[(2, N)]
            row_parts.append(f'{r:>11.6f}')
        line = '|'.join(row_parts) + '|'
        print(line, flush=True)
        summary_lines.append(line)

    print('\n=== Drift per n (deviation from predicted, %) ===', flush=True)
    summary_lines.append('')
    summary_lines.append('=== Drift per n: 100 · (observed / predicted − 1) ===')
    summary_lines.append('')

    header2 = f'  n  | ' + ' | '.join(f'N=10^{int(math.log10(N))}'.rjust(11) for N in ENUMERATION_NS)
    print(header2, flush=True)
    summary_lines.append(header2)
    sep2 = f'  ---+' + '+'.join(['-' * 13] * len(ENUMERATION_NS))
    print(sep2, flush=True)
    summary_lines.append(sep2)
    for n in PANEL_NS:
        if n == 2:
            continue
        pred = C_panel[n] / C_panel[2]
        row_parts = [f'  {n:>2} ']
        for N in ENUMERATION_NS:
            r = M_results[(n, N)] / M_results[(2, N)]
            pct = 100 * (r / pred - 1)
            row_parts.append(f'{pct:>+10.2f}%')
        line = '|'.join(row_parts) + '|'
        print(line, flush=True)
        summary_lines.append(line)

    # Plateau check: compare drift at N=10^7 vs N=10^8 per n.
    summary_lines.append('')
    summary_lines.append('=== Plateau-vs-shift signal: drift change between N=10^7 and N=10^8 ===')
    summary_lines.append('')
    summary_lines.append('  Small change ⇒ plateau ⇒ prefactor correction.')
    summary_lines.append('  Continued change ⇒ c-shift.')
    summary_lines.append('')
    summary_lines.append(f'  {"n":>3} | drift @ 10^7 | drift @ 10^8 | change')
    summary_lines.append(f'  ----+--------------+--------------+----------')
    for n in PANEL_NS:
        if n == 2:
            continue
        pred = C_panel[n] / C_panel[2]
        r7 = M_results[(n, 10**7)] / M_results[(2, 10**7)]
        r8 = M_results[(n, 10**8)] / M_results[(2, 10**8)]
        d7 = 100 * (r7 / pred - 1)
        d8 = 100 * (r8 / pred - 1)
        summary_lines.append(
            f'  {n:>3} | {d7:>+10.3f}% | {d8:>+10.3f}% | '
            f'{(d8 - d7):>+8.3f}%'
        )

    summary_path = os.path.join(HERE, 'h2_predictor_n1e8_summary.txt')
    with open(summary_path, 'w') as f:
        f.write('\n'.join(summary_lines) + '\n')
    print(f'\nwrote {summary_path}', flush=True)


if __name__ == '__main__':
    main()
