"""
EXP-DSUBN-03: Refinement-deviation K-shape.

Subtracts the pooled C_Surv parent from each cofactor refinement
and shows what the refinement adds at each (K, t).

  Panel A: F_N^{C_Surv_prime_m}(t) − F_N^{C_Surv}(t)
  Panel B: F_N^{C_Surv_comp_m}(t)  − F_N^{C_Surv}(t)

Each panel K-stacks at K ∈ {100, 200, 400, 800, 1600, 3200, 6400}.
The entry-shuffle destroyer is overlaid as muted dashed curves so the
EXP-DSUBN-02 finding (K-shape is a marginal property, not an
ordering one) remains readable in this view.

Per-panel mean / min Pearson ρ across K-pairs reads the K-stability
of the refinement effect.

Aligned with experiments/VISUAL-REDUCTION-DISCIPLINE.md
§subtraction-rule (subtract the parent distribution; what survives
is the refinement effect) and §hierarchy (held-fixed-confounder
arithmetic-tomography level).
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

LABELS = ['C_Surv', 'C_Surv_prime_m', 'C_Surv_comp_m']


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

    return {
        'C_Surv':         [c for c in unique_in_appearance if c in S_set],
        'C_Surv_prime_m': [c for c in unique_in_appearance if c in S_prime_set],
        'C_Surv_comp_m':  [c for c in unique_in_appearance if c in S_comp_set],
    }


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


def F_N_on_grid(orbit, t_grid):
    sorted_v = np.sort(orbit)
    return np.searchsorted(sorted_v, t_grid, side='right') / len(sorted_v)


def shuffle_seq(seq, rng):
    indices = rng.permutation(len(seq))
    return [seq[i] for i in indices]


def pairwise_rho(arr):
    n = arr.shape[0]
    rhos = []
    for i in range(n):
        for j in range(i + 1, n):
            rhos.append(float(np.corrcoef(arr[i], arr[j])[0, 1]))
    return np.array(rhos)


# --- Sweep ---

F_raw = {lbl: np.zeros((len(K_VALUES), len(T_GRID))) for lbl in LABELS}
F_shuf = {lbl: np.zeros((len(K_VALUES), len(T_GRID))) for lbl in LABELS}

rng = np.random.default_rng(SEED)
t0 = time.time()
for ki, K in enumerate(K_VALUES):
    seqs = build_atom_sequences(K)
    for lbl in LABELS:
        F_raw[lbl][ki, :] = F_N_on_grid(make_orbit(seqs[lbl]), T_GRID)
        F_shuf[lbl][ki, :] = F_N_on_grid(
            make_orbit(shuffle_seq(seqs[lbl], rng)), T_GRID)
    print(f"K = {K} done (t = {time.time() - t0:.1f}s)")

dev_raw_prime  = F_raw['C_Surv_prime_m'] - F_raw['C_Surv']
dev_raw_comp   = F_raw['C_Surv_comp_m']  - F_raw['C_Surv']
dev_shuf_prime = F_shuf['C_Surv_prime_m'] - F_shuf['C_Surv']
dev_shuf_comp  = F_shuf['C_Surv_comp_m']  - F_shuf['C_Surv']

print()
print("Refinement-deviation pairwise Pearson ρ across K-pairs:")
for name, arr in [
    ('prime-m raw     ', dev_raw_prime),
    ('prime-m shuffled', dev_shuf_prime),
    ('comp-m  raw     ', dev_raw_comp),
    ('comp-m  shuffled', dev_shuf_comp),
]:
    rhos = pairwise_rho(arr)
    print(f"  {name}  mean = {rhos.mean():+.4f},  min = {rhos.min():+.4f}")

# Reference: parent and refinement residual K-stabilities (to read
# whether prime-m's K-stability is inherited from C_Surv vs added
# by the refinement).
print()
print("Parent-reference: K-stability of normalised residual "
      "(F_N − t) / D_N* per construction:")
ref_rhos = {}
for lbl in LABELS:
    res = F_raw[lbl] - T_GRID[None, :]
    peaks_per_K = np.abs(res).max(axis=1)
    norm_res = res / peaks_per_K[:, None]
    rhos = pairwise_rho(norm_res)
    ref_rhos[lbl] = rhos.mean()
    print(f"  {lbl:<18}  mean ρ = {rhos.mean():+.4f},  "
          f"min ρ = {rhos.min():+.4f}")

# --- Plot ---

cmap = LinearSegmentedColormap.from_list('Kgrad', [
    '#3da9c4', '#7dd3e0', '#f5e2a3', '#f9b27a', '#e8643a',
])

fig, axes = plt.subplots(2, 1, figsize=(13, 10),
                          sharex=True, sharey=True)
fig.patch.set_facecolor('#0a0a0a')

panels = [
    ('prime-m refinement:  F_N^{prime-m}(t) − F_N^{C_Surv}(t)',
     dev_raw_prime, dev_shuf_prime),
    ('comp-m refinement:   F_N^{comp-m}(t)  − F_N^{C_Surv}(t)',
     dev_raw_comp,  dev_shuf_comp),
]

for ax, (title, dev_r, dev_s) in zip(axes, panels):
    ax.set_facecolor('#0a0a0a')
    ax.axhline(0, color='#444', linewidth=0.6,
               linestyle='--', alpha=0.7)
    for ki, K in enumerate(K_VALUES):
        color = cmap(ki / (len(K_VALUES) - 1))
        ax.plot(T_GRID, dev_s[ki], color=color, linewidth=0.6,
                alpha=0.45, linestyle=(0, (3, 2)))
        ax.plot(T_GRID, dev_r[ki], color=color, linewidth=1.2,
                alpha=0.95)
    rho_r = pairwise_rho(dev_r)
    rho_s = pairwise_rho(dev_s)
    rho_color = '#a8e22d' if rho_r.mean() > 0.7 else (
        '#f9b27a' if rho_r.mean() > 0.4 else '#ff79c6')
    ax.set_title(title, color='white', fontsize=12, loc='left')
    ax.text(0.01, 0.95,
            f'raw       mean ρ = {rho_r.mean():+.2f}   '
            f'min ρ = {rho_r.min():+.2f}\n'
            f'shuffled  mean ρ = {rho_s.mean():+.2f}   '
            f'min ρ = {rho_s.min():+.2f}',
            color=rho_color, fontsize=10, family='monospace',
            transform=ax.transAxes, verticalalignment='top')
    ax.set_ylabel('F_N^{refinement} − F_N^{C_Surv}',
                  color='white', fontsize=11)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#333')
    ax.grid(alpha=0.1, color='#444')
    ax.set_xlim(0, 1)

axes[-1].set_xlabel('t  (orbit value in [0, 1])',
                     color='white', fontsize=11)

handles = [plt.Line2D([0], [0],
                       color=cmap(i / (len(K_VALUES) - 1)),
                       linewidth=2, label=f'K = {K}')
           for i, K in enumerate(K_VALUES)]
handles.append(plt.Line2D([0], [0], color='#888', linewidth=0.8,
                           linestyle=(0, (3, 2)), alpha=0.6,
                           label='entry-shuffled (destroyer)'))
fig.legend(handles=handles, loc='upper right',
           bbox_to_anchor=(0.995, 0.995),
           facecolor='#1a1a1a', edgecolor='#333',
           labelcolor='white', fontsize=8, ncol=1)

fig.suptitle(
    'Refinement-deviation K-shape — '
    'F_N^{refinement}(t) − F_N^{C_Surv}(t)\n'
    'solid: raw entry order;  dashed: entry-shuffled destroyer',
    color='white', fontsize=12, y=0.995)

# Footer with parent-reference ρ — makes the chart's payload
# (refinement deviation K-noise vs parent K-stability) readable
# without cross-reference.
fig.text(0.50, 0.012,
         f"Parent reference (residual (F_N − t)/D_N* across K, "
         f"from residual_kshape):  "
         f"C_Surv ρ = {ref_rhos['C_Surv']:+.2f}   "
         f"prime-m ρ = {ref_rhos['C_Surv_prime_m']:+.2f}   "
         f"comp-m ρ = {ref_rhos['C_Surv_comp_m']:+.2f}",
         color='#bbb', fontsize=9, family='monospace',
         horizontalalignment='center')

plt.tight_layout(rect=[0, 0.03, 0.96, 0.96])
plt.savefig('refinement_kshape.png', dpi=170,
            facecolor='#0a0a0a', bbox_inches='tight')
print()
print('-> refinement_kshape.png')
