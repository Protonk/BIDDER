"""
spike_drift_extended.py — extend the offset(n) panel to n ∈ {7, 11, 13}
========================================================================

Phase 3.1 (B), follow-up. The previous panel established:

    δ_k(n) = L_{k-1}(n) - C_{k-1}(n) ~ (n - 1) · k + offset(n) - O(b^{-k})

with per-n offsets:

    n=2:  log_10(5)         (= log_b(b/n))
    n=3:  log_10(10/9)      (= log_b(b/(b-1)))
    n=5:  0
    n=6:  -1 + log_10(10/9)

Each is a clean closed form individually, but the n → offset(n) rule
isn't unified. Adding three more primes (n = 7, 11, 13) tests whether
a unified rule pops out, or whether the offset really is per-n.

This script self-contained: runs CF expansion for the new primes,
identifies d = 2, 3, 4 mega-spikes by digit tier, computes δ_k via
log_b(q_{i-1}) tracking, and combines with the previously-recorded
data from offspike_inflation.csv to produce one unified offset table.

Usage:
    sage -python spike_drift_extended.py
"""

import csv
import math
import os
import sys
from fractions import Fraction
from math import log10

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'core'))

from acm_core import acm_n_primes  # noqa: E402

from mpmath import floor as mfloor  # noqa: E402
from mpmath import mp, mpf  # noqa: E402
from mpmath import log10 as mp_log10  # noqa: E402


HERE = os.path.dirname(os.path.abspath(__file__))

BASE = 10
NEW_NS = [7, 11, 13, 17, 19, 23, 29, 31]
KS = [2, 3, 4]
SPIKE_THRESHOLD = 10**4
PREC_BITS = 80000
MAX_PQ = 600
K_PRIMES = 40000


# ---- substrate quantities ----

def atom_count_in_block(n, d, base=BASE):
    lo = base ** (d - 1)
    hi = base ** d - 1
    m_lo = (lo + n - 1) // n
    m_hi = hi // n
    if m_hi < m_lo:
        return 0
    total = m_hi - m_lo + 1
    div_n = m_hi // n - (m_lo - 1) // n
    return total - div_n


def C_km1_actual(n, k, base=BASE):
    return sum(atom_count_in_block(n, d, base) * d for d in range(1, k))


def T_k_actual(n, k, base=BASE):
    return C_km1_actual(n, k + 1, base)  # cumulative through d=k block


# ---- CF with log_b(q) tracking ----

def cf_with_log_q(frac_digits, max_pq, prec_bits):
    mp.prec = prec_bits
    x = mpf('0.' + frac_digits)
    q_prev = 0
    q_curr = 1
    out = []
    for _ in range(max_pq):
        frac = x - mfloor(x)
        if frac == 0:
            break
        x = 1 / frac
        a = int(mfloor(x))
        q_im1_log10 = math.log10(q_curr) if q_curr > 0 else 0.0
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
        return float(mp_log10(mpf(v)))


def select_d234_spikes(cf):
    """Select the d=2, 3, 4 mega-spikes from the CF expansion.

    Strategy: peel from above. d=4 is the largest spike overall.
    d=3 is the largest spike with smaller index than d=4. d=2 is
    the largest spike with smaller index than d=3.

    For large n, d=2 (and sometimes d=3) may not exist as a mega-
    spike (formula predicts negative size). In that case the
    returned dict is missing those keys.

    Returns dict k → (i_zero_indexed, a, q_im1_log10)."""
    spikes = [(i, a, q_log) for i, (a, q_log) in enumerate(cf)
              if a > SPIKE_THRESHOLD]
    if not spikes:
        return {}
    out = {}
    d4 = max(spikes, key=lambda s: s[1])
    out[4] = d4
    earlier = [s for s in spikes if s[0] < d4[0]]
    if not earlier:
        return out
    d3 = max(earlier, key=lambda s: s[1])
    out[3] = d3
    earliest = [s for s in earlier if s[0] < d3[0]]
    if not earliest:
        return out
    d2 = max(earliest, key=lambda s: s[1])
    out[2] = d2
    return out


# ---- assemble panel ----

