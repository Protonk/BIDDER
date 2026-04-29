"""
morlet_scalogram_upper_hyperbolic.py - bend the upper Morlet scalogram.

This is an art renderer for morlet_scalogram_upper.py. It uses the same
n = 3 detrended RDS signal, the same upper half of the log-spaced Morlet
scales, and the same magma purple-to-orange palette. The rectangular
scalogram is sampled through Fermi coordinates around a geodesic in the
Poincare disk, so time runs toward two ideal endpoints and scale becomes
perpendicular hyperbolic distance.
"""

import os
import sys
import math

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import fftconvolve

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..'))                            # base2/
sys.path.insert(0, os.path.join(_here, '..', '..', '..', '..', '..', 'core'))   # core/

from acm_core import acm_n_primes


N = 3
TARGET_BITS = 300_000
N_SCALES = 120
SCALE_MIN = 2.0
SCALE_MAX = 50_000.0
MORLET_W0 = 6.0

IMG_SIZE = 2200
T_MAX = 5.35
RHO_MIN = -0.82
RHO_MAX = 1.18

OUT = os.path.join(_here, 'morlet_scalogram_upper_hyperbolic.png')
BG = np.array([0.002, 0.0015, 0.003], dtype=np.float32)
RIM = np.array([0.18, 0.12, 0.24], dtype=np.float32)


def v2_of(n):
    v = 0
    while n % 2 == 0:
        v += 1
        n //= 2
    return v


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
            bits = []
            for p in used:
                for c in bin(p)[2:]:
                    bits.append(int(c))
            return np.array(bits, dtype=np.int8), used
        count *= 2


def compute_rds(bits):
    pm = 2 * bits.astype(np.int64) - 1
    return np.concatenate(([0], np.cumsum(pm)))


def linear_detrend(y):
    x = np.arange(len(y))
    a, b = np.polyfit(x, y, 1)
    return y - (a * x + b)


def morlet_wavelet(n_points, s, w0=MORLET_W0):
    t = (np.arange(n_points) - (n_points - 1) / 2.0) / s
    norm = (np.pi ** -0.25) / np.sqrt(s)
    return norm * np.exp(1j * w0 * t) * np.exp(-t * t / 2.0)


def cwt_morlet(data, scales, w0=MORLET_W0):
    n = len(data)
    out = np.zeros((len(scales), n), dtype=np.complex128)
    for i, s in enumerate(scales):
        n_pts = min(int(10 * s), n)
        if n_pts < 5:
            n_pts = 5
        if n_pts % 2 == 0:
            n_pts += 1
        wavelet = morlet_wavelet(n_pts, s, w0)
        re = fftconvolve(data, wavelet.real, mode='same')
        im = fftconvolve(data, wavelet.imag, mode='same')
        out[i] = re + 1j * im
    return out


def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def bilinear_sample_scalar(texture, y, x, mask):
    out = np.zeros(mask.shape[0], dtype=np.float32)
    if not np.any(mask):
        return out

    h, w = texture.shape
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

    top = c00 * (1.0 - wx) + c10 * wx
    bottom = c01 * (1.0 - wx) + c11 * wx
    out[mask] = top * (1.0 - wy) + bottom * wy
    return out


def compute_upper_log_power():
    print(f"Generating n = {N} stream of {TARGET_BITS} bits...")
    bits, _entries = gen_for_monoid(N, TARGET_BITS)
    n_bits = len(bits)
    print(f"  bits = {n_bits}")

    rds = compute_rds(bits).astype(np.float64)
    rds_detrended = linear_detrend(rds)

    all_scales = np.geomspace(SCALE_MIN, SCALE_MAX, N_SCALES)
    log_min = np.log10(SCALE_MIN)
    log_max = np.log10(SCALE_MAX)
    log_mid = 0.5 * (log_min + log_max)
    scales = all_scales[np.log10(all_scales) >= log_mid]

    print(f"Computing upper Morlet CWT: {len(scales)} scales "
          f"from {scales.min():.1f} to {scales.max():.1f} bits...")
    cwt = cwt_morlet(rds_detrended, scales)
    log_power = np.log10(np.abs(cwt) ** 2 + 1e-12).astype(np.float32)
    print(f"  log-power range: {log_power.min():.2f} to {log_power.max():.2f}")
    return log_power


