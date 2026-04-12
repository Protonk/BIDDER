"""
butterfly.py — The permutation itself, rendered as a CMB-style oval.

Plot (i, B.at(i)) rotated 45 degrees, colored by output mod 9 on a
yellow-to-blue scale (CMB convention), cropped to a Mollweide-ish oval.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..')
DIST = os.path.join(ROOT, 'dist')
sys.path.insert(0, DIST)

try:
    import bidder_c as bidder
except ImportError:
    import bidder

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from matplotlib.colors import Normalize


BG = '#080808'
PERIOD = 20000
KEY = b'butterfly'


def main():
    print(f'Generating permutation (period={PERIOD})...')
    B = bidder.cipher(period=PERIOD, key=KEY)
    indices = np.arange(PERIOD, dtype=np.float64)
    values = np.array(list(B), dtype=np.float64)
    residues = np.array(list(B), dtype=np.int64) % 9

    # Rotate 45 degrees
    cos45 = np.cos(np.pi / 4)
    sin45 = np.sin(np.pi / 4)
    rx = cos45 * indices - sin45 * values
    ry = sin45 * indices + cos45 * values

    # Centre and normalise to [-1, 1]
    cx, cy = rx.mean(), ry.mean()
    rx -= cx
    ry -= cy
    scale = max(np.abs(rx).max(), np.abs(ry).max()) * 1.02
    rx /= scale
    ry /= scale

    # Oval inscribed inside the diamond: the ellipse touches all four
    # edges of the rotated square. For a diamond with half-diagonals 1,
    # the inscribed ellipse with aspect ratio a has semi-axes
    # (a/(1+a), 1/(1+a)) so it's tangent to all four sides.
    aspect = 1.6
    semi_a = aspect / (1.0 + aspect)  # horizontal
    semi_b = 1.0 / (1.0 + aspect)     # vertical
    inside = (rx / semi_a) ** 2 + (ry / semi_b) ** 2 < 1.0
    rx = rx[inside]
    ry = ry[inside]
    residues = residues[inside]

    # CMB colormap: yellow to blue
    cmap = plt.cm.RdYlBu_r
    norm = Normalize(vmin=0, vmax=8)
    colors = cmap(norm(residues.astype(float)))

    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    ax.scatter(rx, ry, s=2.0, c=colors, alpha=1.0,
               edgecolors='none', rasterized=True)

    # Draw the oval border
    ellipse = Ellipse((0, 0), width=2 * semi_a, height=2 * semi_b,
                      fill=False, edgecolor='#333', linewidth=1.2)
    ax.add_patch(ellipse)

    ax.set_xlim(-semi_a * 1.04, semi_a * 1.04)
    ax.set_ylim(-semi_b * 1.08, semi_b * 1.08)
    ax.set_aspect('equal')
    ax.axis('off')

    fig.text(
        0.5, 0.95,
        f'period {PERIOD:,}  ·  key {KEY.decode()!r}  ·  color = output mod 9',
        ha='center', va='top', color='#444', fontsize=10,
    )

    out = os.path.join(HERE, 'butterfly.png')
    fig.savefig(out, dpi=250, facecolor=BG, bbox_inches='tight',
                pad_inches=0.15)
    plt.close(fig)
    print(f'-> butterfly.png  ({inside.sum()} points inside oval)')


if __name__ == '__main__':
    main()
