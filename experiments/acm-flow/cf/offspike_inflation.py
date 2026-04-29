"""
offspike_inflation.py — does L_{k-1} - C_{k-1} have a closed form?
=====================================================================

Phase 3.1: denominator inflation at the boundary.

`spike_drift_multi_k.py` showed that with empirical L_{k-1} = log_b(q
at the d=k mega-spike index − 1), the spike formula closes to within
~10^{-4} at k=4 across the panel:

    log_b(a) = T_k(actual) - 2 L_{k-1} + log_b(b/(b-1)) - O(b^{-k}).

The remaining unknown on the RHS is L_{k-1} itself — equivalently,
the deviation

    δ_k(n) := L_{k-1}(n) - C_{k-1}(n)

between the actual log-denominator at the d=k boundary and the
substrate-naive prediction (log q ≈ cumulative digit count).

The working question from MEGA-SPIKE.md: whether δ_k(n) is itself a
substrate quantity, given by a closed form or finite recurrence in
n and k. If true, the boundary-spike formula becomes fully
closed-form.

This script reads `spike_drift_multi_k.csv`, computes δ_k(n) per
(n, k), and looks for closed-form structure:

  - linear growth in k per fixed n;
  - polynomial / rational dependence on n;
  - identification with classical CF / Khinchin-typical contributions
    weighted by the spike-spacing.

Outputs:
  offspike_inflation.csv     per-(n, k) table of L, C, δ, and step
  offspike_inflation_summary.txt    human-readable tables and notes

Usage:
    sage -python offspike_inflation.py
"""

import csv
import os
from collections import defaultdict
from fractions import Fraction
from math import log10


HERE = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV = os.path.join(HERE, 'spike_drift_multi_k.csv')

BASE = 10
NS = [2, 3, 4, 5, 6, 10]
KS = [2, 3, 4]


def smooth_factor(n):
    return Fraction(n - 1, n * n)


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


def C_km1_smooth(n, k, base=BASE):
    f = smooth_factor(n)
    return float(sum(
        Fraction(base - 1) * f * d * base ** (d - 1)
        for d in range(1, k)
    ))


def load_input():
    """Load (n, k, spike_index, log10_q_prev) from spike_drift_multi_k.csv."""
    records = []
    with open(INPUT_CSV, newline='') as f:
        for row in csv.DictReader(f):
            records.append({
                'n': int(row['n']),
                'k': int(row['k']),
                'spike_index': int(row['spike_index']),
                'log10_q_prev': float(row['log10_q_prev']),
                'observed_log10_a': float(row['observed_log10_a']),
            })
    return records