def compute_new_panel():
    """For each n in NEW_NS, run CF, identify d=2,3,4 spikes, compute δ_k."""
    results = []
    for n in NEW_NS:
        print(f'\n--- n = {n} ---', flush=True)
        primes = acm_n_primes(n, K_PRIMES)
        digits = ''.join(str(p) for p in primes)
        print(f'  digits available: {len(digits)}', flush=True)

        cf = cf_with_log_q(digits, MAX_PQ, PREC_BITS)
        print(f'  CF PQs computed: {len(cf)}', flush=True)

        spikes = select_d234_spikes(cf)
        if 4 not in spikes:
            print(f'  WARNING: no d=4 mega-spike found in {len(cf)} PQs for n={n}',
                  flush=True)
            continue

        for k in KS:
            if k not in spikes:
                print(f'  k={k}: not present (formula predicts no mega-spike)',
                      flush=True)
                continue
            i, a, q_log = spikes[k]
            log_a = safe_log10_int(a)
            C = C_km1_actual(n, k)
            delta = q_log - C
            print(f'  k={k}: idx={i+1}  pq_digits={len(str(a))}  '
                  f'log10(a)={log_a:.4f}  log10(q_prev)={q_log:.4f}  '
                  f'C_{{k-1}}={C}  δ_k={delta:+.4f}', flush=True)
            results.append({
                'n': n, 'k': k, 'spike_index': i + 1,
                'pq_digits': len(str(a)),
                'log10_a': log_a, 'log10_q_prev': q_log,
                'C_km1': C, 'delta': delta,
            })
    return results


def load_existing_panel():
    """Read offspike_inflation.csv to get δ_k for the previous panel."""
    path = os.path.join(HERE, 'offspike_inflation.csv')
    rows = []
    with open(path, newline='') as f:
        for row in csv.DictReader(f):
            rows.append({
                'n': int(row['n']),
                'k': int(row['k']),
                'spike_index': int(row['spike_index']),
                'log10_q_prev': float(row['L_{k-1}']),
                'C_km1': int(row['C_{k-1}_actual']),
                'delta': float(row['delta_actual']),
            })
    return rows


# ---- offset(n) candidates ----

def candidate_offsets(n, base=BASE):
    """Generate candidate closed-form expressions for offset(n)."""
    cands = []
    cands.append(('0', 0.0))
    cands.append(('log_b(b/n)', log10(base / n)))
    cands.append(('log_b(b/n²)', log10(base / (n * n))))
    cands.append(('log_b(b/n³)', log10(base / (n ** 3))))
    cands.append(('log_b(b/(b-1))', log10(base / (base - 1))))
    cands.append(('log_b(1/(b-1))', log10(1 / (base - 1))))
    cands.append(('log_b(b²/n²)', log10((base ** 2) / (n * n))))
    cands.append(('log_b(1/n)', log10(1 / n)))
    cands.append(('log_b(b/(n-1))', log10(base / (n - 1)) if n > 1 else 0.0))
    cands.append(('log_b((b-1)/n)', log10((base - 1) / n)))
    cands.append(('log_b((b-1)/n²)', log10((base - 1) / (n * n))))
    cands.append(('log_b(n/(b-1))', log10(n / (base - 1))))
    cands.append(('log_b(n²/(b·(n-1)))',
                  log10(n * n / (base * (n - 1))) if n > 1 else 0.0))
    return cands


def best_match(observed, n, tol=0.005):
    cands = candidate_offsets(n)
    matches = [(name, val) for name, val in cands if abs(observed - val) < tol]
    if matches:
        return matches[0][0]
    return None


# ---- main ----

