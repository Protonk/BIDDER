"""
speck.py — Full Speck family implementation (all block/key sizes)
================================================================

Implements all ten Speck variants from the NSA specification
(Beaulieu et al., 2013, Table 4.1 and Appendix C):

    Speck32/64, Speck48/72, Speck48/96, Speck64/96, Speck64/128,
    Speck96/96, Speck96/144, Speck128/128, Speck128/192, Speck128/256

The round function for all variants is:
    R_k(x, y) = ((ROR(x, a) + y) XOR k,  ROL(y, b) XOR (ROR(x, a) + y) XOR k)

with a=7, b=2 for Speck32/64, and a=8, b=3 for all others.

For HCH use, SPECK_PARAMS maps each block size to the *max-key*
variant. The full table is available as SPECK_ALL for testing.
"""

import struct
import hashlib


# =====================================================================
# Speck parameter tables
# =====================================================================
# Full table: keyed by (block_bits, key_bits)
# Value: (word_bits, key_words, alpha, beta, rounds)

SPECK_ALL = {
    (32,  64):  (16, 4, 7, 2, 22),
    (48,  72):  (24, 3, 8, 3, 22),
    (48,  96):  (24, 4, 8, 3, 23),
    (64,  96):  (32, 3, 8, 3, 26),
    (64, 128):  (32, 4, 8, 3, 27),
    (96,  96):  (48, 2, 8, 3, 28),
    (96, 144):  (48, 3, 8, 3, 29),
    (128, 128): (64, 2, 8, 3, 32),
    (128, 192): (64, 3, 8, 3, 33),
    (128, 256): (64, 4, 8, 3, 34),
}

# Max-key variants for each block size (used by HCH)
# Value: (word_bits, key_words, alpha, beta, rounds, key_bits)
SPECK_PARAMS = {
    32:  (16, 4, 7, 2, 22,  64),
    48:  (24, 4, 8, 3, 23,  96),
    64:  (32, 4, 8, 3, 27, 128),
    96:  (48, 3, 8, 3, 29, 144),
    128: (64, 4, 8, 3, 34, 256),
}


def _mask(n):
    """Bitmask for n-bit word."""
    return (1 << n) - 1


def _ror(x, r, n):
    """Right circular shift of n-bit word by r."""
    return ((x >> r) | (x << (n - r))) & _mask(n)


def _rol(x, r, n):
    """Left circular shift of n-bit word by r."""
    return ((x << r) | (x >> (n - r))) & _mask(n)


# =====================================================================
# Key expansion
# =====================================================================

def speck_expand_key(key_bytes, block_bits, key_bits=None):
    """
    Expand key bytes into round keys for the given Speck variant.

    Parameters
    ----------
    key_bytes : bytes
        Raw key material.
    block_bits : int
        Block size in bits (32, 48, 64, 96, or 128).
    key_bits : int or None
        Key size in bits. If None, uses the max-key variant from
        SPECK_PARAMS. If specified, looks up (block_bits, key_bits)
        in the full SPECK_ALL table.

    Returns (round_keys, word_bits) tuple.
    """
    if key_bits is not None:
        spec_key = (block_bits, key_bits)
        if spec_key not in SPECK_ALL:
            raise ValueError(f"Unknown Speck variant: Speck{block_bits}/{key_bits}. "
                             f"Valid: {sorted(SPECK_ALL.keys())}")
        n, m, alpha, beta, T = SPECK_ALL[spec_key]
    else:
        if block_bits not in SPECK_PARAMS:
            raise ValueError(f"Unsupported block size: {block_bits}. "
                             f"Use one of {sorted(SPECK_PARAMS.keys())}")
        n, m, alpha, beta, T, key_bits = SPECK_PARAMS[block_bits]

    mask = _mask(n)
    key_len = key_bits // 8

    # Pad or truncate key material
    kb = (key_bytes + b'\x00' * key_len)[:key_len]

    # Unpack key into m words of n bits each
    if n == 16:
        fmt = f'<{m}H'
    elif n == 24:
        # 24-bit words: unpack manually
        words = []
        for i in range(m):
            b0 = kb[i * 3] if i * 3 < len(kb) else 0
            b1 = kb[i * 3 + 1] if i * 3 + 1 < len(kb) else 0
            b2 = kb[i * 3 + 2] if i * 3 + 2 < len(kb) else 0
            words.append(b0 | (b1 << 8) | (b2 << 16))
        fmt = None
    elif n == 32:
        fmt = f'<{m}I'
    elif n == 48:
        # 48-bit words: unpack manually
        words = []
        for i in range(m):
            chunk = kb[i * 6:(i + 1) * 6].ljust(6, b'\x00')
            lo = struct.unpack('<I', chunk[:4])[0]
            hi = struct.unpack('<H', chunk[4:6])[0]
            words.append(lo | (hi << 32))
        fmt = None
    elif n == 64:
        fmt = f'<{m}Q'
    else:
        raise ValueError(f"Unsupported word size: {n}")

    if fmt is not None:
        words = list(struct.unpack(fmt, kb[:struct.calcsize(fmt)]))

    # Key schedule
    # k[0] = words[0], l = words[1:m]
    k = words[0]
    l = list(words[1:])

    round_keys = [k]
    for i in range(T - 1):
        li = l[i]
        li_new = (_ror(li, alpha, n) + k) & mask
        li_new ^= i
        k = _rol(k, beta, n) ^ li_new
        l.append(li_new)
        round_keys.append(k)

    return round_keys, n


