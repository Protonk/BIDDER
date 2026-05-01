"""
q_lattice_iter_10_renders.py - render the iter_10 cache four ways:

  A. inferno + percentile clip (the original, where moire was seen)
  B. inferno + full data range (no clip)
  C. grayscale + percentile clip
  D. grayscale + full data range

If moire disappears in (D) but is present in (A), the colormap and clip
were creating it. If moire persists across all four, it's downstream of
rendering (display sampling, JPEG screenshot, etc).
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


HERE = os.path.dirname(os.path.abspath(__file__))


def render(img, out_path, cmap, vmin, vmax, fig_inches=15, dpi=150):
    fig = plt.figure(figsize=(fig_inches, fig_inches),
                     dpi=dpi, facecolor='black')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(img, origin='lower', aspect='auto',
              cmap=cmap, vmin=vmin, vmax=vmax,
              interpolation='nearest')
    ax.set_axis_off()
    fig.savefig(out_path, facecolor='black', dpi=dpi, pad_inches=0)
    plt.close(fig)


def main():
    iter10 = np.load(os.path.join(HERE, 'q_lattice_iter_10.npy'))
    print(f'iter_10: range [{iter10.min():.3f}, {iter10.max():.3f}]')

    p2 = float(np.percentile(iter10, 2))
    p99 = float(np.percentile(iter10, 99))
    full_lo = float(iter10.min())
    full_hi = float(iter10.max())
    print(f'  p2-p99   : [{p2:.3f}, {p99:.3f}]')
    print(f'  full data: [{full_lo:.3f}, {full_hi:.3f}]')

    variants = [
        ('A_inferno_clip',  'inferno', p2,      p99),
        ('B_inferno_full',  'inferno', full_lo, full_hi),
        ('C_gray_clip',     'gray',    p2,      p99),
        ('D_gray_full',     'gray',    full_lo, full_hi),
    ]

    for name, cmap, vmin, vmax in variants:
        out = os.path.join(HERE, f'q_lattice_iter_10_{name}.png')
        render(iter10, out, cmap, vmin, vmax)
        print(f'  -> {os.path.basename(out)} '
              f'({os.path.getsize(out) / 1024 / 1024:.1f} MB)  '
              f'cmap={cmap}  vmin={vmin:.3f}  vmax={vmax:.3f}')


if __name__ == '__main__':
    main()
