"""
test_api.py — Tests for core/api.py:fulfill.

Verifies the v1 orchestration layer from core/API-PLAN.md. fulfill is
a thin wrapper around BidderBlock; these tests confirm that the public
entry point validates correctly and that the returned object behaves
as a BidderBlock.

Run: python3 tests/test_api.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

from api import fulfill, BidderBlock, UnsupportedPeriodError, MAX_PERIOD_V1


KEY = b'api test key'


# =====================================================================
# Test 1: fulfill returns a BidderBlock with the requested period
# =====================================================================

def test_fulfill_returns_block_with_period():
    for P in [2, 100, 1000, 65535, MAX_PERIOD_V1]:
        B = fulfill(P, KEY)
        assert isinstance(B, BidderBlock)
        assert B.period == P
    print("  fulfill returns BidderBlock with requested period: OK")


# =====================================================================
# Test 2: fulfill rejects period < 2
# =====================================================================

def test_fulfill_rejects_small_period():
    for bad in [1, 0, -1, -5]:
        try:
            fulfill(bad, KEY)
            assert False, f"fulfill({bad}, ...) should have raised ValueError"
        except ValueError:
            pass
    print("  fulfill rejects period < 2 with ValueError: OK")


# =====================================================================
# Test 3: fulfill rejects unsupported period
# =====================================================================

def test_fulfill_rejects_unsupported_period():
    try:
        fulfill(MAX_PERIOD_V1 + 1, KEY)
        assert False, "fulfill(MAX_PERIOD_V1 + 1, ...) should have raised"
    except UnsupportedPeriodError:
        pass
    try:
        fulfill(1 << 40, KEY)
        assert False, "fulfill(1<<40, ...) should have raised"
    except UnsupportedPeriodError:
        pass
    print("  fulfill rejects unsupported period: OK")


# =====================================================================
# Test 4: fulfill rejects non-integer period
# =====================================================================

def test_fulfill_rejects_non_integer_period():
    for bad in ["100", 1.5, None, [100]]:
        try:
            fulfill(bad, KEY)
            assert False, f"fulfill({bad!r}, ...) should have raised TypeError"
        except TypeError:
            pass
    print("  fulfill rejects non-integer period with TypeError: OK")


# =====================================================================
# Test 5: fulfill rejects non-bytes key
# =====================================================================

def test_fulfill_rejects_non_bytes_key():
    for bad in ["string key", 12345, None]:
        try:
            fulfill(100, bad)
            assert False, f"fulfill(100, {bad!r}) should have raised TypeError"
        except TypeError:
            pass
    print("  fulfill rejects non-bytes key with TypeError: OK")


# =====================================================================
# Test 6: returned object behaves as a BidderBlock
# =====================================================================

def test_returned_object_smoke():
    B = fulfill(50, KEY)
    # Random access
    assert 0 <= B.at(0) < 50
    assert 0 <= B.at(49) < 50
    # Iteration
    out = list(B)
    assert len(out) == 50
    assert sorted(out) == list(range(50))
    # len
    assert len(B) == 50
    # period
    assert B.period == 50
    print("  Returned object behaves as BidderBlock: OK")


# =====================================================================
# Entry point
# =====================================================================

if __name__ == '__main__':
    print("=== api.fulfill tests ===\n")

    test_fulfill_returns_block_with_period()
    test_fulfill_rejects_small_period()
    test_fulfill_rejects_unsupported_period()
    test_fulfill_rejects_non_integer_period()
    test_fulfill_rejects_non_bytes_key()
    test_returned_object_smoke()

    print("\nAll api tests passed.")
