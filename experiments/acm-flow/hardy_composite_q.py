"""
hardy_composite_q.py — Phase 2.4 deep composite-Q witnesses
============================================================

Per `experiments/acm-flow/STRUCTURE-HUNT.md` Phase 2.4 and the closing
caveat of `experiments/math/hardy/DEEP-TROUBLE-No-4.md`.

Hardy random access returns *atoms* of M_n (n-primes), all of which have
trivial rank: ν_n(p_K(n)) = 1 and Q_n(p_K(n)) = 1 vacuously. To probe
the Q_n closed forms at unreachable depth we multiply r ≥ 2 atoms into
a composite m ∈ M_n. For prime n, multiplicativity forces

    h = ν_n(m) = r,

while for prime-power and squarefree-multi-prime n the atom cofactors
can re-introduce primes dividing n, so h ≥ r and h is always measured
directly from the prime factorisation of m.

We then evaluate Q_n(m) by two structurally independent paths and
assert exact `Fraction` equality:

  master path : factor-aware master expansion from `core/Q-FORMULAS.md`,
                with overlap-shifted binomials × τ_j(k');

  direct path : Σ_{j=1..h} (−1)^(j−1) τ_j(m/n^j) / j with τ_j evaluated
                directly on the raw prime factorisation of m/n^j, with
                no overlap split.

Where the displayed-formula scope of `core/Q-FORMULAS.md` applies, the
displayed specialisation is evaluated as a third independent path.

This is not a new proof of the formula. It is a deep-access sanity loop
showing the finite-rank implementation agrees with itself at scales no
prefix sieve or precomputed τ-table can reach.

Usage:
    sage -python hardy_composite_q.py
"""

import csv
import os
import sys
from fractions import Fraction
from math import comb

from sage.all import factor as sage_factor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'experiments', 'math', 'hardy'))

from hardy_echo import nth_n_prime  # noqa: E402


# ---- factorisation utilities ----

def factor_dict(x):
    """Prime factorisation of positive int x as {p: e}. {} when x == 1."""
    if x < 1:
        raise ValueError(f'factor_dict requires x >= 1; got {x}')
    if x == 1:
        return {}
    out = {}
    for p, e in sage_factor(x):
        out[int(p)] = int(e)
    return out


def factor_small(n):
    """Trial division for the small index n. Returns {p: e}."""
    out = {}
    r = n
    p = 2
    while p * p <= r:
        while r % p == 0:
            out[p] = out.get(p, 0) + 1
            r //= p
        p += 1 if p == 2 else 2
    if r > 1:
        out[r] = out.get(r, 0) + 1
    return out


def mul_facs(*dicts):
    out = {}
    for d in dicts:
        for p, e in d.items():
            out[p] = out.get(p, 0) + e
    return out


def divide_n_power(m_facs, n_facs, j):
    """Factorisation of m / n^j. Caller has verified n^j | m."""
    out = dict(m_facs)
    for p, a in n_facs.items():
        e = out.get(p, 0) - a * j
        if e < 0:
            raise ValueError(f'divide_n_power underflow at p={p}, j={j}')
        if e == 0:
            out.pop(p, None)
        else:
            out[p] = e
    return out