def main():
    print('spike_drift_extended.py — extend offset(n) panel to {7, 11, 13}\n',
          flush=True)
    print(f'NEW NS:  {NEW_NS}', flush=True)
    print(f'KS:      {KS}', flush=True)
    print(f'PREC_BITS={PREC_BITS}, MAX_PQ={MAX_PQ}, K_PRIMES={K_PRIMES}',
          flush=True)

    new_results = compute_new_panel()
    existing_results = load_existing_panel()

    all_results = existing_results + new_results
    by_nk = {(r['n'], r['k']): r for r in all_results}

    panel_ns = sorted({r['n'] for r in all_results})

    summary = [
        'spike_drift_extended.py — full δ_k(n) panel',
        '',
        '  n  | k=2 δ      | k=3 δ      | k=4 δ      | (n-1)·4 + offset_k=4',
        '-----+------------+------------+------------+-----------------------',
    ]

    csv_rows = [(
        'n', 'k', 'spike_index', 'log10_q_prev', 'C_km1', 'delta',
        'asymptotic_slope', 'offset_k4', 'offset_match',
    )]

    print(f'\n=== Full panel summary ===', flush=True)
    print(f'  n  | k=2 δ      | k=3 δ      | k=4 δ      | offset(n) at k=4 | match',
          flush=True)
    print(f'-----+------------+------------+------------+------------------+-------',
          flush=True)

    for n in panel_ns:
        d2 = by_nk.get((n, 2), {}).get('delta', None)
        d3 = by_nk.get((n, 3), {}).get('delta', None)
        d4 = by_nk.get((n, 4), {}).get('delta', None)
        slope = n - 1
        if d4 is not None:
            offset_k4 = d4 - slope * 4
            match = best_match(offset_k4, n)
            match_str = match if match else '(no clean match)'
        else:
            offset_k4 = None
            match_str = '(missing)'
        d2_str = f'{d2:>+10.4f}' if d2 is not None else '   (missing)'
        d3_str = f'{d3:>+10.4f}' if d3 is not None else '   (missing)'
        d4_str = f'{d4:>+10.4f}' if d4 is not None else '   (missing)'
        offset_str = f'{offset_k4:>+8.4f}' if offset_k4 is not None else ' missing '
        line = (f'  {n:>2} | {d2_str} | {d3_str} | {d4_str} | '
                f'{offset_str}  |  {match_str}')
        summary.append(line)
        print(line, flush=True)

        for k in KS:
            r = by_nk.get((n, k))
            if r is None:
                continue
            delta = r['delta']
            offset_k = delta - slope * k
            csv_rows.append((
                n, k, r['spike_index'],
                f'{r["log10_q_prev"]:.6f}',
                r['C_km1'],
                f'{delta:+.6f}',
                slope,
                f'{offset_k:+.6f}',
                best_match(offset_k, n) or '',
            ))

    summary.append('')
    summary.append('=== Step structure (asymptotic slope check) ===')
    summary.append('  n  | step 2→3   | step 3→4   | (n - 1) | match')
    summary.append('-----+------------+------------+---------+--------')
    print(f'\n=== Step structure ===', flush=True)
    print(f'  n  | step 2→3   | step 3→4   | (n - 1) | match', flush=True)
    print(f'-----+------------+------------+---------+--------', flush=True)
    for n in panel_ns:
        d2 = by_nk.get((n, 2), {}).get('delta', None)
        d3 = by_nk.get((n, 3), {}).get('delta', None)
        d4 = by_nk.get((n, 4), {}).get('delta', None)
        if None in (d2, d3, d4):
            continue
        s32 = d3 - d2
        s43 = d4 - d3
        match = (
            'YES' if abs(s43 - (n - 1)) < 0.05
            else f'no (off by {s43 - (n - 1):+.3f})'
        )
        line = f'  {n:>2} | {s32:>+10.4f} | {s43:>+10.4f} | {n-1:>7} | {match}'
        summary.append(line)
        print(line, flush=True)

    summary.append('')
    summary.append('=== Per-n offset(n) at k=4, with closed-form match ===')
    summary.append('  n  | observed offset | candidate match')
    summary.append('-----+-----------------+--------------------')
    for n in panel_ns:
        r = by_nk.get((n, 4))
        if r is None:
            continue
        offset_k4 = r['delta'] - (n - 1) * 4
        match = best_match(offset_k4, n) or '(no match)'
        summary.append(f'  {n:>2} | {offset_k4:>+15.6f} | {match}')

    csv_path = os.path.join(HERE, 'spike_drift_extended.csv')
    with open(csv_path, 'w', newline='') as f:
        csv.writer(f).writerows(csv_rows)

    summary_path = os.path.join(HERE, 'spike_drift_extended_summary.txt')
    with open(summary_path, 'w') as f:
        f.write('\n'.join(summary) + '\n')

    print(f'\nwrote {csv_path}', flush=True)
    print(f'wrote {summary_path}', flush=True)


if __name__ == '__main__':
    main()
