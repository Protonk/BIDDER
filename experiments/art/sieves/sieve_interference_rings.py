"""
sieve_interference_rings.py — Sieve density on an Archimedean spiral.

For each integer k = 1..K, count how many monoids nZ+ (n = 2..N) claim
k as an n-prime. Render on a spiral with brightness = density. Primes
glow; highly composite numbers go dark.

See ULAM-SPIRAL.md for the concept.
"""

import sys
sys.path.insert(0, '../../../core')

import numpy as np
import matplotlib.pyplot as plt
from acm_core import acm_n_primes


# --- Parameters ---

K = 10000       # integers to plot
N_MAX = 200     # monoids n = 2..N_MAX to probe
POINT_SIZE = 2.5
DPI = 250


# --- Compute sieve density ---

print(f"Computing sieve density for k = 1..{K}, n = 2..{N_MAX}...")

density = np.zeros(K + 1, dtype=np.int32)  # density[k] = count of n that claim k

for n in range(2, N_MAX + 1):
    # How many n-primes up to K? At most K // n + 1.
    count = K // n + 1
    primes = acm_n_primes(n, count)
    for p in primes:
        if p > K:
            break
        density[p] += 1

# Normalize to [0, 1] with log scaling to reveal low-density structure.
# The density distribution is heavily right-skewed (most integers have
# density 1-3, a few composites reach 30+). Log scaling compresses the
# top and separates the bottom where most of the population lives.
log_density = np.log1p(density.astype(np.float64))
log_max = log_density[2:].max()
norm = log_density / max(log_max, 1e-12)

print(f"  density range: [{density[2:].min()}, {density[2:].max()}]")
print(f"  primes (e.g. k=2): density {density[2]}")
print(f"  highly composite (e.g. k=60): density {density[min(60, K)]}")


# --- Spiral layout ---

# Archimedean spiral: angle proportional to k, radius = sqrt(k)
# This gives roughly equal area per point.
ks = np.arange(1, K + 1, dtype=np.float64)
theta = 2.0 * np.pi * np.sqrt(ks) * 0.618033988749895  # golden angle
r = np.sqrt(ks)

x = r * np.cos(theta)
y = r * np.sin(theta)


# --- Color map ---

# Use 'inferno' truncated to skip the near-black bottom. The lowest
# density (primes, norm ≈ 0.19) needs to be visible against #0a0a0a,
# so we map norm [0, 1] → inferno [0.15, 0.95], keeping the full
# purple→red→yellow ramp but lifting the floor above invisible.
from matplotlib import cm
cmap = cm.get_cmap('inferno')
colors = cmap(0.15 + norm[1:K + 1] * 0.80)


# --- Plot ---

print("Plotting...")

fig, ax = plt.subplots(figsize=(14, 14))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

ax.scatter(x, y, c=colors, s=POINT_SIZE, edgecolors='none', rasterized=True)

ax.set_xlim(-1.05 * r[-1], 1.05 * r[-1])
ax.set_ylim(-1.05 * r[-1], 1.05 * r[-1])
ax.set_aspect('equal')
ax.axis('off')

ax.text(0.5, 0.98,
        f'Sieve Interference Rings — k = 1..{K:,}, n = 2..{N_MAX}',
        transform=ax.transAxes, ha='center', va='top',
        color='white', fontsize=13, fontweight='light')

ax.text(0.5, 0.02,
        'brightness = sieve density (monoids claiming k as n-prime)',
        transform=ax.transAxes, ha='center', va='bottom',
        color='#666666', fontsize=9)

plt.tight_layout(pad=0.5)
plt.savefig('sieve_interference_rings.png', dpi=DPI,
            facecolor='#0a0a0a', bbox_inches='tight')
print(f"-> sieve_interference_rings.png")


# --- Also: a zoomed view of the first 2000 integers with larger points ---

print("Plotting zoom...")

fig2, ax2 = plt.subplots(figsize=(14, 14))
fig2.patch.set_facecolor('#0a0a0a')
ax2.set_facecolor('#0a0a0a')

zoom = 2000
ax2.scatter(x[:zoom], y[:zoom], c=colors[:zoom], s=6.0,
            edgecolors='none', rasterized=True)

r_zoom = np.sqrt(zoom)
ax2.set_xlim(-1.1 * r_zoom, 1.1 * r_zoom)
ax2.set_ylim(-1.1 * r_zoom, 1.1 * r_zoom)
ax2.set_aspect('equal')
ax2.axis('off')

ax2.text(0.5, 0.98,
         f'Sieve Interference Rings (zoom) — k = 1..{zoom:,}',
         transform=ax2.transAxes, ha='center', va='top',
         color='white', fontsize=13, fontweight='light')

plt.tight_layout(pad=0.5)
plt.savefig('sieve_interference_rings_zoom.png', dpi=DPI,
            facecolor='#0a0a0a', bbox_inches='tight')
print(f"-> sieve_interference_rings_zoom.png")
