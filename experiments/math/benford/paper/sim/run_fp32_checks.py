"""
FP32-SIM: precision-robustness runs.

See `FP32-SIM.md` for the rationale and decision rules. This script
reruns two existing sim setups (M3 IC (b) and the T1B-UNIT-BALL
dyadic-ladder) with the walker mantissa coordinate stored as float32
instead of float64, to test whether the T1b story survives a ~10⁴×
loosening of precision.

Runs on the ARM M1 locally; compatible with being executed in
parallel with x86 beef-box work.

Run: sage -python run_fp32_checks.py
"""

import math
import os
import time
import numpy as np


# --- Config -----------------------------------------------------------

N_WALKERS = 10**7
N_STEPS = 600
N_BINS = 1000
SEED_BASE = 0x32323232

E_THRESH = 20

MODES = np.array([1, 2, 3, 4, 5], dtype=np.int32)

SAMPLE_TIMES = np.concatenate([
    np.arange(1, 201, dtype=np.int32),
    np.arange(205, 601, 5, dtype=np.int32),
])

FOURIER_BATCH = 10**7

# fp64 values for module-level math; cast to fp32 at use site.
LOG10_2_F64 = math.log10(2.0)
LOG10_SQRT2_F64 = 0.5 * LOG10_2_F64

# fp32 versions
LOG10_2 = np.float32(LOG10_2_F64)
LOG10_SQRT2 = np.float32(LOG10_SQRT2_F64)

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SIM_DIR, 'fp32_results')
LADDER_DIR = os.path.join(OUT_DIR, 'dyadic_ladder')
for d in (OUT_DIR, LADDER_DIR):
    os.makedirs(d, exist_ok=True)


# --- IC initializers (all emit fp32 m) --------------------------------

def init_single_value_fp32(n, x0):
    """All walkers at x = x0, with fp32 m coordinate."""
    assert x0 != 0.0
    sign_val = 1 if x0 > 0 else -1
    log_x = math.log10(abs(x0))  # fp64 compute
    E_init = int(math.floor(log_x))
    m_init = np.float32(log_x - float(E_init))
    m = np.full(n, m_init, dtype=np.float32)
    E = np.full(n, E_init, dtype=np.int32)
    sign_arr = np.full(n, sign_val, dtype=np.int8)
    return m, E, sign_arr


def init_ic_b_fp32(n, rng):
    """M3 IC (b): m = log10√2 (fp32 delta), E ~ Uniform{−5..5}."""
    m = np.full(n, LOG10_SQRT2, dtype=np.float32)
    E = rng.integers(-5, 6, size=n, dtype=np.int32)
    sign = np.ones(n, dtype=np.int8)
    return m, E, sign


# --- Step kernel (fp32 m) ---------------------------------------------

def step_a(m, E, mask):
    if not mask.any():
        return
    idx = np.where(mask)[0]
    m_new = m[idx] + LOG10_2
    carry = m_new >= np.float32(1.0)
    m[idx] = np.where(carry, m_new - np.float32(1.0), m_new)
    E[idx] += carry.astype(np.int32)


def step_a_inv(m, E, mask):
    if not mask.any():
        return
    idx = np.where(mask)[0]
    m_new = m[idx] - LOG10_2
    borrow = m_new < np.float32(0.0)
    m[idx] = np.where(borrow, m_new + np.float32(1.0), m_new)
    E[idx] -= borrow.astype(np.int32)


