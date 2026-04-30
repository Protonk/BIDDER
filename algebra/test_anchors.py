"""
test_anchors.py — exact validation of predict_q against canonical inputs.

Anchors (in order of strength):

A1.  Prime-row identity: Q_p(p^h * 1) = 1/h for all h >= 1.
     Direct from the master expansion: when shape = (1,) and tau_sig = (),
     coeff = (-1)^{j-1} C(h-1, j-1) / j and tau_j = 1. The classical
     identity sum_j (-1)^{j-1} C(h-1, j-1)/j = 1/h closes this.

A2.  The 8x6 (shape, tau_sig) matrix at h = 5, every cell, including
     gold-ring kernel zeros. This is the canonical algebraic fingerprint
     documented in q_h5_shape_tau_matrix.

A3.  Universal cliff: Q_n(n^2 * k) = 1 - d(k) / 2 for any n, k. Independent
     of shape(n) once h = 2 is fixed.

A4.  Master expansion vs. q_n_verify CSV: predict_q.q_general matches
     q_n_verify.master_q on all rows of payload_q_scan.csv (Fraction
     equality, not float).

If any anchor fails, this script exits non-zero and the closed-form
work cannot proceed — q_value_by_class and q_general are the substrate
for everything else.
"""

from __future__ import annotations

import csv
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from predict_q import (
    factor_tuple, q_general, q_value_by_class, shape_of, tau, tau_sig_of,
)


CSV_PATH = os.path.join(REPO, 'experiments', 'acm-flow', 'payload_q_scan.csv')


# --------------------------------------------------------------------------
# A1 -- prime-row 1/h identity
# --------------------------------------------------------------------------

def anchor_prime_row_one_over_h(h_max: int = 12) -> int:
    fails = 0
    for h in range(1, h_max + 1):
        got = q_value_by_class((1,), h, ())
        want = Fraction(1, h)
        if got != want:
            print(f'A1 FAIL  h={h}: q_value_by_class((1,), {h}, ()) = {got} != 1/{h}')
            fails += 1
    if fails == 0:
        print(f'A1 PASS  Q_p(p^h) = 1/h for h = 1..{h_max}')
    return fails


# --------------------------------------------------------------------------
# A2 -- 8x6 matrix at h = 5
# --------------------------------------------------------------------------

def anchor_matrix_h5() -> int:
    SHAPES = [
        (1,), (2,), (1, 1), (3,), (2, 1), (1, 1, 1), (4,), (3, 1),
    ]
    TAU_SIGS = [
        (), (1,), (2,), (1, 1), (3,), (1, 1, 1),
    ]
    # Cell-by-cell exact rationals at h = 5. Filled out by direct
    # computation from the master expansion below; values are then
    # reproduced by q_value_by_class. Computed and recorded once,
    # then frozen as the matrix anchor.
    expected = {
        # prime row -- 5 of 6 zeros from the alternating-binomial kernel
        ((1,), ()):           Fraction(1, 5),
        ((1,), (1,)):         Fraction(0),
        ((1,), (2,)):         Fraction(0),
        ((1,), (1, 1)):       Fraction(0),
        ((1,), (3,)):         Fraction(0),
        ((1,), (1, 1, 1)):    Fraction(0),

        # p^2 row -- linear-tau kernel kills the (1,) column
        ((2,), ()):           Fraction(1, 5),
        ((2,), (1,)):         Fraction(0),
        ((2,), (2,)):         Fraction(-3, 2),
        ((2,), (1, 1)):       Fraction(-3),
        ((2,), (3,)):         Fraction(-6),
        ((2,), (1, 1, 1)):    Fraction(-27),

        # pq row -- no kernel zeros
        ((1, 1), ()):         Fraction(6, 5),
        ((1, 1), (1,)):       Fraction(6),
        ((1, 1), (2,)):       Fraction(12),
        ((1, 1), (1, 1)):     Fraction(18),
        ((1, 1), (3,)):       Fraction(16),
        ((1, 1), (1, 1, 1)):  Fraction(30),

        # p^3 row -- linear-tau kernel kills (1,)
        ((3,), ()):           Fraction(8, 15),
        ((3,), (1,)):         Fraction(0),
        ((3,), (2,)):         Fraction(-5),
        ((3,), (1, 1)):       Fraction(-10),
        ((3,), (3,)):         Fraction(-56, 3),
        ((3,), (1, 1, 1)):    Fraction(-82),

        # p^2 q row -- no kernel zeros
        ((2, 1), ()):         Fraction(36, 5),
        ((2, 1), (1,)):       Fraction(24),
        ((2, 1), (2,)):       Fraction(42),
        ((2, 1), (1, 1)):     Fraction(60),
        ((2, 1), (3,)):       Fraction(52),
        ((2, 1), (1, 1, 1)):  Fraction(84),

        # pqr row -- no kernel zeros, large positive
        ((1, 1, 1), ()):           Fraction(126, 5),
        ((1, 1, 1), (1,)):         Fraction(90),
        ((1, 1, 1), (2,)):         Fraction(180),
        ((1, 1, 1), (1, 1)):       Fraction(270),
        ((1, 1, 1), (3,)):         Fraction(280),
        ((1, 1, 1), (1, 1, 1)):    Fraction(690),

        # p^4 row -- linear kernel breaks
        ((4,), ()):           Fraction(19, 20),
        ((4,), (1,)):         Fraction(-1),
        ((4,), (2,)):         Fraction(-13),
        ((4,), (1, 1)):       Fraction(-25),
        ((4,), (3,)):         Fraction(-43),
        ((4,), (1, 1, 1)):    Fraction(-181),

        # p^3 q row
        ((3, 1), ()):         Fraction(86, 5),
        ((3, 1), (1,)):       Fraction(50),
        ((3, 1), (2,)):       Fraction(80),
        ((3, 1), (1, 1)):     Fraction(110),
        ((3, 1), (3,)):       Fraction(88),
        ((3, 1), (1, 1, 1)):  Fraction(98),
    }
    H = 5
    fails = 0
    for shape in SHAPES:
        for tau_sig in TAU_SIGS:
            got = q_value_by_class(shape, H, tau_sig)
            want = expected[(shape, tau_sig)]
            if got != want:
                print(f'A2 FAIL  shape={shape} tau_sig={tau_sig}: got {got} != {want}')
                fails += 1
    if fails == 0:
        print(f'A2 PASS  8x6 (shape x tau_sig) matrix at h=5 ({len(SHAPES) * len(TAU_SIGS)} cells)')
    return fails


