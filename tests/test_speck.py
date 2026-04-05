"""
test_speck.py — Tests for the Speck cipher family implementation.

Verifies all 9 test vectors from Appendix C of Beaulieu et al. (2013),
plus auto-selection logic.

Run: python3 -m pytest tests/test_speck.py -v
  or: python3 tests/test_speck.py
"""

import struct
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'generator'))

from speck import (
    speck_expand_key, speck_encrypt, speck_permute,
    select_variant, SPECK_ALL, SPECK_PARAMS,
)


# =====================================================================
# Test vectors from Appendix C
# =====================================================================
# Each entry: (block_bits, key_bits, key_bytes, pt_x, pt_y, ct_x, ct_y)

TEST_VECTORS = [
    # Speck32/64
    (32, 64,
     struct.pack('<4H', 0x0100, 0x0908, 0x1110, 0x1918),
     0x6574, 0x694c, 0xa868, 0x42f2),

    # Speck48/72
    (48, 72,
     bytes([0x00, 0x01, 0x02, 0x08, 0x09, 0x0a, 0x10, 0x11, 0x12]),
     0x20796c, 0x6c6172, 0xc049a5, 0x385adc),

    # Speck48/96
    (48, 96,
     bytes([0x00, 0x01, 0x02, 0x08, 0x09, 0x0a,
            0x10, 0x11, 0x12, 0x18, 0x19, 0x1a]),
     0x6d2073, 0x696874, 0x735e10, 0xb6445d),

    # Speck64/96
    (64, 96,
     struct.pack('<3I', 0x03020100, 0x0b0a0908, 0x13121110),
     0x74614620, 0x736e6165, 0x9f7952ec, 0x4175946c),

    # Speck64/128
    (64, 128,
     struct.pack('<4I', 0x03020100, 0x0b0a0908, 0x13121110, 0x1b1a1918),
     0x3b726574, 0x7475432d, 0x8c6fa548, 0x454e028b),

    # Speck96/96
    (96, 96,
     bytes([0x00, 0x01, 0x02, 0x03, 0x04, 0x05,
            0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d]),
     0x65776f68202c, 0x656761737520, 0x9e4d09ab7178, 0x62bdde8f79aa),

    # Speck96/144
    (96, 144,
     bytes([0x00, 0x01, 0x02, 0x03, 0x04, 0x05,
            0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d,
            0x10, 0x11, 0x12, 0x13, 0x14, 0x15]),
     0x656d6974206e, 0x69202c726576, 0x2bf31072228a, 0x7ae440252ee6),

    # Speck128/128
    (128, 128,
     struct.pack('<2Q', 0x0706050403020100, 0x0f0e0d0c0b0a0908),
     0x6c61766975716520, 0x7469206564616d20,
     0xa65d985179783265, 0x7860fedf5c570d18),

    # Speck128/256
    (128, 256,
     struct.pack('<4Q', 0x0706050403020100, 0x0f0e0d0c0b0a0908,
                        0x1716151413121110, 0x1f1e1d1c1b1a1918),
     0x65736f6874206e49, 0x202e72656e6f6f70,
     0x4109010405c0f53e, 0x4eeeb48d9c188f43),
]


def test_all_vectors():
    """Every Appendix C test vector must match."""
    for block_bits, key_bits, key, pt_x, pt_y, ct_x, ct_y in TEST_VECTORS:
        rk, n = speck_expand_key(key, block_bits, key_bits=key_bits)
        cx, cy = speck_encrypt(pt_x, pt_y, rk, n)
        label = f"Speck{block_bits}/{key_bits}"
        assert cx == ct_x and cy == ct_y, (
            f"{label}: got ({cx:#x}, {cy:#x}), "
            f"expected ({ct_x:#x}, {ct_y:#x})")
        print(f"  {label}: OK")


def test_auto_select():
    """select_variant picks the smallest Speck that covers the value."""
    assert select_variant(100) == 32
    assert select_variant(2**16) == 32
    assert select_variant(2**32) == 48
    assert select_variant(2**48) == 64
    assert select_variant(2**64) == 96
    assert select_variant(2**96) == 128
    print("  Auto-select: OK")


def test_permute_is_deterministic():
    """Same input + same key = same output."""
    key = b'determinism test'
    rk, n = speck_expand_key(key, 32)
    a = speck_permute(12345, rk, n)
    b = speck_permute(12345, rk, n)
    assert a == b
    print("  Determinism: OK")


def test_permute_is_injective():
    """No collisions on a sample of 10000 consecutive inputs."""
    key = b'injectivity test'
    rk, n = speck_expand_key(key, 32)
    outputs = set()
    for i in range(10000):
        out = speck_permute(i, rk, n)
        assert out not in outputs, f"Collision at i={i}"
        outputs.add(out)
    print("  Injectivity (10000 samples): OK")


def test_params_tables_consistent():
    """SPECK_PARAMS entries must exist in SPECK_ALL."""
    for block_bits, (n, m, alpha, beta, T, key_bits) in SPECK_PARAMS.items():
        key = (block_bits, key_bits)
        assert key in SPECK_ALL, f"{key} not in SPECK_ALL"
        assert SPECK_ALL[key] == (n, m, alpha, beta, T)
    print("  Param tables consistent: OK")


if __name__ == '__main__':
    print("=== Speck tests ===\n")
    test_all_vectors()
    test_auto_select()
    test_permute_is_deterministic()
    test_permute_is_injective()
    test_params_tables_consistent()
    print("\nAll Speck tests passed.")
