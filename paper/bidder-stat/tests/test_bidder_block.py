"""
test_bidder_block.py — Tests for the period-only random-access wrapper.

Verifies the BidderBlock contract from core/API-PLAN.md:
- at(i) is the load-bearing primitive
- iteration is fresh and independent (no shared cursor)
- out-of-range raises ValueError, non-integer raises TypeError
- non-bytes key raises TypeError
- period range is [2, 2^32 - 1]; outside raises UnsupportedPeriodError
- no __next__ on the object, no reset()

Run: python3 tests/test_bidder_block.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'generator'))

from bidder_block import BidderBlock, UnsupportedPeriodError, MAX_PERIOD_V1


KEY = b'test key'


# =====================================================================
# Test 1: period property
# =====================================================================

def test_period_property():
    for P in [2, 3, 5, 8, 100, 1000, 65535]:
        B = BidderBlock(P, KEY)
        assert B.period == P, f"period mismatch: {B.period} != {P}"
        assert len(B) == P, f"len mismatch: {len(B)} != {P}"
    print("  Period property: OK")


# =====================================================================
# Test 2: permutation
# =====================================================================

def test_permutation_small():
    """For small P, [B.at(i) for i in range(P)] is a permutation of [0, P)."""
    for P in [2, 3, 5, 10, 100, 1000]:
        B = BidderBlock(P, KEY)
        out = sorted(B.at(i) for i in range(P))
        assert out == list(range(P)), (
            f"P={P}: not a permutation of [0, P)")
    # Spot check a larger one
    B = BidderBlock(10000, KEY)
    out = sorted(B.at(i) for i in range(10000))
    assert out == list(range(10000))
    print("  Permutation of [0, P) for small P: OK")


# =====================================================================
# Test 3: out-of-range raises ValueError
# =====================================================================

def test_out_of_range_raises_value_error():
    B = BidderBlock(100, KEY)
    for bad in [100, 101, -1, 2**40]:
        try:
            B.at(bad)
            assert False, f"at({bad}) should have raised ValueError"
        except ValueError:
            pass
    print("  at() out-of-range raises ValueError: OK")


# =====================================================================
# Test 4: non-integer index raises TypeError
# =====================================================================

def test_non_integer_index_raises_type_error():
    B = BidderBlock(100, KEY)
    for bad in [1.5, "3", None, [1], (2,)]:
        try:
            B.at(bad)
            assert False, f"at({bad!r}) should have raised TypeError"
        except TypeError:
            pass
    # Booleans are int subclasses in Python; True/False should pass
    # and behave as 1/0.
    assert B.at(True) == B.at(1)
    assert B.at(False) == B.at(0)
    print("  at() non-integer raises TypeError, bool accepted: OK")


# =====================================================================
# Test 5: non-bytes key raises TypeError
# =====================================================================

def test_non_bytes_key_raises_type_error():
    for bad in ["string", 12345, None, [1, 2, 3]]:
        try:
            BidderBlock(100, bad)
            assert False, f"BidderBlock(100, {bad!r}) should have raised TypeError"
        except TypeError:
            pass
    # bytes and bytearray are accepted
    BidderBlock(100, b"bytes key")
    BidderBlock(100, bytearray(b"bytearray key"))
    print("  Non-bytes key raises TypeError, bytes/bytearray accepted: OK")


# =====================================================================
# Test 6: period < 2 raises ValueError
# =====================================================================

def test_period_too_small_raises():
    for bad in [1, 0, -1, -100]:
        try:
            BidderBlock(bad, KEY)
            assert False, f"BidderBlock({bad}, ...) should have raised ValueError"
        except ValueError:
            pass
    print("  period < 2 raises ValueError: OK")


# =====================================================================
# Test 7: period > MAX_PERIOD_V1 raises UnsupportedPeriodError
# =====================================================================

def test_unsupported_period_raises():
    for bad in [MAX_PERIOD_V1 + 1, 1 << 33, 1 << 40]:
        try:
            BidderBlock(bad, KEY)
            assert False, (
                f"BidderBlock({bad}, ...) should have raised UnsupportedPeriodError")
        except UnsupportedPeriodError as e:
            assert str(e) == f"period {bad} exceeds maximum of {MAX_PERIOD_V1}"
    # UnsupportedPeriodError is a ValueError subclass — caller can catch either
    try:
        BidderBlock(MAX_PERIOD_V1 + 1, KEY)
    except ValueError:
        pass
    print("  period > MAX_PERIOD_V1 raises UnsupportedPeriodError: OK")


# =====================================================================
# Test 8: determinism under key
# =====================================================================

def test_determinism_under_key():
    B1 = BidderBlock(1000, b"deterministic")
    B2 = BidderBlock(1000, b"deterministic")
    for i in range(100):
        assert B1.at(i) == B2.at(i)
    assert list(B1) == list(B2)
    print("  Determinism under key: OK")


# =====================================================================
# Test 9: key sensitivity
# =====================================================================

def test_key_sensitivity():
    B1 = BidderBlock(1000, b"key one")
    B2 = BidderBlock(1000, b"key two")
    differ = any(B1.at(i) != B2.at(i) for i in range(100))
    assert differ, "Different keys produced identical first 100 outputs"
    print("  Key sensitivity: OK")


# =====================================================================
# Test 10: iter(B) is fresh each time
# =====================================================================

def test_iter_is_fresh():
    B = BidderBlock(100, KEY)
    it1 = iter(B)
    it2 = iter(B)
    # Advance it1 by 5
    for _ in range(5):
        next(it1)
    # it2 should still start from B.at(0)
    assert next(it2) == B.at(0)
    assert next(it2) == B.at(1)
    print("  iter(B) is fresh each call: OK")


# =====================================================================
# Test 11: iteration matches indexing
# =====================================================================

def test_iteration_matches_indexing():
    B = BidderBlock(500, KEY)
    via_iter = list(B)
    via_index = [B.at(i) for i in range(B.period)]
    assert via_iter == via_index
    print("  Iteration matches indexing: OK")


# =====================================================================
# Test 12: no __next__ on B itself
# =====================================================================

def test_no_next_on_object():
    """BidderBlock is iterable but not its own iterator. next(B)
    should raise TypeError. This locks in the iterator-model decision
    from core/API-PLAN.md.
    """
    B = BidderBlock(100, KEY)
    try:
        next(B)
        assert False, "next(B) should have raised TypeError"
    except TypeError:
        pass
    print("  next(B) raises TypeError (B is not its own iterator): OK")


# =====================================================================
# Test 13: no reset() method
# =====================================================================

def test_no_reset_method():
    B = BidderBlock(100, KEY)
    assert not hasattr(B, 'reset'), (
        "BidderBlock should not have a reset() method (no object-level cursor)")
    print("  No reset() method: OK")


# =====================================================================
# Test 14: cipher selection diagnostic
# =====================================================================

def test_cipher_selection_diagnostic():
    """Confirms .cipher reports the underlying mode. Not a correctness
    test — documents the selection rule from generator/bidder.py.
    """
    # Small period -> Feistel (cycle-walk ratio for Speck32 too high)
    small = BidderBlock(100, KEY)
    assert small.cipher == 'feistel', f"expected feistel, got {small.cipher!r}"
    # Period close to 2^32 -> Speck32 (tight fit)
    large = BidderBlock(MAX_PERIOD_V1, KEY)
    assert large.cipher == 'speck32', f"expected speck32, got {large.cipher!r}"
    print(f"  Cipher selection: small=feistel, large=speck32: OK")


# =====================================================================
# Entry point
# =====================================================================

if __name__ == '__main__':
    print("=== BidderBlock tests ===\n")

    test_period_property()
    test_permutation_small()
    test_out_of_range_raises_value_error()
    test_non_integer_index_raises_type_error()
    test_non_bytes_key_raises_type_error()
    test_period_too_small_raises()
    test_unsupported_period_raises()
    test_determinism_under_key()
    test_key_sensitivity()
    test_iter_is_fresh()
    test_iteration_matches_indexing()
    test_no_next_on_object()
    test_no_reset_method()
    test_cipher_selection_diagnostic()

    print("\nAll BidderBlock tests passed.")
