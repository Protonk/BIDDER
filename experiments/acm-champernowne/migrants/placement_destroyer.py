"""
placement_destroyer.py — histogram-preserving destroyer.

Migrant #7. Where `synthesis.py:gap('destroyed')` replaces each
duplicate-atom leading digit with a fresh Benford sample (randomising
both the per-cell distribution and the per-atom assignment), this
script preserves the per-cell multiset of duplicate leading digits and
only permutes which duplicate unique atom gets which digit.

If `G_shuffled ≈ G`: the cross-cutting result is **digit-distribution
coupling** — only the distribution mattered, the placement does not.

If `G_shuffled ≈ G_destroyed` (collapsed): **digit-placement
coupling** — the specific duplicated atoms sit in specific leading-
digit classes, not just "the duplicate-digit distribution has this
shape." Strictly stronger than the result `synthesis.py` already
established.

Outputs:
  placement_destroyer.npz    G_shuffled
  placement_destroyer.png    G | G_shuffled | G − G_shuffled
"""

import os
import time

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm


HERE = os.path.dirname(os.path.abspath(__file__))

W = 10
N0_VALUES = np.arange(10, 1001, 10)
K_VALUES = np.arange(10, 1001, 10)
WARMUP_FRAC = 0.25
RNG = np.random.default_rng(20260430)


def n_primes_vec(n: int, k: int) -> np.ndarray:
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    return (n * m[m % n != 0][:k]).astype(np.int64)


n_min = int(N0_VALUES[0])
n_max = int(N0_VALUES[-1]) + W - 1
K_max = int(K_VALUES.max())
print(f"Precomputing n-primes for n ∈ [{n_min}, {n_max}], K_max={K_max}...")
streams = {n: n_primes_vec(n, K_max) for n in range(n_min, n_max + 1)}


