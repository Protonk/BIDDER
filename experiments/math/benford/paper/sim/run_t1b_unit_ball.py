"""
T1B-UNIT-BALL sim: Runs 1, 2, 3 from `T1B-UNIT-BALL-SIM.md`.

All sub-runs: N = 10⁷ walkers, n_max = 600, M1 sample grid,
symmetric step measure (except Run 2 asymmetric variant), R2-style
exact-zero restart at (m = 0, E = 0, sign = sign(delta)), tracking
numerical zero-hit rates throughout.

Run 1 (DYADIC-LADDER) — 8 ICs:
  D1 x=1, D2 x=3/2, D3 x=9/8  (dyadic rationals)
  N1 x=7/5, N2 x=17/12, N3 x=99/70  (non-dyadic rationals)
  I1 x=√2, I2 x=φ  (irrationals)

Run 2 (BROKEN-SYMMETRY) — 2 runs on IC = √2:
  Asymmetric: P(a)=0.255, P(a⁻¹)=0.245, P(b)=P(b⁻¹)=0.25
  Symmetric control at same N for baseline
  Additional output: mean(E), std(E), frozen_fraction per sample time

Run 3 (SMOOTH-IC) — 2 runs:
  S1: m ~ wrapped-Normal(μ=0.5, σ=0.05), E = 0
  S2: same m, E ~ Uniform{−5..5}

Outputs per sub-run under organized subdirectories.

Run: sage -python run_t1b_unit_ball.py
"""

import math
import os
import time
import numpy as np


# --- Config -----------------------------------------------------------

N_WALKERS = 10**7
N_STEPS = 600
N_BINS = 1000
SEED_BASE = 0x1B1CE901

E_THRESH = 20
E_R = 3  # not used in analysis here but kept for metadata consistency

MODES = np.array([1, 2, 3, 4, 5], dtype=np.int32)

SAMPLE_TIMES = np.concatenate([
    np.arange(1, 201, dtype=np.int32),
    np.arange(205, 601, 5, dtype=np.int32),
])

FOURIER_BATCH = 10**7

LOG10_2 = math.log10(2.0)

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
RUN1_DIR = os.path.join(SIM_DIR, 'run1_dyadic_ladder')
RUN2_DIR = os.path.join(SIM_DIR, 'run2_broken_symmetry')
RUN3_DIR = os.path.join(SIM_DIR, 'run3_smooth_ic')
for d in (RUN1_DIR, RUN2_DIR, RUN3_DIR):
    os.makedirs(d, exist_ok=True)


# --- IC initializers --------------------------------------------------

def init_single_value(n, x0):
    """All walkers at x = x0. Decompose log10(|x0|) into (E, m) with
    m ∈ [0, 1) and E ∈ ℤ."""
    assert x0 != 0.0
    sign_val = 1 if x0 > 0 else -1
    log_x = math.log10(abs(x0))
    E_init = int(math.floor(log_x))
    m_init = log_x - float(E_init)
    m = np.full(n, m_init, dtype=np.float64)
    E = np.full(n, E_init, dtype=np.int32)
    sign_arr = np.full(n, sign_val, dtype=np.int8)
    return m, E, sign_arr


def init_smooth_m_delta_E(n, mu, sigma, rng):
    """m ~ wrapped-Normal(μ, σ) on T, E = 0, sign = +1."""
    m = (rng.normal(mu, sigma, size=n) % 1.0).astype(np.float64)
    E = np.zeros(n, dtype=np.int32)
    sign = np.ones(n, dtype=np.int8)
    return m, E, sign


def init_smooth_m_uniform_E(n, mu, sigma, rng, E_range=5):
    """m ~ wrapped-Normal(μ, σ), E ~ Uniform{−E_range..E_range}, sign = +1."""
    m = (rng.normal(mu, sigma, size=n) % 1.0).astype(np.float64)
    E = rng.integers(-E_range, E_range + 1, size=n, dtype=np.int32)
    sign = np.ones(n, dtype=np.int8)
    return m, E, sign


