"""
echoes_analysis.py — three-population decomposition of the binary
autocorrelation, modelled on the off-spike CF analysis in
experiments/acm/cf/offspike_dynamics.py.

For each monoid n in the panel, compute the streaming binary
autocorrelation R(τ) for τ = 1..MAX_LAG, then partition the lag
range into three populations:

  (a) Spike loci: τ = k · d for d ∈ {d_dom − 1, d_dom, d_dom + 1}
      and k ≥ 1, within MAX_LAG. These are the substrate-predicted
      positions where consecutive entries align bit-by-bit.

  (b) Off-spike interior: lags not on any spike locus.

  (c) Anomalous: lags in (b) where |R| exceeds an Anderson-style
      ±1.96/√N white-noise band by a substantial margin. These are
      the binary-stream analog of CF Test C — perimeter-flavoured
      events not predicted by the substrate envelope.

Outputs:
  echoes.csv          per-(n, lag) rows with category labels
  echoes_summary.txt  panel summary (mean R per population, etc.)
"""

from __future__ import annotations

import csv
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'core'))

from predict_autocorr import (
    autocorr_dblock_at_d,
    avg_entry_length,
    dominant_dblock,
    v2,
)
from binary_core import binary_stream
from acm_core import acm_n_primes


PANEL = (2, 3, 4, 7, 8, 16)
N_PRIMES = 4000
MAX_LAG = 400


def autocorr_fft(bits, max_lag):
    s = 2.0 * np.array(bits, dtype=float) - 1.0
    n = len(s)
    ft = np.fft.rfft(s, n=2 * n)
    ac = np.fft.irfft(ft * np.conj(ft))[:n]
    ac /= ac[0]
    return ac[1:max_lag + 1]


def spike_lags(d_dom: int, max_lag: int, halo: int = 1) -> set:
    """Lags τ that are integer multiples of d ∈ {d_dom-halo, ..., d_dom+halo}."""
    out = set()
    for d in range(d_dom - halo, d_dom + halo + 1):
        if d < 1:
            continue
        for k in range(1, max_lag // d + 1):
            out.add(k * d)
    return {t for t in out if 1 <= t <= max_lag}


def main():
    rows = [(
        'n', 'v2', 'd_dom', 'avg_d', 'lag', 'R',
        'category', 'spike_factor_d', 'spike_factor_k',
    )]
    summary_lines = [
        '# echoes_analysis — binary autocorrelation, three-population test',
        f'# panel = {PANEL}, N_PRIMES = {N_PRIMES}, MAX_LAG = {MAX_LAG}',
        f'# spike loci: τ = k·d for d ∈ {{d_dom−1, d_dom, d_dom+1}}, k ≥ 1',
        '',
        f'  {"n":>3}  {"ν2":>3}  {"d_dom":>5}  {"avg_d":>6}  '
        f'{"R_dpred":>8}  {"R_dobs":>8}  '
        f'{"spike_mean":>10}  {"interior_mean":>12}  '
        f'{"interior_sd":>11}  {"#anomalous":>11}',
    ]

    panel_results = []
    for n in PANEL:
        bits = binary_stream(n, count=N_PRIMES)
        d_dom = dominant_dblock(n, N_PRIMES)
        avg_d = avg_entry_length(n, N_PRIMES)
        ac = autocorr_fft(bits, MAX_LAG)
        spikes = spike_lags(d_dom, MAX_LAG, halo=1)

        spike_R = []
        interior_R = []
        per_lag = []
        for lag in range(1, MAX_LAG + 1):
            R = float(ac[lag - 1])
            if lag in spikes:
                spike_R.append(R)
                # which (d, k) does it land on?
                for d in (d_dom - 1, d_dom, d_dom + 1):
                    if d > 0 and lag % d == 0:
                        per_lag.append(
                            (n, v2(n), d_dom, avg_d, lag, R,
                             'spike', d, lag // d)
                        )
                        break
            else:
                interior_R.append(R)
                per_lag.append(
                    (n, v2(n), d_dom, avg_d, lag, R,
                     'interior', '', '')
                )

        spike_mean = float(np.mean(spike_R)) if spike_R else 0.0
        interior_mean = float(np.mean(interior_R)) if interior_R else 0.0
        interior_sd = float(np.std(interior_R)) if interior_R else 0.0

        # Anomaly threshold: ±1.96 SD of interior population.
        threshold = 1.96 * interior_sd if interior_sd > 0 else 0.05
        n_anom = sum(
            1 for lag in range(1, MAX_LAG + 1)
            if lag not in spikes and abs(float(ac[lag - 1])) > threshold
        )

        # Re-tag anomalous interior lags.
        for i, row in enumerate(per_lag):
            if row[6] == 'interior' and abs(row[5]) > threshold:
                per_lag[i] = row[:6] + ('anomalous',) + row[7:]

        rows.extend(per_lag)

        R_dpred = float(autocorr_dblock_at_d(n, d_dom))
        R_dobs = float(ac[d_dom - 1])

        summary_lines.append(
            f'  {n:>3}  {v2(n):>3}  {d_dom:>5}  {avg_d:>6.2f}  '
            f'{R_dpred:>+8.4f}  {R_dobs:>+8.4f}  '
            f'{spike_mean:>+10.4f}  {interior_mean:>+12.4f}  '
            f'{interior_sd:>11.4f}  {n_anom:>11}'
        )
        panel_results.append({
            'n': n, 'd_dom': d_dom, 'avg_d': avg_d,
            'R_dpred': R_dpred, 'R_dobs': R_dobs,
            'spike_mean': spike_mean,
            'interior_mean': interior_mean,
            'interior_sd': interior_sd,
            'threshold': threshold, 'n_anom': n_anom,
        })

    # Write per-lag CSV.
    csv_path = os.path.join(HERE, 'echoes.csv')
    with open(csv_path, 'w', newline='') as f:
        csv.writer(f).writerows(rows)
    print(f'wrote {csv_path}')

    # Write summary.
    summary_lines.append('')
    summary_lines.append('## Population means')
    summary_lines.append('  spike_mean = mean R over substrate-predicted spike loci')
    summary_lines.append('  interior_mean = mean R over off-spike lags')
    summary_lines.append('  interior_sd = std R over off-spike lags')
    summary_lines.append(
        '  #anomalous = #{interior lags with |R| > 1.96 · interior_sd}'
    )
    summary_lines.append('')
    summary_lines.append('## Headline')
    n_blocks = len(panel_results)
    spike_means = [r['spike_mean'] for r in panel_results]
    interior_means = [r['interior_mean'] for r in panel_results]
    summary_lines.append(
        f'  panel size                       = {n_blocks}'
    )
    summary_lines.append(
        f'  mean spike-loci R across panel   = {np.mean(spike_means):+.4f}'
    )
    summary_lines.append(
        f'  mean interior R across panel     = {np.mean(interior_means):+.4f}'
    )
    summary_lines.append(
        f'  spike/interior ratio             = '
        f'{np.mean(spike_means) / max(abs(np.mean(interior_means)), 1e-9):.2f}'
    )

    summary_path = os.path.join(HERE, 'echoes_summary.txt')
    with open(summary_path, 'w') as f:
        f.write('\n'.join(summary_lines) + '\n')
    print(f'wrote {summary_path}')
    print()
    print('\n'.join(summary_lines))


if __name__ == '__main__':
    main()
