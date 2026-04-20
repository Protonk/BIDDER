"""
FP128-CEILING-SIM: precision-from-above check.

Reruns M3 IC (b) at 128-bit arbitrary precision (via gmpy2 / MPFR)
and at matched-seed fp64, to close the "is fp64 precise enough?"
direction complementing the fp32/fp16 checks from below.

See `FP128-CEILING-SIM.md`.

Run: sage -python run_fp128_check.py
"""

import math
import os
import time
import numpy as np
from gmpy2 import mpfr, get_context, log10 as gmpy2_log10, floor as gmpy2_floor

# Set 128-bit precision for all gmpy2 ops globally.
get_context().precision = 128


# --- Config -----------------------------------------------------------

N_WALKERS = 10**5
N_STEPS = 600
N_BINS = 1000
SEED = 0xF128CE11

E_THRESH = 20

MODES = np.array([1, 2, 3, 4, 5], dtype=np.int32)

SAMPLE_TIMES = np.concatenate([
    np.arange(1, 201, dtype=np.int32),
    np.arange(205, 601, 5, dtype=np.int32),
])

FOURIER_BATCH = 10**7

# High-precision constants
LOG10_2_HP = gmpy2_log10(mpfr(2))          # 128-bit log10(2)
LOG10_SQRT2_HP = LOG10_2_HP / mpfr(2)       # 128-bit log10(sqrt(2))
ONE_HP = mpfr(1)
ZERO_HP = mpfr(0)
TEN_HP = mpfr(10)

# fp64 constants for matched run
LOG10_2_F64 = math.log10(2.0)
LOG10_SQRT2_F64 = 0.5 * LOG10_2_F64

# Walker-trajectory probes (logged at selected checkpoints)
PROBE_INDICES = np.array([0, 1, 100, 1000, 10000, 50000, 99999], dtype=np.int64)
PROBE_TIMES = [100, 300, 600]

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SIM_DIR, 'fp128_results')
os.makedirs(OUT_DIR, exist_ok=True)


# --- IC initializers --------------------------------------------------

def init_ic_b_hp(n, rng):
    """IC (b) at high precision: m = log₁₀√2 delta, E ~ U{−5..5}."""
    m = np.empty(n, dtype=object)
    for i in range(n):
        m[i] = mpfr(LOG10_SQRT2_HP)
    E = rng.integers(-5, 6, size=n, dtype=np.int32)
    sign = np.ones(n, dtype=np.int8)
    return m, E, sign


def init_ic_b_f64(n, rng):
    """IC (b) at fp64 for matched comparison."""
    m = np.full(n, LOG10_SQRT2_F64, dtype=np.float64)
    E = rng.integers(-5, 6, size=n, dtype=np.int32)
    sign = np.ones(n, dtype=np.int8)
    return m, E, sign


# --- High-precision step kernel --------------------------------------

def step_a_hp(m, E, mask):
    """a-step at high precision using numpy object-array broadcasting."""
    if not mask.any():
        return
    idx = np.where(mask)[0]
    m_sub = m[idx] + LOG10_2_HP  # numpy broadcasts + over object dtype
    carry = m_sub >= ONE_HP
    # elementwise subtract for carried
    for i_local, carried in enumerate(carry):
        if carried:
            m_sub[i_local] = m_sub[i_local] - ONE_HP
    m[idx] = m_sub
    E[idx] += carry.astype(np.int32)


def step_a_inv_hp(m, E, mask):
    if not mask.any():
        return
    idx = np.where(mask)[0]
    m_sub = m[idx] - LOG10_2_HP
    borrow = m_sub < ZERO_HP
    for i_local, borrowed in enumerate(borrow):
        if borrowed:
            m_sub[i_local] = m_sub[i_local] + ONE_HP
    m[idx] = m_sub
    E[idx] -= borrow.astype(np.int32)


def step_b_hp(m, E, sign, mask, delta):
    """b-step at 128-bit precision via per-walker Python loop."""
    if not mask.any():
        return
    idx = np.where(mask)[0]
    delta_hp = mpfr(delta)
    for i in idx:
        E_val = int(E[i])
        if E_val > E_THRESH:
            continue
        if E_val < -E_THRESH:
            m[i] = ZERO_HP
            E[i] = 0
            sign[i] = np.int8(1 if delta > 0 else -1)
            continue
        # Active branch
        log_mag = mpfr(E_val) + m[i]
        x = mpfr(int(sign[i])) * (TEN_HP ** log_mag)
        x_new = x + delta_hp
        if x_new == ZERO_HP:
            m[i] = ZERO_HP
            E[i] = 0
            sign[i] = np.int8(1 if delta > 0 else -1)
            continue
        abs_x = abs(x_new)
        log_abs = gmpy2_log10(abs_x)
        new_E = int(gmpy2_floor(log_abs))
        m[i] = log_abs - mpfr(new_E)
        E[i] = np.int32(new_E)
        sign[i] = np.int8(1 if x_new > ZERO_HP else -1)


