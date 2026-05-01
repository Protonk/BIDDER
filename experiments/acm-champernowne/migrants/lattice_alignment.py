"""
lattice_alignment.py — use exp07's collision lattice as a bin-1
isolator and read the bin-2 residue from the L1 tracking gap.

Substrate:
  - l1_grid.npz       — signed gap G(n_0, K), step 10, W = 10
  - exp07_lattice.npz — collision events COLL(n_0, K), step 1

Procedure:
  1. Aggregate COLL into a cumulative count L(n_0, K) sampled at the
     l1_grid K-step (10).
  2. Per-row least-squares fit:  G[i] ≈ α_i · L[i].
     The fitted α_i · L[i] is the bin-1 projection.
     G − α_i · L[i] is the bin-2 residual.
  3. Stats: cell- and row-level Spearman; lattice-vs-non-lattice
     mean |G|; energy split.
  4. Four-panel figure: G, L, bin-1 projection, bin-2 residual.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

HERE = os.path.dirname(os.path.abspath(__file__))

g = np.load(os.path.join(HERE, 'l1_grid.npz'))
G = g['G']
N0 = g['N0_VALUES']
K10 = g['K_VALUES']

l = np.load(os.path.join(HERE, 'exp07_lattice.npz'))
COLL = l['COLL']
assert np.all(l['N0_VALUES'] == N0), "n_0 grids must match"

# Cumulative collision count up to and including each K step.
L_cum = np.cumsum(COLL, axis=1)
L = L_cum[:, K10 - 1].astype(float)
absG = np.abs(G)

# ── Stats ──────────────────────────────────────────────────────────
flat_G = absG.ravel(); flat_L = L.ravel()
def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    return float(np.corrcoef(ra, rb)[0, 1])
rho_cell = spearman(flat_G, flat_L)

mask = L > 0
mean_lat = float(absG[mask].mean())
mean_non = float(absG[~mask].mean()) if (~mask).any() else float('nan')
print(f"Cell-level Spearman(|G|, L cumulative): {rho_cell:+.3f}")
print(f"Mean |G|     lattice-active cells: {mean_lat:.4f} (n={int(mask.sum())})")
print(f"Mean |G| lattice-quiet  cells:    {mean_non:.4f} (n={int((~mask).sum())})")
ratio = float('inf') if mean_non == 0 else mean_lat / mean_non
print(f"Ratio active/quiet: {ratio} "
      f"(quiet cells have NO collisions, so gap is exactly 0)")

row_L = L.sum(axis=1)
row_G = np.sqrt((absG ** 2).mean(axis=1))
rho_row = spearman(row_L, row_G)
print(f"Row-level Spearman(row-sum L, row-RMS |G|): {rho_row:+.3f}")

# Per-row LS fit  G[i] ≈ α_i · L[i]
alphas = np.zeros(G.shape[0])
G_proj = np.zeros_like(G)
for i in range(G.shape[0]):
    denom = float((L[i] * L[i]).sum())
    if denom > 0:
        alphas[i] = float((G[i] * L[i]).sum()) / denom
    G_proj[i] = alphas[i] * L[i]
G_resid = G - G_proj

print(f"\nPer-row α: min={alphas.min():+.5f}, max={alphas.max():+.5f}, "
      f"median={np.median(alphas):+.5f}")
e_total = float(np.abs(G).sum())
e_proj = float(np.abs(G_proj).sum())
e_resid = float(np.abs(G_resid).sum())
print(f"|G|     total: {e_total:.4f}")
print(f"|αL|    bin-1 projection: {e_proj:.4f} ({100*e_proj/e_total:.1f}%)")
print(f"|G−αL|  bin-2 residual:   {e_resid:.4f} ({100*e_resid/e_total:.1f}%)")
print(f"σ_R / σ_G: {np.std(G_resid)/np.std(G):.3f}")

# ── Four-panel figure ──────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(15, 12))
fig.patch.set_facecolor('#0a0a0a')

step = K10[1] - K10[0]
extent = (K10[0]-step/2, K10[-1]+step/2, N0[0]-step/2, N0[-1]+step/2)
vmax = float(np.percentile(absG, 95))
norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)

ax = axes[0, 0]; ax.set_facecolor('#0a0a0a')
im = ax.imshow(G, origin='lower', cmap='RdBu_r', norm=norm,
               extent=extent, aspect='equal', interpolation='nearest')
ax.set_title(f'G  (signed gap, |G|@95% = {vmax:.4f})', color='white', fontsize=11)
plt.colorbar(im, ax=ax, fraction=0.04, pad=0.02)

ax = axes[0, 1]; ax.set_facecolor('#0a0a0a')
im = ax.imshow(L, origin='lower', cmap='hot',
               extent=extent, aspect='equal', interpolation='nearest')
ax.set_title('L  (cumulative collision lattice up to K)', color='white', fontsize=11)
plt.colorbar(im, ax=ax, fraction=0.04, pad=0.02)

ax = axes[1, 0]; ax.set_facecolor('#0a0a0a')
im = ax.imshow(G_proj, origin='lower', cmap='RdBu_r', norm=norm,
               extent=extent, aspect='equal', interpolation='nearest')
ax.set_title(f'α(n_0)·L  (bin 1 projection, {100*e_proj/e_total:.1f}% of |G|)',
             color='white', fontsize=11)
plt.colorbar(im, ax=ax, fraction=0.04, pad=0.02)

ax = axes[1, 1]; ax.set_facecolor('#0a0a0a')
im = ax.imshow(G_resid, origin='lower', cmap='RdBu_r', norm=norm,
               extent=extent, aspect='equal', interpolation='nearest')
ax.set_title(f'G − bin 1  (bin 2 residual, {100*e_resid/e_total:.1f}% of |G|)',
             color='white', fontsize=11)
plt.colorbar(im, ax=ax, fraction=0.04, pad=0.02)

for ax in axes.ravel():
    ax.tick_params(colors='white', labelsize=8)
    for spine in ax.spines.values():
        spine.set_color('#333')

fig.suptitle(
    f'Lattice subtraction:  cell ρ = {rho_cell:+.3f}    '
    f'row ρ = {rho_row:+.3f}    '
    f'lattice-quiet cells have |G| = 0 exactly',
    color='white', fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(HERE, 'lattice_alignment.png'),
            dpi=180, facecolor='#0a0a0a', bbox_inches='tight')
print("\n-> lattice_alignment.png")

# Per-row α plot — does the fit constant correlate with anything?
fig2, ax = plt.subplots(figsize=(11, 5.5))
fig2.patch.set_facecolor('#0a0a0a'); ax.set_facecolor('#0a0a0a')
ax.plot(N0, alphas, 'o-', color='#ffcc5c', markersize=3, linewidth=0.8)
ax.axhline(0, color='#444', linewidth=0.5)
ax.set_xlabel('n_0', color='white'); ax.set_ylabel('α(n_0)', color='white')
ax.set_title('Per-row fit constant α(n_0)  (positive = bin 1 raises L1 gap, '
             'negative = bin 1 suppresses L1 gap)', color='white', fontsize=11)
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('#333')
ax.grid(True, color='#222', linewidth=0.4)
fig2.tight_layout()
fig2.savefig(os.path.join(HERE, 'lattice_alpha_per_row.png'),
             dpi=180, facecolor='#0a0a0a', bbox_inches='tight')
print("-> lattice_alpha_per_row.png")
