"""
Plot 8: Complementary curves.

For each pair of ascending row maps, compute their diagonal images
below x = 10000 and measure how complementarily they cover the
composites. Sweep 8 candidate row maps (28 unique pairs) and rank
by |I_R1 sym_diff I_R2| -- the count of composites caught by exactly
one of the pair.

Renders a 2-panel figure: heatmap of disjoint rates (left) and
Pareto scatter of joint coverage vs disjoint rate (right). Saves
pairs.npz with the full leaderboard data.

Run with `sage complementary_curves.py`.
"""

import numpy as np
import matplotlib.pyplot as plt


X = 10000  # composite bound


# --- Primes (for prime-flavored row maps and the primality oracle) ---

def small_primes(limit):
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False
    return [i for i in range(limit + 1) if sieve[i]]


PRIMES = small_primes(1000)  # plenty for k up to ~150


def p_k(k):
    """k-th prime, 1-indexed."""
    return PRIMES[k - 1]


# Primality oracle for filtering images. Image values <= X.
PRIME_SET = set(small_primes(X))


def is_composite(n):
    return n >= 4 and n not in PRIME_SET


# --- Row map definitions ---

ROW_MAPS = [
    ("pronic",  lambda k: k + 1),
    ("shift_2", lambda k: k + 2),
    ("shift_3", lambda k: k + 3),
    ("odd",     lambda k: 2 * k + 1),
    ("odd_3",   lambda k: 2 * k + 3),
    ("prime",   lambda k: p_k(k)),
    ("square",  lambda k: k * k + 1),
    ("prime_n", lambda k: p_k(k + 1)),
]

NAMES = [name for (name, _) in ROW_MAPS]
N_MAPS = len(ROW_MAPS)


# --- Image computation ---

def compute_image(R, x):
    """Set of composite k * R(k) values up to x. Each row map is
    monotonic in k, so we break as soon as one value exceeds x."""
    image = set()
    k = 1
    while True:
        n_k = R(k)
        # Sanity: row map must be in the lattice (n_k > k) and
        # ascending (n_k >= 2 trivially since n_k > k >= 1).
        assert n_k > k, "row map not in lattice at k=%d" % k
        v = k * n_k
        if v > x:
            break
        if is_composite(v):
            image.add(v)
        k += 1
    return image


images = {name: compute_image(R, X) for (name, R) in ROW_MAPS}

print("Row map images (composites only, x = %d):" % X)
for name in NAMES:
    print("  %-9s : |I| = %4d" % (name, len(images[name])))
print()


# --- Pair statistics ---

pair_data = []
for i in range(N_MAPS):
    for j in range(i + 1, N_MAPS):
        I_i = images[NAMES[i]]
        I_j = images[NAMES[j]]
        union = I_i | I_j
        inter = I_i & I_j
        sym = I_i ^ I_j
        # Sanity from inclusion-exclusion.
        assert len(union) == len(I_i) + len(I_j) - len(inter)
        assert len(sym) == len(union) - len(inter)
        rate = len(sym) / len(union) if union else 0.0
        pair_data.append({
            "i": i,
            "j": j,
            "name_i": NAMES[i],
            "name_j": NAMES[j],
            "size_i": len(I_i),
            "size_j": len(I_j),
            "union": len(union),
            "inter": len(inter),
            "sym": len(sym),
            "rate": rate,
        })

# Rank by |symmetric difference| (raw count of complementary catches).
ranked = sorted(pair_data, key=lambda d: -d["sym"])


# --- Print leaderboard ---

print("Leaderboard (ranked by |symmetric difference|):")
print("  rank  pair                          |I1|  |I2|  union  inter   sym  rate")
print("  ----  ----------------------------  ----  ----  -----  -----  ----  -----")
for rank, d in enumerate(ranked, 1):
    pair_str = "%s x %s" % (d["name_i"], d["name_j"])
    print("  %4d  %-28s  %4d  %4d  %5d  %5d  %4d  %.3f"
          % (rank, pair_str, d["size_i"], d["size_j"],
             d["union"], d["inter"], d["sym"], d["rate"]))
