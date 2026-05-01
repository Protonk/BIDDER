"""
exp04_pareto.py — best-fitting C_Surv at maximum length.

For each (n_0, W, k) configuration, compute:
    L = total digit length of C_Surv  (= sum_{m in survivors} len(str(m)))
    D = leading-digit L1 deviation from uniform (each survivor counted once)

Question: is there a configuration that simultaneously maximises L
and minimises D? I.e., is there a Pareto-optimal "sweet spot" with
large length AND small L1?

Sweep:
    W ∈ {3, 5, 7, 10, 15, 20}      (window widths)
    n_0 ∈ [2, 80]                   (window left edge)
    k ∈ [5, 500] step 5             (truncation)

For each, also record the *trajectory minimum* of L1 along the
read-order — the deepest dip during accumulation. The trajectory
minimum is often much smaller than the terminal value (see two_tongues).

Outputs:
    exp04_pareto.png   — main scatter + Pareto frontier
    exp04_topK.txt     — top-10 configs by terminal L1, length
"""

from __future__ import annotations

import os
import sys
import time
import math

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..', 'core'))

OUT_PNG = os.path.join(HERE, 'exp04_pareto.png')
OUT_TOP = os.path.join(HERE, 'exp04_topK.txt')

WS = [3, 5, 7, 10, 15, 20]
N0_RANGE = range(2, 81)
K_RANGE = range(5, 501, 5)

u9 = np.full(9, 1.0 / 9)


def n_primes_vec(n: int, k: int) -> np.ndarray:
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


