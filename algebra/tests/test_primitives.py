"""
test_primitives.py — Layer 2 unit tests for the algebra primitives.

Covers the building blocks of every theorem in algebra/*.md:

    factor_tuple, shape_of, tau_sig_of, tau,
    n_adic_height, decompose, big_omega, little_omega,
    plus invalid-input gates on q_value_by_class, q_general, q_row,
    row_polynomial, row_polynomial_qe_closed, row_sum.

What this layer is for. Most assertions are tautologies if the
implementations are correct. The value is catching the case where two
primitives drift apart (e.g., shape_of and tau_sig_of are defined to
agree, big_omega is defined as sum of exponents from factor_tuple), or
where a primitive's input contract changes silently and downstream
anchors keep passing for the wrong reason.

A failure here means a building block has a bug or a contract changed.
The first place to look is predict_q.py.

Run:

    python3 algebra/tests/test_primitives.py
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
    big_omega, decompose, factor_tuple, little_omega, n_adic_height,
    q_general, q_row, q_value_by_class,
    row_polynomial, row_polynomial_qe_closed, row_sum,
    shape_of, tau, tau_sig_of,
)


def _expect_raises(name, callable_, *args, **kwargs):
    try:
        callable_(*args, **kwargs)
    except (ValueError, TypeError):
        return 0
    print(f'FAIL  {name}({args}, {kwargs}) was expected to raise')
    return 1


def _naive_divisor_count(x):
    return sum(1 for d in range(1, x + 1) if x % d == 0)


# --------------------------------------------------------------------------
# factor_tuple
# --------------------------------------------------------------------------

def test_factor_tuple(N=2000):
    fails = 0
    for n in range(1, N + 1):
        ft = factor_tuple(n)
        prod = 1
        for p, e in ft:
            prod *= p**e
        if prod != n:
            print(f'FAIL  factor_tuple({n}) = {ft} reconstructs {prod} != {n}')
            fails += 1
        # primes ascending
        primes = [p for p, _e in ft]
        if primes != sorted(primes):
            print(f'FAIL  factor_tuple({n}) primes not ascending: {primes}')
            fails += 1
    if factor_tuple(1) != ():
        print(f'FAIL  factor_tuple(1) != ()')
        fails += 1

    fails += _expect_raises('factor_tuple', factor_tuple, 0)
    fails += _expect_raises('factor_tuple', factor_tuple, -1)

    # cache stability
    if factor_tuple(60) is not factor_tuple(60):
        print('FAIL  factor_tuple cache returned distinct objects')
        fails += 1

    if fails == 0:
        print(f'PASS  factor_tuple roundtrip + edges + reject ({N} cases)')
    return fails


# --------------------------------------------------------------------------
# shape_of / tau_sig_of definitional consistency
# --------------------------------------------------------------------------

def test_shape_and_tau_sig(N=500):
    fails = 0
    for n in range(1, N + 1):
        expected = tuple(sorted((e for _p, e in factor_tuple(n)), reverse=True))
        if shape_of(n) != expected:
            print(f'FAIL  shape_of({n}) = {shape_of(n)} != {expected}')
            fails += 1
        if tau_sig_of(n) != expected:
            print(f'FAIL  tau_sig_of({n}) = {tau_sig_of(n)} != {expected}')
            fails += 1
        if shape_of(n) != tau_sig_of(n):
            print(f'FAIL  shape_of({n}) != tau_sig_of({n})')
            fails += 1

    if shape_of(1) != () or tau_sig_of(1) != ():
        print('FAIL  shape_of(1) or tau_sig_of(1) != ()')
        fails += 1

    if fails == 0:
        print(f'PASS  shape_of, tau_sig_of definitional consistency ({N} cases)')
    return fails


# --------------------------------------------------------------------------
# tau
# --------------------------------------------------------------------------

def test_tau():
    fails = 0
    # tau(1, x) == 1
    for x in range(1, 101):
        if tau(1, x) != 1:
            print(f'FAIL  tau(1, {x}) = {tau(1, x)} != 1')
            fails += 1
    # tau(j, 1) == 1
    for j in range(1, 21):
        if tau(j, 1) != 1:
            print(f'FAIL  tau({j}, 1) != 1')
            fails += 1
    # tau(2, x) == d(x) (naive)
    for x in range(1, 201):
        if tau(2, x) != _naive_divisor_count(x):
            print(f'FAIL  tau(2, {x}) = {tau(2, x)} != d({x}) = {_naive_divisor_count(x)}')
            fails += 1
    # multiplicativity tau(j, p*q) == tau(j, p) * tau(j, q) for coprime p, q
    coprime_pairs = [(2, 3), (2, 5), (3, 5), (4, 9), (4, 25), (8, 27),
                     (3, 7), (5, 7), (9, 25), (11, 13)]
    for j in range(1, 8):
        for p, q in coprime_pairs:
            assert gcd(p, q) == 1
            lhs = tau(j, p * q)
            rhs = tau(j, p) * tau(j, q)
            if lhs != rhs:
                print(f'FAIL  tau({j}, {p}*{q}) = {lhs} != {rhs}')
                fails += 1
    # reject
    fails += _expect_raises('tau(0, 5)', tau, 0, 5)
    fails += _expect_raises('tau(1, 0)', tau, 1, 0)
    fails += _expect_raises('tau(-1, 5)', tau, -1, 5)

    if fails == 0:
        print(f'PASS  tau identities + multiplicativity + reject')
    return fails


# --------------------------------------------------------------------------
# n_adic_height
# --------------------------------------------------------------------------

def test_n_adic_height():
    fails = 0
    # pure powers
    for n in range(2, 21):
        for h in range(0, 11):
            got = n_adic_height(n, n**h)
            if got != h:
                print(f'FAIL  n_adic_height({n}, {n}^{h}) = {got} != {h}')
                fails += 1
    # n^h * k with gcd(k, n) == 1
    for n in [2, 3, 5, 6, 10, 12]:
        for h in range(1, 6):
            for k in range(1, 30):
                if gcd(k, n) != 1:
                    continue
                got = n_adic_height(n, n**h * k)
                if got != h:
                    print(f'FAIL  n_adic_height({n}, {n}^{h}*{k}) = {got} != {h}')
                    fails += 1

    # Composite-overlap: factors of n's primes carried in k can lift the
    # height. n=6, k=12=2^2 * 3, n*k = 72 = 2^3 * 3^2 = 6^2 * 2.
    cases = [
        (6, 1, 12, 2),     # 6 * 12 = 72; 72 / 6 = 12; 12 / 6 = 2; height 2
        (6, 2, 36, 4),     # 6^2 * 36 = 1296 = 6^4
        (10, 1, 100, 3),   # 10 * 100 = 1000 = 10^3
        (4, 1, 8, 2),      # 4 * 8 = 32 = 2^5; 4^2 = 16 | 32, 4^3 = 64 > 32
        (4, 2, 4, 3),      # 4^2 * 4 = 64 = 4^3
    ]
    for n, h, k, expected in cases:
        got = n_adic_height(n, n**h * k)
        if got != expected:
            print(f'FAIL  n_adic_height({n}, {n}^{h}*{k}={n**h*k}) = {got} != {expected}')
            fails += 1

    # reject
    fails += _expect_raises('n_adic_height(1, 100)', n_adic_height, 1, 100)
    fails += _expect_raises('n_adic_height(2, 0)', n_adic_height, 2, 0)
    fails += _expect_raises('n_adic_height(0, 5)', n_adic_height, 0, 5)

    if fails == 0:
        print('PASS  n_adic_height pure-power, coprime-k, composite-overlap, reject')
    return fails


# --------------------------------------------------------------------------
# decompose
# --------------------------------------------------------------------------

def test_decompose():
    fails = 0
    checked = 0
    for n in range(2, 16):
        n_primes = [p for p, _e in factor_tuple(n)]
        for k in range(1, 101):
            n_factors, t_tuple, k_prime = decompose(n, k)
            checked += 1
            # alignment: n_factors comes from factor_tuple(n)
            if n_factors != factor_tuple(n):
                print(f'FAIL  decompose({n}, {k}): n_factors {n_factors} != factor_tuple({n})')
                fails += 1
            # t_tuple has the same length as n_factors
            if len(t_tuple) != len(n_factors):
                print(f'FAIL  decompose({n}, {k}): |t_tuple| = {len(t_tuple)} != |n_factors|')
                fails += 1
            # gcd(k_prime, n) == 1
            if gcd(k_prime, n) != 1:
                print(f'FAIL  decompose({n}, {k}): gcd(k_prime={k_prime}, {n}) != 1')
                fails += 1
            # roundtrip: k = (prod p_i^t_i) * k_prime
            prod = k_prime
            for (p, _a), t in zip(n_factors, t_tuple):
                prod *= p**t
            if prod != k:
                print(f'FAIL  decompose({n}, {k}): roundtrip {prod} != {k}')
                fails += 1
    # invalid input
    fails += _expect_raises('decompose(2, 0)', decompose, 2, 0)
    fails += _expect_raises('decompose(1, 5)', decompose, 1, 5)
    fails += _expect_raises('decompose(2, -3)', decompose, 2, -3)

    if fails == 0:
        print(f'PASS  decompose alignment + coprime + roundtrip + reject ({checked} cases)')
    return fails


# --------------------------------------------------------------------------
# big_omega / little_omega
# --------------------------------------------------------------------------

def test_omegas():
    fails = 0
    for k in range(1, 501):
        bo = big_omega(k)
        lo = little_omega(k)
        ft = factor_tuple(k)
        if bo != sum(e for _p, e in ft):
            print(f'FAIL  big_omega({k}) = {bo} != sum of exponents')
            fails += 1
        if lo != len(ft):
            print(f'FAIL  little_omega({k}) = {lo} != len(factor_tuple)')
            fails += 1
    if big_omega(1) != 0 or little_omega(1) != 0:
        print('FAIL  big_omega(1) or little_omega(1) != 0')
        fails += 1

    fails += _expect_raises('big_omega(0)', big_omega, 0)
    fails += _expect_raises('little_omega(0)', little_omega, 0)

    if fails == 0:
        print('PASS  big_omega + little_omega definitional consistency')
    return fails


# --------------------------------------------------------------------------
# Invalid-input gates on Q-value functions
# --------------------------------------------------------------------------

def test_q_invalid_inputs():
    fails = 0
    # q_value_by_class
    fails += _expect_raises('q_value_by_class h=0', q_value_by_class, (1,), 0, ())
    fails += _expect_raises('q_value_by_class shape=()', q_value_by_class, (), 3, ())
    # q_general — input contract
    fails += _expect_raises('q_general n=1', q_general, 1, 3, 5)
    fails += _expect_raises('q_general h=-1', q_general, 2, -1, 5)
    fails += _expect_raises('q_general k=0', q_general, 2, 3, 0)
    # h=0 short-circuit
    if q_general(2, 0, 5) != Fraction(0):
        print(f'FAIL  q_general(_, 0, _) != 0')
        fails += 1
    # row_polynomial
    fails += _expect_raises('row_polynomial k_prime=1', row_polynomial, 2, 1)
    fails += _expect_raises('row_polynomial p=4 (composite)', row_polynomial, 4, 9)
    fails += _expect_raises('row_polynomial gcd', row_polynomial, 2, 4)  # gcd(2,4)=2
    # row_polynomial_qe_closed
    fails += _expect_raises('row_polynomial_qe_closed e=0', row_polynomial_qe_closed, 0)
    # row_sum
    fails += _expect_raises('row_sum k_prime=1', row_sum, 2, 1)
    fails += _expect_raises('row_sum gcd', row_sum, 2, 4)
    fails += _expect_raises('row_sum p=4 (composite)', row_sum, 4, 9)
    # q_row length
    qr = q_row(2, 3, 7)
    if len(qr) != 7:
        print(f'FAIL  q_row length {len(qr)} != 7')
        fails += 1

    if fails == 0:
        print('PASS  q_value_by_class / q_general / row_* invalid-input gates')
    return fails


# --------------------------------------------------------------------------
# row_polynomial degree contract
# --------------------------------------------------------------------------

def test_row_polynomial_lengths():
    fails = 0
    PRIMES = (2, 3, 5, 7, 11)
    for p in PRIMES:
        for kp in range(2, 100):
            if gcd(p, kp) != 1:
                continue
            coefs = row_polynomial(p, kp)
            om = big_omega(kp)
            if len(coefs) != om:
                print(f'FAIL  row_polynomial({p}, {kp}) length {len(coefs)} != Omega = {om}')
                fails += 1
    for e in range(1, 10):
        if len(row_polynomial_qe_closed(e)) != e:
            print(f'FAIL  row_polynomial_qe_closed({e}) length != {e}')
            fails += 1
    if fails == 0:
        print('PASS  row_polynomial / row_polynomial_qe_closed length contracts')
    return fails


def main():
    fails = 0
    fails += test_factor_tuple()
    fails += test_shape_and_tau_sig()
    fails += test_tau()
    fails += test_n_adic_height()
    fails += test_decompose()
    fails += test_omegas()
    fails += test_q_invalid_inputs()
    fails += test_row_polynomial_lengths()

    print()
    if fails == 0:
        print('ALL PRIMITIVE TESTS PASS')
        return 0
    print(f'TOTAL FAILS: {fails}')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
