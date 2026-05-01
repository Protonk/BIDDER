"""
q_lattice_1d_profiles_split.py - 1D autocorrelation profiles, parity-split.

Same data as q_lattice_1d_profiles.py, but the dense oscillating lines
are split into separate odd-lag and even-lag series so the parity
modulation is directly readable instead of read off zigzags.

Layout: 2 × 2 grid of panels.
  Top-left:    horizontal (k-direction) profile, EVEN lags only
  Top-right:   horizontal (k-direction) profile, ODD lags only
  Bottom-left: vertical (n-direction) profile, EVEN lags only
  Bottom-right: vertical (n-direction) profile, ODD lags only

Within each panel: one line per h ∈ {5, 6, 7, 8}, coloured by h.

Reading: at odd h, even-lag and odd-lag series are both positive but
at different magnitudes (the sawtooth in the unsplit plot). At even h
horizontal, both parities sit at ~0.6–0.8 (the k-direction is parity-
flat). At even h vertical, even-lag stays positive while odd-lag
goes negative — the sign-flip the unsplit plot was hiding behind
oscillation.
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
    print('Loading lattices and computing 1D profiles...')
    profiles = {}
    for h in H_VALUES:
        cache = os.path.join(HERE, f'q_lattice_4000_h{h}.npy')
        if not os.path.exists(cache):
            continue
        t0 = time.time()
        grid = np.load(cache)
        img = slog(grid).astype(np.float64)
        ac = autocorr_2d(img)
        cy, cx = ac.shape[0] // 2, ac.shape[1] // 2
        horiz = ac[cy, cx + 1:cx + 1 + LAG_MAX]
        vert = ac[cy + 1:cy + 1 + LAG_MAX, cx]
        profiles[h] = {'horiz': horiz, 'vert': vert}
        print(f'  h={h}: {time.time() - t0:.1f}s')

    h_colors = {
        5: (1.00, 0.66, 0.30),
        6: (1.00, 0.45, 0.30),
        7: (0.85, 0.30, 0.55),
        8: (0.55, 0.30, 0.95),
    }

    lags = np.arange(1, LAG_MAX + 1)  # actual lag values 1..LAG_MAX
    even_lags = lags[lags % 2 == 0]
    odd_lags = lags[lags % 2 == 1]

    fig = plt.figure(figsize=(15, 11), facecolor='#0a0a0a', dpi=180)

    panel_specs = [
        (0.06, 0.55, 0.42, 0.36, 'horiz', 'even',
         'horizontal (k-direction)  ·  even dx lags only',
         'lag dx (even)'),
        (0.54, 0.55, 0.42, 0.36, 'horiz', 'odd',
         'horizontal (k-direction)  ·  odd dx lags only',
         'lag dx (odd)'),
        (0.06, 0.07, 0.42, 0.36, 'vert', 'even',
         'vertical (n-direction)  ·  even dy lags only',
         'lag dy (even)'),
        (0.54, 0.07, 0.42, 0.36, 'vert', 'odd',
         'vertical (n-direction)  ·  odd dy lags only',
         'lag dy (odd)'),
    ]

    # Track shared y-axis range for top row and bottom row
    horiz_max = max(profiles[h]['horiz'].max() for h in profiles)
    horiz_min = min(profiles[h]['horiz'].min() for h in profiles)
    vert_max = max(profiles[h]['vert'].max() for h in profiles)
    vert_min = min(profiles[h]['vert'].min() for h in profiles)

    for left, bot, w, hgt, axis, parity, title, xlab in panel_specs:
        ax = fig.add_axes([left, bot, w, hgt], facecolor='#0a0a0a')
        for h in H_VALUES:
            if h not in profiles:
                continue
            col = h_colors[h]
            arr = profiles[h][axis]
            if parity == 'even':
                xs = even_lags
                ys = arr[even_lags - 1]  # arr is 0-indexed at lag 1
            else:
                xs = odd_lags
                ys = arr[odd_lags - 1]
            ax.plot(xs, ys, color=(*col, 0.92), lw=1.5,
                    marker='o', ms=2.5,
                    label=f'h={h}  ({"even" if h % 2 == 0 else "odd"})')

        ax.axhline(0, color=(0.95, 0.97, 1.00, 0.30), lw=0.7)
        ax.set_xlabel(xlab, color=(0.85, 0.88, 0.92, 0.92), fontsize=10)
        ax.set_ylabel('Pearson autocorr',
                      color=(0.85, 0.88, 0.92, 0.92), fontsize=10)
        ax.set_title(title, color=(0.96, 0.97, 1.00, 0.95),
                     fontsize=11, pad=6)
        ax.tick_params(colors=(0.78, 0.82, 0.88, 0.85), labelsize=9)
        for spine in ax.spines.values():
            spine.set_color((0.40, 0.45, 0.50, 0.40))
        ax.grid(True, color=(0.30, 0.34, 0.38), alpha=0.18, lw=0.4)
        ax.set_xlim(0, LAG_MAX)
        if axis == 'horiz':
            ax.set_ylim(min(-0.05, horiz_min - 0.03), horiz_max + 0.03)
        else:
            ax.set_ylim(min(-0.2, vert_min - 0.03), vert_max + 0.03)
        ax.legend(loc='upper right', fontsize=9, frameon=False,
                  labelcolor=(0.92, 0.95, 1.00, 1.0))

    fig.text(0.5, 0.985,
             '1D autocorrelation profiles, parity-split  ·  '
             'h ∈ {5, 6, 7, 8}',
             ha='center', va='top', fontsize=14, fontweight='bold',
             color=(1.0, 1.0, 1.0, 0.95), family='serif')
    fig.text(0.5, 0.962,
             'each profile split into even-lag and odd-lag sub-series  ·  '
             'lag range 1..200',
             ha='center', va='top', fontsize=10, fontstyle='italic',
             color=(0.85, 0.88, 0.92, 0.65))

    out = os.path.join(HERE, 'q_lattice_1d_profiles_split.png')
    plt.savefig(out, facecolor='#0a0a0a', dpi=180,
                bbox_inches='tight', pad_inches=0.15)
    plt.close()
    sz = os.path.getsize(out) / 1024
    print(f'\n-> {os.path.basename(out)}  ({sz:.0f} KB)')


if __name__ == '__main__':
    main()
