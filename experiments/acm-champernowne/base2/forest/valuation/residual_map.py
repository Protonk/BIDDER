"""
residual_map.py — V3: depth-residual of mean_rle0.

Reads tree_signatures.npz over n in 1..N_ANALYTIC. For each supported
v_2 row (>= MIN_V2_SUPPORT members), the within-row leave-one-out
mean is subtracted from each cell's mean_rle0. Cell color is the
raw residual on a diverging scale; cell alpha is driven by a
blockwise z-statistic computed from rle0_block_means, so cells
whose residual is not stable across the eight blocks fade out.

Under-supported rows are masked.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as mplcm
from matplotlib.colors import TwoSlopeNorm

_here = os.path.dirname(os.path.abspath(__file__))

N_ANALYTIC = 4096
MIN_V2_SUPPORT = 8
BLOCKS = 8


# ── Load substrate ──────────────────────────────────────────────────

cache = np.load(os.path.join(_here, 'tree_signatures.npz'))
ns = cache['ns']
v2 = cache['v2']
odd_part = cache['odd_part']
mean_rle0 = cache['mean_rle0']
block_means = cache['rle0_block_means']    # (N, BLOCKS)

assert int(ns[-1]) == N_ANALYTIC, f"expected ns up to {N_ANALYTIC}, got {ns[-1]}"


# ── Grid coordinates: (v_2 row, odd_part rank column) ───────────────

odds = np.arange(1, N_ANALYTIC + 1, 2, dtype=np.int64)
N_ODDS = len(odds)
odd_rank = np.full(N_ANALYTIC + 1, -1, dtype=np.int64)
for i, m in enumerate(odds):
    odd_rank[m] = i

V2_MAX = int(v2.max())
raw_residual = np.full((V2_MAX + 1, N_ODDS), np.nan, dtype=np.float64)
zres = np.full((V2_MAX + 1, N_ODDS), np.nan, dtype=np.float64)
support_mask = np.zeros(V2_MAX + 1, dtype=bool)


# ── Per-row leave-one-out residual + blockwise z ────────────────────

for t in range(V2_MAX + 1):
    sel = (v2 == t)
    cnt = int(sel.sum())
    if cnt < MIN_V2_SUPPORT:
        continue
    support_mask[t] = True

    # Raw residual: leave-one-out within-depth mean
    sum_t = mean_rle0[sel].sum()
    loo_mean = (sum_t - mean_rle0[sel]) / (cnt - 1)
    res_t = mean_rle0[sel] - loo_mean

    # Blockwise leave-one-out residuals -> per-monoid z
    block_t = block_means[sel]                      # (cnt, BLOCKS)
    block_sum = block_t.sum(axis=0)                 # (BLOCKS,)
    loo_block = (block_sum[None, :] - block_t) / (cnt - 1)
    block_residual = block_t - loo_block            # (cnt, BLOCKS)

    res_mean = block_residual.mean(axis=1)
    res_std = block_residual.std(axis=1, ddof=1)
    sem = res_std / np.sqrt(BLOCKS)
    z = np.where(sem > 0, res_mean / sem, 0.0)

    odds_in_t = odd_part[sel]
    cols = odd_rank[odds_in_t]
    raw_residual[t, cols] = res_t
    zres[t, cols] = z


# ── Build RGBA image: color = residual, alpha = |z| ─────────────────
# Render the full V2_MAX+1 rows so under-supported depths stay
# explicitly visible as a neutral mask, not silently dropped.

img = raw_residual                                   # (V2_MAX+1, N_ODDS)
zimg = zres

finite_vals = img[np.isfinite(img)]
if finite_vals.size:
    lim = float(np.percentile(np.abs(finite_vals), 98)) or 1.0
else:
    lim = 1.0
norm = TwoSlopeNorm(vcenter=0.0, vmin=-lim, vmax=lim)
cmap = plt.get_cmap('RdBu_r')

finite_mask = np.isfinite(img) & np.isfinite(zimg)
abs_z = np.where(finite_mask, np.abs(zimg), 0.0)
# |z|<=1 -> faint (0.18), |z|>=4 -> opaque (1.00)
z_clip = np.clip((abs_z - 1.0) / 3.0, 0.0, 1.0)
alpha = np.where(finite_mask, 0.18 + 0.82 * z_clip, 0.0)

img_for_color = np.where(finite_mask, img, 0.0)
rgba = cmap(norm(img_for_color))
rgba[..., 3] = alpha

# Repaint under-supported rows in a flat neutral grey wherever a monoid
# actually sits. The cells stay distinguishable from the empty
# background but carry no diverging-residual color.
NEUTRAL = (0.42, 0.42, 0.42, 0.55)
for t in range(V2_MAX + 1):
    if support_mask[t]:
        continue
    sel = (v2 == t)
    if not sel.any():
        continue
    cols = odd_rank[odd_part[sel]]
    rgba[t, cols] = NEUTRAL


# ── Plot ────────────────────────────────────────────────────────────

n_rows = V2_MAX + 1
fig_height = max(4.6, 0.42 * n_rows + 1.2)
fig, ax = plt.subplots(figsize=(14, fig_height), facecolor='#0a0a0a')
ax.set_facecolor('#0a0a0a')
ax.imshow(rgba, aspect='auto', interpolation='nearest', origin='upper',
          extent=(-0.5, N_ODDS - 0.5, n_rows - 0.5, -0.5))

ax.set_yticks(range(n_rows))
yticklabels = []
for t in range(n_rows):
    cnt = int((v2 == t).sum())
    if support_mask[t]:
        yticklabels.append(f"v₂={t}")
    else:
        yticklabels.append(f"v₂={t}  (n={cnt}, under-supported)")
ax.set_yticklabels(yticklabels)
ax.set_xlabel('rank of odd part m', color='white', fontsize=11)
ax.set_title(
    f'V3 — depth residual of mean_rle0  '
    f'(N_analytic = {N_ANALYTIC}, MIN_V2_SUPPORT = {MIN_V2_SUPPORT}, '
    f'cell α = |z_res|)',
    color='white', fontsize=12, pad=12)
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('white')

sm = mplcm.ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])
cb = plt.colorbar(sm, ax=ax, fraction=0.025, pad=0.02)
cb.set_label('mean_rle0 − within-depth leave-one-out mean',
             color='white')
cb.ax.yaxis.set_tick_params(color='white')
plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color='white')

plt.tight_layout()
out = os.path.join(_here, 'residual_map.png')
plt.savefig(out, dpi=200, facecolor='#0a0a0a')
print(f"Wrote {out}")


# ── Numerical summary ──────────────────────────────────────────────

print("\n=== V3 row summary ===")
print(f"{'v_2':>4} {'n':>6} {'|res| mean':>11} {'|res| max':>11} "
      f"{'|z| mean':>9} {'|z| max':>9}")
print('-' * 56)
for t in range(V2_MAX + 1):
    sel = (v2 == t)
    cnt = int(sel.sum())
    flag = '' if support_mask[t] else '  (under-supported)'
    if cnt == 0:
        continue
    row_res = raw_residual[t]
    row_z = zres[t]
    finite = np.isfinite(row_res)
    if finite.any():
        ar = np.abs(row_res[finite])
        az = np.abs(row_z[finite])
        print(f"{t:>4} {cnt:>6} {ar.mean():>11.4f} {ar.max():>11.4f} "
              f"{az.mean():>9.2f} {az.max():>9.2f}{flag}")
    else:
        print(f"{t:>4} {cnt:>6} {'—':>11} {'—':>11} {'—':>9} {'—':>9}{flag}")
