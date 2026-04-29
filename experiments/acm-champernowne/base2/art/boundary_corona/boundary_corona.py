"""
boundary_corona.py - wrap entry-boundary stitches into polar plates.

Each plate is one monoid n. Angle is boundary index, radius is bit
position relative to the entry join. The join itself becomes a bright
ring, the forced trailing zero block becomes dark annuli just inside
that ring, and bit-length transitions become red radial glints.
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


# Data resolution
HALF_WINDOW = 18
WINDOW = 2 * HALF_WINDOW
N_ENTRIES = 2048

# Image geometry
PLATE_SIZE = 560
R_INNER = 44.0
R_OUTER = 264.0
TRANSITION_PAD = 2

MONOIDS = [3, 5, 6, 2, 4, 8, 12, 16, 32, 64, 128, 256]

DARK = '#0a0a0a'


def v2_of(n):
    v = 0
    while n % 2 == 0:
        v += 1
        n //= 2
    return v


def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


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
    if TRANSITION_PAD > 0:
        padded = transitions.copy()
        for k in range(1, TRANSITION_PAD + 1):
            padded[k:] |= transitions[:-k]
            padded[:-k] |= transitions[k:]
        transitions = padded

    return stitch, transitions


def render_plate(stitch, transitions):
    yy, xx = np.mgrid[0:PLATE_SIZE, 0:PLATE_SIZE]
    c = (PLATE_SIZE - 1) / 2.0
    dx = xx.astype(np.float64) - c
    dy = yy.astype(np.float64) - c
    radius = np.sqrt(dx * dx + dy * dy)

    # Put the angular seam at six o'clock.
    theta = (np.arctan2(dy, dx) + np.pi / 2.0) % (2.0 * np.pi)
    row = (theta / (2.0 * np.pi) * stitch.shape[0]).astype(np.int64)
    row = np.clip(row, 0, stitch.shape[0] - 1)

    col = ((radius - R_INNER) / (R_OUTER - R_INNER) * WINDOW).astype(np.int64)
    in_annulus = (radius >= R_INNER) & (radius < R_OUTER)
    col = np.clip(col, 0, WINDOW - 1)

    values = np.full((PLATE_SIZE, PLATE_SIZE), np.nan, dtype=np.float64)
    values[in_annulus] = stitch[row[in_annulus], col[in_annulus]]

    left = in_annulus & (col < HALF_WINDOW)
    join = in_annulus & (col == HALF_WINDOW)
    right = in_annulus & (col > HALF_WINDOW)
    nan = in_annulus & np.isnan(values)

    rgb = np.zeros((PLATE_SIZE, PLATE_SIZE, 3), dtype=np.float64)

    left_zero = np.array([0.002, 0.006, 0.012])
    left_one = np.array([0.12, 0.50, 0.88])
    join_one = np.array([1.00, 0.88, 0.36])
    right_zero = np.array([0.006, 0.020, 0.016])
    right_one = np.array([0.98, 0.62, 0.22])
    missing = np.array([0.10, 0.018, 0.018])

    finite_left = left & np.isfinite(values)
    finite_right = right & np.isfinite(values)
    finite_join = join & np.isfinite(values)

    lv = values[finite_left, None]
    rv = values[finite_right, None]

    rgb[finite_left] = (1.0 - lv) * left_zero + lv * left_one
    rgb[finite_right] = (1.0 - rv) * right_zero + rv * right_one
    rgb[finite_join] = join_one
    rgb[nan] = missing

    transition_pixels = in_annulus & transitions[row]
    rgb[transition_pixels] = (
        0.58 * rgb[transition_pixels]
        + 0.42 * np.array([1.00, 0.12, 0.08])
    )

    # Soft physical edge without blurring the exact stitch cells.
    inner_fade = smoothstep(R_INNER, R_INNER + 10.0, radius)
    outer_fade = 1.0 - smoothstep(R_OUTER - 10.0, R_OUTER, radius)
    alpha = np.clip(inner_fade * outer_fade, 0.0, 1.0)
    rgb *= alpha[:, :, None]

    return rgb


def main():
    print("Building boundary coronas...")
    plates = []
    for n in MONOIDS:
        print(f"  n = {n}")
        stitch, transitions = build_stitch(n)
        plates.append((n, render_plate(stitch, transitions)))

    fig, axes = plt.subplots(3, 4, figsize=(16, 12), facecolor=DARK)
    for ax, (n, plate) in zip(axes.flat, plates):
        ax.set_facecolor(DARK)
        ax.imshow(plate, interpolation='nearest', origin='lower')
        ax.set_axis_off()
        ax.text(
            0.5, -0.035, f"n={n}   $\\nu_2$={v2_of(n)}",
            transform=ax.transAxes,
            ha='center', va='top',
            color='white', fontsize=11,
        )

    plt.subplots_adjust(left=0.015, right=0.985, top=0.985, bottom=0.045,
                        wspace=0.02, hspace=0.13)
    out = os.path.join(_here, 'boundary_corona.png')
    plt.savefig(out, dpi=180, facecolor=DARK)
    plt.close(fig)
    print(f"-> {out}")


if __name__ == '__main__':
    main()