def main():
    records = load_input()
    by_n = defaultdict(dict)
    for r in records:
        by_n[r['n']][r['k']] = r

    # Per (n, k), compute δ_k = L_{k-1} - C_{k-1}.
    rows = [(
        'n', 'k', 'spike_index', 'L_{k-1}', 'C_{k-1}_actual',
        'C_{k-1}_smooth', 'delta_actual', 'delta_smooth',
        'step_in_k', 'spikes_gap',
    )]

    summary_lines = [
        'Phase 3.1 (B) — off-spike denominator inflation δ_k(n) = L_{k-1} - C_{k-1}',
        '',
        '  n  | k | idx |   L_{k-1}    |   C_{k-1}    |    δ_k    | step (δ_k - δ_{k-1})',
        '-----+---+-----+--------------+--------------+-----------+----------------------',
    ]

    delta_table = defaultdict(dict)
    spike_index_table = defaultdict(dict)

    for n in NS:
        prev_delta = None
        for k in KS:
            if k not in by_n[n]:
                continue
            r = by_n[n][k]
            L = r['log10_q_prev']
            C_actual = C_km1_actual(n, k)
            C_smooth = C_km1_smooth(n, k)
            delta_actual = L - C_actual
            delta_smooth = L - C_smooth

            delta_table[n][k] = delta_actual
            spike_index_table[n][k] = r['spike_index']

            if prev_delta is None:
                step_str = '   —   '
                step_val = None
            else:
                step_val = delta_actual - prev_delta
                step_str = f'{step_val:>+8.4f}'

            spikes_gap = ''
            if k > KS[0]:
                prev_idx = spike_index_table[n].get(k - 1)
                if prev_idx is not None:
                    spikes_gap = str(r['spike_index'] - prev_idx)

            rows.append((
                n, k, r['spike_index'],
                f'{L:.6f}', C_actual, f'{C_smooth:.6f}',
                f'{delta_actual:+.6f}', f'{delta_smooth:+.6f}',
                f'{step_val:+.6f}' if step_val is not None else '',
                spikes_gap,
            ))
            summary_lines.append(
                f'  {n:>2} | {k} | {r["spike_index"]:>3} | '
                f'{L:>12.4f} | {C_actual:>12d} | {delta_actual:>+9.4f} | {step_str}'
            )
            prev_delta = delta_actual
        summary_lines.append('')

    # Per-n analysis: linear fit, integer-step check.
    summary_lines.append('=== Per-n step structure ===')
    summary_lines.append('')
    summary_lines.append('  n | δ_2     | δ_3     | δ_4     | step_3-2 | step_4-3 | step ≈ ?')
    summary_lines.append('----+---------+---------+---------+----------+----------+----------')
    for n in NS:
        ds = [delta_table[n].get(k) for k in KS]
        if any(d is None for d in ds):
            continue
        s_32 = ds[1] - ds[0]
        s_43 = ds[2] - ds[1]
        # Identify the integer or simple-rational step pattern, if any.
        if abs(s_32 - s_43) < 0.05:
            step_desc = f'{(s_32 + s_43)/2:.2f} (constant)'
        elif abs(s_43 - s_32 - 1) < 0.05:
            step_desc = f'k-dep, step≈k+{s_32 - 2:.1f}'
        else:
            step_desc = 'irregular'
        summary_lines.append(
            f'  {n:>2} | {ds[0]:>+7.3f} | {ds[1]:>+7.3f} | {ds[2]:>+7.3f} | '
            f'{s_32:>+8.3f} | {s_43:>+8.3f} | {step_desc}'
        )

    # Hypothesis: step relates to the Khinchin-typical contribution between
    # spikes. Khinchin: log10 K_∞ ≈ 0.42909.
    KHINCHIN_LOG10 = log10(2.6854520010)  # ≈ 0.4290
    summary_lines.append('')
    summary_lines.append('=== Spike-gap × Khinchin check ===')
    summary_lines.append(f'Khinchin constant log10 K ≈ {KHINCHIN_LOG10:.4f}')
    summary_lines.append('')
    summary_lines.append(
        '  n | k | spikes_gap | obs Δ_total | Khin pred (gap·logK) | residual'
    )
    summary_lines.append(
        '----+---+------------+-------------+----------------------+----------'
    )
    for n in NS:
        # For each (k-1 → k) gap, Δ_total = L_{k-1} - L_{k-1, post-spike(k-1)}.
        # L post-spike(k-1) = T_{k-1}_actual - L_{k-2} + log10(b/(b-1)).
        log_bb1 = log10(BASE / (BASE - 1))
        prev_L = None
        for k in KS:
            if k not in by_n[n] or k - 1 not in by_n[n]:
                # Need previous spike to compute gap. For k = first KS, skip.
                if k == KS[0]:
                    prev_L = by_n[n][k]['log10_q_prev']
                    continue
            cur = by_n[n][k]
            prev = by_n[n][k - 1] if (k - 1) in by_n[n] else None
            L_curr = cur['log10_q_prev']
            if prev is None:
                prev_L = L_curr
                continue
            T_prev = C_km1_actual(n, k)  # cumulative through d=k-1 block
            L_postspike_prev = T_prev - prev_L + log_bb1
            delta_total = L_curr - L_postspike_prev
            gap = cur['spike_index'] - prev['spike_index']
            khin_pred = gap * KHINCHIN_LOG10
            residual = delta_total - khin_pred
            summary_lines.append(
                f'  {n:>2} | {k} | {gap:>10d} | {delta_total:>11.4f} | '
                f'{khin_pred:>20.4f} | {residual:>+8.4f}'
            )
            prev_L = L_curr

    csv_path = os.path.join(HERE, 'offspike_inflation.csv')
    with open(csv_path, 'w', newline='') as f:
        csv.writer(f).writerows(rows)

    summary_path = os.path.join(HERE, 'offspike_inflation_summary.txt')
    with open(summary_path, 'w') as f:
        f.write('\n'.join(summary_lines) + '\n')

    print('\n'.join(summary_lines))
    print(f'\nwrote {csv_path}')
    print(f'wrote {summary_path}')


if __name__ == '__main__':
    main()
