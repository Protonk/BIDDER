"""
Analyze the parity-falsifier runs. Two things:

(A) lazy-alt (L=31) vs existing z2_full (L=31): compute r on
    full_2d and x_1d. Compare to predicted r = 1.00 (2D) and r =
    2.00 (1D). Contrast with prior alt values r = 2.00 and r = 4.00.

(B) even-L test at L=30: check whether alt's x_1d plateaus at
    ≈ 1.0 while full's x_1d mixes normally.

Run: sage -python analyze_parity_falsifier.py
"""

import math
import os
import numpy as np


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
PAR_DIR = os.path.join(SIM_DIR, 'parity_falsifier_results')
PROJ_DIR = os.path.join(SIM_DIR, 'projection_check_results')

K_VALUES = [5.0, 3.0, 2.0, 1.2]


def theta_N(N, M):
    return math.sqrt(2.0 * M / (math.pi * N))


def first_crossing(times, l1, threshold):
    below = np.where(l1 < threshold)[0]
    if below.size == 0:
        return None
    return int(times[below[0]])


def load(path):
    if not os.path.exists(path):
        print(f'missing: {path}')
        return None
    return np.load(path, allow_pickle=True)


def compare(name_full, path_full, name_other, path_other, L, projections):
    full = load(path_full)
    other = load(path_other)
    if full is None or other is None:
        return
    N = int(full['meta_N'])
    times = full['sample_times']
    print(f'\n--- {name_other}  vs  {name_full}   (L = {L}) ---')
    for proj, M in projections:
        if f'l1_{proj}' not in full or f'l1_{proj}' not in other:
            continue
        l1_full = full[f'l1_{proj}']
        l1_other = other[f'l1_{proj}']
        theta_base = theta_N(N, M)
        print(f'\n  projection = {proj}  (M = {M}, θ_N = {theta_base:.4e})')
        print(f'    k    θ_k           n_full    n_other   r = n_other/n_full')
        for k in K_VALUES:
            theta = k * theta_base
            nf = first_crossing(times, l1_full, theta)
            no = first_crossing(times, l1_other, theta)
            if nf is None or no is None:
                ratio_str = 'CENSORED'
            else:
                ratio_str = f'{no/nf:.3f}'
            print(f'    {k:4.1f}  {theta:.4e}    {str(nf):>6s}    '
                  f'{str(no):>6s}    {ratio_str:>7s}')


def show_plateau(label, path, projection):
    d = load(path)
    if d is None:
        return
    l1 = d[f'l1_{projection}']
    times = d['sample_times']
    print(f'\n  {label}:  {projection}  min={l1.min():.4e}  '
          f'max={l1.max():.4e}  final={l1[-1]:.4e}')
    # tail mean as plateau estimate
    tail = l1[-20:]
    print(f'    tail (last 20 samples): mean={tail.mean():.4e}  '
          f'std={tail.std():.4e}')


def main():
    print('==========================================')
    print('(A) lazy-alt vs full, L=31')
    print('==========================================')
    print('Predicted: r_2D ≈ 1.00,  r_1D ≈ 2.00')
    print('Compare to measured alt: r_2D = 2.00,  r_1D = 4.00')

    compare(
        'full (L=31, existing)',
        os.path.join(PROJ_DIR, 'z2_full.npz'),
        'lazy_alt (ε=0.5, L=31)',
        os.path.join(PAR_DIR, 'z2_lazy_alt_L31.npz'),
        31,
        [('full_2d', 31 * 31), ('x_1d', 31), ('y_1d', 31)],
    )

    print('\n==========================================')
    print('(B) even-L test: alt should plateau, full should mix')
    print('==========================================')
    print('Predicted: alt x_1d plateaus at ≈ 1.0')
    print('           full x_1d → floor ≈ √(2·30/(π·10⁶)) = '
          f'{theta_N(10**6, 30):.4e}')

    print('\nalt @ L=30:')
    show_plateau('alt_L30', os.path.join(PAR_DIR, 'z2_alt_L30.npz'), 'x_1d')
    show_plateau('alt_L30', os.path.join(PAR_DIR, 'z2_alt_L30.npz'), 'full_2d')

    print('\nfull @ L=30:')
    show_plateau('full_L30', os.path.join(PAR_DIR, 'z2_full_L30.npz'), 'x_1d')
    show_plateau('full_L30', os.path.join(PAR_DIR, 'z2_full_L30.npz'), 'full_2d')

    print('\n(comparison: alt x_1d / full x_1d at tail — '
          'if >> 10× then alt is stuck, mechanism confirmed)')
    alt30 = load(os.path.join(PAR_DIR, 'z2_alt_L30.npz'))
    full30 = load(os.path.join(PAR_DIR, 'z2_full_L30.npz'))
    if alt30 is not None and full30 is not None:
        alt_tail = alt30['l1_x_1d'][-20:].mean()
        full_tail = full30['l1_x_1d'][-20:].mean()
        print(f'  alt tail  = {alt_tail:.4e}')
        print(f'  full tail = {full_tail:.4e}')
        print(f'  ratio     = {alt_tail/full_tail:.2f}')


if __name__ == '__main__':
    main()
