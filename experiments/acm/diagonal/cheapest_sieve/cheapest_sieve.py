"""
Plot 9: cheapest sieve per target.

For each composite N in witnesses.npz, find the witness pair (k, n)
that minimizes each of three cost functions on the implied row map:

  cost_k     = k                  catch N at the earliest position
  cost_diag  = n - k              most balanced factorization
  cost_prime = |n - p_k|          closest to the prime row map

Render a 3-panel figure showing the cheapest-sieve winners over the
visible lattice (PLOT_BOUND = 100). Save winners.npz mapping each
composite up to DATA_BOUND = 1000 to its winner under each cost.
Compute the agreement rate -- fraction of composites where all three
costs pick the same winner -- and the pairwise agreement rates.

Run with `sage cheapest_sieve.py`.
"""

import numpy as np
import matplotlib.pyplot as plt

PLOT_BOUND = 100
WITNESSES_PATH = "../witness_density/witnesses.npz"


# --- Primes (for cost_prime) ---

def small_primes(limit):
    """Primes up to limit by sieve of Eratosthenes."""
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False
    return [i for i in range(limit + 1) if sieve[i]]


# Need p_k for k up to floor(sqrt(DATA_BOUND)) ~ 31. 200 gives plenty.
PRIMES = small_primes(200)


def p_k(k):
    """k-th prime, 1-indexed."""
    return PRIMES[k - 1]


# --- Load witnesses substrate ---

def load_witnesses(path):
    data = np.load(path)
    bound = int(data["bound"][0])
    min_k = int(data["min_k"][0])
    out = {}
    for key in data.files:
        if key.startswith("N_"):
            N = int(key[2:])
            out[N] = data[key]
    return out, bound, min_k


witnesses, DATA_BOUND, MIN_K = load_witnesses(WITNESSES_PATH)
print("loaded %d composites from %s (bound=%d, min_k=%d)"
      % (len(witnesses), WITNESSES_PATH, DATA_BOUND, MIN_K))


# --- Cost functions ---

def cost_k(k, n):
    return k


def cost_diag(k, n):
    return n - k


def cost_prime(k, n):
    return abs(n - p_k(k))


COSTS = [
    ("smallest k",     "cost_k",     cost_k,     "#d24b4b"),
    ("smallest n - k", "cost_diag",  cost_diag,  "#4b8fd2"),
    ("|n - p_k|",      "cost_prime", cost_prime, "#7a4bb8"),
]


def cheapest(pairs, cost_fn):
    """argmin over (k, n) witness pairs of the cost function."""
    return min(pairs, key=lambda p: cost_fn(int(p[0]), int(p[1])))


# --- Compute winners ---

winners = {key: {} for (_, key, _, _) in COSTS}
for N, ws in witnesses.items():
    pairs = [(int(p[0]), int(p[1])) for p in ws]
    for (_, key, fn, _) in COSTS:
        winners[key][N] = cheapest(pairs, fn)


# --- Sanity checks: each winner is in the witness list and is the
# argmin under its cost. ---
for N, ws in witnesses.items():
    pairs = [(int(p[0]), int(p[1])) for p in ws]

    w_k = winners["cost_k"][N]
    assert tuple(w_k) in pairs
    assert w_k[0] == min(p[0] for p in pairs)

    w_d = winners["cost_diag"][N]
    assert tuple(w_d) in pairs
    assert w_d[1] - w_d[0] == min(p[1] - p[0] for p in pairs)

    w_p = winners["cost_prime"][N]
    assert tuple(w_p) in pairs
    assert (abs(w_p[1] - p_k(w_p[0]))
            == min(abs(p[1] - p_k(p[0])) for p in pairs))


# --- Save substrate ---

all_Ns = sorted(witnesses.keys())
save_dict = {
    "data_bound": np.array([DATA_BOUND]),
    "min_k":      np.array([MIN_K]),
    "N":          np.array(all_Ns, dtype=int),
}
for (_, key, _, _) in COSTS:
    save_dict["%s_winners" % key] = np.array(
        [winners[key][N] for N in all_Ns], dtype=int
    )

np.savez_compressed("winners.npz", **save_dict)
print("wrote winners.npz with %d composites" % len(all_Ns))


# --- Agreement rates ---

agree_all = 0
for N in all_Ns:
    w = [winners[key][N] for (_, key, _, _) in COSTS]
    if w[0] == w[1] == w[2]:
        agree_all += 1
rate_all = agree_all / len(all_Ns)


def pairwise(key1, key2):
    agree = sum(1 for N in all_Ns if winners[key1][N] == winners[key2][N])
    return agree / len(all_Ns)


pair_kd = pairwise("cost_k",    "cost_diag")
pair_kp = pairwise("cost_k",    "cost_prime")
pair_dp = pairwise("cost_diag", "cost_prime")

print("")
print("Agreement rates over %d composites (k * n <= %d):" % (len(all_Ns), DATA_BOUND))
print("  all three agree:           %d / %d = %.4f" % (agree_all, len(all_Ns), rate_all))
print("  cost_k    + cost_diag:     %.4f" % pair_kd)
print("  cost_k    + cost_prime:    %.4f" % pair_kp)
print("  cost_diag + cost_prime:    %.4f" % pair_dp)
print("")


# --- Render the 3-panel figure ---

# Visible lattice: (k, n) with k * n <= PLOT_BOUND, k >= MIN_K, k < n.
k_max_vis = int(PLOT_BOUND ** 0.5) + 1
visible_lattice = []
for k in range(MIN_K, k_max_vis + 1):
    for n in range(k + 1, PLOT_BOUND // k + 1):
        if k * n <= PLOT_BOUND:
            visible_lattice.append((k, n))

vis_xs = [p[0] for p in visible_lattice]
vis_ys = [p[1] for p in visible_lattice]
y_max = max(vis_ys) + 4


fig, axes = plt.subplots(1, 3, figsize=(16, 6),
                         gridspec_kw={"wspace": 0.22})

for ax, (label, key, fn, color) in zip(axes, COSTS):
    # Faint gray for all visible lattice points.
    ax.scatter(vis_xs, vis_ys, s=22, c="#cccccc",
               edgecolors="none", alpha=0.55, zorder=1)

    # Bright color for winners under this cost.
    win_xs, win_ys = [], []
    for (k, n) in visible_lattice:
        N = k * n
        if N in winners[key] and tuple(winners[key][N]) == (k, n):
            win_xs.append(k)
            win_ys.append(n)

    ax.scatter(win_xs, win_ys, s=58, c=color,
               edgecolors="white", linewidths=0.6, zorder=3)

    ax.set_xlim(MIN_K - 0.5, k_max_vis + 0.5)
    ax.set_ylim(MIN_K, y_max)
    ax.set_xticks(range(MIN_K, k_max_vis + 1))
    ax.set_xlabel("k")
    if ax is axes[0]:
        ax.set_ylabel("n")
    ax.set_title("cheapest by  %s" % label, color=color, fontsize=11)
    ax.grid(True, alpha=0.2)

fig.suptitle(
    "Cheapest sieve per composite  ·  visible: k · n ≤ %d  ·  substrate: k · n ≤ %d"
    % (PLOT_BOUND, DATA_BOUND),
    y=1.02, fontsize=12,
)

plt.tight_layout()
plt.savefig("cheapest_sieve.png", dpi=180, bbox_inches="tight")
print("wrote cheapest_sieve.png")
