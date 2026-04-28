"""
q_n_verify.py -- Phase 2.2 exact Q_n formula verifier
=====================================================

Reads payload_q_scan.csv and verifies:

1. The master expansion from core/Q-FORMULAS.md against every row.
2. The displayed specialisations in their declared scope:
   - prime n, all h in the CSV;
   - n = 4 rows through h = 4;
   - squarefree two-prime rows through h = 4.

The comparison is exact Fraction equality. Run with:

    sage -python q_n_verify.py
"""

import csv
import os
from collections import Counter, defaultdict
from functools import lru_cache
from fractions import Fraction
from math import comb


HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, 'payload_q_scan.csv')
SUMMARY_PATH = os.path.join(HERE, 'q_n_verify_summary.txt')

EXPECTED_PANEL_NS = {2, 3, 4, 5, 6, 10}


@lru_cache(maxsize=None)
def factor_tuple(n):
    """Prime factorisation as ((p, exponent), ...)."""
    if n < 1:
        raise ValueError(f'factor_tuple expects positive n, got {n}')
    out = []
    r = n
    p = 2
    while p * p <= r:
        if r % p == 0:
            e = 0
            while r % p == 0:
                e += 1
                r //= p
            out.append((p, e))
        p += 1 if p == 2 else 2
    if r > 1:
        out.append((r, 1))
    return tuple(out)


def n_type(n):
    factors = factor_tuple(n)
    omega = len(factors)
    Omega = sum(e for _, e in factors)
    if omega == 1 and Omega == 1:
        return 'prime'
    if omega == 1:
        return 'prime_power'
    return 'multi_prime'


def n_height(n, m):
    h = 0
    while m % n == 0:
        h += 1
        m //= n
    return h


def decompose_payload(n, k):
    """Return (n_factors, overlap_exponents, k_prime)."""
    t = []
    k_prime = k
    for p, _a in factor_tuple(n):
        e = 0
        while k_prime % p == 0:
            e += 1
            k_prime //= p
        t.append(e)
    return factor_tuple(n), tuple(t), k_prime


@lru_cache(maxsize=None)
def tau(j, x):
    """Ordered j-fold divisor count tau_j(x)."""
    if j < 1:
        raise ValueError(f'tau index must be >= 1, got {j}')
    if x < 1:
        raise ValueError(f'tau argument must be >= 1, got {x}')
    if j == 1:
        return 1
    prod = 1
    for _p, e in factor_tuple(x):
        prod *= comb(e + j - 1, j - 1)
    return prod


def master_q(n, h, k):
    """Master expansion from core/Q-FORMULAS.md for m = n^h * k."""
    factors, overlaps, k_prime = decompose_payload(n, k)
    total = Fraction(0)
    for j in range(1, h + 1):
        coeff = 1
        for (_p, a), t_i in zip(factors, overlaps):
            coeff *= comb(a * (h - j) + t_i + j - 1, j - 1)
        sign = 1 if j % 2 == 1 else -1
        total += Fraction(sign * coeff * tau(j, k_prime), j)
    return total


def prime_special_q(n, h, k):
    """Displayed prime-n specialisation, valid for every h in the CSV."""
    total = Fraction(0)
    for j in range(1, h + 1):
        sign = 1 if j % 2 == 1 else -1
        total += Fraction(sign * comb(h - 1, j - 1) * tau(j, k), j)
    return total


def n4_special_q(h, k):
    """Displayed n = 4 formulas through h = 4."""
    _factors, overlaps, k_prime = decompose_payload(4, k)
    t = overlaps[0]
    if t not in (0, 1) or h > 4:
        return None
    d = tau(2, k_prime)
    t3 = tau(3, k_prime)
    t4 = tau(4, k_prime)
    if h == 2 and t == 0:
        return Fraction(1) - Fraction(d, 2)
    if h == 2 and t == 1:
        return Fraction(1) - d
    if h == 3 and t == 0:
        return Fraction(1) - Fraction(3 * d, 2) + Fraction(t3, 3)
    if h == 3 and t == 1:
        return Fraction(1) - 2 * d + t3
    if h == 4 and t == 0:
        return Fraction(1) - Fraction(5 * d, 2) + 2 * t3 - Fraction(t4, 4)
    if h == 4 and t == 1:
        return Fraction(1) - 3 * d + Fraction(10 * t3, 3) - t4
    return None


