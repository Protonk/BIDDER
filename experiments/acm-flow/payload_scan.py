"""
payload_scan.py — controlled scan of the local coordinate
==========================================================

Phase 1 of STRUCTURE-HUNT.md, dual to CUTOFF-SCAN. Brief:
PAYLOAD-SCAN.md.

The cutoff coordinate fell in `cutoff_ray_scan.py`: ρ(n, m, Y) is
essentially flat in Y past saturation (Y ≈ 100). The Y-bucket
targeting in PAYLOAD-SCAN.md was therefore unnecessary; we fix
Y_target large enough to be saturated and vary m across payload
buckets at h ∈ {2, 3}.

Tests at fixed (n, h):
  - h=2 cliff (smoke check): τ_2(m/n²) ≤ 2 ⇒ Λ_n ≥ 0;
    τ_2(m/n²) ≥ 3 ⇒ Λ_n < 0. Closed-form identity.
  - h=3 U-shape: payload τ_2 ≤ 4 negative-heavy, [5, 16] positive-
    dominated, ≥ 17 re-negative.
  - prime-n vs composite-n split at matched payload τ_2.

Method choices declared against ACM-MANGOLDT.md statistical-method-
discipline:
  - Chatterjee ξ(payload τ_2, ρ) and ξ(payload τ_2, Λ_n) with
    K=32 random jitter tie-breaks; report ξ_mean and ξ_range.
  - bucket statistics: count, mean, median, sign-fraction of ρ,
    sign-fraction of Λ_n, neg_mass/abs_mass for Λ_n.
  - shape testing: descriptive only at this stage; the U-shape is
    read off the bucket sign-fraction progression.

Outputs (this directory):
  payload_scan.csv             per (n, m, h) row
  payload_scan_summary.txt     per panel cell, bucket stats + ξ
  payload_scan_{n}_{h}.png     per panel cell, ρ and sign(Λ_n)
                                vs payload τ_2

Usage:
    sage -python payload_scan.py
"""

import csv
import os
import sys
from collections import defaultdict
from fractions import Fraction
from math import isqrt, log

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


# Panel of (n, h) cells.
PANEL = [
    (2, 2), (2, 3),
    (3, 2), (3, 3),
    (4, 2), (4, 3),
    (5, 2), (5, 3),
    (6, 2), (6, 3),
]

Y_TARGET = 1000     # saturated; cutoff sweep showed saturation by Y ≈ 100
M_MAX = 20000

TIE_K = 32
TIE_BASE_SEED = 42

EPS = 1e-12

TAU_BUCKET_ORDER = ['1', '2', '3', '4-5', '6-8', '9-16', '17+']


# ---------- Λ_n closed form (shared with cutoff scan) ----------

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


def acm_mangoldt(n, X, tau):
    j_max = len(tau)
    lam = {1: 0.0}
    for m in range(n, X + 1, n):
        Q = Fraction(0)
        nj = 1
        for jx in range(1, j_max + 1):
            nj *= n
            if m % nj != 0:
                break
            mj = m // nj
            sgn = 1 if (jx % 2) == 1 else -1
            Q += Fraction(sgn * tau[jx - 1][mj], jx)
        lam[m] = log(m) * float(Q)
    return lam


def n_height(n, m):
    h = 0
    while m % n == 0:
        h += 1
        m //= n
    return h


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


def payload_tau_bucket(t):
    if t == 1: return '1'
    if t == 2: return '2'
    if t == 3: return '3'
    if t <= 5: return '4-5'
    if t <= 8: return '6-8'
    if t <= 16: return '9-16'
    return '17+'


# ---------- ρ at saturation ----------

def rho_saturated(n, m, Y_target, lam):
    """Compute ρ_n(m; m·Y_target) with Y_target large enough to be saturated."""
    log_m = log(m)
    Out_m = 1.0 / (m * log_m)
    In_m = 0.0
    # Sum over q ∈ M_n with q ≤ Y_target. q = 1 contributes 0.
    for q in range(n, Y_target + 1, n):
        lam_q = lam.get(q, 0.0)
        if lam_q != 0.0:
            mq = m * q
            log_mq = log(mq)
            In_m += lam_q / (mq * log_mq * log_mq)
    X = m * Y_target
    log_X = log(X)
    Delta = In_m - Out_m
    DeltaP = Delta + 1.0 / (m * log_X)
    return DeltaP / Out_m, Out_m, In_m, Delta, DeltaP


