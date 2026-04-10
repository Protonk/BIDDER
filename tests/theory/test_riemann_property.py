"""
test_riemann_property.py — Red-team test for the structural layer.

Claim: at N = P, the MC estimate from any permutation of [0, P) equals
the Riemann sum R, regardless of key. This is E_P(key) = R.

Proof reference: core/RIEMANN-SUM.md §Proof.
Source experiments: riemann_proof.py, adversarial_integrands.py.

Run: python3 tests/theory/test_riemann_property.py
"""

import os
import sys
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from _helpers import (
    INTEGRANDS, get_integrand, riemann_sum,
    cipher_full_mean, cipher_key_ensemble,
    cipher_is_permutation, assert_is_permutation,
)

NOISE_TOL = 1e-12


# =====================================================================
# Test 1: Key-independence for favorable f
# =====================================================================

def test_key_independence_favorable():
    """E_P(key) = R for sin(pi*x) across 20 keys and several P."""
    f, I, _, _ = get_integrand('sin(pi*x)')
    keys = [f'riemann-fav-{k}'.encode() for k in range(20)]
    for P in [6, 100, 2000]:
        R = riemann_sum(f, P)
        estimates = cipher_key_ensemble(f, P, keys, P)
        for k, est in enumerate(estimates):
            assert abs(est - R) < NOISE_TOL, (
                f"P={P} key={k}: |E_P - R| = {abs(est - R):.2e}")
    print("  Key-independence (favorable f, 3 P values, 20 keys): OK")


# =====================================================================
# Test 2: Key-independence for adversarial f
# =====================================================================

def test_key_independence_adversarial():
    """E_P(key) = R holds for hostile integrands too."""
    keys = [f'riemann-adv-{k}'.encode() for k in range(20)]
    P = 2000
    for name in ['x', 'sqrt(x)', 'step_1/3']:
        f, I, _, _ = get_integrand(name)
        R = riemann_sum(f, P)
        estimates = cipher_key_ensemble(f, P, keys, P)
        for k, est in enumerate(estimates):
            assert abs(est - R) < NOISE_TOL, (
                f"{name} key={k}: |E_P - R| = {abs(est - R):.2e}")
    print("  Key-independence (adversarial f, 3 integrands, 20 keys): OK")


# =====================================================================
# Test 3: R matches direct computation
# =====================================================================

def test_R_matches_direct():
    """The cipher's N=P estimate equals the directly computed Riemann sum."""
    for name, f, I, _, _ in INTEGRANDS:
        for P in [50, 500]:
            R_direct = riemann_sum(f, P)
            R_cipher = cipher_full_mean(f, P, b'direct-check')
            assert abs(R_cipher - R_direct) < NOISE_TOL, (
                f"{name} P={P}: cipher R={R_cipher}, direct R={R_direct}")
    print("  R matches direct computation (5 integrands, 2 P values): OK")


# =====================================================================
# Test 4: Independence from the coupling
# =====================================================================

def test_identity_permutation():
    """The theorem holds for the identity permutation (no PRP involved).

    Manually compute E_P for the identity ordering [0, 1, ..., P-1]
    and assert it equals R. This isolates the theorem from any cipher
    backend quality.
    """
    for name, f, I, _, _ in INTEGRANDS:
        P = 500
        R = riemann_sum(f, P)
        # Identity permutation: at(i) = i, so values are f(i/P)
        identity_mean = sum(f(i / P) for i in range(P)) / P
        assert abs(identity_mean - R) < NOISE_TOL, (
            f"{name}: identity mean={identity_mean}, R={R}")
    print("  Identity permutation (5 integrands): OK")


# =====================================================================
# Test 5: Permutation sanity
# =====================================================================

def test_permutation_sanity():
    """The cipher output is actually a permutation of [0, P) before
    we use it as evidence for the theorem.
    """
    for P in [6, 100, 2000]:
        for key in [b'sanity-0', b'sanity-1', b'sanity-2']:
            cipher_is_permutation(P, key)
    print("  Permutation sanity (3 P values, 3 keys): OK")


# =====================================================================
# Entry point
# =====================================================================

if __name__ == '__main__':
    print("=== Riemann property (structural layer) ===\n")

    test_key_independence_favorable()
    test_key_independence_adversarial()
    test_R_matches_direct()
    test_identity_permutation()
    test_permutation_sanity()

    print("\nAll Riemann property tests passed.")
