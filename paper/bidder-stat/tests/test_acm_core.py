"""
test_acm_core.py — Tests for the ACM-Champernowne core definitions.

Verifies n-prime generation, Champernowne encoding, exact uniformity
at block boundaries, first-digit extraction, and utilities.

Run: python3 tests/test_acm_core.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

import numpy as np
from acm_core import (
    acm_n_primes, acm_champernowne_real, acm_digit_count, acm_decompose,
    acm_champernowne_array, acm_running_mean,
    acm_first_digit, acm_first_digit_array, acm_benford_pmf
)


# =====================================================================
# n_primes — the definition is correct
# =====================================================================

def test_n1_ordinary_primes():
    """n=1 special case: should return ordinary primes."""
    assert acm_n_primes(1, 5) == [2, 3, 5, 7, 11]
    assert acm_n_primes(1, 10) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    print("  n=1 ordinary primes: OK")

def test_known_acm_n_primes():
    """Hand-verified n-primes for small n."""
    assert acm_n_primes(2, 5) == [2, 6, 10, 14, 18]
    assert acm_n_primes(3, 5) == [3, 6, 12, 15, 21]
    assert acm_n_primes(4, 5) == [4, 8, 12, 20, 24]
    assert acm_n_primes(5, 5) == [5, 10, 15, 20, 30]
    assert acm_n_primes(10, 5) == [10, 20, 30, 40, 50]
    print("  Known n-primes: OK")

def test_divisibility_contract():
    """Every n-prime must be divisible by n but not by n^2."""
    for n in range(2, 21):
        primes = acm_n_primes(n, 20)
        for p in primes:
            assert p % n == 0, f"n={n}: {p} not divisible by {n}"
            assert p % (n * n) != 0, f"n={n}: {p} divisible by {n}^2"
    print("  Divisibility contract (n=2..20, count=20): OK")

def test_square_boundary_exclusion():
    """n^2 must never appear as an n-prime."""
    for n in range(2, 51):
        primes = acm_n_primes(n, 100)
        assert n * n not in primes, f"n={n}: n^2={n*n} found in n-primes"
    print("  Square boundary exclusion (n=2..50): OK")

def test_first_n_minus_1_below_square():
    """First n-1 n-primes should be n, 2n, ..., (n-1)*n, all < n^2."""
    for n in range(2, 21):
        primes = acm_n_primes(n, n - 1)
        expected = [n * k for k in range(1, n)]
        assert primes == expected, f"n={n}: {primes} != {expected}"
        assert all(p < n * n for p in primes)
    # The n-th n-prime should be > n^2 (it's (n+1)*n)
    for n in range(2, 21):
        primes = acm_n_primes(n, n)
        assert primes[-1] == n * (n + 1), f"n={n}: {n}-th n-prime is {primes[-1]}, expected {n*(n+1)}"
        assert primes[-1] > n * n
    print("  First n-1 below n^2, n-th above: OK")

def test_monotonicity():
    """n-primes must be strictly increasing."""
    for n in range(1, 21):
        primes = acm_n_primes(n, 30)
        for i in range(1, len(primes)):
            assert primes[i] > primes[i - 1], (
                f"n={n}: non-monotone at index {i}: {primes[i-1]} >= {primes[i]}")
    print("  Monotonicity (n=1..20, count=30): OK")


# =====================================================================
# champernowne_real — the encoding is faithful
# =====================================================================

def test_known_champernowne():
    """Pin known value from docstring."""
    c = acm_champernowne_real(2, 5)
    assert c == 1.26101418, f"C(2,5) = {c}, expected 1.26101418"
    print("  Known Champernowne real: OK")

def test_first_n_prime_is_n():
    """For n >= 2, the first n-prime is n itself."""
    for n in range(2, 1000):
        assert acm_n_primes(n, 1) == [n], (
            f"n={n}: first n-prime is {acm_n_primes(n, 1)[0]}, expected {n}")
    print("  First n-prime is n (n=2..999): OK")

def test_leading_digit_preservation():
    """Leading digit of first n-prime equals leading digit of n.

    This is the property the BIDDER generator relies on: the first
    n-prime carries the leading digit of n, so the leading-digit
    distribution over a complete block is preserved through the
    n-prime construction. For n >= 2 this follows from the first
    n-prime being n itself. For n=1 (ordinary primes) the property
    does not hold (first 1-prime is 2, not 1).
    """
    for n in range(2, 10000):
        primes = acm_n_primes(n, 1)
        fd_prime = int(str(primes[0])[0])
        fd_n = int(str(n)[0])
        assert fd_prime == fd_n, (
            f"n={n}: leading digit of first n-prime ({primes[0]}) is {fd_prime}, "
            f"expected {fd_n}")
    print("  Leading digit preservation (n=2..9999): OK")

def test_range():
    """C(n) in [1.1, 2.0) for n >= 10."""
    for n in range(10, 1000):
        c = acm_champernowne_real(n)
        assert 1.1 <= c < 2.0, f"n={n}: C(n)={c} out of range [1.1, 2.0)"
    print("  Range [1.1, 2.0) for n >= 10: OK")


# =====================================================================
# Exact uniformity at block boundaries — the theorem
# =====================================================================

def _leading_digit(n):
    """Leading digit of a positive integer via positional notation."""
    return int(str(n)[0])

def _check_block_uniformity(n_max):
    """At n=1..n_max (where n_max = 10^d - 1), each leading digit appears equally.

    Uses string-based extraction (not first_digit) because this test
    verifies the mathematical property of positional notation, not the
    log10-based utility. See test_first_digit_integer_accuracy for the
    known float-precision issue with first_digit on exact integers.
    """
    counts = [0] * 10
    for n in range(1, n_max + 1):
        counts[_leading_digit(n)] += 1
    expected = n_max // 9
    for d in range(1, 10):
        assert counts[d] == expected, (
            f"n=1..{n_max}: digit {d} count {counts[d]} != {expected}")


def test_block_boundary_99():
    """Block boundary at 10^2 - 1: each digit appears exactly 11 times."""
    _check_block_uniformity(99)
    print("  Block boundary n=1..99: exact 11 each: OK")

def test_block_boundary_999():
    """Block boundary at 10^3 - 1: each digit appears exactly 111 times."""
    _check_block_uniformity(999)
    print("  Block boundary n=1..999: exact 111 each: OK")

def test_block_boundary_9999():
    """Block boundary at 10^4 - 1: each digit appears exactly 1111 times."""
    _check_block_uniformity(9999)
    print("  Block boundary n=1..9999: exact 1111 each: OK")


# =====================================================================
# Sieved block uniformity — see core/BLOCK-UNIFORMITY.md, sieved version
# =====================================================================

def _n_primes_in_block(n, b, d):
    """Direct enumeration of n-primes in [b^(d-1), b^d - 1]."""
    lo, hi = b ** (d - 1), b ** d - 1
    k_lo = (lo + n - 1) // n  # ceil(lo / n)
    k_hi = hi // n            # floor(hi / n)
    return [n * k for k in range(k_lo, k_hi + 1) if k % n != 0]


def _leading_digit_base(x, b):
    """Leading base-b digit of a positive integer."""
    while x >= b:
        x //= b
    return x


def _per_digit_counts(n, b, d):
    """Counts of each base-b leading digit (1..b-1) among n-primes in block."""
    counts = [0] * b
    for p in _n_primes_in_block(n, b, d):
        counts[_leading_digit_base(p, b)] += 1
    return counts[1:b]  # drop the unused 0 slot


def test_block_uniformity_sieved_sufficient():
    """Sufficient condition: if n^2 | b^(d-1), then n-primes in
    [b^(d-1), b^d - 1] have exactly uniform leading base-b digits,
    each appearing b^(d-1)*(n-1)/n^2 times.

    Sweeps b, n in [2, 10] and d in [1, 5] over all triples that
    satisfy the hypothesis. See core/BLOCK-UNIFORMITY.md, sieved
    version, for the proof.
    """
    checked = 0
    for b in range(2, 11):
        for n in range(2, 11):
            for d in range(1, 6):
                if (b ** (d - 1)) % (n * n) != 0:
                    continue
                expected = b ** (d - 1) * (n - 1) // (n * n)
                counts = _per_digit_counts(n, b, d)
                for j, c in enumerate(counts, start=1):
                    assert c == expected, (
                        f"(b,n,d)=({b},{n},{d}): leading digit {j} "
                        f"got count {c}, expected {expected}")
                checked += 1
    assert checked > 0, "no legal triples found in sweep — sweep range broken"
    print(f"  Sieved block uniformity (sufficient condition, {checked} triples): OK")


def test_block_uniformity_sieved_family_e():
    """Family E (second sufficient family): for d >= 2 and
    n in [b^(d-1), floor((b^d - 1)/(b-1))], the n-primes in the block
    are exactly {n, 2n, ..., (b-1)n}, one per leading base-b digit.
    Disjoint from the smooth family. See core/BLOCK-UNIFORMITY.md.
    """
    checked = 0
    for b in range(2, 11):
        for d in range(2, 6):
            L = b ** (d - 1)
            n_max = (b ** d - 1) // (b - 1)
            for n in range(L, n_max + 1):
                # Family E should give exactly uniform counts of 1 each
                counts = _per_digit_counts(n, b, d)
                for k, c in enumerate(counts, start=1):
                    assert c == 1, (
                        f"Family E (b,n,d)=({b},{n},{d}): leading digit {k} "
                        f"got count {c}, expected 1")
                # Family E should be disjoint from the smooth family
                assert (b ** (d - 1)) % (n * n) != 0, (
                    f"Family E (b,n,d)=({b},{n},{d}) unexpectedly satisfies "
                    f"the smooth condition n^2 | b^(d-1); families should be "
                    f"disjoint for d >= 2")
                checked += 1
    assert checked > 0, "no Family E triples found in sweep — sweep range broken"
    print(f"  Sieved block uniformity (Family E, {checked} triples): OK")


def test_block_uniformity_sieved_unconditional_witnesses():
    """Regression fixture for the canonical witness *outside* both
    sufficient families: (b, n, d) = (4, 5, 5). Smooth fails because
    25 does not divide 256. Family E fails because 5 < 256. The
    counts are nevertheless [41, 41, 41] — a "lucky cancellation"
    where strip-by-strip asymmetries in the multiples-of-5 and
    multiples-of-25 counts exactly cancel.

    The earlier (4, 4, 2) witness has been promoted to Family E
    coverage (it is the j = 0 case for (b, d) = (4, 2)) and is
    tested by test_block_uniformity_sieved_family_e.
    """
    b, n, d = 4, 5, 5
    expected_each, expected_total = 41, 123

    # Confirm both sufficient families really do fail
    assert (b ** (d - 1)) % (n * n) != 0, (
        f"({b},{n},{d}) accidentally satisfies the smooth condition")
    assert not (b ** (d - 1) <= n <= (b ** d - 1) // (b - 1)), (
        f"({b},{n},{d}) accidentally lies in Family E")

    counts = _per_digit_counts(n, b, d)
    total = sum(counts)
    assert total == expected_total, (
        f"(b,n,d)=({b},{n},{d}): total {total} != expected {expected_total}")
    for k, c in enumerate(counts, start=1):
        assert c == expected_each, (
            f"(b,n,d)=({b},{n},{d}): leading digit {k} "
            f"got count {c}, expected uniform {expected_each}")
    print("  Sieved block uniformity (unconditional witness (4,5,5)): OK")


def test_block_uniformity_sieved_spread_bound():
    """For any (b, n, d), the per-leading-digit n-prime count
    spread is at most 2. Proof in BLOCK-UNIFORMITY.md (each
    multiples-of-m count contributes at most 1 to the spread,
    and we use two of them: m=n and m=n^2). Sweeps the same
    cube as the sufficient-condition test.
    """
    worst = 0
    worst_at = None
    for b in range(2, 11):
        for n in range(2, 11):
            for d in range(1, 6):
                counts = _per_digit_counts(n, b, d)
                if not counts:
                    continue
                spread = max(counts) - min(counts)
                assert spread <= 2, (
                    f"(b,n,d)=({b},{n},{d}): spread {spread} exceeds "
                    f"the analytic bound of 2 (counts={counts})")
                if spread > worst:
                    worst = spread
                    worst_at = (b, n, d, counts)
    print(f"  Sieved block spread bound (<= 2 across sweep): OK "
          f"(worst seen: spread={worst} at {worst_at})")


# =====================================================================
# first_digit — the extraction works
# =====================================================================

def test_first_digit_powers_of_10():
    """Leading digit of powers of 10 is always 1."""
    for exp in range(6):
        assert acm_first_digit(10.0 ** exp) == 1, f"acm_first_digit(10^{exp}) != 1"
    print("  first_digit powers of 10: OK")

def test_first_digit_boundaries():
    """Digit transitions — values that don't hit the int-truncation bug."""
    assert acm_first_digit(1.999) == 1
    assert acm_first_digit(2.001) == 2
    assert acm_first_digit(9.001) == 9
    assert acm_first_digit(9.999) == 9
    assert acm_first_digit(0.0051) == 5
    assert acm_first_digit(123456.7) == 1
    # Exact integer mantissas (2.0, 5.0, etc.) are subject to the
    # known truncation bug — tested separately in test_first_digit_integer_accuracy.
    print("  first_digit boundaries: OK")