# ---------- Chatterjee ξ (shared) ----------

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
        return 0.0, 0.0, []
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    rng = np.random.default_rng(base_seed)
    xis = []
    for _ in range(K):
        jitter = rng.uniform(-1e-9, 1e-9, n)
        xis.append(chatterjee_xi_single(x_arr + jitter, y_arr))
    return float(np.mean(xis)), float(np.max(xis) - np.min(xis)), xis


# ---------- per-cell sweep ----------

def cell_sweep(n, h, M_max, Y_target, lam):
    """Sweep all m ∈ M_n with n_height(m) = h and m ≤ M_max."""
    n_h = n ** h
    n_h1 = n ** (h + 1)
    rows = []
    # m has height exactly h iff n^h | m and n^(h+1) ∤ m.
    # m = n^h · k with n ∤ k.
    k = 1
    while True:
        m = n_h * k
        if m > M_max:
            break
        if k % n != 0:
            payload = m // n_h
            ptau2 = divisor_count(payload)
            lam_m = lam.get(m, None)
            if lam_m is None:
                k += 1
                continue
            rho, Out_m, In_m, Delta, DeltaP = rho_saturated(n, m, Y_target, lam)
            rows.append({
                'n': n, 'h': h, 'm': m, 'k': k,
                'payload': payload, 'payload_tau2': ptau2,
                'lambda': lam_m, 'rho': rho,
                'Out': Out_m, 'In': In_m, 'Delta': Delta, 'DeltaP': DeltaP,
            })
        k += 1
    return rows


def aggregate_payload_buckets(rows):
    buckets = defaultdict(list)
    for r in rows:
        b = payload_tau_bucket(r['payload_tau2'])
        buckets[b].append(r)

    out = []
    for b in TAU_BUCKET_ORDER:
        if b not in buckets:
            continue
        bs = buckets[b]
        rhos = np.array([r['rho'] for r in bs])
        lams = np.array([r['lambda'] for r in bs])
        abs_lams = np.abs(lams)
        neg_mass = float(np.sum(abs_lams[lams < -EPS]))
        abs_mass = float(np.sum(abs_lams))
        n_lam_pos = int(np.sum(lams > EPS))
        n_lam_neg = int(np.sum(lams < -EPS))
        n_lam_zero = int(np.sum(np.abs(lams) <= EPS))
        n_lam_nonzero = n_lam_pos + n_lam_neg
        nonzero_neg_frac = (n_lam_neg / n_lam_nonzero) if n_lam_nonzero > 0 else 0.0
        out.append({
            'bucket': b,
            'count': len(bs),
            'rho_mean': float(np.mean(rhos)),
            'rho_median': float(np.median(rhos)),
            'rho_neg_frac': float(np.sum(rhos < 0)) / len(rhos),
            'lam_pos': n_lam_pos,
            'lam_neg': n_lam_neg,
            'lam_zero': n_lam_zero,
            'lam_nonzero_neg_frac': nonzero_neg_frac,
            'neg_mass_over_abs_mass': (neg_mass / abs_mass) if abs_mass > 0 else 0.0,
        })
    return out


# ---------- plotting ----------

