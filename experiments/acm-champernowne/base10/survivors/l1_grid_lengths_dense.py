"""
Length surface — heavy-collision regime.

The W=10 grid at n_0 ∈ [10, 1000] shows survival rate ≈ 1 at most
cells: collisions are rare, so the survivor filter barely fires. The
Two Tongues panel ([2, 10], k=400) is in a different regime entirely
— W=9, n_0=2, survival rate 0.62 in the unique-set sense, 0.37 in
the multiset sense. That's where the optimizer is actually doing
work.

This sweep tests whether mean-digit-length neutrality holds where
the optimizer's selection is aggressive: n_0 ∈ [2, 50] step 1,
K ∈ [100, 2000] step 20, W = 9 (matches the Two Tongues window
width). The Two Tongues panel sits as one cell.

Caches l1_grid_lengths_dense.npz with the same fields as the W=10
sweep.
"""

import sys
sys.path.insert(0, '../../../../core')
sys.path.insert(0, '.')

import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

W = 9
N0_VALUES = np.arange(2, 51, 1)              # 49 values
K_VALUES = np.arange(100, 2001, 20)          # 96 values


def n_primes_vec(n, k):
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


def cell_stats(n0, k, w=W):
    n1 = n0 + w - 1
    parts = [n_primes_vec(n, k) for n in range(n0, n1 + 1)]
    m_arr = np.concatenate(parts)

    dlen_arr = np.floor(np.log10(m_arr)).astype(np.int64) + 1
    L_b_multi = int(dlen_arr.sum())

    unique_vals, counts = np.unique(m_arr, return_counts=True)
    n_unique = unique_vals.size
    dlen_unique = np.floor(np.log10(unique_vals)).astype(np.int64) + 1
    L_b_set = int(dlen_unique.sum())

    surv_mask = (counts == 1)
    n_surv = int(surv_mask.sum())
    L_s = int(dlen_unique[surv_mask].sum())

    return n_unique, n_surv, L_b_multi, L_b_set, L_s


print("Sanity at [2, 10], k=400 (n_0=2, W=9):")
nu, ns, lbm, lbs, ls = cell_stats(2, 400)
print(f"  n_unique={nu}  n_surv={ns}  L_b_multi={lbm}  "
      f"L_b_set={lbs}  L_surv={ls}")
print(f"  expected: 2171 / 1338 / 12874 / -- / 4894")
print()

print(f"Computing dense grid: {len(N0_VALUES)} n_0 x {len(K_VALUES)} K "
      f"= {len(N0_VALUES) * len(K_VALUES)} cells, W={W}...")

t0 = time.time()
N_U = np.zeros((len(N0_VALUES), len(K_VALUES)), dtype=np.int64)
N_S = np.zeros_like(N_U)
L_BM = np.zeros_like(N_U)
L_BS = np.zeros_like(N_U)
L_S = np.zeros_like(N_U)

for i, n0 in enumerate(N0_VALUES):
    for j, k in enumerate(K_VALUES):
        nu, ns, lbm, lbs, ls = cell_stats(int(n0), int(k))
        N_U[i, j] = nu
        N_S[i, j] = ns
        L_BM[i, j] = lbm
        L_BS[i, j] = lbs
        L_S[i, j] = ls
    if (i + 1) % 5 == 0 or i == 0:
        print(f"  rows done: {i + 1}/{len(N0_VALUES)} "
              f"(t={time.time() - t0:.1f}s)")

print(f"Total compute: {time.time() - t0:.1f}s")

np.savez('l1_grid_lengths_dense.npz',
         N_UNIQUE=N_U, N_SURV=N_S,
         L_B_MULTI=L_BM, L_B_SET=L_BS, L_SURV=L_S,
         N0_VALUES=N0_VALUES, K_VALUES=K_VALUES, W=W)
print("-> l1_grid_lengths_dense.npz")

n_multi = float(W) * K_VALUES[None, :]
mean_dlen_b_multi = L_BM / n_multi
mean_dlen_b_set = L_BS / N_U
mean_dlen_s = L_S / N_S

set_ratio = mean_dlen_s / mean_dlen_b_set
multi_ratio = mean_dlen_s / mean_dlen_b_multi

surv_share_unique = N_S / N_U
surv_share_multi = N_S / n_multi
length_share = L_S / L_BM

print()
print(f"survival rate (set)    range: "
      f"[{surv_share_unique.min():.4f}, {surv_share_unique.max():.4f}], "
      f"median {np.median(surv_share_unique):.4f}")