# --- Step kernel ------------------------------------------------------

def step_a(m, E, mask):
    if not mask.any():
        return
    idx = np.where(mask)[0]
    m_new = m[idx] + LOG10_2
    carry = m_new >= 1.0
    m[idx] = np.where(carry, m_new - 1.0, m_new)
    E[idx] += carry.astype(np.int32)


def step_a_inv(m, E, mask):
    if not mask.any():
        return
    idx = np.where(mask)[0]
    m_new = m[idx] - LOG10_2
    borrow = m_new < 0.0
    m[idx] = np.where(borrow, m_new + 1.0, m_new)
    E[idx] -= borrow.astype(np.int32)


def step_b_restart(m, E, sign, mask, delta):
    """R2-style b-step: exact-zero restart at (0, 0, sign(delta)).
    Returns number of exact-zero events."""
    if not mask.any():
        return 0
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

    n_zero = 0
    if active.any():
        act_idx = idx[active]
        log_mag = E[act_idx].astype(np.float64) + m[act_idx]
        x = sign[act_idx].astype(np.float64) * np.power(10.0, log_mag)
        x_new = x + float(delta)
        is_zero = x_new == 0.0
        n_zero = int(is_zero.sum())

        if n_zero > 0:
            zero_idx = act_idx[is_zero]
            m[zero_idx] = 0.0
            E[zero_idx] = 0
            sign[zero_idx] = np.int8(1 if delta > 0 else -1)

        nonzero_mask = ~is_zero
        if nonzero_mask.any():
            nz_idx = act_idx[nonzero_mask]
            x_nz = x_new[nonzero_mask]
            abs_x = np.abs(x_nz)
            log_abs = np.log10(abs_x)
            new_E = np.floor(log_abs).astype(np.int32)
            new_m = log_abs - new_E.astype(np.float64)
            new_sign = np.where(x_nz > 0.0, np.int8(1), np.int8(-1))
            m[nz_idx] = new_m
            E[nz_idx] = new_E
            sign[nz_idx] = new_sign

    return n_zero


def step_walkers_symmetric(m, E, sign, rng):
    """Symmetric measure: 1/4 each action."""
    choice = rng.integers(0, 4, size=m.shape[0], dtype=np.int8)
    step_a(m, E, choice == 0)
    step_a_inv(m, E, choice == 1)
    zh_pos = step_b_restart(m, E, sign, choice == 2, +1)
    zh_neg = step_b_restart(m, E, sign, choice == 3, -1)
    return zh_pos + zh_neg


def step_walkers_weighted(m, E, sign, rng, probs):
    """Weighted step measure with probabilities probs = [P(a), P(a⁻¹),
    P(b), P(b⁻¹)] summing to 1."""
    cum = np.cumsum(probs)
    u = rng.random(m.shape[0])
    action = np.searchsorted(cum, u, side='right').astype(np.int8)
    step_a(m, E, action == 0)
    step_a_inv(m, E, action == 1)
    zh_pos = step_b_restart(m, E, sign, action == 2, +1)
    zh_neg = step_b_restart(m, E, sign, action == 3, -1)
    return zh_pos + zh_neg


# --- Statistics -------------------------------------------------------

def compute_l1(m):
    n = m.shape[0]
    if n == 0:
        return float('nan')
    hist, _ = np.histogram(m, bins=N_BINS, range=(0.0, 1.0))
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
        chunk = m_arr[start:end][None, :]
        arg = two_pi_modes * chunk
        cos_sum += np.cos(arg).sum(axis=1)
        sin_sum -= np.sin(arg).sum(axis=1)
    cos_sum /= n
    sin_sum /= n
    return cos_sum + 1j * sin_sum


# --- Generic runner ---------------------------------------------------

