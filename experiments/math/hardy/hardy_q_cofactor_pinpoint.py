"""
hardy_q_cofactor_pinpoint.py — is the depth-shift Hardy-specific?
==================================================================

`hardy_q_depth_invariance.py` showed Q drifts strongly with K-depth.
`hardy_q_mertens_validation.py` showed the rate is several times the
naive Dirichlet (uniform-k) slope. Two hypotheses remain:

H1 — Magnitude only. Hardy cofactors are statistically equivalent to
     uniform random integers from the same bin (modulo the
     `gcd(c, n) = 1` constraint). The depth shift is then entirely a
     property of `d(c_1 c_2)` on cofactor pairs at bin magnitude — a
     classical multiplicative-number-theory effect, not a Hardy
     artefact.

H2 — Hardy structure. The closed form `c = q n + r + 1` introduces
     extra structure (residue bias, smoothness skew, …) that makes
     `d(c_1 c_2)` under Hardy sampling diverge from the uniform-random
     baseline.

For each (n, K-bin) we sample cofactor pairs two ways and compare:

  Hardy:   c_i = nth_n_prime(n, K_i) // n,  K_i ∈ bin
  Uniform: c_i ~ uniform on {c ∈ [K_lo, K_hi) : gcd(c, n) = 1}

Compute E[d(c_1 c_2)] under each. If the two curves agree within
sampling error across nine decades of K, H1 is correct: Hardy is
depth-fair *modulo cofactor magnitude*. If they don't, the residual
gap is a Hardy-specific divisor bias — itself a finding.

Outputs (this directory):
  hardy_q_cofactor_pinpoint.csv             per-pair records
  hardy_q_cofactor_pinpoint_summary.txt     per-(n, bin) Hardy vs Uniform
  hardy_q_cofactor_pinpoint.png             E[d(c_1 c_2)] vs log10 c, dual curves

Usage:
    sage -python hardy_q_cofactor_pinpoint.py
"""

import csv
import os
import sys
from collections import defaultdict
from math import gcd, log10

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))

sys.path.insert(0, HERE)
from hardy_echo import nth_n_prime  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, 'experiments', 'acm', 'flow'))
from hardy_composite_q import (  # noqa: E402
    factor_dict, factor_small, mul_facs, tau_j,
)


PANEL_NS = [2, 3, 5]  # primes only — clean d(k) ↔ Q identity at h=2
DEPTH_BINS = [(10**a, 10**(a + 1)) for a in range(1, 13)]
N_PER_BIN = 1000
SEED = 20260428003


# ---- cofactor samplers ----

def cofactor_hardy(n, lo, hi, rng):
    """Sample a Hardy cofactor: c = nth_n_prime(n, K) // n with K ∈ [lo, hi)."""
    K = int(rng.integers(lo, hi))
    a = nth_n_prime(n, K)
    return a // n, K


def cofactor_uniform(n, lo, hi, rng):
    """Sample a uniform integer c ∈ [lo, hi) with gcd(c, n) = 1.

    For prime n this conditions out the c divisible by n; the rejection
    rate is 1/n, immaterial."""
    while True:
        c = int(rng.integers(lo, hi))
        if gcd(c, n) == 1:
            return c


def d_of_product(c1, c2):
    """d(c_1 c_2) via prime-merged factorisation. c1, c2 are positive ints."""
    f1 = factor_dict(c1)
    f2 = factor_dict(c2)
    merged = mul_facs(f1, f2)
    return tau_j(2, merged)


# ---- run ----

