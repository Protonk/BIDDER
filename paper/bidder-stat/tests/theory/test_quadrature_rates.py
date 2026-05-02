"""
test_quadrature_rates.py — Red-team test for the quadrature layer.

Claim: the Riemann-sum bias |R - I| follows the left-endpoint
Euler-Maclaurin predictions. Each row of the convergence table in
generator/RIEMANN-SUM.md becomes an assertion.

No cipher, no key, no PRP. Pure math on direct grid sums.

Proof reference: generator/RIEMANN-SUM.md §What the Riemann sum costs.
Source experiments: adversarial_integrands.py, riemann_proof.py.

Run: python3 tests/theory/test_quadrature_rates.py
"""

import os
import sys
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from _helpers import get_integrand, riemann_sum, riemann_bias


# =====================================================================
# Test 1: f(x) = x — exact O(1/P), error = 1/(2P)
# =====================================================================

def test_f_x_exact_rate():
    """f(x) = x: R = (P-1)/(2P), error = exactly 1/(2P)."""
    f, I, _, _ = get_integrand('x')
    for P in [10, 100, 1000, 10000]:
        R = riemann_sum(f, P)
        expected_R = (P - 1) / (2 * P)
        expected_error = 1 / (2 * P)
        assert abs(R - expected_R) < 1e-14, (
            f"P={P}: R={R}, expected {expected_R}")
        assert abs(riemann_bias(f, P, I) - expected_error) < 1e-14, (
            f"P={P}: bias={riemann_bias(f, P, I)}, expected {expected_error}")
    print("  f(x) = x: error = 1/(2P) exactly: OK")


# =====================================================================
# Test 2: f(x) = sin(pi*x) — O(1/P^2) with constant pi/6
# =====================================================================

def test_sin_endpoint_cancellation():
    """f(x) = sin(pi*x): P^2 * |R - I| -> pi/6."""
    f, I, _, _ = get_integrand('sin(pi*x)')
    target = math.pi / 6
    for P in [200, 500, 1000, 2000, 5000, 10000]:
        bias = riemann_bias(f, P, I)
        scaled = P * P * bias
        ratio = scaled / target
        assert 0.99 < ratio < 1.01, (
            f"P={P}: P^2 * bias = {scaled:.6f}, "
            f"target pi/6 = {target:.6f}, ratio = {ratio:.4f}")
    print("  f(x) = sin(pi*x): P^2 * error -> pi/6 within 1%: OK")


# =====================================================================
# Test 3: f(x) = x^2(1-x)^2 — O(1/P^4), double cancellation
# =====================================================================

def test_double_endpoint_cancellation():
    """f and f' match at endpoints: O(1/P^4)."""
    f, I, _, _ = get_integrand('x^2(1-x)^2')
    # The constant P^4 * |R - I| should converge.
    # At P=100: P^4 * bias should be approximately 1/30 = 0.03333
    target = 1.0 / 30.0
    for P in [100, 200, 500, 1000]:
        bias = riemann_bias(f, P, I)
        scaled = P**4 * bias
        ratio = scaled / target
        assert 0.95 < ratio < 1.05, (
            f"P={P}: P^4 * bias = {scaled:.6f}, "
            f"target 1/30 = {target:.6f}, ratio = {ratio:.4f}")
    print("  f(x) = x^2(1-x)^2: P^4 * error -> 1/30 within 5%: OK")


# =====================================================================
# Test 4: step function — O(1/P), bounded
# =====================================================================

def test_step_function_bounded():
    """f(x) = 1_{x >= 1/3}: P * |R - I| stays bounded."""
    f, I, _, _ = get_integrand('step_1/3')
    for P in [10, 50, 100, 500, 1000, 10000]:
        bias = riemann_bias(f, P, I)
        scaled = P * bias
        assert scaled <= 1.0, (
            f"P={P}: P * bias = {scaled:.4f}, should be <= 1")
    print("  step function: P * error bounded by 1: OK")


# =====================================================================
# Test 5: Counterexample — f(x) = x does NOT converge at O(1/P^2)
# =====================================================================

def test_x_not_order_p2():
    """f(x) = x: P^2 * error grows linearly (is NOT bounded).

    If it were O(1/P^2), then P^2 * error would be bounded. Instead,
    P^2 * 1/(2P) = P/2, which grows without bound.
    """
    f, I, _, _ = get_integrand('x')
    scaled_values = []
    for P in [100, 1000, 10000]:
        bias = riemann_bias(f, P, I)
        scaled = P * P * bias
        scaled_values.append(scaled)
    # P^2 * error = P/2: grows by 10x when P grows by 10x
    ratio_1 = scaled_values[1] / scaled_values[0]
    ratio_2 = scaled_values[2] / scaled_values[1]
    assert ratio_1 > 5, (
        f"P^2 * error not growing: ratio = {ratio_1:.1f}")
    assert ratio_2 > 5, (
        f"P^2 * error not growing: ratio = {ratio_2:.1f}")
    print("  f(x) = x: P^2 * error grows (NOT O(1/P^2)): OK")


# =====================================================================
# Entry point
# =====================================================================

if __name__ == '__main__':
    print("=== Quadrature rates (Euler-Maclaurin) ===\n")

    test_f_x_exact_rate()
    test_sin_endpoint_cancellation()
    test_double_endpoint_cancellation()
    test_step_function_bounded()
    test_x_not_order_p2()

    print("\nAll quadrature rate tests passed.")