def run_once(label, m, E, sign, rng, out_path, *, probs=None,
             track_E_stats=False, extra_meta=None):
    """Run N_STEPS on (m, E, sign) walkers with given rng. Step
    probabilities default to symmetric; pass `probs` for weighted.
    Returns dict of result arrays."""
    print(f'\n=== {label}: N = {N_WALKERS:_}, n = {N_STEPS} ===')
    n_sample = SAMPLE_TIMES.size
    l1_arr = np.zeros(n_sample, dtype=np.float64)
    h_full = np.zeros((n_sample, MODES.size), dtype=np.complex128)
    l2_norm = np.zeros(n_sample, dtype=np.float64)
    zero_hits_per_step = np.zeros(N_STEPS + 1, dtype=np.int64)

    if track_E_stats:
        mean_E_arr = np.zeros(n_sample, dtype=np.float64)
        std_E_arr = np.zeros(n_sample, dtype=np.float64)
        frozen_frac_arr = np.zeros(n_sample, dtype=np.float64)

    sample_set = set(SAMPLE_TIMES.tolist())
    sample_idx = 0
    t0 = time.time()

    for step in range(1, N_STEPS + 1):
        if probs is None:
            zh = step_walkers_symmetric(m, E, sign, rng)
        else:
            zh = step_walkers_weighted(m, E, sign, rng, probs)
        zero_hits_per_step[step] = zh

        if step in sample_set:
            h = compute_fourier(m, MODES)
            l1_arr[sample_idx] = compute_l1(m)
            h_full[sample_idx] = h
            l2_norm[sample_idx] = float(np.sqrt(np.sum(np.abs(h) ** 2)))

            if track_E_stats:
                E_float = E.astype(np.float64)
                mean_E_arr[sample_idx] = float(E_float.mean())
                std_E_arr[sample_idx] = float(E_float.std())
                frozen_frac_arr[sample_idx] = float((np.abs(E) > E_THRESH).mean())

            if sample_idx % 60 == 0 or step == N_STEPS:
                dt = time.time() - t0
                rate = step / max(dt, 1e-9)
                extra_E = ''
                if track_E_stats:
                    extra_E = (f' mE={mean_E_arr[sample_idx]:+.2f} '
                               f'sE={std_E_arr[sample_idx]:.2f} '
                               f'frz={frozen_frac_arr[sample_idx]:.3f}')
                print(f'  n={step:4d}  L₁={l1_arr[sample_idx]:.4e}  '
                      f'|ĥ(1)|={abs(h[0]):.4e}  zh_cum={int(zero_hits_per_step[:step+1].sum()):_}'
                      f'{extra_E}  ({rate:.2f} s/s)', flush=True)
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
    )
    if track_E_stats:
        save_dict['mean_E'] = mean_E_arr
        save_dict['std_E'] = std_E_arr
        save_dict['frozen_fraction'] = frozen_frac_arr
    if extra_meta:
        for k, v in extra_meta.items():
            save_dict[f'meta_{k}'] = v

    np.savez_compressed(out_path, **save_dict)
    print(f'  -> {out_path}')


# --- Run 1: DYADIC-LADDER ---------------------------------------------

RUN1_ICS = [
    ('D1', 1.0),
    ('D2', 1.5),
    ('D3', 1.125),
    ('N1', 7.0 / 5.0),
    ('N2', 17.0 / 12.0),
    ('N3', 99.0 / 70.0),
    ('I1', math.sqrt(2.0)),
    ('I2', (1.0 + math.sqrt(5.0)) / 2.0),
]


def run1():
    print('\n########## RUN 1 — DYADIC-LADDER ##########')
    for i, (label, x0) in enumerate(RUN1_ICS):
        seed = SEED_BASE ^ (ord('1') << 16) ^ hash(label) & 0xFFFF
        rng = np.random.default_rng(seed)
        m, E, sign = init_single_value(N_WALKERS, x0)
        out_path = os.path.join(RUN1_DIR, f'{label}_results.npz')
        run_once(
            f'Run1 {label}: x={x0}',
            m, E, sign, rng, out_path,
            extra_meta=dict(x0=np.float64(x0), seed=np.int64(seed),
                            ic_label=label),
        )


