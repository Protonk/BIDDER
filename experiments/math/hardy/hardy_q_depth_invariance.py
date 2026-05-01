"""
hardy_q_depth_invariance.py — does Hardy sample M_n fairly by Q?
=================================================================

`experiments/acm/flow/hardy_composite_q.py` (Phase 2.4) verified the
Q-formula at depth — it tested the *algebra*. This script tests the
*sampler*: when we draw composite m via Hardy r = 2 atom pairs at
depth K = 10^12, is the resulting Q_n distribution the same as when we
draw at depth K = 10^3?

If yes, Hardy is depth-fair for Q purposes — a clean licence for
Phase 4 to treat it as a uniform-by-height sampler of M_n. If no,
there is a cofactor bias at depth that downstream predictions must
model. Either outcome is a finding.

For each n ∈ {2, 3, 4, 6}:
  - four K-depth bins: [10^3, 10^4), [10^6, 10^7),
                       [10^9, 10^10), [10^12, 10^13);
  - N = 1000 random K-pairs per bin (r = 2);
  - compute m = a_{K_1} · a_{K_2}, measure h = ν_n(m), evaluate Q via
    the master path from `hardy_composite_q.q_master`.

Per (n, h) cell with sample count ≥ 30 in two bins, two-sample KS the
Q distributions pairwise (6 bin-pairs per cell). The null prediction
is depth invariance — KS fails to reject for every cell. Any rejection
is a real finding about Hardy as a sampler.

Outputs (this directory):
  hardy_q_depth_invariance.csv         per-tuple records
  hardy_q_depth_invariance_summary.txt KS table by (n, h, bin-pair)
  hardy_q_depth_invariance.png         2x2 overlay histograms by n
  hardy_q_depth_invariance_cells.png   per (n, h) small-multiples diagnostic

Usage:
    sage -python hardy_q_depth_invariance.py
"""

import csv
import os
import sys
from collections import defaultdict
from itertools import combinations

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))

sys.path.insert(0, HERE)
from hardy_echo import nth_n_prime  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, 'experiments', 'acm', 'flow'))
from hardy_composite_q import (  # noqa: E402
    factor_dict, factor_small, mul_facs, height_n, q_master,
)


PANEL_NS = [2, 3, 4, 6]
DEPTH_BINS = [
    (10**3, 10**4),
    (10**6, 10**7),
    (10**9, 10**10),
    (10**12, 10**13),
]
N_PER_BIN = 1000
SEED = 20260428
KS_ALPHA = 0.05
MIN_CELL = 30


# ---- sampling and evaluation ----

def sample_K_pair(rng, lo, hi):
    """Random ordered K-pair (K_1 < K_2) drawn uniformly from [lo, hi)."""
    while True:
        K1 = int(rng.integers(lo, hi))
        K2 = int(rng.integers(lo, hi))
        if K1 != K2:
            return (K1, K2) if K1 < K2 else (K2, K1)


