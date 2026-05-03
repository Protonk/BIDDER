"""
Gap Weather.

Render signed discrepancy residuals F_L(t) - t for C_SurvA along a
path through ambient numerical semigroups.  The ACM bundle is fixed;
only the ambient S = <a,b> changes.

Outputs:
- gap_weather.png
- gap_weather.txt
"""

import math
import os
import sys

import numpy as np
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'interlock'))

from ns_atoms import numerical_semigroup, is_atom, frobenius_number, gap_set  # noqa: E402


N0, N1, K = 2, 20, 80
PRECISION = 18
GRID_SIZE = 1600

SEMIGROUP_PATH = [
    (2, 3),
    (3, 5),
    (5, 7),
]

COLORS = {
    "bg": "#0a0a0a",
    "warm": "#ffcc5c",
    "cool": "#6ec6ff",
    "line": "#f8f8f8",
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
    return [m for _, m in atoms if counts[m] == 1]


def digit_string(values):
    return ''.join(str(int(v)) for v in values)


def tail_orbit(ds, precision=PRECISION):
    digits = np.frombuffer(ds.encode(), dtype=np.uint8) - ord('0')
    L = len(digits)
    weights = 10.0 ** (-(np.arange(precision) + 1))
    pad = np.concatenate([digits, np.zeros(precision, dtype=np.uint8)])
    orbit = np.zeros(L, dtype=np.float64)
    for j in range(precision):
        orbit += pad[j:j + L] * weights[j]
    return orbit


def residual_curve(orbit, grid_size=GRID_SIZE):
    sorted_v = np.sort(np.asarray(orbit, dtype=np.float64))
    n = len(sorted_v)
    t = np.linspace(0.0, 1.0, grid_size)
    cdf = np.searchsorted(sorted_v, t, side="right") / n
    residual = cdf - t
    i = np.arange(1, n + 1, dtype=np.float64)
    d_plus = float(np.max(i / n - sorted_v))
    d_minus = float(np.max(sorted_v - (i - 1) / n))
    return t, residual, max(d_plus, d_minus)


def build_records():
    atoms = bundle_atoms(N0, N1, K)
    surv = acm_survivors(atoms)
    max_value = max(m for _, m in atoms)
    records = []
    for generators in SEMIGROUP_PATH:
        if math.gcd(*generators) != 1:
            raise ValueError(f"generators must be coprime: {generators}")
        S = numerical_semigroup(generators, max_value)
        values = [m for m in surv if is_atom(m, S)]
        ds = digit_string(values)
        orbit = tail_orbit(ds)
        t, residual, d_star = residual_curve(orbit)
        records.append({
            "generators": generators,
            "values": values,
            "digit_len": len(ds),
            "atom_count": len(values),
            "gaps": gap_set(S, max_value),
            "F": frobenius_number(S, max_value),
            "t": t,
            "residual": residual,
            "d_star": d_star,
            "ratio": d_star / (math.log(len(ds)) / math.sqrt(len(ds))),
        })
    return records, {
        "bundle_atoms": len(atoms),
        "acm_survivors": len(surv),
        "max_value": max_value,
    }


def draw(records, path):
    fig, ax = plt.subplots(figsize=(12, 12), subplot_kw={"projection": "polar"})
    fig.patch.set_facecolor(COLORS["bg"])
    ax.set_facecolor(COLORS["bg"])
    ax.set_axis_off()

    max_abs = max(float(np.max(np.abs(r["residual"]))) for r in records)
    amp = 0.18 / max_abs
    baselines = np.array([0.95, 1.82, 2.75])

    for r, radius0 in zip(records, baselines):
        theta = 2.0 * np.pi * r["t"]
        radius = radius0 + r["residual"] * amp
        ax.fill_between(theta, radius0, radius, where=radius >= radius0,
                        interpolate=True,
                        color=COLORS["warm"], alpha=0.74, linewidth=0)
        ax.fill_between(theta, radius0, radius, where=radius < radius0,
                        interpolate=True,
                        color=COLORS["cool"], alpha=0.72, linewidth=0)
        ax.plot(theta, radius, color=COLORS["line"], linewidth=0.95, alpha=0.94)
        ax.plot(theta, np.full_like(theta, radius0), color="#151515",
                linewidth=0.35, alpha=0.5)

    ax.set_ylim(0.56, baselines[-1] + 0.48)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    plt.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.98)
    plt.savefig(path, dpi=180, facecolor=COLORS["bg"], bbox_inches="tight")


def write_summary(records, meta, path):
    lines = [
        "Gap Weather",
        f"ACM window = [{N0},{N1}], k = {K}",
        f"bundle atoms = {meta['bundle_atoms']}",
        f"ACM survivors = {meta['acm_survivors']}",
        f"max bundle integer = {meta['max_value']}",
        "",
        f"{'S':<8} {'F':>4} {'|G|':>4} {'atoms':>6} {'L':>6} "
        f"{'D*':>8} {'ratio':>7}",
        "-" * 52,
    ]
    for r in records:
        a, b = r["generators"]
        lines.append(f"<{a},{b}>   {r['F']:>4} {len(r['gaps']):>4} "
                     f"{r['atom_count']:>6} {r['digit_len']:>6} "
                     f"{r['d_star']:>8.4f} {r['ratio']:>7.3f}")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    records, meta = build_records()
    png_path = os.path.join(HERE, "gap_weather.png")
    txt_path = os.path.join(HERE, "gap_weather.txt")
    draw(records, png_path)
    write_summary(records, meta, txt_path)
    print(f"Saved {png_path}")
    print(f"Saved {txt_path}")


if __name__ == "__main__":
    main()
