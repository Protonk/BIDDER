"""
Primality of the survivor collection — does it relate to the L1 fit?

At the Two Tongues panel [n_0, n_1] = [2, 10], k = 400:

1. Primality of survivor integer c — structurally trivial: prime
   survivors = window primes. Reports for completeness.
2. Primality of cofactor m = c / d_source — non-trivial. Each
   survivor c has a unique source stream d ∈ window; m = c / d.
   Tests isprime(m) per survivor.
3. Omega(c) distribution — total prime factors with multiplicity.

Then stratifies the leading-digit L1 deviation by primality
category and checks whether prime-cofactor survivors track the
bundle's L1 trajectory differently from composite-cofactor ones.
"""

import time
import numpy as np
from sympy import isprime, factorint


W = 9
n_0 = 2
n_1 = n_0 + W - 1
k = 400


def n_primes_vec(n, k):
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


# Build bundle and survivors with first-appearance order preserved.
parts_per_stream = []
for n in range(n_0, n_1 + 1):
    parts_per_stream.append((n, n_primes_vec(n, k)))
all_atoms = np.concatenate([arr for _, arr in parts_per_stream])
n_atoms = all_atoms.size

# Stream tag per atom slot.
stream_tag = np.concatenate([
    np.full_like(arr, n) for n, arr in parts_per_stream
])

unique_vals, first_idx, counts = np.unique(
    all_atoms, return_index=True, return_counts=True)
surv_mask = counts == 1
S = unique_vals[surv_mask]
sources_S = stream_tag[first_idx[surv_mask]]
print(f"Panel: [{n_0}, {n_1}], k = {k}")
print(f"Bundle unique integers: {len(unique_vals)}")
print(f"Survivors: {len(S)}, max = {int(S.max())}")
print()

# (1) Primality of c itself.
t0 = time.time()
prime_c = np.array([isprime(int(c)) for c in S])
print(f"isprime(c) over {len(S)} survivors "
      f"in {time.time() - t0:.2f}s")
print(f"Prime survivors:   {prime_c.sum()} = "
      f"{[int(c) for c in S[prime_c]]}")
print(f"Composite count:   {(~prime_c).sum()}")
print()

# (2) Primality of cofactor m = c / d.
m_S = S // sources_S
t0 = time.time()
prime_m = np.array([isprime(int(m)) for m in m_S])
print(f"isprime(m) over {len(S)} cofactors "
      f"in {time.time() - t0:.2f}s")
print(f"Prime-cofactor survivors:     {prime_m.sum()} "
      f"({prime_m.mean() * 100:.1f}% of S)")
print(f"Composite-cofactor survivors: {(~prime_m).sum()} "
      f"({(~prime_m).mean() * 100:.1f}% of S)")
print()

# Stratify by source d.
print("Per source d: prime-cofactor fraction")
print(f"{'d':>3} {'|S_d|':>6} {'prime m':>8} {'frac':>6}")
for d in range(n_0, n_1 + 1):
    md = sources_S == d
    nd = int(md.sum())
    if nd == 0:
        continue
    pm = int(prime_m[md].sum())
    print(f"{d:>3} {nd:>6} {pm:>8} {pm / nd:>6.3f}")
print()

# (3) Omega(c) distribution.
t0 = time.time()
big_omega = np.array([
    sum(factorint(int(c)).values()) for c in S
])
print(f"Omega(c) over {len(S)} survivors "
      f"in {time.time() - t0:.2f}s")
unique_om, counts_om = np.unique(big_omega, return_counts=True)
print("Omega(c) distribution:")
for om, cnt in zip(unique_om, counts_om):
    print(f"  Omega = {om}: {cnt} ({100 * cnt / len(S):.1f}%)")
print()

# Compare with bundle integers (full set).
big_omega_B = np.array([
    sum(factorint(int(c)).values()) for c in unique_vals
])
print("Omega(c) distribution — bundle vs survivors:")
print(f"{'Omega':>6} {'bundle':>10} {'survivors':>12} "
      f"{'B frac':>8} {'S frac':>8}")
