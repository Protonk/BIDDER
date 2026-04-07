"""
walsh.py — Walsh-Hadamard spectrum of binary Champernowne streams

For each monoid n in 2..N_MAX, generate a long binary Champernowne
stream, chunk it into 2^K-bit blocks, apply the Walsh-Hadamard
transform to each chunk, and aggregate the squared magnitudes into
a per-monoid Walsh power spectrum P[s] = mean over chunks of |W[s]|^2.

Then group the 2^K coefficients by popcount of the index s (the
order |S| of the Walsh subset) and produce three plots:

  1. walsh_orders.png       — order-resolved spectrum, one curve per
                              monoid, log y, white-noise baseline.
  2. walsh_heatmap.png      — full per-(n, s) heatmap, indices sorted
                              by popcount.
  3. walsh_high_order.png   — total high-order power (|S| >= 3) vs n,
                              minus the white-noise baseline.

The Walsh-Hadamard normalization used here is

    W[s] = (1 / 2^K) * sum_x  c[x] * (-1)^(popcount(s & x))

with c the chunk values mapped to {-1, +1}. With this convention
Parseval gives sum_s |W[s]|^2 = 1 for any +/-1 chunk, and a fair
coin yields E[|W[s]|^2] = 1/2^K for every s (the white-noise
baseline plotted in walsh_orders.png).

See PLAN.md for the design and motivation.
"""

import sys, os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..'))             # base2/
sys.path.insert(0, os.path.join(_here, '..', '..', '..', '..', '..', 'core'))  # core/

import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import LogNorm
from scipy.linalg import hadamard
from binary_core import binary_stream


# ── Parameters ───────────────────────────────────────────────────────

N_MAX = 32
BITS_TARGET = 2_000_000
K = 8
CHUNK_SIZE = 1 << K          # 256


# ── Helpers ──────────────────────────────────────────────────────────

def v2(n):
    """2-adic valuation: largest m with 2^m | n."""
    m = 0
    x = n
    while x % 2 == 0:
        m += 1
        x //= 2
    return m


