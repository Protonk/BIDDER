"""
row_ogf_cliff/anchors.py — the probe's contract.

Runs the probe under the identity transducer on the algebra-evaluated
substrate and asserts every channel reports PRESENT at strength 1.0
across the (p, q, e) panel.

Source: PROBE.md §"Anchor". Leans on algebra/tests/test_anchors.py
A1 (prime-row identity at h=1), A7 (kernel-zero classifier read
column-wise), A10 (row-OGF degree, leading coefficient, qe closed
form, row sum).

Usage:
    sage -python anchors.py
"""

from __future__ import annotations

import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from probe import (  # noqa: E402
    CHANNEL_ORDER, DEFAULT_EXPONENTS, DEFAULT_H_MAX, DEFAULT_PRIMES,
    run_probe,
)


def main() -> int:
    """Run identity calibration on the algebra column. Anchor passes
    iff every (cell, channel) verdict is PRESENT at strength 1.0
    under TOL = 1e-12. This witnesses ROW-OGF.md (A10) jointly with
    KERNEL-ZEROS.md (ii) (A7) at the substrate: the leading
    coefficient of the prime-row OGF must equal the kernel-zero
    boundary multinomial, and the row must truncate at exactly
    h = Ω(k') + 1."""
    config = {
        'substrate': 'algebra',
        'transducer': 'identity',
        'primes': list(DEFAULT_PRIMES),
        'exponents': list(DEFAULT_EXPONENTS),
        'H_max': DEFAULT_H_MAX,
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
