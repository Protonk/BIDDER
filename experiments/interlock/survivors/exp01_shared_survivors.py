"""
EXP01 — shared survivors for an ACM n/k window inside a numerical
semigroup.

Build the ordinary ACM survivor bundle over rows n0..n1, k atoms per
row.  Then classify every bundle integer against a numerical semigroup
S: gap, S-reducible, or multiplicative atom A_S.  The shared survivor
stream C_SurvA is the subsequence that survives the ACM bundle and is
also in A_S.

Outputs:
- exp01_shared_survivors.png
- exp01_shared_survivors.txt
"""

import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'interlock'))

from ns_atoms import numerical_semigroup, gap_set, frobenius_number, is_atom  # noqa: E402


N0, N1, K = 2, 20, 28
GENERATORS = (5, 7)

PALETTE = {
    "bg": "#0a0a0a",
    "fg": "white",
    "grid": "#333333",
    "yellow": "#ffcc5c",
    "blue": "#6ec6ff",
    "red": "#ff6f61",
    "green": "#88d8b0",
}


def nth_n_prime(n, index):
    """1-indexed atom of M_n = {1} ∪ nZ_{>0}, n >= 2."""
    q, r = divmod(index - 1, n - 1)
    return n * (q * n + r + 1)


def bundle_atoms(n0, n1, k):
    """[(n, m), ...] in row-major ACM read order."""
    return [(n, nth_n_prime(n, j))
            for n in range(n0, n1 + 1)
            for j in range(1, k + 1)]


def survival_mask(atoms):
    counts = {}
    for _, m in atoms:
        counts[m] = counts.get(m, 0) + 1
    return np.array([counts[m] == 1 for _, m in atoms], dtype=bool), counts


def leading_digit(n):
    while n >= 10:
        n //= 10
    return n


def leading_l1_trace(atoms, keep_mask):
    """Running L1 from uniform over leading digits 1..9."""
    counts = np.zeros(9, dtype=np.int64)
    out = np.full(len(atoms), np.nan, dtype=float)
    total = 0
    uniform = np.full(9, 1.0 / 9.0)
    for i, ((_, m), keep) in enumerate(zip(atoms, keep_mask)):
        if keep:
            counts[leading_digit(m) - 1] += 1
            total += 1
        if total:
            out[i] = np.abs(counts / total - uniform).sum()
    return out


def digit_stream(values):
    return [int(ch) for v in values for ch in str(v)]


def classify_bundle(atoms, S):
    """0 = gap, 1 = in S reducible, 2 = in A_S."""
    status = np.zeros(len(atoms), dtype=np.int8)
    for i, (_, m) in enumerate(atoms):
        if m not in S:
            status[i] = 0
        elif is_atom(m, S):
            status[i] = 2
        else:
            status[i] = 1
    return status


def write_summary(path, atoms, status, acm_surv, surv_a, S, counts):
    rows = []
    values = [m for _, m in atoms]
    surv_values = [m for (_, m), keep in zip(atoms, acm_surv) if keep]
    surv_a_values = [m for (_, m), keep in zip(atoms, surv_a) if keep]
    gaps = gap_set(S, max(values))
    lines = [
        "EXP01 shared survivors",
        f"S = <{','.join(map(str, GENERATORS))}>",
        f"ACM window = [{N0},{N1}], k = {K}",
        f"max bundle integer = {max(values)}",
        f"G = {gaps}",
        f"F = {frobenius_number(S, max(values))}",
        "",
        f"bundle atoms          = {len(atoms)}",
        f"distinct integers     = {len(counts)}",
        f"ACM survivors         = {int(acm_surv.sum())}",
        f"gap hits              = {int((status == 0).sum())}",
        f"S-reducible hits      = {int((status == 1).sum())}",
        f"A_S hits              = {int((status == 2).sum())}",
        f"C_SurvA atoms         = {int(surv_a.sum())}",
        f"C_SurvA digit length  = {len(digit_stream(surv_a_values))}",
        "",
        "first C_Surv values:",
        "  " + ", ".join(map(str, surv_values[:60])),
        "",
        "first C_SurvA values:",
        "  " + ", ".join(map(str, surv_a_values[:60])),
        "",
        "Per-row counts:",
        f"{'n':>3} {'gap':>4} {'red':>4} {'A_S':>4} {'surv':>5} {'SurvA':>5}",
        "-" * 31,
    ]
    for n in range(N0, N1 + 1):
        idx = np.array([i for i, (row_n, _) in enumerate(atoms) if row_n == n])
        row = (
            n,
            int((status[idx] == 0).sum()),
            int((status[idx] == 1).sum()),
            int((status[idx] == 2).sum()),
            int(acm_surv[idx].sum()),
            int(surv_a[idx].sum()),
        )
        rows.append(row)
        lines.append(f"{row[0]:>3} {row[1]:>4} {row[2]:>4} {row[3]:>4} "
                     f"{row[4]:>5} {row[5]:>5}")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return rows


