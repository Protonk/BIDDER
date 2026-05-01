"""
kernel_zero/anchors.py — the probe's contract.

Runs the probe under the identity transducer on the cached lattice
rows and asserts every channel reports PRESENT at strength 1.0
across the 4 x 6 (h, p) anchor grid.

Source: PROBE.md §"Anchor". Leans on algebra/test_anchors.py
A2 (h=5 matrix), A7 (kernel-zero classifier), A8 (h=6,7,8 matrices).

Usage:
    python3 anchors.py
"""

from __future__ import annotations

import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from probe import (  # noqa: E402
    CHANNEL_ORDER, DEFAULT_HEIGHTS, DEFAULT_K, DEFAULT_LATTICE_DIR,
    DEFAULT_PRIMES, run_probe,
)


def main() -> int:
    """Run identity calibration on the cached lattice. Anchor passes
    iff every (cell, channel) verdict is PRESENT at strength 1.0
    under TOL = 1e-12. This exercises the lattice-vs-algebra contract:
    cached float values must match q_general's exact-rational
    predictions at machine tolerance."""
    config = {
        'substrate': 'lattice',
        'transducer': 'identity',
        'primes': list(DEFAULT_PRIMES),
        'heights': list(DEFAULT_HEIGHTS),
        'K': DEFAULT_K,
        'lattice_dir': DEFAULT_LATTICE_DIR,
    }
    with tempfile.TemporaryDirectory() as tmp:
        out = run_probe(config, tmp)

    fails = 0
    for cell in out['cells']:
        for ch in CHANNEL_ORDER:
            r = out['results'][cell][ch]
            if r['verdict'] != 'present' or r['strength'] < 1.0 - 1e-15:
                print(f'ANCHOR FAIL  cell={cell} channel={ch}: '
                      f'verdict={r["verdict"]} strength={r["strength"]:.12f}')
                fails += 1

    n_total = len(out['cells']) * len(CHANNEL_ORDER)
    if fails == 0:
        print(f'ANCHOR PASS  all {n_total} (cell, channel) verdicts '
              f'PRESENT at strength 1.0')
        return 0
    print(f'ANCHOR FAIL  {fails} of {n_total} (cell, channel) verdicts wrong')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
