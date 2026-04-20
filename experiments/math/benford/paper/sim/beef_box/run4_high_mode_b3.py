"""
Run 4 — HIGH-MODE-B3.

Beef-box pressure-test of B3's Result 2 — ρ(K̂_5) = 0.924 from the
empirical mode-coupling matrix on r = 1..5. The BENTHIC framework
wants the spectral radius of the full operator; if the 5-mode
truncation is hiding a slower-contracting (or super-unit) high-mode
band, the "injection-dominated but ρ < 1" classification weakens.

This run repeats B3's setup but accumulates a 20×20 K̂ over modes
r = 1..20 and reports:

  - ρ(K̂_20):                full spectral radius
  - truncation ladder:       ρ(K̂_5), ρ(K̂_10), ρ(K̂_15), ρ(K̂_20)
  - banded ρ:                ρ on each 5×5 diagonal block
                             ([1..5], [6..10], [11..15], [16..20])
  - singular-value structure: top 5 σᵢ of K̂_20

Spec (per `EXPENSIVE-BEEF-BOX-SIM.md`):
    N = 10⁷ walkers   (same as B3)
    Symmetric measure
    IC: x = +√2       (same as B3)
    Time range: n = 0 to 600
    Modes: r = 1..20
    Exact-zero convention: none (√2 IC algebraically excludes 0)

Cost (beef box): K̂ update is now 20² = 400 flops/excursion vs 25 in
B3, plus 4× more cos/sin per accumulate. Estimate 5–10 min.

Run: sage -python run4_high_mode_b3.py
"""

import math
import os
import time
import numpy as np


# --- Config -----------------------------------------------------------

N_WALKERS = 10**7
N_STEPS = 600

E_THRESH = 20
E_R = 3

R_MAX = 20
MODES = np.arange(1, R_MAX + 1, dtype=np.int32)

SEED = 0xB3B3B3B3 ^ R_MAX  # = 0xB3B3B3A7, B3 seed XOR mode count, to keep RNG distinct from B3

LOG10_2 = math.log10(2.0)
LOG10_SQRT2 = 0.5 * LOG10_2

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(SIM_DIR, 'run4_high_mode_b3_results.npz')


# --- State + step helpers (same as M1/B3) -----------------------------

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


# --- B3 mode-coupling accumulator (same logic, R = 20) ----------------

def accumulate_K(m_return, m_enter, modes, K_accum):
    """K̂[r,s] += Σ_k exp(-2πi r m_return_k) · exp(+2πi s m_enter_k)."""
    if m_return.size == 0:
        return
    two_pi_r = (2.0 * np.pi * modes.astype(np.float64))[:, None]
    a = np.exp(-1j * two_pi_r * m_return[None, :])    # (R, K)
    b = np.exp(+1j * two_pi_r * m_enter[None, :])     # (R, K)
    K_accum += a @ b.T


# --- Banded analysis --------------------------------------------------

def analyze_K(K_hat, modes):
    """Compute spectral radii for the truncation ladder, the diagonal
    bands, and the top-5 singular values. Returns a dict of arrays
    suitable for direct save / printing."""
    R = K_hat.shape[0]
    out = {}

    # Truncation ladder: ρ(K_5), ρ(K_10), ρ(K_15), ρ(K_20)
    trunc_sizes = [5, 10, 15, 20]
    trunc_rho = []
    trunc_eigs = []
    for sz in trunc_sizes:
        if sz <= R:
            K_sub = K_hat[:sz, :sz]
            eigs = np.linalg.eigvals(K_sub)
            rho = float(np.max(np.abs(eigs)))
            trunc_rho.append(rho)
            trunc_eigs.append(eigs)
    out['trunc_sizes'] = np.array(trunc_sizes, dtype=np.int32)
    out['trunc_rho'] = np.array(trunc_rho, dtype=np.float64)
    # store eigs as a ragged-padded (4, 20) array
    eig_pad = np.zeros((len(trunc_sizes), R), dtype=np.complex128)
    for i, eigs in enumerate(trunc_eigs):
        eig_pad[i, :len(eigs)] = eigs
    out['trunc_eigenvalues'] = eig_pad

    # Banded ρ: 5×5 diagonal blocks at positions [0:5], [5:10], [10:15], [15:20]
    band_starts = list(range(0, R, 5))
    band_rho = []
    band_labels = []
    for s in band_starts:
        e = s + 5
        if e > R:
            break
        block = K_hat[s:e, s:e]
        eigs = np.linalg.eigvals(block)
        rho = float(np.max(np.abs(eigs)))
        band_rho.append(rho)
        # mode labels (1-indexed)
        band_labels.append((modes[s], modes[e - 1]))
    # band_labels holds (start_mode, end_mode) 1-indexed pairs already.
    out['band_starts'] = np.array([s for s, _ in band_labels], dtype=np.int32)
    out['band_ends'] = np.array([e for _, e in band_labels], dtype=np.int32)
    out['band_rho'] = np.array(band_rho, dtype=np.float64)

    # Top-5 singular values of K̂_20
    svs = np.linalg.svd(K_hat, compute_uv=False)
    out['singular_values'] = svs[:min(5, len(svs))]

    return out


# --- Main -------------------------------------------------------------

