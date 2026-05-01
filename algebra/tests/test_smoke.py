"""
test_smoke.py — fast import + canonical-input smoke for the algebra.

One assertion per public symbol in predict_q.py and predict_correlation.py.
Goal: catch import errors, missing modules, dependency drift, silent
renames, and "the wheel is off" regressions in milliseconds. Not a
correctness gate — that lives in test_anchors.py and test_consistency.py.

A failure here means the algebra layer doesn't load or a public symbol
no longer behaves on the simplest input it should accept. Read the
import line that failed.

Run:

    python3 algebra/tests/test_smoke.py
"""

from __future__ import annotations

import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ALGEBRA = os.path.dirname(HERE)
sys.path.insert(0, ALGEBRA)

from predict_q import (  # noqa: E402
    big_omega, count_ordered_factorizations_into_multiples,
    decompose, factor_tuple, little_omega, n_adic_height,
    q_general, q_row, q_value_by_class,
    row_polynomial, row_polynomial_qe_closed, row_sum,
    shape_of, tau, tau_sig_of,
)
from predict_correlation import (  # noqa: E402
    autocorr_profile, autocorr_profile_from_row, class_decomposition,
    class_of, direct_autocorr, q_for_class,
)


def main():
    fails = 0

    def check(name, cond, detail=''):
        nonlocal fails
        if not cond:
            print(f'SMOKE FAIL  {name}: {detail}')
            fails += 1

    # predict_q primitives
    check('factor_tuple(12)', factor_tuple(12) == ((2, 2), (3, 1)))
    check('factor_tuple(1)', factor_tuple(1) == ())
    check('shape_of(12)', shape_of(12) == (2, 1))
    check('shape_of(1)', shape_of(1) == ())
    check('tau_sig_of(12)', tau_sig_of(12) == (2, 1))
    check('tau(2, 12)', tau(2, 12) == 6)
    check('tau(1, 100)', tau(1, 100) == 1)
    check('n_adic_height(2, 8)', n_adic_height(2, 8) == 3)
    check('n_adic_height(6, 36)', n_adic_height(6, 36) == 2)
    check('decompose(6, 12)', decompose(6, 12) == (((2, 1), (3, 1)), (2, 1), 1))
    check('big_omega(12)', big_omega(12) == 3)
    check('big_omega(1)', big_omega(1) == 0)
    check('little_omega(12)', little_omega(12) == 2)
    check('little_omega(1)', little_omega(1) == 0)

    # predict_q Q-values
    qg = q_general(2, 3, 1)
    check('q_general(2, 3, 1)', qg == Fraction(1, 3),
          f'got {qg}, expected 1/3')
    check('q_general type', isinstance(qg, Fraction))
    check('q_general(_, 0, _) == 0', q_general(2, 0, 5) == Fraction(0))

    qc = q_value_by_class((1,), 5, ())
    check('q_value_by_class((1,), 5, ())', qc == Fraction(1, 5))

    qr = q_row(2, 3, 5)
    check('q_row length', len(qr) == 5)
    check('q_row first cell', isinstance(qr[0], float))

    # predict_q row-OGF
    rp = row_polynomial(2, 9)  # q^2 with q=3
    check('row_polynomial(2, 9) length', len(rp) == 2)
    rpc = row_polynomial_qe_closed(2)
    check('row_polynomial_qe_closed(2)',
          rpc == [Fraction(1, 1), Fraction(-1, 2)],
          f'got {rpc}')
    check('row_sum(2, 9)', row_sum(2, 9) == Fraction(1, 2))
    check('row_sum(2, 15)', row_sum(2, 15) == Fraction(0))  # omega = 2

    # predict_q C4 enumerator
    n_2_8_3 = count_ordered_factorizations_into_multiples(2, 8, 3)
    check('count_ordered_factorizations(2, 8, 3)', n_2_8_3 == 1,
          f'got {n_2_8_3}, expected 1 (only (2,2,2))')

    # predict_correlation
    cls = class_of(2, 12)
    check('class_of(2, 12)', cls == ((2,), (1,)),
          f'got {cls}')
    qcls = q_for_class((1,), 3, (0,), ())
    check('q_for_class', qcls == Fraction(1, 3))
    da = direct_autocorr(2, 3, 1, 50)
    check('direct_autocorr type', isinstance(da, float))
    ap = autocorr_profile(2, 3, [1, 2], 50)
    check('autocorr_profile keys', set(ap.keys()) == {1, 2})
    apr = autocorr_profile_from_row([1.0, 0.5, 0.25, 0.125, 0.0625], [1, 2])
    check('autocorr_profile_from_row keys', set(apr.keys()) == {1, 2})
    cd = class_decomposition(2, 3, 1, 50, top_n=4)
    check('class_decomposition has autocorr', 'autocorr' in cd)
    check('class_decomposition has pairs', 'pairs' in cd)

    if fails == 0:
        print('SMOKE PASS  all canonical-input checks')
        return 0
    print(f'SMOKE FAIL  {fails} check(s) failed')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
