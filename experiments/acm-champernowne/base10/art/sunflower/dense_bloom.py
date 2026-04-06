"""
Dense Bloom — the Champernowne sunflower as bioluminescent art.

80,000 points in golden-angle phyllotaxis. Each point rendered in
three passes (halo → glow → core) with size scaling by C(n): bright
points bloom large, dim points shrink to pinpricks. The sawtooth
becomes a rhythmic pulse — bright swells collapsing at each shock
front, then rebuilding outward.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', '..', '..', '..', '..', 'core'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from acm_core import acm_champernowne_array

# ── iridescent colormap ──────────────────────────────────────────────
# Dark violet base → electric blue → cyan flash → magenta → hot gold
# The blue-cyan-magenta sequence creates the iridescent "oil slick" feel

_iri = {
    'red':   [(0.00, 0.05, 0.05), (0.15, 0.08, 0.08),
              (0.30, 0.0,  0.0),  (0.42, 0.0,  0.0),
              (0.55, 0.75, 0.75), (0.70, 0.95, 0.95),
              (0.82, 1.0,  1.0),  (0.92, 1.0,  1.0),
              (1.00, 1.0,  1.0)],
    'green': [(0.00, 0.02, 0.02), (0.15, 0.02, 0.02),
              (0.30, 0.25, 0.25), (0.42, 0.85, 0.85),
              (0.55, 0.20, 0.20), (0.70, 0.10, 0.10),
              (0.82, 0.55, 0.55), (0.92, 0.85, 0.85),
              (1.00, 1.0,  1.0)],
    'blue':  [(0.00, 0.12, 0.12), (0.15, 0.35, 0.35),
              (0.30, 0.90, 0.90), (0.42, 0.95, 0.95),
              (0.55, 0.85, 0.85), (0.70, 0.15, 0.15),
              (0.82, 0.05, 0.05), (0.92, 0.15, 0.15),
              (1.00, 0.85, 0.85)],
}
cmap_iri = LinearSegmentedColormap('iridescent', _iri, N=512)

N = 80000

print(f"Computing C(n) for n = 1…{N:,} …")
vals = acm_champernowne_array(N)
ns = np.arange(1, N + 1, dtype=float)

# ── phyllotaxis layout ───────────────────────────────────────────────

golden_angle = np.pi * (3 - np.sqrt(5))
theta = ns * golden_angle
r = np.sqrt(ns)

x = r * np.cos(theta)
y = r * np.sin(theta)

# ── size and intensity from C(n) ─────────────────────────────────────

# Normalize C(n) to [0, 1] for size/intensity scaling
v_min, v_max = 1.05, 2.05
c_norm = np.clip((vals - v_min) / (v_max - v_min), 0, 1)

# Base size shrinks with radius (so outer ring doesn't dominate)
base = 18.0 / (1 + 0.004 * np.sqrt(ns))

# Bloom: bright points swell, dim points contract
bloom_factor = 0.4 + 3.0 * c_norm**1.3

# ── three-pass rendering ─────────────────────────────────────────────

print("Rendering …")
fig = plt.figure(figsize=(16, 16))
fig.patch.set_facecolor('#050508')
ax = fig.add_axes([0, 0, 1, 1])
ax.set_facecolor('#050508')
ax.set_aspect('equal')

lim = np.sqrt(N) * 1.05
ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)
ax.axis('off')

# Pass 1: wide soft halo
print("  halo …")
ax.scatter(x, y, c=vals, cmap=cmap_iri,
           s=base * bloom_factor * 8.0,
           alpha=0.07, vmin=v_min, vmax=v_max,
           edgecolors='none', rasterized=True)

# Pass 2: medium glow
print("  glow …")
ax.scatter(x, y, c=vals, cmap=cmap_iri,
           s=base * bloom_factor * 3.0,
           alpha=0.22, vmin=v_min, vmax=v_max,
           edgecolors='none', rasterized=True)

# Pass 3: bright core
print("  core …")
ax.scatter(x, y, c=vals, cmap=cmap_iri,
           s=base * bloom_factor * 1.0,
           alpha=0.9, vmin=v_min, vmax=v_max,
           edgecolors='none', rasterized=True)

# ── save ─────────────────────────────────────────────────────────────

out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   'dense_bloom.png')
print("Saving …")
fig.savefig(out, dpi=250, facecolor='#050508', pad_inches=0)
plt.close()
print(f'-> {out}')
