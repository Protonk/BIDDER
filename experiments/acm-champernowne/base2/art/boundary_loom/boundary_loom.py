"""
boundary_loom.py - weave boundary stitches into one aligned fabric.

Rows are grouped by monoid. Columns are bit positions around the entry
join, so every monoid shares the same central join thread. The row axis
inside each band is boundary index, compressed by averaging neighboring
boundaries into visible weft threads.
"""

import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..'))                            # base2/
sys.path.insert(0, os.path.join(_here, '..', '..', '..', '..', '..', 'core'))   # core/

from acm_core import acm_n_primes


HALF_WINDOW = 18
WINDOW = 2 * HALF_WINDOW
N_ENTRIES = 1024
ROWS_PER_MONOID = 112
ROW_GUTTER = 5
GROUP_GUTTER = 18

COL_SCALE = 30
ROW_SCALE = 3
BORDER_COLS = 3

DARK = '#0a0a0a'

MONOID_GROUPS = [
    [3, 5, 7, 9, 11, 13, 15, 17],
    [2, 6, 10, 14, 18, 22, 26, 30],
    [4, 12, 20, 28, 36, 44, 52, 60],
    [8, 24, 40, 56, 72, 88, 104, 120],
    [16, 48, 80, 112, 144, 176, 208, 240],
    [32, 96, 160, 224],
    [64, 192],
    [128, 256],
]


def hex_rgb(s):
    s = s.lstrip('#')
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)],
                    dtype=np.float64) / 255.0


LEFT_ZERO = hex_rgb('#020711')
LEFT_ONE = hex_rgb('#2f9bff')
JOIN_ONE = hex_rgb('#fff0a0')
RIGHT_ZERO = hex_rgb('#06140c')
RIGHT_ONE = hex_rgb('#ffba4a')
MISSING = hex_rgb('#1c0808')
GUTTER = hex_rgb('#050505')
RED = hex_rgb('#ff2b1f')

DEPTH_COLORS = [
    hex_rgb('#333333'),
    hex_rgb('#3b5f8a'),
    hex_rgb('#4f8f7a'),
    hex_rgb('#8aa65c'),
    hex_rgb('#d0a445'),
    hex_rgb('#d46b3d'),
    hex_rgb('#b8465a'),
    hex_rgb('#8e4f99'),
    hex_rgb('#6f77b8'),
]


def v2_of(n):
    v = 0
    while n % 2 == 0:
        v += 1
        n //= 2
    return v


def build_stitch(n):
    primes = acm_n_primes(n, N_ENTRIES)
    entries = [[float(ch) for ch in bin(p)[2:]] for p in primes]
    bit_lengths = np.array([len(bits) for bits in entries], dtype=np.int64)

    stitch = np.full((len(entries) - 1, WINDOW), np.nan, dtype=np.float64)

    for i in range(len(entries) - 1):
        left_entry = entries[i]
        right_entry = entries[i + 1]

        for j in range(HALF_WINDOW):
            col = HALF_WINDOW - 1 - j
            idx = len(left_entry) - 1 - j
            if idx >= 0:
                stitch[i, col] = left_entry[idx]

        for j in range(HALF_WINDOW):
            col = HALF_WINDOW + j
            if j < len(right_entry):
                stitch[i, col] = right_entry[j]

    transitions = bit_lengths[:-1] != bit_lengths[1:]
    return stitch, transitions


def compress_rows(stitch, transitions):
    edges = np.linspace(0, stitch.shape[0], ROWS_PER_MONOID + 1)
    edges = np.round(edges).astype(np.int64)

    compressed = np.full((ROWS_PER_MONOID, WINDOW), np.nan, dtype=np.float64)
    transition_strength = np.zeros(ROWS_PER_MONOID, dtype=np.float64)

    for i in range(ROWS_PER_MONOID):
        start = edges[i]
        stop = max(edges[i + 1], start + 1)
        block = stitch[start:stop]
        valid = np.isfinite(block)
        counts = valid.sum(axis=0)
        sums = np.where(valid, block, 0.0).sum(axis=0)
        cols = counts > 0
        compressed[i, cols] = sums[cols] / counts[cols]
        transition_strength[i] = transitions[start:stop].mean()

    return compressed, transition_strength


