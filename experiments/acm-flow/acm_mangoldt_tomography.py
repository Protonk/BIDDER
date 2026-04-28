"""
acm_mangoldt_tomography.py — ACM-Mangoldt flow tomography
==========================================================

The 1196-style divisibility-flow apparatus, ported to the ACM
monoids M_n = {1} ∪ nℤ⁺.

Three layers:

    L1  Λ_n(m) sign profile, by m and by exact n-height.
    L2  Flow defect Δ_n(m; X) = In_n(m; X) − Out_n(m), where
            Out_n(m) = 1 / (m log m)                                 [exact]
            In_n(m; X) = Σ_{q ∈ M_n, mq ≤ X} Λ_n(q)/(mq log²(mq))
        and first-order Mertens residual
            Δ'_n(m; X) = Δ_n(m; X) + 1/(m log X)
    L3  Block-typed totalisation. Partition (n, m) by base-10
        digit class d and the block type (smooth / Family E /
        uncertified) from core/BLOCK-UNIFORMITY.md.

Brief: ACM-MANGOLDT.md.

Usage:
    sage -python acm_mangoldt_tomography.py
"""

import csv
import os
from collections import defaultdict
from functools import lru_cache
from fractions import Fraction
from math import isqrt, log

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


NS = [2, 3, 4, 5, 6, 10]
X = 10000
B = 10  # base for the digit-class partition
EPS = 1e-12
WITNESS_BUCKETS = ['0', '1', '2', '3-5', '6-9', '10+']
DIST_BUCKETS = ['0', '1', '2', '3-5', '6-10', '11-25', '>25']
TAU_BUCKETS = ['0-2', '3-4', '5-8', '9-16', '17+']


# ---------- core arithmetic ----------

def small_primes(limit):
    """Primes up to limit by sieve of Eratosthenes."""
    if limit < 2:
        return []
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for p in range(2, isqrt(limit) + 1):
        if sieve[p]:
            for k in range(p * p, limit + 1, p):
                sieve[k] = False
    return [p for p in range(2, limit + 1) if sieve[p]]


def first_primes(count):
    """Return at least count primes."""
    if count <= 0:
        return []
    limit = max(16, count * 8)
    while True:
        primes = small_primes(limit)
        if len(primes) >= count:
            return primes[:count]
        limit *= 2


PRIMES = first_primes(isqrt(X) + 4)


def p_k(k):
    """k-th prime, 1-indexed."""
    return PRIMES[k - 1]

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


def n_height(n, m):
    """ν_n(m), the n-adic valuation."""
    h = 0
    while m % n == 0:
        h += 1
        m //= n
    return h


def block_classify(n, d, b=B):
    """Returns 'smooth', 'family_E', or 'uncertified' for digit class d
    under modulus n in base b. Definitions from core/BLOCK-UNIFORMITY.md."""
    if d >= 1 and (b ** (d - 1)) % (n * n) == 0:
        return 'smooth'
    if d >= 2 and b ** (d - 1) <= n <= (b ** d - 1) // (b - 1):
        return 'family_E'
    return 'uncertified'


def digit_count(v):
    return len(str(v)) if v > 0 else 1


def dist_to_multiple(v, modulus):
    r = v % modulus
    return min(r, modulus - r)


def witness_bucket(count):
    if count <= 0:
        return '0'
    if count == 1:
        return '1'
    if count == 2:
        return '2'
    if count <= 5:
        return '3-5'
    if count <= 9:
        return '6-9'
    return '10+'


def dist_bucket(dist):
    if dist <= 0:
        return '0'
    if dist == 1:
        return '1'
    if dist == 2:
        return '2'
    if dist <= 5:
        return '3-5'
    if dist <= 10:
        return '6-10'
    if dist <= 25:
        return '11-25'
    return '>25'


def tau_bucket(tau2):
    if tau2 <= 2:
        return '0-2'
    if tau2 <= 4:
        return '3-4'
    if tau2 <= 8:
        return '5-8'
    if tau2 <= 16:
        return '9-16'
    return '17+'


