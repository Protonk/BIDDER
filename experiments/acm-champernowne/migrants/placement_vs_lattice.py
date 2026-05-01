"""
placement_vs_lattice.py — does the placement residual scale with
lattice density?

Migrant #7 follow-up. EXP4 (placement_destroyer) showed the residual
|G − G_shuffled| is concentrated in the low-K active wedge.
Hypothesis: the residual scales with lattice density per cell —
more duplicates → more permutation freedom → bigger per-cell
placement effect.

Two regressors, both natural:
- L_cum(n_0, K)  = cumulative collision count up to K (monotone in K)
- COLL_at_K(n_0, K) = collisions at this specific K-step (lattice support)

Output:
  placement_vs_lattice.png    scatter + binned mean for both regressors
"""

import os

import numpy as np
import matplotlib.pyplot as plt


HERE = os.path.dirname(os.path.abspath(__file__))

g = np.load(os.path.join(HERE, 'l1_grid.npz'))
G = g['G']
N0 = g['N0_VALUES']
K10 = g['K_VALUES']

p = np.load(os.path.join(HERE, 'placement_destroyer.npz'))
G_shuffled = p['G_shuffled']

l = np.load(os.path.join(HERE, 'exp07_lattice.npz'))
COLL = l['COLL']
assert np.all(l['N0_VALUES'] == N0)

# Aggregations to step-10 grid.
L_cum = np.cumsum(COLL, axis=1)[:, K10 - 1].astype(float)
COLL_block = np.zeros_like(G, dtype=float)
for j, kv in enumerate(K10):
    COLL_block[:, j] = COLL[:, max(0, kv - 10):kv].sum(axis=1)

R = np.abs(G - G_shuffled)


def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    return float(np.corrcoef(ra, rb)[0, 1])


flat_R = R.ravel()
flat_Lcum = L_cum.ravel()
flat_COLL = COLL_block.ravel()
mask = np.isfinite(flat_R) & (flat_R > 0)
n_cells = int(mask.sum())

rho_cum = spearman(flat_R[mask], flat_Lcum[mask])
rho_coll = spearman(flat_R[mask], flat_COLL[mask])
pearson_cum = float(np.corrcoef(flat_R[mask], flat_Lcum[mask])[0, 1])
pearson_coll = float(np.corrcoef(flat_R[mask], flat_COLL[mask])[0, 1])

# Log-log regression for power-law check (cumulative).
both_pos = mask & (flat_Lcum > 0) & (flat_R > 1e-10)
log_R = np.log10(flat_R[both_pos])
log_L = np.log10(flat_Lcum[both_pos])
slope, intercept = np.polyfit(log_L, log_R, 1)
loglog_pearson = float(np.corrcoef(log_L, log_R)[0, 1])

print(f"Cells with R > 0:                {n_cells} / {flat_R.size}")
print(f"\nRegressing |G − G_shuffled| against:")
print(f"  L_cum (cumulative):    "
      f"Spearman {rho_cum:+.3f}   Pearson {pearson_cum:+.3f}")
print(f"  COLL at K (per-step):  "
      f"Spearman {rho_coll:+.3f}   Pearson {pearson_coll:+.3f}")
print(f"\nLog-log fit  log|R| = α · log L_cum + β:")
print(f"  α (slope)        = {slope:+.3f}")
print(f"  β (intercept)    = {intercept:+.3f}")
print(f"  log-log Pearson  = {loglog_pearson:+.3f}")
print(f"  → |R| ≈ 10^{intercept:.2f} · L_cum^{slope:.2f}")


# Binned means: percentile bins of L_cum, mean R per bin.
def binned(x, y, n_bins=20):
    edges = np.percentile(x, np.linspace(0, 100, n_bins + 1))
    centers, means, sems = [], [], []
    for i in range(n_bins):
        lo, hi = edges[i], edges[i + 1]
        if hi <= lo:
            continue
        sel = (x >= lo) & (x < hi if i < n_bins - 1 else x <= hi)
        if sel.sum() < 5:
            continue
        centers.append(0.5 * (lo + hi))
        means.append(float(y[sel].mean()))
        sems.append(float(y[sel].std() / np.sqrt(sel.sum())))
    return np.array(centers), np.array(means), np.array(sems)


cum_x, cum_mean, cum_sem = binned(flat_Lcum[mask], flat_R[mask])
coll_x, coll_mean, coll_sem = binned(flat_COLL[mask], flat_R[mask])

# ── Figure ─────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(15, 6.5))
fig.patch.set_facecolor('#0a0a0a')

ax = axes[0]
ax.set_facecolor('#0a0a0a')
ax.scatter(flat_Lcum[mask], flat_R[mask], s=2, alpha=0.15, color='#6ec6ff')
ax.errorbar(cum_x, cum_mean, yerr=cum_sem, fmt='o-', color='#ffcc5c',
            linewidth=1.5, markersize=5, capsize=2,
            label='binned mean ± SEM')
xs = np.array([flat_Lcum[mask].min(), flat_Lcum[mask].max()])
ax.loglog(xs, 10 ** intercept * xs ** slope, '--', color='#ff6699',
          linewidth=1.0, label=f'power fit α = {slope:+.2f}')
ax.set_xscale('log'); ax.set_yscale('log')
ax.set_xlabel('L_cum (cumulative collisions)', color='white')
ax.set_ylabel('|G − G_shuffled|', color='white')
ax.set_title(f'Residual vs cumulative lattice density\n'
             f'Spearman = {rho_cum:+.3f}, log-log Pearson = '
             f'{loglog_pearson:+.3f}',
             color='white', fontsize=11)
ax.legend(loc='lower right', fontsize=9, framealpha=0.3,
          labelcolor='white', facecolor='#1a1a1a')
ax.grid(True, color='#222', linewidth=0.4, which='both')

ax = axes[1]
ax.set_facecolor('#0a0a0a')
ax.scatter(flat_COLL[mask], flat_R[mask], s=2, alpha=0.15, color='#6ec6ff')
ax.errorbar(coll_x, coll_mean, yerr=coll_sem, fmt='o-', color='#ffcc5c',
            linewidth=1.5, markersize=5, capsize=2,
            label='binned mean ± SEM')
ax.set_xlabel('COLL_at_K (collisions in this K-block)', color='white')
ax.set_ylabel('|G − G_shuffled|', color='white')
ax.set_title(f'Residual vs per-step lattice intensity\n'
             f'Spearman = {rho_coll:+.3f}, Pearson = {pearson_coll:+.3f}',
             color='white', fontsize=11)
ax.legend(loc='lower right', fontsize=9, framealpha=0.3,
          labelcolor='white', facecolor='#1a1a1a')
ax.grid(True, color='#222', linewidth=0.4)

for a in axes:
    a.tick_params(colors='white', labelsize=9)
    for spine in a.spines.values():
        spine.set_color('#333')

fig.suptitle(
    'Migrant #7 follow-up: placement residual scales with lattice density',
    color='white', fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(HERE, 'placement_vs_lattice.png'), dpi=180,
            facecolor='#0a0a0a', bbox_inches='tight')
print("\n-> placement_vs_lattice.png")
