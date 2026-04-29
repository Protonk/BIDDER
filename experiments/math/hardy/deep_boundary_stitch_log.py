#!/usr/bin/env python3
"""Single-pane boundary stitch with log-scaled boundary axis.

This is the left-pane version of the Hardy Echo boundary-stitch image.
Defaults are n=2, deep K around 10^6, and about 10^4 consecutive
boundaries.
"""

from __future__ import annotations

import argparse
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)

from experiments.math.hardy.hardy_echo import boundary_stitch_window, window


N = 2
K0 = 10**6
BOUNDARIES = 10**4
ENTRIES = BOUNDARIES + 1
HALF_WIDTH = 8

OUT = os.path.join(os.path.dirname(__file__), "exp2_boundary_stitch_deep_log.png")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=N)
    parser.add_argument("--k0", type=int, default=K0)
    parser.add_argument("--boundaries", type=int, default=BOUNDARIES)
    parser.add_argument("--half-width", type=int, default=HALF_WIDTH)
    parser.add_argument("--out", default=OUT)
    parser.add_argument(
        "--trailing-bit-only",
        action="store_true",
        help="Plot only the final trailing bit immediately left of the join.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    entries = args.boundaries + 1

    print(
        f"Building n={args.n} boundary stitch at K0={args.k0}, "
        f"boundaries={args.boundaries}, half_width={args.half_width}",
        flush=True,
    )
    img = boundary_stitch_window(
        window(args.n, args.k0, entries),
        half_width=args.half_width,
        base=2,
    )

    barcode_col = args.half_width - 1
    if args.trailing_bit_only:
        plot_img = img[:, barcode_col:barcode_col + 1]
        x_edges = np.array([-0.5, 0.5])
    else:
        plot_img = img
        x_edges = np.arange(2 * args.half_width + 1) - 0.5
    y_edges = np.arange(1, args.boundaries + 2)

    fig_width = 2.2 if args.trailing_bit_only else 6.2
    fig, ax = plt.subplots(figsize=(fig_width, 8.8))
    ax.pcolormesh(
        x_edges,
        y_edges,
        plot_img,
        cmap="gray_r",
        vmin=0,
        vmax=1,
        shading="flat",
        antialiased=False,
    )
    ax.set_yscale("log")
    ax.set_ylim(1, args.boundaries + 1)
    ax.invert_yaxis()
    if not args.trailing_bit_only:
        ax.axvline(args.half_width - 0.5, color="red", lw=0.7)

    if args.trailing_bit_only:
        title = (
            f"Trailing bit only — n={args.n}, "
            f"K=[{args.k0}, +{args.boundaries}]"
        )
        xlabel = "relative bit -1"
        ax.set_xticks([0])
        ax.set_xticklabels(["-1"])
    else:
        title = (
            f"Boundary stitch — n={args.n}, "
            f"K=[{args.k0}, +{args.boundaries}], log boundary axis"
        )
        xlabel = "bit position relative to join (left=trailing, right=leading)"
        ax.set_xticks(range(0, 2 * args.half_width, 2))
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("boundary offset from K0 (log scale)")
    ax.set_yticks([1, 10, 100, 1000, 10000])
    ax.set_yticklabels(["1", "10", "100", "1000", "10000"])

    fig.tight_layout()
    fig.savefig(args.out, dpi=180)
    plt.close(fig)

    one_rate = float(np.mean(img[:, barcode_col]))
    print(f"trailing-zero barcode column {barcode_col} one-rate: {one_rate:.6f}")
    print(f"-> {args.out}")


if __name__ == "__main__":
    main()
