"""
B3 — Excursion-resolved mode coupling matrix.

Measures the empirical mode-coupling matrix K̂ of the return operator
T_R directly. For each completed excursion of a walker (leave R → return
to R), accumulate

    K̂_{rs} += e^{−2πi r m_return} · e^{+2πi s m_enter}

over r, s ∈ {1..5}, normalized by total excursion count at the end.

Diagonal |K̂_{rr}| = per-mode net contraction per return cycle.
Off-diagonal |K̂_{rs}|, r ≠ s = cross-mode injection per return.
ρ(K̂) = creation-destruction balance; compare to γ_r^{c'}.

Analytic γ_r = (1/2)(1 + cos(2π r log₁₀ 2)), the per-step rotation
multiplier outside R, is reported for reference.

Run: sage -python run_b3.py
"""

import math
import os
import time
import numpy as np


# --- Config -----------------------------------------------------------

N_WALKERS = 10**7
N_STEPS = 600
SEED = 0xB3B3B3B3

E_THRESH = 20
E_R = 3

MODES = np.array([1, 2, 3, 4, 5], dtype=np.int32)

LOG10_2 = math.log10(2.0)
LOG10_SQRT2 = 0.5 * LOG10_2

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(SIM_DIR, 'b3_results.npz')


# --- State + step helpers (same as M1) --------------------------------

def initialize(n):
    m = np.full(n, LOG10_SQRT2, dtype=np.float64)
    E = np.zeros(n, dtype=np.int32)
    sign = np.ones(n, dtype=np.int8)
    return m, E, sign


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


def step_b(m, E, sign, mask, delta):
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


def step_walkers(m, E, sign, rng):
    choice = rng.integers(0, 4, size=m.shape[0], dtype=np.int8)
    step_a(m, E, choice == 0)
    step_a_inv(m, E, choice == 1)
    step_b(m, E, sign, choice == 2, +1)
    step_b(m, E, sign, choice == 3, -1)


# --- B3 accumulators --------------------------------------------------

def accumulate_K(m_return, m_enter, modes, K_accum):
    """Vectorized accumulation of K̂_{rs} over all excursion pairs in a step."""
    if m_return.size == 0:
        return
    # a[r, k] = exp(-2πi · r · m_return_k), shape (R, K)
    two_pi_r = (2.0 * np.pi * modes.astype(np.float64))[:, None]
    a = np.exp(-1j * two_pi_r * m_return[None, :])
    b = np.exp(+1j * two_pi_r * m_enter[None, :])
    # K contribution (R, R): sum over excursions of a * conj(b^*)... but b is already conjugated-direction
    # We want e^{-2πi r m_return} · e^{+2πi s m_enter}; so K[r,s] = sum_k a[r,k] * b[s,k]
    K_accum += a @ b.T