def test_first_digit_integer_accuracy():
    """first_digit must agree with string extraction on all integers 1..9999.

    See wonders/curiosity-retired-first-digit.md for the truncation bug this catches.
    """
    failures = []
    for n in range(1, 10000):
        fd = acm_first_digit(float(n))
        expected = int(str(n)[0])
        if fd != expected:
            failures.append(n)
    assert not failures, (
        f"first_digit mismatches on {len(failures)} integers: {failures[:10]}")
    print("  first_digit integer accuracy (n=1..9999): OK")

def test_first_digit_champernowne_accuracy():
    """first_digit is accurate on Champernowne reals (non-integer mantissas).

    The Champernowne reals never land on exact integer mantissas, so
    the truncation bug in first_digit does not affect them. All values
    are in [1.1, 2.0), so first_digit should return 1 for all of them.
    """
    arr = acm_champernowne_array(1000)
    for i, x in enumerate(arr):
        fd = acm_first_digit(x)
        assert fd == 1, (
            f"n={i+1}: acm_first_digit(C(n))={fd}, expected 1 (C(n)={x})")
    print("  first_digit on Champernowne reals: all 1 (correct): OK")

def test_first_digit_array_consistency():
    """Vectorized version must agree with scalar, element-wise."""
    arr = acm_champernowne_array(1000)
    vec = acm_first_digit_array(arr)
    scalar = np.array([acm_first_digit(x) for x in arr])
    assert np.array_equal(vec, scalar), "first_digit_array disagrees with first_digit"
    print("  first_digit_array consistency: OK")