# --- Run 2: BROKEN-SYMMETRY -------------------------------------------

def run2():
    print('\n########## RUN 2 — BROKEN-SYMMETRY ##########')
    x0 = math.sqrt(2.0)

    # Asymmetric
    seed_asym = SEED_BASE ^ (ord('2') << 16) ^ ord('A')
    rng = np.random.default_rng(seed_asym)
    m, E, sign = init_single_value(N_WALKERS, x0)
    probs_asym = np.array([0.255, 0.245, 0.25, 0.25], dtype=np.float64)
    out_asym = os.path.join(RUN2_DIR, 'asymmetric_results.npz')
    run_once(
        'Run2 asymmetric: √2 IC, d=0.01',
        m, E, sign, rng, out_asym,
        probs=probs_asym, track_E_stats=True,
        extra_meta=dict(x0=np.float64(x0), seed=np.int64(seed_asym),
                        probs=probs_asym, drift=np.float64(0.01)),
    )

    # Symmetric control
    seed_sym = SEED_BASE ^ (ord('2') << 16) ^ ord('S')
    rng = np.random.default_rng(seed_sym)
    m, E, sign = init_single_value(N_WALKERS, x0)
    probs_sym = np.array([0.25, 0.25, 0.25, 0.25], dtype=np.float64)
    out_sym = os.path.join(RUN2_DIR, 'symmetric_results.npz')
    run_once(
        'Run2 symmetric control: √2 IC',
        m, E, sign, rng, out_sym,
        probs=probs_sym, track_E_stats=True,
        extra_meta=dict(x0=np.float64(x0), seed=np.int64(seed_sym),
                        probs=probs_sym, drift=np.float64(0.0)),
    )


# --- Run 3: SMOOTH-IC -------------------------------------------------

def run3():
    print('\n########## RUN 3 — SMOOTH-IC ##########')
    mu, sigma = 0.5, 0.05

    # S1: smooth m, E = 0
    seed_s1 = SEED_BASE ^ (ord('3') << 16) ^ ord('1')
    rng_init = np.random.default_rng(seed_s1)
    m, E, sign = init_smooth_m_delta_E(N_WALKERS, mu, sigma, rng_init)
    rng_walk = np.random.default_rng(seed_s1 ^ 0xDEAD)
    out_s1 = os.path.join(RUN3_DIR, 'S1_results.npz')
    run_once(
        'Run3 S1: m~wN(0.5,0.05), E=0',
        m, E, sign, rng_walk, out_s1,
        extra_meta=dict(mu=np.float64(mu), sigma=np.float64(sigma),
                        E_structure=np.str_('delta'),
                        seed=np.int64(seed_s1)),
    )

    # S2: smooth m, uniform E
    seed_s2 = SEED_BASE ^ (ord('3') << 16) ^ ord('2')
    rng_init = np.random.default_rng(seed_s2)
    m, E, sign = init_smooth_m_uniform_E(N_WALKERS, mu, sigma, rng_init)
    rng_walk = np.random.default_rng(seed_s2 ^ 0xDEAD)
    out_s2 = os.path.join(RUN3_DIR, 'S2_results.npz')
    run_once(
        'Run3 S2: m~wN(0.5,0.05), E~U{-5..5}',
        m, E, sign, rng_walk, out_s2,
        extra_meta=dict(mu=np.float64(mu), sigma=np.float64(sigma),
                        E_structure=np.str_('uniform_5'),
                        seed=np.int64(seed_s2)),
    )


def main():
    print(f'T1B-UNIT-BALL sim')
    print(f'  N = {N_WALKERS:_}, n_max = {N_STEPS}, B = {N_BINS}')
    print(f'  modes = {MODES.tolist()}, E_THRESH = {E_THRESH}')
    print(f'  sample count = {SAMPLE_TIMES.size}')

    run1()
    run2()
    run3()

    print('\n########## All runs complete ##########')


if __name__ == '__main__':
    main()
