"""
test_kernel_zero_calibrations.py — Layer 6 integration test for the
kernel_zero probe's three calibration runs.

Runs each calibration end-to-end at the panel's full K and (p, h)
grid, asserts every (cell, channel) verdict matches expected_verdicts
for the calibration. This is the test-side gate that the calibration
pattern documented in PROBE.md and FIRST-CALIBRATION.md still holds.

What this checks vs. what the probe's own anchors.py checks:
- anchors.py asserts identity calibration only (the probe's contract).
- This test asserts identity, reverse, and null calibration patterns,
  including the partial verdicts under reverse and the absent verdicts
  under null.

A failure here means the calibration pattern shifted. Read the run's
report.md and figures/ in the per-test output directory.

Cost: ~2 minutes total (24 cells x 4000 K x 3 calibrations, with the
algebra evaluator's lru_cache amortising across cells). Slow mode;
run on demand, not every commit.

Requires the committed h=6 lattice; uses h=6 only to keep the test
self-contained without needing to regenerate other heights.

Run:

    sage -python algebra/tests/probes/integration/test_kernel_zero_calibrations.py
"""

from __future__ import annotations

import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROBES_TESTS = os.path.dirname(HERE)
TESTS = os.path.dirname(PROBES_TESTS)
ALGEBRA = os.path.dirname(TESTS)
REPO = os.path.dirname(ALGEBRA)
sys.path.insert(0, ALGEBRA)
sys.path.insert(0, os.path.join(REPO, 'experiments', 'probes', 'kernel_zero'))

from probe import (  # noqa: E402
    CHANNEL_ORDER, DEFAULT_LATTICE_DIR, DEFAULT_PRIMES, expected_verdicts,
    run_probe,
)


COMMITTED_HEIGHT = 6
HEIGHTS_FOR_INTEGRATION = (COMMITTED_HEIGHT,)
K = 4000


def run_calibration(name: str, config: dict, output_dir: str) -> int:
    out = run_probe(config, output_dir)
    expected = expected_verdicts(config)
    if expected is None:
        print(f'{name} FAIL  no expected_verdicts entry for config: {config}')
        return 1
    fails = 0
    n_total = 0
    for cell in out['cells']:
        for ch in CHANNEL_ORDER:
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
    lattice_path = os.path.join(DEFAULT_LATTICE_DIR,
                                f'q_lattice_4000_h{COMMITTED_HEIGHT}.npy')
    if not os.path.exists(lattice_path):
        print(f'INTEGRATION FAIL  committed h={COMMITTED_HEIGHT} lattice missing '
              f'at {lattice_path}')
        return 1

    fails = 0
    common = {
        'primes': list(DEFAULT_PRIMES),
        'heights': list(HEIGHTS_FOR_INTEGRATION),
        'K': K,
        'lattice_dir': DEFAULT_LATTICE_DIR,
    }

    with tempfile.TemporaryDirectory() as tmp:
        fails += run_calibration(
            'identity',
            {**common, 'substrate': 'lattice', 'transducer': 'identity'},
            os.path.join(tmp, 'identity'),
        )
        fails += run_calibration(
            'reverse',
            {**common, 'substrate': 'lattice', 'transducer': 'reverse'},
            os.path.join(tmp, 'reverse'),
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