# =====================================================================
# benford_pmf — the reference is right
# =====================================================================

def test_benford_sums_to_one():
    """Benford probabilities must sum to 1."""
    b = acm_benford_pmf()
    assert abs(sum(b) - 1.0) < 1e-12, f"Benford sum = {sum(b)}"
    print("  Benford sums to 1: OK")

def test_benford_known_value():
    """P(d=1) = log10(2)."""
    b = acm_benford_pmf()
    assert abs(b[0] - np.log10(2)) < 1e-15, f"Benford P(1) = {b[0]}"
    print("  Benford P(1) = log10(2): OK")

def test_benford_decreasing():
    """Benford probabilities are strictly decreasing."""
    b = acm_benford_pmf()
    for i in range(1, len(b)):
        assert b[i] < b[i - 1], f"Benford not decreasing at index {i}"
    print("  Benford strictly decreasing: OK")


# =====================================================================
# running_mean — the utility works
# =====================================================================

def test_running_mean_constant():
    """Running mean of a constant array is that constant."""
    arr = np.full(100, 3.7)
    rm = acm_running_mean(arr)
    assert np.allclose(rm, 3.7), "Running mean of constant failed"
    print("  Running mean constant: OK")

def test_running_mean_final():
    """Final element of running mean equals np.mean."""
    arr = acm_champernowne_array(500)
    rm = acm_running_mean(arr)
    assert abs(rm[-1] - np.mean(arr)) < 1e-12, "Running mean final != np.mean"
    print("  Running mean final value: OK")


