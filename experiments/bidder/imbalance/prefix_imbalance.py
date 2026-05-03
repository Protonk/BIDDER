"""
Order-sensitive prefix imbalance for an exact-balanced digit block.

The block [1000, 9999] has exactly 1000 integers with each leading digit
1 through 9. Endpoint counts are therefore uninformative about order. This
experiment compares lexicographic order, BIDDER keyed orders, and random
permutation baselines by measuring the worst standardized prefix imbalance.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DIST = os.path.join(ROOT, "dist")
sys.path.insert(0, DIST)
sys.path.insert(0, ROOT)

if os.environ.get("BIDDER_IMBALANCE_FORCE_PY") == "1":
    import bidder

    BACKEND = "bidder"
else:
    try:
        import bidder_c as bidder

        BACKEND = "bidder_c"
    except ImportError:
        import bidder

        BACKEND = "bidder"

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


BG = "#0a0a0a"
FG = "white"
YELLOW = "#ffcc5c"
BLUE = "#6ec6ff"
RED = "#ff6f61"
GREEN = "#88d8b0"
GRID = "#333333"

BASE = 10
DIGIT_CLASS = 4
PER_DIGIT = BASE ** (DIGIT_CLASS - 1)
N_DIGITS = BASE - 1
PERIOD = N_DIGITS * PER_DIGIT

N_RANDOM = 256
N_BIDDER_KEYS = 64
RNG_SEED = 20260503
KEY_PREFIX = b"bidder-prefix-imbalance-v1"


def lexicographic_labels():
    return np.repeat(np.arange(1, BASE, dtype=np.int16), PER_DIGIT)


def bidder_labels(key):
    block = bidder.cipher(period=PERIOD, key=key)
    indices = np.fromiter((int(block.at(i)) for i in range(PERIOD)), dtype=np.int64, count=PERIOD)
    return (indices // PER_DIGIT + 1).astype(np.int16)


def random_labels(rng):
    return (rng.permutation(PERIOD) // PER_DIGIT + 1).astype(np.int16)


def prefix_imbalance(labels):
    t = np.arange(1, PERIOD, dtype=np.float64)
    p = 1.0 / N_DIGITS
    expected = t * p
    variance = t * p * (1.0 - p) * (PERIOD - t) / (PERIOD - 1)
    sd = np.sqrt(variance)

    z_by_digit = np.empty((N_DIGITS, PERIOD - 1), dtype=np.float64)
    for row, digit in enumerate(range(1, BASE)):
        counts = np.cumsum(labels == digit, dtype=np.int32)[:-1].astype(np.float64)
        z_by_digit[row] = np.abs(counts - expected) / sd

    path = z_by_digit.max(axis=0)
    digit_at_prefix = z_by_digit.argmax(axis=0) + 1
    i = int(path.argmax())

    return {
        "path": path,
        "dmax": float(path[i]),
        "t_at_max": i + 1,
        "digit_at_max": int(digit_at_prefix[i]),
        "endpoint_counts": np.bincount(labels, minlength=BASE)[1:BASE],
    }


def style_axis(ax):
    ax.set_facecolor(BG)
    ax.tick_params(colors=FG, labelsize=9)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.grid(True, color=GRID, linewidth=0.6, alpha=0.55)


def quantile_line(values):
    q = np.percentile(values, [5, 50, 95, 99])
    return (
        f"min={values.min():.3f}, p05={q[0]:.3f}, median={q[1]:.3f}, "
        f"p95={q[2]:.3f}, p99={q[3]:.3f}, max={values.max():.3f}"
    )


def write_summary(path, lex, bid, bidder_dmax, random_dmax):
    with open(path, "w", encoding="utf-8") as f:
        f.write("Prefix imbalance experiment\n")
        f.write("============================\n\n")
        f.write(f"backend: {BACKEND}\n")
        f.write(f"base: {BASE}\n")
        f.write(f"digit_class: {DIGIT_CLASS}\n")
        f.write(f"period: {PERIOD}\n")
        f.write(f"per_digit_count: {PER_DIGIT}\n")
        f.write(f"bidder_keys: {N_BIDDER_KEYS}\n")
        f.write(f"random_permutations: {N_RANDOM}\n")
        f.write(f"random_seed: {RNG_SEED}\n\n")

        f.write("Worst finite-population standardized prefix imbalance:\n")
        f.write(
            "  lexicographic: "
            f"Dmax={lex['dmax']:.3f} at t={lex['t_at_max']} "
            f"(digit {lex['digit_at_max']})\n"
        )
        f.write(
            "  BIDDER:        "
            f"Dmax={bid['dmax']:.3f} at t={bid['t_at_max']} "
            f"(digit {bid['digit_at_max']})\n"
        )
        f.write(f"  BIDDER keys:   {quantile_line(bidder_dmax)}\n")
        f.write(f"  random:        {quantile_line(random_dmax)}\n\n")

        f.write("Endpoint leading-digit counts:\n")
        f.write(f"  lexicographic: {lex['endpoint_counts'].tolist()}\n")
        f.write(f"  BIDDER:        {bid['endpoint_counts'].tolist()}\n")


def main():
    rng = np.random.default_rng(RNG_SEED)

    lex = prefix_imbalance(lexicographic_labels())
    bid = prefix_imbalance(bidder_labels(KEY_PREFIX + b":000"))

    bidder_paths = []
    bidder_dmax = []
    for i in range(N_BIDDER_KEYS):
        key = KEY_PREFIX + f":{i:03d}".encode("ascii")
        res = prefix_imbalance(bidder_labels(key))
        bidder_paths.append(res["path"])
        bidder_dmax.append(res["dmax"])

    random_paths = []
    random_dmax = []
    for _ in range(N_RANDOM):
        res = prefix_imbalance(random_labels(rng))
        random_paths.append(res["path"])
        random_dmax.append(res["dmax"])

    bidder_paths = np.vstack(bidder_paths)
    bidder_dmax = np.array(bidder_dmax)
    random_paths = np.vstack(random_paths)
    random_dmax = np.array(random_dmax)
    bidder_p05, bidder_median, bidder_p95 = np.percentile(bidder_paths, [5, 50, 95], axis=0)
    random_p05, random_median, random_p95 = np.percentile(random_paths, [5, 50, 95], axis=0)

    assert np.all(lex["endpoint_counts"] == PER_DIGIT)
    assert np.all(bid["endpoint_counts"] == PER_DIGIT)
    assert bid["dmax"] < 0.2 * lex["dmax"]
    assert bidder_dmax.max() < 0.2 * lex["dmax"]

    t_fraction = np.arange(1, PERIOD, dtype=np.float64) / PERIOD

    fig, (ax0, ax1) = plt.subplots(
        1,
        2,
        figsize=(14, 6),
        gridspec_kw={"width_ratios": [2.2, 1.0]},
        facecolor=BG,
    )
    style_axis(ax0)
    style_axis(ax1)

    ax0.fill_between(t_fraction, random_p05, random_p95, color=GREEN, alpha=0.18, label="random 5-95% band")
    ax0.plot(t_fraction, random_median, color=YELLOW, linewidth=1.8, label="random median")
    ax0.fill_between(t_fraction, bidder_p05, bidder_p95, color=BLUE, alpha=0.12, label="BIDDER 5-95% band")
    ax0.plot(t_fraction, bidder_median, color=BLUE, linewidth=1.2, alpha=0.75, label="BIDDER median")
    ax0.plot(t_fraction, bid["path"], color=BLUE, linewidth=2.0, label="BIDDER key 0")
    ax0.plot(t_fraction, lex["path"], color=RED, linewidth=1.5, label="lexicographic")
    ax0.set_yscale("log")
    ax0.set_xlim(0.0, 1.0)
    ax0.set_ylim(0.45, max(lex["dmax"] * 1.15, random_paths.max() * 1.2))
    ax0.set_title("Prefix imbalance path")
    ax0.set_xlabel("prefix fraction")
    ax0.set_ylabel("max digit |observed - expected| / hypergeometric sd")
    legend0 = ax0.legend(loc="upper right", facecolor=BG, edgecolor=GRID, framealpha=0.95, fontsize=9)
    for text in legend0.get_texts():
        text.set_color(FG)

    upper = max(random_dmax.max(), bidder_dmax.max()) * 1.04
    lower = min(random_dmax.min(), bidder_dmax.min()) * 0.96
    bins = np.linspace(lower, upper, 26)
    ax1.hist(random_dmax, bins=bins, color=GREEN, alpha=0.58, edgecolor=BG, label="random")
    ax1.hist(bidder_dmax, bins=bins, color=BLUE, alpha=0.42, edgecolor=BG, label="BIDDER keys")
    ax1.axvline(bid["dmax"], color=BLUE, linewidth=2.2, label=f"BIDDER key 0 {bid['dmax']:.2f}")
    ax1.set_title("Worst prefix imbalance")
    ax1.set_xlabel("Dmax")
    ax1.set_ylabel("samples")
    ax1.text(
        0.04,
        0.96,
        f"lexicographic Dmax={lex['dmax']:.1f}\noutside this scale",
        color=RED,
        transform=ax1.transAxes,
        va="top",
        ha="left",
        fontsize=9,
    )
    legend1 = ax1.legend(loc="upper right", facecolor=BG, edgecolor=GRID, framealpha=0.95, fontsize=9)
    for text in legend1.get_texts():
        text.set_color(FG)

    fig.suptitle("Exact endpoint balance can hide order imbalance", color=FG, fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.95))

    png_path = os.path.join(HERE, "prefix_imbalance.png")
    csv_path = os.path.join(HERE, "prefix_imbalance_paths.csv")
    summary_path = os.path.join(HERE, "prefix_imbalance_summary.txt")
    fig.savefig(png_path, dpi=180, facecolor=BG)
    plt.close(fig)

    np.savetxt(
        csv_path,
        np.column_stack(
            [
                t_fraction,
                lex["path"],
                bid["path"],
                bidder_median,
                bidder_p05,
                bidder_p95,
                random_median,
                random_p05,
                random_p95,
            ]
        ),
        delimiter=",",
        header=(
            "prefix_fraction,lexicographic,bidder_key0,bidder_median,"
            "bidder_p05,bidder_p95,random_median,random_p05,random_p95"
        ),
        comments="",
    )
    write_summary(summary_path, lex, bid, bidder_dmax, random_dmax)

    print(f"backend={BACKEND}")
    print(f"wrote {png_path}")
    print(f"wrote {csv_path}")
    print(f"wrote {summary_path}")
    print(f"lexicographic Dmax={lex['dmax']:.3f}")
    print(f"BIDDER Dmax={bid['dmax']:.3f}")
    print(
        "BIDDER key Dmax "
        f"median={np.median(bidder_dmax):.3f}, "
        f"p95={np.percentile(bidder_dmax, 95):.3f}, "
        f"max={bidder_dmax.max():.3f}"
    )
    print(
        "random Dmax "
        f"median={np.median(random_dmax):.3f}, "
        f"p95={np.percentile(random_dmax, 95):.3f}, "
        f"max={random_dmax.max():.3f}"
    )


if __name__ == "__main__":
    main()
