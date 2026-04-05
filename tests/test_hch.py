"""
test_hch.py — Tests for the HCH block generator.

Verifies exact uniformity, key sensitivity, determinism, auto-selection,
and full-period bijection for multiple base/digit-class combinations.

Run: python3 -m pytest tests/test_hch.py -v
  or: python3 tests/test_hch.py
"""

import collections
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'generator'))

from hch_speck import HCHSpeck


# =====================================================================
# Exact uniformity
# =====================================================================

def _check_exact_uniformity(base, digit_class, key=b'test'):
    """Generate a full period and verify every digit appears equally."""
    gen = HCHSpeck(base=base, digit_class=digit_class, key=key)
    output = gen.generate(gen.period)
    counts = collections.Counter(output)
    expected = gen.period // gen.alphabet_size
    for d in range(1, base):
        assert counts[d] == expected, (
            f"base={base} d={digit_class}: digit {d} count {counts[d]} != {expected}")
    return gen


def test_uniformity_base10_d2():
    """base 10, d=2: block [10,99], period 90, 10 per digit."""
    gen = _check_exact_uniformity(10, 2)
    print(f"  {gen}: exact uniform OK")


def test_uniformity_base10_d3():
    """base 10, d=3: block [100,999], period 900, 100 per digit."""
    gen = _check_exact_uniformity(10, 3)
    print(f"  {gen}: exact uniform OK")


def test_uniformity_base10_d4():
    """base 10, d=4: block [1000,9999], period 9000, 1000 per digit."""
    gen = _check_exact_uniformity(10, 4)
    print(f"  {gen}: exact uniform OK")


def test_uniformity_base16_d2():
    """base 16, d=2: block [16,255], period 240, 16 per digit."""
    gen = _check_exact_uniformity(16, 2)
    print(f"  {gen}: exact uniform OK")


def test_uniformity_base256_d2():
    """base 256, d=2: block [256,65535], period 65280, 256 per symbol."""
    gen = _check_exact_uniformity(256, 2)
    print(f"  {gen}: exact uniform OK")


def test_uniformity_base7_d3():
    """Odd base: base 7, d=3, period 294."""
    gen = _check_exact_uniformity(7, 3)
    print(f"  {gen}: exact uniform OK")


def test_uniformity_base2_d10():
    """Binary: base 2, d=10, period 512. One symbol, trivially uniform."""
    gen = _check_exact_uniformity(2, 10)
    print(f"  {gen}: exact uniform OK")


# =====================================================================
# Key sensitivity
# =====================================================================

def test_different_keys_different_output():
    """Same params, different keys -> different sequences."""
    gen_a = HCHSpeck(base=10, digit_class=3, key=b'alpha')
    gen_b = HCHSpeck(base=10, digit_class=3, key=b'bravo')
    out_a = gen_a.generate(50)
    out_b = gen_b.generate(50)
    assert out_a != out_b, "Different keys produced identical output"
    print("  Key sensitivity: OK")


def test_same_key_same_output():
    """Same params + same key -> identical sequences."""
    gen_a = HCHSpeck(base=10, digit_class=3, key=b'same')
    gen_b = HCHSpeck(base=10, digit_class=3, key=b'same')
    assert gen_a.generate(100) == gen_b.generate(100)
    print("  Same key determinism: OK")


# =====================================================================
# Reset and determinism
# =====================================================================

def test_reset():
    """Reset returns the generator to the start of the period."""
    gen = HCHSpeck(base=10, digit_class=3, key=b'reset test')
    first = gen.generate(50)
    gen.reset()
    second = gen.generate(50)
    assert first == second, "Reset did not reproduce output"
    print("  Reset: OK")


def test_period_wraparound():
    """Generating past the period wraps back to the start."""
    gen = HCHSpeck(base=10, digit_class=2, key=b'wrap')
    first_period = gen.generate(gen.period)
    second_period = gen.generate(gen.period)
    assert first_period == second_period, "Period wraparound failed"
    print("  Period wraparound: OK")


