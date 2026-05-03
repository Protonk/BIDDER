"""
Substrate phase diagram at b = 10.

For each (n, d) ∈ [2, 200] × [1, 7], classify the cell by which
clause of the substrate theorem is load-bearing:

    empty:    B_{b,d} contains no n-prime atoms.
    smooth:   n² | b^(d-1), clause 2 (exact uniformity).
    family_e: n ∈ [b^(d-1), ⌊(b^d-1)/(b-1)⌋], clause 3
              (one per leading digit).
    lucky:    spread = 0 with neither clause applying.
    spread_1: max - min count = 1.
    spread_2: max - min count = 2.

Per-cell count is computed in O(b) via leading-digit strips:
within each strip [k·b^(d-1), (k+1)·b^(d-1) − 1], multiples of n
minus multiples of n² gives the count.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap, BoundaryNorm

B = 10
N_VALUES = list(range(2, 201))
D_VALUES = list(range(1, 8))


def per_digit_counts(b, n, d):
    """Count n-prime atoms in each leading-digit strip of B_{b, d}."""
    counts = []
    n_sq = n * n
    base = b**(d - 1)
    for k in range(1, b):
        lo = k * base
        hi = (k + 1) * base - 1
        c_n = hi // n - (lo - 1) // n
        c_nsq = hi // n_sq - (lo - 1) // n_sq
        counts.append(c_n - c_nsq)
    return counts


def classify(b, n, d):
    counts = per_digit_counts(b, n, d)
    total = sum(counts)
    if total == 0:
        return 'empty'
    if (b**(d - 1)) % (n * n) == 0:
        return 'smooth'
    if d >= 2 and b**(d - 1) <= n <= (b**d - 1) // (b - 1):
        return 'family_e'
    spread = max(counts) - min(counts)
    if spread == 0:
        return 'lucky'
    if spread == 1:
        return 'spread_1'
    if spread == 2:
        return 'spread_2'
    # Beyond the theorem's bound — would be a bug.
    return f'spread_{spread}_BUG'


CLASSES = ['empty', 'smooth', 'family_e', 'lucky',
           'spread_1', 'spread_2']
class_to_idx = {c: i for i, c in enumerate(CLASSES)}

# Build matrix.
M = np.zeros((len(D_VALUES), len(N_VALUES)), dtype=int)
class_counts = {c: 0 for c in CLASSES}
lucky_cells = []
spread_2_cells = []
for i, d in enumerate(D_VALUES):
    for j, n in enumerate(N_VALUES):
        cls = classify(B, n, d)
        if 'BUG' in cls:
            raise RuntimeError(f"Theorem violation at (n={n}, d={d}): {cls}")
        M[i, j] = class_to_idx[cls]
        class_counts[cls] += 1
        if cls == 'lucky':
            lucky_cells.append((n, d))
        if cls == 'spread_2':
            spread_2_cells.append((n, d))

print(f"Cells classified: {len(D_VALUES) * len(N_VALUES)}")
for c in CLASSES:
    print(f"  {c:<10} {class_counts[c]:>5}")
print()

# Sample a few lucky cells for inspection.
print(f"Total lucky cells: {len(lucky_cells)}")
if lucky_cells:
    print("First 25 lucky cells (n, d) and their per-digit count vectors:")
    for n, d in lucky_cells[:25]:
        cv = per_digit_counts(B, n, d)
        print(f"  n={n:>3d}, d={d}: {cv}")
print()
print(f"Total spread_2 cells: {len(spread_2_cells)}")
if spread_2_cells:
    print("First 15 spread_2 cells:")
    for n, d in spread_2_cells[:15]:
        cv = per_digit_counts(B, n, d)
        print(f"  n={n:>3d}, d={d}: {cv}")

# --- Render ---
colors = {
    'empty':    '#1d1d1f',  # near-black
    'smooth':   '#3da9c4',  # cyan
    'family_e': '#a8e22d',  # green
    'lucky':    '#f5e2a3',  # pale gold
    'spread_1': '#ffa642',  # orange
    'spread_2': '#cc66ff',  # purple
}
cmap_colors = [colors[c] for c in CLASSES]
cmap = ListedColormap(cmap_colors)
norm = BoundaryNorm(np.arange(len(CLASSES) + 1) - 0.5, cmap.N)

fig, ax = plt.subplots(figsize=(20, 6.5))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

extent = (N_VALUES[0] - 0.5, N_VALUES[-1] + 0.5,
          D_VALUES[0] - 0.5, D_VALUES[-1] + 0.5)
im = ax.imshow(M, aspect='auto', cmap=cmap, norm=norm,
               extent=extent, origin='lower',
               interpolation='nearest')

# Tick marks.
ax.set_yticks(D_VALUES)
ax.set_xticks([2, 3, 5, 7, 10, 20, 50, 100, 150, 200])
ax.set_xlabel('n', color='white', fontsize=12)
ax.set_ylabel('d', color='white', fontsize=12)
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('#333')

# Custom legend with cell counts.
legend_elements = [
    mpatches.Patch(color=colors[c],
                    label=f'{c}  ({class_counts[c]})')
    for c in CLASSES
]
ax.legend(handles=legend_elements, loc='upper left',
          bbox_to_anchor=(1.005, 1.0),
          facecolor='#1a1a1a', edgecolor='#333',
          labelcolor='white', fontsize=10,
          title='class (cell count)', title_fontsize=10)
ax.legend_.get_title().set_color('#bbb')

ax.set_title(
    f'Substrate phase diagram — b = {B}, '
    f'n ∈ [{N_VALUES[0]}, {N_VALUES[-1]}], '
    f'd ∈ [{D_VALUES[0]}, {D_VALUES[-1]}]',
    color='white', fontsize=13)

plt.tight_layout()
plt.savefig('phase_diagram.png', dpi=170,
            facecolor='#0a0a0a', bbox_inches='tight')
print()
print("-> phase_diagram.png")
