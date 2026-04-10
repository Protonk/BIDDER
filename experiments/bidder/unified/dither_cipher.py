"""
dither_cipher.py — Dithering diagnostic via the root bidder.cipher API.

Uses bidder.cipher(period, key) to generate exact-uniform noise for
halftone dithering of smooth gradients. The period is chosen to tile
the image exactly (period = pixels), so every output in [0, period) is
used exactly once and the noise is a perfect permutation.

Diagnostic: compare BIDDER dither (exact permutation) vs numpy PRNG
(statistical uniform) vs threshold (no noise) across several image
sizes and gradient shapes. The dither quality should be visually
indistinguishable between BIDDER and numpy at period boundaries, and
the threshold row should show banding artifacts.

Run: sage -python experiments/bidder/unified/dither_cipher.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, REPO)

import numpy as np
import matplotlib.pyplot as plt
import bidder


# ---------------------------------------------------------------------------
# Dithering helpers
# ---------------------------------------------------------------------------

def dither_with_cipher(image, key):
    """Dither using bidder.cipher. Period = number of pixels, so the
    noise is an exact permutation of [0, period) mapped to [0, 1)."""
    h, w = image.shape
    n_pixels = h * w
    B = bidder.cipher(period=n_pixels, key=key)
    # Map [0, period) to [0, 1) with uniform spacing
    noise = np.array([B.at(i) for i in range(n_pixels)],
                     dtype=np.float64) / n_pixels
    noise = noise.reshape(h, w)
    return (image > noise).astype(np.uint8)


def dither_with_numpy(image, seed):
    rng = np.random.default_rng(seed)
    noise = rng.uniform(0, 1, size=image.shape)
    return (image > noise).astype(np.uint8)


def dither_threshold(image):
    return (image > 0.5).astype(np.uint8)


# ---------------------------------------------------------------------------
# Gradient generators
# ---------------------------------------------------------------------------

def horizontal_gradient(w, h):
    return np.tile(np.linspace(0, 1, w), (h, 1))


def radial_gradient(w, h):
    cx, cy = w / 2, h / 2
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt((xx - cx)**2 + (yy - cy)**2) / np.sqrt(cx**2 + cy**2)
    return np.clip(r, 0, 1)


def diagonal_gradient(w, h):
    yy, xx = np.mgrid[0:h, 0:w]
    return np.clip((xx / w + yy / h) / 2, 0, 1)


# ---------------------------------------------------------------------------
# Configurations
# ---------------------------------------------------------------------------

configs = [
    # (label, w, h, gradient_fn)
    ('Horizontal 30x30 (900 px)',   30, 30, horizontal_gradient),
    ('Horizontal 64x60 (3840 px)',  64, 60, horizontal_gradient),
    ('Radial 30x30 (900 px)',       30, 30, radial_gradient),
    ('Diagonal 48x40 (1920 px)',    48, 40, diagonal_gradient),
    ('Horizontal 100x90 (9000 px)', 100, 90, horizontal_gradient),
]

# ---------------------------------------------------------------------------
# Generate
# ---------------------------------------------------------------------------

print("Generating dithered images via bidder.cipher ...")

rows = []
for i, (label, w, h, grad_fn) in enumerate(configs):
    pixels = w * h
    grad = grad_fn(w, h)
    bc = dither_with_cipher(grad, key=f'dither-{i}'.encode())
    np_d = dither_with_numpy(grad, seed=42 + i)
    th = dither_threshold(grad)
    rows.append((label, pixels, grad, bc, np_d, th))
    print(f"  {label}: period={pixels}")

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------

print("Plotting...")

n_rows = len(configs)
fig, axes = plt.subplots(n_rows, 4, figsize=(20, 5 * n_rows))
fig.patch.set_facecolor('#0a0a0a')


def show(ax, img, title):
    ax.set_facecolor('#0a0a0a')
    ax.imshow(img, cmap='gray', interpolation='nearest', vmin=0, vmax=1)
    ax.set_title(title, color='white', fontsize=10, pad=6)
    ax.set_xticks([])
    ax.set_yticks([])


for r, (label, pixels, grad, bc, np_d, th) in enumerate(rows):
    show(axes[r, 0], grad,  f'Source: {label}')
    show(axes[r, 1], th,    'Threshold')
    show(axes[r, 2], bc,    f'bidder.cipher (period={pixels})')
    show(axes[r, 3], np_d,  'numpy PRNG')

plt.subplots_adjust(wspace=0.04, hspace=0.20)
plt.savefig(os.path.join(HERE, 'dither_cipher.png'),
            dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
print("-> dither_cipher.png")

# ---------------------------------------------------------------------------
# Quantitative diagnostic: per-column black fraction for the first row
# ---------------------------------------------------------------------------

label, pixels, grad, bc, np_d, th = rows[0]
print(f"\nPer-column black fraction ({label}, first 10 cols):")
print(f"  col gray:       {[f'{grad[0,c]:.3f}' for c in range(10)]}")
print(f"  threshold:      {[f'{1 - th[:,c].mean():.3f}' for c in range(10)]}")
print(f"  bidder.cipher:  {[f'{1 - bc[:,c].mean():.3f}' for c in range(10)]}")
print(f"  numpy:          {[f'{1 - np_d[:,c].mean():.3f}' for c in range(10)]}")
