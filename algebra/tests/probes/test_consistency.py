"""
test_consistency.py — Layer 3 cross-form checks for the probes.

Whenever two paths reach the same quantity, the test asserts they
agree. Failures here indicate two implementations have drifted apart.

kernel_zero cross-form checks:

    kz-algebra-vs-q_row:       probe.algebra_row vs predict_q.q_row.
    kz-lattice-vs-algebra:     cached float .npy vs algebra at TOL=1e-12 (h=6 only).
    kz-reverse-symmetry:       measured no_op strength under reverse vs the
                                predicted |Z ∩ σ(Z)| / |Z| identity.
    kz-reverse-squared:        transducer_reverse² == transducer_identity.
    kz-substrate-identity:     run_probe at substrate=lattice vs algebra under
                                identity transducer agrees on every verdict.

row_ogf_cliff cross-form checks:

    roc-algebra-vs-q_general:  probe.algebra_column vs cell-by-cell q_general.
    roc-cross-occurrence:      leading multinomial from ROW-OGF.md (probe's
                                predicted_leading_multinomial) equals the
                                kernel-zero boundary value at Ω = h
                                ((-1)^(h-1)(h-1)!/∏ e_i! at e = h, single-
                                prime cofactor) — the wonders-doc cross-
                                occurrence, witnessed at the substrate.
    roc-qe-closed-vs-algebra:  predicted_qe_closed at q^e cofactor matches
                                algebra_column cell-by-cell. Two independent
                                evaluators of the same row must agree.
    roc-cliff-scale-invariant: transducer_scale_2x preserves the predicted
                                cliff cells (0 ↦ 0).

What failure means. Two paths to the same quantity disagree. Read
both functions named in the failure header.

Run:

    sage -python algebra/tests/probes/test_consistency.py
"""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
from fractions import Fraction
from math import factorial

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.dirname(HERE)
ALGEBRA = os.path.dirname(TESTS)
REPO = os.path.dirname(ALGEBRA)
sys.path.insert(0, ALGEBRA)

from predict_q import q_general, q_row  # noqa: E402


