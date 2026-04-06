"""
epsilon_teeth.py — is the binary Champernowne sawtooth the epsilon function?

For n = 1..N, compute C_2(n) = 1.{binary n-primes} and plot log_2(C_2(n)).
Compare the sawtooth to epsilon(m) = log_2(1+m) - m.

Three panels:
  1. Raw sawtooth: log_2(C_2(n)) vs n
  2. Residual above secant vs epsilon(m)
  3. Second-order residual: actual - secant - epsilon

Prediction (from SIMPLE-EPSILON.md): the second-order residual is a
descending staircase — positive, flat within each tooth, halving at
each tooth boundary. The identity is structurally trivial.
"""

import sys, os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..'))             # base2/
sys.path.insert(0, os.path.join(_here, '..', '..', '..', '..', '..', 'core'))  # core/

import numpy as np
import matplotlib.pyplot as plt
from acm_core import acm_n_primes


N_MAX = 2000   # monoids n = 1..N_MAX
K = 5          # n-primes per monoid


def binary_champernowne_real(n, count=K):
    """
    Compute C_2(n) = 1.{binary concatenation of first count n-primes}.
    Returns the value as a float.
    """
    primes = acm_n_primes(n, count)
    value = 1.0
    pos = 1  # bit position after the radix point
    for p in primes:
        bits = bin(p)[2:]
        for ch in bits:
            value += int(ch) * 2.0**(-pos)
            pos += 1
    return value


def mantissa_2(n):
    """Base-2 mantissa: m such that n = 2^(d-1) * (1 + m), m in [0, 1)."""
    if n < 1:
        return 0.0
    d = n.bit_length()
    return n / (2.0**(d - 1)) - 1.0


def epsilon(m):
    """The floating-point correction: epsilon(m) = log_2(1+m) - m."""
    return np.log2(1.0 + m) - m


# ── Compute ──────────────────────────────────────────────────────────

print("Computing binary Champernowne reals...")
ns = np.arange(1, N_MAX + 1)
c2 = np.empty(N_MAX)
for i, n in enumerate(ns):
    if n % 500 == 0:
        print(f"  n = {n}...")
    c2[i] = binary_champernowne_real(n)

log_c2 = np.log2(c2)

# Mantissas and bit-lengths
mantissas = np.array([mantissa_2(int(n)) for n in ns])
bit_lengths = np.array([int(n).bit_length() for n in ns])

# Secant within each tooth: linear from log_2(1+m_start) to log_2(1+m_end)
# where m ranges [0, 1) within each bit-length class.
# The secant of log_2(1+m) on [0, 1) is y = m (since log_2(1+0)=0, log_2(2)=1).
# So the sawtooth minus the secant should be epsilon(m).
#
# But we're plotting log_2(C_2(n)), not log_2(1+m). We need to align them.
# log_2(C_2(n)) ≈ log_2(1 + n/2^d) = log_2(1 + (1+m)/2)
# Wait — let's be more careful.
#
# C_2(n) = 1 + n/2^d + ... where d = bit_length(n).
# n/2^d = 2^(d-1)(1+m)/2^d = (1+m)/2.
# So C_2(n) ≈ 1 + (1+m)/2 = (3+m)/2.
# log_2(C_2(n)) ≈ log_2((3+m)/2) = log_2(3+m) - 1.
#
# This is NOT log_2(1+m). The "1." prefix shifts things.
#
# The sawtooth range: at m=0, log_2(3/2) = 0.585. At m=1, log_2(4/2) = 1.
# The secant on [0,1): from 0.585 to 1.0, slope = 0.415.
# secant(m) = 0.585 + 0.415 * m = log_2(1.5) + (1 - log_2(1.5)) * m
#
# The residual above secant: log_2((3+m)/2) - secant(m).
# This is the concavity bump — related to epsilon but not identical.

# Per-tooth secant
secant = np.empty(N_MAX)
residual_above_secant = np.empty(N_MAX)

# Group by bit-length class
for d in range(1, int(bit_lengths.max()) + 1):
    mask = bit_lengths == d
    if not np.any(mask):
        continue
    idx = np.where(mask)[0]
    m_vals = mantissas[idx]
    log_vals = log_c2[idx]
    # Secant from m=0 to m→1 within this tooth
    y0 = log_vals[0]   # at smallest m in this tooth (m ≈ 0 for d≥2)
    y1 = log_vals[-1]   # at largest m
    m0 = m_vals[0]
    m1 = m_vals[-1]
    if m1 > m0:
        slope = (y1 - y0) / (m1 - m0)
        secant[idx] = y0 + slope * (m_vals - m0)
    else:
        secant[idx] = y0
    residual_above_secant[idx] = log_vals - secant[idx]

# Theoretical epsilon evaluated at each mantissa
eps_theoretical = epsilon(mantissas)

