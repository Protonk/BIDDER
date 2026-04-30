"""
q_lattice_autocorr_shuffle.py - Test 1 from the harness audit.

For each h, compute the 2D autocorrelation of slog(lattice) under three
conditions:

  1. original integer enumeration (rows = n=2..N, cols = k=1..K)
  2. random permutation of rows (shuffle n-axis)
  3. random permutation of columns (shuffle k-axis)

If the checkerboard / stripe pattern is the substrate's content
(real spatial correlation between Q values), it should change in
specific ways under the permutations: shuffling rows breaks
n-direction structure but preserves k-direction; shuffling columns
does the reverse. If the pattern is a Z/2 × Z/2 fingerprint of
consecutive-integer parity, it should mostly disappear under
either shuffle (no consecutive-integer adjacency anymore).

Render 4 × 3 panel grid: rows = h ∈ {5, 6, 7, 8}, columns =
{original, shuffled-n, shuffled-k}.
"""

import os
import time

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


HERE = os.path.dirname(os.path.abspath(__file__))
H_VALUES = [5, 6, 7, 8]
WINDOW = 31
SEED = 1729


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


def central_window(autocorr, w):
    cy, cx = autocorr.shape[0] // 2, autocorr.shape[1] // 2
    return autocorr[cy - w:cy + w + 1, cx - w:cx + w + 1].copy()


def make_div_cmap():
    return LinearSegmentedColormap.from_list('q_div', [
        (0.00, (0.55, 1.00, 1.00)),
        (0.18, (0.30, 0.55, 0.95)),
        (0.38, (0.20, 0.25, 0.45)),
        (0.50, (0.04, 0.04, 0.05)),
        (0.62, (0.42, 0.28, 0.14)),
        (0.82, (1.00, 0.55, 0.20)),
        (1.00, (1.00, 0.92, 0.45)),
    ], N=512)


