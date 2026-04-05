"""
acm_benford.py — Benford convergence and rolling shutter analysis
==================================================================

Generates:
  1. First-digit histogram vs Benford (demonstrating exact uniformity)
  2. Convergence to Benford under multiplication (grouped bar chart)
  3. Rolling shutter under addition (grouped bar chart)
  4. Dual heatmap: multiplication (1-1000) vs addition (1-1000)
  5. Consecutive-sum comparison: ACM vs commodity uniform (crispness test)

All plots saved to current directory.

Usage:
    python acm_benford.py
"""

import matplotlib.pyplot as plt
import numpy as np
from acm_core import (
    champernowne_array, first_digit_array, first_digit, benford_pmf
)


N = 10000
reals = champernowne_array(N)
log_reals = np.log10(reals)
rng = np.random.default_rng(42)
benford = benford_pmf()


# =====================================================================
# Plot 1: First-digit histogram — exact uniformity
# =====================================================================

print("Plotting first-digit histogram...")
fds = first_digit_array(reals)
counts = np.array([np.sum(fds == d) for d in range(1, 10)])
fracs = counts / N

fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(1, 10)
ax.bar(x - 0.15, fracs, width=0.3, color='steelblue', label='observed')
ax.bar(x + 0.15, benford, width=0.3, color='salmon', alpha=0.7, label='Benford')
ax.set_xticks(x)
ax.set_xlabel('first digit')
ax.set_ylabel('frequency')
ax.set_title(f'First digit distribution of n-Champernowne reals (n=1..{N})')
ax.legend()
plt.tight_layout()
plt.savefig('first_digits.png', dpi=200)
print("  -> first_digits.png")


# =====================================================================
# Plot 2: Multiplication convergence to Benford
# =====================================================================

print("Plotting multiplication convergence...")
mult_ks = [1, 2, 4, 8]
colors_mult = ['#2166ac', '#67a9cf', '#f4a582', '#b2182b']
labels_mult = ['0 mult', '1 mult', '3 mult', '7 mult']
n_samples = 5000

fig, ax = plt.subplots(figsize=(12, 6))
bar_width = 0.18

for idx, k in enumerate(mult_ks):
    indices = rng.integers(0, N, size=(n_samples, k))
    log_products = np.sum(log_reals[indices], axis=1)
    fracs_lp = log_products - np.floor(log_products)
    fds_m = np.minimum((10**fracs_lp).astype(int), 9)
    digit_fracs = [np.sum(fds_m == d) / n_samples for d in range(1, 10)]
    offset = (idx - 1.5) * bar_width
    ax.bar(x + offset, digit_fracs, width=bar_width, color=colors_mult[idx],
           label=labels_mult[idx], alpha=0.85)

ax.plot(x, benford, 'k--', linewidth=2, label='Benford', zorder=5)
ax.set_xticks(x)
ax.set_xlabel('first digit')
ax.set_ylabel('frequency')
ax.set_title('Convergence to Benford under multiplication')
ax.legend()
plt.tight_layout()
plt.savefig('multiplication_convergence.png', dpi=200)
print("  -> multiplication_convergence.png")


# =====================================================================
# Plot 3: Addition rolling shutter
# =====================================================================

print("Plotting addition rolling shutter...")
add_ks = [1, 2, 4, 8]
colors_add = ['#2166ac', '#67a9cf', '#f4a582', '#b2182b']
labels_add = ['0 add', '1 add', '3 add', '7 add']

fig, ax = plt.subplots(figsize=(12, 6))

for idx, k in enumerate(add_ks):
    indices = rng.integers(0, N, size=(n_samples, k))
    sums = np.sum(reals[indices], axis=1)
    fds_a = np.array([first_digit(v) for v in sums])
    digit_fracs = [np.sum(fds_a == d) / n_samples for d in range(1, 10)]
    offset = (idx - 1.5) * bar_width
    ax.bar(x + offset, digit_fracs, width=bar_width, color=colors_add[idx],
           label=labels_add[idx], alpha=0.85)

ax.plot(x, benford, 'k--', linewidth=2, label='Benford', zorder=5)
ax.set_xticks(x)
ax.set_xlabel('first digit')
ax.set_ylabel('frequency')
ax.set_title('Non-convergence under addition (rolling shutter)')
ax.legend()
plt.tight_layout()
plt.savefig('addition_shutter.png', dpi=200)
print("  -> addition_shutter.png")


# =====================================================================
# Plot 4: Dual heatmap — multiplication vs addition, 1-1000
# =====================================================================

print("Building dual heatmaps (this takes a moment)...")
ks_heat = np.unique(np.geomspace(1, 1000, 200).astype(int))