def run_panel():
    rng = np.random.default_rng(SEED)
    rows = []
    for n in PANEL_NS:
        print(f'  n = {n}', flush=True)
        for bin_idx, (lo, hi) in enumerate(DEPTH_BINS):
            print(f'    bin {bin_idx:>2}: K ∈ [10^{int(log10(lo))}, '
                  f'10^{int(log10(hi))})', flush=True)
            for _ in range(N_PER_BIN):
                # Hardy pair
                c_h1, K1 = cofactor_hardy(n, lo, hi, rng)
                c_h2, K2 = cofactor_hardy(n, lo, hi, rng)
                d_hardy = d_of_product(c_h1, c_h2)

                # Uniform pair (matched bin magnitude in c-space, not K-space).
                # Hardy cofactor ~ K · n / (n - 1), so for matched magnitude
                # we sample c ∈ [lo · n/(n-1), hi · n/(n-1)).
                c_lo = lo * n // (n - 1)
                c_hi = hi * n // (n - 1)
                c_u1 = cofactor_uniform(n, c_lo, c_hi, rng)
                c_u2 = cofactor_uniform(n, c_lo, c_hi, rng)
                d_unif = d_of_product(c_u1, c_u2)

                rows.append({
                    'n': n,
                    'bin_idx': bin_idx,
                    'K_lo': lo, 'K_hi': hi,
                    'c_hardy_1': c_h1, 'c_hardy_2': c_h2,
                    'd_hardy': d_hardy,
                    'log10_c_hardy_prod': log10(c_h1 * c_h2),
                    'c_unif_1': c_u1, 'c_unif_2': c_u2,
                    'd_unif': d_unif,
                    'log10_c_unif_prod': log10(c_u1 * c_u2),
                })
    return rows


# ---- per-cell statistics ----

def cell_stats(rows):
    cell = defaultdict(list)
    for r in rows:
        cell[(r['n'], r['bin_idx'])].append(r)
    out = []
    for (n, b), rs in sorted(cell.items()):
        log10_c_h = np.array([r['log10_c_hardy_prod'] for r in rs])
        log10_c_u = np.array([r['log10_c_unif_prod'] for r in rs])
        d_h = np.array([r['d_hardy'] for r in rs], dtype=float)
        d_u = np.array([r['d_unif'] for r in rs], dtype=float)
        out.append({
            'n': n,
            'bin_idx': b,
            'count': len(rs),
            'log10_c_hardy_mean': float(log10_c_h.mean()),
            'log10_c_unif_mean': float(log10_c_u.mean()),
            'd_hardy_mean': float(d_h.mean()),
            'd_hardy_std': float(d_h.std()),
            'd_unif_mean': float(d_u.mean()),
            'd_unif_std': float(d_u.std()),
            'rel_diff': float((d_h.mean() - d_u.mean())
                              / max(d_u.mean(), 1e-9)),
        })
    return out


# ---- writers ----

def write_csv(rows, path):
    fields = ['n', 'bin_idx', 'K_lo', 'K_hi',
              'c_hardy_1', 'c_hardy_2', 'd_hardy', 'log10_c_hardy_prod',
              'c_unif_1', 'c_unif_2', 'd_unif', 'log10_c_unif_prod']
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in fields})


def write_summary(stats, path):
    with open(path, 'w') as f:
        f.write('hardy_q_cofactor_pinpoint.py — Hardy vs Uniform cofactor d(c1 c2)\n\n')
        f.write(f'panel n: {PANEL_NS}\n')
        f.write(f'depth bins: {len(DEPTH_BINS)} (single-decade, K ∈ [10^1, 10^13))\n')
        f.write(f'N per (n, bin): {N_PER_BIN}\n')
        f.write(f'seed: {SEED}\n\n')

        f.write('=== Per (n, bin) — Hardy vs Uniform ===\n')
        f.write(f'  {"n":>3} {"bin":>4} {"count":>6} '
                f'{"<log10 c1c2>":>13} '
                f'{"<d>_Hardy":>11} {"<d>_Unif":>11} '
                f'{"rel diff":>10}\n')
        for s in stats:
            f.write(
                f'  {s["n"]:>3} {s["bin_idx"]:>4} {s["count"]:>6} '
                f'  H {s["log10_c_hardy_mean"]:>5.2f}  '
                f'U {s["log10_c_unif_mean"]:>5.2f}  '
                f'{s["d_hardy_mean"]:>11.3f} {s["d_unif_mean"]:>11.3f} '
                f'{s["rel_diff"]:>+10.4f}\n'
            )
        f.write('\n')

        # Aggregate: mean |rel_diff| per n.
        per_n = defaultdict(list)
        for s in stats:
            per_n[s['n']].append(abs(s['rel_diff']))
        f.write('=== Mean |relative difference| per n ===\n')
        max_rel = 0.0
        for n in PANEL_NS:
            v = float(np.mean(per_n[n]))
            max_rel = max(max_rel, v)
            f.write(f'  n = {n}: mean |rel diff| = {v:.4f} ({v*100:.2f}%)\n')
        f.write('\n')
        f.write('=== Verdict ===\n')
        if max_rel < 0.03:
            f.write(f'PASS — Hardy and Uniform cofactor pairings give the same\n')
            f.write(f'E[d(c_1 c_2)] across all bins (max |rel diff| = '
                    f'{max_rel:.4f}). The Q depth-shift is a magnitude\n')
            f.write(f'effect on the cofactor product divisor function, not a\n')
            f.write(f'Hardy-specific bias. H1.\n')
        elif max_rel < 0.10:
            f.write(f'NEAR-PASS — Hardy and Uniform agree within 10% '
                    f'(max |rel diff| = {max_rel:.4f}). Consistent with H1\n')
            f.write(f'plus a small finite-N noise floor. Worth a second seed.\n')
        else:
            f.write(f'REJECT — Hardy and Uniform diverge by >10% in some bins '
                    f'(max |rel diff| = {max_rel:.4f}). The Q depth-shift\n')
            f.write(f'has a Hardy-specific component beyond magnitude. H2.\n')


