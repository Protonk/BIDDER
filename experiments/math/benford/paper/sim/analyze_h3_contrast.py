"""
Analysis for H3-CONTRAST: compute n(θ_k) per (N, k), tabulate the
ratio r(N, k) = n_alt(θ_k) / n_full(θ_k), check Q1 (k-trend) and
Q2 (N-stability) as in step-buddies / F2-contrast.

Run: sage -python analyze_h3_contrast.py
"""

import glob
import math
import os
import numpy as np


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
H3_DIR = os.path.join(SIM_DIR, 'h3_contrast_results')

K_VALUES = [5.0, 3.0, 2.0, 1.2]
N_VALUES = [10**5, 10**6, 10**7]


def theta_N(N, L):
    """Expected multinomial-null L₁ floor for L³ bins at N walkers.
    Using the standard √(2M/(πN)) approximation for the mean."""
    M = L**3
    return math.sqrt(2.0 * M / (math.pi * N))


def first_crossing(sample_times, l1, threshold):
    below = np.where(l1 < threshold)[0]
    if below.size == 0:
        return None
    return int(sample_times[below[0]])


def main():
    # Load all runs. File schema: {walk}_N1e{log_N}.npz.
    runs = {}
    for walk in ['full', 'alt']:
        for N in N_VALUES:
            log_N = int(round(math.log10(N)))
            path = os.path.join(H3_DIR, f'{walk}_N1e{log_N}.npz')
            if not os.path.exists(path):
                print(f'missing {path}')
                continue
            d = np.load(path, allow_pickle=True)
            runs[(walk, N)] = (d['sample_times'], d['l1'], int(d['meta_L']))

    print('Loaded runs:')
    for key in sorted(runs.keys()):
        times, l1, L = runs[key]
        print(f'  {key}: L={L}, n=[{times[0]}, {times[-1]}], '
              f'L₁={l1.min():.3e}..{l1.max():.3e}')
    print()

    n_values = {}
    for (walk, N), (times, l1, L) in runs.items():
        for k in K_VALUES:
            theta = k * theta_N(N, L)
            n_cross = first_crossing(times, l1, theta)
            n_values[(walk, N, k)] = (n_cross, theta)

    print('=== n(θ_k) table ===')
    print()
    for N in N_VALUES:
        if ('full', N) not in runs:
            continue
        _, _, L = runs[('full', N)]
        print(f'  N = {N:_}  (L = {L}, L³ = {L**3}, θ_N ≈ {theta_N(N, L):.4e})')
        print(f'    k    θ_k           n_full     n_alt      ratio')
        for k in K_VALUES:
            nf, theta = n_values[('full', N, k)]
            na, _ = n_values[('alt', N, k)]
            if nf is None or na is None:
                ratio_str = 'CENSORED'
            else:
                ratio_str = f'{na/nf:.3f}'
            print(f'    {k:4.1f}  {theta:.4e}    {str(nf):>6s}     {str(na):>6s}     {ratio_str:>7s}')
        print()

    print('=== Q1 (k-trend within each N): does r(N, k) grow as k↓? ===')
    for N in N_VALUES:
        if ('full', N) not in runs:
            continue
        rs = []
        for k in K_VALUES:
            nf, _ = n_values[('full', N, k)]
            na, _ = n_values[('alt', N, k)]
            if nf and na:
                rs.append((k, na / nf))
        print(f'  N = {N:_}: ' +
              '  '.join(f'k={k:.1f}→{r:.3f}' for k, r in rs))
    print()

    print('=== Q2 (cross-N stability at fixed k): max/min ratio ≤ 1.5? ===')
    for k in K_VALUES:
        rs = []
        for N in N_VALUES:
            if ('full', N) not in runs:
                continue
            nf, _ = n_values[('full', N, k)]
            na, _ = n_values[('alt', N, k)]
            if nf and na:
                rs.append((N, na / nf))
        if not rs:
            continue
        values = [r for _, r in rs]
        mn, mx = min(values), max(values)
        print(f'  k = {k:.1f}: ' +
              '  '.join(f'N=1e{int(round(math.log10(n)))}→{r:.3f}' for n, r in rs) +
              f'   max/min = {mx/mn:.3f}')


if __name__ == '__main__':
    main()
