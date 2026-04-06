"""
Rolling shutter — high-resolution heatmap of first-digit distribution
under cumulative addition, rendered as a CMOS rolling shutter artifact.

The diagonal stripes emerge because adding Champernowne reals (mean ~1.55)
advances the sum's leading digit at rate log10(1.55) ~ 0.19 per addition.
The "shear angle" arctan(0.19) ~ 10.8 degrees is visible in the stripes.
"""

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT)

import numpy as np
import matplotlib.pyplot as plt
from acm_core import acm_champernowne_array, acm_first_digit_array

N = 10000
reals = acm_champernowne_array(N)
rng = np.random.default_rng(42)

# High-res: 500 rows (number of additions), 9 columns (digits)
n_steps = 500
n_samples = 8000

print("Building rolling shutter heatmap...")
heat = np.zeros((n_steps, 9))
for i, k in enumerate(range(1, n_steps + 1)):
    indices = rng.integers(0, N, size=(n_samples, k))
    sums = np.sum(reals[indices], axis=1)
    fds = acm_first_digit_array(sums)
    for d in range(1, 10):
        heat[i, d - 1] = np.sum(fds == d) / n_samples
    if (i + 1) % 50 == 0:
        print(f"  step {i+1}/{n_steps}")

print("Plotting...")
fig, ax = plt.subplots(figsize=(8, 16))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

im = ax.imshow(heat, aspect='auto', cmap='inferno',
               interpolation='bilinear', origin='lower',
               extent=[0.5, 9.5, 1, n_steps])
ax.set_xticks(range(1, 10))
ax.set_xlabel('first digit', color='white', fontsize=13)
ax.set_ylabel('number of additions', color='white', fontsize=13)
ax.set_title('Rolling Shutter', color='white', fontsize=16, pad=15)
ax.tick_params(colors='white')

cbar = plt.colorbar(im, ax=ax, pad=0.02, shrink=0.8)
cbar.set_label('P(digit)', color='white', fontsize=11)
cbar.ax.tick_params(colors='white')

plt.savefig('rolling_shutter.png', dpi=300, facecolor='#0a0a0a', bbox_inches='tight')
print("-> rolling_shutter.png")
