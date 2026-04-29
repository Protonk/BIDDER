#!/usr/bin/env python3
"""Reproduce the Phase 3.1 d=4 mega-spike comparison table.

The CF spike rows come from experiments/acm-flow/cf/the original CF panel (cf_spikes.py output).
The log10(q_before) values are the rounded values recorded in
the original CF panel (cf_spikes.py output)'s Diophantine-consequence table.
"""

from __future__ import annotations

import csv
from fractions import Fraction
from pathlib import Path


BASE = 10
K = 4
N_VALUES = (2, 3, 4, 5, 6, 10)

# Rounded source values from:
# experiments/acm-flow/cf/the original CF panel (cf_spikes.py output)
LOG10_Q_BEFORE = {
    2: 727.7,
    3: 650.0,
    4: 553.4,
    5: 479.0,
    6: 421.0,
    10: 296.7,
}


EXPERIMENTS = Path(__file__).resolve().parents[2]
CF_SPIKES = EXPERIMENTS / "acm-champernowne" / "base10" / "cf" / "cf_spikes.csv"
OUT_CSV = Path(__file__).with_name("spike_drift_table.csv")
OUT_SUMMARY = Path(__file__).with_name("spike_drift_summary.txt")


def smooth_factor(n: int) -> Fraction:
    return Fraction(n - 1, n * n)


def cumulative_digits_before(n: int, base: int = BASE, k: int = K) -> Fraction:
    factor = smooth_factor(n)
    return sum(
        Fraction(base - 1) * factor * d * (base ** (d - 1))
        for d in range(1, k)
    )


def digit_mass(n: int, base: int = BASE, k: int = K) -> Fraction:
    return Fraction(k * (base - 1) * (base ** (k - 1))) * smooth_factor(n)


def scout(n: int, base: int = BASE, k: int = K) -> Fraction:
    return (
        Fraction((base - 1) ** 2 * (base ** (k - 2)) * k)
        * smooth_factor(n)
    )


def load_mega_spikes() -> dict[int, dict[str, str]]:
    rows: dict[int, dict[str, str]] = {}
    with CF_SPIKES.open(newline="") as f:
        for row in csv.DictReader(f):
            n = int(row["n"])
            if n not in N_VALUES:
                continue
            if n not in rows or int(row["pq_digits"]) > int(rows[n]["pq_digits"]):
                rows[n] = row
    missing = sorted(set(N_VALUES) - set(rows))
    if missing:
        raise RuntimeError(f"missing mega-spike rows for n={missing}")
    return rows


def fmt(x: float) -> str:
    return f"{x:.4f}"


def main() -> None:
    mega = load_mega_spikes()
    out_rows = []

    for n in N_VALUES:
        row = mega[n]
        c_prev = cumulative_digits_before(n)
        d_k = digit_mass(n)
        refined = d_k - c_prev
        q_before = LOG10_Q_BEFORE[n]
        delta = q_before - float(c_prev)
        observed_digits = int(row["pq_digits"])
        observed_log10 = float(row["pq_log10"])

        out_rows.append(
            {
                "n": n,
                "cf_index": int(row["index"]),
                "observed_digits": observed_digits,
                "observed_log10_a": fmt(observed_log10),
                "scout": fmt(float(scout(n))),
                "C_prev": fmt(float(c_prev)),
                "D_k": fmt(float(d_k)),
                "refined_D_minus_C": fmt(float(refined)),
                "log10_q_before": fmt(q_before),
                "denominator_delta": fmt(delta),
                "minus_2_delta": fmt(-2 * delta),
                "residual_digits": fmt(observed_digits - float(refined)),
                "residual_log10": fmt(observed_log10 - float(refined)),
                "scaled_digits": fmt(observed_digits * n * n / (n - 1)),
            }
        )

    with OUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)

    lines = [
        "Phase 3.1 d=4 mega-spike drift table",
        "",
        "log10(q_before) is rounded to the one-decimal values recorded in the original CF panel (cf_spikes.py output).",
        "",
        (
            " n  idx  obs_log10   D-C       residual_log10   "
            "-2*(logq-C)   scaled_digits"
        ),
    ]
    for r in out_rows:
        lines.append(
            f"{r['n']:>2} {r['cf_index']:>4} {r['observed_log10_a']:>10} "
            f"{r['refined_D_minus_C']:>9} {r['residual_log10']:>15} "
            f"{r['minus_2_delta']:>13} {r['scaled_digits']:>15}"
        )
    lines.append("")
    lines.append(f"Wrote {OUT_CSV.name}.")
    OUT_SUMMARY.write_text("\n".join(lines) + "\n")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
