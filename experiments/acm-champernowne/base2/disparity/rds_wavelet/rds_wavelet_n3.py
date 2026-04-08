"""
rds_wavelet_n3.py — multi-scale decomposition of n=3 RDS(t).

Continuous wavelet transform of the n=3 binary ACM stream's running
digital sum. The question this is built to answer is: how many
distinct scales of structure exist in RDS(t)? A Morlet CWT
scalogram lays the energy out as a (scale, position) heatmap; the
scale-marginal energy panel below it counts the dominant scales as
peaks in the wavelet power spectrum.

Two signals are decomposed:
  - RDS(t) − linear fit            (the cleanly-detrended raw stream)
  - residual_pe(t) − linear fit    (the doubly-detrended residual)

Both signals have any remaining linear drift removed before CWT, so
the wavelet only sees oscillatory structure, not residual ramps.

Marginal energy is reported with the Torrence-Compo normalization
`Σ|W|² / scale`, which equalizes white noise across scales so that
genuine spectral peaks stand out as local maxima.

Implementation note: scipy 1.15 dropped scipy.signal.cwt and ricker,
and pywt is not available in this sage. The CWT below is implemented
directly via FFT-based convolution with a complex Morlet wavelet at
log-spaced scales.
"""

import sys
import os
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import fftconvolve
from scipy.fft import rfft, rfftfreq

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..'))                              # base2/
sys.path.insert(0, os.path.join(_here, '..', '..', '..', '..', '..', 'core'))    # core/

from acm_core import acm_n_primes


# ── Parameters ──────────────────────────────────────────────────────

N = 3
TARGET_BITS = 300_000      # long enough to give the slow oscillation
                           # ~13 cycles (visible period is ≈ 22k bits)
N_SCALES = 120
SCALE_MIN = 2.0
SCALE_MAX = 50_000.0       # large enough to cover ~50k-period structures
MORLET_W0 = 6.0            # Morlet central frequency (standard)


# ── Helpers (mirroring detrended_rds.py) ────────────────────────────

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


# ── Wavelet primitives ──────────────────────────────────────────────

def morlet_wavelet(n_points, s, w0=MORLET_W0):
    """Discrete complex Morlet wavelet on `n_points` samples at scale
    `s` (in samples). The wavelet is

        ψ_s(t)  =  s^{-1/2} · π^{-1/4} · exp(i w0 t/s) · exp(-(t/s)² / 2)

    centered at the middle of the array. With w0 ≈ 6 the Fourier
    period associated with scale s is approximately

        T  ≈  4π s / (w0 + sqrt(2 + w0²))  ≈  1.03 s

    so 'scale' and 'period' are roughly interchangeable."""
    t = (np.arange(n_points) - (n_points - 1) / 2.0) / s
    norm = (np.pi ** -0.25) / np.sqrt(s)
    return norm * np.exp(1j * w0 * t) * np.exp(-t * t / 2.0)


def cwt_morlet(data, scales, w0=MORLET_W0):
    """Continuous wavelet transform with complex Morlet wavelet,
    FFT-based. Output shape: (len(scales), len(data)) complex."""
    n = len(data)
    out = np.zeros((len(scales), n), dtype=np.complex128)
    for i, s in enumerate(scales):
        n_pts = min(int(10 * s), n)
        if n_pts < 5:
            n_pts = 5
        if n_pts % 2 == 0:
            n_pts += 1
        wavelet = morlet_wavelet(n_pts, s, w0)
        # fftconvolve handles real arrays only; do real and imag separately
        re = fftconvolve(data, wavelet.real, mode='same')
        im = fftconvolve(data, wavelet.imag, mode='same')
        out[i] = re + 1j * im
    return out


def linear_detrend(y):
    """Subtract the least-squares linear fit from a 1D array."""
    x = np.arange(len(y))
    a, b = np.polyfit(x, y, 1)
    return y - (a * x + b)


# ── Generate the n = 3 stream ───────────────────────────────────────

m = v2_of(N)
bits, entries = gen_for_monoid(N, TARGET_BITS)
n_bits = len(bits)

rds = compute_rds(bits).astype(np.float64)
expected_pe = expected_curve_per_entry(entries, n_bits)
residual_pe = rds - expected_pe

# Doubly detrend: linear fit removed from both signals so the wavelet
# only sees oscillatory structure, not residual ramps
rds_detrended = linear_detrend(rds)
residual_detrended = linear_detrend(residual_pe)

