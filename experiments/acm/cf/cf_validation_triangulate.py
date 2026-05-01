"""
cf_validation_triangulate.py — what bounds the validated CF prefix?

The XL probe (cf_khinchin_probe_xl.py) found that 5x precision did
NOT extend the LO/HI agreement length. Possible explanations:

  (H1) Floor-sensitivity. At the divergence step, both LO and HI
       compute floor(1/frac) — small rounding errors flip the floor
       across an integer. Higher precision shifts but doesn't raise
       this ceiling.

  (H2) Input truncation. mpmath's mpf parser caps decimal-string
       digits at the current mp.prec, so LO at 80k bits sees ~24k
       digits, LO at 400k bits sees ~120k digits — but the CF only
       reaches L_i ≈ 1500 decimal digits before validation stops,
       which is far below either input cap.

  (H3) Some other interaction.

Triangulation: compute n=2 CF at 4 precisions (80k, 200k, 400k, 800k
bits) and report the pairwise stable_prefix_len. If H1 is right,
we'd expect very similar values across all pairs, with the agreement
cap intrinsic to the data. If H2 is right, increasing precision should
unlock more PQs proportionally.
"""

import math
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'core'))

from acm_core import acm_n_primes
from mpmath import floor as mfloor
from mpmath import mp, mpf


N = 2
K_PRIMES = 50_000
MAX_PQ = 1500
PRECS = [80_000, 200_000, 400_000, 800_000]


def cf_partial_quotients(frac_digits, max_pq, prec_bits):
    mp.prec = prec_bits
    x = mpf('0.' + frac_digits)
    a = []
    for _ in range(max_pq):
        frac = x - mfloor(x)
        if frac == 0:
            break
        x = 1 / frac
        ai = int(mfloor(x))
        a.append(ai)
    return a


def stable_prefix_len(a1, a2):
    k = 0
    upper = min(len(a1), len(a2))
    while k < upper and a1[k] == a2[k]:
        k += 1
    return k


def main():
    primes = acm_n_primes(N, K_PRIMES)
    digits = ''.join(str(p) for p in primes)
    print(f'n = {N}, digits available = {len(digits)}')

    runs = {}
    for prec in PRECS:
        t0 = time.time()
        a = cf_partial_quotients(digits, MAX_PQ, prec)
        elapsed = time.time() - t0
        runs[prec] = a
        print(f'  prec = {prec:>7}b: {len(a)} PQs in {elapsed:5.1f}s')

    print('\nPairwise stable_prefix_len:')
    print(f'  {"":>9}', end='')
    for p in PRECS:
        print(f'  {p:>8}b', end='')
    print()
    for p1 in PRECS:
        print(f'  {p1:>7}b ', end='')
        for p2 in PRECS:
            if p1 == p2:
                print(f'    {len(runs[p1]):>5} ', end='')
            else:
                k = stable_prefix_len(runs[p1], runs[p2])
                print(f'    {k:>5} ', end='')
        print()

    # First divergence index (1-based) for each pair, with truncated
    # PQ display since the divergent values can be spike-sized.
    def short(v):
        s = str(v)
        if len(s) <= 16:
            return s
        return f'{s[:8]}...({len(s)} digits)'

    print('\nFirst-divergence diagnostics for prec_lo vs prec_hi:')
    for p_hi in [200_000, 400_000, 800_000]:
        a_hi = runs[p_hi]
        for p_lo in [p for p in PRECS if p < p_hi]:
            a_lo = runs[p_lo]
            k = stable_prefix_len(a_lo, a_hi)
            if k < min(len(a_lo), len(a_hi)):
                print(f'  prec_lo={p_lo}, prec_hi={p_hi}: '
                      f'agree {k} PQs; '
                      f'a_lo[{k+1}]={short(a_lo[k])}, '
                      f'a_hi[{k+1}]={short(a_hi[k])}')


if __name__ == '__main__':
    main()
