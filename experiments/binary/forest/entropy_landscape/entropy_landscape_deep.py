"""
entropy_landscape_deep.py — entropy landscape at high bit depth

20 monoids spanning v_2 = 0..7, 10,000 n-primes each (~100,000 bits),
k-grams up to k=16. Focused and deep.
"""

import sys, os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..'))             # binary/
sys.path.insert(0, os.path.join(_here, '..', '..', '..', 'core'))  # core/

import numpy as np
import matplotlib.pyplot as plt
from binary_core import binary_stream


K_MAX = 16
N_PRIMES = 10_000

# 20 monoids: 2-3 per v_2 level, spanning 0..7
MONOIDS = [
    # v_2=0
    3, 7, 15,
    # v_2=1
    2, 6, 10,
    # v_2=2
    4, 12, 20,
    # v_2=3
    8, 24, 40,
    # v_2=4
    16, 48,
    # v_2=5
    32, 96,
    # v_2=6
    64, 192,
    # v_2=7
    128,
]


def kgram_entropy_per_bit(bits, k):
    n = len(bits)
    if n < k:
        return 0.0
    counts = {}
    val = 0
    for j in range(k):
        val = (val << 1) | bits[j]
    counts[val] = 1
    mask = (1 << k) - 1
    for i in range(1, n - k + 1):
        val = ((val << 1) | bits[i + k - 1]) & mask
        counts[val] = counts.get(val, 0) + 1
    total = sum(counts.values())
    entropy = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            entropy -= p * np.log2(p)
    return entropy / k


def v2(n):
    if n == 0:
        return 0
    v = 0
    while n % 2 == 0:
        n //= 2
        v += 1
    return v


# ── Compute ──────────────────────────────────────────────────────────

print("Computing entropy landscape (deep)...")
N_MON = len(MONOIDS)
landscape = np.zeros((N_MON, K_MAX))
stream_lengths = []

for idx, n in enumerate(MONOIDS):
    print(f"  n = {n} (v_2={v2(n)})...")
    bits = binary_stream(n, count=N_PRIMES)
    stream_lengths.append(len(bits))
    for ki in range(K_MAX):
        k = ki + 1
        landscape[idx, ki] = kgram_entropy_per_bit(bits, k)

deficit = 1.0 - landscape

v2_arr = np.array([v2(n) for n in MONOIDS])
labels = [f'n={n}\n$\\nu_2$={v2(n)}' for n in MONOIDS]


# ── Plot: heatmap ────────────────────────────────────────────────────

print("Plotting heatmap...")

fig, ax = plt.subplots(figsize=(16, 10))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

im = ax.imshow(deficit, aspect='auto', cmap='inferno',
               vmin=0, vmax=deficit.max(),
               interpolation='nearest', origin='lower',
               extent=[0.5, K_MAX + 0.5, -0.5, N_MON - 0.5])

ax.set_xlabel('window size $k$', color='white', fontsize=12)
ax.set_ylabel('monoid', color='white', fontsize=12)
ax.set_title(
    f'Entropy deficit (deep): {N_PRIMES} entries, ~{np.mean(stream_lengths):.0f} bits per stream',
    color='white', fontsize=14, pad=12)
ax.set_xticks(range(1, K_MAX + 1))
ax.set_yticks(range(N_MON))
ax.set_yticklabels(labels, fontsize=8)
ax.tick_params(colors='white', labelsize=9)
for spine in ax.spines.values():
    spine.set_color('#333')

cb = fig.colorbar(im, ax=ax, pad=0.02)
cb.set_label('entropy deficit', color='white', fontsize=11)
cb.ax.tick_params(colors='white', labelsize=9)

plt.tight_layout()
plt.savefig('entropy_landscape_deep.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> entropy_landscape_deep.png")


# ── Plot: line traces by v_2 ─────────────────────────────────────────

print("Plotting line traces...")

fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

v2_colors = {
    0: '#88d8b0',
    1: '#6ec6ff',
    2: '#c49bff',
    3: '#ffcc5c',
    4: '#ff9966',
    5: '#ff6f61',
    6: '#e74c3c',
    7: '#ffffff',
}

ks = np.arange(1, K_MAX + 1)

for idx, n in enumerate(MONOIDS):
    v = v2(n)
    alpha = 0.9 if n == 2**v else 0.4  # bold for pure powers of 2
    lw = 1.5 if n == 2**v else 0.7
    label = f'n={n}' if n == 2**v else None
    ax.plot(ks, deficit[idx, :], 'o-', color=v2_colors[v],
            markersize=3, linewidth=lw, alpha=alpha, label=label)

ax.set_xlabel('window size $k$', color='white', fontsize=12)
ax.set_ylabel('entropy deficit per bit', color='white', fontsize=12)
ax.set_title('Entropy deficit vs. window size, colored by $\\nu_2$',
             color='white', fontsize=14, pad=12)
ax.set_xticks(range(1, K_MAX + 1))
ax.legend(loc='upper left', fontsize=9, framealpha=0.3,
          facecolor='#1a1a1a', edgecolor='#333', labelcolor='white',
          title='pure powers of 2', title_fontsize=9)
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('#333')

plt.tight_layout()
plt.savefig('entropy_landscape_traces.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> entropy_landscape_traces.png")


# ── Summary ──────────────────────────────────────────────────────────

print(f"\nStream lengths: min={min(stream_lengths)}, max={max(stream_lengths)}, "
      f"avg={np.mean(stream_lengths):.0f}")

print("\nDeficit at k=1 vs k=16:")
print(f"  {'monoid':>8s}  {'v_2':>4s}  {'k=1':>10s}  {'k=16':>10s}  {'ratio':>8s}")
for idx, n in enumerate(MONOIDS):
    d1 = deficit[idx, 0]
    d16 = deficit[idx, K_MAX - 1]
    ratio = d16 / d1 if d1 > 0 else 0
    print(f"  n={n:<5d}  {v2(n):4d}  {d1:10.6f}  {d16:10.6f}  {ratio:8.2f}")
