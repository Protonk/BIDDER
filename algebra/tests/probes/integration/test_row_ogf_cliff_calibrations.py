"""
test_row_ogf_cliff_calibrations.py — Layer 6 integration test for the
row_ogf_cliff probe's three calibration runs.

Runs each calibration end-to-end at the panel's full (p, q, e) grid,
asserts every (cell, channel) verdict matches expected_verdicts for
the calibration. Test-side gate for the calibration pattern
documented in `experiments/probes/row_ogf_cliff/PROBE.md`.

What this checks vs. what the probe's own anchors.py checks:
- anchors.py asserts identity calibration only (the probe's contract).
- This test asserts identity, scale_2x, and null calibration patterns,
  including the partial verdicts under scale_2x (where strength is
  (H_max - e) / H_max for the no_op and qe_closed_form channels) and
  the absent verdicts under null.

Substrate is the algebra column (no lattice file required) — the
probe is purely algebra-side. Cost: a few seconds at the panel scale.

Run:

    sage -python algebra/tests/probes/integration/test_row_ogf_cliff_calibrations.py
"""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROBES_TESTS = os.path.dirname(HERE)
TESTS = os.path.dirname(PROBES_TESTS)
ALGEBRA = os.path.dirname(TESTS)
REPO = os.path.dirname(ALGEBRA)
sys.path.insert(0, ALGEBRA)


def load_probe(probe_name: str):
    path = os.path.join(REPO, 'experiments', 'probes', probe_name, 'probe.py')
    spec = importlib.util.spec_from_file_location(f'{probe_name}_probe', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ROC = load_probe('row_ogf_cliff')


def run_calibration(name: str, config: dict, output_dir: str) -> int:
    out = ROC.run_probe(config, output_dir)
    expected = ROC.expected_verdicts(config)
    if expected is None:
        print(f'{name} FAIL  no expected_verdicts entry for config: {config}')
        return 1
    fails = 0
    n_total = 0
    for cell in out['cells']:
        for ch in ROC.CHANNEL_ORDER:
            n_total += 1
            got = out['results'][cell][ch]['verdict']
            want = expected[ch]
            if got != want:
                print(f'{name} FAIL  cell={cell} ch={ch}: '
                      f'got {got!r}, expected {want!r} '
                      f'(strength {out["results"][cell][ch]["strength"]:.6f})')
                fails += 1
    if fails == 0:
        print(f'{name} PASS  {n_total} (cell, channel) verdicts match expected')
    return fails


def main() -> int:
    fails = 0
    common = {
        'primes': list(ROC.DEFAULT_PRIMES),
        'exponents': list(ROC.DEFAULT_EXPONENTS),
        'H_max': ROC.DEFAULT_H_MAX,
    }
    with tempfile.TemporaryDirectory() as tmp:
        fails += run_calibration(
            'identity',
            {**common, 'substrate': 'algebra', 'transducer': 'identity'},
            os.path.join(tmp, 'identity'),
        )
        fails += run_calibration(
            'scale_2x',
            {**common, 'substrate': 'algebra', 'transducer': 'scale_2x'},
            os.path.join(tmp, 'scale_2x'),
        )
        fails += run_calibration(
            'null',
            {**common, 'substrate': 'synth_uniform', 'transducer': 'identity',
             'seed': 0},
            os.path.join(tmp, 'null'),
        )

    print()
    if fails == 0:
        print('ALL CALIBRATIONS PASS')
        return 0
    print(f'TOTAL FAILS: {fails}')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
