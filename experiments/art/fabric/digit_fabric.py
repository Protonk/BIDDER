"""
Digit fabric — the raw digit strings of n-Champernowne reals as a textile.

Each row is one n. Each column is a digit position in the concatenated
n-prime string. Color encodes digit value (0-9). The result is a woven
fabric whose texture reveals the interplay between the modular sieve
and the decimal system.
"""

import sys
sys.path.insert(0, '../..')

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from acm_core import acm_n_primes

N_ROWS = 600    # n = 1..600
N_DIGITS = 80   # first 80 digits of each Champernowne encoding

print("Building digit fabric...")
fabric = np.full((N_ROWS, N_DIGITS), -1, dtype=int)

for i, n in enumerate(range(1, N_ROWS + 1)):
    # Get enough n-primes to fill N_DIGITS digits
    ps = acm_n_primes(n, 40)
    s = ''.join(str(p) for p in ps)
    for j, ch in enumerate(s[:N_DIGITS]):
        fabric[i, j] = int(ch)

# Custom colormap: 10 distinct colors for digits 0-9
digit_colors = [
    '#1a1a2e',  # 0 — deep navy
    '#e74c3c',  # 1 — red
    '#e67e22',  # 2 — orange
    '#f1c40f',  # 3 — gold
    '#2ecc71',  # 4 — green
    '#1abc9c',  # 5 — teal
    '#3498db',  # 6 — blue
    '#9b59b6',  # 7 — purple
    '#e91e8f',  # 8 — magenta
    '#ecf0f1',  # 9 — near-white
]
cmap = ListedColormap(digit_colors)

print("Plotting...")
fig, ax = plt.subplots(figsize=(20, 14))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

im = ax.imshow(fabric, aspect='auto', cmap=cmap, vmin=0, vmax=9,
               interpolation='nearest', origin='lower',
               extent=[0, N_DIGITS, 1, N_ROWS])
ax.set_xlabel('digit position in Champernowne encoding', color='white', fontsize=12)
ax.set_ylabel('n', color='white', fontsize=12)
ax.set_title('Digit Fabric: decimal digits of n-Champernowne reals',
             color='white', fontsize=14, pad=15)
ax.tick_params(colors='white')

# Colorbar with digit labels
cbar = plt.colorbar(im, ax=ax, pad=0.02, ticks=np.arange(10))
cbar.set_label('digit', color='white', fontsize=11)
cbar.ax.set_yticklabels([str(d) for d in range(10)])
cbar.ax.tick_params(colors='white')

plt.savefig('digit_fabric.png', dpi=300, facecolor='#0a0a0a', bbox_inches='tight')
print("-> digit_fabric.png")
