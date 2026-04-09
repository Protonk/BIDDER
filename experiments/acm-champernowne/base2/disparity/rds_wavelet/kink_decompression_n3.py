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
from scipy import stats as scipy_stats

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

# Affine: t_k = a + b*k
a_slope, a_intercept = np.polyfit(k_fit, peaks_fit, 1)
a_fit_vals = a_intercept + a_slope * k_fit
a_resid = peaks_fit - a_fit_vals
a_rss = float(np.sum(a_resid ** 2))
print(f"  affine:    t_k = {a_intercept:.1f} + {a_slope:.1f}·k")
print(f"             RSS(t) = {a_rss:.1f}")

if g_rss < p_rss:
    winner = f"geometric (r = {g_r:.3f})"
else:
    winner = f"power-law (α = {p_slope:.3f})"
print(f"  → better fit (in log space): {winner}")

# ── Same-units fit comparison: all three models in t space ──────────
#
# RSS_pow and RSS_geom are computed in log space; RSS_aff is computed
# in t space. The log-space affine analogue is ill-defined when
# a_intercept < 0 (true for several runs). To get a single common
# error scale we map all three model fits back to t and recompute
# RSS in t-units (bits²). RMS = √(RSS/K) is then directly readable as
# "RMS position error per notch in bits."

geom_fit_t = np.exp(g_fit_vals)
pow_fit_t  = np.exp(p_fit_vals)
aff_fit_t  = a_fit_vals

g_rss_t = float(np.sum((peaks_fit - geom_fit_t) ** 2))
p_rss_t = float(np.sum((peaks_fit - pow_fit_t)  ** 2))
a_rss_t = a_rss

K_fit = float(len(peaks_fit))
g_rms_t = math.sqrt(g_rss_t / K_fit)
p_rms_t = math.sqrt(p_rss_t / K_fit)
a_rms_t = math.sqrt(a_rss_t / K_fit)

print(f"\nSame-units comparison (all three models, in t space):")
print(f"  geometric:   RSS_t = {g_rss_t:.3e}   RMS_t = {g_rms_t:.0f} bits")
print(f"  power law:   RSS_t = {p_rss_t:.3e}   RMS_t = {p_rms_t:.0f} bits")
print(f"  affine:      RSS_t = {a_rss_t:.3e}   RMS_t = {a_rms_t:.0f} bits")
print(f"  RMS_aff / b = {a_rms_t / a_slope:.3f}  "
      f"(per-notch position scatter relative to mean gap)")

gap_k = k_fit[:-1]
gaps = np.diff(peaks_fit)
ratios = peaks_fit[1:] / peaks_fit[:-1]


# ── Gap-sequence diagnostics ────────────────────────────────────────

print("\nGap sequence Δt_k = t_(k+1) - t_k diagnostics:")
n_gaps = len(gaps)

if n_gaps >= 4:
    gap_mean = float(np.mean(gaps))
    gap_std  = float(np.std(gaps, ddof=1))
    gap_skew = float(scipy_stats.skew(gaps))
    gap_kurt = float(scipy_stats.kurtosis(gaps))   # Fisher: 0 = Gaussian
    print(f"  count        = {n_gaps}")
    print(f"  mean         = {gap_mean:.1f} bits")
    print(f"  std          = {gap_std:.1f} bits  (CV = {gap_std/gap_mean:.3f})")
    print(f"  skewness     = {gap_skew:+.3f}")
    print(f"  excess kurt  = {gap_kurt:+.3f}")
else:
    gap_mean = gap_std = gap_skew = gap_kurt = float('nan')

# Lag-1 autocorrelation
if n_gaps >= 4:
    gap_acf1 = float(np.corrcoef(gaps[:-1], gaps[1:])[0, 1])
    print(f"  lag-1 ACF    = {gap_acf1:+.3f}")
else:
    gap_acf1 = float('nan')

