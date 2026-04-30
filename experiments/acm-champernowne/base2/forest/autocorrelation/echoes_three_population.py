"""
echoes_three_population.py — visualise the substrate-vs-noise vs
perimeter decomposition of the binary autocorrelation.

Six rows, one per panel monoid. Each row has two panels:

  full panel (left, wide): R(τ) for τ = 1..MAX_LAG, bars coloured
    by category — spike-locus (substrate blue), interior (gray),
    anomalous (red, |R| > 1.96 · σ_interior off-spike). Horizontal
    dotted lines at the Anderson band ±1.96·σ_interior.

  zoom panel (right, narrow): same data, ylim tight on the
    interior (~3 × threshold), so off-spike structure is legible.

The story across rows: the spike pattern (substrate envelope) is
structurally similar; the anomalous-bar count grows with ν_2(n),
and n = 16 is the visible perimeter signal.
"""

from __future__ import annotations

import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'core'))

from predict_autocorr import dominant_dblock, v2
from binary_core import binary_stream


PANEL = (2, 3, 4, 7, 8, 16)
N_PRIMES = 4000
MAX_LAG = 400

BG = '#0a0a0a'
SPIKE_COLOR = '#4dabf7'
INTERIOR_COLOR = '#888888'
ANOMALOUS_COLOR = '#ff6b6b'
THRESHOLD_COLOR = '#cc8888'
ZERO_COLOR = '#ffffff'


def autocorr_fft(bits, max_lag):
    s = 2.0 * np.array(bits, dtype=float) - 1.0
    n = len(s)
    ft = np.fft.rfft(s, n=2 * n)
    ac = np.fft.irfft(ft * np.conj(ft))[:n]
    ac /= ac[0]
    return ac[1:max_lag + 1]


def spike_lags(d_dom, max_lag, halo=1):
    out = set()
    for d in range(d_dom - halo, d_dom + halo + 1):
        if d < 1:
            continue
        for k in range(1, max_lag // d + 1):
            out.add(k * d)
    return {t for t in out if 1 <= t <= max_lag}


def main():
    print('Computing autocorrelations...')
    results = {}
    for n in PANEL:
        bits = binary_stream(n, count=N_PRIMES)
        d_dom = dominant_dblock(n, N_PRIMES)
        ac = autocorr_fft(bits, MAX_LAG)
        spikes = spike_lags(d_dom, MAX_LAG, halo=1)
        interior = [t for t in range(1, MAX_LAG + 1) if t not in spikes]
        interior_R = [float(ac[t - 1]) for t in interior]
        sd = float(np.std(interior_R))
        threshold = 1.96 * sd

        anomalous = sum(
            1 for t in interior if abs(float(ac[t - 1])) > threshold
        )

        results[n] = {
            'ac': ac,
            'd_dom': d_dom,
            'spikes': spikes,
            'sd': sd,
            'threshold': threshold,
            'n_anomalous': anomalous,
            'spike_mean': float(np.mean([ac[t - 1] for t in spikes])),
            'interior_mean': float(np.mean(interior_R)),
        }
        print(f'  n={n:>2}: d_dom={d_dom}, sigma_int={sd:.4f}, '
              f'thresh={threshold:.4f}, anomalous={anomalous}')

    print('Plotting...')
    fig = plt.figure(figsize=(18, 16), facecolor=BG)
    gs = fig.add_gridspec(
        len(PANEL), 2, width_ratios=[5, 1],
        hspace=0.20, wspace=0.04,
        left=0.07, right=0.99, top=0.94, bottom=0.05,
    )

    lags = np.arange(1, MAX_LAG + 1)

    for row, n in enumerate(PANEL):
        r = results[n]
        ax_full = fig.add_subplot(gs[row, 0])
        ax_zoom = fig.add_subplot(gs[row, 1])

        ac = r['ac']
        thresh = r['threshold']
        spike_set = r['spikes']
        colors = []
        for lag in lags:
            R = float(ac[lag - 1])
            if lag in spike_set:
                colors.append(SPIKE_COLOR)
            elif abs(R) > thresh:
                colors.append(ANOMALOUS_COLOR)
            else:
                colors.append(INTERIOR_COLOR)

        for ax in (ax_full, ax_zoom):
            ax.set_facecolor(BG)
            ax.bar(lags, ac, width=1.0, color=colors, edgecolor='none',
                   zorder=2)
            ax.axhline(thresh, color=THRESHOLD_COLOR, linestyle=':',
                       linewidth=0.8, alpha=0.85, zorder=3)
            ax.axhline(-thresh, color=THRESHOLD_COLOR, linestyle=':',
                       linewidth=0.8, alpha=0.85, zorder=3)
            ax.axhline(0, color=ZERO_COLOR, linewidth=0.3,
                       alpha=0.35, zorder=1)
            ax.tick_params(colors='white', labelsize=8)
            for spine in ax.spines.values():
                spine.set_color('#333')

        full_ymax = max(0.65, float(np.max(ac)) * 1.05)
        full_ymin = min(-0.30, float(np.min(ac)) * 1.05)
        ax_full.set_ylim(full_ymin, full_ymax)
        ax_full.set_xlim(0, MAX_LAG + 1)

        zoom_ymax = max(0.20, thresh * 3)
        ax_zoom.set_ylim(-zoom_ymax, zoom_ymax)
        ax_zoom.set_xlim(0, MAX_LAG + 1)

        ax_full.set_ylabel(
            f'n = {n}\nv2 = {v2(n)}',
            color='white', fontsize=11,
            rotation=0, labelpad=50, va='center'
        )

        ax_zoom.set_title(
            f'sigma={r["sd"]:.3f}  #anom={r["n_anomalous"]}',
            color='#dddddd', fontsize=8, pad=2
        )
        ax_zoom.set_yticks([])

        stats = (
            f'd_dom = {r["d_dom"]}    '
            f'mean R(spike) = {r["spike_mean"]:+.3f}    '
            f'mean R(interior) = {r["interior_mean"]:+.3f}'
        )
        ax_full.text(0.99, 0.95, stats, transform=ax_full.transAxes,
                     color='white', fontsize=8, ha='right', va='top',
                     family='monospace', alpha=0.9)

        if row == len(PANEL) - 1:
            ax_full.set_xlabel('lag tau (bits)',
                               color='white', fontsize=11)
            ax_zoom.set_xlabel('tau  (zoom)',
                               color='#dddddd', fontsize=8)
        else:
            ax_full.set_xticklabels([])
            ax_zoom.set_xticklabels([])

    title = (
        'Echoes in the stream — three-population autocorrelation '
        f'(N_primes = {N_PRIMES})\n'
        'spike loci (blue, multiples of d_dom +/- 1)   ·   '
        'interior (gray)   ·   '
        'anomalous (red, |R| > 1.96 sigma_interior)'
    )
    fig.suptitle(title, color='white', fontsize=12, y=0.985)

    out_path = os.path.join(HERE, 'echoes_three_population.png')
    plt.savefig(out_path, dpi=200, facecolor=BG, bbox_inches='tight')
    print(f'-> {out_path}')


if __name__ == '__main__':
    main()
