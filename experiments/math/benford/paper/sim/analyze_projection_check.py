"""
Analyze projection-check results: for each (group, projection), compute
r = n_alt(θ_k) / n_full(θ_k) across k thresholds and tabulate.

Tests the hypothesis that the ~2× slowdown seen on full-state L₁ washes
out when we look at lower-dimensional projections (as it plausibly does
in the BS(1,2) mantissa case).

Run: sage -python analyze_projection_check.py
"""

import math
import os
import numpy as np


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SIM_DIR, 'projection_check_results')

K_VALUES = [5.0, 3.0, 2.0, 1.2]

Z2_PROJECTIONS = [
    ('full_2d', 31 * 31),
    ('x_1d',    31),
    ('y_1d',    31),
]

H3_PROJECTIONS = [
    ('full_3d', 15 ** 3),
    ('ab_2d',   15 * 15),
    ('a_1d',    15),
    ('b_1d',    15),
    ('c_1d',    15),
]


def theta_N(N, M):
    """Multinomial L₁ mean floor: √(2M/(πN))."""
    return math.sqrt(2.0 * M / (math.pi * N))


def first_crossing(times, l1, threshold):
    below = np.where(l1 < threshold)[0]
    if below.size == 0:
        return None
    return int(times[below[0]])


def load(group, walk):
    path = os.path.join(OUT_DIR, f'{group}_{walk}.npz')
    if not os.path.exists(path):
        return None
    d = np.load(path, allow_pickle=True)
    return d


def report_group(group_name, projections):
    print(f'\n========  {group_name}  ========')
    full = load(group_name, 'full')
    alt = load(group_name, 'alt')
    if full is None or alt is None:
        print(f'  missing data for {group_name}')
        return
    N = int(full['meta_N'])
    times = full['sample_times']

    for proj_name, M in projections:
        l1_full = full[f'l1_{proj_name}']
        l1_alt = alt[f'l1_{proj_name}']
        theta_base = theta_N(N, M)
        print(f'\n  projection = {proj_name}  (M = {M}, θ_N = {theta_base:.4e})')
        print(f'    k    θ_k           n_full     n_alt      r = n_alt/n_full')
        for k in K_VALUES:
            theta = k * theta_base
            nf = first_crossing(times, l1_full, theta)
            na = first_crossing(times, l1_alt, theta)
            if nf is None or na is None:
                ratio_str = 'CENSORED'
            else:
                ratio_str = f'{na/nf:.3f}'
            print(f'    {k:4.1f}  {theta:.4e}    {str(nf):>6s}     {str(na):>6s}     {ratio_str:>7s}')


def main():
    print('Projection check: r(projection) table')
    print(f'(N = 10⁶; ℤ²: L = 31; H_3: L = 15)')
    report_group('z2', Z2_PROJECTIONS)
    report_group('h3', H3_PROJECTIONS)

    print('\n--- summary of r across projections ---')
    print('  If r ≈ 2 across all projections: slowdown survives projection.')
    print('  If r → 1 on low-D projections: projection washes out slowdown.')
    print('  The latter supports the BS(1,2) mantissa-projection hypothesis.')


if __name__ == '__main__':
    main()