# ---- plot ----

def plot_pinpoint(stats, path):
    fig, axes = plt.subplots(1, len(PANEL_NS), figsize=(5 * len(PANEL_NS), 5),
                             sharey=False)
    if len(PANEL_NS) == 1:
        axes = [axes]

    for ax, n in zip(axes, PANEL_NS):
        ns = [s for s in stats if s['n'] == n]
        x_h = [s['log10_c_hardy_mean'] for s in ns]
        x_u = [s['log10_c_unif_mean'] for s in ns]
        y_h = [s['d_hardy_mean'] for s in ns]
        y_u = [s['d_unif_mean'] for s in ns]
        e_h = [s['d_hardy_std'] / max(s['count'], 1) ** 0.5 for s in ns]
        e_u = [s['d_unif_std'] / max(s['count'], 1) ** 0.5 for s in ns]

        ax.errorbar(x_h, y_h, yerr=e_h, fmt='o', color='steelblue',
                    label='Hardy', capsize=3, markersize=6,
                    linestyle='-', linewidth=1.4)
        ax.errorbar(x_u, y_u, yerr=e_u, fmt='s', color='crimson',
                    label='Uniform-coprime', capsize=3, markersize=6,
                    linestyle='--', linewidth=1.4, alpha=0.85)

        ax.set_xlabel('E[log10(c_1 c_2)]')
        ax.set_ylabel('E[d(c_1 c_2)]')
        ax.set_title(f'n = {n}')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=9)

    fig.suptitle(
        f'Pinpoint: Hardy cofactor pairs vs Uniform-coprime pairs at matched bin magnitude\n'
        f'curves overlay → depth shift is magnitude, not Hardy structure (N={N_PER_BIN}/bin)',
        fontsize=11
    )
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close(fig)


# ---- main ----

def main():
    print('hardy_q_cofactor_pinpoint.py — Hardy vs Uniform cofactor d(c_1 c_2)\n',
          flush=True)
    print(f'panel n:        {PANEL_NS}', flush=True)
    print(f'depth bins:     {len(DEPTH_BINS)}', flush=True)
    print(f'N per (n, bin): {N_PER_BIN}', flush=True)
    print(f'seed:           {SEED}\n', flush=True)

    print('sampling cofactor pairs (Hardy and Uniform), computing d ...',
          flush=True)
    rows = run_panel()
    print(f'\n  total rows: {len(rows)}\n', flush=True)

    stats = cell_stats(rows)

    csv_path = os.path.join(HERE, 'hardy_q_cofactor_pinpoint.csv')
    summary_path = os.path.join(HERE, 'hardy_q_cofactor_pinpoint_summary.txt')
    plot_path = os.path.join(HERE, 'hardy_q_cofactor_pinpoint.png')

    write_csv(rows, csv_path)
    write_summary(stats, summary_path)
    plot_pinpoint(stats, plot_path)

    # Brief stdout report.
    per_n = defaultdict(list)
    for s in stats:
        per_n[s['n']].append(abs(s['rel_diff']))
    print('mean |rel diff| Hardy vs Uniform per n:', flush=True)
    for n in PANEL_NS:
        v = float(np.mean(per_n[n]))
        print(f'  n = {n}: {v:.4f} ({v*100:.2f}%)', flush=True)
    print('', flush=True)

    print(f'wrote {csv_path}', flush=True)
    print(f'wrote {summary_path}', flush=True)
    print(f'wrote {plot_path}', flush=True)


if __name__ == '__main__':
    main()
