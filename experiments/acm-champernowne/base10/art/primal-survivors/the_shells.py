"""
THE SHELLS — D_N as ring fuzz.

For each of the five constructions at the Two Tongues panel, plot
the orbit {10ⁿ α} on a concentric ring. Angle θ = 2π α_n. Radial
offset is gaussian with σ proportional to the construction's star
discrepancy D_N* — sharper rings for lower discrepancy, fuzzier
for higher. Innermost ring = lowest D_N* = most uniform.

The visual variable is "ring thickness / sharpness," and it is
literally driven by D_N*. Where the orbit has angular structure
(non-uniform clumping along [0, 1]), it shows up as bright and
dim arcs.
"""

import numpy as np
import matplotlib.pyplot as plt
from numpy.random import default_rng
from sympy import isprime

W = 9
n_0 = 2
n_1 = n_0 + W - 1
k = 400
PRECISION = 18
N_DOTS = 2200   # subsample per ring for visual consistency
SEED = 2026


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


def build_digits(integers_in_order):
    return ''.join(str(int(c)) for c in integers_in_order)


digits = {
    'C_Bundle':        build_digits(all_atoms.tolist()),
    'C_Bundle_sorted': build_digits(sorted(int(c) for c in unique_vals)),
    'C_Surv':          build_digits(surv_app),
    'C_Surv_prime_m':  build_digits(surv_pm_app),
    'C_Surv_comp_m':   build_digits(surv_cm_app),
}


def tail_orbit(digit_string, precision=PRECISION):
    L = len(digit_string)
    digits_arr = np.frombuffer(digit_string.encode(),
                                dtype=np.uint8) - ord('0')
    weights = 10.0 ** (-(np.arange(precision) + 1))
    pad = np.concatenate([digits_arr,
                          np.zeros(precision, dtype=np.uint8)])
    out = np.zeros(L, dtype=np.float64)
    for j in range(precision):
        out += pad[j:j + L] * weights[j]
    return out


def star_discrepancy(values):
    sorted_v = np.sort(np.asarray(values, dtype=np.float64))
    N = len(sorted_v)
    i = np.arange(1, N + 1, dtype=np.float64)
    d_plus = float(np.max(i / N - sorted_v))
    d_minus = float(np.max(sorted_v - (i - 1) / N))
    return max(d_plus, d_minus)


orbits = {label: tail_orbit(d) for label, d in digits.items()}
D_stars = {label: star_discrepancy(o) for label, o in orbits.items()}

sorted_labels = sorted(D_stars.keys(), key=lambda k: D_stars[k])

print("Ring order (innermost → outermost, by D_N*):")
for label in sorted_labels:
    print(f"  {label:<20}  D_N* = {D_stars[label]:.4f}   "
          f"L = {len(orbits[label])}")

colors = {
    'C_Bundle':         '#ffa642',
    'C_Bundle_sorted':  '#bbbbbb',
    'C_Surv':           '#a8e22d',
    'C_Surv_prime_m':   '#5cd4ff',
    'C_Surv_comp_m':    '#cc66ff',
}

# --- Render ---
fig, ax = plt.subplots(figsize=(12, 12))
fig.patch.set_facecolor('#050505')
ax.set_facecolor('#050505')
ax.set_aspect('equal')
ax.axis('off')

rng = default_rng(seed=SEED)

R_INNER = 1.6
R_STEP = 0.95
SIGMA_K = 1.5   # ring fuzz scale: σ_radial = SIGMA_K · D_N*

for ring_idx, label in enumerate(sorted_labels):
    orbit_full = orbits[label]
    if len(orbit_full) > N_DOTS:
        idx_sub = rng.choice(len(orbit_full), N_DOTS,
                              replace=False)
        orbit = orbit_full[idx_sub]
    else:
        orbit = orbit_full

    D_star = D_stars[label]
    color = colors[label]
    r_center = R_INNER + ring_idx * R_STEP
    sigma = D_star * SIGMA_K

    theta = 2 * np.pi * orbit
    r_offset = rng.normal(0, sigma, size=len(orbit))
    r = r_center + r_offset
    x = r * np.cos(theta)
    y = r * np.sin(theta)

    # Halo (large, low alpha).
    ax.scatter(x, y, s=12.0, color=color, alpha=0.10,
               linewidths=0, zorder=3)
    # Mid (medium).
    ax.scatter(x, y, s=4.5, color=color, alpha=0.30,
               linewidths=0, zorder=4)
    # Crisp.
    ax.scatter(x, y, s=1.2, color=color, alpha=0.75,
               linewidths=0, zorder=5)

    # Faint guide circle at ring center radius.
    th = np.linspace(0, 2 * np.pi, 240)
    ax.plot(r_center * np.cos(th), r_center * np.sin(th),
            color=color, linewidth=0.35, alpha=0.16,
            zorder=2)

# Center crosshair.
ax.plot([0, 0], [-0.10, 0.10], color='#444', linewidth=0.8,
        alpha=0.5, zorder=10)
ax.plot([-0.10, 0.10], [0, 0], color='#444', linewidth=0.8,
        alpha=0.5, zorder=10)

max_r = R_INNER + (len(sorted_labels) - 1) * R_STEP + 0.65
ax.set_xlim(-max_r, max_r)
ax.set_ylim(-max_r, max_r)

# Title — same convention as THE COIL and ECHO CATHEDRAL.
fig.text(0.95, 0.060, 'THE SHELLS', color='#ccc',
         fontsize=14, ha='right', va='bottom',
         family='serif', weight='bold')
fig.text(0.95, 0.045,
         'orbit {10ⁿ α} on the unit circle — ring fuzz ∝ D_N*',
         color='#777', fontsize=9, ha='right', va='top',
         style='italic', family='serif')
fig.text(0.95, 0.030,
         'innermost: prime-cofactor (sharpest)   ·   '
         'outermost: composite-cofactor',
         color='#555', fontsize=8, ha='right', va='top',
         family='serif')

plt.savefig('the_shells.png', dpi=180, facecolor='#050505',
            bbox_inches='tight')
print()
print("-> the_shells.png")
