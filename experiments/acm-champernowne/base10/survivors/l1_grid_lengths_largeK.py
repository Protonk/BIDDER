"""
Length surface — large-K regime.

The W=10 grid at moderate (K, n_0) showed perfect neutrality. The
W=9 dense grid at small n_0 showed a structured +1-3% bias
(survivors run slightly longer than bundle). EXP07 predicted high-d
apparent-survivors with shifted cofactor bands at finite k — the
limit-survivor reading predicts the bias should *damp* as k grows
because apparent survivors disappear in the k → ∞ limit.

This sweep pushes K far past where we've looked: K ∈ [2000, 50000]
step 500 (97 values) at n_0 ∈ [2, 50] step 1 (49 values), W = 9.
Tests whether the EXP07 imprint persists at K >> 1000 or damps.

Caches l1_grid_lengths_largeK.npz with the same fields.
"""

import sys
sys.path.insert(0, '../../../../core')
sys.path.insert(0, '.')

import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

W = 9
N0_VALUES = np.arange(2, 51, 1)
K_VALUES = np.arange(2000, 50001, 500)


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


print(f"Computing large-K grid: {len(N0_VALUES)} n_0 x "
      f"{len(K_VALUES)} K = {len(N0_VALUES) * len(K_VALUES)} cells, "
      f"W={W}...")
print(f"  n_0 ∈ [{N0_VALUES[0]}, {N0_VALUES[-1]}], "
      f"K ∈ [{K_VALUES[0]}, {K_VALUES[-1]}]")

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

np.savez('l1_grid_lengths_largeK.npz',
         N_UNIQUE=N_U, N_SURV=N_S,
         L_B_MULTI=L_BM, L_B_SET=L_BS, L_SURV=L_S,
         N0_VALUES=N0_VALUES, K_VALUES=K_VALUES, W=W)
print("-> l1_grid_lengths_largeK.npz")

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
print(f"mean-dlen ratio (set)  range: "
      f"[{set_ratio.min():.4f}, {set_ratio.max():.4f}], "
      f"median {np.median(set_ratio):.4f}")
print(f"mean-dlen ratio (multi)range: "
      f"[{multi_ratio.min():.4f}, {multi_ratio.max():.4f}], "
      f"median {np.median(multi_ratio):.4f}")

# K-decay test: at fixed n_0, does set_ratio − 1 trend toward zero?
print()
print("K-trend at selected n_0 (set ratio − 1, in %):")
for n0_check in [2, 3, 5, 10, 20, 30, 50]:
    if n0_check in N0_VALUES:
        i_n = int(np.where(N0_VALUES == n0_check)[0][0])
        kfirst = K_VALUES[0]
        klast = K_VALUES[-1]
        kmid = K_VALUES[len(K_VALUES) // 2]
        rfirst = (set_ratio[i_n, 0] - 1) * 100
        rmid = (set_ratio[i_n, len(K_VALUES) // 2] - 1) * 100
        rlast = (set_ratio[i_n, -1] - 1) * 100
        print(f"  n_0={n0_check:3d}: K={kfirst:6d} → {rfirst:+.3f}%  "
              f"K={kmid:6d} → {rmid:+.3f}%  "
              f"K={klast:6d} → {rlast:+.3f}%")

# --- Plot ---
fig, axes = plt.subplots(2, 2, figsize=(14, 11))
fig.patch.set_facecolor('#0a0a0a')

step_x = K_VALUES[1] - K_VALUES[0]
step_y = N0_VALUES[1] - N0_VALUES[0]
extent = (K_VALUES[0] - step_x / 2, K_VALUES[-1] + step_x / 2,
          N0_VALUES[0] - step_y / 2, N0_VALUES[-1] + step_y / 2)


def panel(ax, data, title, cmap='viridis', diverging_at=None):
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
                       interpolation='nearest', extent=extent)
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
    f'Length surface — large-K regime  '
    f'(W = {W}, n_0 ∈ [{N0_VALUES[0]}, {N0_VALUES[-1]}], '
    f'K ∈ [{K_VALUES[0]}, {K_VALUES[-1]}])',
    color='white', fontsize=12)

plt.tight_layout()
plt.savefig('l1_grid_lengths_largeK.png', dpi=160,
            facecolor='#0a0a0a', bbox_inches='tight')
print("-> l1_grid_lengths_largeK.png")

# K-decay line plot at small n_0.
fig2, ax2 = plt.subplots(figsize=(10, 6))
fig2.patch.set_facecolor('#0a0a0a')
ax2.set_facecolor('#0a0a0a')
for n0_pick, color in [(2, '#ff6b6b'), (3, '#ffa07a'),
                        (5, '#ffd93d'), (10, '#6dde77'),
                        (20, '#4ecdc4'), (50, '#a78bfa')]:
    if n0_pick in N0_VALUES:
        i_n = int(np.where(N0_VALUES == n0_pick)[0][0])
        ax2.plot(K_VALUES, (set_ratio[i_n, :] - 1) * 100,
                 color=color, linewidth=1.4, label=f'n_0 = {n0_pick}')
ax2.axhline(0, color='#555', linewidth=0.8, linestyle='--')
ax2.set_xlabel('K  (atoms per stream)', color='white', fontsize=11)
ax2.set_ylabel('mean-dlen ratio − 1  (%, set basis)',
               color='white', fontsize=11)
ax2.set_title(
    'K-trend of the survivor-mean-dlen bias  (W=9, set basis)',
    color='white', fontsize=12)
ax2.tick_params(colors='white')
for spine in ax2.spines.values():
    spine.set_color('#333')
ax2.legend(loc='upper right', facecolor='#1a1a1a',
           edgecolor='#333', labelcolor='white', fontsize=10)
ax2.grid(alpha=0.15, color='#444')
plt.tight_layout()
plt.savefig('l1_grid_lengths_largeK_decay.png', dpi=160,
            facecolor='#0a0a0a', bbox_inches='tight')
print("-> l1_grid_lengths_largeK_decay.png")
