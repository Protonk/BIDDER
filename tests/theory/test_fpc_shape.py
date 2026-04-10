"""
test_fpc_shape.py — Red-team test for the statistical layer + coupling.

Claim: for N < P, the variance of the prefix mean around R follows
the FPC shape (sigma^2/N) * (P - N)/(P - 1) for an ideal uniform
permutation. The cipher approximates this shape with a backend-
dependent gap.

This is the only theory test that probes the coupling between the
math and the cipher backend.

Proof reference: core/RIEMANN-SUM.md §The finite-population correction.
Source experiments: mc_diagnostic.py, stratified.py, reseed_test.py.

Run: python3 tests/theory/test_fpc_shape.py
"""

import os
import sys
import math
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from _helpers import (
    get_integrand, riemann_sum, grid_values,
    cipher_key_ensemble, rmse_about, shuffle_prefix_means,
)


P = 2000
F_NAME = 'sin(pi*x)'
f, I_true, _, _ = get_integrand(F_NAME)
R = riemann_sum(f, P)

# Population variance on the grid
f_values = [f(k / P) for k in range(P)]
sigma2 = sum((v - R)**2 for v in f_values) / P


def fpc_std(N, P, sigma2):
    """FPC-predicted standard deviation of the prefix mean about R."""
    if N >= P:
        return 0.0
    return math.sqrt(sigma2 / N * (P - N) / (P - 1))


# =====================================================================
# Test 1: FPC is correct for truly random permutations
# =====================================================================

def test_fpc_matches_random_shuffle():
    """random.shuffle (ideal uniform permutation) matches the FPC
    formula within sampling noise.
    """
    n_trials = 500
    checked = 0
    print(f"    (P={P}, {n_trials} shuffles per N, f={F_NAME})")
    for N in [50, 200, 500, 1000, 1500]:
        theory = fpc_std(N, P, sigma2)
        means = shuffle_prefix_means(f_values, N, n_trials, seed=N)
        empirical = rmse_about(R, means)
        ratio = empirical / theory
        assert 0.80 < ratio < 1.25, (
            f"N={N}: shuffle RMSE/FPC = {ratio:.2f} "
            f"(expected ~1.0 within sampling noise)")
        checked += 1
    print(f"  FPC matches random.shuffle ({checked} N values): OK")


# =====================================================================
# Test 2: FPC endpoint is exact for any permutation
# =====================================================================

def test_endpoint_exact():
    """At N = P, RMSE about R is exactly zero across keys."""
    keys = [f'fpc-endpoint-{k}'.encode() for k in range(50)]
    estimates = cipher_key_ensemble(f, P, keys, P)
    rmse = rmse_about(R, estimates)
    assert rmse < 1e-12, f"N=P RMSE about R = {rmse:.2e}, should be ~0"
    print(f"  FPC endpoint exact (50 keys, RMSE={rmse:.2e}): OK")


# =====================================================================
# Test 3: FPC shape for the cipher
# =====================================================================

def test_cipher_fpc_shape():
    """The cipher's RMSE about R decreases monotonically toward zero
    as N -> P. We assert the shape (monotone + endpoint zero) but
    NOT a tight match to the FPC magnitude.
    """
    keys = [f'fpc-shape-{k}'.encode() for k in range(50)]
    N_fracs = [0.05, 0.10, 0.25, 0.50, 0.75, 0.95, 1.00]
    N_values = [max(1, int(P * frac)) for frac in N_fracs]
    # Ensure N=P is included
    N_values[-1] = P

    rmses = []
    for N in N_values:
        estimates = cipher_key_ensemble(f, P, keys, N)
        rmses.append(rmse_about(R, estimates))

    # Endpoint must be zero
    assert rmses[-1] < 1e-12, (
        f"N=P RMSE = {rmses[-1]:.2e}, should be ~0")

    # Shape: each step should decrease or stay roughly flat. Allow a
    # 15% bump between adjacent steps (sampling noise on 50 keys), but
    # assert every step individually — not just first vs last.
    for j in range(1, len(rmses)):
        if rmses[j - 1] > 0:
            assert rmses[j] <= rmses[j - 1] * 1.15, (
                f"RMSE at N_frac={N_fracs[j]} ({rmses[j]:.4e}) > "
                f"1.15 × RMSE at N_frac={N_fracs[j-1]} ({rmses[j-1]:.4e})")

    print(f"  Cipher FPC shape (stepwise decreasing to zero): OK")
    print(f"    N fracs: {N_fracs}")
    print(f"    RMSEs:   {['%.3e' % r for r in rmses]}")


# =====================================================================
# Test 4: Coupling gap measurement
# =====================================================================

def test_coupling_gap():
    """Report (cipher RMSE) / (FPC predicted std) at several N.
    Assert the ratios are finite and positive. Do NOT assert they
    are close to 1 — the Feistel backend gives ~1.5-2.5x.
    """
    keys = [f'fpc-gap-{k}'.encode() for k in range(50)]
    print(f"    {'N':>6s}  {'FPC std':>10s}  {'cipher RMSE':>12s}  {'ratio':>7s}")
    for N in [50, 200, 500, 1000, 1500, 1900]:
        theory = fpc_std(N, P, sigma2)
        estimates = cipher_key_ensemble(f, P, keys, N)
        empirical = rmse_about(R, estimates)
        ratio = empirical / theory if theory > 0 else float('inf')
        assert ratio > 0, f"N={N}: ratio is non-positive"
        assert math.isfinite(ratio), f"N={N}: ratio is not finite"
        print(f"    {N:>6d}  {theory:>10.4e}  {empirical:>12.4e}  {ratio:>7.2f}")
    print("  Coupling gap measured (ratios finite and positive): OK")


# =====================================================================
# Test 5: Random-shuffle baseline matches FPC directly
# =====================================================================

def test_shuffle_baseline():
    """Confirm that random.shuffle RMSE matches FPC across multiple N,
    independently of any cipher. This validates the FPC formula itself.
    """
    n_trials = 500
    for N in [100, 500, 1000]:
        theory = fpc_std(N, P, sigma2)
        means = shuffle_prefix_means(f_values, N, n_trials, seed=N * 7)
        empirical = rmse_about(R, means)
        ratio = empirical / theory
        assert 0.80 < ratio < 1.25, (
            f"N={N}: shuffle ratio = {ratio:.2f}")
    print("  Shuffle baseline matches FPC (3 N values): OK")


# =====================================================================
# Entry point
# =====================================================================

if __name__ == '__main__':
    print("=== FPC shape (statistical layer + coupling) ===\n")

    test_fpc_matches_random_shuffle()
    test_endpoint_exact()
    test_cipher_fpc_shape()
    test_coupling_gap()
    test_shuffle_baseline()

    print("\nAll FPC shape tests passed.")
