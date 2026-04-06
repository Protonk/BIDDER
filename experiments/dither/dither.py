"""
dither.py — Dithering comparison: BIDDER uniform vs numpy PRNG.

Takes a smooth gradient image and dithers it to 1-bit (black/white)
using three noise sources:

  1. BIDDER generator (exact uniform at block boundary)
  2. numpy PRNG (statistical uniform)
  3. No dither (raw threshold)

For each source we dither at two sizes:
  - N = block boundary (exact uniform for BIDDER)
  - N = non-boundary (mid-sawtooth for BIDDER)

The test image is a smooth horizontal gradient from 0 to 1,
sized so that each column has a constant gray level. Banding
artifacts appear when the dither noise is biased; uniform noise
produces smooth stippling.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'generator'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))

import numpy as np
import matplotlib.pyplot as plt
from bidder import Bidder


def make_gradient(width, height):
    """Horizontal gradient from 0.0 (left) to 1.0 (right)."""
    return np.tile(np.linspace(0, 1, width), (height, 1))


def dither_with_bidder(image, base, digit_class, key):
    """Dither an image using BIDDER generator output as threshold noise."""
    h, w = image.shape
    n_pixels = h * w

    gen = Bidder(base=base, digit_class=digit_class, key=key)
    raw = [gen.next() for _ in range(n_pixels)]

    # Map digits {1, ..., base-1} to equal-width stratum midpoints in [0, 1].
    noise = (np.array(raw, dtype=np.float64) - 0.5) / (base - 1)
    noise = noise.reshape(h, w)

    return (image > noise).astype(np.uint8)


def dither_with_numpy(image, seed):
    """Dither using numpy uniform noise."""
    h, w = image.shape
    rng = np.random.default_rng(seed)
    noise = rng.uniform(0, 1, size=(h, w))
    return (image > noise).astype(np.uint8)


def dither_threshold(image):
    """No dither — hard threshold at 0.5."""
    return (image > 0.5).astype(np.uint8)


# --- Image sizes ---
# Base 10, digit_class 3: period = 900. So a 30x30 image = 900 pixels
# hits the block boundary exactly.
# A 30x28 image = 840 pixels is mid-sawtooth.

base = 10
dc = 3
period = 900  # (base-1) * base^(dc-1) = 9 * 100

# Block-boundary size: 900 pixels = 30x30
w_exact, h_exact = 30, 30

# Non-boundary size: 840 pixels = 30x28
w_mid, h_mid = 30, 28

# Also a larger test: base 16, dc 3 -> period 3840 = 64x60
base_lg = 16
dc_lg = 3
w_lg, h_lg = 64, 60  # 3840 = period

print("Generating dithered images...")

# --- Small gradient (block boundary) ---
grad_exact = make_gradient(w_exact, h_exact)
bidder_exact = dither_with_bidder(grad_exact, base, dc, b'dither exact')
np_exact = dither_with_numpy(grad_exact, seed=42)
thresh_exact = dither_threshold(grad_exact)

# --- Small gradient (mid-sawtooth) ---
grad_mid = make_gradient(w_mid, h_mid)
bidder_mid = dither_with_bidder(grad_mid, base, dc, b'dither mid')
np_mid = dither_with_numpy(grad_mid, seed=43)
thresh_mid = dither_threshold(grad_mid)

# --- Larger gradient (block boundary, base 16) ---
grad_lg = make_gradient(w_lg, h_lg)
bidder_lg = dither_with_bidder(grad_lg, base_lg, dc_lg, b'dither large')
np_lg = dither_with_numpy(grad_lg, seed=44)
thresh_lg = dither_threshold(grad_lg)

# --- Radial gradient (more interesting shape) ---
# 60x60 = 3600 pixels. Use base 10, dc 4 (period 9000) — not a boundary.
# Or reshape: use 45x80 = 3600 and base 6, dc 5 -> period 6^5 - 6^4 = 6480. Nah.
# Just use base 10 dc 3 for a 30x30 radial.
cx, cy = w_exact / 2, h_exact / 2
yy, xx = np.mgrid[0:h_exact, 0:w_exact]
radial = np.sqrt((xx - cx)**2 + (yy - cy)**2) / np.sqrt(cx**2 + cy**2)
radial = np.clip(radial, 0, 1)

bidder_radial = dither_with_bidder(radial, base, dc, b'dither radial')
np_radial = dither_with_numpy(radial, seed=45)
thresh_radial = dither_threshold(radial)


# --- Plot ---
print("Plotting...")

fig, axes = plt.subplots(4, 4, figsize=(22, 22))
fig.patch.set_facecolor('#0a0a0a')

def show(ax, img, title, cmap='gray'):
    ax.set_facecolor('#0a0a0a')
    ax.imshow(img, cmap=cmap, interpolation='nearest', vmin=0, vmax=1)
    ax.set_title(title, color='white', fontsize=11, pad=8)
    ax.set_xticks([])
    ax.set_yticks([])

# Row 1: Block boundary (30x30 = 900 = period)
show(axes[0, 0], grad_exact, f'Source gradient ({w_exact}x{h_exact})')
show(axes[0, 1], thresh_exact, 'Threshold only')
show(axes[0, 2], bidder_exact, 'BIDDER dither (period boundary)')
show(axes[0, 3], np_exact, 'numpy dither')

# Row 2: Mid-sawtooth (30x28 = 840)
show(axes[1, 0], grad_mid, f'Source gradient ({w_mid}x{h_mid})')
show(axes[1, 1], thresh_mid, 'Threshold only')
show(axes[1, 2], bidder_mid, 'BIDDER dither (mid-period)')
show(axes[1, 3], np_mid, 'numpy dither')

# Row 3: Larger (64x60 = 3840 = period, base 16)
show(axes[2, 0], grad_lg, f'Source gradient ({w_lg}x{h_lg})')
show(axes[2, 1], thresh_lg, 'Threshold only')
show(axes[2, 2], bidder_lg, 'BIDDER dither (base 16, period boundary)')
show(axes[2, 3], np_lg, 'numpy dither')

# Row 4: Radial gradient (30x30)
show(axes[3, 0], radial, f'Radial gradient ({w_exact}x{h_exact})')
show(axes[3, 1], thresh_radial, 'Threshold only')
show(axes[3, 2], bidder_radial, 'BIDDER dither (radial)')
show(axes[3, 3], np_radial, 'numpy dither (radial)')

plt.subplots_adjust(wspace=0.05, hspace=0.15)
plt.savefig('dither.png', dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
print("-> dither.png")


# --- Quantitative: count black pixels per column (should track gradient) ---
print("\nBlack pixel fraction per column (30x30 gradient, first 10 cols):")
print("  Column gray: ", [f"{grad_exact[0,c]:.3f}" for c in range(10)])
print("  threshold black%:", [f"{1 - thresh_exact[:,c].mean():.3f}" for c in range(10)])
print("  BIDDER black%:  ", [f"{1 - bidder_exact[:,c].mean():.3f}" for c in range(10)])
print("  numpy black%: ", [f"{1 - np_exact[:,c].mean():.3f}" for c in range(10)])
