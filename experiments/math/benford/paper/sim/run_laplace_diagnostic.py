"""
Mess #1 diagnostic: empirical Laplace transforms of local time.

(A) SRW on ℤ: measure E[q^{L_n}] for local time L_n of simple ±1
    walk at the origin, at a range of n and q. Prediction (MESSES.md
    §1): E[q^{L_n}] ~ q√2 / ((1 − q)√(πn)) — algebraic, not
    stretched-exp.

(B) BS(1,2): measure L_n (time in R = {|E| ≤ E₀}) and N_n (# entries
    into R) for the BS(1,2) walk from default IC. Compute E[q^{L_n}],
    E[q^{N_n}], and check N_n/√n distribution.

Uses a modified b-step that replaces the existing |E| > 20 freeze
with a physically correct no-op (b-step changes log|x| by O(1/|x|)
for large |x|, i.e. nothing at the precision we care about).

Dense E[q^·] expectations at every sample time; raw L/N histograms
only at log-spaced snapshot times (keep file size small).

Run: sage -python run_laplace_diagnostic.py
"""

import math
import os
import time
import numpy as np

from run_comparison_walks import (
    initialize,
    step_a,
    step_a_inv,
)


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SIM_DIR, 'laplace_diagnostic_results')
os.makedirs(OUT_DIR, exist_ok=True)

N_WALKERS = 10**6
N_MAX = 10000

# Dense log-ish sample times for E[q^·] curves
SAMPLE_TIMES = np.unique(np.concatenate([
    np.arange(10, 101, 10, dtype=np.int64),
    np.arange(100, 1001, 50, dtype=np.int64),
    np.arange(1000, N_MAX + 1, 500, dtype=np.int64),
])).astype(np.int64)

# A sparser set where we save full walker-level L/N (for histograms)
SNAPSHOT_TIMES = np.array([100, 300, 1000, 3000, 10000], dtype=np.int64)

Q_VALUES = [0.3, 0.5, 0.7, 0.9]

E0 = 10              # BS(1,2) R cutoff: R = {|E| ≤ E0}
E_SAFE = 20          # |E| ≤ E_SAFE: full x-computation is float-safe

SEED_BASE = 0x1A91ACE0


# -------- Part A: SRW on ℤ --------

def run_srw(seed, out_path):
    print(f'\n=== SRW on ℤ  N={N_WALKERS:_}  n_max={N_MAX}  seed={seed} ===')
    rng = np.random.default_rng(seed)
    pos = np.zeros(N_WALKERS, dtype=np.int64)
    L = np.ones(N_WALKERS, dtype=np.int64)  # start at 0 counts as visit
    N_ret = np.zeros(N_WALKERS, dtype=np.int64)
    prev_at_zero = np.ones(N_WALKERS, dtype=bool)

    # E[q^L] per (sample time, q)
    EqL = np.zeros((SAMPLE_TIMES.size, len(Q_VALUES)), dtype=np.float64)
    EqN = np.zeros((SAMPLE_TIMES.size, len(Q_VALUES)), dtype=np.float64)
    L_snaps = {}  # snapshot_time -> array of L values
    N_snaps = {}
    sample_set = {int(t): i for i, t in enumerate(SAMPLE_TIMES.tolist())}
    snap_set = set(int(t) for t in SNAPSHOT_TIMES.tolist())
    t0 = time.time()
    for step in range(1, N_MAX + 1):
        bit = rng.integers(0, 2, size=N_WALKERS, dtype=np.int8)
        pos += bit.astype(np.int64) * 2 - 1
        at_zero = (pos == 0)
        L += at_zero.astype(np.int64)
        N_ret += (at_zero & ~prev_at_zero).astype(np.int64)
        prev_at_zero = at_zero
        if step in sample_set:
            idx = sample_set[step]
            Lf = L.astype(np.float64)
            Nf = N_ret.astype(np.float64)
            for qi, q in enumerate(Q_VALUES):
                EqL[idx, qi] = float(np.mean(np.power(q, Lf)))
                EqN[idx, qi] = float(np.mean(np.power(q, Nf)))
            if idx % 10 == 0 or step == N_MAX:
                dt = time.time() - t0
                print(f'  n={step:6d}  <L>={L.mean():.2f}  '
                      f'<N_ret>={N_ret.mean():.2f}  '
                      f'E[0.5^L]={EqL[idx, 1]:.4e}  '
                      f'({step/max(dt,1e-9):.1f} s/s)', flush=True)
        if step in snap_set:
            L_snaps[step] = L.copy()
            N_snaps[step] = N_ret.copy()
    print(f'  wall: {time.time()-t0:.1f}s')
    save_dict = {
        'sample_times': SAMPLE_TIMES,
        'q_values': np.array(Q_VALUES, dtype=np.float64),
        'EqL': EqL,
        'EqN': EqN,
        'meta_N': np.int64(N_WALKERS),
        'meta_seed': np.int64(seed),
        'meta_walk': np.str_('srw_z'),
    }
    for t in SNAPSHOT_TIMES.tolist():
        save_dict[f'L_snap_{t}'] = L_snaps[t]
        save_dict[f'N_snap_{t}'] = N_snaps[t]
    np.savez_compressed(out_path, **save_dict)
    print(f'  -> {out_path}')