# But epsilon gives the residual of log_2(1+m) above ITS secant (y=m).
# Our sawtooth is log_2((3+m)/2), not log_2(1+m).
# The concavity of log_2((3+m)/2) is the same as log_2(1+m) shifted —
# actually, d/dm log_2((3+m)/2) = 1/((3+m) ln 2), and
# d/dm log_2(1+m) = 1/((1+m) ln 2). Different curvature.
#
# So epsilon(m) is NOT the right comparison function.
# The right comparison is the concavity bump of log_2((3+m)/2) on [0,1).
#
# Let g(m) = log_2((3+m)/2). Secant from (0, g(0)) to (1, g(1)):
# g(0) = log_2(1.5), g(1) = log_2(2) = 1.
# secant_g(m) = log_2(1.5) + (1 - log_2(1.5)) * m
# bump(m) = g(m) - secant_g(m) = log_2((3+m)/2) - log_2(1.5) - (1 - log_2(1.5)) * m

# Theoretical bump for the actual function g(m) = log_2((3+m)/2)
g0 = np.log2(1.5)
g1 = 1.0
bump_theoretical = np.log2((3.0 + mantissas) / 2.0) - g0 - (g1 - g0) * mantissas

# Second-order residual: actual bump minus theoretical bump
residual_2 = residual_above_secant - bump_theoretical


# ── Plot ─────────────────────────────────────────────────────────────

print("Plotting...")

fig, axes = plt.subplots(3, 1, figsize=(18, 14), sharex=True)
fig.patch.set_facecolor('#0a0a0a')

# Panel 1: raw sawtooth
ax = axes[0]
ax.set_facecolor('#0a0a0a')
ax.plot(ns, log_c2, linewidth=0.5, color='#ffcc5c', alpha=0.9)
# Mark tooth boundaries
for d in range(1, 13):
    bnd = 2**d
    if bnd <= N_MAX:
        ax.axvline(x=bnd, color='white', linewidth=0.3, alpha=0.25)
ax.set_ylabel('$\\log_2(C_2(n))$', color='white', fontsize=11)
ax.set_title('Binary Champernowne sawtooth', color='white',
             fontsize=13, pad=10)
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('#333')

# Panel 2: residual above secant vs theoretical bump
ax = axes[1]
ax.set_facecolor('#0a0a0a')
ax.plot(ns, residual_above_secant, linewidth=0.5, color='#ffcc5c',
        alpha=0.9, label='actual residual above secant')
ax.plot(ns, bump_theoretical, linewidth=0.8, color='#ff6f61',
        alpha=0.7, label='theoretical bump of $\\log_2((3+m)/2)$')
ax.axhline(y=0, color='white', linewidth=0.3, alpha=0.25)
for d in range(1, 13):
    bnd = 2**d
    if bnd <= N_MAX:
        ax.axvline(x=bnd, color='white', linewidth=0.3, alpha=0.25)
ax.set_ylabel('residual above secant', color='white', fontsize=11)
ax.set_title('Sawtooth concavity vs. theoretical bump',
             color='white', fontsize=13, pad=10)
ax.legend(loc='upper right', fontsize=9, framealpha=0.3,
          facecolor='#1a1a1a', edgecolor='#333', labelcolor='white')
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('#333')

# Panel 3: second-order residual
ax = axes[2]
ax.set_facecolor('#0a0a0a')
ax.plot(ns, residual_2, linewidth=0.5, color='#88d8b0', alpha=0.9)
ax.axhline(y=0, color='white', linewidth=0.3, alpha=0.25)
for d in range(1, 13):
    bnd = 2**d
    if bnd <= N_MAX:
        ax.axvline(x=bnd, color='white', linewidth=0.3, alpha=0.25)
ax.set_xlabel('n', color='white', fontsize=11)
ax.set_ylabel('actual − secant − bump', color='white', fontsize=11)
ax.set_title('Second-order residual (staircase prediction)',
             color='white', fontsize=13, pad=10)
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('#333')

plt.tight_layout()
plt.savefig('epsilon_teeth.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> epsilon_teeth.png")


# ── Summary ──────────────────────────────────────────────────────────

print("\nSecond-order residual stats by tooth:")
print(f"  {'d':>3s}  {'n range':>16s}  {'mean resid':>12s}  {'max resid':>12s}  {'ratio':>8s}")
prev_mean = None
for d in range(2, int(bit_lengths.max()) + 1):
    mask = bit_lengths == d
    if not np.any(mask):
        continue
    idx = np.where(mask)[0]
    r = residual_2[idx]
    mn = r.mean()
    mx = r.max()
    ratio_str = ''
    if prev_mean is not None and mn != 0:
        ratio_str = f'{prev_mean / mn:.3f}'
    prev_mean = mn
    n_lo = int(ns[idx[0]])
    n_hi = int(ns[idx[-1]])
    print(f"  {d:3d}  {n_lo:>7d}-{n_hi:<7d}  {mn:12.8f}  {mx:12.8f}  {ratio_str:>8s}")
