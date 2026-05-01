"""
predict_q.py — exact-rational implementation of the Q_n master expansion.

The master expansion (algebra/MASTER-EXPANSION.md):

    Q_n(m) = sum_{j=1}^{h} (-1)^{j-1}
             [ prod_{i} C(a_i (h - j) + t_i + j - 1, j - 1) ]
             * tau_j(k') / j

where m = n^h k, n = prod p_i^{a_i}, k = prod p_i^{t_i} k' with gcd(k', n) = 1,
and h = nu_n(m) is the n-adic height of m. Definitions in
algebra/OBJECTS.md.

Public entry points for Q values:

    q_value_by_class(shape, h, tau_sig)
        Conditional Q_n(n^h k) in the gcd(k, n) = 1 case. Depends only on
        the sorted-exponent shape of n and the sorted-exponent tau-signature
        of k. Returns Fraction.

    q_general(n, h, k)
        Full Q_n(n^h k) for any k >= 1 (no coprimality constraint).
        Handles overlap: writes k = (prod p_i^{t_i}) k' and absorbs
        any excess powers of n into the effective height. Returns Fraction.

Public entry points for the prime-row OGF (algebra/ROW-OGF.md):

    row_polynomial(p, k_prime)
        Coefficients of F(x; p, k') = sum_{h>=1} Q_p(p^h k') x^h.
        Polynomial of degree exactly Omega(k') for k_prime >= 2 coprime
        to p. Returns list[Fraction] of length Omega.

    row_polynomial_qe_closed(e)
        Coefficients from the closed form F(x; p, q^e) = (1 - (1-x)^e)/e.
        Independent of the master expansion; serves as cross-check.

    row_sum(p, k_prime)
        Closed form sum_{h>=1} Q_p(p^h k') = 1/e if k_prime = q^e for
        some prime q != p (single prime cofactor), else 0.

All values are exact (Python's fractions.Fraction; no SymPy, no floats).

Sanity anchors are in algebra/test_anchors.py (A1..A10). The canonical
h=5 (shape, tau_sig) matrix is rendered in
experiments/acm-champernowne/base10/q_distillery/q_h5_shape_tau_matrix.png
and frozen as anchor A2.
"""

from __future__ import annotations

from functools import lru_cache
from fractions import Fraction
from math import comb, gcd
from typing import List, Tuple


# --------------------------------------------------------------------------
# integer primitives
# --------------------------------------------------------------------------

@lru_cache(maxsize=None)
def factor_tuple(n: int) -> Tuple[Tuple[int, int], ...]:
    """Prime factorisation as ((p, e), ...) sorted by prime."""
    if n < 1:
        raise ValueError(f'factor_tuple expects n >= 1, got {n}')
    if n == 1:
        return ()
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


def shape_of(n: int) -> Tuple[int, ...]:
    """Sorted-descending tuple of n's prime exponents."""
    return tuple(sorted((e for _p, e in factor_tuple(n)), reverse=True))


def tau_sig_of(k: int) -> Tuple[int, ...]:
    """Sorted-descending tuple of k's prime exponents (= shape_of(k))."""
    return tuple(sorted((e for _p, e in factor_tuple(k)), reverse=True))


@lru_cache(maxsize=None)
def tau(j: int, x: int) -> int:
    """Ordered j-fold divisor count tau_j(x). tau_j(1) = 1; multiplicative."""
    if j < 1:
        raise ValueError(f'tau index j must be >= 1, got {j}')
    if x < 1:
        raise ValueError(f'tau argument must be >= 1, got {x}')
    if x == 1:
        return 1
    prod = 1
    for _p, e in factor_tuple(x):
        prod *= comb(e + j - 1, j - 1)
    return prod


def n_adic_height(n: int, m: int) -> int:
    """Largest h with n^h | m."""
    if n < 2 or m < 1:
        raise ValueError(f'n_adic_height needs n >= 2 and m >= 1, got n={n}, m={m}')
    h = 0
    while m % n == 0:
        h += 1
        m //= n
    return h


def decompose(n: int, k: int) -> Tuple[Tuple[Tuple[int, int], ...],
                                       Tuple[int, ...], int]:
    """Return (n_factors, t_tuple, k_prime) where k = prod p_i^{t_i} * k_prime
    with gcd(k_prime, n) = 1 and t_tuple aligned with n's prime list."""
    n_factors = factor_tuple(n)
    t_list = []
    k_prime = k
    for p, _a in n_factors:
        e = 0
        while k_prime % p == 0:
            e += 1
            k_prime //= p
        t_list.append(e)
    return n_factors, tuple(t_list), k_prime


# --------------------------------------------------------------------------
# master expansion
# --------------------------------------------------------------------------

