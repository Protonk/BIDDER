"""
Chrysalis — the smoke ring mapped to an egg / limaçon.

The circle is replaced by a limaçon r = R₀(1 + ε·cos θ), an organic
asymmetric form.  The narrow end compresses the boundary structure;
the wide end expands it — like a cross-section of a seed pod or shell.
Same blur / renormalization / twilight treatment as the smoke ring.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', '..', '..', '..', 'core'))

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

# ── smoke ring treatment ─────────────────────────────────────────────

sig = gaussian_filter(sig, sigma=[3, 2])
sig = (sig - sig.min()) / (sig.max() - sig.min() + 1e-12)
sig = sig ** 0.6

# ── limaçon warp ─────────────────────────────────────────────────────

print("Warping to limaçon …")
img_size = 2400
epsilon  = 0.4                          # asymmetry (0 = circle)
R_0      = img_size / 2 - 40           # base radius — fills canvas
cx       = img_size / 2 - R_0 * epsilon  # shift polar origin so egg is centered
cy       = img_size / 2

iy, ix = np.mgrid[0:img_size, 0:img_size]
dx = (ix - cx).astype(np.float64)
dy = (iy - cy).astype(np.float64)
r = np.sqrt(dx * dx + dy * dy)
theta = np.arctan2(dy, dx) % (2 * np.pi)

# limaçon boundary at each angle
r_boundary = R_0 * (1 + epsilon * np.cos(theta))

# normalised radius within the egg (0 = centre, 1 = boundary)
rho = r / np.maximum(r_boundary, 1e-6)

# inversion in rho-space: boundary (rho=1) → low n, centre → high n
rho_min = 0.06
rho_inv = rho_min / np.maximum(rho, 1e-6)

# data coordinates
n_frac = (rho_inv - rho_min) / (1.0 - rho_min) * (N_ROWS - 1)
d_frac = theta / (2 * np.pi) * (N_WIN - 1)

valid = (rho >= rho_min) & (rho <= 1.0) & \
        (n_frac >= 0) & (n_frac <= N_ROWS - 1) & \
        (d_frac >= 0) & (d_frac <= N_WIN - 1)

# ── bilinear interpolation ───────────────────────────────────────────

n0 = np.clip(np.floor(n_frac).astype(int), 0, N_ROWS - 2)
d0 = np.clip(np.floor(d_frac).astype(int), 0, N_WIN - 2)
nf = n_frac - n0
df = d_frac - d0

bg = np.full((img_size, img_size, 3), 0.04)

v00 = sig[n0[valid], d0[valid]]
v10 = sig[np.minimum(n0[valid] + 1, N_ROWS - 1), d0[valid]]
v01 = sig[n0[valid], np.minimum(d0[valid] + 1, N_WIN - 1)]
v11 = sig[np.minimum(n0[valid] + 1, N_ROWS - 1),
          np.minimum(d0[valid] + 1, N_WIN - 1)]

nf_v = nf[valid]
df_v = df[valid]
vals = (v00 * (1 - nf_v) * (1 - df_v) +
        v10 * nf_v       * (1 - df_v) +
        v01 * (1 - nf_v) * df_v +
        v11 * nf_v       * df_v)

bg[valid] = plt.cm.twilight_shifted(vals)[:, :3]

# post-warp softness
bg = gaussian_filter(bg, sigma=[2, 2, 0])

# ── save ─────────────────────────────────────────────────────────────

print("Saving …")
fig = plt.figure(figsize=(14, 14))
fig.patch.set_facecolor('#0a0a0a')
ax = fig.add_axes([0, 0, 1, 1])
ax.imshow(bg, origin='lower', interpolation='lanczos')
ax.axis('off')

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chrysalis.png')
fig.savefig(out, dpi=200, facecolor='#0a0a0a', pad_inches=0)
plt.close()
print(f'-> {out}')
