"""
Polar dual shutter — addition vs multiplication as two discs.

Angle = digit (1-9, each gets a 40-degree sector)
Radius = number of operations (1 at center, 500 at edge)

The addition disc's diagonal stripes become spiral arms.
The multiplication disc's static Benford gradient becomes
concentric rings that lock in almost immediately.
"""

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT)

import numpy as np
import matplotlib.pyplot as plt
from acm_core import acm_champernowne_array, acm_first_digit_array

N = 10000
reals = acm_champernowne_array(N)
log_reals = np.log10(reals)
rng_add = np.random.default_rng(42)
rng_mul = np.random.default_rng(42)

n_steps = 500
n_samples = 8000


def first_digits_from_log_fracs(fracs):
    return np.minimum((10**fracs + 1e-9).astype(int), 9)

print("Building addition heatmap...")
heat_add = np.zeros((n_steps, 9))
for i, k in enumerate(range(1, n_steps + 1)):
    indices = rng_add.integers(0, N, size=(n_samples, k))
    sums = np.sum(reals[indices], axis=1)
    fds = acm_first_digit_array(sums)
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
    fds = first_digits_from_log_fracs(fracs)
    for d in range(1, 10):
        heat_mul[i, d - 1] = np.sum(fds == d) / n_samples
    if (i + 1) % 50 == 0:
        print(f"  mul step {i+1}/{n_steps}")

print("Warping to polar...")

def warp_heatmap_to_polar(heat, img_size=1800):
    """Warp a (n_steps x 9) heatmap into a polar disc.

    Radius = row index (operation count). Center = 1, edge = n_steps.
    Angle = column index (digit 1-9). Each digit gets 2*pi/9 radians.
    """
    cx, cy = img_size / 2, img_size / 2
    r_max = img_size / 2 - 20
    r_min = r_max * 0.02

    iy, ix = np.mgrid[0:img_size, 0:img_size]
    dx = (ix - cx).astype(np.float64)
    dy = (iy - cy).astype(np.float64)
    r = np.sqrt(dx * dx + dy * dy)
    theta = np.arctan2(dy, dx) % (2 * np.pi)

    # Radius -> operation count (row)
    row_idx = ((r - r_min) / (r_max - r_min) * heat.shape[0]).astype(int)
    # Angle -> digit (column). Offset so digit 1 is at top.
    theta_shifted = (theta + np.pi / 2) % (2 * np.pi)
    col_idx = (theta_shifted / (2 * np.pi) * 9).astype(int)

    valid = (r >= r_min) & (r <= r_max) & \
            (row_idx >= 0) & (row_idx < heat.shape[0]) & \
            (col_idx >= 0) & (col_idx < 9)

    img = np.zeros((img_size, img_size))
    img[valid] = heat[row_idx[valid], col_idx[valid]]
    return img

img_add = warp_heatmap_to_polar(heat_add)
img_mul = warp_heatmap_to_polar(heat_mul)

vmax = max(heat_add.max(), heat_mul.max())

print("Plotting...")
fig, (ax_add, ax_mul) = plt.subplots(1, 2, figsize=(24, 12))
fig.patch.set_facecolor('#0a0a0a')

for ax, img, title in [(ax_add, img_add, 'Addition'),
                        (ax_mul, img_mul, 'Multiplication')]:
    ax.set_facecolor('#0a0a0a')
    ax.imshow(img, cmap='inferno', interpolation='bilinear',
              origin='lower', vmin=0, vmax=vmax)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title(title, color='white', fontsize=18, pad=15)

plt.subplots_adjust(wspace=0.05)
plt.savefig('shutter_polar.png', dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
print("-> shutter_polar.png")
