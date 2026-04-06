"""
acm_core.py — Central definitions for the ACM-Champernowne process
===================================================================

This module defines the n-prime construction and its derived objects.
All other scripts import from here.

BQN companions (see guidance/BQN-AGENT.md):
    acm_n_primes          -> NPn2 (n >= 2 only)
    acm_champernowne_real -> parse of "1." ++ ChamDigits10
    acm_digit_count       -> DigitCount10
    acm_first_digit       -> LD10 (with +1e-9 guard)
    acm_benford_pmf       -> Benford10

DEFINITIONS
-----------

n-primality:
    A positive integer n >= 1 defining a multiplicative monoid nZ+ = {n, 2n, 3n, ...}.

n-prime:
    An irreducible element of the monoid nZ+.
    The element n*k is n-prime iff n does not divide k.
    Equivalently: multiples of n that are not multiples of n^2.
    For n >= 2, the first n-1 n-primes are n, 2n, 3n, ..., (n-1)n, all below n^2.
    The value n^2 = n*n is the first n-composite (the square boundary).

    For n = 1 (special case), n-primes are ordinary primes.

n-Champernowne real:
    Given the first K n-primes p_1, ..., p_K, concatenate their decimal
    representations after "1." to form a real number.
    Example: 2-primes [2, 6, 10, 14, 18] -> 1.26101418

    The n-Champernowne real encodes both number-theoretic content (primality
    of the monoid) and typographic cost (digit count) in a single scalar.

Decomposition (in log space):
    ln(n-Champernowne) decomposes into:
      - ln(n-primality) = ln(n)         [number-theoretic content, unbounded]
      - ln(n-digitfrac) = ln(digits/K)  [typographic cost, staircase]
      - ln(n-Champernowne)              [full encoding, bounded sawtooth]

    The running mean of the Champernowne reals moves toward ~1.55 = (10+1)/(2*10)
    but we conjecture it approaches from below and never arrives.

CONNECTION TO ARITHMETIC CONGRUENCE MONOIDS (ACMs)
--------------------------------------------------

The monoid nZ+ ∪ {1} is the simplest ACM, denoted M_{n,n} in the literature
(Geroldinger, Halter-Koch, Chapman, Baginski). Hilbert used M_{1,4} = {1,5,9,13,...}
to demonstrate non-unique factorization: 441 = 9 × 49 = 21 × 21.

For n >= 2, unique factorization fails in nZ+. Example in 2Z+:
    36 = 2 × 18 = 6 × 6

The n-Champernowne encoding is new: it turns the irreducible elements of each
ACM into a real number whose significand distribution is exactly uniform (not
Benford), and whose behavior under addition vs. multiplication reveals the
fundamental asymmetry between these operations.

KEY OBSERVATIONS
----------------

1. First-digit distribution of n-Champernowne reals is perfectly uniform (1/9 each),
   NOT Benford. This is the signature of the missing multiplicative structure.

2. Under multiplication, significands converge to Benford within ~10 operations.
   Under addition, significands cycle through digits forever (rolling shutter effect).

3. The sawtooth shape of ln(n-Champernowne) is ln(1+m) where m is the base-10
   mantissa of n. The running mean is the average error of the linear approximation
   — a base-10 cousin of the epsilon correction function ε(m) = log₂(1+m) - m.

4. The rolling shutter shear rate is log₁₀(μ) where μ ≈ 1.55 is the mean of the
   Champernowne reals. This is log₁₀(1 + m̄), the true log evaluated at the mean
   mantissa — the function whose computational cost ε measures.
"""

import numpy as np
from typing import List, Tuple


# ---------------------------------------------------------------------------
# Core generators
# ---------------------------------------------------------------------------

def acm_n_primes(n: int, count: int = 5) -> List[int]:
    """
    Return the first `count` n-primes.

    For n = 1: ordinary primes (trial division).
    For n >= 2: elements n*k where k is not divisible by n.

    These are the irreducible elements of the multiplicative monoid nZ+.
    Returns None on invalid input (n < 1 or count < 1).
    """
    if n < 1 or count < 1:
        return None

    if n == 1:
        primes = []
        candidate = 2
        while len(primes) < count:
            if all(candidate % p != 0 for p in primes):
                primes.append(candidate)
            candidate += 1
        return primes

    result = []
    k = 1
    while len(result) < count:
        if k % n != 0:
            result.append(n * k)
        k += 1
    return result