# =====================================================================
# Encryption
# =====================================================================

def speck_encrypt(x, y, round_keys, n, alpha=None, beta=None):
    """
    Encrypt one block: two n-bit words (x, y) -> (x', y').
    """
    if alpha is None:
        alpha = 7 if n == 16 else 8
    if beta is None:
        beta = 2 if n == 16 else 3

    mask = _mask(n)
    for rk in round_keys:
        x = (_ror(x, alpha, n) + y) & mask
        x ^= rk
        y = _rol(y, beta, n) ^ x
    return x, y


def speck_block_to_int(x, y, n):
    """Pack two n-bit words into a 2n-bit integer."""
    return (x << n) | y


def int_to_speck_block(val, n):
    """Unpack a 2n-bit integer into two n-bit words."""
    mask = _mask(n)
    return (val >> n) & mask, val & mask


# =====================================================================
# Auto-select variant for a given block size requirement
# =====================================================================

def select_variant(max_value):
    """
    Choose the smallest Speck variant whose block covers max_value.

    Returns the block_bits parameter.
    """
    for block_bits in [32, 48, 64, 96, 128]:
        if max_value < (1 << block_bits):
            return block_bits
    raise ValueError(f"Value {max_value} exceeds Speck128 range (2^128)")


# =====================================================================
# Convenience: encrypt an integer index
# =====================================================================

def speck_permute(index, round_keys, n):
    """Encrypt an integer through the Speck permutation."""
    x, y = int_to_speck_block(index, n)
    x2, y2 = speck_encrypt(x, y, round_keys, n)
    return speck_block_to_int(x2, y2, n)


# =====================================================================
# Test vectors from the paper (Appendix C)
# =====================================================================

