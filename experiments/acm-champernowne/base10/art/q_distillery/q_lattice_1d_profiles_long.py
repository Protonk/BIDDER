"""
q_lattice_1d_profiles_long.py - 1D autocorrelation profiles, long range.

Same per-axis profiles as q_lattice_1d_profiles_split.py, but pushed
to lag = 1500 with proper FFT padding (no circular wrap-around). Per-row
FFTs accumulate into the dy = 0 slice of the global 2D autocorrelation;
analogous for the dx = 0 slice via transpose.

Question: does the parity-modulation that's so clean at lags 1-200
persist out to lags ~1000-1500, or does it decay at some characteristic
scale? It does not have to.
"""

import os
import time

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


HERE = os.path.dirname(os.path.abspath(__file__))
H_VALUES = [5, 6, 7, 8]
LAG_MAX = 1500


def slog(arr, lt=1.0):
    arr = np.asarray(arr, dtype=float)
    return np.sign(arr) * np.log10(1.0 + np.abs(arr) / lt)


def horiz_profile(grid, lag_max):
    """Compute the dy = 0 slice of the 2D global Pearson autocorrelation
    via per-row FFT with zero-pad (no wrap-around)."""
    h, w = grid.shape
    grid_c = grid - grid.mean()
    global_var = float((grid_c * grid_c).sum())
    if global_var == 0:
        return np.zeros(lag_max + 1)
    pad_size = 2 * w
    accum = np.zeros(lag_max + 1, dtype=np.float64)
    for i in range(h):
        row = grid_c[i]
        padded = np.zeros(pad_size, dtype=np.float64)
        padded[:w] = row
        F = np.fft.fft(padded)
        ac = np.real(np.fft.ifft(np.abs(F) ** 2))
        accum += ac[:lag_max + 1]
    return accum / global_var


def vert_profile(grid, lag_max):
    return horiz_profile(grid.T, lag_max)


def main():
    profiles = {}
    for h in H_VALUES:
        cache = os.path.join(HERE, f'q_lattice_4000_h{h}.npy')
        if not os.path.exists(cache):
            continue
        print(f'h = {h}:')
        t0 = time.time()
        grid = np.load(cache)
        img = slog(grid).astype(np.float64)
        h_prof = horiz_profile(img, LAG_MAX)
        v_prof = vert_profile(img, LAG_MAX)
        profiles[h] = {'horiz': h_prof, 'vert': v_prof}
        print(f'  compute: {time.time() - t0:.1f}s')
        # Sanity: lag 0 should be 1
        print(f'  horiz[0] = {h_prof[0]:.4f}   vert[0] = {v_prof[0]:.4f}')
        # Pick a few summary points
        print(f'  horiz[1] = {h_prof[1]:+.4f}  '
              f'horiz[100] = {h_prof[100]:+.4f}  '
              f'horiz[500] = {h_prof[500]:+.4f}  '
              f'horiz[1500] = {h_prof[1500]:+.4f}')
        print(f'  vert[1]  = {v_prof[1]:+.4f}  '
              f'vert[100]  = {v_prof[100]:+.4f}  '
              f'vert[500]  = {v_prof[500]:+.4f}  '
              f'vert[1500]  = {v_prof[1500]:+.4f}')

    h_colors = {
        5: (1.00, 0.66, 0.30),
        6: (1.00, 0.45, 0.30),
        7: (0.85, 0.30, 0.55),
        8: (0.55, 0.30, 0.95),
    }

    lags = np.arange(1, LAG_MAX + 1)
    even_lags = lags[lags % 2 == 0]
    odd_lags = lags[lags % 2 == 1]

    fig = plt.figure(figsize=(16, 11), facecolor='#0a0a0a', dpi=180)

    panels = [
        (0.06, 0.55, 0.42, 0.36, 'horiz', 'even',
         'horizontal (k-direction)  ·  even dx lags'),
        (0.54, 0.55, 0.42, 0.36, 'horiz', 'odd',
         'horizontal (k-direction)  ·  odd dx lags'),
        (0.06, 0.07, 0.42, 0.36, 'vert', 'even',
         'vertical (n-direction)  ·  even dy lags'),
        (0.54, 0.07, 0.42, 0.36, 'vert', 'odd',
         'vertical (n-direction)  ·  odd dy lags'),
    ]

    for left, bot, w, hgt, axis, parity, title in panels:
        ax = fig.add_axes([left, bot, w, hgt], facecolor='#0a0a0a')
        for h in H_VALUES:
            if h not in profiles:
                continue
            arr = profiles[h][axis]  # arr[L] = corr at lag L; arr has length LAG_MAX + 1
            if parity == 'even':
                xs = even_lags
                ys = arr[even_lags]
            else:
                xs = odd_lags
                ys = arr[odd_lags]
            col = h_colors[h]
            label = f'h={h}  ({"even" if h % 2 == 0 else "odd"})'
            ax.plot(xs, ys, color=(*col, 0.85), lw=0.7, label=label)
        ax.axhline(0, color=(0.95, 0.97, 1.00, 0.30), lw=0.6)
        ax.set_xlabel(
            ('lag dx' if axis == 'horiz' else 'lag dy') + f'  ({parity})',
            color=(0.85, 0.88, 0.92, 0.92), fontsize=10,
        )
        ax.set_ylabel('Pearson autocorr',
                      color=(0.85, 0.88, 0.92, 0.92), fontsize=10)
        ax.set_title(title, color=(0.96, 0.97, 1.00, 0.95),
                     fontsize=11, pad=6)
        ax.tick_params(colors=(0.78, 0.82, 0.88, 0.85), labelsize=9)
        for spine in ax.spines.values():
            spine.set_color((0.40, 0.45, 0.50, 0.40))
        ax.grid(True, color=(0.30, 0.34, 0.38), alpha=0.18, lw=0.4)
        ax.set_xlim(0, LAG_MAX)
        ax.legend(loc='upper right', fontsize=9, frameon=False,
                  labelcolor=(0.92, 0.95, 1.00, 1.0))

    fig.text(0.5, 0.985,
             '1D autocorrelation profiles, long range  ·  lag = 1 .. 1500',
             ha='center', va='top', fontsize=14, fontweight='bold',
             color=(1.0, 1.0, 1.0, 0.95), family='serif')
    fig.text(0.5, 0.962,
             'parity-split  ·  zero-padded FFT (no wrap-around)  ·  '
             'h ∈ {5, 6, 7, 8}',
             ha='center', va='top', fontsize=10, fontstyle='italic',
             color=(0.85, 0.88, 0.92, 0.65))

    out = os.path.join(HERE, 'q_lattice_1d_profiles_long.png')
    plt.savefig(out, facecolor='#0a0a0a', dpi=180,
                bbox_inches='tight', pad_inches=0.15)
    plt.close()
    sz = os.path.getsize(out) / 1024
    print(f'\n-> {os.path.basename(out)}  ({sz:.0f} KB)')


if __name__ == '__main__':
    main()