# --------------------------------------------------------------------------
# A3 -- universal h=2 cliff: Q_n(n^2 * k) = 1 - d(k) / 2
# --------------------------------------------------------------------------

def anchor_h2_cliff(n_max: int = 20, k_max: int = 30) -> int:
    """For every n >= 2 and every k coprime to n, Q_n(n^2 k) = 1 - d(k)/2."""
    fails = 0
    checked = 0
    for n in range(2, n_max + 1):
        for k in range(1, k_max + 1):
            if any(k % p == 0 for p, _e in factor_tuple(n)):
                continue
            got = q_general(n, 2, k)
            want = Fraction(1) - Fraction(tau(2, k), 2)
            checked += 1
            if got != want:
                print(f'A3 FAIL  n={n} k={k}: got {got} != 1 - d({k})/2 = {want}')
                fails += 1
    if fails == 0:
        print(f'A3 PASS  Q_n(n^2 k) = 1 - d(k)/2 ({checked} (n, k) pairs)')
    return fails


# --------------------------------------------------------------------------
# A4 -- payload_q_scan.csv full match
# --------------------------------------------------------------------------

def anchor_csv_match() -> int:
    if not os.path.exists(CSV_PATH):
        print(f'A4 SKIP  payload_q_scan.csv not present at {CSV_PATH}')
        return 0
    fails = 0
    rows = 0
    with open(CSV_PATH, newline='') as f:
        for r in csv.DictReader(f):
            n = int(r['n'])
            h = int(r['h'])
            k = int(r['k'])
            q_csv = Fraction(int(r['Q_num']), int(r['Q_den']))
            q_pred = q_general(n, h, k)
            rows += 1
            if q_pred != q_csv:
                if fails < 10:
                    print(f'A4 FAIL  n={n} h={h} k={k}: predict_q {q_pred} != CSV {q_csv}')
                fails += 1
    if fails == 0:
        print(f'A4 PASS  predict_q.q_general matches payload_q_scan.csv on all {rows} rows')
    else:
        print(f'A4 FAIL  {fails} mismatches across {rows} rows')
    return fails


# --------------------------------------------------------------------------
# A5 -- consistency: q_general agrees with q_value_by_class on coprime k
# --------------------------------------------------------------------------

def anchor_q_general_vs_class() -> int:
    """For (n, k) with gcd(k, n) = 1, q_general(n, h, k) == q_value_by_class(shape(n), h, tau_sig(k))."""
    fails = 0
    checked = 0
    for n in range(2, 25):
        n_primes = {p for p, _e in factor_tuple(n)}
        for k in range(1, 60):
            if any(k % p == 0 for p in n_primes):
                continue
            for h in range(1, 6):
                got_general = q_general(n, h, k)
                got_class = q_value_by_class(shape_of(n), h, tau_sig_of(k))
                checked += 1
                if got_general != got_class:
                    if fails < 10:
                        print(f'A5 FAIL  n={n} k={k} h={h}: general {got_general} != class {got_class}')
                    fails += 1
    if fails == 0:
        print(f'A5 PASS  q_general == q_value_by_class on coprime (n, k) ({checked} cases)')
    return fails


# --------------------------------------------------------------------------
# A6 -- displayed h=3 tables (prime / prime-power / squarefree multi-prime)
# --------------------------------------------------------------------------