print(f"n = {N}")
print(f"  bits = {n_bits}, entries = {len(entries)}")
print(f"  RDS_end = {int(rds[-1]):+d}, residual_pe_end = {residual_pe[-1]:+.1f}")
print(f"  After linear detrending:")
print(f"    rds_detrended      range: {rds_detrended.min():+.1f} .. {rds_detrended.max():+.1f}")
print(f"    residual_detrended range: {residual_detrended.min():+.1f} .. {residual_detrended.max():+.1f}")


# ── CWT ─────────────────────────────────────────────────────────────

scales = np.geomspace(SCALE_MIN, SCALE_MAX, N_SCALES)
print(f"\nComputing Morlet CWT over {N_SCALES} scales "
      f"in [{SCALE_MIN:.1f}, {SCALE_MAX:.1f}]...")

print("  ... CWT of detrended RDS(t)")
cwt_rds = cwt_morlet(rds_detrended, scales)
power_rds = np.abs(cwt_rds) ** 2

print("  ... CWT of detrended residual_pe(t)")
cwt_res = cwt_morlet(residual_detrended, scales)
power_res = np.abs(cwt_res) ** 2

# Wavelet variance: (1/N) Σ |W(s, t)|² — this is the canonical
# Torrence–Compo wavelet power spectrum, comparable across scales.
energy_rds = power_rds.mean(axis=1)
energy_res = power_res.mean(axis=1)

# ── Fourier power spectrum for cross-check ─────────────────────────

print("\nComputing Fourier power spectra for cross-check...")
fft_rds = rfft(rds_detrended)
fft_res = rfft(residual_detrended)
freqs = rfftfreq(n_bits + 1, d=1.0)
fft_power_rds = np.abs(fft_rds) ** 2
fft_power_res = np.abs(fft_res) ** 2
# Drop the DC bin (freq = 0)
freqs_pos = freqs[1:]
periods_pos = 1.0 / freqs_pos
fft_power_rds = fft_power_rds[1:]
fft_power_res = fft_power_res[1:]


# Find peaks in the marginal energy curves (simple local-max search)
def find_peaks_1d(y, min_prominence_frac=0.05):
    y = np.asarray(y)
    n = len(y)
    if n < 3:
        return np.array([], dtype=int)
    is_peak = (y[1:-1] > y[:-2]) & (y[1:-1] > y[2:])
    peak_idx = np.where(is_peak)[0] + 1
    if len(peak_idx) == 0:
        return peak_idx
    threshold = y.max() * min_prominence_frac
    peak_idx = peak_idx[y[peak_idx] >= threshold]
    return peak_idx


peaks_rds = find_peaks_1d(energy_rds, min_prominence_frac=0.05)
peaks_res = find_peaks_1d(energy_res, min_prominence_frac=0.05)

print(f"\nMarginal-energy peaks (≥ 5% of max), TC-normalized:")
print(f"  detrended RDS(t):         {len(peaks_rds)} peaks at scales "
      f"{[round(float(scales[i]), 1) for i in peaks_rds]}")
print(f"  detrended residual_pe(t): {len(peaks_res)} peaks at scales "
      f"{[round(float(scales[i]), 1) for i in peaks_res]}")


# ── Plot ────────────────────────────────────────────────────────────

DARK = '#0a0a0a'
WHITE = 'white'
RDS_COLOR = '#6ec6ff'
PE_COLOR = '#ff6f61'
RES_COLOR = '#88d8b0'
PEAK_COLOR = '#ffcc5c'

fig = plt.figure(figsize=(16, 14), facecolor=DARK)
gs = fig.add_gridspec(
    4, 1,
    height_ratios=[1.0, 1.8, 1.0, 1.0],
    hspace=0.50,
    left=0.07, right=0.97, top=0.95, bottom=0.06,
)


def style(ax):
    ax.set_facecolor(DARK)
    ax.tick_params(colors=WHITE, labelsize=10)
    for spine in ax.spines.values():
        spine.set_color(WHITE)
    ax.grid(True, alpha=0.10, color=WHITE)


# Panel A: detrended RDS(t) and detrended residual_pe(t)
ax0 = fig.add_subplot(gs[0])
style(ax0)
xs = np.arange(len(rds))
ax0.plot(xs, rds_detrended, color=RDS_COLOR, lw=0.8,
         label='RDS(t) − linear fit')
ax0.plot(xs, residual_detrended, color=RES_COLOR, lw=0.8,
         label='residual_pe(t) − linear fit')
ax0.axhline(0, color=WHITE, lw=0.4, alpha=0.4)
ax0.set_ylabel('value', color=WHITE, fontsize=11)
ax0.set_title(f'n = {N},  v₂(n) = {m},  {len(entries)} entries,  '
              f'{n_bits} bits  '
              '(both signals doubly-detrended for the wavelet)',
              color=WHITE, fontsize=13, pad=10)
