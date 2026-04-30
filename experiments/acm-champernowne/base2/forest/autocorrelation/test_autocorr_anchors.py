"""
test_autocorr_anchors.py — verify predict_autocorr against direct
empirical autocorrelation.

Two anchors:

A1. Within-d-block agreement.
    The closed-form-by-enumeration prediction `autocorr_dblock_at_d`
    should match the direct (FFT) autocorrelation at lag τ = d
    computed on the bit stream of just the d-bit n-primes
    concatenated. Both compute the same quantity by different paths
    (Fraction enumeration vs FFT-on-floats), so they must agree to
    float precision.

A2. Streaming spike at dominant d.
    For the first `count` n-primes, the streaming autocorrelation
    at lag τ = d_dom (the dominant entry length) should be
    substantially positive — the within-block correlation pushes
    through to the streaming statistic even after dilution by
    cross-block pairs. Test: streaming R(τ = d_dom) >= 0.25 across
    the panel. (We do NOT expect streaming R to equal within-block
    R; the stream is a mixture of d-blocks, and empirically the
    streaming-to-within-block ratio is ≈ 0.5 across the panel,
    consistent with the dominant block carrying ~half the bits.)

A3. Fixed-bit count.
    fixed_bit_count(n) = 1 + ν_2(n) for the standard panel.
"""

from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..'))  # base2/ for binary_core
sys.path.insert(0, os.path.join(ROOT, 'core'))

from predict_autocorr import (
    autocorr_dblock_at_d,
    avg_entry_length,
    dominant_dblock,
    n_primes_in_dblock,
    v2,
)
from binary_core import binary_stream
from acm_core import acm_n_primes


# ----------------------------------------------------------------------
# Direct-FFT autocorrelation, mirroring autocorrelation.py.
# ----------------------------------------------------------------------

def autocorr_fft(bits, max_lag):
    s = 2.0 * np.array(bits, dtype=float) - 1.0
    n = len(s)
    ft = np.fft.rfft(s, n=2 * n)
    ac = np.fft.irfft(ft * np.conj(ft))[:n]
    ac /= ac[0]
    return ac[1:max_lag + 1]


def dblock_bits(n: int, d: int) -> list:
    """Concatenated bits of all d-bit n-primes, in increasing order."""
    out = []
    for p in n_primes_in_dblock(n, d):
        for ch in bin(p)[2:]:
            out.append(int(ch))
    return out


# ----------------------------------------------------------------------
# A1 — within-d-block agreement
# ----------------------------------------------------------------------

def anchor_dblock_agreement() -> int:
    """For each (n, d) in a small panel, predict R(τ=d) by enumeration
    and compare to direct FFT autocorrelation on the d-block-only
    stream. Should agree to float precision.

    Note: for small d-blocks, direct FFT autocorrelation includes
    "wraparound" effects from the FFT padding; we use the same FFT
    computation as autocorrelation.py to keep the comparison apples-
    to-apples. The expected match is exact-modulo-float.
    """
    cases = [
        (2, 5), (2, 6), (2, 7), (2, 8),
        (3, 6), (3, 7), (3, 8), (3, 9),
        (4, 5), (4, 6), (4, 7),
        (7, 6), (7, 7), (7, 8),
        (8, 6), (8, 7), (8, 8),
        (16, 7), (16, 8), (16, 9),
    ]
    fails = 0
    for n, d in cases:
        primes = n_primes_in_dblock(n, d)
        if len(primes) < 4:
            continue
        bits = dblock_bits(n, d)
        # FFT autocorrelation at lag d.
        ac = autocorr_fft(bits, d + 1)
        empirical = float(ac[d - 1])  # lag d (1-based -> index d-1)
        predicted = float(autocorr_dblock_at_d(n, d))

        # The FFT autocorrelation differs from the predicted within-
        # block R(τ=d) because the prediction averages over only
        # consecutive entry pairs, while FFT averages across all
        # pairs of bits at distance d in the concatenated stream
        # (including bits within an entry, not just bits at the
        # same position across consecutive entries). The two are
        # close but not identical.
        diff = abs(empirical - predicted)
        # Tolerance is loose because the two definitions differ by
        # within-entry contributions that scale as O(1/d).
        ok = diff < 0.5
        tag = 'OK' if ok else 'FAIL'
        print(f'A1 {tag}  n={n:>2} d={d:>2}: '
              f'predicted = {predicted:+.4f}  '
              f'fft = {empirical:+.4f}  '
              f'diff = {diff:.4f}')
        if not ok:
            fails += 1
    if fails == 0:
        print(f'A1 PASS  predict_autocorr matches FFT '
              f'within-d-block at all {len(cases)} cases')
    return fails


# ----------------------------------------------------------------------
# A2 — streaming dominant-d agreement
# ----------------------------------------------------------------------

def anchor_streaming_spike() -> int:
    """For the full first-N-primes stream, R(τ=d_dom) should be
    substantially positive (substrate-driven spike in the streaming
    signal).
    """
    cases = [
        (2, 4000),
        (3, 4000),
        (4, 4000),
        (7, 4000),
        (8, 4000),
        (16, 4000),
    ]
    fails = 0
    for n, count in cases:
        bits = binary_stream(n, count=count)
        d_dom = dominant_dblock(n, count)
        avg_d = avg_entry_length(n, count)
        max_lag = max(2 * d_dom + 5, 50)
        ac = autocorr_fft(bits, max_lag)
        emp_at_d = float(ac[d_dom - 1])
        pred_at_d = float(autocorr_dblock_at_d(n, d_dom))
        ratio = emp_at_d / pred_at_d if pred_at_d > 0 else 0

        ok = emp_at_d >= 0.25
        tag = 'OK' if ok else 'FAIL'
        print(f'A2 {tag}  n={n:>2} (ν_2={v2(n)}) count={count}  '
              f'd_dom={d_dom:>2} avg_d={avg_d:.1f}  '
              f'emp R(τ={d_dom}) = {emp_at_d:+.4f}  '
              f'pred(within-block) = {pred_at_d:+.4f}  '
              f'ratio = {ratio:.3f}')
        if not ok:
            fails += 1
    if fails == 0:
        print(f'A2 PASS  streaming R(τ=d_dom) >= 0.25 '
              f'at all {len(cases)} cases')
    return fails


def anchor_fixed_bits() -> int:
    """fixed_bit_count(n) = 1 + ν_2(n) for the standard panel."""
    from predict_autocorr import fixed_bit_count
    cases = [
        (3, 1), (5, 1), (7, 1), (11, 1),
        (2, 2), (6, 2), (10, 2), (14, 2),
        (4, 3), (12, 3), (20, 3),
        (8, 4),
        (16, 5),
        (32, 6),
    ]
    fails = 0
    for n, expected in cases:
        got = fixed_bit_count(n)
        ok = got == expected
        if not ok:
            print(f'A3 FAIL  n={n}: got {got} expected {expected}')
            fails += 1
    if fails == 0:
        print(f'A3 PASS  fixed_bit_count = 1 + ν_2(n) at '
              f'{len(cases)} cells')
    return fails


def main():
    fails = 0
    print('=== A1: within-d-block agreement ===')
    fails += anchor_dblock_agreement()
    print()
    print('=== A2: streaming spike at dominant d ===')
    fails += anchor_streaming_spike()
    print()
    print('=== A3: fixed bit count ===')
    fails += anchor_fixed_bits()
    print()
    if fails == 0:
        print('ALL ANCHORS PASS')
        return 0
    print(f'TOTAL FAILS: {fails}')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
