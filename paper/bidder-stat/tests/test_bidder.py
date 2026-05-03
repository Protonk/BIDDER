"""
test_bidder.py — Tests for the BIDDER block generator.

Verifies exact uniformity, key sensitivity, determinism, mode selection,
and full-period bijection for multiple base/digit-class combinations.

Tests apply to both the Python (bidder.py) and C (bidder.c) implementations.

Run: python3 tests/test_bidder.py
"""

import collections
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'generator'))

from coupler import Bidder


# =====================================================================
# Exact uniformity
# =====================================================================

def _check_exact_uniformity(base, digit_class, key=b'test'):
    """Generate a full period and verify every digit appears equally."""
    gen = Bidder(base=base, digit_class=digit_class, key=key)
    output = [gen.next() for _ in range(gen.period)]
    counts = collections.Counter(output)
    expected = gen.period // (base - 1)
    for d in range(1, base):
        assert counts[d] == expected, (
            f"base={base} d={digit_class}: digit {d} count {counts[d]} != {expected}")
    return gen


def test_uniformity_base10_d2():
    gen = _check_exact_uniformity(10, 2)
    print(f"  {gen}: exact uniform OK")

def test_uniformity_base10_d3():
    gen = _check_exact_uniformity(10, 3)
    print(f"  {gen}: exact uniform OK")

def test_uniformity_base10_d4():
    gen = _check_exact_uniformity(10, 4)
    print(f"  {gen}: exact uniform OK")

def test_uniformity_base16_d2():
    gen = _check_exact_uniformity(16, 2)
    print(f"  {gen}: exact uniform OK")

def test_uniformity_base256_d2():
    gen = _check_exact_uniformity(256, 2)
    print(f"  {gen}: exact uniform OK")

def test_uniformity_base7_d3():
    gen = _check_exact_uniformity(7, 3)
    print(f"  {gen}: exact uniform OK")

def test_uniformity_base2_d10():
    gen = _check_exact_uniformity(2, 10)
    print(f"  {gen}: exact uniform OK")


# =====================================================================
# Key sensitivity
# =====================================================================

def test_different_keys_different_output():
    gen_a = Bidder(base=10, digit_class=3, key=b'alpha')
    gen_b = Bidder(base=10, digit_class=3, key=b'bravo')
    out_a = [gen_a.next() for _ in range(50)]
    out_b = [gen_b.next() for _ in range(50)]
    assert out_a != out_b, "Different keys produced identical output"
    print("  Key sensitivity: OK")

def test_same_key_same_output():
    gen_a = Bidder(base=10, digit_class=3, key=b'same')
    gen_b = Bidder(base=10, digit_class=3, key=b'same')
    out_a = [gen_a.next() for _ in range(100)]
    out_b = [gen_b.next() for _ in range(100)]
    assert out_a == out_b
    print("  Same key determinism: OK")


# =====================================================================
# Reset and determinism
# =====================================================================

def test_reset():
    gen = Bidder(base=10, digit_class=3, key=b'reset test')
    first = [gen.next() for _ in range(50)]
    gen.reset()
    second = [gen.next() for _ in range(50)]
    assert first == second, "Reset did not reproduce output"
    print("  Reset: OK")

def test_period_wraparound():
    gen = Bidder(base=10, digit_class=2, key=b'wrap')
    first_period = [gen.next() for _ in range(gen.period)]
    second_period = [gen.next() for _ in range(gen.period)]
    assert first_period == second_period, "Period wraparound failed"
    print("  Period wraparound: OK")


# =====================================================================
# Mode selection
# =====================================================================

def test_feistel_fallback():
    """Small blocks use Feistel (cycle-walk ratio too high for Speck)."""
    gen = Bidder(base=10, digit_class=2, key=b'small')
    assert gen._mode == 1, f"Expected feistel (1), got {gen._mode}"
    _check_exact_uniformity(10, 2, key=b'small')
    print(f"  Feistel fallback: OK ({gen})")

def test_speck_mode_tight_fit():
    """Tight-fit blocks use Speck32 directly."""
    gen = Bidder(base=65536, digit_class=2, key=b'tight')
    assert gen._mode == 0, f"Expected speck32 (0), got {gen._mode}"
    print(f"  Speck tight fit: OK ({gen})")


