"""
cf_spikes.py — Continued-fraction analysis of n-Champernowne reals
==================================================================

For each n in NS, build the n-Champernowne real C_10(n) to high
precision, compute up to MAX_PQ partial quotients, and plot
log10(a_i) vs i. Save spike loci (a_i > SPIKE_THRESHOLD) to CSV.

Brief 2 of EXPERIMENTAL.md. Empirically the spikes are *enormous*
(thousands of decimal digits), so we treat them as bignum throughout
and record their digit-count rather than their value.

Pipeline:
  1. Smoke test against classical Champernowne (OEIS A030167).
  2. For each n, compute CF at PREC_BITS_LO and PREC_BITS_HI.
  3. The longest agreeing prefix is the validated CF; PQs past
     that are precision artifacts and are dropped.
  4. Plot, write CSV, write summary.

Outputs (this directory):
  cf_spikes_n{n}.png       per-n stem plot of log10(a_i) vs i
  cf_spikes.csv            (n, index, pq_digits, pq_log10, pq_head)
                           pq_head is the first 24 decimal digits
  cf_spikes_summary.txt    headline counts per n

Usage:
    sage -python cf_spikes.py
"""

import csv
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'core'))

from acm_core import acm_n_primes

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from mpmath import floor as mfloor
from mpmath import mp, mpf
from mpmath import log10 as mp_log10


NS = [2, 3, 4, 5, 6, 10]
MAX_PQ = 5000
SPIKE_THRESHOLD = 10**4
PREC_BITS_LO = 80000      # ~24 000 decimal digits
PREC_BITS_HI = 160000     # 2x for stability check
K_PRIMES = 20000          # ~80k digits across all n in NS — feeds HI run too


def cf_partial_quotients(frac_digits, max_pq, prec_bits):
    """Return [a_1, a_2, ...] (skipping a_0=0) up to max_pq partial
    quotients of the real 0.<frac_digits>, computed at prec_bits bits."""
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
    """Longest k such that a_lo[:k] == a_hi[:k]. PQs past k are
    precision artifacts in the lower-precision run."""
    k = 0
    upper = min(len(a_lo), len(a_hi))
    while k < upper and a_lo[k] == a_hi[k]:
        k += 1
    return k


def safe_log10(v):
    """log10 of a (possibly huge) Python int. Returns float; for v
    large enough to overflow float we fall back to mpmath."""
    if v <= 0:
        return 0.0
    try:
        return math.log10(v)
    except (OverflowError, ValueError):
        return float(mp_log10(mpf(v)))


def smoke_test():
    """Classical Champernowne 0.123456789101112... has tabulated PQs.
    OEIS A030167: a_5 (1-indexed in the fractional CF) = 149083."""
    digits = ''.join(str(i) for i in range(1, 4000))
    a = cf_partial_quotients(digits, 30, PREC_BITS_LO)
    print(f'[smoke] classical Champernowne first 8 PQs: {a[:8]}')
    expected = [8, 9, 1, 149083, 1, 1, 1, 4]
    if a[:8] != expected:
        raise SystemExit(f'[smoke] FAIL — expected {expected}, got {a[:8]}')
    print('[smoke] PASS — pipeline matches OEIS A030167.')


