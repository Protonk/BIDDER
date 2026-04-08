"""
Recovery curves -- how fast does a walk through the n-prime table
recover the row labels?

Two panels for the contiguous row list n_k = k + 1, k = 1..N (so the
table has rows for n = 2, 3, ..., N+1).

Left:  the N x N table with the rank-1 region shaded, and three
       walks (main diagonal, row-by-row, Cantor antidiagonal) drawn
       as polylines up to the step at which each first recovers all
       N rows.

Right: the recovery curves -- number of row labels reconstructable
       as a function of enumeration step -- for each walk.

The story: the diagonal walk's slope matches the rank-1 region's
slope (the lower triangle in the contiguous case), so it stays inside
the region and recovers one row per step. The other walks have to
traverse cells outside the region (or in other rows) before reaching
each new row, so their recovery rates are slower. Cantor recovers
row k at step k(k+1)/2 (quadratic in k); row-by-row at step
(k - 1) * N + 1 (linear in k with giant slope N).

Run with `sage recovery_curves.py`.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

N = 20
ROWS = [k + 1 for k in range(1, N + 1)]  # n_k = k + 1


# --- The n-prime table (closed form plus brute-force assertion). ---

def j_index(n, k_prime):
    """k'-th positive integer not divisible by n."""
    return k_prime + (k_prime - 1) // (n - 1)


def n_prime_value(n, k_prime):
    return n * j_index(n, k_prime)


def brute_n_primes(n, count):
    out, j = [], 0
    while len(out) < count:
        j += 1
        if j % n != 0:
            out.append(j * n)
    return out


for n in ROWS:
    expected = brute_n_primes(n, N)
    actual = [n_prime_value(n, k + 1) for k in range(N)]
    assert expected == actual, "formula mismatch at n=%d" % n


# --- The rank-1 region. ---
# Cell (k, k') is in the rank-1 region of row k iff k' <= n_k - 1.
# For contiguous rows n_k = k + 1, this is k' <= k -- the closed
# lower triangle of the table.

def is_rank1(k, k_prime):
    n_k = ROWS[k - 1]
    return k_prime <= n_k - 1


# --- The three walks. ---
# Each walk is a list of (k, k') 1-indexed cells in enumeration order.

def diagonal_walk():
    return [(k, k) for k in range(1, N + 1)]


def row_by_row_walk():
    return [(k, kp) for k in range(1, N + 1) for kp in range(1, N + 1)]


def cantor_walk():
    """Cantor antidiagonal walk. Antidiagonal d (where d = k + k',
    so d ranges from 2 to 2N) is visited in order of increasing k.
    """
    out = []
    for d in range(2, 2 * N + 1):
        k_min = max(1, d - N)
        k_max = min(N, d - 1)
        for k in range(k_min, k_max + 1):
            out.append((k, d - k))
    return out


# --- Recovery curves. ---

def recovery_curve(walk):
    """At each step of the walk, how many distinct rows have been
    recovered? A row is recovered the first time the walk visits a
    rank-1 cell in that row.
    """
    seen = set()
    counts = []
    for (k, kp) in walk:
        if k not in seen and is_rank1(k, kp):
            seen.add(k)
        counts.append(len(seen))
    return counts


diag = diagonal_walk()
rbr = row_by_row_walk()
cant = cantor_walk()
rec_diag = recovery_curve(diag)
rec_rbr = recovery_curve(rbr)
rec_cant = recovery_curve(cant)

