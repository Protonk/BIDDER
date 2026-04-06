"""
noising_gaussian.py — Gaussian blur survival series

1500x1500 grid, blurred at sigma = 0, 2, 8, 32, 128.
The structure survives far longer than it should.
"""

import sys
sys.path.insert(0, '../../../../../../core')

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from scipy.ndimage import gaussian_filter

N = 1500

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
    return [int(c) for c in ''.join(parts)[:target]]

print("Building grid...")
primes = sieve_primes(300_000)
grid = np.zeros((N, N), dtype=np.float64)
for i in range(N):
    n = i + 1
    if n % 500 == 0:
        print(f"  n = {n}...")
    digits = n_primes_digits(n, N, prime_cache=primes)
    grid[i, :len(digits)] = digits[:N]

sigmas = [0, 2, 8, 32, 128]

print("Rendering...")
fig, axes = plt.subplots(1, 5, figsize=(25, 5))
fig.patch.set_facecolor('#0a0a0a')

for ax, sigma in zip(axes, sigmas):
    ax.set_axis_off()
    img = grid if sigma == 0 else gaussian_filter(grid, sigma=sigma)
    ax.imshow(img, aspect='auto', cmap='inferno', vmin=0, vmax=9,
              interpolation='nearest')
    ax.set_title(f'σ={sigma}', color='white', fontsize=12, pad=6)

plt.tight_layout(pad=0.5)
plt.savefig('noising_gaussian.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> noising_gaussian.png")
