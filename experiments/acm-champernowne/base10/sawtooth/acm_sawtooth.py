"""
acm_sawtooth.py — Sawtooth structure and decomposition plots
=============================================================

Generates:
  1. The raw sawtooth of n-Champernowne reals (n = 1..10000)
  2. Four-strip decomposition: ln(primality), ln(digitfrac), ln(Champernowne), ln(running mean)
  3. Running mean convergence analysis

All plots saved to current directory.

Usage:
    python acm_sawtooth.py
    sage acm_sawtooth.py       # also works under SageMath
"""

import sys
sys.path.insert(0, '../../../../core')

import matplotlib.pyplot as plt
import numpy as np
from acm_core import (
    acm_champernowne_real, acm_champernowne_array, acm_running_mean,
    acm_digit_count, acm_n_primes
)


N = 10000
ns = np.arange(1, N + 1)


# --- Compute all quantities ---

print("Computing Champernowne reals...")
vals = acm_champernowne_array(N)
rmean = acm_running_mean(vals)

# Decomposition layers
ln_champ = np.log(vals)
ln_prim = np.log(ns.astype(float))
ln_digit = np.array([np.log(acm_digit_count(n, 5) / 5.0) for n in ns])
ln_rmean = np.log(rmean)


# =====================================================================
# Plot 1: Raw sawtooth with running mean
# =====================================================================

print("Plotting sawtooth...")
fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

axes[0].plot(ns, vals, linewidth=0.2, color='black')
axes[0].set_ylabel('f(n)')
axes[0].set_title('n-Champernowne reals, n = 1..10000')
for x in [10, 100, 1000, 10000]:
    axes[0].axvline(x=x, color='red', linewidth=0.3, alpha=0.5)

axes[1].plot(ns, rmean, linewidth=0.8, color='blue')
axes[1].set_ylabel('M(n)')
axes[1].set_title('Running mean')
axes[1].set_xlabel('n')

plt.tight_layout()
plt.savefig('sawtooth_and_mean.png', dpi=200)
print("  -> sawtooth_and_mean.png")


# =====================================================================
# Plot 2: Four-strip decomposition (small multiples)
# =====================================================================

print("Plotting decomposition...")
fig, axes = plt.subplots(4, 1, figsize=(14, 16), sharex=True)

# Strip 1: ln(n-primality) = ln(n)
# Smooth, concave, unbounded. Pure number-theoretic content.
ax = axes[0]
ax.plot(ns, ln_prim, linewidth=0.8, color='red')
ax.set_ylabel('ln(n)')
ax.set_title('ln(n-primality)', fontsize=11)

# Strip 2: ln(n-digitfrac)
# Staircase. Jumps when any of the 5 primes crosses a power-of-10 boundary.
ax = axes[1]
ax.plot(ns, ln_digit, linewidth=0.8, color='green')
ax.set_ylabel('ln(digits/5)')
ax.set_title('ln(n-digitfrac)', fontsize=11)

# Strip 3: ln(n-Champernowne)
# Bounded sawtooth in [ln(1.1), ln(2)] = [0.0953, 0.6931].
# Each tooth is the secant of ln(1+m) where m is the base-10 mantissa.
ax = axes[2]
ax.plot(ns, ln_champ, linewidth=0.2, color='black')
ax.set_ylabel('ln(f(n))')
ax.set_title('ln(n-Champernowne)', fontsize=11)

# Strip 4: ln(running mean)
# Damped oscillation approaching ln(31/20) ≈ 0.438 from below.
# We conjecture it never arrives.
ax = axes[3]
ax.plot(ns, ln_rmean, linewidth=1, color='blue')
ax.set_ylabel('ln(M(n))')
ax.set_title('ln(running mean)', fontsize=11)
ax.set_xlabel('n')

plt.tight_layout()
plt.savefig('decomposition_strips.png', dpi=200)
print("  -> decomposition_strips.png")


# =====================================================================
# Plot 3: Running mean convergence
# =====================================================================

print("Plotting convergence...")
fig, ax = plt.subplots(figsize=(14, 5))

ax.semilogx(ns, rmean, linewidth=0.8, color='blue', label='M(n)')
ax.axhline(y=1.55, color='green', linewidth=1, linestyle='--', label='1.55 = 31/20')
ax.axhline(y=1 + np.log(2), color='red', linewidth=1, linestyle=':', label=f'1 + ln(2) ≈ {1+np.log(2):.4f}')
ax.set_xlabel('n')
ax.set_ylabel('running mean')
ax.set_title('Running mean convergence (log scale)')
ax.legend()

plt.tight_layout()
plt.savefig('convergence.png', dpi=200)
print("  -> convergence.png")


# =====================================================================
# Print summary statistics
# =====================================================================

print("\n=== Summary ===")
print(f"N = {N}")
print(f"Range of f(n): [{vals.min():.6f}, {vals.max():.6f}]")
print(f"Range of ln(f(n)): [{ln_champ.min():.6f}, {ln_champ.max():.6f}]")
print(f"  cf. ln(1.1) = {np.log(1.1):.6f},  ln(2) = {np.log(2):.6f}")
print(f"Running mean at n=100:   {rmean[99]:.6f}")
print(f"Running mean at n=1000:  {rmean[999]:.6f}")
print(f"Running mean at n=10000: {rmean[-1]:.6f}")
print(f"Limit candidate: 31/20 = {31/20:.6f}")
print(f"Mean mantissa: {rmean[-1] - 1:.6f}")
