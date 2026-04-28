"""
cutoff_ray_stripe.py — boundary-stitch-style visualization of cutoff sweep
==========================================================================

Loads `cutoff_ray_scan.csv` and produces per-panel-cell stripe charts.
Premise: bucketing ρ by `τ_2(Y)` and friends collapses any spatial /
fractal structure that `ρ(Y)` at fixed `(n, m)` might carry. Look at
the texture before claiming no signal.

Per panel cell, one wide figure:

    ρ(Y)                    full-resolution curve, log-x
    ρ(Y) − ρ_∞              local Mertens-error residual
    τ_2(Y)                  side track, scatter colored by value
    witness count           side track
    ν_n(Y)                  side track  (n-adic valuation of Y)
    Y mod n²                side track
    digit tier              side track  (base-10 digit class of Y)

Plus, for each cell, two 2D folds when the periods make sense:

    fold over (Y mod n², Y // n²)
    fold over (Y mod 100, Y // 100)   — base-10 reference period

Reveals n²-periodic columns (algebraic structure) or row-monotone
trends (positional structure) if either exists.

Usage:
    sage -python cutoff_ray_stripe.py
"""

import csv
import os
from collections import defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def n_adic_valuation(v, n):
    if v <= 0:
        return 0
    h = 0
    while v % n == 0:
        h += 1
        v //= n
    return h


def digit_tier(v):
    if v < 1:
        return 0
    return len(str(v))


def load_csv(path):
    by_cell = defaultdict(list)
    with open(path) as f:
        reader = csv.reader(f)
        next(reader)  # header
        for row in reader:
            n = int(row[0])
            m = int(row[1])
            label = row[2]
            Y = int(row[3])
            rho = float(row[5])
            tau2 = int(row[10])
            wc = int(row[11])
            spf = int(row[12])
            is_sq = int(row[13])
            dist_n2 = int(row[14])
            by_cell[(n, m, label)].append({
                'Y': Y, 'rho': rho, 'tau2': tau2, 'wc': wc,
                'spf': spf, 'is_sq': is_sq, 'dist_n2': dist_n2,
            })
    for k in by_cell:
        by_cell[k].sort(key=lambda r: r['Y'])
    return by_cell


def stripe_figure(n, m, label, data, out_dir):
    Ys = np.array([d['Y'] for d in data])
    rhos = np.array([d['rho'] for d in data])
    tau2s = np.array([d['tau2'] for d in data])
    wcs = np.array([d['wc'] for d in data])
    nu_n = np.array([n_adic_valuation(y, n) for y in Ys])
    Y_mod_n2 = np.array([y % (n * n) for y in Ys])
    digit = np.array([digit_tier(y) for y in Ys])

    # Local Mertens error: ρ(Y) − ρ_∞, where ρ_∞ is the median of the
    # second half of the sweep (well past saturation).
    rho_inf = float(np.median(rhos[len(rhos) // 2:]))
    local_err = rhos - rho_inf

    fig, axes = plt.subplots(7, 1, figsize=(16, 9), sharex=True,
                             gridspec_kw={'height_ratios': [3, 3, 1, 1, 1, 1, 1]})

    ax = axes[0]
    ax.plot(Ys, rhos, lw=0.4, color='steelblue', alpha=0.8)
    ax.axhline(rho_inf, color='black', lw=0.5, ls=':', alpha=0.6,
               label=f'ρ_∞ = {rho_inf:+.4f}')
    ax.set_ylabel('ρ')
    ax.set_title(f'CUTOFF stripe — n={n}, m={m}  ({label})')
    ax.set_xscale('log')
    ax.legend(fontsize=9, loc='lower right')
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    ax.plot(Ys, local_err, lw=0.4, color='crimson', alpha=0.8)
    ax.axhline(0, color='black', lw=0.5, alpha=0.5)
    ax.set_ylabel('ρ − ρ_∞')
    ax.set_xscale('log')
    ax.grid(True, alpha=0.3)

    side_tracks = [
        ('τ_2(Y)', tau2s, 'viridis'),
        ('witness', wcs, 'viridis'),
        ('ν_n(Y)', nu_n, 'cividis'),
        ('Y mod n²', Y_mod_n2, 'twilight'),
        ('digit tier', digit, 'plasma'),
    ]
    for i, (name, vals, cmap) in enumerate(side_tracks):
        ax = axes[i + 2]
        # Render as a 1D heatmap: scatter at y=0 with color=vals.
        ax.scatter(Ys, np.zeros_like(Ys), s=2, c=vals, cmap=cmap, marker='|')
        ax.set_ylabel(name, rotation=0, ha='right', va='center')
        ax.set_yticks([])
        ax.set_xscale('log')
        ax.set_xlim(Ys.min(), Ys.max())

    axes[-1].set_xlabel('Y  (log)')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f'cutoff_stripe_{label}.png'), dpi=120)
    plt.close(fig)


def fold_figure(n, m, label, data, out_dir):
    """Two side-by-side 2D folds of ρ(Y).

    Fold A: (Y mod n²) × (Y // n²) — reveals n²-periodicity if any.
    Fold B: (Y mod 100) × (Y // 100) — base-10 reference period.
    """
    Ys = np.array([d['Y'] for d in data])
    rhos = np.array([d['rho'] for d in data])
    rho_inf = float(np.median(rhos[len(rhos) // 2:]))
    local_err = rhos - rho_inf

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    for ax_idx, (period, label2) in enumerate([
        (n * n, f'n² = {n*n}'),
        (100, '100 (base-10 ref)'),
    ]):
        ax = axes[ax_idx]
        n_rows = (Ys.max() // period) + 1
        # Build image: rows = Y // period, cols = Y mod period.
        img = np.full((n_rows, period), np.nan)
        for Y, e in zip(Ys, local_err):
            r = Y // period
            c = Y % period
            if r < n_rows:
                img[r, c] = e
        # symlog norm-ish; use linear colormap centred on 0.
        vmax = float(np.nanmax(np.abs(img))) or 1.0
        im = ax.imshow(
            img, aspect='auto', cmap='PuOr',
            vmin=-vmax, vmax=vmax, origin='lower',
            interpolation='nearest',
        )
        ax.set_xlabel(f'Y mod {period}')
        ax.set_ylabel(f'Y // {period}')
        ax.set_title(f'{label2}: ρ − ρ_∞  fold')
        plt.colorbar(im, ax=ax, fraction=0.04)

    fig.suptitle(f'CUTOFF fold — n={n}, m={m}  ({label})')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f'cutoff_fold_{label}.png'), dpi=120)
    plt.close(fig)


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(out_dir, 'cutoff_ray_scan.csv')

    print(f'loading {csv_path}', flush=True)
    by_cell = load_csv(csv_path)
    print(f'  {len(by_cell)} panel cells', flush=True)

    for (n, m, label), data in by_cell.items():
        print(f'  rendering {label} ({len(data)} Y values)', flush=True)
        stripe_figure(n, m, label, data, out_dir)
        fold_figure(n, m, label, data, out_dir)

    print('done.')


if __name__ == '__main__':
    main()
