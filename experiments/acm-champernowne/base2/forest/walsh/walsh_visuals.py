"""
walsh_visuals.py — post-hoc visualizations for the corrected Walsh result

Builds four plots from the saved spectra and the upgrade table:

  plots/robustness/
    1. walsh_survival_cascade.png  — 44 cells × 5 stages, green/red survival
    2. walsh_robust_heatmap.png    — 44 cells × 31 monoids, P[s] heatmap
  plots/interpretation/
    3. walsh_brightness_vs_v2.png  — scatter of mean P[s] vs corr with v_2(n)
    4. walsh_tier1_core.png        — 9 tier-1 cells × 31 monoids

These are the visuals that match the corrected story (entry-order shuffle
destroys all 44 robust cells; the brightest cells are not the v_2 cells).
The earlier plots in this folder (walsh_orders, walsh_high_order) were
built from bucket-averaged views that hid the headline.
"""

import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, TwoSlopeNorm


_here = os.path.dirname(os.path.abspath(__file__))
_robustness_dir = os.path.join(_here, "plots", "robustness")
_interpretation_dir = os.path.join(_here, "plots", "interpretation")
os.makedirs(_robustness_dir, exist_ok=True)
os.makedirs(_interpretation_dir, exist_ok=True)


# ── Load data ─────────────────────────────────────────────────────────

spectra_npz = np.load(os.path.join(_here, "walsh_spectra.npz"))
ns = spectra_npz["ns"]
all_spectra = spectra_npz["spectra"]   # shape (31, 256)
chunk_size = int(spectra_npz["chunk_size"])
WN = 1.0 / chunk_size

rows = []
with open(os.path.join(_here, "walsh_upgrade_table.csv")) as f:
    for r in csv.DictReader(f):
        rows.append({
            "s": int(r["s"]),
            "popcount": int(r["popcount"]),
            "mean_p": float(r["mean P[s]"]),
            "ratio": float(r["ratio"]),
            "corr_v2": float(r["corr v2"]),
            "geometry": r["geometry"],
            "sequency": int(r["sequency"]),
            "phase": r["phase"] == "yes",
            "k_stable": r["k-stable"] != "no",
            "length_ctrl": r["length-ctrl"] == "yes",
            "v2_ctrl": r["v2-ctrl"] == "yes",
            "shuffle": r["shuffle"] == "yes",
        })

# Tier classification:
#   tier1 (uniform): elevated in ALL 31 monoids
#   tier2 (uniform + phase): also survives phase averaging
#   tier3 (core):    also survives at least one alternative chunk size
for r in rows:
    col = all_spectra[:, r["s"]]
    r["count_all"] = int((col > WN).sum())
    r["tier1"] = r["count_all"] == 31
    r["tier2"] = r["tier1"] and r["phase"]
    r["tier3"] = r["tier2"] and r["k_stable"]

# Sort by mean P[s] descending so the brightest cells are at the top
rows.sort(key=lambda r: -r["mean_p"])

# Y-axis labels carry a tier marker: ★ for tier 3, ◆ for tier 1, blank otherwise
def tier_marker(r):
    if r["tier3"]:
        return "★"
    if r["tier1"]:
        return "◆"
    return " "

y_labels = [
    f"{tier_marker(r)} {r['s']:>3}  ({r['ratio']:.2f}×)"
    for r in rows
]

# Print tier counts as a sanity check
n_robust = len(rows)
n_tier1 = sum(1 for r in rows if r["tier1"])
n_tier2 = sum(1 for r in rows if r["tier2"])
n_tier3 = sum(1 for r in rows if r["tier3"])
print(f"robust set: {n_robust}")
print(f"  tier 1 (uniform across all 31 monoids): {n_tier1}")
print(f"  tier 2 (also phase-stable):             {n_tier2}")
print(f"  tier 3 (also k-stable):                 {n_tier3}")
print(f"  tier 3 cells: {[r['s'] for r in rows if r['tier3']]}")
print()