def plot_one(n, a, n_validated, out_path):
    idx = np.arange(1, len(a) + 1)
    log_a = np.array([safe_log10(max(1, v)) for v in a], dtype=float)
    spike_thr_log = math.log10(SPIKE_THRESHOLD)
    spike_mask = log_a >= spike_thr_log

    fig, ax = plt.subplots(figsize=(13, 4.2))
    ax.vlines(idx, 0, log_a, color='black', lw=0.4, alpha=0.6)
    ax.scatter(idx[spike_mask], log_a[spike_mask], s=22, c='red', zorder=3,
               label=f'a_i > {SPIKE_THRESHOLD} ({int(spike_mask.sum())} spikes)')
    ax.axhline(spike_thr_log, color='red', lw=0.5, ls='--', alpha=0.6)
    if n_validated < len(a):
        ax.axvline(n_validated + 0.5, color='blue', lw=0.7, ls=':',
                   label=f'precision-validated prefix ends at i={n_validated}')
    ax.set_xlabel('CF index i')
    ax.set_ylabel(r'$\log_{10}\, a_i$')
    ax.set_title(f'C$_{{10}}$({n}) — partial quotients '
                 f'(K={K_PRIMES} primes, prec={PREC_BITS_LO} bits, max {MAX_PQ} PQs)')
    ax.set_xlim(0, len(a) + 1)
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close(fig)


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    smoke_test()

    spike_rows = [('n', 'index', 'pq_digits', 'pq_log10', 'pq_head24')]
    summary = []
    for n in NS:
        print(f'\n--- n = {n} ---', flush=True)
        primes = acm_n_primes(n, K_PRIMES)
        digits = ''.join(str(p) for p in primes)
        print(f'  digits available: {len(digits)}', flush=True)

        a_lo = cf_partial_quotients(digits, MAX_PQ, PREC_BITS_LO)
        print(f'  PQs at LO prec ({PREC_BITS_LO}b): {len(a_lo)}', flush=True)
        a_hi = cf_partial_quotients(digits, MAX_PQ, PREC_BITS_HI)
        print(f'  PQs at HI prec ({PREC_BITS_HI}b): {len(a_hi)}', flush=True)
        n_validated = stable_prefix_len(a_lo, a_hi)
        print(f'  stable prefix: {n_validated} PQs match', flush=True)
        if n_validated < min(len(a_lo), len(a_hi)):
            divergence = a_lo[n_validated] if n_validated < len(a_lo) else None
            print(f'  divergence at index {n_validated+1}; '
                  f'LO has a={str(divergence)[:24]}…')

        # Use only the validated PQs.
        a = a_lo[:n_validated]

        spikes = [(i + 1, a[i]) for i in range(len(a)) if a[i] > SPIKE_THRESHOLD]
        max_v = max(a) if a else 0
        max_i = a.index(max_v) + 1 if a else 0
        print(f'  spikes (a_i > {SPIKE_THRESHOLD}): {len(spikes)}')
        for i, v in spikes[:6]:
            d = len(str(v))
            head = str(v)[:24] + ('…' if d > 24 else '')
            print(f'    i={i:>5}  digits={d:>5}  log10≈{safe_log10(v):.2f}  head={head}')
        if max_v:
            d = len(str(max_v))
            print(f'  max a_i: {d}-digit int at CF index {max_i}, '
                  f'log10≈{safe_log10(max_v):.2f}')

        for i, v in spikes:
            d = len(str(v))
            head = str(v)[:24]
            spike_rows.append((n, i, d, f'{safe_log10(v):.4f}', head))
        summary.append((n, len(a), len(a_lo), n_validated,
                        len(spikes), len(str(max_v)) if max_v else 0, max_i))

        out_path = os.path.join(out_dir, f'cf_spikes_n{n}.png')
        # Plot uses validated PQs; no point showing precision-noise tail.
        plot_one(n, a, n_validated, out_path)
        print(f'  wrote {out_path}')

    csv_path = os.path.join(out_dir, 'cf_spikes.csv')
    with open(csv_path, 'w', newline='') as f:
        csv.writer(f).writerows(spike_rows)
    print(f'\nwrote {csv_path}')

    summary_path = os.path.join(out_dir, 'cf_spikes_summary.txt')
    with open(summary_path, 'w') as f:
        f.write(f'cf_spikes — '
                f'MAX_PQ={MAX_PQ}, K_PRIMES={K_PRIMES}, '
                f'PREC_BITS_LO={PREC_BITS_LO}, PREC_BITS_HI={PREC_BITS_HI}, '
                f'SPIKE_THRESHOLD={SPIKE_THRESHOLD}\n\n')
        f.write(f'{"n":>3}  {"valid":>5}  {"pq_lo":>5}  {"stable":>6}  '
                f'{"spikes":>6}  {"max_digits":>10}  {"max_idx":>7}\n')
        for n, nvalid, npqlo, nstab, ns, mdig, mi in summary:
            f.write(f'{n:>3}  {nvalid:>5}  {npqlo:>5}  {nstab:>6}  '
                    f'{ns:>6}  {mdig:>10}  {mi:>7}\n')
    print(f'wrote {summary_path}')


if __name__ == '__main__':
    main()
