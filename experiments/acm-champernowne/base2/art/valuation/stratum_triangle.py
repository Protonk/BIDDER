"""
stratum_triangle.py — Variant B: triangular layout colored by V3 residual.

Vertical axis is v_2, growing downward from v_2=0 at the top. Each row is
centred horizontally and has width proportional to its stratum size, so
row v_2=0 (2048 monoids) is the widest and each successive row is
half as wide. Cells inside a row are placed at evenly-spaced positions
in order of their odd part. The result is a sharp downward-narrowing
pyramid that mirrors the actual stratum structure of the data.

Color is the V3 residual on a diverging scale; alpha is driven by
|z_res| through a sigmoid centred at |z|=2. Dots only.

Reads ../../forest/valuation/tree_signatures.npz and rederives the
residual + z_res locally, the same way residual_map.py does.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as mplcm
from matplotlib.colors import TwoSlopeNorm

_here = os.path.dirname(os.path.abspath(__file__))
_cache_path = os.path.join(
    _here, '..', '..', 'forest', 'valuation', 'tree_signatures.npz'
)


# ── Constants ────────────────────────────────────────────────────────

MIN_V2_SUPPORT = 8
BLOCKS = 8

TOP_WIDTH = 2.0           # row v_2=0 spans [-1, +1]
ROW_HEIGHT = 0.20         # vertical spacing between rows


# ── Load cache and rederive residual + z_res ────────────────────────

cache = np.load(_cache_path)
ns = cache['ns']
v2 = cache['v2']
odd_part = cache['odd_part']
mean_rle0 = cache['mean_rle0']
block_means = cache['rle0_block_means']

V2_MAX = int(v2.max())
res_by_n = np.full(len(ns), np.nan, dtype=np.float64)
z_by_n = np.full(len(ns), np.nan, dtype=np.float64)
support_mask = np.zeros(V2_MAX + 1, dtype=bool)

for t in range(V2_MAX + 1):
    sel = (v2 == t)
    cnt = int(sel.sum())
    if cnt < MIN_V2_SUPPORT:
        continue
    support_mask[t] = True

    sum_t = mean_rle0[sel].sum()
    loo_mean = (sum_t - mean_rle0[sel]) / (cnt - 1)
    res_by_n[sel] = mean_rle0[sel] - loo_mean

    bt = block_means[sel]
    bsum = bt.sum(axis=0)
    loo_block = (bsum[None, :] - bt) / (cnt - 1)
    bres = bt - loo_block
    rmean = bres.mean(axis=1)
    rstd = bres.std(axis=1, ddof=1)
    sem = rstd / np.sqrt(BLOCKS)
    z_by_n[sel] = np.where(sem > 0, rmean / sem, 0.0)


# ── Triangular coordinates ──────────────────────────────────────────

top_count = int((v2 == 0).sum())
xs = np.zeros(len(ns), dtype=np.float64)
ys = np.zeros(len(ns), dtype=np.float64)

for t in range(V2_MAX + 1):
    sel_idx = np.where(v2 == t)[0]
    cnt = len(sel_idx)
    if cnt == 0:
        continue
    # Order columns by odd_part ascending so m=1 lands at the leftmost edge
    order = np.argsort(odd_part[sel_idx])
    sorted_idx = sel_idx[order]
    row_width = TOP_WIDTH * (cnt / top_count)
    if cnt > 1:
        positions = np.linspace(-row_width / 2, row_width / 2, cnt)
    else:
        positions = np.array([0.0])
    xs[sorted_idx] = positions
    ys[sorted_idx] = -t * ROW_HEIGHT


# ── Diverging norm + sigmoid alpha ──────────────────────────────────

finite_res = res_by_n[np.isfinite(res_by_n)]
lim = float(np.percentile(np.abs(finite_res), 98)) or 1.0
norm = TwoSlopeNorm(vcenter=0.0, vmin=-lim, vmax=lim)
cmap = plt.get_cmap('RdBu_r')


def alpha_curve(z):
    """Sigmoid centred at |z|=2 with steepness 1.5."""
    az = np.abs(z)
    return 1.0 / (1.0 + np.exp(-(az - 2.0) * 1.5))


# ── Render ──────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(9, 11), facecolor='#0a0a0a')
ax.set_facecolor('#0a0a0a')

v2_int = v2.astype(np.int64)
under = ~support_mask[v2_int]
if under.any():
    ax.scatter(
        xs[under], ys[under],
        c='#555555', s=8, alpha=0.30,
        edgecolor='none', zorder=2,
    )

sup_finite = (~under) & np.isfinite(res_by_n)
faint = sup_finite & (np.abs(z_by_n) < 1.5)
bright = sup_finite & (np.abs(z_by_n) >= 1.5)

for stage_mask, base_size, zorder in [(faint, 9, 3), (bright, 22, 4)]:
    if not stage_mask.any():
        continue
    rgba = cmap(norm(res_by_n[stage_mask]))
    rgba[:, 3] = alpha_curve(z_by_n[stage_mask])
    ax.scatter(
        xs[stage_mask], ys[stage_mask],
        c=rgba, s=base_size,
        edgecolor='none', zorder=zorder,
    )

ax.set_aspect('equal')
ax.axis('off')
ax.set_title(
    'Stratum Triangle — V3 residual on the depth-stratum pyramid',
    color='white', fontsize=13, pad=14,
)

sm = mplcm.ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])
cb = plt.colorbar(sm, ax=ax, fraction=0.03, pad=0.04)
cb.set_label('mean_rle0 − within-depth LOO mean', color='white')
cb.ax.yaxis.set_tick_params(color='white')
plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color='white')

plt.tight_layout()
out = os.path.join(_here, 'stratum_triangle.png')
plt.savefig(out, dpi=200, facecolor='#0a0a0a')
print(f"Wrote {out}")
print(f"  {len(ns)} monoids; "
      f"{int(under.sum())} under-supported (grey); "
      f"{int(bright.sum())} bright (|z|>=1.5); "
      f"{int(faint.sum())} faint (|z|<1.5)")
