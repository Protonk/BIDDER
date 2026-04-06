"""
binary_core.py — shared utilities for binary Champernowne streams
=================================================================

Root module for the binary/ tree. Provides stream generation, RLE,
and entry-boundary tracking for binary concatenations of n-primes.

BQN companions (see guidance/BQN-AGENT.md):
    binary_stream    -> BStream
    rle              -> (prose only — no tidy one-liner)
    entry_boundaries -> (prose only)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'core'))
from acm_core import acm_n_primes


def binary_stream(n, count=500):
    """
    Binary Champernowne bit stream for monoid n.

    Concatenates the binary representations of the first `count` n-primes.
    Returns a list of ints (0s and 1s).
    """
    bits = []
    for p in acm_n_primes(n, count):
        for ch in bin(p)[2:]:
            bits.append(int(ch))
    return bits


def rle(bits):
    """Run-length encode a bit stream. Returns list of (value, length) pairs."""
    if not bits:
        return []
    runs = []
    val = bits[0]
    length = 1
    for b in bits[1:]:
        if b == val:
            length += 1
        else:
            runs.append((val, length))
            val = b
            length = 1
    runs.append((val, length))
    return runs


def entry_boundaries(n, count=500):
    """Bit positions where each n-prime entry begins in the stream."""
    pos = 0
    bounds = [0]
    for p in acm_n_primes(n, count):
        pos += p.bit_length()
        bounds.append(pos)
    return bounds
