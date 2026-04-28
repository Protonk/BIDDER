"""
flow_heatmaps.py — residual-spectroscopy heatmaps for cutoff and payload scans
==============================================================================

The RLE-image analogy from `experiments/acm-champernowne/base2/forest/rle/`:
once you pick the right observable and subtract the universal background,
structure that bucket-means hide will surface as bright/dark stripes
(special monoids), bright/dark columns (active scout coordinates), or
finite-spectrum patterns. Raw flow is dominated by Mertens truncation
the way raw RLE is dominated by geometric decay; the structure lives in
the *residual* after universal background subtraction.

This script produces three groups of heatmaps:

  1. Cutoff matrix: panel-cell rows × scout-bucket columns. One subplot
     per scout (τ_2(Y), witness count, dist_n²). Two color encodings
     side by side: raw mean ρ, and mean ρ − row mean.
  2. Cutoff per-cell texture: per panel cell, Y-batch rows × τ_2(Y)
     bucket columns; color = mean ρ in that batch+bucket minus the
     batch's mean. Finer-grained spatial probe.
  3. Payload matrix: (n, h) rows × payload τ_2 bucket columns. Four
     observables in subplots: mean ρ, mean Λ_n, nonzero-sign neg
     fraction, neg_mass/abs_mass. Each shown both raw and row-background-
     subtracted.

The cautions from the RLE work apply: a black-tail / blank cell here
means "effectively absent at this Y_max", not "provably zero". The
finite-looking scout palette is evidence for an effective finite
spectrum at the scale we tested, not a theorem.

Usage:
    sage -python flow_heatmaps.py
"""

import csv
import os
from collections import defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


WITNESS_BUCKETS = ['0', '1', '2', '3-5', '6-9', '10+']
TAU_BUCKETS = ['0-2', '3-4', '5-8', '9-16', '17+']
DIST_BUCKETS = ['0', '1', '2', '3-5', '6-10', '11-25', '>25']
PAYLOAD_TAU_BUCKETS = ['1', '2', '3', '4-5', '6-8', '9-16', '17+']


def witness_bucket(c):
    if c == 0: return '0'
    if c == 1: return '1'
    if c == 2: return '2'
    if c <= 5: return '3-5'
    if c <= 9: return '6-9'
    return '10+'


def tau_bucket(t):
    if t <= 2: return '0-2'
    if t <= 4: return '3-4'
    if t <= 8: return '5-8'
    if t <= 16: return '9-16'
    return '17+'


def dist_bucket(d):
    if d == 0: return '0'
    if d == 1: return '1'
    if d == 2: return '2'
    if d <= 5: return '3-5'
    if d <= 10: return '6-10'
    if d <= 25: return '11-25'
    return '>25'


def payload_tau_bucket(t):
    if t == 1: return '1'
    if t == 2: return '2'
    if t == 3: return '3'
    if t <= 5: return '4-5'
    if t <= 8: return '6-8'
    if t <= 16: return '9-16'
    return '17+'


def load_cutoff_csv(path):
    by_cell = defaultdict(list)
    with open(path) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            n = int(row[0]); m = int(row[1]); label = row[2]
            Y = int(row[3])
            rho = float(row[5])
            tau2 = int(row[10]); wc = int(row[11])
            dist_n2 = int(row[14])
            by_cell[(n, m, label)].append({
                'Y': Y, 'rho': rho, 'tau2': tau2, 'wc': wc, 'dist_n2': dist_n2,
            })
    return by_cell


def load_payload_csv(path):
    rows = []
    with open(path) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            rows.append({
                'n': int(row[0]),
                'h': int(row[1]),
                'm': int(row[2]),
                'payload_tau2': int(row[5]),
                'lambda': float(row[6]),
                'rho': float(row[7]),
            })
    return rows


def build_cutoff_matrix(by_cell, scout_key, bucket_fn, bucket_order):
    """Returns (cell_labels, bucket_order, raw_matrix, residual_matrix).

    raw_matrix[i, j] = mean ρ over cell i, bucket j.
    residual_matrix[i, j] = raw[i, j] − raw[i, :].mean (i.e. row-mean subtracted).
    """
    cell_labels = list(by_cell.keys())
    raw = np.full((len(cell_labels), len(bucket_order)), np.nan)
    for i, key in enumerate(cell_labels):
        rows = by_cell[key]
        # Drop transient: use only Y past saturation.
        rows = [r for r in rows if r['Y'] >= 200]
        per_bucket = defaultdict(list)
        for r in rows:
            per_bucket[bucket_fn(r[scout_key])].append(r['rho'])
        for j, b in enumerate(bucket_order):
            if b in per_bucket and per_bucket[b]:
                raw[i, j] = float(np.mean(per_bucket[b]))
    # Row-mean subtract (ignore NaN).
    residual = np.full_like(raw, np.nan)
    for i in range(raw.shape[0]):
        row_mean = float(np.nanmean(raw[i]))
        residual[i] = raw[i] - row_mean
    return cell_labels, raw, residual


