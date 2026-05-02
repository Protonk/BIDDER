"""
K-scaling of D_L* for the five constructions at [2, 10].

The PRNG-FRAMEWORK conjecture predicts D_L*(K) → 0 as K → ∞ for
C_Surv (and friends). Empirical question: does the decay beat the
Erdős–Copeland-type benchmark (log L)/√L, hit it, or fall behind?
The echo cascade in ECHO-STRUCTURE.md predicts a slow,
decade-paced staircase decay rather than smooth power-law — this
sweep tests that.

For each K ∈ {100, 200, 400, 800, 1600, 3200, 6400}, build the five
constructions, compute D_L*, and plot D_L*(K) vs K with reference
benchmarks.
"""

import time
import numpy as np
from sympy import isprime
import matplotlib.pyplot as plt

W = 9
n_0 = 2
n_1 = n_0 + W - 1
PRECISION = 18
K_VALUES = [100, 200, 400, 800, 1600, 3200, 6400]


def n_primes_vec(n, k):
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


def build_orbits_for_K(k):
    """Return dict label -> orbit array, plus dict label -> L."""
    parts_per_stream = [(n, n_primes_vec(n, k))
                        for n in range(n_0, n_1 + 1)]
    all_atoms = np.concatenate([arr for _, arr in parts_per_stream])
    stream_tag = np.concatenate([np.full_like(arr, n)
                                  for n, arr in parts_per_stream])

    unique_vals, first_idx, counts = np.unique(
        all_atoms, return_index=True, return_counts=True)
    surv_mask = counts == 1
    S = unique_vals[surv_mask]
    sources_S = stream_tag[first_idx[surv_mask]]
    m_S = S // sources_S
    prime_m_arr = np.array([isprime(int(m)) for m in m_S])

    S_set = set(int(c) for c in S)
    S_prime_set = set(int(c) for c, pm in zip(S, prime_m_arr) if pm)
    S_comp_set = set(int(c) for c, pm in zip(S, prime_m_arr) if not pm)

    seen = set()
    unique_in_appearance = []
    for c in all_atoms:
        c_int = int(c)
        if c_int not in seen:
            seen.add(c_int)
            unique_in_appearance.append(c_int)

    surv_app = [c for c in unique_in_appearance if c in S_set]
    surv_pm_app = [c for c in unique_in_appearance
                    if c in S_prime_set]
    surv_cm_app = [c for c in unique_in_appearance
                    if c in S_comp_set]

    digits = {
        'C_Bundle': ''.join(str(int(c)) for c in all_atoms.tolist()),
        'C_Bundle_sorted': ''.join(str(int(c))
                                    for c in sorted(int(x)
                                                    for x in unique_vals)),
        'C_Surv': ''.join(str(int(c)) for c in surv_app),
        'C_Surv_prime_m': ''.join(str(int(c)) for c in surv_pm_app),
        'C_Surv_comp_m': ''.join(str(int(c)) for c in surv_cm_app),
    }
    orbits = {}
    Ls = {}
    for label, ds in digits.items():
        L = len(ds)
        Ls[label] = L
        ds_arr = np.frombuffer(ds.encode(), dtype=np.uint8) - ord('0')
        weights = 10.0 ** (-(np.arange(PRECISION) + 1))
        pad = np.concatenate([ds_arr,
                              np.zeros(PRECISION, dtype=np.uint8)])
        orbit = np.zeros(L, dtype=np.float64)
        for j in range(PRECISION):
            orbit += pad[j:j + L] * weights[j]
        orbits[label] = orbit
    return orbits, Ls


def star_discrepancy(values):
    sorted_v = np.sort(np.asarray(values, dtype=np.float64))
    N = len(sorted_v)
    if N == 0:
        return float('nan')
    i = np.arange(1, N + 1, dtype=np.float64)
    d_plus = float(np.max(i / N - sorted_v))
    d_minus = float(np.max(sorted_v - (i - 1) / N))
    return max(d_plus, d_minus)


print(f"K-scaling sweep over K ∈ {K_VALUES}, W = {W}, n_0 = {n_0}")
print()
LABELS = ['C_Bundle', 'C_Bundle_sorted', 'C_Surv',
          'C_Surv_prime_m', 'C_Surv_comp_m']

# Results: dict label -> list of (K, L, D_L*)
results = {label: [] for label in LABELS}

t0 = time.time()
for K in K_VALUES:
    print(f"K = {K}  (cumulative t = {time.time() - t0:.1f}s)")
    orbits, Ls = build_orbits_for_K(K)
    for label in LABELS:
        L = Ls[label]
        d_star = star_discrepancy(orbits[label])
        results[label].append((K, L, d_star))
        print(f"  {label:<22}  L = {L:>7d}   "
              f"D_L* = {d_star:.5f}")

print(f"\nTotal compute: {time.time() - t0:.1f}s")
print()

