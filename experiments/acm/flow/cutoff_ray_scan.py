"""
cutoff_ray_scan.py — controlled scan of the truncation coordinate
==================================================================

Phase 1 of STRUCTURE-HUNT.md. Brief: CUTOFF-SCAN.md.

For each (n, m) in PANEL, sweep X = mY across Y ∈ [1, Y_MAX] so
⌊X/m⌋ = Y exactly. At each Y, compute

    Out_n(m)        = 1 / (m log m)                       [closed form]
    In_n(m; mY)     = Σ_{q ∈ M_n, q ≤ Y}
                          Λ_n(q) / (mq · log²(mq))
    Δ_n(m; mY)      = In − Out
    Δ'_n(m; mY)     = Δ + 1/(m · log(mY))
    ρ_n(m; mY)      = Δ' / Out

Bucket Y by scouts: τ_2(Y), witness count, smallest prime factor,
square-flag, distance to nearest multiple of n² and n³, diag/prime-
row disagreement. Aggregate ρ per bucket. Compute Chatterjee ξ on
each (scout, ρ) pair with K random tie-breakings of the predictor
to handle the heavy-ties regime that follows from fixed (n, m).

Method choices declared against ACM-MANGOLDT.md statistical-method-
discipline:
  - structural dependence: Chatterjee ξ with K=32 random tie-breaks
    (jitter), reporting ξ_mean and ξ_range; never single-value.
  - bucket statistics: mean, median, sign-fraction, count.
  - shape testing: not done here. Shape is read off the bucket
    progressions; CUTOFF-SCAN.md does not prescribe a shape.

Outputs (this directory):
  cutoff_ray_scan.csv            per (n, m, Y) row with scouts
  cutoff_ray_summary.txt         per panel cell, bucket stats + ξ
  cutoff_ray_{label}.png         per panel cell, ρ vs scouts (4-panel)

Usage:
    sage -python cutoff_ray_scan.py
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


# Panel — covers Tier-1 cells from CUTOFF-SCAN.md.
# Format: (n, m, label).
PANEL = [
    (2, 4,    'n2_m4_h2_p1'),         # h=2 atom-square, payload τ_2 = 1
    (2, 12,   'n2_m12_h2_p2'),        # h=2 prime-payload, payload τ_2 = 2
    (2, 36,   'n2_m36_h2_p3'),        # h=2 first non-UF, payload τ_2 = 3
    (2, 100,  'n2_m100_h2_p3_smooth'),# h=2 d=3 smooth-block
    (2, 180,  'n2_m180_h2_p6_smooth'),# h=2 d=3 smooth, high payload τ_2
    (2, 72,   'n2_m72_h3_p3'),        # h=3 payload τ_2 = 3
    (3, 36,   'n3_m36_h2_p3'),        # h=2 for n=3 (mirror of n2_m36)
    (5, 100,  'n5_m100_h2_p3_smooth'),# smooth, n=5 (matched to n2_m100)
    (4, 48,   'n4_m48_h2_p2'),        # composite n=4, payload τ_2 = 2 (matched to n2_m12)
]

Y_MAX = 50_000
TIE_K = 32
TIE_BASE_SEED = 42

EPS = 1e-12

WITNESS_BUCKET_ORDER = ['0', '1', '2', '3-5', '6-9', '10+']
TAU_BUCKET_ORDER = ['0-2', '3-4', '5-8', '9-16', '17+']
DIST_BUCKET_ORDER = ['0', '1', '2', '3-5', '6-10', '11-25', '>25']


# ---------- Λ_n closed form ----------

def tau_table(mmax, j_max):
    """τ_j(k) for 1 ≤ k ≤ mmax, 1 ≤ j ≤ j_max via Dirichlet convolution."""
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
    """Λ_n(m) for m ∈ M_n ∩ [1, X]. Returns dict m → float (in nats)."""
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


# ---------- scouts ----------

def small_primes_sieve(limit):
    if limit < 2:
        return []
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for p in range(2, isqrt(limit) + 1):
        if sieve[p]:
            for k in range(p * p, limit + 1, p):
                sieve[k] = False
    return [p for p in range(2, limit + 1) if sieve[p]]


PRIMES = []  # populated in main


def scout_Y(Y, n):
    """Scout features for cutoff Y at modulus n."""
    if Y < 1:
        return None

    root = isqrt(Y)
    is_square = (root * root == Y)

    tau2 = 0
    pairs = []
    spf = Y if Y > 1 else 0
    for k in range(1, root + 1):
        if Y % k == 0:
            other = Y // k
            tau2 += 1 if k == other else 2
            if k >= 2 and k < other:
                pairs.append((k, other))
            if k >= 2 and spf == Y:
                spf = k

    witness_count = len(pairs)

    n2 = n * n
    r2 = Y % n2
    dist_n2 = min(r2, n2 - r2)

    n3 = n2 * n
    r3 = Y % n3
    dist_n3 = min(r3, n3 - r3)

    if pairs and PRIMES:
        diag = min(pairs, key=lambda kn: kn[1] - kn[0])
        prime = min(
            pairs,
            key=lambda kn: abs(kn[1] - PRIMES[kn[0] - 1])
                           if (kn[0] - 1) < len(PRIMES) else float('inf'),
        )
        disagree = int(diag != prime)
    else:
        disagree = 0

    return {
        'tau2': tau2,
        'witness_count': witness_count,
        'spf': spf,
        'is_square': int(is_square),
        'dist_n2': dist_n2,
        'dist_n3': dist_n3,
        'disagree': disagree,
    }


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


# ---------- ρ sweep ----------

def cutoff_ray_sweep(n, m, Y_max, lam):
    """For fixed (n, m), sweep Y ∈ [1, Y_max] incrementally maintaining
    In_n(m; mY). Returns list of dicts."""
    out = []
    log_m = log(m)
    Out_m = 1.0 / (m * log_m)
    In_m = 0.0
    for Y in range(1, Y_max + 1):
        # Update In if Y ∈ M_n: Y == 1 contributes 0 (Λ_n(1) = 0); else
        # Y % n == 0.
        if Y > 1 and Y % n == 0:
            lam_q = lam.get(Y, 0.0)
            if lam_q != 0.0:
                mq = m * Y
                log_mq = log(mq)
                In_m += lam_q / (mq * log_mq * log_mq)
        X = m * Y
        log_X = log(X)
        Delta = In_m - Out_m
        DeltaP = Delta + 1.0 / (m * log_X)
        rho = DeltaP / Out_m
        out.append({
            'Y': Y, 'X': X, 'In': In_m, 'Out': Out_m,
            'Delta': Delta, 'DeltaP': DeltaP, 'rho': rho,
        })
    return out


# ---------- Chatterjee ξ ----------

def chatterjee_xi_single(x, y):
    """Single ξ(x → y). Assumes x has no exact ties."""
    n = len(x)
    if n < 2:
        return 0.0
    order = np.argsort(x)
    y_perm = y[order]
    # Ranks of y_perm (1-indexed). With no ties this is unambiguous.
    ranks = np.argsort(np.argsort(y_perm)) + 1
    return 1.0 - 3.0 * np.sum(np.abs(np.diff(ranks))) / (n * n - 1)


def chatterjee_xi_with_ties(x, y, K=TIE_K, base_seed=TIE_BASE_SEED):
    """ξ(x → y) under K random tie-breaks of x. Returns (mean, range, all)."""
    n = len(x)
    if n < 2:
        return 0.0, 0.0, []
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    rng = np.random.default_rng(base_seed)
    xis = []
    for _ in range(K):
        # Jitter scale: smaller than any meaningful integer gap (predictors
        # are integer-valued). 1e-9 is safe; ρ values are ~10^-1 typically.
        jitter = rng.uniform(-1e-9, 1e-9, n)
        xis.append(chatterjee_xi_single(x_arr + jitter, y_arr))
    return float(np.mean(xis)), float(np.max(xis) - np.min(xis)), xis


# ---------- aggregation ----------

def aggregate_buckets(rows, bucket_fn, key, order=None):
    buckets = defaultdict(list)
    for r in rows:
        b = bucket_fn(r[key])
        buckets[b].append(r['rho'])

    out = []
    keys = list(buckets.keys())
    if order:
        keys = [b for b in order if b in buckets]
    else:
        keys.sort()
    for b in keys:
        arr = np.array(buckets[b])
        out.append({
            'bucket': b,
            'count': len(arr),
            'mean': float(np.mean(arr)),
            'median': float(np.median(arr)),
            'sign_neg_fraction': float(np.sum(arr < 0)) / len(arr),
            'mean_minus_median': float(np.mean(arr) - np.median(arr)),
        })
    return out


# ---------- plotting ----------

def plot_panel_cell(n, m, label, sweep, out_dir):
    fig, axes = plt.subplots(2, 2, figsize=(13, 7))

    Ys = np.array([r['Y'] for r in sweep])
    rhos = np.array([r['rho'] for r in sweep])

    ax = axes[0, 0]
    ax.plot(Ys, rhos, lw=0.4, color='steelblue', alpha=0.6)
    ax.axhline(0, color='black', lw=0.5, alpha=0.5)
    ax.set_xscale('log')
    ax.set_xlabel('Y')
    ax.set_ylabel(r'$\rho$')
    ax.set_title(f'n={n}, m={m} — ρ vs Y')
    ax.grid(True, alpha=0.3)

    ax = axes[0, 1]
    tau2s = np.array([r['tau2'] for r in sweep])
    ax.scatter(tau2s, rhos, s=2, c='steelblue', alpha=0.4)
    ax.axhline(0, color='black', lw=0.5, alpha=0.5)
    ax.set_xscale('log')
    ax.set_xlabel(r'$\tau_2(Y)$')
    ax.set_ylabel(r'$\rho$')
    ax.set_title('ρ vs τ_2(Y)')
    ax.grid(True, alpha=0.3)

    ax = axes[1, 0]
    wcs = np.array([r['witness_count'] for r in sweep])
    ax.scatter(wcs, rhos, s=2, c='steelblue', alpha=0.4)
    ax.axhline(0, color='black', lw=0.5, alpha=0.5)
    ax.set_xlabel('witness count')
    ax.set_ylabel(r'$\rho$')
    ax.set_title('ρ vs witness count')
    ax.grid(True, alpha=0.3)

    ax = axes[1, 1]
    dns = np.array([r['dist_n2'] for r in sweep])
    ax.scatter(dns, rhos, s=2, c='steelblue', alpha=0.4)
    ax.axhline(0, color='black', lw=0.5, alpha=0.5)
    ax.set_xlabel(r'distance to nearest multiple of $n^2$')
    ax.set_ylabel(r'$\rho$')
    ax.set_title(r'ρ vs dist($n^2$)')
    ax.grid(True, alpha=0.3)

    fig.suptitle(f'CUTOFF-SCAN — {label}')
    plt.tight_layout()
    plot_path = os.path.join(out_dir, f'cutoff_ray_{label}.png')
    plt.savefig(plot_path, dpi=120)
    plt.close(fig)


# ---------- main ----------

def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))

    global PRIMES
    PRIMES = small_primes_sieve(2000)

    # τ_j table: shared across all n (τ_j is independent of n).
    j_max = 1
    while 2 ** j_max <= Y_MAX:
        j_max += 1
    print(f'pre-computing τ_j for j ≤ {j_max}, k ≤ {Y_MAX}', flush=True)
    tau = tau_table(Y_MAX, j_max)
    print(f'  done; max τ_{j_max} = {max(tau[j_max - 1])}', flush=True)

    # Λ_n per panel n.
    ns_in_panel = sorted(set(n for n, _, _ in PANEL))
    lam_by_n = {}
    for n in ns_in_panel:
        print(f'pre-computing Λ_{n} on M_{n} ∩ [1, {Y_MAX}]', flush=True)
        lam_by_n[n] = acm_mangoldt(n, Y_MAX, tau)

    # Smoke check.
    expected_36 = -log(6)
    actual_36 = lam_by_n.get(2, {}).get(36, 0.0)
    if abs(actual_36 - expected_36) > 1e-12:
        raise SystemExit(f'[smoke] FAIL: Λ_2(36) = {actual_36}, expected {expected_36}')
    print(f'[smoke] Λ_2(36) = {actual_36:+.6f}  OK\n', flush=True)

    csv_rows = [(
        'n', 'm', 'label', 'Y', 'X', 'rho', 'Out', 'In', 'Delta', 'DeltaP',
        'tau2', 'witness_count', 'spf', 'is_square', 'dist_n2', 'dist_n3', 'disagree'
    )]
    summary_lines = [
        f'cutoff_ray_scan summary',
        f'Y_MAX = {Y_MAX}, TIE_K = {TIE_K}, base_seed = {TIE_BASE_SEED}',
        f'method: Chatterjee ξ via direct numpy implementation, K random uniform jitter tie-breaks',
        '',
    ]

    for (n, m, label) in PANEL:
        print(f'--- panel cell: n={n}, m={m} ({label}) ---', flush=True)
        sweep = cutoff_ray_sweep(n, m, Y_MAX, lam_by_n[n])
        for r in sweep:
            r.update(scout_Y(r['Y'], n))

        for r in sweep:
            csv_rows.append((
                n, m, label, r['Y'], r['X'],
                f'{r["rho"]:+.6e}', f'{r["Out"]:.6e}', f'{r["In"]:.6e}',
                f'{r["Delta"]:+.6e}', f'{r["DeltaP"]:+.6e}',
                r['tau2'], r['witness_count'], r['spf'],
                r['is_square'], r['dist_n2'], r['dist_n3'], r['disagree'],
            ))

        # Summary block for this panel cell.
        summary_lines.append(f'=== n={n}, m={m}, label={label} ===')
        for scout_name, bucket_fn, key, order in [
            ('tau2(Y)', tau_bucket, 'tau2', TAU_BUCKET_ORDER),
            ('witness_count(Y)', witness_bucket, 'witness_count', WITNESS_BUCKET_ORDER),
            ('dist_to_n^2', dist_bucket, 'dist_n2', DIST_BUCKET_ORDER),
            ('dist_to_n^3', dist_bucket, 'dist_n3', DIST_BUCKET_ORDER),
        ]:
            stats = aggregate_buckets(sweep, bucket_fn, key, order=order)
            summary_lines.append(f'\n  scout: {scout_name}')
            summary_lines.append(
                f'  {"bucket":>10}  {"count":>6}  {"mean ρ":>10}  '
                f'{"median ρ":>10}  {"neg_frac":>9}  {"|m-md|":>9}'
            )
            for s in stats:
                flag = ' *' if abs(s['mean_minus_median']) > 0.05 else '  '
                summary_lines.append(
                    f'  {s["bucket"]:>10}  {s["count"]:>6}  '
                    f'{s["mean"]:>+10.4f}  {s["median"]:>+10.4f}  '
                    f'{s["sign_neg_fraction"]:>9.4f}  '
                    f'{abs(s["mean_minus_median"]):>9.4f}{flag}'
                )

        # ξ rankings.
        rho_arr = np.array([r['rho'] for r in sweep])
        scout_keys = [
            ('tau2', 'tau2'),
            ('witness_count', 'witness_count'),
            ('spf', 'spf'),
            ('is_square', 'is_square'),
            ('dist_n2', 'dist_n2'),
            ('dist_n3', 'dist_n3'),
            ('disagree', 'disagree'),
        ]
        xi_results = []
        for nm, k in scout_keys:
            scout_arr = np.array([r[k] for r in sweep], dtype=float)
            xi_mean, xi_range, _ = chatterjee_xi_with_ties(
                scout_arr, rho_arr, K=TIE_K, base_seed=TIE_BASE_SEED
            )
            xi_results.append((nm, xi_mean, xi_range))
        xi_results.sort(key=lambda x: -x[1])

        summary_lines.append(f'\n  Chatterjee ξ (K={TIE_K} random jitter tie-breaks):')
        summary_lines.append(f'  {"scout":>16}  {"ξ_mean":>9}  {"ξ_range":>9}')
        for nm, xm, xr in xi_results:
            summary_lines.append(f'  {nm:>16}  {xm:>+9.4f}  {xr:>9.4f}')
        summary_lines.append('')

        plot_panel_cell(n, m, label, sweep, out_dir)
        top = xi_results[0]
        print(
            f'  swept {len(sweep)} Y values; top scout by ξ_mean: '
            f'{top[0]} (ξ_mean={top[1]:+.4f}, range={top[2]:.4f})',
            flush=True,
        )

    csv_path = os.path.join(out_dir, 'cutoff_ray_scan.csv')
    with open(csv_path, 'w', newline='') as f:
        csv.writer(f).writerows(csv_rows)
    print(f'\nwrote {csv_path}  ({len(csv_rows) - 1} rows)', flush=True)

    summary_path = os.path.join(out_dir, 'cutoff_ray_summary.txt')
    with open(summary_path, 'w') as f:
        f.write('\n'.join(summary_lines))
        f.write('\n')
    print(f'wrote {summary_path}', flush=True)


if __name__ == '__main__':
    main()