@lru_cache(maxsize=None)
def scout_features(N):
    """Cheap composite-lattice scouts for N.

    Returns (spf, tau2, witness_count, diag_k, prime_dist, diag_prime_disagree).
    Witness pairs follow experiments/acm/diagonal/witness_density:
    (k, N/k) with k >= 2 and k < sqrt(N).
    """
    if N == 1:
        return (0, 1, 0, 0, -1, 0)
    if N < 1:
        return (0, 0, 0, 0, -1, 0)

    root = isqrt(N)
    spf = N
    tau2 = 0
    pairs = []
    for k in range(1, root + 1):
        if N % k != 0:
            continue
        other = N // k
        tau2 += 1 if k == other else 2
        if k >= 2 and spf == N:
            spf = k
        if k >= 2 and k < other:
            pairs.append((k, other))

    if not pairs:
        return (spf, tau2, 0, 0, -1, 0)

    diag = min(pairs, key=lambda pair: pair[1] - pair[0])
    prime = min(pairs, key=lambda pair: abs(pair[1] - p_k(pair[0])))
    prime_dist = abs(prime[1] - p_k(prime[0]))
    disagree = 0 if diag == prime else 1
    return (spf, tau2, len(pairs), diag[0], prime_dist, disagree)


def add_residual(total, key, out_value, delta_mertens, disagree):
    row = total[key]
    row[0] += 1
    row[1] += out_value
    row[2] += delta_mertens
    row[3] += disagree


def add_sign(total, key, value, disagree):
    row = total[key]
    row[0] += 1
    if value > EPS:
        row[1] += 1
    elif value < -EPS:
        row[2] += 1
        row[3] += -value
    row[4] += abs(value)
    row[5] += disagree


def flow_defect(n, X, lam):
    """For each m ∈ M_n ∩ [n, X], compute Out_n(m), In_n(m; X), Δ_n,
    and the first-order Mertens residual Δ'_n.
    Returns dict m → (Out, In, Delta, DeltaMertens)."""
    out = {}
    log_X = log(X)
    for m in range(n, X + 1, n):
        log_m = log(m)
        Out_m = 1.0 / (m * log_m)
        In_m = 0.0
        max_q = X // m
        for q in range(n, max_q + 1, n):
            lam_q = lam.get(q, 0.0)
            if lam_q == 0.0:
                continue
            mq = m * q
            log_mq = log(mq)
            In_m += lam_q / (mq * log_mq * log_mq)
        Delta_m = In_m - Out_m
        DeltaM_m = Delta_m + 1.0 / (m * log_X)
        out[m] = (Out_m, In_m, Delta_m, DeltaM_m)
    return out


# ---------- sanity ----------

def smoke_test(tau):
    lam2 = acm_mangoldt(2, 50, tau)
    expected = {2: log(2), 6: log(6), 12: 0.0, 36: -log(6)}
    for m, ev in expected.items():
        actual = lam2.get(m, None)
        ok = actual is not None and abs(actual - ev) < 1e-12
        tag = 'OK ' if ok else 'FAIL'
        print(f'  [smoke] Λ_2({m:>2}) = {actual:+.6f}  expected {ev:+.6f}  {tag}')
        if not ok:
            raise SystemExit(f'[smoke] FAIL on m={m}')


# ---------- plotting ----------

def plot_lambda(n, lam, out_path):
    ms = sorted(m for m in lam if m != 1)
    vs = np.array([lam[m] for m in ms])
    ms = np.array(ms)
    pos = vs > EPS
    neg = vs < -EPS
    zero = (~pos) & (~neg)

    fig, ax = plt.subplots(figsize=(13, 4))
    if pos.any():
        ax.scatter(ms[pos], vs[pos], s=3, c='steelblue', alpha=0.6,
                   label=f'Λ > 0 ({int(pos.sum())})')
    if neg.any():
        ax.scatter(ms[neg], vs[neg], s=10, c='crimson', alpha=0.85,
                   label=f'Λ < 0 ({int(neg.sum())})')
    if zero.any():
        ax.scatter(ms[zero], vs[zero], s=8, c='gray', alpha=0.7,
                   label=f'Λ = 0 ({int(zero.sum())})')
    ax.axhline(0, color='black', lw=0.5, alpha=0.5)
    ax.set_xscale('log')
    ax.set_xlabel('m  (log scale)')
    ax.set_ylabel(r'$\Lambda_n(m)$  [nats]')
    ax.set_title(f'$\\Lambda_{{M_{n}}}(m)$ on M$_{n}$ ∩ [{n}, {X}]')
    ax.legend(fontsize=9, loc='best')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close(fig)