# =====================================================================
# digit_count — consistent with encoding
# =====================================================================

def test_digit_count_known():
    """n=2, count=5: primes [2,6,10,14,18] -> 1+1+2+2+2 = 8 digits."""
    assert acm_digit_count(2, 5) == 8, f"acm_digit_count(2,5) = {acm_digit_count(2,5)}"
    print("  digit_count known value: OK")

def test_digit_count_consistency():
    """digit_count must equal total length of concatenated n-prime strings."""
    for n in range(1, 50):
        for count in [1, 5, 10]:
            primes = acm_n_primes(n, count)
            expected = sum(len(str(p)) for p in primes)
            actual = acm_digit_count(n, count)
            assert actual == expected, (
                f"n={n}, count={count}: digit_count={actual} != sum(len(str))={expected}")
    print("  digit_count consistency (n=1..49): OK")


# =====================================================================
# Champernowne precision — cross-language round-trip
#
# Both Python (float()) and C (strtod()) parse the same concatenated
# string as an IEEE 754 double. This test checks that the Python side
# produces the expected values across a range of string lengths — from
# well within double precision (4 fractional digits) through well
# past it (38 fractional digits). The C test suite checks the same
# values against its own output.
# =====================================================================

def test_champernowne_precision():
    """Cross-language precision: Python must match hardcoded C-checked values."""
    cases = [
        # (n, count, expected, frac_digits)
        (    2,  3,  1.261,                4),
        (    2,  5,  1.26101418,           8),
        (    5,  5,  1.51015203,           9),
        (   10,  5,  1.102030405,         10),
        (    1,  5,  1.235711,             6),
        (    1, 10,  1.2357111317192329,  16),
        (    7, 10,  1.7142128354256636,  19),
        (    3, 10,  1.3612152124303338,  18),
        (   99,  5,  1.99198297396495,    14),
        (  100,  5,  1.1002003004005,     15),
        (    2, 20,  1.2610141822263035,  38),
        ( 1000,  5,  1.1000200030004001, 20),
        (   50, 10,  1.501001502002503,  29),
    ]
    for n, count, expected, frac_digits in cases:
        c = acm_champernowne_real(n, count)
        tol = 0.0 if frac_digits <= 16 else 5e-16
        assert abs(c - expected) <= tol, (
            f"n={n} count={count}: got {c!r}, expected {expected!r} "
            f"(frac_digits={frac_digits})")
    print(f"  Champernowne precision ({len(cases)} cases): OK")


# =====================================================================
# Entry point
# =====================================================================

if __name__ == '__main__':
    print("=== ACM core tests ===\n")

    test_n1_ordinary_primes()
    test_known_acm_n_primes()
    test_divisibility_contract()
    test_square_boundary_exclusion()
    test_first_n_minus_1_below_square()
    test_monotonicity()

    test_known_champernowne()
    test_first_n_prime_is_n()
    test_leading_digit_preservation()
    test_range()

    test_block_boundary_99()
    test_block_boundary_999()
    test_block_boundary_9999()

    test_block_uniformity_sieved_sufficient()
    test_block_uniformity_sieved_family_e()
    test_block_uniformity_sieved_unconditional_witnesses()
    test_block_uniformity_sieved_spread_bound()

    test_first_digit_powers_of_10()
    test_first_digit_boundaries()
    test_first_digit_integer_accuracy()
    test_first_digit_champernowne_accuracy()
    test_first_digit_array_consistency()

    test_benford_sums_to_one()
    test_benford_known_value()
    test_benford_decreasing()

    test_running_mean_constant()
    test_running_mean_final()

    test_digit_count_known()
    test_digit_count_consistency()

    test_champernowne_precision()

    print("\nAll ACM core tests passed.")
