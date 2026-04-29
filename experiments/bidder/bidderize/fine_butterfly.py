"""
fine_butterfly.py — high-density variant of butterfly.py.

Same construction as butterfly.py — keyed permutation of [0, PERIOD)
plotted as (i, B(i)) rotated 45 degrees, colored by output mod 9 on
a yellow-to-blue (CMB) scale, cropped to a Mollweide-ish oval — but
50x the point count and ~8x finer dots so the 2D pattern of the
permutation can resolve. The original butterfly.png is preserved
alongside (this script writes fine_butterfly.png).
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
PERIOD = 1_000_000   # 50x butterfly.py's 20,000
KEY = b'butterfly'   # same key as butterfly.py for direct comparability

DOT_SIZE = 0.25      # was 2.0 in butterfly.py
DPI = 400            # was 250
FIGSIZE = (16, 8)    # was (14, 7)
ALPHA = 0.85         # slight blend so dense regions accumulate


def main():
    print(f'Generating permutation (period={PERIOD:,})...')
    B = bidder.cipher(period=PERIOD, key=KEY)
    indices = np.arange(PERIOD, dtype=np.float64)
    values = np.fromiter(B, dtype=np.int64, count=PERIOD)
    residues = values % 9
    values_f = values.astype(np.float64)

    # Rotate 45 degrees.
    cos45 = np.cos(np.pi / 4)
    sin45 = np.sin(np.pi / 4)
    rx = cos45 * indices - sin45 * values_f
    ry = sin45 * indices + cos45 * values_f

    # Centre and normalise to [-1, 1].
    cx, cy = rx.mean(), ry.mean()
    rx -= cx
    ry -= cy
    scale = max(np.abs(rx).max(), np.abs(ry).max()) * 1.02
    rx /= scale
    ry /= scale

    # Inscribed oval inside the rotated diamond. Same geometry as
    # butterfly.py — semi-axes (a/(1+a), 1/(1+a)) with aspect=1.6.
    aspect = 1.6
    semi_a = aspect / (1.0 + aspect)
    semi_b = 1.0 / (1.0 + aspect)
    inside = (rx / semi_a) ** 2 + (ry / semi_b) ** 2 < 1.0
    rx = rx[inside]
    ry = ry[inside]
    residues = residues[inside]

    print(f'Rendering {len(rx):,} points inside oval at dpi={DPI}, '
          f's={DOT_SIZE}...')

    # CMB-style yellow-to-blue colormap on residues mod 9.
    cmap = plt.cm.RdYlBu_r
    norm = Normalize(vmin=0, vmax=8)
    colors = cmap(norm(residues.astype(float)))

    fig, ax = plt.subplots(figsize=FIGSIZE)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    ax.scatter(
        rx, ry,
        s=DOT_SIZE, c=colors, alpha=ALPHA,
        edgecolors='none', rasterized=True,
        marker=',',  # pixel-style marker for densest rendering at this size
    )

    # Oval border.
    ellipse = Ellipse(
        (0, 0), width=2 * semi_a, height=2 * semi_b,
        fill=False, edgecolor='#333', linewidth=1.0,
    )
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

    out = os.path.join(HERE, 'fine_butterfly.png')
    fig.savefig(out, dpi=DPI, facecolor=BG, bbox_inches='tight',
                pad_inches=0.15)
    plt.close(fig)
    print(f'-> fine_butterfly.png  ({len(rx):,} points inside oval)')


if __name__ == '__main__':
    main()
