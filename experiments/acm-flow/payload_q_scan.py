"""
payload_q_scan.py — payload scan with Q_n = Λ_n / log(m) as observable
=======================================================================

Per Phase 1 finding (`PHASE1-RESULTS.md`, family-geometry subtraction):
the closed form gives `Λ_n(m) = log(m) · Q_n(m)` where

    Q_n(m) = Σ_{j ≥ 1, n^j | m} (-1)^(j-1) τ_j(m/n^j) / j

is an exact rational divisor-sum residual. The structure lives in
`Q_n`; `log(m)` is just scale. Switching to Q_n as the local
observable removes the log(n) cross-n bias that inflated the
family-geometry residual at extreme buckets.

Pushes the panel to h ∈ {2, 3, 4, 5} as the web-agent next-move
prescribed: do prime / prime_power / multi_prime have an explicit
divisor-function formula at each h? Q_n is the natural quantity
to read those off.

Outputs (this directory):
  payload_q_scan.csv             per (n, h, m) row with exact Q numerator+denominator
  payload_q_summary.txt          per cell bucket stats + ξ + m-shuffle null
  payload_q_matrix.png           (n, h) × payload τ_2 heatmaps for Q_n raw,
                                 row-mean subtracted, and family-geometry-residual.
  payload_q_destroyer.png        observed ξ vs m-shuffle null per (n, h)

Methods declared against ACM-MANGOLDT.md statistical-method-discipline:
  - Q_n stored exactly (Fraction); float used only for output and stats.
  - ξ(payload τ_2 → Q_n) with K=32 random jitter tie-breaks; m-shuffle
    null at K=100 with K=8 inner ξ-tie-breaks per shuffle.
  - bucket statistics: count, mean, median, sign-fraction.

Usage:
    sage -python payload_q_scan.py
"""

import csv
import os
from collections import defaultdict
from fractions import Fraction
from math import isqrt, log

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


PANEL_NS = [2, 3, 4, 5, 6, 10]
PANEL_HS = [2, 3, 4, 5]
M_MAX = 50000

TIE_K = 32
TIE_BASE_SEED = 42
SHUFFLE_K = 100
EPS = 1e-12

PAYLOAD_TAU_BUCKETS = ['1', '2', '3', '4-5', '6-8', '9-16', '17+']


# ---- arithmetic ----

def tau_table(mmax, j_max):
    tau = [[0] * (mmax + 1) for _ in range(j_max)]
    for k in range(1, mmax + 1):
        tau[0][k] = 1
    for jx in range(1, j_max):
        prev = tau[jx - 1]
        cur = tau[jx]
        for d in range(1, mmax + 1):
            v = prev[d]
            if v == 0:
                continue
            for k in range(d, mmax + 1, d):
                cur[k] += v
    return tau


def q_value(n, m, tau):
    """Exact Q_n(m) as Fraction. Λ_n(m) = log(m) · Q_n(m)."""
    j_max = len(tau)
    Q = Fraction(0)
    nj = 1
    for jx in range(1, j_max + 1):
        nj *= n
        if m % nj != 0:
            break
        mj = m // nj
        sgn = 1 if (jx % 2) == 1 else -1
        Q += Fraction(sgn * tau[jx - 1][mj], jx)
    return Q


def divisor_count(k):
    if k <= 0:
        return 0
    if k == 1:
        return 1
    d = 0
    root = isqrt(k)
    for i in range(1, root + 1):
        if k % i == 0:
            d += 2 if i != k // i else 1
    return d


def n_type(n):
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


def payload_tau_bucket(t):
    if t == 1: return '1'
    if t == 2: return '2'
    if t == 3: return '3'
    if t <= 5: return '4-5'
    if t <= 8: return '6-8'
    if t <= 16: return '9-16'
    return '17+'


# ---- ξ ----

def chatterjee_xi_single(x, y):
    n = len(x)
    if n < 2:
        return 0.0
    order = np.argsort(x)
    y_perm = y[order]
    ranks = np.argsort(np.argsort(y_perm)) + 1
    return 1.0 - 3.0 * np.sum(np.abs(np.diff(ranks))) / (n * n - 1)


def chatterjee_xi_with_ties(x, y, K=TIE_K, base_seed=TIE_BASE_SEED):
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


# ---- panel sweep ----