def gap_shuffled(n0: int, K: int) -> float:
    """Compute G(n_0, K) with duplicate-leading-digit values permuted
    among duplicate unique atoms only (per-cell multiset preserved).
    Singleton-atom digits are left alone.
    """
    parts = [streams[n][:K] for n in range(n0, n0 + W)]
    m_arr = np.concatenate(parts)
    n_atoms = m_arr.size

    unique_atoms, inv, counts_per_unique = np.unique(
        m_arr, return_inverse=True, return_counts=True)
    mask_per_atom = (counts_per_unique[inv] == 1).astype(np.int64)

    unique_log_floor = np.floor(np.log10(unique_atoms)).astype(np.int64)
    unique_leading = (unique_atoms // 10 ** unique_log_floor).astype(np.int64)

    is_dup = counts_per_unique > 1
    new_unique_leading = unique_leading.copy()
    n_dup_unique = int(is_dup.sum())
    if n_dup_unique > 1:
        # Permute the multiset of duplicate leading digits among
        # duplicate unique atoms. Multiset preserved exactly; placement
        # randomised.
        dup_vals = unique_leading[is_dup].copy()
        RNG.shuffle(dup_vals)
        new_unique_leading[is_dup] = dup_vals
    leading = new_unique_leading[inv]

    ld = np.zeros((n_atoms, 9), dtype=np.int64)
    ld[np.arange(n_atoms), leading - 1] = 1

    ld_b = np.cumsum(ld, axis=0)
    ld_s = np.cumsum(ld * mask_per_atom[:, None], axis=0)
    tot_b = ld_b.sum(axis=1)
    tot_s = ld_s.sum(axis=1)

    valid = (tot_b > 0) & (tot_s > 0)
    pb = ld_b[valid] / tot_b[valid, None]
    ps = ld_s[valid] / tot_s[valid, None]
    l1_b = np.abs(pb - 1.0 / 9).sum(axis=1)
    l1_s = np.abs(ps - 1.0 / 9).sum(axis=1)

    n_valid = l1_b.size
    start = int(WARMUP_FRAC * n_valid)
    if start >= n_valid:
        return float('nan')
    return float(np.mean(l1_s[start:] - l1_b[start:]))


print("Computing G_shuffled (multiset preserved, placement permuted)...")
t0 = time.time()
G_shuffled = np.full((len(N0_VALUES), len(K_VALUES)), np.nan)
for i, n0 in enumerate(N0_VALUES):
    for j, K in enumerate(K_VALUES):
        G_shuffled[i, j] = gap_shuffled(int(n0), int(K))
    if (i + 1) % 10 == 0:
        print(f"  rows: {i+1}/{len(N0_VALUES)} (t={time.time()-t0:.1f}s)")
print(f"Total: {time.time()-t0:.1f}s")

np.savez(os.path.join(HERE, 'placement_destroyer.npz'),
         G_shuffled=G_shuffled,
         N0_VALUES=N0_VALUES, K_VALUES=K_VALUES, W=W)
print("-> placement_destroyer.npz")

# Compare to G and G_destroyed.
g = np.load(os.path.join(HERE, 'l1_grid.npz'))
G = g['G']
synth = np.load(os.path.join(HERE, 'synthesis.npz'))
G_destroyed = synth['G_destroyed']


def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    return float(np.corrcoef(ra, rb)[0, 1])


mask = np.isfinite(G) & np.isfinite(G_shuffled) & np.isfinite(G_destroyed)
total_mean_abs = float(np.abs(G[mask]).mean())

# G vs G_shuffled (the new experiment)
rho_shuf = spearman(G[mask].ravel(), G_shuffled[mask].ravel())
sign_shuf = float((np.sign(G[mask]) == np.sign(G_shuffled[mask])).mean())
mae_shuf = float(np.abs(G[mask] - G_shuffled[mask]).mean())
pearson_shuf = float(np.corrcoef(G[mask].ravel(), G_shuffled[mask].ravel())[0, 1])

# G vs G_destroyed (recompute for comparison)
rho_des = spearman(G[mask].ravel(), G_destroyed[mask].ravel())
sign_des = float((np.sign(G[mask]) == np.sign(G_destroyed[mask])).mean())
mae_des = float(np.abs(G[mask] - G_destroyed[mask]).mean())
pearson_des = float(np.corrcoef(G[mask].ravel(), G_destroyed[mask].ravel())[0, 1])

print()
print(f"{'metric':<22s}  {'shuffled':>10s}  {'destroyed':>10s}  {'(reference: synth = G exactly)':>32s}")
print(f"{'Spearman ρ':<22s}  {rho_shuf:>+10.4f}  {rho_des:>+10.4f}")
print(f"{'Pearson r':<22s}  {pearson_shuf:>+10.4f}  {pearson_des:>+10.4f}")
print(f"{'sign agreement':<22s}  {sign_shuf:>10.3f}  {sign_des:>10.3f}")
print(f"{'MAE / mean|G|':<22s}  {100*mae_shuf/total_mean_abs:>9.1f}%  "
      f"{100*mae_des/total_mean_abs:>9.1f}%")

# Verdict.
if mae_shuf / total_mean_abs < 0.20:
    print("\nVerdict: G_shuffled tracks G closely → digit-DISTRIBUTION coupling.")
    print("  The per-cell multiset of duplicate leading digits is sufficient;")
    print("  placement among duplicate atoms does not matter.")
elif mae_shuf / total_mean_abs > 0.50:
    print("\nVerdict: G_shuffled collapses → digit-PLACEMENT coupling.")
    print("  The specific duplicated atoms sit in specific leading-digit classes;")
    print("  preserving only the distribution is not enough.")
else:
    print("\nVerdict: intermediate. Distribution matters but placement also "
          "carries some signal.")

# ── Three-panel figure ─────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(20, 7))
fig.patch.set_facecolor('#0a0a0a')
step = K_VALUES[1] - K_VALUES[0]
extent = (K_VALUES[0]-step/2, K_VALUES[-1]+step/2,
          N0_VALUES[0]-step/2, N0_VALUES[-1]+step/2)
vmax = float(np.nanpercentile(np.abs(G), 95))
norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)

panels = [
    (G, 'G  (observed)'),
    (G_shuffled,
     f'G_shuffled  (multiset preserved, placement permuted)\n'
     f'ρ = {rho_shuf:+.4f}, sign agree {100*sign_shuf:.1f}%, '
     f'MAE = {100*mae_shuf/total_mean_abs:.1f}% of mean|G|'),
    (G - G_shuffled,
     f'G − G_shuffled  (residual)\n'
     f'compare to destroyer residual MAE {100*mae_des/total_mean_abs:.1f}%')
]
for ax, (data, title) in zip(axes, panels):
    ax.set_facecolor('#0a0a0a')
    im = ax.imshow(data, origin='lower', cmap='RdBu_r', norm=norm,
                   extent=extent, aspect='equal', interpolation='nearest')
    ax.set_title(title, color='white', fontsize=11)
    ax.set_xlabel('K', color='white')
    ax.set_ylabel('n_0', color='white')
    ax.tick_params(colors='white', labelsize=8)
    for spine in ax.spines.values():
        spine.set_color('#333')
    plt.colorbar(im, ax=ax, fraction=0.04, pad=0.02)

fig.suptitle(
    'Placement destroyer (migrant #7): does the per-cell multiset alone reproduce G?',
    color='white', fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(HERE, 'placement_destroyer.png'), dpi=180,
            facecolor='#0a0a0a', bbox_inches='tight')
print("\n-> placement_destroyer.png")
