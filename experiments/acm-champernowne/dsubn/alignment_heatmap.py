"""
EXP-DSUBN-04: (t, K) alignment heatmap.

Localizes the interaction between the parent C_Surv residual and the
refinement deviation across (t, K):

  align(t, K) = (F_N^{surv}(t, K) − t) × (F_N^{ref}(t, K) − F_N^{surv}(t, K))
                ────────────────────────   ────────────────────────────────
                parent residual at (t, K)  refinement deviation at (t, K)

Per-(t, K) sign:
  +  parent and refinement push in the same t-direction (constructive)
  −  parent and refinement push in opposite t-directions (destructive)

The integral ∫align(t, K) dt at fixed K is proportional to the
covariance contributing to the cross-K Pearson ρ that EXP-DSUBN-01
measured. So this chart is the spatial decomposition of the effect
EXP-DSUBN-03 measured globally (small K-noisy refinement, parent
ρ = 0.73, prime-m ρ = 0.91, comp-m ρ = 0.24).

Layout: 2×2. Cols: prime-m, comp-m. Rows: raw, entry-shuffled
(the EXP-DSUBN-02 destroyer). Each cell has a thin per-K integrated
∫align dt strip above the main heatmap.

Aligned with VISUAL-REDUCTION-DISCIPLINE.md §hierarchy (arithmetic
tomography: parent held fixed; refinement contribution decomposed
by (t, K) coordinates).
"""

import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.gridspec import GridSpec
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

# --- Alignment matrices ---

parent_raw  = F_raw['C_Surv']  - T_GRID[None, :]
parent_shuf = F_shuf['C_Surv'] - T_GRID[None, :]

dev_raw_prime  = F_raw['C_Surv_prime_m']  - F_raw['C_Surv']
dev_raw_comp   = F_raw['C_Surv_comp_m']   - F_raw['C_Surv']
dev_shuf_prime = F_shuf['C_Surv_prime_m'] - F_shuf['C_Surv']
dev_shuf_comp  = F_shuf['C_Surv_comp_m']  - F_shuf['C_Surv']

align_raw_prime  = parent_raw  * dev_raw_prime
align_raw_comp   = parent_raw  * dev_raw_comp
align_shuf_prime = parent_shuf * dev_shuf_prime
align_shuf_comp  = parent_shuf * dev_shuf_comp


def per_K_integrated(align):
    dt = T_GRID[1] - T_GRID[0]
    return align.sum(axis=1) * dt


ints_raw_prime  = per_K_integrated(align_raw_prime)
ints_raw_comp   = per_K_integrated(align_raw_comp)
ints_shuf_prime = per_K_integrated(align_shuf_prime)
ints_shuf_comp  = per_K_integrated(align_shuf_comp)

print()
print("Per-K integrated ∫align dt (drives ρ-shift sign):")
print(f"{'K':>6}  {'prime raw':>12}  {'prime shuf':>12}  "
      f"{'comp raw':>12}  {'comp shuf':>12}")
for ki, K in enumerate(K_VALUES):
    print(f"{K:>6}  "
          f"{ints_raw_prime[ki]:>+12.6f}  {ints_shuf_prime[ki]:>+12.6f}  "
          f"{ints_raw_comp[ki]:>+12.6f}  {ints_shuf_comp[ki]:>+12.6f}")

print()
print("Mean over K (sign predicts ρ-shift direction at residual_kshape):")
print(f"  prime raw       {ints_raw_prime.mean():+.6f}   "
      f"(prime-m ρ = 0.91 vs parent 0.73 → constructive expected)")
print(f"  prime shuffled  {ints_shuf_prime.mean():+.6f}")
print(f"  comp  raw       {ints_raw_comp.mean():+.6f}   "
      f"(comp-m ρ = 0.24 vs parent 0.73 → destructive expected)")
print(f"  comp  shuffled  {ints_shuf_comp.mean():+.6f}")

# --- Plot ---

