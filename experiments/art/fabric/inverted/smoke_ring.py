"""
Smoke Ring — soft inverted significand disc.

Heavy pre-warp blur dissolves the mosaic into smooth flowing bands.
Cyclic colormap (twilight_shifted) eliminates the hard 0/1 boundary.
Gamma < 1 lifts the midtones. Larger central hole opens the ring.
The result is an aurora or gas cloud viewed end-on.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', '..', '..', '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from acm_core import acm_n_primes

N_ROWS   = 600
N_DIGITS = 80
W        = 4

# ── build + compute ──────────────────────────────────────────────────

print("Building digit strings …")
fabric = np.zeros((N_ROWS, N_DIGITS), dtype=int)
for i, n in enumerate(range(1, N_ROWS + 1)):
    ps = acm_n_primes(n, 40)
    s = ''.join(str(p) for p in ps)
    for j, ch in enumerate(s[:N_DIGITS]):
        fabric[i, j] = int(ch)

print("Computing significands …")
N_WIN = N_DIGITS - W + 1
powers = 10 ** np.arange(W - 1, -1, -1)
sig = np.zeros((N_ROWS, N_WIN))
for j in range(N_WIN):
    sig[:, j] = np.dot(fabric[:, j:j + W], powers) / 10**W

# ── artistic transforms ──────────────────────────────────────────────

# pre-warp blur: dissolve the stitch boundaries
sig = gaussian_filter(sig, sigma=[3, 2])

# renormalize — blur compresses dynamic range, spread it back out
sig = (sig - sig.min()) / (sig.max() - sig.min() + 1e-12)

# mild gamma lift
sig = sig ** 0.6

# ── inverted polar warp ──────────────────────────────────────────────

print("Warping …")
img_size = 2400
cx, cy = img_size / 2, img_size / 2
r_max = img_size / 2 - 40
r_min = r_max * 0.15                # larger hole — open ring
R2 = r_min * r_max

iy, ix = np.mgrid[0:img_size, 0:img_size]
dx = (ix - cx).astype(np.float64)
dy = (iy - cy).astype(np.float64)
r = np.sqrt(dx * dx + dy * dy)
theta = np.arctan2(dy, dx) % (2 * np.pi)

r_safe = np.maximum(r, 1e-6)
r_orig = R2 / r_safe

# bilinear sampling for smoothness
n_frac = (r_orig - r_min) / (r_max - r_min) * (N_ROWS - 1)
d_frac = theta / (2 * np.pi) * (N_WIN - 1)

n0 = np.clip(np.floor(n_frac).astype(int), 0, N_ROWS - 2)
d0 = np.clip(np.floor(d_frac).astype(int), 0, N_WIN - 2)
nf = n_frac - n0
df = d_frac - d0

valid = (r >= r_min) & (r <= r_max) & \
        (n_frac >= 0) & (n_frac <= N_ROWS - 1) & \
        (d_frac >= 0) & (d_frac <= N_WIN - 1)

# bilinear interpolation
bg = np.full((img_size, img_size, 3), 0.04)
v_n0d0 = sig[n0[valid], d0[valid]]
v_n1d0 = sig[np.minimum(n0[valid] + 1, N_ROWS - 1), d0[valid]]
v_n0d1 = sig[n0[valid], np.minimum(d0[valid] + 1, N_WIN - 1)]
v_n1d1 = sig[np.minimum(n0[valid] + 1, N_ROWS - 1),
             np.minimum(d0[valid] + 1, N_WIN - 1)]

nf_v = nf[valid]
df_v = df[valid]
vals = (v_n0d0 * (1 - nf_v) * (1 - df_v) +
        v_n1d0 * nf_v * (1 - df_v) +
        v_n0d1 * (1 - nf_v) * df_v +
        v_n1d1 * nf_v * df_v)

bg[valid] = plt.cm.twilight_shifted(vals)[:, :3]

# post-warp blur: soft atmospheric glow
bg = gaussian_filter(bg, sigma=[2, 2, 0])

# ── save ─────────────────────────────────────────────────────────────

print("Saving …")
fig = plt.figure(figsize=(14, 14))
fig.patch.set_facecolor('#0a0a0a')
ax = fig.add_axes([0, 0, 1, 1])
ax.imshow(bg, origin='lower', interpolation='lanczos')
ax.axis('off')

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'smoke_ring.png')
fig.savefig(out, dpi=200, facecolor='#0a0a0a', pad_inches=0)
plt.close()
print(f'-> {out}')
