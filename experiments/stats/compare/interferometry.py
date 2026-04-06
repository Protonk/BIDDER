"""
Interferometry — three ways to detect the difference between ACM and
numpy uniform as sources for digit-frequency experiments.

Panel 1: Interferogram
  ACM addition heatmap minus numpy addition heatmap, diverging colormap.
  Structure = real difference. Snow = indistinguishable.

Panel 2: Power spectrum
  FFT of the digit-1 frequency column from each addition heatmap.
  Peaks above the noise floor = periodic structure in the source.

Panel 3: Consecutive sums (the crispness test)
  Sliding-window sums (preserving order) instead of random draws.
  The ACM sawtooth is deterministic; numpy is stochastic. Ordering
  is where the difference lives.
"""

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, ROOT)

import numpy as np
import matplotlib.pyplot as plt
from acm_core import acm_champernowne_array, acm_first_digit_array

N = 10000
n_steps = 500
n_samples = 8000

print("Building sources...")
acm_reals = acm_champernowne_array(N)
acm_log = np.log10(acm_reals)

rng_source = np.random.default_rng(99)
py_reals = rng_source.uniform(1.1, 2.0, size=N)
py_log = np.log10(py_reals)


def first_digits_from_log_fracs(fracs):
    return np.minimum((10**fracs + 1e-9).astype(int), 9)


# =================================================================
# Build random-draw addition heatmaps (same as shutter_dual)
# =================================================================

def build_addition_heat(reals, n_steps, n_samples, seed):
    rng = np.random.default_rng(seed)
    heat = np.zeros((n_steps, 9))
    for i, k in enumerate(range(1, n_steps + 1)):
        indices = rng.integers(0, len(reals), size=(n_samples, k))
        sums = np.sum(reals[indices], axis=1)
        fds = acm_first_digit_array(sums)
        for d in range(1, 10):
            heat[i, d - 1] = np.sum(fds == d) / n_samples
    return heat

print("Random-draw heatmaps...")
print("  ACM...")
acm_heat = build_addition_heat(acm_reals, n_steps, n_samples, 42)
print("  numpy...")
py_heat = build_addition_heat(py_reals, n_steps, n_samples, 42)


# =================================================================
# Build consecutive-sum (sliding window) heatmaps
# =================================================================

def build_consecutive_heat(reals, ks):
    """Sliding-window sums preserve ordering."""
    N = len(reals)
    cumsum = np.concatenate([[0], np.cumsum(reals)])
    heat = np.zeros((len(ks), 9))
    for i, k in enumerate(ks):
        n_windows = N - k + 1
        sums = cumsum[k:k + n_windows] - cumsum[:n_windows]
        log_sums = np.log10(sums)
        fracs = log_sums - np.floor(log_sums)
        fds = first_digits_from_log_fracs(fracs)
        for d in range(1, 10):
            heat[i, d - 1] = np.sum(fds == d) / n_windows
    return heat

ks_consec = np.unique(np.geomspace(1, 5000, 300).astype(int))

print("Consecutive-sum heatmaps...")
print("  ACM...")
acm_consec = build_consecutive_heat(acm_reals, ks_consec)
print("  numpy...")
py_consec = build_consecutive_heat(py_reals, ks_consec)


# =================================================================
# Plot
# =================================================================

print("Plotting...")
fig = plt.figure(figsize=(20, 16))
fig.patch.set_facecolor('#0a0a0a')

# --- Panel 1: Interferogram ---
ax1 = fig.add_subplot(2, 2, 1)
ax1.set_facecolor('#0a0a0a')
diff = acm_heat - py_heat
vlim = np.max(np.abs(diff)) * 0.8
ax1.imshow(diff, aspect='auto', cmap='RdBu_r',
           interpolation='bilinear', origin='lower',
           extent=[0.5, 9.5, 1, n_steps],
           vmin=-vlim, vmax=vlim)
ax1.set_xticks(range(1, 10))
ax1.set_xlabel('first digit', color='white', fontsize=10)
ax1.set_ylabel('additions', color='white', fontsize=10)
ax1.set_title('Interferogram (ACM - numpy)', color='white', fontsize=12, pad=10)
ax1.tick_params(colors='white')

# --- Panel 2: Power spectrum of digit-1 column ---
ax2 = fig.add_subplot(2, 2, 2)
ax2.set_facecolor('#0a0a0a')

# FFT of digit-1 frequency time series
acm_d1 = acm_heat[:, 0]
py_d1 = py_heat[:, 0]
freqs = np.fft.rfftfreq(n_steps)
acm_psd = np.abs(np.fft.rfft(acm_d1 - acm_d1.mean()))**2
py_psd = np.abs(np.fft.rfft(py_d1 - py_d1.mean()))**2

ax2.semilogy(freqs[1:], acm_psd[1:], linewidth=0.8, color='#ffcc5c',
             alpha=0.9, label='ACM')
ax2.semilogy(freqs[1:], py_psd[1:], linewidth=0.8, color='#6ec6ff',
             alpha=0.9, label='numpy')
ax2.set_xlabel('frequency (cycles / addition step)', color='white', fontsize=10)
ax2.set_ylabel('power', color='white', fontsize=10)
ax2.set_title('Power spectrum (digit 1)', color='white', fontsize=12, pad=10)
ax2.tick_params(colors='white')
ax2.legend(fontsize=10, framealpha=0.3, labelcolor='white', facecolor='#1a1a1a')

# --- Panel 3: Consecutive sums — ACM ---
ax3 = fig.add_subplot(2, 2, 3)
ax3.set_facecolor('#0a0a0a')
ax3.imshow(acm_consec, aspect='auto', cmap='inferno',
           interpolation='bilinear', origin='lower',
           extent=[0.5, 9.5, ks_consec[0], ks_consec[-1]],
           vmin=0, vmax=0.5)
ax3.set_xticks(range(1, 10))
ax3.set_xlabel('first digit', color='white', fontsize=10)
ax3.set_ylabel('window size', color='white', fontsize=10)
ax3.set_title('Consecutive sums — ACM', color='white', fontsize=12, pad=10)
ax3.tick_params(colors='white')

# --- Panel 4: Consecutive sums — numpy ---
ax4 = fig.add_subplot(2, 2, 4)
ax4.set_facecolor('#0a0a0a')
ax4.imshow(py_consec, aspect='auto', cmap='inferno',
           interpolation='bilinear', origin='lower',
           extent=[0.5, 9.5, ks_consec[0], ks_consec[-1]],
           vmin=0, vmax=0.5)
ax4.set_xticks(range(1, 10))
ax4.set_xlabel('first digit', color='white', fontsize=10)
ax4.set_ylabel('window size', color='white', fontsize=10)
ax4.set_title('Consecutive sums — numpy', color='white', fontsize=12, pad=10)
ax4.tick_params(colors='white')

plt.subplots_adjust(wspace=0.15, hspace=0.2)
plt.savefig('interferometry.png', dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
print("-> interferometry.png")
