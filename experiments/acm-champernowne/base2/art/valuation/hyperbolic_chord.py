"""
hyperbolic_chord.py — Variant D: faux-hyperbolic chord layout.

Each odd-rooted doubling chain is drawn as a circular arc inside the
unit disk, starting at a fixed focal point on the boundary at (1, 0)
and bending back to a different point on the boundary determined by
the chain's rank. The arc is the unique circle through (1, 0) and
the chain's bend-back point that is perpendicular to the unit circle
at both endpoints — i.e., the actual Poincaré-disk geodesic between
those two ideal points. We use it as a layout primitive, not as a
claim that the data lives in hyperbolic space; the transformation is
honest in its geometry but for effect in its application.

Long chains (m = 1, 3, 5, ...) get angular positions clustered near
the antipode (β = π), so their arcs sweep across most of the disk.
Shorter chains spiral outward toward the focal, so their arcs hug
the focal side. Within each arc, chain members are placed at
fractions (V2_SUP_MAX − v_2) / V2_SUP_MAX, so deeper members sit
closer to the focal. V3 hot cells are drawn on top.

Reads ../../forest/valuation/tree_signatures.npz.
"""

import os
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import TwoSlopeNorm

_here = os.path.dirname(os.path.abspath(__file__))
_cache_path = os.path.join(
    _here, '..', '..', 'forest', 'valuation', 'tree_signatures.npz'
)


# ── Constants ────────────────────────────────────────────────────────

MIN_V2_SUPPORT = 8
BLOCKS = 8

MIN_CHAIN_LEN = 5       # only draw chains with this many supported nodes
DOT_THRESHOLD = 1.5     # only draw hot cells with |z_res| >= this
ANGULAR_GAP = 0.05      # fraction of 2π reserved as a gap around the focal

BG = '#f8f8f5'
LINE_COLOR = '#1a1a1a'
LINE_LW = 0.55
LINE_ALPHA = 0.32
DISK_COLOR = '#888888'

ARC_SAMPLES = 120


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

V2_SUP_MAX = int(np.where(support_mask)[0].max())


# ── Build per-chain data ────────────────────────────────────────────

n_to_v2 = {int(ns[i]): int(v2[i]) for i in range(len(ns))}
n_idx = {int(ns[i]): i for i in range(len(ns))}

odds = sorted(set(int(m) for m in odd_part))
chains = []     # list of (m, [(n, v_2), ...]) restricted to supported rows
for m in odds:
    members = []
    n = m
    while n in n_to_v2:
        if support_mask[n_to_v2[n]]:
            members.append((n, n_to_v2[n]))
        n *= 2
    if len(members) >= MIN_CHAIN_LEN:
        chains.append((m, members))

# Sort chains by chain length descending so longest are first.
# Ties (same length) broken by m so the ordering is deterministic.
chains.sort(key=lambda c: (-len(c[1]), c[0]))
n_chains = len(chains)


# ── Assign β: longest chain at antipode π, others alternating outward ─

def compute_betas(n):
    if n == 0:
        return []
    if n == 1:
        return [math.pi]
    available = 2 * math.pi * (1 - ANGULAR_GAP)
    step = available / n
    betas = []
    for i in range(n):
        if i == 0:
            beta = math.pi
        else:
            half = (i + 1) // 2
            sign = -1 if i % 2 == 1 else 1
            beta = math.pi + sign * half * step
        betas.append(beta)
    return betas


betas = compute_betas(n_chains)


# ── Geodesic helpers (Poincaré disk model) ──────────────────────────