print(f"survival rate (multi)  range: "
      f"[{surv_share_multi.min():.4f}, {surv_share_multi.max():.4f}], "
      f"median {np.median(surv_share_multi):.4f}")
print(f"L_surv / L_b_multi     range: "
      f"[{length_share.min():.4f}, {length_share.max():.4f}], "
      f"median {np.median(length_share):.4f}")
print(f"mean-dlen ratio (set)  range: "
      f"[{set_ratio.min():.4f}, {set_ratio.max():.4f}], "
      f"median {np.median(set_ratio):.4f}")
print(f"mean-dlen ratio (multi)range: "
      f"[{multi_ratio.min():.4f}, {multi_ratio.max():.4f}], "
      f"median {np.median(multi_ratio):.4f}")

# Two Tongues panel cell (n_0=2, K=400) — find indices.
i_tt = int(np.where(N0_VALUES == 2)[0][0])
j_tt = int(np.argmin(np.abs(K_VALUES - 400)))
print()
print(f"Two Tongues cell (n_0={N0_VALUES[i_tt]}, K={K_VALUES[j_tt]}):")
print(f"  set ratio   = {set_ratio[i_tt, j_tt]:.4f}")
print(f"  multi ratio = {multi_ratio[i_tt, j_tt]:.4f}")
print(f"  surv share (set)   = {surv_share_unique[i_tt, j_tt]:.4f}")
print(f"  surv share (multi) = {surv_share_multi[i_tt, j_tt]:.4f}")

# --- Plot ---
fig, axes = plt.subplots(2, 2, figsize=(13, 11))
fig.patch.set_facecolor('#0a0a0a')

step_x = K_VALUES[1] - K_VALUES[0]
step_y = N0_VALUES[1] - N0_VALUES[0]
extent = (K_VALUES[0] - step_x / 2, K_VALUES[-1] + step_x / 2,
          N0_VALUES[0] - step_y / 2, N0_VALUES[-1] + step_y / 2)


def panel(ax, data, title, cmap='viridis', diverging_at=None,
          vmin=None, vmax=None):
    ax.set_facecolor('#0a0a0a')
    if diverging_at is not None:
        d = max(np.abs(np.nanmin(data) - diverging_at),
                np.abs(np.nanmax(data) - diverging_at))
        norm = TwoSlopeNorm(vmin=diverging_at - d, vcenter=diverging_at,
                            vmax=diverging_at + d)
        im = ax.imshow(data, aspect='auto', origin='lower',
                       cmap='RdBu_r', norm=norm,
                       interpolation='nearest', extent=extent)
    else:
        im = ax.imshow(data, aspect='auto', origin='lower', cmap=cmap,
                       interpolation='nearest', extent=extent,
                       vmin=vmin, vmax=vmax)
    ax.set_xlabel('K  (atoms per stream)', color='white', fontsize=10)
    ax.set_ylabel(f'n_0  (window = [n_0, n_0 + {W - 1}])',
                  color='white', fontsize=10)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#333')
    ax.set_title(title, color='white', fontsize=10)
    cbar = plt.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cbar.ax.tick_params(colors='white')
    cbar.outline.set_edgecolor('#333')
    # Mark the Two Tongues panel.
    ax.plot(400, 2, marker='*', markersize=14,
            markerfacecolor='#ffcc5c', markeredgecolor='black',
            markeredgewidth=0.8, linestyle='none')


panel(axes[0, 0], surv_share_unique,
      '|Surv| / |Unique|  (set survival rate)')
panel(axes[0, 1], length_share,
      'L_surv / L_b_multi  (length share of C_Bundle)')
panel(axes[1, 0], set_ratio,
      '(L_surv/|Surv|) / (L_b_set/|Unique|)\n'
      'survivor mean dlen / unique-bundle mean (1 = neutral)',
      diverging_at=1.0)
panel(axes[1, 1], multi_ratio,
      '(L_surv/|Surv|) / (L_b_multi/W·K)\n'
      'survivor mean dlen / multiset-bundle mean (1 = neutral)',
      diverging_at=1.0)

fig.suptitle(
    f'Length surface — heavy-collision regime  '
    f'(W = {W}, n_0 ∈ [{N0_VALUES[0]}, {N0_VALUES[-1]}], '
    f'K ∈ [{K_VALUES[0]}, {K_VALUES[-1]}])  '
    f'★ = Two Tongues panel',
    color='white', fontsize=12)

plt.tight_layout()
plt.savefig('l1_grid_lengths_dense.png', dpi=180,
            facecolor='#0a0a0a', bbox_inches='tight')
print("-> l1_grid_lengths_dense.png")
