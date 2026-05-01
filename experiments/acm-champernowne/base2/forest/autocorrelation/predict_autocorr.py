"""
predict_autocorr.py — closed-form prediction of binary autocorrelation
======================================================================

The binary Champernowne stream of monoid `n` concatenates the binary
representations of n-primes. Within a d-bit block (the n-primes with
exactly d bits), the autocorrelation at lag τ = d is fully determined
by the bits of those entries: at each of the d bit positions, R picks
up the average of `s(bit_p_K) * s(bit_p_{K+1})` over consecutive
pairs (K, K+1) in the block, with `s = 2*bit - 1`.

This module computes that within-d-block prediction by direct
enumeration. No closed form in n, h, b — just exact integer
arithmetic on the bits of the n-primes in the d-block.

The predicted streaming autocorrelation at lag τ ≈ d_dom (the
dominant entry length in the data window) is approximately the
within-block R for the dominant d-block, weighted by that block's
share of the bit stream.

This is the binary-stream analog of `algebra/predict_q.py` and
`experiments/acm/cf/offspike_dynamics.py`: an algebraic
predictor verified against the empirical signal.

BQN (per `guidance/BQN-AGENT.md`):
    n_primes_in_dblock  -> mirrors NPn2 filtered by bit-length
    autocorr_dblock_at_d -> the closed-form-by-enumeration prediction
"""

from __future__ import annotations

import os
import sys
from fractions import Fraction
from typing import List

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'core'))

from acm_core import acm_n_primes


def v2(n: int) -> int:
    """2-adic valuation of n: largest v with 2^v | n."""
    if n < 1:
        raise ValueError(f'v2 needs n >= 1, got {n}')
    v = 0
    while n % 2 == 0:
        v += 1
        n //= 2
    return v


def n_primes_in_dblock(n: int, d: int, max_count: int = 200_000) -> List[int]:
    """All n-primes p with p.bit_length() == d, in increasing order.

    For monoid n, p = n*k with n ∤ k. The d-bit range is
    [2^(d-1), 2^d - 1], so k ranges over [⌈2^(d-1)/n⌉, ⌊(2^d - 1)/n⌋]
    with k not divisible by n.
    """
    if d < 1:
        raise ValueError(f'd must be >= 1, got {d}')
    if n < 2:
        raise ValueError(f'n must be >= 2, got {n}')
    lo = 1 if d == 1 else 2 ** (d - 1)
    hi = 2 ** d - 1
    k_lo = (lo + n - 1) // n
    if k_lo < 1:
        k_lo = 1
    k_hi = hi // n
    out = []
    for k in range(k_lo, k_hi + 1):
        if k % n == 0:
            continue
        out.append(n * k)
        if len(out) > max_count:
            break
    return out


def autocorr_dblock_at_d(n: int, d: int) -> Fraction:
    """Within-block autocorrelation R(τ = d) for the d-bit block of
    monoid n. Computed exactly as a Fraction.

    For a d-bit block with M primes (p_1 < p_2 < ... < p_M), the
    autocorrelation at lag d-bits within the block aggregates over
    M-1 consecutive pairs: at each pair (K, K+1) and each bit
    position p ∈ [0, d), accumulate (2*bit_p(p_K) - 1) *
    (2*bit_p(p_{K+1}) - 1). Total contribution is divided by
    (M-1) * d.

    Equivalent identity (used here for clarity): for each bit
    position p, count A_p = #{K : bit_p(p_K) == bit_p(p_{K+1})}
    over K = 1..M-1. Then E[s_K s_{K+1}] at position p =
    (A_p - (M - 1 - A_p)) / (M - 1) = (2 A_p - (M-1)) / (M - 1).
    Average over p ∈ [0, d) gives R.
    """
    primes = n_primes_in_dblock(n, d)
    M = len(primes)
    if M < 2:
        raise ValueError(
            f'need at least 2 d-bit n-primes for n={n} d={d}, got M={M}'
        )
    pairs = M - 1
    total = Fraction(0)
    for p_pos in range(d):
        # Bit at position p_pos counted from MSB (0 = leading bit).
        agree = 0
        for i in range(pairs):
            b_a = (primes[i] >> (d - 1 - p_pos)) & 1
            b_b = (primes[i + 1] >> (d - 1 - p_pos)) & 1
            if b_a == b_b:
                agree += 1
        # mean(s*s) at this position = (2 * agree / pairs) - 1
        total += Fraction(2 * agree - pairs, pairs)
    return total / d


