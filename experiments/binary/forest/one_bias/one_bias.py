"""
one_bias.py — the running fraction of 1-bits in binary Champernowne streams

For several monoids, track the cumulative fraction of 1-bits as n-primes
are concatenated. Overlay the theoretical prediction (d+1)/(2d) for
all d-bit integers as a stepped function.

The gap between theory and actuality is the sieve's fingerprint: what
does n-primality do to bit balance compared to raw counting?

Two races:
  - For n=2: trailing 0 (from v_2=1) vs. penultimate 1 (from k odd).
    Which wins in the global balance?
  - For odd n: no forced bits at all. Does the sieve still tilt the
    balance, or does it wash out?
"""

import sys, os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..'))             # binary/
sys.path.insert(0, os.path.join(_here, '..', '..', '..', 'core'))  # core/

import numpy as np
import matplotlib.pyplot as plt
from acm_core import acm_n_primes


N_PRIMES = 3000   # entries per monoid

# Monoids: two odd (no forced bits), two with v_2=1, two with higher v_2
MONOIDS = [3, 7, 2, 6, 4, 16]
COLORS  = {
    3:  '#88d8b0',   # green
    7:  '#6ec6ff',   # blue
    2:  '#ffcc5c',   # yellow
    6:  '#ff6f61',   # red
    4:  '#c49bff',   # purple
    16: '#ff9966',   # orange
}


def theoretical_step(total_bits_by_entry):
    """
    Build the theoretical (d+1)/(2d) stepped curve.

    For each entry, the bit-length d determines the theoretical
    1-fraction if entries were all d-bit integers drawn uniformly.
    The stepped curve is the running average of these per-entry
    predictions, weighted by the number of bits each entry contributes.
    """
    curve = np.empty(len(total_bits_by_entry))
    cum_ones = 0.0
    cum_bits = 0
    for i, d in enumerate(total_bits_by_entry):
        # A random d-bit integer has expected 1-fraction (d+1)/(2d)
        expected_ones = d * (d + 1.0) / (2.0 * d)
        cum_ones += expected_ones
        cum_bits += d
        curve[i] = cum_ones / cum_bits
    return curve


def compute_traces(n):
    """
    Compute the actual and theoretical running 1-fraction for monoid n.

    Returns (x_axis, actual, theoretical) where x_axis is cumulative
    bit count after each entry.
    """
    primes = acm_n_primes(n, N_PRIMES)

    cum_ones = 0
    cum_bits = 0
    actual = []
    bit_lengths = []
    x_axis = []

    for p in primes:
        b = bin(p)[2:]
        d = len(b)
        ones = b.count('1')
        cum_ones += ones
        cum_bits += d
        actual.append(cum_ones / cum_bits)
        bit_lengths.append(d)
        x_axis.append(cum_bits)

    theoretical = theoretical_step(bit_lengths)
    return np.array(x_axis), np.array(actual), theoretical


# ── Compute ──────────────────────────────────────────────────────────

print("Computing running 1-fractions...")
traces = {}
for n in MONOIDS:
    print(f"  n = {n}...")
    traces[n] = compute_traces(n)


# ── Plot ─────────────────────────────────────────────────────────────

print("Plotting...")

fig, axes = plt.subplots(3, 1, figsize=(18, 14), sharex=False)
fig.patch.set_facecolor('#0a0a0a')

# Panel 1: actual running 1-fraction for all monoids
ax = axes[0]
ax.set_facecolor('#0a0a0a')
for n in MONOIDS:
    x, actual, _ = traces[n]
    ax.plot(x, actual, linewidth=0.8, color=COLORS[n], alpha=0.9,
            label=f'n={n}  ($\\nu_2$={bin(n)[-1::-1].index("1") if n > 0 and n & (n-1) != 0 or n == 1 else int(np.log2(n))})')

ax.axhline(y=0.5, color='white', linewidth=0.5, alpha=0.3,
           linestyle='--')
ax.set_ylabel('fraction of 1-bits', color='white', fontsize=11)
ax.set_title('Running 1-fraction: actual', color='white',
             fontsize=13, pad=10)
ax.legend(loc='upper right', fontsize=9, framealpha=0.3,
          facecolor='#1a1a1a', edgecolor='#333', labelcolor='white')
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('#333')

# Panel 2: actual vs theoretical for a few monoids (detail)
ax = axes[1]
ax.set_facecolor('#0a0a0a')
detail_monoids = [3, 2, 4]
for n in detail_monoids:
    x, actual, theo = traces[n]
    ax.plot(x, actual, linewidth=0.9, color=COLORS[n], alpha=0.9,
            label=f'n={n} actual')
    ax.plot(x, theo, linewidth=0.9, color=COLORS[n], alpha=0.4,
            linestyle=':', label=f'n={n} theory')

ax.axhline(y=0.5, color='white', linewidth=0.5, alpha=0.3,
           linestyle='--')
ax.set_ylabel('fraction of 1-bits', color='white', fontsize=11)
ax.set_title('Actual vs. theoretical (d+1)/(2d)',
             color='white', fontsize=13, pad=10)
ax.legend(loc='upper right', fontsize=8, framealpha=0.3,
          facecolor='#1a1a1a', edgecolor='#333', labelcolor='white',
          ncol=2)
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('#333')

# Panel 3: residual (actual - theoretical)
ax = axes[2]
ax.set_facecolor('#0a0a0a')
for n in MONOIDS:
    x, actual, theo = traces[n]
    residual = actual - theo
    ax.plot(x, residual, linewidth=0.8, color=COLORS[n], alpha=0.9,
            label=f'n={n}')

ax.axhline(y=0, color='white', linewidth=0.5, alpha=0.3,
           linestyle='--')
ax.set_xlabel('cumulative bits in stream', color='white', fontsize=11)
ax.set_ylabel('actual − theory', color='white', fontsize=11)
ax.set_title('Sieve residual: deviation from (d+1)/(2d)',
             color='white', fontsize=13, pad=10)
ax.legend(loc='upper right', fontsize=9, framealpha=0.3,
          facecolor='#1a1a1a', edgecolor='#333', labelcolor='white')
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('#333')

plt.tight_layout()
plt.savefig('one_bias.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> one_bias.png")


# ── Summary ──────────────────────────────────────────────────────────

print("\nFinal 1-fractions (after all entries):")
print(f"  {'monoid':>8s}  {'actual':>8s}  {'theory':>8s}  {'residual':>10s}")
for n in MONOIDS:
    x, actual, theo = traces[n]
    r = actual[-1] - theo[-1]
    print(f"  n={n:<5d}  {actual[-1]:8.6f}  {theo[-1]:8.6f}  {r:+10.6f}")
