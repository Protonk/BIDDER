"""
hardy_q_mertens_validation.py — does Mertens explain the depth shift?
======================================================================

`hardy_q_depth_invariance.py` showed the Hardy r=2 composite-Q
distribution shifts strongly with K-depth. This script tests the
mechanism we suspect: Dirichlet–Mertens.

For prime `n` and `h = 2`, the master expansion gives the exact identity

    Q_n(m) = 1 - d(k) / 2,    k = m / n^2,   gcd(k, n) = 1.

So `d(k) = 2 (1 - Q)` is recoverable directly from Q. By the
Dirichlet–Mertens summatory result,

    (1/N) Σ_{j ≤ N} d(j) = log N + (2γ - 1) + O(N^{-1/2}),

so for k drawn at typical magnitude `M` we expect

    E[d(k)] ≈ log M + (2γ - 1)         (natural log on the right).

This script samples 12 log-spaced K-bins covering 10^1 ≤ K < 10^13,
computes the empirical `E[d(k)]` and `E[log m]` per (n, bin), and
overlays the Dirichlet line. If the empirical curve traces the
prediction across nine decades of K, the depth shift is Mertens —
not a Hardy artifact.

Composite `n` (here `n ∈ {4, 6}`) is included as a reference: the
direct identity `Q = 1 - d(k)/2` requires t = 0 overlap there, but
the same depth drift appears qualitatively.

Outputs (this directory):
  hardy_q_mertens_validation.csv            per-row records
  hardy_q_mertens_validation_summary.txt    per-(n, bin) statistics + slope fit
  hardy_q_mertens_main.png                  E[d(k)] vs log10(m) with Mertens line
  hardy_q_mertens_dk_distributions.png      d(k) distributions across depth, n=2

Usage:
    sage -python hardy_q_mertens_validation.py
"""

import csv
import os
import sys
from collections import defaultdict
from math import log, log10

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))

sys.path.insert(0, HERE)
from hardy_echo import nth_n_prime  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, 'experiments', 'acm-flow'))
from hardy_composite_q import (  # noqa: E402
    factor_dict, factor_small, mul_facs, height_n, q_master,
    integer_from_facs, divide_n_power, tau_j,
)


EULER_GAMMA = 0.5772156649015329

PRIME_NS = [2, 3, 5]
COMPOSITE_NS = [4, 6]
ALL_NS = PRIME_NS + COMPOSITE_NS

DEPTH_BINS = [(10**a, 10**(a + 1)) for a in range(1, 13)]
N_PER_BIN = 1000
SEED = 20260428002


# ---- sampling ----

def sample_K_pair(rng, lo, hi):
    while True:
        K1 = int(rng.integers(lo, hi))
        K2 = int(rng.integers(lo, hi))
        if K1 != K2:
            return (K1, K2) if K1 < K2 else (K2, K1)


