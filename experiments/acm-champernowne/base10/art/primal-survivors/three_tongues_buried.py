"""
THREE TONGUES, BURIED — Rothko-style rendering of the L1 bracketing.

Three colored bands stacked vertically: composite-m above, bundle
middle, prime-m below. Each band's vertical position traces its
L1 trajectory across the bundle's atom horizon. At atom ≈ 250 the
n=2 dip plunges all three bands toward zero, with bundle diving
*through* prime-m's stripe — the wound.

Stream transitions appear as faint vertical seams.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from sympy import isprime

W = 9
n_0 = 2
n_1 = n_0 + W - 1
k = 400


def n_primes_vec(n, k):
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


u9 = np.full(9, 1.0 / 9)

parts_per_stream = [(n, n_primes_vec(n, k))
                    for n in range(n_0, n_1 + 1)]
all_atoms = np.concatenate([arr for _, arr in parts_per_stream])
n_atoms = all_atoms.size
stream_tag = np.concatenate([np.full_like(arr, n)
                             for n, arr in parts_per_stream])

unique_vals, first_idx, counts = np.unique(
    all_atoms, return_index=True, return_counts=True)
surv_mask = counts == 1
S = unique_vals[surv_mask]
sources_S = stream_tag[first_idx[surv_mask]]
m_S = S // sources_S
prime_m_arr = np.array([isprime(int(m)) for m in m_S])

bundle_set = set(int(c) for c in unique_vals)
pm_set = set(int(c) for c, pm in zip(S, prime_m_arr) if pm)
cm_set = set(int(c) for c, pm in zip(S, prime_m_arr) if not pm)


def running_l1(in_set):
    seen = set()
    counts_arr = np.zeros(9, dtype=np.int64)
    out_l1, out_idx = [], []
    for i in range(n_atoms):
        c = int(all_atoms[i])
        if c in seen:
            continue
        seen.add(c)
        if c not in in_set:
            continue
        log_floor = int(np.floor(np.log10(c)))
        leading = c // 10**log_floor
        counts_arr[leading - 1] += 1
        tot = counts_arr.sum()
        p = counts_arr / tot
        out_l1.append(np.abs(p - u9).sum())
        out_idx.append(i)
    return np.array(out_idx), np.array(out_l1)


idx_b, l1_b = running_l1(bundle_set)
idx_pm, l1_pm = running_l1(pm_set)
idx_cm, l1_cm = running_l1(cm_set)


def step_interp(idx, vals, x):
    positions = np.searchsorted(idx, x, side='right') - 1
    out = np.full(len(x), np.nan)
    valid = positions >= 0
    out[valid] = vals[positions[valid]]
    return out


grid = np.arange(n_atoms)
L1_b = step_interp(idx_b, l1_b, grid)
L1_pm = step_interp(idx_pm, l1_pm, grid)
L1_cm = step_interp(idx_cm, l1_cm, grid)


def fill_leading_nan(arr):
    idx_first = int(np.argmin(np.isnan(arr)))
    arr = arr.copy()
    arr[:idx_first] = arr[idx_first]
    return arr


L1_b = fill_leading_nan(L1_b)
L1_pm = fill_leading_nan(L1_pm)
L1_cm = fill_leading_nan(L1_cm)

# Mild smoothing — keeps the dip dramatic, softens the noise.
sigma = 6
L1_b_s = gaussian_filter1d(L1_b, sigma=sigma)
L1_pm_s = gaussian_filter1d(L1_pm, sigma=sigma)
L1_cm_s = gaussian_filter1d(L1_cm, sigma=sigma)

# Find the wound location (bundle's deepest minimum).
wound_idx = int(np.argmin(L1_b))
print(f"Wound at atom {wound_idx}, L1_b = {L1_b[wound_idx]:.4f}")

# --- Render ---
fig, ax = plt.subplots(figsize=(22, 11))
BG = '#0e0807'  # warm near-black
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

Y_TOP = 1.35
Y_BOTTOM = -0.06

# Rothko-leaning palette: deep crimson, burning scarlet, midnight ink.
COMP_COLOR = '#6e1818'   # composite-m, top — deep crimson
BUND_COLOR = '#d4602f'   # bundle, middle — burning scarlet
PRIM_COLOR = '#16203a'   # prime-m, bottom — midnight

# Each band has thickness — thicker than a line, less than a region.
# Multiple fills with decreasing alpha give soft Rothko edges.
def soft_band(ax, x, center, color, base_t=0.030, layers=10,
              edge_alpha=0.0, core_alpha=1.0, zorder=3):
    """Layered fills: opaque core fading out at the edges."""
    for i in range(layers):
        frac = (i + 1) / layers   # 1/L .. 1
        # Outer layers: thicker, lower alpha. Inner: thinner, higher alpha.
        t = base_t * (2.2 - 1.2 * frac)
        alpha = edge_alpha + (core_alpha - edge_alpha) * (frac ** 1.5)
        ax.fill_between(x, center - t, center + t,
                         color=color, alpha=alpha,
                         zorder=zorder + 0.001 * i,
                         linewidth=0)


# Stream transitions first (back layer).
for slot in range(400, n_atoms, 400):
    ax.axvline(slot, color='#ffffff', linewidth=0.4, alpha=0.04,
               zorder=1)

# Three bands.
soft_band(ax, grid, L1_cm_s, COMP_COLOR, base_t=0.032,
          core_alpha=0.96, zorder=3)
soft_band(ax, grid, L1_pm_s, PRIM_COLOR, base_t=0.032,
          core_alpha=0.96, zorder=3)
# Bundle drawn last (top zorder) so its dive is visible crossing
# prime's band at the wound.
soft_band(ax, grid, L1_b_s, BUND_COLOR, base_t=0.030,
          core_alpha=0.98, zorder=4)

# The wound: a thin vertical chasm cutting through everything.
WOUND_W = 4
ax.axvspan(wound_idx - WOUND_W / 2, wound_idx + WOUND_W / 2,
           color=BG, alpha=1.0, zorder=10)
# Hairline outline of the wound to make it crisp.
ax.plot([wound_idx - WOUND_W / 2, wound_idx - WOUND_W / 2],
        [Y_BOTTOM, Y_TOP], color='#000', linewidth=0.3,
        alpha=0.55, zorder=11)
ax.plot([wound_idx + WOUND_W / 2, wound_idx + WOUND_W / 2],
        [Y_BOTTOM, Y_TOP], color='#000', linewidth=0.3,
        alpha=0.55, zorder=11)

ax.set_xlim(0, n_atoms)
ax.set_ylim(Y_BOTTOM, Y_TOP)
ax.axis('off')

# Title at lower-right (matching the COIL and CATHEDRAL conventions).
fig.text(0.97, 0.06, 'THREE TONGUES, BURIED', color='#aaa',
         fontsize=14, ha='right', va='bottom',
         family='serif', weight='bold')
fig.text(0.97, 0.045,
         'composite-m  ·  bundle  ·  prime-m   along the n=2 horizon',
         color='#666', fontsize=9, ha='right', va='top',
         style='italic', family='serif')
fig.text(0.97, 0.030,
         '[2, 10], k = 400   ·   wound at atom ≈ 250',
         color='#555', fontsize=8, ha='right', va='top',
         family='serif')

plt.savefig('three_tongues_buried.png', dpi=180, facecolor=BG,
            bbox_inches='tight')
print("-> three_tongues_buried.png")
