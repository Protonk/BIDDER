"""
test_anchors.py — exact validation of predict_q against canonical inputs.

Each anchor cites the canonical doc that states the theorem; the
implementation in predict_q.py must reproduce the theorem's value at
the listed inputs in exact Fraction arithmetic.

A1.  Prime-row identity Q_p(p^h * 1) = 1/h for all h >= 1.
     Source: MASTER-EXPANSION.md "Corollaries" (prime-row 1/h identity).

A2.  The 8x6 (shape, tau_sig) matrix at h = 5, every cell.
     Source: KERNEL-ZEROS.md "(shape, tau-signature) matrices" (h=5).

A3.  Universal cliff Q_n(n^2 * k) = 1 - d(k) / 2 for n >= 2 and
     k coprime to n. (Hypothesis gcd(k,n)=1 is required: when k
     carries factors of n the height exceeds 2.)
     Source: UNIVERSAL-CLIFF.md.

A4.  Master expansion vs. payload_q_scan.csv on every row (24,203 rows).
     Source: MASTER-EXPANSION.md and RANK-LEMMA.md.

A5.  q_general agrees with q_value_by_class on coprime (n, k).
     Source: MASTER-EXPANSION.md (consistency between general and
     class-form evaluators).

A6.  TABLES.md h=3 displayed cells match q_general
     (prime / prime-power / squarefree multi-prime).
     Source: TABLES.md.

A7.  Kernel-zero classifier (prime n).
     For prime shape and h in [2, 8]: k >= 2 coprime to p with
     Omega(k) <= h - 1 gives Q = 0; Omega(k) = h gives
     Q = (-1)^(h-1) (h-1)! / prod e_i!; no accidental zeros at
     Omega in [h+1, 13].
     Source: KERNEL-ZEROS.md.

A8.  The 8 x 6 (shape, tau_sig) matrices at h = 6, 7, 8, every cell.
     Source: KERNEL-ZEROS.md "(shape, tau-signature) matrices".

A9.  Denominator bound: denom(Q_n(m)) divides lcm(1, ..., nu_n(m)).
     Source: DENOMINATOR-BOUND.md.

A10. Prime-row OGF: F(x; p, k') = sum_{h>=1} Q_p(p^h k') x^h has
     degree exactly Omega(k') for k' >= 2 coprime to p; leading
     coefficient matches the KERNEL-ZEROS.md boundary formula;
     row_polynomial_qe_closed cross-check on q^e cofactors;
     row_sum closed form 1/e or 0.
     Source: ROW-OGF.md.

If any anchor fails, this script exits non-zero and the closed-form
work cannot proceed — q_value_by_class and q_general are the substrate
for everything else.
"""

from __future__ import annotations

import csv
import os
import sys
from fractions import Fraction
from math import factorial, gcd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from predict_q import (
    big_omega, factor_tuple, little_omega, q_general, q_value_by_class,
    row_polynomial, row_polynomial_qe_closed, row_sum,
    shape_of, tau, tau_sig_of,
)


def _lcm(a, b):
    return a * b // gcd(a, b)


def _lcm_range(n):
    out = 1
    for i in range(1, n + 1):
        out = _lcm(out, i)
    return out


def _partitions(n, max_part=None):
    """Integer partitions of n in descending-part form."""
    if max_part is None:
        max_part = n
    if n == 0:
        yield ()
        return
    for first in range(min(n, max_part), 0, -1):
        for rest in _partitions(n - first, first):
            yield (first,) + rest


