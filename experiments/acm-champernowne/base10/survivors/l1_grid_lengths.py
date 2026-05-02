"""
Length surface — does the survivor filter preserve mean digit-length?

Re-runs the l1_grid sweep but records survivor count, unique bundle
count, total survivor digit-length, total bundle digit-length per
cell. Tests whether the magnitude-level "tracking" claim about
C_Surv-as-optimizer extends one rung past L1 deviation: are survivor
integers, on average, the same digit-length as the bundle's?

Two views:

  multiset basis  — bundle is the W*K multiset of stream atoms (with
                    duplicates from cross-stream collisions). This is
                    the C_Bundle real number's actual atom sequence.
                    Mean digit length = L_b_multi / (W*K).

  set basis       — bundle is the deduplicated set of unique integers
                    appearing in the streams. Survivors live inside
                    this set. Mean digit length = L_b_set / n_unique.

Caches l1_grid_lengths.npz with arrays:
  N_UNIQUE   - unique bundle integer count
  N_SURV     - survivor count
  L_B_MULTI  - total digit length of bundle (multiset, length of C_Bundle)
  L_B_SET    - total digit length of bundle (set of unique integers)
  L_SURV     - total digit length of survivors (= length of C_Surv)
"""

import sys
sys.path.insert(0, '../../../../core')
sys.path.insert(0, '.')

import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

W = 10
N0_VALUES = np.arange(10, 1001, 10)
K_VALUES = np.arange(10, 1001, 10)


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


# Sanity check at the Two Tongues panel before sweeping the grid.
print("Sanity check at [2, 10], k=400 (W=9):")
nu, ns, lbm, lbs, ls = cell_stats(2, 400, w=9)
print(f"  n_unique={nu}  n_surv={ns}  L_b_multi={lbm}  "
      f"L_b_set={lbs}  L_surv={ls}")
print(f"  expected: n_surv=1338, L_b_multi=12874, L_surv=4894")
print()

print(f"Computing length grid: {len(N0_VALUES)} x {len(K_VALUES)} "
      f"cells, W={W}...")

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
    if (i + 1) % 10 == 0 or i == 0:
        print(f"  rows done: {i + 1}/{len(N0_VALUES)} "
              f"(t={time.time() - t0:.1f}s)")

print(f"Total compute: {time.time() - t0:.1f}s")

np.savez('l1_grid_lengths.npz',
         N_UNIQUE=N_U, N_SURV=N_S,
         L_B_MULTI=L_BM, L_B_SET=L_BS, L_SURV=L_S,
         N0_VALUES=N0_VALUES, K_VALUES=K_VALUES, W=W)
print("-> l1_grid_lengths.npz")

# Derived ratios.
n_multi = float(W) * K_VALUES[None, :]  # W*K, broadcast over n_0 axis
mean_dlen_b_multi = L_BM / n_multi              # digit length per atom slot
mean_dlen_b_set = L_BS / N_U                    # per unique bundle integer
mean_dlen_s = L_S / N_S                         # per survivor

set_ratio = mean_dlen_s / mean_dlen_b_set       # 1 ⇒ filter neutral on dlen
multi_ratio = mean_dlen_s / mean_dlen_b_multi   # 1 ⇒ C_Surv ~ C_Bundle dlen

surv_share_unique = N_S / N_U                   # of unique integers
length_share = L_S / L_BM                       # of C_Bundle digit positions

print()
print(f"survivor-share-of-unique   range: "
      f"[{surv_share_unique.min():.4f}, {surv_share_unique.max():.4f}], "
      f"median {np.median(surv_share_unique):.4f}")
print(f"L_surv / L_b_multi         range: "
      f"[{length_share.min():.4f}, {length_share.max():.4f}], "
      f"median {np.median(length_share):.4f}")
print(f"mean-dlen ratio (set)      range: "
      f"[{set_ratio.min():.4f}, {set_ratio.max():.4f}], "
      f"median {np.median(set_ratio):.4f}")
print(f"mean-dlen ratio (multiset) range: "
      f"[{multi_ratio.min():.4f}, {multi_ratio.max():.4f}], "
      f"median {np.median(multi_ratio):.4f}")

# --- Plot: 2x2 grid ---
fig, axes = plt.subplots(2, 2, figsize=(13, 13))
fig.patch.set_facecolor('#0a0a0a')

step_x = K_VALUES[1] - K_VALUES[0]
step_y = N0_VALUES[1] - N0_VALUES[0]
extent = (K_VALUES[0] - step_x / 2, K_VALUES[-1] + step_x / 2,
          N0_VALUES[0] - step_y / 2, N0_VALUES[-1] + step_y / 2)


def panel(ax, data, title, cmap='viridis', diverging_at=None):
    ax.set_facecolor('#0a0a0a')
    if diverging_at is not None:
        d = np.abs(data - diverging_at).max()
        norm = TwoSlopeNorm(vmin=diverging_at - d, vcenter=diverging_at,
                            vmax=diverging_at + d)
        im = ax.imshow(data, aspect='equal', origin='lower',
                       cmap='RdBu_r', norm=norm,
                       interpolation='nearest', extent=extent)
    else:
        im = ax.imshow(data, aspect='equal', origin='lower', cmap=cmap,
                       interpolation='nearest', extent=extent)
    ax.set_xlabel('K  (atoms per stream)', color='white', fontsize=10)
    ax.set_ylabel(f'n_0  (window = [n_0, n_0 + {W - 1}])',
                  color='white', fontsize=10)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#333')
    ax.set_title(title, color='white', fontsize=11)
    cbar = plt.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cbar.ax.tick_params(colors='white')
    cbar.outline.set_edgecolor('#333')


panel(axes[0, 0], surv_share_unique,
      '|Surv| / |Unique bundle integers|  (survival rate, set)')
panel(axes[0, 1], length_share,
      'L_surv / L_b_multi  (length ratio, C_Surv vs. C_Bundle)')
panel(axes[1, 0], set_ratio,
      '(L_surv / |Surv|) / (L_b_set / |Unique|)\n'
      '— survivor mean digit-length / unique-bundle mean (1 = neutral)',
      diverging_at=1.0)
panel(axes[1, 1], multi_ratio,
      '(L_surv / |Surv|) / (L_b_multi / W·K)\n'
      '— survivor mean digit-length / multiset-bundle mean (1 = neutral)',
      diverging_at=1.0)

fig.suptitle(
    f'Length surface — C_Surv vs. C_Bundle  '
    f'(W = {W}, n_0 ∈ [{N0_VALUES[0]}, {N0_VALUES[-1]}], '
    f'K ∈ [{K_VALUES[0]}, {K_VALUES[-1]}], step = {step_x})',
    color='white', fontsize=12)

plt.tight_layout()
plt.savefig('l1_grid_lengths.png', dpi=180, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> l1_grid_lengths.png")