# Drift: linear regression of Δt_k against gap index
if n_gaps >= 4:
    drift_slope, drift_intercept = np.polyfit(gap_k, gaps, 1)
    drift_slope = float(drift_slope)
    drift_intercept = float(drift_intercept)
    drift_total = drift_slope * (gap_k[-1] - gap_k[0])
    drift_frac = drift_total / gap_mean
    print(f"  drift slope  = {drift_slope:+.3f} bits per notch index")
    print(f"  total drift over k range = {drift_total:+.0f} bits "
          f"({drift_frac*100:+.1f}% of mean gap)")
else:
    drift_slope = drift_intercept = drift_total = drift_frac = float('nan')

# FFT of de-meaned gap sequence (only meaningful for n_gaps ≳ 30)
if n_gaps >= 30:
    gap_centered = gaps - gap_mean
    fft = np.fft.rfft(gap_centered)
    fft_power = np.abs(fft) ** 2
    fft_freqs = np.fft.rfftfreq(n_gaps, d=1.0)   # cycles per notch
    # Drop DC
    fft_power_nodc = fft_power.copy()
    fft_power_nodc[0] = 0.0
    peak_bin = int(np.argmax(fft_power_nodc))
    peak_freq = float(fft_freqs[peak_bin])
    peak_period = (1.0 / peak_freq) if peak_freq > 0 else float('inf')
    peak_strength = float(fft_power_nodc[peak_bin] / np.sum(fft_power_nodc))
    print(f"  FFT peak     = {peak_freq:.4f} cyc/notch  "
          f"(period ≈ {peak_period:.1f} notches, "
          f"power frac = {peak_strength*100:.1f}%)")
else:
    fft = None
    fft_power = None
    fft_freqs = None
    peak_freq = peak_period = peak_strength = float('nan')


# ── Distribution shape tests (for the Three Distance Theorem
#    signature: is the gap distribution Gaussian, or does it have
#    structural multimodality?) ────────────────────────────────────

print("\nGap distribution shape tests:")

