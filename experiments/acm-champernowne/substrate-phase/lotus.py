"""
LUCKY-LOTUS: three polar visualizations of the lucky locus, each
exploring a different conceptual angle but rendering as a lotus flower
under the polar wrap.

  lotus_pond.png      — Observable. All 96 lucky cells as 9-fold
                        rose curves at radius = log(q + 1). Green =
                        Generalised Family E (M_k(n) uniform), magenta
                        = n²-cancellation (M_k(n) varies).

  lotus_alignment.png — Mechanism. The 27 n²-cancellation cells, each
                        rendered as two stacked extras-pattern bumps:
                        outer curve from M_k(n)'s extras (green), inner
                        curve from M_k(n²)'s extras (magenta). The
                        Beatty pattern-alignment manifests as the
                        bumps lining up at identical angular positions.

  lotus_lattice.png   — Parameter space. The 69 Generalised Family E
                        cells as radial petals, length = log(qp + 1),
                        color = d. Petals tile the polar plane;
                        d-classes form rings of varying length.
"""

import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

B = 10
N_MAX = 200
D_MAX = 7
BG = '#070712'

GREEN = '#a8e22d'
MAGENTA = '#ff79c6'

D_COLORS = {
    1: '#3da9c4',
    2: '#5dc8d4',
    3: '#a8e22d',
    4: '#f5e2a3',
    5: '#ffa642',
    6: '#cc66ff',
    7: '#ff79c6',
}


def per_strip_counts(b, n, d):
    W = b**(d - 1)
    n_sq = n * n
    cn, cnsq, ca = [], [], []
    for k in range(1, b):
        lo = k * W
        hi = (k + 1) * W - 1
        c_n = hi // n - (lo - 1) // n
        c_nsq = hi // n_sq - (lo - 1) // n_sq
        cn.append(c_n)
        cnsq.append(c_nsq)
        ca.append(c_n - c_nsq)
    return cn, cnsq, ca


def is_smooth(b, n, d):
    return (b**(d - 1)) % (n * n) == 0


def is_family_e(b, n, d):
    return d >= 2 and b**(d - 1) <= n <= (b**d - 1) // (b - 1)


# Collect lucky cells, split by mechanism.
gfe_cells, n2c_cells = [], []
for d in range(1, D_MAX + 1):
    for n in range(2, N_MAX + 1):
        if is_smooth(B, n, d) or is_family_e(B, n, d):
            continue
        cn, cnsq, ca = per_strip_counts(B, n, d)
        if not all(c == ca[0] for c in ca) or ca[0] == 0:
            continue
        info = {'cn': cn, 'cnsq': cnsq, 'ca': ca, 'q': ca[0]}
        if all(c == cn[0] for c in cn):
            gfe_cells.append((n, d, info))
        else:
            n2c_cells.append((n, d, info))

print(f"Generalised Family E cells: {len(gfe_cells)}")
print(f"n²-cancellation cells:       {len(n2c_cells)}")


def style_polar(ax):
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.spines['polar'].set_visible(False)
    ax.grid(False)


# ============================================================
# LOTUS 1 — POND
# All 96 lucky cells as nested 9-fold roses.
# ============================================================

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

theta = np.linspace(0, 2 * np.pi, 1200)

all_cells = sorted(gfe_cells + n2c_cells, key=lambda c: c[2]['q'])

for i, (n, d, info) in enumerate(all_cells):
    q = info['q']
    r_base = np.log10(q + 1) * 1.6
    # Ripple amplitude tapers from inner to outer for visual depth.
    ripple = 0.13 - 0.06 * (i / max(1, len(all_cells) - 1))
    r = r_base * (1 + ripple * np.cos(9 * theta))
    is_gfe = all(c == info['cn'][0] for c in info['cn'])
    color = GREEN if is_gfe else MAGENTA
    alpha = 0.50 if is_gfe else 0.85
    lw = 0.7 if is_gfe else 1.0
    ax.plot(theta, r, color=color, alpha=alpha, linewidth=lw)

style_polar(ax)
ax.set_rmax(np.log10(max(c[2]['q'] for c in all_cells) + 1) * 2.0)
plt.savefig('lotus_pond.png', dpi=170, facecolor=BG,
            bbox_inches='tight', pad_inches=0.25)
plt.close()
print("→ lotus_pond.png")


# ============================================================
# LOTUS 2 — ALIGNMENT
# n²-cancellation cells grouped by their unique extras pattern:
# each *unique pattern* gets one (cn, cnsq) curve pair. The two
# curves bump at identical θ_k positions because the two patterns
# coincide bit-for-bit (verified 27/27).
# ============================================================

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

theta_pts = np.array([2 * np.pi * k / 9 for k in range(9)])
bump_sigma = 0.20