def estimate_count_for_bits(n, bits):
    """How many n-primes do we need to hit roughly `bits` bits?"""
    # Average bit length of the i-th n-prime is ~ log2(n * i).
    # Solve count * log2(n * count) ~ bits.
    avg = math.log2(max(n * (bits // 10), 4))
    return int(bits / max(avg, 4)) + 200


# Hadamard matrix in natural (Sylvester) order, +/-1 entries
H = hadamard(CHUNK_SIZE).astype(np.float64)

# Popcount of each index 0..255 — corresponds to |S| of subset s
POPCOUNT = np.array([bin(i).count('1') for i in range(CHUNK_SIZE)],
                    dtype=np.int8)


# ── Compute Walsh power spectra ──────────────────────────────────────

print(f"Computing Walsh power spectra for n = 2..{N_MAX}")
print(f"Chunk size 2^{K} = {CHUNK_SIZE}, target {BITS_TARGET} bits/monoid\n")

power_spectra = {}    # n -> length-256 vector of mean |W[s]|^2
parseval_check = {}
order0_obs = {}       # n -> (P[0], stream_mean_pm^2)
n_chunks_by_n = {}

for n in range(2, N_MAX + 1):
    count = estimate_count_for_bits(n, BITS_TARGET)
    bits_list = binary_stream(n, count=count)

    n_chunks = len(bits_list) // CHUNK_SIZE
    if n_chunks < 100:
        print(f"  n={n:2d}: WARNING only {n_chunks} chunks — skipping")
        continue

    bits = np.asarray(bits_list[:n_chunks * CHUNK_SIZE], dtype=np.float64)
    del bits_list

    chunks = bits.reshape(n_chunks, CHUNK_SIZE)
    chunks_pm = 2.0 * chunks - 1.0   # map {0, 1} -> {-1, +1}

    # WHT via single matrix-matrix multiply
    W = (chunks_pm @ H) / CHUNK_SIZE   # shape (n_chunks, 256)
    P = np.mean(W * W, axis=0)         # length 256

    power_spectra[n] = P
    parseval_check[n] = float(P.sum())
    order0_obs[n] = (float(P[0]), float(chunks_pm.mean() ** 2))
    n_chunks_by_n[n] = n_chunks

    print(f"  n={n:2d}: {n_chunks} chunks, "
          f"Parseval Σ P = {parseval_check[n]:.6f}")


# ── Order-resolved aggregation ───────────────────────────────────────

print("\nGrouping by popcount (order)...")

# Mean P[s] within each popcount bucket
order_mean = {}
for n, P in power_spectra.items():
    om = np.zeros(K + 1)
    for o in range(K + 1):
        om[o] = P[POPCOUNT == o].mean()
    order_mean[n] = om

WN_BASELINE = 1.0 / CHUNK_SIZE


# ── Plot 1: order-resolved spectrum ──────────────────────────────────

print("\nPlotting order-resolved spectrum...")

fig, ax = plt.subplots(figsize=(13, 8))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

v2_max = max(v2(n) for n in power_spectra)
cmap = cm.get_cmap('viridis')

# Highlighted monoids get explicit labels in the legend
HIGHLIGHT = {2, 3, 4, 5, 7, 8, 16, 32}

orders = np.arange(K + 1)
for n in sorted(power_spectra.keys()):
    om = order_mean[n]
    color = cmap(v2(n) / max(v2_max, 1))
    label = f'n={n}  (ν₂={v2(n)})' if n in HIGHLIGHT else None
    ax.plot(orders, om, '-o', color=color, linewidth=1.4,
            markersize=5, alpha=0.9, label=label)

ax.axhline(y=WN_BASELINE, color='white', linestyle='--',
           linewidth=1, alpha=0.7, label=f'white noise = 1/{CHUNK_SIZE}')

ax.set_xlabel('Walsh subset order $|S|$', color='white', fontsize=12)
ax.set_ylabel(r'mean Walsh power $\langle |W[S]|^2 \rangle$',
              color='white', fontsize=12)
ax.set_yscale('log')
ax.set_title(
    'Order-resolved Walsh power spectrum of binary Champernowne streams\n'
    'colored by $\\nu_2(n)$ — darker = higher 2-adic valuation',
    color='white', fontsize=13, pad=12,
)
ax.legend(facecolor='#1a1a1a', edgecolor='#444', labelcolor='white',
          fontsize=8, loc='best', ncol=2)
ax.tick_params(colors='white')
ax.grid(True, alpha=0.1, color='white')
for spine in ax.spines.values():
    spine.set_color('#444')

plt.tight_layout()
plt.savefig('walsh_orders.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
plt.close()
print("-> walsh_orders.png")


# ── Plot 2: full spectrum heatmap ────────────────────────────────────

print("Plotting full spectrum heatmap...")

# Sort 0..255 first by popcount, then by raw index
order_indices = np.array(
    sorted(range(CHUNK_SIZE), key=lambda i: (int(POPCOUNT[i]), i))
)

ns_sorted = sorted(power_spectra.keys())
heatmap = np.array([power_spectra[n][order_indices] for n in ns_sorted])

fig, ax = plt.subplots(figsize=(16, 9))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

vmin = max(heatmap[heatmap > 0].min(), 1e-10)
im = ax.imshow(heatmap, aspect='auto', cmap='inferno',
               norm=LogNorm(vmin=vmin, vmax=heatmap.max()),
               interpolation='nearest')

# Vertical lines marking popcount boundaries
prev_o = int(POPCOUNT[order_indices[0]])
for i in range(1, len(order_indices)):
    o = int(POPCOUNT[order_indices[i]])
    if o != prev_o:
        ax.axvline(x=i - 0.5, color='white', linewidth=0.4, alpha=0.5)
        prev_o = o

# Annotate order labels along the top
prev_o = -1
for i, idx in enumerate(order_indices):
    o = int(POPCOUNT[idx])
    if o != prev_o:
        ax.text(i + 0.5, -0.7, f'|S|={o}', color='white',
                fontsize=8, ha='left', va='bottom')
        prev_o = o

ax.set_xlabel('Walsh subset index (sorted by popcount, then value)',
              color='white', fontsize=12)
ax.set_ylabel('monoid $n$', color='white', fontsize=12)
ax.set_yticks(range(len(ns_sorted)))
ax.set_yticklabels([f'{n}  (ν₂={v2(n)})' for n in ns_sorted], fontsize=8)
ax.set_title(
    'Walsh power spectrum heatmap — rows=monoid, cols=subset (popcount-sorted)',
    color='white', fontsize=13, pad=18,
)
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('#444')

cbar = plt.colorbar(im, ax=ax, pad=0.02)
cbar.set_label('Walsh power $|W[s]|^2$', color='white', fontsize=11)
cbar.ax.yaxis.set_tick_params(color='white')
plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
cbar.outline.set_edgecolor('#444')

plt.tight_layout()
plt.savefig('walsh_heatmap.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
plt.close()
print("-> walsh_heatmap.png")


# ── Plot 3: high-order power vs monoid ───────────────────────────────

print("Plotting high-order power vs monoid...")

high_order_power = {}
high_order_mask = POPCOUNT >= 3
n_high_cells = int(high_order_mask.sum())
WN_HIGH = n_high_cells * WN_BASELINE

for n, P in power_spectra.items():
    high_order_power[n] = float(P[high_order_mask].sum())

ns_arr = np.array(sorted(high_order_power.keys()))
hop = np.array([high_order_power[n] for n in ns_arr])
v2_arr = np.array([v2(n) for n in ns_arr])
excess = hop - WN_HIGH
colors = [cmap(v / max(v2_max, 1)) for v in v2_arr]

fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

ax.bar(ns_arr, excess, color=colors, edgecolor='none', alpha=0.92)
ax.axhline(y=0, color='white', linewidth=0.6, alpha=0.6)

# Annotate v_2 for high-v_2 monoids
for n, e, v in zip(ns_arr, excess, v2_arr):
    if v >= 2:
        ax.annotate(
            f'ν₂={v}', xy=(n, e),
            xytext=(0, 4 if e >= 0 else -10), textcoords='offset points',
            color='white', fontsize=7, ha='center',
        )

ax.set_xlabel('monoid $n$', color='white', fontsize=12)
ax.set_ylabel(r'excess high-order Walsh power'
              + '\n' + r'$\sum_{|S| \geq 3} |W[S]|^2 \, - \,$ white-noise baseline',
              color='white', fontsize=11)
ax.set_title(
    'High-order Walsh power (orders ≥ 3) vs monoid\n'
    'colored by $\\nu_2(n)$',
    color='white', fontsize=13, pad=12,
)
ax.set_xticks(ns_arr)
ax.tick_params(colors='white')
ax.tick_params(axis='x', labelsize=8)
ax.grid(True, axis='y', alpha=0.1, color='white')
for spine in ax.spines.values():
    spine.set_color('#444')

plt.tight_layout()
plt.savefig('walsh_high_order.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
plt.close()
print("-> walsh_high_order.png")


# ── Save raw spectra so we can re-analyze without re-running ─────────

print("\nSaving raw spectra to walsh_spectra.npz...")
np.savez(
    'walsh_spectra.npz',
    ns=np.array(sorted(power_spectra.keys())),
    spectra=np.array([power_spectra[n] for n in sorted(power_spectra.keys())]),
    popcount=POPCOUNT,
    chunk_size=CHUNK_SIZE,
    bits_target=BITS_TARGET,
)


# ── Sanity-check table ───────────────────────────────────────────────

print("\n=== Sanity checks ===")
print(f"White-noise per-cell baseline: 1/{CHUNK_SIZE} = {WN_BASELINE:.6f}")
print(f"White-noise high-order ({n_high_cells} cells) total: {WN_HIGH:.6f}")
print()
print(f"{'n':>4} {'ν₂':>4} {'#chunks':>8} {'Parseval':>11} "
      f"{'P[0]':>11} {'mean²':>11} {'high-ord':>11}")
print('-' * 72)
for n in sorted(power_spectra.keys()):
    p_par = parseval_check[n]
    p0, m2 = order0_obs[n]
    ho = high_order_power[n]
    nc = n_chunks_by_n[n]
    print(f"{n:>4} {v2(n):>4} {nc:>8d} {p_par:>11.6f} "
          f"{p0:>11.6f} {m2:>11.6f} {ho:>11.6f}")

print("\nDone.")