def cell_sweep(n, h, M_max, tau):
    n_h = n ** h
    rows = []
    k = 1
    while True:
        m = n_h * k
        if m > M_max:
            break
        if k % n != 0:
            payload = m // n_h
            ptau2 = divisor_count(payload)
            Q = q_value(n, m, tau)
            rows.append({
                'n': n, 'h': h, 'm': m, 'k': k,
                'payload': payload, 'payload_tau2': ptau2,
                'Q': Q, 'Q_float': float(Q),
            })
        k += 1
    return rows


# ---- family-geometry residual ----

def family_geometry_residual(rows):
    pool = defaultdict(list)
    for r in rows:
        nt = n_type(r['n'])
        b = payload_tau_bucket(r['payload_tau2'])
        pool[(r['h'], nt, b)].append(r['Q_float'])
    pred = {k: float(np.mean(v)) for k, v in pool.items()}

    cells = sorted({(r['n'], r['h']) for r in rows})
    matrix = np.full((len(cells), len(PAYLOAD_TAU_BUCKETS)), np.nan)
    counts = np.zeros((len(cells), len(PAYLOAD_TAU_BUCKETS)), dtype=int)
    for i, (n, h) in enumerate(cells):
        nt = n_type(n)
        for j, b in enumerate(PAYLOAD_TAU_BUCKETS):
            cell_rows = [
                r for r in rows
                if r['n'] == n and r['h'] == h and payload_tau_bucket(r['payload_tau2']) == b
            ]
            if not cell_rows:
                continue
            counts[i, j] = len(cell_rows)
            obs = np.array([r['Q_float'] for r in cell_rows])
            p = pred.get((h, nt, b))
            if p is None:
                continue
            matrix[i, j] = float(np.mean(obs - p))
    return cells, matrix, counts


# ---- aggregate matrices ----

def build_matrices(rows):
    cells = sorted({(r['n'], r['h']) for r in rows})
    grid_rho = np.full((len(cells), len(PAYLOAD_TAU_BUCKETS)), np.nan)
    grid_count = np.zeros((len(cells), len(PAYLOAD_TAU_BUCKETS)), dtype=int)
    for r in rows:
        i = cells.index((r['n'], r['h']))
        j = PAYLOAD_TAU_BUCKETS.index(payload_tau_bucket(r['payload_tau2']))
        if not np.isfinite(grid_rho[i, j]):
            grid_rho[i, j] = 0
        grid_count[i, j] += 1
    # Compute means properly.
    sum_q = defaultdict(float)
    cnt = defaultdict(int)
    for r in rows:
        i = cells.index((r['n'], r['h']))
        j = PAYLOAD_TAU_BUCKETS.index(payload_tau_bucket(r['payload_tau2']))
        sum_q[(i, j)] += r['Q_float']
        cnt[(i, j)] += 1
    grid_mean = np.full((len(cells), len(PAYLOAD_TAU_BUCKETS)), np.nan)
    for (i, j), s in sum_q.items():
        grid_mean[i, j] = s / cnt[(i, j)]
    return cells, grid_mean, grid_count


def row_mean_subtract(matrix):
    out = np.full_like(matrix, np.nan)
    for i in range(matrix.shape[0]):
        rm = float(np.nanmean(matrix[i]))
        if not np.isnan(rm):
            out[i] = matrix[i] - rm
    return out


# ---- plotting ----

