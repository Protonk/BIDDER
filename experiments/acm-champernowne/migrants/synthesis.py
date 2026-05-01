"""
synthesis.py — synthesise G(n_0, K) from bin-1 lattice + bin-2
leading-digit lens, then run a destroyer that randomises the
duplicate-atom leading digits to show that the cell-specific bin-2
information is essential.

Two modes:
  real        actual leading digits (should reproduce l1_grid's G)
  destroyed   duplicate-atom leading digits replaced by Benford samples
              (bin-1 lattice unchanged, bin-2 cell-specific info killed)

Outputs:
  synthesis.npz             — G_synth, G_destroyed cached
  synthesis.png             — G vs G_synth (Image 1)
  synthesis_destroyer.png   — G − G_synth vs G − G_destroyed (Image 2)
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


# Precompute streams up to max K for n in window range.
n_min = int(N0_VALUES[0])
n_max = int(N0_VALUES[-1]) + W - 1
K_max = int(K_VALUES.max())
print(f"Precomputing n-primes for n ∈ [{n_min}, {n_max}], K_max={K_max}...")
t_pre = time.time()
streams = {n: n_primes_vec(n, K_max) for n in range(n_min, n_max + 1)}
print(f"  done in {time.time() - t_pre:.1f}s")

BENFORD_P = np.log10(1 + 1.0 / np.arange(1, 10))
BENFORD_P = BENFORD_P / BENFORD_P.sum()


def gap(n0: int, K: int, mode: str = 'real') -> float:
    parts = [streams[n][:K] for n in range(n0, n0 + W)]
    m_arr = np.concatenate(parts)
    n_atoms = m_arr.size

    unique_atoms, inv, counts_per_unique = np.unique(
        m_arr, return_inverse=True, return_counts=True)
    mask_per_atom = (counts_per_unique[inv] == 1).astype(np.int64)

    log_floor = np.floor(np.log10(m_arr)).astype(np.int64)
    leading = (m_arr // 10 ** log_floor).astype(np.int64)

    if mode == 'destroyed':
        unique_log_floor = np.floor(np.log10(unique_atoms)).astype(np.int64)
        unique_leading = (unique_atoms // 10 ** unique_log_floor).astype(np.int64)
        is_dup = counts_per_unique > 1
        n_dup_unique = int(is_dup.sum())
        new_unique_leading = unique_leading.copy()
        if n_dup_unique > 0:
            new_unique_leading[is_dup] = RNG.choice(
                np.arange(1, 10), size=n_dup_unique, p=BENFORD_P)
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


print('Computing G_synth (real) and G_destroyed (Benford-randomised duplicates)...')
t0 = time.time()
G_synth = np.full((len(N0_VALUES), len(K_VALUES)), np.nan)
G_destroyed = np.full((len(N0_VALUES), len(K_VALUES)), np.nan)
for i, n0 in enumerate(N0_VALUES):
    for j, K in enumerate(K_VALUES):
        G_synth[i, j] = gap(int(n0), int(K), 'real')
        G_destroyed[i, j] = gap(int(n0), int(K), 'destroyed')
    if (i + 1) % 10 == 0:
        print(f'  rows: {i+1}/{len(N0_VALUES)} (t={time.time()-t0:.1f}s)')
print(f'Total: {time.time()-t0:.1f}s')

np.savez(os.path.join(HERE, 'synthesis.npz'),
         G_synth=G_synth, G_destroyed=G_destroyed,
         N0_VALUES=N0_VALUES, K_VALUES=K_VALUES, W=W)
print('-> synthesis.npz')

# Compare to G from l1_grid.
g = np.load(os.path.join(HERE, 'l1_grid.npz'))
G = g['G']


def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    return float(np.corrcoef(ra, rb)[0, 1])


mask = np.isfinite(G) & np.isfinite(G_synth) & np.isfinite(G_destroyed)
rho_synth = spearman(G[mask].ravel(), G_synth[mask].ravel())
rho_destroyed = spearman(G[mask].ravel(), G_destroyed[mask].ravel())
sign_synth = float((np.sign(G[mask]) == np.sign(G_synth[mask])).mean())
sign_destroyed = float((np.sign(G[mask]) == np.sign(G_destroyed[mask])).mean())
mae_synth = float(np.abs(G[mask] - G_synth[mask]).mean())
mae_destroyed = float(np.abs(G[mask] - G_destroyed[mask]).mean())
total_mean_abs = float(np.abs(G[mask]).mean())

print(f'\nρ(G, G_synth):       {rho_synth:+.4f}    '
      f'sign agreement: {sign_synth:.3f}    '
      f'MAE / mean|G|: {mae_synth:.5f} / {total_mean_abs:.5f} = '
      f'{100*mae_synth/total_mean_abs:.1f}%')
print(f'ρ(G, G_destroyed):   {rho_destroyed:+.4f}    '
      f'sign agreement: {sign_destroyed:.3f}    '
      f'MAE / mean|G|: {mae_destroyed:.5f} / {total_mean_abs:.5f} = '
      f'{100*mae_destroyed/total_mean_abs:.1f}%')

# ── Image 1: G observed | G_synth ──────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(15, 7))
fig.patch.set_facecolor('#0a0a0a')
step = K_VALUES[1] - K_VALUES[0]
extent = (K_VALUES[0]-step/2, K_VALUES[-1]+step/2,
          N0_VALUES[0]-step/2, N0_VALUES[-1]+step/2)
vmax = float(np.nanpercentile(np.abs(G), 95))
norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)

panel_data = [
    (G,       'G  (observed, l1_grid.npz)'),
    (G_synth, f'G_synth  (bin-1 × bin-2 synthesis)\n'
              f'ρ = {rho_synth:+.4f}, sign agree {100*sign_synth:.1f}%')
]
for ax, (data, title) in zip(axes, panel_data):
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
    'Synthesis: bin-1 lattice × bin-2 leading-digit lens reproduces the L1 tracking gap',
    color='white', fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(HERE, 'synthesis.png'), dpi=180,
            facecolor='#0a0a0a', bbox_inches='tight')
print('-> synthesis.png')

# ── Image 2: residuals — synthesis vs destroyer ────────────────────
fig2, axes2 = plt.subplots(1, 2, figsize=(15, 7))
fig2.patch.set_facecolor('#0a0a0a')

panel_data2 = [
    (G - G_synth,
     f'G − G_synth  (synthesis residual)\n'
     f'MAE / mean|G| = {100*mae_synth/total_mean_abs:.1f}%'),
    (G - G_destroyed,
     f'G − G_destroyed  (destroyer: Benford-random dup digits)\n'
     f'MAE / mean|G| = {100*mae_destroyed/total_mean_abs:.1f}%')
]
for ax, (data, title) in zip(axes2, panel_data2):
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

fig2.suptitle(
    'Destroyer: randomising bin-2 (duplicate leading digits) collapses the synthesis match',
    color='white', fontsize=12)
fig2.tight_layout()
fig2.savefig(os.path.join(HERE, 'synthesis_destroyer.png'), dpi=180,
             facecolor='#0a0a0a', bbox_inches='tight')
print('-> synthesis_destroyer.png')
