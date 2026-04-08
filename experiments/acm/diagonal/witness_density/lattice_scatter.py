"""
Composite lattice -- witness pairs.

Renders the lattice {(k, n) : 1 <= k < n, k*n <= PLOT_BOUND} as a
scatter, where each point (k, n) is a witness pair for the integer
k*n. Color encodes the target value k*n. Three row maps and one
highly-composite hyperbola are overlaid to make "row map = curve
through the lattice" visible.

Also writes witnesses.npz: a dict mapping each composite N from 4 to
DATA_BOUND to its sorted list of witness pairs (k, N/k) with k | N
and k < sqrt(N). This file is the substrate for plots 6, 8, and 9.

Run with `sage lattice_scatter.py`.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm


PLOT_BOUND = 100      # max value k*n shown in the scatter
DATA_BOUND = 1000     # max value k*n in witnesses.npz
HIGHLIGHT_N = 60      # composite whose hyperbola is highlighted
MIN_K = 2             # exclude k=1 (the trivial row map)


def divisors(n):
    """All positive divisors of n in ascending order."""
    out = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            out.append(i)
            if i != n // i:
                out.append(n // i)
        i += 1
    return sorted(out)


def witnesses(N, min_k=MIN_K):
    """Witness pairs (k, N/k) with k | N, min_k <= k, and k < sqrt(N).

    With min_k = 2 the trivial row map (1, N) at position 1 is
    excluded, so primes and squares of primes have no witnesses.
    """
    out = []
    for k in divisors(N):
        if k >= min_k and k * k < N:
            out.append((k, N // k))
    return out


def is_perfect_square(N):
    r = int(round(N ** 0.5))
    return r * r == N


# --- Sanity check the witness count formula. ---
# Excluding k = 1 removes exactly one witness from the full count
# (since 1 always divides N and 1 < sqrt(N) for N >= 2). The full
# count is floor(d(N)/2) for non-squares and (d(N) - 1)/2 for
# squares; subtract 1, clamp at zero.
for N in range(2, PLOT_BOUND + 1):
    w = witnesses(N)
    d = len(divisors(N))
    full = (d - 1) // 2 if is_perfect_square(N) else d // 2
    expected = max(0, full - 1)
    assert len(w) == expected, "witness count mismatch at N=%d" % N


# --- Build the scatter data: lattice up to PLOT_BOUND with k >= 2. ---
xs, ys, cs = [], [], []
for N in range(4, PLOT_BOUND + 1):
    for (k, n) in witnesses(N):
        xs.append(k)
        ys.append(n)
        cs.append(N)

xs = np.array(xs)
ys = np.array(ys)
cs = np.array(cs)


# --- Build the substrate file: composites only, up to DATA_BOUND. ---
# Plots 6, 8, and 9 want per-composite witness lists with k >= 2.
# Composites with no non-trivial witness (primes and squares of
# primes) are omitted.
witness_dict = {}
for N in range(4, DATA_BOUND + 1):
    w = witnesses(N)
    if len(w) > 0:
        witness_dict[N] = np.array(w, dtype=int)

np.savez_compressed(
    "witnesses.npz",
    bound=np.array([DATA_BOUND]),
    min_k=np.array([MIN_K]),
    **{"N_%d" % N: arr for N, arr in witness_dict.items()},
)
print("wrote witnesses.npz with %d composites up to %d (k >= %d)"
      % (len(witness_dict), DATA_BOUND, MIN_K))


# --- Render the scatter. ---
fig, ax = plt.subplots(figsize=(11, 7.5))

k_max = int(np.sqrt(PLOT_BOUND)) + 1  # 11 for PLOT_BOUND = 100

# Discrete bins for the color scale: 5 ascending bands, with the
# lower region split more finely so the dense lower-left of the
# lattice carries more gradation.
BINS = [6, 12, 20, 35, 60, 100]
cmap = plt.get_cmap("viridis", len(BINS) - 1)
norm = BoundaryNorm(BINS, cmap.N)

# Scatter colored by binned k * n.
sc = ax.scatter(xs, ys, c=cs, cmap=cmap, norm=norm,
                s=42, edgecolors="white", linewidths=0.4,
                alpha=0.92, zorder=2)
cbar = fig.colorbar(sc, ax=ax, pad=0.02, ticks=BINS, spacing="proportional")
cbar.set_label("k · n  (target, binned)")

# Row-map curves over the visible k range.
k_curve = np.arange(MIN_K, k_max + 1)

ax.plot(k_curve, k_curve + 1, color="#d24b4b", linewidth=2.0,
        label="n = k + 1  (pronic)", zorder=3)

ax.plot(k_curve, 2 * k_curve + 1, color="#4b8fd2", linewidth=2.0,
        label="n = 2k + 1", zorder=3)


def small_primes(limit):
    """Primes up to limit by sieve of Eratosthenes."""
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False
    return [i for i in range(limit + 1) if sieve[i]]


primes = small_primes(50)
prime_curve = primes[MIN_K - 1 : MIN_K - 1 + len(k_curve)]
ax.plot(k_curve, prime_curve, color="#7a4bb8", linewidth=2.0,
        label="n = p_k  (k-th prime)", zorder=3)

# Highlight the hyperbola k * n = HIGHLIGHT_N. Extend past sqrt(N)
# into the excluded region (k >= n) so the curve's full shape is
# visible -- the "other half" of the divisor pairs lives there.
hyp_k = np.linspace(MIN_K, 9, 200)
hyp_n = HIGHLIGHT_N / hyp_k
ax.plot(hyp_k, hyp_n, color="#000000", linewidth=1.8, alpha=0.85,
        linestyle=":", label="k · n = %d" % HIGHLIGHT_N, zorder=4)

# Mark integer witnesses on the highlighted hyperbola with bold
# circles and (k, n) annotations.
hl = witnesses(HIGHLIGHT_N)
hl_xs = [k for k, _ in hl]
hl_ys = [n for _, n in hl]
ax.scatter(hl_xs, hl_ys, s=190, facecolors="white",
           edgecolors="#000000", linewidths=2.2, zorder=6)
for (k_, n_) in hl:
    ax.annotate("(%d, %d)" % (k_, n_), xy=(k_, n_),
                xytext=(9, 7), textcoords="offset points",
                fontsize=9, color="#000000",
                bbox=dict(boxstyle="round,pad=0.2",
                          fc="white", ec="#000000", lw=0.6, alpha=0.9),
                zorder=7)

# Find the y range from the actual data.
y_max = int(ys.max()) + 4
ax.set_xlim(MIN_K - 0.5, k_max + 0.5)
ax.set_ylim(MIN_K, y_max)
ax.set_xlabel("k  (position)")
ax.set_ylabel("n  (row label)")
ax.set_title("Composite lattice  ·  2 ≤ k < n,  k · n ≤ %d" % PLOT_BOUND)
ax.legend(loc="upper right", fontsize=9, framealpha=0.95)
ax.set_xticks(range(MIN_K, k_max + 1))
ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig("lattice_scatter.png", dpi=180, bbox_inches="tight")
print("wrote lattice_scatter.png")
