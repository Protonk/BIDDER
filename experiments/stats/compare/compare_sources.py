"""
Source comparison — ACM Champernowne vs Python uniform.

2x2 grid:
  Top row:    ACM Champernowne reals as source
  Bottom row: numpy uniform(1.1, 2.0) as source
  Left col:   Addition
  Right col:  Multiplication

Same RNG seeds, same sample counts, same colormap and scale.
"""

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'core'))

import numpy as np
import matplotlib.pyplot as plt
from acm_core import acm_champernowne_array, acm_first_digit_array

N = 10000
n_steps = 500
n_samples = 8000

# --- Build both sources ---
print("Building ACM source...")
acm_reals = acm_champernowne_array(N)
acm_log = np.log10(acm_reals)

print("Building Python uniform source...")
rng_source = np.random.default_rng(99)
py_reals = rng_source.uniform(1.1, 2.0, size=N)
py_log = np.log10(py_reals)


def first_digits_from_log_fracs(fracs):
    return np.minimum((10**fracs + 1e-9).astype(int), 9)


def build_heatmaps(reals, log_reals, n_steps, n_samples, seed):
    """Build addition and multiplication heatmaps for a source."""
    rng_a = np.random.default_rng(seed)
    rng_m = np.random.default_rng(seed)

    heat_add = np.zeros((n_steps, 9))
    heat_mul = np.zeros((n_steps, 9))

    for i, k in enumerate(range(1, n_steps + 1)):
        idx_a = rng_a.integers(0, len(reals), size=(n_samples, k))
        sums = np.sum(reals[idx_a], axis=1)
        fds = acm_first_digit_array(sums)
        for d in range(1, 10):
            heat_add[i, d - 1] = np.sum(fds == d) / n_samples

        idx_m = rng_m.integers(0, len(reals), size=(n_samples, k))
        log_products = np.sum(log_reals[idx_m], axis=1)
        fracs = log_products - np.floor(log_products)
        fds = first_digits_from_log_fracs(fracs)
        for d in range(1, 10):
            heat_mul[i, d - 1] = np.sum(fds == d) / n_samples

        if (i + 1) % 100 == 0:
            print(f"    step {i+1}/{n_steps}")

    return heat_add, heat_mul


print("Computing ACM heatmaps...")
acm_add, acm_mul = build_heatmaps(acm_reals, acm_log, n_steps, n_samples, 42)

print("Computing Python uniform heatmaps...")
py_add, py_mul = build_heatmaps(py_reals, py_log, n_steps, n_samples, 42)

# Shared color scale
vmax = max(acm_add.max(), acm_mul.max(), py_add.max(), py_mul.max())

print("Plotting...")
fig, axes = plt.subplots(2, 2, figsize=(14, 16), sharey=True, sharex='col')
fig.patch.set_facecolor('#0a0a0a')

panels = [
    (axes[0, 0], acm_add, 'ACM — Addition'),
    (axes[0, 1], acm_mul, 'ACM — Multiplication'),
    (axes[1, 0], py_add,  'numpy.uniform — Addition'),
    (axes[1, 1], py_mul,  'numpy.uniform — Multiplication'),
]

for ax, heat, title in panels:
    ax.set_facecolor('#0a0a0a')
    ax.imshow(heat, aspect='auto', cmap='inferno',
              interpolation='bilinear', origin='lower',
              extent=[0.5, 9.5, 1, n_steps],
              vmin=0, vmax=vmax)
    ax.set_xticks(range(1, 10))
    ax.set_title(title, color='white', fontsize=12, pad=10)
    ax.tick_params(colors='white')

axes[1, 0].set_xlabel('first digit', color='white', fontsize=11)
axes[1, 1].set_xlabel('first digit', color='white', fontsize=11)
axes[0, 0].set_ylabel('operations', color='white', fontsize=11)
axes[1, 0].set_ylabel('operations', color='white', fontsize=11)

plt.subplots_adjust(wspace=0.08, hspace=0.12)
plt.savefig('compare_sources.png', dpi=300, facecolor='#0a0a0a', bbox_inches='tight')
print("-> compare_sources.png")
