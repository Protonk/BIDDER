"""
rle_mirror.py — 0-runs and 1-runs mirrored, meeting in the middle

Transposed layout: n on x-axis (2048 columns), run length on y-axis.
0-runs on top (flipped: long runs at top edge, short at center seam).
1-runs on bottom (short at center seam, long at bottom edge).
Two colormaps meeting at the horizontal seam. No axes, no chrome.
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
MAX_RUN = 64
PRIMES_PER_N = 5000


def v2(n):
    if n == 0:
        return 0
    v = 0
    while n % 2 == 0:
        n //= 2
        v += 1
    return v


# ── Compute ──────────────────────────────────────────────────────────

print(f"Computing RLE for n=1..{N_MAX}...")

# Histograms: shape (N_MAX, MAX_RUN) — rows are monoids, cols are run lengths
zero_hist = np.zeros((N_MAX, MAX_RUN), dtype=float)
one_hist  = np.zeros((N_MAX, MAX_RUN), dtype=float)

for idx in range(N_MAX):
    n = idx + 1
    if n % 256 == 0:
        print(f"  n = {n}...")

    bits = binary_stream(n, count=PRIMES_PER_N)[:TARGET_BITS]
    runs = rle(bits)

    zc = np.zeros(MAX_RUN, dtype=int)
    oc = np.zeros(MAX_RUN, dtype=int)

    for val, length in runs:
        k = min(length, MAX_RUN) - 1
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

FLOOR = 1e-5

# Transpose: (N_MAX, MAX_RUN) -> (MAX_RUN, N_MAX)
# Now rows = run lengths, cols = monoids
zero_t = np.clip(zero_hist.T, FLOOR, None)  # shape (MAX_RUN, N_MAX)
one_t  = np.clip(one_hist.T, FLOOR, None)

# 0-runs on top, flipped vertically (long runs at top)
# 1-runs on bottom (short runs at top of bottom half, long at bottom)
zero_flipped = zero_t[::-1, :]   # long runs at top
# one_t is already short-at-top, long-at-bottom

# ── Colormaps ────────────────────────────────────────────────────────

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

norm = LogNorm(vmin=1e-4, vmax=1.0)

def to_rgb(data, cmap):
    normed = norm(data)
    return cmap(normed)[:, :, :3]

top_rgb    = to_rgb(zero_flipped, cmap_zero)
bottom_rgb = to_rgb(one_t, cmap_one)

full_rgb = np.vstack([top_rgb, bottom_rgb])

# Crop to square: 128 rows × 128 columns (n=1..128)
crop = full_rgb[:, :128, :]

# ── Render ───────────────────────────────────────────────────────────

print("Rendering...")

fig = plt.figure(frameon=False, figsize=(20, 20))
ax = plt.Axes(fig, [0., 0., 1., 1.])
ax.set_axis_off()
fig.add_axes(ax)

ax.imshow(crop, aspect='equal', interpolation='nearest')

# Thin seam at the horizontal join
ax.axhline(y=MAX_RUN - 0.5, color='white', linewidth=0.3, alpha=0.15)

plt.savefig('rle_mirror.png', dpi=200, pad_inches=0, bbox_inches='tight',
            facecolor='#000000')
print("-> rle_mirror.png")