# -------- Part B: BS(1,2) --------

def step_b_nofreeze(m, E, sign, mask, delta):
    if not mask.any():
        return
    idx = np.where(mask)[0]
    E_local = E[idx]
    safe = np.abs(E_local) <= E_SAFE
    if not safe.any():
        return
    act_idx = idx[safe]
    log_mag = E[act_idx].astype(np.float64) + m[act_idx]
    x = sign[act_idx].astype(np.float64) * np.power(10.0, log_mag)
    x_new = x + float(delta)
    abs_x = np.abs(x_new)
    zero_mask = abs_x == 0.0
    if zero_mask.any():
        abs_x = np.where(zero_mask, 1e-300, abs_x)
    log_abs = np.log10(abs_x)
    new_E = np.floor(log_abs).astype(np.int32)
    new_m = log_abs - new_E.astype(np.float64)
    new_sign = np.where(x_new > 0.0, np.int8(1), np.int8(-1))
    m[act_idx] = new_m
    E[act_idx] = new_E
    sign[act_idx] = new_sign


def step_bs12_nofreeze(m, E, sign, rng, step_index):
    choice = rng.integers(0, 4, size=m.shape[0], dtype=np.int8)
    step_a(m, E, choice == 0)
    step_a_inv(m, E, choice == 1)
    step_b_nofreeze(m, E, sign, choice == 2, +1)
    step_b_nofreeze(m, E, sign, choice == 3, -1)


def run_bs12(seed, out_path):
    print(f'\n=== BS(1,2)  N={N_WALKERS:_}  n_max={N_MAX}  E₀={E0}  seed={seed} ===')
    rng = np.random.default_rng(seed)
    m, E, sign = initialize(N_WALKERS)
    in_R = (np.abs(E) <= E0)
    L = in_R.astype(np.int64)
    N_ret = np.zeros(N_WALKERS, dtype=np.int64)
    prev_in_R = in_R.copy()

    EqL = np.zeros((SAMPLE_TIMES.size, len(Q_VALUES)), dtype=np.float64)
    EqN = np.zeros((SAMPLE_TIMES.size, len(Q_VALUES)), dtype=np.float64)
    L_snaps = {}
    N_snaps = {}
    E_snaps = {}
    sample_set = {int(t): i for i, t in enumerate(SAMPLE_TIMES.tolist())}
    snap_set = set(int(t) for t in SNAPSHOT_TIMES.tolist())
    t0 = time.time()
    for step in range(1, N_MAX + 1):
        step_bs12_nofreeze(m, E, sign, rng, step)
        in_R = (np.abs(E) <= E0)
        L += in_R.astype(np.int64)
        N_ret += (in_R & ~prev_in_R).astype(np.int64)
        prev_in_R = in_R
        if step in sample_set:
            idx = sample_set[step]
            Lf = L.astype(np.float64)
            Nf = N_ret.astype(np.float64)
            for qi, q in enumerate(Q_VALUES):
                EqL[idx, qi] = float(np.mean(np.power(q, Lf)))
                EqN[idx, qi] = float(np.mean(np.power(q, Nf)))
            if idx % 10 == 0 or step == N_MAX:
                dt = time.time() - t0
                print(f'  n={step:6d}  <L>={L.mean():.2f}  '
                      f'<N>={N_ret.mean():.2f}  '
                      f'frac_in_R={in_R.mean():.3f}  '
                      f'E_range=[{E.min()}, {E.max()}]  '
                      f'({step/max(dt,1e-9):.1f} s/s)', flush=True)
        if step in snap_set:
            L_snaps[step] = L.copy()
            N_snaps[step] = N_ret.copy()
            E_snaps[step] = E.copy()
    print(f'  wall: {time.time()-t0:.1f}s')
    save_dict = {
        'sample_times': SAMPLE_TIMES,
        'q_values': np.array(Q_VALUES, dtype=np.float64),
        'EqL': EqL,
        'EqN': EqN,
        'meta_N': np.int64(N_WALKERS),
        'meta_E0': np.int32(E0),
        'meta_seed': np.int64(seed),
        'meta_walk': np.str_('bs12'),
    }
    for t in SNAPSHOT_TIMES.tolist():
        save_dict[f'L_snap_{t}'] = L_snaps[t]
        save_dict[f'N_snap_{t}'] = N_snaps[t]
        save_dict[f'E_snap_{t}'] = E_snaps[t]
    np.savez_compressed(out_path, **save_dict)
    print(f'  -> {out_path}')


def main():
    print('Laplace diagnostic: SRW on ℤ and BS(1,2)')
    print(f'N={N_WALKERS:_}, n_max={N_MAX}, q ∈ {Q_VALUES}, E₀={E0}')
    run_srw(SEED_BASE + 1, os.path.join(OUT_DIR, 'srw_z.npz'))
    run_bs12(SEED_BASE + 2, os.path.join(OUT_DIR, 'bs12.npz'))
    print('\n=== Laplace diagnostic complete ===')


if __name__ == '__main__':
    main()
