"""
corona_attempt.py — the wrong polar coordinates

n = angle (monoids around the circle), run-length = radius
(center = short runs, edge = long runs), color = frequency.

The exponential decay of run-length frequency means 95% of the
visual mass is in the inner 20% of the radius. A blinding core
with faint coronal ejections at powers of 2.
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
MAX_RUN = 48
PRIMES_PER_N = 5000

IMG_SIZE = 2000
CX, CY = IMG_SIZE // 2, IMG_SIZE // 2
R_MAX = 950


# ── Compute ──────────────────────────────────────────────────────────

print(f"Computing 0-run histograms for n=1..{N_MAX}...")

hist = np.zeros((N_MAX, MAX_RUN), dtype=float)

for idx in range(N_MAX):
    n = idx + 1
    if n % 256 == 0:
        print(f"  n = {n}...")

    bits = binary_stream(n, count=PRIMES_PER_N)[:TARGET_BITS]
    runs = rle(bits)

    zc = np.zeros(MAX_RUN, dtype=int)
    for val, length in runs:
        if val == 0:
            k = min(length, MAX_RUN) - 1
            zc[k] += 1

    zt = zc.sum()
    if zt > 0:
        hist[idx] = zc / zt

# ── Polar mapping ────────────────────────────────────────────────────

print("Building polar image...")

yy, xx = np.mgrid[0:IMG_SIZE, 0:IMG_SIZE]
dx = (xx - CX).astype(np.float64)
dy = (yy - CY).astype(np.float64)
r = np.sqrt(dx**2 + dy**2)
theta = np.arctan2(dy, dx) % (2 * np.pi)

# Map theta -> monoid index
n_idx = (theta / (2 * np.pi) * N_MAX).astype(int)
n_idx = np.clip(n_idx, 0, N_MAX - 1)

# Map radius -> run-length bin (center = bin 0, edge = bin MAX_RUN-1)
run_bin = (r / R_MAX * MAX_RUN).astype(int)
run_bin = np.clip(run_bin, 0, MAX_RUN - 1)

# Mask: inside the disk
in_disk = r <= R_MAX

# Look up values
FLOOR = 1e-6
values = np.full((IMG_SIZE, IMG_SIZE), FLOOR)
values[in_disk] = np.maximum(hist[n_idx[in_disk], run_bin[in_disk]], FLOOR)

# ── Render ───────────────────────────────────────────────────────────

print("Rendering...")

# Solar colormap: black -> deep red -> orange -> yellow -> white
cmap = LinearSegmentedColormap.from_list('corona', [
    '#000000',
    '#1a0000',
    '#4a0000',
    '#8b0000',
    '#cc3300',
    '#ff6600',
    '#ffaa00',
    '#ffdd44',
    '#ffffaa',
    '#ffffff',
])

norm = LogNorm(vmin=1e-5, vmax=0.5)
rgb = cmap(norm(values))[:, :, :3]
rgb[~in_disk] = 0.0

# Rotate 45 degrees and crop to the bright region
from scipy.ndimage import rotate as ndrotate

rgb_rotated = ndrotate(rgb, 45, reshape=False, order=1, cval=0.0)

# Crop a circle around the center, sized to capture the corona
# The bright core extends to about run-length 10-12, which is
# r ≈ (12/MAX_RUN) * R_MAX ≈ 237px. Include some corona: crop at ~350px.
CROP_R = 380
y0 = CY - CROP_R
y1 = CY + CROP_R
x0 = CX - CROP_R
x1 = CX + CROP_R
cropped = rgb_rotated[y0:y1, x0:x1]

# Apply circular mask
cy_c, cx_c = CROP_R, CROP_R
yy_c, xx_c = np.mgrid[0:2*CROP_R, 0:2*CROP_R]
dist_c = np.sqrt((xx_c - cx_c)**2 + (yy_c - cy_c)**2)
outside = dist_c > CROP_R
cropped[outside] = 0.0

fig = plt.figure(frameon=False, figsize=(20, 20))
ax = plt.Axes(fig, [0., 0., 1., 1.])
ax.set_axis_off()
fig.add_axes(ax)

ax.imshow(cropped, interpolation='nearest', origin='lower')

plt.savefig('corona_attempt.png', dpi=150, pad_inches=0, bbox_inches='tight',
            facecolor='#000000')
print("-> corona_attempt.png")
