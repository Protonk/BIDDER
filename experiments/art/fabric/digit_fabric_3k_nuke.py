"""
digit_fabric_3k_nuke.py — how much blur to destroy the structure?

Push sigma from 8 to 256. Find where the arcs finally die.
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

sigmas = [8, 16, 32, 64, 128, 256]

print("Rendering...")
fig, axes = plt.subplots(2, 3, figsize=(30, 20))
fig.patch.set_facecolor('#0a0a0a')

for ax, sigma in zip(axes.flat, sigmas):
    ax.set_axis_off()
    img = gaussian_filter(grid, sigma=sigma)
    ax.imshow(img, aspect='auto', cmap='inferno', vmin=0, vmax=9,
              interpolation='nearest')
    ax.set_title(f'σ={sigma}', color='white', fontsize=16, pad=8)

plt.tight_layout(pad=1.0)
plt.savefig('digit_fabric_3k_nuke.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> digit_fabric_3k_nuke.png")
