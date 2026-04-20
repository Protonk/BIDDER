"""
Analyze ε-scan of lazy-alt on ℤ²/L=31. Compute r_1D(ε) and r_2D(ε)
vs full at each ε, verify U-shape with minimum at ε ≈ 0.008.

Predictions:
  ε      r_1D   r_2D
  0.000  4.000  2.000
  0.001  2.877  1.439
  0.003  1.841  0.920
  0.005  1.352  0.676
  0.008  1.003  0.501
  0.010  1.005  0.502
  0.030  1.026  0.513
  0.100  1.107  0.553
  0.300  1.426  0.713
  0.500  2.000  1.000

Run: sage -python analyze_epsilon_scan.py
"""

import math
import os
import numpy as np


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
EPS_DIR = os.path.join(SIM_DIR, 'epsilon_scan_results')
PROJ_DIR = os.path.join(SIM_DIR, 'projection_check_results')

EPSILONS = [0.0, 0.001, 0.003, 0.005, 0.008, 0.01, 0.03, 0.1, 0.3, 0.5]
K_VALUES = [5.0, 3.0, 2.0, 1.2]
L = 31

PREDICTED = {
    0.0:   (4.000, 2.000),
    0.001: (2.877, 1.439),
    0.003: (1.841, 0.920),
    0.005: (1.352, 0.676),
    0.008: (1.003, 0.501),
    0.01:  (1.005, 0.502),
    0.03:  (1.026, 0.513),
    0.1:   (1.107, 0.553),
    0.3:   (1.426, 0.713),
    0.5:   (2.000, 1.000),
}


def theta_N(N, M):
    return math.sqrt(2.0 * M / (math.pi * N))


def first_crossing(times, l1, threshold):
    below = np.where(l1 < threshold)[0]
    if below.size == 0:
        return None
    return int(times[below[0]])


def eps_path(eps):
    tag = f'eps{eps:.3f}'.replace('.', 'p')
    return os.path.join(EPS_DIR, f'z2_lazy_alt_{tag}.npz')


def main():
    full_path = os.path.join(PROJ_DIR, 'z2_full.npz')
    full = np.load(full_path, allow_pickle=True)
    times_full = full['sample_times']
    N = int(full['meta_N'])

    theta_2D = theta_N(N, L * L)
    theta_1D = theta_N(N, L)

    print(f'Ref: full @ L={L}, N=10^6. θ_2D = {theta_2D:.4e}, θ_1D = {theta_1D:.4e}')
    print()
    print(f'{"eps":>6s}   {"k":>4s}  {"n_full":>6s} {"n_lazy":>6s}   {"r_1D":>6s}  {"r_1D_pred":>9s}     {"n_full":>6s} {"n_lazy":>6s}   {"r_2D":>6s}  {"r_2D_pred":>9s}')
    print('-' * 110)

    for eps in EPSILONS:
        path = eps_path(eps)
        if not os.path.exists(path):
            print(f'missing {path}')
            continue
        d = np.load(path, allow_pickle=True)
        times_eps = d['sample_times']
        l1_2d_f = full['l1_full_2d']
        l1_1d_f = full['l1_x_1d']
        l1_2d = d['l1_full_2d']
        l1_1d = d['l1_x_1d']
        p1, p2 = PREDICTED[eps]
        for k in K_VALUES:
            t2 = k * theta_2D
            t1 = k * theta_1D
            nf_2 = first_crossing(times_full, l1_2d_f, t2)
            no_2 = first_crossing(times_eps, l1_2d, t2)
            nf_1 = first_crossing(times_full, l1_1d_f, t1)
            no_1 = first_crossing(times_eps, l1_1d, t1)
            r_1D = (no_1 / nf_1) if (nf_1 and no_1) else None
            r_2D = (no_2 / nf_2) if (nf_2 and no_2) else None
            r_1D_s = f'{r_1D:.3f}' if r_1D else 'CENS'
            r_2D_s = f'{r_2D:.3f}' if r_2D else 'CENS'
            print(f'{eps:>6.3f}   {k:>4.1f}  {str(nf_1):>6s} {str(no_1):>6s}   '
                  f'{r_1D_s:>6s}  {p1:>9.3f}     '
                  f'{str(nf_2):>6s} {str(no_2):>6s}   {r_2D_s:>6s}  {p2:>9.3f}')
        print()

    # Compact summary: r vs ε at k=2.0 only
    print('\n=== Compact summary at k=2.0 ===')
    print(f'{"ε":>6s}  {"r_1D":>8s}  {"r_1D_pred":>10s}  {"r_2D":>8s}  {"r_2D_pred":>10s}')
    for eps in EPSILONS:
        path = eps_path(eps)
        if not os.path.exists(path):
            continue
        d = np.load(path, allow_pickle=True)
        times_eps = d['sample_times']
        l1_2d_f = full['l1_full_2d']
        l1_1d_f = full['l1_x_1d']
        l1_2d = d['l1_full_2d']
        l1_1d = d['l1_x_1d']
        k = 2.0
        t2 = k * theta_2D
        t1 = k * theta_1D
        nf_2 = first_crossing(times_full, l1_2d_f, t2)
        no_2 = first_crossing(times_eps, l1_2d, t2)
        nf_1 = first_crossing(times_full, l1_1d_f, t1)
        no_1 = first_crossing(times_eps, l1_1d, t1)
        r_1D = (no_1 / nf_1) if (nf_1 and no_1) else float('nan')
        r_2D = (no_2 / nf_2) if (nf_2 and no_2) else float('nan')
        p1, p2 = PREDICTED[eps]
        print(f'{eps:>6.3f}  {r_1D:>8.3f}  {p1:>10.3f}  {r_2D:>8.3f}  {p2:>10.3f}')


if __name__ == '__main__':
    main()