print()


# --- Prediction check: where does (pronic, prime) land? ---

pronic_prime = next(
    d for d in pair_data
    if {d["name_i"], d["name_j"]} == {"pronic", "prime"}
)
pp_rank = ranked.index(pronic_prime) + 1
print("Prediction check (from plot 9):")
print("  (pronic, prime) is at rank %d / %d" % (pp_rank, len(ranked)))
print("  |I_pronic|=%d, |I_prime|=%d, union=%d, intersection=%d, sym=%d, rate=%.3f"
      % (pronic_prime["size_i"], pronic_prime["size_j"],
         pronic_prime["union"], pronic_prime["inter"],
         pronic_prime["sym"], pronic_prime["rate"]))
print()


# --- Best pair, by various metrics ---

best_sym = ranked[0]
best_rate = max(pair_data, key=lambda d: d["rate"])
best_union = max(pair_data, key=lambda d: d["union"])

print("Best pair by each metric:")
print("  by |sym|:  %s x %s   (sym=%d, rate=%.3f)"
      % (best_sym["name_i"], best_sym["name_j"],
         best_sym["sym"], best_sym["rate"]))
print("  by rate:   %s x %s   (sym=%d, rate=%.3f)"
      % (best_rate["name_i"], best_rate["name_j"],
         best_rate["sym"], best_rate["rate"]))
print("  by union:  %s x %s   (sym=%d, rate=%.3f)"
      % (best_union["name_i"], best_union["name_j"],
         best_union["sym"], best_union["rate"]))
print()


# --- Pareto frontier in (coverage, disjoint_rate) space ---

def is_dominated(p, others):
    for q in others:
        if q is p:
            continue
        if (q["union"] >= p["union"] and q["rate"] >= p["rate"] and
                (q["union"] > p["union"] or q["rate"] > p["rate"])):
            return True
    return False


pareto = [p for p in pair_data if not is_dominated(p, pair_data)]
pareto_sorted = sorted(pareto, key=lambda d: d["union"])

print("Pareto frontier (non-dominated in coverage / disjoint rate):")
for p in pareto_sorted:
    print("  %s x %s   (union=%d, rate=%.3f)"
          % (p["name_i"], p["name_j"], p["union"], p["rate"]))
print()


# --- Save substrate ---

i_arr     = np.array([d["i"]     for d in pair_data], dtype=int)
j_arr     = np.array([d["j"]     for d in pair_data], dtype=int)
union_arr = np.array([d["union"] for d in pair_data], dtype=int)
inter_arr = np.array([d["inter"] for d in pair_data], dtype=int)
sym_arr   = np.array([d["sym"]   for d in pair_data], dtype=int)
rate_arr  = np.array([d["rate"]  for d in pair_data], dtype=float)
sizes_arr = np.array([len(images[name]) for name in NAMES], dtype=int)

np.savez_compressed(
    "pairs.npz",
    bound=np.array([X]),
    names=np.array(NAMES),
    individual=sizes_arr,
    i=i_arr, j=j_arr,
    union=union_arr, inter=inter_arr, sym=sym_arr, rate=rate_arr,
)
print("wrote pairs.npz")


# --- Render: 2-panel figure ---

fig, (ax_heat, ax_scatter) = plt.subplots(
    1, 2, figsize=(15, 6.5),
    gridspec_kw={"width_ratios": [1, 1.15]},
)


# === Left panel: heatmap of joint coverage |I_1 ∪ I_2| ===
#
# We had originally rendered disjoint rate here, but rate is essentially
# uniform (all pairs in [0.974, 1.000] at this lattice scale -- see
# the README). Joint coverage has the actual dynamic range: 64 to 196.