if n_gaps >= 30:
    # KS test against best-fit Gaussian
    gauss_cdf = lambda x: scipy_stats.norm.cdf(x, loc=gap_mean, scale=gap_std)
    ks_g = scipy_stats.kstest(gaps, gauss_cdf)
    ks_g_stat = float(ks_g.statistic)
    ks_g_p = float(ks_g.pvalue)
    print(f"  KS vs Normal(μ={gap_mean:.0f}, σ={gap_std:.0f}):  "
          f"D = {ks_g_stat:.4f}, p = {ks_g_p:.3e}")

    # KS test against best-fit lognormal
    if np.all(gaps > 0):
        log_gaps = np.log(gaps)
        ln_mu = float(np.mean(log_gaps))
        ln_sigma = float(np.std(log_gaps, ddof=1))
        lnorm_cdf = lambda x: scipy_stats.norm.cdf(np.log(x), loc=ln_mu, scale=ln_sigma)
        ks_l = scipy_stats.kstest(gaps, lnorm_cdf)
        ks_l_stat = float(ks_l.statistic)
        ks_l_p = float(ks_l.pvalue)
        print(f"  KS vs LogNormal(μ={ln_mu:.3f}, σ={ln_sigma:.3f}):  "
              f"D = {ks_l_stat:.4f}, p = {ks_l_p:.3e}")
    else:
        ks_l_stat = ks_l_p = float('nan')

    # KDE-based mode detection on a fine grid.
    # Default 'scott' bandwidth (~σ · n^(-1/5)) over-smooths narrow
    # clusters, so use a tighter bandwidth scaled to ~10% of the
    # data std. Catches narrow modes as well as broad ones.
    bw = 0.10
    kde = scipy_stats.gaussian_kde(gaps, bw_method=bw)
    grid = np.linspace(gaps.min(), gaps.max(), 1200)
    density = kde(grid)
    # Local maxima of the smoothed density, with a low prominence
    # threshold so that secondary modes survive.
    mode_idx, mode_props = find_peaks(density,
                                      prominence=density.max() * 0.03)
    mode_locations = grid[mode_idx]
    mode_heights = density[mode_idx] / density.max()
    print(f"  KDE (bw_method={bw}) modes "
          f"(prominence ≥ 3% of max density): "
          f"{len(mode_locations)} mode(s)")
    for loc, h in zip(mode_locations, mode_heights):
        # How many gaps fall within ±σ_local of each mode?
        local_window = max(50, int(0.05 * (gaps.max() - gaps.min())))
        n_in_window = int(np.sum(np.abs(gaps - loc) <= local_window))
        print(f"    at Δt = {loc:6.0f} bits   "
              f"(relative height {h:.3f}, "
              f"~{n_in_window} gaps within ±{local_window})")

    # ── Lattice fit on the dominant KDE modes ──────────────────────
    #
    # Post-hoc: if at least three modes were found, fit
    #
    #     Δt(n)  =  a + n · b      for n = 0, 1, 2
    #
    # by ordinary least squares against the first three KDE mode
    # locations (sorted ascending). Report per-mode residuals against
    # this lattice for the first four modes, so that any "fourth rung"
    # claim can be checked against its actual deviation rather than
    # being read off the histogram by eye.
    #
    # The fit is post-hoc by construction: it fits 2 free parameters
    # to 3 points and so has 1 residual degree of freedom. The
    # absolute residual scale is what to look at; the per-rung
    # residual table is what KINK-INVESTIGATION.md cites.
    if len(mode_locations) >= 3:
        L = np.sort(mode_locations)[:3].astype(np.float64)
        n_lat = np.array([0.0, 1.0, 2.0])
        b_lat, a_lat = np.polyfit(n_lat, L, 1)
        max_resid = float(np.max(np.abs(L - (a_lat + n_lat * b_lat))))
        max_resid_pct = 100.0 * max_resid / b_lat
        print(f"\n  Lattice fit  Δt = a + n·b  on first 3 KDE modes:")
        print(f"    a = {a_lat:.2f} bits   b = {b_lat:.2f} bits")
        print(f"    max |residual| over n=0..2: {max_resid:.2f} bits "
              f"({max_resid_pct:.2f}% of click period)")
        print(f"    per-mode (first 4 KDE modes vs lattice prediction):")
        sorted_locs = np.sort(mode_locations)
        for k in range(min(4, len(sorted_locs))):
            pred = a_lat + k * b_lat
            obs  = float(sorted_locs[k])
            resid = obs - pred
            resid_pct = 100.0 * resid / b_lat
            tag = "fit" if k < 3 else "extrapolation"
            print(f"      n={k} ({tag:13s}): "
                  f"pred={pred:8.2f}  obs={obs:8.2f}  "
                  f"resid={resid:+7.2f}  ({resid_pct:+5.2f}% of b)")

    # Save gaps to CSV for any downstream offline analysis
    csv_out = os.path.join(_here, f'kink_gaps{OUT_SUFFIX}.csv')
    with open(csv_out, 'w') as f:
        f.write('gap_index,delta_t\n')
        for i, g in enumerate(gaps):
            f.write(f'{i},{g}\n')
    print(f"  gap CSV: {csv_out}")
else:
    ks_g_stat = ks_g_p = ks_l_stat = ks_l_p = float('nan')
    kde = None
    grid = None
    density = None
    mode_locations = np.array([])
    mode_heights = np.array([])


# ── Render 4-panel figure ──────────────────────────────────────────

print("\nRendering kink_decompression_n3.png...")

DARK = '#0a0a0a'
WHITE = 'white'
ACCENT = '#ffcc5c'
SIGNAL = '#6ec6ff'
GUIDE = '#88d8b0'
GEOM = '#ff6f61'

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


# ── Render direct spacing diagnostic figure ─────────────────────────

print("\nRendering kink_spacing_diagnostic_n3.png...")

fig = plt.figure(figsize=(16, 16), facecolor=DARK)
gs = fig.add_gridspec(4, 1, hspace=0.48,
                      height_ratios=[3.0, 2.3, 2.1, 2.1])

band_scales = scales[band_mask]
band_log_power = np.log10(band_power + 1e-12)

