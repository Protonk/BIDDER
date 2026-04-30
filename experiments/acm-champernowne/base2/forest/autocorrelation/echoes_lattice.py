"""
echoes_lattice.py — heatmap of binary autocorrelation across the
(n, d) lattice, plus the streaming-side spike structure.

Three panels share the n-axis on the y:

  Left (substrate prediction):
    R_block(n, d) = within-d-block autocorrelation at lag τ = d.
    Computed exactly via direct enumeration of d-bit n-primes
    (algebra/predict_autocorr.py:autocorr_dblock_at_d).
    Rows: n ∈ N_GRID. Columns: d ∈ D_GRID.

  Middle (streaming signal):
    R_stream(n, τ) = streaming binary autocorrelation at lag τ
    for the first N_PRIMES n-primes. Same colormap as left.
    Rows: n. Columns: τ ∈ TAU_GRID (small lags where spikes live).
    The d_dom column lights up per row; multiples of d_dom carry
    streaming spikes diluted by a factor ~0.5 relative to the
    within-block prediction.

  Right (dilution):
    streaming-to-within-block ratio: R_stream(n, d_dom) /
    R_block(n, d_dom). One narrow column. Documents the
    cross-block dilution that A2 reports as ~0.49 across the
    panel of six.

Cells with too few d-bit n-primes (M < 4) are masked (gray).
"""

from __future__ import annotations

import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'core'))

from predict_autocorr import (
    autocorr_dblock_at_d, dominant_dblock, n_primes_in_dblock, v2,
)
from binary_core import binary_stream


N_GRID = list(range(2, 33))             # n = 2..32
D_GRID = list(range(4, 15))             # d = 4..14
TAU_GRID = list(range(1, 41))           # streaming lag = 1..40
                                        # (covers d_dom and 2*d_dom for all panel n)
N_PRIMES = 4000

BG = '#0a0a0a'
CMAP = 'magma'
MASK_COLOR = '#1a1a1a'
ANNOT_COLOR = '#dddddd'


def autocorr_fft(bits, max_lag):
    s = 2.0 * np.array(bits, dtype=float) - 1.0
    n = len(s)
    ft = np.fft.rfft(s, n=2 * n)
    ac = np.fft.irfft(ft * np.conj(ft))[:n]
    ac /= ac[0]
    return ac[1:max_lag + 1]