# --- Numerical summary ---
print("=" * 92)
print(f"{'construction':<20} " + "  ".join(f"K={K:>5}"
                                             for K in K_VALUES))
print("-" * 92)
for label in LABELS:
    line = f"{label:<20} "
    for (K, L, d) in results[label]:
        line += f"  {d:>6.4f}"
    print(line)
print()

print(f"{'construction':<20} " +
      "  ".join(f"L@K={K:>5}" for K in K_VALUES))
print("-" * 92)
for label in LABELS:
    line = f"{label:<20} "
    for (K, L, d) in results[label]:
        line += f"  {L:>9d}"
    print(line)
print()

# Ratio to (log L)/√L benchmark
print(f"D_L* / ((log L)/√L)  — Erdős–Copeland baseline ratio")
print(f"{'construction':<20} " + "  ".join(f"K={K:>5}"
                                             for K in K_VALUES))
print("-" * 92)
for label in LABELS:
    line = f"{label:<20} "
    for (K, L, d) in results[label]:
        ref = np.log(L) / np.sqrt(L)
        line += f"  {d/ref:>6.3f}"
    print(line)

# --- Plot: two-panel ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 11))
fig.patch.set_facecolor('#0a0a0a')

colors = {
    'C_Bundle':         '#ffa642',
    'C_Bundle_sorted':  '#bbbbbb',
    'C_Surv':           '#a8e22d',
    'C_Surv_prime_m':   '#5cd4ff',
    'C_Surv_comp_m':    '#cc66ff',
}

# Panel 1: D_L* vs K (log-log).
ax1.set_facecolor('#0a0a0a')
for label in LABELS:
    Ks = np.array([r[0] for r in results[label]])
    Ds = np.array([r[2] for r in results[label]])
    ax1.loglog(Ks, Ds, 'o-', color=colors[label], linewidth=1.5,
               markersize=6, label=label, alpha=0.95)

# Reference benchmarks: (log L)/√L and 1/√(2L) at the C_Bundle L
# (since L scales linearly with K for any construction).
Ks_arr = np.array(K_VALUES)
L_bundle = np.array([results['C_Bundle'][i][1]
                      for i in range(len(K_VALUES))])
ref_log = np.log(L_bundle) / np.sqrt(L_bundle)
ref_sqrt = 1.0 / np.sqrt(2 * L_bundle)
ax1.loglog(Ks_arr, ref_log, '--', color='#777', linewidth=0.8,
           label='(log L)/√L  at C_Bundle L')
ax1.loglog(Ks_arr, ref_sqrt, ':', color='#777', linewidth=0.8,
           label='1/√(2L)  at C_Bundle L')

ax1.set_xlabel('K  (atoms per stream)', color='white', fontsize=11)
ax1.set_ylabel('D_L*  (star discrepancy at full length)',
               color='white', fontsize=11)
ax1.set_title(
    'K-scaling of D_L*  ([n_0, n_1] = [2, 10], '
    f'W = {W})', color='white', fontsize=12)
ax1.tick_params(colors='white', which='both')
for spine in ax1.spines.values():
    spine.set_color('#333')
ax1.legend(loc='lower left', facecolor='#1a1a1a',
           edgecolor='#333', labelcolor='white', fontsize=9)
ax1.grid(alpha=0.15, color='#444', which='both')

# Panel 2: ratio D_L* / ((log L)/√L) vs K (linear).
ax2.set_facecolor('#0a0a0a')
for label in LABELS:
    Ks = np.array([r[0] for r in results[label]])
    Ds = np.array([r[2] for r in results[label]])
    Ls = np.array([r[1] for r in results[label]])
    ratio = Ds / (np.log(Ls) / np.sqrt(Ls))
    ax2.semilogx(Ks, ratio, 'o-', color=colors[label],
                 linewidth=1.5, markersize=6, label=label,
                 alpha=0.95)

ax2.axhline(1.0, color='#666', linestyle='--', linewidth=0.7,
            alpha=0.7, label='ratio = 1 (Erdős–Copeland)')
ax2.set_xlabel('K  (atoms per stream)', color='white', fontsize=11)
ax2.set_ylabel('D_L* / ((log L)/√L)',
               color='white', fontsize=11)
ax2.set_title(
    'Normalised to Erdős–Copeland benchmark — < 1 beats it',
    color='white', fontsize=12)
ax2.tick_params(colors='white', which='both')
for spine in ax2.spines.values():
    spine.set_color('#333')
ax2.legend(loc='upper right', facecolor='#1a1a1a',
           edgecolor='#333', labelcolor='white', fontsize=9)
ax2.grid(alpha=0.15, color='#444', which='both')

plt.tight_layout()
plt.savefig('k_scaling.png', dpi=170, facecolor='#0a0a0a',
            bbox_inches='tight')
print()
print("-> k_scaling.png")
