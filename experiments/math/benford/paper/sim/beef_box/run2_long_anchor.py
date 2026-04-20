"""
Run 2 — LONG-ANCHOR.

Beef-box pressure-test of M3 IC (b)'s α̂ = 0.525 anchor on [100, 600],
the single direct measurement of α for T1b. Extends the same IC out to
the M4 horizon (n = 20,000) so we can test whether α stays near 1/2 or
drifts. If stable, the anchor is locked. If it drifts to 0.4 / 0.6 or
curves back to a stretched-exp shape, T1b's exponent claim needs
reassessment.

Spec (per `EXPENSIVE-BEEF-BOX-SIM.md`):
    N = 10⁸ walkers   (plan's recommended baseline; N = 10⁹ was tried
                       and killed at step 301 after 13 hrs when throughput
                       projected to ~37 days on the shared beef box)
    Symmetric measure
    IC: m = log₁₀√2 (delta), E ~ Uniform{−5, …, 5}, sign = +1
        (exactly the M3 IC (b) setup)
    Time range: n = 0 to 20,000
    Sampling:
        every step from n = 1 to 500   (dense, M3-overlap)
        every 10 from n = 500 to 5000
        {7500, 10000, 14000, 20000} beyond
    Exact-zero convention: restart at (m=0, E=0, sign=sign(delta))
        — defensive; should not trigger on this IC, but tracked.
    Output: L₁(n), ensemble ĥ(r, n) for r = 1..5, l2_norm(n),
        per-walker return-count histogram at checkpoints
        {500, 1000, 2000, 5000, 10000, 20000}.

Memory: ~1.3 GB walker state + ~0.4 GB return_counts + ~0.1 GB
prev_in_R + ~1–2 GB transient ⇒ peak ~3 GB on a 64 GB box
(comfortably concurrent with Run 1).

Cost estimate (beef box ≳ 5×10⁷ ws/s): 2×10¹² walker-steps
≈ 11 hrs walk time + sampling/Fourier overhead, matching Run 1.

Run: sage -python run2_long_anchor.py
"""

import math
import os
import time
import numpy as np


# --- Config -----------------------------------------------------------

N_WALKERS = 10**8
N_STEPS = 20000
N_BINS = 1000
SEED = 0xEE1C3A11 ^ ord('b')  # = 0xEE1C3A73, matching M3 IC (b)'s seed.
# Bit-exact trajectory overlap with M3 on [1, 500] is *not* achievable
# because N differs (M3 uses 10⁷; this run uses 10⁹, so the PCG64 stream
# diverges after the first rng.integers() call at init). The matched
# seed keeps any statistical cross-check at the same base point rather
# than an arbitrary one.

E_THRESH = 20
E_R = 3
E_INIT_RANGE = 5  # E ~ Uniform{−5, …, 5}, matching M3 IC (b)

MODES = np.array([1, 2, 3, 4, 5], dtype=np.int32)

# Sampling per plan: dense early (M3 grid), every 10 to 5000, then sparse tail
SAMPLE_TIMES = np.concatenate([
    np.arange(1, 501, dtype=np.int32),
    np.arange(510, 5001, 10, dtype=np.int32),
    np.array([7500, 10000, 14000, 20000], dtype=np.int32),
])

# Per-walker return-count histogram checkpoints
RC_CHECKPOINTS = np.array([500, 1000, 2000, 5000, 10000, 20000], dtype=np.int32)

FOURIER_BATCH = 10**7

LOG10_2 = math.log10(2.0)
LOG10_SQRT2 = 0.5 * LOG10_2

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(SIM_DIR, 'run2_long_anchor_results.npz')

CHECKPOINT_EVERY = 1000


# --- IC initializer (M3 IC (b)) --------------------------------------

def initialize(n, rng):
    """IC (b): m = log₁₀√2 (delta), E ~ Uniform{−5, …, 5}, sign = +1."""
    m = np.full(n, LOG10_SQRT2, dtype=np.float64)
    E = rng.integers(-E_INIT_RANGE, E_INIT_RANGE + 1, size=n, dtype=np.int32)
    sign = np.ones(n, dtype=np.int8)
    return m, E, sign


# --- Step kernel (M1/M3 with R2-style defensive zero restart) --------

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
    """Symmetric b-step with defensive exact-zero restart (R2 convention).
    Returns count of exact-zero events; expected to be 0 for this IC."""
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


