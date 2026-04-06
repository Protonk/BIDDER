"""
noising_permutation.py — digit permutation does nothing

1500x1500 grid, original + 3 successive random digit permutations.
The arcs recolor but never move, blur, or break.
"""

import sys
sys.path.insert(0, '../../../../../../core')

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

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
grid = np.zeros((N, N), dtype=np.uint8)
for i in range(N):
    n = i + 1
    if n % 500 == 0:
        print(f"  n = {n}...")
    digits = n_primes_digits(n, N, prime_cache=primes)
    grid[i, :len(digits)] = digits[:N]

colors = [
    '#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786',
    '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921',
]
cmap = ListedColormap(colors)

rng = np.random.default_rng(42)

print("Permuting...")
frames = [grid.copy()]
current = grid.copy()
for step in range(3):
    perm = rng.permutation(10).astype(np.uint8)
    current = perm[current]
    frames.append(current.copy())

titles = ['original', 'perm 1', 'perm 2', 'perm 3']

print("Rendering...")
fig, axes = plt.subplots(1, 4, figsize=(20, 5))
fig.patch.set_facecolor('#0a0a0a')

for ax, frame, title in zip(axes, frames, titles):
    ax.set_axis_off()
    ax.imshow(frame, aspect='auto', cmap=cmap, vmin=0, vmax=9,
              interpolation='nearest')
    ax.set_title(title, color='white', fontsize=12, pad=6)

plt.tight_layout(pad=0.5)
plt.savefig('noising_permutation.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> noising_permutation.png")
