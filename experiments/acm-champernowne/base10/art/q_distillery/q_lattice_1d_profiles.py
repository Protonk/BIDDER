"""
q_lattice_1d_profiles.py - extract the surviving 1D correlation
profiles along each axis.

After the shuffle test established that the 2D autocorrelation pattern
is the cross-product of two 1D correlation structures (one per axis),
the right primitive to look at is the 1D profiles directly:

  horiz_profile(L) = Pearson autocorrelation of slog(grid) at lag (0, L)
                  = within-row correlation at column-distance L
                  = "k-direction structure"

  vert_profile(L) = Pearson autocorrelation of slog(grid) at lag (L, 0)
                  = between-row correlation at row-distance L
                  = "n-direction structure"

Plot both profiles for h = 5, 6, 7, 8 over a wide lag range (L = 0 to
some large value, e.g. 200 or longer). Look for:
  - the L = 1 < L = 4 anomaly mechanism (does correlation peak at
    some characteristic lag?)
  - parity dependence (odd h vs even h profile shapes)
  - long-range behaviour (does it decay, stay flat, oscillate?)
  - any periodicity that would explain the checkerboard cross-product.
"""

import os
import time

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


HERE = os.path.dirname(os.path.abspath(__file__))
H_VALUES = [5, 6, 7, 8]
LAG_MAX = 200


def slog(arr, lt=1.0):
    arr = np.asarray(arr, dtype=float)
    return np.sign(arr) * np.log10(1.0 + np.abs(arr) / lt)


def autocorr_2d(img):
    img = img.astype(np.float64)
    img = img - img.mean()
    var = (img * img).sum()
    if var == 0:
        return np.zeros_like(img)
    F = np.fft.fft2(img)
    autocorr = np.real(np.fft.ifft2(np.abs(F) ** 2)) / var
    return np.fft.fftshift(autocorr)


