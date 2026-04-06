"""
Polar Champernowne — two approaches that actually work.

Piece 1: Sunflower
  Standard phyllotaxis packing (r = sqrt(n), theta = n * golden_angle).
  Color = C(n). The sawtooth produces three sharp color contours at
  n = 10, 100, 1000 — circles where C(n) drops from ~2.0 to ~1.1.
  Between the contours, color ramps smoothly.

Piece 2: Polar Waveform
  The sawtooth C(n) drawn as a polar line plot. One revolution per
  digit class (theta = 2*pi * frac(log10(n))), and radius IS C(n)
  directly — but now as a LINE, not scattered points. The line's
  continuous sweep makes the 4 nested loops (one per digit class)
  read as a coherent shape rather than random points. The sharp
  drops at powers of 10 create radial slashes from r=2 to r=1.1.
"""

import sys
sys.path.insert(0, '../../../../../core')

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from acm_core import acm_champernowne_array

N = 10000
vals = acm_champernowne_array(N)
ns = np.arange(1, N + 1, dtype=float)

digit_class = np.floor(np.log10(ns)).astype(int)

# =====================================================================
# Piece 1: Sunflower with sawtooth color
# =====================================================================

golden_angle = np.pi * (3 - np.sqrt(5))
theta_s = ns * golden_angle
r_s = np.sqrt(ns)

x_s = r_s * np.cos(theta_s)
y_s = r_s * np.sin(theta_s)

fig, ax = plt.subplots(figsize=(14, 14))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

# Size decreases with n so outer ring doesn't dominate
sizes = 8.0 / (1 + 0.03 * np.sqrt(ns))

sc = ax.scatter(x_s, y_s, c=vals, cmap='magma',
                s=sizes, alpha=0.9, vmin=1.05, vmax=2.05,
                edgecolors='none', rasterized=True)

# Annotate the shock fronts
for p10, label in [(10, 'n=10'), (100, 'n=100'), (1000, 'n=1000')]:
    r_ring = np.sqrt(p10)
    th = np.linspace(0, 2*np.pi, 200)
    ax.plot(r_ring * np.cos(th), r_ring * np.sin(th),
            color='white', linewidth=0.3, alpha=0.3)

ax.set_aspect('equal')
lim = np.sqrt(N) * 1.08
ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)
ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)
ax.set_title('Champernowne Sunflower', color='white', fontsize=16, pad=15)

cbar = plt.colorbar(sc, ax=ax, pad=0.01, shrink=0.7)
cbar.set_label('C(n)', color='white', fontsize=11)
cbar.ax.tick_params(colors='white')

plt.savefig('sunflower.png', dpi=300, facecolor='#0a0a0a', bbox_inches='tight')
print("-> sunflower.png")
plt.close()

# =====================================================================
# Piece 2: Polar waveform — the sawtooth as a line
# =====================================================================

log_n = np.log10(ns)
theta_w = 2 * np.pi * (log_n - np.floor(log_n))
r_w = vals  # radius IS C(n) directly

x_w = r_w * np.cos(theta_w)
y_w = r_w * np.sin(theta_w)

fig, ax = plt.subplots(figsize=(14, 14))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

dc_colors = ['#ff6f61', '#ffcc5c', '#88d8b0', '#6ec6ff']
dc_labels = ['1-digit', '2-digit', '3-digit', '4-digit']
dc_lw = [2.0, 1.5, 0.8, 0.15]

# Draw each digit class as a colored line, with glow
for dc in range(4):
    mask = digit_class == dc
    idx = np.where(mask)[0]
    # Glow layer (wider, transparent)
    ax.plot(x_w[idx], y_w[idx], color=dc_colors[dc],
            linewidth=dc_lw[dc] * 3, alpha=0.08)
    # Core line
    ax.plot(x_w[idx], y_w[idx], color=dc_colors[dc],
            linewidth=dc_lw[dc], alpha=0.85, label=dc_labels[dc])

# Draw the radial slashes at digit-class boundaries (the drops)
for boundary in [9, 99, 999]:
    # Line from the end of one class to start of next
    bx = [x_w[boundary], x_w[boundary + 1]]
    by = [y_w[boundary], y_w[boundary + 1]]
    ax.plot(bx, by, color='white', linewidth=0.8, alpha=0.6, linestyle='--')

# Reference circles
for r_ref in [1.1, 1.55, 2.0]:
    th = np.linspace(0, 2*np.pi, 200)
    ax.plot(r_ref * np.cos(th), r_ref * np.sin(th),
            color='#333', linewidth=0.5, linestyle=':')

ax.set_aspect('equal')
ax.set_xlim(-2.3, 2.3)
ax.set_ylim(-2.3, 2.3)
ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)
ax.legend(loc='upper left', fontsize=10, framealpha=0.3,
          labelcolor='white', facecolor='#1a1a1a')
ax.set_title('Polar Sawtooth', color='white', fontsize=16, pad=15)

plt.savefig('polar_sawtooth.png', dpi=300, facecolor='#0a0a0a', bbox_inches='tight')
print("-> polar_sawtooth.png")