heat = np.full((N_MAPS, N_MAPS), np.nan)
for d in pair_data:
    heat[d["i"], d["j"]] = d["union"]
    heat[d["j"], d["i"]] = d["union"]

vmin = min(d["union"] for d in pair_data)
vmax = max(d["union"] for d in pair_data)

im = ax_heat.imshow(heat, cmap="viridis", vmin=vmin, vmax=vmax, aspect="equal")
ax_heat.set_xticks(range(N_MAPS))
ax_heat.set_yticks(range(N_MAPS))
ax_heat.set_xticklabels(NAMES, rotation=45, ha="right", fontsize=9)
ax_heat.set_yticklabels(NAMES, fontsize=9)
ax_heat.set_title("joint coverage per pair  ·  $|I_1 \\cup I_2|$", fontsize=11)
cbar = plt.colorbar(im, ax=ax_heat, fraction=0.046, pad=0.04)
cbar.set_label("composites caught (union)")

# Annotate each cell with the union count so the heatmap doubles as
# a table.
for d in pair_data:
    for (r, c) in [(d["i"], d["j"]), (d["j"], d["i"])]:
        # Choose label color for contrast against the background.
        rel = (d["union"] - vmin) / (vmax - vmin) if vmax > vmin else 0.5
        text_color = "white" if rel < 0.55 else "black"
        ax_heat.text(c, r, "%d" % d["union"], ha="center", va="center",
                     fontsize=8, color=text_color)


# === Right panel: Pareto scatter ===

xs_all = [d["union"] for d in pair_data]
ys_all = [d["rate"]  for d in pair_data]
ax_scatter.scatter(xs_all, ys_all, s=72, c="#4b8fd2",
                   edgecolors="white", linewidths=0.6, zorder=3,
                   label="all pairs")

# Pareto frontier as a dashed connecting line.
pareto_xs = [p["union"] for p in pareto_sorted]
pareto_ys = [p["rate"]  for p in pareto_sorted]
ax_scatter.plot(pareto_xs, pareto_ys, color="#888", linewidth=1.0,
                linestyle="--", alpha=0.7, zorder=2,
                label="Pareto frontier")
ax_scatter.scatter(pareto_xs, pareto_ys, s=130,
                   facecolors="none", edgecolors="#888", linewidths=1.4,
                   zorder=4)

# Highlight the (pronic, prime) prediction.
ax_scatter.scatter([pronic_prime["union"]], [pronic_prime["rate"]],
                   s=240, facecolors="none", edgecolors="#d24b4b",
                   linewidths=2.4, zorder=5,
                   label="(pronic, prime) — predicted")

# Label the top 5 by symmetric difference.
for d in ranked[:5]:
    pair_str = "(%s, %s)" % (d["name_i"], d["name_j"])
    ax_scatter.annotate(
        pair_str, xy=(d["union"], d["rate"]),
        xytext=(8, 6), textcoords="offset points", fontsize=8.5,
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#888",
                  lw=0.5, alpha=0.92),
        zorder=6,
    )

ax_scatter.set_xlabel("$|I_1 \\cup I_2|$  (joint coverage)")
ax_scatter.set_ylabel("disjoint rate  $|I_1 \\triangle I_2| / |I_1 \\cup I_2|$")
ax_scatter.set_title("coverage vs disjointness  ·  top 5 labeled", fontsize=11)
ax_scatter.grid(True, alpha=0.25)
ax_scatter.set_ylim(0.7, 1.03)
ax_scatter.legend(loc="lower right", fontsize=8.5, framealpha=0.95)


fig.suptitle(
    "Complementary curves  ·  composites below %d  ·  %d row maps, %d pairs"
    % (X, N_MAPS, len(pair_data)),
    y=1.02, fontsize=12,
)

plt.tight_layout()
plt.savefig("complementary_curves.png", dpi=180, bbox_inches="tight")
print("wrote complementary_curves.png")
