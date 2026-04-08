"""
treefan_rose.py — Variant A: polar treefan colored by the V3 residual.

Each odd m anchors a spiral arm at angular position 2π·rank(m)/num_odds;
the arm winds inward as v_2 grows. m=1 is the longest arm and reaches
the centre. Color is the V3 residual on a diverging scale; alpha is
driven by |z_res| through a sigmoid centred at |z|=2 so that low-
confidence cells fade and high-confidence cells burn. Dots only.

Reads ../../forest/valuation/tree_signatures.npz and rederives the
residual + z_res locally, the same way residual_map.py does.
"""

import os
import math
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


# ── Constants (mirror residual_map.py) ───────────────────────────────

MIN_V2_SUPPORT = 8
BLOCKS = 8

R_RIM = 1.0
R_INNER = 0.04
TWIST = 0.18                # radians per v_2 step


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


# ── Polar coordinates (V2 idiom) ────────────────────────────────────

odds = np.array(sorted(set(int(m) for m in odd_part)), dtype=np.int64)
num_odds = len(odds)
odd_index = {int(m): i for i, m in enumerate(odds)}


def radius_at(t):
    return R_RIM - (R_RIM - R_INNER) * (t / V2_MAX)


thetas = np.zeros(len(ns), dtype=np.float64)
radii = np.zeros(len(ns), dtype=np.float64)
for i in range(len(ns)):
    m = int(odd_part[i])
    t = int(v2[i])
    theta0 = 2.0 * math.pi * odd_index[m] / num_odds
    thetas[i] = theta0 + TWIST * t
    radii[i] = radius_at(t)


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

fig, ax = plt.subplots(
    figsize=(11, 11),
    subplot_kw=dict(projection='polar'),
    facecolor='#0a0a0a',
)
ax.set_facecolor('#0a0a0a')

# Pass 1: under-supported nodes — neutral grey context, no chroma
v2_int = v2.astype(np.int64)
under = ~support_mask[v2_int]
if under.any():
    ax.scatter(
        thetas[under], radii[under],
        c='#555555', s=8, alpha=0.30,
        edgecolor='none', zorder=2,
    )

# Pass 2: faint cells (|z| < 1.5) — small dots, low alpha
sup_finite = (~under) & np.isfinite(res_by_n)
faint = sup_finite & (np.abs(z_by_n) < 1.5)
bright = sup_finite & (np.abs(z_by_n) >= 1.5)

for stage_mask, base_size, zorder in [(faint, 9, 3), (bright, 22, 4)]:
    if not stage_mask.any():
        continue
    rgba = cmap(norm(res_by_n[stage_mask]))
    rgba[:, 3] = alpha_curve(z_by_n[stage_mask])
    ax.scatter(
        thetas[stage_mask], radii[stage_mask],
        c=rgba, s=base_size,
        edgecolor='none', zorder=zorder,
    )

ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)
ax.set_rticks([])
ax.set_xticks([])
ax.set_ylim(0, R_RIM * 1.05)
ax.spines['polar'].set_color('#222222')
ax.grid(False)

ax.set_title(
    'Treefan Rose — V3 residual on the polar treefan',
    color='white', fontsize=13, pad=18,
)

sm = mplcm.ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])
cb = plt.colorbar(sm, ax=ax, fraction=0.03, pad=0.06)
cb.set_label('mean_rle0 − within-depth LOO mean', color='white')
cb.ax.yaxis.set_tick_params(color='white')
plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color='white')

plt.tight_layout()
out = os.path.join(_here, 'treefan_rose.png')
plt.savefig(out, dpi=200, facecolor='#0a0a0a')
print(f"Wrote {out}")
print(f"  {len(ns)} monoids; "
      f"{int(under.sum())} under-supported (grey); "
      f"{int(bright.sum())} bright (|z|>=1.5); "
      f"{int(faint.sum())} faint (|z|<1.5)")
