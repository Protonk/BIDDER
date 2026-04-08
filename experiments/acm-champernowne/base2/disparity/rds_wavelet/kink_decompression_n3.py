"""
kink_decompression_n3.py — quantify the t-dependence of dark-notch
spacing in the n = 3 Morlet scalogram.

Observation (from `../../art/morlet_corona/morlet_scalogram_upper.png`):
the dark vertical notches that punctuate each scale band of the
n = 3 detrended-RDS scalogram are crowded together at small t and
spread out at large t. The conjecture is that this is a perspective
effect — notch positions are invariant under linear scaling of t,
so they should look uniform on a log(t) axis. Equivalently: notch
positions form an approximate geometric progression

    t_k  =  t_1 · r^(k − 1)

for some ratio r > 1 independent of t. The corresponding notch
spacing is then proportional to t.

This script tests that hypothesis quantitatively:

  1. Re-runs the n = 3 Morlet CWT with the same parameters as
     morlet_corona.py.
  2. Picks a kink-rich scale band (where the dark notches read
     crisply) and forms a 1D notch indicator by averaging
     −log10|W|² across that band along t. Deep notches in the
     scalogram show up as positive peaks in this 1D signal.
  3. Extracts notch positions via local-max detection.
  4. Fits two models for the notch positions:
       (a) geometric: log(t_k) = a + b · k → ratio r = exp(b)
       (b) power law: log(t_k) = a + α · log(k)
     Reports the residual sum of squares of each.
  5. Renders a 4-panel figure:
       Panel 1: upper-half scalogram on linear t
       Panel 2: same scalogram on log10(t) — visual self-similarity test
       Panel 3: 1D notch indicator with extracted peaks marked
       Panel 4: log(t_k) vs k with the geometric-model fit overlaid
"""

import sys
import os
import math
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import fftconvolve, find_peaks
from scipy.ndimage import uniform_filter1d

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

# Scale band where the notches read crisply (between the dominant
# arches and where the small-scale streaks start to smear into fur)
KINK_BAND_LO = 3_000.0
KINK_BAND_HI = 15_000.0

# Smoothing of the 1D notch signal (uniform-window σ in bits)
NOTCH_SMOOTH = 50

# Peak detector parameters
PEAK_PROMINENCE = 0.04
PEAK_DISTANCE = 25       # bits — small enough to catch the early crowded notches

# Drop notches within this many bits of either edge (a couple of
# wavelengths at the smallest band scale).
EDGE_PAD = 2_000

# Earliest t to use for the geometric/power-law fit.
T_FIT_MIN = 3_000


# ── CLI overrides for the parameters most likely to matter ─────────

_parser = argparse.ArgumentParser(
    description='Quantify n=3 Morlet scalogram notch decompression')
_parser.add_argument('--target-bits', type=int, default=TARGET_BITS,
                     help='length of n=3 stream in bits')
_parser.add_argument('--kink-lo', type=float, default=KINK_BAND_LO,
                     help='lower edge of kink-rich scale band (bits)')
_parser.add_argument('--kink-hi', type=float, default=KINK_BAND_HI,
                     help='upper edge of kink-rich scale band (bits)')
_parser.add_argument('--smooth', type=int, default=NOTCH_SMOOTH,
                     help='uniform smoothing window for notch indicator (bits)')
_parser.add_argument('--prominence', type=float, default=PEAK_PROMINENCE,
                     help='minimum peak prominence for notch detection')
_parser.add_argument('--distance', type=int, default=PEAK_DISTANCE,
                     help='minimum peak distance for notch detection (bits)')
_parser.add_argument('--edge-pad', type=int, default=EDGE_PAD,
                     help='bits of edge to trim from peak list')
_parser.add_argument('--suffix', type=str, default='',
                     help='suffix appended to the output filename')
_args = _parser.parse_args()

TARGET_BITS = _args.target_bits
KINK_BAND_LO = _args.kink_lo
KINK_BAND_HI = _args.kink_hi
NOTCH_SMOOTH = _args.smooth
PEAK_PROMINENCE = _args.prominence
PEAK_DISTANCE = _args.distance
EDGE_PAD = _args.edge_pad
OUT_SUFFIX = _args.suffix

print(f"Run config: target_bits={TARGET_BITS}, "
      f"kink_band=[{KINK_BAND_LO:.0f}, {KINK_BAND_HI:.0f}], "
      f"smooth={NOTCH_SMOOTH}, prominence={PEAK_PROMINENCE}, "
      f"distance={PEAK_DISTANCE}, edge_pad={EDGE_PAD}, "
      f"suffix='{OUT_SUFFIX}'")


# ── Helpers (mirror morlet_corona.py) ──────────────────────────────

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