def q_value_by_class(shape: Tuple[int, ...],
                     h: int,
                     tau_sig: Tuple[int, ...]) -> Fraction:
    """Q_n(n^h k) in the gcd(k, n) = 1 case, by class.

    shape    sorted-descending exponent tuple of n
    h        n-adic height (>= 1)
    tau_sig  sorted-descending exponent tuple of k (k coprime to n)
    """
    if h < 1:
        raise ValueError(f'h must be >= 1, got {h}')
    if not shape:
        raise ValueError('shape must be non-empty (n must have at least one prime factor)')
    total = Fraction(0)
    for j in range(1, h + 1):
        bin_prod = 1
        for a in shape:
            bin_prod *= comb(a * (h - j) + j - 1, j - 1)
        tau_j = 1
        for e in tau_sig:
            tau_j *= comb(e + j - 1, j - 1)
        sign = 1 if j % 2 == 1 else -1
        total += Fraction(sign * bin_prod * tau_j, j)
    return total


def q_general(n: int, h: int, k: int) -> Fraction:
    """Q_n(n^h k) for arbitrary n >= 2, h >= 0, k >= 1.

    If k carries any extra power of n's primes that conspire to make
    n^h k have a strictly higher n-adic height than h, that is still
    fine: the master expansion's binomial-product coefficient already
    accounts for the overlap exponents t_i. The sum runs to
    h_effective = h + nu_n(k), where the rank lemma forces the sum
    to terminate.
    """
    if n < 2:
        raise ValueError(f'q_general needs n >= 2, got {n}')
    if h < 0:
        raise ValueError(f'q_general needs h >= 0, got {h}')
    if k < 1:
        raise ValueError(f'q_general needs k >= 1, got {k}')
    if h == 0:
        return Fraction(0)

    n_factors, t_tuple, k_prime = decompose(n, k)

    # Effective height: nu_n(n^h k) = h + min over n's primes of t_i // a_i.
    nu_n_of_k = min(t // a for (_p, a), t in zip(n_factors, t_tuple))
    h_eff = h + nu_n_of_k

    total = Fraction(0)
    for j in range(1, h_eff + 1):
        bin_prod = 1
        for (_p, a), t_i in zip(n_factors, t_tuple):
            bin_prod *= comb(a * (h - j) + t_i + j - 1, j - 1)
        tau_j_kprime = tau(j, k_prime)
        sign = 1 if j % 2 == 1 else -1
        total += Fraction(sign * bin_prod * tau_j_kprime, j)
    return total


# --------------------------------------------------------------------------
# convenience: vectorised numeric Q over a (k) range at fixed n, h
# --------------------------------------------------------------------------

def q_row(n: int, h: int, k_max: int) -> list:
    """[Q_n(n^h * k) as float for k = 1..k_max].

    Mirrors the row layout of q_lattice_4000_h{5,6,7,8}.npy column index.
    """
    return [float(q_general(n, h, k)) for k in range(1, k_max + 1)]


# --------------------------------------------------------------------------
# Prime-row OGF
# --------------------------------------------------------------------------
#
# For prime p and k_prime >= 1 coprime to p, define
#
#     F(x; p, k') = sum_{h >= 1} Q_p(p^h k') * x^h.
#
# Theorem (algebra/ROW-OGF.md):
# - If k' = 1: F(x; p, 1) = -log(1 - x), with [x^h] F = 1/h. NOT polynomial.
# - If k' >= 2 coprime to p: F is a polynomial in x of degree exactly
#   Omega(k') (number of prime factors with multiplicity). The leading
#   coefficient is (-1)^(Omega-1) (Omega-1)! / prod e_i! (boundary value
#   in KERNEL-ZEROS.md (ii)).
#
# Closed form (single-prime-power cofactor):
#     F(x; p, q^e) = (1 - (1 - x)^e) / e,
#     [x^h] F = (-1)^(h-1) C(e, h) / e for h = 1..e.
#
# Closed form for the row sum F(1; p, k'):
#     F(1; p, k') = 1/e   if k' = q^e for some prime q != p (omega(k') = 1),
#                 = 0     if omega(k') >= 2.
# (Diverges for k' = 1; raises.)


def big_omega(k: int) -> int:
    """Number of prime factors of k with multiplicity (Big Omega)."""
    if k < 1:
        raise ValueError(f'big_omega expects k >= 1, got {k}')
    return sum(e for _p, e in factor_tuple(k))


def little_omega(k: int) -> int:
    """Number of distinct prime factors of k (lowercase omega)."""
    if k < 1:
        raise ValueError(f'little_omega expects k >= 1, got {k}')
    return len(factor_tuple(k))


def row_polynomial(p: int, k_prime: int) -> List[Fraction]:
    """Coefficients of F(x; p, k') = sum_{h>=1} Q_p(p^h k') x^h.

    Returns [c_1, c_2, ..., c_Omega] of exact Fractions, where c_h =
    Q_p(p^h k') and Omega = Omega(k_prime). The polynomial has degree
    exactly Omega; no coefficient at h > Omega is needed (kernel-zero
    band, KERNEL-ZEROS.md (i)).

    Requirements:
    - p prime (the OGF theorem in ROW-OGF.md is prime-n only;
      composite p admits cyclotomic-denominator OGFs that are not
      polynomial, see PROPOSED-CLOSED-FORMS.md Proposal 4)
    - k_prime >= 2
    - gcd(p, k_prime) = 1

    The k_prime = 1 case is excluded because F is then -log(1 - x), not
    polynomial. Use q_general(p, h, 1) directly for that case (returns 1/h).
    """
    if k_prime < 2:
        raise ValueError(
            f'row_polynomial requires k_prime >= 2 (k_prime=1 gives '
            f'F = -log(1-x), not polynomial); got {k_prime}')
    if p < 2:
        raise ValueError(f'row_polynomial requires p >= 2, got {p}')
    if len(factor_tuple(p)) != 1 or factor_tuple(p)[0][1] != 1:
        raise ValueError(
            f'row_polynomial requires p prime; got p={p} '
            f'(composite p has cyclotomic-denominator OGF, not '
            f'polynomial; see ROW-OGF.md and PROPOSED-CLOSED-FORMS.md '
            f'Proposal 4)')
    if gcd(p, k_prime) != 1:
        raise ValueError(
            f'row_polynomial requires gcd(p, k_prime) = 1; got '
            f'p={p}, k_prime={k_prime}')
    omega = big_omega(k_prime)
    return [q_general(p, h, k_prime) for h in range(1, omega + 1)]


def row_polynomial_qe_closed(e: int) -> List[Fraction]:
    """Coefficients of F(x; p, q^e) = (1 - (1 - x)^e) / e.

    Returns [c_1, ..., c_e] with c_h = (-1)^(h-1) C(e, h) / e.

    Independent of the master expansion: this is a direct evaluation of
    the closed form in algebra/ROW-OGF.md. Serves
    as a cross-check on row_polynomial(p, q^e) for any prime q != p.
    """
    if e < 1:
        raise ValueError(f'row_polynomial_qe_closed requires e >= 1, got {e}')
    return [Fraction((-1)**(h - 1) * comb(e, h), e) for h in range(1, e + 1)]


def row_sum(p: int, k_prime: int) -> Fraction:
    """Closed form for F(1; p, k') = sum_{h>=1} Q_p(p^h k').

    For k_prime >= 2 coprime to p:
        - If omega(k_prime) = 1, i.e., k_prime = q^e for some prime q
          (with q != p by coprimality), returns 1/e.
        - If omega(k_prime) >= 2, returns 0.

    The proof is direct from the master expansion plus the hockey-stick
    identity and the Stirling-like vanishing
    sum_{j=0}^Omega (-1)^j C(Omega, j) p(j) = 0 for any polynomial p of
    degree <= Omega - 1; the residue is p(0), where p(j) = tau_j(k')/j.
    The factor structure tau_j(k') = j^omega * (...) makes p(0) = 0
    for omega >= 2 and 1/e for omega = 1 (k' = q^e).

    Diverges for k_prime = 1 (sum is the harmonic series); raises.
    """
    if k_prime < 2:
        raise ValueError(
            f'row_sum diverges at k_prime = {k_prime} '
            f'(harmonic series); requires k_prime >= 2')
    if p < 2 or gcd(p, k_prime) != 1:
        raise ValueError(
            f'row_sum requires p >= 2 coprime to k_prime; got '
            f'p={p}, k_prime={k_prime}')
    factors = factor_tuple(k_prime)
    if len(factors) == 1:
        e = factors[0][1]
        return Fraction(1, e)
    return Fraction(0)


# --------------------------------------------------------------------------
# Verification entry point
# --------------------------------------------------------------------------
# The canonical anchor harness lives in test_anchors.py, which checks
# this module against the prime-row 1/h identity, the 8x6 matrix at
# h = 5, the universal h = 2 cliff, the master/class-form consistency,
# and the full payload_q_scan.csv. To avoid duplicate frozen tables
# drifting apart, running predict_q.py as a script delegates to that
# harness rather than maintaining a parallel expected-values dict.

if __name__ == '__main__':
    import test_anchors
    raise SystemExit(test_anchors.main())