def main():
    print('Computing predicted R_block(n, d)...')
    # Left panel: predicted within-d-block R, rows n, cols d.
    R_pred = np.full((len(N_GRID), len(D_GRID)), np.nan)
    for i, n in enumerate(N_GRID):
        for j, d in enumerate(D_GRID):
            primes = n_primes_in_dblock(n, d)
            if len(primes) < 4:
                continue
            try:
                R = float(autocorr_dblock_at_d(n, d))
                R_pred[i, j] = R
            except ValueError:
                pass
    print(f'  populated {np.sum(~np.isnan(R_pred))} / '
          f'{R_pred.size} cells')

    print('Computing streaming R_stream(n, τ)...')
    # Middle panel: streaming R, rows n, cols τ.
    max_tau = max(TAU_GRID)
    R_stream = np.full((len(N_GRID), len(TAU_GRID)), np.nan)
    d_doms = []
    for i, n in enumerate(N_GRID):
        bits = binary_stream(n, count=N_PRIMES)
        ac = autocorr_fft(bits, max_tau)
        for j, tau in enumerate(TAU_GRID):
            R_stream[i, j] = float(ac[tau - 1])
        d_doms.append(dominant_dblock(n, N_PRIMES))
        print(f'  n={n:>2}: d_dom={d_doms[-1]:>2}, '
              f'stream R(τ=d_dom) = {ac[d_doms[-1] - 1]:+.3f}')

    # Right panel: dilution ratio at τ = d_dom per row.
    print('Computing dilution ratio...')
    ratios = np.full(len(N_GRID), np.nan)
    for i, n in enumerate(N_GRID):
        d_dom = d_doms[i]
        try:
            R_block_at_dom = float(autocorr_dblock_at_d(n, d_dom))
            R_stream_at_dom = float(R_stream[i, d_dom - 1]) \
                if d_dom <= max_tau else np.nan
            if R_block_at_dom > 0:
                ratios[i] = R_stream_at_dom / R_block_at_dom
        except ValueError:
            pass

    # Common colour normalisation for left and middle panels.
    vmin, vmax = -0.1, 0.9
    norm = Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.get_cmap(CMAP).copy()
    cmap.set_bad(MASK_COLOR)

    print('Plotting...')
    fig = plt.figure(figsize=(18, 12), facecolor=BG)
    gs = fig.add_gridspec(
        1, 4, width_ratios=[len(D_GRID), len(TAU_GRID), 2, 1.2],
        wspace=0.10,
        left=0.06, right=0.96, top=0.92, bottom=0.10,
    )

    ax_pred = fig.add_subplot(gs[0, 0])
    ax_str = fig.add_subplot(gs[0, 1])
    ax_rat = fig.add_subplot(gs[0, 2])
    ax_cb = fig.add_subplot(gs[0, 3])

    # ---- Left: predicted R_block(n, d) ----
    im_pred = ax_pred.imshow(
        R_pred, aspect='auto', origin='lower',
        cmap=cmap, norm=norm, interpolation='nearest',
    )
    ax_pred.set_xticks(np.arange(len(D_GRID)))
    ax_pred.set_xticklabels(D_GRID, fontsize=9)
    ax_pred.set_yticks(np.arange(len(N_GRID)))
    ax_pred.set_yticklabels(
        [f'{n:>2} (ν2={v2(n)})' for n in N_GRID],
        fontsize=9, family='monospace'
    )
    ax_pred.set_xlabel('d   (bits per entry)', color='white',
                       fontsize=11)
    ax_pred.set_ylabel('n', color='white', fontsize=11)
    ax_pred.set_title(
        'predicted within-d-block\nR(τ = d) = '
        'autocorr_dblock_at_d(n, d)',
        color='white', fontsize=11, pad=8
    )
    # Annotate values on left heatmap (compact integers ×100).
    for i, n in enumerate(N_GRID):
        for j, d in enumerate(D_GRID):
            v = R_pred[i, j]
            if np.isnan(v):
                ax_pred.text(j, i, '·', ha='center', va='center',
                             color='#555555', fontsize=8)
            else:
                ax_pred.text(j, i, f'{v:.2f}',
                             ha='center', va='center',
                             color='white' if v < 0.5 else 'black',
                             fontsize=7)

    # ---- Middle: streaming R(n, τ) ----
    im_str = ax_str.imshow(
        R_stream, aspect='auto', origin='lower',
        cmap=cmap, norm=norm, interpolation='nearest',
    )
    ax_str.set_xticks(np.arange(len(TAU_GRID)))
    ax_str.set_xticklabels(TAU_GRID, fontsize=8)
    ax_str.set_yticks([])  # share with left
    ax_str.set_xlabel('τ  (streaming lag, bits)',
                      color='white', fontsize=11)
    ax_str.set_title(
        'streaming binary autocorrelation\n'
        f'R_stream(n, τ),  N_primes = {N_PRIMES}',
        color='white', fontsize=11, pad=8
    )
    # Mark d_dom and 2·d_dom per row with green outlines (substrate
    # spike loci). Single d_dom = thicker; 2·d_dom = thinner.
    for i, n in enumerate(N_GRID):
        d_dom = d_doms[i]
        for k, lw in ((1, 1.4), (2, 0.8)):
            t = k * d_dom
            if t in TAU_GRID:
                j = TAU_GRID.index(t)
                ax_str.add_patch(plt.Rectangle(
                    (j - 0.5, i - 0.5), 1, 1,
                    fill=False, edgecolor='#7df97d',
                    linewidth=lw, zorder=3
                ))

    # ---- Right: dilution ratio ----
    rat_arr = ratios.reshape(-1, 1)
    rat_norm = Normalize(vmin=0, vmax=1)
    cmap_rat = plt.get_cmap('cividis').copy()
    cmap_rat.set_bad(MASK_COLOR)
    ax_rat.imshow(
        rat_arr, aspect='auto', origin='lower',
        cmap=cmap_rat, norm=rat_norm, interpolation='nearest',
    )
    ax_rat.set_xticks([0])
    ax_rat.set_xticklabels(['ratio'], fontsize=9)
    ax_rat.set_yticks([])
    ax_rat.set_title(
        'streaming /\nwithin-block\nat τ = d_dom',
        color='white', fontsize=10, pad=8
    )
    for i, r in enumerate(ratios):
        if not np.isnan(r):
            ax_rat.text(0, i, f'{r:.2f}', ha='center', va='center',
                        color='white' if r < 0.5 else 'black',
                        fontsize=8)

    # Common colorbar for left and middle (shared scale).
    cb = fig.colorbar(im_pred, cax=ax_cb)
    cb.set_label('R(τ)', color='white', fontsize=10)
    cb.ax.tick_params(colors='white', labelsize=8)
    cb.outline.set_edgecolor('#444')

    for ax in (ax_pred, ax_str, ax_rat):
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#333')
        ax.set_facecolor(BG)

    title = (
        'Echoes lattice — substrate prediction (left), '
        'streaming signal (middle), and cross-block dilution (right)'
    )
    fig.suptitle(title, color='white', fontsize=13, y=0.97)

    out_path = os.path.join(HERE, 'echoes_lattice.png')
    plt.savefig(out_path, dpi=200, facecolor=BG, bbox_inches='tight')
    print(f'-> {out_path}')


if __name__ == '__main__':
    main()
