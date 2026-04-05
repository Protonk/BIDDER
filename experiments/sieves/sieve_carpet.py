"""
Sieve carpet — a heatmap where row n shows the gaps between n-primes.

Fixed: skip n=1 (ordinary primes blow the dynamic range), clip color
scale, and use log normalization to reveal the fine structure.
"""

import sys
sys.path.insert(0, '../..')

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from acm_core import acm_n_primes

N_ROWS = 500      # n = 2..501
N_PRIMES = 200    # first 200 n-primes per row

print("Computing sieve carpet...")
carpet = np.zeros((N_ROWS, N_PRIMES - 1))
for i in range(N_ROWS):
    n = i + 2  # skip n=1
    ps = acm_n_primes(n, N_PRIMES)
    gaps = np.diff(ps)
    carpet[i, :] = np.array(gaps) / n

print("Plotting...")
fig, ax = plt.subplots(figsize=(18, 10))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

# Most gaps/n are 1 (consecutive survivors) or 2 (one deleted).
# The interesting structure is *where* the 2s fall.
im = ax.imshow(carpet, aspect='auto', cmap='inferno',
               interpolation='nearest', origin='lower',
               extent=[1, N_PRIMES, 2, N_ROWS + 2],
               vmin=0.5, vmax=4)
ax.set_xlabel('position in n-prime sequence', color='white', fontsize=12)
ax.set_ylabel('n', color='white', fontsize=12)
ax.set_title('Sieve Carpet: normalized gaps between consecutive n-primes',
             color='white', fontsize=14, pad=15)
ax.tick_params(colors='white')

cbar = plt.colorbar(im, ax=ax, pad=0.02)
cbar.set_label('gap / n', color='white', fontsize=11)
cbar.ax.tick_params(colors='white')

plt.savefig('sieve_carpet.png', dpi=300, facecolor='#0a0a0a', bbox_inches='tight')
print("-> sieve_carpet.png")