# ── Build the notch indicator ───────────────────────────────────────

print(f"\nBuilding 1D notch indicator from scales "
      f"[{KINK_BAND_LO:.0f}, {KINK_BAND_HI:.0f}]...")

band_mask = (scales >= KINK_BAND_LO) & (scales <= KINK_BAND_HI)
band_power = power[band_mask]
print(f"  scale-band rows kept: {band_mask.sum()}")

# Average log power across the band, then negate so notches are peaks.
log_band = np.log10(band_power + 1e-12).mean(axis=0)
notch_raw = -(log_band - log_band.mean())
notch_smooth = uniform_filter1d(notch_raw, size=NOTCH_SMOOTH)


# ── Extract notch positions ─────────────────────────────────────────

print(f"\nExtracting notch peaks "
      f"(prominence ≥ {PEAK_PROMINENCE}, distance ≥ {PEAK_DISTANCE})...")

peaks, props = find_peaks(notch_smooth,
                          prominence=PEAK_PROMINENCE,
                          distance=PEAK_DISTANCE)
print(f"  raw peaks found: {len(peaks)}")

keep_edges = (peaks >= EDGE_PAD) & (peaks < (n_bits + 1) - EDGE_PAD)
peaks_kept = peaks[keep_edges]
print(f"  after edge trim ({EDGE_PAD} bits): {len(peaks_kept)} notches")
if len(peaks_kept) >= 4:
    print(f"  earliest notch: t = {peaks_kept[0]}")
    print(f"  latest notch:   t = {peaks_kept[-1]}")


# ── Fit geometric and power-law models ──────────────────────────────

peaks_fit = peaks_kept[peaks_kept >= T_FIT_MIN].astype(np.float64)
k_fit = np.arange(1, len(peaks_fit) + 1, dtype=np.float64)

print(f"\nFitting models on {len(peaks_fit)} notches "
      f"with t ≥ {T_FIT_MIN}...")

# Geometric: log(t_k) = a + b*k
log_t = np.log(peaks_fit)
g_slope, g_intercept = np.polyfit(k_fit, log_t, 1)
g_fit_vals = g_intercept + g_slope * k_fit
g_resid = log_t - g_fit_vals
g_rss = float(np.sum(g_resid ** 2))
g_r = float(np.exp(g_slope))
print(f"  geometric: log(t_k) = {g_intercept:.3f} + {g_slope:.4f}·k")
print(f"             ratio r = exp(b) = {g_r:.4f} per notch "
      f"({(g_r - 1) * 100:.2f}% growth per notch)")
print(f"             RSS(log) = {g_rss:.4f}")

# Power law: log(t_k) = a + α * log(k)
log_k = np.log(k_fit)
p_slope, p_intercept = np.polyfit(log_k, log_t, 1)
p_fit_vals = p_intercept + p_slope * log_k
p_resid = log_t - p_fit_vals
p_rss = float(np.sum(p_resid ** 2))
print(f"  power law: log(t_k) = {p_intercept:.3f} + {p_slope:.4f}·log(k)")
print(f"             exponent α = {p_slope:.4f}")
print(f"             RSS(log) = {p_rss:.4f}")

if g_rss < p_rss:
    winner = f"geometric (r = {g_r:.3f})"
else:
    winner = f"power-law (α = {p_slope:.3f})"
print(f"  → better fit: {winner}")


# ── Render 4-panel figure ──────────────────────────────────────────

print("\nRendering kink_decompression_n3.png...")

DARK = '#0a0a0a'
WHITE = 'white'
ACCENT = '#ffd166'
SIGNAL = '#ffe9c4'
GUIDE = '#888888'

fig = plt.figure(figsize=(16, 16), facecolor=DARK)
gs = fig.add_gridspec(4, 1, hspace=0.55,
                      height_ratios=[3, 3, 2.2, 3])

# Crop to a generous scale window for both scalogram panels
crop_mask = (scales >= 500.0) & (scales <= 50_000.0)
scales_crop = scales[crop_mask]
power_crop = power[crop_mask]
log_power_crop = np.log10(power_crop + 1e-12)

# Panel 1: linear t scalogram
ax1 = fig.add_subplot(gs[0])
ax1.set_facecolor(DARK)
extent_lin = [0, n_bits, scales_crop.min(), scales_crop.max()]
ax1.imshow(log_power_crop, aspect='auto', cmap='magma',
           extent=extent_lin, origin='lower', interpolation='bilinear')
ax1.set_yscale('log')
ax1.set_xlabel('bit position  t', color=WHITE, fontsize=12)
ax1.set_ylabel('scale  s (bits)', color=WHITE, fontsize=12)
ax1.set_title(
    'Morlet scalogram (linear t)   —   notches are crowded at the left, '
    'spread out at the right',
    color=WHITE, fontsize=13)