def draw_plot(atoms, status, acm_surv, surv_a, row_counts, out_path):
    surv_a_values = [m for (_, m), keep in zip(atoms, surv_a) if keep]
    n_atoms = len(atoms)
    x = np.arange(1, n_atoms + 1)
    row_n = np.array([n for n, _ in atoms])

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.patch.set_facecolor(PALETTE["bg"])
    axes = axes.ravel()
    for ax in axes:
        ax.set_facecolor(PALETTE["bg"])
        ax.tick_params(colors=PALETTE["fg"])
        for spine in ax.spines.values():
            spine.set_color(PALETTE["grid"])
        ax.grid(color=PALETTE["grid"], linewidth=0.35, alpha=0.55)

    # Ordered bundle barcode.
    ax = axes[0]
    colors = np.array([PALETTE["red"], PALETTE["blue"], PALETTE["green"]])
    ax.scatter(x, row_n, c=colors[status], s=22, marker="s", linewidths=0)
    killed = ~acm_surv
    ax.scatter(x[killed], row_n[killed], c=PALETTE["bg"], s=12, marker="s",
               linewidths=0, alpha=0.72)
    ax.scatter(x[surv_a], row_n[surv_a], facecolors="none",
               edgecolors=PALETTE["yellow"], s=40, marker="s", linewidths=0.8)
    for j, n in enumerate(range(N0, N1 + 1)):
        boundary = j * K + 0.5
        ax.axvline(boundary, color="white", linewidth=0.35, alpha=0.16)
        ax.text(j * K + K / 2, N1 + 0.9, str(n), color="#999999",
                ha="center", va="bottom", fontsize=8)
    ax.set_ylim(N0 - 1, N1 + 1.8)
    ax.set_xlim(0, n_atoms + 1)
    ax.set_title("ACM bundle ordered by n-row; S-status overlay",
                 color=PALETTE["fg"])
    ax.set_xlabel("bundle position", color=PALETTE["fg"])
    ax.set_ylabel("ACM row n", color=PALETTE["fg"])
    handles = [
        Line2D([0], [0], marker="s", color="none", markerfacecolor=PALETTE["red"],
               label="gap", markersize=8),
        Line2D([0], [0], marker="s", color="none", markerfacecolor=PALETTE["blue"],
               label="in S, reducible", markersize=8),
        Line2D([0], [0], marker="s", color="none", markerfacecolor=PALETTE["green"],
               label="A_S", markersize=8),
        Line2D([0], [0], marker="s", color=PALETTE["yellow"], markerfacecolor="none",
               label="SurvA", markersize=8),
    ]
    ax.legend(handles=handles, facecolor="#1a1a1a", labelcolor=PALETTE["fg"],
              framealpha=0.35, loc="lower right")

    # Two/three tongues.
    ax = axes[1]
    all_mask = np.ones(n_atoms, dtype=bool)
    ax.semilogy(x, leading_l1_trace(atoms, all_mask), color=PALETTE["yellow"],
                linewidth=1.3, label="bundle")
    ax.semilogy(x, leading_l1_trace(atoms, acm_surv), color=PALETTE["blue"],
                linewidth=1.3, label="C_Surv")
    ax.semilogy(x, leading_l1_trace(atoms, surv_a), color=PALETTE["green"],
                linewidth=1.4, label="C_SurvA")
    for j in range(1, N1 - N0 + 1):
        ax.axvline(j * K, color="white", linewidth=0.35, alpha=0.14)
    ax.set_title("Running leading-digit L1", color=PALETTE["fg"])
    ax.set_xlabel("bundle position", color=PALETTE["fg"])
    ax.set_ylabel("L1 from uniform", color=PALETTE["fg"])
    ax.legend(facecolor="#1a1a1a", labelcolor=PALETTE["fg"], framealpha=0.35)

    # Per-row composition.
    ax = axes[2]
    ns = np.array([r[0] for r in row_counts])
    gap = np.array([r[1] for r in row_counts])
    red = np.array([r[2] for r in row_counts])
    atom = np.array([r[3] for r in row_counts])
    surv = np.array([r[4] for r in row_counts])
    surva = np.array([r[5] for r in row_counts])
    ax.bar(ns, gap, color=PALETTE["red"], label="gap")
    ax.bar(ns, red, bottom=gap, color=PALETTE["blue"], label="in S, reducible")
    ax.bar(ns, atom, bottom=gap + red, color=PALETTE["green"], label="A_S")
    ax.plot(ns, surv, color="white", marker="o", linewidth=1.2,
            markersize=4, label="ACM survivors")
    ax.plot(ns, surva, color=PALETTE["yellow"], marker="o", linewidth=1.2,
            markersize=4, label="SurvA")
    ax.set_title("Row composition", color=PALETTE["fg"])
    ax.set_xlabel("ACM row n", color=PALETTE["fg"])
    ax.set_ylabel("count among k atoms", color=PALETTE["fg"])
    ax.set_xticks(ns)
    ax.legend(facecolor="#1a1a1a", labelcolor=PALETTE["fg"], framealpha=0.35,
              fontsize=9)

    # Digit strip of C_SurvA.
    ax = axes[3]
    digits = digit_stream(surv_a_values)
    max_digits = min(260, len(digits))
    arr = np.array(digits[:max_digits], dtype=np.int8)[None, :]
    cmap = ListedColormap([
        "#1f77b4", "#ffcc5c", "#88d8b0", "#ff6f61", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
    ])
    ax.imshow(arr, aspect="auto", interpolation="nearest", cmap=cmap,
              vmin=0, vmax=9)
    ax.set_yticks([])
    ax.set_xlabel("digits of C_SurvA", color=PALETTE["fg"])
    ax.set_title(f"C_SurvA digit strip, first {max_digits} digits",
                 color=PALETTE["fg"])
    ax.grid(False)

    fig.suptitle(
        f"EXP01 shared survivors: ACM [{N0},{N1}], k={K}, "
        f"S=<{','.join(map(str, GENERATORS))}>",
        color=PALETTE["fg"],
        fontsize=14,
    )
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, facecolor=PALETTE["bg"],
                bbox_inches="tight")


def main():
    atoms = bundle_atoms(N0, N1, K)
    # ACM survivor sanity check from SURVIVORS.md.
    ex_atoms = bundle_atoms(2, 4, 5)
    ex_mask, _ = survival_mask(ex_atoms)
    assert [m for (_, m), keep in zip(ex_atoms, ex_mask) if keep] == [
        2, 10, 14, 18, 3, 15, 21, 4, 8, 20, 24
    ]

    acm_surv, counts = survival_mask(atoms)
    max_value = max(m for _, m in atoms)
    S = numerical_semigroup(GENERATORS, max_value)
    status = classify_bundle(atoms, S)
    surv_a = acm_surv & (status == 2)

    txt_path = os.path.join(HERE, "exp01_shared_survivors.txt")
    row_counts = write_summary(txt_path, atoms, status, acm_surv, surv_a, S, counts)
    png_path = os.path.join(HERE, "exp01_shared_survivors.png")
    draw_plot(atoms, status, acm_surv, surv_a, row_counts, png_path)

    print(f"Saved {txt_path}")
    print(f"Saved {png_path}")


if __name__ == "__main__":
    main()
