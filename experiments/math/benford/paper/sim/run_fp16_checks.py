"""
FP16-MINI-SIM: precision ladder completion.

Runs a reduced-scope fp16 sim plus a matched-E_THRESH fp32 control
to construct a three-point precision ladder (fp64 / fp32 / fp16)
for Result 5's zero-hit-rate observation.

See `FP16-MINI-SIM.md` for rationale and decision rules.

Run: sage -python run_fp16_checks.py
"""

import math
import os
import time
import numpy as np


# --- Config -----------------------------------------------------------

N_WALKERS = 10**7
N_STEPS = 100
N_BINS = 1000
SEED_BASE = 0x16161616

E_THRESH = 3  # Reduced from 20; fp16 overflows at 10^(E+m) for E ≥ 4

MODES = np.array([1, 2, 3, 4, 5], dtype=np.int32)

# Sample every 10 steps from n=10 to 100 (mini horizon).
SAMPLE_TIMES = np.arange(10, N_STEPS + 1, 10, dtype=np.int32)

FOURIER_BATCH = 10**7

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SIM_DIR, 'fp16_results')
RUN1_DIR = os.path.join(OUT_DIR, 'run1_fp16')
RUN2_DIR = os.path.join(OUT_DIR, 'run2_fp32_control')
for d in (OUT_DIR, RUN1_DIR, RUN2_DIR):
    os.makedirs(d, exist_ok=True)

# fp64 truth values
LOG10_2_F64 = math.log10(2.0)
LOG10_SQRT2_F64 = 0.5 * LOG10_2_F64


# --- Step kernel, parameterized by dtype ------------------------------

def make_constants(dtype):
    """Return LOG10_2 and related constants cast to the given dtype."""
    one = dtype(1.0)
    zero = dtype(0.0)
    ten = dtype(10.0)
    log10_2 = dtype(LOG10_2_F64)
    log10_sqrt2 = dtype(LOG10_SQRT2_F64)
    return dict(one=one, zero=zero, ten=ten,
                log10_2=log10_2, log10_sqrt2=log10_sqrt2)


def step_a(m, E, mask, consts):
    if not mask.any():
        return
    idx = np.where(mask)[0]
    m_new = m[idx] + consts['log10_2']
    carry = m_new >= consts['one']
    m[idx] = np.where(carry, m_new - consts['one'], m_new)
    E[idx] += carry.astype(np.int32)


def step_a_inv(m, E, mask, consts):
    if not mask.any():
        return
    idx = np.where(mask)[0]
    m_new = m[idx] - consts['log10_2']
    borrow = m_new < consts['zero']
    m[idx] = np.where(borrow, m_new + consts['one'], m_new)
    E[idx] -= borrow.astype(np.int32)


