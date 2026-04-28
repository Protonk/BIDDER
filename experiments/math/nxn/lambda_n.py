"""
lambda_n.py — Λ_{M_n} sign-table diagnostic
============================================

Computes the monoid Mangoldt function on M_n = {1} ∪ nℤ⁺,

    Λ_{M_n}(m)  =  log(m) · Σ_{j ≥ 1, n^j | m} (-1)^(j-1) τ_j(m/n^j) / j

where τ_j is the j-fold ordered divisor function. Sign of Λ_{M_n}(m)
is the sign of the rational
`Q_n(m) = Σ (-1)^(j-1) τ_j(m/n^j)/j`, since `log m > 0` for `m ≥ 2`.

Outputs (this directory):
  poset_factor.csv          (n, m, Q rational, Λ value, sign)
  lambda_n{n}.png           per-n scatter of Λ_n(m) vs m, coloured by sign
  lambda_sign_strip.png     negativity-locus strip across n
  sign_summary.txt          per-n: count, first negative locus

Brief: POSET-FACTOR.md.

Usage:
    sage -python lambda_n.py
"""

import csv
import os
from fractions import Fraction
from math import log

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


NS = [2, 3, 4, 5, 6, 10]
MMAX = 10000


def tau_table(mmax, j_max):
    """τ_j(k) for 1 ≤ k ≤ mmax, 1 ≤ j ≤ j_max.
    Returns tau[j-1][k] = τ_j(k). τ_1 ≡ 1; τ_{j+1}(k) = Σ_{d | k} τ_j(d)."""
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


def lambda_n_sweep(n, mmax, tau):
    """For m ∈ M_n ∩ [n, mmax], compute (m, Q_n(m), Λ value).
    Λ_{M_n}(m) = log(m) · Q_n(m). Q is exact (Fraction)."""
    out = []
    j_max = len(tau)
    for m in range(n, mmax + 1, n):
        Q = Fraction(0)
        nj = 1
        for jx in range(1, j_max + 1):
            nj *= n
            if m % nj != 0:
                break
            mj = m // nj
            sgn = 1 if (jx % 2) == 1 else -1
            Q += Fraction(sgn * tau[jx - 1][mj], jx)
        out.append((m, Q, log(m) * float(Q)))
    return out


def per_n_plot(n, sweep, out_path):
    ms = np.array([m for m, _, _ in sweep])
    lams = np.array([v for _, _, v in sweep])
    Qs = [Q for _, Q, _ in sweep]
    pos = np.array([Q > 0 for Q in Qs])
    neg = np.array([Q < 0 for Q in Qs])
    zero = np.array([Q == 0 for Q in Qs])

    fig, ax = plt.subplots(figsize=(13, 4))
    if pos.any():
        ax.scatter(ms[pos], lams[pos], s=3, c='steelblue', alpha=0.6,
                   label=f'Λ > 0 ({int(pos.sum())})')
    if neg.any():
        ax.scatter(ms[neg], lams[neg], s=10, c='crimson', alpha=0.85,
                   label=f'Λ < 0 ({int(neg.sum())})')
    if zero.any():
        ax.scatter(ms[zero], lams[zero], s=10, c='gray', alpha=0.7,
                   label=f'Λ = 0 ({int(zero.sum())})')
    ax.axhline(0, color='black', lw=0.5, alpha=0.5)
    ax.set_xscale('log')
    ax.set_xlabel('m  (log scale)')
    ax.set_ylabel(r'$\Lambda_{M_n}(m)$  [nats]')
    ax.set_title(f'Λ$_{{M_{n}}}$(m) on m ∈ M$_{n}$ ∩ [{n}, {MMAX}]')
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close(fig)


