"""
violin_diagnostic.py — the three curves, honest

C_2(n), its running mean, and the 7/4 target. No secant subtraction,
no normalization. Just the signal, its average, and the limit.
"""

import sys, os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..'))
sys.path.insert(0, os.path.join(_here, '..', '..', '..'))

import numpy as np
import matplotlib.pyplot as plt
from acm_core import acm_n_primes


N_MAX = 4000
K = 5


def binary_champernowne_real(n, count=K):
    primes = acm_n_primes(n, count)
    value = 1.0
    pos = 1
    for p in primes:
        for ch in bin(p)[2:]:
            value += int(ch) * 2.0**(-pos)
            pos += 1
    return value


print("Computing binary Champernowne reals...")
ns = np.arange(1, N_MAX + 1)
c2 = np.empty(N_MAX)
for i, n in enumerate(ns):
    if n % 1000 == 0:
        print(f"  n = {n}...")
    c2[i] = binary_champernowne_real(n)

run_mean = np.cumsum(c2) / np.arange(1, N_MAX + 1)

print("Plotting...")
fig, ax = plt.subplots(figsize=(22, 8))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

# Sawtooth
ax.plot(ns, c2, linewidth=0.3, color='#ffcc5c', alpha=0.6,
        label='$C_2(n)$', zorder=1)

# Running mean
ax.plot(ns, run_mean, linewidth=1.2, color='#6ec6ff', alpha=0.95,
        label='running mean $M(n)$', zorder=3)

# Target
ax.axhline(y=1.75, color='#ff6f61', linewidth=0.8, alpha=0.6,
           linestyle='--', label='$7/4 = 1.75$', zorder=2)

# Tooth boundaries
for d in range(1, 14):
    bnd = 2**d
    if bnd <= N_MAX:
        ax.axvline(x=bnd, color='white', linewidth=0.3, alpha=0.15)

ax.set_xlim(1, N_MAX)
ax.set_ylim(1.45, 2.05)
ax.set_xlabel('n', color='white', fontsize=12)
ax.set_ylabel('value', color='white', fontsize=12)
ax.set_title('Binary Champernowne reals: signal, mean, target',
             color='white', fontsize=14, pad=12)
ax.legend(loc='upper right', fontsize=10, framealpha=0.3,
          facecolor='#1a1a1a', edgecolor='#333', labelcolor='white')
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('#333')

plt.tight_layout()
plt.savefig('violin_diagnostic.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> violin_diagnostic.png")
print(f"Running mean at n={N_MAX}: {run_mean[-1]:.6f}")
