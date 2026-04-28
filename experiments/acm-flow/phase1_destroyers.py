"""
phase1_destroyers.py — destroyer + subtraction tests for Phase 1 claims
========================================================================

Per `experiments/VISUAL-REDUCTION-DISCIPLINE.md`: every visual claim
should pair with an operation that would erase it if it were artifact.
A chart that survives the right destroyer is evidence; a chart with
no destroyer is a sketch.

Three tests:

  1. Y-shuffle null for the cutoff "dist-to-n² coherent line."
     Within each (n, m) cell, shuffle ρ across Y; recompute the panel-
     cell × dist_n² bucket heatmap with row-mean subtracted. If the
     dist=0 / dist=2 pattern appears in the shuffled null, it's a
     marginal artifact. If it survives at z >> null variation, it's
     evidence.

  2. m-shuffle null for the payload graduation.
     Within each (n, h) cell, shuffle Λ_n across m. Recompute
     ξ(payload τ_2 → Λ_n). If shuffled ξ ≈ 0, the graduation is real;
     if shuffled ξ ≈ observed, it is a marginal artifact.

  3. Family-geometry subtraction.
     Per `VISUAL-REDUCTION-DISCIPLINE.md` family-geometry layer: predict
     Λ_n(m) from a coarse `(h, n_type, payload τ_2 bucket)` model where
     `n_type ∈ {prime, prime_power, multi_prime}`. Subtract the bucket
     mean from each observation. Render residual heatmap. If residual
     is uniformly small, the coarse model captures the structure. If
     not, more coordinates remain.

Loads:
  cutoff_ray_scan.csv   (50000 Y per cell, 9 cells)
  payload_scan.csv      (8206 m × (n, h) rows)

Outputs:
  destroyer_cutoff_shuffle.png   actual / null mean / z-score panels
  destroyer_payload_shuffle.png  observed ξ vs null distribution per (n, h)
  family_geometry_residual.png   per-cell residual after coarse model

Method choices declared against ACM-MANGOLDT.md:
  - ξ as workhorse, K=32 random tie-breaks for observed; K=8 per
    shuffle iteration for null distribution (100 shuffles × 8 = 800
    null ξ per cell, traded against compute).
  - bucket aggregation as before; row-background subtraction;
    z-score = (actual − null mean) / null std as the destroyer
    discriminator.

Usage:
    sage -python phase1_destroyers.py
"""

import csv
import os
from collections import defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


EPS = 1e-12
K_SHUFFLES = 100
SEED = 42


# ---- bucket helpers ----

def dist_bucket(d):
    if d == 0: return '0'
    if d == 1: return '1'
    if d == 2: return '2'
    if d <= 5: return '3-5'
    if d <= 10: return '6-10'
    if d <= 25: return '11-25'
    return '>25'


DIST_BUCKETS = ['0', '1', '2', '3-5', '6-10', '11-25', '>25']


def payload_tau_bucket(t):
    if t == 1: return '1'
    if t == 2: return '2'
    if t == 3: return '3'
    if t <= 5: return '4-5'
    if t <= 8: return '6-8'
    if t <= 16: return '9-16'
    return '17+'


PAYLOAD_TAU_BUCKETS = ['1', '2', '3', '4-5', '6-8', '9-16', '17+']


# ---- ξ ----

def chatterjee_xi_single(x, y):
    n = len(x)
    if n < 2:
        return 0.0
    order = np.argsort(x)
    y_perm = y[order]
    ranks = np.argsort(np.argsort(y_perm)) + 1
    return 1.0 - 3.0 * np.sum(np.abs(np.diff(ranks))) / (n * n - 1)


def chatterjee_xi_with_ties(x, y, K=32, base_seed=SEED):
    n = len(x)
    if n < 2:
        return 0.0
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    rng = np.random.default_rng(base_seed)
    xis = []
    for _ in range(K):
        jitter = rng.uniform(-1e-9, 1e-9, n)
        xis.append(chatterjee_xi_single(x_arr + jitter, y_arr))
    return float(np.mean(xis))


# ---- n family classifier ----

