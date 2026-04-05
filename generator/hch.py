"""
hch.py — Hilbert-Champernowne-Hyland block generator
=====================================================

Python implementation matching hch.c exactly. Speck32/64 for
tight-fit blocks, balanced Feistel for small blocks. SHA-256
for key derivation.

Blocks up to 2^32. Three operations: init, next, reset.

Usage:
    from hch import HCH

    gen = HCH(base=65536, digit_class=2, key=b'secret')
    for i in range(100):
        print(gen.next())
"""

import hashlib
import math
import struct

# Constants matching hch.h
SPECK32_ROUNDS = 22
FEISTEL_ROUNDS = 8
MAX_CYCLE_WALK_RATIO = 64


# =====================================================================
# Speck32/64
# =====================================================================

def _ror16(x, r):
    return ((x >> r) | (x << (16 - r))) & 0xFFFF

def _rol16(x, r):
    return ((x << r) | (x >> (16 - r))) & 0xFFFF

def _speck32_expand_key(key_bytes):
    """Expand 8-byte key into 22 round keys for Speck32/64."""
    kb = (key_bytes + b'\x00' * 8)[:8]
    k = kb[0] | (kb[1] << 8)
    l = [
        kb[2] | (kb[3] << 8),
        kb[4] | (kb[5] << 8),
        kb[6] | (kb[7] << 8),
    ]
    rk = [k]
    for i in range(21):
        li_new = (_ror16(l[i], 7) + k) & 0xFFFF
        li_new ^= i
        k = _rol16(k, 2) ^ li_new
        l.append(li_new)
        rk.append(k)
    return rk

def _speck32_encrypt(pt, rk):
    """Encrypt a 32-bit integer through Speck32/64."""
    x = (pt >> 16) & 0xFFFF
    y = pt & 0xFFFF
    for i in range(SPECK32_ROUNDS):
        x = (_ror16(x, 7) + y) & 0xFFFF
        x ^= rk[i]
        y = _rol16(y, 2) ^ x
    return (x << 16) | y


# =====================================================================
# HCH generator
# =====================================================================

class HCH:
    """
    HCH block generator.

    Parameters
    ----------
    base : int
        Output symbols are in {1, ..., base-1}.
    digit_class : int
        Operating block is [base^(d-1), base^d - 1].
    key : bytes
        Raw key material.
    """

    def __init__(self, base, digit_class, key):
        if base < 2:
            raise ValueError("base must be >= 2")
        if digit_class < 1:
            raise ValueError("digit_class must be >= 1")

        self.base = base
        self.digit_class = digit_class

        self.block_start = base ** (digit_class - 1)
        block_end = base ** digit_class - 1
        self.block_size = block_end - self.block_start + 1

        if self.block_size > 2**32:
            raise ValueError(
                f"block_size {self.block_size} exceeds 2^32")

        # Choose mode: speck32 or feistel
        if (1 << 32) <= MAX_CYCLE_WALK_RATIO * self.block_size:
            self._mode = 0  # speck32
            speck_key = hashlib.sha256(key).digest()[:8]
            self._rk = _speck32_expand_key(speck_key)
        else:
            self._mode = 1  # feistel
            s = int(math.isqrt(self.block_size))
            while s * s < self.block_size:
                s += 1
            self._L_size = s
            self._R_size = s
            key_hash = hashlib.sha256(key).digest()
            self._fk = []
            for i in range(FEISTEL_ROUNDS):
                h = hashlib.sha256(key_hash + struct.pack('<I', i)).digest()
                self._fk.append(int.from_bytes(h[:8], 'little'))

        self.counter = 0

    def _permute(self, index):
        if self._mode == 0:
            return self._permute_speck(index)
        return self._permute_feistel(index)

    def _permute_speck(self, index):
        val = index
        while True:
            val = _speck32_encrypt(val, self._rk)
            if val < self.block_size:
                return val

    def _permute_feistel(self, index):
        while True:
            L = index // self._R_size
            R = index % self._R_size
            for i in range(FEISTEL_ROUNDS):
                rk = self._fk[i]
                f = ((R + (rk >> (i * 3))) ^
                     (rk >> (i * 5 + 1))) % self._L_size
                L, R = R, (L + f) % self._L_size
            result = L * self._R_size + R
            if result < self.block_size:
                return result
            index = result

    def next(self):
        """Generate the next output symbol in {1, ..., base-1}."""
        if self.counter >= self.block_size:
            self.counter = 0
        perm = self._permute(self.counter)
        self.counter += 1
        n = self.block_start + perm
        b = self.base
        while n >= b:
            n //= b
        return n

    def reset(self):
        """Reset counter to start of period."""
        self.counter = 0

    @property
    def period(self):
        return self.block_size

    # Pythonic conveniences (language-required, not feature additions)
    def __iter__(self):
        self.counter = 0
        return self

    def __next__(self):
        if self.counter >= self.block_size:
            raise StopIteration
        return self.next()

    def __repr__(self):
        mode = 'speck32' if self._mode == 0 else 'feistel'
        return f"HCH(base={self.base}, d={self.digit_class}, {mode}, period={self.period})"
