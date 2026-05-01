"""
test_primitives.py — Layer 2 unit tests for the probes' building blocks.

Covers transducers, predicted-set helpers, channels, and the
verdict-from-strength rule for each probe. Most assertions are
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

import importlib.util
import os
import sys
from fractions import Fraction
from math import comb, gcd

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.dirname(HERE)
ALGEBRA = os.path.dirname(TESTS)
REPO = os.path.dirname(ALGEBRA)
sys.path.insert(0, ALGEBRA)

from predict_q import big_omega, q_general  # noqa: E402


def load_probe(probe_name: str):
    path = os.path.join(REPO, 'experiments', 'probes', probe_name, 'probe.py')
    spec = importlib.util.spec_from_file_location(f'{probe_name}_probe', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


KZ = load_probe('kernel_zero')
ROC = load_probe('row_ogf_cliff')


SMALL_PRIMES = (2, 3, 5)
SMALL_HEIGHTS = (5, 6)
SMALL_K = 100


# ==========================================================================
# kernel_zero primitives
# ==========================================================================

def test_kz_transducer_identity():
    fails = 0
    for K in (1, 5, 100):
        row = np.arange(K, dtype=np.float64)
        out = KZ.transducer_identity(row)
        if not np.array_equal(out, row):
            print(f'FAIL  kz transducer_identity changed row at K={K}')
            fails += 1
        if out is row:
            print(f'FAIL  kz transducer_identity returned same object at K={K}')
            fails += 1
    if fails == 0:
        print('PASS  kz transducer_identity preserves values, returns copy')
    return fails


def test_kz_transducer_reverse_involutive():
    fails = 0
    for K in (1, 2, 5, 100, 4000):
        row = np.arange(K, dtype=np.float64) + 0.5
        twice = KZ.transducer_reverse(KZ.transducer_reverse(row))
        if not np.array_equal(twice, row):
            print(f'FAIL  kz reverse² != row at K={K}')
            fails += 1
        once = KZ.transducer_reverse(row)
        for i in range(K):
            if once[i] != row[K - 1 - i]:
                print(f'FAIL  kz transducer_reverse off-by-one at K={K}, i={i}')
                fails += 1
                break
    if fails == 0:
        print('PASS  kz transducer_reverse involutive and σ(k)=K+1-k correct')
    return fails


def test_kz_transducers_immutable_on_input():
    fails = 0
    row = np.array([1.0, 2.0, 3.0, 4.0])
    snapshot = row.copy()
    KZ.transducer_identity(row)
    KZ.transducer_reverse(row)
    if not np.array_equal(row, snapshot):
        print(f'FAIL  kz transducer mutated input')
        fails += 1
    if fails == 0:
        print('PASS  kz transducers do not mutate input row')
    return fails


def test_kz_synth_uniform_row():
    fails = 0
    a = KZ.synth_uniform_row(K=50, seed=42)
    b = KZ.synth_uniform_row(K=50, seed=42)
    if not np.array_equal(a, b):
        print(f'FAIL  kz synth_uniform_row not deterministic')
        fails += 1
    r = KZ.synth_uniform_row(K=10000, seed=0, lo=-100.0, hi=100.0)
    if r.min() < -100.0 or r.max() > 100.0:
        print(f'FAIL  kz synth_uniform_row out of range')
        fails += 1
    if np.array_equal(KZ.synth_uniform_row(K=50, seed=0),
                       KZ.synth_uniform_row(K=50, seed=1)):
        print(f'FAIL  kz synth_uniform_row seed-independent')
        fails += 1
    if fails == 0:
        print('PASS  kz synth_uniform_row deterministic + bounded + seed-sensitive')
    return fails


def test_kz_algebra_row_matches_q_general():
    fails = 0
    checked = 0
    for p in SMALL_PRIMES:
        for h in SMALL_HEIGHTS:
            row = KZ.algebra_row(p, h, SMALL_K)
            for k in range(1, SMALL_K + 1):
                expected = float(q_general(p, h, k))
                if row[k - 1] != expected:
                    print(f'FAIL  kz algebra_row({p},{h})[{k-1}] != q_general')
                    fails += 1
                checked += 1
    if fails == 0:
        print(f'PASS  kz algebra_row == q_general row ({checked} cells)')
    return fails


def test_kz_predicted_zero_indices():
    fails = 0
    checked = 0
    for p in SMALL_PRIMES:
        for h in SMALL_HEIGHTS:
            Z = KZ.predicted_zero_indices(p, h, SMALL_K)
            for i in Z:
                k = int(i) + 1
                if q_general(p, h, k) != Fraction(0):
                    print(f'FAIL  kz predicted_zero_indices includes nonzero at k={k}')
                    fails += 1
            Z_set = set(int(i) for i in Z)
            for k in range(1, SMALL_K + 1):
                if q_general(p, h, k) == Fraction(0):
                    if (k - 1) not in Z_set:
                        print(f'FAIL  kz predicted_zero_indices misses k={k}')
                        fails += 1
                checked += 1
    if fails == 0:
        print(f'PASS  kz predicted_zero_indices == {{k : q_general == 0}} '
              f'({checked} cells)')
    return fails


def test_kz_predicted_multiset_sorted():
    fails = 0
    for p in SMALL_PRIMES:
        for h in SMALL_HEIGHTS:
            M = KZ.predicted_multiset(p, h, SMALL_K)
            if len(M) != SMALL_K or not np.all(M[:-1] <= M[1:]):
                print(f'FAIL  kz predicted_multiset({p},{h}) wrong')
                fails += 1
    if fails == 0:
        print('PASS  kz predicted_multiset sorted ascending, length K')
    return fails


def test_kz_verdict_from_strength():
    fails = 0
    cases = [
        (1.0, 'present'),
        (1.0 - 1e-16, 'present'),
        (0.0, 'absent'),
        (1e-16, 'absent'),
        (0.5, 'partial'),
        (0.99999, 'partial'),
        (1e-12, 'partial'),
    ]
    for s, expected in cases:
        if KZ._verdict_from_strength(s) != expected:
            print(f'FAIL  kz _verdict_from_strength({s}) != {expected}')
            fails += 1
    if fails == 0:
        print('PASS  kz _verdict_from_strength boundary cases')
    return fails


def test_kz_channels_canonical():
    fails = 0
    for p in SMALL_PRIMES:
        for h in SMALL_HEIGHTS:
            row = KZ.algebra_row(p, h, SMALL_K)
            for ch_name in ('no_op', 'zero_count', 'value_multiset',
                             'prime_row_identity_at_k1'):
                fn = KZ.CHANNELS[ch_name]
                v, s = fn(row, p, h)
                if v != 'present' or s != 1.0:
                    print(f'FAIL  kz {ch_name}({p},{h}) on algebra row: '
                          f'{v}/{s}')
                    fails += 1
    if fails == 0:
        print('PASS  kz channels on algebra row are PRESENT/1.0')
    return fails


def test_kz_channels_strengths_in_unit_interval():
    fails = 0
    rng = np.random.default_rng(1)
    rows = [
        KZ.algebra_row(2, 5, 50),
        np.zeros(50, dtype=np.float64),
        np.ones(50, dtype=np.float64),
        rng.uniform(-1.0, 1.0, size=50),
    ]
    for row in rows:
        for ch_name, fn in KZ.CHANNELS.items():
            v, s = fn(row, 2, 5)
            if not (0.0 <= s <= 1.0):
                print(f'FAIL  kz {ch_name} strength {s} out of [0,1]')
                fails += 1
            if v not in ('present', 'partial', 'absent'):
                print(f'FAIL  kz {ch_name} verdict {v!r} not valid')
                fails += 1
    if fails == 0:
        print('PASS  kz channel strengths in [0, 1] across canonical rows')
    return fails


# ==========================================================================
# row_ogf_cliff primitives
# ==========================================================================

ROC_PANEL = ROC.panel_cells()  # 16 cells
ROC_H = ROC.DEFAULT_H_MAX


def test_roc_transducer_identity():
    fails = 0
    for H in (1, 5, 9, 100):
        col = np.arange(H, dtype=np.float64) + 0.5
        out = ROC.transducer_identity(col)
        if not np.array_equal(out, col) or out is col:
            print(f'FAIL  roc transducer_identity at H={H}')
            fails += 1
    if fails == 0:
        print('PASS  roc transducer_identity preserves values, returns copy')
    return fails


def test_roc_transducer_scale_2x():
    fails = 0
    for H in (1, 5, 9, 100):
        col = np.arange(H, dtype=np.float64) + 0.5
        out = ROC.transducer_scale_2x(col)
        if not np.array_equal(out, 2 * col):
            print(f'FAIL  roc transducer_scale_2x at H={H}: not 2x')
            fails += 1
    # cliff invariance: c * 0 = 0
    z = np.zeros(9, dtype=np.float64)
    if not np.array_equal(ROC.transducer_scale_2x(z), z):
        print('FAIL  roc transducer_scale_2x does not preserve zeros')
        fails += 1
    if fails == 0:
        print('PASS  roc transducer_scale_2x doubles cells, preserves zeros')
    return fails


def test_roc_transducers_immutable_on_input():
    fails = 0
    col = np.array([1.0, -0.5, 0.333])
    snapshot = col.copy()
    ROC.transducer_identity(col)
    ROC.transducer_scale_2x(col)
    if not np.array_equal(col, snapshot):
        print('FAIL  roc transducer mutated input column')
        fails += 1
    if fails == 0:
        print('PASS  roc transducers do not mutate input column')
    return fails


def test_roc_synth_uniform_column():
    fails = 0
    a = ROC.synth_uniform_column(H_max=9, seed=42)
    b = ROC.synth_uniform_column(H_max=9, seed=42)
    if not np.array_equal(a, b):
        print('FAIL  roc synth_uniform_column not deterministic')
        fails += 1
    r = ROC.synth_uniform_column(H_max=10000, seed=0, lo=-100.0, hi=100.0)
    if r.min() < -100.0 or r.max() > 100.0:
        print('FAIL  roc synth_uniform_column out of range')
        fails += 1
    if fails == 0:
        print('PASS  roc synth_uniform_column deterministic + bounded')
    return fails


def test_roc_algebra_column_matches_q_general():
    fails = 0
    checked = 0
    for p, q, e in ROC_PANEL:
        col = ROC.algebra_column(p, q, e, ROC_H)
        for h in range(1, ROC_H + 1):
            expected = float(q_general(p, h, q ** e))
            if col[h - 1] != expected:
                print(f'FAIL  roc algebra_column({p},{q},{e})[{h-1}] != q_general')
                fails += 1
            checked += 1
    if fails == 0:
        print(f'PASS  roc algebra_column == q_general column ({checked} cells)')
    return fails


def test_roc_predicted_qe_closed():
    """predicted_qe_closed(e, H_max) implements (1-(1-x)^e)/e directly."""
    fails = 0
    for e in (1, 2, 3, 4, 5):
        closed = ROC.predicted_qe_closed(e, ROC_H)
        # closed[h - 1] = (-1)^(h-1) C(e, h) / e for h <= e, else 0
        for h in range(1, ROC_H + 1):
            if h <= e:
                expected = float(Fraction((-1) ** (h - 1) * comb(e, h), e))
            else:
                expected = 0.0
            if abs(closed[h - 1] - expected) > 1e-15:
                print(f'FAIL  roc predicted_qe_closed(e={e})[h={h}] = '
                      f'{closed[h-1]} != {expected}')
                fails += 1
    if fails == 0:
        print('PASS  roc predicted_qe_closed matches (-1)^(h-1) C(e,h)/e formula')
    return fails


def test_roc_predicted_leading_multinomial():
    """predicted_leading_multinomial(e) == (-1)^(e-1) / e."""
    fails = 0
    for e in (1, 2, 3, 4, 5, 10):
        got = ROC.predicted_leading_multinomial(e)
        want = (-1) ** (e - 1) / e
        if abs(got - want) > 1e-15:
            print(f'FAIL  roc predicted_leading_multinomial({e}) = {got} != {want}')
            fails += 1
    if fails == 0:
        print('PASS  roc predicted_leading_multinomial == (-1)^(e-1)/e')
    return fails


def test_roc_predicted_cliff_indices():
    """predicted_cliff_indices(e, H_max) == [e, e+1, ..., H_max - 1]."""
    fails = 0
    for e in (1, 2, 3, 4):
        cliff = ROC.predicted_cliff_indices(e, ROC_H)
        expected = np.arange(e, ROC_H, dtype=np.int64)
        if not np.array_equal(cliff, expected):
            print(f'FAIL  roc predicted_cliff_indices(e={e}) = {cliff} != {expected}')
            fails += 1
    if fails == 0:
        print('PASS  roc predicted_cliff_indices == [e, ..., H_max - 1]')
    return fails


def test_roc_verdict_from_strength():
    fails = 0
    cases = [(1.0, 'present'), (0.0, 'absent'), (0.5, 'partial')]
    for s, expected in cases:
        if ROC._verdict_from_strength(s) != expected:
            print(f'FAIL  roc _verdict_from_strength({s}) != {expected}')
            fails += 1
    if fails == 0:
        print('PASS  roc _verdict_from_strength boundary cases')
    return fails


def test_roc_channels_canonical():
    """Every channel on the algebra column reports PRESENT/1.0."""
    fails = 0
    for p, q, e in ROC_PANEL:
        col = ROC.algebra_column(p, q, e, ROC_H)
        for ch_name in ('no_op', 'cliff', 'leading_multinomial',
                         'qe_closed_form', 'prime_row_identity_at_h1'):
            fn = ROC.CHANNELS[ch_name]
            v, s = fn(col, p, q, e, ROC_H)
            if v != 'present' or s != 1.0:
                print(f'FAIL  roc {ch_name}({p},{q},{e}) on algebra col: '
                      f'{v}/{s}')
                fails += 1
    if fails == 0:
        print('PASS  roc channels on algebra column are PRESENT/1.0')
    return fails


def test_roc_cliff_under_scaling():
    """Under transducer_scale_2x, channel_cliff stays PRESENT (cliff is
    scale-invariant: c * 0 = 0)."""
    fails = 0
    for p, q, e in ROC_PANEL:
        col = ROC.algebra_column(p, q, e, ROC_H)
        col_scaled = ROC.transducer_scale_2x(col)
        v, s = ROC.channel_cliff(col_scaled, p, q, e, ROC_H)
        if v != 'present' or s != 1.0:
            print(f'FAIL  roc cliff({p},{q},{e}) under 2x: {v}/{s}')
            fails += 1
    if fails == 0:
        print('PASS  roc channel_cliff is scale-invariant under 2x')
    return fails


def test_roc_leading_multinomial_destroyed_by_scaling():
    """Under transducer_scale_2x, channel_leading_multinomial reports
    ABSENT (the leading coefficient scales by c)."""
    fails = 0
    for p, q, e in ROC_PANEL:
        col = ROC.algebra_column(p, q, e, ROC_H)
        col_scaled = ROC.transducer_scale_2x(col)
        v, s = ROC.channel_leading_multinomial(col_scaled, p, q, e, ROC_H)
        if v != 'absent' or s != 0.0:
            print(f'FAIL  roc leading_multinomial({p},{q},{e}) under 2x: '
                  f'{v}/{s}, expected absent/0')
            fails += 1
    if fails == 0:
        print('PASS  roc channel_leading_multinomial destroyed by 2x scaling')
    return fails


def test_roc_channels_strengths_in_unit_interval():
    fails = 0
    rng = np.random.default_rng(2)
    cols = [
        ROC.algebra_column(2, 3, 2, ROC_H),
        np.zeros(ROC_H, dtype=np.float64),
        np.ones(ROC_H, dtype=np.float64),
        rng.uniform(-1.0, 1.0, size=ROC_H),
    ]
    for col in cols:
        for ch_name, fn in ROC.CHANNELS.items():
            v, s = fn(col, 2, 3, 2, ROC_H)
            if not (0.0 <= s <= 1.0):
                print(f'FAIL  roc {ch_name} strength {s} out of [0,1]')
                fails += 1
            if v not in ('present', 'partial', 'absent'):
                print(f'FAIL  roc {ch_name} verdict {v!r} not valid')
                fails += 1
    if fails == 0:
        print('PASS  roc channel strengths in [0, 1] across canonical columns')
    return fails


def test_roc_companion_q_and_panel():
    fails = 0
    if ROC.companion_q(2) != 3:
        print('FAIL  roc companion_q(2) != 3'); fails += 1
    for p in (3, 5, 7, 11):
        if ROC.companion_q(p) != 2:
            print(f'FAIL  roc companion_q({p}) != 2'); fails += 1
    cells = ROC.panel_cells()
    if len(cells) != 16:
        print(f'FAIL  roc panel_cells default length {len(cells)} != 16')
        fails += 1
    # every cell has p ≠ q
    for p, q, e in cells:
        if p == q:
            print(f'FAIL  roc panel cell ({p},{q},{e}) has p == q')
            fails += 1
        if e < 1 or e > 4:
            print(f'FAIL  roc panel cell ({p},{q},{e}) e out of 1..4')
            fails += 1
    if fails == 0:
        print('PASS  roc companion_q + panel_cells contracts')
    return fails


def main():
    fails = 0
    # kernel_zero
    fails += test_kz_transducer_identity()
    fails += test_kz_transducer_reverse_involutive()
    fails += test_kz_transducers_immutable_on_input()
    fails += test_kz_synth_uniform_row()
    fails += test_kz_algebra_row_matches_q_general()
    fails += test_kz_predicted_zero_indices()
    fails += test_kz_predicted_multiset_sorted()
    fails += test_kz_verdict_from_strength()
    fails += test_kz_channels_canonical()
    fails += test_kz_channels_strengths_in_unit_interval()
    # row_ogf_cliff
    fails += test_roc_transducer_identity()
    fails += test_roc_transducer_scale_2x()
    fails += test_roc_transducers_immutable_on_input()
    fails += test_roc_synth_uniform_column()
    fails += test_roc_algebra_column_matches_q_general()
    fails += test_roc_predicted_qe_closed()
    fails += test_roc_predicted_leading_multinomial()
    fails += test_roc_predicted_cliff_indices()
    fails += test_roc_verdict_from_strength()
    fails += test_roc_channels_canonical()
    fails += test_roc_cliff_under_scaling()
    fails += test_roc_leading_multinomial_destroyed_by_scaling()
    fails += test_roc_channels_strengths_in_unit_interval()
    fails += test_roc_companion_q_and_panel()

    print()
    if fails == 0:
        print('ALL PRIMITIVE TESTS PASS')
        return 0
    print(f'TOTAL FAILS: {fails}')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