def dominant_dblock(n: int, count: int) -> int:
    """Dominant entry-length (in bits) for the first `count` n-primes.

    Returns the d that contributes the most bits to the binary stream
    of `count` entries. Roughly: argmax_d d * N_d^obs, where N_d^obs
    is the number of n-primes among the first `count` with bit-length
    d.
    """
    primes = acm_n_primes(n, count)
    bit_counts = {}
    for p in primes:
        bl = p.bit_length()
        bit_counts[bl] = bit_counts.get(bl, 0) + bl
    return max(bit_counts, key=bit_counts.get)


def avg_entry_length(n: int, count: int) -> float:
    """Mean bit-length of the first `count` n-primes."""
    primes = acm_n_primes(n, count)
    return sum(p.bit_length() for p in primes) / len(primes)


# ----------------------------------------------------------------------
# Structural decomposition (not a bound).
# ----------------------------------------------------------------------

def fixed_bit_count(n: int) -> int:
    """Number of always-fixed bits per d-bit n-prime entry.

    Always-fixed bits are: (a) the leading bit (always 1, since the
    integer is d-bit), and (b) the trailing ν_2(n) bits (always 0,
    since p = n*k has at least ν_2(n) trailing zeros in binary).

    Returns 1 + ν_2(n).
    """
    return 1 + v2(n)


def fixed_bit_contribution(n: int, d: int) -> Fraction:
    """The (1 + ν_2(n)) / d contribution to R(τ = d) from fixed bits
    alone. This is a *structural component* of R, NOT a bound: bits
    just above the trailing fixed zeros can carry a negative
    correlation that pulls R below this number. (Example: n = 4,
    d = 4 has R = 1/2 < (1 + 2)/4 = 3/4 because the bit just above
    the trailing zeros toggles every step in the d-block, giving a
    −1 contribution.)

    The full decomposition of R(τ = d) is:

        R(τ = d) = [ fixed_contribution + carry_contribution +
                     slow_high_order_contribution ] / d

    where fixed_contribution = (1 + ν_2(n)) (always +1 per fixed bit),
    carry_contribution sums the −1..+1 means of bits in the carry
    zone above the trailing zeros, and slow_high_order_contribution
    sums the ≈ +1 means of bits well above the carry zone (whose
    bit-flip period exceeds the d-block length).
    """
    return Fraction(fixed_bit_count(n), d)


if __name__ == '__main__':
    # Self-check: predict R(τ=d) for the first few d-blocks of small n.
    print('predict_autocorr self-check\n')
    print(f'{"n":>3}  {"ν2":>3}  {"d":>3}  {"M":>5}  '
          f'{"R(τ=d)":>10}  {"fixed_part":>11}  {"R_residual":>11}')
    for n in (2, 3, 4, 7, 8, 16):
        for d in range(4, 13):
            try:
                primes = n_primes_in_dblock(n, d)
                if len(primes) < 2:
                    continue
                R = autocorr_dblock_at_d(n, d)
                fixed = fixed_bit_contribution(n, d)
                residual = R - fixed
                print(f'{n:>3}  {v2(n):>3}  {d:>3}  {len(primes):>5}  '
                      f'{float(R):>+10.4f}  {float(fixed):>+11.4f}  '
                      f'{float(residual):>+11.4f}')
            except ValueError:
                continue
        print()