def geodesic_polyline(beta, f_start, f_end, n_samples=ARC_SAMPLES):
    """Polyline along the Poincaré-disk geodesic from F=(1,0) to
    P=(cos β, sin β), with f=0 at F and f=1 at P. The geodesic is the
    unique circle through F and P that is perpendicular to the unit
    circle at both endpoints (the orthogonal circle), i.e., the
    standard hyperbolic geodesic between two ideal points."""
    if abs(math.sin(beta)) < 1e-9:
        # β ≈ 0 or β ≈ π: the geodesic is a diameter
        fs = np.linspace(f_start, f_end, n_samples)
        return 1.0 - 2.0 * fs, np.zeros_like(fs)

    # Orthogonal circle: C·F = 1 and C·P = 1 with F = (1, 0).
    # C·F = 1 ⇒ Cx = 1.
    # C·P = Cx cos β + Cy sin β = 1 ⇒ Cy = (1 − cos β) / sin β = tan(β/2).
    cx = 1.0
    cy = math.tan(beta / 2.0)
    R = abs(cy)

    # Angles from C to F and P
    angle_F = math.atan2(0.0 - cy, 1.0 - cx)              # atan2(-cy, 0)
    angle_P = math.atan2(math.sin(beta) - cy,
                         math.cos(beta) - cx)

    # Take the shorter arc (inside the disk)
    delta = angle_P - angle_F
    while delta > math.pi:
        delta -= 2 * math.pi
    while delta < -math.pi:
        delta += 2 * math.pi

    fs = np.linspace(f_start, f_end, n_samples)
    angles = angle_F + fs * delta
    xs_arc = cx + R * np.cos(angles)
    ys_arc = cy + R * np.sin(angles)
    return xs_arc, ys_arc


def geodesic_point(beta, fraction):
    xs_arc, ys_arc = geodesic_polyline(beta, fraction, fraction, n_samples=1)
    return float(xs_arc[0]), float(ys_arc[0])


# ── Place chain members and build arc polylines ────────────────────

xs = np.zeros(len(ns), dtype=np.float64)
ys = np.zeros(len(ns), dtype=np.float64)
n_to_xy = {}
arc_polylines = []

for ci, (m, members) in enumerate(chains):
    beta = betas[ci]
    max_v2_in_chain = max(t for (_, t) in members)
    f_start = (V2_SUP_MAX - max_v2_in_chain) / V2_SUP_MAX
    f_end = 1.0

    arc_xs, arc_ys = geodesic_polyline(beta, f_start, f_end)
    arc_polylines.append((arc_xs, arc_ys))

    for (n, t) in members:
        fraction = (V2_SUP_MAX - t) / V2_SUP_MAX
        x, y = geodesic_point(beta, fraction)
        xs[n_idx[n]] = x
        ys[n_idx[n]] = y
        n_to_xy[n] = (x, y)


# ── Bright cells ────────────────────────────────────────────────────

v2_int = v2.astype(np.int64)
under = ~support_mask[v2_int]
sup_finite = (~under) & np.isfinite(res_by_n)
in_chain = np.array([int(ns[i]) in n_to_xy for i in range(len(ns))])
bright = sup_finite & (np.abs(z_by_n) >= DOT_THRESHOLD) & in_chain

finite_res = res_by_n[np.isfinite(res_by_n)]
lim = float(np.percentile(np.abs(finite_res), 98)) or 1.0
norm = TwoSlopeNorm(vcenter=0.0, vmin=-lim, vmax=lim)
cmap = plt.get_cmap('RdBu_r')


# ── Render ──────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(11, 11), facecolor=BG)
ax.set_facecolor(BG)

disk = mpatches.Circle((0, 0), 1.0,
                       fill=False, edgecolor=DISK_COLOR, lw=0.6,
                       zorder=1)
ax.add_patch(disk)

for (arc_xs, arc_ys) in arc_polylines:
    ax.plot(arc_xs, arc_ys,
            color=LINE_COLOR, lw=LINE_LW, alpha=LINE_ALPHA, zorder=2)

if bright.any():
    rgba = cmap(norm(res_by_n[bright]))
    rgba[:, 3] = 0.95
    ax.scatter(xs[bright], ys[bright],
               c=rgba, s=60, edgecolor='none', zorder=4)

ax.set_aspect('equal')
ax.axis('off')
ax.set_xlim(-1.05, 1.05)
ax.set_ylim(-1.05, 1.05)
ax.set_title(
    'Hyperbolic Chord — chains as faux-geodesic arcs',
    color='#222222', fontsize=13, pad=10,
)

plt.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.02)
out = os.path.join(_here, 'hyperbolic_chord.png')
plt.savefig(out, dpi=200, facecolor=BG)
print(f"Wrote {out}")
print(f"  {n_chains} chains drawn (length >= {MIN_CHAIN_LEN}); "
      f"{int(bright.sum())} hot cells")
