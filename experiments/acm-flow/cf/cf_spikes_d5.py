"""
cf_spikes_d5.py — d=5 boundary spike push at b=10
=================================================

Phase 2 of BRIEF2-CLOSED-FORM.md / SPIKE-CLOSED-FORM-PANEL.md (a):
push the closed-form prediction one decade in d. The d=4 panel covered
varying d across bases but tested d-scaling only weakly (different
bases at different d). This script does direct d-scaling at b=10:
n ∈ {2, 3, 4, 5, 6, 10} at d=5, vs. the same n-set at d=4 in the
original cf_spikes.py.

Predicted at b=10:
    F(5, 10) = 5 · 8 · 10⁴ + (10⁵ - 1)/9 = 400 000 + 11 111 = 411 111
    spike(n, d=5, b=10) ≈ (n-1)/n² · 411 111  base-10 digits

  | n  | predicted (decimal digits) |
  |---:|---:|
  | 2  | 102 778 |
  | 3  |  91 358 |
  | 4  |  77 084 |
  | 5  |  65 778 |
  | 6  |  57 099 |
  | 10 |  37 000 |

PREC_BITS_LO scaled to ~3.5× predicted spike in bits (≈ 1.2 M bits
for n=2 down to ≈ 430 k bits for n=10), PREC_BITS_HI = 2× LO.

Memory: at d=5 the convergent denominators q_i past the spike grow
to ~10^102 000 decimal digits each — keeping a full q_list of 8 000
entries would use multi-GB. Instead we run an *inline* CF loop that
checks the cumulative-digit identity at each step against a magnitude
threshold, keeping only a rolling (q_prev, q_curr) pair. Cross-precision
validation still uses the a_list (small Python ints).

Per-case runtime: ~3 (n=10) to ~10 minutes (n=2). Full panel: ~30–60 min.

Outputs (this directory):
  cf_d5_summary.txt
  cf_d5.csv

Usage:
    sage -python cf_spikes_d5.py
"""

import csv
import importlib.util
import math
import os
import sys
import time

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    'cfx', os.path.join(THIS_DIR, 'cf_spikes_extended.py'),
)
cfx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cfx)

from mpmath import mp, mpf, floor as mfloor

PANEL = [(10, n, 5) for n in (2, 3, 4, 5, 6, 10)]


# ---------------------------------------------------------------------------
# Inline CF loop with on-the-fly d-boundary spike search
# ---------------------------------------------------------------------------

def cf_inline_d_spike(digits, b, max_pq, prec_bits, n, d_target,
                      spike_log_b_threshold):
    """CF expansion that identifies the d_target boundary spike inline,
    avoiding q_list storage. Tracks rolling (q_prev, q_curr) only.

    Returns (a_list, spike_record_or_None).
    spike_record is dict with keys i, a, log_b_a, log_b_q_im1, identity
    for the largest a_i that passes the identity check; None if no
    candidate.

    Note: if the cf at LO precision diverges from x mid-loop, a_list
    will reflect that divergence. The caller cross-validates a_list
    between LO and HI precisions to determine the trustworthy prefix
    length, and only spikes within that prefix are taken."""
    mp.prec = prec_bits
    L = len(digits)
    # Read digits as integer in base b
    N = 0
    for d in digits:
        N = N * b + d
    x = mpf(N) / (mpf(b) ** L)

    log_b = math.log(b)
    target_C = float(cfx.cumulative_baseb_digits(n, d_target, b))
    slack = max(10.0, 2.0 * (b - 1) * d_target)

    a_list = []
    q_prev, q_curr = 0, 1
    best = None  # dict or None

    for step in range(max_pq):
        frac = x - mfloor(x)
        if frac == 0:
            break
        x = 1 / frac
        ai = int(mfloor(x))
        a_list.append(ai)
        i = step + 1
        q_im1 = q_curr  # this is q_{i-1} relative to a_i
        q_prev, q_curr = q_curr, ai * q_curr + q_prev

        # Inline spike check, only for candidate a_i big enough
        if ai > 1:
            log_a = math.log(ai) / log_b
            if log_a >= spike_log_b_threshold and q_im1 > 0:
                log_q = math.log(q_im1) / log_b
                identity = 2 * log_q + log_a
                if abs(identity - target_C) <= slack:
                    if best is None or ai > best['a']:
                        best = {
                            'i': i, 'a': ai,
                            'log_b_a': log_a, 'log_b_q_im1': log_q,
                            'identity': identity,
                        }
    return a_list, best


# ---------------------------------------------------------------------------
# One panel cell
# ---------------------------------------------------------------------------

