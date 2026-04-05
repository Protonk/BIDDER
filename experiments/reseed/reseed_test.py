"""
reseed_test.py — Can we rekey at the period boundary without issue?

Three questions:
  1. Does each rekeyed period still have exact uniformity?
  2. Is there a detectable seam at the boundary between periods?
  3. Does the cross-period stream look different from a single period?
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../generator'))

import collections
import hashlib
import struct
import numpy as np
import matplotlib.pyplot as plt
from hch import HCH


def rekey(old_key, period_num):
    """Derive a new key from the old key and the period counter."""
    return hashlib.sha256(old_key + struct.pack('<Q', period_num)).digest()


def generate_rekeyed_stream(base, digit_class, seed_key, n_periods):
    """Generate n_periods full periods, rekeying at each boundary."""
    key = seed_key
    full_stream = []
    per_period_counts = []

    for p in range(n_periods):
        gen = HCH(base=base, digit_class=digit_class, key=key)
        period_output = [gen.next() for _ in range(gen.period)]
        full_stream.extend(period_output)
        per_period_counts.append(collections.Counter(period_output))
        key = rekey(key, p)

    return full_stream, per_period_counts


# =====================================================================
# Test 1: Per-period exact uniformity survives rekeying
# =====================================================================

print("=== Test 1: Per-period uniformity ===\n")

base, dc = 10, 3  # period = 900
n_periods = 100

stream, period_counts = generate_rekeyed_stream(
    base, dc, b'reseed test', n_periods)

period = 900
expected = period // (base - 1)  # 100
all_exact = True

for p, counts in enumerate(period_counts):
    for d in range(1, base):
        if counts[d] != expected:
            print(f"  Period {p}: digit {d} count {counts[d]} != {expected}")
            all_exact = False

print(f"  {n_periods} periods, each period exactly uniform: {all_exact}")
print(f"  Total stream length: {len(stream)}")


# =====================================================================
# Test 2: Seam detection — is the boundary visible?
# =====================================================================

print("\n=== Test 2: Seam detection ===\n")

# Look at digit bigrams (consecutive pairs) across the whole stream.
# If there's a seam, the bigrams at period boundaries will have a
# different distribution than bigrams within a period.

stream_arr = np.array(stream)

# All bigrams
all_bigrams = collections.Counter(
    zip(stream_arr[:-1].tolist(), stream_arr[1:].tolist()))

# Bigrams at period boundaries (last of period N, first of period N+1)
boundary_bigrams = collections.Counter()
for p in range(n_periods - 1):
    idx = (p + 1) * period - 1  # last element of period p
    boundary_bigrams[(stream_arr[idx], stream_arr[idx + 1])] += 1

# Bigrams NOT at boundaries
interior_bigrams = collections.Counter()
for i in range(len(stream_arr) - 1):
    if (i + 1) % period != 0:  # skip boundary positions
        interior_bigrams[(stream_arr[i], stream_arr[i + 1])] += 1

# Chi-squared test: are boundary bigrams drawn from the same
# distribution as interior bigrams?
n_boundary = sum(boundary_bigrams.values())
n_interior = sum(interior_bigrams.values())

# Expected boundary count for each bigram = n_boundary * (interior_count / n_interior)
chi2 = 0
df = 0
for bigram in set(list(all_bigrams.keys())):
    obs = boundary_bigrams.get(bigram, 0)
    interior_rate = interior_bigrams.get(bigram, 0) / n_interior
    exp = n_boundary * interior_rate
    if exp > 0.5:  # only count cells with reasonable expected count
        chi2 += (obs - exp) ** 2 / exp
        df += 1

# With ~81 bigrams and 99 boundary transitions, df is around 80
# Chi-squared critical value at 0.05 for df=80 is ~101.9
print(f"  Boundary bigrams: {n_boundary}")
print(f"  Interior bigrams: {n_interior}")
print(f"  Chi-squared: {chi2:.2f} (df={df})")
print(f"  Threshold (0.05, df={df}): ~{df + 2 * (2*df)**0.5:.0f}")
seam_detected = chi2 > df + 3 * (2 * df) ** 0.5  # ~3 sigma
print(f"  Seam detected: {seam_detected}")


# =====================================================================
# Test 3: Cross-period digit distribution
# =====================================================================

print("\n=== Test 3: Cross-period distribution ===\n")

# The full stream spans n_periods periods. At each period boundary,
# the distribution is exact. But is the CROSS-PERIOD distribution
# also well-behaved?

total_counts = collections.Counter(stream)
total = len(stream)
print(f"  Total stream: {total} symbols")
for d in range(1, base):
    frac = total_counts[d] / total
    expected_frac = 1.0 / (base - 1)
    print(f"    digit {d}: {total_counts[d]} ({frac:.6f}), "
          f"expected {expected_frac:.6f}")

# Are all periods producing different sequences?
first_20 = []
key = b'reseed test'
for p in range(5):
    gen = HCH(base=base, digit_class=dc, key=key)
    first_20.append([gen.next() for _ in range(20)])
    key = rekey(key, p)

print(f"\n  First 20 outputs per period (5 periods):")
for p, seq in enumerate(first_20):
    print(f"    Period {p}: {seq}")
all_different = len(set(tuple(s) for s in first_20)) == len(first_20)
print(f"  All sequences different: {all_different}")


# =====================================================================
# Plot: running deviation across period boundaries
# =====================================================================

print("\nPlotting...")

fig, axes = plt.subplots(2, 1, figsize=(18, 10), sharex=True)
fig.patch.set_facecolor('#0a0a0a')

# Top: running max deviation over the full multi-period stream
ax = axes[0]
ax.set_facecolor('#0a0a0a')

target = 1.0 / (base - 1)
counts_running = np.zeros(base, dtype=int)
dev = np.empty(len(stream))
for i, d in enumerate(stream):
    counts_running[d] += 1
    fracs = counts_running[1:base] / (i + 1)
    dev[i] = np.max(np.abs(fracs - target))

ns = np.arange(1, len(stream) + 1)
ax.plot(ns, dev, linewidth=0.3, color='#ffcc5c', alpha=0.9)

# Mark period boundaries
for p in range(1, n_periods):
    ax.axvline(x=p * period, color='white', linewidth=0.2, alpha=0.2)

ax.set_ylabel('max deviation', color='white', fontsize=11)
ax.set_title(f'Running deviation across {n_periods} rekeyed periods '
             f'(base {base}, d={dc})',
             color='white', fontsize=13, pad=10)
ax.tick_params(colors='white')

# Bottom: zoom on first 5 periods
ax = axes[1]
ax.set_facecolor('#0a0a0a')
zoom = 5 * period
ax.plot(ns[:zoom], dev[:zoom], linewidth=0.6, color='#ffcc5c', alpha=0.9)
for p in range(1, 5):
    ax.axvline(x=p * period, color='#ff6f61', linewidth=1, alpha=0.5,
               linestyle='--')
    ax.text(p * period + 10, dev[:zoom].max() * 0.9, f'rekey',
            color='#ff6f61', fontsize=8, alpha=0.7)
ax.set_xlabel('output index', color='white', fontsize=11)
ax.set_ylabel('max deviation', color='white', fontsize=11)
ax.set_title('Zoom: first 5 periods', color='white', fontsize=12, pad=8)
ax.set_xlim(0, zoom)
ax.tick_params(colors='white')

plt.tight_layout()
plt.savefig('reseed_test.png', dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
print("-> reseed_test.png")