def population(r):
    if r["length_ctrl"] and r["v2_ctrl"]:
        return "length + v_2"
    if r["length_ctrl"] and not r["v2_ctrl"]:
        return "length only"
    return "neither"


POP_COLORS = {
    "length + v_2": "#88d8b0",
    "length only": "#ffcc5c",
    "neither": "#ff6f61",
}


# ── 1. Survival cascade ───────────────────────────────────────────────

print("Building walsh_survival_cascade.png ...")

stages = ["phase", "k_stable", "length_ctrl", "v2_ctrl", "shuffle"]
stage_labels = [
    "phase\navg",
    "k-stable\n(any k)",
    "length\nmatched",
    "v_2\npreserving",
    "entry-order\nshuffle",
]

matrix = np.zeros((len(rows), len(stages)))
for i, r in enumerate(rows):
    for j, s in enumerate(stages):
        matrix[i, j] = 1.0 if r[s] else 0.0

fig, ax = plt.subplots(figsize=(9, 14))
fig.patch.set_facecolor("#0a0a0a")
ax.set_facecolor("#0a0a0a")

cmap = ListedColormap(["#a8323a", "#5fa367"])
ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=1)

# Cell-level markers
for i in range(len(rows)):
    for j in range(len(stages)):
        ch = "✓" if matrix[i, j] == 1 else "✗"
        ax.text(j, i, ch, ha="center", va="center",
                color="white", fontsize=9)

# Tick labels
ax.set_xticks(range(len(stages)))
ax.set_xticklabels(stage_labels, color="white", fontsize=10)
ax.set_yticks(range(len(rows)))
ax.set_yticklabels(y_labels, fontsize=8)

# Color y-axis labels by population
for tick, r in zip(ax.get_yticklabels(), rows):
    tick.set_color(POP_COLORS[population(r)])

# Cell separators
for i in range(len(rows) + 1):
    ax.axhline(y=i - 0.5, color="#0a0a0a", linewidth=0.6)
for j in range(len(stages) + 1):
    ax.axvline(x=j - 0.5, color="#0a0a0a", linewidth=0.6)

# Legend for populations (encoded in y-tick label color)
import matplotlib.patches as mpatches
handles = [
    mpatches.Patch(color=POP_COLORS["length + v_2"],
                   label="population: length + v₂ explainable (9)"),
    mpatches.Patch(color=POP_COLORS["length only"],
                   label="population: length-only explainable (15)"),
    mpatches.Patch(color=POP_COLORS["neither"],
                   label="population: neither control reproduces (20)"),
]
leg = ax.legend(
    handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.04),
    ncol=1, facecolor="#1a1a1a", edgecolor="#444",
    labelcolor="white", fontsize=9,
)

ax.set_title(
    "44 robust universal Walsh cells — stage-by-stage survival\n"
    "shuffle column is uniformly red: every robust cell collapses under "
    "entry-order randomization\n"
    "★ = tier-3 core (3 cells)   ◆ = tier-1 uniform (9 cells)",
    color="white", fontsize=12, pad=14,
)
ax.set_xlabel("treatment", color="white", fontsize=11)
ax.set_ylabel(
    "Walsh cell index   (ratio vs white-noise baseline)",
    color="white", fontsize=11,
)
ax.tick_params(colors="white", which="both", length=0)
for spine in ax.spines.values():
    spine.set_color("#444")

# Footer with stage counts
counts = [int(matrix[:, j].sum()) for j in range(len(stages))]
total = len(rows)
footer = "   ".join(
    f"{lbl.replace(chr(10), ' ')}: {c}/{total}"
    for lbl, c in zip(stage_labels, counts)
)
fig.text(0.5, 0.005, footer, ha="center", color="white", fontsize=10)

plt.tight_layout(rect=[0, 0.10, 1, 1])
plt.savefig(
    os.path.join(_robustness_dir, "walsh_survival_cascade.png"),
    dpi=200, facecolor="#0a0a0a", bbox_inches="tight",
)
plt.close()
print("  -> walsh_survival_cascade.png")


# ── 2. Restricted heatmap (44 cells × 31 monoids) ─────────────────────