def step_b_restart(m, E, sign, was_snapped, mask, delta, consts, dtype):
    """Exact-zero restart convention with pristine-walker tracking.

    Returns (n_zero_total, n_zero_pristine, n_active).
    - n_zero_total: all x_new==0 events in active branch (same as before)
    - n_zero_pristine: subset where walker had not previously been
      snapped or zero-hit. These are the precision-induced signal.
    """
    if not mask.any():
        return 0, 0, 0
    idx = np.where(mask)[0]
    E_local = E[idx]
    frozen = E_local > E_THRESH
    snap = E_local < -E_THRESH
    active = ~(frozen | snap)
    n_active = int(active.sum())

    snap_idx = idx[snap]
    if snap_idx.size > 0:
        m[snap_idx] = consts['zero']
        E[snap_idx] = 0
        sign[snap_idx] = np.int8(1 if delta > 0 else -1)
        was_snapped[snap_idx] = True  # walker is post-snap now

    n_zero = 0
    n_zero_pristine = 0
    if active.any():
        act_idx = idx[active]
        log_mag = E[act_idx].astype(dtype) + m[act_idx]
        x = sign[act_idx].astype(dtype) * np.power(consts['ten'], log_mag)
        x_new = x + dtype(delta)
        is_zero = x_new == consts['zero']
        n_zero = int(is_zero.sum())

        if n_zero > 0:
            zero_idx = act_idx[is_zero]
            # Subset of zero-hit walkers that were still pristine.
            pristine_mask = ~was_snapped[zero_idx]
            n_zero_pristine = int(pristine_mask.sum())
            # Restart all zero-hit walkers and mark them post-snap.
            m[zero_idx] = consts['zero']
            E[zero_idx] = 0
            sign[zero_idx] = np.int8(1 if delta > 0 else -1)
            was_snapped[zero_idx] = True

        nonzero_mask = ~is_zero
        if nonzero_mask.any():
            nz_idx = act_idx[nonzero_mask]
            x_nz = x_new[nonzero_mask]
            abs_x = np.abs(x_nz)
            log_abs = np.log10(abs_x)
            new_E = np.floor(log_abs).astype(np.int32)
            new_m = log_abs - new_E.astype(dtype)
            new_sign = np.where(x_nz > consts['zero'], np.int8(1), np.int8(-1))
            m[nz_idx] = new_m
            E[nz_idx] = new_E
            sign[nz_idx] = new_sign

    return n_zero, n_zero_pristine, n_active


def step_walkers(m, E, sign, was_snapped, rng, consts, dtype):
    """Symmetric measure. Returns (zero_hits_total, zero_hits_pristine, active_count)."""
    choice = rng.integers(0, 4, size=m.shape[0], dtype=np.int8)
    step_a(m, E, choice == 0, consts)
    step_a_inv(m, E, choice == 1, consts)
    zh_pos, zhp_pos, act_pos = step_b_restart(m, E, sign, was_snapped, choice == 2, +1, consts, dtype)
    zh_neg, zhp_neg, act_neg = step_b_restart(m, E, sign, was_snapped, choice == 3, -1, consts, dtype)
    return zh_pos + zh_neg, zhp_pos + zhp_neg, act_pos + act_neg




# --- IC initializers --------------------------------------------------

def init_single_value(n, x0, dtype):
    """All walkers at x = x0, m coord in the given dtype."""
    assert x0 != 0.0
    sign_val = 1 if x0 > 0 else -1
    log_x = math.log10(abs(x0))  # fp64 compute
    E_init = int(math.floor(log_x))
    m_init = dtype(log_x - float(E_init))
    m = np.full(n, m_init, dtype=dtype)
    E = np.full(n, E_init, dtype=np.int32)
    sign_arr = np.full(n, sign_val, dtype=np.int8)
    return m, E, sign_arr


def init_b_like(n, rng, dtype):
    """IC (b) analog: m = log₁₀√2 delta, E ~ Uniform{−3..3}."""
    consts = make_constants(dtype)
    m = np.full(n, consts['log10_sqrt2'], dtype=dtype)
    E = rng.integers(-E_THRESH, E_THRESH + 1, size=n, dtype=np.int32)
    sign = np.ones(n, dtype=np.int8)
    return m, E, sign


# --- Statistics (fp64 accumulators) -----------------------------------

def compute_l1(m):
    n = m.shape[0]
    if n == 0:
        return float('nan')
    # Histogram input is fp16/fp32/fp64; need to cast to fp64 for histogram.
    hist, _ = np.histogram(m.astype(np.float64), bins=N_BINS, range=(0.0, 1.0))
    freq = hist.astype(np.float64) / n
    return float(np.sum(np.abs(freq - 1.0 / N_BINS)))


