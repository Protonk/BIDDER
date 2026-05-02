"""
Echo extension — push K to test the log-spacing prediction.

Echo test on combined caches found echoes at log-spaced K:
  main peak ≈ K=150
  first echo ≈ K=1500   (10x main)
  second echo ≈ K=15000 (10x first)

Prediction under the "echoes forever" reading: a third echo near
K ≈ 150000 with smaller amplitude. This script computes bias at
K ∈ [50000, 500000] step 5000 for selected small n_0 to test.
"""

import sys
sys.path.insert(0, '../../../../core')
sys.path.insert(0, '.')

import time
import numpy as np
from scipy.signal import find_peaks

W = 9
N0_VALUES = [2, 3, 5, 8, 12]
K_VALUES = np.arange(50000, 500001, 5000)


def n_primes_vec(n, k):
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


def cell_stats(n0, k, w=W):
    n1 = n0 + w - 1
    parts = [n_primes_vec(n, k) for n in range(n0, n1 + 1)]
    m_arr = np.concatenate(parts)
    unique_vals, counts = np.unique(m_arr, return_counts=True)
    n_unique = unique_vals.size
    dlen_unique = np.floor(np.log10(unique_vals)).astype(np.int64) + 1
    L_b_set = int(dlen_unique.sum())
    surv_mask = (counts == 1)
    n_surv = int(surv_mask.sum())
    L_s = int(dlen_unique[surv_mask].sum())
    return n_unique, n_surv, L_b_set, L_s


print(f"Computing extended K range: {len(N0_VALUES)} n_0 x "
      f"{len(K_VALUES)} K = {len(N0_VALUES) * len(K_VALUES)} cells, "
      f"K ∈ [{K_VALUES[0]}, {K_VALUES[-1]}] step "
      f"{K_VALUES[1] - K_VALUES[0]}")

t0 = time.time()
data = {}
for n0 in N0_VALUES:
    bias = np.zeros(len(K_VALUES))
    for j, k in enumerate(K_VALUES):
        nu, ns, lbs, ls = cell_stats(int(n0), int(k))
        mean_b = lbs / nu
        mean_s = ls / ns
        bias[j] = (mean_s / mean_b - 1) * 100
    data[n0] = bias
    print(f"  n_0={n0} done (t={time.time() - t0:.1f}s)")

print(f"Total compute: {time.time() - t0:.1f}s")
np.savez('echo_extend.npz', K_VALUES=K_VALUES,
         **{f'bias_n0_{n0}': data[n0] for n0 in N0_VALUES})
print("-> echo_extend.npz")

print()
print("Echo search in extended K ∈ [50000, 500000]:")
print(f"{'n_0':>4} {'#peaks':>7} "
      f"{'peak (K, %, prom)':>40}")
print("-" * 80)

for n0 in N0_VALUES:
    bias = data[n0]
    # Use absolute prominence 0.05 (same scale as primary test).
    peaks, props = find_peaks(bias, prominence=0.03)
    Ke = K_VALUES[peaks]
    Ae = bias[peaks]
    Pe = props['prominences']
    echo_str = "  ".join(f"({K_e}, {a_e:+.3f}, {p_e:.3f})"
                          for K_e, a_e, p_e in zip(Ke, Ae, Pe)) or "—"
    print(f"{n0:>4d} {len(peaks):>7d}   {echo_str}")

# Combined view: find the trend amplitude at the predicted third
# echo location (K ≈ 150000-200000) per n_0.
print()
print(f"Bias values at predicted third-echo region (K ≈ 150K):")
print(f"{'n_0':>4} "
      f"{'K=100K':>9} {'K=150K':>9} {'K=200K':>9} {'K=300K':>9} "
      f"{'K=500K':>9}")
for n0 in N0_VALUES:
    bias = data[n0]
    targets = [100000, 150000, 200000, 300000, 500000]
    vals = [bias[np.argmin(np.abs(K_VALUES - t))] for t in targets]
    print(f"{n0:>4d} " +
          " ".join(f"{v:>+9.3f}" for v in vals))
