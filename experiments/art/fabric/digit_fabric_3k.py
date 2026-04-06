"""
digit_fabric_3k.py — 3000x3000 digit fabric

Each row is one monoid n (1..3000). Each column is a digit position
in the concatenated n-prime string. Color encodes digit value (0-9).
Full-bleed rendering, no axes.
"""

import sys
sys.path.insert(0, '../../../core')

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

N_ROWS = 3000
N_COLS = 3000


def sieve_primes(limit):
    """Fast sieve for n=1 (ordinary primes)."""
    is_prime = np.ones(limit + 1, dtype=bool)
    is_prime[:2] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    return np.nonzero(is_prime)[0]


def n_primes_digits(n, target, prime_cache=None):
    """
    Return the first `target` decimal digits of the Champernowne
    encoding for monoid n.
    """
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


print("Sieving primes for n=1...")
primes = sieve_primes(500_000)
print(f"  {len(primes)} primes cached")

print("Building 3000x3000 digit fabric...")
grid = np.zeros((N_ROWS, N_COLS), dtype=np.uint8)

for i in range(N_ROWS):
    n = i + 1
    if n % 100 == 0:
        print(f"  n = {n}...", flush=True)
    digits = n_primes_digits(n, N_COLS, prime_cache=primes)
    grid[i, :len(digits)] = digits[:N_COLS]

print("Rendering...")

colors = [
    '#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786',
    '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921',
]
cmap = ListedColormap(colors)

fig = plt.figure(frameon=False)
fig.set_size_inches(N_COLS / 100, N_ROWS / 100)
ax = plt.Axes(fig, [0., 0., 1., 1.])
ax.set_axis_off()
fig.add_axes(ax)
ax.imshow(grid, aspect='auto', cmap=cmap, vmin=0, vmax=9,
          interpolation='nearest')

plt.savefig('digit_fabric_3k.png', dpi=300, pad_inches=0, bbox_inches='tight')
print("-> digit_fabric_3k.png")
