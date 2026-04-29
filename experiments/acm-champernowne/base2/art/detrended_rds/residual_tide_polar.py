"""
residual_tide_polar.py - wrap residual tide ribbons into an annulus.

The source image is residual_tide.py's normalized original-order
residual field. Bit position becomes angle. The stacked monoid axis
becomes radius, so the residual tide becomes nested luminous rings.
"""

import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import residual_tide


IMG_SIZE = 2500
R_INNER = 260.0
R_OUTER = 1160.0
OUT = os.path.join(residual_tide.shuffle_funeral._here,
                   'residual_tide_polar.png')
SRC_X0 = residual_tide.MARGIN_X + 85
SRC_X1 = residual_tide.IMG_W - residual_tide.MARGIN_X - 85


def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def bilinear_sample(texture, y, x, mask):
    out = np.zeros((mask.shape[0], 3), dtype=np.float32)
    if not np.any(mask):
        return out

    h, w, _ = texture.shape
    xm = np.clip(x[mask], 0.0, w - 1.001)
    ym = np.clip(y[mask], 0.0, h - 1.001)

    x0 = np.floor(xm).astype(np.int64)
    y0 = np.floor(ym).astype(np.int64)
    x1 = x0 + 1
    y1 = y0 + 1

    wx = (xm - x0).astype(np.float32)
    wy = (ym - y0).astype(np.float32)

    c00 = texture[y0, x0]
    c10 = texture[y0, x1]
    c01 = texture[y1, x0]
    c11 = texture[y1, x1]

    top = c00 * (1.0 - wx[:, None]) + c10 * wx[:, None]
    bottom = c01 * (1.0 - wx[:, None]) + c11 * wx[:, None]
    out[mask] = top * (1.0 - wy[:, None]) + bottom * wy[:, None]
    return out


def polar_wrap(texture):
    h, w, _ = texture.shape

    yy, xx = np.mgrid[0:IMG_SIZE, 0:IMG_SIZE]
    c = (IMG_SIZE - 1) / 2.0
    dx = xx.astype(np.float64) - c
    dy = yy.astype(np.float64) - c
    radius = np.sqrt(dx * dx + dy * dy)

    # Put the time seam at six o'clock.
    theta = (np.arctan2(dy, dx) + np.pi / 2.0) % (2.0 * np.pi)
    radial = (radius - R_INNER) / (R_OUTER - R_INNER)

    in_ring = (radius >= R_INNER) & (radius <= R_OUTER)

    x_src = SRC_X0 + theta / (2.0 * np.pi) * (SRC_X1 - SRC_X0)
    y_src = radial * (h - 1)

    flat_mask = in_ring.ravel()
    sampled = bilinear_sample(texture.astype(np.float32),
                              y_src.ravel(), x_src.ravel(), flat_mask)

    bg = residual_tide.BG.astype(np.float32) * 0.50
    canvas = np.zeros((IMG_SIZE * IMG_SIZE, 3), dtype=np.float32)
    canvas[:] = bg
    canvas[flat_mask] = sampled[flat_mask]
    canvas = canvas.reshape((IMG_SIZE, IMG_SIZE, 3))

    inner_fade = smoothstep(R_INNER, R_INNER + 30.0, radius)
    outer_fade = 1.0 - smoothstep(R_OUTER - 40.0, R_OUTER, radius)
    ring_fade = np.clip(inner_fade * outer_fade, 0.0, 1.0)

    # A small seam shadow keeps the wrap from looking accidentally tiled.
    seam = np.minimum(theta, 2.0 * np.pi - theta)
    seam_px = seam * IMG_SIZE / (2.0 * np.pi)
    seam_shadow = 1.0 - 0.36 * (1.0 - smoothstep(0.0, 15.0, seam_px))

    mid = (R_INNER + R_OUTER) / 2.0
    radial_light = 0.72 + 0.34 / np.cosh((radius - mid) / 420.0)

    canvas *= ring_fade[:, :, None]
    canvas *= seam_shadow[:, :, None]
    canvas *= radial_light[:, :, None]

    outside = ~in_ring
    canvas[outside] = bg

    # Quiet rim lines, just enough to make the annulus physical.
    rim = (
        0.08 * (1.0 - smoothstep(0.0, 10.0, np.abs(radius - R_INNER)))
        + 0.08 * (1.0 - smoothstep(0.0, 10.0, np.abs(radius - R_OUTER)))
    )
    canvas += rim[:, :, None] * np.array([0.30, 0.36, 0.38],
                                         dtype=np.float32)

    return np.clip(canvas, 0.0, 1.0)


def main():
    results = residual_tide.compute_results()
    print("Rendering rectangular residual tide source...")
    texture = residual_tide.render(results)
    print("Wrapping residual tide into polar coordinates...")
    img = polar_wrap(texture)
    plt.imsave(OUT, img)
    print(f"-> {OUT}")


if __name__ == '__main__':
    main()
