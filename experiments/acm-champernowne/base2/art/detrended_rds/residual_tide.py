"""
residual_tide.py - layer per-entry detrended RDS residuals as ribbons.

Only the original-order residual is used. Each monoid is normalized by
its own maximum excursion, so the image emphasizes phase and slow motion
rather than raw amplitude. Color is keyed by v_2(n).
"""

import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import shuffle_funeral


IMG_W = 2600
IMG_H = 1550
MARGIN_X = 150
MARGIN_Y = 120
SAMPLES = IMG_W - 2 * MARGIN_X
OUT = os.path.join(shuffle_funeral._here, 'residual_tide.png')

BG = np.array([0.004, 0.006, 0.008], dtype=np.float64)


def smooth(y, radius):
    if radius <= 0:
        return y
    x = np.arange(-radius, radius + 1, dtype=np.float64)
    kernel = np.exp(-0.5 * (x / max(radius / 2.5, 1.0)) ** 2)
    kernel /= kernel.sum()
    return np.convolve(y, kernel, mode='same')


def compute_results():
    results = []
    print(f"Computing residual tide curves, target {shuffle_funeral.TOTAL_BITS} bits")
    for n, expected_m in shuffle_funeral.PANEL:
        m = shuffle_funeral.v2_of(n)
        assert m == expected_m

        bits, entries = shuffle_funeral.gen_for_monoid(
            n, shuffle_funeral.TOTAL_BITS
        )
        rds = shuffle_funeral.compute_rds(bits).astype(np.float64)
        expected = shuffle_funeral.expected_curve_per_entry(entries, len(bits))
        residual = rds - expected

        samples = shuffle_funeral.resample_curve(residual, SAMPLES)
        samples = smooth(samples, 18)
        scale = np.max(np.abs(samples)) or 1.0
        norm = samples / scale

        results.append({
            'n': n,
            'm': m,
            'norm': norm,
            'max_abs': scale,
        })
        print(f"  n={n:4d}  v2={m}  bits={len(bits):6d}  "
              f"|res|max={scale:7.1f}")
    return results


def add_ribbon(canvas, xs, y_curve, baseline, color, phase, depth):
    n = len(xs)
    mag = np.clip(np.abs((baseline - y_curve) / 96.0), 0.0, 1.5)
    slope = smooth(np.gradient(y_curve), 9)
    slope_scale = np.percentile(np.abs(slope), 95) + 1e-6
    shimmer = 0.82 + 0.18 * np.sin(np.linspace(0, 9.0 * np.pi, n) + phase)
    curl = np.clip(np.abs(slope) / slope_scale, 0.0, 1.8)

    for i in range(n):
        x = int(xs[i])
        if x < 0 or x >= IMG_W:
            continue

        yc = y_curve[i]
        sigma = 5.5 + 10.0 * mag[i] + 2.2 * curl[i]
        half = int(max(12, min(70, 4.0 * sigma)))
        y0 = max(0, int(yc) - half)
        y1 = min(IMG_H - 1, int(yc) + half)
        if y1 <= y0:
            continue

        ys = np.arange(y0, y1 + 1, dtype=np.float64)
        ridge = np.exp(-0.5 * ((ys - yc) / sigma) ** 2)
        ridge_alpha = (0.75 + 0.35 * mag[i]) * shimmer[i]
        for xo, xw in ((x - 1, 0.35), (x, 1.00), (x + 1, 0.35)):
            if 0 <= xo < IMG_W:
                canvas[y0:y1 + 1, xo] += (
                    ridge[:, None] * ridge_alpha * xw * color[None, :]
                )

        # A faint body connects the wave to its quiet baseline, making
        # each residual read as tide rather than as a naked line.
        lo = int(min(yc, baseline))
        hi = int(max(yc, baseline))
        if hi > lo:
            lo = max(0, lo)
            hi = min(IMG_H - 1, hi)
            fill_len = hi - lo + 1
            fade = np.linspace(0.12, 0.02, fill_len)
            if yc > baseline:
                fade = fade[::-1]
            for xo, xw in ((x - 1, 0.25), (x, 1.00), (x + 1, 0.25)):
                if 0 <= xo < IMG_W:
                    canvas[lo:hi + 1, xo] += (
                        fade[:, None] * color[None, :] * 0.40 * xw
                    )

    # Add a few bright foam threads, offset from the main curve.
    offsets = [-18.0, 18.0, -33.0 + depth * 0.7]
    weights = [0.18, 0.16, 0.10]
    for offset, weight in zip(offsets, weights):
        yy = y_curve + offset * np.sin(np.linspace(0, 3.0 * np.pi, n) + phase)
        for i in range(0, n, 2):
            x = int(xs[i])
            y = int(yy[i])
            if 1 <= x < IMG_W - 1 and 1 <= y < IMG_H - 1:
                canvas[y - 1:y + 2, x - 1:x + 2] += color * weight


def render(results):
    canvas = np.zeros((IMG_H, IMG_W, 3), dtype=np.float64)
    canvas[:] = BG

    xs = np.linspace(MARGIN_X, IMG_W - MARGIN_X - 1, SAMPLES)
    baselines = np.linspace(MARGIN_Y + 80, IMG_H - MARGIN_Y - 80,
                            len(results))

    # Draw deep strata first, then shallower curves on top.
    for idx, r in reversed(list(enumerate(results))):
        color = shuffle_funeral.DEPTH_COLORS[
            min(r['m'], len(shuffle_funeral.DEPTH_COLORS) - 1)
        ]
        color = 0.85 * color + 0.15 * np.array([0.95, 0.98, 1.0])
        amp = 80.0 + 4.0 * r['m']
        y_curve = baselines[idx] - amp * r['norm']
        add_ribbon(canvas, xs, y_curve, baselines[idx], color,
                   phase=0.6 * idx, depth=r['m'])

    yy, xx = np.mgrid[0:IMG_H, 0:IMG_W]
    xfade = np.minimum(
        smoothstep(MARGIN_X - 80, MARGIN_X + 80, xx),
        1.0 - smoothstep(IMG_W - MARGIN_X - 80, IMG_W - MARGIN_X + 80, xx),
    )
    yfade = np.minimum(
        smoothstep(MARGIN_Y - 70, MARGIN_Y + 80, yy),
        1.0 - smoothstep(IMG_H - MARGIN_Y - 80, IMG_H - MARGIN_Y + 70, yy),
    )
    fade = np.clip(xfade * yfade, 0.0, 1.0)

    glow = 1.0 - np.exp(-canvas * 1.16)
    glow *= fade[:, :, None]

    vignette = (
        ((xx - IMG_W / 2.0) / (IMG_W * 0.62)) ** 2
        + ((yy - IMG_H / 2.0) / (IMG_H * 0.70)) ** 2
    )
    shade = np.clip(1.10 - 0.42 * vignette, 0.45, 1.08)
    glow *= shade[:, :, None]

    return np.clip(glow, 0.0, 1.0)


def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def main():
    results = compute_results()
    print("Rendering residual tide...")
    img = render(results)
    plt.imsave(OUT, img)
    print(f"-> {OUT}")


if __name__ == '__main__':
    main()
