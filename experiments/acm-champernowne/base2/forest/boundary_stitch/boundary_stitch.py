"""
boundary_stitch.py — visualize the bit pattern at every entry boundary

For each monoid n, extract a window of bits around every entry boundary
in the binary Champernowne stream, stack the windows into an image, and
display them side by side for several n values.

Predictions (from BOUNDARY_STITCH.md):
  - LEFT of join: v_2(n) solid dark columns (guaranteed trailing zeros)
  - JOIN (column 0): solid bright column (leading 1 of incoming entry)
  - RIGHT of join: possible gradient (consecutive n-primes share
    leading bits because they're close in value)
  - Bit-length transitions: anomalous rows where window is asymmetric
"""

import sys, os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..'))             # base2/
sys.path.insert(0, os.path.join(_here, '..', '..', '..', '..', '..', 'core'))  # core/

import numpy as np
import matplotlib.pyplot as plt
from acm_core import acm_n_primes


HALF_WINDOW = 10          # bits on each side of the join
WINDOW = 2 * HALF_WINDOW  # total columns per boundary
N_ENTRIES = 800           # n-primes per monoid (gives ~800 boundary rows)

# Monoids to display: mix of v_2 values and odd/even
MONOIDS = [3, 5, 2, 6, 4, 12, 8, 16, 32, 64]
LABELS  = ['n=3\n$\\nu_2$=0',
           'n=5\n$\\nu_2$=0',
           'n=2\n$\\nu_2$=1',
           'n=6\n$\\nu_2$=1',
           'n=4\n$\\nu_2$=2',
           'n=12\n$\\nu_2$=2',
           'n=8\n$\\nu_2$=3',
           'n=16\n$\\nu_2$=4',
           'n=32\n$\\nu_2$=5',
           'n=64\n$\\nu_2$=6']


def build_stitch(n):
    """
    Build the boundary stitch matrix for monoid n.

    Returns an (N_ENTRIES-1, WINDOW) array of floats (0.0 or 1.0).
    Each row is one boundary, columns are bit positions relative to
    the join (negative indices = trailing bits of outgoing entry,
    positive indices = leading bits of incoming entry).
    NaN marks positions that fall outside the entry's bits.
    """
    primes = acm_n_primes(n, N_ENTRIES)

    # Convert each n-prime to a list of bits
    entries = []
    for p in primes:
        bits = []
        for ch in bin(p)[2:]:
            bits.append(float(ch))
        entries.append(bits)

    n_boundaries = len(entries) - 1
    stitch = np.full((n_boundaries, WINDOW), np.nan)

    for i in range(n_boundaries):
        left_entry  = entries[i]
        right_entry = entries[i + 1]

        # Left side: last HALF_WINDOW bits of outgoing entry
        for j in range(HALF_WINDOW):
            col = HALF_WINDOW - 1 - j   # column index (0 = just left of join)
            idx = len(left_entry) - 1 - j
            if idx >= 0:
                stitch[i, col] = left_entry[idx]

        # Right side: first HALF_WINDOW bits of incoming entry
        for j in range(HALF_WINDOW):
            col = HALF_WINDOW + j
            if j < len(right_entry):
                stitch[i, col] = right_entry[j]

    return stitch


# ── Compute ──────────────────────────────────────────────────────────

print("Building stitch matrices...")
stitches = []
for n in MONOIDS:
    print(f"  n = {n}...")
    stitches.append(build_stitch(n))


# ── Plot ─────────────────────────────────────────────────────────────

print("Plotting...")

n_panels = len(MONOIDS)
fig, axes = plt.subplots(1, n_panels, figsize=(2.2 * n_panels, 12),
                         sharey=True)
fig.patch.set_facecolor('#0a0a0a')

for ax, stitch, label in zip(axes, stitches, LABELS):
    ax.set_facecolor('#0a0a0a')

    # Use a two-tone colormap: black (0) and white (1), NaN = dark gray
    ax.imshow(stitch, aspect='auto', cmap='gray', vmin=0, vmax=1,
              interpolation='nearest', origin='lower',
              extent=[-HALF_WINDOW, HALF_WINDOW, 0, stitch.shape[0]])

    # Mark the join
    ax.axvline(x=0, color='#ff6f61', linewidth=0.6, alpha=0.5)

    ax.set_xlabel(label, color='white', fontsize=9)
    ax.set_xticks([-HALF_WINDOW, -HALF_WINDOW // 2, 0,
                    HALF_WINDOW // 2, HALF_WINDOW])
    ax.tick_params(colors='white', labelsize=7)
    for spine in ax.spines.values():
        spine.set_color('#333')

axes[0].set_ylabel('boundary index (entry k → entry k+1)',
                    color='white', fontsize=10)

fig.suptitle(
    'Boundary Stitch: bit windows around every entry join',
    color='white', fontsize=14, y=0.95
)

# Column-position annotation
fig.text(0.25, 0.02, '← trailing bits of outgoing entry',
         color='#6ec6ff', fontsize=9, ha='center')
fig.text(0.75, 0.02, 'leading bits of incoming entry →',
         color='#ffcc5c', fontsize=9, ha='center')

plt.tight_layout(rect=[0, 0.04, 1, 0.93])
plt.savefig('boundary_stitch.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> boundary_stitch.png")


# ── Summary stats ────────────────────────────────────────────────────

print("\nBoundary column means (fraction of 1-bits):")
print(f"  {'':>8s}  ", end='')
for c in range(-3, 4):
    tag = 'JOIN' if c == 0 else f'{c:+d}'
    print(f'{tag:>6s}', end='')
print()

for n, stitch in zip(MONOIDS, stitches):
    print(f"  n={n:<5d}  ", end='')
    for c in range(-3, 4):
        col = HALF_WINDOW + c
        vals = stitch[:, col]
        valid = vals[~np.isnan(vals)]
        if len(valid) > 0:
            print(f'{np.mean(valid):6.3f}', end='')
        else:
            print(f'{"---":>6s}', end='')
    print()