# =====================================================================
# Output range
# =====================================================================

def test_output_range():
    gen = Bidder(base=100, digit_class=2, key=b'range test')
    for _ in range(gen.period):
        v = gen.next()
        assert 1 <= v <= 99, f"Out of range: {v}"
    print("  Output range [1..99]: OK")


# =====================================================================
# Bijection (full period)
# =====================================================================

def test_bijection_small():
    gen = Bidder(base=10, digit_class=3, key=b'bijection')
    seen = set()
    for i in range(gen.period):
        idx = gen._permute(i)
        assert idx not in seen, f"Collision at counter={i}, permuted={idx}"
        seen.add(idx)
    assert len(seen) == gen.period
    print(f"  Bijection (period {gen.period}): OK")


# =====================================================================
# Iterator protocol (Python-specific, language-required)
# =====================================================================

def test_iterator():
    gen = Bidder(base=10, digit_class=2, key=b'iter')
    output = list(gen)
    assert len(output) == gen.period
    counts = collections.Counter(output)
    expected = gen.period // 9
    for d in range(1, 10):
        assert counts[d] == expected
    print("  Iterator protocol: OK")


# =====================================================================
# Cross-check with C implementation
# =====================================================================

def test_cross_check_feistel():
    """Feistel-mode output must match C exactly."""
    gen = Bidder(base=10, digit_class=2, key=b'test')
    out = [gen.next() for _ in range(20)]
    expected = [5, 6, 5, 8, 3, 8, 7, 8, 9, 4, 5, 7, 7, 4, 3, 1, 3, 1, 5, 8]
    assert out == expected, f"Feistel cross-check: {out} != {expected}"

    gen2 = Bidder(base=10, digit_class=3, key=b'test')
    out2 = [gen2.next() for _ in range(20)]
    expected2 = [2, 3, 7, 6, 8, 3, 1, 3, 6, 7, 3, 1, 9, 9, 8, 1, 5, 2, 8, 3]
    assert out2 == expected2, f"Feistel cross-check: {out2} != {expected2}"
    print("  Cross-check (feistel): OK")

def test_cross_check_speck():
    """Speck-mode output must match C exactly."""
    gen = Bidder(base=65536, digit_class=2, key=b'speck parity')
    out = [gen.next() for _ in range(10)]
    expected = [13270, 65198, 24145, 34590, 8655, 22902, 22414, 22244, 30259, 20443]
    assert gen._mode == 0, f"Expected speck mode, got {gen._mode}"
    assert out == expected, f"Speck cross-check: {out} != {expected}"
    print("  Cross-check (speck): OK")

def test_cross_check_mode_boundary():
    """Mode-boundary case (base=8130, d=2) must match C."""
    gen = Bidder(base=8130, digit_class=2, key=b'boundary')
    out = [gen.next() for _ in range(10)]
    expected = [1277, 2420, 5041, 1546, 5039, 1560, 947, 108, 961, 3498]
    assert out == expected, f"Boundary cross-check: {out} != {expected}"
    print(f"  Cross-check (mode boundary, mode={gen._mode}): OK")


# =====================================================================
# at(i) — random access (parity work, see core/API-PLAN.md)
# =====================================================================

def test_at_matches_next_sequence():
    """at(i) for i in range(period) must equal the next() sequence
    from a fresh generator.
    """
    for base, d in [(10, 2), (10, 3), (16, 2), (7, 3)]:
        gen_seq = Bidder(base=base, digit_class=d, key=b'at-test')
        seq = [gen_seq.next() for _ in range(gen_seq.period)]
        gen_at = Bidder(base=base, digit_class=d, key=b'at-test')
        rand = [gen_at.at(i) for i in range(gen_at.period)]
        assert seq == rand, (
            f"base={base} d={d}: at(i) sequence diverges from next() sequence")
    print("  at(i) matches next() sequence: OK")

