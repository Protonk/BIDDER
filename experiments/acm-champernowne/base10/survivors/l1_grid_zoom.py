"""
l1_grid_zoom.py — render the cached gap matrix with a tight colour
range, plus reference curves for first-collision and decade-crossing
predictions, so any roughness / harmonics in the active wedge are
visible. Loads l1_grid.npz; if missing, run l1_grid.py first.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

CACHE = 'l1_grid.npz'
if not os.path.exists(CACHE):
    raise SystemExit(f"missing {CACHE} — run `sage -python l1_grid.py` first")

z = np.load(CACHE)
G          = z['G']
N0_VALUES  = z['N0_VALUES']
K_VALUES   = z['K_VALUES']
W          = int(z['W'])
WARMUP     = float(z['WARMUP_FRAC'])

# Tight clipping based on the bulk distribution (95th pct of |G|).
abs_G = np.abs(G)
vmax = float(np.nanpercentile(abs_G, 95))
print(f"95th-pct |gap|: {vmax:.4f}  (full max: {abs_G.max():.4f})")

step_x = K_VALUES[1] - K_VALUES[0]
step_y = N0_VALUES[1] - N0_VALUES[0]
extent = (K_VALUES[0] - step_x / 2, K_VALUES[-1] + step_x / 2,
          N0_VALUES[0] - step_y / 2, N0_VALUES[-1] + step_y / 2)

fig, ax = plt.subplots(figsize=(11, 11))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
im = ax.imshow(G, aspect='equal', origin='lower', cmap='RdBu_r',
               norm=norm, interpolation='nearest', extent=extent)

# Reference curves on top.
n_grid = np.linspace(N0_VALUES[0], N0_VALUES[-1], 400)

# First-collision diagonal: K = n_0 + 1.
ax.plot(n_grid + 1, n_grid, color='#ffcc5c', linewidth=0.8,
        alpha=0.55, label='K = n_0 + 1  (first collision)')

# Half-collision (when n_0 even, lcm(n_0, n_0+2)/n_0 ≈ (n_0+2)/2 ≈ n_0/2).
ax.plot(n_grid / 2, n_grid, color='#6ec6ff', linewidth=0.8,
        alpha=0.5, label='K ≈ n_0 / 2')

# Decade hyperbolae: K · n_0 = 10^d  (d = 4, 5, 6).
for d, alpha in [(4, 0.45), (5, 0.45), (6, 0.4)]:
    Kd = 10**d / n_grid
    mask = (Kd >= K_VALUES[0]) & (Kd <= K_VALUES[-1])
    if mask.any():
        ax.plot(Kd[mask], n_grid[mask], color='#cccccc',
                linewidth=0.7, linestyle='--', alpha=alpha,
                label=(f'K · n_0 = 10^{d}  (decade)' if d == 4 else None))

ax.set_xlim(K_VALUES[0] - step_x / 2, K_VALUES[-1] + step_x / 2)
ax.set_ylim(N0_VALUES[0] - step_y / 2, N0_VALUES[-1] + step_y / 2)

ax.set_xlabel('K  (atoms per stream)', color='white', fontsize=12)
ax.set_ylabel(f'n_0  (window = [n_0, n_0 + {W - 1}])',
              color='white', fontsize=12)
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('#333')

ax.set_xticks(np.arange(100, 1001, 100))
ax.set_xticks(np.arange(50, 1001, 50), minor=True)
ax.set_yticks(np.arange(100, 1001, 100))
ax.set_yticks(np.arange(50, 1001, 50), minor=True)
ax.tick_params(which='minor', length=2, color='#555')

cbar = plt.colorbar(im, ax=ax, fraction=0.04, pad=0.02, extend='both')
cbar.set_label('mean (surv_L1 − bundle_L1)  '
               '(clipped at 95th pct)',
               color='white', fontsize=11)
cbar.ax.tick_params(colors='white')
cbar.outline.set_edgecolor('#333')

ax.legend(loc='upper right', fontsize=9, framealpha=0.35,
          labelcolor='white', facecolor='#1a1a1a')

ax.set_title(
    f'L1 tracking gap (zoom)  —  '
    f'W = {W}, n_0 ∈ [{N0_VALUES[0]}, {N0_VALUES[-1]}], '
    f'K ∈ [{K_VALUES[0]}, {K_VALUES[-1]}], step = {step_x}',
    color='white', fontsize=12)

plt.tight_layout()
plt.savefig('l1_grid_zoom.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> l1_grid_zoom.png")
