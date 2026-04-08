"""
morlet_scalogram_upper.py — upper-half (large-scale) crop of the
morlet_corona scalogram.

Same Morlet CWT and parameters as morlet_corona.py, but only the
upper half of the log-scale axis is rendered. The lower half —
small scales where the cone narrows into thousands of stretched
near-vertical streaks — is dropped, leaving the dominant-scale
arches and the transition zone where they break up into banding
and fur.

The split is taken in log10(scale) space, so "upper half" means
scales from sqrt(SCALE_MIN · SCALE_MAX) up to SCALE_MAX. For the
default range [2, 50000] that's roughly 316 → 50000 bits.
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


# ── Parameters (mirror morlet_corona.py exactly) ────────────────────

N = 3
TARGET_BITS = 300_000
N_SCALES = 120
SCALE_MIN = 2.0
SCALE_MAX = 50_000.0
MORLET_W0 = 6.0


# ── ACM stream + RDS + linear detrend ──────────────────────────────

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
rds_detrended = linear_detrend(rds)

scales = np.geomspace(SCALE_MIN, SCALE_MAX, N_SCALES)
print(f"Computing Morlet CWT over {N_SCALES} log-spaced scales "
      f"in [{SCALE_MIN:.1f}, {SCALE_MAX:.1f}]...")
cwt = cwt_morlet(rds_detrended, scales)
power = np.abs(cwt) ** 2


# ── Crop to upper half of log(scale) ───────────────────────────────

log_min = np.log10(SCALE_MIN)
log_max = np.log10(SCALE_MAX)
log_mid = 0.5 * (log_min + log_max)
upper_mask = np.log10(scales) >= log_mid
scales_upper = scales[upper_mask]
power_upper = power[upper_mask]
print(f"  upper-half scale range: "
      f"{scales_upper.min():.1f} -> {scales_upper.max():.1f} bits "
      f"({len(scales_upper)} of {N_SCALES} rows)")


# ── Render ──────────────────────────────────────────────────────────

print("\nRendering morlet_scalogram_upper.png...")

DARK = '#0a0a0a'
WHITE = 'white'

fig, ax = plt.subplots(figsize=(16, 6.5), facecolor=DARK)
ax.set_facecolor(DARK)

log_power = np.log10(power_upper + 1e-12)
extent = [0, n_bits, scales_upper.min(), scales_upper.max()]

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
    f'Morlet scalogram of detrended RDS(t) — upper half of log scale   '
    f'(n = {N},  {n_bits} bits,  '
    f'scales {scales_upper.min():.0f}–{scales_upper.max():.0f})',
    color=WHITE, fontsize=14, pad=12,
)

ax.tick_params(colors=WHITE, labelsize=11)
for spine in ax.spines.values():
    spine.set_color(WHITE)

cb = plt.colorbar(im, ax=ax, fraction=0.025, pad=0.012)
cb.set_label('log₁₀ |W(s, t)|²', color=WHITE, fontsize=12)
cb.ax.yaxis.set_tick_params(color=WHITE)
plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color=WHITE)

plt.tight_layout()
out = os.path.join(_here, 'morlet_scalogram_upper.png')
plt.savefig(out, dpi=200, facecolor=DARK)
plt.close()
print(f"  -> {out}")
