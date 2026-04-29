"""
shuffle_funeral_polar.py - wrap the shuffle funeral into a circular wake.

This script recomputes the same residual smoke image as shuffle_funeral.py
and samples it as a polar texture: horizontal position becomes angle, and
vertical position becomes radius. Residual time runs outward from the
inner ring.
"""

import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import shuffle_funeral


IMG_SIZE = 2400
R_INNER = 180.0
R_OUTER = 1120.0
OUT = os.path.join(shuffle_funeral._here, 'shuffle_funeral_polar.png')


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

    # Put the rectangular seam at six o'clock.
    theta = (np.arctan2(dy, dx) + np.pi / 2.0) % (2.0 * np.pi)

    in_ring = (radius >= R_INNER) & (radius <= R_OUTER)
    radial = (radius - R_INNER) / (R_OUTER - R_INNER)

    # Bottom of the source image is the beginning of the residual run.
    x_src = theta / (2.0 * np.pi) * (w - 1)
    y_src = (1.0 - radial) * (h - 1)

    flat_mask = in_ring.ravel()
    sampled = bilinear_sample(texture.astype(np.float32),
                              y_src.ravel(), x_src.ravel(), flat_mask)

    bg = shuffle_funeral.DARK.astype(np.float32) * 0.45
    canvas = np.zeros((IMG_SIZE * IMG_SIZE, 3), dtype=np.float32)
    canvas[:] = bg
    canvas[flat_mask] = sampled[flat_mask]
    canvas = canvas.reshape((IMG_SIZE, IMG_SIZE, 3))

    inner_fade = smoothstep(R_INNER, R_INNER + 28.0, radius)
    outer_fade = 1.0 - smoothstep(R_OUTER - 36.0, R_OUTER, radius)
    radial_fade = np.clip(inner_fade * outer_fade, 0.0, 1.0)

    # Keep the angular seams visible as quiet black cuts through the wreath.
    seam = np.minimum(theta, 2.0 * np.pi - theta)
    seam *= IMG_SIZE / (2.0 * np.pi)
    seam_cut = 1.0 - 0.45 * (1.0 - smoothstep(0.0, 13.0, seam))

    vignette = 0.70 + 0.38 / np.cosh((radius - (R_INNER + R_OUTER) / 2.0) / 360.0)
    canvas *= radial_fade[:, :, None]
    canvas *= seam_cut[:, :, None]
    canvas *= vignette[:, :, None]

    outside = ~in_ring
    canvas[outside] = bg

    return np.clip(canvas, 0.0, 1.0)


def main():
    results = shuffle_funeral.compute_results()
    print("Rendering rectangular smoke source...")
    texture = shuffle_funeral.render(results)
    print("Wrapping smoke source into polar coordinates...")
    img = polar_wrap(texture)
    plt.imsave(OUT, img)
    print(f"-> {OUT}")


if __name__ == '__main__':
    main()
