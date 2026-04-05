"""
Polar fabric — the digit fabric warped into a disc.

Angle = digit position (0..N_DIGITS maps to 0..2*pi)
Radius = n (monoid index, 1..N_ROWS)
Color = digit value (0-9), same palette as the flat fabric

Each concentric ring is one n-Champernowne encoding wrapped around a
circle. The vertical stripes of the rectangular fabric become radial
spokes. The diagonal sweeps become spirals. The black zero-curves
become dark radial arcs.

Rendered by building the rectangular fabric first, then sampling it
via a vectorized polar->Cartesian warp.
"""

import sys
sys.path.insert(0, '../../..')

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from acm_core import acm_n_primes

N_ROWS = 600
N_DIGITS = 80

print("Building digit fabric...")
fabric = np.full((N_ROWS, N_DIGITS), -1, dtype=int)

for i, n in enumerate(range(1, N_ROWS + 1)):
    ps = acm_n_primes(n, 40)
    s = ''.join(str(p) for p in ps)
    for j, ch in enumerate(s[:N_DIGITS]):
        fabric[i, j] = int(ch)

digit_colors_rgb = np.array([
    [0.102, 0.102, 0.180],  # 0 — deep navy
    [0.906, 0.298, 0.235],  # 1 — red
    [0.902, 0.494, 0.133],  # 2 — orange
    [0.945, 0.769, 0.059],  # 3 — gold
    [0.180, 0.800, 0.443],  # 4 — green
    [0.102, 0.737, 0.612],  # 5 — teal
    [0.204, 0.596, 0.859],  # 6 — blue
    [0.608, 0.349, 0.714],  # 7 — purple
    [0.914, 0.118, 0.561],  # 8 — magenta
    [0.926, 0.941, 0.945],  # 9 — near-white
])

print("Warping to polar...")
img_size = 2400
cx, cy = img_size / 2, img_size / 2
r_max = img_size / 2 - 40
r_min = r_max * 0.05  # small hole in center

# Build coordinate grid
iy, ix = np.mgrid[0:img_size, 0:img_size]
dx = (ix - cx).astype(np.float64)
dy = (iy - cy).astype(np.float64)
r = np.sqrt(dx * dx + dy * dy)
theta = np.arctan2(dy, dx) % (2 * np.pi)

# Map polar coords to fabric coords
# radius -> row (n index): r_min..r_max maps to 0..N_ROWS-1
n_idx = ((r - r_min) / (r_max - r_min) * N_ROWS).astype(int)
# angle -> column (digit position): 0..2*pi maps to 0..N_DIGITS-1
d_idx = (theta / (2 * np.pi) * N_DIGITS).astype(int)

valid = (r >= r_min) & (r <= r_max) & (n_idx >= 0) & (n_idx < N_ROWS) & (d_idx >= 0) & (d_idx < N_DIGITS)

# Build RGB image
bg = np.full((img_size, img_size, 3), 0.04)  # near-black background
digit_vals = np.full((img_size, img_size), -1, dtype=int)
digit_vals[valid] = fabric[n_idx[valid], d_idx[valid]]

for d in range(10):
    mask = digit_vals == d
    bg[mask] = digit_colors_rgb[d]

print("Plotting...")
fig, ax = plt.subplots(figsize=(14, 14))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

ax.imshow(bg, origin='lower', interpolation='nearest')
ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)
ax.set_title('Polar Fabric', color='white', fontsize=16, pad=15)

# Add a small legend
legend_y = img_size * 0.03
legend_x_start = img_size * 0.02
digit_names = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
for d in range(10):
    ax.plot(legend_x_start + d * img_size * 0.025, legend_y, 's',
            color=digit_colors_rgb[d], markersize=8)
    ax.text(legend_x_start + d * img_size * 0.025, legend_y - img_size * 0.02,
            digit_names[d], color='white', fontsize=7, ha='center')

plt.savefig('polar_fabric.png', dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
print("-> polar_fabric.png")
