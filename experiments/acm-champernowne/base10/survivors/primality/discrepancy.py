"""
Star discrepancy for C_Bundle, C_Surv, and the cofactor-primality
stratifications.

For a real α ∈ [0, 1) with digit expansion 0.d₁d₂d₃…, the orbit
{10ⁿ α} for n = 0, …, L − 1 is the sequence of tail values. α is
b-normal iff this orbit equidistributes; b-density follows from
star discrepancy D_N → 0.

This is the canonical observable Bailey–Crandall use; our
leading-digit L1 is a coarse projection of it. See
`../../../../../algebra/PRNG-FRAMEWORK.md`.

Computes star discrepancy for:
  - C_Bundle (multiset, stream-first order with duplicates)
  - C_Bundle_unique_sorted (Erdős–Copeland Champernowne baseline)
  - C_Surv (survivors in bundle-first-appearance order)
  - C_Surv_prime_m (prime-cofactor survivors)
  - C_Surv_comp_m (composite-cofactor survivors)
"""

import time
import numpy as np
from sympy import isprime
import matplotlib.pyplot as plt

W = 9
n_0 = 2
n_1 = n_0 + W - 1
k = 400

PRECISION = 18  # digits of tail used to compute the float value


def n_primes_vec(n, k):
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


print("Building bundle and survivors...")
parts_per_stream = [(n, n_primes_vec(n, k))
                    for n in range(n_0, n_1 + 1)]
all_atoms = np.concatenate([arr for _, arr in parts_per_stream])
n_atoms = all_atoms.size
stream_tag = np.concatenate([np.full_like(arr, n)
                             for n, arr in parts_per_stream])

unique_vals, first_idx, counts = np.unique(
    all_atoms, return_index=True, return_counts=True)
surv_mask = counts == 1
S = unique_vals[surv_mask]
sources_S = stream_tag[first_idx[surv_mask]]
m_S = S // sources_S
prime_m_arr = np.array([isprime(int(m)) for m in m_S])

S_prime_set = set(int(c) for c, pm in zip(S, prime_m_arr) if pm)
S_comp_set = set(int(c) for c, pm in zip(S, prime_m_arr) if not pm)
S_set = set(int(c) for c in S)

# Build first-appearance order of unique integers.
seen = set()
unique_in_appearance = []
for c in all_atoms:
    c_int = int(c)
    if c_int not in seen:
        seen.add(c_int)
        unique_in_appearance.append(c_int)

surv_appearance = [c for c in unique_in_appearance if c in S_set]
surv_pm_appearance = [c for c in unique_in_appearance
                       if c in S_prime_set]
surv_cm_appearance = [c for c in unique_in_appearance
                       if c in S_comp_set]


def build_digits(integers_in_order):
    return ''.join(str(int(c)) for c in integers_in_order)


digits_bundle = build_digits(all_atoms.tolist())
digits_bundle_sorted = build_digits(sorted(int(c) for c in unique_vals))
digits_surv = build_digits(surv_appearance)
digits_surv_pm = build_digits(surv_pm_appearance)
digits_surv_cm = build_digits(surv_cm_appearance)

print(f"  C_Bundle:               {len(digits_bundle)} digits "
      f"({len(all_atoms)} atoms, multiset)")
print(f"  C_Bundle_unique_sorted: {len(digits_bundle_sorted)} digits "
      f"({len(unique_vals)} integers, sorted set)")
print(f"  C_Surv:                 {len(digits_surv)} digits "
      f"({len(surv_appearance)} survivors)")
print(f"  C_Surv (prime-m):       {len(digits_surv_pm)} digits "
      f"({len(surv_pm_appearance)} survivors)")
print(f"  C_Surv (comp-m):        {len(digits_surv_cm)} digits "
      f"({len(surv_cm_appearance)} survivors)")
print()


def tail_orbit(digit_string, precision=PRECISION):
    """Return [{10ⁿ α} for n = 0, …, L−1] as a numpy array.

    For α = 0.d₁d₂…d_L, {10ⁿ α} = 0.d_{n+1}…d_L padded with zeros.
    We approximate with `precision` digits of the tail (sufficient
    for star discrepancy to better than 10^(-precision)).
    """
    L = len(digit_string)
    # Convert to numeric arrays for speed.
    digits = np.frombuffer(digit_string.encode(), dtype=np.uint8) - ord('0')
    # tail[n] = sum_{j=0..p-1} digit[n+j] * 10^(-(j+1))
    weights = 10.0 ** (-(np.arange(precision) + 1))
    out = np.zeros(L, dtype=np.float64)
    # Vectorised but bounded by precision per index — use a loop here.
    pad_digits = np.concatenate([digits,
                                  np.zeros(precision, dtype=np.uint8)])
    for j in range(precision):
        out += pad_digits[j:j + L] * weights[j]
    return out


