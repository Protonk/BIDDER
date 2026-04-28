"""
cutoff_texture.py — high-resolution texture probe of the cutoff sweep
======================================================================

The cutoff_ray_scan stripe and fold visualizations at coarse color
scale show no structure past saturation (Y ≳ 100). But |ρ − ρ_∞|
decays like 1/log(Y) past saturation, with discrete micro-jumps of
size ≈ 1/(m·q·log q) per new q ∈ M_n entering the In sum. At Y=1000
and m=36 that's ~10^-6 per step — invisible at scales ±0.05.

This script probes texture at the right scale:

  1. Per cell, plot ρ(Y) − ρ_∞ post-saturation on a log-y axis.
     Smooth decay → no texture. Wiggles → spatial structure.
  2. Subtract a smooth fit (1/log Y model) and show the residual.
     Any non-zero structure here is genuine spatial texture.
  3. Per-row variance for the (Y mod n²) × (Y // n²) fold,
     post-saturation. If columns (residue classes) carry signal,
     the row-centered variance pattern reveals it.
  4. Autocorrelation of post-saturation residual at integer lags
     up to a few periods of n², n³, 10, 100. Peaks indicate
     periodic structure.

Loads `cutoff_ray_scan.csv` produced by `cutoff_ray_scan.py`.

Usage:
    sage -python cutoff_texture.py
"""

import csv
import os
from collections import defaultdict
from math import log

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


SAT_THRESHOLD = 200  # Y past which ρ is considered saturated for these probes.


def load_csv(path):
    by_cell = defaultdict(list)
    with open(path) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            n = int(row[0])
            m = int(row[1])
            label = row[2]
            Y = int(row[3])
            rho = float(row[5])
            by_cell[(n, m, label)].append((Y, rho))
    for k in by_cell:
        by_cell[k].sort(key=lambda r: r[0])
    return by_cell