def evaluate(n, K_pair):
    n_facs = factor_small(n)
    a1 = nth_n_prime(n, K_pair[0])
    a2 = nth_n_prime(n, K_pair[1])
    cof_facs1 = factor_dict(a1 // n)
    cof_facs2 = factor_dict(a2 // n)
    a1_facs = mul_facs(n_facs, cof_facs1)
    a2_facs = mul_facs(n_facs, cof_facs2)
    m_facs = mul_facs(a1_facs, a2_facs)
    h = height_n(m_facs, n_facs)
    Q = q_master(m_facs, n_facs, h)
    return h, Q


def run_panel():
    rng = np.random.default_rng(SEED)
    rows = []
    for n in PANEL_NS:
        print(f'  n = {n}', flush=True)
        for bin_idx, (lo, hi) in enumerate(DEPTH_BINS):
            print(f'    bin {bin_idx}: K ∈ [{lo}, {hi})', flush=True)
            for _ in range(N_PER_BIN):
                K_pair = sample_K_pair(rng, lo, hi)
                h, Q = evaluate(n, K_pair)
                rows.append({
                    'n': n, 'bin_idx': bin_idx,
                    'K_lo': lo, 'K_hi': hi,
                    'K_1': K_pair[0], 'K_2': K_pair[1],
                    'h': h,
                    'q_num': Q.numerator,
                    'q_den': Q.denominator,
                    'q_float': float(Q),
                })
    return rows


# ---- KS table ----

def ks_table(rows):
    """For each (n, h, bin-pair), pairwise KS on Q values.
    Skips cells where either bin has fewer than MIN_CELL samples."""
    by_cell = defaultdict(list)
    for r in rows:
        by_cell[(r['n'], r['h'], r['bin_idx'])].append(r['q_float'])

    out = []
    for (n, h) in sorted({(r['n'], r['h']) for r in rows}):
        for a, b in combinations(range(len(DEPTH_BINS)), 2):
            xs = by_cell.get((n, h, a), [])
            ys = by_cell.get((n, h, b), [])
            if len(xs) < MIN_CELL or len(ys) < MIN_CELL:
                continue
            ks_stat, ks_p = stats.ks_2samp(xs, ys)
            out.append({
                'n': n, 'h': h,
                'bin_a': a, 'bin_b': b,
                'count_a': len(xs), 'count_b': len(ys),
                'ks_stat': float(ks_stat),
                'ks_p': float(ks_p),
            })
    return out


# ---- writers ----

def write_csv(rows, path):
    fields = ['n', 'bin_idx', 'K_lo', 'K_hi', 'K_1', 'K_2',
              'h', 'q_num', 'q_den', 'q_float']
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in fields})


def write_summary(rows, ks_rows, path):
    cell_count = defaultdict(int)
    for r in rows:
        cell_count[(r['n'], r['h'], r['bin_idx'])] += 1
    n_pass = sum(1 for k in ks_rows if k['ks_p'] >= KS_ALPHA)
    n_fail = sum(1 for k in ks_rows if k['ks_p'] < KS_ALPHA)

    with open(path, 'w') as f:
        f.write('hardy_q_depth_invariance.py — sampler fairness across depth\n\n')
        f.write(f'panel n: {PANEL_NS}\n')
        f.write(f'depth bins: {DEPTH_BINS}\n')
        f.write(f'N per (n, bin): {N_PER_BIN}\n')
        f.write(f'r = 2 (atom pairs)\n')
        f.write(f'seed: {SEED}\n')
        f.write(f'KS α: {KS_ALPHA}\n')
        f.write(f'cell minimum: {MIN_CELL}\n\n')

        f.write('=== Sample counts per (n, h, bin_idx) ===\n')
        for n in PANEL_NS:
            hs = sorted({r['h'] for r in rows if r['n'] == n})
            for h in hs:
                counts = [cell_count.get((n, h, b), 0)
                          for b in range(len(DEPTH_BINS))]
                f.write(f'  n={n} h={h}  by bin: {counts}\n')
        f.write('\n')

        f.write('=== Pairwise KS — Q_float distributions across depth bins ===\n')
        f.write(f'  cells with both counts >= {MIN_CELL}; '
                f'a < b means bin_a is shallower\n')
        f.write(f'  {"n":>3} {"h":>3} {"a":>3} {"b":>3} '
                f'{"n_a":>6} {"n_b":>6} {"KS":>8} {"p":>10}  flag\n')
        for k in ks_rows:
            flag = 'OK' if k['ks_p'] >= KS_ALPHA else 'REJECT'
            f.write(
                f'  {k["n"]:>3} {k["h"]:>3} {k["bin_a"]:>3} {k["bin_b"]:>3} '
                f'{k["count_a"]:>6} {k["count_b"]:>6} '
                f'{k["ks_stat"]:>8.4f} {k["ks_p"]:>10.3e}  {flag}\n'
            )
        f.write('\n')

        # Per-(n, h) cell worst-case p over bin pairs (informational).
        worst_per_cell = {}
        for k in ks_rows:
            key = (k['n'], k['h'])
            if key not in worst_per_cell or k['ks_p'] < worst_per_cell[key]['ks_p']:
                worst_per_cell[key] = k
        if worst_per_cell:
            f.write('=== Per-(n, h) worst KS p across bin-pairs ===\n')
            for (n, h), k in sorted(worst_per_cell.items()):
                flag = 'OK' if k['ks_p'] >= KS_ALPHA else 'REJECT'
                f.write(
                    f'  n={n} h={h}: '
                    f'min p = {k["ks_p"]:.3e}  '
                    f'(bins {k["bin_a"]} vs {k["bin_b"]}, '
                    f'KS={k["ks_stat"]:.4f})  {flag}\n'
                )
            f.write('\n')

        f.write('=== Verdict ===\n')
        f.write(f'KS pairs OK   (p >= {KS_ALPHA}): {n_pass}\n')
        f.write(f'KS pairs FAIL (p <  {KS_ALPHA}): {n_fail}\n')
        if n_fail == 0:
            f.write('PASS — Q distribution depth-invariant for every (n, h, '
                    'bin-pair) tested. Hardy is depth-fair as a Q sampler at '
                    'r = 2 over this panel.\n')
        else:
            f.write('FINDING — at least one (n, h) cell shows depth-dependent\n')
            f.write('shift in the Q distribution. Hardy is not a uniform-by-\n')
            f.write('height Q sampler in those cells. This is a real Phase 4\n')
            f.write('caveat, not a Phase 2 failure: the Q formula is exact\n')
            f.write('(Phase 2.4); the cofactor distribution under deep Hardy\n')
            f.write('is what shifts.\n')