def step_walkers(m, E, sign, rng):
    """Returns total exact-zero events this step."""
    choice = rng.integers(0, 4, size=m.shape[0], dtype=np.int8)
    step_a(m, E, choice == 0)
    step_a_inv(m, E, choice == 1)
    n_zero_pos = step_b_restart(m, E, sign, choice == 2, +1)
    n_zero_neg = step_b_restart(m, E, sign, choice == 3, -1)
    return n_zero_pos + n_zero_neg


# --- Statistics -------------------------------------------------------

def compute_l1(m):
    n = m.shape[0]
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


# --- Main -------------------------------------------------------------

def main():
    print('Run 2 — LONG-ANCHOR (M3 IC (b) extended to n = 20,000)')
    print(f'  N = {N_WALKERS:_}, n_max = {N_STEPS}, B = {N_BINS}, modes = {MODES.tolist()}')
    print(f'  IC: m = log₁₀√2, E ~ U{{-{E_INIT_RANGE}..{E_INIT_RANGE}}}, sign = +1')
    print(f'  sample count = {SAMPLE_TIMES.size}')
    print(f'  RC checkpoints = {RC_CHECKPOINTS.tolist()}')
    print(f'  exact-zero convention: restart (defensive)')
    print(f'  seed = {SEED:#x}')
    print()

    rng = np.random.default_rng(SEED)

    t0 = time.time()
    m, E, sign = initialize(N_WALKERS, rng)
    state_gb = (m.nbytes + E.nbytes + sign.nbytes) / 1e9
    print(f'  init: {time.time()-t0:.2f}s, walker state ~{state_gb:.2f} GB')

    # Per-walker return-count bookkeeping for S0-style analysis at long n.
    # An "entry into R" is a 0→1 transition of the predicate |E| ≤ E_R.
    # IC has E ~ U{-5..5}, so most walkers start *outside* R (E_R = 3 means
    # 7 of 11 starting E values are inside, 4 are outside). prev_in_R is
    # initialized to the actual starting membership, so the first entry
    # into R from a walker that starts outside is correctly counted.
    return_counts = np.zeros(N_WALKERS, dtype=np.int32)
    prev_in_R = (np.abs(E) <= E_R)
    rc_state_gb = (return_counts.nbytes + prev_in_R.nbytes) / 1e9
    print(f'  return-count bookkeeping ~{rc_state_gb:.2f} GB')

    n_sample = SAMPLE_TIMES.size
    l1_arr = np.zeros(n_sample, dtype=np.float64)
    h_full = np.zeros((n_sample, MODES.size), dtype=np.complex128)
    l2_norm = np.zeros(n_sample, dtype=np.float64)

    zero_hits_per_step = np.zeros(N_STEPS + 1, dtype=np.int64)

    # RC histograms saved per-checkpoint (ragged; pad on save).
    rc_hists = {}

    sample_set = set(SAMPLE_TIMES.tolist())
    rc_set = set(RC_CHECKPOINTS.tolist())
    sample_idx = 0
    t_start = time.time()

    for step in range(1, N_STEPS + 1):
        n_zero = step_walkers(m, E, sign, rng)
        zero_hits_per_step[step] = n_zero

        # Update return counts (0→1 entries into R)
        in_R_now = np.abs(E) <= E_R
        entered_R = in_R_now & ~prev_in_R
        return_counts[entered_R] += 1
        prev_in_R = in_R_now

        if step in sample_set:
            h = compute_fourier(m, MODES)
            l1_arr[sample_idx] = compute_l1(m)
            h_full[sample_idx] = h
            l2_norm[sample_idx] = float(np.sqrt(np.sum(np.abs(h) ** 2)))

            if (sample_idx % 50 == 0) or step == N_STEPS:
                dt = time.time() - t_start
                rate = step / max(dt, 1e-9)
                eta = (N_STEPS - step) / max(rate, 1e-9)
                cum_zh = int(zero_hits_per_step[:step + 1].sum())
                print(f'  n={step:6d}  L₁={l1_arr[sample_idx]:.5e}  '
                      f'|ĥ(1)|={abs(h[0]):.4e}  '
                      f'zero hits cum={cum_zh:_}  '
                      f'({rate:.2f} steps/s, ETA {eta/3600:.1f} hrs)',
                      flush=True)
            sample_idx += 1

        # Per-walker return-count histogram at checkpoints
        if step in rc_set:
            max_k = int(return_counts.max())
            hist = np.bincount(return_counts, minlength=max_k + 1)
            rc_hists[int(step)] = hist
            print(f'    RC checkpoint n={step}: max N_n = {max_k}, '
                  f'mean N_n = {return_counts.mean():.3f}', flush=True)

        # Periodic checkpoint save
        if step % CHECKPOINT_EVERY == 0 and step > 0:
            keys = sorted(rc_hists.keys())
            if keys:
                L = max(len(rc_hists[k]) for k in keys)
                rc_stack = np.zeros((len(keys), L), dtype=np.int64)
                for i, k in enumerate(keys):
                    rc_stack[i, :len(rc_hists[k])] = rc_hists[k]
                rc_keys_arr = np.array(keys, dtype=np.int32)
            else:
                rc_keys_arr = np.zeros(0, dtype=np.int32)
                rc_stack = np.zeros((0, 0), dtype=np.int64)

            np.savez_compressed(
                OUT_PATH + '.partial',
                sample_times=SAMPLE_TIMES[:sample_idx],
                l1=l1_arr[:sample_idx],
                h_full=h_full[:sample_idx],
                l2_norm=l2_norm[:sample_idx],
                modes=MODES,
                zero_hits_per_step=zero_hits_per_step[:step + 1],
                rc_checkpoints=rc_keys_arr,
                rc_histograms=rc_stack,
                meta_N=np.int64(N_WALKERS),
                meta_steps=np.int32(step),
                meta_bins=np.int32(N_BINS),
                meta_E_R=np.int32(E_R),
                meta_E_THRESH=np.int32(E_THRESH),
                meta_E_INIT_RANGE=np.int32(E_INIT_RANGE),
                meta_seed=np.int64(SEED),
                checkpoint_step=np.int32(step),
            )

    total_time = time.time() - t_start
    total_zero = int(zero_hits_per_step.sum())
    print(f'\nTotal walk time: {total_time:.1f}s = {total_time/3600:.2f} hrs')
    print(f'Throughput: {N_WALKERS * N_STEPS / total_time:.2e} walker-steps/s')
    print(f'Total exact-zero hits: {total_zero:_} '
          f'({total_zero / (N_WALKERS * N_STEPS):.2e} per walker-step)')

    print()
    print('=== L₁ at key times ===')
    for target in [10, 100, 500, 1000, 2000, 5000, 10000, 20000]:
        if target in sample_set:
            i = np.argmin(np.abs(SAMPLE_TIMES - target))
            print(f'  n={int(SAMPLE_TIMES[i]):6d}  L₁={l1_arr[i]:.4e}')

    # Pad and stack the per-checkpoint RC histograms (they have different lengths).
    keys = sorted(rc_hists.keys())
    if keys:
        L = max(len(rc_hists[k]) for k in keys)
        rc_stack = np.zeros((len(keys), L), dtype=np.int64)
        for i, k in enumerate(keys):
            rc_stack[i, :len(rc_hists[k])] = rc_hists[k]
        rc_keys_arr = np.array(keys, dtype=np.int32)
    else:
        rc_keys_arr = np.zeros(0, dtype=np.int32)
        rc_stack = np.zeros((0, 0), dtype=np.int64)

    np.savez_compressed(
        OUT_PATH,
        sample_times=SAMPLE_TIMES,
        l1=l1_arr,
        h_full=h_full,
        l2_norm=l2_norm,
        modes=MODES,
        zero_hits_per_step=zero_hits_per_step,
        rc_checkpoints=rc_keys_arr,
        rc_histograms=rc_stack,
        meta_N=np.int64(N_WALKERS),
        meta_steps=np.int32(N_STEPS),
        meta_bins=np.int32(N_BINS),
        meta_E_R=np.int32(E_R),
        meta_E_THRESH=np.int32(E_THRESH),
        meta_E_INIT_RANGE=np.int32(E_INIT_RANGE),
        meta_seed=np.int64(SEED),
    )

    partial = OUT_PATH + '.partial'
    if os.path.exists(partial):
        os.remove(partial)

    print(f'\n-> {OUT_PATH}')


if __name__ == '__main__':
    main()