# Closed-form sanity checks: the recovery position of row k under
# each walk.
assert rec_diag[-1] == N and rec_rbr[-1] == N and rec_cant[-1] == N
for k in range(1, N + 1):
    # Diagonal recovers row k at step k.
    assert rec_diag[k - 1] == k
    # Row-by-row recovers row k at step (k-1) * N + 1.
    assert rec_rbr[(k - 1) * N] == k
    if k > 1:
        assert rec_rbr[(k - 1) * N - 1] == k - 1
    # Cantor recovers row k at step k(k+1)/2.
    assert rec_cant[k * (k + 1) // 2 - 1] == k
    if k > 1:
        assert rec_cant[k * (k + 1) // 2 - 2] == k - 1


# Recovery completion steps.
end_diag = N                          # 20
end_cant = N * (N + 1) // 2           # 210
end_rbr = (N - 1) * N + 1             # 381


# --- Render. ---

fig, (ax_grid, ax_rate) = plt.subplots(
    1, 2, figsize=(15, 7),
    gridspec_kw={"width_ratios": [1, 1.15]},
)


# === Left panel: grid + walks. ===

# Shade the rank-1 region (closed lower triangle for contiguous rows).
triangle = Polygon(
    [(0.5, 0.5), (0.5, N + 0.5), (N + 0.5, N + 0.5)],
    closed=True, facecolor="#dde8f0", edgecolor="none", zorder=1,
    label="rank-1 region",
)
ax_grid.add_patch(triangle)

# Faint cell grid.
for x in np.arange(0.5, N + 1.5, 1):
    ax_grid.axvline(x, color="#e8e8e8", linewidth=0.3, zorder=0)
    ax_grid.axhline(x, color="#e8e8e8", linewidth=0.3, zorder=0)

# Build polyline coordinates with NaN breaks so matplotlib stops
# drawing between disconnected segments.

# Row-by-row truncated at recovery completion (step 381 = (N-1)*N + 1).
# This covers all of rows 1..N-1 plus the first cell (N, 1) of row N.
xs_rbr, ys_rbr = [], []
for k in range(1, N):
    for kp in range(1, N + 1):
        xs_rbr.append(kp)
        ys_rbr.append(k)
    xs_rbr.append(np.nan)
    ys_rbr.append(np.nan)

# Cantor truncated at recovery completion (step 210 = N(N+1)/2).
# This covers antidiagonals d = 2 through d = N + 1.
xs_cant, ys_cant = [], []
for d in range(2, N + 2):
    for k in range(1, d):
        xs_cant.append(d - k)
        ys_cant.append(k)
    xs_cant.append(np.nan)
    ys_cant.append(np.nan)

# Main diagonal: just the diagonal cells.
xs_diag = list(range(1, N + 1))
ys_diag = list(range(1, N + 1))


ax_grid.plot(xs_rbr, ys_rbr, color="#7a4bb8", linewidth=1.4, alpha=0.55,
             label="row-by-row  (381 steps)", zorder=2)
# Mark the isolated cell (N, 1) where row-by-row finally recovers row N.
ax_grid.scatter([1], [N], s=55, facecolors="#7a4bb8",
                edgecolors="white", linewidths=0.6, zorder=2)

ax_grid.plot(xs_cant, ys_cant, color="#d24b4b", linewidth=1.4, alpha=0.7,
             label="Cantor antidiagonal  (210 steps)", zorder=3)

ax_grid.plot(xs_diag, ys_diag, color="#000000", linewidth=2.4, alpha=1.0,
             label="main diagonal  (20 steps)", zorder=4)

# Recovery cells: where each walk first recovers each row.
# Diagonal recovers at (k, k); row-by-row and Cantor both recover at
# (k, 1) (just at different steps -- that difference is the right
# panel's job).
ax_grid.scatter(list(range(1, N + 1)), list(range(1, N + 1)),
                s=46, facecolors="black", edgecolors="white",
                linewidths=0.7, zorder=5)
ax_grid.scatter([1] * N, list(range(1, N + 1)),
                s=46, facecolors="white", edgecolors="black",
                linewidths=0.9, zorder=6)

ax_grid.set_xlim(0.4, N + 0.6)
ax_grid.set_ylim(N + 0.6, 0.4)  # row 1 at top
ax_grid.set_xticks(range(1, N + 1, 2))
ax_grid.set_yticks(range(1, N + 1, 2))
ax_grid.set_xlabel("column k'")
ax_grid.set_ylabel("row k")
ax_grid.set_title("Walks through the n-prime table  ·  $n_k = k + 1$,  $N = 20$")
ax_grid.legend(loc="lower right", fontsize=8.5, framealpha=0.95)
ax_grid.set_aspect("equal")


# === Right panel: recovery curves. ===

steps_rbr = list(range(1, end_rbr + 1))
y_rbr = rec_rbr[:end_rbr]
steps_cant = list(range(1, end_cant + 1))
y_cant = rec_cant[:end_cant]
steps_diag = list(range(1, end_diag + 1))
y_diag = rec_diag[:end_diag]

ax_rate.step(steps_rbr, y_rbr, where="post", color="#7a4bb8",
             linewidth=1.6, label="row-by-row", alpha=0.95)
ax_rate.step(steps_cant, y_cant, where="post", color="#d24b4b",
             linewidth=1.6, label="Cantor antidiagonal", alpha=0.95)
ax_rate.step(steps_diag, y_diag, where="post", color="#000000",
             linewidth=2.4, label="main diagonal")

# All-rows-recovered reference.
ax_rate.axhline(N, color="#888888", linewidth=0.8, linestyle="--", alpha=0.6)
ax_rate.text(end_rbr * 0.5, N + 0.3, "all rows recovered",
             fontsize=8.5, color="#888888", ha="center")

ax_rate.set_xlim(0, end_rbr + 30)
ax_rate.set_ylim(0, N + 1.6)
ax_rate.set_xlabel("enumeration step")
ax_rate.set_ylabel("rows recovered")
ax_rate.set_title("Recovery curves")
ax_rate.legend(loc="lower right", fontsize=9, framealpha=0.95)
ax_rate.grid(True, alpha=0.25)

# Annotate completion points.
ax_rate.annotate(
    "diag: %d" % end_diag, xy=(end_diag, N),
    xytext=(end_diag + 30, N - 3.5), fontsize=8.5, color="#000000",
    arrowprops=dict(arrowstyle="-", color="#000000", linewidth=0.7),
)
ax_rate.annotate(
    "Cantor: %d" % end_cant, xy=(end_cant, N),
    xytext=(end_cant + 30, N - 5.5), fontsize=8.5, color="#d24b4b",
    arrowprops=dict(arrowstyle="-", color="#d24b4b", linewidth=0.7),
)
ax_rate.annotate(
    "row-by-row: %d" % end_rbr, xy=(end_rbr, N),
    xytext=(end_rbr - 130, N - 7.5), fontsize=8.5, color="#7a4bb8",
    arrowprops=dict(arrowstyle="-", color="#7a4bb8", linewidth=0.7),
)

plt.tight_layout()
plt.savefig("recovery_curves.png", dpi=180, bbox_inches="tight")
print("wrote recovery_curves.png")