def step_walkers_hp(m, E, sign, rng):
    choice = rng.integers(0, 4, size=m.shape[0], dtype=np.int8)
    step_a_hp(m, E, choice == 0)
    step_a_inv_hp(m, E, choice == 1)
    step_b_hp(m, E, sign, choice == 2, +1)
    step_b_hp(m, E, sign, choice == 3, -1)


# --- Matched fp64 kernel (same as m3) --------------------------------

def step_a_f64(m, E, mask):
    if not mask.any():
        return
    idx = np.where(mask)[0]
    m_new = m[idx] + LOG10_2_F64
    carry = m_new >= 1.0
    m[idx] = np.where(carry, m_new - 1.0, m_new)
    E[idx] += carry.astype(np.int32)


def step_a_inv_f64(m, E, mask):
    if not mask.any():
        return
    idx = np.where(mask)[0]
    m_new = m[idx] - LOG10_2_F64
    borrow = m_new < 0.0
    m[idx] = np.where(borrow, m_new + 1.0, m_new)
    E[idx] -= borrow.astype(np.int32)


def step_b_f64(m, E, sign, mask, delta):
    if not mask.any():
        return
    idx = np.where(mask)[0]
    E_local = E[idx]
    frozen = E_local > E_THRESH
    snap = E_local < -E_THRESH
    active = ~(frozen | snap)

    snap_idx = idx[snap]
    if snap_idx.size > 0:
        m[snap_idx] = 0.0
        E[snap_idx] = 0
        sign[snap_idx] = np.int8(1 if delta > 0 else -1)

    if active.any():
        act_idx = idx[active]
        log_mag = E[act_idx].astype(np.float64) + m[act_idx]
        x = sign[act_idx].astype(np.float64) * np.power(10.0, log_mag)
        x_new = x + float(delta)
        abs_x = np.abs(x_new)
        log_abs = np.log10(abs_x)
        new_E = np.floor(log_abs).astype(np.int32)
        new_m = log_abs - new_E.astype(np.float64)
        new_sign = np.where(x_new > 0.0, np.int8(1), np.int8(-1))
        m[act_idx] = new_m
        E[act_idx] = new_E
        sign[act_idx] = new_sign


def step_walkers_f64(m, E, sign, rng):
    choice = rng.integers(0, 4, size=m.shape[0], dtype=np.int8)
    step_a_f64(m, E, choice == 0)
    step_a_inv_f64(m, E, choice == 1)
    step_b_f64(m, E, sign, choice == 2, +1)
    step_b_f64(m, E, sign, choice == 3, -1)


# --- Statistics -------------------------------------------------------

def m_as_fp64(m):
    """Promote object array of mpfr to fp64 for histogramming / Fourier.
    This loses precision for statistics, but we only do high-precision
    DYNAMICS; stats are fp64 and that's fine (they're ensemble averages
    at 10⁵-walker precision, well above fp64 eps)."""
    if m.dtype == object:
        return np.array([float(mv) for mv in m], dtype=np.float64)
    return m.astype(np.float64)


def compute_l1(m_fp64):
    n = m_fp64.shape[0]
    if n == 0:
        return float('nan')
    hist, _ = np.histogram(m_fp64, bins=N_BINS, range=(0.0, 1.0))
    freq = hist.astype(np.float64) / n
    return float(np.sum(np.abs(freq - 1.0 / N_BINS)))


def compute_fourier(m_fp64, modes):
    n = m_fp64.shape[0]
    R = modes.shape[0]
    if n == 0:
        return np.zeros(R, dtype=np.complex128)
    cos_sum = np.zeros(R, dtype=np.float64)
    sin_sum = np.zeros(R, dtype=np.float64)
    two_pi_modes = (2.0 * np.pi * modes.astype(np.float64))[:, None]
    for start in range(0, n, FOURIER_BATCH):
        end = min(start + FOURIER_BATCH, n)
        chunk = m_fp64[start:end][None, :]
        arg = two_pi_modes * chunk
        cos_sum += np.cos(arg).sum(axis=1)
        sin_sum -= np.sin(arg).sum(axis=1)
    cos_sum /= n
    sin_sum /= n
    return cos_sum + 1j * sin_sum