def evaluate(n, n_facs, K_pair):
    a1 = nth_n_prime(n, K_pair[0])
    a2 = nth_n_prime(n, K_pair[1])
    a1_facs = mul_facs(n_facs, factor_dict(a1 // n))
    a2_facs = mul_facs(n_facs, factor_dict(a2 // n))
    m_facs = mul_facs(a1_facs, a2_facs)
    h = height_n(m_facs, n_facs)
    Q = q_master(m_facs, n_facs, h)
    k_facs = divide_n_power(m_facs, n_facs, h)
    d_k = tau_j(2, k_facs)
    m_int = integer_from_facs(m_facs)
    return {
        'h': h,
        'q_float': float(Q),
        'd_k': d_k,
        'log10_m': log10(m_int),
        'm_digits': len(str(m_int)),
    }


def run_panel():
    rng = np.random.default_rng(SEED)
    rows = []
    for n in ALL_NS:
        n_facs = factor_small(n)
        print(f'  n = {n}', flush=True)
        for bin_idx, (lo, hi) in enumerate(DEPTH_BINS):
            print(f'    bin {bin_idx:>2}: K ∈ [10^{int(log10(lo))}, '
                  f'10^{int(log10(hi))})', flush=True)
            for _ in range(N_PER_BIN):
                K_pair = sample_K_pair(rng, lo, hi)
                ev = evaluate(n, n_facs, K_pair)
                ev.update({
                    'n': n,
                    'bin_idx': bin_idx,
                    'K_lo': lo, 'K_hi': hi,
                    'K_1': K_pair[0], 'K_2': K_pair[1],
                })
                rows.append(ev)
    return rows


# ---- per-cell statistics, restricted to h = 2 ----

def cell_stats(rows):
    """For each (n, bin_idx) cell, compute h=2 statistics."""
    cell = defaultdict(list)
    for r in rows:
        if r['h'] == 2:
            cell[(r['n'], r['bin_idx'])].append(r)

    stats = []
    for (n, b), rs in sorted(cell.items()):
        log10_m = np.array([r['log10_m'] for r in rs])
        d_k = np.array([r['d_k'] for r in rs], dtype=float)
        q = np.array([r['q_float'] for r in rs])
        stats.append({
            'n': n,
            'bin_idx': b,
            'count': len(rs),
            'log10_m_mean': float(log10_m.mean()),
            'log10_m_std': float(log10_m.std()),
            'd_k_mean': float(d_k.mean()),
            'd_k_std': float(d_k.std()),
            'q_mean': float(q.mean()),
            'q_std': float(q.std()),
        })
    return stats


# ---- Mertens prediction & slope fit ----

def mertens_prediction(log10_m_values, n):
    """Predicted E[d(k)] = ln(k) + (2γ - 1) for k = m / n^2.

    Args in log10(m); returns vector of predicted d_k values."""
    log10_k = np.asarray(log10_m_values) - 2.0 * log10(n)
    return np.log(10) * log10_k + (2 * EULER_GAMMA - 1)


def slope_fit(stats, ns):
    """Per n, OLS fit E[d(k)] vs E[log10(m)] over h=2 stats. Returns dict
    n -> (slope, intercept, R²)."""
    out = {}
    for n in ns:
        xs = np.array([s['log10_m_mean'] for s in stats if s['n'] == n])
        ys = np.array([s['d_k_mean'] for s in stats if s['n'] == n])
        if len(xs) < 2:
            continue
        slope, intercept = np.polyfit(xs, ys, 1)
        ys_pred = slope * xs + intercept
        ss_res = float(np.sum((ys - ys_pred) ** 2))
        ss_tot = float(np.sum((ys - ys.mean()) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float('nan')
        out[n] = {'slope': float(slope), 'intercept': float(intercept), 'r2': r2}
    return out


# ---- writers ----

def write_csv(rows, path):
    fields = ['n', 'bin_idx', 'K_lo', 'K_hi', 'K_1', 'K_2',
              'h', 'q_float', 'd_k', 'log10_m', 'm_digits']
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in fields})


def write_summary(stats, fits, path):
    target_slope = log(10)  # ≈ 2.302585; Mertens slope for log10 axis.
    target_intercept = lambda n: 2 * EULER_GAMMA - 1 - 2 * log(10) * log10(n)

    with open(path, 'w') as f:
        f.write('hardy_q_mertens_validation.py — Mertens slope across depth\n\n')
        f.write(f'panel n: {ALL_NS}\n')
        f.write(f'depth bins: {len(DEPTH_BINS)} single-decade bins '
                f'over K ∈ [10^1, 10^13)\n')
        f.write(f'N per (n, bin): {N_PER_BIN}\n')
        f.write(f'restricted to h = 2\n')
        f.write(f'seed: {SEED}\n\n')

        f.write('=== Per (n, bin) h=2 cell statistics ===\n')
        f.write(f'  {"n":>3} {"bin":>4} {"count":>6} '
                f'{"<log10 m>":>10} {"<d(k)>":>9} {"<Q>":>10} '
                f'{"σ(d_k)":>9}\n')
        for s in stats:
            f.write(
                f'  {s["n"]:>3} {s["bin_idx"]:>4} {s["count"]:>6} '
                f'{s["log10_m_mean"]:>10.3f} {s["d_k_mean"]:>9.3f} '
                f'{s["q_mean"]:>10.3f} {s["d_k_std"]:>9.3f}\n'
            )
        f.write('\n')

        f.write('=== Mertens slope fit: E[d(k)] = slope · E[log10 m] + intercept ===\n')
        f.write(f'  Mertens prediction (k = m/n²): slope = ln(10) ≈ '
                f'{log(10):.4f}\n\n')
        f.write(f'  {"n":>3} {"slope":>9} {"intercept":>11} '
                f'{"R²":>7}    {"target int.":>13} {"slope/target":>13}\n')
        for n, fit in sorted(fits.items()):
            ti = target_intercept(n)
            f.write(
                f'  {n:>3} {fit["slope"]:>9.4f} {fit["intercept"]:>11.4f} '
                f'{fit["r2"]:>7.4f}    {ti:>13.4f} '
                f'{fit["slope"] / target_slope:>13.4f}\n'
            )
        f.write('\n')

        # Verdict heuristic.
        prime_slopes = [fits[n]['slope'] for n in PRIME_NS if n in fits]
        if prime_slopes:
            avg_p_slope = np.mean(prime_slopes)
            ratio = avg_p_slope / target_slope
            f.write('=== Verdict ===\n')
            f.write(f'mean prime-n slope / Mertens target = {ratio:.4f}\n')
            if 0.85 < ratio < 1.15:
                f.write('PASS — empirical slope agrees with Dirichlet–Mertens '
                        'within 15%. Depth shift is Mertens.\n')
            else:
                f.write('NOTE — slope deviates from Mertens prediction. The '
                        'depth shift is real but its rate is not the simple '
                        'k-uniform Dirichlet rate; cofactor-multiplicativity '
                        'or another mechanism is in play.\n')


# ---- plots ----

def plot_main(stats, fits, path):
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # ---- (a) E[d(k)] vs E[log10 m] with Mertens overlay ----
    ax = axes[0]
    color_prime = plt.cm.cool(np.linspace(0.1, 0.85, len(PRIME_NS)))
    color_comp = plt.cm.autumn(np.linspace(0.1, 0.6, len(COMPOSITE_NS)))
    n_to_color = {**dict(zip(PRIME_NS, color_prime)),
                  **dict(zip(COMPOSITE_NS, color_comp))}

    for n in ALL_NS:
        xs = [s['log10_m_mean'] for s in stats if s['n'] == n]
        ys = [s['d_k_mean'] for s in stats if s['n'] == n]
        yerr = [s['d_k_std'] / max(s['count'], 1) ** 0.5
                for s in stats if s['n'] == n]
        is_prime = n in PRIME_NS
        marker = 'o' if is_prime else 's'
        ax.errorbar(xs, ys, yerr=yerr, fmt=marker, color=n_to_color[n],
                    label=f'n = {n} ({"prime" if is_prime else "comp."})',
                    capsize=3, markersize=6, linestyle='-', linewidth=1.4)

    # Mertens line for n=2 (k = m/4): y = ln(10) · (log10 m - 2 log10 2) + 2γ - 1.
    all_x = [s['log10_m_mean'] for s in stats]
    if all_x:
        x_grid = np.linspace(min(all_x) - 0.5, max(all_x) + 0.5, 200)
        for n in PRIME_NS:
            y_pred = mertens_prediction(x_grid, n)
            ax.plot(x_grid, y_pred, color=n_to_color[n], linestyle='--',
                    linewidth=1.0, alpha=0.7)

    ax.set_xlabel('E[log10 m] per (n, K-bin)')
    ax.set_ylabel('E[d(k)] per (n, K-bin)   (k = m / n²)')
    ax.set_title(
        'Mertens validation: E[d(k)] ≈ ln(k) + (2γ − 1)\n'
        'dashed = Dirichlet prediction per prime n; markers = empirical'
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=9)

    # ---- (b) E[Q] vs E[log10 m], all n ----
    ax = axes[1]
    for n in ALL_NS:
        xs = [s['log10_m_mean'] for s in stats if s['n'] == n]
        ys = [s['q_mean'] for s in stats if s['n'] == n]
        is_prime = n in PRIME_NS
        marker = 'o' if is_prime else 's'
        ax.plot(xs, ys, marker=marker, color=n_to_color[n],
                label=f'n = {n}', linewidth=1.4)

    # Mertens prediction for E[Q] = 1 - E[d(k)]/2 (prime n only).
    if all_x:
        for n in PRIME_NS:
            y_pred_dk = mertens_prediction(x_grid, n)
            y_pred_q = 1 - y_pred_dk / 2
            ax.plot(x_grid, y_pred_q, color=n_to_color[n], linestyle='--',
                    linewidth=1.0, alpha=0.7)

    ax.set_xlabel('E[log10 m] per (n, K-bin)')
    ax.set_ylabel('E[Q | h=2] per (n, K-bin)')
    ax.set_title(
        'Companion: E[Q] = 1 − E[d(k)]/2 for prime n\n'
        'depth shift is the Mertens slope, written in Q'
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=9)

    fig.suptitle(
        f'Hardy r=2 composite-Q  —  Mertens slope across {len(DEPTH_BINS)} '
        f'K-bins, n ∈ {ALL_NS}, N={N_PER_BIN}/bin (h=2 only)'
    )
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close(fig)


def plot_dk_distributions(rows, path, n_target=2):
    bins_to_show = [0, 5, 11]  # K ∈ [10^1,10^2), [10^6,10^7), [10^12,10^13)
    cell = defaultdict(list)
    for r in rows:
        if r['n'] == n_target and r['h'] == 2:
            cell[r['bin_idx']].append(r['d_k'])

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = plt.cm.viridis(np.linspace(0.15, 0.85, len(bins_to_show)))
    for color, b in zip(colors, bins_to_show):
        d_ks = np.array(cell.get(b, []))
        if len(d_ks) == 0:
            continue
        lo, hi = DEPTH_BINS[b]
        label = (f'K∈[10^{int(log10(lo))}, 10^{int(log10(hi))}):  '
                 f'<d(k)>={d_ks.mean():.1f}, σ={d_ks.std():.1f}, n={len(d_ks)}')
        # Log-spaced bins because d(k) is heavy-tailed.
        max_d = int(np.percentile(d_ks, 99))
        if max_d < 4:
            max_d = 4
        bin_edges = np.logspace(0, np.log10(max_d + 1), 41)
        ax.hist(d_ks, bins=bin_edges, alpha=0.5, color=color,
                label=label, edgecolor=color, density=True)

    ax.set_xscale('log')
    ax.set_xlabel('d(k)   (log scale)')
    ax.set_ylabel('density')
    ax.set_title(
        f'Cofactor-product divisor count d(k) at three K-depths, n = {n_target}\n'
        'right-shifting density is the Mertens drift; matched on log axis'
    )
    ax.grid(True, alpha=0.3, which='both')
    ax.legend(loc='best', fontsize=9)
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close(fig)


# ---- main ----

def main():
    print('hardy_q_mertens_validation.py — does Mertens explain it?\n', flush=True)
    print(f'panel n:        {ALL_NS}', flush=True)
    print(f'depth bins:     {len(DEPTH_BINS)} (single-decade, K ∈ [10^1, 10^13))',
          flush=True)
    print(f'N per (n, bin): {N_PER_BIN}', flush=True)
    print(f'seed:           {SEED}\n', flush=True)

    print('sampling and computing Q ...', flush=True)
    rows = run_panel()
    print(f'\n  total rows: {len(rows)}\n', flush=True)

    stats = cell_stats(rows)
    fits = slope_fit(stats, ALL_NS)
    print('per-prime-n slope vs Mertens target:', flush=True)
    target = log(10)
    for n in PRIME_NS:
        if n in fits:
            f = fits[n]
            print(f'  n = {n}: slope = {f["slope"]:.4f}  '
                  f'(target = {target:.4f}, ratio = {f["slope"]/target:.4f}, '
                  f'R² = {f["r2"]:.4f})', flush=True)
    print('', flush=True)

    csv_path = os.path.join(HERE, 'hardy_q_mertens_validation.csv')
    summary_path = os.path.join(HERE, 'hardy_q_mertens_validation_summary.txt')
    main_plot_path = os.path.join(HERE, 'hardy_q_mertens_main.png')
    dk_plot_path = os.path.join(HERE, 'hardy_q_mertens_dk_distributions.png')

    write_csv(rows, csv_path)
    write_summary(stats, fits, summary_path)
    plot_main(stats, fits, main_plot_path)
    plot_dk_distributions(rows, dk_plot_path)

    print(f'wrote {csv_path}', flush=True)
    print(f'wrote {summary_path}', flush=True)
    print(f'wrote {main_plot_path}', flush=True)
    print(f'wrote {dk_plot_path}', flush=True)


if __name__ == '__main__':
    main()
