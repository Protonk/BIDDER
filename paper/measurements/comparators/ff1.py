"""
ff1.py — minimal NIST SP 800-38G FF1 reference (radix=2 + cycle-walking).

The §7.4 / DEBTS.md D1 comparator. FF1 with AES is the de facto
format-preserving encryption standard; this module implements the
algorithm exactly as specified in NIST SP 800-38G §6.3 (Algorithm
7), validated against the official test vectors (Appendix A.1).

For BIDDER's comparison, we want a keyed bijection of `[0, P)` for
arbitrary `P`. FF1 itself operates on character sequences over a
radix; we set `radix = 2` and `length = ceil(log2(P))` to encode
`[0, 2^length)`, then cycle-walk to land in `[0, P)`. This matches
how the BIDDER cipher reduces to Speck32/64 cycle-walking.

Only ENCRYPT is implemented (DECRYPT is symmetric and not needed
for the throughput / FPC measurements). AES-128 backend via
pycryptodome (`pip install pycryptodome` per requirements.txt).

Public surface:
    Ff1(key: bytes, tweak: bytes = b'') ->
        ff1.encrypt_int(period: int, x: int) -> int     # cycle-walking
        ff1.encrypt_seq(radix: int, x: list[int]) -> list[int]  # raw FF1
"""

from __future__ import annotations

import math
from Crypto.Cipher import AES


def _num(seq: list[int], radix: int) -> int:
    """Algorithm 1 (NUM_radix): convert a digit sequence to integer."""
    n = 0
    for d in seq:
        n = n * radix + d
    return n


def _str_radix(n: int, radix: int, length: int) -> list[int]:
    """Algorithm 2 (STR_radix^m): convert integer back to digit sequence."""
    out = [0] * length
    for i in range(length - 1, -1, -1):
        out[i] = n % radix
        n //= radix
    return out


def _xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def _prf(aes: 'AES', data: bytes) -> bytes:
    """CBC-MAC over `data`. `data` must be a multiple of 16 bytes."""
    assert len(data) % 16 == 0, 'PRF input length must be 16-aligned'
    state = b'\x00' * 16
    for i in range(0, len(data), 16):
        state = aes.encrypt(_xor_bytes(state, data[i:i + 16]))
    return state


class Ff1:
    """FF1 encryptor with a fixed key and tweak.

    Per NIST SP 800-38G §6.3, FF1 is parameterised by:
      - a key K (AES-128 / 192 / 256)
      - a tweak T (variable length, may be empty)
      - a radix (2 ≤ radix ≤ 2^16)
      - a digit-sequence length n (with radix^n ≥ 100)

    This implementation fixes radix and length per call (since we
    cycle-walk over [0, 2^length) for arbitrary `period`).
    """

    def __init__(self, key: bytes, tweak: bytes = b''):
        if len(key) not in (16, 24, 32):
            raise ValueError('FF1 key must be 128/192/256 bits')
        self._aes = AES.new(key, AES.MODE_ECB)
        self._tweak = tweak

    def encrypt_seq(self, radix: int, x: list[int]) -> list[int]:
        """FF1.Encrypt per NIST SP 800-38G §6.3 Algorithm 7.

        Args:
            radix: alphabet size (>= 2).
            x: input digit sequence (each element in [0, radix)).
        Returns:
            Output digit sequence of the same length.
        """
        n = len(x)
        if n < 2:
            raise ValueError('FF1 requires len(x) >= 2')
        if radix < 2:
            raise ValueError('FF1 requires radix >= 2')
        if radix ** n < 100:
            raise ValueError('FF1 requires radix^n >= 100')

        # Step 1-3: split.
        u = n // 2
        v = n - u
        A = x[:u]
        B = x[u:]

        # Step 4: b = ceil(ceil(v * log2(radix)) / 8).
        b = math.ceil(math.ceil(v * math.log2(radix)) / 8)

        # Step 5: d = 4 * ceil(b/4) + 4.
        d = 4 * math.ceil(b / 4) + 4

        # Step 6: P = [1]^1 || [2]^1 || [1]^1 || [radix]^3 || [10]^1
        #              || [u mod 256]^1 || [n]^4 || [t]^4
        # where t = len(tweak).
        P = (
            bytes([1, 2, 1])
            + radix.to_bytes(3, 'big')
            + bytes([10])
            + bytes([u % 256])
            + n.to_bytes(4, 'big')
            + len(self._tweak).to_bytes(4, 'big')
        )
        assert len(P) == 16

        for i in range(10):
            # Step 7.i: Q = T || [0]^((-t-b-1) mod 16) || [i]^1 || [NUM_radix(B)]^b
            num_b = _num(B, radix)
            q_pad_len = (-len(self._tweak) - b - 1) % 16
            Q = (
                self._tweak
                + b'\x00' * q_pad_len
                + bytes([i])
                + num_b.to_bytes(b, 'big')
            )

            # Step 7.ii: R = PRF(P || Q).
            R = _prf(self._aes, P + Q)

            # Step 7.iii: S = R || ENC_K(R xor [1]^16) || ENC_K(R xor [2]^16) || ...
            #             then truncated to d bytes.
            S = R
            j = 1
            while len(S) < d:
                block = self._aes.encrypt(_xor_bytes(R, j.to_bytes(16, 'big')))
                S += block
                j += 1
            S = S[:d]

            # Step 7.iv: y = NUM(S).
            y = int.from_bytes(S, 'big')

            # Step 7.v: m = u if i even else v.
            m = u if i % 2 == 0 else v

            # Step 7.vi: c = (NUM_radix(A) + y) mod radix^m.
            c = (_num(A, radix) + y) % (radix ** m)

            # Step 7.vii: C = STR_radix^m(c).
            C = _str_radix(c, radix, m)

            # Step 7.viii: A, B = B, C.
            A, B = B, C

        # Step 8: Z = A || B.
        return A + B

    def encrypt_int(self, period: int, x: int) -> int:
        """Keyed bijection of [0, period) using FF1 with cycle-walking.

        Encodes x in radix=2 with length=max(7, ceil(log2 period)),
        runs FF1, decodes back to int, repeats until result < period.
        Length floor of 7 ensures radix^length >= 100 (NIST minimum).
        """
        if period < 2:
            raise ValueError('period must be >= 2')
        if not 0 <= x < period:
            raise ValueError(f'x={x} out of range [0, {period})')

        radix = 2
        length = max(7, math.ceil(math.log2(period)))
        domain = radix ** length

        y = x
        # If x is past the cycle-walking domain, that's a caller error;
        # since x < period <= domain, we're fine on entry.
        guard = 0
        while True:
            seq = _str_radix(y, radix, length)
            out_seq = self.encrypt_seq(radix, seq)
            y = _num(out_seq, radix)
            if y < period:
                return y
            guard += 1
            if guard > 1024:
                raise RuntimeError('cycle-walking failed to terminate')
