"""
test_primitives.py — Layer 2 unit tests for the probes' building blocks.

Covers transducers, predicted-set helpers, channels, and the
verdict-from-strength rule for kernel_zero. Most assertions are
tautologies if the primitives are correct. The value is catching
the case where a channel and its predicted-set helper drift apart, or
where the verdict thresholding silently changes.

A failure here means a channel, transducer, or predicted-set helper
has a bug. The first place to look is
`experiments/probes/<probe>/probe.py`.

Run:

    sage -python algebra/tests/probes/test_primitives.py
"""

from __future__ import annotations

import os
import sys
from fractions import Fraction
from math import gcd

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.dirname(HERE)
ALGEBRA = os.path.dirname(TESTS)
REPO = os.path.dirname(ALGEBRA)
sys.path.insert(0, ALGEBRA)
sys.path.insert(0, os.path.join(REPO, 'experiments', 'probes', 'kernel_zero'))

from predict_q import big_omega, q_general  # noqa: E402
from probe import (  # noqa: E402
    TOL, _verdict_from_strength,
    algebra_row, channel_no_op, channel_prime_row_identity_at_k1,
    channel_value_multiset, channel_zero_count,
    predicted_multiset, predicted_zero_indices, synth_uniform_row,
    transducer_identity, transducer_reverse,
)


SMALL_PRIMES = (2, 3, 5)
SMALL_HEIGHTS = (5, 6)
SMALL_K = 100


# --------------------------------------------------------------------------
# transducers
# --------------------------------------------------------------------------

def test_transducer_identity():
    fails = 0
    for K in (1, 5, 100):
        row = np.arange(K, dtype=np.float64)
        out = transducer_identity(row)
        if not np.array_equal(out, row):
            print(f'FAIL  transducer_identity changed row at K={K}')
            fails += 1
        if out is row:
            print(f'FAIL  transducer_identity returned same object at K={K}')
            fails += 1
    if fails == 0:
        print('PASS  transducer_identity preserves values, returns copy')
    return fails


def test_transducer_reverse_involutive():
    """reverse ∘ reverse == identity (the property used to predict reverse
    calibration's σ-invariant channels)."""
    fails = 0
    for K in (1, 2, 5, 100, 4000):
        row = np.arange(K, dtype=np.float64) + 0.5
        twice = transducer_reverse(transducer_reverse(row))
        if not np.array_equal(twice, row):
            print(f'FAIL  reverse(reverse(row)) != row at K={K}')
            fails += 1
        once = transducer_reverse(row)
        # σ(k) = K + 1 - k, so post[k - 1] = pre[K - k] (0-indexed: post[i] = pre[K-1-i])
        for i in range(K):
            if once[i] != row[K - 1 - i]:
                print(f'FAIL  transducer_reverse off-by-one at K={K}, i={i}')
                fails += 1
                break
    if fails == 0:
        print('PASS  transducer_reverse is involutive and σ(k)=K+1-k correct')
    return fails


def test_transducers_immutable_on_input():
    """Transducers must not mutate their input row."""
    fails = 0
    row = np.array([1.0, 2.0, 3.0, 4.0])
    snapshot = row.copy()
    transducer_identity(row)
    transducer_reverse(row)
    if not np.array_equal(row, snapshot):
        print(f'FAIL  transducer mutated input row: {row} != {snapshot}')
        fails += 1
    if fails == 0:
        print('PASS  transducers do not mutate input row')
    return fails


# --------------------------------------------------------------------------
# substrate generators
# --------------------------------------------------------------------------

def test_synth_uniform_row():
    fails = 0
    # determinism
    a = synth_uniform_row(K=50, seed=42)
    b = synth_uniform_row(K=50, seed=42)
    if not np.array_equal(a, b):
        print(f'FAIL  synth_uniform_row not deterministic for fixed seed')
        fails += 1
    # range
    r = synth_uniform_row(K=10000, seed=0, lo=-100.0, hi=100.0)
    if r.min() < -100.0 or r.max() > 100.0:
        print(f'FAIL  synth_uniform_row out of range [-100, 100]: '
              f'[{r.min()}, {r.max()}]')
        fails += 1
    # different seeds => different rows
    c = synth_uniform_row(K=50, seed=0)
    d = synth_uniform_row(K=50, seed=1)
    if np.array_equal(c, d):
        print(f'FAIL  synth_uniform_row seed-independent')
        fails += 1
    if fails == 0:
        print('PASS  synth_uniform_row deterministic + bounded + seed-sensitive')
    return fails


