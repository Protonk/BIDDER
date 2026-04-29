"""
shuffle_funeral.py - render detrended RDS order as smoke.

The left half uses the original per-entry detrended RDS residual. The
right half uses the same entries after a seeded shuffle. Each monoid
becomes a vertical smoke column. Residual amplitude drives brightness
and lateral displacement; local slope drives curl; zero crossings cut
dark scars through the plume.
"""

import os
import sys
import math
import random

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..'))                            # base2/
sys.path.insert(0, os.path.join(_here, '..', '..', '..', '..', '..', 'core'))   # core/

from acm_core import acm_n_primes


TOTAL_BITS = 100_000
SEED = 12345

PANEL = [
    (3, 0),
    (5, 0),
    (7, 0),
    (2, 1),
    (6, 1),
    (4, 2),
    (12, 2),
    (8, 3),
    (16, 4),
    (32, 5),
    (64, 6),
    (128, 7),
    (256, 8),
]

IMG_W = 2600
IMG_H = 1700
PANE_W = 1120
PANE_GAP = 120
MARGIN_X = 120
MARGIN_Y = 95
PLUME_H = IMG_H - 2 * MARGIN_Y

OUT = os.path.join(_here, 'shuffle_funeral.png')
DARK = np.array([0.008, 0.006, 0.006], dtype=np.float64)


def hex_rgb(s):
    s = s.lstrip('#')
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)],
                    dtype=np.float64) / 255.0


DEPTH_COLORS = [
    hex_rgb('#88d8b0'),
    hex_rgb('#6ec6ff'),
    hex_rgb('#5da4ff'),
    hex_rgb('#8fbf6a'),
    hex_rgb('#ffcc5c'),
    hex_rgb('#f5a04c'),
    hex_rgb('#ff6f61'),
    hex_rgb('#c55f95'),
    hex_rgb('#9a84d6'),
]


def v2_of(n):
    v = 0
    while n % 2 == 0:
        v += 1
        n //= 2
    return v


def slope_for_entry(m, d):
    if m == 0:
        return 1.0
    if d <= 2 * m:
        return 1.0 - m
    return 1.0 - 2.0 * m + (m * (2 ** m)) / (2 ** m - 1)