def plot_matrix_panels(cells, raw, residual, family_resid, counts, out_path):
    cell_labels = [f'n={n} h={h} ({n_type(n)})' for (n, h) in cells]

    fig, axes = plt.subplots(1, 3, figsize=(18, 0.4 * len(cells) + 4))

    vmax_raw = max(float(np.nanmax(np.abs(raw))), 1e-3)
    im = axes[0].imshow(raw, aspect='auto', cmap='RdBu_r',
                        vmin=-vmax_raw, vmax=vmax_raw)
    axes[0].set_xticks(range(len(PAYLOAD_TAU_BUCKETS)))
    axes[0].set_xticklabels(PAYLOAD_TAU_BUCKETS, fontsize=9)
    axes[0].set_yticks(range(len(cell_labels)))
    axes[0].set_yticklabels(cell_labels, fontsize=8)
    axes[0].set_title(f'mean Q_n  (raw); max |Q| = {vmax_raw:.3f}')
    for i in range(raw.shape[0]):
        for j in range(raw.shape[1]):
            c = counts[i, j]
            if c > 0:
                axes[0].text(j, i, f'{c}', ha='center', va='center',
                             fontsize=6, color='gray')
    plt.colorbar(im, ax=axes[0], fraction=0.04)

    vmax_res = max(float(np.nanmax(np.abs(residual))), 1e-3)
    im = axes[1].imshow(residual, aspect='auto', cmap='PuOr',
                        vmin=-vmax_res, vmax=vmax_res)
    axes[1].set_xticks(range(len(PAYLOAD_TAU_BUCKETS)))
    axes[1].set_xticklabels(PAYLOAD_TAU_BUCKETS, fontsize=9)
    axes[1].set_yticks(range(len(cell_labels)))
    axes[1].set_yticklabels(cell_labels, fontsize=8)
    axes[1].set_title(f'mean Q_n − row mean; max = {vmax_res:.3f}')
    plt.colorbar(im, ax=axes[1], fraction=0.04)

    vmax_fg = max(float(np.nanmax(np.abs(family_resid))), 1e-3)
    im = axes[2].imshow(family_resid, aspect='auto', cmap='PuOr',
                        vmin=-vmax_fg, vmax=vmax_fg)
    axes[2].set_xticks(range(len(PAYLOAD_TAU_BUCKETS)))
    axes[2].set_xticklabels(PAYLOAD_TAU_BUCKETS, fontsize=9)
    axes[2].set_yticks(range(len(cell_labels)))
    axes[2].set_yticklabels(cell_labels, fontsize=8)
    axes[2].set_title(
        f'Q_n − E[Q | (h, n_type, payload τ_2)]; max = {vmax_fg:.3f}'
    )
    plt.colorbar(im, ax=axes[2], fraction=0.04)

    fig.suptitle(f'PAYLOAD-Q matrix (M_MAX={M_MAX})')
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close(fig)