def plot_cell(n, h, rows, out_dir):
    if not rows:
        return
    payload_tau2 = np.array([r['payload_tau2'] for r in rows])
    rhos = np.array([r['rho'] for r in rows])
    lams = np.array([r['lambda'] for r in rows])

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

    ax = axes[0]
    pos = lams > EPS
    neg = lams < -EPS
    zero = np.abs(lams) <= EPS
    if pos.any():
        ax.scatter(payload_tau2[pos], rhos[pos], s=12, c='steelblue', alpha=0.7,
                   label=f'Λ > 0 ({int(pos.sum())})')
    if neg.any():
        ax.scatter(payload_tau2[neg], rhos[neg], s=12, c='crimson', alpha=0.7,
                   label=f'Λ < 0 ({int(neg.sum())})')
    if zero.any():
        ax.scatter(payload_tau2[zero], rhos[zero], s=12, c='gray', alpha=0.7,
                   label=f'Λ = 0 ({int(zero.sum())})')
    ax.set_xscale('log')
    ax.set_xlabel(r'payload $\tau_2(m/n^h)$')
    ax.set_ylabel(r'$\rho$')
    ax.set_title(f'n={n}, h={h} — ρ vs payload τ_2')
    ax.legend(fontsize=9, loc='best')
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    if pos.any():
        ax.scatter(payload_tau2[pos], lams[pos], s=12, c='steelblue', alpha=0.7,
                   label=f'Λ > 0 ({int(pos.sum())})')
    if neg.any():
        ax.scatter(payload_tau2[neg], lams[neg], s=12, c='crimson', alpha=0.7,
                   label=f'Λ < 0 ({int(neg.sum())})')
    if zero.any():
        ax.scatter(payload_tau2[zero], lams[zero], s=12, c='gray', alpha=0.7,
                   label=f'Λ = 0 ({int(zero.sum())})')
    ax.axhline(0, color='black', lw=0.5, alpha=0.5)
    ax.set_xscale('log')
    ax.set_xlabel(r'payload $\tau_2(m/n^h)$')
    ax.set_ylabel(r'$\Lambda_n(m)$  [nats]')
    ax.set_title(f'n={n}, h={h} — Λ_n vs payload τ_2')
    ax.legend(fontsize=9, loc='best')
    ax.grid(True, alpha=0.3)

    fig.suptitle(f'PAYLOAD-SCAN — n={n}, h={h}')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f'payload_scan_n{n}_h{h}.png'), dpi=120)
    plt.close(fig)


# ---------- main ----------

