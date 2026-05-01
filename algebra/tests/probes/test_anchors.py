"""
test_anchors.py — Layer 1 anchors gate for the probes.

Runs each probe's `anchors.py` and asserts it exits with code 0. The
probe-side `anchors.py` is the contract: identity calibration must
report PRESENT at strength 1.0 across every (cell, channel) in the
panel. This test is the suite-side gate that runs that contract.

A failure here means a probe's contract drifted from its
implementation. Read the probe's `PROBE.md` § "Anchor" and the
relevant `anchors.py`.

Run:

    sage -python algebra/tests/probes/test_anchors.py
"""

from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.dirname(HERE)
ALGEBRA = os.path.dirname(TESTS)
REPO = os.path.dirname(ALGEBRA)


PROBES = [
    ('kernel_zero',
     os.path.join(REPO, 'experiments', 'probes', 'kernel_zero', 'anchors.py')),
    ('row_ogf_cliff',
     os.path.join(REPO, 'experiments', 'probes', 'row_ogf_cliff', 'anchors.py')),
]


def run_probe_anchor(probe_name: str, anchors_path: str) -> int:
    if not os.path.exists(anchors_path):
        print(f'ANCHOR FAIL  {probe_name}: anchors.py missing at {anchors_path}')
        return 1
    # Use the same interpreter the test runs under, which is sage's
    # python when invoked via `sage -python`.
    proc = subprocess.run(
        [sys.executable, anchors_path],
        capture_output=True, text=True, cwd=REPO,
    )
    last_line = proc.stdout.strip().split('\n')[-1] if proc.stdout else ''
    if proc.returncode != 0:
        print(f'ANCHOR FAIL  {probe_name}: exit code {proc.returncode}')
        if proc.stdout:
            print('  stdout (last 20 lines):')
            for line in proc.stdout.strip().split('\n')[-20:]:
                print(f'    {line}')
        if proc.stderr:
            print('  stderr (last 20 lines):')
            for line in proc.stderr.strip().split('\n')[-20:]:
                print(f'    {line}')
        return 1
    print(f'ANCHOR PASS  {probe_name}: {last_line}')
    return 0


def main() -> int:
    fails = 0
    for probe_name, anchors_path in PROBES:
        fails += run_probe_anchor(probe_name, anchors_path)
    print()
    if fails == 0:
        print(f'ALL PROBE ANCHORS PASS ({len(PROBES)} probe(s))')
        return 0
    print(f'TOTAL FAILS: {fails}')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