def compute_fourier(m_arr, modes):
    n = m_arr.shape[0]
    R = modes.shape[0]
    if n == 0:
        return np.zeros(R, dtype=np.complex128)
    cos_sum = np.zeros(R, dtype=np.float64)
    sin_sum = np.zeros(R, dtype=np.float64)
    two_pi_modes = (2.0 * np.pi * modes.astype(np.float64))[:, None]
    for start in range(0, n, FOURIER_BATCH):
        end = min(start + FOURIER_BATCH, n)
        chunk = m_arr[start:end].astype(np.float64)[None, :]
        arg = two_pi_modes * chunk
        cos_sum += np.cos(arg).sum(axis=1)
        sin_sum -= np.sin(arg).sum(axis=1)
    cos_sum /= n
    sin_sum /= n
    return cos_sum + 1j * sin_sum


# --- Runner -----------------------------------------------------------

def run_once(label, init_fn, rng, dtype, out_path, extra_meta=None):
    """init_fn signature: (N_WALKERS, rng, dtype) -> (m, E, sign)."""
    print(f'\n=== {label}: N = {N_WALKERS:_}, n = {N_STEPS}, dtype = {dtype.__name__} ===')
    consts = make_constants(dtype)
    m, E, sign = init_fn(N_WALKERS, rng, dtype)
    was_snapped = np.zeros(N_WALKERS, dtype=bool)

    n_sample = SAMPLE_TIMES.size
    l1_arr = np.zeros(n_sample, dtype=np.float64)
    h_full = np.zeros((n_sample, MODES.size), dtype=np.complex128)
    zero_hits_per_step = np.zeros(N_STEPS + 1, dtype=np.int64)
    zero_hits_pristine_per_step = np.zeros(N_STEPS + 1, dtype=np.int64)
    active_per_step = np.zeros(N_STEPS + 1, dtype=np.int64)

    sample_set = set(SAMPLE_TIMES.tolist())
    sample_idx = 0
    t0 = time.time()

    for step in range(1, N_STEPS + 1):
        zh, zh_pristine, act = step_walkers(m, E, sign, was_snapped, rng, consts, dtype)
        zero_hits_per_step[step] = zh
        zero_hits_pristine_per_step[step] = zh_pristine
        active_per_step[step] = act

        if step in sample_set:
            h = compute_fourier(m, MODES)
            l1_arr[sample_idx] = compute_l1(m)
            h_full[sample_idx] = h
            if sample_idx % 5 == 0 or step == N_STEPS:
                dt = time.time() - t0
                rate = step / max(dt, 1e-9)
                total_zh = int(zero_hits_per_step[:step+1].sum())
                total_zh_pr = int(zero_hits_pristine_per_step[:step+1].sum())
                print(f'  n={step:4d}  L₁={l1_arr[sample_idx]:.4e}  '
                      f'|ĥ(1)|={abs(h[0]):.4e}  zh={total_zh:_} (pristine={total_zh_pr:_})  '
                      f'active={act:_}  ({rate:.2f} s/s)', flush=True)
            sample_idx += 1

    total = time.time() - t0
    total_zh = int(zero_hits_per_step.sum())
    total_zh_pristine = int(zero_hits_pristine_per_step.sum())
    total_active = int(active_per_step.sum())
    total_walker_steps = N_WALKERS * N_STEPS
    print(f'  wall time: {total:.1f}s = {total/60:.2f} min')
    print(f'  total zero-hits: {total_zh:,}   (pristine only: {total_zh_pristine:,})')
    print(f'  total active b-step operations: {total_active:,}')
    print(f'  pristine rate per active op: {total_zh_pristine / max(total_active, 1):.3e}')
    print(f'  pristine rate per total walker-step: {total_zh_pristine / total_walker_steps:.3e}')

    save_dict = dict(
        sample_times=SAMPLE_TIMES,
        l1=l1_arr,
        h_full=h_full,
        modes=MODES,
        zero_hits_per_step=zero_hits_per_step,
        zero_hits_pristine_per_step=zero_hits_pristine_per_step,
        active_per_step=active_per_step,
        total_zero_hits=np.int64(total_zh),
        total_zero_hits_pristine=np.int64(total_zh_pristine),
        total_active_ops=np.int64(total_active),
        meta_N=np.int64(N_WALKERS),
        meta_steps=np.int32(N_STEPS),
        meta_E_THRESH=np.int32(E_THRESH),
        meta_dtype=np.str_(dtype.__name__),
    )
    if extra_meta:
        for k, v in extra_meta.items():
            save_dict[f'meta_{k}'] = v
    np.savez_compressed(out_path, **save_dict)
    print(f'  -> {out_path}')


