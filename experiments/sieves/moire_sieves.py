"""
Moire sieves — overlapping sieve patterns for different n.

For each n, the sieve deletes every n-th integer from the positive integers.
Overlaying these binary patterns (present/absent) for many n values creates
moire interference. We render this as a bitmap where columns are integers
and rows are n-values, with a pixel lit if that integer is an n-prime.
"""

import sys
sys.path.insert(0, '../..')

import numpy as np
import matplotlib.pyplot as plt

N_MAX = 400    # n = 1..400
K_MAX = 600    # integers 1..600

print("Building moire bitmap...")
bitmap = np.zeros((N_MAX, K_MAX), dtype=np.uint8)

for n in range(1, N_MAX + 1):
    if n == 1:
        # For n=1, mark primes
        sieve = np.ones(K_MAX + 1, dtype=bool)
        sieve[0] = sieve[1] = False
        for p in range(2, int(K_MAX**0.5) + 1):
            if sieve[p]:
                sieve[p*p::p] = False
        for k in range(1, K_MAX + 1):
            if sieve[k]:
                bitmap[n - 1, k - 1] = 1
    else:
        # n-prime: n*k where k is not divisible by n
        for k in range(1, K_MAX // n + 2):
            val = n * k
            if val > K_MAX:
                break
            if k % n != 0:
                bitmap[n - 1, val - 1] = 1

print("Plotting...")
fig, ax = plt.subplots(figsize=(18, 10))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

# Use a custom colormap: black background, bright points
ax.imshow(bitmap, aspect='auto', cmap='hot', interpolation='nearest',
          origin='lower', extent=[1, K_MAX, 1, N_MAX])
ax.set_xlabel('integer value', color='white', fontsize=12)
ax.set_ylabel('n (monoid index)', color='white', fontsize=12)
ax.set_title('Moire Sieves: n-prime membership bitmap', color='white', fontsize=14, pad=15)
ax.tick_params(colors='white')

plt.savefig('moire_sieves.png', dpi=300, facecolor='#0a0a0a', bbox_inches='tight')
print("-> moire_sieves.png")
