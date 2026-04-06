"""
sunflower_attempt.py — phyllotaxis sunflower of RLE statistics

Each monoid n placed at (sqrt(n), n * golden_angle). Color encodes
the mean 0-run length. The golden angle has no relationship to
powers of 2, so v_2 structure creates interference spirals with
the Fibonacci lattice.
"""

import sys, os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..', 'binary'))
sys.path.insert(0, os.path.join(_here, '..', '..', 'core'))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from binary_core import binary_stream, rle


N_MAX = 3000
TARGET_BITS = 15_000
MAX_RUN = 32
PRIMES_PER_N = 2000

GOLDEN_ANGLE = np.pi * (3 - np.sqrt(5))  # ~137.508 degrees


# ── Compute ──────────────────────────────────────────────────────────

print(f"Computing mean 0-run length for n=1..{N_MAX}...")

mean_zero_run = np.zeros(N_MAX)
mean_one_run  = np.zeros(N_MAX)

for idx in range(N_MAX):
    n = idx + 1
    if n % 500 == 0:
        print(f"  n = {n}...")

    bits = binary_stream(n, count=PRIMES_PER_N)[:TARGET_BITS]
    runs = rle(bits)

    zero_lengths = []
    one_lengths = []
    for val, length in runs:
        if val == 0:
            zero_lengths.append(length)
        else:
            one_lengths.append(length)

    mean_zero_run[idx] = np.mean(zero_lengths) if zero_lengths else 1.0
    mean_one_run[idx]  = np.mean(one_lengths) if one_lengths else 1.0


# ── Phyllotaxis layout ───────────────────────────────────────────────

print("Building sunflower...")

ns = np.arange(1, N_MAX + 1, dtype=float)
theta = ns * GOLDEN_ANGLE
r = np.sqrt(ns)

# Scale to fill a disk
r_max = np.sqrt(N_MAX)
scale = 950.0 / r_max
x = 1000 + scale * r * np.cos(theta)
y = 1000 + scale * r * np.sin(theta)

# Dot size: decreasing slightly with n so inner seeds are visible
# but outer seeds don't overlap
base_size = 18000.0 / N_MAX  # area units for scatter
sizes = np.full(N_MAX, base_size)


# ── Render ───────────────────────────────────────────────────────────

print("Rendering...")

cmap = LinearSegmentedColormap.from_list('sunflower', [
    '#0a0a2e',
    '#1a1a4e',
    '#0d3b66',
    '#1a759f',
    '#34a0a4',
    '#76c893',
    '#d9ed92',
    '#ffcc5c',
    '#ff9966',
    '#ff6f61',
    '#e74c3c',
])

fig, ax = plt.subplots(figsize=(20, 20))
fig.patch.set_facecolor('#000000')
ax.set_facecolor('#000000')
ax.set_xlim(0, 2000)
ax.set_ylim(0, 2000)
ax.set_aspect('equal')
ax.set_axis_off()

norm = Normalize(vmin=1.0, vmax=mean_zero_run.max())

# Size seeds so they nearly touch: approximate area per seed
# at mid-radius. The spacing between seeds ~ scale * 0.5/sqrt(n_mid).
# We want dot diameter ≈ that spacing.
seed_area = 2.23 * (2000.0 / np.sqrt(N_MAX))**2
sizes = np.full(N_MAX, seed_area)

ax.scatter(x, y, c=mean_zero_run, cmap=cmap, norm=norm,
           s=sizes, edgecolors='none', alpha=0.85)

plt.savefig('sunflower_attempt.png', dpi=150, pad_inches=0,
            bbox_inches='tight', facecolor='#000000')
print("-> sunflower_attempt.png")

# Quick stats
print(f"\nMean 0-run length range: {mean_zero_run.min():.3f} to {mean_zero_run.max():.3f}")
print(f"Top 5 by mean 0-run length:")
top = np.argsort(mean_zero_run)[-5:][::-1]
for i in top:
    n = i + 1
    v = 0
    tmp = n
    while tmp % 2 == 0:
        v += 1
        tmp //= 2
    print(f"  n={n:5d} (v_2={v}): mean 0-run = {mean_zero_run[i]:.3f}")
