"""
rle_spiral.py — 0-runs and 1-runs on opposite sides of a spiral arm

Each monoid n gets a position on the spiral. The arm is split:
  - Inner half (toward center): 0-run distribution, cool colormap.
    Short runs at the midline, long runs at the inner edge.
  - Outer half (toward rim): 1-run distribution, warm colormap.
    Short runs at the midline, long runs at the outer edge.

The two distributions face each other across the arm's midline.
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
MAX_RUN_DISP = 24
PRIMES_PER_N = 5000

# Spiral geometry
IMG_SIZE = 2000
CX, CY = IMG_SIZE // 2, IMG_SIZE // 2
R_INNER = 60
R_OUTER = 960
ARM_WIDTH = 148
GAP = 1
RING_SPACING = ARM_WIDTH + GAP
HALF_ARM = ARM_WIDTH / 2.0


def v2(n):
    if n == 0:
        return 0
    v = 0
    while n % 2 == 0:
        n //= 2
        v += 1
    return v


# ── Compute ──────────────────────────────────────────────────────────

print(f"Computing run histograms for n=1..{N_MAX}...")

zero_hist = np.zeros((N_MAX, MAX_RUN_FULL), dtype=float)
one_hist  = np.zeros((N_MAX, MAX_RUN_FULL), dtype=float)

for idx in range(N_MAX):
    n = idx + 1
    if n % 256 == 0:
        print(f"  n = {n}...")

    bits = binary_stream(n, count=PRIMES_PER_N)[:TARGET_BITS]
    runs = rle(bits)

    zc = np.zeros(MAX_RUN_FULL, dtype=int)
    oc = np.zeros(MAX_RUN_FULL, dtype=int)
    for val, length in runs:
        k = min(length, MAX_RUN_FULL) - 1
        if val == 0:
            zc[k] += 1
        else:
            oc[k] += 1

    zt = zc.sum()
    ot = oc.sum()
    if zt > 0:
        zero_hist[idx] = zc / zt
    if ot > 0:
        one_hist[idx] = oc / ot

zhist = zero_hist[:, :MAX_RUN_DISP]
ohist = one_hist[:, :MAX_RUN_DISP]

# ── Spiral mapping ───────────────────────────────────────────────────

print("Building spiral...")

b = RING_SPACING / (2 * np.pi)
n_revolutions = (R_OUTER - R_INNER) / RING_SPACING
monoids_per_rev = N_MAX / n_revolutions

yy, xx = np.mgrid[0:IMG_SIZE, 0:IMG_SIZE]
dx = (xx - CX).astype(np.float64)
dy = (yy - CY).astype(np.float64)
r = np.sqrt(dx**2 + dy**2)
theta = np.arctan2(dy, dx) % (2 * np.pi)

k_float = (r - R_INNER) / (2 * np.pi * b) - theta / (2 * np.pi)
k = np.round(k_float).astype(int)
r_arm = R_INNER + b * (theta + 2 * np.pi * k)
dr = r - r_arm  # negative = inner half, positive = outer half

on_arm = ((np.abs(dr) < HALF_ARM) &
          (k >= 0) &
          (r >= R_INNER - ARM_WIDTH) &
          (r <= R_OUTER + ARM_WIDTH))

n_idx = (k * monoids_per_rev + theta / (2 * np.pi) * monoids_per_rev).astype(int)
on_arm &= (n_idx >= 0) & (n_idx < N_MAX)
n_idx = np.clip(n_idx, 0, N_MAX - 1)

# Inner half (dr < 0): 0-runs. Short runs at midline (dr=0), long at inner edge (dr=-HALF_ARM)
# Outer half (dr > 0): 1-runs. Short runs at midline (dr=0), long at outer edge (dr=+HALF_ARM)
inner_half = on_arm & (dr < 0)
outer_half = on_arm & (dr >= 0)

# 0-run bin: map dr from [-HALF_ARM, 0] to [MAX_RUN_DISP-1, 0] (long runs at edge, short at center)
zero_bin = ((-dr / HALF_ARM) * MAX_RUN_DISP).astype(int)
zero_bin = np.clip(zero_bin, 0, MAX_RUN_DISP - 1)

# 1-run bin: map dr from [0, HALF_ARM] to [0, MAX_RUN_DISP-1] (short at center, long at edge)
one_bin = ((dr / HALF_ARM) * MAX_RUN_DISP).astype(int)
one_bin = np.clip(one_bin, 0, MAX_RUN_DISP - 1)

# Look up values
FLOOR = 1e-5
zero_vals = np.full((IMG_SIZE, IMG_SIZE), FLOOR)
one_vals  = np.full((IMG_SIZE, IMG_SIZE), FLOOR)

zero_vals[inner_half] = np.maximum(zhist[n_idx[inner_half], zero_bin[inner_half]], FLOOR)
one_vals[outer_half]  = np.maximum(ohist[n_idx[outer_half], one_bin[outer_half]], FLOOR)

# ── Colormaps ────────────────────────────────────────────────────────

print("Rendering...")

cmap_zero = LinearSegmentedColormap.from_list('zero_runs', [
    '#000000',
    '#0a0a2e',
    '#0d3b66',
    '#1a759f',
    '#34a0a4',
    '#76c893',
    '#d9ed92',
])

cmap_one = LinearSegmentedColormap.from_list('one_runs', [
    '#000000',
    '#2d0a0a',
    '#6a040f',
    '#9d0208',
    '#dc2f02',
    '#e85d04',
    '#ffba08',
])

norm = LogNorm(vmin=1e-4, vmax=0.6)

zero_rgb = cmap_zero(norm(zero_vals))[:, :, :3]
one_rgb  = cmap_one(norm(one_vals))[:, :, :3]

# Composite
rgb = np.zeros((IMG_SIZE, IMG_SIZE, 3))
rgb[inner_half] = zero_rgb[inner_half]
rgb[outer_half] = one_rgb[outer_half]

fig = plt.figure(frameon=False, figsize=(20, 20))
ax = plt.Axes(fig, [0., 0., 1., 1.])
ax.set_axis_off()
fig.add_axes(ax)

ax.imshow(rgb, interpolation='nearest', origin='lower')

plt.savefig('rle_spiral.png', dpi=150, pad_inches=0, bbox_inches='tight',
            facecolor='#000000')
print("-> rle_spiral.png")
