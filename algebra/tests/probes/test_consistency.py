"""
test_consistency.py — Layer 3 cross-form checks for the probes.

Whenever two paths reach the same quantity, the test asserts they
agree. Failures here indicate two implementations have drifted apart.

Cross-form checks (in priority order — keystone first):

algebra-vs-q_row. probe.algebra_row(p, h, K) versus
    predict_q.q_row(p, h, K). Both compute the float'd row of
    Q_p(p^h k); they must agree exactly. Source: probe.py +
    predict_q.py.

lattice-vs-algebra. lattice_row(p, h, K) (cached float .npy) versus
    algebra_row(p, h, K) (exact Fraction → float). The
    lattice-vs-algebra contract this probe is built to test, asserted
    in the test layer at the same K and TOL. Source:
    PROBE.md § "Recovery". Requires the committed h=6 lattice file.

reverse-symmetry. The PROBE.md prediction
    no_op_strength_under_reverse(p, h)
        == |Z ∩ σ(Z)| / |Z|
    where Z is the algebra-zero index set and σ(k) = K + 1 - k.
    Computes the predicted strength independently and compares to the
    measured strength from a small-K calibration run. The y = x
    reversal_symmetry.png figure assertion in numeric form. Source:
    PROBE.md § "Calibrations".

reverse²-vs-identity. transducer_reverse(transducer_reverse(row))
    must equal transducer_identity(row) at every K. Source: probe.py.

What failure means. Two paths to the same quantity disagree. Read
both functions named in the failure header.

Run:

    sage -python algebra/tests/probes/test_consistency.py
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

from predict_q import q_row  # noqa: E402
from probe import (  # noqa: E402
    DEFAULT_LATTICE_DIR,
    algebra_row, channel_no_op, lattice_row,
    predicted_zero_indices, run_probe,
    transducer_identity, transducer_reverse,
)


SMALL_PRIMES = (2, 3, 5, 7)
SMALL_HEIGHTS = (5, 6)
COMMITTED_HEIGHT = 6  # the only committed lattice file


# --------------------------------------------------------------------------
# algebra-vs-q_row
# --------------------------------------------------------------------------

def consistency_algebra_row_vs_q_row(K: int = 200) -> int:
    """probe.algebra_row(p, h, K) == np.array(predict_q.q_row(p, h, K))
    for every (p, h) in SMALL_PRIMES x SMALL_HEIGHTS."""
    fails = 0
    checked = 0
    for p in SMALL_PRIMES:
        for h in SMALL_HEIGHTS:
            ar = algebra_row(p, h, K)
            qr = np.array(q_row(p, h, K), dtype=np.float64)
            if not np.array_equal(ar, qr):
                diff = np.max(np.abs(ar - qr))
                print(f'algebra-vs-q_row FAIL  p={p} h={h}: '
                      f'max diff {diff:.3e}')
                fails += 1
            checked += K
    if fails == 0:
        print(f'algebra-vs-q_row PASS  algebra_row == q_row '
              f'({checked} cells)')
    return fails


# --------------------------------------------------------------------------
# lattice-vs-algebra (committed h=6 only)
# --------------------------------------------------------------------------

def consistency_lattice_vs_algebra(K: int = 4000) -> int:
    """For h=6, every cell of the committed lattice equals the float'd
    q_general value at TOL=1e-12. This is the contract the probe was
    built to test."""
    h = COMMITTED_HEIGHT
    path = os.path.join(DEFAULT_LATTICE_DIR, f'q_lattice_4000_h{h}.npy')
    if not os.path.exists(path):
        print(f'lattice-vs-algebra SKIP  h={h} lattice missing at {path}')
        return 0
    fails = 0
    for p in SMALL_PRIMES:
        lr = lattice_row(p, h, DEFAULT_LATTICE_DIR, K)
        ar = algebra_row(p, h, K)
        diff = np.abs(lr - ar)
        max_diff = float(diff.max())
        n_above_tol = int((diff >= 1e-12).sum())
        if n_above_tol > 0:
            print(f'lattice-vs-algebra FAIL  p={p} h={h}: '
                  f'{n_above_tol} cells with |diff| >= 1e-12, '
                  f'max_diff={max_diff:.3e}')
            fails += 1
    if fails == 0:
        print(f'lattice-vs-algebra PASS  h={h}, p in {SMALL_PRIMES}, '
              f'K={K}, max diff < 1e-12 across {K * len(SMALL_PRIMES)} cells')
    return fails


# --------------------------------------------------------------------------
# reverse-symmetry: predicted |Z ∩ σ(Z)| / |Z| == measured no_op strength
# --------------------------------------------------------------------------

def _predicted_reversal_symmetry(p: int, h: int, K: int) -> float:
    Z = predicted_zero_indices(p, h, K)
    if Z.size == 0:
        return 1.0
    Z_set = set(int(z) for z in Z)
    sigma_Z = set(K - 1 - z for z in Z_set)
    return len(Z_set & sigma_Z) / len(Z_set)


def consistency_reverse_symmetry(K: int = 1000) -> int:
    """Predicted reversal-symmetry of the algebra-zero set equals the
    measured no_op strength under the reverse transducer.

    Uses the algebra substrate (no lattice file required) so the test
    runs without depending on substrate caching. Smaller K than the
    full panel for speed; the relationship is K-independent up to
    finite-K effects that don't matter for equality."""
    fails = 0
    for p in SMALL_PRIMES:
        for h in SMALL_HEIGHTS:
            row = algebra_row(p, h, K)
            row_rev = transducer_reverse(row)
            measured = channel_no_op(row_rev, p, h)[1]
            predicted = _predicted_reversal_symmetry(p, h, K)
            if abs(measured - predicted) > 1e-12:
                print(f'reverse-symmetry FAIL  p={p} h={h}: '
                      f'measured {measured:.6f} != predicted {predicted:.6f}')
                fails += 1
    if fails == 0:
        n_cells = len(SMALL_PRIMES) * len(SMALL_HEIGHTS)
        print(f'reverse-symmetry PASS  measured == predicted '
              f'(|Z ∩ σ(Z)| / |Z|) at {n_cells} cells, K={K}')
    return fails


