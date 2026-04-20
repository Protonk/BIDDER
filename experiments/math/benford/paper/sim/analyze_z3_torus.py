"""
Analyze ℤ³ torus runs: compute r on each projection and compare
to predictions.

Predictions (from parity-mode spectral calc, exact at any odd L):
  full_3d:  r = 3.00   (alt: axis-parity (15,0,0) at 1/3 rate;
                        full: diagonal-parity (15,15,15) at full rate)
  ab/ac/bc_2d marginal: r = 4.00
  a/b/c_1d marginal:    r = 4.00

Run: sage -python analyze_z3_torus.py
"""

import math
import os
import numpy as np


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
Z3_DIR = os.path.join(SIM_DIR, 'z3_torus_results')
L = 15
K_VALUES = [5.0, 3.0, 2.0, 1.2]

PROJECTIONS = [
    ('full_3d', L ** 3, 3.00),
    ('ab_2d',   L * L, 4.00),
    ('ac_2d',   L * L, 4.00),
    ('bc_2d',   L * L, 4.00),
    ('a_1d',    L,     4.00),
    ('b_1d',    L,     4.00),
    ('c_1d',    L,     4.00),
]


def theta_N(N, M):
    return math.sqrt(2.0 * M / (math.pi * N))


def first_crossing(times, l1, threshold):
    below = np.where(l1 < threshold)[0]
    if below.size == 0:
        return None
    return int(times[below[0]])


def main():
    full = np.load(os.path.join(Z3_DIR, 'z3_full.npz'), allow_pickle=True)
    alt = np.load(os.path.join(Z3_DIR, 'z3_alt.npz'), allow_pickle=True)
    N = int(full['meta_N'])
    times = full['sample_times']

    print(f'ℤ³ torus L={L}, N=10^6, full vs alt')
    print()
    for proj_name, M, pred in PROJECTIONS:
        theta_base = theta_N(N, M)
        print(f'--- {proj_name}  (M = {M}, θ_N = {theta_base:.4e}, predicted r = {pred}) ---')
        print(f'    k    θ_k           n_full     n_alt      r_measured    r_predicted')
        rs = []
        for k in K_VALUES:
            theta = k * theta_base
            nf = first_crossing(times, full[f'l1_{proj_name}'], theta)
            na = first_crossing(times, alt[f'l1_{proj_name}'], theta)
            if nf is None or na is None:
                ratio_str = 'CENSORED'
            else:
                r = na / nf
                rs.append(r)
                ratio_str = f'{r:.3f}'
            print(f'    {k:4.1f}  {theta:.4e}    {str(nf):>6s}     {str(na):>6s}     {ratio_str:>7s}       {pred:.3f}')
        if rs:
            print(f'    range: {min(rs):.3f} – {max(rs):.3f}   mean: {sum(rs)/len(rs):.3f}')
        print()


if __name__ == '__main__':
    main()
