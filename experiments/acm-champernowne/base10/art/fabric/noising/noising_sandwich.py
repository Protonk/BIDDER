"""
noising_sandwich.py — Gaussian, then permutation, then Gaussian

The sandwich: a small blur makes the values continuous (breaking the
integer structure), a permutation scrambles the color mapping (now
meaningful because values are continuous and the scramble is nonlinear),
and a second small blur finishes the job.

Five panels:
  1. original
  2. Gaussian σ=2 (values become continuous, arcs intact)
  3. digit permutation of the blurred grid (nonlinear scramble of
     continuous values — this is NOT the same as permuting integers)
  4. Gaussian σ=2 again (smooths the scramble damage)
  5. for comparison: Gaussian σ=4 alone (same total blur budget)
"""

import sys
sys.path.insert(0, '../../../../../../core')

import numpy as np
import matplotlib.pyplot as plt
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

rng = np.random.default_rng(42)

# Build a nonlinear scramble: a random piecewise-linear map on [0, 9]
# that permutes the integer anchors and interpolates between them.
# This is the continuous-domain version of a digit permutation.
perm = rng.permutation(10)
# Map: value v (continuous in [0,9]) -> perm[floor(v)] + (v - floor(v)) * (perm[ceil(v)] - perm[floor(v)])
# But simpler: just use the permutation as a lookup with linear interp
anchors_in = np.arange(10, dtype=np.float64)
anchors_out = perm.astype(np.float64)

def scramble(img):
    """Nonlinear value scramble: piecewise-linear between permuted anchors."""
    return np.interp(img, anchors_in, anchors_out)

print("Building sandwich...")
step1 = grid.copy()                           # original
step2 = gaussian_filter(grid, sigma=2)         # blur σ=2
step3 = scramble(step2)                        # nonlinear scramble
step4 = gaussian_filter(step3, sigma=2)        # blur σ=2 again
step5 = gaussian_filter(grid, sigma=4)         # comparison: σ=4 alone

frames = [step1, step2, step3, step4, step5]
titles = ['original',
          'Gaussian σ=2',
          '+ scramble',
          '+ Gaussian σ=2',
          'Gaussian σ=4\n(same budget)']

print("Rendering...")
fig, axes = plt.subplots(1, 5, figsize=(25, 5))
fig.patch.set_facecolor('#0a0a0a')

for ax, frame, title in zip(axes, frames, titles):
    ax.set_axis_off()
    ax.imshow(frame, aspect='auto', cmap='inferno', vmin=0, vmax=9,
              interpolation='nearest')
    ax.set_title(title, color='white', fontsize=11, pad=6)

plt.tight_layout(pad=0.5)
plt.savefig('noising_sandwich.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> noising_sandwich.png")