def cutoff_matrix_figure(by_cell, out_path):
    fig, axes = plt.subplots(3, 2, figsize=(13, 10))
    plot_specs = [
        ('tau2', tau_bucket, TAU_BUCKETS, 'τ_2(Y)'),
        ('wc', witness_bucket, WITNESS_BUCKETS, 'witness count'),
        ('dist_n2', dist_bucket, DIST_BUCKETS, 'dist to n²'),
    ]
    for row_i, (key, bucket_fn, order, name) in enumerate(plot_specs):
        cells, raw, residual = build_cutoff_matrix(by_cell, key, bucket_fn, order)
        labels = [f'{n}_{m}' for (n, m, _) in cells]

        ax = axes[row_i, 0]
        im = ax.imshow(raw, aspect='auto', cmap='RdBu_r',
                       vmin=-0.5, vmax=0.0)
        ax.set_xticks(range(len(order)))
        ax.set_xticklabels(order)
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels, fontsize=8)
        ax.set_title(f'raw mean ρ — scout: {name}')
        plt.colorbar(im, ax=ax, fraction=0.04)

        ax = axes[row_i, 1]
        # Symmetric color scale around zero, clipped to non-NaN max.
        finite_max = np.nanmax(np.abs(residual)) if np.isfinite(residual).any() else 1e-3
        vmax = max(finite_max, 1e-6)
        im = ax.imshow(residual, aspect='auto', cmap='PuOr',
                       vmin=-vmax, vmax=vmax)
        ax.set_xticks(range(len(order)))
        ax.set_xticklabels(order)
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels, fontsize=8)
        ax.set_title(f'mean ρ − row mean ({name}); max = {vmax:.2e}')
        plt.colorbar(im, ax=ax, fraction=0.04)

    fig.suptitle('CUTOFF matrix: panel cells × scout buckets, post-saturation')
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close(fig)


def per_cell_texture_figure(by_cell, out_dir, n_batches=40):
    """For each panel cell: Y-batch × τ_2(Y) bucket heatmap of (mean ρ −
    batch mean). Reveals whether spatial bands carry bucket-correlated
    structure."""
    for (n, m, label), rows in by_cell.items():
        # Post-saturation only.
        rows = [r for r in rows if r['Y'] >= 200]
        if not rows:
            continue
        Y_max = max(r['Y'] for r in rows)
        Y_min = min(r['Y'] for r in rows)
        batch_size = max(1, (Y_max - Y_min + 1) // n_batches)

        # batches[b][bucket] = list of ρ
        batches = [defaultdict(list) for _ in range(n_batches)]
        for r in rows:
            b = min(n_batches - 1, (r['Y'] - Y_min) // batch_size)
            batches[b][tau_bucket(r['tau2'])].append(r['rho'])

        raw = np.full((n_batches, len(TAU_BUCKETS)), np.nan)
        for b in range(n_batches):
            for j, bk in enumerate(TAU_BUCKETS):
                if bk in batches[b] and batches[b][bk]:
                    raw[b, j] = float(np.mean(batches[b][bk]))

        # Subtract batch mean.
        residual = np.full_like(raw, np.nan)
        for b in range(n_batches):
            row_mean = float(np.nanmean(raw[b]))
            if np.isnan(row_mean):
                continue
            residual[b] = raw[b] - row_mean

        fig, ax = plt.subplots(figsize=(8, 7))
        finite_max = np.nanmax(np.abs(residual)) if np.isfinite(residual).any() else 1e-4
        vmax = max(finite_max, 1e-6)
        im = ax.imshow(residual, aspect='auto', cmap='PuOr',
                       vmin=-vmax, vmax=vmax,
                       extent=[0, len(TAU_BUCKETS), Y_max, Y_min],
                       interpolation='nearest')
        ax.set_xticks(np.arange(len(TAU_BUCKETS)) + 0.5)
        ax.set_xticklabels(TAU_BUCKETS)
        ax.set_xlabel('τ_2(Y) bucket')
        ax.set_ylabel('Y (binned, post-saturation)')
        ax.set_title(f'CUTOFF texture — n={n}, m={m} ({label})\n'
                     f'mean ρ in (batch × τ_2(Y)), batch mean subtracted; max = {vmax:.2e}')
        plt.colorbar(im, ax=ax, fraction=0.04)
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, f'cutoff_heatmap_{label}.png'),
                    dpi=120)
        plt.close(fig)