divcmap = LinearSegmentedColormap.from_list('align', [
    '#ff4477',  # vivid red (negative)
    '#992233',  # dark red
    '#0a0a0a',  # black (zero)
    '#226633',  # dark green
    '#55ff77',  # vivid green (positive)
])

vmax = max(np.abs(align_raw_prime).max(), np.abs(align_raw_comp).max(),
           np.abs(align_shuf_prime).max(), np.abs(align_shuf_comp).max())
bar_vmax = max(np.abs(ints_raw_prime).max(), np.abs(ints_raw_comp).max(),
               np.abs(ints_shuf_prime).max(), np.abs(ints_shuf_comp).max())

fig = plt.figure(figsize=(14, 11))
fig.patch.set_facecolor('#0a0a0a')

gs = GridSpec(4, 2, figure=fig,
              height_ratios=[0.18, 1.0, 0.18, 1.0],
              hspace=0.10, wspace=0.10,
              left=0.07, right=0.92, top=0.93, bottom=0.06)

panels = [
    (0, 1, 0, 'prime-m  (raw)',                  align_raw_prime,  ints_raw_prime),
    (0, 1, 1, 'comp-m  (raw)',                   align_raw_comp,   ints_raw_comp),
    (2, 3, 0, 'prime-m  (entry-shuffled)',       align_shuf_prime, ints_shuf_prime),
    (2, 3, 1, 'comp-m  (entry-shuffled)',        align_shuf_comp,  ints_shuf_comp),
]

last_im = None
for row_s, row_m, col, title, align, ints in panels:
    ax_bar = fig.add_subplot(gs[row_s, col])
    ax_bar.set_facecolor('#0a0a0a')
    bar_data = ints.reshape(1, -1)
    ax_bar.imshow(bar_data, aspect='auto', cmap=divcmap,
                  vmin=-bar_vmax, vmax=bar_vmax,
                  extent=(-0.5, len(K_VALUES) - 0.5, 0, 1))
    for i, v in enumerate(ints):
        ax_bar.text(i, 0.5, f'{v:+.3f}',
                    color='white', fontsize=7,
                    ha='center', va='center', family='monospace')
    ax_bar.set_xticks([])
    ax_bar.set_yticks([])
    ax_bar.set_title(f"{title}    "
                     f"mean ∫align dt = {ints.mean():+.4f}",
                     color='white', fontsize=11, loc='left')
    for sp in ax_bar.spines.values():
        sp.set_color('#333')

    ax = fig.add_subplot(gs[row_m, col])
    ax.set_facecolor('#0a0a0a')
    last_im = ax.imshow(align.T, aspect='auto', cmap=divcmap,
                        vmin=-vmax, vmax=vmax,
                        extent=(-0.5, len(K_VALUES) - 0.5, 0, 1),
                        origin='lower', interpolation='nearest')
    ax.set_xticks(range(len(K_VALUES)))
    ax.set_xticklabels([str(K) for K in K_VALUES],
                       color='white', fontsize=9)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.tick_params(colors='white')
    if row_m == 3:
        ax.set_xlabel('K', color='white', fontsize=11)
    if col == 0:
        ax.set_ylabel('t  (orbit value)', color='white', fontsize=11)
    for sp in ax.spines.values():
        sp.set_color('#333')

cbar_ax = fig.add_axes([0.935, 0.06, 0.012, 0.87])
cbar = plt.colorbar(last_im, cax=cbar_ax)
cbar.set_label('align(t, K) = parent_residual · refinement_deviation',
               color='white', fontsize=9)
cbar.ax.tick_params(colors='white', labelsize=8)
cbar.outline.set_edgecolor('#333')

fig.suptitle(
    '(t, K) alignment heatmap — '
    'parent_residual(t, K) × refinement_deviation(t, K)\n'
    'green = constructive (same direction)  ·  '
    'red = destructive (opposite direction)  ·  '
    'top strip: per-K integrated ∫align dt',
    color='white', fontsize=11.5, y=0.985)

plt.savefig('alignment_heatmap.png', dpi=170,
            facecolor='#0a0a0a', bbox_inches='tight')
print()
print('-> alignment_heatmap.png')