print("Building walsh_robust_heatmap.png ...")

robust_indices = np.array([r["s"] for r in rows])
robust_spectra = all_spectra[:, robust_indices]   # (31, 44)
heatmap_data = robust_spectra.T                    # (44, 31)

fig, ax = plt.subplots(figsize=(13, 14))
fig.patch.set_facecolor("#0a0a0a")
ax.set_facecolor("#0a0a0a")

vmin = float(heatmap_data.min())
vmax = float(heatmap_data.max())
norm = TwoSlopeNorm(vmin=min(vmin, WN - 1e-4), vcenter=WN, vmax=vmax)
im = ax.imshow(
    heatmap_data, aspect="auto", cmap="RdBu_r", norm=norm,
    interpolation="nearest",
)

ax.set_xticks(range(len(ns)))
ax.set_xticklabels(
    [str(int(n)) for n in ns], color="white", fontsize=8,
)
ax.set_yticks(range(len(rows)))
ax.set_yticklabels(y_labels, fontsize=8)

# Color y-tick labels by population
for tick, r in zip(ax.get_yticklabels(), rows):
    tick.set_color(POP_COLORS[population(r)])

ax.set_xlabel("monoid n", color="white", fontsize=11)
ax.set_ylabel(
    "Walsh cell index   (ratio vs white-noise baseline)",
    color="white", fontsize=11,
)
ax.set_title(
    "44 robust universal Walsh cells across all 31 monoids\n"
    f"red = above baseline (1/{chunk_size} ≈ {WN:.5f}); "
    "blue patches on the small-n side reveal non-uniformly elevated cells\n"
    "★ = tier-3 core (3 cells)   ◆ = tier-1 uniform (9 cells)",
    color="white", fontsize=12, pad=12,
)
ax.tick_params(colors="white", length=0)
for spine in ax.spines.values():
    spine.set_color("#444")

cbar = plt.colorbar(im, ax=ax, pad=0.02)
cbar.set_label("P[s]", color="white", fontsize=11)
cbar.ax.yaxis.set_tick_params(color="white")
plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="white")
cbar.outline.set_edgecolor("#444")

plt.tight_layout()
plt.savefig(
    os.path.join(_robustness_dir, "walsh_robust_heatmap.png"),
    dpi=200, facecolor="#0a0a0a", bbox_inches="tight",
)
plt.close()
print("  -> walsh_robust_heatmap.png")


# ── 3. Brightness vs v_2-correlation scatter ──────────────────────────

print("Building walsh_brightness_vs_v2.png ...")

fig, ax = plt.subplots(figsize=(13, 9))
fig.patch.set_facecolor("#0a0a0a")
ax.set_facecolor("#0a0a0a")

for pop, color in POP_COLORS.items():
    pts = [(r["corr_v2"], r["ratio"]) for r in rows if population(r) == pop]
    if pts:
        xs, ys = zip(*pts)
        ax.scatter(
            xs, ys, c=color, s=140, edgecolor="white", linewidth=0.6,
            label=f"{pop}  ({len(pts)})", alpha=0.95, zorder=3,
        )

# Label the brightest 12 cells; mark tier-3 with a star
for r in rows[:12]:
    label = ("★ " if r["tier3"] else "") + str(r["s"])
    ax.annotate(
        label, xy=(r["corr_v2"], r["ratio"]),
        xytext=(6, 6), textcoords="offset points",
        color="white", fontsize=9, alpha=0.95,
    )

# Also mark tier-3 cells outside the top 12 if any
for r in rows[12:]:
    if r["tier3"]:
        ax.annotate(
            "★ " + str(r["s"]), xy=(r["corr_v2"], r["ratio"]),
            xytext=(6, 6), textcoords="offset points",
            color="white", fontsize=9, alpha=0.95,
        )

ax.axvline(x=0, color="white", linewidth=0.5, alpha=0.4, linestyle="--")
ax.axhline(y=1.0, color="white", linewidth=0.5, alpha=0.4, linestyle="--")