def test_algebra_row_matches_q_general():
    """algebra_row(p, h, K) is the float'd q_general row."""
    fails = 0
    checked = 0
    for p in SMALL_PRIMES:
        for h in SMALL_HEIGHTS:
            row = algebra_row(p, h, SMALL_K)
            for k in range(1, SMALL_K + 1):
                expected = float(q_general(p, h, k))
                if row[k - 1] != expected:
                    print(f'FAIL  algebra_row({p},{h})[{k-1}] = {row[k-1]} '
                          f'!= q_general = {expected}')
                    fails += 1
                checked += 1
    if fails == 0:
        print(f'PASS  algebra_row == q_general row ({checked} cells)')
    return fails


# --------------------------------------------------------------------------
# predicted-set helpers
# --------------------------------------------------------------------------

def test_predicted_zero_indices():
    """Algebra-defined zero set: indices where q_general returns Fraction(0)."""
    fails = 0
    checked = 0
    for p in SMALL_PRIMES:
        for h in SMALL_HEIGHTS:
            Z = predicted_zero_indices(p, h, SMALL_K)
            # Each member must satisfy the definition.
            for i in Z:
                k = int(i) + 1
                if q_general(p, h, k) != Fraction(0):
                    print(f'FAIL  predicted_zero_indices({p},{h}) includes '
                          f'k={k} but q_general != 0')
                    fails += 1
            # Conversely, every k with q_general(p, h, k) == 0 must be in Z.
            Z_set = set(int(i) for i in Z)
            for k in range(1, SMALL_K + 1):
                if q_general(p, h, k) == Fraction(0):
                    if (k - 1) not in Z_set:
                        print(f'FAIL  predicted_zero_indices({p},{h}) misses '
                              f'k={k} where q_general == 0')
                        fails += 1
                checked += 1
    if fails == 0:
        print(f'PASS  predicted_zero_indices == {{k : q_general == 0}} '
              f'({checked} cells across {len(SMALL_PRIMES)*len(SMALL_HEIGHTS)} (p,h))')
    return fails


def test_predicted_multiset_sorted():
    fails = 0
    for p in SMALL_PRIMES:
        for h in SMALL_HEIGHTS:
            M = predicted_multiset(p, h, SMALL_K)
            if len(M) != SMALL_K:
                print(f'FAIL  predicted_multiset({p},{h}) length {len(M)} != {SMALL_K}')
                fails += 1
            if not np.all(M[:-1] <= M[1:]):
                print(f'FAIL  predicted_multiset({p},{h}) not sorted')
                fails += 1
    if fails == 0:
        print(f'PASS  predicted_multiset sorted ascending, length K')
    return fails


# --------------------------------------------------------------------------
# verdict-from-strength
# --------------------------------------------------------------------------

def test_verdict_from_strength():
    fails = 0
    cases = [
        (1.0, 'present'),
        (1.0 - 1e-16, 'present'),  # below numerical-equality threshold
        (0.0, 'absent'),
        (1e-16, 'absent'),
        (0.5, 'partial'),
        (0.99999, 'partial'),
        (1e-12, 'partial'),  # strictly above 1e-15 absent threshold
    ]
    for s, expected in cases:
        got = _verdict_from_strength(s)
        if got != expected:
            print(f'FAIL  _verdict_from_strength({s}) = {got} != {expected}')
            fails += 1
    if fails == 0:
        print(f'PASS  _verdict_from_strength boundary cases')
    return fails


# --------------------------------------------------------------------------
# channels — correctness on synthetic rows
# --------------------------------------------------------------------------

def test_channel_no_op_on_algebra_row():
    """no_op on the exact algebra row is PRESENT/1.0."""
    fails = 0
    for p in SMALL_PRIMES:
        for h in SMALL_HEIGHTS:
            row = algebra_row(p, h, SMALL_K)
            v, s = channel_no_op(row, p, h)
            if v != 'present' or s != 1.0:
                print(f'FAIL  channel_no_op({p},{h}) on algebra row: '
                      f'{v}/{s}, expected present/1.0')
                fails += 1
    if fails == 0:
        print('PASS  channel_no_op on algebra row is PRESENT/1.0')
    return fails


def test_channel_no_op_on_constant_row():
    """no_op on a row of all 1.0 is ABSENT (no predicted-zero cell is zero)."""
    fails = 0
    for p in SMALL_PRIMES:
        for h in SMALL_HEIGHTS:
            Z = predicted_zero_indices(p, h, SMALL_K)
            if Z.size == 0:
                continue  # no predicted zeros to be missing
            row = np.ones(SMALL_K, dtype=np.float64)
            v, s = channel_no_op(row, p, h)
            if v != 'absent' or s != 0.0:
                print(f'FAIL  channel_no_op({p},{h}) on all-ones: '
                      f'{v}/{s}, expected absent/0.0')
                fails += 1
    if fails == 0:
        print('PASS  channel_no_op on all-ones row is ABSENT/0.0')
    return fails


