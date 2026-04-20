"""
Mess #2 diagnostic: empirical π_T ν_R.

Samples walker states at return events to R = {|E| ≤ E₀} and
histograms the m-component. If visually Lebesgue and the low-r
Fourier coefficients are small, the "convergence to Benford"
aspiration of Mess #2 is empirically supported, even while the
proof gap remains.

Per walker:
- Start at (m₀ = log₁₀ √2, E = 0, sign = +1), in R.
- Simulate BS(1,2) via paper's default kernel (run_comparison_walks,
  with snap at |E| < −20).
- Detect return events: step transitions "not in R → in R".
- Discard first K_BURN return events per walker (burn-in).
- From return K_BURN+1 onwards, accumulate (m, E) into a histogram
  and Fourier sums.

Fourier coefficient convention: σ̂(r) = E_{x ∼ ν_R} [e^{−2πi r m}].
Under Leb_T: σ̂(r) = 0 for r ≠ 0. Empirical noise ~ 1/√M for M
samples.

Run: sage -python run_return_marginal.py
"""

import math
import os
import time
import numpy as np

from run_comparison_walks import (
    initialize, step_a, step_a_inv, step_b,
    LOG10_2, LOG10_SQRT2, E_THRESH,
)


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SIM_DIR, 'return_marginal_results')
os.makedirs(OUT_DIR, exist_ok=True)

N_WALKERS = 10**6
N_MAX = 10000
E0 = 10          # R = {|E| ≤ E0}; must be < E_THRESH = 20
K_BURN = 5       # discard first K_BURN return events per walker
N_MBINS = 1000
FOURIER_MODES = np.array([1, 2, 3, 5, 10, 20, 50, 93, 100, 196, 485],
                         dtype=np.int64)

SEED_BASE = 0xA_7E7_0_1D


def step_bs12(m, E, sign, rng):
    """Paper's default 4-generator BS(1,2) step."""
    choice = rng.integers(0, 4, size=m.shape[0], dtype=np.int8)
    step_a(m, E, choice == 0)
    step_a_inv(m, E, choice == 1)
    step_b(m, E, sign, choice == 2, +1)
    step_b(m, E, sign, choice == 3, -1)


def main():
    print(f'Return-marginal sim: π_T ν_R for BS(1,2)')
    print(f'N = {N_WALKERS:_}, n_max = {N_MAX}, E₀ = {E0}, K_BURN = {K_BURN}')

    rng = np.random.default_rng(SEED_BASE)
    m, E, sign = initialize(N_WALKERS)
    in_R_prev = (np.abs(E) <= E0)  # True at step 0 (all walkers start in R)
    return_count = np.zeros(N_WALKERS, dtype=np.int32)

    # Histograms and Fourier accumulators (post-burn-in only)
    m_hist = np.zeros(N_MBINS, dtype=np.int64)
    E_hist = np.zeros(2 * E0 + 1, dtype=np.int64)  # E ∈ [-E0, E0]
    fourier_re = np.zeros(FOURIER_MODES.size, dtype=np.float64)
    fourier_im = np.zeros(FOURIER_MODES.size, dtype=np.float64)
    total_samples = 0

    # Also track how many walkers contributed at least one post-burn sample
    walker_contributed = np.zeros(N_WALKERS, dtype=bool)

    t0 = time.time()
    for step in range(1, N_MAX + 1):
        step_bs12(m, E, sign, rng)
        in_R = (np.abs(E) <= E0)
        # Return event: wasn't in R previous step, is now in R
        enter = in_R & ~in_R_prev
        if enter.any():
            return_count[enter] += 1
            # Samples for which return_count > K_BURN (post-burn-in)
            post_burn = enter & (return_count > K_BURN)
            if post_burn.any():
                mvals = m[post_burn]
                Evals = E[post_burn]
                # m-hist
                m_bins = np.minimum((mvals * N_MBINS).astype(np.int64), N_MBINS - 1)
                np.add.at(m_hist, m_bins, 1)
                # E-hist
                np.add.at(E_hist, Evals + E0, 1)
                # Fourier
                for i, r_mode in enumerate(FOURIER_MODES):
                    angles = 2.0 * math.pi * r_mode * mvals
                    fourier_re[i] += float(np.cos(-angles).sum())
                    fourier_im[i] += float(np.sin(-angles).sum())
                total_samples += int(post_burn.sum())
                walker_contributed[post_burn] = True
        in_R_prev = in_R
        if step % 1000 == 0 or step == N_MAX:
            dt = time.time() - t0
            frac_in_R = in_R.mean()
            median_returns = float(np.median(return_count))
            contrib_frac = walker_contributed.mean()
            print(f'  n={step:6d}  total_samples={total_samples:>10_}  '
                  f'frac_in_R={frac_in_R:.3f}  '
                  f'median_returns_per_walker={median_returns:.1f}  '
                  f'contrib={contrib_frac:.3f}  '
                  f'({step/max(dt,1e-9):.1f} s/s)', flush=True)
    wall = time.time() - t0
    print(f'  wall: {wall:.1f}s')
    print(f'  total post-burn samples: {total_samples:_}')
    print(f'  walkers contributing: {int(walker_contributed.sum()):_} '
          f'({walker_contributed.mean():.3%})')

    # Normalize
    if total_samples > 0:
        m_density = (m_hist.astype(np.float64) * N_MBINS) / float(total_samples)
        sigma_hat = (fourier_re + 1j * fourier_im) / float(total_samples)
    else:
        m_density = np.zeros(N_MBINS)
        sigma_hat = np.zeros(FOURIER_MODES.size, dtype=complex)

    # L₁ distance from uniform on T
    L1 = float(np.sum(np.abs(m_density - 1.0)) / N_MBINS)
    print(f'\n  L₁(m_density, 1) = {L1:.6e}')
    # Noise floor: for M samples × B bins multinomial, mean L₁ ~ √(2B/(πM))
    noise_L1 = math.sqrt(2 * N_MBINS / (math.pi * max(total_samples, 1)))
    print(f'  multinomial L₁ noise floor: {noise_L1:.6e}')
    print(f'  ratio meas / noise: {L1 / noise_L1:.3f}')

    print(f'\n  Fourier coefficients |σ̂(r)| (noise floor ~ 1/√M = '
          f'{1.0 / math.sqrt(max(total_samples, 1)):.4e}):')
    for i, r in enumerate(FOURIER_MODES.tolist()):
        mag = abs(sigma_hat[i])
        print(f'    r = {r:>4d}:  |σ̂| = {mag:.6e}  arg = '
              f'{math.degrees(math.atan2(sigma_hat[i].imag, sigma_hat[i].real)):+7.2f}°')

    np.savez_compressed(os.path.join(OUT_DIR, 'return_marginal.npz'),
                        m_hist=m_hist,
                        E_hist=E_hist,
                        m_density=m_density,
                        fourier_modes=FOURIER_MODES,
                        sigma_hat_re=np.real(sigma_hat),
                        sigma_hat_im=np.imag(sigma_hat),
                        total_samples=np.int64(total_samples),
                        walkers_contributed=np.int64(walker_contributed.sum()),
                        meta_N=np.int64(N_WALKERS),
                        meta_n_max=np.int64(N_MAX),
                        meta_E0=np.int32(E0),
                        meta_K_burn=np.int32(K_BURN),
                        meta_seed=np.int64(SEED_BASE))
    print(f"\n-> {os.path.join(OUT_DIR, 'return_marginal.npz')}")


if __name__ == '__main__':
    main()
