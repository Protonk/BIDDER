"""
test_within_row_lattice.py — verify predict_correlation against the
empirical lattice q_lattice_4000_h6.npy (the height kept live by
the Tier B prune; h={5,7,8} are regenerable from
experiments/acm-champernowne/base10/q_distillery/q_lattice_4000_h_regen.py
and not committed).

What this checks.

The cached lattice is an evaluation of the master expansion over the
(n, k) grid. predict_q.q_general is also an evaluation of the master
expansion. So row-by-row, lattice[n - 2, k - 1] should equal
float(q_general(n, h, k)) up to float precision. The first check is a
spot agreement: predict_q reproduces a sample of lattice cells.

Then, with that established, the within-row autocorrelation profile
computed from the lattice row equals the profile computed from
predict_correlation.autocorr_profile. The two pipelines independently
compute the same quantity, so their agreement is a sanity check on the
indexing conventions and on the class decomposition.

What this also surfaces.

For each h in LIVE_HEIGHTS and each prime n in {2, 3, 5, 7, 11, 13},
we record the lag-L autocorrelation profile for L = 1..20 and compute:

  - mean over odd L
  - mean over even L
  - ratio  (a parity-of-L gap diagnostic)

This is the closed-form translation of the substrate-side parity-of-L
finding from arguments/ATTRACTOR-AND-MIRAGE.md. The values are exact
in the sense that they come from the master expansion; their structure
across (h, n) is open to interpretation.

Contract. Every height in LIVE_HEIGHTS must have its lattice file
present; missing-but-declared lattices are a FAIL, not a SKIP. To run
against additional heights, regenerate the lattice via
q_lattice_4000_h_regen.py and add the height here.

Run:

    sage -python algebra/tests/integration/test_within_row_lattice.py

(numpy is required; per AGENTS.md it ships with sage.)

Outputs:

    - stdout: agreement summary, parity-of-L profile per (h, n)
    - algebra/tests/integration/test_within_row_lattice_summary.txt:
      the same, captured
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

from predict_q import q_general
from predict_correlation import autocorr_profile_from_row


LATTICE_DIR = os.path.join(REPO, 'experiments', 'acm-champernowne', 'base10',
                           'q_distillery')

PRIMES = (2, 3, 5, 7, 11, 13)
LAGS = list(range(1, 21))
K_MAX_TEST = 4000  # full lattice width
SPOT_K_VALUES = (1, 2, 3, 4, 5, 7, 11, 31, 100, 999, 3999)
SUMMARY_PATH = os.path.join(HERE, 'test_within_row_lattice_summary.txt')
LIVE_HEIGHTS = (6,)  # see Tier B (.gitignore: lattice arrays regenerable)


def lattice_path(h: int) -> str:
    return os.path.join(LATTICE_DIR, f'q_lattice_4000_h{h}.npy')


def load_lattice(h: int):
    p = lattice_path(h)
    if not os.path.exists(p):
        raise FileNotFoundError(p)
    return np.load(p, mmap_mode='r')


def spot_check(lattice, h: int, n: int, log) -> int:
    """Compare lattice[n - 2, k - 1] to float(q_general(n, h, k)) at SPOT_K_VALUES."""
    row_idx = n - 2
    fails = 0
    for k in SPOT_K_VALUES:
        if k > lattice.shape[1]:
            continue
        empirical = float(lattice[row_idx, k - 1])
        predicted = float(q_general(n, h, k))
        diff = abs(empirical - predicted)
        rel = diff / max(1.0, abs(predicted)) if predicted else diff
        if not (rel < 1e-5 or diff < 1e-5):
            log(f'    SPOT FAIL  h={h} n={n} k={k}: '
                f'empirical={empirical:+.6e} predicted={predicted:+.6e} diff={diff:.2e}')
            fails += 1
    return fails


def autocorr_from_predict(n: int, h: int, K_max: int):
    """Build the predicted row of length K_max using predict_q, then autocorr."""
    row = [float(q_general(n, h, k)) for k in range(1, K_max + 1)]
    return autocorr_profile_from_row(row, LAGS), row


def autocorr_from_lattice(lattice, n: int):
    row_idx = n - 2
    row = [float(x) for x in np.asarray(lattice[row_idx, :])]
    return autocorr_profile_from_row(row, LAGS), row


def parity_summary(autocorr: dict) -> dict:
    odd = [autocorr[L] for L in LAGS if L % 2 == 1]
    even = [autocorr[L] for L in LAGS if L % 2 == 0]
    odd_mean = sum(odd) / len(odd)
    even_mean = sum(even) / len(even)
    return {'odd_mean': odd_mean,
            'even_mean': even_mean,
            'gap': even_mean - odd_mean,
            'ratio': (even_mean / odd_mean) if odd_mean else float('nan')}


def main():
    out_lines = []

    def log(*args, **kwargs):
        line = ' '.join(str(a) for a in args)
        print(line, **kwargs)
        out_lines.append(line)

    log('test_within_row_lattice.py')
    log('=' * 70)
    log('')

    total_fails = 0

    for h in LIVE_HEIGHTS:
        log(f'h = {h}')
        log('-' * 70)
        try:
            lat = load_lattice(h)
        except FileNotFoundError as e:
            log(f'  FAIL  declared-live lattice missing: {e}')
            log(f'  regenerate via experiments/acm-champernowne/base10/'
                f'q_distillery/q_lattice_4000_h_regen.py')
            total_fails += 1
            continue

        log(f'  lattice shape: {lat.shape}  '
            f'(rows = n-1, n in 2..{lat.shape[0] + 1};  cols = k, k in 1..{lat.shape[1]})')

        log(f'  spot-check predict_q vs lattice at k = {SPOT_K_VALUES}:')
        for n in PRIMES:
            f = spot_check(lat, h, n, log)
            total_fails += f
            if f == 0:
                log(f'    OK  h={h} n={n}: predict_q matches lattice on all spot k-values')

        log('')
        log(f'  within-row autocorrelation, L = 1..20, K_max = {K_MAX_TEST}:')
        log(f'    {"n":>3}  {"odd-L mean":>12}  {"even-L mean":>12}  '
            f'{"gap (e - o)":>12}  {"ratio e/o":>10}  {"agree":>6}')
        for n in PRIMES:
            ac_pred, _ = autocorr_from_predict(n, h, K_MAX_TEST)
            ac_emp, _ = autocorr_from_lattice(lat, n)

            max_diff = max(abs(ac_pred[L] - ac_emp[L]) for L in LAGS)
            agreement = max_diff < 1e-7

            ps = parity_summary(ac_emp)
            ratio_str = f'{ps["ratio"]:>10.3f}' if abs(ps['odd_mean']) > 1e-15 else '       inf'
            log(f'    {n:>3}  {ps["odd_mean"]:>+12.4e}  {ps["even_mean"]:>+12.4e}  '
                f'{ps["gap"]:>+12.4e}  {ratio_str}  '
                f'{"OK" if agreement else "FAIL":>6}')
            if not agreement:
                total_fails += 1
                log(f'        max |pred - empirical| = {max_diff:.3e}')

        log('')
        log(f'  per-lag profile, n = 2 (illustrative):')
        ac_pred_n2, _ = autocorr_from_predict(2, h, K_MAX_TEST)
        for L in LAGS:
            par = 'odd' if L % 2 else 'even'
            log(f'    L = {L:>2}  ({par})   A = {ac_pred_n2[L]:+.4e}')
        log('')

    log('=' * 70)
    log(f'total disagreements: {total_fails}')
    log('PASS' if total_fails == 0 else 'FAIL')

    with open(SUMMARY_PATH, 'w') as f:
        f.write('\n'.join(out_lines))
    print(f'\n-> {SUMMARY_PATH}')

    return 0 if total_fails == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