ax0.set_xlim(0, n_bits)
ax0.legend(loc='upper left', fontsize=9, facecolor=DARK,
           edgecolor='none', labelcolor=WHITE)


def scalogram(ax, power, title, per_scale_norm=False):
    style(ax)
    if per_scale_norm:
        # Each row normalized to its own max so structure at every scale
        # is visible (loses absolute energy comparison across scales).
        row_max = power.max(axis=1, keepdims=True)
        row_max[row_max == 0] = 1.0
        plot_data = power / row_max
        cb_label = '|W|² / max(scale)'
    else:
        plot_data = np.log10(power + 1e-12)
        cb_label = 'log₁₀ |W|²'
    extent = [0, n_bits, scales.min(), scales.max()]
    im = ax.imshow(
        plot_data, aspect='auto', cmap='magma',
        extent=extent, origin='lower',
        interpolation='bilinear',
    )
    ax.set_yscale('log')
    ax.set_ylabel('Morlet scale  s (bits)', color=WHITE, fontsize=11)
    ax.set_title(title, color=WHITE, fontsize=12)
    ax.set_xlim(0, n_bits)
    cb = plt.colorbar(im, ax=ax, fraction=0.018, pad=0.01)
    cb.ax.yaxis.set_tick_params(color=WHITE)
    plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color=WHITE)
    cb.set_label(cb_label, color=WHITE, fontsize=9)
    return im


# Panel B: scalogram of detrended RDS(t), absolute log power
ax1 = fig.add_subplot(gs[1])
scalogram(ax1, power_rds,
          'Morlet scalogram of detrended RDS(t)  '
          '(absolute log power, full dynamic range)',
          per_scale_norm=False)

# Panel C: wavelet variance vs scale (Torrence-Compo)
ax3 = fig.add_subplot(gs[2])
style(ax3)
e_rds_n = energy_rds / energy_rds.max()
e_res_n = energy_res / energy_res.max()
ax3.plot(scales, e_rds_n, color=RDS_COLOR, lw=1.6,
         label='detrended RDS(t)')
ax3.plot(scales, e_res_n, color=RES_COLOR, lw=1.6,
         label='detrended residual_pe(t)')

for i in peaks_rds:
    ax3.plot([scales[i]], [e_rds_n[i]], 'o',
             color=PEAK_COLOR, markersize=8,
             markeredgecolor=RDS_COLOR, markeredgewidth=1.4,
             zorder=5)
for i in peaks_res:
    ax3.plot([scales[i]], [e_res_n[i]], 'o',
             color=PEAK_COLOR, markersize=8,
             markeredgecolor=RES_COLOR, markeredgewidth=1.4,
             zorder=5)

ax3.set_xscale('log')
ax3.set_xlabel('Morlet scale  s (bits)  ≈  Fourier period',
               color=WHITE, fontsize=11)
ax3.set_ylabel('wavelet variance (rel.)',
               color=WHITE, fontsize=11)
ax3.set_title('Wavelet power spectrum '
              '⟨|W(s,·)|²⟩ '
              '(each curve normalized to its own max; '
              f'RDS peaks: {len(peaks_rds)}, residual peaks: {len(peaks_res)})',
              color=WHITE, fontsize=12)
ax3.legend(loc='best', fontsize=9, facecolor=DARK,
           edgecolor='none', labelcolor=WHITE)


# Panel D: Fourier power spectrum (cross-check)
ax4 = fig.add_subplot(gs[3])
style(ax4)
# Plot vs period (= 1/freq)
ax4.loglog(periods_pos, fft_power_rds / fft_power_rds.max(),
           color=RDS_COLOR, lw=1.0, alpha=0.85,
           label='detrended RDS(t)')
ax4.loglog(periods_pos, fft_power_res / fft_power_res.max(),
           color=RES_COLOR, lw=1.0, alpha=0.85,
           label='detrended residual_pe(t)')
ax4.set_xlabel('Fourier period (bits)', color=WHITE, fontsize=11)
ax4.set_ylabel('|FFT|² (rel.)', color=WHITE, fontsize=11)
ax4.set_title('Fourier power spectrum '
              '(cross-check; each curve normalized to its own max)',
              color=WHITE, fontsize=12)
ax4.set_xlim(scales.min(), scales.max())
ax4.legend(loc='best', fontsize=9, facecolor=DARK,
           edgecolor='none', labelcolor=WHITE)


out = os.path.join(_here, 'rds_wavelet_n3.png')
plt.savefig(out, dpi=200, facecolor=DARK)
print(f"\nWrote {out}")