# Panel 1: band-cropped scalogram with fitted peaks marked
ax1 = fig.add_subplot(gs[0])
ax1.set_facecolor(DARK)
extent_band = [0, n_bits, band_scales.min(), band_scales.max()]
ax1.imshow(band_log_power, aspect='auto', cmap='magma',
           extent=extent_band, origin='lower', interpolation='bilinear')
ax1.set_yscale('log')
for t in peaks_fit:
    ax1.axvline(float(t), color=ACCENT, lw=0.55, alpha=0.35)
ax1.axvline(T_FIT_MIN, color=WHITE, lw=0.8, ls='--', alpha=0.8)
ax1.set_xlim(0, n_bits)
ax1.set_xlabel('bit position  t', color=WHITE, fontsize=12)
ax1.set_ylabel('scale  s (bits)', color=WHITE, fontsize=12)
ax1.set_title(
    f'Band-cropped scalogram [{KINK_BAND_LO:.0f}, {KINK_BAND_HI:.0f}] '
    f'with fitted notch positions marked',
    color=WHITE, fontsize=13)
ax1.tick_params(colors=WHITE)
for sp in ax1.spines.values():
    sp.set_color(WHITE)

# Panel 2: t_k vs k with affine and geometric overlays
ax2 = fig.add_subplot(gs[1])
ax2.set_facecolor(DARK)
ax2.scatter(k_fit, peaks_fit, color=ACCENT, s=26, zorder=5,
            label='fitted notch positions  t_k')
ax2.plot(k_fit, a_fit_vals, color=GUIDE, lw=2.0,
         label=(f'affine fit:  t_k = {a_intercept:.0f} + {a_slope:.1f}·k'))
ax2.plot(k_fit, geom_fit_t, color=GEOM, lw=1.6, ls='--',
         label=(f'geometric fit mapped back to t:  '
                f't_k = exp({g_intercept:.2f} + {g_slope:.3f}·k)'))
ax2.set_xlabel('notch index  k', color=WHITE, fontsize=12)
ax2.set_ylabel('position  t_k', color=WHITE, fontsize=12)
ax2.set_title(
    'Peak positions on linear t: affine should look straight here; '
    'geometric should bend upward',
    color=WHITE, fontsize=13)
ax2.tick_params(colors=WHITE)
ax2.legend(loc='upper left', fontsize=9, framealpha=0.0,
           labelcolor=WHITE)
for sp in ax2.spines.values():
    sp.set_color(WHITE)

# Panel 3: successive gaps
ax3 = fig.add_subplot(gs[2])
ax3.set_facecolor(DARK)
ax3.plot(gap_k, gaps, color=SIGNAL, lw=1.0, alpha=0.9)
ax3.scatter(gap_k, gaps, color=ACCENT, s=18, zorder=5,
            label='observed gaps  Δt_k')
ax3.axhline(a_slope, color=GUIDE, lw=1.8,
            label=f'affine benchmark: constant gap b = {a_slope:.1f}')
ax3.set_xlabel('gap index  k', color=WHITE, fontsize=12)
ax3.set_ylabel('Δt_k = t_(k+1) - t_k', color=WHITE, fontsize=12)
ax3.set_title(
    'Successive gaps: an affine model predicts a flat sequence',
    color=WHITE, fontsize=13)
ax3.tick_params(colors=WHITE)
ax3.legend(loc='upper right', fontsize=9, framealpha=0.0,
           labelcolor=WHITE)
for sp in ax3.spines.values():
    sp.set_color(WHITE)

# Panel 4: successive ratios
ax4 = fig.add_subplot(gs[3])
ax4.set_facecolor(DARK)
ax4.plot(gap_k, ratios, color=GEOM, lw=1.0, alpha=0.9)
ax4.scatter(gap_k, ratios, color=ACCENT, s=18, zorder=5,
            label='observed ratios  ρ_k')
ax4.axhline(g_r, color=GEOM, lw=1.8, ls='--',
            label=f'geometric benchmark: constant ratio r = {g_r:.4f}')
ax4.set_xlabel('ratio index  k', color=WHITE, fontsize=12)
ax4.set_ylabel('ρ_k = t_(k+1) / t_k', color=WHITE, fontsize=12)
ax4.set_title(
    'Successive ratios: a geometric model predicts a flat sequence',
    color=WHITE, fontsize=13)