def n_type(n):
    """Family-geometry classifier of n via prime factorization."""
    if n < 2:
        return 'unit'
    factors = {}
    r = n
    p = 2
    while p * p <= r:
        while r % p == 0:
            factors[p] = factors.get(p, 0) + 1
            r //= p
        p += 1
    if r > 1:
        factors[r] = factors.get(r, 0) + 1
    omega = len(factors)
    Omega = sum(factors.values())
    if omega == 1 and Omega == 1:
        return 'prime'
    if omega == 1 and Omega > 1:
        return 'prime_power'
    if omega > 1:
        return 'multi_prime'
    return 'unit'


# ---- I/O ----

def load_cutoff(path):
    by_cell = defaultdict(list)
    with open(path) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            n = int(row[0]); m = int(row[1]); label = row[2]
            Y = int(row[3])
            rho = float(row[5])
            dist_n2 = int(row[14])
            by_cell[(n, m, label)].append({
                'Y': Y, 'rho': rho, 'dist_n2': dist_n2,
            })
    return by_cell


def load_payload(path):
    by_cell = defaultdict(list)
    with open(path) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            n = int(row[0]); h = int(row[1]); m = int(row[2])
            payload_tau2 = int(row[5])
            lam = float(row[6])
            rho = float(row[7])
            by_cell[(n, h)].append({
                'm': m, 'payload_tau2': payload_tau2,
                'lambda': lam, 'rho': rho,
            })
    return by_cell


# ---- Destroyer 1: Y-shuffle for cutoff dist_n² ----

def cutoff_dist_residual_matrix(by_cell, perm_by_cell=None):
    """Returns a (#cells × #dist_buckets) matrix of mean ρ minus row mean,
    where ρ in cell `key` is optionally permuted by `perm_by_cell[key]`
    (a numpy array of indices into the post-saturation rho array)."""
    cells = list(by_cell.keys())
    n_cells = len(cells)
    n_buckets = len(DIST_BUCKETS)
    matrix = np.full((n_cells, n_buckets), np.nan)
    for i, key in enumerate(cells):
        rows = [r for r in by_cell[key] if r['Y'] >= 200]
        if not rows:
            continue
        rhos = np.array([r['rho'] for r in rows])
        if perm_by_cell is not None:
            rhos = rhos[perm_by_cell[key]]
        bucket_idx = np.array([DIST_BUCKETS.index(dist_bucket(r['dist_n2']))
                                for r in rows])
        for j in range(n_buckets):
            mask = bucket_idx == j
            if mask.any():
                matrix[i, j] = float(np.mean(rhos[mask]))
        # Row-mean subtract.
        rm = float(np.nanmean(matrix[i]))
        if not np.isnan(rm):
            matrix[i] = matrix[i] - rm
    return cells, matrix


