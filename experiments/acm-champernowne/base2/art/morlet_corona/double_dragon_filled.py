"""
double_dragon_filled.py — looser zoom that fills the canvas corners.

Same conformal warp as double_dragon_zoom.py (Q = 0.5, z = w²) and the
same body-modulation recipe (coarse + fine wavelet bands), but the disk
mask is removed and R_CROP is bumped from 0.5 to 0.6 so the spiral
content extends past the inscribed disk into the corners of the canvas.

Math constraint: for every corner pixel to fall inside the source disk
(|z| ≤ 1) we need

    R_CROP  ≤  R_OUT / (sqrt(2) · OUT_SIZE / 2)  ≈  0.683

R_CROP = 0.6 sits comfortably inside that bound — corner |z| ≈ 0.77,
all pixels render with valid spiral lookups, no black corner wedges.
"""

import sys
import os
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import fftconvolve

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..'))                              # base2/
sys.path.insert(0, os.path.join(_here, '..', '..', '..', '..', '..', 'core'))    # core/

from acm_core import acm_n_primes


# ── Parameters ──────────────────────────────────────────────────────

N = 3
TARGET_BITS = 300_000
N_SCALES = 120
SCALE_MIN = 2.0
SCALE_MAX = 50_000.0
MORLET_W0 = 6.0

OUT_SIZE = 3000
R_OUT = 1450
R_CROP = 0.6             # slightly looser than the 0.5 of double_dragon_zoom
Q = 0.5

N_LOOPS = 12
SCALE_COARSE = 27_559.0
SCALE_FINE = 800.0
FINE_WEIGHT = 1.0
ARM_SIGMA = 0.18


# ── ACM stream + RDS + per-entry detrend ───────────────────────────

def v2_of(n):
    v = 0
    while n % 2 == 0:
        v += 1
        n //= 2
    return v


def slope_for_entry(m, d):
    if m == 0:
        return 1.0
    if d <= 2 * m:
        return 1.0 - m
    return 1.0 - 2.0 * m + (m * (2 ** m)) / (2 ** m - 1)