def evaluate(n0: int, w: int, k: int):
    """Returns dict with: length, L1_terminal, L1_trajectory_min,
    L_at_traj_min (the digit length AT the trajectory's min L1),
    n_survivors."""
    parts = [n_primes_vec(n, k) for n in range(n0, n0 + w)]
    m_arr = np.concatenate(parts)
    n_atoms = m_arr.size

    _, inverse, counts = np.unique(m_arr, return_inverse=True, return_counts=True)
    mask = counts[inverse] == 1
    survivors = m_arr[mask]
    if survivors.size == 0:
        return None

    # Leading digits and digit lengths (vectorised)
    log_floor = np.floor(np.log10(survivors)).astype(np.int64)
    leading = (survivors // 10 ** log_floor).astype(np.int64)
    digit_lens = log_floor + 1                                # len(str(m))

    # Running cumulative leading-digit counts in read order.
    # Read order = order of survivor appearance in the bundle.
    # The mask preserves order.
    ld_one = np.zeros((n_atoms, 9), dtype=np.int64)
    surv_idx = np.where(mask)[0]
    surv_log_floor = np.floor(np.log10(m_arr[surv_idx])).astype(np.int64)
    surv_leading = (m_arr[surv_idx] // 10 ** surv_log_floor).astype(np.int64)
    n_surv = surv_idx.size
    ld_seq = np.zeros((n_surv, 9), dtype=np.int64)
    ld_seq[np.arange(n_surv), surv_leading - 1] = 1
    cum = np.cumsum(ld_seq, axis=0)
    tot = cum.sum(axis=1)
    p = cum / tot[:, None]
    l1_traj = np.abs(p - u9).sum(axis=1)

    # Per-atom digit length, then cumulative
    surv_digit_len = (surv_log_floor + 1).astype(np.int64)
    cum_digit_len = np.cumsum(surv_digit_len)

    return {
        'length': int(cum_digit_len[-1]),
        'L1_terminal': float(l1_traj[-1]),
        'L1_trajectory_min': float(l1_traj.min()),
        'L_at_traj_min': int(cum_digit_len[l1_traj.argmin()]),
        'n_survivors': int(n_surv),
    }


def main():
    print('Sweeping (n_0, W, k) to find Pareto-optimal C_Surv configs')
    print(f'  W ∈ {WS}')
    print(f'  n_0 ∈ [{N0_RANGE.start}, {N0_RANGE.stop - 1}]')
    print(f'  k ∈ [{K_RANGE.start}, {K_RANGE.stop - K_RANGE.step}, step {K_RANGE.step}]')

    results = []  # list of dicts with keys 'length', 'L1_terminal', 'L1_trajectory_min', 'L_at_traj_min', 'n_0', 'W', 'k'
    t0 = time.time()
    total = len(WS) * len(N0_RANGE) * len(K_RANGE)
    done = 0
    for W in WS:
        for n0 in N0_RANGE:
            for k in K_RANGE:
                r = evaluate(n0, W, int(k))
                if r is not None:
                    r.update({'n_0': int(n0), 'W': int(W), 'k': int(k)})
                    results.append(r)
                done += 1
        print(f'  W={W} done ({done}/{total}, t={time.time()-t0:.1f}s)')
    print(f'Total: {time.time()-t0:.1f}s, {len(results)} valid configs')

    # Pareto frontier (minimise L1, maximise length).
    # Optimal = no other point has both higher length AND lower L1.
    arr_len = np.array([r['length'] for r in results])
    arr_l1 = np.array([r['L1_terminal'] for r in results])
    arr_l1_min = np.array([r['L1_trajectory_min'] for r in results])
    arr_L_at_min = np.array([r['L_at_traj_min'] for r in results])

    # Pareto frontier on (length, L1_terminal):
    order = np.argsort(-arr_len)  # descending length
    pareto_term = []
    min_l1_so_far = float('inf')
    for idx in order:
        if arr_l1[idx] < min_l1_so_far:
            min_l1_so_far = arr_l1[idx]
            pareto_term.append(idx)

    # Pareto frontier on (L_at_traj_min, L1_trajectory_min):
    order2 = np.argsort(-arr_L_at_min)
    pareto_traj = []
    min_l1_so_far = float('inf')
    for idx in order2:
        if arr_l1_min[idx] < min_l1_so_far:
            min_l1_so_far = arr_l1_min[idx]
            pareto_traj.append(idx)

    pareto_term_pts = sorted([(arr_len[i], arr_l1[i]) for i in pareto_term])
    pareto_traj_pts = sorted([(arr_L_at_min[i], arr_l1_min[i]) for i in pareto_traj])

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(18, 8), dpi=140)
    fig.patch.set_facecolor('#0a0a0a')

    cmap = plt.get_cmap('viridis')
    color_for_W = {W: cmap(i / max(1, len(WS) - 1)) for i, W in enumerate(WS)}

    # Panel 1: terminal L1 vs length
    ax = axes[0]
    ax.set_facecolor('#0a0a0a')
    for W in WS:
        idx = [i for i, r in enumerate(results) if r['W'] == W]
        if not idx:
            continue
        ax.scatter(arr_len[idx], arr_l1[idx], s=4, alpha=0.35,
                   color=color_for_W[W], label=f'W={W}')
    if pareto_term_pts:
        px, py = zip(*pareto_term_pts)
        ax.plot(px, py, color='#ff5555', linewidth=2.0, alpha=0.95,
                label='Pareto frontier (terminal)')
        ax.scatter(px, py, color='#ff5555', s=22, zorder=4,
                   edgecolor='white', linewidth=0.5)
    ax.set_xlabel('digit length of C_Surv', color='white', fontsize=11)
    ax.set_ylabel('terminal leading-digit L1', color='white', fontsize=11)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#333')
    ax.grid(True, alpha=0.15, color='#888', which='both')
    ax.legend(loc='lower left', fontsize=8, framealpha=0.4,
              labelcolor='white', facecolor='#1a1a1a', ncol=2)
    ax.set_title('Terminal L1 vs digit length\n(end-of-stream value)',
                 color='white', fontsize=11)

    # Panel 2: trajectory-minimum L1 vs length-at-min
    ax = axes[1]
    ax.set_facecolor('#0a0a0a')
    for W in WS:
        idx = [i for i, r in enumerate(results) if r['W'] == W]
        if not idx:
            continue
        ax.scatter(arr_L_at_min[idx], arr_l1_min[idx], s=4, alpha=0.35,
                   color=color_for_W[W], label=f'W={W}')
    if pareto_traj_pts:
        px, py = zip(*pareto_traj_pts)
        ax.plot(px, py, color='#ff5555', linewidth=2.0, alpha=0.95,
                label='Pareto frontier (trajectory)')
        ax.scatter(px, py, color='#ff5555', s=22, zorder=4,
                   edgecolor='white', linewidth=0.5)
    ax.set_xlabel('digit length AT trajectory min', color='white', fontsize=11)
    ax.set_ylabel('trajectory-min leading-digit L1', color='white', fontsize=11)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#333')
    ax.grid(True, alpha=0.15, color='#888', which='both')
    ax.legend(loc='lower left', fontsize=8, framealpha=0.4,
              labelcolor='white', facecolor='#1a1a1a', ncol=2)
    ax.set_title('Trajectory-min L1 vs digit length at that minimum\n'
                 '(deepest dip along the read order, and where it was)',
                 color='white', fontsize=11)

    fig.suptitle(
        'C_Surv Pareto: digit length vs leading-digit L1\n'
        f'{len(results)} configs across (n_0 ∈ [2,80]) × (W ∈ {{3,5,7,10,15,20}}) × (k ∈ [5,500])',
        color='white', fontsize=13, y=0.99
    )

    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f'-> {OUT_PNG}')

    # Top-10 by various criteria
    with open(OUT_TOP, 'w') as f:
        f.write('exp04 — top configurations\n')
        f.write('=' * 70 + '\n\n')

        f.write('Top-15 configs by LARGEST length with TERMINAL L1 < 0.05:\n')
        f.write(f'{"length":>8} {"L1_t":>8} {"L1_min":>8} {"L_at_min":>8} '
                f'{"n_0":>5} {"W":>3} {"k":>4}\n')
        good = [r for r in results if r['L1_terminal'] < 0.05]
        good.sort(key=lambda r: -r['length'])
        for r in good[:15]:
            f.write(f'{r["length"]:>8} {r["L1_terminal"]:>8.4f} '
                    f'{r["L1_trajectory_min"]:>8.4f} {r["L_at_traj_min"]:>8} '
                    f'{r["n_0"]:>5} {r["W"]:>3} {r["k"]:>4}\n')

        f.write('\nTop-15 configs on PARETO FRONTIER (terminal):\n')
        f.write(f'{"length":>8} {"L1_t":>8} {"n_0":>5} {"W":>3} {"k":>4}\n')
        for idx in pareto_term[:15]:
            r = results[idx]
            f.write(f'{r["length"]:>8} {r["L1_terminal"]:>8.4f} '
                    f'{r["n_0"]:>5} {r["W"]:>3} {r["k"]:>4}\n')

        f.write('\nTop-15 configs on PARETO FRONTIER (trajectory-min):\n')
        f.write(f'{"L_at_min":>8} {"L1_min":>8} {"n_0":>5} {"W":>3} {"k":>4}\n')
        for idx in pareto_traj[:15]:
            r = results[idx]
            f.write(f'{r["L_at_traj_min"]:>8} {r["L1_trajectory_min"]:>8.4f} '
                    f'{r["n_0"]:>5} {r["W"]:>3} {r["k"]:>4}\n')

        f.write('\nThe lowest-L1 trajectory point ever seen (any length):\n')
        idx = int(np.argmin(arr_l1_min))
        r = results[idx]
        f.write(f'  L1_min = {r["L1_trajectory_min"]:.6f}, '
                f'L_at_min = {r["L_at_traj_min"]}, '
                f'n_0 = {r["n_0"]}, W = {r["W"]}, k = {r["k"]}\n')

        f.write('\nThe longest C_Surv with L1 < 0.01 (trajectory min):\n')
        good = [r for r in results if r['L1_trajectory_min'] < 0.01]
        if good:
            good.sort(key=lambda r: -r['L_at_traj_min'])
            for r in good[:5]:
                f.write(f'  L1_min = {r["L1_trajectory_min"]:.6f}, '
                        f'L_at_min = {r["L_at_traj_min"]}, '
                        f'n_0 = {r["n_0"]}, W = {r["W"]}, k = {r["k"]}\n')
        else:
            f.write('  (none with L1 < 0.01)\n')

    print(f'-> {OUT_TOP}')

    # Summary to stdout
    print(f'\nPareto frontier (terminal): {len(pareto_term)} points')
    print(f'Pareto frontier (trajectory min): {len(pareto_traj)} points')
    idx_best = int(np.argmin(arr_l1_min))
    r = results[idx_best]
    print(f'\nDeepest L1 dip ever (any length): L1 = {r["L1_trajectory_min"]:.6f}')
    print(f'  at L = {r["L_at_traj_min"]}, n_0 = {r["n_0"]}, '
          f'W = {r["W"]}, k = {r["k"]}')


if __name__ == '__main__':
    main()
