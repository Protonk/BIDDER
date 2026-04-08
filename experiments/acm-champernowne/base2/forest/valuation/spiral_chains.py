"""
spiral_chains.py — V2: polar spiral arms, one per odd-rooted chain.

Each odd m anchors a spiral arm at the outer rim. The arm winds
inward as v_2 increases. The arm for m = 1 is the longest and
spirals deepest into the centre. Outer rim drawn first; inward arms
drawn last so they remain legible through any rim occlusion.

Reads only tree_signatures.npz.
"""

import os
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as mplcm
from matplotlib.colors import Normalize

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


# ── Group monoids into chains by odd part ───────────────────────────

odds = np.array(sorted(set(int(m) for m in odd_r)), dtype=np.int64)
num_odds = len(odds)
odd_index = {int(m): i for i, m in enumerate(odds)}

chains = {int(m): [] for m in odds}
for i in range(len(ns_r)):
    chains[int(odd_r[i])].append(
        (int(ns_r[i]), int(v2_r[i]), float(rle0_r[i]))
    )
for m in chains:
    chains[m].sort(key=lambda t: t[1])

V2_MAX_RENDER = int(v2_r.max())


# ── Polar coordinates ───────────────────────────────────────────────

R_RIM = 1.0
R_INNER = 0.04
TWIST = 0.18  # radians per v_2 step


def radius_at(t):
    if V2_MAX_RENDER == 0:
        return R_RIM
    return R_RIM - (R_RIM - R_INNER) * (t / V2_MAX_RENDER)


def theta_for_odd(m):
    return 2.0 * math.pi * odd_index[int(m)] / num_odds


# ── Plot ────────────────────────────────────────────────────────────

vmin = float(np.percentile(rle0_r, 2))
vmax = float(np.percentile(rle0_r, 98))
cmap = plt.get_cmap('magma_r')

fig, ax = plt.subplots(
    figsize=(10, 10),
    subplot_kw=dict(projection='polar'),
    facecolor='#0a0a0a',
)
ax.set_facecolor('#0a0a0a')

# Pass 1: outer rim (v_2 = 0 nodes)
rim_thetas, rim_rs, rim_cs = [], [], []
for m in odds:
    chain = chains[int(m)]
    if not chain or chain[0][1] != 0:
        continue
    rim_thetas.append(theta_for_odd(m))
    rim_rs.append(R_RIM)
    rim_cs.append(chain[0][2])
ax.scatter(rim_thetas, rim_rs, c=rim_cs, cmap=cmap,
           vmin=vmin, vmax=vmax,
           s=14, edgecolor='none', zorder=2)

# Pass 2: inward arms (v_2 >= 1)
for m in odds:
    chain = chains[int(m)]
    if len(chain) <= 1:
        continue
    theta0 = theta_for_odd(m)
    arm_thetas, arm_rs, arm_cs = [], [], []
    for (n, t, c) in chain:
        if t == 0:
            continue
        arm_thetas.append(theta0 + TWIST * t)
        arm_rs.append(radius_at(t))
        arm_cs.append(c)
    if not arm_thetas:
        continue
    # faint connector from rim through the arm
    ax.plot([theta0] + arm_thetas, [R_RIM] + arm_rs,
            color='#6ec6ff', lw=0.45, alpha=0.22, zorder=3)
    ax.scatter(arm_thetas, arm_rs, c=arm_cs, cmap=cmap,
               vmin=vmin, vmax=vmax,
               s=24, edgecolor='none', zorder=4)

ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)
ax.set_rticks([])
ax.set_xticks([])
ax.set_ylim(0, R_RIM * 1.05)
ax.spines['polar'].set_color('#222222')
ax.grid(False)

ax.set_title(
    f'V2 — spiral chains  '
    f'(N_render = {N_RENDER}, color = mean zero-run length)',
    color='white', fontsize=13, pad=18,
)

sm = mplcm.ScalarMappable(norm=Normalize(vmin=vmin, vmax=vmax), cmap=cmap)
sm.set_array([])
cb = plt.colorbar(sm, ax=ax, fraction=0.04, pad=0.06)
cb.set_label('mean zero-run length', color='white')
cb.ax.yaxis.set_tick_params(color='white')
plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color='white')

plt.tight_layout()
out = os.path.join(_here, 'spiral_chains.png')
plt.savefig(out, dpi=200, facecolor='#0a0a0a')
print(f"Wrote {out}")
print(f"  {num_odds} arms, deepest reaches v_2 = {V2_MAX_RENDER} "
      f"(arm m = 1 is the central vortex)")
