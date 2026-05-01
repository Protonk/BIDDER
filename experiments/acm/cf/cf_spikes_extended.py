"""
cf_spikes_extended.py — extended (b, n, d) panel for the closed-form
====================================================================

Tests the closed-form spike prediction from MEGA-SPIKE.md:

    spike_baseb_digits(n, d, b)  ≈  (n − 1)/n²  ·  F(d, b)
    F(d, b)  =  d (b − 2) b^(d−1)  +  (b^d − 1) / (b − 1)

across two extension axes:

  1. n-monotone drift at fixed (b, d) = (10, 4):
     n ∈ {7, 8, 9, 11, 12, 13, 15, 20} (extends cf_spikes.py's
     {2, 3, 4, 5, 6, 10} panel).
  2. (b − 2)/(b − 1) base-b prefactor:
     b ∈ {3, 4, 6, 8, 12}, n ∈ {2, 3, 5}, d chosen per b so the
     predicted spike is well above 100 decimal digits.

For each (b, n, d) the script
  - generates K_PRIMES n-primes (sized to cover the d-block + buffer),
  - converts them to a base-b digit list,
  - builds the real `0.d_1 d_2 …` (in base b) at LO and HI mp precision,
  - runs the reciprocal-and-floor CF loop, tracking convergent
    denominators q_i alongside partial quotients a_i,
  - keeps the precision-validated prefix only,
  - identifies the d-block boundary spike via the cumulative-digit
    identity  2·log_b q_{i−1} + log_b a_i ≈ C_d(n).

The Mahler smoke test from cf_spikes.py runs at start as a pipeline
guard.

Outputs (this directory):
  cf_extended_summary.txt   — main per-(b, n, d) table
  cf_extended.csv           — same data in CSV form

Usage:
    sage -python cf_spikes_extended.py

The full panel takes ~15–45 minutes depending on machine. Set
QUICK_PANEL_ONLY = True to run just the b=10 extension (~5 minutes).
"""

import csv
import math
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'core'))

from acm_core import acm_n_primes

from mpmath import floor as mfloor
from mpmath import mp, mpf
from mpmath import log10 as mp_log10

# ---------------------------------------------------------------------------
# Panel
# ---------------------------------------------------------------------------

QUICK_PANEL_ONLY = False  # if True, skips the heavier other-base cases

PANEL_N_AT_B10D4 = [(10, n, 4) for n in (7, 8, 9, 11, 12, 13, 15, 20)]

# d per base chosen so predicted spike ≥ ~100 decimal digits
PANEL_OTHER_BASES = [
    (3,  2, 8), (3,  3, 8), (3,  5, 8),
    (4,  2, 6), (4,  3, 6), (4,  5, 6),
    (6,  2, 5), (6,  3, 5), (6,  5, 5),
    (8,  2, 4), (8,  3, 4), (8,  5, 4),
    (12, 2, 4), (12, 3, 4), (12, 5, 4),
]


def panel():
    if QUICK_PANEL_ONLY:
        return PANEL_N_AT_B10D4
    return PANEL_N_AT_B10D4 + PANEL_OTHER_BASES


# ---------------------------------------------------------------------------
# Closed-form predictor
# ---------------------------------------------------------------------------

def F_formula(d, b):
    """F(d, b) = d (b-2) b^(d-1) + (b^d - 1)/(b - 1)."""
    return d * (b - 2) * b**(d - 1) + (b**d - 1) // (b - 1)


def predicted_spike_baseb_digits(n, d, b):
    """Leading-order spike size in base-b digits (smooth case)."""
    return F_formula(d, b) * (n - 1) / (n * n)


def cumulative_baseb_digits(n, d, b):
    """C_d(n) — cumulative base-b digits through end of the d-th block."""
    s = sum(j * b**(j - 1) for j in range(1, d + 1))
    return (n - 1) * (b - 1) * s / (n * n)


# ---------------------------------------------------------------------------
# Base-b digit utilities
# ---------------------------------------------------------------------------

def int_to_baseb_digits(value, b):
    """Most-significant-first list of base-b digits in [0, b-1]."""
    if value == 0:
        return [0]
    out = []
    while value > 0:
        out.append(value % b)
        value //= b
    out.reverse()
    return out


def n_primes_baseb_digits(n, K, b):
    """Concatenated base-b digits of the first K n-primes."""
    primes = acm_n_primes(n, K)
    out = []
    for p in primes:
        out.extend(int_to_baseb_digits(p, b))
    return out


# ---------------------------------------------------------------------------
# CF expansion with convergent denominators
# ---------------------------------------------------------------------------