# --- Per-run driver ---------------------------------------------------

def run_sim(label, step_fn, init_fn, out_path, record_probes=False):
    print(f'\n=== {label}: N = {N_WALKERS:_}, n = {N_STEPS} ===')
    rng = np.random.default_rng(SEED)
    t0 = time.time()
    m, E, sign = init_fn(N_WALKERS, rng)
    print(f'  init: {time.time()-t0:.2f}s, m dtype: {m.dtype}')

    n_sample = SAMPLE_TIMES.size
    l1_arr = np.zeros(n_sample, dtype=np.float64)
    h_full = np.zeros((n_sample, MODES.size), dtype=np.complex128)
    l2_norm = np.zeros(n_sample, dtype=np.float64)

    probes = {}  # time -> list of (walker_idx, m_str, E, sign)

    sample_set = set(SAMPLE_TIMES.tolist())
    probe_set = set(PROBE_TIMES)
    sample_idx = 0
    t_start = time.time()

    for step in range(1, N_STEPS + 1):
        step_fn(m, E, sign, rng)

        if step in sample_set:
            m_f64 = m_as_fp64(m)
            h = compute_fourier(m_f64, MODES)
            l1_arr[sample_idx] = compute_l1(m_f64)
            h_full[sample_idx] = h
            l2_norm[sample_idx] = float(np.sqrt(np.sum(np.abs(h) ** 2)))

            if sample_idx % 60 == 0 or step == N_STEPS:
                dt = time.time() - t_start
                rate = step / max(dt, 1e-9)
                eta = (N_STEPS - step) / max(rate, 1e-9)
                print(f'  n={step:4d}  L₁={l1_arr[sample_idx]:.4e}  '
                      f'|ĥ(1)|={abs(h[0]):.4e}  '
                      f'({rate:.2f} s/s, ETA {eta/60:.1f} min)', flush=True)
            sample_idx += 1

        if record_probes and (step in probe_set):
            probe_data = []
            for w in PROBE_INDICES:
                if w < N_WALKERS:
                    mv = m[w]
                    m_str = str(mv) if not isinstance(mv, float) else f'{mv:.20e}'
                    probe_data.append((int(w), m_str, int(E[w]), int(sign[w])))
            probes[step] = probe_data

    total = time.time() - t_start
    print(f'  wall time: {total:.1f}s = {total/60:.2f} min')

    save_dict = dict(
        sample_times=SAMPLE_TIMES,
        l1=l1_arr,
        h_full=h_full,
        l2_norm=l2_norm,
        modes=MODES,
        meta_N=np.int64(N_WALKERS),
        meta_steps=np.int32(N_STEPS),
        meta_bins=np.int32(N_BINS),
        meta_seed=np.int64(SEED),
    )

    if record_probes:
        # Store probe data as a structured object array
        probe_arrs = {}
        for t_probe, probe_list in probes.items():
            probe_arrs[f'probe_n{t_probe}_walker_idx'] = np.array(
                [p[0] for p in probe_list], dtype=np.int64)
            probe_arrs[f'probe_n{t_probe}_m_str'] = np.array(
                [p[1] for p in probe_list], dtype=object)
            probe_arrs[f'probe_n{t_probe}_E'] = np.array(
                [p[2] for p in probe_list], dtype=np.int32)
            probe_arrs[f'probe_n{t_probe}_sign'] = np.array(
                [p[3] for p in probe_list], dtype=np.int8)
        save_dict.update(probe_arrs)

    np.savez_compressed(out_path, **save_dict)
    print(f'  -> {out_path}')


def main():
    print('FP128-CEILING: precision ceiling check')
    print(f'  N = {N_WALKERS:_}, n = {N_STEPS}')
    print(f'  gmpy2 precision (bits): {get_context().precision}')
    print(f'  LOG10_2 at 128-bit: {str(LOG10_2_HP)[:40]}...')
    print(f'  LOG10_SQRT2 at 128-bit: {str(LOG10_SQRT2_HP)[:40]}...')

    # Run 1: fp64 matched control (quick)
    run_sim('fp64 matched control',
            step_walkers_f64, init_ic_b_f64,
            os.path.join(OUT_DIR, 'ic_b_fp64_matched_results.npz'),
            record_probes=True)

    # Run 2: 128-bit (slow)
    run_sim('fp128 (gmpy2 128-bit)',
            step_walkers_hp, init_ic_b_hp,
            os.path.join(OUT_DIR, 'ic_b_fp128_results.npz'),
            record_probes=True)

    print('\n=== FP128-CEILING complete ===')


if __name__ == '__main__':
    main()
