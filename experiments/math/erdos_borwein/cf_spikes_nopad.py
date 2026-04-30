"""
Erdős-Borwein brief #3, padding-free control.

The fixed-width-w binary encoding pads each d(n) with leading zeros
because d(n) ≤ 64 << 2^w. This padding is a structural artifact:
every w-bit chunk has ≥ 10 leading zeros, creating periodic zero runs
in R_d's binary expansion, which dominate its CF spike density (see
cf_spikes_controls).

Two padding-free controls:

  R_d^65  := Σ d(n) · 65^{-n}, exact rational.
             Each d(n) is one base-65 "digit". Since max d(n)=64,
             no padding, no separator. The cleanest encoding of d(n)
             as a real.

  R_d^65^shuf := same, but d(n) values shuffled. Null for the
                 divisor-correlation contribution, given this
                 encoding.

If R_d^65 still has non-Khinchin spike density above R_d^65^shuf,
divisor structure is contributing something visible. If both drop
to Khinchin-typical (or both stay non-Khinchin in matched amounts),
divisor structure adds nothing the encoding doesn't already.
"""

import random
import time
from math import log2
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent

N = 10_000
BASE = 65
SEED = 20260429
MAX_CF_STEPS = 40_000


def divisor_count_sieve(n_max):
    d = [0] * (n_max + 1)
    for i in range(1, n_max + 1):
        for j in range(i, n_max + 1, i):
            d[j] += 1
    return d


def log2_bigint(n):
    if n <= 0:
        return 0.0
    b = n.bit_length()
    if b <= 53:
        return log2(n)
    top = n >> (b - 53)
    return (b - 53) + log2(top)


def build_real_baseB(seq, base):
    """x = sum_{n=1..N} seq[n-1] * base^{-n}, returned as num/den."""
    N = len(seq)
    num = 0
    for v in seq:
        assert 0 <= v < base, f"value {v} does not fit in base {base}"
        num = num * base + v
    den = base ** N
    return num, den


def cf_expand(num, den, max_steps):
    a_list, log2a, log2q = [], [], []
    q_prev, q_curr = 0, 1
    A, B = num, den
    while B != 0 and len(a_list) < max_steps:
        a, r = divmod(A, B)
        a_list.append(a)
        log2a.append(log2_bigint(a + 1))
        q_prev, q_curr = q_curr, a * q_curr + q_prev
        log2q.append(log2_bigint(q_curr))
        A, B = B, r
    return a_list, log2a, log2q


def spike_counts(log2a, thresholds):
    return {T: sum(1 for x in log2a if x > T) for T in thresholds}


def khinchin_expected(n_steps, T):
    """Gauss-Kuzmin survival count: P(a >= 2**T) = log2(1 + 1/2**T)."""
    return n_steps * log2(1.0 + 1.0 / (2 ** T))


def main():
    random.seed(SEED)

    print(f"sieving d(n) for n=1..{N}")
    d = divisor_count_sieve(N)
    seq_d = d[1:]
    seq_shuf = list(seq_d)
    random.shuffle(seq_shuf)
    print(f"  max d(n) = {max(seq_d)}; using base {BASE}")

    runs = [
        (f"R_d^{BASE}",        seq_d,    BASE),
        (f"R_d^{BASE}^shuf",   seq_shuf, BASE),
    ]

    thresholds = [4, 6, 8, 10, 12, 14]
    results = []

    for label, seq, base in runs:
        print(f"\n=== {label} ===")
        t0 = time.time()
        num, den = build_real_baseB(seq, base)
        print(f"  built real: {num.bit_length()} bits ({time.time()-t0:.2f}s)")
        t0 = time.time()
        a_list, log2a, log2q = cf_expand(num, den, MAX_CF_STEPS)
        print(f"  CF: {len(a_list)} steps in {time.time()-t0:.2f}s; "
              f"final log2 q = {log2q[-1]:.1f}")
        counts = spike_counts(log2a, thresholds)
        results.append((label, base, log2a, log2q, counts))

    print("\n=== spike density (40K steps) ===")
    header = f"{'T':>3}  " + "  ".join(f"{lbl:>20}" for lbl, *_ in results) \
             + "  " + f"{'Khinchin expect':>16}"
    print(header)
    rows = []
    for T in thresholds:
        row = f"{T:>3}  " + "  ".join(
            f"{counts[T]:>20d}" for _, _, _, _, counts in results
        ) + "  " + f"{khinchin_expected(MAX_CF_STEPS, T):>16.1f}"
        print(row)
        rows.append(row)

    summary = ["# Erdős–Borwein brief #3 — base-65 (padding-free)", "",
               header, *rows, ""]
    for label, base, log2a, log2q, _ in results:
        summary.append(f"## {label} — top 10 by log2(a+1)")
        summary.append(
            f"  {'i':>6}  {'log2 a+1':>9}  {'log2 q':>9}"
        )
        top = sorted(enumerate(log2a), key=lambda x: -x[1])[:10]
        for i, la in top:
            summary.append(f"  {i:>6d}  {la:>9.3f}  {log2q[i]:>9.1f}")
        summary.append("")

    fig, axes = plt.subplots(2, 1, figsize=(13, 6), sharex=True)
    for ax, (label, base, log2a, _, _) in zip(axes, results):
        ax.plot(log2a, linewidth=0.3, color="steelblue")
        ax.set_title(label)
        ax.set_ylabel("log₂(aᵢ + 1)")
        ax.grid(True, alpha=0.3)
    axes[-1].set_xlabel("CF index i")
    plt.tight_layout()
    plot_path = HERE / "cf_spikes_nopad_trace.png"
    plt.savefig(plot_path, dpi=140)
    print(f"\nwrote {plot_path.name}")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    bins = [i * 0.5 for i in range(0, 41)]
    for ax, (label, base, log2a, _, _) in zip(axes, results):
        ax.hist(log2a, bins=bins, log=True, color="steelblue",
                edgecolor="black", linewidth=0.2)
        ax.set_title(label)
        ax.set_xlabel("log₂(aᵢ + 1)")
        ax.grid(True, alpha=0.3)
    axes[0].set_ylabel("count (log scale)")
    plt.tight_layout()
    hist_path = HERE / "cf_spikes_nopad_hist.png"
    plt.savefig(hist_path, dpi=140)
    print(f"wrote {hist_path.name}")

    summary_path = HERE / "cf_spikes_nopad_summary.txt"
    summary_path.write_text("\n".join(summary) + "\n")
    print(f"wrote {summary_path.name}")
    print()
    print("\n".join(summary))


if __name__ == "__main__":
    main()
