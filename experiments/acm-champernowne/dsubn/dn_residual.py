"""
F_N(t) − t residual: visualisation of star discrepancy.

For α with digit expansion 0.d₁d₂…, the orbit {10ⁿ α} for
n = 0, …, L − 1 has empirical CDF
    F_N(t) = #{i : {10ⁱ α} ≤ t} / N.
The signed residual F_N(t) − t hits ±D_N* at most.

Plot for the five constructions at the Two Tongues panel
([2, 10], k = 400):
    C_Bundle, C_Bundle_sorted, C_Surv,
    C_Surv_prime_m, C_Surv_comp_m.

The maximum vertical excursion of each curve is its star
discrepancy. Visually, this turns the scalar D_N* into a *shape*
on the [0, 1] interval — bracketing differences become curve
amplitudes rather than just numbers.
"""

import numpy as np
import matplotlib.pyplot as plt
from sympy import isprime

W = 9
n_0 = 2
n_1 = n_0 + W - 1
k = 400
PRECISION = 18


def n_primes_vec(n, k):
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


# Build constructions.
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

S_prime_set = set(int(c) for c, pm in zip(S, prime_m_arr) if pm)
S_comp_set = set(int(c) for c, pm in zip(S, prime_m_arr) if not pm)
S_set = set(int(c) for c in S)

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


digits = {
    'C_Bundle':        build_digits(all_atoms.tolist()),
    'C_Bundle_sorted': build_digits(sorted(int(c) for c in unique_vals)),
    'C_Surv':          build_digits(surv_appearance),
    'C_Surv_prime_m':  build_digits(surv_pm_appearance),
    'C_Surv_comp_m':   build_digits(surv_cm_appearance),
}


def tail_orbit(digit_string, precision=PRECISION):
    L = len(digit_string)
    digits_arr = np.frombuffer(digit_string.encode(),
                                dtype=np.uint8) - ord('0')
    weights = 10.0 ** (-(np.arange(precision) + 1))
    pad_digits = np.concatenate([digits_arr,
                                  np.zeros(precision, dtype=np.uint8)])
    out = np.zeros(L, dtype=np.float64)
    for j in range(precision):
        out += pad_digits[j:j + L] * weights[j]
    return out


orbits = {label: tail_orbit(d) for label, d in digits.items()}

# --- Plot ---
fig, ax = plt.subplots(figsize=(13, 8))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

# Colour scheme aligned with the existing primality work.
colors = {
    'C_Bundle':         '#ffa642',
    'C_Bundle_sorted':  '#bbbbbb',
    'C_Surv':           '#a8e22d',
    'C_Surv_prime_m':   '#5cd4ff',
    'C_Surv_comp_m':    '#cc66ff',
}

# Reference: zero line (uniform CDF).
ax.axhline(0, color='#444', linestyle='--', linewidth=0.6,
           alpha=0.7)

results = []
for label, orbit in orbits.items():
    sorted_v = np.sort(orbit)
    N = len(sorted_v)
    cdf_x = sorted_v
    cdf_y = np.arange(1, N + 1) / N
    residual = cdf_y - cdf_x
    color = colors[label]
    ax.plot(cdf_x, residual, color=color, linewidth=1.2,
            label=f'{label}  (N={N})', alpha=0.92)
    # Mark the maximum |residual| point.
    idx_max = int(np.argmax(np.abs(residual)))
    ax.plot(cdf_x[idx_max], residual[idx_max], 'o', color=color,
            markersize=6, markeredgecolor='white',
            markeredgewidth=0.5, zorder=5)
    d_star = float(np.abs(residual).max())
    results.append((label, N, d_star,
                    cdf_x[idx_max], residual[idx_max]))

# Faint horizontal guides at ±D_N max for reference.
d_max = max(r[2] for r in results)
ax.axhline(d_max, color='#333', linestyle=':', linewidth=0.5,
           alpha=0.6)
ax.axhline(-d_max, color='#333', linestyle=':', linewidth=0.5,
           alpha=0.6)

ax.set_xlim(0, 1)
y_pad = d_max * 1.25
ax.set_ylim(-y_pad, y_pad)
ax.set_xlabel('t  (orbit value in [0, 1])',
              color='white', fontsize=11)
ax.set_ylabel('F_N(t) − t  (signed residual from uniform)',
              color='white', fontsize=11)
ax.set_title(
    'D_N residual — orbits {10ⁿ α} at [2, 10], k = 400\n'
    'max |F_N − t| of each curve is its star discrepancy D_N*; '
    'circles mark attainment',
    color='white', fontsize=12)
ax.tick_params(colors='white', which='both')
for spine in ax.spines.values():
    spine.set_color('#333')
ax.legend(loc='upper right', facecolor='#1a1a1a',
          edgecolor='#333', labelcolor='white', fontsize=9)
ax.grid(alpha=0.15, color='#444')
plt.tight_layout()
plt.savefig('dn_residual.png', dpi=180, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> dn_residual.png")
print()
print("D_N* attainment per construction:")
print(f"{'label':<20} {'N':>6} {'D_N*':>8} {'t*':>8} "
      f"{'(F_N − t)(t*)':>14}")
for label, N, d_star, t_star, sgn_res in results:
    print(f"{label:<20} {N:>6} {d_star:>8.4f} {t_star:>8.4f} "
          f"{sgn_res:>+14.4f}")