# ---- plots ----

def _bin_labels():
    out = []
    for lo, hi in DEPTH_BINS:
        out.append(f'K∈[10^{int(np.log10(lo))}, 10^{int(np.log10(hi))})')
    return out


def plot_overlay(rows, ks_rows, path):
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    axes = axes.flatten()
    bin_colors = plt.cm.viridis(np.linspace(0.15, 0.85, len(DEPTH_BINS)))
    bin_labels = _bin_labels()

    worst_per_n = {}
    for k in ks_rows:
        n = k['n']
        if n not in worst_per_n or k['ks_p'] < worst_per_n[n]['ks_p']:
            worst_per_n[n] = k

    for ax, n in zip(axes, PANEL_NS):
        cell_qs = defaultdict(list)
        for r in rows:
            if r['n'] == n:
                cell_qs[r['bin_idx']].append(r['q_float'])
        all_qs = np.concatenate([np.asarray(v) for v in cell_qs.values()]) \
            if cell_qs else np.array([])
        if len(all_qs) == 0:
            continue
        lo_q, hi_q = np.percentile(all_qs, [1, 99])
        if lo_q == hi_q:
            lo_q -= 1
            hi_q += 1
        bins = np.linspace(lo_q, hi_q, 51)

        for b in range(len(DEPTH_BINS)):
            qs = np.asarray(cell_qs.get(b, []))
            if len(qs) == 0:
                continue
            ax.hist(qs, bins=bins, alpha=0.45, density=True,
                    color=bin_colors[b], label=bin_labels[b],
                    histtype='stepfilled', edgecolor=bin_colors[b])

        worst = worst_per_n.get(n)
        title_extra = ''
        if worst:
            flag = 'OK' if worst['ks_p'] >= KS_ALPHA else 'REJECT'
            title_extra = (
                f'  [worst KS p = {worst["ks_p"]:.2e}, '
                f'h={worst["h"]}, bins {worst["bin_a"]}↔{worst["bin_b"]}, '
                f'{flag}]'
            )
        ax.set_title(f'n = {n}{title_extra}', fontsize=10)
        ax.set_xlabel('Q_n  (1–99 percentile clipped for display)')
        ax.set_ylabel('density')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=7, loc='best')

    fig.suptitle(
        f'Hardy r=2 composite-Q distribution across depth  '
        f'(N={N_PER_BIN} K-pairs per (n, depth bin))'
    )
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close(fig)


