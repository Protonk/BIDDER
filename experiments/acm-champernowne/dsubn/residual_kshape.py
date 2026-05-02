"""
EXP-DSUBN-01: residual K-shape invariance.

Q: Is the t-shape of F_N(t) − t K-invariant for each construction,
   or does it morph with K?

For each of the five constructions, compute the empirical CDF
residual F_N(t) − t on a common t-grid at K ∈ {100, 200, 400,
800, 1600, 3200, 6400}. Normalize by peak |residual| (= D_N*) and
overlay the seven normalized curves per construction. K is encoded
by color (cool → small K, warm → large K).

If curves overlap: shape K-invariant. The orbit has a t-fingerprint;
only amplitude is K-dependent.
If curves spread: shape morphs with K. Each K-decade has its own
profile.

Comparison: C_Bundle_sorted (Erdős–Copeland-class, known b-normal)
serves as the control.
"""

import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from sympy import isprime

W = 9
n_0 = 2
n_1 = n_0 + W - 1
PRECISION = 18
K_VALUES = [100, 200, 400, 800, 1600, 3200, 6400]
T_GRID = np.linspace(0.0, 1.0, 401)


def n_primes_vec(n, k):
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


def build_orbits_for_K(k):
    parts = [(n, n_primes_vec(n, k)) for n in range(n_0, n_1 + 1)]
    all_atoms = np.concatenate([arr for _, arr in parts])
    stream_tag = np.concatenate([np.full_like(arr, n)
                                  for n, arr in parts])

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
    for label, ds in digits.items():
        L = len(ds)
        ds_arr = np.frombuffer(ds.encode(),
                                dtype=np.uint8) - ord('0')
        weights = 10.0 ** (-(np.arange(PRECISION) + 1))
        pad = np.concatenate([ds_arr,
                              np.zeros(PRECISION, dtype=np.uint8)])
        orbit = np.zeros(L, dtype=np.float64)
        for j in range(PRECISION):
            orbit += pad[j:j + L] * weights[j]
        orbits[label] = orbit
    return orbits


def residual_on_grid(orbit, t_grid):
    sorted_v = np.sort(orbit)
    N = len(sorted_v)
    counts = np.searchsorted(sorted_v, t_grid, side='right')
    F_N = counts / N
    return F_N - t_grid


LABELS = ['C_Bundle', 'C_Bundle_sorted', 'C_Surv',
          'C_Surv_prime_m', 'C_Surv_comp_m']

# residuals[label][K_idx] = residual array on T_GRID
residuals = {label: np.zeros((len(K_VALUES), len(T_GRID)))
              for label in LABELS}
peaks = {label: np.zeros(len(K_VALUES)) for label in LABELS}

t0 = time.time()
for i, K in enumerate(K_VALUES):
    orbits = build_orbits_for_K(K)
    for label in LABELS:
        res = residual_on_grid(orbits[label], T_GRID)
        residuals[label][i, :] = res
        peaks[label][i] = float(np.abs(res).max())
    print(f"K = {K} done (t = {time.time() - t0:.1f}s)")

print()
print("Peak |F_N(t) − t| = D_N* per (construction, K):")
print(f"{'construction':<20} " + "  ".join(f"K={K:>5}" for K in K_VALUES))
for label in LABELS:
    line = f"{label:<20} "
    for p in peaks[label]:
        line += f"  {p:>6.4f}"
    print(line)
print()

# Pairwise correlation of normalized residuals across K, per construction.
print("Mean pairwise Pearson correlation of normalized residuals:")
print("  (1.00 = K-invariant shape; lower = shape morphs with K)")
print(f"{'construction':<20}  mean ρ    min ρ   K_pair_argmin")
for label in LABELS:
    norm_res = residuals[label] / peaks[label][:, None]
    K_n = norm_res.shape[0]
    rhos = []
    pair_indices = []
    for i in range(K_n):
        for j in range(i + 1, K_n):
            r1 = norm_res[i, :]
            r2 = norm_res[j, :]
            rho = float(np.corrcoef(r1, r2)[0, 1])
            rhos.append(rho)
            pair_indices.append((K_VALUES[i], K_VALUES[j]))
    rhos = np.array(rhos)
    idx_min = int(np.argmin(rhos))
    print(f"{label:<20}  {rhos.mean():>+.4f}  {rhos.min():>+.4f}  "
          f"K = ({pair_indices[idx_min][0]}, {pair_indices[idx_min][1]})")
print()

# --- Plot: one panel per construction, normalized residuals overlaid ---
cmap = LinearSegmentedColormap.from_list('Kgrad', [
    '#3da9c4',  # cool: small K
    '#7dd3e0',
    '#f5e2a3',
    '#f9b27a',
    '#e8643a',  # warm: large K
])

fig, axes = plt.subplots(5, 1, figsize=(12, 16), sharex=True)
fig.patch.set_facecolor('#0a0a0a')

for ax, label in zip(axes, LABELS):
    ax.set_facecolor('#0a0a0a')
    ax.axhline(0, color='#444', linewidth=0.6, linestyle='--',
               alpha=0.7)
    norm_res = residuals[label] / peaks[label][:, None]
    for i, K in enumerate(K_VALUES):
        color = cmap(i / (len(K_VALUES) - 1))
        ax.plot(T_GRID, norm_res[i, :], color=color, linewidth=1.2,
                alpha=0.85,
                label=f'K = {K} (D_N*={peaks[label][i]:.3f})')
    ax.set_ylabel(f'{label}\n(F_N − t) / D_N*', color='white',
                  fontsize=10)
    ax.set_xlim(0, 1)
    ax.set_ylim(-1.15, 1.15)
    ax.tick_params(colors='white', which='both')
    for spine in ax.spines.values():
        spine.set_color('#333')
    ax.legend(loc='lower right', facecolor='#1a1a1a',
              edgecolor='#333', labelcolor='white', fontsize=7,
              ncol=2)
    ax.grid(alpha=0.10, color='#444')

axes[-1].set_xlabel('t  (orbit value in [0, 1])',
                     color='white', fontsize=11)
fig.suptitle(
    'Residual K-shape invariance — (F_N(t) − t) / D_N*\n'
    'overlap = K-invariant shape; spread = K-dependent morphing',
    color='white', fontsize=13, y=0.995)

plt.tight_layout()
plt.savefig('residual_kshape.png', dpi=170,
            facecolor='#0a0a0a', bbox_inches='tight')
print("-> residual_kshape.png")