def _test():
    print("=== Speck test vectors (Appendix C) ===\n")

    all_ok = True

    # ------------------------------------------------------------------
    # Speck32/64  (m=4, 22 rounds)
    # Key:  1918 1110 0908 0100
    # PT:   6574 694c
    # CT:   a868 42f2
    key = struct.pack('<4H', 0x0100, 0x0908, 0x1110, 0x1918)
    rk, n = speck_expand_key(key, 32, key_bits=64)
    cx, cy = speck_encrypt(0x6574, 0x694c, rk, n)
    ok = cx == 0xa868 and cy == 0x42f2
    all_ok &= ok
    print(f"Speck32/64:   {cx:04x} {cy:04x}  "
          f"expected a868 42f2  {'OK' if ok else 'FAIL'}")

    # ------------------------------------------------------------------
    # Speck48/72  (m=3, 22 rounds)
    # Key:  121110 0a0908 020100
    # PT:   20796c 6c6172
    # CT:   c049a5 385adc
    key = bytes([0x00, 0x01, 0x02,
                 0x08, 0x09, 0x0a,
                 0x10, 0x11, 0x12])
    rk, n = speck_expand_key(key, 48, key_bits=72)
    cx, cy = speck_encrypt(0x20796c, 0x6c6172, rk, n)
    ok = cx == 0xc049a5 and cy == 0x385adc
    all_ok &= ok
    print(f"Speck48/72:   {cx:06x} {cy:06x}  "
          f"expected c049a5 385adc  {'OK' if ok else 'FAIL'}")

    # ------------------------------------------------------------------
    # Speck48/96  (m=4, 23 rounds)
    # Key:  1a1918 121110 0a0908 020100
    # PT:   6d2073 696874
    # CT:   735e10 b6445d
    key = bytes([0x00, 0x01, 0x02,
                 0x08, 0x09, 0x0a,
                 0x10, 0x11, 0x12,
                 0x18, 0x19, 0x1a])
    rk, n = speck_expand_key(key, 48, key_bits=96)
    cx, cy = speck_encrypt(0x6d2073, 0x696874, rk, n)
    ok = cx == 0x735e10 and cy == 0xb6445d
    all_ok &= ok
    print(f"Speck48/96:   {cx:06x} {cy:06x}  "
          f"expected 735e10 b6445d  {'OK' if ok else 'FAIL'}")

    # ------------------------------------------------------------------
    # Speck64/96  (m=3, 26 rounds)
    # Key:  13121110 0b0a0908 03020100
    # PT:   74614620 736e6165
    # CT:   9f7952ec 4175946c
    key = struct.pack('<3I', 0x03020100, 0x0b0a0908, 0x13121110)
    rk, n = speck_expand_key(key, 64, key_bits=96)
    cx, cy = speck_encrypt(0x74614620, 0x736e6165, rk, n)
    ok = cx == 0x9f7952ec and cy == 0x4175946c
    all_ok &= ok
    print(f"Speck64/96:   {cx:08x} {cy:08x}  "
          f"expected 9f7952ec 4175946c  {'OK' if ok else 'FAIL'}")

    # ------------------------------------------------------------------
    # Speck64/128  (m=4, 27 rounds)
    # Key:  1b1a1918 13121110 0b0a0908 03020100
    # PT:   3b726574 7475432d
    # CT:   8c6fa548 454e028b
    key = struct.pack('<4I', 0x03020100, 0x0b0a0908, 0x13121110, 0x1b1a1918)
    rk, n = speck_expand_key(key, 64, key_bits=128)
    cx, cy = speck_encrypt(0x3b726574, 0x7475432d, rk, n)
    ok = cx == 0x8c6fa548 and cy == 0x454e028b
    all_ok &= ok
    print(f"Speck64/128:  {cx:08x} {cy:08x}  "
          f"expected 8c6fa548 454e028b  {'OK' if ok else 'FAIL'}")

    # ------------------------------------------------------------------
    # Speck96/96  (m=2, 28 rounds)
    # Key:  0d0c0b0a0908 050403020100
    # PT:   65776f68202c 656761737520
    # CT:   9e4d09ab7178 62bdde8f79aa
    key = bytes([0x00, 0x01, 0x02, 0x03, 0x04, 0x05,
                 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d])
    rk, n = speck_expand_key(key, 96, key_bits=96)
    cx, cy = speck_encrypt(0x65776f68202c, 0x656761737520, rk, n)
    ok = cx == 0x9e4d09ab7178 and cy == 0x62bdde8f79aa
    all_ok &= ok
    print(f"Speck96/96:   {cx:012x} {cy:012x}  "
          f"expected 9e4d09ab7178 62bdde8f79aa  {'OK' if ok else 'FAIL'}")

    # ------------------------------------------------------------------
    # Speck96/144  (m=3, 29 rounds)
    # Key:  151413121110 0d0c0b0a0908 050403020100
    # PT:   656d6974206e 69202c726576
    # CT:   2bf31072228a 7ae440252ee6
    key = bytes([0x00, 0x01, 0x02, 0x03, 0x04, 0x05,
                 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d,
                 0x10, 0x11, 0x12, 0x13, 0x14, 0x15])
    rk, n = speck_expand_key(key, 96, key_bits=144)
    cx, cy = speck_encrypt(0x656d6974206e, 0x69202c726576, rk, n)
    ok = cx == 0x2bf31072228a and cy == 0x7ae440252ee6
    all_ok &= ok
    print(f"Speck96/144:  {cx:012x} {cy:012x}  "
          f"expected 2bf31072228a 7ae440252ee6  {'OK' if ok else 'FAIL'}")

    # ------------------------------------------------------------------
    # Speck128/128  (m=2, 32 rounds)
    # Key:  0f0e0d0c0b0a0908 0706050403020100
    # PT:   6c61766975716520 7469206564616d20
    # CT:   a65d985179783265 7860fedf5c570d18
    key = struct.pack('<2Q', 0x0706050403020100, 0x0f0e0d0c0b0a0908)
    rk, n = speck_expand_key(key, 128, key_bits=128)
    cx, cy = speck_encrypt(0x6c61766975716520, 0x7469206564616d20, rk, n)
    ok = cx == 0xa65d985179783265 and cy == 0x7860fedf5c570d18
    all_ok &= ok
    print(f"Speck128/128: {cx:016x} {cy:016x}  "
          f"expected a65d985179783265 7860fedf5c570d18  {'OK' if ok else 'FAIL'}")

    # ------------------------------------------------------------------
    # Speck128/256  (m=4, 34 rounds)
    # Key:  1f1e1d1c1b1a1918 1716151413121110 0f0e0d0c0b0a0908 0706050403020100
    # PT:   65736f6874206e49 202e72656e6f6f70
    # CT:   4109010405c0f53e 4eeeb48d9c188f43
    key = struct.pack('<4Q',
        0x0706050403020100, 0x0f0e0d0c0b0a0908,
        0x1716151413121110, 0x1f1e1d1c1b1a1918)
    rk, n = speck_expand_key(key, 128, key_bits=256)
    cx, cy = speck_encrypt(0x65736f6874206e49, 0x202e72656e6f6f70, rk, n)
    ok = cx == 0x4109010405c0f53e and cy == 0x4eeeb48d9c188f43
    all_ok &= ok
    print(f"Speck128/256: {cx:016x} {cy:016x}  "
          f"expected 4109010405c0f53e 4eeeb48d9c188f43  {'OK' if ok else 'FAIL'}")

    # ------------------------------------------------------------------
    print(f"\nAll vectors pass: {all_ok}")

    print(f"\nAuto-select examples:")
    for val in [100, 2**16, 2**32, 2**48, 2**64, 2**96]:
        v = select_variant(val)
        print(f"  max_value={val}: Speck{v}")

    return all_ok


if __name__ == '__main__':
    import sys
    ok = _test()
    if not ok:
        sys.exit(1)
