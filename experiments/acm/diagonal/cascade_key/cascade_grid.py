"""
Cascade key heatmap.

Renders the rank-1 patch structure of the n-prime table for a small
ascending row list. Each cell (row, k') is colored by the parity of
its rank-1 patch index, so patch boundaries appear as stripe
transitions. Diagonal cells -- the cells the abductive key decodes
-- are marked with circles.

The point of the picture: each row is a staircase of rank-1 patches
of width n_k - 1, the diagonal cell of row k always lives in the
first patch (because strict ascent gives k <= n_k - 1), and once the
first patch yields n_k by division by k, every later patch in that
row is computable from k' and n_k alone. One key per row, all locks.

Run with `sage cascade_grid.py`.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


# Strict-ascending row list and column window.
ROWS = [5, 7, 11, 13, 17, 19]
NCOLS = 60


def j_index(n, k_prime):
    """The k'-th positive integer not divisible by n.

    Equal to k' plus the number of multiples of n that have been
    skipped among the first k' admissible integers, which is the
    floor of (k' - 1) / (n - 1).
    """
    return k_prime + (k_prime - 1) // (n - 1)


def n_prime_value(n, k_prime):
    """The k'-th n-prime: j_{k'} * n."""
    return n * j_index(n, k_prime)


def patch_index(n, k_prime):
    """0-indexed rank-1 patch containing column k' of row n."""
    return (k_prime - 1) // (n - 1)


# Brute-force sanity check: build n-primes by sieving and compare to
# the closed-form value computed above. If the formula is off by one
# anywhere, this catches it before we render.
def brute_n_primes(n, count):
    out = []
    j = 0
    while len(out) < count:
        j += 1
        if j % n != 0:
            out.append(j * n)
    return out


for n in ROWS:
    expected = brute_n_primes(n, NCOLS)
    actual = [n_prime_value(n, k + 1) for k in range(NCOLS)]
    assert expected == actual, "formula mismatch at n=%d" % n


# Build the parity grid that drives the heatmap.
N_ROWS = len(ROWS)
patch_parity = np.zeros((N_ROWS, NCOLS), dtype=int)
for r, n in enumerate(ROWS):
    for c in range(NCOLS):
        patch_parity[r, c] = patch_index(n, c + 1) % 2


# Two alternating colors: muted blue for even patches, warm tan for
# odd. Two colors keeps the read "stripe stripe stripe" rather than
# turning the picture into a coding scheme.
cmap = ListedColormap(["#2c4e6f", "#e8b873"])

fig, ax = plt.subplots(figsize=(14, 4.5))
ax.imshow(patch_parity, cmap=cmap, aspect="auto", interpolation="nearest")

# Mark diagonal cells. Row index r corresponds to position k = r + 1
# in the ascending row list, so the diagonal cell of that row is at
# column index k - 1 = r.
for r in range(N_ROWS):
    ax.plot(
        r,
        r,
        marker="o",
        markersize=13,
        markerfacecolor="white",
        markeredgecolor="black",
        markeredgewidth=1.6,
        zorder=4,
    )

# Row labels and axes.
ax.set_yticks(range(N_ROWS))
ax.set_yticklabels(["n = %d" % n for n in ROWS])
ax.set_xlabel("column index k'")
ax.set_title(
    "Cascade key -- rank-1 patches of the n-prime table\n"
    "alternating stripes are patches of width n_k - 1; "
    "circles mark the diagonal cell of each row"
)

# X tick every 5 columns for readability.
ax.set_xticks(range(0, NCOLS, 5))
ax.set_xticklabels([str(c + 1) for c in range(0, NCOLS, 5)])

# Subtle white grid between cells so individual columns are visible.
ax.set_xticks(np.arange(-0.5, NCOLS, 1), minor=True)
ax.set_yticks(np.arange(-0.5, N_ROWS, 1), minor=True)
ax.grid(
    which="minor", color="white", linestyle="-", linewidth=0.25, alpha=0.35
)
ax.tick_params(which="minor", length=0)

plt.tight_layout()
plt.savefig("cascade_grid.png", dpi=180, bbox_inches="tight")
print("wrote cascade_grid.png")
