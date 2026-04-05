"""
Strata — frequency-multiplied shattered disc.

The raw significand is multiplied by k and taken mod 1 before the
gamma crush.  This creates k contour bands, each with the same sharp
bright-on-dark character as the original shattered disc.  Structure
that was invisible in the single-band original — buried under the
gamma crush — surfaces as new rings of lava.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', '..', '..', '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from acm_core import acm_n_primes

# ── hyperspace colormap ──────────────────────────────────────────────

_hyper_data = {
    'red':   [(0.0, 0.02, 0.02), (0.3, 0.0,  0.0),
              (0.6, 0.0,  0.0),  (0.8, 0.27, 0.27),
              (0.9, 0.53, 0.53), (1.0, 0.87, 0.87)],
    'green': [(0.0, 0.02, 0.02), (0.3, 0.04, 0.04),
              (0.6, 0.47, 0.47), (0.8, 0.67, 0.67),
              (0.9, 0.80, 0.80), (1.0, 0.93, 0.93)],
    'blue':  [(0.0, 0.06, 0.06), (0.3, 0.18, 0.18),
              (0.6, 1.0,  1.0),  (0.8, 1.0,  1.0),
              (0.9, 1.0,  1.0),  (1.0, 1.0,  1.0)],
}
cmap_hyper = LinearSegmentedColormap('hyperspace', _hyper_data, N=256)

N_ROWS   = 600
N_DIGITS = 80
W        = 2

K_FREQ   = 4       # frequency multiplier — number of contour bands
GAMMA    = 2.0     # slightly gentler than shattered's 2.5

# ── build + compute ──────────────────────────────────────────────────

print("Building digit strings …")
fabric = np.zeros((N_ROWS, N_DIGITS), dtype=int)
for i, n in enumerate(range(1, N_ROWS + 1)):
    ps = acm_n_primes(n, 40)
    s = ''.join(str(p) for p in ps)
    for j, ch in enumerate(s[:N_DIGITS]):
        fabric[i, j] = int(ch)

print(f"Computing significands (W={W}) …")
N_WIN = N_DIGITS - W + 1
powers = 10 ** np.arange(W - 1, -1, -1)
sig = np.zeros((N_ROWS, N_WIN))
for j in range(N_WIN):
    sig[:, j] = np.dot(fabric[:, j:j + W], powers) / 10**W

# ── frequency multiplication then crush ──────────────────────────────

sig = (np.clip(sig, 0, 1) * K_FREQ) % 1.0
sig = sig ** GAMMA

# ── inverted polar warp (identical to shattered.py) ──────────────────

print("Warping …")
img_size = 2400
cx, cy = img_size / 2, img_size / 2
r_max = img_size / 2 - 40
r_min = r_max * 0.03
R2 = r_min * r_max

iy, ix = np.mgrid[0:img_size, 0:img_size]
dx = (ix - cx).astype(np.float64)
dy = (iy - cy).astype(np.float64)
r = np.sqrt(dx * dx + dy * dy)
theta = np.arctan2(dy, dx) % (2 * np.pi)

r_safe = np.maximum(r, 0.5)
r_orig = R2 / r_safe

# modular wrap — data tiles infinitely inward and outward
n_idx = np.floor((r_orig - r_min) / (r_max - r_min) * N_ROWS).astype(int) % N_ROWS
d_idx = (theta / (2 * np.pi) * N_WIN).astype(int) % N_WIN

# every pixel gets data — no blank regions
bg = np.empty((img_size, img_size, 3))
vals = sig[n_idx, d_idx]
bg = cmap_hyper(vals)[:, :, :3].copy()

# ── save ─────────────────────────────────────────────────────────────

print("Saving …")
fig = plt.figure(figsize=(14, 14))
fig.patch.set_facecolor('#0a0a0a')
ax = fig.add_axes([0, 0, 1, 1])
ax.imshow(bg, origin='lower', interpolation='nearest')
ax.axis('off')

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'strata.png')
fig.savefig(out, dpi=200, facecolor='#0a0a0a', pad_inches=0)
plt.close()
print(f'-> {out}')
