"""
Bigram flow - consecutive digit pairs as oriented threads.

This starts from the same source plane as bigram_weave.py:

    x = digit position
    y = monoid n

Each cell encodes the pair (d_p, d_{p+1}), but the pair is drawn as a
short translucent stroke. Digits live on a 10-point ring; the stroke
direction is the chord from current digit to next digit. Color follows
the bigram_weave RGB rule, with brighter pigment and rarity-driven glow.

The output is not the flat plane. The plane is mapped through a twisted
polar shell: digit position winds around angle, n becomes radius, and the
low-n structure is pushed outward where it has more room. Stroke
directions are transformed through the local geometry, not wrapped after
the fact.
"""

import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..', '..', '..', '..', 'core'))

from acm_core import acm_n_primes


N_ROWS = 720
N_DIGITS = 120
N_PRIMES = 80

IMG_SIZE = 3000
CX = CY = IMG_SIZE / 2.0
R_INNER = 210.0
R_OUTER = 1425.0
R_SPAN = R_OUTER - R_INNER

TURNS = 2.85
TWIST = 0.64
WAVE = 0.075
RADIAL_GAMMA = 0.58
VERTICAL_GAIN = 10.0

DARK = '#070707'
OUT = os.path.join(_here, 'bigram_flow.png')


def polar_map(u, v):
    """Map normalized fabric coordinates to the twisted polar shell.

    u: digit-position coordinate in [0, 1]
    v: monoid coordinate in [0, 1], low n at v=0
    """
    low_n_weight = 1.0 - v
    r = R_INNER + R_SPAN * (low_n_weight ** RADIAL_GAMMA)
    theta = 2.0 * np.pi * (
        TURNS * u
        + TWIST * (low_n_weight ** 0.72)
        + WAVE * np.sin(2.0 * np.pi * (3.0 * low_n_weight + 0.35 * u))
    )
    return CX + r * np.cos(theta), CY + r * np.sin(theta)


print("Building digit strings...")
fabric = np.zeros((N_ROWS, N_DIGITS), dtype=np.int8)

for i, n in enumerate(range(1, N_ROWS + 1)):
    ps = acm_n_primes(n, N_PRIMES)
    s = ''.join(str(p) for p in ps)
    if len(s) < N_DIGITS:
        raise RuntimeError(f"not enough digits for n={n}: {len(s)}")
    for j, ch in enumerate(s[:N_DIGITS]):
        fabric[i, j] = int(ch)


print("Computing bigram flow field...")
d_curr = fabric[:, :-1].astype(np.float64)
d_next = fabric[:, 1:].astype(np.float64)
contrast = np.abs(d_curr - d_next) / 9.0

# Same channel rule as bigram_weave.py, brightened for the polar shell.
base_rgb = np.stack([
    d_curr / 9.0,
    contrast,
    d_next / 9.0,
], axis=-1)

# Rarity of each digit transition, used as intensity rather than geometry.
pairs = (fabric[:, :-1] * 10 + fabric[:, 1:]).astype(np.int16)
counts = np.bincount(pairs.ravel(), minlength=100).astype(np.float64)
freq = counts[pairs] / pairs.size
surprise = -np.log(freq + 1e-12)
surprise = (surprise - surprise.min()) / (surprise.max() - surprise.min())

rgb = np.clip(
    0.08
    + 1.22 * (base_rgb ** 0.62)
    + 0.14 * surprise[:, :, None],
    0.0,
    1.0,
)

# Place digits on a ring and use the chord direction as transition angle.
theta_digits = np.pi / 2.0 + 2.0 * np.pi * np.arange(10) / 10.0
digit_xy = np.stack([np.cos(theta_digits), np.sin(theta_digits)], axis=1)
vec = digit_xy[fabric[:, 1:]] - digit_xy[fabric[:, :-1]]

same = np.linalg.norm(vec, axis=-1) < 1e-9
if same.any():
    # Same-digit transitions become tiny tangential threads at that digit.
    tangent = theta_digits[fabric[:, :-1]] + np.pi / 2.0
    vec[same, 0] = np.cos(tangent[same])
    vec[same, 1] = np.sin(tangent[same])

norm = np.linalg.norm(vec, axis=-1)
unit = vec / norm[:, :, None]

n_bigrams = N_DIGITS - 1
cell_u = 1.0 / n_bigrams
cell_v = 1.0 / N_ROWS

jj = np.arange(n_bigrams, dtype=np.float64)[None, :]
ii = np.arange(N_ROWS, dtype=np.float64)[:, None]
u = (jj + 0.5) * cell_u
v = (ii + 0.5) * cell_v

x, y = polar_map(u, v)

