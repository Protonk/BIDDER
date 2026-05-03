"""
EXP02 — phase space of ambient numerical semigroups for C_SurvA.

Fix the ACM survivor window from the interlock setting, then vary the
ambient two-generator numerical semigroup S = <a,b>.  For each coprime
pair a < b, build C_SurvA: the ACM survivors that are also
multiplicative atoms of (S, ·), in ACM read order.

The plotted observables are atom count, digit length, star discrepancy
D_L* of the shifted decimal-tail orbit, and the ratio to (log L)/sqrt L.

Outputs:
- exp02_phase_space.png
- exp02_phase_space.txt
"""

import math
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'interlock'))

from ns_atoms import numerical_semigroup, is_atom, frobenius_number, gap_set  # noqa: E402


N0, N1, K = 2, 20, 80
A_MIN, A_MAX = 2, 18
B_MIN, B_MAX = 3, 30
PRECISION = 18

PALETTE = {
    "bg": "#0a0a0a",
    "fg": "white",
    "grid": "#333333",
}


def nth_n_prime(n, index):
    q, r = divmod(index - 1, n - 1)
    return n * (q * n + r + 1)


def bundle_atoms(n0, n1, k):
    return [(n, nth_n_prime(n, j))
            for n in range(n0, n1 + 1)
            for j in range(1, k + 1)]


def acm_survivors(atoms):
    counts = {}
    for _, m in atoms:
        counts[m] = counts.get(m, 0) + 1
    return [m for _, m in atoms if counts[m] == 1], counts


def digit_string(values):
    return ''.join(str(int(v)) for v in values)


def tail_orbit(ds, precision=PRECISION):
    L = len(ds)
    if L == 0:
        return np.array([], dtype=np.float64)
    digits = np.frombuffer(ds.encode(), dtype=np.uint8) - ord('0')
    weights = 10.0 ** (-(np.arange(precision) + 1))
    pad = np.concatenate([digits, np.zeros(precision, dtype=np.uint8)])
    orbit = np.zeros(L, dtype=np.float64)
    for j in range(precision):
        orbit += pad[j:j + L] * weights[j]
    return orbit


def star_discrepancy(values):
    sorted_v = np.sort(np.asarray(values, dtype=np.float64))
    n = len(sorted_v)
    if n == 0:
        return float('nan')
    i = np.arange(1, n + 1, dtype=np.float64)
    d_plus = float(np.max(i / n - sorted_v))
    d_minus = float(np.max(sorted_v - (i - 1) / n))
    return max(d_plus, d_minus)


def build_grids():
    atoms = bundle_atoms(N0, N1, K)
    surv_values, counts = acm_survivors(atoms)
    max_value = max(m for _, m in atoms)

    shape = (A_MAX - A_MIN + 1, B_MAX - B_MIN + 1)
    atom_count = np.full(shape, np.nan)
    digit_len = np.full(shape, np.nan)
    d_star = np.full(shape, np.nan)
    ratio = np.full(shape, np.nan)
    frob = np.full(shape, np.nan)
    gap_count = np.full(shape, np.nan)
    records = []

    for a in range(A_MIN, A_MAX + 1):
        for b in range(B_MIN, B_MAX + 1):
            if b <= a or math.gcd(a, b) != 1:
                continue
            row = a - A_MIN
            col = b - B_MIN
            S = numerical_semigroup((a, b), max_value)
            values = [m for m in surv_values if is_atom(m, S)]
            ds = digit_string(values)
            L = len(ds)
            D = star_discrepancy(tail_orbit(ds)) if L else float('nan')
            ref = math.log(L) / math.sqrt(L) if L > 1 else float('nan')
            R = D / ref if ref and not math.isnan(ref) else float('nan')
            F = frobenius_number(S, max_value)
            G = gap_set(S, max_value)

            atom_count[row, col] = len(values)
            digit_len[row, col] = L
            d_star[row, col] = D
            ratio[row, col] = R
            frob[row, col] = F
            gap_count[row, col] = len(G)
            records.append({
                "a": a,
                "b": b,
                "F": F,
                "gap_count": len(G),
                "atom_count": len(values),
                "digit_len": L,
                "d_star": D,
                "ratio": R,
                "first": values[:16],
            })
    meta = {
        "atoms": atoms,
        "surv_values": surv_values,
        "counts": counts,
        "max_value": max_value,
    }
    grids = {
        "atom_count": atom_count,
        "digit_len": digit_len,
        "d_star": d_star,
        "ratio": ratio,
        "frob": frob,
        "gap_count": gap_count,
    }
    return records, grids, meta


