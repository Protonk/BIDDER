"""
Sawtooth + running mean — 5 decades on a log axis.

Single plot showing C(n) as a thin sawtooth band and M(n) as a solid
line bouncing toward 31/20. The log x-axis gives equal visual weight
to each decade, so you can see every tooth and every bounce.
"""

import sys
sys.path.insert(0, '../../../../core')

import numpy as np
import matplotlib.pyplot as plt
from acm_core import acm_champernowne_real

N = 100_000

print("Computing Champernowne reals (n=1..100000)...")
vals = np.empty(N)
for i in range(N):
    vals[i] = acm_champernowne_real(i + 1, 5)
    if (i + 1) % 10000 == 0:
        print(f"  {i+1}/{N}")

ns = np.arange(1, N + 1)
rmean = np.cumsum(vals) / ns

print("Plotting...")
fig, ax = plt.subplots(figsize=(20, 8))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

# Sawtooth — thin, semi-transparent
ax.semilogx(ns, vals, linewidth=0.08, color='#ffcc5c', alpha=0.6,
            rasterized=True, label='C(n)')

# Running mean — solid
ax.semilogx(ns, rmean, linewidth=1.8, color='#6ec6ff',
            label='running mean M(n)')

# Reference: 31/20
ax.axhline(y=1.55, color='#ff6f61', linewidth=1, linestyle='--',
           alpha=0.8, label='31/20 = 1.55')

# Mark the teeth at powers of 10
for exp in range(1, 6):
    p10 = 10**exp
    ax.axvline(x=p10, color='white', linewidth=0.4, alpha=0.25)

ax.set_xlim(1, N)
ax.set_ylim(1.0, 2.1)
ax.set_xlabel('n', color='white', fontsize=13)
ax.set_ylabel('C(n)', color='white', fontsize=13)
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('#333')

ax.legend(loc='upper right', fontsize=11, framealpha=0.3,
          labelcolor='white', facecolor='#1a1a1a')

plt.tight_layout()
plt.savefig('sawtooth.png', dpi=300, facecolor='#0a0a0a', bbox_inches='tight')
print("-> sawtooth.png")