def estimate_count(n, target_bits):
    avg = math.log2(max(n, 2)) + math.log2(max(target_bits // 20, 4))
    return int(target_bits / max(avg, 4)) + 200


def gen_for_monoid(n, target_bits):
    count = estimate_count(n, target_bits)
    while True:
        primes = acm_n_primes(n, 2 * count)
        cum = 0
        used = []
        for p in primes:
            d = p.bit_length()
            if cum + d > target_bits:
                break
            cum += d
            used.append(p)
        if used and cum >= target_bits - 200:
            return bits_from_entries(used), used
        count *= 2


def bits_from_entries(entries):
    bits = []
    for p in entries:
        for c in bin(p)[2:]:
            bits.append(int(c))
    return np.array(bits, dtype=np.int8)


def compute_rds(bits):
    pm = 2 * bits.astype(np.int64) - 1
    return np.concatenate(([0], np.cumsum(pm)))


def expected_curve_per_entry(entries, n_bits):
    ds = np.array([p.bit_length() for p in entries], dtype=np.int64)
    ms = np.array([v2_of(int(p)) for p in entries], dtype=np.int64)
    slopes = np.array([slope_for_entry(int(m), int(d))
                       for m, d in zip(ms, ds)], dtype=np.float64)
    cum_bits = np.concatenate(([0], np.cumsum(ds))).astype(np.float64)
    cum_expected = np.concatenate(([0.0], np.cumsum(slopes)))
    return np.interp(np.arange(n_bits + 1, dtype=np.float64),
                     cum_bits, cum_expected)


def residual_for_entries(entries):
    bits = bits_from_entries(entries)
    rds = compute_rds(bits).astype(np.float64)
    expected = expected_curve_per_entry(entries, len(bits))
    return rds - expected


def smooth(y, radius):
    if radius <= 0:
        return y
    x = np.arange(-radius, radius + 1, dtype=np.float64)
    kernel = np.exp(-0.5 * (x / max(radius / 2.5, 1.0)) ** 2)
    kernel /= kernel.sum()
    return np.convolve(y, kernel, mode='same')


def resample_curve(curve, n_samples):
    xs = np.linspace(0, len(curve) - 1, n_samples)
    return np.interp(xs, np.arange(len(curve)), curve)


def color_for_depth(depth, shuffled):
    base = DEPTH_COLORS[min(depth, len(DEPTH_COLORS) - 1)]
    if not shuffled:
        return base
    grey = np.array([0.56, 0.58, 0.58], dtype=np.float64)
    return 0.82 * grey + 0.18 * base


def add_plume(canvas, curve, center_x, depth, global_scale, shuffled=False):
    raw = resample_curve(curve, PLUME_H)
    raw = smooth(raw, 10)
    norm = raw / global_scale

    mag = np.clip(np.abs(norm), 0.0, 1.45)
    deriv = smooth(np.gradient(norm), 7)
    deriv_scale = np.percentile(np.abs(deriv), 95) + 1e-6
    slope = np.clip(deriv / deriv_scale, -2.0, 2.0)

    phase = np.cumsum(slope) * (0.12 if shuffled else 0.18) + depth * 0.7
    curl = np.sin(phase) * (9.0 if shuffled else 15.0) * (0.25 + mag)
    drift = norm * (42.0 if shuffled else 58.0)
    x_centers = center_x + drift + curl

    base_width = 11.0 if shuffled else 8.5
    widths = base_width + (26.0 if shuffled else 18.0) * mag
    brightness = (mag ** 0.62) * (0.70 if shuffled else 1.20)
    brightness += (np.abs(slope) ** 0.8) * (0.020 if shuffled else 0.035)

    color = color_for_depth(depth, shuffled)

    for j in range(PLUME_H):
        y = IMG_H - MARGIN_Y - 1 - j
        sigma = widths[j]
        half = int(max(4, min(95, 3.0 * sigma)))
        xc = x_centers[j]
        x0 = max(0, int(xc) - half)
        x1 = min(IMG_W - 1, int(xc) + half)
        if x1 <= x0:
            continue
        xs = np.arange(x0, x1 + 1, dtype=np.float64)
        g = np.exp(-0.5 * ((xs - xc) / sigma) ** 2)
        a = brightness[j] * g
        if shuffled:
            a *= 0.55 + 0.25 * (j / PLUME_H)
        else:
            a *= 0.80 + 0.35 * (j / PLUME_H)
        canvas[y, x0:x1 + 1] += a[:, None] * color[None, :]

    signs = np.sign(raw)
    crossings = np.where(signs[:-1] * signs[1:] < 0)[0]
    scar_half = 48 if shuffled else 56
    for j in crossings:
        y = IMG_H - MARGIN_Y - 1 - j
        x0 = max(0, int(center_x) - scar_half)
        x1 = min(IMG_W, int(center_x) + scar_half)
        y0 = max(0, y - 1)
        y1 = min(IMG_H, y + 2)
        canvas[y0:y1, x0:x1] *= 0.20 if not shuffled else 0.34


def add_panel_frame(canvas, x0, x1, original):
    tint = hex_rgb('#20342c') if original else hex_rgb('#2b2f32')
    canvas[MARGIN_Y - 22:MARGIN_Y - 16, x0:x1] += tint * 0.18
    canvas[IMG_H - MARGIN_Y + 16:IMG_H - MARGIN_Y + 22, x0:x1] += tint * 0.18


def render(results):
    canvas = np.zeros((IMG_H, IMG_W, 3), dtype=np.float64)
    canvas[:] = DARK

    left_x0 = MARGIN_X
    left_x1 = left_x0 + PANE_W
    right_x0 = left_x1 + PANE_GAP
    right_x1 = right_x0 + PANE_W

    add_panel_frame(canvas, left_x0, left_x1, original=True)
    add_panel_frame(canvas, right_x0, right_x1, original=False)

    n_cols = len(results)
    left_centers = np.linspace(left_x0 + 45, left_x1 - 45, n_cols)
    right_centers = np.linspace(right_x0 + 45, right_x1 - 45, n_cols)

    global_scale = max(
        np.max(np.abs(r['residual'])) for r in results
    )

    for i, r in enumerate(results):
        add_plume(canvas, r['residual'], left_centers[i], r['m'],
                  global_scale, shuffled=False)
    for i, r in enumerate(results):
        add_plume(canvas, r['shuffled'], right_centers[i], r['m'],
                  global_scale, shuffled=True)

    yy, xx = np.mgrid[0:IMG_H, 0:IMG_W]
    cx = IMG_W / 2.0
    cy = IMG_H / 2.0
    dist = ((xx - cx) / (IMG_W * 0.55)) ** 2 + ((yy - cy) / (IMG_H * 0.62)) ** 2
    vignette = np.clip(1.10 - 0.58 * dist, 0.35, 1.05)

    canvas = 1.0 - np.exp(-canvas * 1.35)
    canvas *= vignette[:, :, None]
    canvas = np.clip(canvas, 0.0, 1.0)

    return canvas


def compute_results():
    random.seed(SEED)
    np.random.seed(SEED)

    results = []
    print(f"Computing shuffle funeral residuals, target {TOTAL_BITS} bits")
    for n, expected_m in PANEL:
        m = v2_of(n)
        assert m == expected_m
        bits, entries = gen_for_monoid(n, TOTAL_BITS)
        rds = compute_rds(bits).astype(np.float64)
        expected = expected_curve_per_entry(entries, len(bits))
        residual = rds - expected

        shuffled_entries = list(entries)
        random.shuffle(shuffled_entries)
        shuffled = residual_for_entries(shuffled_entries)

        results.append({
            'n': n,
            'm': m,
            'residual': residual,
            'shuffled': shuffled,
        })
        print(f"  n={n:4d}  v2={m}  bits={len(bits):6d}  "
              f"|res|max={np.max(np.abs(residual)):7.1f}  "
              f"|shuf|max={np.max(np.abs(shuffled)):7.1f}")
    return results


def main():
    results = compute_results()
    print("Rendering smoke diptych...")
    img = render(results)
    plt.imsave(OUT, img)
    print(f"-> {OUT}")


if __name__ == '__main__':
    main()
