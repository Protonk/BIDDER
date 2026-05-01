"""
cf_khinchin_probe_xxl.py — push validation past the k=5 mega-spike

Triangulation (cf_validation_triangulate.py) showed that for n=2 at
b=10, the LO/HI agreement caps at 407 PQs because i=408 is the k=5
boundary spike with ~102 765 decimal digits — too large to validate at
LO=400k / HI=800k.

This probe goes to LO=1.5M bits (≈ 450k decimal digits) and HI=3M bits
(≈ 900k decimal digits), which should validate past the k=5 mega-spike
for low-n cells and extend the validated prefix.

Compute scales roughly as O(prec * log prec) per CF step. At 1.5M bits
and ~600 PQs per cell, expect 30s LO + 60s HI = ~90s per cell, ~10 min
for the full panel.

Outputs the same shape as cf_khinchin_probe.py but with a different
file prefix.
"""

import csv
import math
import os
import sys
import time
from math import log2

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'core'))

from acm_core import acm_n_primes

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mpmath import floor as mfloor
from mpmath import mp, mpf
from mpmath import log10 as mp_log10


NS = [2, 3, 4, 5, 6, 10]
MAX_PQ = 2000
LOG10_SPIKE = 3.0
PREC_BITS_LO = 1_500_000
PREC_BITS_HI = 3_000_000
K_PRIMES = 100_000
# Survival thresholds. T must satisfy 2^T - 1 < 10^LOG10_SPIKE so the
# survival range a >= 2^T does not collide with the spike mask
# (a > 10^LOG10_SPIKE) — otherwise off-spike T-tail counts are forced
# to zero by the masking and produce spurious z-scores. With
# LOG10_SPIKE = 3, 10^3 = 1000 ≈ 2^9.97, so T <= 9 is safe.
THRESHOLDS = [4, 5, 6, 7, 8, 9]
HERE = os.path.dirname(os.path.abspath(__file__))


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


def stable_prefix_len(a_lo, a_hi):
    k = 0
    upper = min(len(a_lo), len(a_hi))
    while k < upper and a_lo[k] == a_hi[k]:
        k += 1
    return k


def safe_log10(v):
    if v <= 0:
        return 0.0
    try:
        return math.log10(v)
    except (OverflowError, ValueError):
        return float(mp_log10(mpf(v)))


def safe_log2_plus_1(v):
    if v <= 0:
        return 0.0
    bl = (v + 1).bit_length()
    if bl <= 53:
        return log2(v + 1)
    return safe_log10(v + 1) / math.log10(2)


def khinchin_survival(T):
    return log2(1.0 + 1.0 / (2 ** T))


def smoke_test():
    digits = ''.join(str(i) for i in range(1, 4000))
    a = cf_partial_quotients(digits, 30, 80_000)
    expected = [8, 9, 1, 149083, 1, 1, 1, 4]
    if a[:8] != expected:
        raise SystemExit(f'[smoke] FAIL — expected {expected}, got {a[:8]}')
    print('[smoke] PASS — pipeline matches OEIS A030167.', flush=True)


def compute_one(n):
    print(f'\n--- n = {n} ---', flush=True)
    t0 = time.time()
    primes = acm_n_primes(n, K_PRIMES)
    digits = ''.join(str(p) for p in primes)
    print(f'  digits available: {len(digits)}  '
          f'({time.time() - t0:.1f}s prime-gen)', flush=True)

    t0 = time.time()
    a_lo = cf_partial_quotients(digits, MAX_PQ, PREC_BITS_LO)
    print(f'  PQs at LO ({PREC_BITS_LO}b): {len(a_lo)}  '
          f'({time.time() - t0:.1f}s)', flush=True)
    t0 = time.time()
    a_hi = cf_partial_quotients(digits, MAX_PQ, PREC_BITS_HI)
    print(f'  PQs at HI ({PREC_BITS_HI}b): {len(a_hi)}  '
          f'({time.time() - t0:.1f}s)', flush=True)
    n_validated = stable_prefix_len(a_lo, a_hi)
    print(f'  validated prefix: {n_validated}', flush=True)
    return a_lo[:n_validated]


