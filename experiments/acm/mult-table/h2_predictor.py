"""
h2_predictor.py — h = 2 multiplication-table predictor for prime n
====================================================================

Per `BRIEF4-h2.md`. For prime n, the rank-2 (binary) multiplication-table
count

    M_n(N) := |{ a · b : a, b ∈ A_n, a, b ≤ √N }|

is predicted by Ford's anatomy + coprime-to-n density:

    M_n(N) · Φ(N) / N  →  κ_F · (n−1)² / n⁴       as N → ∞,

where Φ(N) = (log N)^c · (log log N)^{3/2} with Ford's deficit
exponent c = 1 − (1 + log log 2)/log 2 ≈ 0.0860713320, and κ_F is
Ford's universal constant.

The script:

1. Computes the predicted constant `C(n) = (n−1)²/n⁴` for the panel.
2. Direct-enumerates `M_n(N)` for small N (panel n, N ∈ {10^4, 10^5, 10^6}).
3. Compares the empirical ratio `M_n(N) · Φ(N) / N` to the predicted
   constant (modulo κ_F, identifiable from the n=2 row).
4. Reports the asymptote ratio `M_n / M_2` for each N — testable
   without κ_F.

Usage:
    sage -python h2_predictor.py
"""

import csv
import math
import os
from math import gcd, log


HERE = os.path.dirname(os.path.abspath(__file__))

PANEL_NS = [2, 3, 5, 7]  # primes only — composite n needs rank decomposition
ENUMERATION_NS = [10**4, 10**5, 10**6, 10**7]
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


# ---- direct enumeration of M_n(N) ----

def coprime_below(c_max, n):
    """Integers c with 1 ≤ c ≤ c_max and gcd(c, n) = 1."""
    return [c for c in range(1, c_max + 1) if gcd(c, n) == 1]


def M_n_enumerate(n, N):
    """Direct enumeration of M_n(N) = |{c_1·c_2 : c_i ≤ √N / n, c_i ⊥ n}|.

    Returns a set-cardinality (the count of distinct cofactor products
    in the balanced n-prime mult-table). Cost ≈ |coprime|² which is
    ((n−1)·√N/n)² ~ ((n−1)²/n²) · N. Manageable for N ≤ 10^7."""
    c_max = int(math.isqrt(N)) // n
    cs = coprime_below(c_max, n)
    products = set()
    for c1 in cs:
        for c2 in cs:
            products.add(c1 * c2)
    return len(products)


# ---- main ----

def main():
    print('h2_predictor.py — Brief 4 / Phase 4 — h=2 prime-n mult-table\n', flush=True)
    print(f'Ford c = {FORD_C:.10f}\n', flush=True)

    print('=== Predicted constants C(n) = (n−1)² / n⁴ ===', flush=True)
    print(f'  {"n":>3} | {"C(n)":>12} | {"C(n)/C(2)":>12} | predicted asymptote',
          flush=True)
    print(f'  ----+--------------+--------------+--------------', flush=True)
    C_panel = {}
    for n in PANEL_NS:
        c = C_predicted(n)
        C_panel[n] = c
        ratio = c / C_panel[2] if 2 in C_panel else 1
        print(f'  {n:>3} | {c:>12.6f} | {ratio:>12.6f} | κ_F · {c:.6f}',
              flush=True)
    print('', flush=True)

    print('=== Empirical M_n(N) by direct enumeration ===', flush=True)
    print(f'  {"n":>3} | {"N":>10} | {"c_max":>5} | {"|coprime|":>9} | '
          f'{"M_n(N)":>10} | {"M_n·Φ/N":>10} | ratio to n=2',
          flush=True)
    print(f'  ----+------------+-------+-----------+------------+'
          f'------------+--------------', flush=True)

    csv_rows = [(
        'n', 'N', 'c_max', 'coprime_count', 'M_n', 'M_n_phi_over_N',
        'ratio_to_n_eq_2', 'predicted_ratio', 'predicted_diff',
    )]
    M_results = {}
    for N in ENUMERATION_NS:
        for n in PANEL_NS:
            c_max = int(math.isqrt(N)) // n
            cs = coprime_below(c_max, n)
            M_n = M_n_enumerate(n, N)
            M_results[(n, N)] = M_n
            m_phi_over_N = M_n * Phi(N) / N

            ratio_to_2 = ''
            pred_ratio = ''
            pred_diff = ''
            if 2 in PANEL_NS and (2, N) in M_results:
                M_2 = M_results[(2, N)]
                if M_2 > 0:
                    r = M_n / M_2
                    pr = C_panel[n] / C_panel[2]
                    ratio_to_2 = f'{r:.6f}'
                    pred_ratio = f'{pr:.6f}'
                    pred_diff = f'{r - pr:+.6f}'

            print(f'  {n:>3} | {N:>10} | {c_max:>5} | {len(cs):>9} | '
                  f'{M_n:>10} | {m_phi_over_N:>10.4f} | '
                  f'{ratio_to_2:>10}{(f" (pred {pred_ratio})") if pred_ratio else ""}',
                  flush=True)

            csv_rows.append((
                n, N, c_max, len(cs),
                M_n, f'{m_phi_over_N:.6f}',
                ratio_to_2, pred_ratio, pred_diff,
            ))
        print('', flush=True)

    csv_path = os.path.join(HERE, 'h2_predictor.csv')
    with open(csv_path, 'w', newline='') as f:
        csv.writer(f).writerows(csv_rows)
    print(f'wrote {csv_path}', flush=True)

    # ---- summary: convergence of ratio to predicted ----
    print('\n=== Ratio convergence: M_n / M_2 vs predicted (n−1)²·16/n⁴ ===',
          flush=True)
    print(f'  Smaller |diff| = closer to Ford-flat with prefactor (n−1)²/n⁴.',
          flush=True)
    print(f'  |diff| at largest N is the cleanest single-shot test.\n',
          flush=True)
    for n in PANEL_NS:
        if n == 2:
            continue
        diffs = []
        for N in ENUMERATION_NS:
            r = M_results[(n, N)] / M_results[(2, N)]
            pr = C_panel[n] / C_panel[2]
            diffs.append((N, r, pr, r - pr))
        last_diff = diffs[-1][3]
        print(f'  n = {n}: predicted ratio = {C_panel[n]/C_panel[2]:.6f}',
              flush=True)
        for N, r, pr, d in diffs:
            print(f'    N = {N:>10}: observed = {r:.6f}, '
                  f'diff = {d:+.6f} ({100*d/pr:+.2f}%)', flush=True)
        print('', flush=True)


if __name__ == '__main__':
    main()
