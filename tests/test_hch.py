"""
test_hch.py — Tests for the HCH block generator.

Verifies exact uniformity, key sensitivity, determinism, mode selection,
and full-period bijection for multiple base/digit-class combinations.

Tests apply to both the Python (hch.py) and C (hch.c) implementations.

Run: python3 tests/test_hch.py
"""

import collections
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'generator'))

from hch import HCH


# =====================================================================
# Exact uniformity
# =====================================================================

def _check_exact_uniformity(base, digit_class, key=b'test'):
    """Generate a full period and verify every digit appears equally."""
    gen = HCH(base=base, digit_class=digit_class, key=key)
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
    gen_a = HCH(base=10, digit_class=3, key=b'alpha')
    gen_b = HCH(base=10, digit_class=3, key=b'bravo')
    out_a = [gen_a.next() for _ in range(50)]
    out_b = [gen_b.next() for _ in range(50)]
    assert out_a != out_b, "Different keys produced identical output"
    print("  Key sensitivity: OK")

def test_same_key_same_output():
    gen_a = HCH(base=10, digit_class=3, key=b'same')
    gen_b = HCH(base=10, digit_class=3, key=b'same')
    out_a = [gen_a.next() for _ in range(100)]
    out_b = [gen_b.next() for _ in range(100)]
    assert out_a == out_b
    print("  Same key determinism: OK")


# =====================================================================
# Reset and determinism
# =====================================================================

def test_reset():
    gen = HCH(base=10, digit_class=3, key=b'reset test')
    first = [gen.next() for _ in range(50)]
    gen.reset()
    second = [gen.next() for _ in range(50)]
    assert first == second, "Reset did not reproduce output"
    print("  Reset: OK")

def test_period_wraparound():
    gen = HCH(base=10, digit_class=2, key=b'wrap')
    first_period = [gen.next() for _ in range(gen.period)]
    second_period = [gen.next() for _ in range(gen.period)]
    assert first_period == second_period, "Period wraparound failed"
    print("  Period wraparound: OK")


# =====================================================================
# Mode selection
# =====================================================================

def test_feistel_fallback():
    """Small blocks use Feistel (cycle-walk ratio too high for Speck)."""
    gen = HCH(base=10, digit_class=2, key=b'small')
    assert gen._mode == 1, f"Expected feistel (1), got {gen._mode}"
    _check_exact_uniformity(10, 2, key=b'small')
    print(f"  Feistel fallback: OK ({gen})")

def test_speck_mode_tight_fit():
    """Tight-fit blocks use Speck32 directly."""
    gen = HCH(base=65536, digit_class=2, key=b'tight')
    assert gen._mode == 0, f"Expected speck32 (0), got {gen._mode}"
    print(f"  Speck tight fit: OK ({gen})")


# =====================================================================
# Output range
# =====================================================================

def test_output_range():
    gen = HCH(base=100, digit_class=2, key=b'range test')
    for _ in range(gen.period):
        v = gen.next()
        assert 1 <= v <= 99, f"Out of range: {v}"
    print("  Output range [1..99]: OK")


# =====================================================================
# Bijection (full period)
# =====================================================================

def test_bijection_small():
    gen = HCH(base=10, digit_class=3, key=b'bijection')
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
    gen = HCH(base=10, digit_class=2, key=b'iter')
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

def test_cross_check():
    """Output must match the C implementation exactly."""
    gen = HCH(base=10, digit_class=2, key=b'test')
    out = [gen.next() for _ in range(20)]
    expected = [3, 8, 1, 2, 7, 1, 5, 4, 7, 4, 2, 5, 8, 7, 8, 9, 2, 9, 6, 7]
    assert out == expected, f"Cross-check failed: {out} != {expected}"

    gen2 = HCH(base=10, digit_class=3, key=b'test')
    out2 = [gen2.next() for _ in range(20)]
    expected2 = [1, 1, 8, 8, 3, 2, 9, 9, 3, 2, 2, 4, 5, 2, 3, 6, 7, 3, 6, 6]
    assert out2 == expected2, f"Cross-check failed: {out2} != {expected2}"
    print("  Cross-check with C: OK")


# =====================================================================
# Properties
# =====================================================================

def test_properties():
    gen = HCH(base=10, digit_class=3, key=b'props')
    assert gen.period == 900
    assert gen.block_start == 100
    assert gen.block_size == 900
    print("  Properties: OK")


# =====================================================================
# Entry point
# =====================================================================

if __name__ == '__main__':
    print("=== HCH generator tests ===\n")

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
    test_cross_check()
    test_properties()

    print("\nAll HCH tests passed.")