ax4.tick_params(colors=WHITE)
ax4.legend(loc='upper right', fontsize=9, framealpha=0.0,
           labelcolor=WHITE)
for sp in ax4.spines.values():
    sp.set_color(WHITE)

out = os.path.join(_here, f'kink_spacing_diagnostic_n3{OUT_SUFFIX}.png')
plt.savefig(out, dpi=160, facecolor=DARK, bbox_inches='tight')
plt.close()
print(f"  -> {out}")


# ── Render gap-sequence diagnostic figure ───────────────────────────

print("\nRendering kink_gap_diagnostic_n3.png...")

fig = plt.figure(figsize=(16, 14), facecolor=DARK)
gs = fig.add_gridspec(2, 2, hspace=0.42, wspace=0.28)

# Panel A: histogram of Δt_k with Gaussian overlay, KDE, and mode markers
axA = fig.add_subplot(gs[0, 0])
axA.set_facecolor(DARK)
if n_gaps >= 4:
    n_bins = max(8, min(40, int(np.sqrt(n_gaps) * 2)))
    counts, edges, _ = axA.hist(gaps, bins=n_bins, color=SIGNAL,
                                edgecolor=DARK, alpha=0.85,
                                label=f'observed gaps (n = {n_gaps})')
    # Gaussian overlay matched to mean and std
    x_g = np.linspace(edges[0], edges[-1], 400)
    bin_w = edges[1] - edges[0]
    g_pdf = (1.0 / (gap_std * math.sqrt(2 * math.pi))) * \
            np.exp(-0.5 * ((x_g - gap_mean) / gap_std) ** 2)
    axA.plot(x_g, g_pdf * n_gaps * bin_w,
             color=GEOM, lw=1.6,
             label=f'Normal(μ={gap_mean:.0f}, σ={gap_std:.0f})')
    # KDE overlay
    if n_gaps >= 30 and density is not None:
        # Scale KDE so that integral over the bins matches n_gaps
        kde_y = density * n_gaps * bin_w
        axA.plot(grid, kde_y, color=ACCENT, lw=1.4,
                 label=f'KDE  ({len(mode_locations)} mode(s))')
        # Mark KDE-detected modes
        for loc in mode_locations:
            axA.axvline(float(loc), color=ACCENT, lw=0.8, ls=':',
                        alpha=0.7)
    axA.axvline(gap_mean, color=GUIDE, lw=1.0, ls='--',
                label=f'mean = {gap_mean:.0f}')
axA.set_xlabel('Δt_k  (bits)', color=WHITE, fontsize=12)
axA.set_ylabel('count', color=WHITE, fontsize=12)
ks_label = (f'KS-Normal p = {ks_g_p:.2e}'
            if not math.isnan(ks_g_p) else '')
axA.set_title(
    f'Gap distribution  (skew {gap_skew:+.2f}, ex-kurt {gap_kurt:+.2f}, '
    f'{ks_label})',
    color=WHITE, fontsize=12)
axA.tick_params(colors=WHITE)
axA.legend(loc='upper right', fontsize=9, framealpha=0.0,
           labelcolor=WHITE)
for sp in axA.spines.values():
    sp.set_color(WHITE)

# Panel B: drift — Δt_k vs k with linear-regression overlay
axB = fig.add_subplot(gs[0, 1])
axB.set_facecolor(DARK)
axB.scatter(gap_k, gaps, color=ACCENT, s=14, zorder=5,
            label='observed gaps  Δt_k')
axB.axhline(gap_mean, color=GUIDE, lw=1.0, ls='--',
            label=f'mean gap = {gap_mean:.0f}')
if n_gaps >= 4:
    axB.plot(gap_k, drift_intercept + drift_slope * gap_k,
             color=GEOM, lw=1.4,
             label=(f'drift fit: slope = {drift_slope:+.2f}, '
                    f'total = {drift_total:+.0f} '
                    f'({drift_frac*100:+.1f}% of mean)'))
