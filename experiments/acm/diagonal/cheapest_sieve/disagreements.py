"""
Disagreement analysis: what are the 220 composites where cost_diag
and cost_prime pick different winners?

Loads `winners.npz` from this folder and `witnesses.npz` from
`../witness_density/`. Classifies each disagreement as tie-affected
or structural, computes the k-gap distribution, compares witness
counts on agreements vs disagreements, and renders a single-panel
figure showing the disagreements as connecting lines in the
composite lattice.

Run with `sage disagreements.py`.
"""

import collections
import numpy as np
import matplotlib.pyplot as plt

PLOT_BOUND = 200
WITNESSES_PATH = "../witness_density/witnesses.npz"
WINNERS_PATH = "winners.npz"


# --- Primes (for cost_prime distance computation) ---

def small_primes(limit):
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False
    return [i for i in range(limit + 1) if sieve[i]]


PRIMES = small_primes(300)


def p_k(k):
    return PRIMES[k - 1]


def cost_prime_value(k, n):
    return abs(n - p_k(k))


# --- Load substrates ---

witnesses_data = np.load(WITNESSES_PATH)
DATA_BOUND = int(witnesses_data["bound"][0])
MIN_K = int(witnesses_data["min_k"][0])

witnesses = {}
for key in witnesses_data.files:
    if key.startswith("N_"):
        N = int(key[2:])
        witnesses[N] = [(int(p[0]), int(p[1])) for p in witnesses_data[key]]

winners_data = np.load(WINNERS_PATH)
N_arr = winners_data["N"]
diag_win = winners_data["cost_diag_winners"]
prime_win = winners_data["cost_prime_winners"]


# --- Identify and classify disagreements ---

disagreements = []   # (N, diag_pair, prime_pair, is_tied)
agreements = []      # N

for i, N_val in enumerate(N_arr):
    N = int(N_val)
    d = (int(diag_win[i][0]), int(diag_win[i][1]))
    p = (int(prime_win[i][0]), int(prime_win[i][1]))
    if d != p:
        # Tie-affected if there exists any witness other than the
        # prime winner with the same cost_prime distance.
        prime_min_dist = cost_prime_value(p[0], p[1])
        n_at_min = sum(
            1 for w in witnesses[N]
            if cost_prime_value(w[0], w[1]) == prime_min_dist
        )
        is_tied = n_at_min > 1
        disagreements.append((N, d, p, is_tied))
    else:
        agreements.append(N)

total = len(N_arr)
n_dis = len(disagreements)
n_tied = sum(1 for x in disagreements if x[3])
n_structural = n_dis - n_tied


print("Disagreement analysis")
print("=" * 60)
print("Total composites in substrate:        %4d" % total)
print("Disagreements (cost_diag != cost_prime): %3d  (%.2f%%)"
      % (n_dis, 100 * n_dis / total))
print("  Tie-affected:  %3d  (%.1f%% of disagreements)"
      % (n_tied, 100 * n_tied / n_dis))
print("  Structural:    %3d  (%.1f%% of disagreements)"
      % (n_structural, 100 * n_structural / n_dis))
print()


# --- k-gap distribution: diag_k - prime_k ---

