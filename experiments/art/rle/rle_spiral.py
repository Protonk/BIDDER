"""
rle_spiral.py — 0-run distributions on an Archimedean spiral

Each monoid n gets a position on the spiral. The arm width encodes
run length (inner edge = short runs, outer edge = long runs).
Color encodes frequency. High-v_2 monoids flash bright at the arm's
outer edge as their trailing zeros create long 0-runs.
"""

import sys, os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..', 'binary'))
sys.path.insert(0, os.path.join(_here, '..', '..', 'core'))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, LinearSegmentedColormap
from binary_core import binary_stream, rle


N_MAX = 2048
TARGET_BITS = 50_000
MAX_RUN_FULL = 64
MAX_RUN_DISP = 24     # display bins for the spiral arm
PRIMES_PER_N = 5000

# Spiral geometry
IMG_SIZE = 2000
CX, CY = IMG_SIZE // 2, IMG_SIZE // 2
R_INNER = 60
R_OUTER = 960
ARM_WIDTH = 108
GAP = 2
RING_SPACING = ARM_WIDTH + GAP


def v2(n):
    if n == 0:
        return 0
    v = 0
    while n % 2 == 0:
        n //= 2
        v += 1
    return v


# ── Compute ──────────────────────────────────────────────────────────

print(f"Computing 0-run histograms for n=1..{N_MAX}...")

zero_hist = np.zeros((N_MAX, MAX_RUN_FULL), dtype=float)

for idx in range(N_MAX):
    n = idx + 1
    if n % 256 == 0:
        print(f"  n = {n}...")

    bits = binary_stream(n, count=PRIMES_PER_N)[:TARGET_BITS]
    runs = rle(bits)

    zc = np.zeros(MAX_RUN_FULL, dtype=int)
    for val, length in runs:
        if val == 0:
            k = min(length, MAX_RUN_FULL) - 1
            zc[k] += 1

    zt = zc.sum()
    if zt > 0:
        zero_hist[idx] = zc / zt

# Trim to display bins
hist = zero_hist[:, :MAX_RUN_DISP]

# ── Spiral mapping ───────────────────────────────────────────────────

print("Building spiral...")

b = RING_SPACING / (2 * np.pi)
n_revolutions = (R_OUTER - R_INNER) / RING_SPACING
monoids_per_rev = N_MAX / n_revolutions

# Pixel grid
yy, xx = np.mgrid[0:IMG_SIZE, 0:IMG_SIZE]
dx = (xx - CX).astype(np.float64)
dy = (yy - CY).astype(np.float64)
r = np.sqrt(dx**2 + dy**2)
theta = np.arctan2(dy, dx) % (2 * np.pi)

# Find nearest spiral arm
k_float = (r - R_INNER) / (2 * np.pi * b) - theta / (2 * np.pi)
k = np.round(k_float).astype(int)
r_arm = R_INNER + b * (theta + 2 * np.pi * k)
dr = r - r_arm

# Mask: on the arm, within valid radius and winding
on_arm = ((np.abs(dr) < ARM_WIDTH / 2.0) &
          (k >= 0) &
          (r >= R_INNER - ARM_WIDTH) &
          (r <= R_OUTER + ARM_WIDTH))

# Monoid index from spiral position
n_idx = (k * monoids_per_rev + theta / (2 * np.pi) * monoids_per_rev).astype(int)

# Further mask: valid monoid range
on_arm &= (n_idx >= 0) & (n_idx < N_MAX)
n_idx = np.clip(n_idx, 0, N_MAX - 1)

# Run-length bin from radial offset within the arm
# Inner edge of arm = short runs (bin 0), outer edge = long runs (bin MAX_RUN_DISP-1)
run_bin = ((dr / ARM_WIDTH + 0.5) * MAX_RUN_DISP).astype(int)
run_bin = np.clip(run_bin, 0, MAX_RUN_DISP - 1)

# Look up histogram values
FLOOR = 1e-5
values = np.full((IMG_SIZE, IMG_SIZE), FLOOR)
values[on_arm] = np.maximum(hist[n_idx[on_arm], run_bin[on_arm]], FLOOR)

# ── Colormap & render ────────────────────────────────────────────────

print("Rendering...")

cmap = LinearSegmentedColormap.from_list('spiral_zero', [
    '#000000',
    '#0a0a2e',
    '#0d3b66',
    '#1a759f',
    '#34a0a4',
    '#76c893',
    '#d9ed92',
    '#ffffcc',
])

norm = LogNorm(vmin=1e-4, vmax=0.6)
normed = norm(values)
rgb = cmap(normed)[:, :, :3]

# Black background for off-spiral pixels
rgb[~on_arm] = 0.0

fig = plt.figure(frameon=False, figsize=(20, 20))
ax = plt.Axes(fig, [0., 0., 1., 1.])
ax.set_axis_off()
fig.add_axes(ax)

ax.imshow(rgb, interpolation='nearest', origin='lower')

plt.savefig('rle_spiral.png', dpi=150, pad_inches=0, bbox_inches='tight',
            facecolor='#000000')
print("-> rle_spiral.png")