# Transform source directions through the local polar geometry. The v
# direction is intentionally amplified so radial motion remains visible
# against the much longer angular cell spacing.
x_up, y_up = polar_map(np.clip(u + 0.5 * cell_u, 0.0, 1.0), v)
x_um, y_um = polar_map(np.clip(u - 0.5 * cell_u, 0.0, 1.0), v)
e_u = np.stack([x_up - x_um, y_up - y_um], axis=-1)

x_vp, y_vp = polar_map(u, np.clip(v + 0.5 * cell_v, 0.0, 1.0))
x_vm, y_vm = polar_map(u, np.clip(v - 0.5 * cell_v, 0.0, 1.0))
e_v = np.stack([x_vp - x_vm, y_vp - y_vm], axis=-1) * VERTICAL_GAIN

direction = unit[:, :, 0, None] * e_u + unit[:, :, 1, None] * e_v
direction_norm = np.linalg.norm(direction, axis=-1)
direction = direction / np.maximum(direction_norm[:, :, None], 1e-9)

length = 4.0 + 22.0 * contrast + 11.0 * surprise
length[same] = 2.8 + 8.0 * surprise[same]

dx = direction[:, :, 0] * length * 0.5
dy = direction[:, :, 1] * length * 0.5

segments = np.empty((N_ROWS * n_bigrams, 2, 2), dtype=np.float64)
segments[:, 0, 0] = (x - dx).ravel()
segments[:, 0, 1] = (y - dy).ravel()
segments[:, 1, 0] = (x + dx).ravel()
segments[:, 1, 1] = (y + dy).ravel()

alpha = 0.16 + 0.48 * contrast + 0.36 * surprise
alpha = np.clip(alpha, 0.12, 0.95)

colors = np.empty((N_ROWS * n_bigrams, 4), dtype=np.float64)
colors[:, :3] = rgb.reshape((-1, 3))
colors[:, 3] = alpha.ravel()

linewidth = 0.22 + 1.05 * contrast + 0.72 * surprise
linewidth = np.clip(linewidth, 0.22, 2.45).ravel()

glow_colors = colors.copy()
glow_colors[:, 3] *= 0.18


print("Rendering...")
fig = plt.figure(figsize=(15, 15), dpi=200, facecolor=DARK, frameon=False)
fig.patch.set_alpha(1.0)
ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
ax.set_axis_off()
fig.add_axes(ax)
ax.set_facecolor(DARK)
ax.patch.set_alpha(1.0)

# Faint transformed grid: enough to keep the warped plane readable.
grid_color = (0.11, 0.12, 0.13, 0.18)
for ug in np.linspace(0.0, 1.0, N_DIGITS):
    vv = np.linspace(0.0, 1.0, 900)
    xx, yy = polar_map(np.full_like(vv, ug), vv)
    ax.plot(xx, yy, color=grid_color, lw=0.26, zorder=1)
for vg in np.linspace(0.0, 1.0, 24):
    uu = np.linspace(0.0, 1.0, 900)
    xx, yy = polar_map(uu, np.full_like(uu, vg))
    ax.plot(xx, yy, color=(0.09, 0.10, 0.11, 0.16), lw=0.34, zorder=1)

ax.add_collection(LineCollection(
    segments,
    colors=glow_colors,
    linewidths=linewidth * 5.5,
    capstyle='round',
    joinstyle='round',
    antialiased=True,
    zorder=2,
))
ax.add_collection(LineCollection(
    segments,
    colors=colors,
    linewidths=linewidth,
    capstyle='round',
    joinstyle='round',
    antialiased=True,
    zorder=3,
))

# Quiet outer and inner rim.
rim_t = np.linspace(0.0, 2.0 * np.pi, 1600)
for rr, lw, a in [(R_OUTER, 0.75, 0.20), (R_INNER, 0.55, 0.12)]:
    ax.plot(CX + rr * np.cos(rim_t), CY + rr * np.sin(rim_t),
            color=(0.20, 0.22, 0.23, a), lw=lw, zorder=0)

ax.set_xlim(0, IMG_SIZE)
ax.set_ylim(0, IMG_SIZE)
ax.set_aspect('equal')

fig.canvas.draw()
rgba = np.asarray(fig.canvas.buffer_rgba()).astype(np.float64) / 255.0
bg = np.array([7, 7, 7], dtype=np.float64) / 255.0
rgb_out = rgba[:, :, :3] * rgba[:, :, 3:4] + bg * (1.0 - rgba[:, :, 3:4])
plt.imsave(OUT, np.clip(rgb_out, 0.0, 1.0))
plt.close(fig)
print(f"-> {OUT}")
