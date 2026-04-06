"""
rle_ridgeline.py — stacked waveforms of 0-run distributions

Each monoid's 0-run distribution rendered as a filled curve stacked
vertically with overlap (Unknown Pleasures style). High-v_2 monoids
bulge rightward. The ν₂ structure creates periodic eruptions in the
otherwise smooth exponential decay.
"""

import sys, os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..'))
sys.path.insert(0, os.path.join(_here, '..', '..', '..', '..', '..', 'core'))

import numpy as np
import matplotlib.pyplot as plt
from binary_core import binary_stream, rle


N_MAX = 2048
N_DISPLAY = 100      # number of waveform rows
TARGET_BITS = 50_000
MAX_RUN = 20         # display up to run-length 20
PRIMES_PER_N = 5000
SMOOTH_PTS = 400     # interpolation resolution per waveform

# Visual parameters
WAVE_HEIGHT = 8.0    # max wave amplitude (in row-spacing units)


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

zero_hist = np.zeros((N_MAX, MAX_RUN), dtype=float)

for idx in range(N_MAX):
    n = idx + 1
    if n % 256 == 0:
        print(f"  n = {n}...")

    bits = binary_stream(n, count=PRIMES_PER_N)[:TARGET_BITS]
    runs = rle(bits)

    zc = np.zeros(MAX_RUN + 1, dtype=int)  # +1 to include bin 0
    for val, length in runs:
        if val == 0:
            k = min(length, MAX_RUN + 1) - 1
            zc[k] += 1

    zt = zc.sum()
    if zt > 0:
        zero_hist[idx] = zc[:MAX_RUN] / zt

# Curated selection: ensure every ν₂ level is well-represented.
# Include powers of 2 AND their small multiples (3×2^k, 5×2^k, etc.)
# so we see the full cascade of eruptions, not just isolated peaks.
special = set()
for k in range(1, 12):
    for m in [1, 3, 5]:
        n = m * 2**k
        if 1 <= n <= N_MAX:
            special.add(n - 1)  # convert to 0-based idx
fill = np.linspace(0, N_MAX - 1, N_DISPLAY - len(special), dtype=int)
indices = np.unique(np.sort(np.concatenate([fill, list(special)])))
N_DISPLAY = len(indices)
sub_hist = zero_hist[indices]
sub_n = indices + 1

# Compute residual from the mean distribution.
# This strips the universal exponential decay and reveals the
# ν₂-dependent deviations — exactly the structural fingerprint.
mean_hist = zero_hist.mean(axis=0)
residual = sub_hist - mean_hist[np.newaxis, :]

# Cubic spline interpolation for smooth peaks
from scipy.interpolate import CubicSpline

x_bins = np.linspace(0, MAX_RUN - 1, MAX_RUN)
x_smooth = np.linspace(0, MAX_RUN - 1, SMOOTH_PTS)
smooth_hist = np.zeros((N_DISPLAY, SMOOTH_PTS))
for i in range(N_DISPLAY):
    cs = CubicSpline(x_bins, residual[i], bc_type='clamped')
    smooth_hist[i] = cs(x_smooth)


# ── Render ───────────────────────────────────────────────────────────

global_max = max(smooth_hist.max(), abs(smooth_hist.min()), 1e-10)

print("Rendering ridgeline...")

fig, ax = plt.subplots(figsize=(14, 20))
fig.patch.set_facecolor('#000000')
ax.set_facecolor('#000000')

# Draw back to front: row 0 is the topmost (highest n), drawn first.
# Lower rows (lower n) are drawn on top, so their fill occludes upper rows.
for row_idx in range(N_DISPLAY):
    i = N_DISPLAY - 1 - row_idx   # start from top
    n = sub_n[i]
    baseline = i                   # y-position of this waveform's baseline

    wave = np.clip(smooth_hist[i], 0, None)   # positive residuals only
    heights = wave / global_max * WAVE_HEIGHT

    y_vals = baseline + heights

    # Color by v_2: cool blue-white for low, warm amber for high
    v = v2(int(n))
    t = min(v / 7.0, 1.0)
    # Blue-white (0.70, 0.80, 1.0) -> amber (1.0, 0.65, 0.15)
    edge_color = (0.70 + 0.30 * t,
                  0.80 - 0.15 * t,
                  1.0 - 0.85 * t)
    lw = 0.6 + 0.8 * t   # thin for ν₂=0, thick for high ν₂

    # Black fill from well below baseline — occludes rows behind
    ax.fill_between(x_smooth, baseline - WAVE_HEIGHT - 1, y_vals,
                    facecolor='#000000', edgecolor='none',
                    zorder=row_idx * 4)
    # Colored interior fill
    ax.fill_between(x_smooth, baseline, y_vals,
                    facecolor=edge_color, edgecolor='none',
                    alpha=0.22, zorder=row_idx * 4 + 1)
    # Glow layer
    ax.plot(x_smooth, y_vals, color=edge_color, linewidth=lw * 3,
            alpha=0.12, zorder=row_idx * 4 + 2)
    # Sharp edge line
    ax.plot(x_smooth, y_vals, color=edge_color, linewidth=lw,
            zorder=row_idx * 4 + 3)

ax.set_xlim(0, MAX_RUN - 1)
ax.set_ylim(-1, N_DISPLAY + WAVE_HEIGHT + 1)
ax.set_axis_off()

plt.savefig('rle_ridgeline.png', dpi=200, pad_inches=0.1,
            bbox_inches='tight', facecolor='#000000')
print("-> rle_ridgeline.png")
