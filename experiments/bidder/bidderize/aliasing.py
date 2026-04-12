"""
aliasing.py — Sampling aliasing at declining coverage.

Small multiples grid: 2 rows (BIDDER, numpy) × 6 columns
(coverage ratios from 90% to 5%). Each panel is a first-digit
shutter heatmap for a short add-then-mul schedule, showing where
IID speckle becomes visible while the permutation stays clean.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..')
DIST = os.path.join(ROOT, 'dist')
sys.path.insert(0, DIST)
sys.path.insert(0, os.path.join(ROOT, 'generator'))
sys.path.insert(0, os.path.join(ROOT, 'core'))

try:
    import bidder_c as bidder
except ImportError:
    import bidder

from coupler import Bidder

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


BG = '#0a0a0a'
FG = 'white'
SPINE = '#333'

COVERAGES = [0.90, 0.05, 0.01]
N_ADD = 1000
MUL_COUNTS = [1, 2, 3, 4, 5]


def first_digits_from_log(log_values):
    frac = log_values - np.floor(log_values)
    return np.minimum((10**frac + 1e-9).astype(int), 9)


MUL_DISPLAY_ROWS = 150


def run_schedule(reals, log_reals, n_trials, N, index_source, n_add, mul_counts):
    """Run n_add adds, then 1 mul (snapshot), then 1 more mul (snapshot),
    etc. up to max(mul_counts) muls. Each mul snapshot is spread over
    MUL_DISPLAY_ROWS for visibility. Returns a heatmap and the y
    positions of the mul boundaries."""
    n_muls = max(mul_counts)
    n_display = n_add + n_muls * MUL_DISPLAY_ROWS
    heat = np.zeros((n_display, 9))
    mul_boundaries = []

    init_idx = index_source(0, n_trials, N)
    values = reals[init_idx].copy()
    log_values = log_reals[init_idx].copy()

    # Add phase
    for step in range(n_add):
        idx2 = index_source(step + 1, n_trials, N)
        values = values + reals[idx2]
        log_values = np.log10(np.maximum(values, 1e-300))

        fds = first_digits_from_log(log_values)
        for d in range(1, 10):
            heat[step, d - 1] = np.sum(fds == d) / n_trials

    # Mul phase: one mul at a time, snapshot after each
    for m in range(n_muls):
        idx2 = index_source(n_add + 1 + m, n_trials, N)
        log_values = log_values + log_reals[idx2]
        values = 10**log_values

        fds = first_digits_from_log(log_values)
        mul_row = np.zeros(9)
        for d in range(1, 10):
            mul_row[d - 1] = np.sum(fds == d) / n_trials

        row_start = n_add + m * MUL_DISPLAY_ROWS
        for row in range(MUL_DISPLAY_ROWS):
            heat[row_start + row] = mul_row
        mul_boundaries.append(row_start)

    return heat, mul_boundaries


def make_numpy_source(seed_base):
    def source(step, n_trials, N):
        rng = np.random.default_rng(seed_base + step)
        return rng.integers(0, N, size=n_trials)
    return source


def make_bidder_source(name_base):
    def source(step, n_trials, N):
        B = bidder.cipher(period=N, key=f'{name_base}:s{step}'.encode())
        perm = np.array(list(B), dtype=np.int64)
        return perm[:n_trials]
    return source


def main():
    print("Generating uniform source (BIDDER)...")
    gen = Bidder(base=10, digit_class=4, key=b'aliasing')
    N = gen.period
    raw = np.array([gen.next() for _ in range(N)], dtype=np.float64)
    reals = 1.0 + raw / 10.0
    log_reals = np.log10(reals)

    n_cols = len(COVERAGES)
    fig, axes = plt.subplots(2, n_cols, figsize=(5.5 * n_cols, 16),
                             sharex=True, sharey=True)
    fig.patch.set_facecolor(BG)

    vmax = 0.0
    results = {}

    for ci, cov in enumerate(COVERAGES):
        n_trials = max(10, int(N * cov))
        label = f'{int(cov * 100)}%  (n={n_trials})'
        print(f'  coverage {label}...')

        heat_b, bounds_b = run_schedule(
            reals, log_reals, n_trials, N,
            make_bidder_source(f'alias_b_{ci}'),
            N_ADD, MUL_COUNTS,
        )
        heat_n, bounds_n = run_schedule(
            reals, log_reals, n_trials, N,
            make_numpy_source(ci * 10000),
            N_ADD, MUL_COUNTS,
        )
        results[ci] = (heat_b, heat_n, bounds_b, label)
        vmax = max(vmax, heat_b.max(), heat_n.max())

    for ci, cov in enumerate(COVERAGES):
        heat_b, heat_n, mul_bounds, label = results[ci]

        for row, (heat, row_label) in enumerate([
            (heat_b, 'BIDDER'),
            (heat_n, 'numpy'),
        ]):
            ax = axes[row, ci]
            ax.set_facecolor(BG)
            ax.tick_params(colors=FG)
            for spine in ax.spines.values():
                spine.set_color(SPINE)

            n_display = heat.shape[0]
            ax.imshow(heat, aspect='auto', origin='lower', cmap='inferno',
                      extent=[0.5, 9.5, 0, n_display],
                      vmin=0.0, vmax=vmax, interpolation='nearest')

            for mi, boundary in enumerate(mul_bounds):
                ax.axhline(boundary, color=FG, linewidth=0.6,
                           linestyle='--', alpha=0.4)
                if ci == n_cols - 1 and row == 0:
                    ax.text(9.6, boundary + MUL_DISPLAY_ROWS / 2,
                            f'{mi+1} mul', color=FG, fontsize=8,
                            va='center', ha='left')

            ax.set_xticks(range(1, 10))

            if row == 0:
                ax.set_title(label, color=FG, fontsize=12)
            if ci == 0:
                ax.set_ylabel(f'{row_label}\nstep', color=FG, fontsize=11)
            if row == 1:
                ax.set_xlabel('first digit', color=FG, fontsize=10)

    fig.suptitle('1000 adds, then 1..5 muls:  BIDDER (top) vs numpy (bottom)',
                 color=FG, fontsize=14, y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    out = os.path.join(HERE, 'aliasing.png')
    fig.savefig(out, dpi=200, facecolor=BG, bbox_inches='tight')
    plt.close(fig)
    print(f'-> aliasing.png')


if __name__ == '__main__':
    main()