def destroyer_cutoff(by_cell, K, out_dir):
    cells, actual = cutoff_dist_residual_matrix(by_cell)

    # Pre-compute post-saturation sizes for each cell.
    cell_size = {key: sum(1 for r in rows if r['Y'] >= 200)
                 for key, rows in by_cell.items()}

    rng = np.random.default_rng(SEED)
    null_samples = np.full((K, len(cells), len(DIST_BUCKETS)), np.nan)
    for k in range(K):
        perms = {key: rng.permutation(cell_size[key]) for key in by_cell}
        _, residual = cutoff_dist_residual_matrix(by_cell, perm_by_cell=perms)
        null_samples[k] = residual

    null_mean = np.nanmean(null_samples, axis=0)
    null_std = np.nanstd(null_samples, axis=0)
    z = np.where(null_std > 0,
                 (actual - null_mean) / null_std,
                 0.0)

    # Plot.
    fig, axes = plt.subplots(1, 3, figsize=(17, 6))
    cell_labels = [f'n={n} m={m}' for (n, m, _) in cells]

    vmax_a = max(float(np.nanmax(np.abs(actual))), 1e-7)
    im = axes[0].imshow(actual, aspect='auto', cmap='PuOr',
                        vmin=-vmax_a, vmax=vmax_a)
    axes[0].set_xticks(range(len(DIST_BUCKETS)))
    axes[0].set_xticklabels(DIST_BUCKETS, fontsize=9)
    axes[0].set_yticks(range(len(cells)))
    axes[0].set_yticklabels(cell_labels, fontsize=9)
    axes[0].set_title(f'actual residual (mean ρ − row mean)\n max = {vmax_a:.2e}')
    plt.colorbar(im, ax=axes[0], fraction=0.04)

    vmax_n = max(float(np.nanmax(np.abs(null_mean))), 1e-7)
    im = axes[1].imshow(null_mean, aspect='auto', cmap='PuOr',
                        vmin=-vmax_n, vmax=vmax_n)
    axes[1].set_xticks(range(len(DIST_BUCKETS)))
    axes[1].set_xticklabels(DIST_BUCKETS, fontsize=9)
    axes[1].set_yticks(range(len(cells)))
    axes[1].set_yticklabels(cell_labels, fontsize=9)
    axes[1].set_title(f'shuffle null mean (K={K})\n max = {vmax_n:.2e}')
    plt.colorbar(im, ax=axes[1], fraction=0.04)

    vmax_z = max(float(np.nanmax(np.abs(z))), 1.0)
    im = axes[2].imshow(z, aspect='auto', cmap='PuOr',
                        vmin=-vmax_z, vmax=vmax_z)
    axes[2].set_xticks(range(len(DIST_BUCKETS)))
    axes[2].set_xticklabels(DIST_BUCKETS, fontsize=9)
    axes[2].set_yticks(range(len(cells)))
    axes[2].set_yticklabels(cell_labels, fontsize=9)
    axes[2].set_title(f'z = (actual − null) / null_std\n max |z| = {vmax_z:.2f}')
    plt.colorbar(im, ax=axes[2], fraction=0.04)

    fig.suptitle(
        'CUTOFF destroyer — Y-shuffle null for dist_n² residual'
    )
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'destroyer_cutoff_shuffle.png'), dpi=120)
    plt.close(fig)

    # Single-line summary per cell × bucket:
    z0_mean = float(np.nanmean(np.abs(z[:, 0])))
    z2_mean = float(np.nanmean(np.abs(z[:, 2])))
    z_max = float(np.nanmax(np.abs(z)))
    return {
        'max_actual': vmax_a,
        'max_null': vmax_n,
        'max_z': z_max,
        'mean_|z|_dist0': z0_mean,
        'mean_|z|_dist2': z2_mean,
        'cells': cells,
        'actual': actual,
        'null_mean': null_mean,
        'null_std': null_std,
        'z': z,
    }


# ---- Destroyer 2: m-shuffle for payload ξ ----

def destroyer_payload(by_cell, K, out_dir):
    rng = np.random.default_rng(SEED)
    results = []
    for (n, h), rows in sorted(by_cell.items()):
        if len(rows) < 5:
            continue
        ptau2 = np.array([r['payload_tau2'] for r in rows], dtype=float)
        lam = np.array([r['lambda'] for r in rows], dtype=float)

        obs = chatterjee_xi_with_ties(ptau2, lam, K=32, base_seed=SEED)

        null_xis = np.empty(K)
        for i in range(K):
            shuffled = rng.permutation(lam)
            null_xis[i] = chatterjee_xi_with_ties(
                ptau2, shuffled, K=8, base_seed=SEED + i + 1
            )
        null_mean = float(np.mean(null_xis))
        null_std = float(np.std(null_xis))
        z = (obs - null_mean) / null_std if null_std > 0 else float('inf')
        results.append({
            'n': n, 'h': h, 'count': len(rows),
            'observed_xi': obs,
            'null_mean': null_mean,
            'null_std': null_std,
            'z': z,
            'null_xis': null_xis,
        })

    cell_labels = [f'n={r["n"]} h={r["h"]}' for r in results]
    obs_vals = [r['observed_xi'] for r in results]
    null_means = [r['null_mean'] for r in results]
    null_stds = [r['null_std'] for r in results]

    fig, ax = plt.subplots(figsize=(13, 6))
    x_pos = np.arange(len(results))
    width = 0.35
    bars = ax.bar(x_pos - width / 2, obs_vals, width, label='observed ξ',
                  color='steelblue', alpha=0.85)
    ax.errorbar(x_pos + width / 2, null_means, yerr=null_stds, fmt='o',
                color='crimson', label=f'null ξ mean ± std (K={K})',
                capsize=4)
    for x, r in zip(x_pos, results):
        z_text = f'z={r["z"]:+.1f}' if abs(r['z']) < 1e6 else 'z=∞'
        ax.text(x - width / 2, r['observed_xi'] + 0.02, z_text,
                ha='center', fontsize=8)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(cell_labels, rotation=45, ha='right')
    ax.set_ylabel('ξ(payload τ_2 → Λ_n)')
    ax.set_title('PAYLOAD destroyer — m-shuffle null for ξ graduation')
    ax.axhline(0, color='black', lw=0.5)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'destroyer_payload_shuffle.png'), dpi=120)
    plt.close(fig)

    return results


