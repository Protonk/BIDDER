"""
h2_ratio_n1e8.py — extend ratio test to K = 10^8
====================================================

Per the cross-thread critique: at K=10^7 the ratio drift hasn't
visibly stopped. Whether it converges to α_n (independence) or to
something else needs another decade. K=10^8 is one bytearray pass
away.

Skips the divisor sieve at this K (we don't need S_n bins for the
ratio test). Memory: ~200 MB peak (M_Ford bytearray + one n at a
time).

Predictions PRE-WRITTEN (before computing) per geometric-slowdown
extrapolation of the K=10^4..10^7 ratio drift:

    n=2:  ρ_K(K=10^8) ≈ 0.378 ± 0.001    (drift slowed from +0.0037/dec)
    n=3:  0.557 ± 0.002                   (+0.0044/dec last)
    n=5:  0.719 ± 0.002                   (+0.0051/dec last)
    n=7:  0.792 ± 0.002                   (+0.0035/dec last)
    n=11: 0.862 ± 0.002                   (+0.0025/dec last)
    n=13: 0.881 ± 0.002                   (+0.0023/dec last)

Read-outs per the agent's three cases:
  - In range: geometric slowdown continues; α_n asymptote plausible.
  - Above range: drift NOT slowing as expected; outcome 2 less clean.
  - Below range or reversal: structure change.

Usage:
    python3 h2_ratio_n1e8.py
"""

import csv
import math
import os
import time
from math import gcd


HERE = os.path.dirname(os.path.abspath(__file__))
PANEL_NS = [2, 3, 5, 7, 11, 13]
K = 10**8

# K=10^7 reference ratios (from h2_ratio_vs_ford.csv).
K7_RATIOS = {
    2: 0.374891, 3: 0.554332, 5: 0.715020,
    7: 0.789136, 11: 0.859843, 13: 0.879547,
}

# Pre-written predictions (drift extrapolation).
PREDICTIONS = {
    2: (0.378, 0.001),
    3: (0.557, 0.002),
    5: (0.719, 0.002),
    7: (0.792, 0.002),
    11: (0.862, 0.002),
    13: (0.881, 0.002),
}


def M_Ford(K):
    """Unrestricted Ford M(K) via bytearray. ~30-60s at K=10^8."""
    c_max = math.isqrt(K)
    seen = bytearray(K + 1)
    for c1 in range(1, c_max + 1):
        for c2 in range(c1, c_max + 1):
            seen[c1 * c2] = 1
    return seen.count(1)


def M_n_count(n, K):
    """Coprime-to-n distinct cofactor products via bytearray."""
    c_max = math.isqrt(K)
    cs = [c for c in range(1, c_max + 1) if gcd(c, n) == 1]
    seen = bytearray(K + 1)
    for i, c1 in enumerate(cs):
        for c2 in cs[i:]:
            seen[c1 * c2] = 1
    return seen.count(1)


def main():
    print(f'h2_ratio_n1e8.py — extending ratio test to K = {K}\n', flush=True)
    print('Pre-written predictions from K=10^4..10^7 drift extrapolation:',
          flush=True)
    for n in PANEL_NS:
        pred, tol = PREDICTIONS[n]
        print(f'  n={n:>2}: ρ_K(10^8) ≈ {pred:.4f} ± {tol:.4f}', flush=True)
    print('', flush=True)

    # ---- Compute M_Ford at K=10^8 ----
    print(f'Computing M_Ford(K = {K})...', flush=True)
    t0 = time.time()
    M_F = M_Ford(K)
    elapsed = time.time() - t0
    print(f'  M_Ford = {M_F:>12} ({elapsed:.1f}s)\n', flush=True)

    # ---- Compute M_n per n, compare ----
    print('=== K = 10^8 results ===', flush=True)
    print(f'  {"n":>3} | {"M_n":>12} | {"ratio":>9} | {"K=10^7":>9} | '
          f'{"Δ":>9} | {"pred":>7} | in range?', flush=True)
    print('  ----+--------------+-----------+-----------+-----------+'
          '---------+----------', flush=True)

    results = {}
    for n in PANEL_NS:
        t0 = time.time()
        M = M_n_count(n, K)
        elapsed = time.time() - t0
        ratio = M / M_F
        prev_ratio = K7_RATIOS[n]
        delta = ratio - prev_ratio
        pred, tol = PREDICTIONS[n]
        in_range = abs(ratio - pred) <= tol
        marker = 'YES' if in_range else f'NO ({ratio - pred:+.4f})'
        results[n] = (M, ratio, delta, in_range)
        print(f'  {n:>3} | {M:>12} | {ratio:>9.6f} | {prev_ratio:>9.6f} | '
              f'{delta:>+9.6f} | {pred:>7.4f} | {marker}    ({elapsed:.1f}s)',
              flush=True)

    # ---- Drift slowdown check ----
    print('\n=== Drift slowdown check ===', flush=True)
    print('  (drift K6→7) vs (drift K7→8); geometric slowdown predicts '
          'second is smaller', flush=True)
    K6_ratios = {2: 0.371170, 3: 0.549921, 5: 0.709940,
                 7: 0.785604, 11: 0.857338, 13: 0.877295}
    print(f'  {"n":>3} | {"drift 6→7":>11} | {"drift 7→8":>11} | ratio',
          flush=True)
    for n in PANEL_NS:
        d67 = K7_RATIOS[n] - K6_ratios[n]
        d78 = results[n][1] - K7_RATIOS[n]
        slowdown = d78 / d67 if d67 > 0 else float('nan')
        print(f'  {n:>3} | {d67:>+11.6f} | {d78:>+11.6f} | {slowdown:>5.3f}',
              flush=True)

    # ---- Compare to α_n and α_n² ----
    print('\n=== Compared to candidate limits ===', flush=True)
    print(f'  {"n":>3} | {"ratio":>9} | {"α_n²":>9} | {"α_n":>9} | '
          f'{"diff α_n²":>10} | {"diff α_n":>10}', flush=True)
    for n in PANEL_NS:
        ratio = results[n][1]
        a = (n - 1) / n
        a2 = a ** 2
        print(f'  {n:>3} | {ratio:>9.6f} | {a2:>9.6f} | {a:>9.6f} | '
              f'{ratio - a2:>+10.6f} | {ratio - a:>+10.6f}', flush=True)

    # ---- Output ----
    csv_path = os.path.join(HERE, 'h2_ratio_n1e8.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['n', 'K', 'M_Ford', 'M_n', 'ratio',
                    'alpha_n2', 'alpha_n',
                    'K7_ratio', 'delta_from_K7',
                    'predicted', 'tolerance', 'in_range'])
        for n in PANEL_NS:
            M, ratio, delta, in_range = results[n]
            a = (n - 1) / n
            a2 = a ** 2
            pred, tol = PREDICTIONS[n]
            w.writerow([n, K, M_F, M, f'{ratio:.6f}',
                        f'{a2:.6f}', f'{a:.6f}',
                        f'{K7_RATIOS[n]:.6f}', f'{delta:+.6f}',
                        f'{pred:.4f}', f'{tol:.4f}',
                        'YES' if in_range else 'NO'])
    print(f'\nwrote {csv_path}', flush=True)


if __name__ == '__main__':
    main()