axB.set_xlabel('gap index  k', color=WHITE, fontsize=12)
axB.set_ylabel('Δt_k  (bits)', color=WHITE, fontsize=12)
axB.set_title('Drift in gaps  (slope ≠ 0 ⇒ non-stationary mean gap)',
              color=WHITE, fontsize=13)
axB.tick_params(colors=WHITE)
axB.legend(loc='upper right', fontsize=9, framealpha=0.0,
           labelcolor=WHITE)
for sp in axB.spines.values():
    sp.set_color(WHITE)

# Panel C: autocorrelation function of Δt_k
axC = fig.add_subplot(gs[1, 0])
axC.set_facecolor(DARK)
if n_gaps >= 6:
    max_lag = max(4, min(40, n_gaps // 4))
    lags = np.arange(0, max_lag + 1)
    g_centered = gaps - gap_mean
    var = float(np.dot(g_centered, g_centered))
    acf_vals = []
    for lag in lags:
        if lag == 0:
            acf_vals.append(1.0)
        else:
            num = float(np.dot(g_centered[:-lag], g_centered[lag:]))
            acf_vals.append(num / var)
    acf_vals = np.array(acf_vals)
    # ±2/√n approximate 95% confidence band for white noise
    conf = 2.0 / math.sqrt(n_gaps)
    axC.bar(lags, acf_vals, color=SIGNAL, width=0.7, alpha=0.85)
    axC.axhline(0.0, color=WHITE, lw=0.6)
    axC.axhline(+conf, color=GUIDE, lw=0.8, ls='--',
                label=f'±2/√n  ≈ ±{conf:.2f}')
    axC.axhline(-conf, color=GUIDE, lw=0.8, ls='--')
    axC.set_xlim(-0.5, max_lag + 0.5)
axC.set_xlabel('lag', color=WHITE, fontsize=12)
axC.set_ylabel('autocorrelation', color=WHITE, fontsize=12)
axC.set_title(
    f'ACF of Δt_k  (lag-1 = {gap_acf1:+.3f})',
    color=WHITE, fontsize=13)
axC.tick_params(colors=WHITE)
axC.legend(loc='upper right', fontsize=9, framealpha=0.0,
           labelcolor=WHITE)
for sp in axC.spines.values():
    sp.set_color(WHITE)

# Panel D: FFT power spectrum of de-meaned Δt_k
axD = fig.add_subplot(gs[1, 1])
axD.set_facecolor(DARK)
if n_gaps >= 30 and fft_power is not None:
    axD.plot(fft_freqs[1:], fft_power[1:],
             color=SIGNAL, lw=1.0)
    axD.axvline(peak_freq, color=GEOM, lw=1.2, ls='--',
                label=(f'peak: {peak_freq:.4f} cyc/notch '
                       f'(period {peak_period:.1f}, '
                       f'{peak_strength*100:.1f}% of power)'))
    axD.set_xlim(0, fft_freqs[-1])
    axD.set_xlabel('frequency  (cycles per notch)',
                   color=WHITE, fontsize=12)
    axD.set_ylabel('|FFT(Δt_k − mean)|²',
                   color=WHITE, fontsize=12)
else:
    axD.text(0.5, 0.5,
             f'n_gaps = {n_gaps} < 30\nFFT skipped',
             color=WHITE, ha='center', va='center',
             transform=axD.transAxes, fontsize=12)
    axD.set_xticks([])
    axD.set_yticks([])
axD.set_title('FFT of de-meaned gaps  (peak ≠ DC ⇒ hidden period)',
              color=WHITE, fontsize=13)
axD.tick_params(colors=WHITE)
if n_gaps >= 30:
    axD.legend(loc='upper right', fontsize=9, framealpha=0.0,
               labelcolor=WHITE)
for sp in axD.spines.values():
    sp.set_color(WHITE)

out = os.path.join(_here, f'kink_gap_diagnostic_n3{OUT_SUFFIX}.png')
plt.savefig(out, dpi=160, facecolor=DARK, bbox_inches='tight')
plt.close()
print(f"  -> {out}")