def cf_with_convergents(digits, b, max_pq, prec_bits):
    """For x = 0.d_1 d_2 … (base b), return (a_list, q_list) where
    a_list = [a_1, a_2, …] are partial quotients and q_list[i] = q_i
    is the i-th convergent denominator (Python int; q_0 = 1, q_{-1} = 0)."""
    mp.prec = prec_bits
    L = len(digits)
    # Read digits as an integer in base b: N = sum d_i b^(L-i)
    N = 0
    for d in digits:
        N = N * b + d
    x = mpf(N) / (mpf(b) ** L)

    a_list = []
    q_prev, q_curr = 0, 1
    q_list = [q_curr]
    for _ in range(max_pq):
        frac = x - mfloor(x)
        if frac == 0:
            break
        x = 1 / frac
        ai = int(mfloor(x))
        a_list.append(ai)
        q_prev, q_curr = q_curr, ai * q_curr + q_prev
        q_list.append(q_curr)
    return a_list, q_list


def stable_prefix_len(a_lo, a_hi):
    k = 0
    upper = min(len(a_lo), len(a_hi))
    while k < upper and a_lo[k] == a_hi[k]:
        k += 1
    return k


# ---------------------------------------------------------------------------
# Spike identification via cumulative-digit identity
# ---------------------------------------------------------------------------

def find_d_boundary_spike(a_list, q_list, n, d_target, b, slack=None):
    """Locate the maximum a_i in the validated prefix whose
    `2 log_b q_{i-1} + log_b a_i` lands within `slack` base-b digits of
    C_{d_target}(n). For non-smooth (b, n, d) the smooth-case C_d formula
    is off by up to (b-1)·d due to the spread bound; default slack is
    max(10, 2·(b-1)·d). Returns (idx_1based, a_value) or (None, None)."""
    if slack is None:
        slack = max(10.0, 2.0 * (b - 1) * d_target)
    target_C = float(cumulative_baseb_digits(n, d_target, b))
    log_b = math.log(b)
    best_i = None
    best_a = -1
    for idx, a in enumerate(a_list):
        if a < 2:
            continue
        i = idx + 1
        # q_{i-1} is q_list[i-1]
        q_prev = q_list[i - 1]
        if q_prev <= 0:
            continue
        log_a = math.log(a) / log_b
        log_q = math.log(q_prev) / log_b
        identity = 2 * log_q + log_a
        if abs(identity - target_C) <= slack and a > best_a:
            best_a = a
            best_i = i
    return best_i, (best_a if best_i is not None else None)


# ---------------------------------------------------------------------------
# Smoke test (Mahler classical Champernowne, base 10)
# ---------------------------------------------------------------------------

def smoke_test():
    """Reproduces OEIS A030167 a_4 = 149083 for the classical
    Champernowne in base 10."""
    digits = []
    for v in range(1, 4000):
        digits.extend(int_to_baseb_digits(v, 10))
    a, _ = cf_with_convergents(digits, 10, 30, 80000)
    expected = [8, 9, 1, 149083, 1, 1, 1, 4]
    if a[:8] != expected:
        raise SystemExit(f'[smoke] FAIL — expected {expected}, got {a[:8]}')
    print(f'[smoke] PASS — Mahler a_4=149083 reproduced.')


# ---------------------------------------------------------------------------
# One panel cell
# ---------------------------------------------------------------------------

def safe_log10(v):
    if v <= 0:
        return 0.0
    try:
        return math.log10(v)
    except (OverflowError, ValueError):
        return float(mp_log10(mpf(v)))