def anchor_h3_displayed_tables() -> int:
    """Freeze the specific (n, k, Q) values displayed at h=3 in
    algebra/Q-FORMULAS.md across the three factorisation types.

    A4 already verifies q_general against payload_q_scan.csv, but A4
    only checks the implementation against itself; if a typo enters
    either the formula sheet or q_value_by_class without invalidating
    the master expansion, A4 won't catch it. A6 freezes the *displayed*
    values from the formula sheet so a divergence between the human
    table and the implementation is caught as a FAIL.

    Tables covered (Q-FORMULAS.md sections "Prime n", "Prime Powers",
    "Squarefree Multi-Prime n"):
      - Prime n at h=3: 1/h identity at k=1, low-payload zero band
        at k in {q, q^2, qr} for primes q, r != p.
      - Prime power n=4 at h=3: t=0 sub-cases (k coprime to 2) and
        t=1 sub-cases (k = 2 * k' with k' coprime to 2).
      - Squarefree multi-prime n=6, n=10 at h=3 with (0, 0) overlap
        (k coprime to n): k' in {1, q, q^2, qr}.
    """
    cases = [
        # Prime n at h=3: Q_p(p^3 k) = 1 - d(k) + tau_3(k)/3.
        # k=1 -> 1/h; k in {q, q^2, qr} -> 0 (low-payload zero band).
        (3, 3, 1, Fraction(1, 3)),    # 1/h identity
        (3, 3, 2, Fraction(0)),       # k = q
        (3, 3, 4, Fraction(0)),       # k = q^2
        (3, 3, 10, Fraction(0)),      # k = qr (q=2, r=5)
        (5, 3, 1, Fraction(1, 3)),
        (5, 3, 2, Fraction(0)),
        (5, 3, 4, Fraction(0)),
        (5, 3, 6, Fraction(0)),       # k = qr (q=2, r=3)
        (7, 3, 1, Fraction(1, 3)),
        (7, 3, 6, Fraction(0)),

        # Prime power n=4 at h=3, t=0 (k coprime to 2):
        # Q_4 = 1 - 3 d(k')/2 + tau_3(k')/3.
        (4, 3, 1, Fraction(-1, 6)),   # k'=1: 1 - 3/2 + 1/3 = -1/6
        (4, 3, 3, Fraction(-1)),      # k'=q=3: 1 - 3 + 1 = -1
        (4, 3, 5, Fraction(-1)),      # k'=q=5: same shape

        # Prime power n=4 at h=3, t=1 (k = 2 * k' with k' coprime to 2):
        # Q_4 = 1 - 2 d(k') + tau_3(k').
        (4, 3, 2, Fraction(0)),       # k=2 (k'=1): 1 - 2 + 1 = 0
        (4, 3, 6, Fraction(0)),       # k=6 (k'=3): 1 - 4 + 3 = 0
        (4, 3, 10, Fraction(0)),      # k=10 (k'=5): same

        # Squarefree multi-prime n=6 at h=3, (0,0) overlap
        # (k coprime to 6, k = k'): Q_6 = 1 - 2 d(k') + tau_3(k')/3.
        (6, 3, 1, Fraction(-2, 3)),   # k'=1: 1 - 2 + 1/3 = -2/3
        (6, 3, 5, Fraction(-2)),      # k'=q=5: 1 - 4 + 1 = -2
        (6, 3, 25, Fraction(-3)),     # k'=q^2=25: 1 - 6 + 2 = -3
        (6, 3, 35, Fraction(-4)),     # k'=qr=5*7: 1 - 8 + 3 = -4

        # Squarefree multi-prime n=10 at h=3, (0,0) overlap
        # (k coprime to 10).
        (10, 3, 1, Fraction(-2, 3)),
        (10, 3, 3, Fraction(-2)),     # k'=q=3
        (10, 3, 9, Fraction(-3)),     # k'=q^2=9
        (10, 3, 21, Fraction(-4)),    # k'=qr=3*7
    ]
    fails = 0
    for n, h, k, want in cases:
        got = q_general(n, h, k)
        if got != want:
            print(f'A6 FAIL  n={n} h={h} k={k}: q_general = {got}, '
                  f'displayed table says {want}')
            fails += 1
    if fails == 0:
        print(f'A6 PASS  Q-FORMULAS.md h=3 displayed tables match q_general '
              f'({len(cases)} cells across prime / prime-power / squarefree)')
    return fails


def main():
    fails = 0
    fails += anchor_prime_row_one_over_h()
    fails += anchor_matrix_h5()
    fails += anchor_h2_cliff()
    fails += anchor_q_general_vs_class()
    fails += anchor_h3_displayed_tables()
    fails += anchor_csv_match()

    print()
    if fails == 0:
        print('ALL ANCHORS PASS')
        return 0
    print(f'TOTAL FAILS: {fails}')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