# --- IC set: representative subset -----------------------------------

# For single-value ICs: (label, x0)
SINGLE_ICS = [
    ('D1', 1.0),
    ('N1', 7.0 / 5.0),
    ('I1', math.sqrt(2.0)),
    ('I2', (1.0 + math.sqrt(5.0)) / 2.0),
]


def run_block(out_dir, dtype, tag):
    """Run all single-value ICs + IC (b) analog at given dtype."""
    for label, x0 in SINGLE_ICS:
        seed = SEED_BASE ^ hash((tag, label)) & 0xFFFFFFFF
        rng = np.random.default_rng(seed)
        # Wrap init_single_value for uniform signature
        def init_fn(n, rng_, dtype_, _x0=x0):
            return init_single_value(n, _x0, dtype_)
        out_path = os.path.join(out_dir, f'{label}_{tag}_results.npz')
        run_once(f'{tag} {label} (x={x0})', init_fn, rng, dtype, out_path,
                 extra_meta=dict(x0=np.float64(x0), seed=np.int64(seed),
                                 ic_label=np.str_(label)))

    # IC (b) analog
    seed = SEED_BASE ^ hash((tag, 'B')) & 0xFFFFFFFF
    rng = np.random.default_rng(seed)
    def init_b(n, rng_, dtype_):
        return init_b_like(n, rng_, dtype_)
    out_path = os.path.join(out_dir, f'B-like_{tag}_results.npz')
    run_once(f'{tag} B-like (m=log₁₀√2 δ, E~U{{−3..3}})', init_b, rng, dtype, out_path,
             extra_meta=dict(seed=np.int64(seed),
                             ic_structure=np.str_('m_delta_log10sqrt2_E_uniform_pm_E_THRESH')))


def main():
    print(f'FP16-MINI-SIM: precision ladder')
    print(f'  N = {N_WALKERS:_}, n_max = {N_STEPS}, E_THRESH = {E_THRESH}')
    print(f'  ICs: {[l for l, _ in SINGLE_ICS]} + B-like')

    print('\n########## Run 1 — fp16 ##########')
    run_block(RUN1_DIR, np.float16, 'fp16')

    print('\n########## Run 2 — fp32 control (E_THRESH=3) ##########')
    run_block(RUN2_DIR, np.float32, 'fp32_ctrl')

    # Run 3 — fp64 control (also at E_THRESH=3).
    # Needed as the "snap-induced baseline": because E_THRESH=3 is much
    # smaller than the usual 20, walkers reach |E|>3 frequently. Each
    # such event triggers the snap branch, re-emitting walkers at x=±1,
    # where the next b-step has 1/4 chance of producing x_new=0 exactly
    # via arithmetic, *at any precision*. So some fraction of zero-hits
    # at any dtype is mechanical, not precision-driven. The fp64 control
    # measures that mechanical baseline; fp32-control subtracts to give
    # the fp32 precision signal; fp16 subtracts to give fp16 precision.
    run3_dir = os.path.join(OUT_DIR, 'run3_fp64_control')
    os.makedirs(run3_dir, exist_ok=True)
    print('\n########## Run 3 — fp64 control (E_THRESH=3, snap baseline) ##########')
    run_block(run3_dir, np.float64, 'fp64_ctrl')

    print('\n########## FP16-MINI-SIM complete ##########')


if __name__ == '__main__':
    main()
