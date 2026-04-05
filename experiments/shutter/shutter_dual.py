"""
Dual shutter — addition vs multiplication, side by side.

Left pane:  first-digit distribution under cumulative addition (1..500)
Right pane: first-digit distribution under cumulative multiplication (1..500)

Same N, same n_samples, same RNG seed, same colormap and scale.
The addition pane shows the rolling shutter (diagonal stripes forever).
The multiplication pane shows rapid convergence to Benford's law.
"""

import sys
sys.path.insert(0, '../..')

import numpy as np
import matplotlib.pyplot as plt
from acm_core import champernowne_array

N = 10000
reals = champernowne_array(N)
log_reals = np.log10(reals)
rng_add = np.random.default_rng(42)
rng_mul = np.random.default_rng(42)

n_steps = 500
n_samples = 8000

print("Building addition heatmap...")
heat_add = np.zeros((n_steps, 9))
for i, k in enumerate(range(1, n_steps + 1)):
    indices = rng_add.integers(0, N, size=(n_samples, k))
    sums = np.sum(reals[indices], axis=1)
    log_sums = np.log10(sums)
    fracs = log_sums - np.floor(log_sums)
    fds = np.minimum((10**fracs).astype(int), 9)
    for d in range(1, 10):
        heat_add[i, d - 1] = np.sum(fds == d) / n_samples
    if (i + 1) % 50 == 0:
        print(f"  add step {i+1}/{n_steps}")

print("Building multiplication heatmap...")
heat_mul = np.zeros((n_steps, 9))
for i, k in enumerate(range(1, n_steps + 1)):
    indices = rng_mul.integers(0, N, size=(n_samples, k))
    log_products = np.sum(log_reals[indices], axis=1)
    fracs = log_products - np.floor(log_products)
    fds = np.minimum((10**fracs).astype(int), 9)
    for d in range(1, 10):
        heat_mul[i, d - 1] = np.sum(fds == d) / n_samples
    if (i + 1) % 50 == 0:
        print(f"  mul step {i+1}/{n_steps}")

# Benford reference for the multiplication pane
benford = np.array([np.log10(1 + 1/d) for d in range(1, 10)])

print("Plotting...")
fig, (ax_add, ax_mul) = plt.subplots(1, 2, figsize=(14, 16),
                                      sharey=True)
fig.patch.set_facecolor('#0a0a0a')

# Shared color scale
vmin, vmax = 0, max(heat_add.max(), heat_mul.max())

# --- Addition pane ---
ax_add.set_facecolor('#0a0a0a')
im1 = ax_add.imshow(heat_add, aspect='auto', cmap='inferno',
                     interpolation='bilinear', origin='lower',
                     extent=[0.5, 9.5, 1, n_steps],
                     vmin=vmin, vmax=vmax)
ax_add.set_xticks(range(1, 10))
ax_add.set_xlabel('first digit', color='white', fontsize=13)
ax_add.set_ylabel('number of operations', color='white', fontsize=13)
ax_add.set_title('Addition', color='white', fontsize=15, pad=12)
ax_add.tick_params(colors='white')

# --- Multiplication pane ---
ax_mul.set_facecolor('#0a0a0a')
im2 = ax_mul.imshow(heat_mul, aspect='auto', cmap='inferno',
                     interpolation='bilinear', origin='lower',
                     extent=[0.5, 9.5, 1, n_steps],
                     vmin=vmin, vmax=vmax)
ax_mul.set_xticks(range(1, 10))
ax_mul.set_xlabel('first digit', color='white', fontsize=13)
ax_mul.set_title('Multiplication', color='white', fontsize=15, pad=12)
ax_mul.tick_params(colors='white')

plt.subplots_adjust(wspace=0.08)
plt.savefig('shutter_dual.png', dpi=300, facecolor='#0a0a0a', bbox_inches='tight')
print("-> shutter_dual.png")
