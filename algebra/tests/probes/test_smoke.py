"""
test_smoke.py — fast import + canonical-input smoke for the probes.

One assertion per public symbol in each probe's module. Goal: catch
import errors, missing lattice files, dependency drift, silent
renames. Not a correctness gate — that lives in test_anchors.py and
test_consistency.py.

A failure here means the probes layer doesn't load, a public symbol
no longer behaves on the simplest input it should accept, or a
required substrate file is missing. Read the import line that failed.

Run:

    sage -python algebra/tests/probes/test_smoke.py
"""

from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.dirname(HERE)
ALGEBRA = os.path.dirname(TESTS)
REPO = os.path.dirname(ALGEBRA)
sys.path.insert(0, ALGEBRA)
sys.path.insert(0, os.path.join(REPO, 'experiments', 'probes', 'kernel_zero'))

# kernel_zero probe
from probe import (  # noqa: E402
    CHANNEL_ORDER, CHANNELS, DEFAULT_HEIGHTS, DEFAULT_K,
    DEFAULT_LATTICE_DIR, DEFAULT_PRIMES, TOL, TRANSDUCERS,
    algebra_row, channel_no_op, channel_prime_row_identity_at_k1,
    channel_value_multiset, channel_zero_count, expected_verdicts,
    figure_lattice_diff, figure_reversal_symmetry,
    figure_verdict_matrix, lattice_row, make_figures,
    predicted_multiset, predicted_zero_indices, run_probe,
    synth_uniform_row, transducer_identity, transducer_reverse,
)


LATTICE_H6 = os.path.join(DEFAULT_LATTICE_DIR, 'q_lattice_4000_h6.npy')


def main() -> int:
    fails = 0

    def check(name, cond, detail=''):
        nonlocal fails
        if not cond:
            print(f'SMOKE FAIL  {name}: {detail}')
            fails += 1

    # constants
    check('CHANNEL_ORDER tuple of 4',
          isinstance(CHANNEL_ORDER, tuple) and len(CHANNEL_ORDER) == 4)
    check('CHANNELS keys match CHANNEL_ORDER',
          set(CHANNELS.keys()) == set(CHANNEL_ORDER))
    check('TRANSDUCERS has identity', 'identity' in TRANSDUCERS)
    check('TRANSDUCERS has reverse', 'reverse' in TRANSDUCERS)
    check('TOL is positive float',
          isinstance(TOL, float) and 0 < TOL < 1)
    check('DEFAULT_PRIMES non-empty', len(DEFAULT_PRIMES) > 0)
    check('DEFAULT_HEIGHTS non-empty', len(DEFAULT_HEIGHTS) > 0)
    check('DEFAULT_K positive', DEFAULT_K > 0)

    # transducers
    row = np.array([1.0, 2.0, 3.0, 4.0])
    check('transducer_identity returns ndarray',
          isinstance(transducer_identity(row), np.ndarray))
    check('transducer_identity preserves',
          np.array_equal(transducer_identity(row), row))
    check('transducer_identity returns copy',
          transducer_identity(row) is not row)
    rev = transducer_reverse(row)
    check('transducer_reverse reverses',
          np.array_equal(rev, np.array([4.0, 3.0, 2.0, 1.0])))

    # substrate generators
    sr = synth_uniform_row(K=10, seed=0)
    check('synth_uniform_row length', len(sr) == 10)
    check('synth_uniform_row dtype is float64',
          sr.dtype == np.float64)
    check('synth_uniform_row deterministic',
          np.array_equal(sr, synth_uniform_row(K=10, seed=0)))

    ar = algebra_row(2, 3, 5)
    check('algebra_row length', len(ar) == 5)
    check('algebra_row dtype is float64', ar.dtype == np.float64)
    # Q_2(2^3 * 1) = 1/3 by C2.
    check('algebra_row first cell', abs(ar[0] - 1/3) < 1e-15)

    # lattice_row only if the committed lattice exists
    if os.path.exists(LATTICE_H6):
        lr = lattice_row(2, 6, DEFAULT_LATTICE_DIR, 10)
        check('lattice_row length', len(lr) == 10)
        check('lattice_row dtype is float64', lr.dtype == np.float64)
        check('lattice_row first cell == 1/6 (h=6 prime row at k=1)',
              abs(lr[0] - 1/6) < 1e-15)
    else:
        print(f'SMOKE NOTE  lattice file not present at {LATTICE_H6}; '
              f'skipping lattice_row check')

    # predicted-set helpers
    Z = predicted_zero_indices(2, 5, 50)
    check('predicted_zero_indices is ndarray', isinstance(Z, np.ndarray))
    check('predicted_zero_indices integer dtype',
          np.issubdtype(Z.dtype, np.integer))
    M = predicted_multiset(2, 5, 50)
    check('predicted_multiset length', len(M) == 50)
    check('predicted_multiset sorted ascending',
          np.all(M[:-1] <= M[1:]))

    # channels — each returns (verdict_str, float)
    canon_row = algebra_row(2, 5, 50)
    for name, fn in [('channel_no_op', channel_no_op),
                     ('channel_zero_count', channel_zero_count),
                     ('channel_value_multiset', channel_value_multiset),
                     ('channel_prime_row_identity_at_k1',
                      channel_prime_row_identity_at_k1)]:
        v, s = fn(canon_row, 2, 5)
        check(f'{name} returns verdict str',
              v in ('present', 'partial', 'absent'))
        check(f'{name} returns float strength',
              isinstance(s, float) and 0.0 <= s <= 1.0)

    # expected_verdicts: known calibration configs
    ev_id = expected_verdicts({'substrate': 'lattice', 'transducer': 'identity'})
    check('expected_verdicts identity all present',
          ev_id is not None and all(v == 'present' for v in ev_id.values()))
    ev_rev = expected_verdicts({'substrate': 'lattice', 'transducer': 'reverse'})
    check('expected_verdicts reverse no_op partial',
          ev_rev is not None and ev_rev['no_op'] == 'partial')
    ev_null = expected_verdicts(
        {'substrate': 'synth_uniform', 'transducer': 'identity'})
    check('expected_verdicts null all absent',
          ev_null is not None and all(v == 'absent' for v in ev_null.values()))
    ev_unknown = expected_verdicts({'substrate': 'foo', 'transducer': 'bar'})
    check('expected_verdicts unknown returns None', ev_unknown is None)

    # figure functions exist (import sanity)
    check('figure_verdict_matrix is callable', callable(figure_verdict_matrix))
    check('figure_lattice_diff is callable', callable(figure_lattice_diff))
    check('figure_reversal_symmetry is callable',
          callable(figure_reversal_symmetry))
    check('make_figures is callable', callable(make_figures))

    # run_probe is callable
    check('run_probe is callable', callable(run_probe))

    if fails == 0:
        print('SMOKE PASS  all canonical-input checks (kernel_zero)')
        return 0
    print(f'SMOKE FAIL  {fails} check(s) failed')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
