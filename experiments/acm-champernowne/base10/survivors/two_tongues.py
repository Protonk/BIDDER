"""
Two Tongues — running L1-deviation of the bundle vs. C_Surv digit streams.

For a window [n_0, n_1] truncated at k, walk the bundle atom by atom in
read order. After processing the first N atoms, compute the L1 distance
of the running leading-digit-frequency vector from uniform (1/9 over
digits 1-9) — once for the bundle (every atom counted), once for C_Surv
(only surviving atoms counted). Vertical guides mark stream boundaries.
"""

import sys
sys.path.insert(0, '../../../../core')
sys.path.insert(0, '.')

import numpy as np
import matplotlib.pyplot as plt
from survivors_core import bundle_atoms, survival_mask

N0, N1, K = 2, 10, 400

print(f"Building bundle for [{N0},{N1}], k={K}...")
atoms = bundle_atoms(N0, N1, K)
mask = np.array(survival_mask(atoms), dtype=np.int64)
n_atoms = len(atoms)
n_surv = int(mask.sum())
print(f"  {n_atoms} atoms, {n_surv} survivors "
      f"({100.0 * n_surv / n_atoms:.1f}%)")

# Per-atom one-hot tables.
str_atoms = [str(m) for _, m in atoms]
leading_digits = np.array([int(s[0]) for s in str_atoms])

ld_per_atom = np.zeros((n_atoms, 9), dtype=np.int64)
ld_per_atom[np.arange(n_atoms), leading_digits - 1] = 1

# Cumulative counts — bundle and survivor-masked.
m_col = mask[:, None]
ld_bundle_cum = np.cumsum(ld_per_atom, axis=0)
ld_surv_cum   = np.cumsum(ld_per_atom * m_col, axis=0)

bundle_ld_total = ld_bundle_cum.sum(axis=1)
surv_ld_total   = ld_surv_cum.sum(axis=1)


def l1_dev(cum, total, uniform):
    out = np.full(len(total), np.nan)
    valid = total > 0
    p = cum[valid] / total[valid, None]
    out[valid] = np.abs(p - uniform).sum(axis=1)
    return out


u9 = np.full(9, 1.0 / 9)
bundle_ld_l1 = l1_dev(ld_bundle_cum, bundle_ld_total, u9)
surv_ld_l1   = l1_dev(ld_surv_cum,   surv_ld_total,   u9)

# --- Plot ---
fig, ax = plt.subplots(figsize=(14, 5.5))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

x = np.arange(1, n_atoms + 1)

ax.semilogy(x, bundle_ld_l1, linewidth=1.3, color='#ffcc5c', alpha=0.9,
            label='bundle')
ax.semilogy(x, surv_ld_l1, linewidth=1.3, color='#6ec6ff', alpha=0.9,
            label='C_Surv')

# Stream boundaries.
for j, n in enumerate(range(N0, N1 + 1)):
    boundary = (j + 1) * K
    ax.axvline(x=boundary, color='white', linewidth=0.4, alpha=0.18)
    ax.text(boundary - K / 2, 0.97, f'n={n}',
            color='#888', fontsize=8,
            ha='center', va='top',
            transform=ax.get_xaxis_transform())

ax.set_ylabel('L1 deviation (leading digit, 1-9)',
              color='white', fontsize=12)
ax.set_xlabel('atoms processed (read order)', color='white', fontsize=12)
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('#333')
ax.legend(loc='upper right', fontsize=11, framealpha=0.3,
          labelcolor='white', facecolor='#1a1a1a')
ax.grid(True, which='both', color='#222', linewidth=0.4)

ax.set_title(
    f'Two Tongues — bundle vs. C_Surv on [{N0},{N1}], k={K}    '
    f'({n_atoms} atoms, {n_surv} survivors, '
    f'{100.0 * n_surv / n_atoms:.1f}%)',
    color='white', fontsize=13)

plt.tight_layout()
plt.savefig('two_tongues.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> two_tongues.png")
