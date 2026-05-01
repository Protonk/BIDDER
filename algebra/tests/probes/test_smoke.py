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

import importlib.util
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.dirname(HERE)
ALGEBRA = os.path.dirname(TESTS)
REPO = os.path.dirname(ALGEBRA)
sys.path.insert(0, ALGEBRA)


def load_probe(probe_name: str):
    """Load <probes>/<probe_name>/probe.py as a uniquely-named module so
    multiple probes can be imported in the same test process without
    name collisions."""
    path = os.path.join(REPO, 'experiments', 'probes', probe_name, 'probe.py')
    spec = importlib.util.spec_from_file_location(f'{probe_name}_probe', path)
    mod = importlib.util.module_from_spec(spec)
    # The probe.py adds its own directory to sys.path on import for its
    # algebra-side imports; let it run.
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    fails = 0

    def check(name, cond, detail=''):
        nonlocal fails
        if not cond:
            print(f'SMOKE FAIL  {name}: {detail}')
            fails += 1

    # ----------------------------------------------------------------------
    # kernel_zero probe
    # ----------------------------------------------------------------------
    kz = load_probe('kernel_zero')

    check('kernel_zero CHANNEL_ORDER tuple of 4',
          isinstance(kz.CHANNEL_ORDER, tuple) and len(kz.CHANNEL_ORDER) == 4)
    check('kernel_zero CHANNELS keys match CHANNEL_ORDER',
          set(kz.CHANNELS.keys()) == set(kz.CHANNEL_ORDER))
    check('kernel_zero TRANSDUCERS has identity',
          'identity' in kz.TRANSDUCERS)
    check('kernel_zero TRANSDUCERS has reverse',
          'reverse' in kz.TRANSDUCERS)
    check('kernel_zero TOL is positive float',
          isinstance(kz.TOL, float) and 0 < kz.TOL < 1)

    # transducers
    row = np.array([1.0, 2.0, 3.0, 4.0])
    check('kernel_zero transducer_identity preserves',
          np.array_equal(kz.transducer_identity(row), row))
    check('kernel_zero transducer_reverse reverses',
          np.array_equal(kz.transducer_reverse(row),
                         np.array([4.0, 3.0, 2.0, 1.0])))

    # substrate generators
    sr = kz.synth_uniform_row(K=10, seed=0)
    check('kernel_zero synth_uniform_row length', len(sr) == 10)
    check('kernel_zero synth_uniform_row deterministic',
          np.array_equal(sr, kz.synth_uniform_row(K=10, seed=0)))

    ar = kz.algebra_row(2, 3, 5)
    check('kernel_zero algebra_row first cell', abs(ar[0] - 1/3) < 1e-15)

    # lattice_row only if committed h=6 lattice exists
    lat_h6 = os.path.join(kz.DEFAULT_LATTICE_DIR, 'q_lattice_4000_h6.npy')
    if os.path.exists(lat_h6):
        lr = kz.lattice_row(2, 6, kz.DEFAULT_LATTICE_DIR, 10)
        check('kernel_zero lattice_row first cell == 1/6',
              abs(lr[0] - 1/6) < 1e-15)
    else:
        print(f'SMOKE NOTE  kernel_zero lattice file not present at {lat_h6}; '
              f'skipping lattice_row check')

    # predicted-set helpers
    Z = kz.predicted_zero_indices(2, 5, 50)
    check('kernel_zero predicted_zero_indices is ndarray',
          isinstance(Z, np.ndarray))
    M = kz.predicted_multiset(2, 5, 50)
    check('kernel_zero predicted_multiset sorted ascending',
          np.all(M[:-1] <= M[1:]))

    # channels
    canon_row = kz.algebra_row(2, 5, 50)
    for name, fn in [('no_op', kz.channel_no_op),
                     ('zero_count', kz.channel_zero_count),
                     ('value_multiset', kz.channel_value_multiset),
                     ('prime_row_identity_at_k1',
                      kz.channel_prime_row_identity_at_k1)]:
        v, s = fn(canon_row, 2, 5)
        check(f'kernel_zero channel_{name} returns valid verdict',
              v in ('present', 'partial', 'absent'))
        check(f'kernel_zero channel_{name} returns float strength in [0, 1]',
              isinstance(s, float) and 0.0 <= s <= 1.0)

    # expected_verdicts
    ev_id = kz.expected_verdicts({'substrate': 'lattice', 'transducer': 'identity'})
    check('kernel_zero expected_verdicts identity all present',
          ev_id is not None and all(v == 'present' for v in ev_id.values()))
    ev_rev = kz.expected_verdicts({'substrate': 'lattice', 'transducer': 'reverse'})
    check('kernel_zero expected_verdicts reverse no_op partial',
          ev_rev is not None and ev_rev['no_op'] == 'partial')

    check('kernel_zero run_probe is callable', callable(kz.run_probe))
    check('kernel_zero make_figures is callable', callable(kz.make_figures))

    # ----------------------------------------------------------------------
    # row_ogf_cliff probe
    # ----------------------------------------------------------------------
    roc = load_probe('row_ogf_cliff')

    check('row_ogf_cliff CHANNEL_ORDER tuple of 5',
          isinstance(roc.CHANNEL_ORDER, tuple) and len(roc.CHANNEL_ORDER) == 5)
    check('row_ogf_cliff CHANNELS keys match CHANNEL_ORDER',
          set(roc.CHANNELS.keys()) == set(roc.CHANNEL_ORDER))
    check('row_ogf_cliff TRANSDUCERS has identity',
          'identity' in roc.TRANSDUCERS)
    check('row_ogf_cliff TRANSDUCERS has scale_2x',
          'scale_2x' in roc.TRANSDUCERS)
    check('row_ogf_cliff TOL is positive float',
          isinstance(roc.TOL, float) and 0 < roc.TOL < 1)
    check('row_ogf_cliff DEFAULT_C is 2', roc.DEFAULT_C == 2)
    check('row_ogf_cliff DEFAULT_H_MAX is positive', roc.DEFAULT_H_MAX > 0)

    # transducers
    col = np.array([1.0, -0.5, 0.333, 0.0, 0.0])
    check('row_ogf_cliff transducer_identity preserves',
          np.array_equal(roc.transducer_identity(col), col))
    check('row_ogf_cliff transducer_scale_2x doubles',
          np.array_equal(roc.transducer_scale_2x(col), 2 * col))
    # cliff invariance: c * 0 = 0
    check('row_ogf_cliff transducer_scale_2x preserves zeros',
          np.array_equal(roc.transducer_scale_2x(np.zeros(5)), np.zeros(5)))

    # substrate generators
    ac = roc.algebra_column(2, 3, 2, 9)  # k' = 9 = 3^2, p = 2
    check('row_ogf_cliff algebra_column length', len(ac) == 9)
    check('row_ogf_cliff algebra_column dtype float64', ac.dtype == np.float64)
    check('row_ogf_cliff algebra_column first cell == 1 (Q_p(p k\') always)',
          abs(ac[0] - 1.0) < 1e-15)

    sc = roc.synth_uniform_column(H_max=9, seed=0)
    check('row_ogf_cliff synth_uniform_column length', len(sc) == 9)
    check('row_ogf_cliff synth_uniform_column deterministic',
          np.array_equal(sc, roc.synth_uniform_column(H_max=9, seed=0)))

    # closed-form predictions
    closed = roc.predicted_qe_closed(2, 9)
    # F(x; p, q^2) = (1 - (1-x)^2)/2 = x - x²/2 → coeffs [1, -1/2, 0, 0, ...]
    check('row_ogf_cliff predicted_qe_closed e=2 first cell',
          abs(closed[0] - 1.0) < 1e-15)
    check('row_ogf_cliff predicted_qe_closed e=2 second cell',
          abs(closed[1] + 0.5) < 1e-15)
    check('row_ogf_cliff predicted_qe_closed e=2 cliff cells zero',
          np.all(closed[2:] == 0.0))

    lm = roc.predicted_leading_multinomial(3)
    # (-1)^(3-1) / 3 = 1/3
    check('row_ogf_cliff predicted_leading_multinomial e=3',
          abs(lm - 1/3) < 1e-15)

    cliff_idx = roc.predicted_cliff_indices(2, 9)
    check('row_ogf_cliff predicted_cliff_indices e=2',
          np.array_equal(cliff_idx, np.array([2, 3, 4, 5, 6, 7, 8])))

    # channels
    canon_col = roc.algebra_column(2, 3, 2, 9)
    for name, fn in [('no_op', roc.channel_no_op),
                     ('cliff', roc.channel_cliff),
                     ('leading_multinomial', roc.channel_leading_multinomial),
                     ('qe_closed_form', roc.channel_qe_closed_form),
                     ('prime_row_identity_at_h1',
                      roc.channel_prime_row_identity_at_h1)]:
        v, s = fn(canon_col, 2, 3, 2, 9)
        check(f'row_ogf_cliff channel_{name} returns valid verdict',
              v in ('present', 'partial', 'absent'))
        check(f'row_ogf_cliff channel_{name} returns float strength in [0, 1]',
              isinstance(s, float) and 0.0 <= s <= 1.0)

    # expected_verdicts
    ev_id = roc.expected_verdicts(
        {'substrate': 'algebra', 'transducer': 'identity'})
    check('row_ogf_cliff expected_verdicts identity all present',
          ev_id is not None and all(v == 'present' for v in ev_id.values()))
    ev_scale = roc.expected_verdicts(
        {'substrate': 'algebra', 'transducer': 'scale_2x'})
    check('row_ogf_cliff expected_verdicts scale_2x cliff PRESENT',
          ev_scale is not None and ev_scale['cliff'] == 'present')
    check('row_ogf_cliff expected_verdicts scale_2x leading_multinomial ABSENT',
          ev_scale is not None and ev_scale['leading_multinomial'] == 'absent')

    check('row_ogf_cliff run_probe is callable', callable(roc.run_probe))
    check('row_ogf_cliff make_figures is callable', callable(roc.make_figures))

    # panel helper
    check('row_ogf_cliff companion_q(2) == 3', roc.companion_q(2) == 3)
    check('row_ogf_cliff companion_q(3) == 2', roc.companion_q(3) == 2)
    check('row_ogf_cliff companion_q(7) == 2', roc.companion_q(7) == 2)
    cells = roc.panel_cells()
    check('row_ogf_cliff panel_cells default length 16', len(cells) == 16)

    if fails == 0:
        print('SMOKE PASS  all canonical-input checks (kernel_zero, row_ogf_cliff)')
        return 0
    print(f'SMOKE FAIL  {fails} check(s) failed')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