def estimate_count(n, target_bits):
    avg = math.log2(max(n, 2)) + math.log2(max(target_bits // 20, 4))
    return int(target_bits / max(avg, 4)) + 200


def gen_for_monoid(n, target_bits):
    count = estimate_count(n, target_bits)
    while True:
        primes = acm_n_primes(n, 2 * count)
        cum = 0
        used = []
        for p in primes:
            d = p.bit_length()
            if cum + d > target_bits:
                break
            cum += d
            used.append(p)
        if len(used) > 0 and cum >= target_bits - 200:
            bits = []
            for p in used:
                for c in bin(p)[2:]:
                    bits.append(int(c))
            return np.array(bits, dtype=np.int8), used
        count *= 2


def compute_rds(bits):
    pm = 2 * bits.astype(np.int64) - 1
    return np.concatenate(([0], np.cumsum(pm)))


def expected_curve_per_entry(entries, n_bits):
    ds = np.array([p.bit_length() for p in entries], dtype=np.int64)
    ms = np.array([v2_of(int(p)) for p in entries], dtype=np.int64)
    slopes = np.array([slope_for_entry(int(m), int(d))
                       for m, d in zip(ms, ds)], dtype=np.float64)
    cum_bits = np.concatenate(([0], np.cumsum(ds))).astype(np.float64)
    cum_expected = np.concatenate(([0.0], np.cumsum(slopes)))
    return np.interp(np.arange(n_bits + 1, dtype=np.float64),
                     cum_bits, cum_expected)


def linear_detrend(y):
    x = np.arange(len(y))
    a, b = np.polyfit(x, y, 1)
    return y - (a * x + b)


def morlet_wavelet(n_points, s, w0=MORLET_W0):
    t = (np.arange(n_points) - (n_points - 1) / 2.0) / s
    norm = (np.pi ** -0.25) / np.sqrt(s)
    return norm * np.exp(1j * w0 * t) * np.exp(-t * t / 2.0)


def cwt_morlet(data, scales, w0=MORLET_W0):
    n = len(data)
    out = np.zeros((len(scales), n), dtype=np.complex128)
    for i, s in enumerate(scales):
        n_pts = min(int(10 * s), n)
        if n_pts < 5:
            n_pts = 5
        if n_pts % 2 == 0:
            n_pts += 1
        wavelet = morlet_wavelet(n_pts, s, w0)
        re = fftconvolve(data, wavelet.real, mode='same')
        im = fftconvolve(data, wavelet.imag, mode='same')
        out[i] = re + 1j * im
    return out


# ── Compute CWT ────────────────────────────────────────────────────

print(f"Generating n = {N} stream of {TARGET_BITS} bits...")
bits, entries = gen_for_monoid(N, TARGET_BITS)
n_bits = len(bits)
print(f"  bits = {n_bits}, entries = {len(entries)}")

rds = compute_rds(bits).astype(np.float64)
expected_pe = expected_curve_per_entry(entries, n_bits)
rds_detrended = linear_detrend(rds)

scales = np.geomspace(SCALE_MIN, SCALE_MAX, N_SCALES)
print(f"Computing Morlet CWT over {N_SCALES} scales...")
cwt = cwt_morlet(rds_detrended, scales)
power = np.abs(cwt) ** 2


# ── Body modulation ────────────────────────────────────────────────

coarse_idx = int(np.argmin(np.abs(scales - SCALE_COARSE)))
fine_idx   = int(np.argmin(np.abs(scales - SCALE_FINE)))
print(f"  coarse scale = {scales[coarse_idx]:.0f} bits")
print(f"  fine   scale = {scales[fine_idx]:.0f} bits")

p_coarse = power[coarse_idx]
p_fine   = power[fine_idx]
p_coarse_n = p_coarse / np.percentile(p_coarse, 99)
p_fine_n   = p_fine   / np.percentile(p_fine,   99)
modulated_body = p_coarse_n + FINE_WEIGHT * p_fine_n


# ── Spatial mapping (no disk mask, corners fill in) ─────────────────

print(f"Conformally warping at zoom (R_CROP = {R_CROP}, Q = {Q})...")

# Sanity check that corners are inside the source disk
canvas_edge_w = (OUT_SIZE / 2.0) / R_OUT * R_CROP
corner_w = canvas_edge_w * np.sqrt(2)
corner_z = corner_w ** (1.0 / Q)
print(f"  canvas edge |w| = {canvas_edge_w:.4f}")
print(f"  canvas corner |w| = {corner_w:.4f}, |z| = {corner_z:.4f}")
if corner_z > 1.0:
    print("  WARNING: corner pixels exceed source disk; expect black wedges")

yy, xx = np.mgrid[0:OUT_SIZE, 0:OUT_SIZE]
out_c = OUT_SIZE // 2
dx_out = (xx - out_c).astype(np.float64) / R_OUT * R_CROP
dy_out = (yy - out_c).astype(np.float64) / R_OUT * R_CROP

w = dx_out + 1j * dy_out

# Inverse map: z = w^(1/Q). For Q = 0.5 this is z = w², single-valued.
z = w ** (1.0 / Q)

b_norm = 1.0 / (2 * np.pi * N_LOOPS)


def spiral_lookup(z_branch):
    r_norm = np.abs(z_branch)
    theta = (np.angle(z_branch) + np.pi / 2) % (2 * np.pi)

    k_real = (r_norm / b_norm - theta) / (2 * np.pi)
    k_int = np.round(k_real).astype(int)
    fractional = k_real - k_int

    u = theta + 2 * np.pi * k_int
    t_idx_local = (u / (2 * np.pi * N_LOOPS) * n_bits).astype(int)
    t_idx_local = np.clip(t_idx_local, 0, n_bits)

    in_source = r_norm <= 1.0
    valid_k = (k_int >= 0) & (k_int < N_LOOPS)
    branch_mask = in_source & valid_k

    body = np.zeros_like(r_norm, dtype=np.float64)
    body[branch_mask] = modulated_body[t_idx_local[branch_mask]]

    envelope = np.exp(-(fractional ** 2) / (2 * ARM_SIGMA ** 2))
    envelope[~branch_mask] = 0.0

    return body * envelope, branch_mask


# Note: no in_output disk mask. Mask comes only from the spiral lookup
# itself, so any pixel whose inverse-mapped z is inside the source disk
# and lands in a valid loop will render.
combined, mask = spiral_lookup(z)


# ── Colormap ────────────────────────────────────────────────────────

print("Rendering...")

field = np.sqrt(np.maximum(combined, 0.0))
in_field = field[mask]
vmin = float(np.percentile(in_field, 2))
vmax = float(np.percentile(in_field, 99.5))
norm_vals = np.clip((field - vmin) / (vmax - vmin), 0.0, 1.0)

cmap = plt.get_cmap('magma')
rgb = cmap(norm_vals)[:, :, :3]
rgb[~mask] = 0.0


# ── Save ───────────────────────────────────────────────────────────

fig = plt.figure(frameon=False, figsize=(20, 20))
ax = plt.Axes(fig, [0., 0., 1., 1.])
ax.set_axis_off()
fig.add_axes(ax)
ax.imshow(rgb, interpolation='nearest', origin='lower')

out = os.path.join(_here, 'double_dragon_filled.png')
plt.savefig(out, dpi=150, pad_inches=0, bbox_inches='tight',
            facecolor='#000000')
plt.close()
print(f"  -> {out}")