def acm_champernowne_real(n: int, count: int = 5) -> float:
    """
    Construct the n-Champernowne real from the first `count` n-primes.

    Concatenates the decimal representations of the n-primes after "1."
    Example: n=2, count=5 -> primes [2,6,10,14,18] -> 1.26101418

    Precision: the concatenated string is parsed as an IEEE 754 double
    via float(). Only the first ~16 significant decimal digits of the
    fractional part survive the conversion. For large n or large count,
    the trailing n-primes contribute nothing to the returned value.
    This caps effective precision at ~53 bits. The leading-digit
    property (which needs 1 digit) and the sawtooth structure (which
    needs ~10) are unaffected.

    Returns 0.0 on invalid input.
    """
    primes = acm_n_primes(n, count)
    if primes is None:
        return 0.0
    s = ''.join(str(p) for p in primes)
    return float('1.' + s)


def acm_digit_count(n: int, count: int = 5) -> int:
    """
    Total decimal digits used by the first `count` n-primes.
    This is the "typographic cost" of the Champernowne encoding.
    Returns -1 on invalid input.
    """
    primes = acm_n_primes(n, count)
    if primes is None:
        return -1
    return sum(len(str(p)) for p in primes)


# ---------------------------------------------------------------------------
# Decomposition in log space
# ---------------------------------------------------------------------------

def acm_decompose(n: int, count: int = 5) -> Tuple[float, float, float]:
    """
    Return (ln_champernowne, ln_primality, ln_digitfrac) for a given n.

    ln_champernowne = ln(n-Champernowne real)
    ln_primality    = ln(n)
    ln_digitfrac    = ln(total_digits / count)
    """
    c = acm_champernowne_real(n, count)
    d = acm_digit_count(n, count)
    return (
        np.log(c),
        np.log(n) if n > 0 else 0.0,
        np.log(d / count)
    )


# ---------------------------------------------------------------------------
# Batch computation (numpy convenience — no C equivalent)
# ---------------------------------------------------------------------------

def acm_champernowne_array(n_max: int, count: int = 5) -> np.ndarray:
    """
    Return array of Champernowne reals for n = 1, 2, ..., n_max.
    """
    return np.array([acm_champernowne_real(n, count) for n in range(1, n_max + 1)])


def acm_running_mean(arr: np.ndarray) -> np.ndarray:
    """
    Running (cumulative) mean of an array.
    """
    return np.cumsum(arr) / np.arange(1, len(arr) + 1)


# ---------------------------------------------------------------------------
# First-digit extraction
# ---------------------------------------------------------------------------

def acm_first_digit(x: float) -> int:
    """
    Extract the leading significant digit (1-9) of a positive number.
    Uses log10 to avoid string manipulation.
    Returns 0 for non-positive input.
    """
    if x <= 0:
        return 0
    l = np.log10(x)
    frac = l - np.floor(l)
    return min(int(10**frac + 1e-9), 9)


def acm_first_digit_array(arr: np.ndarray) -> np.ndarray:
    """
    Vectorized first-digit extraction for an array of positive numbers.
    """
    log_arr = np.log10(arr)
    frac = log_arr - np.floor(log_arr)
    return np.minimum((10**frac + 1e-9).astype(int), 9)


# ---------------------------------------------------------------------------
# Benford reference
# ---------------------------------------------------------------------------

def acm_benford_pmf() -> np.ndarray:
    """
    Return Benford's law probabilities for digits 1-9 as a numpy array.

    Computes log10(1 + 1/d) for d = 1..9 and returns all nine values
    at once. This is convenient for vectorized comparisons against
    observed digit distributions: subtract, square, sum, and you have
    a chi-squared-flavored distance from Benford in one expression.
    """
    return np.array([np.log10(1 + 1/d) for d in range(1, 10)])