def plot_delta(n, flow, out_path):
    ms = np.array(sorted(flow.keys()))
    deltas = np.array([flow[m][2] for m in ms])
    pos = deltas > 0
    neg = deltas < 0

    fig, ax = plt.subplots(figsize=(13, 4))
    if pos.any():
        ax.scatter(ms[pos], deltas[pos], s=3, c='steelblue', alpha=0.6,
                   label=f'Δ > 0 ({int(pos.sum())})')
    if neg.any():
        ax.scatter(ms[neg], deltas[neg], s=8, c='crimson', alpha=0.85,
                   label=f'Δ < 0 ({int(neg.sum())})')
    ax.axhline(0, color='black', lw=0.5, alpha=0.5)
    ax.set_xscale('log')
    ax.set_yscale('symlog', linthresh=1e-8)
    ax.set_xlabel('m  (log scale)')
    ax.set_ylabel(r'$\Delta_n(m; X)$')
    ax.set_title(f'Flow defect $\\Delta_{{n}}(m; X={X})$ for n={n}')
    ax.legend(fontsize=9, loc='best')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close(fig)


def plot_delta_mertens(n, flow, out_path):
    ms = np.array(sorted(flow.keys()))
    deltas = np.array([flow[m][3] for m in ms])
    pos = deltas > 0
    neg = deltas < 0

    fig, ax = plt.subplots(figsize=(13, 4))
    if pos.any():
        ax.scatter(ms[pos], deltas[pos], s=3, c='steelblue', alpha=0.6,
                   label=f"Δ' > 0 ({int(pos.sum())})")
    if neg.any():
        ax.scatter(ms[neg], deltas[neg], s=8, c='crimson', alpha=0.85,
                   label=f"Δ' < 0 ({int(neg.sum())})")
    ax.axhline(0, color='black', lw=0.5, alpha=0.5)
    ax.set_xscale('log')
    ax.set_yscale('symlog', linthresh=1e-8)
    ax.set_xlabel('m  (log scale)')
    ax.set_ylabel(r"$\Delta'_n(m; X)$")
    ax.set_title(f"Mertens residual $\\Delta'_{{n}}(m; X={X})$ for n={n}")
    ax.legend(fontsize=9, loc='best')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close(fig)


# ---------- main ----------

