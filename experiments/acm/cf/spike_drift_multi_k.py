"""
spike_drift_multi_k.py — test T_k − 2 L_{k−1} at k ∈ {2, 3, 4}
================================================================

spike_drift_table.py verified the formula at k = 4 only, using
rounded log10(q_before) values from the original CF panel. This
script computes log10(q_{i−1}) directly along the CF expansion
for each n in the panel and tests the formula at k = 2, 3, 4.
Consumed by MULTI-K-RESULT.md.

Method:
  1. Build C_b(n) digit string (smoke-tested against classical
     Champernowne in cf_spikes.py; we trust that infrastructure).
  2. Run the CF expansion at PREC_BITS, tracking convergent
     denominators q_j as exact Python ints (q is small enough at
     i ≤ ~250 even when a_i has 8000 digits).
  3. For each spike (a_i > SPIKE_THRESHOLD), record (i, log10(a_i),
     log10(q_{i−1})).
  4. Identify each spike's k-tier (k = 2, 3, 4) by digit count tier
     from the d=4 mega-spike scaling.
  5. Compute both smooth and actual T_k(n,b). Compare observed
     log10(a_i) against predicted T_k − 2 · log10(q_{i−1}).
     Tabulate residuals.

A clean fit at every k does not close the structure. It locates the
remaining scalar in L_{k−1} itself: the off-spike denominator process
before the boundary. This script records where the residual lives,
not a finished derivation of that residual.

Outputs:
  spike_drift_multi_k.csv       per-(n, k) row
  spike_drift_multi_k_summary.txt   human-readable table

Usage:
    sage -python spike_drift_multi_k.py
"""

import csv
import math
import os
import sys
from fractions import Fraction

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'core'))

from acm_core import acm_n_primes  # noqa: E402

from mpmath import floor as mfloor  # noqa: E402
from mpmath import mp, mpf  # noqa: E402


HERE = os.path.dirname(os.path.abspath(__file__))

BASE = 10
NS = [2, 3, 4, 5, 6, 10]
KS = [2, 3, 4]
SPIKE_THRESHOLD = 10**4
PREC_BITS = 80000        # 24k decimal digits — covers d=4 mega-spikes
MAX_PQ = 250             # all panel d=4 spikes sit at index ≤ 215
K_PRIMES = 20000         # provides ~80k digits, plenty for d ≤ 4


# ---- closed-form substrate quantities ----

def smooth_factor(n):
    return Fraction(n - 1, n * n)


def D_k_smooth(n, k, base=BASE):
    """Smooth-block formula: exact iff n² | b^{k-1}."""
    return Fraction(k * (base - 1) * base ** (k - 1)) * smooth_factor(n)


def C_km1_smooth(n, k, base=BASE):
    f = smooth_factor(n)
    return sum(
        Fraction(base - 1) * f * d * base ** (d - 1)
        for d in range(1, k)
    )


def T_k_smooth(n, k, base=BASE):
    return C_km1_smooth(n, k, base) + D_k_smooth(n, k, base)


def atom_count_in_block(n, d, base=BASE):
    """Exact number of n-primes in [base^{d-1}, base^d).

    n-primes are n·m with n ∤ m. For fixed d, m ranges over
    [⌈base^{d-1}/n⌉, ⌊(base^d - 1)/n⌋]. Subtract m divisible by n."""
    lo = base ** (d - 1)
    hi = base ** d - 1
    m_lo = (lo + n - 1) // n  # ⌈lo/n⌉
    m_hi = hi // n
    if m_hi < m_lo:
        return 0
    total = m_hi - m_lo + 1
    # Count m ∈ [m_lo, m_hi] divisible by n.
    div_n = m_hi // n - (m_lo - 1) // n
    return total - div_n


def D_k_actual(n, k, base=BASE):
    """Exact digit contribution of the k-digit block: count × k."""
    return atom_count_in_block(n, k, base) * k