def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))

    # Single Λ_n table on [1, M_MAX] covers both the In sum (q ≤ Y_TARGET ≤
    # M_MAX) and the Λ_n(m) sample lookup (m ≤ M_MAX).
    j_max = 1
    while 2 ** j_max <= M_MAX:
        j_max += 1
    print(f'pre-computing τ_j for j ≤ {j_max}, k ≤ {M_MAX}', flush=True)
    tau = tau_table(M_MAX, j_max)

    ns = sorted({n for n, _ in PANEL})
    lam_by_n = {}
    for n in ns:
        print(f'pre-computing Λ_{n} on [1, {M_MAX}]', flush=True)
        lam_by_n[n] = acm_mangoldt(n, M_MAX, tau)

    # Smoke check: Λ_2(36) = -log 6
    expected_36 = -log(6)
    actual_36 = lam_by_n[2].get(36, 0.0)
    if abs(actual_36 - expected_36) > 1e-12:
        raise SystemExit(f'[smoke] FAIL Λ_2(36) = {actual_36}, expected {expected_36}')
    print(f'[smoke] Λ_2(36) = {actual_36:+.6f}  OK\n', flush=True)
    lam_M_by_n = lam_by_n  # alias

    csv_rows = [(
        'n', 'h', 'm', 'k', 'payload', 'payload_tau2',
        'lambda', 'rho', 'Out', 'In', 'Delta', 'DeltaP'
    )]
    summary_lines = [
        f'payload_scan summary',
        f'Y_TARGET = {Y_TARGET} (cutoff saturation), M_MAX = {M_MAX}',
        f'TIE_K = {TIE_K}, base_seed = {TIE_BASE_SEED}',
        f'method: Chatterjee ξ via direct numpy implementation, K random uniform jitter tie-breaks',
        '',
    ]

    cell_data = {}
    for (n, h) in PANEL:
        print(f'--- panel cell: n={n}, h={h} ---', flush=True)
        rows = cell_sweep(n, h, M_MAX, Y_TARGET, lam_by_n[n])
        # Override lambda values from M-range table (some m > Y_TARGET)
        for r in rows:
            r['lambda'] = lam_M_by_n[n].get(r['m'], 0.0)
        cell_data[(n, h)] = rows
        print(f'  swept {len(rows)} m values', flush=True)

        # CSV rows
        for r in rows:
            csv_rows.append((
                r['n'], r['h'], r['m'], r['k'], r['payload'], r['payload_tau2'],
                f'{r["lambda"]:+.10f}', f'{r["rho"]:+.6e}',
                f'{r["Out"]:.6e}', f'{r["In"]:.6e}',
                f'{r["Delta"]:+.6e}', f'{r["DeltaP"]:+.6e}',
            ))

        # Summary
        summary_lines.append(f'=== n={n}, h={h} ===\n')
        stats = aggregate_payload_buckets(rows)
        summary_lines.append(
            f'  {"bucket":>8}  {"count":>5}  {"ρ mean":>9}  {"ρ medn":>9}  '
            f'{"ρ neg":>6}  {"Λ pos":>5}  {"Λ neg":>5}  {"Λ zero":>6}  '
            f'{"Λ NZneg":>8}  {"neg/abs":>8}'
        )
        for s in stats:
            summary_lines.append(
                f'  {s["bucket"]:>8}  {s["count"]:>5}  '
                f'{s["rho_mean"]:>+9.4f}  {s["rho_median"]:>+9.4f}  '
                f'{s["rho_neg_frac"]:>6.3f}  '
                f'{s["lam_pos"]:>5}  {s["lam_neg"]:>5}  {s["lam_zero"]:>6}  '
                f'{s["lam_nonzero_neg_frac"]:>8.4f}  '
                f'{s["neg_mass_over_abs_mass"]:>8.4f}'
            )

        # ξ tests on payload τ_2
        if len(rows) >= 2:
            ptau2_arr = np.array([r['payload_tau2'] for r in rows], dtype=float)
            rho_arr = np.array([r['rho'] for r in rows])
            lam_arr = np.array([r['lambda'] for r in rows])

            xi_rho_mean, xi_rho_range, _ = chatterjee_xi_with_ties(
                ptau2_arr, rho_arr, K=TIE_K, base_seed=TIE_BASE_SEED
            )
            xi_lam_mean, xi_lam_range, _ = chatterjee_xi_with_ties(
                ptau2_arr, lam_arr, K=TIE_K, base_seed=TIE_BASE_SEED
            )
            summary_lines.append(
                f'\n  Chatterjee ξ (K={TIE_K}, jitter):'
            )
            summary_lines.append(
                f'    ξ(payload_τ_2 → ρ) = {xi_rho_mean:+.4f}  '
                f'(range {xi_rho_range:.4f})'
            )
            summary_lines.append(
                f'    ξ(payload_τ_2 → Λ_n) = {xi_lam_mean:+.4f}  '
                f'(range {xi_lam_range:.4f})'
            )
        summary_lines.append('')

        plot_cell(n, h, rows, out_dir)

    # Cross-cell comparison: prime n vs composite n at fixed h.
    summary_lines.append('=== prime-n vs composite-n at matched (h, payload τ_2) ===\n')
    for h in [2, 3]:
        summary_lines.append(f'  h = {h}:')
        # Build a cell-by-cell bucket table.
        cells = [(n, h) for n in ns]
        bucket_table = {}
        for (n, h2) in cells:
            if (n, h2) not in cell_data:
                continue
            stats = aggregate_payload_buckets(cell_data[(n, h2)])
            for s in stats:
                bucket_table.setdefault(s['bucket'], {})[n] = s

        summary_lines.append(
            f'    {"τ_2":>6}  ' + '  '.join(f'n={n}_ρ_mean'.rjust(13) for n in ns)
        )
        summary_lines.append(
            f'    {"":>6}  ' + '  '.join(f'(NZneg)'.rjust(13) for _ in ns)
        )
        for b in TAU_BUCKET_ORDER:
            if b not in bucket_table:
                continue
            row1 = f'    {b:>6}  '
            row2 = f'    {"":>6}  '
            for n in ns:
                s = bucket_table[b].get(n)
                if s is None:
                    row1 += f'{"--":>13}  '
                    row2 += f'{"--":>13}  '
                else:
                    row1 += f'{s["rho_mean"]:>+13.4f}  '
                    row2 += f'({s["lam_nonzero_neg_frac"]:>5.2f},c={s["count"]:>3}) '
            summary_lines.append(row1)
            summary_lines.append(row2)
        summary_lines.append('')

    csv_path = os.path.join(out_dir, 'payload_scan.csv')
    with open(csv_path, 'w', newline='') as f:
        csv.writer(f).writerows(csv_rows)
    print(f'\nwrote {csv_path}  ({len(csv_rows) - 1} rows)', flush=True)

    summary_path = os.path.join(out_dir, 'payload_scan_summary.txt')
    with open(summary_path, 'w') as f:
        f.write('\n'.join(summary_lines))
        f.write('\n')
    print(f'wrote {summary_path}', flush=True)


if __name__ == '__main__':
    main()
