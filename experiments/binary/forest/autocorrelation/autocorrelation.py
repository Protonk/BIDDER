"""
autocorrelation.py — how far do correlations reach in the binary stream?

Compute the autocorrelation function of the binary Champernowne stream
(mapping 0 -> -1, 1 -> +1) for lags tau = 1..MAX_LAG. Plot for several
monoids. Entry boundaries create periodic structure; the autocorrelation
measures how that structure propagates across distances.

For a fair coin, autocorrelation is zero at all lags. Departures from
zero are the algebra's signature.
"""

import sys, os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..'))             # binary/
sys.path.insert(0, os.path.join(_here, '..', '..', '..', 'core'))  # core/

import numpy as np
import matplotlib.pyplot as plt
from binary_core import binary_stream


MAX_LAG = 400
N_PRIMES = 4000   # enough entries to get a long stream

MONOIDS = [3, 7, 2, 4, 8, 16]
COLORS = {
    3:  '#88d8b0',
    7:  '#6ec6ff',
    2:  '#ffcc5c',
    4:  '#c49bff',
    8:  '#ff6f61',
    16: '#ff9966',
}


def autocorr(bits, max_lag):
    """
    Normalized autocorrelation of a +/-1 stream.

    R(tau) = (1/N) * sum_t s(t) * s(t + tau)

    where s = 2*bit - 1. Normalized by R(0) so R(0) = 1.
    Uses FFT for speed.
    """
    s = 2.0 * np.array(bits, dtype=float) - 1.0
    n = len(s)
    # FFT-based autocorrelation
    ft = np.fft.rfft(s, n=2 * n)
    ac = np.fft.irfft(ft * np.conj(ft))[:n]
    ac /= ac[0]  # normalize so R(0) = 1
    return ac[1:max_lag + 1]  # lags 1..max_lag


def avg_entry_length(n, count=500):
    """Average bit-length of the first `count` n-primes of monoid n."""
    from acm_core import acm_n_primes
    primes = acm_n_primes(n, count)
    return np.mean([p.bit_length() for p in primes])


# ── Compute ──────────────────────────────────────────────────────────

print("Computing autocorrelations...")
results = {}
avg_lens = {}

for n in MONOIDS:
    print(f"  n = {n}...")
    bits = binary_stream(n, count=N_PRIMES)
    print(f"    stream length: {len(bits)} bits")
    results[n] = autocorr(bits, MAX_LAG)
    avg_lens[n] = avg_entry_length(n, count=N_PRIMES)
    print(f"    avg entry length: {avg_lens[n]:.1f} bits")


# ── Plot ─────────────────────────────────────────────────────────────

print("Plotting...")

fig, axes = plt.subplots(len(MONOIDS), 1, figsize=(18, 3 * len(MONOIDS)),
                         sharex=True, sharey=True)
fig.patch.set_facecolor('#0a0a0a')

lags = np.arange(1, MAX_LAG + 1)

for ax, n in zip(axes, MONOIDS):
    ax.set_facecolor('#0a0a0a')
    ac = results[n]

    ax.bar(lags, ac, width=1.0, color=COLORS[n], alpha=0.8,
           edgecolor='none')
    ax.axhline(y=0, color='white', linewidth=0.3, alpha=0.3)

    # Mark multiples of average entry length
    avg_l = avg_lens[n]
    for k in range(1, int(MAX_LAG / avg_l) + 1):
        pos = k * avg_l
        if pos <= MAX_LAG:
            ax.axvline(x=pos, color='white', linewidth=0.4,
                       alpha=0.2, linestyle=':')

    # 95% confidence band for white noise
    stream_len = len(binary_stream(n, count=100))  # rough estimate
    band = 1.96 / np.sqrt(len(results[n]) * 10)  # conservative
    ax.axhline(y=band, color='#ff6f61', linewidth=0.3, alpha=0.3,
               linestyle='--')
    ax.axhline(y=-band, color='#ff6f61', linewidth=0.3, alpha=0.3,
               linestyle='--')

    v2 = 0
    tmp = n
    while tmp % 2 == 0:
        v2 += 1
        tmp //= 2

    ax.set_ylabel(f'n={n}\n$\\nu_2$={v2}', color='white', fontsize=10,
                  rotation=0, labelpad=50, va='center')
    ax.tick_params(colors='white', labelsize=8)
    for spine in ax.spines.values():
        spine.set_color('#333')

axes[-1].set_xlabel('lag $\\tau$ (bits)', color='white', fontsize=11)
axes[0].set_title(
    'Autocorrelation of binary Champernowne streams',
    color='white', fontsize=14, pad=10)

plt.tight_layout()
plt.savefig('autocorrelation.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> autocorrelation.png")


# ── Summary: peak lags ───────────────────────────────────────────────

print("\nTop-5 autocorrelation peaks per monoid:")
for n in MONOIDS:
    ac = results[n]
    top_idx = np.argsort(np.abs(ac))[-5:][::-1]
    peaks = [(i + 1, ac[i]) for i in top_idx]
    avg_l = avg_lens[n]
    print(f"  n={n} (avg entry len {avg_l:.1f}):")
    for lag, val in peaks:
        ratio = lag / avg_l
        print(f"    lag={lag:4d}  R={val:+.6f}  lag/avg_len={ratio:.2f}")
