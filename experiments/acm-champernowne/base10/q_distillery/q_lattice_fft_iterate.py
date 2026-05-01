"""
q_lattice_fft_iterate.py - iterate FFT-then-log-magnitude on the lattice.

Operation per step:  img -> fftshift(fft2(img - mean(img)))  ->  log10(|.|+1).

Mean-centring before each FFT keeps DC from dominating the next round.
Each iteration is rendered as a percentile-clipped inferno image at
~5 px / cell (3000 px square output) to keep file sizes manageable.

Question: how many iterations of (FFT, log-magnitude) before the
structure degrades into noise?
"""

import os
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


HERE = os.path.dirname(os.path.abspath(__file__))
N_ITER = 10
FIG_INCHES = 15.0
DPI = 150


def slog(arr, lt=1.0):
    arr = np.asarray(arr, dtype=float)
    return np.sign(arr) * np.log10(1.0 + np.abs(arr) / lt)


def fft_log_mag(img):
    centered = img - img.mean()
    F = np.fft.fftshift(np.fft.fft2(centered))
    return np.log10(np.abs(F) + 1.0).astype(np.float32)


def render(img, out_path):
    lo = float(np.percentile(img, 2))
    hi = float(np.percentile(img, 99))
    fig = plt.figure(figsize=(FIG_INCHES, FIG_INCHES),
                     dpi=DPI, facecolor='black')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(img, origin='lower', aspect='auto',
              cmap='inferno', vmin=lo, vmax=hi,
              interpolation='nearest')
    ax.set_axis_off()
    fig.savefig(out_path, facecolor='black', dpi=DPI, pad_inches=0)
    plt.close(fig)


def stats(img, label):
    lo2 = float(np.percentile(img, 2))
    hi98 = float(np.percentile(img, 98))
    p99 = float(np.percentile(img, 99))
    p1 = float(np.percentile(img, 1))
    std = float(img.std())
    rng = float(img.max() - img.min())
    print(f'{label:>9}: range [{img.min():+.3f}, {img.max():+.3f}]  '
          f'p1-p99 = [{p1:+.3f}, {p99:+.3f}]  '
          f'std={std:.3f}  '
          f'dynamic range (p99-p1)/std = {(p99 - p1) / std:.2f}')


def main():
    cache = os.path.join(HERE, 'q_lattice_4000.npy')
    print('Loading cache...')
    grid = np.load(cache)
    img = slog(grid).astype(np.float32)
    stats(img, 'initial')

    out0 = os.path.join(HERE, 'q_lattice_iter_00.png')
    render(img, out0)
    print(f'  saved {os.path.basename(out0)} '
          f'({os.path.getsize(out0) / 1024 / 1024:.1f} MB)')

    for i in range(1, N_ITER + 1):
        t0 = time.time()
        img = fft_log_mag(img)
        elapsed = time.time() - t0
        stats(img, f'iter {i}')
        out = os.path.join(HERE, f'q_lattice_iter_{i:02d}.png')
        render(img, out)
        print(f'  iter {i}: {elapsed:.1f}s   '
              f'-> {os.path.basename(out)} '
              f'({os.path.getsize(out) / 1024 / 1024:.1f} MB)')


if __name__ == '__main__':
    main()
