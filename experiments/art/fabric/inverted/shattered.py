"""
Shattered — volcanic inverted significand disc.

Window width W=2 maximises grain. Gamma > 1 crushes everything to
darkness except the brightest significands, which burn through like
lava in fractured obsidian. The 'hot' colormap (black → red → yellow
→ white) completes the geological metaphor. Tiny central hole packs
the high-n regularity into a dense dark core.
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
W        = 2       # maximally grainy

# ── build + compute ──────────────────────────────────────────────────

print("Building digit strings …")
fabric = np.zeros((N_ROWS, N_DIGITS), dtype=int)
for i, n in enumerate(range(1, N_ROWS + 1)):
    ps = acm_n_primes(n, 40)
    s = ''.join(str(p) for p in ps)
    for j, ch in enumerate(s[:N_DIGITS]):
        fabric[i, j] = int(ch)

print("Computing significands (W=2) …")
N_WIN = N_DIGITS - W + 1      # 79
powers = 10 ** np.arange(W - 1, -1, -1)   # [10, 1]
sig = np.zeros((N_ROWS, N_WIN))
for j in range(N_WIN):
    sig[:, j] = np.dot(fabric[:, j:j + W], powers) / 10**W

# ── artistic transform: crush to darkness ────────────────────────────

sig = np.clip(sig, 0, 1) ** 2.5

# ── inverted polar warp ──────────────────────────────────────────────

print("Warping …")
img_size = 2400
cx, cy = img_size / 2, img_size / 2
r_max = img_size / 2 - 40
r_min = r_max * 0.03                # tiny hole — dense core
R2 = r_min * r_max

iy, ix = np.mgrid[0:img_size, 0:img_size]
dx = (ix - cx).astype(np.float64)
dy = (iy - cy).astype(np.float64)
r = np.sqrt(dx * dx + dy * dy)
theta = np.arctan2(dy, dx) % (2 * np.pi)

r_safe = np.maximum(r, 1e-6)
r_orig = R2 / r_safe

n_idx = ((r_orig - r_min) / (r_max - r_min) * N_ROWS).astype(int)
d_idx = (theta / (2 * np.pi) * N_WIN).astype(int)

valid = (r >= r_min) & (r <= r_max) & \
        (n_idx >= 0) & (n_idx < N_ROWS) & \
        (d_idx >= 0) & (d_idx < N_WIN)

# nearest-neighbour — keep every edge sharp
bg = np.full((img_size, img_size, 3), 0.02)   # near-black
vals = sig[n_idx[valid], d_idx[valid]]
bg[valid] = plt.cm.hot(vals)[:, :3]

# ── save ─────────────────────────────────────────────────────────────

print("Saving …")
fig = plt.figure(figsize=(14, 14))
fig.patch.set_facecolor('#0a0a0a')
ax = fig.add_axes([0, 0, 1, 1])
ax.imshow(bg, origin='lower', interpolation='nearest')
ax.axis('off')

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shattered.png')
fig.savefig(out, dpi=200, facecolor='#0a0a0a', pad_inches=0)
plt.close()
print(f'-> {out}')
