"""
use_case_02_benford_null.py — §7.2 Benford-test null distribution.

Demonstrates the substrate-level (§3.2) and sieved-level (§3.3)
exact uniformity claims as a deterministic anti-Benford reference
for Benford-detector calibration.

Two demonstrations per (b, d) panel:

  1. Integer-level: enumerate [b^(d-1), b^d - 1], count leading
     digits. Pearson chi-squared = 0 by construction (each digit
     j ∈ {1, ..., b-1} occurs exactly b^(d-1) times).

  2. Sieved n-prime level (when n² | b^(d-1)): filter to multiples
     of n not divisible by n². Each leading digit gets exactly
     b^(d-1)·(n-1)/n² atoms.

Comparator: i.i.d. uniform sampling on the same domain. Pearson
chi-squared distribution under the null is χ²(b-2); we report the
empirical mean and standard deviation across 1000 trials at the
matching sample size.

Output: replication/use_case_02_results.md.
"""

import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def leading_digit(n: int, b: int) -> int:
    while n >= b:
        n //= b
    return n


def chi_squared_uniform(counts: list[int], expected: float) -> float:
    return sum((c - expected) ** 2 / expected for c in counts)


def integer_block_demo(b: int, d: int):
    lo, hi = b ** (d - 1), b ** d - 1
    N = hi - lo + 1
    counts = [0] * b
    for x in range(lo, hi + 1):
        counts[leading_digit(x, b)] += 1
    expected = b ** (d - 1)
    by_digit = counts[1:b]
    chi2 = chi_squared_uniform(by_digit, expected)
    return {
        'N': N,
        'expected_per_bin': expected,
        'counts': by_digit,
        'chi2': chi2,
    }


def sieved_nprime_demo(b: int, n: int, d: int):
    """Filter to n-prime atoms (multiples of n not divisible by n²)."""
    if (b ** (d - 1)) % (n * n) != 0:
        return None  # smooth condition fails
    lo, hi = b ** (d - 1), b ** d - 1
    counts = [0] * b
    total = 0
    for x in range(lo, hi + 1):
        if x % n == 0 and x % (n * n) != 0:
            counts[leading_digit(x, b)] += 1
            total += 1
    expected = b ** (d - 1) * (n - 1) // (n * n)
    by_digit = counts[1:b]
    chi2 = chi_squared_uniform(by_digit, expected)
    return {
        'n': n,
        'N': total,
        'expected_per_bin': expected,
        'counts': by_digit,
        'chi2': chi2,
    }


def iid_chi_squared_distribution(b: int, d: int, N: int, n_trials: int = 1000):
    rng = np.random.default_rng(seed=20260502)
    lo, hi = b ** (d - 1), b ** d - 1
    expected = N / (b - 1)
    chi2_values = np.empty(n_trials)
    for t in range(n_trials):
        sample = rng.integers(lo, hi + 1, size=N)
        counts = np.zeros(b, dtype=np.int64)
        for x in sample:
            counts[leading_digit(int(x), b)] += 1
        by_digit = counts[1:b]
        chi2 = float(np.sum((by_digit - expected) ** 2 / expected))
        chi2_values[t] = chi2
    return float(chi2_values.mean()), float(chi2_values.std()), expected