def texture_figure(n, m, label, data, out_dir):
    Ys = np.array([d[0] for d in data])
    rhos = np.array([d[1] for d in data])

    # Asymptote from the last quartile.
    rho_inf = float(np.median(rhos[3 * len(rhos) // 4:]))

    # Post-saturation only.
    mask = Ys >= SAT_THRESHOLD
    Y_sat = Ys[mask]
    err = rhos[mask] - rho_inf

    fig, axes = plt.subplots(4, 1, figsize=(15, 11))

    # Panel 1: |ρ − ρ_∞| on log-log axes. Generic 1/log Y decay if
    # there is no extra structure.
    ax = axes[0]
    pos = err > 0
    neg = err < 0
    ax.scatter(Y_sat[pos], np.log10(err[pos] + 1e-15),
               s=1, c='steelblue', alpha=0.5, label='ρ > ρ_∞')
    ax.scatter(Y_sat[neg], np.log10(-err[neg] + 1e-15),
               s=1, c='crimson', alpha=0.5, label='ρ < ρ_∞')
    ax.set_xscale('log')
    ax.set_xlabel('Y')
    ax.set_ylabel(r'$\log_{10}\, |\rho - \rho_\infty|$')
    ax.set_title(f'n={n}, m={m} — texture probe ({label}); ρ_∞ = {rho_inf:+.6f}')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9, loc='best')

    # Panel 2: residual after a 1/log(Y) fit. Anything non-zero here
    # is texture beyond the smooth Mertens-tail decay.
    log_Y = np.log(Y_sat)
    # Linear regression: err ~ a / log(Y) + b
    inv_log = 1.0 / log_Y
    A = np.vstack([inv_log, np.ones_like(inv_log)]).T
    coef, *_ = np.linalg.lstsq(A, err, rcond=None)
    smooth = A @ coef
    residual = err - smooth

    ax = axes[1]
    ax.plot(Y_sat, residual, lw=0.4, color='black', alpha=0.7)
    ax.axhline(0, color='gray', lw=0.5, ls=':')
    ax.set_xscale('log')
    ax.set_xlabel('Y')
    ax.set_ylabel(r'$(\rho - \rho_\infty)$ minus  $a/\log Y + b$  fit')
    ax.set_title(
        f'fit:  ρ − ρ_∞ ≈ {coef[0]:+.4e}/log(Y) + {coef[1]:+.4e};'
        f'  residual std = {np.std(residual):.2e}'
    )
    ax.grid(True, alpha=0.3)

    # Panel 3: per-residue variance in (Y mod n²) bucket of the
    # post-saturation residual. If columns carry signal, the per-bucket
    # mean differs from zero.
    n2 = n * n
    bucket_means = []
    bucket_stds = []
    bucket_counts = []
    for r in range(n2):
        bm = Y_sat % n2 == r
        if bm.any():
            vals = residual[bm]
            bucket_means.append(np.mean(vals))
            bucket_stds.append(np.std(vals))
            bucket_counts.append(int(bm.sum()))
        else:
            bucket_means.append(np.nan)
            bucket_stds.append(np.nan)
            bucket_counts.append(0)

    ax = axes[2]
    ax.bar(range(n2), bucket_means, yerr=[s / np.sqrt(c) if c > 0 else 0
                                          for s, c in zip(bucket_stds,
                                                          bucket_counts)],
           color='steelblue', alpha=0.7, edgecolor='black')
    ax.axhline(0, color='black', lw=0.5)
    ax.set_xlabel(f'Y mod n² = Y mod {n2}')
    ax.set_ylabel('mean residual')
    bm_max = max(abs(m) for m in bucket_means if not np.isnan(m))
    ax.set_title(
        f'post-saturation residual mean by (Y mod n²); '
        f'max |bucket mean| = {bm_max:.2e}'
    )
    ax.grid(True, alpha=0.3, axis='y')

    # Panel 4: autocorrelation at integer lags 1..max_lag.
    max_lag = min(500, len(residual) // 4)
    # Center residual.
    r_c = residual - residual.mean()
    var = np.var(r_c)
    if var > 0:
        acf = np.array([np.mean(r_c[:-lag] * r_c[lag:]) / var
                        for lag in range(1, max_lag + 1)])
    else:
        acf = np.zeros(max_lag)

    ax = axes[3]
    ax.plot(range(1, max_lag + 1), acf, lw=0.5, color='darkgreen')
    ax.axhline(0, color='black', lw=0.5)
    # Mark n² and n³ periods.
    for k, c in [(n * n, 'red'), (n * n * n, 'blue'), (10, 'purple'), (100, 'orange')]:
        if k <= max_lag:
            ax.axvline(k, color=c, lw=0.5, ls='--', alpha=0.5,
                       label=f'lag={k}')
    ax.set_xlabel('Y lag')
    ax.set_ylabel('residual ACF')
    ax.set_title(f'autocorrelation of post-saturation residual (lag 1..{max_lag})')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8, loc='upper right')

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f'cutoff_texture_{label}.png'), dpi=120)
    plt.close(fig)

    return {
        'rho_inf': rho_inf,
        'fit_a': coef[0],
        'fit_b': coef[1],
        'residual_std': float(np.std(residual)),
        'bucket_mean_max': bm_max,
        'acf_lag_n2': float(acf[n * n - 1]) if n * n - 1 < len(acf) else float('nan'),
        'acf_lag_n3': float(acf[n ** 3 - 1]) if n ** 3 - 1 < len(acf) else float('nan'),
        'acf_lag_10': float(acf[9]) if 9 < len(acf) else float('nan'),
        'acf_lag_100': float(acf[99]) if 99 < len(acf) else float('nan'),
    }


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(out_dir, 'cutoff_ray_scan.csv')

    print(f'loading {csv_path}', flush=True)
    by_cell = load_csv(csv_path)

    summary_lines = [
        f'cutoff_texture summary',
        f'SAT_THRESHOLD = {SAT_THRESHOLD}',
        '',
        f'{"label":>32}  {"ρ_∞":>10}  {"fit a":>10}  {"resid std":>10}  '
        f'{"max|bucket μ|":>14}  {"ACF n²":>9}  {"ACF n³":>9}  '
        f'{"ACF 10":>9}  {"ACF 100":>9}',
    ]
    for (n, m, label), data in by_cell.items():
        print(f'  {label}', flush=True)
        stats = texture_figure(n, m, label, data, out_dir)
        summary_lines.append(
            f'  {label:>32}  {stats["rho_inf"]:>+10.6f}  '
            f'{stats["fit_a"]:>+10.4e}  '
            f'{stats["residual_std"]:>10.2e}  '
            f'{stats["bucket_mean_max"]:>14.2e}  '
            f'{stats["acf_lag_n2"]:>+9.4f}  '
            f'{stats["acf_lag_n3"]:>+9.4f}  '
            f'{stats["acf_lag_10"]:>+9.4f}  '
            f'{stats["acf_lag_100"]:>+9.4f}'
        )

    summary_path = os.path.join(out_dir, 'cutoff_texture_summary.txt')
    with open(summary_path, 'w') as f:
        f.write('\n'.join(summary_lines))
        f.write('\n')
    print(f'wrote {summary_path}', flush=True)


if __name__ == '__main__':
    main()
