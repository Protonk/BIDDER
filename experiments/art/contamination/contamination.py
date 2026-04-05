"""
contamination.py — How operations contaminate a uniform source.

Start with the HCH generator producing perfectly uniform digits.
Then watch what happens as we apply operations:

  Row 1: Raw uniform output (the irreducibles)
  Row 2: Pairwise addition
  Row 3: Pairwise multiplication after the addition
  Row 4: Pairwise addition after the multiplication

Each row is a heatmap of first-digit frequency as a function of
how many operations have been applied. The uniform source gets
"contaminated" by multiplication (which bends it toward Benford)
and "un-contaminated" by addition (which smears it back).

The result shows the tug-of-war: multiplication introduces
logarithmic structure, addition fights it with linear cycling.
"""

import sys
sys.path.insert(0, '../../../generator')
sys.path.insert(0, '../../..')

import numpy as np
import matplotlib.pyplot as plt
from hch_speck import HCHSpeck

# --- Generate uniform source ---
print("Generating uniform source...")
gen = HCHSpeck(base=10, digit_class=4, key=b'contamination')
N = gen.period  # 9000 outputs, exactly uniform
raw = np.array(gen.generate(N), dtype=np.float64)

# Map digits {1..9} to reals in [1.1, 2.0) for arithmetic
reals = 1.0 + raw / 10.0

n_trials = 5000
n_ops = 200  # operations per chain
rng = np.random.default_rng(42)


def first_digits(values):
    """Extract base-10 first significant digit from array of positive reals."""
    log_v = np.log10(values)
    frac = log_v - np.floor(log_v)
    return np.minimum((10**frac).astype(int), 9)


def build_heatmap(reals, ops_sequence, n_trials, n_ops, rng):
    """
    Build a heatmap of first-digit frequencies under a sequence of operations.

    ops_sequence: list of 'add' or 'mul' strings, applied cyclically.
    Returns (n_ops, 9) array.
    """
    heat = np.zeros((n_ops, 9))
    N = len(reals)
    log_reals = np.log10(reals)

    # Start with random draws from the source
    idx = rng.integers(0, N, size=n_trials)
    values = reals[idx].copy()
    log_values = log_reals[idx].copy()

    for step in range(n_ops):
        op = ops_sequence[step % len(ops_sequence)]
        idx2 = rng.integers(0, N, size=n_trials)

        if op == 'add':
            values = values + reals[idx2]
            log_values = np.log10(values)
        else:  # mul
            log_values = log_values + log_reals[idx2]
            values = 10**log_values

        fds = first_digits(values)
        for d in range(1, 10):
            heat[step, d - 1] = np.sum(fds == d) / n_trials

    return heat


print("Building heatmaps...")

# Chain 1: pure addition (rolling shutter)
print("  add, add, add, ...")
heat_aaa = build_heatmap(reals, ['add'], n_trials, n_ops, np.random.default_rng(1))

# Chain 2: pure multiplication (Benford convergence)
print("  mul, mul, mul, ...")
heat_mmm = build_heatmap(reals, ['mul'], n_trials, n_ops, np.random.default_rng(1))

# Chain 3: add then mul alternating
print("  add, mul, add, mul, ...")
heat_am = build_heatmap(reals, ['add', 'mul'], n_trials, n_ops, np.random.default_rng(1))

# Chain 4: mul then add alternating
print("  mul, add, mul, add, ...")
heat_ma = build_heatmap(reals, ['mul', 'add'], n_trials, n_ops, np.random.default_rng(1))

# Chain 5: mul, mul, add (two muls per add — does Benford win?)
print("  mul, mul, add, ...")
heat_mma = build_heatmap(reals, ['mul', 'mul', 'add'], n_trials, n_ops, np.random.default_rng(1))

# Chain 6: add, add, mul (two adds per mul — does the shutter win?)
print("  add, add, mul, ...")
heat_aam = build_heatmap(reals, ['add', 'add', 'mul'], n_trials, n_ops, np.random.default_rng(1))


# --- Plot ---
print("Plotting...")

benford = np.array([np.log10(1 + 1/d) for d in range(1, 10)])

fig, axes = plt.subplots(2, 3, figsize=(24, 14), sharey=True, sharex=True)
fig.patch.set_facecolor('#0a0a0a')

panels = [
    (axes[0, 0], heat_aaa, 'add, add, add, ...'),
    (axes[0, 1], heat_mmm, 'mul, mul, mul, ...'),
    (axes[0, 2], heat_am,  'add, mul, add, mul, ...'),
    (axes[1, 0], heat_ma,  'mul, add, mul, add, ...'),
    (axes[1, 1], heat_mma, 'mul, mul, add, ...'),
    (axes[1, 2], heat_aam, 'add, add, mul, ...'),
]

vmax = max(h.max() for _, h, _ in panels)

for ax, heat, title in panels:
    ax.set_facecolor('#0a0a0a')
    ax.imshow(heat, aspect='auto', cmap='inferno',
              interpolation='bilinear', origin='lower',
              extent=[0.5, 9.5, 0, n_ops],
              vmin=0, vmax=vmax)
    ax.set_xticks(range(1, 10))
    ax.set_title(title, color='white', fontsize=13, pad=10)
    ax.tick_params(colors='white')

axes[1, 0].set_xlabel('first digit', color='white', fontsize=12)
axes[1, 1].set_xlabel('first digit', color='white', fontsize=12)
axes[1, 2].set_xlabel('first digit', color='white', fontsize=12)
axes[0, 0].set_ylabel('operations', color='white', fontsize=12)
axes[1, 0].set_ylabel('operations', color='white', fontsize=12)

plt.subplots_adjust(wspace=0.05, hspace=0.15)
plt.savefig('contamination.png', dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
print("-> contamination.png")