def main():
    panel = [(10, 3), (10, 4), (10, 5), (8, 5), (16, 4)]
    n_trials = 1000

    print('§7.2 Benford-test null distribution')
    print(f'  panel: {panel}, n_trials = {n_trials}')
    print()

    integer_rows = []
    print('Integer-level (substrate §3.2):')
    print(f'  {"(b, d)":<10} {"N":>10} {"expected":>10} {"BIDDER χ²":>10} {"i.i.d. mean":>12} {"i.i.d. std":>12} {"χ²(b-2) df":>10}')
    for b, d in panel:
        bidder = integer_block_demo(b, d)
        iid_mean, iid_std, _ = iid_chi_squared_distribution(b, d, bidder['N'], n_trials)
        integer_rows.append({
            'b': b, 'd': d,
            'N': bidder['N'],
            'expected': bidder['expected_per_bin'],
            'bidder_chi2': bidder['chi2'],
            'iid_mean': iid_mean,
            'iid_std': iid_std,
            'df': b - 2,
        })
        print(f'  ({b:>2}, {d}) {bidder["N"]:>10,} {bidder["expected_per_bin"]:>10,} '
              f'{bidder["chi2"]:>10.4f} {iid_mean:>12.4f} {iid_std:>12.4f} {b - 2:>10}')
    print()

    sieved_rows = []
    print('Sieved n-prime level (substrate §3.3, smooth n² | b^(d-1)):')
    print(f'  {"(b, n, d)":<14} {"N (n-primes)":>14} {"expected":>10} {"BIDDER χ²":>10}')
    for b, d in panel:
        for n_candidate in [2, 3, 5, 7, 10]:
            if (b ** (d - 1)) % (n_candidate * n_candidate) == 0 and n_candidate < b:
                sieved = sieved_nprime_demo(b, n_candidate, d)
                if sieved is None:
                    continue
                sieved_rows.append({
                    'b': b, 'n': n_candidate, 'd': d,
                    'N': sieved['N'],
                    'expected': sieved['expected_per_bin'],
                    'chi2': sieved['chi2'],
                })
                print(f'  ({b:>2}, {n_candidate:>2}, {d}) {sieved["N"]:>14,} '
                      f'{sieved["expected_per_bin"]:>10,} {sieved["chi2"]:>10.4f}')
                break  # one n per (b, d) is enough for the demo
    print()

    md_path = os.path.join(HERE, 'use_case_02_results.md')
    with open(md_path, 'w') as f:
        f.write('# §7.2 — Benford-test null distribution\n\n')
        f.write('Generated by `replication/use_case_02_benford_null.py`. '
                'Substrate-leveraged use case (§3.2 + §3.3 do the work).\n\n')
        f.write('The integer-level lemma (§3.2) gives exact leading-digit '
                'uniformity on the digit-class block `[b^(d-1), b^d - 1]`. '
                'The sieved lemma (§3.3) extends the result to n-prime '
                'atoms when the smooth condition `n² | b^(d-1)` holds. '
                'Pearson chi-squared on either is **exactly zero** — '
                'no sampling noise at any panel size.\n\n')

        f.write('## Integer-level (substrate §3.2)\n\n')
        f.write('| (b, d) | N | expected per bin | BIDDER χ² | i.i.d. mean | i.i.d. std | χ²(b-2) df |\n')
        f.write('|---|---|---|---|---|---|---|\n')
        for r in integer_rows:
            f.write(f'| ({r["b"]}, {r["d"]}) | {r["N"]:,} | {r["expected"]:,} | '
                    f'{r["bidder_chi2"]:.4f} | {r["iid_mean"]:.4f} | '
                    f'{r["iid_std"]:.4f} | {r["df"]} |\n')
        f.write('\n')
        f.write('*BIDDER row:* chi-squared = 0 exactly at every cell — '
                'the substrate guarantee is structural, not statistical. '
                f'*i.i.d. row:* {n_trials} trials of uniform sampling on '
                'the same block; reported as mean ± std. The theoretical '
                'i.i.d. distribution under the null is `χ²(b-2)`, which '
                'has mean `b-2` and standard deviation `sqrt(2(b-2))`. '
                'The empirical mean / std should track these closely.\n\n')

        f.write('## Sieved n-prime level (substrate §3.3, smooth `n² | b^(d-1)`)\n\n')
        f.write('| (b, n, d) | N (n-primes) | expected per bin | BIDDER χ² |\n')
        f.write('|---|---|---|---|\n')
        for r in sieved_rows:
            f.write(f'| ({r["b"]}, {r["n"]}, {r["d"]}) | {r["N"]:,} | '
                    f'{r["expected"]:,} | {r["chi2"]:.4f} |\n')
        f.write('\n')
        f.write('*All sieved rows: chi-squared = 0 exactly.* The '
                'smooth-block lemma gives exactly `b^(d-1)·(n-1)/n²` '
                'n-prime atoms per leading digit. This is the corpus '
                'a Benford-detector calibration would draw from when '
                'using `bidder.sawtooth` to produce the n-prime '
                'sequence.\n\n')

        f.write('## Reading\n\n')
        f.write('- **Headline payoff.** The substrate produces a '
                'deterministic anti-Benford reference with zero '
                'sampling noise on the leading-digit counts at any '
                'block size. A Benford-detector\'s response on this '
                'reference reflects the detector\'s properties alone '
                'rather than the reference\'s finite-sample variance.\n')
        f.write('- **i.i.d. comparator.** The same block sampled with '
                'replacement gives chi-squared distributed as `χ²(b-2)` '
                'under the null. The expected value is `b-2` (so 8 at '
                '`b = 10`, 6 at `b = 8`, 14 at `b = 16`); the standard '
                'deviation is `sqrt(2(b-2))`. The contrast is sharp: '
                'zero (BIDDER, exact) vs the χ²(b-2) mean and spread '
                '(i.i.d., asymptotic).\n')
        f.write('- **Use something else when** a Benford-conforming '
                'reference is what the calibration needs (sample from '
                'Benford\'s distribution); BIDDER is uniform-leading-'
                'digit, not Benford-conforming.\n')

    print(f'Wrote {md_path}')


if __name__ == '__main__':
    main()
