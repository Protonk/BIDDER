"""
ECHO CATHEDRAL — geometric architecture of the K-decade echoes.

Each detected peak in the survivor mean-digit-length bias becomes
a column. log K = position. amplitude = height. n_0 = aisle.
Decade gridlines = floors. Arches = colonnade between consecutive
echoes within each aisle. The same architectural element repeats
at every base-10 decade with geometric amplitude decay (~0.80
per echo).
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch

# (n_0, K_peak, amplitude_pct) — from echo_test.py / echo_extend.py
peaks_data = [
    (2,    160, 2.678), (2,   1640, 2.130), (2,  16000, 1.751), (2, 160000, 1.464),
    (3,    160, 3.681), (3,   1640, 2.865), (3,  16000, 2.341), (3, 160000, 1.964),
    (5,    140, 3.243), (5,   1370, 2.135), (5,  14000, 1.785), (5, 140000, 1.494),
    (8,    110, 2.445), (8,    980, 1.633), (8,  10000, 1.306), (8, 100000, 1.092),
    (12,    90, 1.133), (12,   720, 1.014), (12,  7500, 0.697), (12,  75000, 0.587),
]

aisle_map = {2: 0, 3: 1, 5: 2, 8: 3, 12: 4}
N_AISLES = 5
LK_MIN, LK_MAX = 1.65, 5.55

# Isometric projection — strong depth angle for cathedral feel.
DEPTH_DX = -1.55
DEPTH_DY = +0.95
LK_SCALE = 3.2
HEIGHT_SCALE = 2.1


def project(lk, depth, h):
    sx = (lk - LK_MIN) * LK_SCALE + depth * DEPTH_DX
    sy = h * HEIGHT_SCALE + depth * DEPTH_DY
    return sx, sy


fig, ax = plt.subplots(figsize=(16, 11))
fig.patch.set_facecolor('#040404')
ax.set_facecolor('#040404')
ax.set_aspect('equal')

# Floor outline (subtle parallelogram).
fc = [project(LK_MIN - 0.20, -0.6, 0),
      project(LK_MAX + 0.20, -0.6, 0),
      project(LK_MAX + 0.20, N_AISLES - 1 + 0.6, 0),
      project(LK_MIN - 0.20, N_AISLES - 1 + 0.6, 0)]
fxs = [p[0] for p in fc] + [fc[0][0]]
fys = [p[1] for p in fc] + [fc[0][1]]
ax.plot(fxs, fys, color='#3a3a3a', linewidth=0.5, alpha=0.7)

# Decade gridlines on the floor — running back through aisles.
for d_log in [2, 3, 4, 5]:
    p_front = project(d_log, -0.6, 0)
    p_back = project(d_log, N_AISLES - 1 + 0.6, 0)
    ax.plot([p_front[0], p_back[0]], [p_front[1], p_back[1]],
            color='#666', linewidth=0.7, alpha=0.7)
    # Decade label — placed below the front aisle.
    p_label = project(d_log, 0, -0.4)
    ax.text(p_label[0], p_label[1], f'$10^{d_log}$',
            fontsize=14, color='#bbb',
            ha='center', va='top', family='serif')

# Aisle floor lines + n_0 labels (placed on the left margin so
# they don't get hidden by the receding columns).
for n0, depth in aisle_map.items():
    p_left = project(LK_MIN - 0.15, depth, 0)
    p_right = project(LK_MAX + 0.15, depth, 0)
    ax.plot([p_left[0], p_right[0]], [p_left[1], p_right[1]],
            color='#555', linewidth=0.55, alpha=0.65)
    p_label = project(LK_MIN - 0.55, depth, 0)
    ax.text(p_label[0], p_label[1], f'n₀ = {n0}',
            fontsize=11, color='#bbb',
            ha='right', va='center', family='serif')


def draw_column(ax, lk, depth, height, fade=1.0):
    """Five-piece column: plinth, base, shaft, capital, abacus."""
    edges = [(0, 1), (1, 2), (2, 3), (3, 0),
             (4, 5), (5, 6), (6, 7), (7, 4),
             (0, 4), (1, 5), (2, 6), (3, 7)]

    w = 0.06       # shaft half-width
    d = 0.22       # shaft half-depth
    plinth_h = 0.05
    plinth_w = w * 1.65
    plinth_d = d * 1.55
    base_h = 0.04
    base_w = w * 1.45
    base_d = d * 1.4
    cap_h = 0.06 + 0.018 * height
    cap_w = w * 1.5
    cap_d = d * 1.45
    abacus_h = 0.05
    abacus_w = w * 1.7
    abacus_d = d * 1.55

    def cuboid_corners(x_half, d_half, z_lo, z_hi):
        return [
            (lk - x_half, depth - d_half, z_lo),
            (lk + x_half, depth - d_half, z_lo),
            (lk + x_half, depth + d_half, z_lo),
            (lk - x_half, depth + d_half, z_lo),
            (lk - x_half, depth - d_half, z_hi),
            (lk + x_half, depth - d_half, z_hi),
            (lk + x_half, depth + d_half, z_hi),
            (lk - x_half, depth + d_half, z_hi),
        ]

    pieces = []
    z = 0
    pieces.append((plinth_w, plinth_d, z, z + plinth_h, 0.85))
    z += plinth_h
    pieces.append((base_w, base_d, z, z + base_h, 0.75))
    z += base_h
    shaft_top = height - cap_h - abacus_h
    pieces.append((w, d, z, shaft_top, 1.15))
    z = shaft_top
    pieces.append((cap_w, cap_d, z, z + cap_h, 0.75))
    z += cap_h
    pieces.append((abacus_w, abacus_d, z, z + abacus_h, 0.85))

    for x_half, d_half, lo, hi, lw_factor in pieces:
        cs = cuboid_corners(x_half, d_half, lo, hi)
        ps = [project(*c) for c in cs]
        for a, b in edges:
            ax.plot([ps[a][0], ps[b][0]], [ps[a][1], ps[b][1]],
                    color='white', linewidth=lw_factor * fade,
                    alpha=fade * 0.95)

    # Subtle fluting: a single internal vertical on the shaft front face.
    flute_lo = base_h + plinth_h
    flute_hi = shaft_top
    p_lo = project(lk, depth - d, flute_lo)
    p_hi = project(lk, depth - d, flute_hi)
    ax.plot([p_lo[0], p_hi[0]], [p_lo[1], p_hi[1]],
            color='white', linewidth=0.35 * fade, alpha=fade * 0.5)


# Draw columns back-to-front for proper layering.
peaks_sorted = sorted(peaks_data, key=lambda p: -aisle_map[p[0]])
for n0, K, amp in peaks_sorted:
    lk = np.log10(K)
    depth = aisle_map[n0]
    fade = 1.0 - 0.18 * (depth / (N_AISLES - 1))
    draw_column(ax, lk, depth, amp, fade=fade)


def draw_arch(ax, p1, p2, fade=1.0):
    """Round-arch via two cubic-Bezier halves for a fuller curve."""
    rise = abs(p1[0] - p2[0]) * 0.42 + 0.20
    midx = (p1[0] + p2[0]) / 2
    midy = max(p1[1], p2[1]) + rise
    apex = (midx, midy)
    span = abs(p2[0] - p1[0])
    # Control points pulled toward apex for round-arch look.
    c1 = (p1[0] + span * 0.05, p1[1] + rise * 0.65)
    c2 = (midx - span * 0.20, midy)
    c3 = (midx + span * 0.20, midy)
    c4 = (p2[0] - span * 0.05, p2[1] + rise * 0.65)
    verts = [p1, c1, c2, apex, c3, c4, p2]
    codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.CURVE4, Path.CURVE4, Path.CURVE4]
    path = Path(verts, codes)
    patch = PathPatch(path, fill=False,
                      edgecolor=(1, 1, 1, fade * 0.62),
                      linewidth=0.85)
    ax.add_patch(patch)


# Arches connecting consecutive column tops within each aisle.
for n0 in sorted(aisle_map.keys(), key=lambda n: -aisle_map[n]):
    depth = aisle_map[n0]
    columns = sorted([(np.log10(K), amp)
                      for n, K, amp in peaks_data if n == n0])
    fade = 1.0 - 0.18 * (depth / (N_AISLES - 1))
    for i in range(len(columns) - 1):
        lk1, amp1 = columns[i]
        lk2, amp2 = columns[i + 1]
        p1 = project(lk1, depth, amp1)
        p2 = project(lk2, depth, amp2)
        draw_arch(ax, p1, p2, fade=fade)

# Title in lower-right.
fig.text(0.95, 0.07, 'ECHO CATHEDRAL', color='#ddd',
         fontsize=14, ha='right', va='bottom',
         family='serif', weight='bold')
fig.text(0.95, 0.055,
         'K-decade echoes of the survivor mean-dlen bias',
         color='#777', fontsize=9, ha='right', va='top',
         style='italic', family='serif')
fig.text(0.95, 0.038,
         'columns: peak amplitude   ·   floors: K decades   ·   '
         'aisles: n₀',
         color='#555', fontsize=8, ha='right', va='top',
         family='serif')

ax.axis('off')
plt.savefig('echo_cathedral.png', dpi=200, facecolor='#040404',
            bbox_inches='tight')
print("-> echo_cathedral.png")