def height_n(m_facs, n_facs):
    """ν_n(m) = min over p | n of ⌊v_p(m) / v_p(n)⌋."""
    if not n_facs:
        raise ValueError('height_n requires n with at least one prime')
    return min(m_facs.get(p, 0) // a for p, a in n_facs.items())


def tau_j(j, facs):
    """τ_j(x) = ∏_{p^e || x} C(e + j − 1, j − 1)."""
    if j < 1:
        raise ValueError(f'tau_j requires j >= 1; got {j}')
    if not facs:
        return 1
    out = 1
    for e in facs.values():
        out *= comb(e + j - 1, j - 1)
    return out


def integer_from_facs(facs):
    out = 1
    for p, e in facs.items():
        out *= p ** e
    return out


# ---- two routes plus displayed-specialisation route ----

def q_direct(m_facs, n_facs, h):
    """Direct: Q_n(m) = Σ (−1)^(j−1) τ_j(m/n^j) / j for j = 1..h, with
    τ_j evaluated on the raw factorisation of m/n^j."""
    total = Fraction(0)
    for j in range(1, h + 1):
        sub = divide_n_power(m_facs, n_facs, j)
        sgn = 1 if j % 2 == 1 else -1
        total += Fraction(sgn * tau_j(j, sub), j)
    return total


def q_master(m_facs, n_facs, h):
    """Master expansion (Q-FORMULAS §Master): split k = m/n^h into
    overlap (t_i on primes of n) and a coprime remainder k', then
    Σ (−1)^(j−1) [∏ C(a_i(h−j) + t_i + j − 1, j − 1)] · τ_j(k') / j."""
    k_facs = divide_n_power(m_facs, n_facs, h)
    k_prime_facs = {}
    overlaps = {p: 0 for p in n_facs}
    for p, e in k_facs.items():
        if p in n_facs:
            overlaps[p] = e
        else:
            k_prime_facs[p] = e

    total = Fraction(0)
    for j in range(1, h + 1):
        coeff = 1
        for p, a in n_facs.items():
            t = overlaps[p]
            coeff *= comb(a * (h - j) + t + j - 1, j - 1)
        sgn = 1 if j % 2 == 1 else -1
        total += Fraction(sgn * coeff * tau_j(j, k_prime_facs), j)
    return total


def n_kind(n_facs):
    omega = len(n_facs)
    Omega = sum(n_facs.values())
    if omega == 1 and Omega == 1:
        return 'prime'
    if omega == 1:
        return 'prime_power'
    return 'multi_prime'


def q_displayed(n_facs, m_facs, h):
    """Displayed specialisation from `core/Q-FORMULAS.md` if (n_kind, h)
    is in declared scope. Returns (kind_label, value_or_None)."""
    kind = n_kind(n_facs)
    k_facs = divide_n_power(m_facs, n_facs, h)
    k_prime_facs = {p: e for p, e in k_facs.items() if p not in n_facs}
    overlaps = [(p, k_facs.get(p, 0)) for p in n_facs]

    if kind == 'prime':
        # Exact-height for prime n forces overlap t = 0; structural.
        if overlaps[0][1] != 0:
            return 'prime_overlap_violation', None
        total = Fraction(0)
        for j in range(1, h + 1):
            sgn = 1 if j % 2 == 1 else -1
            total += Fraction(sgn * comb(h - 1, j - 1) * tau_j(j, k_prime_facs), j)
        return 'prime', total

    if kind == 'prime_power':
        ((p, a),) = list(n_facs.items())
        if a != 2 or h > 4:
            return 'out_of_declared_scope', None
        t = overlaps[0][1]
        if t not in (0, 1):
            return 'out_of_declared_scope', None
        d = tau_j(2, k_prime_facs)
        t3 = tau_j(3, k_prime_facs)
        t4 = tau_j(4, k_prime_facs)
        if h == 1:
            return 'n4', Fraction(1)
        if h == 2 and t == 0:
            return 'n4', Fraction(1) - Fraction(d, 2)
        if h == 2 and t == 1:
            return 'n4', Fraction(1) - d
        if h == 3 and t == 0:
            return 'n4', Fraction(1) - Fraction(3 * d, 2) + Fraction(t3, 3)
        if h == 3 and t == 1:
            return 'n4', Fraction(1) - 2 * d + t3
        if h == 4 and t == 0:
            return 'n4', Fraction(1) - Fraction(5 * d, 2) + 2 * t3 - Fraction(t4, 4)
        if h == 4 and t == 1:
            return 'n4', Fraction(1) - 3 * d + Fraction(10 * t3, 3) - t4
        return 'out_of_declared_scope', None

    # squarefree two-prime through h = 4
    if all(e == 1 for e in n_facs.values()) and len(n_facs) == 2 and h <= 4:
        t1, t2 = overlaps[0][1], overlaps[1][1]
        if t1 > 0 and t2 > 0:
            return 'out_of_declared_scope', None
        if h == 1:
            return 'sq2', Fraction(1)
        if h == 2:
            return 'sq2', Fraction(1) - Fraction(tau_j(2, k_facs), 2)
        d = tau_j(2, k_prime_facs)
        t3 = tau_j(3, k_prime_facs)
        t4 = tau_j(4, k_prime_facs)
        if h == 3 and t1 == 0 and t2 == 0:
            return 'sq2', Fraction(1) - 2 * d + Fraction(t3, 3)
        if h == 3:
            t = t1 if t1 > 0 else t2
            return 'sq2', (
                Fraction(1)
                - (t + 2) * d
                + Fraction((t + 2) * (t + 1) * t3, 6)
            )
        if h == 4 and t1 == 0 and t2 == 0:
            return 'sq2', Fraction(1) - Fraction(9 * d, 2) + 3 * t3 - Fraction(t4, 4)
        if h == 4:
            t = t1 if t1 > 0 else t2
            return 'sq2', (
                Fraction(1)
                - Fraction(3 * (t + 3) * d, 2)
                + Fraction((t + 3) * (t + 2) * t3, 2)
                - Fraction((t + 3) * (t + 2) * (t + 1) * t4, 24)
            )

    return 'out_of_declared_scope', None


# ---- panel ----

PANEL = [
    # --- prime n: h = r exactly ---
    (2, (10**6, 10**6 + 1), 'n=2 r=2 mid'),
    (2, (10**6, 10**9, 10**12), 'n=2 r=3 spread mid-deep'),
    (2, (10**6, 10**7, 10**8, 10**9, 10**10), 'n=2 r=5 spread'),
    (2, tuple(10**6 + i for i in range(8)), 'n=2 r=8 high-rank stress'),
    (2, (10**50, 10**50 + 1), 'n=2 r=2 deep K=10^50'),
    (2, (10**100, 10**100 + 1), 'n=2 r=2 very deep K=10^100'),
    (3, (10**6, 10**6 + 1), 'n=3 r=2 mid'),
    (3, (10**9, 10**10, 10**11), 'n=3 r=3 deep'),
    (5, (10**6, 10**6 + 1), 'n=5 r=2 mid'),
    (5, (10**6, 10**7, 10**8), 'n=5 r=3 spread'),

    # --- prime power n = 4: h ≥ r, with deliberate h > r cases ---
    (4, (10**6, 10**6 + 1), 'n=4 r=2 mid (expect h=r=2)'),
    (4, (2, 2), 'n=4 r=2 forced h>r (cof 2,2 → h=3)'),
    (4, (2, 2, 2), 'n=4 r=3 forced h>r (cof 2,2,2 → h=4)'),
    (4, (2, 2, 2, 2), 'n=4 r=4 jump=2 (m=2^12 → h=6)'),
    (4, (10**6 + 1, 10**6 + 1), 'n=4 r=2 deep+forced h>r at K=10^6+1'),
    (4, (10**6, 10**7, 10**8), 'n=4 r=3 spread'),
    (4, (10**6, 10**9, 10**12), 'n=4 r=3 spread mid-deep'),

    # --- squarefree multi-prime n = 6, n = 10: h ≥ r, with forced h > r ---
    (6, (10**6, 10**6 + 1), 'n=6 r=2 mid'),
    (6, (2, 3), 'n=6 r=2 forced h>r (cof 2,3 → h=3)'),
    (6, (1, 2, 3), 'n=6 r=3 forced h>r (cof 1,2,3 → h=4)'),
    (6, (4, 8), 'n=6 r=2 jump=2 (cof 4,9 → m=6^4)'),
    (6, (10**6, 10**7), 'n=6 r=2 mid spread'),
    (6, (10**12, 10**12 + 1), 'n=6 r=2 deep K=10^12'),
    (10, (10**6, 10**6 + 1), 'n=10 r=2 mid'),
    (10, (2, 5), 'n=10 r=2 forced h>r (cof 2,5 → h=3)'),
    (10, (10**6, 10**7), 'n=10 r=2 mid spread'),
    (10, (10**12, 10**12 + 1), 'n=10 r=2 deep K=10^12'),
]


# ---- bridge smoke: enumerable cases against payload_q_scan-era values ----

SMOKE_CASES = [
    # (n, m, expected Q)  — derived by hand from Q-FORMULAS.md.
    (2, 4,  Fraction(1, 2)),
    (2, 36, Fraction(-1, 2)),
    (3, 27, Fraction(1, 3)),
    (4, 16, Fraction(1, 2)),
    (6, 36, Fraction(1, 2)),
]


def smoke_check():
    print('[smoke] enumerable cases — both paths agree with hand values', flush=True)
    for n, m, expected in SMOKE_CASES:
        n_facs = factor_small(n)
        m_facs = factor_dict(m)
        h = height_n(m_facs, n_facs)
        a = q_direct(m_facs, n_facs, h)
        b = q_master(m_facs, n_facs, h)
        ok = (a == b == expected)
        marker = 'OK' if ok else 'FAIL'
        print(f'  Q_{n}({m}) = direct {a} | master {b} | expected {expected}  {marker}',
              flush=True)
        if not ok:
            raise SystemExit('[smoke] FAIL')
    print('  [smoke] all pass.\n', flush=True)


# ---- per-row evaluation ----

def evaluate_row(n, K_tuple, label):
    n_facs = factor_small(n)

    atoms = [nth_n_prime(n, K) for K in K_tuple]
    cofactors = [a // n for a in atoms]
    cof_facs = [factor_dict(c) for c in cofactors]
    atom_facs = [mul_facs(n_facs, cf) for cf in cof_facs]
    m_facs = mul_facs(*atom_facs) if atom_facs else {}

    h = height_n(m_facs, n_facs)
    r = len(K_tuple)
    m_int = integer_from_facs(m_facs)
    m_digits = len(str(m_int))

    q_d = q_direct(m_facs, n_facs, h)
    q_m = q_master(m_facs, n_facs, h)
    direct_master_agree = (q_d == q_m)

    spec_kind, q_s = q_displayed(n_facs, m_facs, h)
    if q_s is None:
        spec_agree = None
    else:
        spec_agree = (q_s == q_m)

    return {
        'n': n,
        'r': r,
        'K_tuple': K_tuple,
        'label': label,
        'h_measured': h,
        'h_expected_min': r,
        'm_digits': m_digits,
        'q_master': q_m,
        'q_direct': q_d,
        'spec_kind': spec_kind,
        'q_spec': q_s,
        'direct_master_agree': direct_master_agree,
        'spec_agree': spec_agree,
    }


def main():
    print('hardy_composite_q.py — Phase 2.4 deep composite-Q witnesses\n', flush=True)
    smoke_check()

    csv_path = os.path.join(HERE, 'hardy_composite_q.csv')
    summary_path = os.path.join(HERE, 'hardy_composite_q_summary.txt')

    csv_rows = [(
        'n', 'r', 'K_tuple', 'label', 'h_measured', 'h_expected_min',
        'm_digits', 'q_master_num', 'q_master_den',
        'q_direct_num', 'q_direct_den', 'spec_kind',
        'q_spec_num', 'q_spec_den',
        'direct_master_agree', 'spec_agree',
    )]
    direct_master_mismatches = []
    spec_mismatches = []
    height_jumps = []  # informational: composite/prime-power n with h > r

    print(f'panel size: {len(PANEL)}\n', flush=True)
    for n, K_tuple, label in PANEL:
        print(f'-- {label}', flush=True)
        print(f'   n={n}  K={K_tuple}', flush=True)
        result = evaluate_row(n, K_tuple, label)
        h_tag = '' if result['h_measured'] == result['r'] else f'  (h>r: +{result["h_measured"] - result["r"]})'
        print(f'   h measured = {result["h_measured"]}'
              f'  (r = {result["r"]}, m has {result["m_digits"]} '
              f'base-10 digits){h_tag}', flush=True)
        print(f'   Q master = {result["q_master"]}', flush=True)
        print(f'   Q direct = {result["q_direct"]}'
              f'    direct==master: {result["direct_master_agree"]}', flush=True)
        if result['q_spec'] is not None:
            print(f'   Q displayed ({result["spec_kind"]}) = '
                  f'{result["q_spec"]}    spec==master: {result["spec_agree"]}',
                  flush=True)
        else:
            print(f'   displayed: {result["spec_kind"]} (skipped)', flush=True)
        print('', flush=True)

        if not result['direct_master_agree']:
            direct_master_mismatches.append(result)
        if result['spec_agree'] is False:
            spec_mismatches.append(result)
        if result['h_measured'] > result['r']:
            height_jumps.append(result)

        spec_num = result['q_spec'].numerator if result['q_spec'] is not None else ''
        spec_den = result['q_spec'].denominator if result['q_spec'] is not None else ''
        csv_rows.append((
            result['n'], result['r'],
            ' '.join(str(K) for K in result['K_tuple']),
            result['label'],
            result['h_measured'], result['h_expected_min'],
            result['m_digits'],
            result['q_master'].numerator, result['q_master'].denominator,
            result['q_direct'].numerator, result['q_direct'].denominator,
            result['spec_kind'], spec_num, spec_den,
            result['direct_master_agree'], result['spec_agree'],
        ))

    with open(csv_path, 'w', newline='') as f:
        csv.writer(f).writerows(csv_rows)
    print(f'wrote {csv_path}  ({len(csv_rows) - 1} rows)', flush=True)

    ok = (not direct_master_mismatches) and (not spec_mismatches)
    with open(summary_path, 'w') as f:
        f.write('hardy_composite_q.py — Phase 2.4 deep composite-Q witnesses\n\n')
        f.write(f'panel size: {len(PANEL)}\n')
        f.write(f'direct vs master mismatches: {len(direct_master_mismatches)}\n')
        f.write(f'displayed-special mismatches: {len(spec_mismatches)}\n')
        f.write(f'height jumps (h > r), informational: {len(height_jumps)}\n')
        f.write('\n')

        if height_jumps:
            f.write('=== Height jumps (composite / prime-power n, h > r) ===\n')
            for row in height_jumps:
                f.write(
                    f'  {row["label"]}: n={row["n"]} r={row["r"]} '
                    f'h_measured={row["h_measured"]}\n'
                )
            f.write('\n')

        if direct_master_mismatches:
            f.write('=== Direct vs master mismatches ===\n')
            for row in direct_master_mismatches[:20]:
                f.write(
                    f'  {row["label"]}: master {row["q_master"]} '
                    f'direct {row["q_direct"]}\n'
                )
            f.write('\n')

        if spec_mismatches:
            f.write('=== Displayed-special mismatches ===\n')
            for row in spec_mismatches[:20]:
                f.write(
                    f'  {row["label"]}: master {row["q_master"]} '
                    f'spec ({row["spec_kind"]}) {row["q_spec"]}\n'
                )
            f.write('\n')

        f.write('=== Verdict ===\n')
        f.write('PASS\n' if ok else 'FAIL\n')

    print(f'wrote {summary_path}', flush=True)
    if not ok:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