def main():
    print('Loading cached lattices and computing 1D autocorrelation '
          'profiles...')
    profiles = {}
    for h in H_VALUES:
        cache = os.path.join(HERE, f'q_lattice_4000_h{h}.npy')
        if not os.path.exists(cache):
            print(f'  no cache for h={h}; skipping')
            continue
        t0 = time.time()
        grid = np.load(cache)
        img = slog(grid).astype(np.float64)
        ac = autocorr_2d(img)
        cy, cx = ac.shape[0] // 2, ac.shape[1] // 2
        # horiz: dy = 0, dx = 1..LAG_MAX
        horiz = ac[cy, cx + 1:cx + 1 + LAG_MAX]
        # vert: dx = 0, dy = 1..LAG_MAX
        vert = ac[cy + 1:cy + 1 + LAG_MAX, cx]
        profiles[h] = {'horiz': horiz, 'vert': vert,
                       'center': ac[cy, cx]}
        print(f'  h={h}: {time.time() - t0:.1f}s   '
              f'horiz max = {horiz.max():.4f}  '
              f'vert max = {vert.max():.4f}  '
              f'horiz min = {horiz.min():+.4f}  '
              f'vert min = {vert.min():+.4f}')

    # ---- Render ----
    h_colors = {
        5: (1.00, 0.66, 0.30),
        6: (1.00, 0.45, 0.30),
        7: (0.85, 0.30, 0.55),
        8: (0.55, 0.30, 0.95),
    }
    lags = np.arange(1, LAG_MAX + 1)

    fig = plt.figure(figsize=(15, 11), facecolor='#0a0a0a', dpi=180)

    # Panel 1: horizontal (k-direction) profiles
    ax_h = fig.add_axes([0.07, 0.55, 0.88, 0.38], facecolor='#0a0a0a')
    for h in H_VALUES:
        if h not in profiles:
            continue
        col = h_colors[h]
        parity = 'even' if h % 2 == 0 else 'odd'
        ax_h.plot(lags, profiles[h]['horiz'],
                  color=(*col, 0.92), lw=1.7,
                  label=f'h = {h}  ({parity})')
    ax_h.axhline(0, color=(0.95, 0.97, 1.00, 0.30), lw=0.7)
    ax_h.set_xlabel('lag dx  (within-row column distance)',
                    color=(0.85, 0.88, 0.92, 0.92), fontsize=11)
    ax_h.set_ylabel('Pearson autocorrelation',
                    color=(0.85, 0.88, 0.92, 0.92), fontsize=11)
    ax_h.set_title(
        'horizontal (k-direction) 1D autocorrelation profile',
        color=(0.96, 0.97, 1.00, 0.95), fontsize=12, pad=8,
    )
    ax_h.legend(loc='upper right', fontsize=10, frameon=False,
                labelcolor=(0.92, 0.95, 1.00, 1.0))
    ax_h.tick_params(colors=(0.78, 0.82, 0.88, 0.85), labelsize=9)
    for spine in ax_h.spines.values():
        spine.set_color((0.40, 0.45, 0.50, 0.40))
    ax_h.grid(True, color=(0.30, 0.34, 0.38), alpha=0.18, lw=0.4)
    ax_h.set_xlim(0, LAG_MAX)

    # Panel 2: vertical (n-direction) profiles
    ax_v = fig.add_axes([0.07, 0.07, 0.88, 0.38], facecolor='#0a0a0a')
    for h in H_VALUES:
        if h not in profiles:
            continue
        col = h_colors[h]
        parity = 'even' if h % 2 == 0 else 'odd'
        ax_v.plot(lags, profiles[h]['vert'],
                  color=(*col, 0.92), lw=1.7,
                  label=f'h = {h}  ({parity})')
    ax_v.axhline(0, color=(0.95, 0.97, 1.00, 0.30), lw=0.7)
    ax_v.set_xlabel('lag dy  (between-row row distance)',
                    color=(0.85, 0.88, 0.92, 0.92), fontsize=11)
    ax_v.set_ylabel('Pearson autocorrelation',
                    color=(0.85, 0.88, 0.92, 0.92), fontsize=11)
    ax_v.set_title(
        'vertical (n-direction) 1D autocorrelation profile',
        color=(0.96, 0.97, 1.00, 0.95), fontsize=12, pad=8,
    )
    ax_v.legend(loc='upper right', fontsize=10, frameon=False,
                labelcolor=(0.92, 0.95, 1.00, 1.0))
    ax_v.tick_params(colors=(0.78, 0.82, 0.88, 0.85), labelsize=9)
    for spine in ax_v.spines.values():
        spine.set_color((0.40, 0.45, 0.50, 0.40))
    ax_v.grid(True, color=(0.30, 0.34, 0.38), alpha=0.18, lw=0.4)
    ax_v.set_xlim(0, LAG_MAX)

    fig.text(0.5, 0.985,
             '1D autocorrelation profiles along each axis  ·  h ∈ {5, 6, 7, 8}',
             ha='center', va='top', fontsize=14, fontweight='bold',
             color=(1.0, 1.0, 1.0, 0.95), family='serif')
    fig.text(0.5, 0.962,
             'extracted from row 0 / column 0 of the 2D autocorrelation map  ·  '
             'lag range L = 1 .. 200',
             ha='center', va='top', fontsize=10, fontstyle='italic',
             color=(0.85, 0.88, 0.92, 0.65))

    out = os.path.join(HERE, 'q_lattice_1d_profiles.png')
    plt.savefig(out, facecolor='#0a0a0a', dpi=180,
                bbox_inches='tight', pad_inches=0.15)
    plt.close()
    sz = os.path.getsize(out) / 1024
    print(f'\n-> {os.path.basename(out)}  ({sz:.0f} KB)')

    # Print first 20 lags for inspection
    print('\n=== first 20 lags ===')
    for h in H_VALUES:
        if h not in profiles:
            continue
        print(f'\nh = {h}')
        print(f'  horiz: {", ".join(f"{v:+.4f}" for v in profiles[h]["horiz"][:20])}')
        print(f'   vert: {", ".join(f"{v:+.4f}" for v in profiles[h]["vert"][:20])}')


if __name__ == '__main__':
    main()