CSV_PATH = os.path.join(REPO, 'experiments', 'acm', 'flow', 'payload_q_scan.csv')


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
    algebra/TABLES.md across the three factorisation types.

    A4 already verifies q_general against payload_q_scan.csv, but A4
    only checks the implementation against itself; if a typo enters
    either the table or q_value_by_class without invalidating the
    master expansion, A4 won't catch it. A6 freezes the *displayed*
    values from TABLES.md so a divergence between the displayed
    table and the implementation is caught as a FAIL.

    Tables covered (TABLES.md sections "Prime n", "Prime power n =
    p^a, a >= 2", "Squarefree multi-prime n, r >= 2"):
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
        print(f'A6 PASS  TABLES.md h=3 displayed tables match q_general '
              f'({len(cases)} cells across prime / prime-power / squarefree)')
    return fails


# --------------------------------------------------------------------------
# A7 -- kernel-zero classifier (prime n)
# --------------------------------------------------------------------------

def anchor_kernel_zero_classifier(h_max: int = 8, omega_max: int = 13) -> int:
    """Prime-n kernel-zero theorem (algebra/KERNEL-ZEROS.md).

    For every h in [2, h_max] and every k >= 2 coprime to p:
      (i)  Omega(k) <= h - 1  =>  Q_p(p^h k) = 0.
      (ii) Omega(k) == h      =>  Q_p(p^h k) = (-1)^(h-1) (h-1)! / prod e_i!.
      (iii) Omega(k) in [h+1, omega_max] => Q_p(p^h k) != 0.

    Tested via q_value_by_class on shape = (1,) over every partition of
    every Omega in [1, omega_max]. Coverage independent of any specific
    prime p (the master expansion at shape (1,) does not see p).
    """
    fails = 0
    checked = 0
    shape = (1,)
    for h in range(2, h_max + 1):
        # (i) below the kernel
        for om in range(1, h):
            for ts in _partitions(om):
                got = q_value_by_class(shape, h, ts)
                checked += 1
                if got != 0:
                    print(f'A7 FAIL  (i) h={h} ts={ts} Omega={om}: '
                          f'Q={got} (expected 0)')
                    fails += 1
        # (ii) at the boundary
        for ts in _partitions(h):
            got = q_value_by_class(shape, h, ts)
            prod_efact = 1
            for e in ts:
                prod_efact *= factorial(e)
            want = Fraction((-1)**(h-1) * factorial(h-1), prod_efact)
            checked += 1
            if got != want:
                print(f'A7 FAIL  (ii) h={h} ts={ts} Omega={h}: '
                      f'Q={got}, formula={want}')
                fails += 1
        # (iii) above the kernel — no accidental zeros
        for om in range(h + 1, omega_max + 1):
            for ts in _partitions(om):
                got = q_value_by_class(shape, h, ts)
                checked += 1
                if got == 0:
                    print(f'A7 FAIL  (iii) h={h} ts={ts} Omega={om}: '
                          f'Q=0 (accidental zero above kernel)')
                    fails += 1
    if fails == 0:
        print(f'A7 PASS  kernel-zero classifier (prime n) at h in [2, {h_max}], '
              f'Omega in [1, {omega_max}] ({checked} cases)')
    return fails


# --------------------------------------------------------------------------
# A8 -- 8x6 matrices at h = 6, 7, 8
# --------------------------------------------------------------------------

def anchor_matrix_h6_h7_h8() -> int:
    """The (shape, tau_sig) matrices at h = 6, 7, 8 (algebra/KERNEL-ZEROS.md).

    Same eight shapes and six tau_sigs as A2. Cell values frozen as
    exact Fractions; the displayed tables in KERNEL-ZEROS.md are these
    exact values.
    """
    SHAPES = [
        (1,), (2,), (1, 1), (3,), (2, 1), (1, 1, 1), (4,), (3, 1),
    ]
    TAU_SIGS = [
        (), (1,), (2,), (1, 1), (3,), (1, 1, 1),
    ]
    expected_h6 = {
        ((1,), ()):           Fraction(1, 6),
        ((1,), (1,)):         Fraction(0),
        ((1,), (2,)):         Fraction(0),
        ((1,), (1, 1)):       Fraction(0),
        ((1,), (3,)):         Fraction(0),
        ((1,), (1, 1, 1)):    Fraction(0),

        ((2,), ()):           Fraction(-1, 12),
        ((2,), (1,)):         Fraction(-1),
        ((2,), (2,)):         Fraction(-5, 2),
        ((2,), (1, 1)):       Fraction(-4),
        ((2,), (3,)):         Fraction(-3),
        ((2,), (1, 1, 1)):    Fraction(-4),

        ((1, 1), ()):         Fraction(5, 3),
        ((1, 1), (1,)):       Fraction(0),
        ((1, 1), (2,)):       Fraction(-15),
        ((1, 1), (1, 1)):     Fraction(-30),
        ((1, 1), (3,)):       Fraction(-50),
        ((1, 1), (1, 1, 1)):  Fraction(-210),

        ((3,), ()):           Fraction(-4, 3),
        ((3,), (1,)):         Fraction(-7),
        ((3,), (2,)):         Fraction(-17),
        ((3,), (1, 1)):       Fraction(-27),
        ((3,), (3,)):         Fraction(-26),
        ((3,), (1, 1, 1)):    Fraction(-61),

        ((2, 1), ()):         Fraction(-5, 6),
        ((2, 1), (1,)):       Fraction(-40),
        ((2, 1), (2,)):       Fraction(-160),
        ((2, 1), (1, 1)):     Fraction(-280),
        ((2, 1), (3,)):       Fraction(-390),
        ((2, 1), (1, 1, 1)):  Fraction(-1420),

        ((1, 1, 1), ()):           Fraction(140, 3),
        ((1, 1, 1), (1,)):         Fraction(0),
        ((1, 1, 1), (2,)):         Fraction(-315),
        ((1, 1, 1), (1, 1)):       Fraction(-630),
        ((1, 1, 1), (3,)):         Fraction(-1050),
        ((1, 1, 1), (1, 1, 1)):    Fraction(-4410),

        ((4,), ()):           Fraction(-55, 12),
        ((4,), (1,)):         Fraction(-21),
        ((4,), (2,)):         Fraction(-97, 2),
        ((4,), (1, 1)):       Fraction(-76),
        ((4,), (3,)):         Fraction(-74),
        ((4,), (1, 1, 1)):    Fraction(-174),

        ((3, 1), ()):         Fraction(-70, 3),
        ((3, 1), (1,)):       Fraction(-180),
        ((3, 1), (2,)):       Fraction(-575),
        ((3, 1), (1, 1)):     Fraction(-970),
        ((3, 1), (3,)):       Fraction(-1280),
        ((3, 1), (1, 1, 1)):  Fraction(-4410),
    }
    expected_h7 = {
        ((1,), ()):           Fraction(1, 7),
        ((1,), (1,)):         Fraction(0),
        ((1,), (2,)):         Fraction(0),
        ((1,), (1, 1)):       Fraction(0),
        ((1,), (3,)):         Fraction(0),
        ((1,), (1, 1, 1)):    Fraction(0),

        ((2,), ()):           Fraction(1, 7),
        ((2,), (1,)):         Fraction(1),
        ((2,), (2,)):         Fraction(5),
        ((2,), (1, 1)):       Fraction(9),
        ((2,), (3,)):         Fraction(15),
        ((2,), (1, 1, 1)):    Fraction(61),

        ((1, 1), ()):         Fraction(-20, 7),
        ((1, 1), (1,)):       Fraction(-20),
        ((1, 1), (2,)):       Fraction(-50),
        ((1, 1), (1, 1)):     Fraction(-80),
        ((1, 1), (3,)):       Fraction(-70),
        ((1, 1), (1, 1, 1)):  Fraction(-140),

        ((3,), ()):           Fraction(8, 7),
        ((3,), (1,)):         Fraction(11),
        ((3,), (2,)):         Fraction(47),
        ((3,), (1, 1)):       Fraction(83),
        ((3,), (3,)):         Fraction(395, 3),
        ((3,), (1, 1, 1)):    Fraction(519),

        ((2, 1), ()):         Fraction(-265, 7),
        ((2, 1), (1,)):       Fraction(-145),
        ((2, 1), (2,)):       Fraction(-235),
        ((2, 1), (1, 1)):     Fraction(-325),
        ((2, 1), (3,)):       Fraction(-95),
        ((2, 1), (1, 1, 1)):  Fraction(695),

        ((1, 1, 1), ()):           Fraction(-2400, 7),
        ((1, 1, 1), (1,)):         Fraction(-1680),
        ((1, 1, 1), (2,)):         Fraction(-4200),
        ((1, 1, 1), (1, 1)):       Fraction(-6720),
        ((1, 1, 1), (3,)):         Fraction(-7560),
        ((1, 1, 1), (1, 1, 1)):    Fraction(-21840),

        ((4,), ()):           Fraction(165, 28),
        ((4,), (1,)):         Fraction(48),
        ((4,), (2,)):         Fraction(186),
        ((4,), (1, 1)):       Fraction(324),
        ((4,), (3,)):         Fraction(495),
        ((4,), (1, 1, 1)):    Fraction(1902),

        ((3, 1), ()):         Fraction(-825, 7),
        ((3, 1), (1,)):       Fraction(-315),
        ((3, 1), (2,)):       Fraction(-135),
        ((3, 1), (1, 1)):     Fraction(45),
        ((3, 1), (3,)):       Fraction(1285),
        ((3, 1), (1, 1, 1)):  Fraction(8205),
    }
    expected_h8 = {
        ((1,), ()):           Fraction(1, 8),
        ((1,), (1,)):         Fraction(0),
        ((1,), (2,)):         Fraction(0),
        ((1,), (1, 1)):       Fraction(0),
        ((1,), (3,)):         Fraction(0),
        ((1,), (1, 1, 1)):    Fraction(0),

        ((2,), ()):           Fraction(1, 8),
        ((2,), (1,)):         Fraction(0),
        ((2,), (2,)):         Fraction(-5, 2),
        ((2,), (1, 1)):       Fraction(-5),
        ((2,), (3,)):         Fraction(-15),
        ((2,), (1, 1, 1)):    Fraction(-75),

        ((1, 1), ()):         Fraction(-35, 8),
        ((1, 1), (1,)):       Fraction(0),
        ((1, 1), (2,)):       Fraction(70),
        ((1, 1), (1, 1)):     Fraction(140),
        ((1, 1), (3,)):       Fraction(280),
        ((1, 1), (1, 1, 1)):  Fraction(1260),

        ((3,), ()):           Fraction(23, 24),
        ((3,), (1,)):         Fraction(-1),
        ((3,), (2,)):         Fraction(-67, 2),
        ((3,), (1, 1)):       Fraction(-66),
        ((3,), (3,)):         Fraction(-518, 3),
        ((3,), (1, 1, 1)):    Fraction(-836),

        ((2, 1), ()):         Fraction(245, 8),
        ((2, 1), (1,)):       Fraction(420),
        ((2, 1), (2,)):       Fraction(3535, 2),
        ((2, 1), (1, 1)):     Fraction(3115),
        ((2, 1), (3,)):       Fraction(4655),
        ((2, 1), (1, 1, 1)):  Fraction(17745),

        ((1, 1, 1), ()):           Fraction(-5775, 8),
        ((1, 1, 1), (1,)):         Fraction(0),
        ((1, 1, 1), (2,)):         Fraction(8400),
        ((1, 1, 1), (1, 1)):       Fraction(16800),
        ((1, 1, 1), (3,)):         Fraction(33600),
        ((1, 1, 1), (1, 1, 1)):    Fraction(151200),

        ((4,), ()):           Fraction(21, 8),
        ((4,), (1,)):         Fraction(-20),
        ((4,), (2,)):         Fraction(-206),
        ((4,), (1, 1)):       Fraction(-392),
        ((4,), (3,)):         Fraction(-891),
        ((4,), (1, 1, 1)):    Fraction(-4130),

        ((3, 1), ()):         Fraction(3017, 8),
        ((3, 1), (1,)):       Fraction(2709),
        ((3, 1), (2,)):       Fraction(18333, 2),
        ((3, 1), (1, 1)):     Fraction(15624),
        ((3, 1), (3,)):       Fraction(21294),
        ((3, 1), (1, 1, 1)):  Fraction(75474),
    }
    fails = 0
    checked = 0
    for H, expected in [(6, expected_h6), (7, expected_h7), (8, expected_h8)]:
        for shape in SHAPES:
            for tau_sig in TAU_SIGS:
                got = q_value_by_class(shape, H, tau_sig)
                want = expected[(shape, tau_sig)]
                checked += 1
                if got != want:
                    print(f'A8 FAIL  h={H} shape={shape} tau_sig={tau_sig}: '
                          f'got {got} != {want}')
                    fails += 1
    if fails == 0:
        print(f'A8 PASS  8x6 (shape x tau_sig) matrices at h=6, 7, 8 ({checked} cells)')
    return fails


# --------------------------------------------------------------------------
# A9 -- denominator bound
# --------------------------------------------------------------------------

def anchor_denominator_bound(n_max: int = 12, h_max: int = 6, k_max: int = 25) -> int:
    """Q_n(m) has denominator dividing lcm(1, ..., nu_n(m))
    (algebra/DENOMINATOR-BOUND.md).

    The bound is in the *true* n-adic valuation nu_n(m) of m = n^h k,
    which can exceed the input h when k itself carries factors of n.
    The corollary's statement uses h = nu_n(m); this test mirrors it
    by recomputing the effective height for each m before bounding.
    """
    from predict_q import n_adic_height
    fails = 0
    checked = 0
    for h in range(1, h_max + 1):
        for n in range(2, n_max + 1):
            for k in range(1, k_max + 1):
                m = n**h * k
                h_true = n_adic_height(n, m)
                L = _lcm_range(h_true)
                v = q_general(n, h, k)
                checked += 1
                if L % v.denominator != 0:
                    print(f'A9 FAIL  n={n} h={h} k={k}: Q={v} '
                          f'denominator {v.denominator} does not divide '
                          f'lcm(1..{h_true})={L} '
                          f'(nu_n(m={m}) = {h_true})')
                    fails += 1
    if fails == 0:
        print(f'A9 PASS  Q_n(m) denominator divides lcm(1..nu_n(m)) '
              f'({checked} (n, h, k) cases)')
    return fails


def anchor_row_ogf(p_list=(2, 3, 5, 7, 11, 13),
                    e_max: int = 6, omega_cap: int = 5,
                    k_max: int = 200) -> int:
    """Prime-row OGF anchor (algebra/ROW-OGF.md).

    Four sub-checks:

    A10a. row_polynomial(p, q^e) matches row_polynomial_qe_closed(e)
          for primes p != q, exponents e in [1, e_max]. The closed
          form (1 - (1-x)^e)/e is computed independently of the
          master expansion; equality cross-checks both.

    A10b. row_polynomial(p, k_prime) has length exactly Omega(k_prime)
          and a non-zero leading coefficient, for every k_prime in
          [2, k_max] coprime to p with Omega <= omega_cap.

    A10c. The leading coefficient equals the KERNEL-ZEROS.md (ii)
          boundary formula (-1)^(Omega-1) * (Omega-1)! / prod e_i!.

    A10d. row_sum(p, k_prime) equals sum(row_polynomial(p, k_prime))
          (closed form vs. polynomial sum), and equals 1/e or 0 by
          omega(k_prime) == 1 vs >= 2.
    """
    fails = 0
    checked_a = 0
    checked_b = 0
    checked_c = 0
    checked_d = 0
    QS = (2, 3, 5, 7, 11, 13)

    # A10a — closed-form for q^e
    for p in p_list:
        for q in QS:
            if q == p:
                continue
            for e in range(1, e_max + 1):
                kp = q**e
                got = row_polynomial(p, kp)
                want = row_polynomial_qe_closed(e)
                checked_a += 1
                if got != want:
                    print(f'A10a FAIL  p={p} q={q} e={e}: '
                          f'row_polynomial={got}, closed={want}')
                    fails += 1

    # A10b — degree exactly Omega(k_prime), leading nonzero
    # A10c — leading matches boundary formula
    # A10d — row_sum closed form vs sum
    from math import factorial
    for p in p_list:
        for kp in range(2, k_max + 1):
            if gcd(p, kp) != 1:
                continue
            om = big_omega(kp)
            if om > omega_cap:
                continue
            coefs = row_polynomial(p, kp)
            checked_b += 1
            if len(coefs) != om:
                print(f'A10b FAIL  p={p} k_prime={kp}: row_polynomial '
                      f'len={len(coefs)} != Omega={om}')
                fails += 1
                continue
            if coefs[-1] == 0:
                print(f'A10b FAIL  p={p} k_prime={kp}: leading '
                      f'coefficient is zero')
                fails += 1
                continue

            prod_efact = 1
            for _q, e in factor_tuple(kp):
                prod_efact *= factorial(e)
            expected = Fraction((-1)**(om - 1) * factorial(om - 1),
                                prod_efact)
            checked_c += 1
            if coefs[-1] != expected:
                print(f'A10c FAIL  p={p} k_prime={kp}: leading '
                      f'{coefs[-1]} != boundary {expected}')
                fails += 1

            closed = row_sum(p, kp)
            via_sum = sum(coefs, Fraction(0))
            checked_d += 1
            if closed != via_sum:
                print(f'A10d FAIL  p={p} k_prime={kp}: row_sum '
                      f'closed={closed} != sum(poly)={via_sum}')
                fails += 1

            om_distinct = little_omega(kp)
            if om_distinct == 1:
                _, e = factor_tuple(kp)[0]
                want_sum = Fraction(1, e)
            else:
                want_sum = Fraction(0)
            if closed != want_sum:
                print(f'A10d FAIL  p={p} k_prime={kp} omega={om_distinct}: '
                      f'row_sum={closed} != expected {want_sum}')
                fails += 1

    if fails == 0:
        print(f'A10 PASS  prime-row OGF '
              f'(A10a: {checked_a} q^e closed-form matches; '
              f'A10b: {checked_b} degree+leading checks; '
              f'A10c: {checked_c} boundary-formula matches; '
              f'A10d: {checked_d} row_sum closed-form matches)')
    return fails


def main():
    fails = 0
    fails += anchor_prime_row_one_over_h()
    fails += anchor_matrix_h5()
    fails += anchor_h2_cliff()
    fails += anchor_q_general_vs_class()
    fails += anchor_h3_displayed_tables()
    fails += anchor_kernel_zero_classifier()
    fails += anchor_matrix_h6_h7_h8()
    fails += anchor_denominator_bound()
    fails += anchor_row_ogf()
    fails += anchor_csv_match()

    print()
    if fails == 0:
        print('ALL ANCHORS PASS')
        return 0
    print(f'TOTAL FAILS: {fails}')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