def squarefree_two_prime_special_q(n, h, k):
    """Displayed squarefree two-prime formulas through h = 4."""
    factors = factor_tuple(n)
    if len(factors) != 2 or any(e != 1 for _p, e in factors) or h > 4:
        return None
    _factors, overlaps, k_prime = decompose_payload(n, k)
    t1, t2 = overlaps
    if t1 > 0 and t2 > 0:
        return None
    if h == 2:
        return Fraction(1) - Fraction(tau(2, k), 2)

    d = tau(2, k_prime)
    t3 = tau(3, k_prime)
    t4 = tau(4, k_prime)

    if h == 3:
        if t1 == 0 and t2 == 0:
            return Fraction(1) - 2 * d + Fraction(t3, 3)
        t = t1 if t1 > 0 else t2
        return (
            Fraction(1)
            - (t + 2) * d
            + Fraction((t + 2) * (t + 1) * t3, 6)
        )

    if h == 4:
        if t1 == 0 and t2 == 0:
            return Fraction(1) - Fraction(9 * d, 2) + 3 * t3 - Fraction(t4, 4)
        t = t1 if t1 > 0 else t2
        return (
            Fraction(1)
            - Fraction(3 * (t + 3) * d, 2)
            + Fraction((t + 3) * (t + 2) * t3, 2)
            - Fraction((t + 3) * (t + 2) * (t + 1) * t4, 24)
        )

    return None


def displayed_special_q(n, h, k):
    kind = n_type(n)
    if kind == 'prime':
        return 'prime', prime_special_q(n, h, k)
    if n == 4 and h <= 4:
        return 'n4', n4_special_q(h, k)
    if kind == 'multi_prime' and h <= 4:
        return 'squarefree_two_prime', squarefree_two_prime_special_q(n, h, k)
    return 'out_of_declared_scope', None


def read_rows(path):
    with open(path, newline='') as f:
        for row in csv.DictReader(f):
            yield {
                'n': int(row['n']),
                'h': int(row['h']),
                'm': int(row['m']),
                'k': int(row['k']),
                'payload': int(row['payload']),
                'Q_csv': Fraction(int(row['Q_num']), int(row['Q_den'])),
            }


def verify(path=CSV_PATH):
    rows = list(read_rows(path))
    seen_ns = {r['n'] for r in rows}

    counts = Counter()
    by_case = Counter()
    master_mismatches = []
    special_mismatches = []
    structural_errors = []
    skipped_special = Counter()

    for r in rows:
        n = r['n']
        h = r['h']
        m = r['m']
        k = r['k']
        q_csv = r['Q_csv']

        counts['rows'] += 1
        by_case[(n, h, n_type(n))] += 1

        if m != (n ** h) * k:
            structural_errors.append((r, 'm != n^h*k'))
            continue
        if r['payload'] != k:
            structural_errors.append((r, 'payload column != k column'))
            continue
        actual_h = n_height(n, m)
        if actual_h != h:
            structural_errors.append((r, f'height {actual_h} != csv h {h}'))
            continue
        if k % n == 0:
            structural_errors.append((r, 'payload divisible by n; not exact height'))
            continue

        q_master = master_q(n, h, k)
        counts['master_checked'] += 1
        if q_master != q_csv:
            counts['master_mismatches'] += 1
            master_mismatches.append((r, q_master))

        special_kind, q_special = displayed_special_q(n, h, k)
        if q_special is None:
            skipped_special[(special_kind, n, h)] += 1
        else:
            counts['special_checked'] += 1
            if q_special != q_csv:
                counts['special_mismatches'] += 1
                special_mismatches.append((special_kind, r, q_special))

    return {
        'rows': rows,
        'seen_ns': seen_ns,
        'missing_expected_ns': sorted(EXPECTED_PANEL_NS - seen_ns),
        'extra_ns': sorted(seen_ns - EXPECTED_PANEL_NS),
        'counts': counts,
        'by_case': by_case,
        'structural_errors': structural_errors,
        'master_mismatches': master_mismatches,
        'special_mismatches': special_mismatches,
        'skipped_special': skipped_special,
    }


