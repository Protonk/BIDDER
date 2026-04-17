"""
M0 — empirical null-floor calibration.

Draws 5000 replicates of a multinomial(N, 1/B, ..., 1/B) vector and
computes the L1-to-uniform statistic Σ |freq_j/N − 1/B| for each
replicate. Reports mean, std, 99% and 99.9% quantiles. The 99.9%
quantile is θ_N, the detection threshold used in D3 and the
decision rule.

Sanity check: expected mean(L1) under the multinomial null is
approximately √(2B/(πN)). Empirical mean should match within 50%.

Matches `common.py`'s l1_to_uniform convention (no 1/B prefactor).

Run: sage -python run_m0.py
"""

import math
import numpy as np


N = 10**8           # walkers per M0 draw
B = 1000            # bin count on T = [0, 1)
REPS = 5000         # null replicates
SEED = 0xA11CAF10


def l1_to_uniform(counts, N_total, B_bins):
    """L1 statistic: Σ |count_j/N − 1/B| (no 1/B prefactor)."""
    freq = counts.astype(np.float64) / float(N_total)
    uniform = 1.0 / float(B_bins)
    return float(np.sum(np.abs(freq - uniform)))


def main():
    rng = np.random.default_rng(SEED)
    pvals = np.full(B, 1.0 / B, dtype=np.float64)

    l1_samples = np.empty(REPS, dtype=np.float64)
    for i in range(REPS):
        counts = rng.multinomial(N, pvals)
        l1_samples[i] = l1_to_uniform(counts, N, B)
        if (i + 1) % 500 == 0:
            print(f'  rep {i+1}/{REPS}', flush=True)

    # Stats
    mean = float(np.mean(l1_samples))
    sd = float(np.std(l1_samples))
    q99 = float(np.quantile(l1_samples, 0.99))
    q999 = float(np.quantile(l1_samples, 0.999))

    # Sanity vs analytic expectation
    # For L1 = Σ |freq_j - 1/B|, with counts ~ multinomial,
    # E[|freq_j - 1/B|] ≈ sqrt(Var(freq_j) * 2/π) for large N
    # where Var(freq_j) = (1/B)(1 - 1/B) / N ≈ 1/(BN) for large B.
    # Summed over B bins: E[L1] ≈ B * sqrt(2/(π·B·N)) = √(2B/(πN))
    analytic_mean = math.sqrt(2.0 * B / (math.pi * N))

    print()
    print('=== M0 RESULTS ===')
    print(f'N = {N:_}, B = {B}, replicates = {REPS}')
    print(f'mean(L1)    = {mean:.6e}')
    print(f'sd(L1)      = {sd:.6e}')
    print(f'q99 (L1)    = {q99:.6e}')
    print(f'theta_N     = {q999:.6e}  (99.9% quantile; used as floor)')
    print()
    print(f'analytic expected mean = {analytic_mean:.6e}')
    ratio = mean / analytic_mean
    print(f'empirical / analytic   = {ratio:.3f}  (should be in [0.5, 1.5])')
    if 0.5 <= ratio <= 1.5:
        print('OK: M0 null calibration passes sanity check.')
    else:
        print('WARNING: empirical mean is off analytic expectation.')
        print('Investigate implementation before using theta_N downstream.')

    # Persist for downstream consumption.
    out = dict(
        N=N, B=B, reps=REPS,
        mean=mean, sd=sd, q99=q99, theta_N=q999,
        analytic_mean=analytic_mean,
        l1_samples=l1_samples,
    )
    np.savez_compressed('m0_results.npz', **out)
    print(f'-> m0_results.npz')


if __name__ == '__main__':
    main()
