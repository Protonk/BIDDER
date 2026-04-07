"""
walsh.py — Walsh-Hadamard spectrum of binary Champernowne streams

For each monoid n in 2..N_MAX, generate a long binary Champernowne
stream, chunk it into 2^K-bit blocks, apply the Walsh-Hadamard
transform to each chunk, and aggregate the squared magnitudes into
a per-monoid Walsh power spectrum P[s] = mean over chunks of |W[s]|^2.

The Walsh-Hadamard normalization used here is

    W[s] = (1 / 2^K) * sum_x  c[x] * (-1)^(popcount(s & x))

with c the chunk values mapped to {-1, +1}. With this convention
Parseval gives sum_s |W[s]|^2 = 1 for any +/-1 chunk, and a fair
coin yields E[|W[s]|^2] = 1/2^K for every s (the white-noise
baseline).

Output is walsh_spectra.npz; downstream coefficient-level analysis
lives in walsh_upgrade.py and the visuals in walsh_visuals.py.

Earlier versions of this script also produced order-bucketed plots
(walsh_orders.png, walsh_heatmap.png, walsh_high_order.png). They
were removed because the popcount-bucket averages obscured the
per-coefficient signal that the rest of the pipeline reads — the
unit of analysis must be the coefficient, not the bucket. See
WALSH.md for the corrected story.
"""

import sys, os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..'))             # base2/
sys.path.insert(0, os.path.join(_here, '..', '..', '..', '..', '..', 'core'))  # core/

import math
import numpy as np
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


# ── High-order summary (kept for the sanity table below) ────────────

WN_BASELINE = 1.0 / CHUNK_SIZE
high_order_mask = POPCOUNT >= 3
n_high_cells = int(high_order_mask.sum())
WN_HIGH = n_high_cells * WN_BASELINE

high_order_power = {
    n: float(P[high_order_mask].sum()) for n, P in power_spectra.items()
}


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