# ---- Subtraction 3: family-geometry residual ----

def family_geometry_residual(by_cell, out_dir):
    # Pool by (h, n_type, payload τ_2 bucket).
    pool = defaultdict(list)
    for (n, h), rows in by_cell.items():
        nt = n_type(n)
        for r in rows:
            b = payload_tau_bucket(r['payload_tau2'])
            pool[(h, nt, b)].append(r['lambda'])
    pred = {k: float(np.mean(v)) for k, v in pool.items()}
    pred_size = {k: len(v) for k, v in pool.items()}

    cells = sorted(by_cell.keys())
    cell_labels = [f'n={n} h={h}  ({n_type(n)})' for (n, h) in cells]

    matrix = np.full((len(cells), len(PAYLOAD_TAU_BUCKETS)), np.nan)
    counts = np.zeros((len(cells), len(PAYLOAD_TAU_BUCKETS)), dtype=int)
    for i, (n, h) in enumerate(cells):
        nt = n_type(n)
        for j, b in enumerate(PAYLOAD_TAU_BUCKETS):
            cell_rows = [r for r in by_cell[(n, h)]
                         if payload_tau_bucket(r['payload_tau2']) == b]
            if not cell_rows:
                continue
            counts[i, j] = len(cell_rows)
            obs = np.array([r['lambda'] for r in cell_rows])
            p = pred.get((h, nt, b))
            if p is None:
                continue
            matrix[i, j] = float(np.mean(obs - p))

    fig, ax = plt.subplots(figsize=(11, 7))
    vmax = max(float(np.nanmax(np.abs(matrix))), 1e-3)
    im = ax.imshow(matrix, aspect='auto', cmap='PuOr',
                   vmin=-vmax, vmax=vmax)
    ax.set_xticks(range(len(PAYLOAD_TAU_BUCKETS)))
    ax.set_xticklabels(PAYLOAD_TAU_BUCKETS, fontsize=9)
    ax.set_yticks(range(len(cells)))
    ax.set_yticklabels(cell_labels, fontsize=9)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            c = counts[i, j]
            if c > 0:
                ax.text(j, i, f'{c}', ha='center', va='center',
                        fontsize=6, color='gray')
    ax.set_title(
        f'Family-geometry residual: Λ_n(m) − E[Λ_n | (h, n_type, payload τ_2)]\n'
        f'max |residual| = {vmax:.4f}'
    )
    plt.colorbar(im, ax=ax, fraction=0.04)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'family_geometry_residual.png'), dpi=120)
    plt.close(fig)

    # Aggregate magnitude by n_type (the discipline-doc question:
    # how much does the depth-only-style coordinate explain?).
    summary_by_type = defaultdict(list)
    for i, (n, h) in enumerate(cells):
        nt = n_type(n)
        for j in range(len(PAYLOAD_TAU_BUCKETS)):
            v = matrix[i, j]
            if not np.isnan(v):
                summary_by_type[nt].append(abs(v))
    type_summary = {nt: float(np.mean(v)) for nt, v in summary_by_type.items()}

    return {
        'max_residual': vmax,
        'matrix': matrix,
        'counts': counts,
        'cells': cells,
        'pred_buckets': pred_size,
        'mean_abs_residual_by_n_type': type_summary,
    }


