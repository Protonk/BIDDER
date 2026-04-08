"""
stratum_fan.py — Variant C: stratum triangle with doubling-chain skeleton.

Same triangular geometry as stratum_triangle.py, but with the m=1 chain
running down the central axis (smallest odd part placed at the centre
of each row, alternating outward), and with each odd-rooted doubling
chain drawn as a thin dark polyline on a white background. The V3
residual hot cells are placed on top as colored dots.

Reads ../../forest/valuation/tree_signatures.npz and rederives the
residual + z_res locally, the same way residual_map.py does.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

_here = os.path.dirname(os.path.abspath(__file__))
_cache_path = os.path.join(
    _here, '..', '..', 'forest', 'valuation', 'tree_signatures.npz'
)


# ── Constants ────────────────────────────────────────────────────────

MIN_V2_SUPPORT = 8
BLOCKS = 8

TOP_WIDTH = 2.0
ROW_HEIGHT = 0.22

# Linear (trapezoidal) narrowing instead of strict halving: row width
# decreases linearly from TOP_WIDTH at v_2=0 down to 0 at v_2=V2_MAX.
# This breaks stratum-size honesty, but it gives column spacings that
# grow with depth — which is what makes the chain lines actually fan
# out instead of running parallel.
def row_width_at(t, v2_max):
    return TOP_WIDTH * max(0.0, 1.0 - t / max(v2_max, 1))


# Only draw chains that reach at least this depth (= these many nodes).
# Filtering keeps the line count manageable so individual lines stay
# visible against white.
MIN_CHAIN_LEN = 5

BG = '#f8f8f5'
LINE_COLOR = '#1a1a1a'
LINE_LW = 0.55
LINE_ALPHA = 0.32

DOT_THRESHOLD = 1.5     # only show cells with |z_res| >= this


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


# ── Centered ordering: smallest m at the row's centre, alternating ──

def center_order(cnt):
    """Position indices for items 0..cnt-1, smallest item at the centre
    of a linspace, subsequent items placed alternately to the right and
    left of centre."""
    if cnt <= 1:
        return list(range(cnt))
    middle = (cnt - 1) / 2.0
    return sorted(range(cnt),
                  key=lambda p: (abs(p - middle), -(p - middle)))


# ── Build coordinates ───────────────────────────────────────────────

top_count = int((v2 == 0).sum())
xs = np.zeros(len(ns), dtype=np.float64)
ys = np.zeros(len(ns), dtype=np.float64)
n_to_xy = {}

for t in range(V2_MAX + 1):
    sel_idx = np.where(v2 == t)[0]
    cnt = len(sel_idx)
    if cnt == 0:
        continue
    order = np.argsort(odd_part[sel_idx])
    sorted_idx = sel_idx[order]
    row_width = row_width_at(t, V2_MAX)
    if cnt > 1:
        positions = np.linspace(-row_width / 2, row_width / 2, cnt)
    else:
        positions = np.array([0.0])
    pos_indices = center_order(cnt)
    for i, idx in enumerate(sorted_idx):
        x = float(positions[pos_indices[i]])
        y = -t * ROW_HEIGHT
        xs[idx] = x
        ys[idx] = y
        n_to_xy[int(ns[idx])] = (x, y)


# ── Build doubling-chain polylines (supported rows only) ────────────

n_to_v2 = {int(ns[i]): int(v2[i]) for i in range(len(ns))}

odds = sorted(set(int(m) for m in odd_part))
chain_polylines = []
for m in odds:
    poly = []
    n = m
    while n in n_to_xy:
        if support_mask[n_to_v2[n]]:
            poly.append(n_to_xy[n])
        n *= 2
    if len(poly) >= MIN_CHAIN_LEN:
        chain_polylines.append(poly)


# ── Bright cells ────────────────────────────────────────────────────

v2_int = v2.astype(np.int64)
under = ~support_mask[v2_int]
sup_finite = (~under) & np.isfinite(res_by_n)
bright = sup_finite & (np.abs(z_by_n) >= DOT_THRESHOLD)

finite_res = res_by_n[np.isfinite(res_by_n)]
lim = float(np.percentile(np.abs(finite_res), 98)) or 1.0
norm = TwoSlopeNorm(vcenter=0.0, vmin=-lim, vmax=lim)
cmap = plt.get_cmap('RdBu_r')


# ── Render ──────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(9, 11), facecolor=BG)
ax.set_facecolor(BG)

# Chain skeleton first (background structure)
for poly in chain_polylines:
    xs_p = [p[0] for p in poly]
    ys_p = [p[1] for p in poly]
    ax.plot(xs_p, ys_p,
            color=LINE_COLOR, lw=LINE_LW, alpha=LINE_ALPHA, zorder=2)

# Hot cells on top
if bright.any():
    rgba = cmap(norm(res_by_n[bright]))
    rgba[:, 3] = 0.95
    ax.scatter(xs[bright], ys[bright],
               c=rgba, s=36, edgecolor='none', zorder=4)

# Crop tight to the supported region
v2_supported_max = int(np.where(support_mask)[0].max())
margin = 0.06
ax.set_xlim(-TOP_WIDTH / 2 - margin, TOP_WIDTH / 2 + margin)
ax.set_ylim(-(v2_supported_max + 0.5) * ROW_HEIGHT, ROW_HEIGHT * 0.5)

ax.set_aspect('equal')
ax.axis('off')
ax.set_title(
    'Stratum Fan — chain skeleton + V3 residual hot cells',
    color='#222222', fontsize=13, pad=10,
)

plt.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.02)
out = os.path.join(_here, 'stratum_fan.png')
plt.savefig(out, dpi=200, facecolor=BG)
print(f"Wrote {out}")
print(f"  {len(ns)} monoids; "
      f"{len(chain_polylines)} doubling-chain polylines (supported rows only); "
      f"{int(bright.sum())} hot cells (|z_res| >= {DOT_THRESHOLD})")