def test_channel_zero_count_on_algebra_row():
    fails = 0
    for p in SMALL_PRIMES:
        for h in SMALL_HEIGHTS:
            row = algebra_row(p, h, SMALL_K)
            v, s = channel_zero_count(row, p, h)
            if v != 'present' or s != 1.0:
                print(f'FAIL  channel_zero_count({p},{h}) on algebra row: '
                      f'{v}/{s}')
                fails += 1
    if fails == 0:
        print('PASS  channel_zero_count on algebra row is PRESENT/1.0')
    return fails


def test_channel_value_multiset_invariant_under_shuffle():
    """value_multiset is a sorted-multiset comparison; permuting the row
    must not change the verdict."""
    fails = 0
    rng = np.random.default_rng(0)
    for p in SMALL_PRIMES:
        for h in SMALL_HEIGHTS:
            row = algebra_row(p, h, SMALL_K)
            permuted = rng.permutation(row)
            v_orig, s_orig = channel_value_multiset(row, p, h)
            v_perm, s_perm = channel_value_multiset(permuted, p, h)
            if (v_orig, s_orig) != (v_perm, s_perm):
                print(f'FAIL  channel_value_multiset({p},{h}) not '
                      f'permutation-invariant: orig={v_orig}/{s_orig}, '
                      f'perm={v_perm}/{s_perm}')
                fails += 1
    if fails == 0:
        print('PASS  channel_value_multiset is permutation-invariant')
    return fails


def test_channel_prime_row_identity_at_k1():
    """row[0] == 1/h iff PRESENT; otherwise ABSENT."""
    fails = 0
    for h in SMALL_HEIGHTS:
        # canonical: cell[0] = 1/h
        row = np.zeros(10, dtype=np.float64)
        row[0] = 1.0 / h
        v, s = channel_prime_row_identity_at_k1(row, 2, h)
        if v != 'present' or s != 1.0:
            print(f'FAIL  channel_prime_row_identity_at_k1 missed canonical at h={h}')
            fails += 1
        # off by something larger than TOL
        row[0] = 1.0 / h + 10 * TOL
        v, s = channel_prime_row_identity_at_k1(row, 2, h)
        if v != 'absent' or s != 0.0:
            print(f'FAIL  channel_prime_row_identity_at_k1 false positive at h={h}')
            fails += 1
    if fails == 0:
        print('PASS  channel_prime_row_identity_at_k1 boundary cases')
    return fails


def test_channels_strength_in_unit_interval():
    """For any input row, every channel's strength is in [0, 1]."""
    fails = 0
    rng = np.random.default_rng(1)
    rows = [
        algebra_row(2, 5, 50),
        np.zeros(50, dtype=np.float64),
        np.ones(50, dtype=np.float64),
        rng.uniform(-1.0, 1.0, size=50),
        rng.standard_normal(50) * 100,
    ]
    for ri, row in enumerate(rows):
        for ch_name, fn in [
            ('no_op', channel_no_op),
            ('zero_count', channel_zero_count),
            ('value_multiset', channel_value_multiset),
            ('prime_row_identity_at_k1', channel_prime_row_identity_at_k1),
        ]:
            v, s = fn(row, 2, 5)
            if not (0.0 <= s <= 1.0):
                print(f'FAIL  channel {ch_name} strength {s} out of [0, 1] '
                      f'on row {ri}')
                fails += 1
            if v not in ('present', 'partial', 'absent'):
                print(f'FAIL  channel {ch_name} verdict {v!r} not in '
                      f'{{present, partial, absent}}')
                fails += 1
    if fails == 0:
        print('PASS  all channel strengths in [0, 1] across canonical rows')
    return fails


def main():
    fails = 0
    # transducers
    fails += test_transducer_identity()
    fails += test_transducer_reverse_involutive()
    fails += test_transducers_immutable_on_input()
    # substrate generators
    fails += test_synth_uniform_row()
    fails += test_algebra_row_matches_q_general()
    # predicted-set helpers
    fails += test_predicted_zero_indices()
    fails += test_predicted_multiset_sorted()
    # verdict rule
    fails += test_verdict_from_strength()
    # channels
    fails += test_channel_no_op_on_algebra_row()
    fails += test_channel_no_op_on_constant_row()
    fails += test_channel_zero_count_on_algebra_row()
    fails += test_channel_value_multiset_invariant_under_shuffle()
    fails += test_channel_prime_row_identity_at_k1()
    fails += test_channels_strength_in_unit_interval()

    print()
    if fails == 0:
        print('ALL PRIMITIVE TESTS PASS')
        return 0
    print(f'TOTAL FAILS: {fails}')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