ax1.tick_params(colors=WHITE)
for sp in ax1.spines.values():
    sp.set_color(WHITE)

# Panel 2: log10 t scalogram (the visual self-similarity test)
ax2 = fig.add_subplot(gs[1])
ax2.set_facecolor(DARK)

# Resample t-axis onto a log grid so pcolormesh can render with log x.
t_edges = np.geomspace(1.0, float(n_bits), 1024)
t_centers = 0.5 * (t_edges[:-1] + t_edges[1:])
sample_idx = np.clip(t_centers.astype(int), 0, n_bits - 1)
log_power_logt = log_power_crop[:, sample_idx]
S_edges = np.geomspace(scales_crop.min(), scales_crop.max(),
                       len(scales_crop) + 1)
ax2.pcolormesh(t_edges, S_edges, log_power_logt,
               cmap='magma', shading='flat')
ax2.set_xscale('log')
ax2.set_yscale('log')
ax2.set_xlim(1, n_bits)
ax2.set_xlabel('bit position  t  (log scale)', color=WHITE, fontsize=12)
ax2.set_ylabel('scale  s (bits)', color=WHITE, fontsize=12)
ax2.set_title(
    'Morlet scalogram (log10 t)   —   if the notches are self-similar in '
    'log t, they become uniformly spaced here',
    color=WHITE, fontsize=13)
ax2.tick_params(colors=WHITE)
for sp in ax2.spines.values():
    sp.set_color(WHITE)

# Panel 3: 1D notch indicator with peaks marked
ax3 = fig.add_subplot(gs[2])
ax3.set_facecolor(DARK)
t_axis = np.arange(n_bits + 1)
ax3.plot(t_axis, notch_smooth, color=SIGNAL, lw=0.7,
         label=f'notch indicator: mean(−log10|W|²) over '
               f'[{KINK_BAND_LO:.0f}, {KINK_BAND_HI:.0f}], '
               f'smoothed window {NOTCH_SMOOTH}')
ax3.scatter(peaks_kept, notch_smooth[peaks_kept],
            color=ACCENT, s=14, zorder=5,
            label=f'extracted notch peaks ({len(peaks_kept)})')
ax3.axvline(T_FIT_MIN, color=GUIDE, lw=0.6, ls='--',
            label=f't = {T_FIT_MIN} (fit cutoff)')
ax3.set_xlim(0, n_bits)
ax3.set_xlabel('bit position  t', color=WHITE, fontsize=12)
ax3.set_ylabel('notch indicator', color=WHITE, fontsize=12)
ax3.set_title('1D notch indicator with extracted peaks',
              color=WHITE, fontsize=13)
ax3.tick_params(colors=WHITE)
ax3.legend(loc='upper right', fontsize=9, framealpha=0.0,
           labelcolor=WHITE)
for sp in ax3.spines.values():
    sp.set_color(WHITE)

# Panel 4: log(t_k) vs k with the geometric-model fit
ax4 = fig.add_subplot(gs[3])
ax4.set_facecolor(DARK)
k_all = np.arange(1, len(peaks_kept) + 1, dtype=np.float64)
ax4.scatter(k_all, np.log(peaks_kept.astype(np.float64)),
            color=ACCENT, s=20, zorder=5,
            label='notch positions  ln(t_k)')
ax4.plot(k_fit, g_fit_vals, color=GUIDE, lw=1.4,
         label=(f'geometric fit:  ln(t_k) = '
                f'{g_intercept:.2f} + {g_slope:.3f}·k    '
                f'(r = exp(b) = {g_r:.3f}, '
                f'spacing grows {(g_r - 1) * 100:.1f}% per notch)'))
ax4.set_xlabel('notch index  k', color=WHITE, fontsize=12)
ax4.set_ylabel('ln(t_k)', color=WHITE, fontsize=12)
ax4.set_title(
    f'Geometric-spacing test:   '
    f'geometric RSS(log) = {g_rss:.3f},  '
    f'power-law RSS(log) = {p_rss:.3f}   '
    f'(α = {p_slope:.3f})',
    color=WHITE, fontsize=13)
ax4.tick_params(colors=WHITE)
ax4.legend(loc='lower right', fontsize=9, framealpha=0.0,
           labelcolor=WHITE)
for sp in ax4.spines.values():
    sp.set_color(WHITE)

out = os.path.join(_here, f'kink_decompression_n3{OUT_SUFFIX}.png')
plt.savefig(out, dpi=160, facecolor=DARK, bbox_inches='tight')
plt.close()
print(f"  -> {out}")
