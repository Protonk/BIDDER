"""
Erdős-Borwein brief #3, first cut: CF spikes of the divisor-encoded real.

R_d := 0 . [d(1)]_w [d(2)]_w [d(3)]_w ...   (base 2)

where [k]_w is k written as a w-bit unsigned binary string. We compute
R_d as an exact rational num/2^{N*w} and run its continued fraction.

Three predictions to discriminate:
  (1) spike loci track SHCN(m) positions — substrate transparency
      reaches the divisor encoding.
  (2) spike loci track multiples of w — encoding does the work.
  (3) Khinchin-typical — null result, no structural correlation.
"""

import csv
import time
from math import log2
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent

N = 10_000
W = 16
SPIKE_LOG2_THRESHOLD = 5
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


# OEIS A002201 (superior highly composite numbers), up to ~ 10^6
SHCN = [
    1, 2, 4, 6, 12, 24, 36, 48, 60, 120, 180, 240, 360, 720, 840,
    1260, 1680, 2520, 5040, 7560, 10080, 15120, 20160, 25200, 27720,
    45360, 50400, 55440, 83160, 110880, 166320, 221760, 277200, 332640,
    498960, 720720,
]


def main():
    print(f"params: N={N}, W={W}")

    t0 = time.time()
    print(f"sieving d(n) for n=1..{N}")
    d = divisor_count_sieve(N)
    max_d = max(d[1:])
    print(f"  done in {time.time()-t0:.2f}s; max d(n) = {max_d} "
          f"(fits in {max_d.bit_length()} bits)")
    assert max_d < (1 << W), f"W={W} too small for max d(n)={max_d}"

    print("packing R_d numerator")
    t0 = time.time()
    num = 0
    mask = (1 << W) - 1
    for n in range(1, N + 1):
        num = (num << W) | (d[n] & mask)
    den = 1 << (N * W)
    print(f"  num has {num.bit_length()} bits; "
          f"den has {den.bit_length()} bits ({time.time()-t0:.2f}s)")

    print("running continued fraction expansion")
    t0 = time.time()
    a_list = []
    log2a_list = []
    log2q_list = []
    q_prev, q_curr = 0, 1
    A, B = num, den
    step = 0
    while B != 0 and step < MAX_CF_STEPS:
        a, r = divmod(A, B)
        a_list.append(a)
        log2a_list.append(log2_bigint(a + 1))
        q_prev, q_curr = q_curr, a * q_curr + q_prev
        log2q_list.append(log2_bigint(q_curr))
        A, B = B, r
        step += 1
        if step % 5000 == 0:
            print(f"    step {step}: log2(q) = {log2q_list[-1]:.1f}, "
                  f"elapsed {time.time()-t0:.1f}s")
    print(f"  extracted {step} CF steps in {time.time()-t0:.2f}s")

    spike_idx = [i for i, la in enumerate(log2a_list)
                 if la > SPIKE_LOG2_THRESHOLD]
    print(f"  {len(spike_idx)} steps with log2(a+1) > {SPIKE_LOG2_THRESHOLD}")

    # Map SHCN(m) to the first CF index i where log2(q_i) >= m*W/2.
    # This is the CF index at which the convergent has matched ~m*w bits
    # of R_d, i.e. has "reached" the SHCN entry's digit position.
    SHCN_in_range = [m for m in SHCN if m <= N]
    shcn_marks = []
    for m in SHCN_in_range:
        target = m * W / 2.0
        for i, lq in enumerate(log2q_list):
            if lq >= target:
                shcn_marks.append((m, i, lq))
                break

    # Same mapping for w-multiple loci (encoding-inertness control):
    # mark every 64-th entry, i.e. bit positions that are multiples of W
    # but uncorrelated with SHCN structure.
    w_marks = []
    stride = max(64, N // 32)
    for m in range(stride, N + 1, stride):
        target = m * W / 2.0
        for i, lq in enumerate(log2q_list):
            if lq >= target:
                w_marks.append((m, i, lq))
                break

    csv_path = HERE / f"cf_spikes_w{W}_N{N}.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["i", "log2_a_plus_1", "log2_q"])
        for i, (la, lq) in enumerate(zip(log2a_list, log2q_list)):
            writer.writerow([i, f"{la:.6f}", f"{lq:.6f}"])
    print(f"  wrote {csv_path.name}")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8), sharex=True)

    ax1.plot(log2a_list, linewidth=0.4, color="steelblue")
    ax1.set_ylabel("log₂(aᵢ + 1)")
    ax1.set_title(
        f"R_d continued fraction (w={W}, N={N})  "
        f"red = SHCN-mapped CF index"
    )
    for _, idx, _ in shcn_marks:
        ax1.axvline(idx, color="crimson", alpha=0.35, linewidth=0.5)
    ax1.grid(True, alpha=0.3)

    ax2.plot(log2q_list, color="gray", linewidth=0.6, label="log₂ qᵢ")
    ax2.set_ylabel("log₂ qᵢ")
    ax2.set_xlabel("CF index i")
    for m, idx, lq in shcn_marks:
        ax2.axhline(m * W / 2.0, color="crimson", alpha=0.25,
                    linewidth=0.4)
        ax2.axvline(idx, color="crimson", alpha=0.35, linewidth=0.5)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plot_path = HERE / f"cf_spikes_w{W}_N{N}.png"
    plt.savefig(plot_path, dpi=140)
    print(f"  wrote {plot_path.name}")

    # Top spikes summary: which ones land near SHCN-mapped indices?
    top = sorted(enumerate(log2a_list), key=lambda x: -x[1])[:25]
    summary_lines = []
    summary_lines.append(f"# Top 25 spikes (w={W}, N={N})")
    summary_lines.append(
        f"{'i':>7}  {'log2(a+1)':>10}  {'log2(q)':>10}  "
        f"{'nearest SHCN':>13}  {'|Δ bits|':>9}"
    )
    for i, la in top:
        if log2q_list[i] > 0 and SHCN_in_range:
            nearest = min(
                SHCN_in_range,
                key=lambda m: abs(m * W / 2.0 - log2q_list[i]),
            )
            delta = abs(nearest * W / 2.0 - log2q_list[i])
        else:
            nearest, delta = "-", float("nan")
        summary_lines.append(
            f"{i:>7}  {la:>10.3f}  {log2q_list[i]:>10.2f}  "
            f"{str(nearest):>13}  {delta:>9.2f}"
        )

    summary_lines.append("")
    summary_lines.append(f"# SHCN-mapped CF indices (m, i, log2 q_i)")
    for m, idx, lq in shcn_marks:
        la_at = log2a_list[idx] if idx < len(log2a_list) else float("nan")
        # Look at neighbourhood ±5: max log2(a+1) within window
        lo, hi = max(0, idx - 5), min(len(log2a_list), idx + 6)
        local_max = max(log2a_list[lo:hi])
        summary_lines.append(
            f"  m={m:>6d}  i={idx:>6d}  log2 q={lq:>8.2f}  "
            f"log2(a+1) at i = {la_at:>6.2f}  "
            f"max in ±5 = {local_max:>6.2f}"
        )

    summary_path = HERE / f"cf_spikes_w{W}_N{N}_summary.txt"
    summary_path.write_text("\n".join(summary_lines) + "\n")
    print(f"  wrote {summary_path.name}")
    print()
    print("\n".join(summary_lines))


if __name__ == "__main__":
    main()
