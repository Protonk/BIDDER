"""
digit_fabric_3k_smooth.py — how fast does smoothing destroy structure?

Load the 3k grid, apply Gaussian blur at several sigma values,
render side by side. The question: is the structure fragile (destroyed
by a little blur) or robust (survives moderate blur)?
"""

import sys
sys.path.insert(0, '../../../core')

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from scipy.ndimage import gaussian_filter


N_ROWS = 3000
N_COLS = 3000


def sieve_primes(limit):
    is_prime = np.ones(limit + 1, dtype=bool)
    is_prime[:2] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    return np.nonzero(is_prime)[0]


def n_primes_digits(n, target, prime_cache=None):
    parts = []
    total = 0
    if n == 1:
        for p in prime_cache:
            s = str(p)
            parts.append(s)
            total += len(s)
            if total >= target:
                break
    else:
        k = 1
        while total < target:
            if k % n != 0:
                s = str(n * k)
                parts.append(s)
                total += len(s)
            k += 1
    flat = ''.join(parts)
    return [int(c) for c in flat[:target]]


print("Building grid...")
primes = sieve_primes(500_000)
grid = np.zeros((N_ROWS, N_COLS), dtype=np.float64)

for i in range(N_ROWS):
    n = i + 1
    if n % 500 == 0:
        print(f"  n = {n}...", flush=True)
    digits = n_primes_digits(n, N_COLS, prime_cache=primes)
    grid[i, :len(digits)] = digits[:N_COLS]

sigmas = [0, 0.5, 1, 2, 4, 8]

colors = [
    '#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786',
    '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921',
]
cmap = ListedColormap(colors)

print("Rendering smoothed versions...")
fig, axes = plt.subplots(2, 3, figsize=(30, 20))
fig.patch.set_facecolor('#0a0a0a')

for ax, sigma in zip(axes.flat, sigmas):
    ax.set_axis_off()
    if sigma == 0:
        img = grid
        label = 'raw (σ=0)'
    else:
        img = gaussian_filter(grid, sigma=sigma)
        label = f'σ={sigma}'

    ax.imshow(img, aspect='auto', cmap='inferno', vmin=0, vmax=9,
              interpolation='nearest')
    ax.set_title(label, color='white', fontsize=16, pad=8)

plt.tight_layout(pad=1.0)
plt.savefig('digit_fabric_3k_smooth.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> digit_fabric_3k_smooth.png")
