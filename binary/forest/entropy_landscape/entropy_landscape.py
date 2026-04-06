"""
entropy_landscape.py — Shannon entropy of k-grams in binary Champernowne streams

For each monoid n = 1..N_MAX and window size k = 1..K_MAX, compute the
Shannon entropy of k-grams in the binary Champernowne stream, divided
by k (entropy per bit). Plot as a heatmap.

A truly random stream has entropy per bit = 1.0 everywhere. The deficit
from 1.0 is the algebraic content the ACM structure injects.
"""

import sys, os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..'))
sys.path.insert(0, os.path.join(_here, '..', '..', '..'))

import numpy as np
import matplotlib.pyplot as plt
from binary_core import binary_stream


N_MAX = 200
K_MAX = 12
N_PRIMES = 2000   # entries per monoid, gives ~20,000+ bits


def kgram_entropy_per_bit(bits, k):
    """
    Shannon entropy of k-grams in a bit stream, divided by k.

    Returns entropy per bit in [0, 1]. A fair coin gives 1.0.
    """
    n = len(bits)
    if n < k:
        return 0.0

    # Count k-grams using integer encoding
    counts = {}
    # Build initial window
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

print("Computing entropy landscape...")
landscape = np.zeros((N_MAX, K_MAX))

for idx in range(N_MAX):
    n = idx + 1
    if n % 50 == 0:
        print(f"  n = {n}...")

    bits = binary_stream(n, count=N_PRIMES)

    for ki in range(K_MAX):
        k = ki + 1
        landscape[idx, ki] = kgram_entropy_per_bit(bits, k)

# Deficit from 1.0
deficit = 1.0 - landscape

v2_arr = np.array([v2(n) for n in range(1, N_MAX + 1)])


# ── Plot ─────────────────────────────────────────────────────────────

print("Plotting...")

fig = plt.figure(figsize=(20, 12))
fig.patch.set_facecolor('#0a0a0a')

gs = fig.add_gridspec(1, 3, width_ratios=[1, 14, 0.6], wspace=0.06)
ax_v = fig.add_subplot(gs[0])
ax_h = fig.add_subplot(gs[1])
ax_cb = fig.add_subplot(gs[2])

# ── v_2 strip ────────────────────────────────────────────────────────

ax_v.set_facecolor('#0a0a0a')
ax_v.imshow(v2_arr.reshape(-1, 1), aspect='auto', cmap='YlOrRd',
            vmin=0, vmax=int(v2_arr.max()),
            interpolation='nearest', origin='lower',
            extent=[0, 1, 1, N_MAX + 1])
ax_v.set_xticks([])
ax_v.set_ylabel('n', color='white', fontsize=12)
ax_v.set_title('$\\nu_2$', color='white', fontsize=11, pad=10)
ax_v.tick_params(colors='white', labelsize=9)

pow2 = [2**k for k in range(0, 8) if 2**k <= N_MAX]
ax_v.set_yticks(pow2)
ax_v.set_yticklabels([str(p) for p in pow2])
for spine in ax_v.spines.values():
    spine.set_color('#333')

# ── Main heatmap: deficit ────────────────────────────────────────────

ax_h.set_facecolor('#0a0a0a')
im = ax_h.imshow(deficit, aspect='auto', cmap='inferno',
                 vmin=0, vmax=deficit.max(),
                 interpolation='nearest', origin='lower',
                 extent=[0.5, K_MAX + 0.5, 1, N_MAX + 1])

ax_h.set_xlabel('window size $k$', color='white', fontsize=12)
ax_h.set_title('Entropy deficit: $1 - H(k\\text{-grams})/k$',
               color='white', fontsize=14, pad=10)
ax_h.set_xticks(range(1, K_MAX + 1))
ax_h.tick_params(colors='white', labelsize=9)

# Mark powers of 2 on y
for p in pow2:
    ax_h.axhline(y=p, color='white', linewidth=0.3, alpha=0.2)

ax_h.set_yticks([])
for spine in ax_h.spines.values():
    spine.set_color('#333')

# ── Colorbar ─────────────────────────────────────────────────────────

cb = fig.colorbar(im, cax=ax_cb)
cb.set_label('entropy deficit', color='white', fontsize=11)
cb.ax.tick_params(colors='white', labelsize=9)

fig.suptitle(
    'Entropy Landscape: where does the algebraic content live?',
    color='white', fontsize=15, y=0.97
)

plt.savefig('entropy_landscape.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> entropy_landscape.png")


# ── Summary ──────────────────────────────────────────────────────────

print("\nEntropy deficit by k (averaged over all n):")
for ki in range(K_MAX):
    k = ki + 1
    avg_def = deficit[:, ki].mean()
    max_def = deficit[:, ki].max()
    max_n = np.argmax(deficit[:, ki]) + 1
    print(f"  k={k:2d}:  avg deficit={avg_def:.6f}  "
          f"max deficit={max_def:.6f} (at n={max_n})")

print("\nEntropy deficit by n (averaged over all k), top 10:")
avg_by_n = deficit.mean(axis=1)
top_n = np.argsort(avg_by_n)[-10:][::-1]
for idx in top_n:
    n = idx + 1
    print(f"  n={n:4d} (v_2={v2(n)}):  avg deficit={avg_by_n[idx]:.6f}")
