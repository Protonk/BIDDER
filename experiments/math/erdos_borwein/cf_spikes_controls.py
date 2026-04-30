"""
Erdős-Borwein brief #3, control runs.

Discriminator: does the structural signal in R_d come from the divisor
function, the encoding width w, or neither?

Three reals:
  R_d(w=16)        — fixed-width binary, w=16
  R_d(w=8)         — fixed-width binary, w=8 (encoding period halved)
  R_d^shuffle(w=16) — same w=16, but d(n) values randomly permuted
                      (destroys divisor structure, preserves encoding)

For each, run CF and compare:
  - histogram of log2(a_i + 1)
  - spike count (# steps with log2(a+1) > T) for several thresholds
  - top-10 spike loci (in bit-position space, i.e. via 2 * log2 q_i)

If R_d^shuffle has the same spike density as R_d, the structure is
encoding-driven, not divisor-driven.

If R_d(w=8) shows different spike-locus structure than R_d(w=16) when
read in *bit-position* coordinates, the encoding controls the loci.

If R_d^shuffle drops to Khinchin-typical and R_d(w=8/16) agree in
bit-position space, divisor structure is driving the signal.
"""

import csv
import random
import time
from math import log2
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent

N = 10_000
W_LIST = [8, 16]
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


def build_real(seq, w):
    """Pack non-negative ints in seq into a w-bit-per-entry binary fraction."""
    mask = (1 << w) - 1
    num = 0
    for v in seq:
        assert 0 <= v <= mask, f"value {v} does not fit in w={w} bits"
        num = (num << w) | (v & mask)
    den = 1 << (w * len(seq))
    return num, den


def cf_expand(num, den, max_steps):
    """Run CF on num/den < 1. Returns lists of a_i, log2(a+1), log2(q)."""
    a_list = []
    log2a = []
    log2q = []
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
    """For each threshold T, count steps with log2(a+1) > T."""
    return {T: sum(1 for x in log2a if x > T) for T in thresholds}


def khinchin_expected(n_steps, T):
    """Expected count of log2(a + 1) > T for a Gauss-Kuzmin-typical
    real. The condition log2(a + 1) > T means a >= 2**T, and the
    Gauss-Kuzmin survival is P(a >= m) = log2(1 + 1/m), so
    P(a >= 2**T) = log2(1 + 1 / 2**T)."""
    return n_steps * log2(1.0 + 1.0 / (2 ** T))


def main():
    random.seed(SEED)

    print(f"sieving d(n) for n=1..{N}")
    t0 = time.time()
    d = divisor_count_sieve(N)
    seq_d = d[1:]                  # d(1), d(2), ..., d(N)
    seq_shuffle = list(seq_d)
    random.shuffle(seq_shuffle)
    print(f"  done in {time.time()-t0:.2f}s; max d(n) = {max(seq_d)}")

    runs = [
        ("R_d w=16",        seq_d,        16),
        ("R_d w=8",         seq_d,        8),
        ("R_d^shuf w=16",   seq_shuffle,  16),
    ]

    thresholds = [4, 6, 8, 10, 12, 14]
    results = []

    for label, seq, w in runs:
        print(f"\n=== {label} ===")
        max_v = max(seq)
        if max_v >= (1 << w):
            print(f"  SKIPPED — max d(n)={max_v} does not fit in w={w}")
            continue
        t0 = time.time()
        num, den = build_real(seq, w)
        print(f"  built real: {num.bit_length()} bits ({time.time()-t0:.2f}s)")
        t0 = time.time()
        a_list, log2a, log2q = cf_expand(num, den, MAX_CF_STEPS)
        print(f"  CF: {len(a_list)} steps in {time.time()-t0:.2f}s; "
              f"final log2 q = {log2q[-1]:.1f}")
        counts = spike_counts(log2a, thresholds)
        results.append((label, w, log2a, log2q, counts))

    # Spike-count comparison table
    print("\n=== spike density: # steps with log2(a+1) > T (40K steps) ===")
    header = f"{'T':>3}  " + "  ".join(f"{lbl:>16}" for lbl, *_ in results) \
             + "  " + f"{'Khinchin expect':>16}"
    print(header)
    for T in thresholds:
        row = f"{T:>3}  " + "  ".join(
            f"{counts[T]:>16d}" for _, _, _, _, counts in results
        ) + "  " + f"{khinchin_expected(MAX_CF_STEPS, T):>16.1f}"
        print(row)

    # Top-10 spike loci (in bit-position space) for each run
    print("\n=== top 10 spikes per run (bit-position space) ===")
    summary_lines = ["# Erdős–Borwein brief #3 controls", ""]
    summary_lines.append(header)
    for T in thresholds:
        row = f"{T:>3}  " + "  ".join(
            f"{counts[T]:>16d}" for _, _, _, _, counts in results
        ) + "  " + f"{khinchin_expected(MAX_CF_STEPS, T):>16.1f}"
        summary_lines.append(row)
    summary_lines.append("")
    for label, w, log2a, log2q, _ in results:
        summary_lines.append(f"## {label} (w={w}) — top 10 by log2(a+1)")
        top = sorted(enumerate(log2a), key=lambda x: -x[1])[:10]
        summary_lines.append(
            f"  {'i':>6}  {'log2 a+1':>9}  {'log2 q':>9}  "
            f"{'bit pos (≈2 log q)':>20}  {'entry m=bitpos/w':>17}"
        )
        for i, la in top:
            lq = log2q[i]
            bp = 2 * lq
            entry = bp / w
            summary_lines.append(
                f"  {i:>6d}  {la:>9.3f}  {lq:>9.1f}  {bp:>20.1f}  "
                f"{entry:>17.1f}"
            )
        summary_lines.append("")

    # Plot: histogram of log2(a+1) for each run
    fig, axes = plt.subplots(1, len(results), figsize=(5 * len(results), 4),
                             sharey=True)
    if len(results) == 1:
        axes = [axes]
    bins = [i * 0.5 for i in range(0, 41)]
    for ax, (label, w, log2a, _, _) in zip(axes, results):
        ax.hist(log2a, bins=bins, log=True, color="steelblue",
                edgecolor="black", linewidth=0.2)
        ax.set_title(f"{label}")
        ax.set_xlabel("log₂(aᵢ + 1)")
        ax.grid(True, alpha=0.3)
    axes[0].set_ylabel("count (log scale)")
    plt.tight_layout()
    hist_path = HERE / "cf_spikes_controls_hist.png"
    plt.savefig(hist_path, dpi=140)
    print(f"\nwrote {hist_path.name}")

    # Plot: log2(a+1) trace for each run, stacked
    fig, axes = plt.subplots(len(results), 1, figsize=(13, 3 * len(results)),
                             sharex=True)
    if len(results) == 1:
        axes = [axes]
    for ax, (label, w, log2a, _, _) in zip(axes, results):
        ax.plot(log2a, linewidth=0.3, color="steelblue")
        ax.set_title(f"{label}")
        ax.set_ylabel("log₂(aᵢ + 1)")
        ax.grid(True, alpha=0.3)
    axes[-1].set_xlabel("CF index i")
    plt.tight_layout()
    trace_path = HERE / "cf_spikes_controls_trace.png"
    plt.savefig(trace_path, dpi=140)
    print(f"wrote {trace_path.name}")

    summary_path = HERE / "cf_spikes_controls_summary.txt"
    summary_path.write_text("\n".join(summary_lines) + "\n")
    print(f"wrote {summary_path.name}")
    print()
    print("\n".join(summary_lines))


if __name__ == "__main__":
    main()
