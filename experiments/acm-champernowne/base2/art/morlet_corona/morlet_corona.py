"""
morlet_corona.py — two visualizations of the n = 3 Morlet scalogram.

Both views are derived from the same Morlet CWT of the doubly-detrended
n = 3 RDS stream and use the same magma palette (orange → purple).

Outputs:

  morlet_scalogram.png  — standard scientific viz of the scalogram, with
                          axes, ticks, log y, title, and colorbar.

  morlet_sun.png        — corona-style polar wrap. Scale axis inverted
                          so the largest (brightest) scales sit at the
                          centre and the smallest scales sit on the rim.
                          The polar zero is shifted so the bright t = 0 / t = N
                          seam points straight down (6 o'clock). No chrome.
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

# Sun image
IMG_SIZE = 2000
R_MAX = 950


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
print(f"Computing Morlet CWT over {N_SCALES} log-spaced scales "
      f"in [{SCALE_MIN:.1f}, {SCALE_MAX:.1f}]...")
cwt = cwt_morlet(rds_detrended, scales)
power = np.abs(cwt) ** 2
print(f"  power range: 10^{np.log10(power[power > 0].min()):.1f} "
      f"to 10^{np.log10(power.max()):.1f}")


# ── Visualization 1: standard scientific scalogram ──────────────────

print("\nRendering morlet_scalogram.png...")

DARK = '#0a0a0a'
WHITE = 'white'

fig, ax = plt.subplots(figsize=(16, 9), facecolor=DARK)
ax.set_facecolor(DARK)

log_power = np.log10(power + 1e-12)
extent = [0, n_bits, scales.min(), scales.max()]

im = ax.imshow(
    log_power,
    aspect='auto',
    cmap='magma',
    extent=extent,
    origin='lower',
    interpolation='bilinear',
)

ax.set_yscale('log')
ax.set_xlabel('bit position  t', color=WHITE, fontsize=14)
ax.set_ylabel('Morlet scale  s (bits)  ≈  Fourier period',
              color=WHITE, fontsize=14)
ax.set_title(
    f'Morlet scalogram of detrended RDS(t)   '
    f'(n = {N},  {n_bits} bits,  {N_SCALES} log-spaced scales)',
    color=WHITE, fontsize=15, pad=14,
)

ax.tick_params(colors=WHITE, labelsize=11)
for spine in ax.spines.values():
    spine.set_color(WHITE)

cb = plt.colorbar(im, ax=ax, fraction=0.025, pad=0.012)
cb.set_label('log₁₀ |W(s, t)|²', color=WHITE, fontsize=12)
cb.ax.yaxis.set_tick_params(color=WHITE)
plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color=WHITE)

plt.tight_layout()
out1 = os.path.join(_here, 'morlet_scalogram.png')
plt.savefig(out1, dpi=200, facecolor=DARK)
plt.close()
print(f"  -> {out1}")


# ── Visualization 2: Morlet sun (corona-style polar wrap) ───────────

print("\nRendering morlet_sun.png...")

# Polar coordinates for every pixel
yy, xx = np.mgrid[0:IMG_SIZE, 0:IMG_SIZE]
cx = cy = IMG_SIZE // 2
dx = (xx - cx).astype(np.float64)
dy = (yy - cy).astype(np.float64)
r = np.sqrt(dx * dx + dy * dy)
# theta ∈ [0, 2π) with the seam (θ=0 / θ=2π) at 6 o'clock
theta = (np.arctan2(dy, dx) + np.pi / 2) % (2 * np.pi)

# theta ↦ time index (one full revolution per signal length, CCW from 6:00)
t_idx = (theta / (2 * np.pi) * n_bits).astype(int)
t_idx = np.clip(t_idx, 0, n_bits)

# r ↦ scale index, INVERTED so the largest (brightest) scales sit at the
# centre and the smallest scales sit on the rim. r = 0 → s = SCALE_MAX,
# r = R_MAX → s = SCALE_MIN.
s_idx = ((1.0 - r / R_MAX) * (N_SCALES - 1)).astype(int)
s_idx = np.clip(s_idx, 0, N_SCALES - 1)

in_disk = r <= R_MAX

FLOOR = 1e-12
values = np.full((IMG_SIZE, IMG_SIZE), FLOOR, dtype=np.float64)
values[in_disk] = np.maximum(power[s_idx[in_disk], t_idx[in_disk]], FLOOR)

log_vals = np.log10(values)
in_log = log_vals[in_disk]
vmin = float(in_log.min())
vmax = float(in_log.max())
norm_vals = (log_vals - vmin) / (vmax - vmin)
norm_vals = np.clip(norm_vals, 0.0, 1.0)
norm_vals[~in_disk] = 0.0

cmap = plt.get_cmap('magma')
rgb = cmap(norm_vals)[:, :, :3]
rgb[~in_disk] = 0.0

fig = plt.figure(frameon=False, figsize=(20, 20))
ax = plt.Axes(fig, [0., 0., 1., 1.])
ax.set_axis_off()
fig.add_axes(ax)
ax.imshow(rgb, interpolation='nearest', origin='lower')

out2 = os.path.join(_here, 'morlet_sun.png')
plt.savefig(out2, dpi=150, pad_inches=0, bbox_inches='tight',
            facecolor='#000000')
plt.close()
print(f"  -> {out2}")
print("\nDone.")