def plot_destroyer(results, out_path):
    cell_labels = [f'n={r["n"]} h={r["h"]}' for r in results]
    obs_vals = [r['observed_xi'] for r in results]
    null_means = [r['null_mean'] for r in results]
    null_stds = [r['null_std'] for r in results]

    fig, ax = plt.subplots(figsize=(15, 6))
    x_pos = np.arange(len(results))
    width = 0.35
    ax.bar(x_pos - width / 2, obs_vals, width, label='observed ξ',
           color='steelblue', alpha=0.85)
    ax.errorbar(x_pos + width / 2, null_means, yerr=null_stds, fmt='o',
                color='crimson', label=f'null ξ mean ± std (K={SHUFFLE_K})',
                capsize=4)
    for x, r in zip(x_pos, results):
        z_text = f'z={r["z"]:+.0f}' if abs(r['z']) < 1e6 else 'z=∞'
        ax.text(x - width / 2, r['observed_xi'] + 0.02, z_text,
                ha='center', fontsize=7, rotation=90)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(cell_labels, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('ξ(payload τ_2 → Q_n)')
    ax.set_title('PAYLOAD-Q destroyer — m-shuffle null for ξ graduation, h ∈ {2,3,4,5}')
    ax.axhline(0, color='black', lw=0.5)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close(fig)


# ---- main ----

def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))

    j_max = 1
    while 2 ** j_max <= M_MAX:
        j_max += 1
    print(f'pre-computing τ_j for j ≤ {j_max}, k ≤ {M_MAX}', flush=True)
    tau = tau_table(M_MAX, j_max)
    print(f'  done; max τ_{j_max} = {max(tau[j_max - 1])}', flush=True)

    # Smoke check on Q.
    expected_q_36_n2 = Fraction(-1, 2)
    actual = q_value(2, 36, tau)
    if actual != expected_q_36_n2:
        raise SystemExit(f'[smoke] FAIL Q_2(36) = {actual}, expected {expected_q_36_n2}')
    print(f'[smoke] Q_2(36) = {actual} == -1/2 OK\n', flush=True)

    all_rows = []
    csv_rows = [(
        'n', 'h', 'm', 'k', 'payload', 'payload_tau2',
        'Q_num', 'Q_den', 'Q_float'
    )]
    for n in PANEL_NS:
        for h in PANEL_HS:
            print(f'--- panel cell: n={n}, h={h} ---', flush=True)
            rows = cell_sweep(n, h, M_MAX, tau)
            all_rows.extend(rows)
            print(f'  swept {len(rows)} m values', flush=True)
            for r in rows:
                csv_rows.append((
                    r['n'], r['h'], r['m'], r['k'],
                    r['payload'], r['payload_tau2'],
                    r['Q'].numerator, r['Q'].denominator,
                    f'{r["Q_float"]:+.10f}',
                ))

    # Heatmap matrices.
    cells, raw, counts = build_matrices(all_rows)
    residual = row_mean_subtract(raw)
    fg_cells, fg_resid, fg_counts = family_geometry_residual(all_rows)
    assert cells == fg_cells

    plot_matrix_panels(
        cells, raw, residual, fg_resid, counts,
        os.path.join(out_dir, 'payload_q_matrix.png')
    )

    # ξ + m-shuffle destroyer per (n, h).
    rng = np.random.default_rng(TIE_BASE_SEED)
    destroyer_results = []
    for (n, h) in cells:
        cell_rows = [r for r in all_rows if r['n'] == n and r['h'] == h]
        if len(cell_rows) < 5:
            continue
        ptau2 = np.array([r['payload_tau2'] for r in cell_rows], dtype=float)
        q = np.array([r['Q_float'] for r in cell_rows], dtype=float)

        obs = chatterjee_xi_with_ties(ptau2, q, K=TIE_K, base_seed=TIE_BASE_SEED)
        null_xis = np.empty(SHUFFLE_K)
        for i in range(SHUFFLE_K):
            shuffled = rng.permutation(q)
            null_xis[i] = chatterjee_xi_with_ties(
                ptau2, shuffled, K=8, base_seed=TIE_BASE_SEED + i + 1
            )
        null_mean = float(np.mean(null_xis))
        null_std = float(np.std(null_xis))
        z = (obs - null_mean) / null_std if null_std > 0 else float('inf')
        destroyer_results.append({
            'n': n, 'h': h, 'count': len(cell_rows),
            'observed_xi': obs,
            'null_mean': null_mean,
            'null_std': null_std,
            'z': z,
        })

    plot_destroyer(destroyer_results,
                   os.path.join(out_dir, 'payload_q_destroyer.png'))

    # Outputs.
    csv_path = os.path.join(out_dir, 'payload_q_scan.csv')
    with open(csv_path, 'w', newline='') as f:
        csv.writer(f).writerows(csv_rows)
    print(f'\nwrote {csv_path}  ({len(csv_rows) - 1} rows)', flush=True)

    summary_path = os.path.join(out_dir, 'payload_q_summary.txt')
    with open(summary_path, 'w') as f:
        f.write(f'payload_q_scan summary (M_MAX={M_MAX})\n')
        f.write(f'observable: Q_n(m) = Λ_n(m) / log(m)  (exact rational)\n\n')

        f.write('=== Per-cell ξ destroyer ===\n')
        f.write(f'  {"(n, h)":>10}  {"count":>5}  {"obs ξ":>9}  '
                f'{"null mean":>10}  {"null std":>9}  {"z":>8}\n')
        for r in destroyer_results:
            f.write(
                f'  ({r["n"]:>2}, {r["h"]:>2})  {r["count"]:>5}  '
                f'{r["observed_xi"]:>+9.4f}  '
                f'{r["null_mean"]:>+10.4f}  {r["null_std"]:>9.4f}  '
                f'{r["z"]:>+8.1f}\n'
            )
        f.write('\n')

        f.write('=== Family-geometry residual on Q_n ===\n')
        f.write(f'  {"cell":>20}  {"n_type":>15}  {"max |residual|":>16}\n')
        for i, (n, h) in enumerate(cells):
            row = fg_resid[i]
            mx = float(np.nanmax(np.abs(row))) if np.isfinite(row).any() else 0.0
            f.write(f'  n={n} h={h:>2}{"":>10}  {n_type(n):>15}  {mx:>16.4f}\n')

        f.write('\n  Mean |residual| by n_type:\n')
        by_type = defaultdict(list)
        for i, (n, h) in enumerate(cells):
            for j in range(len(PAYLOAD_TAU_BUCKETS)):
                v = fg_resid[i, j]
                if not np.isnan(v):
                    by_type[n_type(n)].append(abs(v))
        for nt, vs in by_type.items():
            f.write(f'    {nt:>20}: {float(np.mean(vs)):.4f}\n')
    print(f'wrote {summary_path}', flush=True)


if __name__ == '__main__':
    main()
