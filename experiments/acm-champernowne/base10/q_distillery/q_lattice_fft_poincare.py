"""
q_lattice_fft_poincare.py - the FFT of the cached lattice mapped to the
Poincare disk model of the hyperbolic plane.

Radial transform:  r_disk = tanh(s * r_fft / 2),  inverse  r_fft = 2 atanh(r_disk) / s.
Center of FFT (DC) maps to disk centre; FFT image corner maps to disk
radius ~= 0.995. Beyond that we are outside the FFT and render black.

The angular coordinate is preserved (conformal radial map), so the bright
DC cross of the FFT reads as two diameters of the disk; the discrete
prime-harmonic grid reads as concentric arcs / radial spokes that
compress toward the boundary as r -> 1.
"""

import os
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import map_coordinates


HERE = os.path.dirname(os.path.abspath(__file__))
FIG_INCHES = 24.0
DPI = 200
OUT_SIZE = 4000


def slog(arr, lt=1.0):
    arr = np.asarray(arr, dtype=float)
    return np.sign(arr) * np.log10(1.0 + np.abs(arr) / lt)


def main():
    cache = os.path.join(HERE, 'q_lattice_4000.npy')
    print('Loading cache...')
    grid = np.load(cache)

    print('FFT...')
    t0 = time.time()
    sgrid = slog(grid)
    F = np.fft.fftshift(np.fft.fft2(sgrid))
    log_mag = np.log10(np.abs(F) + 1.0).astype(np.float32)
    print(f'  fft: {time.time() - t0:.2f}s')

    # Mask the DC pixel (it's a one-pixel outlier in dynamic range).
    cy_in, cx_in = log_mag.shape[0] // 2, log_mag.shape[1] // 2
    log_mag[cy_in, cx_in] = np.median(log_mag)

    # Pre-clip into [0, 1] for downstream colormap.
    lo = float(np.percentile(log_mag, 2))
    hi = float(np.percentile(log_mag, 99.5))
    print(f'  log_mag p2-p99.5: [{lo:.3f}, {hi:.3f}]')
    base = np.clip((log_mag - lo) / (hi - lo + 1e-9), 0.0, 1.0).astype(np.float32)

    # Hyperbolic mapping setup.
    H, W = base.shape
    max_r_in = np.sqrt((H / 2) ** 2 + (W / 2) ** 2)  # corner distance from DC
    edge_target = 0.995
    s = 2.0 * np.arctanh(edge_target) / max_r_in
    print(f'  hyperbolic scale s = {s:.6g}   '
          f'(disk r=0.995 ↔ fft corner at {max_r_in:.0f} px)')

    out_mid = OUT_SIZE / 2.0
    R_out = out_mid - 30.0

    print('Building disk coordinates...')
    t0 = time.time()
    yy, xx = np.indices((OUT_SIZE, OUT_SIZE), dtype=np.float32)
    u = (xx - out_mid) / R_out
    v = (yy - out_mid) / R_out
    r = np.sqrt(u * u + v * v)
    inside = r < 0.999
    theta = np.arctan2(v, u)
    r_safe = np.clip(r, 0.0, 0.999)
    d = 2.0 * np.arctanh(r_safe) / s
    src_x = cx_in + d * np.cos(theta)
    src_y = cy_in + d * np.sin(theta)
    print(f'  coords: {time.time() - t0:.2f}s')

    print('Resampling FFT into disk via bilinear...')
    t0 = time.time()
    sampled = map_coordinates(
        base,
        np.array([src_y.ravel(), src_x.ravel()]),
        order=1, mode='constant', cval=0.0,
    ).reshape(OUT_SIZE, OUT_SIZE)
    sampled[~inside] = 0.0
    print(f'  sample: {time.time() - t0:.2f}s')

    out = os.path.join(HERE, 'q_lattice_4000_fft_poincare.png')
    print('Rendering...')
    t0 = time.time()
    fig = plt.figure(figsize=(FIG_INCHES, FIG_INCHES),
                     dpi=DPI, facecolor='black')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(sampled, origin='lower', aspect='auto',
              cmap='inferno', vmin=0.0, vmax=1.0,
              interpolation='nearest')
    ax.set_axis_off()
    fig.savefig(out, facecolor='black', dpi=DPI, pad_inches=0)
    plt.close(fig)
    print(f'  render: {time.time() - t0:.2f}s   '
          f'{os.path.getsize(out) / 1024 / 1024:.1f} MB   '
          f'-> {os.path.basename(out)}')


if __name__ == '__main__':
    main()
