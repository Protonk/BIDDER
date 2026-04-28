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
from fractions import Fraction
from math import log

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


NS = [2, 3, 4, 5, 6, 10]
X = 10000
B = 10  # base for the digit-class partition
EPS = 1e-12


# ---------- core arithmetic ----------

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
             'Lambda', 'Out', 'In', 'Delta', 'DeltaMertens')]
    height_summary = {}
    cell_totals = defaultdict(lambda: [0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0, 0])
    # cell key (n, d, block_type) →
    # [count, sumOut, sumIn, sumDelta, sumDeltaMertens,
    #  posDelta, negDelta, posDeltaMertens, negDeltaMertens]
    type_totals = defaultdict(lambda: [0, 0.0, 0.0, 0.0])
    # block_type → [count, sumOut, sumDelta, sumDeltaMertens]
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
            d = len(str(m))
            bt = block_classify(n, d, B)
            Out_m, In_m, Delta_m, DeltaM_m = flow[m]
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

            rows.append((n, m, n_height(n, m), d, bt,
                         f'{v:+.10f}',
                         f'{Out_m:.6e}', f'{In_m:.6e}', f'{Delta_m:+.6e}',
                         f'{DeltaM_m:+.6e}'))

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

    print(f'wrote {summary_path}')

    print('\ndone.')


if __name__ == '__main__':
    main()