def step_b_restart_fp32(m, E, sign, mask, delta):
    """R2-style b-step with exact-zero restart, fp32 m."""
    if not mask.any():
        return 0
    idx = np.where(mask)[0]
    E_local = E[idx]
    frozen = E_local > E_THRESH
    snap = E_local < -E_THRESH
    active = ~(frozen | snap)

    snap_idx = idx[snap]
    if snap_idx.size > 0:
        m[snap_idx] = np.float32(0.0)
        E[snap_idx] = 0
        sign[snap_idx] = np.int8(1 if delta > 0 else -1)

    n_zero = 0
    if active.any():
        act_idx = idx[active]
        # Reconstruct x in fp32. For |E| ≤ 20, 10^20 = 1e20 < 3.4e38 (fp32 max), OK.
        log_mag = E[act_idx].astype(np.float32) + m[act_idx]
        x = sign[act_idx].astype(np.float32) * np.power(np.float32(10.0), log_mag)
        x_new = x + np.float32(delta)
        is_zero = x_new == np.float32(0.0)
        n_zero = int(is_zero.sum())

        if n_zero > 0:
            zero_idx = act_idx[is_zero]
            m[zero_idx] = np.float32(0.0)
            E[zero_idx] = 0
            sign[zero_idx] = np.int8(1 if delta > 0 else -1)

        nonzero_mask = ~is_zero
        if nonzero_mask.any():
            nz_idx = act_idx[nonzero_mask]
            x_nz = x_new[nonzero_mask]
            abs_x = np.abs(x_nz)
            log_abs = np.log10(abs_x)  # fp32 log
            new_E = np.floor(log_abs).astype(np.int32)
            new_m = log_abs - new_E.astype(np.float32)
            new_sign = np.where(x_nz > np.float32(0.0), np.int8(1), np.int8(-1))
            m[nz_idx] = new_m
            E[nz_idx] = new_E
            sign[nz_idx] = new_sign

    return n_zero


def step_walkers(m, E, sign, rng):
    """Symmetric measure."""
    choice = rng.integers(0, 4, size=m.shape[0], dtype=np.int8)
    step_a(m, E, choice == 0)
    step_a_inv(m, E, choice == 1)
    zh_pos = step_b_restart_fp32(m, E, sign, choice == 2, +1)
    zh_neg = step_b_restart_fp32(m, E, sign, choice == 3, -1)
    return zh_pos + zh_neg


# --- Statistics (fp64 accumulators, fp32 inputs) ----------------------

def compute_l1(m):
    n = m.shape[0]
    if n == 0:
        return float('nan')
    # histogram takes fp32 input, counts are integers
    hist, _ = np.histogram(m, bins=N_BINS, range=(0.0, 1.0))
    freq = hist.astype(np.float64) / n  # fp64 normalization
    return float(np.sum(np.abs(freq - 1.0 / N_BINS)))


def compute_fourier(m_arr, modes):
    """fp64 accumulator with fp32 input. Precision-safe for N up to ~10⁹."""
    n = m_arr.shape[0]
    R = modes.shape[0]
    if n == 0:
        return np.zeros(R, dtype=np.complex128)
    cos_sum = np.zeros(R, dtype=np.float64)
    sin_sum = np.zeros(R, dtype=np.float64)
    two_pi_modes = (2.0 * np.pi * modes.astype(np.float64))[:, None]  # fp64 constants
    for start in range(0, n, FOURIER_BATCH):
        end = min(start + FOURIER_BATCH, n)
        chunk = m_arr[start:end].astype(np.float64)[None, :]  # promote to fp64 for trig
        arg = two_pi_modes * chunk
        cos_sum += np.cos(arg).sum(axis=1)
        sin_sum -= np.sin(arg).sum(axis=1)
    cos_sum /= n
    sin_sum /= n
    return cos_sum + 1j * sin_sum


# --- Generic runner ---------------------------------------------------