def build_heatmap(reals, log_reals, ks, n_samples, rng, mode='mult'):
    """Build first-digit heatmap for multiplication or addition."""
    heat = np.zeros((len(ks), 9))
    for i, k in enumerate(ks):
        indices = rng.integers(0, len(reals), size=(n_samples, k))
        if mode == 'mult':
            log_products = np.sum(log_reals[indices], axis=1)
            fracs = log_products - np.floor(log_products)
        else:  # addition
            sums = np.sum(reals[indices], axis=1)
            log_sums = np.log10(sums)
            fracs = log_sums - np.floor(log_sums)
        fds = np.minimum((10**fracs).astype(int), 9)
        for d in range(1, 10):
            heat[i, d-1] = np.sum(fds == d) / n_samples
    return heat

mult_heat = build_heatmap(reals, log_reals, ks_heat, n_samples, rng, 'mult')
add_heat = build_heatmap(reals, log_reals, ks_heat, n_samples, rng, 'add')

fig, axes = plt.subplots(2, 1, figsize=(12, 14))

ax = axes[0]
im = ax.pcolormesh(np.arange(0.5, 10.5),
                   np.concatenate([[ks_heat[0]*0.9], ks_heat]),
                   mult_heat, cmap='RdBu_r', vmin=0, vmax=0.5)
ax.set_yscale('log')
ax.set_xticks(range(1, 10))
ax.set_xlabel('first digit')
ax.set_ylabel('multiplications (log scale)')
ax.set_title('Multiplications (1–1000)')
plt.colorbar(im, ax=ax, label='frequency')

ax = axes[1]
im2 = ax.pcolormesh(np.arange(0.5, 10.5),
                    np.concatenate([[ks_heat[0]*0.9], ks_heat]),
                    add_heat, cmap='RdBu_r', vmin=0, vmax=0.5)
ax.set_yscale('log')
ax.set_xticks(range(1, 10))
ax.set_xlabel('first digit')
ax.set_ylabel('additions (log scale)')
ax.set_title('Additions (1–1000)')
plt.colorbar(im2, ax=ax, label='frequency')

plt.tight_layout()
plt.savefig('dual_heatmap.png', dpi=200)
print("  -> dual_heatmap.png")


# =====================================================================
# Plot 5: Consecutive-sum crispness comparison
# =====================================================================

print("Building crispness comparison...")
unif_reals = rng.uniform(1.1, 2.0, size=N)

acm_cumsum = np.concatenate([[0], np.cumsum(reals)])
unif_cumsum = np.concatenate([[0], np.cumsum(unif_reals)])

ks_cons = np.unique(np.geomspace(1, 5000, 300).astype(int))

def build_consecutive_heatmap(cumsum, ks, N):
    """Sliding window sums: preserves ordering structure."""
    heat = np.zeros((len(ks), 9))
    for i, k in enumerate(ks):
        n_windows = N - k + 1
        sums = cumsum[k:k+n_windows] - cumsum[:n_windows]
        log_sums = np.log10(sums)
        fracs = log_sums - np.floor(log_sums)
        fds = np.minimum((10**fracs).astype(int), 9)
        for d in range(1, 10):
            heat[i, d-1] = np.sum(fds == d) / n_windows
    return heat

unif_heat = build_consecutive_heatmap(unif_cumsum, ks_cons, N)
acm_heat = build_consecutive_heatmap(acm_cumsum, ks_cons, N)

fig, axes = plt.subplots(2, 1, figsize=(12, 14))

ax = axes[0]
im = ax.pcolormesh(np.arange(0.5, 10.5),
                   np.concatenate([[ks_cons[0]*0.9], ks_cons]),
                   unif_heat, cmap='RdBu_r', vmin=0, vmax=0.5)
ax.set_yscale('log')
ax.set_xticks(range(1, 10))
ax.set_xlabel('first digit')
ax.set_ylabel('window size (log scale)')
ax.set_title('Commodity uniform — consecutive sums (sliding window)')
plt.colorbar(im, ax=ax, label='frequency')

ax = axes[1]
im2 = ax.pcolormesh(np.arange(0.5, 10.5),
                    np.concatenate([[ks_cons[0]*0.9], ks_cons]),
                    acm_heat, cmap='RdBu_r', vmin=0, vmax=0.5)
ax.set_yscale('log')
ax.set_xticks(range(1, 10))
ax.set_xlabel('first digit')
ax.set_ylabel('window size (log scale)')
ax.set_title('ACM n-Champernowne — consecutive sums (sliding window)')
plt.colorbar(im2, ax=ax, label='frequency')

plt.tight_layout()
plt.savefig('crispness_comparison.png', dpi=200)
print("  -> crispness_comparison.png")

print("\nDone. All plots saved.")
