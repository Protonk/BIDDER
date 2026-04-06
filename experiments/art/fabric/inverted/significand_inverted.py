"""
Significand inverted disc — the significand carpet warped inside-out.

Same polar mapping as the annular disc, then radial inversion r → R²/r
(where R = sqrt(r_min · r_max)).  The low-n rows — with the richest
structure (1-digit/2-digit transition, dense diagonal interference) —
move to the outer rim where pixel density is highest.  The regular
high-n rows compress toward the center.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', '..', '..', '..', 'core'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from acm_core import acm_n_primes

N_ROWS   = 600
N_DIGITS = 80
W        = 4

# ── build digit fabric ───────────────────────────────────────────────

print("Building digit strings …")
fabric = np.zeros((N_ROWS, N_DIGITS), dtype=int)
for i, n in enumerate(range(1, N_ROWS + 1)):
    ps = acm_n_primes(n, 40)
    s = ''.join(str(p) for p in ps)
    for j, ch in enumerate(s[:N_DIGITS]):
        fabric[i, j] = int(ch)

# ── sliding-window significand ───────────────────────────────────────

print(f"Computing {W}-digit significands …")
N_WIN = N_DIGITS - W + 1
powers = 10 ** np.arange(W - 1, -1, -1)
sig = np.zeros((N_ROWS, N_WIN))
for j in range(N_WIN):
    sig[:, j] = np.dot(fabric[:, j:j + W], powers) / 10**W

# ── inverted polar warp ──────────────────────────────────────────────

print("Warping to inverted disc …")
img_size = 2400
cx, cy = img_size / 2, img_size / 2
r_max = img_size / 2 - 40
r_min = r_max * 0.05
R2 = r_min * r_max          # inversion constant R² = r_min · r_max

iy, ix = np.mgrid[0:img_size, 0:img_size]
dx = (ix - cx).astype(np.float64)
dy = (iy - cy).astype(np.float64)
r = np.sqrt(dx * dx + dy * dy)
theta = np.arctan2(dy, dx) % (2 * np.pi)

# invert: map output radius r to source radius R²/r
r_safe = np.maximum(r, 1e-6)
r_orig = R2 / r_safe

# source radius → fabric row
n_idx = ((r_orig - r_min) / (r_max - r_min) * N_ROWS).astype(int)
d_idx = (theta / (2 * np.pi) * N_WIN).astype(int)

valid = (r >= r_min) & (r <= r_max) & \
        (n_idx >= 0) & (n_idx < N_ROWS) & \
        (d_idx >= 0) & (d_idx < N_WIN)

# ── colour ───────────────────────────────────────────────────────────

bg = np.full((img_size, img_size, 3), 0.04)
vals = sig[n_idx[valid], d_idx[valid]]
bg[valid] = plt.cm.inferno(vals)[:, :3]

# ── save (no chrome) ─────────────────────────────────────────────────

print("Saving …")
fig = plt.figure(figsize=(14, 14))
fig.patch.set_facecolor('#0a0a0a')
ax = fig.add_axes([0, 0, 1, 1])
ax.imshow(bg, origin='lower', interpolation='lanczos')
ax.axis('off')

out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   'significand_inverted.png')
fig.savefig(out, dpi=200, facecolor='#0a0a0a', pad_inches=0)
plt.close()
print(f'-> {out}')
