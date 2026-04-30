"""
L1 Tracking-Gap Heatmap — does C_Surv's L1 curve track the bundle's?

For each (K, n_0) with fixed window width W, compute the running
leading-digit L1 deviation from uniform for both the bundle and C_Surv,
then summarise their gap with a single signed scalar:

    gap(K, n_0) = mean over N >= N_warmup of (surv_l1(N) - bundle_l1(N))

Positive = survivor filter makes the leading-digit distribution less
uniform than the bundle; negative = more uniform; zero = perfect
tracking. Plotted as a diverging heatmap (red/blue) with x = K (linear,
fine grid) and y = n_0 (linear). The original Two Tongues parameters
are marked.
"""

import sys
sys.path.insert(0, '../../../../core')
sys.path.insert(0, '.')

import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

# --- Grid: square — same range and step on both axes ---
W = 10
N0_VALUES = np.arange(10, 1001, 10)                 # 100 values
K_VALUES = np.arange(10, 1001, 10)                  # 100 values
WARMUP_FRAC = 0.25
HIGHLIGHT = None

u9 = np.full(9, 1.0 / 9)


def n_primes_vec(n, k):
    """Vectorized: return the first k n-primes as an int64 array.

    n-primes for n >= 2 are n*m where m is not divisible by n.
    """
    # Count blocks of n consecutive m's needed to yield k valid ones.
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


def gap_signed(n0, k, w=W):
    n1 = n0 + w - 1
    parts = [n_primes_vec(n, k) for n in range(n0, n1 + 1)]
    m_arr = np.concatenate(parts)
    n_atoms = m_arr.size

    # Survival mask: True where the integer occurs exactly once.
    _, inverse, counts = np.unique(m_arr, return_inverse=True,
                                   return_counts=True)
    mask = (counts[inverse] == 1).astype(np.int64)

    # Leading digit via integer arithmetic.
    log_floor = np.floor(np.log10(m_arr)).astype(np.int64)
    leading = (m_arr // 10**log_floor).astype(np.int64)  # in 1..9

    ld = np.zeros((n_atoms, 9), dtype=np.int64)
    ld[np.arange(n_atoms), leading - 1] = 1

    ld_b = np.cumsum(ld, axis=0)
    ld_s = np.cumsum(ld * mask[:, None], axis=0)
    tot_b = ld_b.sum(axis=1)
    tot_s = ld_s.sum(axis=1)

    valid = (tot_b > 0) & (tot_s > 0)
    pb = ld_b[valid] / tot_b[valid, None]
    ps = ld_s[valid] / tot_s[valid, None]
    l1_b = np.abs(pb - u9).sum(axis=1)
    l1_s = np.abs(ps - u9).sum(axis=1)

    n_valid = l1_b.size
    start = int(WARMUP_FRAC * n_valid)
    if start >= n_valid:
        return np.nan
    return float(np.mean(l1_s[start:] - l1_b[start:]))


print(f"Computing gap grid: {len(N0_VALUES)} n_0 x {len(K_VALUES)} K "
      f"= {len(N0_VALUES) * len(K_VALUES)} cells, W={W}...")

t0 = time.time()
G = np.full((len(N0_VALUES), len(K_VALUES)), np.nan)
for i, n0 in enumerate(N0_VALUES):
    for j, k in enumerate(K_VALUES):
        G[i, j] = gap_signed(int(n0), int(k))
    if (i + 1) % 5 == 0 or i == 0:
        print(f"  rows done: {i + 1}/{len(N0_VALUES)} "
              f"(t={time.time() - t0:.1f}s)")

print(f"Total compute: {time.time() - t0:.1f}s")
vmax = float(np.nanmax(np.abs(G)))
print(f"Grid range: [{np.nanmin(G):+.4f}, {np.nanmax(G):+.4f}], "
      f"|max|={vmax:.4f}")

# Cache for downstream re-renders.
np.savez('l1_grid.npz', G=G, N0_VALUES=N0_VALUES, K_VALUES=K_VALUES,
         W=W, WARMUP_FRAC=WARMUP_FRAC)
print("-> l1_grid.npz")

# --- Plot ---
fig, ax = plt.subplots(figsize=(11, 11))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

step_x = K_VALUES[1] - K_VALUES[0]
step_y = N0_VALUES[1] - N0_VALUES[0]
norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
extent = (K_VALUES[0] - step_x / 2, K_VALUES[-1] + step_x / 2,
          N0_VALUES[0] - step_y / 2, N0_VALUES[-1] + step_y / 2)
im = ax.imshow(G, aspect='equal', origin='lower', cmap='RdBu_r',
               norm=norm, interpolation='nearest', extent=extent)

ax.set_xlabel('K  (atoms per stream)', color='white', fontsize=12)
ax.set_ylabel(f'n_0  (window = [n_0, n_0 + {W - 1}])',
              color='white', fontsize=12)
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('#333')

ticks = np.arange(100, 1001, 100)
ax.set_xticks(ticks)
ax.set_xticks(np.arange(50, 1001, 50), minor=True)
ax.set_yticks(ticks)
ax.set_yticks(np.arange(50, 1001, 50), minor=True)
ax.tick_params(which='minor', length=2, color='#555')

if HIGHLIGHT is not None:
    hk, hn0 = HIGHLIGHT
    ax.add_patch(plt.Rectangle(
        (hk - step_x / 2, hn0 - step_y / 2), step_x, step_y,
        fill=False, edgecolor='#ffcc5c', linewidth=1.8))

cbar = plt.colorbar(im, ax=ax, fraction=0.025, pad=0.015)
cbar.set_label('mean (surv_L1 − bundle_L1), post-warmup',
               color='white', fontsize=11)
cbar.ax.tick_params(colors='white')
cbar.outline.set_edgecolor('#333')

ax.set_title(
    f'L1 tracking gap — C_Surv vs. bundle   '
    f'(W = {W}, n_0 ∈ [{N0_VALUES[0]}, {N0_VALUES[-1]}], '
    f'K ∈ [{K_VALUES[0]}, {K_VALUES[-1]}], step = {step_x}, '
    f'warmup = {int(WARMUP_FRAC * 100)}%)',
    color='white', fontsize=12)

plt.tight_layout()
plt.savefig('l1_grid.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> l1_grid.png")
