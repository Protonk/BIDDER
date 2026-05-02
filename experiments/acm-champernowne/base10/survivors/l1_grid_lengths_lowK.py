"""
Length surface — small-K extension.

The large-K decay plot showed n_0 ∈ [2, 3] hit their grid-edge max at
K=2000, suggesting the true peak sits below that. Other n_0 had clean
rise-peak-fall shapes inside the grid. This sweep extends downward
to K = 10 in fine steps to find the peak for small n_0 and verify
the rise-peak-fall shape is universal.

Combines with the existing large-K grid for a full-range view at
K ∈ [10, 50000] on a log x-axis.
"""

import sys
sys.path.insert(0, '../../../../core')
sys.path.insert(0, '.')

import time
import numpy as np
import matplotlib.pyplot as plt

W = 9
N0_VALUES = np.arange(2, 13, 1)              # [2..12]
K_VALUES = np.arange(10, 2001, 10)           # 200 values, step 10


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


print(f"Computing low-K grid: {len(N0_VALUES)} n_0 x "
      f"{len(K_VALUES)} K = {len(N0_VALUES) * len(K_VALUES)} cells, "
      f"W={W}...")

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
print(f"Total compute: {time.time() - t0:.1f}s")

np.savez('l1_grid_lengths_lowK.npz',
         N_UNIQUE=N_U, N_SURV=N_S,
         L_B_MULTI=L_BM, L_B_SET=L_BS, L_SURV=L_S,
         N0_VALUES=N0_VALUES, K_VALUES=K_VALUES, W=W)
print("-> l1_grid_lengths_lowK.npz")

mean_b_set = L_BS / N_U
mean_s = L_S / N_S
set_ratio = mean_s / mean_b_set
bias_pct = (set_ratio - 1) * 100

print()
print("True peak (small-K range):")
print(f"{'n_0':>4} {'peak K':>8} {'peak %':>8}")
for n0 in N0_VALUES:
    i = int(np.where(N0_VALUES == n0)[0][0])
    j_peak = int(np.argmax(bias_pct[i, :]))
    print(f"{n0:>4d} {int(K_VALUES[j_peak]):>8d} "
          f"{float(bias_pct[i, j_peak]):>+8.3f}")

# Load large-K cache for full-range plot.
zL = np.load('l1_grid_lengths_largeK.npz')
N0_L = zL['N0_VALUES']
K_L = zL['K_VALUES']
mean_b_L = zL['L_B_SET'] / zL['N_UNIQUE']
mean_s_L = zL['L_SURV'] / zL['N_SURV']
bias_L_pct = (mean_s_L / mean_b_L - 1) * 100

# --- Plot: full-range decay on log-x ---
fig, axes = plt.subplots(2, 1, figsize=(13, 10))
fig.patch.set_facecolor('#0a0a0a')

curves = [(2, '#ff4444'), (3, '#ff8c42'), (4, '#ffcc33'),
          (5, '#a8e22d'), (6, '#33d6a8'), (7, '#33b5e5'),
          (8, '#7e6bff'), (10, '#cc66ff'), (12, '#ff66cc')]

ax = axes[0]
ax.set_facecolor('#0a0a0a')
for n0, color in curves:
    if n0 in N0_VALUES:
        i = int(np.where(N0_VALUES == n0)[0][0])
        ax.plot(K_VALUES, bias_pct[i, :], color=color,
                linewidth=1.5, label=f'n_0 = {n0}')
        j_peak = int(np.argmax(bias_pct[i, :]))
        ax.plot(K_VALUES[j_peak], bias_pct[i, j_peak],
                marker='o', color=color, markersize=8,
                markeredgecolor='white', markeredgewidth=0.7,
                linestyle='none')
ax.axhline(0, color='#444', linewidth=0.8, linestyle='--')
ax.set_xlabel('K  (atoms per stream)', color='white', fontsize=11)
ax.set_ylabel('mean-dlen ratio − 1  (%, set basis)',
              color='white', fontsize=11)
ax.set_title(
    'Low-K extension  (W=9, K ∈ [10, 2000], step 10)  '
    '● marks peak K',
    color='white', fontsize=12)
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('#333')
ax.legend(loc='upper right', facecolor='#1a1a1a',
          edgecolor='#333', labelcolor='white',
          fontsize=9, ncol=2)
ax.grid(alpha=0.15, color='#444')

# --- Bottom panel: full K range, log-x, combining low-K + large-K ---
ax = axes[1]
ax.set_facecolor('#0a0a0a')
for n0, color in curves:
    K_combined = []
    bias_combined = []
    if n0 in N0_VALUES:
        i = int(np.where(N0_VALUES == n0)[0][0])
        K_combined.append(K_VALUES)
        bias_combined.append(bias_pct[i, :])
    if n0 in N0_L:
        i = int(np.where(N0_L == n0)[0][0])
        K_combined.append(K_L)
        bias_combined.append(bias_L_pct[i, :])
    if K_combined:
        Kc = np.concatenate(K_combined)
        bc = np.concatenate(bias_combined)
        idx = np.argsort(Kc)
        ax.plot(Kc[idx], bc[idx], color=color, linewidth=1.5,
                label=f'n_0 = {n0}')

ax.axhline(0, color='#444', linewidth=0.8, linestyle='--')
ax.set_xscale('log')
ax.set_xlabel('K  (log scale)', color='white', fontsize=11)
ax.set_ylabel('mean-dlen ratio − 1  (%, set basis)',
              color='white', fontsize=11)
ax.set_title(
    'Full K range  (K ∈ [10, 50000], log x)  '
    '— combines low-K + large-K caches',
    color='white', fontsize=12)
ax.tick_params(colors='white', which='both')
for spine in ax.spines.values():
    spine.set_color('#333')
ax.legend(loc='upper right', facecolor='#1a1a1a',
          edgecolor='#333', labelcolor='white',
          fontsize=9, ncol=2)
ax.grid(alpha=0.15, color='#444', which='both')

plt.tight_layout()
plt.savefig('l1_grid_lengths_lowK.png', dpi=170,
            facecolor='#0a0a0a', bbox_inches='tight')
print()
print("-> l1_grid_lengths_lowK.png")
