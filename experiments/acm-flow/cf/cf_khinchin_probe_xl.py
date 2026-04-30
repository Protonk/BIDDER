"""
cf_khinchin_probe_xl.py — Khinchin / off-spike CF at extended precision
========================================================================

Attempted power-up of cf_khinchin_probe.py: 5x LO/HI precision
(80k/160k -> 400k/800k bits) and 10x n-primes (20k -> 200k), with the
goal of extending the validated CF prefix from 400-840 PQs per cell
to several thousand, so that the marginal Khinchin probe could power
up at T in {10, 12, 14, 16}.

OUTCOME: the validated prefix did NOT extend. Partial run on
n = 2, 3, 4 returned 407, 487, 515 validated PQs — same as the
original probe's 408, 487, 514 (within +/-1). The validation
bottleneck is floor sensitivity at the LO/HI divergence step,
not LO precision. At each step the floor of `1/frac` can flip
between LO and HI when their tiny rounding errors land on opposite
sides of an integer, regardless of how much precision either has.
Increasing both precisions shifts but does not raise this ceiling
proportionally.

Reaching k = 5 canonical boundaries needs a different validation
strategy:
  (a) multi-precision triangulation (compare 3+ precisions);
  (b) exact rational arithmetic on truncated input;
  (c) interval arithmetic with rigorous error bounds.

Not pursued here. The block-aggregate substrate test in
DENOMINATOR-PROCESS.md works on the existing 400-840-PQ
validated data and does not need a longer prefix.

Outputs:
  cf_khinchin_probe_xl.csv               per-(n, i): log10_a, log2_a_plus_1, is_spike
  cf_khinchin_probe_xl_summary.txt       survival table per n
  cf_khinchin_probe_xl_survival.png      survival curves overlaid on Khinchin
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
MAX_PQ = 30_000
LOG10_SPIKE = 3.0
PREC_BITS_LO = 400_000      # ~120 000 decimal digits
PREC_BITS_HI = 800_000      # 2x for stability check
K_PRIMES = 200_000          # plenty of substrate to feed the validation
THRESHOLDS = [4, 6, 8, 10, 12, 14, 16, 18, 20]
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

    csv_path = os.path.join(HERE, 'cf_khinchin_probe_xl.csv')
    with open(csv_path, 'w', newline='') as f:
        csv.writer(f).writerows(rows)
    print(f'\nwrote {csv_path}')

    summary_lines = [
        '# cf_khinchin_probe_xl — extended-precision Khinchin probe',
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

    summary_path = os.path.join(HERE, 'cf_khinchin_probe_xl_summary.txt')
    with open(summary_path, 'w') as f:
        f.write('\n'.join(summary_lines) + '\n')
    print(f'wrote {summary_path}')
    print()
    print('\n'.join(summary_lines))

    # Plot.
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
    plot_path = os.path.join(HERE, 'cf_khinchin_probe_xl_survival.png')
    plt.savefig(plot_path, dpi=140)
    print(f'wrote {plot_path}')


if __name__ == '__main__':
    main()