def main():
    smoke_test()

    rows = [('n', 'i', 'log10_a', 'log2_a_plus_1', 'is_spike')]
    per_n_data = {}

    for n in NS:
        a = compute_one(n)
        if not a:
            continue

        log10s = [safe_log10(v) for v in a]
        log2s = [safe_log2_plus_1(v) for v in a]
        spikes = [l > LOG10_SPIKE for l in log10s]
        n_spikes = sum(spikes)
        print(f'  total PQs: {len(a)};  '
              f'spikes (log10 a > {LOG10_SPIKE}): {n_spikes}',
              flush=True)

        for i in range(len(a)):
            rows.append((n, i + 1,
                         f'{log10s[i]:.4f}',
                         f'{log2s[i]:.4f}',
                         int(spikes[i])))

        per_n_data[n] = {
            'log10': log10s,
            'log2': log2s,
            'spikes': spikes,
            'count': len(a),
            'n_spikes': n_spikes,
        }

    csv_path = os.path.join(HERE, 'cf_khinchin_probe_xxl.csv')
    with open(csv_path, 'w', newline='') as f:
        csv.writer(f).writerows(rows)
    print(f'\nwrote {csv_path}')

    summary_lines = [
        '# cf_khinchin_probe_xxl — past-k=5 validation probe',
        f'# K_PRIMES={K_PRIMES}  MAX_PQ={MAX_PQ}  '
        f'LOG10_SPIKE={LOG10_SPIKE}',
        f'# PREC_BITS_LO={PREC_BITS_LO}  PREC_BITS_HI={PREC_BITS_HI}',
        f'# Khinchin survival: P(log2(a+1) > T) = log2(1 + 1/2^T)',
        '',
    ]

    for n, dat in per_n_data.items():
        log2s = dat['log2']
        spikes = dat['spikes']
        offspike = [log2s[i] for i in range(len(log2s)) if not spikes[i]]
        n_off = len(offspike)
        n_on = len(log2s) - n_off

        summary_lines.append(f'## n = {n}')
        summary_lines.append(f'  validated PQs : {len(log2s)}')
        summary_lines.append(f'  spike PQs     : {n_on}  '
                             f'(log10 a > {LOG10_SPIKE})')
        summary_lines.append(f'  off-spike PQs : {n_off}')
        summary_lines.append('')
        summary_lines.append(
            f'  {"T":>3}  {"obs":>6}  {"Khinch":>10}  '
            f'{"obs/Khinch":>11}  {"z":>7}'
        )
        for T in THRESHOLDS:
            obs = sum(1 for x in offspike if x > T)
            p = khinchin_survival(T)
            expected = n_off * p
            ratio = obs / expected if expected > 0 else float('inf')
            sd = math.sqrt(n_off * p * (1 - p)) if 0 < p < 1 else 0
            z = (obs - expected) / sd if sd > 0 else float('nan')
            summary_lines.append(
                f'  {T:>3}  {obs:>6d}  {expected:>10.3f}  '
                f'{ratio:>11.3f}  {z:>7.2f}'
            )
        summary_lines.append('')

    summary_path = os.path.join(HERE, 'cf_khinchin_probe_xxl_summary.txt')
    with open(summary_path, 'w') as f:
        f.write('\n'.join(summary_lines) + '\n')
    print(f'wrote {summary_path}')
    print()
    print('\n'.join(summary_lines))

    fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharey=True)
    for ax, n in zip(axes.flat, NS):
        if n not in per_n_data:
            ax.set_visible(False)
            continue
        dat = per_n_data[n]
        offspike = [dat['log2'][i] for i in range(len(dat['log2']))
                    if not dat['spikes'][i]]
        n_off = len(offspike)
        Ts = THRESHOLDS
        obs = [sum(1 for x in offspike if x > T) for T in Ts]
        kh = [n_off * khinchin_survival(T) for T in Ts]
        ax.plot(Ts, kh, 's-', color='gray',
                label='Khinchin (Gauss–Kuzmin)',
                markersize=6, linewidth=1.2)
        ax.plot(Ts, obs, 'o-', color='crimson',
                label=f'C_10({n}) off-spike',
                markersize=6, linewidth=1.2)
        ax.set_yscale('log')
        ax.set_title(f'n = {n}  ({n_off} off-spike PQs)')
        ax.set_xlabel('threshold T: log2(a+1) > T')
        ax.grid(True, alpha=0.3, which='both')
        ax.legend(fontsize=8)
    axes[0, 0].set_ylabel('count (log scale)')
    axes[1, 0].set_ylabel('count (log scale)')
    plt.tight_layout()
    plot_path = os.path.join(HERE, 'cf_khinchin_probe_xxl_survival.png')
    plt.savefig(plot_path, dpi=140)
    print(f'wrote {plot_path}')


if __name__ == '__main__':
    main()
