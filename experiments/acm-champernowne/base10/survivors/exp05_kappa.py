"""
exp05_kappa.py — survival-rate phase diagram.

κ(K, n_0) := |Surv| / |Bundle|  for window [n_0, n_0 + W - 1] at K.

Tests whether the triangular fingers in the L1-gap heatmap are
features of the underlying set-membership object (κ itself) or
artefacts of the leading-digit measurement.

Predictions:
- κ = 1 below the smallest K_pair in the window (no collisions).
- κ has step-downs at each K_pair threshold.
- The triangular structure of the gap should appear in κ as well,
  if the gap is a faithful projection of κ.

Output: exp05_kappa.png (κ heatmap with reference curves; for direct
comparison, panel 2 shows the gap heatmap on the same coordinates).
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

OUT = os.path.join(HERE, 'exp05_kappa.png')
GAP_CACHE = os.path.join(HERE, 'l1_grid.npz')

# Match the l1_grid grid for direct comparison
W = 10
N0_VALUES = np.arange(10, 1001, 10)
K_VALUES = np.arange(10, 1001, 10)


def n_primes_vec(n: int, k: int) -> np.ndarray:
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


def kappa(n0: int, k: int, w: int = W) -> float:
    parts = [n_primes_vec(n, k) for n in range(n0, n0 + w)]
    m_arr = np.concatenate(parts)
    n_atoms = m_arr.size
    if n_atoms == 0:
        return float('nan')
    _, inverse, counts = np.unique(m_arr, return_inverse=True, return_counts=True)
    n_surv = int((counts[inverse] == 1).sum())
    return n_surv / n_atoms


print(f'Computing κ grid: {len(N0_VALUES)} × {len(K_VALUES)} = '
      f'{len(N0_VALUES) * len(K_VALUES)} cells, W={W}')
t0 = time.time()
K_GRID = np.zeros((len(N0_VALUES), len(K_VALUES)))
for i, n0 in enumerate(N0_VALUES):
    for j, K in enumerate(K_VALUES):
        K_GRID[i, j] = kappa(int(n0), int(K))
    if (i + 1) % 20 == 0 or i == 0:
        print(f'  rows: {i + 1}/{len(N0_VALUES)} (t={time.time() - t0:.1f}s)')
print(f'Total: {time.time() - t0:.1f}s')
print(f'κ range: [{np.nanmin(K_GRID):.4f}, {np.nanmax(K_GRID):.4f}]')

# Save cache for downstream
np.savez(os.path.join(HERE, 'kappa_grid.npz'), KAPPA=K_GRID,
         N0_VALUES=N0_VALUES, K_VALUES=K_VALUES, W=W)

# Load gap for comparison
if os.path.exists(GAP_CACHE):
    z = np.load(GAP_CACHE)
    G = z['G']
else:
    G = None

# Plot
n_panels = 2 if G is not None else 1
fig, axes = plt.subplots(1, n_panels, figsize=(11 * n_panels, 11), dpi=130)
fig.patch.set_facecolor('#0a0a0a')
if n_panels == 1:
    axes = [axes]
for ax in axes:
    ax.set_facecolor('#0a0a0a')

step_x = K_VALUES[1] - K_VALUES[0]
step_y = N0_VALUES[1] - N0_VALUES[0]
extent = (K_VALUES[0] - step_x / 2, K_VALUES[-1] + step_x / 2,
          N0_VALUES[0] - step_y / 2, N0_VALUES[-1] + step_y / 2)

# Panel 1: κ heatmap with sequential colormap (1 = white, smaller = darker)
ax = axes[0]
im1 = ax.imshow(K_GRID, aspect='equal', origin='lower', cmap='magma_r',
                interpolation='nearest', extent=extent,
                vmin=np.nanmin(K_GRID), vmax=1.0)
ax.set_title(f'κ = |Surv| / |Bundle|   (W={W})\n'
             f'1 = no collisions; smaller = more atoms culled',
             color='white', fontsize=12)
plt.colorbar(im1, ax=ax, fraction=0.045, pad=0.02)

# Panel 2: gap (if available), 95th-pct clip
if G is not None:
    ax = axes[1]
    vmax_g = float(np.nanpercentile(np.abs(G), 95))
    norm_g = TwoSlopeNorm(vmin=-vmax_g, vcenter=0.0, vmax=vmax_g)
    im2 = ax.imshow(G, aspect='equal', origin='lower', cmap='RdBu_r',
                    norm=norm_g, interpolation='nearest', extent=extent)
    ax.set_title('gap = mean(surv_L1 − bundle_L1)\n(95th-pct clip, leading-digit projection of κ?)',
                 color='white', fontsize=12)
    plt.colorbar(im2, ax=ax, fraction=0.045, pad=0.02)

# Reference curves on both panels
n_grid = np.linspace(N0_VALUES[0], N0_VALUES[-1], 400)
for ax in axes:
    ax.plot(n_grid + 1, n_grid, color='#ffcc5c', linewidth=0.8,
            alpha=0.55, label='K = n_0 + 1')
    ax.plot(n_grid / 2, n_grid, color='#6ec6ff', linewidth=0.8,
            alpha=0.5, label='K ≈ n_0 / 2')
    ax.set_xlim(K_VALUES[0] - step_x / 2, K_VALUES[-1] + step_x / 2)
    ax.set_ylim(N0_VALUES[0] - step_y / 2, N0_VALUES[-1] + step_y / 2)
    ax.set_xlabel('K (atoms per stream)', color='white', fontsize=11)
    ax.set_ylabel(f'n_0 (window=[n_0, n_0+{W-1}])', color='white', fontsize=11)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#333')

axes[0].legend(loc='upper right', fontsize=9, framealpha=0.4,
               labelcolor='white', facecolor='#1a1a1a')

fig.suptitle(
    'Survival rate κ vs leading-digit gap: same coordinates, '
    'different observable',
    color='white', fontsize=14, y=0.995
)

plt.tight_layout()
plt.savefig(OUT, dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
plt.close()
print(f'-> {OUT}')

# Numerical comparison: do κ and |gap| have correlated structure?
if G is not None:
    nan_mask = ~np.isnan(K_GRID) & ~np.isnan(G)
    # κ-deficit = 1 - κ (more deficit = more culling)
    kappa_def = 1.0 - K_GRID[nan_mask]
    gap_abs = np.abs(G[nan_mask])
    if kappa_def.std() > 0 and gap_abs.std() > 0:
        corr = float(np.corrcoef(kappa_def, gap_abs)[0, 1])
        print(f'\nCorrelation (1 - κ) vs |gap|: {corr:+.4f}')
