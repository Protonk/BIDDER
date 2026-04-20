"""
Analysis for SUBSET-STEP-BUDDIES: compute n(θ_k) for each run,
aggregate across seeds, tabulate the ratio r(N, k) =
n_purple(θ_k) / n_red(θ_k), and check the Q1 (k-trend) and
Q2 (N-stability) questions from the plan.

Run: sage -python analyze_step_buddies.py
"""

import glob
import math
import os
import numpy as np


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
BUDDIES_DIR = os.path.join(SIM_DIR, 'comparison_walks_results', 'step_buddies')

# M0 null floor at N=10^8
THETA_N_1E8 = 2.717e-3

K_VALUES = [5.0, 3.0, 2.0, 1.2]
N_VALUES = [10**4, 10**5, 10**6, 10**7]


def theta_N(N):
    return THETA_N_1E8 * math.sqrt(1e8 / N)


def first_crossing(sample_times, l1, threshold):
    """Smallest sample time at which l1 < threshold. Returns None if
    no crossing by end of sampling."""
    below = np.where(l1 < threshold)[0]
    if below.size == 0:
        return None
    return int(sample_times[below[0]])


def load_runs():
    """Return dict: {(walk, N): [l1_arrays_one_per_seed]}."""
    runs = {}
    for walk in ['bs12', 'alt']:
        for N in N_VALUES:
            log_N = int(round(math.log10(N)))
            pattern = os.path.join(BUDDIES_DIR, f'{walk}_N1e{log_N}_s*.npz')
            files = sorted(glob.glob(pattern))
            l1s = []
            times = None
            for f in files:
                d = np.load(f, allow_pickle=True)
                if times is None:
                    times = d['sample_times']
                l1s.append(d['l1'])
            runs[(walk, N)] = (times, l1s)
    return runs


def aggregate_n_threshold(sample_times, l1_list, threshold):
    """Compute median n(threshold) over list of l1 trajectories.
    Returns (median_n, list_of_individual_ns, n_censored)."""
    ns = [first_crossing(sample_times, l1, threshold) for l1 in l1_list]
    valid = [n for n in ns if n is not None]
    n_censored = len(ns) - len(valid)
    if not valid:
        return None, ns, n_censored
    return float(np.median(valid)), ns, n_censored


def main():
    runs = load_runs()
    print('Loaded runs:')
    for key in sorted(runs.keys()):
        times, l1s = runs[key]
        print(f'  {key}: {len(l1s)} seeds, times=[{times[0]}, {times[-1]}]')
    print()

    # n(θ_k) per (walk, N, k)
    # Assemble n_values[(walk, N, k)] = (median_n, individual_ns, censored_count)
    n_values = {}
    for (walk, N), (times, l1s) in runs.items():
        for k in K_VALUES:
            theta = k * theta_N(N)
            median_n, indiv, cens = aggregate_n_threshold(times, l1s, theta)
            n_values[(walk, N, k)] = (median_n, indiv, cens)

    # Print per-panel n table
    print('=== n(θ_k) table (median across seeds; asterisk = some seeds censored) ===')
    print()
    for N in N_VALUES:
        print(f'  N = {N:_}  (θ_N = {theta_N(N):.4e})')
        print(f'    k    θ_k           n_red         n_purple     ratio  (seeds red / purple)')
        for k in K_VALUES:
            theta = k * theta_N(N)
            nr_med, nr_all, nr_cens = n_values[('bs12', N, k)]
            np_med, np_all, np_cens = n_values[('alt', N, k)]
            if nr_med is None or np_med is None:
                ratio_str = 'CENSORED'
            else:
                ratio = np_med / nr_med
                ratio_str = f'{ratio:.3f}'
            cens_flag_r = '*' if nr_cens > 0 else ' '
            cens_flag_p = '*' if np_cens > 0 else ' '
            print(f'    {k:4.1f}  {theta:.4e}    {str(nr_med):>6s}{cens_flag_r}    '
                  f'{str(np_med):>6s}{cens_flag_p}    {ratio_str:>7s}   '
                  f'({nr_all} / {np_all})')
        print()

    # Q1: within-panel k-trend
    print('=== Q1: does r(N, k) grow as k decreases? (expected yes) ===')
    for N in N_VALUES:
        print(f'  N = {N:_}')
        ratios = []
        for k in K_VALUES:
            nr_med, _, _ = n_values[('bs12', N, k)]
            np_med, _, _ = n_values[('alt', N, k)]
            if nr_med and np_med:
                r = np_med / nr_med
                ratios.append((k, r))
        for k, r in ratios:
            print(f'    k={k:.1f}  r={r:.3f}')
        # Check monotone
        ratios.sort(key=lambda x: -x[0])  # decreasing k
        is_monotone = all(ratios[i][1] <= ratios[i+1][1] + 0.05 for i in range(len(ratios)-1))
        print(f'    Monotone non-decreasing as k↓? {"YES" if is_monotone else "NO"}')
    print()

    # Q2: cross-N stability at fixed k
    print('=== Q2: at fixed k, is r(N, k) stable across N (max/min ≤ 1.5)? ===')
    for k in K_VALUES:
        rs_by_n = []
        for N in N_VALUES:
            nr_med, _, _ = n_values[('bs12', N, k)]
            np_med, _, _ = n_values[('alt', N, k)]
            if nr_med and np_med:
                r = np_med / nr_med
                rs_by_n.append((N, r))
        if not rs_by_n:
            continue
        rs = [r for _, r in rs_by_n]
        mn, mx = min(rs), max(rs)
        spread = mx / mn if mn > 0 else float('inf')
        print(f'  k = {k:.1f}: ' +
              '  '.join(f'N=1e{int(round(math.log10(n)))}→{r:.3f}' for n, r in rs_by_n))
        print(f'    min={mn:.3f}  max={mx:.3f}  max/min={spread:.3f}  '
              f'{"(stable ≤1.5)" if spread <= 1.5 else "(NOT stable, >1.5)"}')

    # Save processed table
    print()
    out_npz = os.path.join(BUDDIES_DIR, 'analysis.npz')
    save_dict = {}
    for k in K_VALUES:
        for N in N_VALUES:
            nr_med, nr_all, nr_cens = n_values[('bs12', N, k)]
            np_med, np_all, np_cens = n_values[('alt', N, k)]
            key = f'k{k}_N1e{int(round(math.log10(N)))}'
            save_dict[f'{key}_n_red'] = float(nr_med) if nr_med else -1.0
            save_dict[f'{key}_n_purple'] = float(np_med) if np_med else -1.0
            save_dict[f'{key}_ratio'] = (np_med / nr_med) if (nr_med and np_med) else -1.0
    np.savez_compressed(out_npz, **save_dict)
    print(f'-> {out_npz}')


if __name__ == '__main__':
    main()