def main():
    print('Run 4 — HIGH-MODE-B3 (mode coupling on r = 1..20)')
    print(f'  N = {N_WALKERS:_}, steps = {N_STEPS}, E_R = {E_R}, E_THRESH = {E_THRESH}')
    print(f'  modes = 1..{R_MAX}')
    print(f'  seed = {SEED:#x}')

    rng = np.random.default_rng(SEED)

    t0 = time.time()
    m, E, sign = initialize(N_WALKERS)
    print(f'  init: {time.time()-t0:.2f}s, state ~{(m.nbytes + E.nbytes + sign.nbytes) / 1e9:.2f} GB')

    prev_in_R = np.ones(N_WALKERS, dtype=bool)
    pending_m_enter = np.full(N_WALKERS, np.nan, dtype=np.float64)

    K_accum = np.zeros((R_MAX, R_MAX), dtype=np.complex128)
    total_excursions = 0
    excursions_per_step = np.zeros(N_STEPS + 1, dtype=np.int64)
    excursion_length_hist = np.zeros(N_STEPS + 2, dtype=np.int64)

    current_excursion_start = np.zeros(N_WALKERS, dtype=np.int32)

    t_start = time.time()

    for step in range(1, N_STEPS + 1):
        step_walkers(m, E, sign, rng)

        in_R_now = np.abs(E) <= E_R
        left_R = prev_in_R & ~in_R_now
        returned_R = ~prev_in_R & in_R_now

        if left_R.any():
            left_idx = np.where(left_R)[0]
            pending_m_enter[left_idx] = m[left_idx]
            current_excursion_start[left_idx] = step

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

                lens = step - current_excursion_start[ret_idx[valid]]
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
    print(f'\nTotal walk time: {total_time:.1f}s = {total_time/60:.2f} min')
    print(f'Total completed excursions: {total_excursions:_}')
    print(f'Mean excursions per walker: {total_excursions / N_WALKERS:.3f}')

    if total_excursions == 0:
        print('WARNING: zero completed excursions; K̂ undefined.')
        return

    K_hat = K_accum / total_excursions

    # Full eigenvalues for K̂_20
    eigs_full = np.linalg.eigvals(K_hat)
    rho_full = float(np.max(np.abs(eigs_full)))

    print(f'\nρ(K̂_20) = {rho_full:.4f}')
    print(f'top |eigenvalues|: {sorted(np.abs(eigs_full).tolist(), reverse=True)[:8]}')

    # Banded / truncation analysis
    analysis = analyze_K(K_hat, MODES)

    print('\n=== Truncation ladder ===')
    for sz, rho in zip(analysis['trunc_sizes'], analysis['trunc_rho']):
        print(f'  ρ(K̂_{sz:2d}) = {rho:.4f}')

    print('\n=== Banded ρ (5×5 diagonal blocks) ===')
    for s, e, rho in zip(analysis['band_starts'], analysis['band_ends'], analysis['band_rho']):
        print(f'  modes [{s:2d}..{e:2d}]: ρ = {rho:.4f}')

    print('\n=== Top singular values of K̂_20 ===')
    for i, sv in enumerate(analysis['singular_values']):
        print(f'  σ_{i+1} = {sv:.4e}')

    # Diagonal dominance for the full 20×20
    abs_K = np.abs(K_hat)
    print('\n=== |K̂_rr| diagonal (mode-by-mode contraction) ===')
    for i, r in enumerate(MODES):
        diag = abs_K[i, i]
        off_sum = abs_K[i].sum() - diag
        print(f'  r={r:2d}: |K_rr|={diag:.4e}, sum off-diag={off_sum:.4e}, '
              f'ratio off/diag = {off_sum / max(diag, 1e-20):.3f}')

    # Mean excursion length
    lens_vals = np.arange(excursion_length_hist.size)
    mean_len = float((lens_vals * excursion_length_hist).sum() / max(total_excursions, 1))
    print(f'\nMean excursion length = {mean_len:.3f} steps')

    np.savez_compressed(
        OUT_PATH,
        K_hat=K_hat,
        abs_K=abs_K,
        modes=MODES,
        total_excursions=np.int64(total_excursions),
        mean_excursions_per_walker=np.float64(total_excursions / N_WALKERS),
        eigenvalues=eigs_full,
        spectral_radius=np.float64(rho_full),
        trunc_sizes=analysis['trunc_sizes'],
        trunc_rho=analysis['trunc_rho'],
        trunc_eigenvalues=analysis['trunc_eigenvalues'],
        band_starts=analysis['band_starts'],
        band_ends=analysis['band_ends'],
        band_rho=analysis['band_rho'],
        singular_values=analysis['singular_values'],
        excursions_per_step=excursions_per_step,
        excursion_length_hist=excursion_length_hist,
        mean_excursion_length=np.float64(mean_len),
        gamma_r=np.array([0.5 * (1.0 + math.cos(2.0 * math.pi * float(r) * LOG10_2)) for r in MODES]),
        meta_N=np.int64(N_WALKERS),
        meta_steps=np.int32(N_STEPS),
        meta_E_R=np.int32(E_R),
        meta_E_THRESH=np.int32(E_THRESH),
        meta_seed=np.int64(SEED),
    )
    print(f'\n-> {OUT_PATH}')


if __name__ == '__main__':
    main()