def colorize_band(compressed, transition_strength, depth):
    rgb = np.zeros((ROWS_PER_MONOID, WINDOW + 2 * BORDER_COLS, 3),
                   dtype=np.float64)
    rgb[:] = GUTTER

    data = rgb[:, BORDER_COLS:BORDER_COLS + WINDOW]
    vals = compressed
    finite = np.isfinite(vals)

    left = finite & (np.arange(WINDOW)[None, :] < HALF_WINDOW)
    join = finite & (np.arange(WINDOW)[None, :] == HALF_WINDOW)
    right = finite & (np.arange(WINDOW)[None, :] > HALF_WINDOW)
    missing = ~finite

    lv = vals[left, None]
    rv = vals[right, None]
    data[left] = (1.0 - lv) * LEFT_ZERO + lv * LEFT_ONE
    data[right] = (1.0 - rv) * RIGHT_ZERO + rv * RIGHT_ONE
    data[join] = JOIN_ONE
    data[missing] = MISSING

    alpha = np.clip(transition_strength * 5.5, 0.0, 0.70)[:, None, None]
    data[:] = (1.0 - alpha) * data + alpha * RED

    depth_color = DEPTH_COLORS[min(depth, len(DEPTH_COLORS) - 1)]
    rgb[:, :BORDER_COLS] = depth_color * 0.55
    rgb[:, -BORDER_COLS:] = depth_color * 0.55

    return rgb


def make_lowres_loom():
    rows = []
    first_group = True

    for group in MONOID_GROUPS:
        if not first_group:
            rows.append(np.full((GROUP_GUTTER, WINDOW + 2 * BORDER_COLS, 3),
                                GUTTER, dtype=np.float64))
        first_group = False

        for n in group:
            print(f"  n = {n}")
            stitch, transitions = build_stitch(n)
            compressed, transition_strength = compress_rows(stitch, transitions)
            rows.append(colorize_band(compressed, transition_strength, v2_of(n)))
            rows.append(np.full((ROW_GUTTER, WINDOW + 2 * BORDER_COLS, 3),
                                GUTTER, dtype=np.float64))

    return np.vstack(rows)


def apply_weave(rgb):
    img = np.repeat(np.repeat(rgb, ROW_SCALE, axis=0), COL_SCALE, axis=1)
    h, w, _ = img.shape
    yy, xx = np.mgrid[0:h, 0:w]

    warp_phase = (xx % COL_SCALE) / COL_SCALE
    weft_phase = (yy % (ROW_SCALE * 4)) / (ROW_SCALE * 4)
    warp = 0.88 + 0.12 * np.cos((warp_phase - 0.5) * 2.0 * np.pi) ** 2
    weft = 0.94 + 0.06 * np.cos(weft_phase * 2.0 * np.pi)
    shade = np.clip(warp * weft, 0.82, 1.08)

    img = np.clip(img * shade[:, :, None], 0.0, 1.0)

    join_center = (BORDER_COLS + HALF_WINDOW) * COL_SCALE + COL_SCALE // 2
    img[:, max(0, join_center - 1):join_center + 2, :] = np.maximum(
        img[:, max(0, join_center - 1):join_center + 2, :],
        JOIN_ONE * 0.95,
    )

    return img


def main():
    print("Building boundary loom...")
    lowres = make_lowres_loom()
    img = apply_weave(lowres)

    fig = plt.figure(frameon=False, figsize=(9, 18), facecolor=DARK)
    ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    ax.set_axis_off()
    fig.add_axes(ax)
    ax.imshow(img, interpolation='nearest', origin='upper', aspect='auto')

    out = os.path.join(_here, 'boundary_loom.png')
    plt.savefig(out, dpi=180, facecolor=DARK, pad_inches=0,
                bbox_inches='tight')
    plt.close(fig)
    print(f"-> {out}")


if __name__ == '__main__':
    main()