def plot_cells(rows, path):
    by_cell = defaultdict(list)
    for r in rows:
        by_cell[(r['n'], r['h'], r['bin_idx'])].append(r['q_float'])

    cells_per_n = {}
    for n in PANEL_NS:
        hs = sorted({r['h'] for r in rows if r['n'] == n})
        hs = [h for h in hs if any(
            len(by_cell.get((n, h, b), [])) >= MIN_CELL
            for b in range(len(DEPTH_BINS))
        )]
        cells_per_n[n] = hs
    max_cols = max((len(v) for v in cells_per_n.values()), default=0)
    if max_cols == 0:
        return

    fig, axes = plt.subplots(
        len(PANEL_NS), max_cols,
        figsize=(3.6 * max_cols, 2.7 * len(PANEL_NS)),
        squeeze=False,
    )
    bin_colors = plt.cm.viridis(np.linspace(0.15, 0.85, len(DEPTH_BINS)))
    bin_labels = _bin_labels()

    for i, n in enumerate(PANEL_NS):
        for j in range(max_cols):
            ax = axes[i][j]
            if j >= len(cells_per_n[n]):
                ax.axis('off')
                continue
            h = cells_per_n[n][j]
            cell_q_lists = [by_cell.get((n, h, b), []) for b in range(len(DEPTH_BINS))]
            present = [v for v in cell_q_lists if len(v) >= MIN_CELL]
            if not present:
                ax.axis('off')
                continue
            all_qs = np.concatenate([np.asarray(v) for v in present])
            lo_q, hi_q = np.percentile(all_qs, [1, 99])
            if lo_q == hi_q:
                lo_q -= 1
                hi_q += 1
            bins = np.linspace(lo_q, hi_q, 31)
            for b, qs in enumerate(cell_q_lists):
                qs = np.asarray(qs)
                if len(qs) < MIN_CELL:
                    continue
                ax.hist(qs, bins=bins, alpha=0.5, density=True,
                        color=bin_colors[b], histtype='stepfilled',
                        edgecolor=bin_colors[b],
                        label=bin_labels[b] if (i, j) == (0, 0) else None)
            counts = [len(v) for v in cell_q_lists]
            ax.set_title(f'n={n}, h={h}  counts={counts}', fontsize=9)
            ax.tick_params(axis='both', labelsize=7)
            ax.grid(True, alpha=0.25)
            if (i, j) == (0, 0):
                ax.legend(fontsize=7, loc='best')

    fig.suptitle(
        'Per-cell Hardy r=2 composite-Q distribution by depth bin '
        '(viridis colour: shallow → deep)'
    )
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close(fig)


# ---- main ----

def main():
    print('hardy_q_depth_invariance.py — sampler fairness across depth\n', flush=True)
    print(f'panel n:        {PANEL_NS}', flush=True)
    print(f'depth bins:     {DEPTH_BINS}', flush=True)
    print(f'N per (n, bin): {N_PER_BIN}', flush=True)
    print(f'seed:           {SEED}\n', flush=True)

    print('sampling and computing Q ...', flush=True)
    rows = run_panel()
    print(f'\n  total rows: {len(rows)}\n', flush=True)

    print('KS table ...', flush=True)
    ks_rows = ks_table(rows)
    n_pass = sum(1 for k in ks_rows if k['ks_p'] >= KS_ALPHA)
    n_fail = sum(1 for k in ks_rows if k['ks_p'] < KS_ALPHA)
    print(f'  KS pairs OK   (p >= {KS_ALPHA}): {n_pass}', flush=True)
    print(f'  KS pairs FAIL (p <  {KS_ALPHA}): {n_fail}\n', flush=True)

    csv_path = os.path.join(HERE, 'hardy_q_depth_invariance.csv')
    summary_path = os.path.join(HERE, 'hardy_q_depth_invariance_summary.txt')
    overlay_path = os.path.join(HERE, 'hardy_q_depth_invariance.png')
    cells_path = os.path.join(HERE, 'hardy_q_depth_invariance_cells.png')

    write_csv(rows, csv_path)
    write_summary(rows, ks_rows, summary_path)
    plot_overlay(rows, ks_rows, overlay_path)
    plot_cells(rows, cells_path)

    print(f'wrote {csv_path}', flush=True)
    print(f'wrote {summary_path}', flush=True)
    print(f'wrote {overlay_path}', flush=True)
    print(f'wrote {cells_path}', flush=True)


if __name__ == '__main__':
    main()