def bump_curve(theta, extras, base, amp, sigma):
    r = np.full_like(theta, base, dtype=float)
    for k in range(9):
        if extras[k] > 0:
            dt = ((theta - theta_pts[k] + np.pi) % (2 * np.pi)) - np.pi
            r = r + extras[k] * amp * np.exp(-(dt ** 2) / (2 * sigma ** 2))
    return r

# Group cells by the (extras_n) tuple — unique patterns layer cleanly.
pattern_groups = defaultdict(list)
for n, d, info in n2c_cells:
    cn = np.array(info['cn'])
    extras = tuple((cn - cn.min()).tolist())
    pattern_groups[extras].append((n, d, info))

# Sort by the count of extras then lexicographically, so similar
# patterns sit in adjacent rings.
patterns = sorted(pattern_groups.keys(), key=lambda p: (sum(p), p))

n_rings = len(patterns)
for i, pattern in enumerate(patterns):
    extras_n = np.array(pattern, dtype=float)
    # cnsq extras pattern is identical (verified).
    extras_nsq = extras_n.copy()

    r_base = 0.6 + 0.42 * i
    gap = 0.16
    amp = 0.32

    r_outer = bump_curve(theta, extras_n, r_base + gap, amp, bump_sigma)
    r_inner = bump_curve(theta, extras_nsq, r_base - gap, amp, bump_sigma)

    ax.plot(theta, r_outer, color=GREEN, alpha=0.85, linewidth=1.4)
    ax.plot(theta, r_inner, color=MAGENTA, alpha=0.85, linewidth=1.4)
    ax.fill_between(theta, r_inner, r_outer, color='#3a4a55', alpha=0.10)

# Reference ring through theta_pts to anchor angular positions.
for tk in theta_pts:
    ax.plot([tk, tk], [0, 0.6 + 0.42 * (n_rings - 1) + 0.6],
            color='#222230', linewidth=0.4, alpha=0.7, zorder=0)

style_polar(ax)
ax.set_rmax(0.6 + 0.42 * (n_rings - 1) + 0.6)
plt.savefig('lotus_alignment.png', dpi=170, facecolor=BG,
            bbox_inches='tight', pad_inches=0.25)
plt.close()
print(f"→ lotus_alignment.png ({n_rings} unique patterns)")


# ============================================================
# LOTUS 3 — LATTICE
# Generalised Family E cells as a tiered flower: each d-class is
# a concentric ring of petals, petals within a ring evenly spaced,
# petal length modulated by log10(qp + 1) within the d-tier.
# ============================================================

# Group cells by d.
by_d = defaultdict(list)
for n, d, info in gfe_cells:
    by_d[d].append((info['cn'][0], n, info))

ds = sorted(by_d.keys())

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

petal_s = np.linspace(0, np.pi, 200)

# Each d-tier is a concentric band. Inner d's at smaller radius.
TIER_GAP = 1.4
PETAL_LEN_BASE = 0.55
PETAL_LEN_VAR = 0.55

for tier_idx, d in enumerate(ds):
    cells = sorted(by_d[d])  # ascending qp
    n_d = len(cells)
    r_base = 1.0 + TIER_GAP * tier_idx
    color = D_COLORS.get(d, '#dddddd')

    # qp range within tier for length normalisation.
    qps = np.array([qp for qp, _, _ in cells], dtype=float)
    log_qps = np.log10(qps + 1)
    if log_qps.max() > log_qps.min():
        norm = (log_qps - log_qps.min()) / (log_qps.max() - log_qps.min())
    else:
        norm = np.zeros_like(log_qps)

    petal_width = 0.7 * np.pi / max(n_d, 6)  # tighter for crowded tiers

    for i, ((qp, n, info), w) in enumerate(zip(cells, norm)):
        theta_c = 2 * np.pi * (i + 0.5) / n_d
        petal_len = PETAL_LEN_BASE + PETAL_LEN_VAR * w
        # Petal shape parametric: from base to tip and back.
        petal_r = r_base + petal_len * np.sin(petal_s)
        petal_theta = theta_c + (petal_width * 0.5) * np.cos(petal_s)

        ax.plot(petal_theta, petal_r, color=color, alpha=0.88, linewidth=1.0)
        ax.fill(petal_theta, petal_r, color=color, alpha=0.22)

    # A faint ring at r_base shows the tier baseline.
    ring_t = np.linspace(0, 2 * np.pi, 400)
    ax.plot(ring_t, np.full_like(ring_t, r_base),
            color=color, alpha=0.18, linewidth=0.5)

style_polar(ax)
ax.set_rmax(1.0 + TIER_GAP * (len(ds) - 1) + PETAL_LEN_BASE + PETAL_LEN_VAR + 0.3)
plt.savefig('lotus_lattice.png', dpi=170, facecolor=BG,
            bbox_inches='tight', pad_inches=0.25)
plt.close()
print(f"→ lotus_lattice.png ({len(ds)} d-tiers)")