def main():
    print('B3 — Excursion-resolved mode coupling')
    print(f'  N = {N_WALKERS:_}, steps = {N_STEPS}, E_R = {E_R}, E_THRESH = {E_THRESH}')
    print(f'  modes = {MODES.tolist()}')

    rng = np.random.default_rng(SEED)

    t0 = time.time()
    m, E, sign = initialize(N_WALKERS)
    print(f'  init: {time.time()-t0:.2f}s, state ~{(m.nbytes + E.nbytes + sign.nbytes) / 1e9:.2f} GB')

    # All walkers start inside R (E=0, E_R≥0)
    prev_in_R = np.ones(N_WALKERS, dtype=bool)

    # Per-walker pending_m_enter: mantissa at the moment the walker last left R.
    # NaN when the walker is currently inside R.
    pending_m_enter = np.full(N_WALKERS, np.nan, dtype=np.float64)

    # Mode-coupling accumulator and counters
    K_accum = np.zeros((MODES.size, MODES.size), dtype=np.complex128)
    total_excursions = 0
    excursions_per_step = np.zeros(N_STEPS + 1, dtype=np.int64)
    excursion_length_hist = np.zeros(N_STEPS + 2, dtype=np.int64)

    # Per-walker excursion length bookkeeping
    current_excursion_start = np.zeros(N_WALKERS, dtype=np.int32)

    t_start = time.time()

    for step in range(1, N_STEPS + 1):
        step_walkers(m, E, sign, rng)

        in_R_now = np.abs(E) <= E_R
        left_R = prev_in_R & ~in_R_now
        returned_R = ~prev_in_R & in_R_now

        # Walkers that left R this step: record their current m as m_enter of new excursion
        if left_R.any():
            left_idx = np.where(left_R)[0]
            pending_m_enter[left_idx] = m[left_idx]
            current_excursion_start[left_idx] = step

        # Walkers that returned to R this step: close their excursion
        if returned_R.any():
            ret_idx = np.where(returned_R)[0]
            m_ret = m[ret_idx]
            m_ent = pending_m_enter[ret_idx]
            valid = ~np.isnan(m_ent)
            if valid.any():
                m_ret_v = m_ret[valid]
                m_ent_v = m_ent[valid]
                accumulate_K(m_ret_v, m_ent_v, MODES, K_accum)
                excursions_this_step = int(valid.sum())
                total_excursions += excursions_this_step
                excursions_per_step[step] = excursions_this_step

                # Excursion length histogram
                lens = step - current_excursion_start[ret_idx[valid]]
                # clip defensively
                lens_clipped = np.clip(lens, 0, N_STEPS + 1)
                bc = np.bincount(lens_clipped, minlength=N_STEPS + 2)
                excursion_length_hist += bc[:N_STEPS + 2]

            pending_m_enter[ret_idx] = np.nan

        prev_in_R = in_R_now

        if step % 50 == 0 or step == N_STEPS:
            dt = time.time() - t_start
            rate = step / max(dt, 1e-9)
            eta = (N_STEPS - step) / max(rate, 1e-9)
            n_pending = int(np.sum(~np.isnan(pending_m_enter)))
            print(f'  step {step:4d}/{N_STEPS}  excursions so far = {total_excursions:_}  '
                  f'pending = {n_pending:_}  ({rate:.1f} steps/s, ETA {eta:.0f}s)', flush=True)

    total_time = time.time() - t_start
    print(f'\nTotal B3 time: {total_time:.1f}s = {total_time/60:.2f} min')
    print(f'Total completed excursions: {total_excursions:_}')
    print(f'Mean excursions per walker: {total_excursions / N_WALKERS:.3f}')

    if total_excursions == 0:
        print('WARNING: zero completed excursions; K̂ undefined.')
        return

    # Normalize
    K_hat = K_accum / total_excursions
    print('\n|K̂| matrix (modes 1..5):')
    abs_K = np.abs(K_hat)
    print('       s=1         s=2         s=3         s=4         s=5')
    for i, r in enumerate(MODES):
        row = '   '.join(f'{abs_K[i, j]:.4e}' for j in range(MODES.size))
        print(f'  r={r}: {row}')

    # Spectral radius
    eigs = np.linalg.eigvals(K_hat)
    rho = float(np.max(np.abs(eigs)))
    print(f'\nρ(K̂) = max |eigenvalue| = {rho:.4f}')
    print(f'|eigenvalues|: {sorted(np.abs(eigs).tolist(), reverse=True)}')

    # Diagonal dominance
    for i, r in enumerate(MODES):
        diag = abs_K[i, i]
        off_sum = abs_K[i].sum() - diag
        print(f'  r={r}: |K_rr|={diag:.4e}, sum off-diag |K_rs|={off_sum:.4e}, '
              f'ratio off/diag = {off_sum/max(diag,1e-20):.3f}')

    # Analytic γ_r per-step for comparison
    print('\nAnalytic γ_r = (1/2)(1 + cos(2π r log₁₀2))  (per-step outside R):')
    for r in MODES:
        gamma_r = 0.5 * (1.0 + math.cos(2.0 * math.pi * float(r) * LOG10_2))
        print(f'  r={r}: γ_r = {gamma_r:.4f}')

    # Mean excursion length
    lens_vals = np.arange(excursion_length_hist.size)
    mean_len = float((lens_vals * excursion_length_hist).sum() / max(total_excursions, 1))
    print(f'\nMean excursion length = {mean_len:.3f} steps')
    print(f'Mean time-in-R per return cycle ≈ 1 (entering R is one step)')

    # Save
    np.savez_compressed(
        OUT_PATH,
        K_hat=K_hat,
        abs_K=abs_K,
        modes=MODES,
        total_excursions=np.int64(total_excursions),
        mean_excursions_per_walker=np.float64(total_excursions / N_WALKERS),
        eigenvalues=eigs,
        spectral_radius=np.float64(rho),
        excursions_per_step=excursions_per_step,
        excursion_length_hist=excursion_length_hist,
        mean_excursion_length=np.float64(mean_len),
        gamma_r=np.array([0.5 * (1.0 + math.cos(2.0 * math.pi * float(r) * LOG10_2)) for r in MODES]),
        meta_N=np.int64(N_WALKERS),
        meta_steps=np.int32(N_STEPS),
        meta_E_R=np.int32(E_R),
        meta_seed=np.int64(SEED),
    )
    print(f'\n-> {OUT_PATH}')


if __name__ == '__main__':
    main()
