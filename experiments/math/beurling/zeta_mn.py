"""
zeta_mn.py — numerical objects for the M_n zeta function.

The non-UF arithmetic congruence monoid `M_n = {1} ∪ nZ_{>0}` has Dirichlet
series

    zeta_{M_n}(s) = sum_{m in M_n} m^{-s} = 1 + n^{-s} zeta(s)

(see algebra/Q-FORMULAS.md). This module provides numerical evaluation of:

    zeta_mn(n, s)         — direct evaluation, mpmath complex
    log_zeta_mn(n, s)     — log zeta_{M_n}(s) (principal branch)
    zeta_mn_prime(n, s)   — derivative ζ'_{M_n}(s) by symmetric difference
    log_deriv_mn(n, s)    — von-Mangoldt-style log-derivative -ζ'_{M_n}/ζ_{M_n}
    psi_mn(n, x)          — signed Mangoldt sum Σ_{m in M_n, m<=x} Q_n(m) log m
    n_mn(n, x)            — set count of M_n elements <= x

The signed Mangoldt sum uses `algebra.predict_q.q_general` for exact-rational
Q_n values, then accumulates as floats. Q_n is supported on nZ_{>0}, so the
sum iterates m = jn for j = 1..⌊x/n⌋.

mpmath provides arbitrary-precision zeta. Default precision is 30 digits.
"""

from __future__ import annotations

import os
import sys
from math import log

import mpmath


HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ALGEBRA = os.path.join(REPO, 'algebra')
if ALGEBRA not in sys.path:
    sys.path.insert(0, ALGEBRA)
from predict_q import q_general


mpmath.mp.dps = 30


# --------------------------------------------------------------------------
# zeta_{M_n}(s) and its log / log-derivative
# --------------------------------------------------------------------------

def zeta_mn(n: int, s) -> mpmath.mpc:
    """zeta_{M_n}(s) = 1 + n^{-s} zeta(s). Pole at s=1 only (residue 1/n)."""
    s = mpmath.mpc(s)
    return 1 + mpmath.power(n, -s) * mpmath.zeta(s)


def log_zeta_mn(n: int, s) -> mpmath.mpc:
    return mpmath.log(zeta_mn(n, s))


def zeta_mn_prime(n: int, s, h=None) -> mpmath.mpc:
    """ζ'_{M_n}(s) by symmetric difference."""
    if h is None:
        h = mpmath.mpf('1e-12')
    s = mpmath.mpc(s)
    return (zeta_mn(n, s + h) - zeta_mn(n, s - h)) / (2 * h)


def log_deriv_mn(n: int, s) -> mpmath.mpc:
    """-ζ'_{M_n}(s) / ζ_{M_n}(s). Mellin transform of the signed Λ_{M_n}."""
    return -zeta_mn_prime(n, s) / zeta_mn(n, s)


# --------------------------------------------------------------------------
# Counting functions on the arithmetic side
# --------------------------------------------------------------------------

def n_mn(n: int, x) -> int:
    """Set count: #{m in M_n : m <= x} = 1 + floor(x/n) for x >= 1."""
    if x < 1:
        return 0
    return 1 + int(x) // n


def psi_mn(n: int, x: int) -> float:
    """Signed Mangoldt sum.

    psi_{M_n}(x) := sum_{m in M_n, m <= x} Q_n(m) log m
                  = sum_{j=1}^{x//n} q_general(n, 1, j) * log(j*n)

    Q_n is supported on nZ_{>0} (so m = jn), and q_general(n, 1, j) =
    Q_n(n * j) handles the n-adic-height inflation when j is divisible
    by n's primes.
    """
    if x < n:
        return 0.0
    total = 0.0
    j_max = int(x) // n
    for j in range(1, j_max + 1):
        m = j * n
        if m > x:
            break
        q = float(q_general(n, 1, j))
        if q != 0:
            total += q * log(m)
    return total


def lambda_mn(n: int, m: int) -> float:
    """Single-point Mangoldt analog Λ_{M_n}(m) = Q_n(m) log m.

    Returns 0 unless m is in nZ_{>0}.
    """
    if m < n or m % n != 0:
        return 0.0
    j = m // n
    q = float(q_general(n, 1, j))
    return q * log(m)


# --------------------------------------------------------------------------
# Self-check: spot evaluations at canonical s
# --------------------------------------------------------------------------

def _self_check():
    print('zeta_mn self-check')
    print('-' * 60)
    for n in (2, 3, 5, 6, 10):
        z0 = zeta_mn(n, mpmath.mpf('0'))
        # zeta(0) = -1/2 so zeta_mn(n, 0) = 1 - 1/2 = 1/2 exactly.
        ok_at_0 = abs(z0 - mpmath.mpf('0.5')) < mpmath.mpf('1e-20')
        # Near s=1: expect simple pole with residue 1/n. So
        # (s-1) zeta_mn(n, s) -> 1/n as s -> 1.
        eps = mpmath.mpf('1e-8')
        residue_est = eps * zeta_mn(n, 1 + eps)
        ok_residue = abs(residue_est - mpmath.mpf(1) / n) < mpmath.mpf('1e-6')
        print(f'  n={n:>3}: zeta_mn(0) = {float(z0.real):+.6f} '
              f'(expect 0.5)  [{"OK" if ok_at_0 else "FAIL"}]')
        print(f'         residue at s=1 ≈ {float(residue_est.real):+.6f} '
              f'(expect {1/n:.6f})  [{"OK" if ok_residue else "FAIL"}]')

    print()
    print('psi_mn vs predict_q sanity at small x:')
    for n in (2, 3):
        # psi_mn(n, 4n) = Q_n(n)·log(n) + Q_n(2n)·log(2n) + Q_n(3n)·log(3n) + Q_n(4n)·log(4n)
        psi = psi_mn(n, 4 * n)
        manual = sum(float(q_general(n, 1, j)) * log(j * n) for j in (1, 2, 3, 4))
        print(f'  n={n}: psi_mn({4*n}) = {psi:.6f}, manual = {manual:.6f}, '
              f'diff = {abs(psi - manual):.2e}')


if __name__ == '__main__':
    _self_check()