# --------------------------------------------------------------------------
# reverse² == identity
# --------------------------------------------------------------------------

def consistency_reverse_squared(K_list=(1, 2, 5, 100, 4000)) -> int:
    """transducer_reverse ∘ transducer_reverse must equal
    transducer_identity at every length."""
    fails = 0
    rng = np.random.default_rng(7)
    for K in K_list:
        row = rng.standard_normal(K)
        twice = transducer_reverse(transducer_reverse(row))
        ident = transducer_identity(row)
        if not np.array_equal(twice, ident):
            print(f'reverse² FAIL  K={K}: max |diff| {np.max(np.abs(twice - ident)):.3e}')
            fails += 1
    if fails == 0:
        print(f'reverse² PASS  reverse ∘ reverse == identity at K in {K_list}')
    return fails


# --------------------------------------------------------------------------
# substrate=lattice vs substrate=algebra under identity transducer
# --------------------------------------------------------------------------

def consistency_lattice_vs_algebra_substrate_identity(K: int = 200) -> int:
    """Running the probe at substrate=lattice and substrate=algebra under
    the identity transducer must produce the same per-channel verdicts.
    This is the lattice-vs-algebra contract expressed at the verdict
    layer, not the cell layer."""
    h = COMMITTED_HEIGHT
    path = os.path.join(DEFAULT_LATTICE_DIR, f'q_lattice_4000_h{h}.npy')
    if not os.path.exists(path):
        print(f'lattice-vs-algebra-substrate SKIP  h={h} lattice missing')
        return 0

    fails = 0
    import tempfile
    common = {
        'transducer': 'identity',
        'primes': list(SMALL_PRIMES),
        'heights': [h],
        'K': K,
        'lattice_dir': DEFAULT_LATTICE_DIR,
    }
    with tempfile.TemporaryDirectory() as tmp1:
        out_lat = run_probe({**common, 'substrate': 'lattice'},
                             os.path.join(tmp1, 'lat'))
    with tempfile.TemporaryDirectory() as tmp2:
        out_alg = run_probe({**common, 'substrate': 'algebra'},
                             os.path.join(tmp2, 'alg'))
    for cell in out_lat['cells']:
        for ch, r_lat in out_lat['results'][cell].items():
            r_alg = out_alg['results'][cell][ch]
            if r_lat['verdict'] != r_alg['verdict']:
                print(f'lattice-vs-algebra-substrate FAIL  cell={cell} '
                      f'ch={ch}: lattice={r_lat}, algebra={r_alg}')
                fails += 1
    if fails == 0:
        n = len(out_lat['cells']) * len(out_lat['results'][out_lat['cells'][0]])
        print(f'lattice-vs-algebra-substrate PASS  identity verdicts agree '
              f'across {n} (cell, channel) pairs')
    return fails


def main() -> int:
    fails = 0
    fails += consistency_algebra_row_vs_q_row()
    fails += consistency_reverse_squared()
    fails += consistency_reverse_symmetry()
    fails += consistency_lattice_vs_algebra()
    fails += consistency_lattice_vs_algebra_substrate_identity()

    print()
    if fails == 0:
        print('ALL CONSISTENCY CHECKS PASS')
        return 0
    print(f'TOTAL FAILS: {fails}')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