ax.set_xlabel(
    r"correlation of $P[s]$ with $\nu_2(n)$ across the 31 monoids",
    color="white", fontsize=12,
)
ax.set_ylabel(
    r"ratio of mean $P[s]$ to white-noise baseline",
    color="white", fontsize=12,
)
ax.set_title(
    "44 robust universal cells: brightness vs $\\nu_2$-correlation\n"
    r"the brightest cells cluster near corr $= 0$, not at the "
    r"$\nu_2$-correlated edge",
    color="white", fontsize=13, pad=12,
)
ax.legend(
    facecolor="#1a1a1a", edgecolor="#444", labelcolor="white",
    fontsize=10, loc="upper right",
)
ax.tick_params(colors="white")
ax.grid(True, alpha=0.10, color="white")
for spine in ax.spines.values():
    spine.set_color("#444")

plt.tight_layout()
plt.savefig(
    os.path.join(_interpretation_dir, "walsh_brightness_vs_v2.png"),
    dpi=200, facecolor="#0a0a0a", bbox_inches="tight",
)
plt.close()
print("  -> walsh_brightness_vs_v2.png")


# ── 4. Tier 1 core focused heatmap ────────────────────────────────────

print("Building walsh_tier1_core.png ...")

tier1_rows = [r for r in rows if r["tier1"]]
tier1_indices = np.array([r["s"] for r in tier1_rows])
tier1_spectra = all_spectra[:, tier1_indices].T   # (9, 31)

fig, ax = plt.subplots(figsize=(14, 6))
fig.patch.set_facecolor("#0a0a0a")
ax.set_facecolor("#0a0a0a")

vmin = float(tier1_spectra.min())
vmax = float(tier1_spectra.max())
norm = TwoSlopeNorm(vmin=min(vmin, WN - 1e-4), vcenter=WN, vmax=vmax)
im = ax.imshow(
    tier1_spectra, aspect="auto", cmap="RdBu_r", norm=norm,
    interpolation="nearest",
)

ax.set_xticks(range(len(ns)))
ax.set_xticklabels(
    [str(int(n)) for n in ns], color="white", fontsize=9,
)
ax.set_yticks(range(len(tier1_rows)))
tier1_labels = [
    f"{tier_marker(r)} {r['s']:>3}  ({r['ratio']:.2f}×)"
    for r in tier1_rows
]
ax.set_yticklabels(tier1_labels, fontsize=10)
for tick, r in zip(ax.get_yticklabels(), tier1_rows):
    tick.set_color(POP_COLORS[population(r)])

# Numerical annotations on each cell
for i in range(len(tier1_rows)):
    for j in range(len(ns)):
        v = tier1_spectra[i, j]
        c = "white" if abs(v - WN) > 0.0015 else "#888"
        ax.text(j, i, f"{v * 256:.2f}", ha="center", va="center",
                color=c, fontsize=7)

ax.set_xlabel("monoid n", color="white", fontsize=11)
ax.set_ylabel(
    "Walsh cell   (ratio vs WN)", color="white", fontsize=11,
)
ax.set_title(
    "Tier 1 core: 9 Walsh cells elevated above baseline in ALL 31 monoids\n"
    "annotation = P[s] · 256 (i.e., ratio vs white-noise baseline)\n"
    "★ = tier-3 (also k-stable);   y-tick color = control population",
    color="white", fontsize=12, pad=12,
)
ax.tick_params(colors="white", length=0)
for spine in ax.spines.values():
    spine.set_color("#444")

cbar = plt.colorbar(im, ax=ax, pad=0.02)
cbar.set_label("P[s]", color="white", fontsize=11)
cbar.ax.yaxis.set_tick_params(color="white")
plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="white")
cbar.outline.set_edgecolor("#444")

plt.tight_layout()
plt.savefig(
    os.path.join(_interpretation_dir, "walsh_tier1_core.png"),
    dpi=200, facecolor="#0a0a0a", bbox_inches="tight",
)
plt.close()
print("  -> walsh_tier1_core.png")

print("\nDone.")
