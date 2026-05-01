"""
q_lattice_fft.py - 2D FFT of the cached 4000 x 4000 Q lattice.

Loads slog(Q) from the cached array, takes fft2, fftshift, log-magnitude,
percentile-clipped, full-bleed render. Produces:

  q_lattice_4000_fft.png       - full spectrum, 8000 x 8000 px
  q_lattice_4000_fft_zoom.png  - center 800 x 800 frequency window
                                 (low-frequency / large-period structure)
"""

import os
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


HERE = os.path.dirname(os.path.abspath(__file__))
FIG_INCHES = 24.0
DPI = 250


def slog(arr, lt=1.0):
    arr = np.asarray(arr, dtype=float)
    return np.sign(arr) * np.log10(1.0 + np.abs(arr) / lt)


def percentile_render(img, out_path, lo_pct=2, hi_pct=99,
                      cmap='inferno', fig_inches=FIG_INCHES, dpi=DPI):
    lo = float(np.percentile(img, lo_pct))
    hi = float(np.percentile(img, hi_pct))
    fig = plt.figure(figsize=(fig_inches, fig_inches),
                     dpi=dpi, facecolor='black')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(img, origin='lower', aspect='auto',
              cmap=cmap, vmin=lo, vmax=hi,
              interpolation='nearest')
    ax.set_axis_off()
    fig.savefig(out_path, facecolor='black', dpi=dpi, pad_inches=0)
    plt.close(fig)
    return lo, hi


def main():
    cache = os.path.join(HERE, 'q_lattice_4000.npy')
    if not os.path.exists(cache):
        print('No cache.')
        return

    print('Loading cached grid...')
    t0 = time.time()
    grid = np.load(cache)
    print(f'  shape {grid.shape}, loaded in {time.time() - t0:.2f}s')

    print('Applying slog...')
    sgrid = slog(grid)

    print('Computing 2D FFT...')
    t0 = time.time()
    F = np.fft.fft2(sgrid)
    F = np.fft.fftshift(F)
    mag = np.abs(F)
    print(f'  fft + shift + abs: {time.time() - t0:.2f}s')
    print(f'  magnitude range: {mag.min():.3g} .. {mag.max():.3g}')

    log_mag = np.log10(mag + 1.0)
    print(f'  log10(1+mag) range: {log_mag.min():.3g} .. {log_mag.max():.3g}')

    # Full spectrum.
    out_full = os.path.join(HERE, 'q_lattice_4000_fft.png')
    print('Rendering full spectrum...')
    t0 = time.time()
    lo, hi = percentile_render(log_mag, out_full, lo_pct=2, hi_pct=99)
    print(f'  p2={lo:.3f}  p99={hi:.3f}  '
          f'render {time.time() - t0:.1f}s   '
          f'{os.path.getsize(out_full) / 1024 / 1024:.1f} MB   '
          f'-> {os.path.basename(out_full)}')

    # Zoomed center: low frequency / large-period structure lives here.
    h, w = log_mag.shape
    cy, cx = h // 2, w // 2
    z = 400
    zoom = log_mag[cy - z:cy + z, cx - z:cx + z]
    out_zoom = os.path.join(HERE, 'q_lattice_4000_fft_zoom.png')
    print('Rendering centre zoom (800 x 800 frequency window)...')
    t0 = time.time()
    lo, hi = percentile_render(zoom, out_zoom, lo_pct=2, hi_pct=99)
    print(f'  p2={lo:.3f}  p99={hi:.3f}  '
          f'render {time.time() - t0:.1f}s   '
          f'{os.path.getsize(out_zoom) / 1024 / 1024:.1f} MB   '
          f'-> {os.path.basename(out_zoom)}')


if __name__ == '__main__':
    main()