def write_summary(result, path=SUMMARY_PATH):
    counts = result['counts']
    with open(path, 'w') as f:
        f.write('q_n_verify.py -- Phase 2.2 exact verifier\n\n')
        f.write(f'input rows: {counts["rows"]}\n')
        f.write(f'n values present: {sorted(result["seen_ns"])}\n')
        if result['missing_expected_ns']:
            f.write(f'n values expected by broader panel but absent from CSV: '
                    f'{result["missing_expected_ns"]}\n')
        if result['extra_ns']:
            f.write(f'extra n values: {result["extra_ns"]}\n')
        f.write('\n')

        f.write('=== Checks ===\n')
        f.write(f'structural errors: {len(result["structural_errors"])}\n')
        f.write(f'master checked: {counts["master_checked"]}\n')
        f.write(f'master mismatches: {counts["master_mismatches"]}\n')
        f.write(f'displayed-special checked: {counts["special_checked"]}\n')
        f.write(f'displayed-special mismatches: {counts["special_mismatches"]}\n')
        f.write('\n')

        f.write('=== Rows by (n, h, n_type) ===\n')
        for key, count in sorted(result['by_case'].items()):
            f.write(f'{key}: {count}\n')
        f.write('\n')

        f.write('=== Displayed-special rows skipped by declared scope ===\n')
        if result['skipped_special']:
            for key, count in sorted(result['skipped_special'].items()):
                f.write(f'{key}: {count}\n')
        else:
            f.write('none\n')
        f.write('\n')

        def write_examples(title, examples, formatter):
            f.write(f'=== {title} ===\n')
            if not examples:
                f.write('none\n\n')
                return
            for item in examples[:20]:
                f.write(formatter(item))
                f.write('\n')
            if len(examples) > 20:
                f.write(f'... {len(examples) - 20} more\n')
            f.write('\n')

        write_examples(
            'Structural errors',
            result['structural_errors'],
            lambda item: f'{item[1]} :: {item[0]}',
        )
        write_examples(
            'Master mismatches',
            result['master_mismatches'],
            lambda item: f'row={item[0]} master={item[1]} csv={item[0]["Q_csv"]}',
        )
        write_examples(
            'Displayed-special mismatches',
            result['special_mismatches'],
            lambda item: (
                f'kind={item[0]} row={item[1]} '
                f'special={item[2]} csv={item[1]["Q_csv"]}'
            ),
        )

        ok = (
            not result['structural_errors']
            and counts['master_mismatches'] == 0
            and counts['special_mismatches'] == 0
        )
        f.write('=== Verdict ===\n')
        f.write('PASS\n' if ok else 'FAIL\n')


def main():
    result = verify()
    write_summary(result)
    counts = result['counts']
    print('q_n_verify.py -- Phase 2.2 exact verifier')
    print(f'  rows: {counts["rows"]}')
    print(f'  n values present: {sorted(result["seen_ns"])}')
    if result['missing_expected_ns']:
        print(f'  note: expected panel values absent from CSV: '
              f'{result["missing_expected_ns"]}')
    print(f'  structural errors: {len(result["structural_errors"])}')
    print(f'  master checked: {counts["master_checked"]}')
    print(f'  master mismatches: {counts["master_mismatches"]}')
    print(f'  displayed-special checked: {counts["special_checked"]}')
    print(f'  displayed-special mismatches: {counts["special_mismatches"]}')
    print(f'  summary: {SUMMARY_PATH}')

    if (
        result['structural_errors']
        or counts['master_mismatches']
        or counts['special_mismatches']
    ):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
