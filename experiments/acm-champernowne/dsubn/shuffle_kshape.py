"""
EXP-DSUBN-02: Shuffle-null K-shape map.

Discharges the destroyer that residual_kshape.py's "prime-m has
K-invariant shape (mean ρ = 0.91); comp-m does not (mean ρ = 0.24)"
claim is missing. Holds the atom set fixed; varies only the ordering.

Three orderings per construction:

  raw            — first-appearance order from C_Bundle (existing
                   baseline; reproduces residual_kshape.py).
  entry-shuffled — same atoms, random permutation. Marginal
                   distribution preserved; all entry order destroyed.
  d-matched      — atoms grouped by digit length, shuffled within
                   each group. The positional/length-class skeleton
                   is preserved (which positions in the stream are
                   filled by d-digit atoms is unchanged); fine-
                   grained order within a length class is destroyed.

Reading the result:

  prime-m K-invariance dies under shuffle but survives d-match
       → positional / digit-length-class property
  prime-m K-invariance dies under both
       → fine-grained entry-order property
  prime-m K-invariance survives shuffle
       → marginal-distribution property; the original chart's
         claim downgrades to "the prime-m atom marginals are
         what give the K-invariance," not entry order

Aligned with experiments/VISUAL-REDUCTION-DISCIPLINE.md
§hierarchy ("arithmetic tomography: held-fixed confounder
coordinates") and §subtraction-rule (entry-order shuffle as
canonical destroyer for shape claims).
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
SEED = 42

LABELS = ['C_Surv_prime_m', 'C_Surv_comp_m']
VARIANTS = ['raw', 'entry-shuffled', 'd-matched']


def n_primes_vec(n, k):
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


def build_atom_sequences(k):
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

    S_prime_set = set(int(c) for c, pm in zip(S, prime_m_arr) if pm)
    S_comp_set = set(int(c) for c, pm in zip(S, prime_m_arr) if not pm)

    seen = set()
    unique_in_appearance = []
    for c in all_atoms:
        c_int = int(c)
        if c_int not in seen:
            seen.add(c_int)
            unique_in_appearance.append(c_int)

    return {
        'C_Surv_prime_m': [c for c in unique_in_appearance
                           if c in S_prime_set],
        'C_Surv_comp_m':  [c for c in unique_in_appearance
                           if c in S_comp_set],
    }


def variant_sequences(seq, rng):
    arr = list(seq)
    n = len(arr)
    perm = rng.permutation(n)
    shuffled = [arr[i] for i in perm]

    by_d = {}
    for i, c in enumerate(arr):
        d = len(str(c))
        by_d.setdefault(d, []).append(i)
    dmatched = list(arr)
    for d, indices in by_d.items():
        values = [arr[i] for i in indices]
        local_perm = rng.permutation(len(values))
        for i, p in zip(indices, local_perm):
            dmatched[i] = values[p]

    return {'raw': arr, 'entry-shuffled': shuffled,
            'd-matched': dmatched}


def make_orbit(atom_seq):
    ds = ''.join(str(c) for c in atom_seq)
    L = len(ds)
    ds_arr = np.frombuffer(ds.encode(), dtype=np.uint8) - ord('0')
    weights = 10.0 ** (-(np.arange(PRECISION) + 1))
    pad = np.concatenate([ds_arr, np.zeros(PRECISION, dtype=np.uint8)])
    orbit = np.zeros(L, dtype=np.float64)
    for j in range(PRECISION):
        orbit += pad[j:j + L] * weights[j]
    return orbit


def residual_on_grid(orbit, t_grid):
    sorted_v = np.sort(orbit)
    counts = np.searchsorted(sorted_v, t_grid, side='right')
    return counts / len(sorted_v) - t_grid


# --- Sweep ---

residuals = {(lbl, var): np.zeros((len(K_VALUES), len(T_GRID)))
             for lbl in LABELS for var in VARIANTS}
peaks = {(lbl, var): np.zeros(len(K_VALUES))
         for lbl in LABELS for var in VARIANTS}

rng = np.random.default_rng(SEED)
t0 = time.time()
for ki, K in enumerate(K_VALUES):
    seqs = build_atom_sequences(K)
    for lbl in LABELS:
        variants = variant_sequences(seqs[lbl], rng)
        for var in VARIANTS:
            orbit = make_orbit(variants[var])
            res = residual_on_grid(orbit, T_GRID)
            residuals[(lbl, var)][ki, :] = res
            peaks[(lbl, var)][ki] = float(np.abs(res).max())
    print(f"K = {K} done (t = {time.time() - t0:.1f}s)")

# --- Pairwise correlations ---

print()
print("Mean pairwise Pearson ρ of normalised residuals across K:")
print(f"{'construction':<20} {'variant':<16}  mean ρ    min ρ")
print('-' * 60)
correlations = {}
for lbl in LABELS:
    for var in VARIANTS:
        norm_res = residuals[(lbl, var)] / peaks[(lbl, var)][:, None]
        rhos = []
        for i in range(len(K_VALUES)):
            for j in range(i + 1, len(K_VALUES)):
                rhos.append(float(np.corrcoef(norm_res[i],
                                              norm_res[j])[0, 1]))
        rhos = np.array(rhos)
        correlations[(lbl, var)] = (rhos.mean(), rhos.min())
        print(f"{lbl:<20} {var:<16}  "
              f"{rhos.mean():>+.4f}  {rhos.min():>+.4f}")

# --- Plot ---

cmap = LinearSegmentedColormap.from_list('Kgrad', [
    '#3da9c4', '#7dd3e0', '#f5e2a3', '#f9b27a', '#e8643a',
])

fig, axes = plt.subplots(3, 2, figsize=(13, 12),
                          sharex=True, sharey=True)
fig.patch.set_facecolor('#0a0a0a')

for ri, var in enumerate(VARIANTS):
    for ci, lbl in enumerate(LABELS):
        ax = axes[ri, ci]
        ax.set_facecolor('#0a0a0a')
        ax.axhline(0, color='#444', linewidth=0.6,
                   linestyle='--', alpha=0.7)
        norm_res = residuals[(lbl, var)] / peaks[(lbl, var)][:, None]
        for ki, K in enumerate(K_VALUES):
            color = cmap(ki / (len(K_VALUES) - 1))
            ax.plot(T_GRID, norm_res[ki, :], color=color,
                    linewidth=1.0, alpha=0.85)
        mean_rho, min_rho = correlations[(lbl, var)]
        rho_color = '#a8e22d' if mean_rho > 0.7 else (
            '#f9b27a' if mean_rho > 0.4 else '#ff79c6')
        ax.text(0.02, 0.05,
                f'mean ρ = {mean_rho:+.2f}\nmin ρ = {min_rho:+.2f}',
                color=rho_color, fontsize=10,
                transform=ax.transAxes,
                family='monospace',
                verticalalignment='bottom')
        if ri == 0:
            ax.set_title(lbl, color='white', fontsize=12)
        if ci == 0:
            ax.set_ylabel(f'{var}\n(F_N − t) / D_N*',
                           color='white', fontsize=10)
        ax.set_ylim(-1.2, 1.2)
        ax.set_xlim(0, 1)
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#333')
        ax.grid(alpha=0.1, color='#444')

axes[-1, 0].set_xlabel('t  (orbit value in [0, 1])',
                        color='white', fontsize=11)
axes[-1, 1].set_xlabel('t  (orbit value in [0, 1])',
                        color='white', fontsize=11)

handles = [plt.Line2D([0], [0],
                       color=cmap(i / (len(K_VALUES) - 1)),
                       linewidth=2, label=f'K = {K}')
           for i, K in enumerate(K_VALUES)]
fig.legend(handles=handles, loc='upper right',
           bbox_to_anchor=(0.995, 0.995),
           facecolor='#1a1a1a', edgecolor='#333',
           labelcolor='white', fontsize=8, ncol=1)

fig.suptitle(
    'Shuffle-null K-shape map — (F_N(t) − t) / D_N*\n'
    'rows: ordering of the same atom set;  cols: construction;  '
    'ρ green = K-invariant, orange = mixed, magenta = K-dependent',
    color='white', fontsize=11, y=0.995)

plt.tight_layout(rect=[0, 0, 0.96, 0.97])
plt.savefig('shuffle_kshape.png', dpi=170,
            facecolor='#0a0a0a', bbox_inches='tight')
print()
print('-> shuffle_kshape.png')
