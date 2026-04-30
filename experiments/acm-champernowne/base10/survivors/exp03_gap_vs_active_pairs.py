"""
exp03_gap_vs_active_pairs.py — side-by-side test of mechanism.

Left panel: existing gap heatmap (loaded from l1_grid.npz).
Middle panel: predicted "active pair count" — at (K, n_0), the number
              of pairs (a, b) in the window [n_0, n_0 + W - 1] with
              K_pair(a, b) < K.
Right panel: difference of (suitably-scaled) two — to show whether
             the active-pair-count predicts gap location and sign.

Hypothesis: triangular features in the gap heatmap should align with
sharp transitions in the active-pair-count heatmap. If they do, the
gap structure is fully explained by the lcm/gcd lattice of
within-window pair collisions.

Output:
    exp03_gap_vs_active_pairs.png
"""

import os
import sys
import time

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from pair_thresholds import all_k_pairs

CACHE = os.path.join(HERE, 'l1_grid.npz')
OUT = os.path.join(HERE, 'exp03_gap_vs_active_pairs.png')

if not os.path.exists(CACHE):
    raise SystemExit(f'missing {CACHE}; run l1_grid.py first')

z = np.load(CACHE)
G = z['G']
N0_VALUES = z['N0_VALUES']
K_VALUES = z['K_VALUES']
W = int(z['W'])
TOTAL_PAIRS = W * (W - 1) // 2

print(f'Loaded gap grid: shape {G.shape}, W={W}, {TOTAL_PAIRS} pairs/window')

# Build active-pair-count grid.
print(f'Building active-pair-count grid ({len(N0_VALUES)} x {len(K_VALUES)})...')
A = np.zeros_like(G, dtype=np.int32)
t0 = time.time()
for i, n0 in enumerate(N0_VALUES):
    kps = sorted(all_k_pairs(int(n0), W))
    kps_arr = np.array(kps)
    for j, K in enumerate(K_VALUES):
        # Count K_pair < K (active pairs).
        A[i, j] = int((kps_arr < int(K)).sum())
print(f'  done in {time.time() - t0:.1f}s')

# Compute "delta-A" — the rate-of-change of active pair count along K.
# Cells where A jumps (new pair just activated) should correlate with
# the spikes in the gap. Use a per-row diff.
dA = np.zeros_like(A, dtype=np.float32)
dA[:, 1:] = np.diff(A.astype(np.float32), axis=1)

# Plot
fig, axes = plt.subplots(1, 3, figsize=(22, 8), dpi=130)
fig.patch.set_facecolor('#0a0a0a')
for ax in axes:
    ax.set_facecolor('#0a0a0a')

step_x = K_VALUES[1] - K_VALUES[0]
step_y = N0_VALUES[1] - N0_VALUES[0]
extent = (K_VALUES[0] - step_x / 2, K_VALUES[-1] + step_x / 2,
          N0_VALUES[0] - step_y / 2, N0_VALUES[-1] + step_y / 2)

# Panel 1: gap (95th-pct clipping like the zoom)
vmax_g = float(np.nanpercentile(np.abs(G), 95))
norm_g = TwoSlopeNorm(vmin=-vmax_g, vcenter=0.0, vmax=vmax_g)
im1 = axes[0].imshow(G, aspect='equal', origin='lower', cmap='RdBu_r',
                     norm=norm_g, interpolation='nearest', extent=extent)
axes[0].set_title('gap = mean(surv_L1 − bundle_L1)\n(95th-pct clip)',
                  color='white', fontsize=11)
plt.colorbar(im1, ax=axes[0], fraction=0.045, pad=0.02)

# Panel 2: active pair count
im2 = axes[1].imshow(A, aspect='equal', origin='lower', cmap='magma',
                     interpolation='nearest', extent=extent,
                     vmin=0, vmax=TOTAL_PAIRS)
axes[1].set_title(f'active pair count\n(0 to {TOTAL_PAIRS} pairs in window W={W})',
                  color='white', fontsize=11)
plt.colorbar(im2, ax=axes[1], fraction=0.045, pad=0.02,
             label=f'pairs with K_pair < K')

# Panel 3: dA (where pairs just activated)
vmax_d = float(np.nanpercentile(dA[dA > 0], 95)) if (dA > 0).any() else 1.0
im3 = axes[2].imshow(dA, aspect='equal', origin='lower', cmap='hot',
                     interpolation='nearest', extent=extent,
                     vmin=0, vmax=vmax_d)
axes[2].set_title('dA/dK = pairs activated\nin this K step\n(bright = activation event)',
                  color='white', fontsize=11)
plt.colorbar(im3, ax=axes[2], fraction=0.045, pad=0.02)

# Reference curves on all three panels.
n_grid = np.linspace(N0_VALUES[0], N0_VALUES[-1], 400)
for ax in axes:
    # K = n_0 + 1 first-collision diagonal (when gcd=1)
    ax.plot(n_grid + 1, n_grid, color='#ffcc5c', linewidth=0.7,
            alpha=0.5, label='K = n_0 + 1')
    ax.plot(n_grid / 2, n_grid, color='#6ec6ff', linewidth=0.7,
            alpha=0.4, label='K = n_0 / 2')
    ax.set_xlim(K_VALUES[0] - step_x / 2, K_VALUES[-1] + step_x / 2)
    ax.set_ylim(N0_VALUES[0] - step_y / 2, N0_VALUES[-1] + step_y / 2)
    ax.set_xlabel('K', color='white', fontsize=11)
    ax.set_ylabel(f'n_0 (window=[n_0,n_0+{W-1}])', color='white', fontsize=11)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#333')

axes[0].legend(loc='upper right', fontsize=8, framealpha=0.4,
               labelcolor='white', facecolor='#1a1a1a')

fig.suptitle(
    'Mechanism test: do the triangular fingers in the gap match '
    'pair-collision activation?',
    color='white', fontsize=13, y=0.99
)

plt.tight_layout()
plt.savefig(OUT, dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
plt.close()
print(f'-> {OUT}')

# Quick correlation: does |gap| correlate with dA?
nan_mask = ~np.isnan(G)
gap_abs = np.abs(G[nan_mask])
dA_flat = dA[nan_mask]
corr = np.corrcoef(gap_abs, dA_flat)[0, 1] if dA_flat.std() > 0 else float('nan')
print(f'\nCorrelation |gap| vs dA/dK: {corr:.4f}')

# And |gap| vs A directly
A_flat = A[nan_mask].astype(np.float32)
corr_A = np.corrcoef(gap_abs, A_flat)[0, 1] if A_flat.std() > 0 else float('nan')
print(f'Correlation |gap| vs A: {corr_A:.4f}')