def render_hyperbolic(log_power):
    h, w = log_power.shape
    vmin = float(np.percentile(log_power, 1.0))
    vmax = float(np.percentile(log_power, 99.75))
    print(f"Rendering with robust range [{vmin:.2f}, {vmax:.2f}]...")

    yy, xx = np.mgrid[0:IMG_SIZE, 0:IMG_SIZE]
    qx = (xx.astype(np.float64) + 0.5) / IMG_SIZE * 2.0 - 1.0
    qy = (yy.astype(np.float64) + 0.5) / IMG_SIZE * 2.0 - 1.0

    angle = -0.10
    ca = np.cos(angle)
    sa = np.sin(angle)
    x = ca * qx - sa * qy
    y = sa * qx + ca * qy

    r2 = x * x + y * y
    in_disk = r2 < 0.996 * 0.996

    denom = np.maximum(1.0 - r2, 1e-9)
    x1 = 2.0 * x / denom
    x2 = 2.0 * y / denom

    rho = np.arcsinh(x2)
    cosh_rho = np.sqrt(1.0 + x2 * x2)
    t = np.arcsinh(x1 / cosh_rho)

    in_strip = (
        in_disk
        & (np.abs(t) <= T_MAX)
        & (rho >= RHO_MIN)
        & (rho <= RHO_MAX)
    )

    x_src = (t + T_MAX) / (2.0 * T_MAX) * (w - 1)
    y_src = (rho - RHO_MIN) / (RHO_MAX - RHO_MIN) * (h - 1)

    flat_mask = in_strip.ravel()
    sampled = bilinear_sample_scalar(
        log_power, y_src.ravel(), x_src.ravel(), flat_mask
    )

    norm = np.zeros(IMG_SIZE * IMG_SIZE, dtype=np.float32)
    norm[flat_mask] = np.clip(
        (sampled[flat_mask] - vmin) / (vmax - vmin),
        0.0, 1.0,
    )

    cmap = plt.get_cmap('magma')
    rgb = cmap(norm).astype(np.float32)[:, :3]
    rgb[~flat_mask] = BG
    rgb = rgb.reshape((IMG_SIZE, IMG_SIZE, 3))

    lower_edge = smoothstep(RHO_MIN, RHO_MIN + 0.075, rho)
    upper_edge = 1.0 - smoothstep(RHO_MAX - 0.075, RHO_MAX, rho)
    end_fade = 1.0 - 0.45 * smoothstep(T_MAX - 0.90, T_MAX, np.abs(t))
    strip_fade = np.clip(lower_edge * upper_edge * end_fade, 0.0, 1.0)

    curvature_light = 0.74 + 0.30 / np.cosh(0.36 * t) + 0.08 / np.cosh(rho)
    rgb[in_strip] *= np.clip(
        strip_fade[in_strip] * curvature_light[in_strip],
        0.0,
        1.16,
    )[:, None]

    disk_radius = np.sqrt(r2)
    rim = 1.0 - smoothstep(0.985, 0.996, disk_radius)
    rim = np.clip(1.0 - rim, 0.0, 1.0)
    rgb += rim[:, :, None] * RIM[None, None, :] * 0.13

    rgb[~in_disk] = BG * 0.45
    return np.clip(rgb, 0.0, 1.0)


def main():
    log_power = compute_upper_log_power()
    img = render_hyperbolic(log_power)
    plt.imsave(OUT, img)
    print(f"-> {OUT}")


if __name__ == '__main__':
    main()