def main():
    rng = np.random.default_rng(SEED)
    print(f'Random seed for permutations: {SEED}')

    panels = {}
    print('\nComputing 2D autocorrelations under three conditions per h...')
    for h in H_VALUES:
        cache = os.path.join(HERE, f'q_lattice_4000_h{h}.npy')
        if not os.path.exists(cache):
            print(f'  no cache for h={h}; skipping')
            continue

        t0 = time.time()
        grid = np.load(cache)
        img_orig = slog(grid).astype(np.float64)

        # 1. original
        ac_orig = autocorr_2d(img_orig)
        win_orig = central_window(ac_orig, WINDOW)

        # 2. shuffle rows (n axis)
        n_perm = rng.permutation(img_orig.shape[0])
        img_n = img_orig[n_perm]
        ac_n = autocorr_2d(img_n)
        win_n = central_window(ac_n, WINDOW)

        # 3. shuffle columns (k axis)
        k_perm = rng.permutation(img_orig.shape[1])
        img_k = img_orig[:, k_perm]
        ac_k = autocorr_2d(img_k)
        win_k = central_window(ac_k, WINDOW)

        panels[h] = {
            'original': win_orig,
            'shuffle_n': win_n,
            'shuffle_k': win_k,
        }
        # Print summary stats (off-center max |corr|)
        for name, w in panels[h].items():
            cy, cx = w.shape[0] // 2, w.shape[1] // 2
            tmp = w.copy()
            tmp[cy, cx] = 0
            print(f'  h={h} {name:>11}: '
                  f'max|corr| (off-center) = {np.abs(tmp).max():.4f}   '
                  f'std = {tmp.std():.4f}')
        print(f'  h={h} total: {time.time() - t0:.1f}s')

    # Determine shared color scale
    all_off = []
    for h, conds in panels.items():
        for name, w in conds.items():
            tmp = w.copy()
            cy, cx = tmp.shape[0] // 2, tmp.shape[1] // 2
            tmp[cy, cx] = 0
            all_off.append(np.abs(tmp).ravel())
    pooled = np.concatenate(all_off)
    vmax = float(np.percentile(pooled, 99.5))
    print(f'\n  shared color vmax = {vmax:.3f}')

    cmap = make_div_cmap()

    # ---- Render 4 × 3 grid ----
    fig = plt.figure(figsize=(13, 16), facecolor='#0a0a0a', dpi=180)
    rows = len(H_VALUES)
    cols = 3
    titles = ['original (integer order)',
              'rows shuffled  (n-axis randomised)',
              'cols shuffled  (k-axis randomised)']

    cell_w = 0.27
    cell_h = 0.21
    left_margin = 0.05
    right_margin = 0.05
    bot_margin = 0.04
    inner_pad = 0.005
    total_h_avail = 1 - bot_margin - 0.06  # leave room for title

    for i, h in enumerate(H_VALUES):
        if h not in panels:
            continue
        for j, key in enumerate(['original', 'shuffle_n', 'shuffle_k']):
            left = left_margin + j * (cell_w + 0.02)
            bot = (rows - 1 - i) * (cell_h + 0.018) + bot_margin
            ax = fig.add_axes([left, bot, cell_w, cell_h],
                              facecolor='#0a0a0a')
            win = panels[h][key]
            im = ax.imshow(
                win, origin='lower',
                extent=[-WINDOW - 0.5, WINDOW + 0.5,
                        -WINDOW - 0.5, WINDOW + 0.5],
                cmap=cmap, vmin=-vmax, vmax=vmax,
                interpolation='nearest', aspect='equal',
            )
            ax.plot(0, 0, marker='+', ms=8,
                    markeredgecolor=(1.0, 1.0, 1.0, 0.5),
                    markeredgewidth=0.8)
            for r in [4, 8, 16, 31]:
                theta = np.linspace(0, 2 * np.pi, 200)
                ax.plot(r * np.cos(theta), r * np.sin(theta),
                        color=(1.0, 1.0, 1.0, 0.08), lw=0.5)
            ax.axhline(0, color=(1.0, 1.0, 1.0, 0.08), lw=0.5)
            ax.axvline(0, color=(1.0, 1.0, 1.0, 0.08), lw=0.5)
            ax.tick_params(colors=(0.78, 0.82, 0.88, 0.78), labelsize=7)
            for spine in ax.spines.values():
                spine.set_color((0.40, 0.45, 0.50, 0.40))
            ax.set_xticks([-30, -15, 0, 15, 30])
            ax.set_yticks([-30, -15, 0, 15, 30])

            if j == 0:
                ax.set_ylabel(
                    f'h = {h}  ({"even" if h % 2 == 0 else "odd"})',
                    color=(0.96, 0.97, 1.00, 0.92),
                    fontsize=11, labelpad=8,
                )
            if i == 0:
                ax.set_title(titles[j],
                             color=(0.96, 0.97, 1.00, 0.92),
                             fontsize=10.5, pad=6)

    # Title at top
    fig.text(0.5, 0.985,
             'Test 1: 2D autocorrelation under row / column permutations',
             ha='center', va='top', fontsize=14, fontweight='bold',
             color=(1.0, 1.0, 1.0, 0.95), family='serif')
    fig.text(0.5, 0.962,
             'central window dy, dx ∈ [−31, +31]   ·   '
             'random permutation seed = 1729',
             ha='center', va='top', fontsize=10, fontstyle='italic',
             color=(0.85, 0.88, 0.92, 0.65))

    out = os.path.join(HERE, 'q_lattice_autocorr_shuffle.png')
    plt.savefig(out, facecolor='#0a0a0a', dpi=180,
                bbox_inches='tight', pad_inches=0.15)
    plt.close()
    sz = os.path.getsize(out) / 1024
    print(f'\n-> {os.path.basename(out)}  ({sz:.0f} KB)')


if __name__ == '__main__':
    main()