def test_at_is_stateless():
    """at(i) must not advance the counter; interleaving at() and
    next() must leave the next() sequence unchanged.
    """
    # Build the reference next() sequence on a fresh generator
    ref = Bidder(base=10, digit_class=3, key=b'stateless')
    expected = [ref.next() for _ in range(20)]

    # Now interleave at() and next() on a separate generator with the
    # same key. The next() outputs should still match the reference.
    gen = Bidder(base=10, digit_class=3, key=b'stateless')
    out = []
    for i in range(20):
        _ = gen.at(i * 7 % gen.period)
        _ = gen.at(0)
        out.append(gen.next())
    assert out == expected, "at(i) leaked into the next() sequence"
    print("  at(i) is stateless under interleaving: OK")

def test_at_out_of_range_raises():
    """at(i) must raise ValueError for i not in [0, period)."""
    gen = Bidder(base=10, digit_class=2, key=b'oor')
    for bad in [-1, gen.period, gen.period + 1, 2**40]:
        try:
            gen.at(bad)
            assert False, f"at({bad}) should have raised"
        except ValueError:
            pass
    print("  at(i) out-of-range raises ValueError: OK")

def test_at_non_integer_raises():
    """at(i) must raise TypeError at the API boundary for non-integer
    indices, not fall through into cipher internals.
    """
    gen = Bidder(base=10, digit_class=2, key=b'type')
    for bad in [1.5, "3", None, [1], (2,)]:
        try:
            gen.at(bad)
            assert False, f"at({bad!r}) should have raised TypeError"
        except TypeError:
            pass
    # bool is a subclass of int and should pass through
    assert gen.at(True) == gen.at(1)
    assert gen.at(False) == gen.at(0)
    print("  at(i) non-integer raises TypeError: OK")

def test_at_cross_check_feistel():
    """at(i) cross-check against the cached C output for feistel mode."""
    gen = Bidder(base=10, digit_class=2, key=b'test')
    out = [gen.at(i) for i in range(20)]
    expected = [5, 6, 5, 8, 3, 8, 7, 8, 9, 4, 5, 7, 7, 4, 3, 1, 3, 1, 5, 8]
    assert out == expected, f"at() feistel cross-check: {out} != {expected}"
    print("  at() cross-check (feistel): OK")

def test_at_cross_check_speck():
    """at(i) cross-check for Speck mode."""
    gen = Bidder(base=65536, digit_class=2, key=b'speck parity')
    out = [gen.at(i) for i in range(10)]
    expected = [13270, 65198, 24145, 34590, 8655, 22902, 22414, 22244, 30259, 20443]
    assert gen._mode == 0
    assert out == expected, f"at() speck cross-check: {out} != {expected}"
    print("  at() cross-check (speck): OK")


# =====================================================================
# Properties
# =====================================================================

def test_rejects_base_too_large():
    """base > 2^32 must be rejected (output is uint32)."""
    try:
        Bidder(base=2**32 + 1, digit_class=1, key=b'x')
        assert False, "Should have rejected base > 2^32"
    except ValueError:
        pass
    print("  Rejects base > 2^32: OK")

def test_properties():
    gen = Bidder(base=10, digit_class=3, key=b'props')
    assert gen.period == 900
    assert gen.block_start == 100
    assert gen.block_size == 900
    print("  Properties: OK")


# =====================================================================
# Entry point
# =====================================================================

if __name__ == '__main__':
    print("=== BIDDER generator tests ===\n")

    test_uniformity_base10_d2()
    test_uniformity_base10_d3()
    test_uniformity_base10_d4()
    test_uniformity_base16_d2()
    test_uniformity_base256_d2()
    test_uniformity_base7_d3()
    test_uniformity_base2_d10()

    test_different_keys_different_output()
    test_same_key_same_output()

    test_reset()
    test_period_wraparound()

    test_feistel_fallback()
    test_speck_mode_tight_fit()

    test_output_range()
    test_bijection_small()
    test_iterator()
    test_cross_check_feistel()
    test_cross_check_speck()
    test_cross_check_mode_boundary()

    test_at_matches_next_sequence()
    test_at_is_stateless()
    test_at_out_of_range_raises()
    test_at_non_integer_raises()
    test_at_cross_check_feistel()
    test_at_cross_check_speck()

    test_rejects_base_too_large()
    test_properties()

    print("\nAll BIDDER tests passed.")