# ---- main ----

def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    cutoff_csv = os.path.join(out_dir, 'cutoff_ray_scan.csv')
    payload_csv = os.path.join(out_dir, 'payload_scan.csv')

    summary_lines = ['phase1_destroyers summary',
                     f'K_SHUFFLES = {K_SHUFFLES}, SEED = {SEED}', '']

    print('=== Destroyer 1: Y-shuffle for cutoff dist_n² coherent line ===',
          flush=True)
    cutoff = load_cutoff(cutoff_csv)
    cr = destroyer_cutoff(cutoff, K=K_SHUFFLES, out_dir=out_dir)
    print(f'  actual max |residual|: {cr["max_actual"]:.2e}', flush=True)
    print(f'  null mean max |residual|: {cr["max_null"]:.2e}', flush=True)
    print(f'  max |z|: {cr["max_z"]:.2f}', flush=True)
    print(f'  mean |z| in dist=0 column: {cr["mean_|z|_dist0"]:.2f}', flush=True)
    print(f'  mean |z| in dist=2 column: {cr["mean_|z|_dist2"]:.2f}', flush=True)
    summary_lines.extend([
        f'=== Destroyer 1 — cutoff dist_n² Y-shuffle ===',
        f'  actual max |residual|: {cr["max_actual"]:.2e}',
        f'  null mean max |residual|: {cr["max_null"]:.2e}',
        f'  max |z|: {cr["max_z"]:.2f}',
        f'  mean |z| in dist=0 column: {cr["mean_|z|_dist0"]:.2f}',
        f'  mean |z| in dist=2 column: {cr["mean_|z|_dist2"]:.2f}',
        '',
    ])

    print('\n=== Destroyer 2: m-shuffle for payload ξ graduation ===',
          flush=True)
    payload = load_payload(payload_csv)
    pr = destroyer_payload(payload, K=K_SHUFFLES, out_dir=out_dir)
    summary_lines.append('=== Destroyer 2 — payload ξ m-shuffle ===')
    summary_lines.append(
        f'  {"(n, h)":>10}  {"count":>5}  {"obs ξ":>9}  '
        f'{"null mean":>10}  {"null std":>9}  {"z":>8}'
    )
    for r in pr:
        msg = (f'  n={r["n"]} h={r["h"]}: count={r["count"]}, '
               f'obs ξ = {r["observed_xi"]:+.4f}, '
               f'null = {r["null_mean"]:+.4f} ± {r["null_std"]:.4f}, '
               f'z = {r["z"]:+.1f}')
        print(msg, flush=True)
        summary_lines.append(
            f'  ({r["n"]:>2}, {r["h"]:>2})  {r["count"]:>5}  '
            f'{r["observed_xi"]:>+9.4f}  '
            f'{r["null_mean"]:>+10.4f}  {r["null_std"]:>9.4f}  '
            f'{r["z"]:>+8.1f}'
        )
    summary_lines.append('')

    print('\n=== Subtraction 3: family-geometry residual ===', flush=True)
    fg = family_geometry_residual(payload, out_dir=out_dir)
    print(f'  max |family-geometry residual|: {fg["max_residual"]:.4f}', flush=True)
    print('  mean |residual| by n_type:', flush=True)
    for nt, v in fg['mean_abs_residual_by_n_type'].items():
        print(f'    {nt:>20}: {v:.4f}', flush=True)
    summary_lines.append('=== Subtraction 3 — family-geometry residual ===')
    summary_lines.append(
        f'  max |residual|: {fg["max_residual"]:.4f}'
    )
    summary_lines.append('  mean |residual| by n_type:')
    for nt, v in fg['mean_abs_residual_by_n_type'].items():
        summary_lines.append(f'    {nt:>20}: {v:.4f}')

    summary_path = os.path.join(out_dir, 'phase1_destroyers_summary.txt')
    with open(summary_path, 'w') as f:
        f.write('\n'.join(summary_lines))
        f.write('\n')
    print(f'\nwrote {summary_path}', flush=True)


if __name__ == '__main__':
    main()