all_om = sorted(set(big_omega.tolist()) | set(big_omega_B.tolist()))
for om in all_om:
    bn = int((big_omega_B == om).sum())
    sn = int((big_omega == om).sum())
    print(f"{om:>6} {bn:>10} {sn:>12} "
          f"{bn / len(unique_vals):>8.3f} "
          f"{sn / len(S):>8.3f}")
print()

# (4) Stratify L1 deviation by primality category.
# Compute leading-digit L1 deviation accumulated along the
# bundle's read order, but for each subset of S separately.

# For each atom slot, mark whether it's a prime-cofactor survivor,
# composite-cofactor survivor, or non-survivor.
# Build masks at slot level.

# Find which atom slot corresponds to each survivor (first-appearance).
S_to_slot = {int(c): int(first_idx[i])
              for i, c in enumerate(unique_vals) if surv_mask[i]}

prime_m_set = set(int(c) for c, pm in zip(S, prime_m) if pm)
composite_m_set = set(int(c) for c, pm in zip(S, prime_m) if not pm)

# Cumulative leading-digit counts.
lead = np.zeros(n_atoms, dtype=np.int64)
for i, c in enumerate(all_atoms):
    c_int = int(c)
    log_floor = int(np.floor(np.log10(c_int)))
    lead[i] = c_int // 10**log_floor

u9 = np.full(9, 1.0 / 9)


def running_l1(atom_subset_mask):
    """Running L1 deviation for the leading-digit distribution
    of atoms (in slot order) that pass the mask, counting each
    integer at first appearance only.
    """
    seen = set()
    counts = np.zeros(9, dtype=np.int64)
    out_l1 = []
    out_idx = []
    for i in range(n_atoms):
        c = int(all_atoms[i])
        if c in seen:
            continue
        seen.add(c)
        if not atom_subset_mask(c, i):
            continue
        counts[lead[i] - 1] += 1
        tot = counts.sum()
        if tot == 0:
            continue
        p = counts / tot
        out_l1.append(np.abs(p - u9).sum())
        out_idx.append(i)
    return np.array(out_idx), np.array(out_l1)


def is_bundle(c, i):
    return True


def is_surv_prime_m(c, i):
    return c in prime_m_set


def is_surv_comp_m(c, i):
    return c in composite_m_set


idx_b, l1_b = running_l1(is_bundle)
idx_pm, l1_pm = running_l1(is_surv_prime_m)
idx_cm, l1_cm = running_l1(is_surv_comp_m)

print("End-of-stream L1 deviations (leading digit, 1..9):")
print(f"  bundle               (n={len(idx_b)}):  L1 = {l1_b[-1]:.4f}")
print(f"  surv (prime cofactor)(n={len(idx_pm)}): L1 = "
      f"{l1_pm[-1]:.4f}")
print(f"  surv (composite cofactor)(n={len(idx_cm)}): L1 = "
      f"{l1_cm[-1]:.4f}")

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(11, 6))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')
ax.plot(idx_b, l1_b, color='#ffa642', linewidth=1.4,
        label=f'bundle  (n={len(idx_b)})')
ax.plot(idx_pm, l1_pm, color='#5cd4ff', linewidth=1.4,
        label=f'survivors, prime cofactor  (n={len(idx_pm)})')
ax.plot(idx_cm, l1_cm, color='#cc66ff', linewidth=1.4,
        label=f'survivors, composite cofactor  (n={len(idx_cm)})')
ax.set_yscale('log')
ax.set_xlabel('atoms processed (read order)',
              color='white', fontsize=11)
ax.set_ylabel('L1 deviation from uniform (leading digit, 1-9)',
              color='white', fontsize=11)
ax.set_title(
    'L1 trajectory stratified by cofactor primality  '
    f'([{n_0},{n_1}], k={k})',
    color='white', fontsize=12)
ax.tick_params(colors='white', which='both')
for spine in ax.spines.values():
    spine.set_color('#333')
ax.legend(loc='upper right', facecolor='#1a1a1a',
          edgecolor='#333', labelcolor='white', fontsize=10)
ax.grid(alpha=0.15, color='#444', which='both')
plt.tight_layout()
plt.savefig('primality_l1.png', dpi=170,
            facecolor='#0a0a0a', bbox_inches='tight')
print()
print("-> primality_l1.png")
