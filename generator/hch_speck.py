"""
hch_speck.py — HCH block generator using the full Speck family
===============================================================

Uses speck.py to auto-select the smallest Speck variant whose block
size covers the digit-class range, then cycle-walks to restrict the
permutation domain to exactly [b^(d-1), b^d - 1].

The Speck variant is chosen via speck.select_variant(), which picks
the smallest block size >= the required range.  The largest-key
variant for that block size is used (max security per Table 4.1):

    Block 32  -> Speck32/64   (22 rounds)
    Block 48  -> Speck48/96   (23 rounds)
    Block 64  -> Speck64/128  (27 rounds)
    Block 96  -> Speck96/144  (29 rounds)
    Block 128 -> Speck128/256 (34 rounds)

Usage:
    from hch_speck import HCHSpeck

    gen = HCHSpeck(base=256, digit_class=2, key=b'secret')
    output = gen.generate(100)
"""

import hashlib
import math
import struct

from speck import (
    select_variant,
    speck_expand_key,
    speck_permute,
    SPECK_PARAMS,
)

# Maximum ratio of Speck block to operating block before we fall back
# to the balanced Feistel. At ratio 64, cycle-walking rejects ~98% of
# evaluations — still tolerable. Above that, Feistel is faster.
_MAX_CYCLE_WALK_RATIO = 64


class HCHSpeck:
    """
    HCH block generator using Speck as the keyed permutation.

    Auto-selects the right Speck variant for the digit-class range,
    then cycle-walks within that range.

    Parameters
    ----------
    base : int
        Base b. Output symbols are in {1, ..., b-1}.
    digit_class : int
        Digit class d. Operating block is [b^(d-1), b^d - 1].
    key : bytes
        Key material (hashed to derive the Speck key).
    """

    def __init__(self, base=256, digit_class=2, key=b''):
        if base < 2:
            raise ValueError("base must be >= 2")
        if digit_class < 1:
            raise ValueError("digit_class must be >= 1")

        self.base = base
        self.digit_class = digit_class
        self.key = key

        self.block_start = base ** (digit_class - 1)
        self.block_end = base ** digit_class - 1
        self.block_size = self.block_end - self.block_start + 1

        # Auto-select permutation strategy
        self.block_bits = select_variant(self.block_size)
        speck_block = 1 << self.block_bits
        ratio = speck_block / self.block_size

        if ratio <= _MAX_CYCLE_WALK_RATIO:
            # Speck + cycle-walking: block is close to Speck's native size
            self._mode = 'speck'
            _n, _m, _alpha, _beta, _T, key_bits = SPECK_PARAMS[self.block_bits]
            key_len = key_bits // 8
            if key_len <= 32:
                speck_key = hashlib.sha256(key).digest()[:key_len]
            else:
                speck_key = hashlib.sha512(key).digest()[:key_len]
            self.round_keys, self.word_bits = speck_expand_key(
                speck_key, self.block_bits)
        else:
            # Balanced Feistel with Speck-derived round keys: block is
            # much smaller than any Speck variant. Uses the same ARX
            # mixing principle but at the block's natural width.
            self._mode = 'feistel'
            s = int(math.isqrt(self.block_size))
            while s * s < self.block_size:
                s += 1
            self._L_size = s
            self._R_size = s
            self._feistel_keys = []
            for i in range(8):
                h = hashlib.sha256(key + struct.pack('<I', i)).digest()
                self._feistel_keys.append(
                    struct.unpack('<Q', h[:8])[0])

        self._counter = 0

    def _permute(self, index):
        """Keyed permutation with cycle-walking."""
        if self._mode == 'speck':
            return self._permute_speck(index)
        return self._permute_feistel(index)

    def _permute_speck(self, index):
        """Full Speck permutation with cycle-walking."""
        val = index
        while True:
            result = speck_permute(val, self.round_keys, self.word_bits)
            if result < self.block_size:
                return result
            val = result

    def _permute_feistel(self, index):
        """Balanced Feistel with cycle-walking for small blocks."""
        while True:
            L = index // self._R_size
            R = index % self._R_size
            for i, rk in enumerate(self._feistel_keys):
                f = ((R + (rk >> (i * 3))) ^ (rk >> (i * 5 + 1))) % self._L_size
                L, R = R, (L + f) % self._L_size
            result = L * self._R_size + R
            if result < self.block_size:
                return result
            index = result

    def _leading_digit(self, n):
        """Leading base-b digit of integer n."""
        b = self.base
        while n >= b:
            n //= b
        return n

    def generate_one(self):
        """Generate the next output symbol."""
        if self._counter >= self.block_size:
            self._counter = 0

        permuted_index = self._permute(self._counter)
        self._counter += 1

        n = self.block_start + permuted_index
        return self._leading_digit(n)

    def generate(self, count):
        """Generate `count` output symbols as a list."""
        return [self.generate_one() for _ in range(count)]

    def reset(self):
        """Reset the counter to the start of the period."""
        self._counter = 0

    @property
    def period(self):
        return self.block_size

    @property
    def alphabet_size(self):
        return self.base - 1

    def __iter__(self):
        self._counter = 0
        return self

    def __next__(self):
        if self._counter >= self.block_size:
            raise StopIteration
        return self.generate_one()

    def __repr__(self):
        if self._mode == 'speck':
            perm = f"Speck{self.block_bits}/{SPECK_PARAMS[self.block_bits][5]}"
        else:
            perm = f"Feistel({self._L_size}x{self._R_size})"
        return (f"HCHSpeck(base={self.base}, d={self.digit_class}, "
                f"{perm}, period={self.period})")