def star_discrepancy(values):
    """Star discrepancy D_N* of a sequence of values in [0, 1)."""
    sorted_v = np.sort(np.asarray(values, dtype=np.float64))
    N = len(sorted_v)
    i = np.arange(1, N + 1, dtype=np.float64)
    d_plus = float(np.max(i / N - sorted_v))
    d_minus = float(np.max(sorted_v - (i - 1) / N))
    return max(d_plus, d_minus)


def compute_at_blocks(digit_string, label, block_sizes=None):
    """Star discrepancy at a series of block sizes N ∈ block_sizes,
    plus the full-length value."""
    L = len(digit_string)
    if block_sizes is None:
        # Geometric block sizes.
        bs = []
        N = 100
        while N < L:
            bs.append(N)
            N = int(N * 1.6)
        bs.append(L)
        block_sizes = bs

    t0 = time.time()
    full_orbit = tail_orbit(digit_string)
    print(f"  built orbit ({L} pts) in {time.time() - t0:.2f}s")

    rows = []
    for N in block_sizes:
        d = star_discrepancy(full_orbit[:N])
        rows.append((N, d))
    return rows, full_orbit


# Compute for each variant.
results = {}
for label, digits in [
    ('C_Bundle', digits_bundle),
    ('C_Bundle_sorted', digits_bundle_sorted),
    ('C_Surv', digits_surv),
    ('C_Surv_prime_m', digits_surv_pm),
    ('C_Surv_comp_m', digits_surv_cm),
]:
    print(f"{label}:")
    rows, orbit = compute_at_blocks(digits, label)
    results[label] = (rows, orbit, len(digits))
    print(f"  D_L* = {rows[-1][1]:.5f}  at  N = L = {rows[-1][0]}")
    print()

# Summary table.
print("=" * 78)
print("Star discrepancy summary  (D_N* at each block size)")
print("=" * 78)

# Choose comparison block sizes shared across all (use the smallest L).
L_min = min(results[k][2] for k in results)

shared_blocks = [500, 1000, 2000, 4000, 8000]
shared_blocks = [b for b in shared_blocks if b <= L_min]

header = f"{'label':<20}"
for N in shared_blocks:
    header += f"  N={N:>5}"
header += f"  D_L*    L"
print(header)
print("-" * len(header))

for label in ['C_Bundle', 'C_Bundle_sorted', 'C_Surv',
              'C_Surv_prime_m', 'C_Surv_comp_m']:
    rows, orbit, L = results[label]
    line = f"{label:<20}"
    for N in shared_blocks:
        d = star_discrepancy(orbit[:N])
        line += f"  {d:>7.4f}"
    line += f"  {rows[-1][1]:>6.4f}  {L}"
    print(line)
print()

# Reference: 1/√N for uniform random.
print("Reference:  random uniform sequence has D_N* ~ 1/√(2N)")
for N in shared_blocks:
    print(f"  N={N}: 1/√(2N) ≈ {1.0/np.sqrt(2*N):.4f}")
print()

# Reference: Erdős-Copeland Champernowne D_N = O((log N)/√N).
# Concrete constant unclear; use C=1 as scale.
print("Reference:  Erdős-Copeland-type D_N ~ (log N)/√N (constant ~1)")
for N in shared_blocks:
    print(f"  N={N}: (log N)/√N ≈ {np.log(N)/np.sqrt(N):.4f}")

# --- Plot: D_N vs N on log-log ---
fig, ax = plt.subplots(figsize=(11, 7))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

colors = {
    'C_Bundle':         '#ffa642',
    'C_Bundle_sorted':  '#bbbbbb',
    'C_Surv':           '#a8e22d',
    'C_Surv_prime_m':   '#5cd4ff',
    'C_Surv_comp_m':    '#cc66ff',
}

for label, color in colors.items():
    rows, orbit, L = results[label]
    Ns = np.array([r[0] for r in rows])
    Ds = np.array([r[1] for r in rows])
    ax.loglog(Ns, Ds, 'o-', color=color, linewidth=1.4,
              markersize=5, label=f'{label}  (L={L})')

# Reference lines.
N_ref = np.array([100, 50000])
ax.loglog(N_ref, 1.0 / np.sqrt(2 * N_ref), '--', color='#666',
          linewidth=0.7, label='1/√(2N)')
ax.loglog(N_ref, np.log(N_ref) / np.sqrt(N_ref), ':', color='#666',
          linewidth=0.7, label='(log N)/√N')

ax.set_xlabel('N (block size)', color='white', fontsize=11)
ax.set_ylabel('D_N*  (star discrepancy)', color='white', fontsize=11)
ax.set_title(
    'Star discrepancy D_N* of {10ⁿ α} orbits  '
    '— [2, 10], K=400',
    color='white', fontsize=12)
ax.tick_params(colors='white', which='both')
for spine in ax.spines.values():
    spine.set_color('#333')
ax.legend(loc='lower left', facecolor='#1a1a1a',
          edgecolor='#333', labelcolor='white', fontsize=9)
ax.grid(alpha=0.15, color='#444', which='both')
plt.tight_layout()
plt.savefig('discrepancy.png', dpi=170, facecolor='#0a0a0a',
            bbox_inches='tight')
print()
print("-> discrepancy.png")