def load_probe(probe_name: str):
    path = os.path.join(REPO, 'experiments', 'probes', probe_name, 'probe.py')
    spec = importlib.util.spec_from_file_location(f'{probe_name}_probe', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


KZ = load_probe('kernel_zero')
ROC = load_probe('row_ogf_cliff')


SMALL_PRIMES = (2, 3, 5, 7)
SMALL_HEIGHTS = (5, 6)
COMMITTED_HEIGHT = 6


# ==========================================================================
# kernel_zero
# ==========================================================================

def consistency_kz_algebra_row_vs_q_row(K: int = 200) -> int:
    fails = 0
    checked = 0
    for p in SMALL_PRIMES:
        for h in SMALL_HEIGHTS:
            ar = KZ.algebra_row(p, h, K)
            qr = np.array(q_row(p, h, K), dtype=np.float64)
            if not np.array_equal(ar, qr):
                diff = np.max(np.abs(ar - qr))
                print(f'kz-algebra-vs-q_row FAIL  p={p} h={h}: max diff {diff:.3e}')
                fails += 1
            checked += K
    if fails == 0:
        print(f'kz-algebra-vs-q_row PASS  ({checked} cells)')
    return fails


def consistency_kz_lattice_vs_algebra(K: int = 4000) -> int:
    h = COMMITTED_HEIGHT
    path = os.path.join(KZ.DEFAULT_LATTICE_DIR, f'q_lattice_4000_h{h}.npy')
    if not os.path.exists(path):
        print(f'kz-lattice-vs-algebra SKIP  h={h} lattice missing')
        return 0
    fails = 0
    for p in SMALL_PRIMES:
        lr = KZ.lattice_row(p, h, KZ.DEFAULT_LATTICE_DIR, K)
        ar = KZ.algebra_row(p, h, K)
        diff = np.abs(lr - ar)
        n_above_tol = int((diff >= 1e-12).sum())
        if n_above_tol > 0:
            print(f'kz-lattice-vs-algebra FAIL  p={p} h={h}: '
                  f'{n_above_tol} cells with |diff| >= 1e-12')
            fails += 1
    if fails == 0:
        print(f'kz-lattice-vs-algebra PASS  h={h}, '
              f'{K * len(SMALL_PRIMES)} cells')
    return fails


def _predicted_reversal_symmetry(p: int, h: int, K: int) -> float:
    Z = KZ.predicted_zero_indices(p, h, K)
    if Z.size == 0:
        return 1.0
    Z_set = set(int(z) for z in Z)
    sigma_Z = set(K - 1 - z for z in Z_set)
    return len(Z_set & sigma_Z) / len(Z_set)


def consistency_kz_reverse_symmetry(K: int = 1000) -> int:
    fails = 0
    for p in SMALL_PRIMES:
        for h in SMALL_HEIGHTS:
            row = KZ.algebra_row(p, h, K)
            row_rev = KZ.transducer_reverse(row)
            measured = KZ.channel_no_op(row_rev, p, h)[1]
            predicted = _predicted_reversal_symmetry(p, h, K)
            if abs(measured - predicted) > 1e-12:
                print(f'kz-reverse-symmetry FAIL  p={p} h={h}: '
                      f'measured {measured:.6f} != predicted {predicted:.6f}')
                fails += 1
    if fails == 0:
        n_cells = len(SMALL_PRIMES) * len(SMALL_HEIGHTS)
        print(f'kz-reverse-symmetry PASS  measured == predicted '
              f'(|Z ∩ σ(Z)| / |Z|) at {n_cells} cells, K={K}')
    return fails


def consistency_kz_reverse_squared(K_list=(1, 2, 5, 100, 4000)) -> int:
    fails = 0
    rng = np.random.default_rng(7)
    for K in K_list:
        row = rng.standard_normal(K)
        twice = KZ.transducer_reverse(KZ.transducer_reverse(row))
        ident = KZ.transducer_identity(row)
        if not np.array_equal(twice, ident):
            print(f'kz-reverse² FAIL  K={K}')
            fails += 1
    if fails == 0:
        print(f'kz-reverse² PASS  reverse ∘ reverse == identity at K in {K_list}')
    return fails


def consistency_kz_substrate_identity(K: int = 200) -> int:
    h = COMMITTED_HEIGHT
    path = os.path.join(KZ.DEFAULT_LATTICE_DIR, f'q_lattice_4000_h{h}.npy')
    if not os.path.exists(path):
        print('kz-substrate-identity SKIP  lattice missing')
        return 0
    fails = 0
    common = {
        'transducer': 'identity',
        'primes': list(SMALL_PRIMES),
        'heights': [h],
        'K': K,
        'lattice_dir': KZ.DEFAULT_LATTICE_DIR,
    }
    with tempfile.TemporaryDirectory() as t1:
        out_lat = KZ.run_probe({**common, 'substrate': 'lattice'},
                                os.path.join(t1, 'lat'))
    with tempfile.TemporaryDirectory() as t2:
        out_alg = KZ.run_probe({**common, 'substrate': 'algebra'},
                                os.path.join(t2, 'alg'))
    for cell in out_lat['cells']:
        for ch, r_lat in out_lat['results'][cell].items():
            r_alg = out_alg['results'][cell][ch]
            if r_lat['verdict'] != r_alg['verdict']:
                print(f'kz-substrate-identity FAIL  cell={cell} ch={ch}')
                fails += 1
    if fails == 0:
        n = len(out_lat['cells']) * len(out_lat['results'][out_lat['cells'][0]])
        print(f'kz-substrate-identity PASS  {n} (cell, channel) verdicts agree')
    return fails


# ==========================================================================
# row_ogf_cliff
# ==========================================================================

def consistency_roc_algebra_column_vs_q_general() -> int:
    fails = 0
    checked = 0
    panel = ROC.panel_cells()
    H = ROC.DEFAULT_H_MAX
    for p, q, e in panel:
        col = ROC.algebra_column(p, q, e, H)
        for h in range(1, H + 1):
            expected = float(q_general(p, h, q ** e))
            if col[h - 1] != expected:
                print(f'roc-algebra-vs-q_general FAIL  ({p},{q},{e})[h={h}]')
                fails += 1
            checked += 1
    if fails == 0:
        print(f'roc-algebra-vs-q_general PASS  algebra_column == q_general '
              f'({checked} cells, {len(panel)} panel cells)')
    return fails


def consistency_roc_cross_occurrence() -> int:
    """The leading multinomial from ROW-OGF.md (probe's
    predicted_leading_multinomial(e)) must equal the kernel-zero
    boundary multinomial at Ω = h with single-prime partition (e,):
        (-1)^(e-1) (e-1)! / e! = (-1)^(e-1) / e.
    Both expressions evaluate to (-1)^(e-1)/e by hand; the test
    asserts the probe's predictor matches the boundary formula
    independently re-evaluated."""
    fails = 0
    for e in (1, 2, 3, 4, 5, 6, 7, 8):
        from_probe = ROC.predicted_leading_multinomial(e)
        # Independent evaluation of KERNEL-ZEROS.md (ii) at partition (e,):
        boundary = (-1) ** (e - 1) * factorial(e - 1) / factorial(e)
        if abs(from_probe - boundary) > 1e-15:
            print(f'roc-cross-occurrence FAIL  e={e}: probe={from_probe} '
                  f'!= boundary {boundary}')
            fails += 1
    if fails == 0:
        print(f'roc-cross-occurrence PASS  ROW-OGF leading multinomial == '
              f'KERNEL-ZEROS boundary multinomial at partition (e,)')
    return fails


def consistency_roc_qe_closed_vs_algebra() -> int:
    """For every panel cell (p, q, e), the closed-form prediction
    predicted_qe_closed(e, H_max) must equal algebra_column(p, q, e, H_max)
    cell-by-cell. Two independent evaluators of the same row (master
    expansion vs (1-(1-x)^e)/e) must agree — the wonders-doc claim."""
    fails = 0
    panel = ROC.panel_cells()
    H = ROC.DEFAULT_H_MAX
    for p, q, e in panel:
        algebra = ROC.algebra_column(p, q, e, H)
        closed = ROC.predicted_qe_closed(e, H)
        diff = np.abs(algebra - closed)
        if not np.all(diff < 1e-15):
            print(f'roc-qe-closed-vs-algebra FAIL  ({p},{q},{e}): '
                  f'max diff {diff.max():.3e}')
            fails += 1
    if fails == 0:
        n = len(panel) * H
        print(f'roc-qe-closed-vs-algebra PASS  closed-form (1-(1-x)^e)/e '
              f'== master-expansion column ({n} cells)')
    return fails


def consistency_roc_cliff_scale_invariant() -> int:
    """For every panel cell, predicted_cliff_indices map to zero in the
    algebra column AND in the scaled column (since c · 0 = 0)."""
    fails = 0
    panel = ROC.panel_cells()
    H = ROC.DEFAULT_H_MAX
    for p, q, e in panel:
        col = ROC.algebra_column(p, q, e, H)
        col_scaled = ROC.transducer_scale_2x(col)
        cliff = ROC.predicted_cliff_indices(e, H)
        if not np.all(np.abs(col[cliff]) < 1e-15):
            print(f'roc-cliff FAIL pre-scaling ({p},{q},{e})')
            fails += 1
        if not np.all(np.abs(col_scaled[cliff]) < 1e-15):
            print(f'roc-cliff-scale-invariant FAIL  ({p},{q},{e}): '
                  f'scaled cliff cell nonzero')
            fails += 1
    if fails == 0:
        print(f'roc-cliff-scale-invariant PASS  cliff cells are zero before '
              f'and after 2x scaling ({len(panel)} cells)')
    return fails


def main() -> int:
    fails = 0
    # kernel_zero
    fails += consistency_kz_algebra_row_vs_q_row()
    fails += consistency_kz_reverse_squared()
    fails += consistency_kz_reverse_symmetry()
    fails += consistency_kz_lattice_vs_algebra()
    fails += consistency_kz_substrate_identity()
    # row_ogf_cliff
    fails += consistency_roc_algebra_column_vs_q_general()
    fails += consistency_roc_cross_occurrence()
    fails += consistency_roc_qe_closed_vs_algebra()
    fails += consistency_roc_cliff_scale_invariant()

    print()
    if fails == 0:
        print('ALL CONSISTENCY CHECKS PASS')
        return 0
    print(f'TOTAL FAILS: {fails}')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