# =====================================================================
# Auto-selection
# =====================================================================

def test_auto_selects_speck32():
    """Small blocks use Speck32."""
    gen = HCHSpeck(base=10, digit_class=2, key=b'test')
    assert gen.block_bits == 32
    print(f"  Auto-select Speck32: OK ({gen})")


def test_auto_selects_speck48():
    """Blocks near 2^32 step up to Speck48."""
    gen = HCHSpeck(base=65536, digit_class=3, key=b'test')
    assert gen.block_bits == 48
    print(f"  Auto-select Speck48: OK ({gen})")


def test_auto_selects_speck64():
    """Blocks near 2^48 step up to Speck64."""
    gen = HCHSpeck(base=10, digit_class=15, key=b'test')
    assert gen.block_bits == 64
    print(f"  Auto-select Speck64: OK ({gen})")


def test_feistel_fallback():
    """Small blocks fall back to Feistel when cycle-walk ratio is too high."""
    gen = HCHSpeck(base=10, digit_class=2, key=b'small')
    # block_size=90, Speck32=2^32, ratio ~47M -> must use feistel
    assert gen._mode == 'feistel', f"Expected feistel, got {gen._mode}"
    # But it still produces exact uniformity
    _check_exact_uniformity(10, 2, key=b'small')
    print(f"  Feistel fallback: OK ({gen})")


def test_speck_mode_tight_fit():
    """Tight-fit blocks use Speck directly."""
    gen = HCHSpeck(base=65536, digit_class=2, key=b'tight')
    # block_size ~2^32, Speck32 block = 2^32, ratio ~1.00002
    assert gen._mode == 'speck', f"Expected speck, got {gen._mode}"
    print(f"  Speck tight fit: OK ({gen})")


# =====================================================================
# Output range
# =====================================================================

def test_output_range():
    """Every output is in {1, ..., base-1}."""
    gen = HCHSpeck(base=100, digit_class=2, key=b'range test')
    output = gen.generate(gen.period)
    for v in output:
        assert 1 <= v <= 99, f"Out of range: {v}"
    print(f"  Output range [1..99]: OK")


# =====================================================================
# Bijection (full period)
# =====================================================================

def test_bijection_small():
    """
    The permutation is a bijection: full period output has no repeated
    (counter, output) pairs, and the leading-digit counts are exact.
    """
    gen = HCHSpeck(base=10, digit_class=3, key=b'bijection')
    # Track the permuted indices directly
    seen = set()
    for i in range(gen.period):
        idx = gen._permute(i)
        assert idx not in seen, f"Collision at counter={i}, permuted={idx}"
        seen.add(idx)
    assert len(seen) == gen.period
    print(f"  Bijection (period {gen.period}): OK")


# =====================================================================
# Iterator protocol
# =====================================================================

def test_iterator():
    """Generator supports for-loop iteration over one period."""
    gen = HCHSpeck(base=10, digit_class=2, key=b'iter')
    output = list(gen)
    assert len(output) == gen.period
    counts = collections.Counter(output)
    expected = gen.period // gen.alphabet_size
    for d in range(1, 10):
        assert counts[d] == expected
    print(f"  Iterator protocol: OK")


# =====================================================================
# Properties
# =====================================================================

def test_properties():
    """Period and alphabet_size report correctly."""
    gen = HCHSpeck(base=10, digit_class=3, key=b'props')
    assert gen.period == 900
    assert gen.alphabet_size == 9
    assert gen.block_start == 100
    assert gen.block_end == 999
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

    test_auto_selects_speck32()
    test_auto_selects_speck48()
    test_auto_selects_speck64()
    test_feistel_fallback()
    test_speck_mode_tight_fit()

    test_output_range()
    test_bijection_small()
    test_iterator()
    test_properties()

    print("\nAll HCH tests passed.")