k_gaps = [d[0] - p[0] for (_, d, p, _) in disagreements]
counter = collections.Counter(k_gaps)
print("k-gap (diag_k - prime_k) distribution:")
for gap in sorted(counter.keys()):
    bar = "#" * (counter[gap] // 2)
    sign = "+" if gap > 0 else " " if gap == 0 else "-"
    print("  gap = %s%d: %3d  %s" % (sign, abs(gap), counter[gap], bar))
print("  (positive gap = prime picks smaller k than diag)")
print()


# --- Witness count comparison ---

agree_counts = [len(witnesses[N]) for N in agreements]
dis_counts = [len(witnesses[N]) for (N, _, _, _) in disagreements]

print("Witness count statistics (testing 'disagreements concentrate on highly composite N'):")
print("  Agreements:    mean witnesses = %.2f, max = %d, count(witnesses=1) = %d"
      % (np.mean(agree_counts), max(agree_counts),
         sum(1 for c in agree_counts if c == 1)))
print("  Disagreements: mean witnesses = %.2f, max = %d, count(witnesses=1) = %d"
      % (np.mean(dis_counts), max(dis_counts),
         sum(1 for c in dis_counts if c == 1)))
print()


# --- Distribution by N range ---

ranges = [(4, 100), (101, 500), (501, 1000)]
print("Disagreement rate by N range:")
for lo, hi in ranges:
    in_range = [int(N) for N in N_arr if lo <= int(N) <= hi]
    dis_in_range = [d for d in disagreements if lo <= d[0] <= hi]
    rate = len(dis_in_range) / len(in_range) if in_range else 0
    print("  N in [%4d, %4d]:  %3d / %3d  = %5.1f%%"
          % (lo, hi, len(dis_in_range), len(in_range), 100 * rate))
print()


# --- Sample disagreements for manual inspection ---

print("First 10 structural disagreements (non-tied):")
print("  %4s   %-12s   %-12s   %-12s   %-12s"
      % ("N", "diag_winner", "prime_winner", "diag_dist", "prime_dist"))
shown = 0
for (N, d, p, is_tied) in disagreements:
    if is_tied:
        continue
    d_dist = cost_prime_value(d[0], d[1])
    p_dist = cost_prime_value(p[0], p[1])
    print("  %4d   (%2d, %3d)      (%2d, %3d)      %3d           %3d"
          % (N, d[0], d[1], p[0], p[1], d_dist, p_dist))
    shown += 1
    if shown >= 10:
        break
print()


# --- Render: single-panel disagreement plot ---

# Visible lattice up to PLOT_BOUND.
k_max_vis = int(PLOT_BOUND ** 0.5) + 1
visible_lattice = []
for k in range(MIN_K, k_max_vis + 1):
    for n in range(k + 1, PLOT_BOUND // k + 1):
        if k * n <= PLOT_BOUND:
            visible_lattice.append((k, n))

vis_xs = [p[0] for p in visible_lattice]
vis_ys = [p[1] for p in visible_lattice]
y_max = max(vis_ys) + 6


fig, ax = plt.subplots(figsize=(12, 8))

# Faint gray lattice background.
ax.scatter(vis_xs, vis_ys, s=18, c="#cccccc", edgecolors="none",
           alpha=0.5, zorder=1)

DIAG_COLOR = "#4b8fd2"
PRIME_COLOR = "#7a4bb8"

# Disagreements visible in the plot range.
visible_dis = [(N, d, p, t) for (N, d, p, t) in disagreements
               if N <= PLOT_BOUND]

# Draw structural disagreements first (darker), then tied (lighter).
for (N, d, p, is_tied) in visible_dis:
    if is_tied:
        line_color = "#aaaaaa"
        line_alpha = 0.5
        line_width = 0.9
    else:
        line_color = "#333333"
        line_alpha = 0.75
        line_width = 1.3
    ax.plot([d[0], p[0]], [d[1], p[1]],
            color=line_color, linewidth=line_width, alpha=line_alpha,
            zorder=2)

# Endpoints: cost_diag winners and cost_prime winners. Plot all
# diag winners then all prime winners so the legend is clean.
diag_xs = [d[0] for (_, d, _, _) in visible_dis]
diag_ys = [d[1] for (_, d, _, _) in visible_dis]
ax.scatter(diag_xs, diag_ys, s=70, c=DIAG_COLOR,
           edgecolors="white", linewidths=0.7, zorder=3,
           label="cost_diag winner")

prime_xs = [p[0] for (_, _, p, _) in visible_dis]
prime_ys = [p[1] for (_, _, p, _) in visible_dis]
ax.scatter(prime_xs, prime_ys, s=70, c=PRIME_COLOR,
           edgecolors="white", linewidths=0.7, zorder=4,
           label="cost_prime winner")

ax.set_xlim(MIN_K - 0.5, k_max_vis + 0.5)
ax.set_ylim(MIN_K, y_max)
ax.set_xticks(range(MIN_K, k_max_vis + 1))
ax.set_xlabel("k")
ax.set_ylabel("n")
ax.set_title(
    "Disagreements: cost_diag vs cost_prime  ·  k · n ≤ %d  "
    "(%d visible of %d total)"
    % (PLOT_BOUND, len(visible_dis), n_dis)
)
ax.legend(loc="upper right", fontsize=9, framealpha=0.95)
ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig("disagreements.png", dpi=180, bbox_inches="tight")
print("wrote disagreements.png")
