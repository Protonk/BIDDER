"""
Erdős-Borwein brief #3, shuffle-noise band.

cf_spikes_nopad showed R_d^65 has 6 spikes with log2(a+1) > 14 vs
1 for a single shuffle. To determine whether that gap is signal
(divisor structure adding sub-leading high-end spike content) or
shuffle-noise variance, run multiple shuffles and compare R_d^65's
spike counts to the empirical shuffle distribution.

If R_d^65 sits near the median of the shuffle distribution at every
threshold, divisor structure adds nothing to spike density.

If R_d^65 is in the tail (e.g. 95th+ percentile) at some threshold,
that's evidence of a sub-leading divisor contribution at that scale.
"""

import random
import statistics
import time
from math import log2
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent

N = 10_000
BASE = 65
N_SHUFFLES = 32
SEED = 20260429
MAX_CF_STEPS = 40_000
THRESHOLDS = [4, 6, 8, 10, 12, 14, 16]


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
    num = 0
    for v in seq:
        num = num * base + v
    den = base ** len(seq)
    return num, den


def cf_spike_counts(num, den, max_steps, thresholds):
    counts = {T: 0 for T in thresholds}
    A, B = num, den
    step = 0
    while B != 0 and step < max_steps:
        a, r = divmod(A, B)
        la = log2_bigint(a + 1)
        for T in thresholds:
            if la > T:
                counts[T] += 1
        A, B = B, r
        step += 1
    return counts, step


def main():
    random.seed(SEED)
    print(f"sieving d(n) for n=1..{N}")
    d = divisor_count_sieve(N)
    seq_d = d[1:]

    print(f"\n=== R_d^{BASE} (true sequence) ===")
    t0 = time.time()
    num, den = build_real_baseB(seq_d, BASE)
    true_counts, true_steps = cf_spike_counts(
        num, den, MAX_CF_STEPS, THRESHOLDS
    )
    print(f"  CF: {true_steps} steps in {time.time()-t0:.2f}s")
    print(f"  spike counts: {true_counts}")

    print(f"\n=== {N_SHUFFLES} shuffles of d(n) ===")
    shuffle_counts = {T: [] for T in THRESHOLDS}
    t0 = time.time()
    for k in range(N_SHUFFLES):
        seq_shuf = list(seq_d)
        random.shuffle(seq_shuf)
        num_s, den_s = build_real_baseB(seq_shuf, BASE)
        counts, _ = cf_spike_counts(num_s, den_s, MAX_CF_STEPS, THRESHOLDS)
        for T in THRESHOLDS:
            shuffle_counts[T].append(counts[T])
        if (k + 1) % 8 == 0:
            print(f"  done {k+1}/{N_SHUFFLES} ({time.time()-t0:.1f}s elapsed)")

    print(f"\n=== summary ===")
    header = (f"{'T':>3}  {'true':>6}  {'shuf mean':>10}  "
              f"{'shuf sd':>9}  {'shuf min':>9}  {'shuf max':>9}  "
              f"{'rank of true':>13}  {'z-score':>8}")
    print(header)
    summary = ["# Erdős–Borwein brief #3 — shuffle band",
               f"# N={N}, base={BASE}, shuffles={N_SHUFFLES}, "
               f"max CF steps={MAX_CF_STEPS}", "", header]
    for T in THRESHOLDS:
        true_c = true_counts[T]
        sc = shuffle_counts[T]
        m = statistics.mean(sc)
        s = statistics.pstdev(sc) if len(sc) > 1 else 0.0
        mn = min(sc)
        mx = max(sc)
        rank = sum(1 for x in sc if x < true_c)
        z = (true_c - m) / s if s > 0 else float("nan")
        line = (f"{T:>3}  {true_c:>6d}  {m:>10.2f}  {s:>9.2f}  "
                f"{mn:>9d}  {mx:>9d}  {rank:>5d}/{N_SHUFFLES:<6d}  "
                f"{z:>8.2f}")
        print(line)
        summary.append(line)

    fig, ax = plt.subplots(figsize=(10, 5))
    Ts = THRESHOLDS
    means = [statistics.mean(shuffle_counts[T]) for T in Ts]
    stds = [statistics.pstdev(shuffle_counts[T]) for T in Ts]
    true_vals = [true_counts[T] for T in Ts]
    ax.errorbar(Ts, means, yerr=stds, fmt='o-', color='gray',
                label=f'shuffle mean ± sd (n={N_SHUFFLES})',
                capsize=4, markersize=6)
    ax.plot(Ts, true_vals, 's-', color='crimson', label='R_d (true)',
            markersize=6)
    ax.set_yscale('log')
    ax.set_xlabel('threshold T: log₂(aᵢ + 1) > T')
    ax.set_ylabel('count of CF steps (log scale)')
    ax.set_title(f'R_d^{BASE} vs shuffle band (N={N})')
    ax.legend()
    ax.grid(True, alpha=0.3, which='both')
    plt.tight_layout()
    plot_path = HERE / "cf_spikes_shuffle_band.png"
    plt.savefig(plot_path, dpi=140)
    print(f"\nwrote {plot_path.name}")

    summary_path = HERE / "cf_spikes_shuffle_band_summary.txt"
    summary_path.write_text("\n".join(summary) + "\n")
    print(f"wrote {summary_path.name}")


if __name__ == "__main__":
    main()