def run_one(b, n, d):
    pred_spike_baseb = predicted_spike_baseb_digits(n, d, b)
    pred_spike_dec = pred_spike_baseb * math.log10(b)

    # K_PRIMES: cover all n-primes ≤ b^d, plus a 50% buffer floor 200
    n_primes_in_d_block = b**d * (n - 1) / (n * n)
    K = max(200, int(1.5 * n_primes_in_d_block) + 100)

    # Precision floor at 80 000 bits (matches cf_spikes.py); above that,
    # scale to ~3.5× the predicted spike in bits so the cross-precision
    # check has headroom past the boundary.
    bits_per_baseb_digit = math.log(b) / math.log(2)
    pred_spike_bits = pred_spike_baseb * bits_per_baseb_digit
    prec_lo = max(80000, int(3.5 * pred_spike_bits))
    prec_hi = 2 * prec_lo

    cum_C_d_dec = float(cumulative_baseb_digits(n, d, b)) * math.log10(b)
    # MAX_PQ: well past the d-block, capped so we don't run forever.
    max_pq = max(500, int(2.0 * cum_C_d_dec))
    max_pq = min(max_pq, 8000)

    print(
        f'\n--- (b={b}, n={n}, d={d}) ---\n'
        f'  predicted spike ≈ {pred_spike_baseb:.1f} base-{b} digits '
        f'= {pred_spike_dec:.1f} decimal digits\n'
        f'  K_PRIMES={K}, prec_lo={prec_lo}, prec_hi={prec_hi}, max_pq={max_pq}',
        flush=True,
    )

    digits = n_primes_baseb_digits(n, K, b)
    print(f'  total base-{b} digits available: {len(digits)}', flush=True)

    t0 = time.time()
    a_lo, q_lo = cf_with_convergents(digits, b, max_pq, prec_lo)
    t_lo = time.time() - t0
    print(f'  LO CF: {len(a_lo)} PQs, {t_lo:.1f}s', flush=True)

    t0 = time.time()
    a_hi, q_hi = cf_with_convergents(digits, b, max_pq, prec_hi)
    t_hi = time.time() - t0
    print(f'  HI CF: {len(a_hi)} PQs, {t_hi:.1f}s', flush=True)

    n_validated = stable_prefix_len(a_lo, a_hi)
    print(f'  validated prefix: {n_validated} PQs', flush=True)

    a = a_lo[:n_validated]
    q = q_lo[:n_validated + 1]

    spike_i, spike_a = find_d_boundary_spike(a, q, n, d, b)
    if spike_i is None:
        print(f'  [no d={d} boundary spike found in validated prefix]', flush=True)
        return {
            'b': b, 'n': n, 'd': d, 'K': K,
            'prec_lo': prec_lo, 'validated': n_validated,
            'pred_spike_baseb': pred_spike_baseb,
            'pred_spike_decimal': pred_spike_dec,
            'observed_idx': None,
            'observed_baseb': None,
            'observed_decimal': None,
            'gap_baseb': None,
            'gap_pct': None,
        }

    log_b = math.log(b)
    obs_baseb = math.log(spike_a) / log_b
    obs_dec = math.log10(spike_a)
    gap_baseb = obs_baseb - pred_spike_baseb
    gap_pct = 100.0 * gap_baseb / pred_spike_baseb if pred_spike_baseb else 0.0

    print(
        f'  spike at i={spike_i}: a has {len(str(spike_a))} decimal digits '
        f'(log_{b}={obs_baseb:.2f}, log_10={obs_dec:.2f})\n'
        f'  predicted log_{b}: {pred_spike_baseb:.2f}; gap = {gap_baseb:+.2f} '
        f'base-{b} digits = {gap_pct:+.3f}%',
        flush=True,
    )

    return {
        'b': b, 'n': n, 'd': d, 'K': K,
        'prec_lo': prec_lo, 'validated': n_validated,
        'pred_spike_baseb': pred_spike_baseb,
        'pred_spike_decimal': pred_spike_dec,
        'observed_idx': spike_i,
        'observed_baseb': obs_baseb,
        'observed_decimal': obs_dec,
        'gap_baseb': gap_baseb,
        'gap_pct': gap_pct,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main():
    print('Closed form: spike_baseb_digits(n,d) ≈ (n-1)/n² · F(d,b)')
    print('             F(d,b) = d(b-2)b^(d-1) + (b^d - 1)/(b - 1)')
    print()
    smoke_test()

    rows = []
    for b, n, d in panel():
        try:
            rows.append(run_one(b, n, d))
        except Exception as e:
            print(f'  FAIL ({b},{n},{d}): {e}', flush=True)
            rows.append({'b': b, 'n': n, 'd': d, 'error': str(e)})

    out_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(out_dir, 'cf_extended.csv')
    summary_path = os.path.join(out_dir, 'cf_extended_summary.txt')

    fieldnames = [
        'b', 'n', 'd', 'K', 'prec_lo', 'validated',
        'pred_spike_baseb', 'pred_spike_decimal',
        'observed_idx', 'observed_baseb', 'observed_decimal',
        'gap_baseb', 'gap_pct',
    ]
    with open(csv_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k) for k in fieldnames})
    print(f'\nwrote {csv_path}', flush=True)

    with open(summary_path, 'w') as f:
        f.write('cf_spikes_extended — closed-form panel\n')
        f.write('=' * 78 + '\n\n')
        f.write('spike_baseb_digits(n,d) ≈ (n-1)/n² · F(d,b)\n')
        f.write('F(d,b) = d(b-2)b^(d-1) + (b^d - 1)/(b - 1)\n\n')
        f.write(
            f'{"b":>3} {"n":>3} {"d":>3} '
            f'{"pred_b-d":>10} {"obs_b-d":>10} {"gap":>9} {"gap%":>8} '
            f'{"i":>5} {"valid":>6}\n'
        )
        f.write('-' * 78 + '\n')
        for r in rows:
            if r.get('error') or r.get('observed_idx') is None:
                err = r.get('error', 'no spike')
                f.write(f'{r["b"]:>3} {r["n"]:>3} {r["d"]:>3}  ({err})\n')
                continue
            f.write(
                f'{r["b"]:>3} {r["n"]:>3} {r["d"]:>3} '
                f'{r["pred_spike_baseb"]:>10.2f} '
                f'{r["observed_baseb"]:>10.2f} '
                f'{r["gap_baseb"]:>+9.2f} '
                f'{r["gap_pct"]:>+7.3f}% '
                f'{r["observed_idx"]:>5} '
                f'{r["validated"]:>6}\n'
            )
    print(f'wrote {summary_path}', flush=True)


if __name__ == '__main__':
    main()