def T_k_actual(n, k, base=BASE):
    """Exact cumulative digit count through the k-digit block."""
    return sum(D_k_actual(n, d, base) for d in range(1, k + 1))


def C_km1_actual(n, k, base=BASE):
    return sum(D_k_actual(n, d, base) for d in range(1, k))


# ---- CF expansion with log10(q) tracking ----

def cf_with_log_q(frac_digits, max_pq, prec_bits):
    """Expand 0.<frac_digits> as a CF up to max_pq partial quotients,
    tracking exact q_j as Python ints.

    Returns list of (a_i, q_im1_log10) for i = 1 .. n_pq.
    q_im1 is the denominator of the convergent BEFORE this PQ —
    i.e. q_{i−1} in the standard CF notation where the convergent
    after PQ_i is p_i / q_i.
    """
    mp.prec = prec_bits
    x = mpf('0.' + frac_digits)

    q_prev = 0   # q_{-1}
    q_curr = 1   # q_0
    out = []
    for _ in range(max_pq):
        frac = x - mfloor(x)
        if frac == 0:
            break
        x = 1 / frac
        a = int(mfloor(x))
        # log10(q_{i−1}) is the denominator BEFORE this step's update.
        q_im1_log10 = math.log10(q_curr) if q_curr > 0 else 0.0
        # Now update: q_i = a · q_{i−1} + q_{i−2}.
        q_new = a * q_curr + q_prev
        q_prev = q_curr
        q_curr = q_new
        out.append((a, q_im1_log10))
    return out


def safe_log10_int(v):
    if v <= 0:
        return 0.0
    try:
        return math.log10(v)
    except (OverflowError, ValueError):
        from mpmath import log10 as mp_log10
        return float(mp_log10(mpf(v)))


# ---- spike identification by digit-count tier ----

def classify_by_tier(n, pq_digits):
    """From the empirical b=10 panel: d=2 spikes have 5-50 digits,
    d=3 have ~150-700, d=4 mega-spikes have ~2500-8500. Returns k or
    None for non-tier spikes (like the n=2 i=71 13-digit off-tier event)."""
    if 5 <= pq_digits <= 50:
        return 2
    if 150 <= pq_digits <= 800:
        return 3
    if 2500 <= pq_digits <= 9000:
        return 4
    return None


def load_panel_spikes():
    """Read cf_spikes.csv. Returns dict n -> {k: (index, pq_digits, pq_log10)}.

    Takes the first spike per (n, k) tier in index order — the canonical
    d=k mega-spike. Ignores off-tier events and d=k-tail spikes."""
    cf_csv = os.path.join(HERE, 'cf_spikes.csv')
    spikes = {n: {} for n in NS}
    with open(cf_csv, newline='') as f:
        rows = sorted(csv.DictReader(f), key=lambda r: (int(r['n']), int(r['index'])))
        for row in rows:
            n = int(row['n'])
            if n not in NS:
                continue
            idx = int(row['index'])
            pq_digits = int(row['pq_digits'])
            pq_log10 = float(row['pq_log10'])
            k = classify_by_tier(n, pq_digits)
            if k is None or k in spikes[n]:
                continue
            spikes[n][k] = (idx, pq_digits, pq_log10)
    return spikes


# ---- main ----

