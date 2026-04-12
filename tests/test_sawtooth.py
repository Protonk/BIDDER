"""
test_sawtooth.py — Tests for core/sawtooth.py:NPrimeSequence.

Verifies the deterministic n-prime sequence against the brute-force
enumerator in acm_core, locks in the interface-shape contract, and
spot-checks astronomical K.

Run: sage -python tests/test_sawtooth.py
     (acm_core imports numpy; NPrimeSequence itself needs only stock python3)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

from sawtooth import NPrimeSequence


# =====================================================================
# Cross-check against brute-force acm_n_primes
# =====================================================================

def test_at_matches_acm_n_primes():
    """at(K) for K in range(count) must equal acm_n_primes(n, count)."""
    from acm_core import acm_n_primes
    checked = 0
    for n in range(2, 13):
        for count in [1, 5, 50]:
            S = NPrimeSequence(n, count)
            expected = acm_n_primes(n, count)
            actual = [S.at(K) for K in range(count)]
            assert actual == expected, (
                f"n={n} count={count}: mismatch at "
                f"{next(i for i, (a, e) in enumerate(zip(actual, expected)) if a != e)}")
            checked += 1
    print(f"  at(K) matches acm_n_primes ({checked} configurations): OK")


# =====================================================================
# Construction validation
# =====================================================================

def test_n_type_error():
    for bad in [2.0, "3", None, [2]]:
        try:
            NPrimeSequence(bad, 10)
            assert False, f"NPrimeSequence({bad!r}, 10) should raise TypeError"
        except TypeError:
            pass
    print("  n type error: OK")

def test_n_value_error():
    for bad in [1, 0, -1]:
        try:
            NPrimeSequence(bad, 10)
            assert False, f"NPrimeSequence({bad}, 10) should raise ValueError"
        except ValueError as e:
            assert str(e) == "n must be >= 2"
    print("  n value error (n < 2): OK")

def test_count_type_error():
    for bad in [1.0, "5", None]:
        try:
            NPrimeSequence(3, bad)
            assert False, f"NPrimeSequence(3, {bad!r}) should raise TypeError"
        except TypeError:
            pass
    print("  count type error: OK")

def test_count_value_error():
    for bad in [0, -1, -100]:
        try:
            NPrimeSequence(3, bad)
            assert False, f"NPrimeSequence(3, {bad}) should raise ValueError"
        except ValueError:
            pass
    print("  count value error (count < 1): OK")


# =====================================================================
# at(K) boundary errors
# =====================================================================

def test_at_out_of_range():
    S = NPrimeSequence(5, 100)
    for bad in [-1, 100, 101, 2**40]:
        try:
            S.at(bad)
            assert False, f"at({bad}) should raise ValueError"
        except ValueError:
            pass
    print("  at(K) out-of-range: OK")

def test_at_type_error():
    S = NPrimeSequence(5, 100)
    for bad in [1.5, "3", None]:
        try:
            S.at(bad)
            assert False, f"at({bad!r}) should raise TypeError"
        except TypeError:
            pass
    # bool passes (int subclass with __index__)
    assert S.at(True) == S.at(1)
    assert S.at(False) == S.at(0)
    print("  at(K) type error, bool accepted: OK")


# =====================================================================
# Properties
# =====================================================================

def test_properties():
    S = NPrimeSequence(7, 50)
    assert S.n == 7
    assert S.count == 50
    assert S.period == 50
    assert len(S) == 50
    assert repr(S) == "NPrimeSequence(n=7, count=50)"
    print("  Properties: OK")


# =====================================================================
# Iteration
# =====================================================================

def test_iteration_matches_indexing():
    S = NPrimeSequence(3, 100)
    assert list(S) == [S.at(K) for K in range(100)]
    print("  Iteration matches indexing: OK")

def test_iter_is_fresh():
    S = NPrimeSequence(3, 50)
    it1 = iter(S)
    it2 = iter(S)
    for _ in range(5):
        next(it1)
    assert next(it2) == S.at(0), "iter not fresh"
    print("  iter(S) is fresh each call: OK")

def test_no_next_on_object():
    S = NPrimeSequence(3, 10)
    try:
        next(S)
        assert False, "next(S) should raise TypeError"
    except TypeError:
        pass
    print("  next(S) raises TypeError: OK")

def test_no_reset():
    S = NPrimeSequence(3, 10)
    assert not hasattr(S, 'reset')
    print("  No reset() method: OK")


# =====================================================================
# Determinism
# =====================================================================

def test_determinism():
    S1 = NPrimeSequence(5, 100)
    S2 = NPrimeSequence(5, 100)
    assert list(S1) == list(S2)
    print("  Determinism: OK")


# =====================================================================
# Astronomical K spot check
# =====================================================================

def test_astronomical_K():
    """NPrimeSequence(2, 2**40) then at(2**40 - 1) should produce
    the same value as the Hardy closed form in core/hardy_sidestep.py.
    """
    import sys as _sys
    _sys.set_int_max_str_digits(1_000_000)
    S = NPrimeSequence(2, 2**40)
    p = S.at(2**40 - 1)
    # The (2^40)-th 2-prime: q, r = divmod(2^40 - 1, 1) = (2^40 - 1, 0)
    # result = 2 * (2*(2^40 - 1) + 0 + 1) = 2 * (2^41 - 1) = 2^42 - 2
    expected = 2**42 - 2
    assert p == expected, f"got {p}, expected {expected}"
    assert p.bit_length() == 42
    print(f"  Astronomical K (2^40): {p.bit_length()}-bit result: OK")


# =====================================================================
# Entry point
# =====================================================================

if __name__ == '__main__':
    print("=== NPrimeSequence tests ===\n")

    test_at_matches_acm_n_primes()
    test_n_type_error()
    test_n_value_error()
    test_count_type_error()
    test_count_value_error()
    test_at_out_of_range()
    test_at_type_error()
    test_properties()
    test_iteration_matches_indexing()
    test_iter_is_fresh()
    test_no_next_on_object()
    test_no_reset()
    test_determinism()
    test_astronomical_K()

    print("\nAll NPrimeSequence tests passed.")