def run_one_d5(b, n, d):
    pred_spike_baseb = cfx.predicted_spike_baseb_digits(n, d, b)
    pred_spike_dec = pred_spike_baseb * math.log10(b)

    # K_PRIMES: 1.5x n-prime count up to b^d, plus buffer
    n_primes_in_d_block = b**d * (n - 1) / (n * n)
    K = max(500, int(1.5 * n_primes_in_d_block) + 200)

    bits_per_baseb_digit = math.log(b) / math.log(2)
    pred_spike_bits = pred_spike_baseb * bits_per_baseb_digit
    prec_lo = max(80000, int(3.5 * pred_spike_bits))
    prec_hi = 2 * prec_lo

    cum_C_d_dec = float(cfx.cumulative_baseb_digits(n, d, b)) * math.log10(b)
    max_pq = max(500, int(2.0 * cum_C_d_dec))
    max_pq = min(max_pq, 12000)  # bumped from cf_spikes_extended's 8000 cap

    # Spike threshold: 0.1× predicted in base-b digits, so we don't
    # spend CPU on log() of every PQ
    spike_thr = 0.1 * pred_spike_baseb

    print(
        f'\n--- (b={b}, n={n}, d={d}) ---\n'
        f'  predicted spike ≈ {pred_spike_baseb:.1f} base-{b} digits '
        f'= {pred_spike_dec:.1f} decimal digits\n'
        f'  K_PRIMES={K}, prec_lo={prec_lo}, prec_hi={prec_hi}, '
        f'max_pq={max_pq}, spike_thr={spike_thr:.1f}',
        flush=True,
    )

    digits = cfx.n_primes_baseb_digits(n, K, b)
    print(f'  total base-{b} digits available: {len(digits)}', flush=True)

    t0 = time.time()
    a_lo, spike_lo = cf_inline_d_spike(
        digits, b, max_pq, prec_lo, n, d, spike_thr,
    )
    t_lo = time.time() - t0
    print(f'  LO CF: {len(a_lo)} PQs, {t_lo:.1f}s', flush=True)

    t0 = time.time()
    a_hi, spike_hi = cf_inline_d_spike(
        digits, b, max_pq, prec_hi, n, d, spike_thr,
    )
    t_hi = time.time() - t0
    print(f'  HI CF: {len(a_hi)} PQs, {t_hi:.1f}s', flush=True)

    n_validated = cfx.stable_prefix_len(a_lo, a_hi)
    print(f'  validated prefix: {n_validated} PQs', flush=True)

    # Take the spike from whichever precision identified it within the
    # validated prefix; prefer the smaller-precision one if both agree
    spike = None
    for s in (spike_lo, spike_hi):
        if s is not None and s['i'] <= n_validated:
            if spike is None or s['a'] > spike['a']:
                spike = s

    if spike is None:
        print('  [no d=%d boundary spike found in validated prefix]' % d,
              flush=True)
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

    obs_baseb = spike['log_b_a']
    obs_dec = obs_baseb * math.log10(b)
    gap_baseb = obs_baseb - pred_spike_baseb
    gap_pct = 100.0 * gap_baseb / pred_spike_baseb if pred_spike_baseb else 0.0

    print(
        f'  spike at i={spike["i"]}: log_{b}={obs_baseb:.2f} '
        f'(log_10={obs_dec:.2f})\n'
        f'  predicted log_{b}: {pred_spike_baseb:.2f}; '
        f'gap = {gap_baseb:+.2f} base-{b} digits = {gap_pct:+.4f}%',
        flush=True,
    )

    return {
        'b': b, 'n': n, 'd': d, 'K': K,
        'prec_lo': prec_lo, 'validated': n_validated,
        'pred_spike_baseb': pred_spike_baseb,
        'pred_spike_decimal': pred_spike_dec,
        'observed_idx': spike['i'],
        'observed_baseb': obs_baseb,
        'observed_decimal': obs_dec,
        'gap_baseb': gap_baseb,
        'gap_pct': gap_pct,
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main():
    print('cf_spikes_d5 — d=5 boundary push at b=10')
    print(
        'Closed form: spike(n) ≈ (n-1)/n² · F(5, 10) '
        '= (n-1)/n² · 411 111  base-10 digits'
    )
    print()
    cfx.smoke_test()

    rows = []
    for b, n, d in PANEL:
        try:
            rows.append(run_one_d5(b, n, d))
        except Exception as e:
            import traceback
            print(f'  FAIL ({b},{n},{d}): {e}', flush=True)
            traceback.print_exc()
            rows.append({'b': b, 'n': n, 'd': d, 'error': str(e)})

    out_dir = THIS_DIR
    csv_path = os.path.join(out_dir, 'cf_d5.csv')
    summary_path = os.path.join(out_dir, 'cf_d5_summary.txt')

    fieldnames = [
        'b', 'n', 'd', 'K', 'prec_lo', 'validated',
        'pred_spike_baseb', 'pred_spike_decimal',
        'observed_idx', 'observed_baseb', 'observed_decimal',
        'gap_baseb', 'gap_pct',
    ]
    with open(csv_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fieldnames})

    with open(summary_path, 'w') as f:
        f.write('cf_spikes_d5 — d=5 boundary push at b=10\n')
        f.write('=' * 78 + '\n\n')
        f.write(
            'spike(n, d=5, b=10) ≈ (n-1)/n² · F(5, 10) '
            '= (n-1)/n² · 411 111  base-10 digits\n\n'
        )
        f.write(
            f'{"n":>3} {"pred_b-d":>11} {"obs_b-d":>11} '
            f'{"gap":>9} {"gap%":>9} {"i":>5} {"valid":>6}\n'
        )
        f.write('-' * 78 + '\n')
        for r in rows:
            if r.get('error') or r.get('observed_idx') is None:
                err = r.get('error', 'no spike')
                f.write(f'{r["n"]:>3}  ({err})\n')
                continue
            f.write(
                f'{r["n"]:>3} '
                f'{r["pred_spike_baseb"]:>11.2f} '
                f'{r["observed_baseb"]:>11.2f} '
                f'{r["gap_baseb"]:>+9.2f} '
                f'{r["gap_pct"]:>+8.4f}% '
                f'{r["observed_idx"]:>5} '
                f'{r["validated"]:>6}\n'
            )
    print(f'\nwrote {csv_path}', flush=True)
    print(f'wrote {summary_path}', flush=True)


if __name__ == '__main__':
    main()