def run_once(label, m, E, sign, rng, out_path, extra_meta=None):
    print(f'\n=== {label}: N = {N_WALKERS:_}, n = {N_STEPS} ===')
    print(f'  m dtype: {m.dtype}')
    n_sample = SAMPLE_TIMES.size
    l1_arr = np.zeros(n_sample, dtype=np.float64)
    h_full = np.zeros((n_sample, MODES.size), dtype=np.complex128)
    l2_norm = np.zeros(n_sample, dtype=np.float64)
    zero_hits_per_step = np.zeros(N_STEPS + 1, dtype=np.int64)

    sample_set = set(SAMPLE_TIMES.tolist())
    sample_idx = 0
    t0 = time.time()

    for step in range(1, N_STEPS + 1):
        zh = step_walkers(m, E, sign, rng)
        zero_hits_per_step[step] = zh

        if step in sample_set:
            h = compute_fourier(m, MODES)
            l1_arr[sample_idx] = compute_l1(m)
            h_full[sample_idx] = h
            l2_norm[sample_idx] = float(np.sqrt(np.sum(np.abs(h) ** 2)))

            if sample_idx % 60 == 0 or step == N_STEPS:
                dt = time.time() - t0
                rate = step / max(dt, 1e-9)
                total_zh = int(zero_hits_per_step[:step+1].sum())
                print(f'  n={step:4d}  L₁={l1_arr[sample_idx]:.4e}  '
                      f'|ĥ(1)|={abs(h[0]):.4e}  zh={total_zh:_}  '
                      f'({rate:.2f} s/s)', flush=True)
            sample_idx += 1

    total = time.time() - t0
    total_zh = int(zero_hits_per_step.sum())
    print(f'  wall time: {total:.1f}s = {total/60:.2f} min, total zero-hits = {total_zh:_}')

    save_dict = dict(
        sample_times=SAMPLE_TIMES,
        l1=l1_arr,
        h_full=h_full,
        l2_norm=l2_norm,
        modes=MODES,
        zero_hits_per_step=zero_hits_per_step,
        total_zero_hits=np.int64(total_zh),
        meta_N=np.int64(N_WALKERS),
        meta_steps=np.int32(N_STEPS),
        meta_bins=np.int32(N_BINS),
        meta_dtype=np.str_('float32'),
    )
    if extra_meta:
        for k, v in extra_meta.items():
            save_dict[f'meta_{k}'] = v

    np.savez_compressed(out_path, **save_dict)
    print(f'  -> {out_path}')


# --- Run 1: M3 IC (b) at fp32 ----------------------------------------

def run_ic_b():
    print('\n########## Run 1 — M3 IC (b) at fp32 ##########')
    seed = SEED_BASE ^ ord('B')
    rng = np.random.default_rng(seed)
    m, E, sign = init_ic_b_fp32(N_WALKERS, rng)
    out_path = os.path.join(OUT_DIR, 'ic_b_fp32_results.npz')
    run_once(
        'Run1 IC (b) fp32: m=log₁₀√2, E~U{-5..5}',
        m, E, sign, rng, out_path,
        extra_meta=dict(seed=np.int64(seed),
                        ic_structure=np.str_('m_delta_log10sqrt2_E_uniform_pm5')),
    )


# --- Run 2: Dyadic-ladder at fp32 ------------------------------------

LADDER_ICS = [
    ('D1', 1.0),
    ('D2', 1.5),
    ('D3', 1.125),
    ('N1', 7.0 / 5.0),
    ('N2', 17.0 / 12.0),
    ('N3', 99.0 / 70.0),
    ('I1', math.sqrt(2.0)),
    ('I2', (1.0 + math.sqrt(5.0)) / 2.0),
]


def run_ladder():
    print('\n########## Run 2 — Dyadic-ladder at fp32 ##########')
    for label, x0 in LADDER_ICS:
        seed = SEED_BASE ^ (ord('L') << 16) ^ hash(label) & 0xFFFF
        rng = np.random.default_rng(seed)
        m, E, sign = init_single_value_fp32(N_WALKERS, x0)
        out_path = os.path.join(LADDER_DIR, f'{label}_fp32_results.npz')
        run_once(
            f'Run2 {label} fp32: x={x0}',
            m, E, sign, rng, out_path,
            extra_meta=dict(x0=np.float64(x0),
                            seed=np.int64(seed),
                            ic_label=np.str_(label)),
        )


def main():
    print(f'FP32-SIM: precision-robustness runs')
    print(f'  N = {N_WALKERS:_}, n_max = {N_STEPS}, B = {N_BINS}')
    print(f'  modes = {MODES.tolist()}, E_THRESH = {E_THRESH}')
    print(f'  sample count = {SAMPLE_TIMES.size}')
    print(f'  LOG10_2 (fp32) = {LOG10_2!r}')
    print(f'  LOG10_SQRT2 (fp32) = {LOG10_SQRT2!r}')

    run_ic_b()
    run_ladder()

    print('\n########## FP32-SIM complete ##########')


if __name__ == '__main__':
    main()
