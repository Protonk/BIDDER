"""
bent_loom.py - stretch the boundary loom through a hyperbolic strip.

The source fabric is the same aligned boundary loom. Its long direction
is mapped to distance along a geodesic in the Poincare disk, and its
short direction is mapped to perpendicular hyperbolic distance from that
geodesic. The result is a negative-curvature textile: broad in the
middle, compressed toward the ideal boundary.
"""

import os

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import boundary_loom as loom


IMG_SIZE = 2200
T_MAX = 5.25
RHO_MAX = 1.05
COL_REPEAT = 24

BG = loom.hex_rgb('#050505')
EDGE_GLOW = loom.hex_rgb('#20313a')


def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def make_texture():
    lowres = loom.make_lowres_loom().astype(np.float32)
    texture = np.repeat(lowres, COL_REPEAT, axis=1)

    h, w, _ = texture.shape
    yy, xx = np.mgrid[0:h, 0:w]

    warp_phase = (xx % COL_REPEAT) / COL_REPEAT
    weft_phase = (yy % 6) / 6.0
    warp = 0.90 + 0.10 * np.cos((warp_phase - 0.5) * 2.0 * np.pi) ** 2
    weft = 0.95 + 0.05 * np.cos(weft_phase * 2.0 * np.pi)
    texture = np.clip(texture * (warp * weft)[:, :, None], 0.0, 1.0)

    join_col = (loom.BORDER_COLS + loom.HALF_WINDOW) * COL_REPEAT
    texture[:, max(0, join_col - 2):join_col + 3, :] = np.maximum(
        texture[:, max(0, join_col - 2):join_col + 3, :],
        loom.JOIN_ONE * 0.96,
    )

    return texture.astype(np.float32)


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


def render_bent(texture):
    h, w, _ = texture.shape
    yy, xx = np.mgrid[0:IMG_SIZE, 0:IMG_SIZE]
    qx = (xx.astype(np.float64) + 0.5) / IMG_SIZE * 2.0 - 1.0
    qy = (yy.astype(np.float64) + 0.5) / IMG_SIZE * 2.0 - 1.0

    # A small rotation keeps the ideal endpoints off the horizontal axis.
    angle = -0.16
    ca = np.cos(angle)
    sa = np.sin(angle)
    x = ca * qx - sa * qy
    y = sa * qx + ca * qy

    r2 = x * x + y * y
    in_disk = r2 < 0.995 * 0.995

    denom = np.maximum(1.0 - r2, 1e-9)
    x1 = 2.0 * x / denom
    x2 = 2.0 * y / denom

    rho = np.arcsinh(x2)
    cosh_rho = np.sqrt(1.0 + x2 * x2)
    t = np.arcsinh(x1 / cosh_rho)

    in_strip = (
        in_disk
        & (np.abs(t) <= T_MAX)
        & (np.abs(rho) <= RHO_MAX)
    )

    y_src = (t + T_MAX) / (2.0 * T_MAX) * (h - 1)
    x_src = (rho + RHO_MAX) / (2.0 * RHO_MAX) * (w - 1)

    flat_mask = in_strip.ravel()
    sampled = bilinear_sample(texture, y_src.ravel(), x_src.ravel(), flat_mask)

    canvas = np.zeros((IMG_SIZE * IMG_SIZE, 3), dtype=np.float32)
    canvas[:] = BG
    canvas[flat_mask] = sampled[flat_mask]
    canvas = canvas.reshape((IMG_SIZE, IMG_SIZE, 3))

    rho_abs = np.abs(rho)
    t_abs = np.abs(t)

    edge_fade = (
        1.0 - 0.60 * smoothstep(RHO_MAX - 0.12, RHO_MAX, rho_abs)
    )
    end_fade = (
        1.0 - 0.45 * smoothstep(T_MAX - 0.70, T_MAX, t_abs)
    )
    curvature_light = 0.78 + 0.24 / np.cosh(0.36 * t) + 0.06 / np.cosh(rho)
    shade = np.clip(edge_fade * end_fade * curvature_light, 0.0, 1.18)
    canvas[in_strip] = np.clip(canvas[in_strip] * shade[in_strip, None],
                               0.0, 1.0)

    boundary = smoothstep(0.965, 0.995, np.sqrt(r2))
    canvas = (
        canvas * (1.0 - 0.28 * boundary[:, :, None])
        + EDGE_GLOW * (0.22 * boundary[:, :, None])
    )

    outside = ~in_disk
    canvas[outside] = BG * 0.55

    # Add a thin glow along the two ideal endpoints of the central join.
    central = in_strip & (np.abs(rho) < 0.018)
    canvas[central] = np.maximum(canvas[central], loom.JOIN_ONE * 0.92)

    return np.clip(canvas, 0.0, 1.0)


def main():
    print("Building bent boundary loom...")
    texture = make_texture()
    print(f"  texture = {texture.shape[1]} x {texture.shape[0]}")
    img = render_bent(texture)

    out = os.path.join(loom._here, 'bent_loom.png')
    plt.imsave(out, img)
    print(f"-> {out}")


if __name__ == '__main__':
    main()