def main():
    print('spike_drift_multi_k.py — k = 2, 3, 4 verification\n', flush=True)
    print(f'panel n: {NS}', flush=True)
    print(f'k tiers: {KS}', flush=True)
    print(f'PREC_BITS={PREC_BITS}, MAX_PQ={MAX_PQ}, K_PRIMES={K_PRIMES}\n',
          flush=True)

    panel_spikes = load_panel_spikes()
    print('panel spikes from cf_spikes.csv (k → (index, pq_digits, log10)):', flush=True)
    for n in NS:
        print(f'  n={n}: {panel_spikes[n]}', flush=True)
    print('', flush=True)

    csv_rows = [(
        'n', 'k', 'spike_index', 'pq_digits',
        'observed_log10_a', 'csv_log10_a', 'log10_a_match',
        'log10_q_prev',
        'T_k_smooth', 'T_k_actual', 'T_diff',
        'predicted_smooth', 'residual_smooth',
        'predicted_actual', 'residual_actual',
    )]

    summary_lines = [
        'Multi-k spike-drift table — actual vs smooth T_k',
        '',
        ('  k | n  | idx | obs log10(a) | log10(q_prev) | '
         'T_k smooth |  T_k actual |  res (smooth) |  res (actual)'),
        '----|----|-----|--------------|---------------|'
        '-----------|-------------|---------------|----------------',
    ]

    for n in NS:
        print(f'--- n = {n} ---', flush=True)
        primes = acm_n_primes(n, K_PRIMES)
        digits = ''.join(str(p) for p in primes)
        print(f'  digits: {len(digits)}', flush=True)

        cf = cf_with_log_q(digits, MAX_PQ, PREC_BITS)
        print(f'  computed {len(cf)} PQs', flush=True)

        for k in KS:
            if k not in panel_spikes[n]:
                print(f'  WARNING: no d={k} spike found in cf_spikes.csv for n={n}',
                      flush=True)
                continue
            idx, pq_digits, csv_log_a = panel_spikes[n][k]

            if idx > len(cf):
                print(f'  WARNING: spike index {idx} > computed PQs {len(cf)} '
                      f'for n={n}, k={k}', flush=True)
                continue

            a, q_log = cf[idx - 1]
            log_a = safe_log10_int(a)

            tk_s = float(T_k_smooth(n, k))
            tk_a = float(T_k_actual(n, k))
            t_diff = tk_a - tk_s
            predicted_s = tk_s - 2.0 * q_log
            predicted_a = tk_a - 2.0 * q_log
            residual_s = log_a - predicted_s
            residual_a = log_a - predicted_a

            log_a_match = abs(log_a - csv_log_a) < 0.01

            print(f'  k={k}: idx={idx}  log10(a)={log_a:.4f} '
                  f'(csv {csv_log_a:.4f})  log10(q_prev)={q_log:.4f}  '
                  f'T_smooth={tk_s:.4f}  T_actual={tk_a}  '
                  f'res_actual={residual_a:+.4f}',
                  flush=True)

            csv_rows.append((
                n, k, idx, pq_digits,
                f'{log_a:.6f}', f'{csv_log_a:.6f}', log_a_match,
                f'{q_log:.6f}',
                f'{tk_s:.6f}', f'{tk_a}', f'{t_diff:+.6f}',
                f'{predicted_s:.6f}', f'{residual_s:+.6f}',
                f'{predicted_a:.6f}', f'{residual_a:+.6f}',
            ))
            summary_lines.append(
                f'  {k} | {n:>2} | {idx:>3} | {log_a:>12.4f} | '
                f'{q_log:>13.4f} | {tk_s:>9.4f} | {int(tk_a):>11d} | '
                f'{residual_s:>+13.4f} | {residual_a:>+14.4f}'
            )

    csv_path = os.path.join(HERE, 'spike_drift_multi_k.csv')
    with open(csv_path, 'w', newline='') as f:
        csv.writer(f).writerows(csv_rows)

    summary_path = os.path.join(HERE, 'spike_drift_multi_k_summary.txt')
    summary_lines.append('')
    summary_lines.append(f'PREC_BITS={PREC_BITS}, MAX_PQ={MAX_PQ}, '
                         f'K_PRIMES={K_PRIMES}')
    summary_lines.append('')
    summary_lines.append(
        'A clean residual at every (n, k) does not mean closure. '
        'It locates the\n'
        'remaining scalar in L_{k−1}, i.e. in the off-spike denominator\n'
        'process before the boundary.'
    )
    with open(summary_path, 'w') as f:
        f.write('\n'.join(summary_lines) + '\n')

    print(f'\nwrote {csv_path}', flush=True)
    print(f'wrote {summary_path}', flush=True)


if __name__ == '__main__':
    main()
