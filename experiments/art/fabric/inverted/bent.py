"""
Bent — the smoke ring significand warped by gravitational lenses
in the Cartesian plane.

Two point-mass lenses placed asymmetrically in the rectangular carpet
create voids surrounded by stretched, bent twilight bands — like
looking at the data through a pair of invisible singularities.
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

# ── gravitational lens warp ──────────────────────────────────────────

print("Bending …")
img_size = 2400

iy, ix = np.mgrid[0:img_size, 0:img_size]
u = ix.astype(np.float64) / img_size     # 0→1 = window position
v = iy.astype(np.float64) / img_size     # 0→1 = monoid n

# two lenses: (u_center, v_center, Einstein_radius)
lenses = [
    (0.33, 0.42, 0.07),     # left, slightly below mid — strong
    (0.71, 0.64, 0.045),    # right, slightly above mid — weaker
]

u_disp = np.zeros_like(u)
v_disp = np.zeros_like(v)

for u0, v0, R in lenses:
    du = u - u0
    dv = v - v0
    d2 = np.maximum(du**2 + dv**2, 1e-10)
    factor = R**2 / d2
    u_disp += du * factor
    v_disp += dv * factor

u_src = u + u_disp
v_src = v + v_disp

# ── sample data with bilinear interpolation ──────────────────────────

n_frac = v_src * (N_ROWS - 1)
d_frac = u_src * (N_WIN - 1)

valid = (n_frac >= 0) & (n_frac <= N_ROWS - 1) & \
        (d_frac >= 0) & (d_frac <= N_WIN - 1)

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

# post-warp blur
bg = gaussian_filter(bg, sigma=[2, 2, 0])

# ── save ─────────────────────────────────────────────────────────────

print("Saving …")
fig = plt.figure(figsize=(14, 14))
fig.patch.set_facecolor('#0a0a0a')
ax = fig.add_axes([0, 0, 1, 1])
ax.imshow(bg, origin='lower', interpolation='lanczos')
ax.axis('off')

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bent.png')
fig.savefig(out, dpi=200, facecolor='#0a0a0a', pad_inches=0)
plt.close()
print(f'-> {out}')