def build_payload_matrix(rows):
    cells = sorted({(r['n'], r['h']) for r in rows})
    grid = {(c, b): [] for c in cells for b in PAYLOAD_TAU_BUCKETS}
    for r in rows:
        c = (r['n'], r['h'])
        b = payload_tau_bucket(r['payload_tau2'])
        grid[(c, b)].append(r)

    n_cells = len(cells)
    n_buckets = len(PAYLOAD_TAU_BUCKETS)

    obs = {
        'mean_rho': np.full((n_cells, n_buckets), np.nan),
        'mean_lambda': np.full((n_cells, n_buckets), np.nan),
        'nz_neg_frac': np.full((n_cells, n_buckets), np.nan),
        'neg_mass_frac': np.full((n_cells, n_buckets), np.nan),
        'count': np.zeros((n_cells, n_buckets), dtype=int),
    }
    EPS = 1e-12
    for i, c in enumerate(cells):
        for j, b in enumerate(PAYLOAD_TAU_BUCKETS):
            cell = grid[(c, b)]
            obs['count'][i, j] = len(cell)
            if not cell:
                continue
            rhos = np.array([r['rho'] for r in cell])
            lams = np.array([r['lambda'] for r in cell])
            abs_lams = np.abs(lams)
            n_pos = int(np.sum(lams > EPS))
            n_neg = int(np.sum(lams < -EPS))
            obs['mean_rho'][i, j] = float(np.mean(rhos))
            obs['mean_lambda'][i, j] = float(np.mean(lams))
            n_nonzero = n_pos + n_neg
            obs['nz_neg_frac'][i, j] = (n_neg / n_nonzero) if n_nonzero > 0 else np.nan
            denom = float(np.sum(abs_lams))
            obs['neg_mass_frac'][i, j] = (
                float(np.sum(abs_lams[lams < -EPS])) / denom if denom > 0 else np.nan
            )
    return cells, obs


def payload_matrix_figure(rows, out_path):
    cells, obs = build_payload_matrix(rows)
    cell_labels = [f'n={n} h={h}' for (n, h) in cells]

    fig, axes = plt.subplots(4, 2, figsize=(15, 14))

    obs_specs = [
        ('mean_rho', 'mean ρ', 'RdBu_r', None),
        ('mean_lambda', 'mean Λ_n  [nats]', 'RdBu_r', None),
        ('nz_neg_frac', 'fraction of nonzero Λ_n that are negative',
         'RdBu_r', (0.0, 1.0)),
        ('neg_mass_frac', 'neg_mass / abs_mass for Λ_n',
         'RdBu_r', (0.0, 1.0)),
    ]
    for row_i, (key, name, cmap, vlim) in enumerate(obs_specs):
        raw = obs[key]
        ax = axes[row_i, 0]
        if vlim is None:
            vmax = float(np.nanmax(np.abs(raw))) if np.isfinite(raw).any() else 1.0
            im = ax.imshow(raw, aspect='auto', cmap=cmap, vmin=-vmax, vmax=vmax)
        else:
            im = ax.imshow(raw, aspect='auto', cmap=cmap, vmin=vlim[0], vmax=vlim[1])
        ax.set_xticks(range(len(PAYLOAD_TAU_BUCKETS)))
        ax.set_xticklabels(PAYLOAD_TAU_BUCKETS, fontsize=9)
        ax.set_yticks(range(len(cell_labels)))
        ax.set_yticklabels(cell_labels, fontsize=9)
        ax.set_title(f'{name}  (raw)')
        # Annotate cells with count for context.
        for i in range(raw.shape[0]):
            for j in range(raw.shape[1]):
                c = obs['count'][i, j]
                if c > 0:
                    ax.text(j, i, f'{c}', ha='center', va='center',
                            fontsize=6, color='gray')
        plt.colorbar(im, ax=ax, fraction=0.04)

        # Row-background subtracted version.
        residual = np.full_like(raw, np.nan)
        for i in range(raw.shape[0]):
            row_mean = float(np.nanmean(raw[i]))
            if not np.isnan(row_mean):
                residual[i] = raw[i] - row_mean

        ax = axes[row_i, 1]
        finite_max = (
            float(np.nanmax(np.abs(residual))) if np.isfinite(residual).any() else 1.0
        )
        vmax = max(finite_max, 1e-6)
        im = ax.imshow(residual, aspect='auto', cmap='PuOr',
                       vmin=-vmax, vmax=vmax)
        ax.set_xticks(range(len(PAYLOAD_TAU_BUCKETS)))
        ax.set_xticklabels(PAYLOAD_TAU_BUCKETS, fontsize=9)
        ax.set_yticks(range(len(cell_labels)))
        ax.set_yticklabels(cell_labels, fontsize=9)
        ax.set_title(f'{name} − row mean   (max = {vmax:.3f})')
        plt.colorbar(im, ax=ax, fraction=0.04)

    fig.suptitle('PAYLOAD matrix: (n, h) × payload τ_2  bucket')
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close(fig)


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))

    cutoff_csv = os.path.join(out_dir, 'cutoff_ray_scan.csv')
    payload_csv = os.path.join(out_dir, 'payload_scan.csv')

    print('loading cutoff csv', flush=True)
    cutoff = load_cutoff_csv(cutoff_csv)
    print(f'  {len(cutoff)} cells', flush=True)

    print('rendering cutoff matrix', flush=True)
    cutoff_matrix_figure(cutoff,
                         os.path.join(out_dir, 'cutoff_matrix.png'))

    print('rendering per-cell cutoff textures', flush=True)
    per_cell_texture_figure(cutoff, out_dir, n_batches=40)

    print('loading payload csv', flush=True)
    payload = load_payload_csv(payload_csv)
    print(f'  {len(payload)} rows', flush=True)

    print('rendering payload matrix', flush=True)
    payload_matrix_figure(payload,
                          os.path.join(out_dir, 'payload_matrix.png'))

    print('done.')


if __name__ == '__main__':
    main()