def write_summary(path, records, meta):
    by_len = sorted(records, key=lambda r: r["digit_len"])
    by_d = sorted(records, key=lambda r: r["d_star"])
    by_ratio = sorted(records, key=lambda r: r["ratio"])
    lines = [
        "EXP02 ambient-S phase space for C_SurvA",
        f"ACM window = [{N0},{N1}], k = {K}",
        f"ambient S = <a,b>, {A_MIN} <= a <= {A_MAX}, "
        f"{B_MIN} <= b <= {B_MAX}, gcd(a,b)=1, a<b",
        f"bundle atoms = {len(meta['atoms'])}",
        f"ACM survivors = {len(meta['surv_values'])}",
        f"max bundle integer = {meta['max_value']}",
        f"phase cells = {len(records)}",
        "",
        "Metric definitions:",
        "  atoms = number of ACM survivors that are also in A_S",
        "  L = decimal digit length of C_SurvA",
        "  D_L* = star discrepancy of shifted decimal-tail orbit",
        "  ratio = D_L* / ((log L)/sqrt L)",
        "",
    ]

    def add_table(title, rows, reverse=False):
        lines.extend([title, f"{'S':<9} {'F':>4} {'|G|':>4} {'atoms':>6} "
                      f"{'L':>6} {'D_L*':>8} {'ratio':>7}",
                      "-" * 52])
        for r in (list(reversed(rows)) if reverse else rows)[:10]:
            lines.append(f"<{r['a']},{r['b']}>   {r['F']:>4} "
                         f"{r['gap_count']:>4} {r['atom_count']:>6} "
                         f"{r['digit_len']:>6} {r['d_star']:>8.4f} "
                         f"{r['ratio']:>7.3f}")
        lines.append("")

    add_table("Smallest C_SurvA digit length:", by_len)
    add_table("Largest C_SurvA digit length:", by_len, reverse=True)
    add_table("Lowest D_L*:", by_d)
    add_table("Highest D_L*:", by_d, reverse=True)
    add_table("Lowest benchmark ratio:", by_ratio)
    add_table("Highest benchmark ratio:", by_ratio, reverse=True)

    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def draw_heatmaps(path, grids):
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    fig.patch.set_facecolor(PALETTE["bg"])
    axes = axes.ravel()

    panels = [
        ("C_SurvA atom count", grids["atom_count"], "viridis"),
        ("C_SurvA digit length L", grids["digit_len"], "viridis"),
        ("Star discrepancy D_L*", grids["d_star"], "magma"),
        ("D_L* / ((log L)/sqrt L)", grids["ratio"], "plasma"),
    ]

    x0, x1 = B_MIN - 0.5, B_MAX + 0.5
    y0, y1 = A_MAX + 0.5, A_MIN - 0.5
    for ax, (title, data, cmap) in zip(axes, panels):
        ax.set_facecolor(PALETTE["bg"])
        masked = np.ma.masked_invalid(data)
        im = ax.imshow(masked, extent=(x0, x1, y0, y1),
                       interpolation="nearest", aspect="auto", cmap=cmap)
        ax.set_title(title, color=PALETTE["fg"], fontsize=12)
        ax.set_xlabel("b in S=<a,b>", color=PALETTE["fg"])
        ax.set_ylabel("a in S=<a,b>", color=PALETTE["fg"])
        ax.set_xticks(range(B_MIN, B_MAX + 1, 2))
        ax.set_yticks(range(A_MIN, A_MAX + 1, 2))
        ax.tick_params(colors=PALETTE["fg"])
        for spine in ax.spines.values():
            spine.set_color(PALETTE["grid"])
        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
        cbar.ax.tick_params(colors=PALETTE["fg"])
        cbar.outline.set_edgecolor(PALETTE["grid"])

    fig.suptitle(
        f"EXP02 ambient-S phase space: ACM [{N0},{N1}], k={K}, "
        "C_SurvA in row-major survivor order",
        color=PALETTE["fg"],
        fontsize=14,
    )
    plt.tight_layout()
    plt.savefig(path, dpi=150, facecolor=PALETTE["bg"], bbox_inches="tight")


def main():
    records, grids, meta = build_grids()
    txt_path = os.path.join(HERE, "exp02_phase_space.txt")
    png_path = os.path.join(HERE, "exp02_phase_space.png")
    write_summary(txt_path, records, meta)
    draw_heatmaps(png_path, grids)
    print(f"Saved {txt_path}")
    print(f"Saved {png_path}")


if __name__ == "__main__":
    main()
