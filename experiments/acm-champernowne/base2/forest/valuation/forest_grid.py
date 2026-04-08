"""
forest_grid.py — V1: literal Cartesian forest of odd-rooted trunks.

Each odd m in 1..N_RENDER is a vertical trunk. Monoid n = m * 2^t
sits at (rank(m), -t) and is colored by mean_rle0. The leftmost
trunk (m = 1) is the powers-of-2 spine.

Reads only tree_signatures.npz.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

_here = os.path.dirname(os.path.abspath(__file__))

N_RENDER = 512


# ── Load substrate ──────────────────────────────────────────────────

cache = np.load(os.path.join(_here, 'tree_signatures.npz'))
ns = cache['ns']
v2 = cache['v2']
odd_part = cache['odd_part']
mean_rle0 = cache['mean_rle0']

mask = ns <= N_RENDER
ns_r = ns[mask]
v2_r = v2[mask]
odd_r = odd_part[mask]
rle0_r = mean_rle0[mask]


# ── Coordinates ─────────────────────────────────────────────────────

odds = np.array(sorted(set(int(m) for m in odd_r)), dtype=np.int64)
num_odds = len(odds)
rank_of = {int(m): i for i, m in enumerate(odds)}

xs = np.array([rank_of[int(m)] for m in odd_r], dtype=np.int64)
ys = -v2_r.astype(np.float64)


# ── Plot ────────────────────────────────────────────────────────────

vmin = float(np.percentile(rle0_r, 2))
vmax = float(np.percentile(rle0_r, 98))

fig, ax = plt.subplots(figsize=(14, 7), facecolor='#0a0a0a')
ax.set_facecolor('#0a0a0a')

# Faint trunk segments — drawn first so dots sit on top
for m in odds:
    sel = odd_r == m
    if int(sel.sum()) < 2:
        continue
    xs_m = xs[sel]
    ys_m = ys[sel]
    order = np.argsort(-ys_m)  # crown to base
    ax.plot(xs_m[order], ys_m[order],
            color='#88d8b0', lw=0.4, alpha=0.18, zorder=1)

sc = ax.scatter(xs, ys, c=rle0_r, cmap='magma_r',
                vmin=vmin, vmax=vmax,
                s=22, edgecolor='none', zorder=2)

ax.set_xlabel('rank of odd part m  (m = 1 leftmost)',
              color='white', fontsize=11)
ax.set_ylabel('−v₂(n)  (depth grows downward)',
              color='white', fontsize=11)
ax.set_title(f'V1 — Valuation Forest  '
             f'(N_render = {N_RENDER}, color = mean zero-run length)',
             color='white', fontsize=13, pad=12)
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('white')

cb = plt.colorbar(sc, ax=ax, fraction=0.025, pad=0.02)
cb.set_label('mean zero-run length', color='white')
cb.ax.yaxis.set_tick_params(color='white')
plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color='white')

plt.tight_layout()
out = os.path.join(_here, 'forest_grid.png')
plt.savefig(out, dpi=200, facecolor='#0a0a0a')
print(f"Wrote {out}")
print(f"  {num_odds} odd-rooted trunks, "
      f"max trunk length = {int(v2_r.max()) + 1} nodes (m = 1 spine)")