def sign_strip_plot(sweeps, out_path):
    fig, ax = plt.subplots(figsize=(13, len(NS) * 0.55 + 1.2))
    for i, n in enumerate(NS):
        sweep = sweeps[n]
        neg_ms = [m for m, Q, _ in sweep if Q < 0]
        zero_ms = [m for m, Q, _ in sweep if Q == 0]
        if neg_ms:
            ax.scatter(neg_ms, [i] * len(neg_ms), s=4, c='crimson', alpha=0.7)
        if zero_ms:
            ax.scatter(zero_ms, [i] * len(zero_ms), s=4, c='gray', alpha=0.5)
    ax.set_xscale('log')
    ax.set_yticks(range(len(NS)))
    ax.set_yticklabels([f'n={n}' for n in NS])
    ax.set_xlabel('m  (log scale)')
    ax.set_title(f'Λ$_{{M_n}}$(m) negativity locus, m ≤ {MMAX}  (red = Λ<0, gray = Λ=0)')
    ax.set_xlim(1.5, MMAX * 1.1)
    ax.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close(fig)


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))

    j_max = 1
    while min(NS) ** j_max <= MMAX:
        j_max += 1
    print(f'pre-computing τ_j for j = 1..{j_max}, k ≤ {MMAX}', flush=True)
    tau = tau_table(MMAX, j_max)
    print(f'  done — max τ_j seen: {max(tau[j_max - 1])}', flush=True)

    rows = [('n', 'm', 'Q_rational', 'Lambda_value', 'sign')]
    summary = []
    sweeps = {}

    for n in NS:
        print(f'\n--- n = {n} ---', flush=True)
        sweep = lambda_n_sweep(n, MMAX, tau)
        sweeps[n] = sweep
        n_total = len(sweep)
        n_neg = sum(1 for _, Q, _ in sweep if Q < 0)
        n_zero = sum(1 for _, Q, _ in sweep if Q == 0)
        first_neg = next(((m, Q, v) for m, Q, v in sweep if Q < 0), None)

        print(f'  |M_{n} ∩ [{n}, {MMAX}]|: {n_total}')
        print(f'  Λ < 0: {n_neg}   Λ = 0: {n_zero}')
        if first_neg:
            m0, Q0, v0 = first_neg
            print(f'  first Λ < 0:  Λ_{{M_{n}}}({m0}) = {float(Q0):+.6f} · log m  =  {v0:+.6f}')
        else:
            print(f'  no negativity in tested range')

        for m, Q, v in sweep:
            sgn = '+' if Q > 0 else ('-' if Q < 0 else '0')
            rows.append((n, m, str(Q), f'{v:+.10f}', sgn))
        summary.append((n, n_total, n_neg, n_zero,
                        first_neg[0] if first_neg else None,
                        float(first_neg[1]) if first_neg else None))

        per_n_plot(n, sweep, os.path.join(out_dir, f'lambda_n{n}.png'))

    sign_strip_plot(sweeps, os.path.join(out_dir, 'lambda_sign_strip.png'))

    csv_path = os.path.join(out_dir, 'poset_factor.csv')
    with open(csv_path, 'w', newline='') as f:
        csv.writer(f).writerows(rows)
    print(f'\nwrote {csv_path}  ({len(rows) - 1} rows)')

    summary_path = os.path.join(out_dir, 'sign_summary.txt')
    with open(summary_path, 'w') as f:
        f.write(f'Λ_{{M_n}}(m) sign-table summary, m up to {MMAX}\n\n')
        f.write(f'{"n":>3}  {"|sweep|":>8}  {"|Λ<0|":>6}  {"|Λ=0|":>6}  '
                f'{"first_neg_m":>11}  {"first_neg_Q":>12}\n')
        for n, total, neg, zero, fnm, fnq in summary:
            fnm_s = str(fnm) if fnm is not None else '—'
            fnq_s = f'{fnq:+.6f}' if fnq is not None else '—'
            f.write(f'{n:>3}  {total:>8}  {neg:>6}  {zero:>6}  '
                    f'{fnm_s:>11}  {fnq_s:>12}\n')
    print(f'wrote {summary_path}')


if __name__ == '__main__':
    main()