def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))

    j_max = 1
    while min(NS) ** j_max <= X:
        j_max += 1
    print(f'pre-computing τ_j for j = 1..{j_max}, k ≤ {X}', flush=True)
    tau = tau_table(X, j_max)
    print(f'  done — max τ_{j_max} seen: {max(tau[j_max - 1])}', flush=True)

    print('\n[smoke] checking user-supplied Λ_2 values:')
    smoke_test(tau)

    rows = [('n', 'm', 'height', 'block_d', 'block_type',
             'Lambda', 'Out', 'In', 'Delta', 'DeltaMertens',
             'Y', 'cutoff_d', 'cutoff_type', 'cutoff_phase_n2',
             'cutoff_dist_n2', 'cutoff_tau2', 'cutoff_witness_count',
             'cutoff_spf', 'cutoff_diag_k', 'cutoff_prime_dist',
             'cutoff_diag_prime_disagree',
             'payload2', 'payload2_tau2', 'payload2_witness_count',
             'payload2_spf', 'payload2_diag_k', 'payload2_prime_dist',
             'payload2_diag_prime_disagree',
             'payload3', 'payload3_tau2', 'payload3_witness_count',
             'payload3_spf', 'payload3_diag_k', 'payload3_prime_dist',
             'payload3_diag_prime_disagree')]
    height_summary = {}
    cell_totals = defaultdict(lambda: [0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0, 0])
    # cell key (n, d, block_type) →
    # [count, sumOut, sumIn, sumDelta, sumDeltaMertens,
    #  posDelta, negDelta, posDeltaMertens, negDeltaMertens]
    type_totals = defaultdict(lambda: [0, 0.0, 0.0, 0.0])
    # block_type → [count, sumOut, sumDelta, sumDeltaMertens]
    cutoff_phase_totals = defaultdict(lambda: [0, 0.0, 0.0, 0])
    cutoff_dist_totals = defaultdict(lambda: [0, 0.0, 0.0, 0])
    cutoff_wc_type_totals = defaultdict(lambda: [0, 0.0, 0.0, 0])
    cutoff_tau_type_totals = defaultdict(lambda: [0, 0.0, 0.0, 0])
    payload2_wc_type_sign = defaultdict(lambda: [0, 0, 0, 0.0, 0.0, 0])
    payload2_tau_sign = defaultdict(lambda: [0, 0, 0, 0.0, 0.0, 0])
    payload3_wc_type_sign = defaultdict(lambda: [0, 0, 0, 0.0, 0.0, 0])
    payload3_tau_sign = defaultdict(lambda: [0, 0, 0, 0.0, 0.0, 0])
    per_n_lambda = {}
    per_n_flow = {}

    for n in NS:
        print(f'\n--- n = {n} ---', flush=True)
        lam = acm_mangoldt(n, X, tau)
        per_n_lambda[n] = lam
        flow = flow_defect(n, X, lam)
        per_n_flow[n] = flow

        n_total = sum(1 for m in lam if m != 1)
        n_neg = sum(1 for m, v in lam.items() if m != 1 and v < -EPS)
        n_zero = sum(1 for m, v in lam.items() if m != 1 and abs(v) <= EPS)
        first_neg = next((m for m in sorted(lam) if m != 1 and lam[m] < -EPS), None)
        print(f'  |M_{n} ∩ [{n}, {X}]|: {n_total}   '
              f'Λ < 0: {n_neg}   Λ = 0: {n_zero}')
        if first_neg is not None:
            print(f'  first Λ < 0:  Λ_{{M_{n}}}({first_neg}) = {lam[first_neg]:+.6f}')

        # Height table
        h_summary = defaultdict(lambda: [0, 0, 0, 0.0, 0.0])
        for m in lam:
            if m == 1:
                continue
            v = lam[m]
            h = n_height(n, m)
            row = h_summary[h]
            row[0] += 1
            if v > EPS:
                row[1] += 1
            elif v < -EPS:
                row[2] += 1
                row[3] += -v
            row[4] += abs(v)
        height_summary[n] = h_summary

        # Cell totals
        for m in lam:
            if m == 1:
                continue
            v = lam[m]
            h = n_height(n, m)
            d = len(str(m))
            bt = block_classify(n, d, B)
            Out_m, In_m, Delta_m, DeltaM_m = flow[m]
            Y = X // m
            cutoff_d = digit_count(Y)
            cutoff_type = block_classify(n, cutoff_d, B)
            cutoff_phase_n2 = (Y // n) % n
            cutoff_dist_n2 = dist_to_multiple(Y, n * n)
            (cutoff_spf, cutoff_tau2, cutoff_wc, cutoff_diag_k,
             cutoff_prime_dist, cutoff_disagree) = scout_features(Y)

            n2 = n * n
            if m % n2 == 0:
                payload2 = m // n2
                (payload2_spf, payload2_tau2, payload2_wc, payload2_diag_k,
                 payload2_prime_dist, payload2_disagree) = scout_features(payload2)
            else:
                payload2 = 0
                payload2_spf = payload2_tau2 = payload2_wc = payload2_diag_k = 0
                payload2_prime_dist = -1
                payload2_disagree = 0
            n3 = n2 * n
            if m % n3 == 0:
                payload3 = m // n3
                (payload3_spf, payload3_tau2, payload3_wc, payload3_diag_k,
                 payload3_prime_dist, payload3_disagree) = scout_features(payload3)
            else:
                payload3 = 0
                payload3_spf = payload3_tau2 = payload3_wc = payload3_diag_k = 0
                payload3_prime_dist = -1
                payload3_disagree = 0

            cell = cell_totals[(n, d, bt)]
            cell[0] += 1
            cell[1] += Out_m
            cell[2] += In_m
            cell[3] += Delta_m
            cell[4] += DeltaM_m
            if Delta_m > 0:
                cell[5] += 1
            elif Delta_m < 0:
                cell[6] += 1
            if DeltaM_m > 0:
                cell[7] += 1
            elif DeltaM_m < 0:
                cell[8] += 1

            tcell = type_totals[bt]
            tcell[0] += 1
            tcell[1] += Out_m
            tcell[2] += Delta_m
            tcell[3] += DeltaM_m

            add_residual(cutoff_phase_totals, (n, cutoff_phase_n2),
                         Out_m, DeltaM_m, cutoff_disagree)
            add_residual(cutoff_dist_totals, (n, dist_bucket(cutoff_dist_n2)),
                         Out_m, DeltaM_m, cutoff_disagree)
            add_residual(cutoff_wc_type_totals, (bt, witness_bucket(cutoff_wc)),
                         Out_m, DeltaM_m, cutoff_disagree)
            add_residual(cutoff_tau_type_totals, (bt, tau_bucket(cutoff_tau2)),
                         Out_m, DeltaM_m, cutoff_disagree)
            if payload2:
                add_sign(payload2_wc_type_sign, (bt, witness_bucket(payload2_wc)),
                         v, payload2_disagree)
                add_sign(payload2_tau_sign, (tau_bucket(payload2_tau2), payload2_disagree),
                         v, payload2_disagree)
            if payload3:
                add_sign(payload3_wc_type_sign, (bt, witness_bucket(payload3_wc)),
                         v, payload3_disagree)
                add_sign(payload3_tau_sign, (tau_bucket(payload3_tau2), payload3_disagree),
                         v, payload3_disagree)

            rows.append((n, m, h, d, bt,
                         f'{v:+.10f}',
                         f'{Out_m:.6e}', f'{In_m:.6e}', f'{Delta_m:+.6e}',
                         f'{DeltaM_m:+.6e}',
                         Y, cutoff_d, cutoff_type, cutoff_phase_n2,
                         cutoff_dist_n2, cutoff_tau2, cutoff_wc,
                         cutoff_spf, cutoff_diag_k, cutoff_prime_dist,
                         cutoff_disagree,
                         payload2, payload2_tau2, payload2_wc,
                         payload2_spf, payload2_diag_k, payload2_prime_dist,
                         payload2_disagree,
                         payload3, payload3_tau2, payload3_wc,
                         payload3_spf, payload3_diag_k, payload3_prime_dist,
                         payload3_disagree))

        plot_lambda(n, lam, os.path.join(out_dir, f'lambda_n{n}.png'))
        plot_delta(n, flow, os.path.join(out_dir, f'delta_n{n}.png'))
        plot_delta_mertens(n, flow, os.path.join(out_dir, f'delta_mertens_n{n}.png'))

    # Write CSV
    csv_path = os.path.join(out_dir, 'acm_mangoldt.csv')
    with open(csv_path, 'w', newline='') as f:
        csv.writer(f).writerows(rows)
    print(f'\nwrote {csv_path}  ({len(rows) - 1} rows)')

    # Summary
    summary_path = os.path.join(out_dir, 'summary.txt')
    with open(summary_path, 'w') as f:
        f.write(f'ACM-Mangoldt flow tomography — X = {X}, base = {B}, n ∈ {NS}\n\n')

        f.write('=== L1: Λ_n by exact n-height ===\n')
        for n in NS:
            f.write(f'\nn = {n}\n')
            f.write(f'{"height":>6}  {"count":>6}  {"Λ>0":>5}  {"Λ<0":>5}  '
                    f'{"neg_mass/abs_mass":>17}\n')
            for h in sorted(height_summary[n]):
                count, pos, neg, neg_mass, abs_mass = height_summary[n][h]
                ratio = neg_mass / abs_mass if abs_mass else 0.0
                f.write(f'{h:>6}  {count:>6}  {pos:>5}  {neg:>5}  '
                        f'{ratio:>17.6f}\n')

        f.write('\n\n=== L3: Block-typed Δ totalisation ===\n')
        dmp = "Δ'>0"
        dmn = "Δ'<0"
        sd_m = "Σ Δ'"
        mean_d_m = "mean Δ'"
        ratio_d_m = "Σ Δ'/Σ Out"
        f.write(f'\n{"n":>3}  {"d":>2}  {"type":>12}  {"count":>6}  '
                f'{"Δ>0":>5}  {"Δ<0":>5}  '
                f'{dmp:>6}  {dmn:>6}  '
                f'{"Σ Out":>14}  {"Σ In":>14}  {"Σ Δ":>14}  '
                f'{sd_m:>14}  {mean_d_m:>14}  '
                f'{"Σ Δ/Σ Out":>11}  {ratio_d_m:>12}\n')
        for key in sorted(cell_totals):
            n, d, bt = key
            count, sOut, sIn, sDelta, sDeltaM, posD, negD, posDM, negDM = cell_totals[key]
            mean_delta_m = sDeltaM / count if count else 0.0
            ratio = sDelta / sOut if sOut > 0 else 0.0
            ratio_m = sDeltaM / sOut if sOut > 0 else 0.0
            f.write(f'{n:>3}  {d:>2}  {bt:>12}  {count:>6}  '
                    f'{posD:>5}  {negD:>5}  {posDM:>6}  {negDM:>6}  '
                    f'{sOut:>14.6e}  {sIn:>14.6e}  {sDelta:>+14.6e}  '
                    f'{sDeltaM:>+14.6e}  {mean_delta_m:>+14.6e}  '
                    f'{ratio:>11.4f}  {ratio_m:>12.4f}\n')

        f.write('\n\n=== L3b: Block-type residual rollup ===\n')
        f.write(f'\n{"type":>12}  {"count":>6}  {"Σ Out":>14}  '
                f'{"Σ Δ":>14}  {sd_m:>14}  '
                f'{"Σ Δ/Σ Out":>11}  {ratio_d_m:>12}\n')
        for bt in sorted(type_totals):
            count, sOut, sDelta, sDeltaM = type_totals[bt]
            ratio = sDelta / sOut if sOut > 0 else 0.0
            ratio_m = sDeltaM / sOut if sOut > 0 else 0.0
            f.write(f'{bt:>12}  {count:>6}  {sOut:>14.6e}  '
                    f'{sDelta:>+14.6e}  {sDeltaM:>+14.6e}  '
                    f'{ratio:>11.4f}  {ratio_m:>12.4f}\n')

        f.write('\n\n=== L4a: Cutoff n^2 phase residual ===\n')
        f.write(f'\n{"n":>3}  {"phase":>5}  {"count":>6}  {"dp_dis":>6}  '
                f'{"Σ Out":>14}  {sd_m:>14}  {ratio_d_m:>12}\n')
        for key in sorted(cutoff_phase_totals):
            n, phase = key
            count, sOut, sDeltaM, disagree = cutoff_phase_totals[key]
            ratio_m = sDeltaM / sOut if sOut > 0 else 0.0
            f.write(f'{n:>3}  {phase:>5}  {count:>6}  {disagree:>6}  '
                    f'{sOut:>14.6e}  {sDeltaM:>+14.6e}  {ratio_m:>12.4f}\n')

        f.write('\n\n=== L4b: Cutoff distance-to-n^2 residual ===\n')
        f.write(f'\n{"n":>3}  {"dist":>7}  {"count":>6}  {"dp_dis":>6}  '
                f'{"Σ Out":>14}  {sd_m:>14}  {ratio_d_m:>12}\n')
        dist_order = {name: i for i, name in enumerate(DIST_BUCKETS)}
        for key in sorted(cutoff_dist_totals, key=lambda x: (x[0], dist_order[x[1]])):
            n, bucket = key
            count, sOut, sDeltaM, disagree = cutoff_dist_totals[key]
            ratio_m = sDeltaM / sOut if sOut > 0 else 0.0
            f.write(f'{n:>3}  {bucket:>7}  {count:>6}  {disagree:>6}  '
                    f'{sOut:>14.6e}  {sDeltaM:>+14.6e}  {ratio_m:>12.4f}\n')

        f.write('\n\n=== L4c: Cutoff witness-count × block-type residual ===\n')
        f.write(f'\n{"type":>12}  {"cut_wc":>6}  {"count":>6}  {"dp_dis":>6}  '
                f'{"Σ Out":>14}  {sd_m:>14}  {ratio_d_m:>12}\n')
        for bt in sorted({key[0] for key in cutoff_wc_type_totals}):
            for bucket in WITNESS_BUCKETS:
                key = (bt, bucket)
                if key not in cutoff_wc_type_totals:
                    continue
                count, sOut, sDeltaM, disagree = cutoff_wc_type_totals[key]
                ratio_m = sDeltaM / sOut if sOut > 0 else 0.0
                f.write(f'{bt:>12}  {bucket:>6}  {count:>6}  {disagree:>6}  '
                        f'{sOut:>14.6e}  {sDeltaM:>+14.6e}  {ratio_m:>12.4f}\n')

        f.write('\n\n=== L4d: Cutoff tau2 × block-type residual ===\n')
        f.write(f'\n{"type":>12}  {"tau2":>6}  {"count":>6}  {"dp_dis":>6}  '
                f'{"Σ Out":>14}  {sd_m:>14}  {ratio_d_m:>12}\n')
        for bt in sorted({key[0] for key in cutoff_tau_type_totals}):
            for bucket in TAU_BUCKETS:
                key = (bt, bucket)
                if key not in cutoff_tau_type_totals:
                    continue
                count, sOut, sDeltaM, disagree = cutoff_tau_type_totals[key]
                ratio_m = sDeltaM / sOut if sOut > 0 else 0.0
                f.write(f'{bt:>12}  {bucket:>6}  {count:>6}  {disagree:>6}  '
                        f'{sOut:>14.6e}  {sDeltaM:>+14.6e}  {ratio_m:>12.4f}\n')

        f.write('\n\n=== L1b: Payload2 witness-count × block-type sign profile ===\n')
        f.write(f'\n{"type":>12}  {"p2_wc":>6}  {"count":>6}  {"dp_dis":>6}  '
                f'{"Λ>0":>5}  {"Λ<0":>5}  {"neg_mass/abs_mass":>17}\n')
        for bt in sorted({key[0] for key in payload2_wc_type_sign}):
            for bucket in WITNESS_BUCKETS:
                key = (bt, bucket)
                if key not in payload2_wc_type_sign:
                    continue
                count, pos, neg, neg_mass, abs_mass, disagree = payload2_wc_type_sign[key]
                ratio = neg_mass / abs_mass if abs_mass else 0.0
                f.write(f'{bt:>12}  {bucket:>6}  {count:>6}  {disagree:>6}  '
                        f'{pos:>5}  {neg:>5}  {ratio:>17.6f}\n')

        f.write('\n\n=== L1c: Payload2 tau2 sign profile ===\n')
        f.write(f'\n{"tau2":>6}  {"dp_dis":>6}  {"count":>6}  '
                f'{"Λ>0":>5}  {"Λ<0":>5}  {"neg_mass/abs_mass":>17}\n')
        tau_order = {name: i for i, name in enumerate(TAU_BUCKETS)}
        for key in sorted(payload2_tau_sign, key=lambda x: (tau_order[x[0]], x[1])):
            bucket, disagree_flag = key
            count, pos, neg, neg_mass, abs_mass, disagree = payload2_tau_sign[key]
            ratio = neg_mass / abs_mass if abs_mass else 0.0
            f.write(f'{bucket:>6}  {disagree_flag:>6}  {count:>6}  '
                    f'{pos:>5}  {neg:>5}  {ratio:>17.6f}\n')

        f.write('\n\n=== L1d: Payload3 witness-count × block-type sign profile ===\n')
        f.write(f'\n{"type":>12}  {"p3_wc":>6}  {"count":>6}  {"dp_dis":>6}  '
                f'{"Λ>0":>5}  {"Λ<0":>5}  {"neg_mass/abs_mass":>17}\n')
        for bt in sorted({key[0] for key in payload3_wc_type_sign}):
            for bucket in WITNESS_BUCKETS:
                key = (bt, bucket)
                if key not in payload3_wc_type_sign:
                    continue
                count, pos, neg, neg_mass, abs_mass, disagree = payload3_wc_type_sign[key]
                ratio = neg_mass / abs_mass if abs_mass else 0.0
                f.write(f'{bt:>12}  {bucket:>6}  {count:>6}  {disagree:>6}  '
                        f'{pos:>5}  {neg:>5}  {ratio:>17.6f}\n')

        f.write('\n\n=== L1e: Payload3 tau2 sign profile ===\n')
        f.write(f'\n{"tau2":>6}  {"dp_dis":>6}  {"count":>6}  '
                f'{"Λ>0":>5}  {"Λ<0":>5}  {"neg_mass/abs_mass":>17}\n')
        for key in sorted(payload3_tau_sign, key=lambda x: (tau_order[x[0]], x[1])):
            bucket, disagree_flag = key
            count, pos, neg, neg_mass, abs_mass, disagree = payload3_tau_sign[key]
            ratio = neg_mass / abs_mass if abs_mass else 0.0
            f.write(f'{bucket:>6}  {disagree_flag:>6}  {count:>6}  '
                    f'{pos:>5}  {neg:>5}  {ratio:>17.6f}\n')

    print(f'wrote {summary_path}')

    print('\ndone.')


if __name__ == '__main__':
    main()
