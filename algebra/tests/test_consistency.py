"""
test_consistency.py — Layer 3 cross-form checks for the algebra.

Whenever two implementations of the same object share a domain, the
test asserts they agree on a sample of that domain. Failures here
indicate two implementations have drifted apart — most often an
indexing-convention drift between forms.

Cross-form checks (in priority order — keystone first):

C4-cross. Master-expansion (q_general) versus C4 integer-language
    enumeration (count_ordered_factorizations_into_multiples).
    The flagship test of this layer. q_general computes Q_n(m) by the
    Mercator-derived master expansion; the C4 enumerator counts ordered
    j-fold factorisations of m into multiples of n by direct iteration,
    using neither Mercator nor the multiplicative kernel tau. Agreement
    between the two is independent evidence that the master expansion
    is correct, since the two paths share no algebraic infrastructure
    beyond the integers themselves. Source: MASTER-EXPANSION.md C4.

C4-tau-identity. The C4 enumerator versus the tau identity it should
    satisfy: N_j(n, m) == tau(j, m // n**j) when n**j divides m, else 0.
    Source: MASTER-EXPANSION.md C4.

A5-extended. q_general versus q_value_by_class on coprime (n, k), at a
    denser grid than A5 in test_anchors.py. Source:
    MASTER-EXPANSION.md (consistency between general and class-form).

A10a-extended. row_polynomial versus row_polynomial_qe_closed on q^e
    cofactors, lifting the omega cap and e cap from A10. Source:
    ROW-OGF.md.

What failure means. Two implementations disagree. Read both functions
named in the failure header and identify the convention drift. The C4
cross-check is the strongest gate: if C4 fails, the master expansion
itself is suspect.

Run:

    python3 algebra/tests/test_consistency.py
"""

from __future__ import annotations

import os
import sys
from fractions import Fraction
from math import gcd

HERE = os.path.dirname(os.path.abspath(__file__))
ALGEBRA = os.path.dirname(HERE)
sys.path.insert(0, ALGEBRA)

from predict_q import (  # noqa: E402
    big_omega, count_ordered_factorizations_into_multiples,
    factor_tuple, n_adic_height, q_general, q_value_by_class,
    row_polynomial, row_polynomial_qe_closed,
    shape_of, tau, tau_sig_of,
)


# --------------------------------------------------------------------------
# C4-cross: master expansion vs. direct enumeration of N_j
# --------------------------------------------------------------------------

def consistency_c4_cross(n_list=(2, 3, 5, 6), h_list=(1, 2, 3, 4),
                          k_list=tuple(range(1, 16))) -> int:
    """Assert q_general(n, h, k) == sum_{j=1..nu_n(m)} (-1)^(j-1) N_j(m) / j
    where N_j is computed by direct enumeration (no tau, no Mercator).
    """
    fails = 0
    checked = 0
    for n in n_list:
        for h in h_list:
            for k in k_list:
                m = n**h * k
                h_eff = n_adic_height(n, m)
                via_c4 = sum(
                    Fraction((-1)**(j - 1)
                              * count_ordered_factorizations_into_multiples(n, m, j),
                              j)
                    for j in range(1, h_eff + 1)
                )
                via_q = q_general(n, h, k)
                checked += 1
                if via_c4 != via_q:
                    print(f'C4-cross FAIL  n={n} h={h} k={k} (m={m}, h_eff={h_eff}): '
                          f'C4 sum = {via_c4}, q_general = {via_q}')
                    fails += 1
    if fails == 0:
        print(f'C4-cross PASS  master expansion == alt-sum N_j/j '
              f'({checked} cases via direct enumeration)')
    return fails


# --------------------------------------------------------------------------
# C4-tau-identity: N_j matches the tau formula it must satisfy
# --------------------------------------------------------------------------

def consistency_c4_tau_identity(n_list=(2, 3, 4, 5, 6, 10),
                                 m_max: int = 200,
                                 j_max: int = 6) -> int:
    """N_j(n, m) == tau(j, m // n**j) when n**j divides m, else 0."""
    fails = 0
    checked = 0
    for n in n_list:
        for m in range(1, m_max + 1):
            for j in range(1, j_max + 1):
                lhs = count_ordered_factorizations_into_multiples(n, m, j)
                if m % n**j == 0:
                    rhs = tau(j, m // n**j)
                else:
                    rhs = 0
                checked += 1
                if lhs != rhs:
                    print(f'C4-tau FAIL  n={n} m={m} j={j}: '
                          f'N_j={lhs}, tau identity={rhs}')
                    fails += 1
    if fails == 0:
        print(f'C4-tau PASS  N_j(n, m) == tau(j, m/n^j)·[n^j|m] '
              f'({checked} cases)')
    return fails


# --------------------------------------------------------------------------
# A5-extended: q_general vs q_value_by_class on a denser coprime grid
# --------------------------------------------------------------------------

def consistency_general_vs_class(n_max: int = 30, k_max: int = 100,
                                   h_max: int = 10) -> int:
    fails = 0
    checked = 0
    for n in range(2, n_max + 1):
        n_primes = {p for p, _e in factor_tuple(n)}
        for k in range(1, k_max + 1):
            if any(k % p == 0 for p in n_primes):
                continue
            for h in range(1, h_max + 1):
                got_general = q_general(n, h, k)
                got_class = q_value_by_class(shape_of(n), h, tau_sig_of(k))
                checked += 1
                if got_general != got_class:
                    if fails < 5:
                        print(f'A5-ext FAIL  n={n} k={k} h={h}: '
                              f'general {got_general} != class {got_class}')
                    fails += 1
    if fails == 0:
        print(f'A5-ext PASS  q_general == q_value_by_class on coprime (n, k) '
              f'(n<={n_max}, k<={k_max}, h<={h_max}; {checked} cases)')
    return fails


# --------------------------------------------------------------------------
# A10a-extended: row_polynomial vs row_polynomial_qe_closed at higher e
# --------------------------------------------------------------------------

def consistency_row_polynomial_qe(p_list=(2, 3, 5, 7, 11, 13, 17),
                                    q_list=(2, 3, 5, 7, 11, 13, 17),
                                    e_max: int = 12) -> int:
    fails = 0
    checked = 0
    for p in p_list:
        for q in q_list:
            if q == p:
                continue
            for e in range(1, e_max + 1):
                kp = q**e
                got = row_polynomial(p, kp)
                want = row_polynomial_qe_closed(e)
                checked += 1
                if got != want:
                    print(f'A10a-ext FAIL  p={p} q={q} e={e}: '
                          f'row_polynomial={got}, closed={want}')
                    fails += 1
    if fails == 0:
        print(f'A10a-ext PASS  row_polynomial == closed (1 - (1-x)^e)/e '
              f'(e<={e_max}; {checked} cases)')
    return fails


def main():
    fails = 0
    fails += consistency_c4_tau_identity()
    fails += consistency_c4_cross()
    fails += consistency_general_vs_class()
    fails += consistency_row_polynomial_qe()

    print()
    if fails == 0:
        print('ALL CONSISTENCY CHECKS PASS')
        return 0
    print(f'TOTAL FAILS: {fails}')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
