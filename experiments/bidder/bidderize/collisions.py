"""
collisions.py — Birthday-problem collision heatmap.

Numpy shows the smooth n^2/(2N) gradient. BIDDER is solid black
(zero collisions) for all n <= N, then lights up at n > N.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..')
DIST = os.path.join(ROOT, 'dist')
sys.path.insert(0, DIST)

try:
    import bidder_c as bidder
except ImportError:
    import bidder

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


BG = '#0a0a0a'
FG = 'white'
SPINE = '#333'

N_POOL = 1000
RATIOS = np.linspace(0.02, 1.5, 75)
N_DRAWS = 60
SAMPLE_SIZES = (RATIOS * N_POOL).astype(int)
SAMPLE_SIZES = np.clip(SAMPLE_SIZES, 1, None)


def count_collisions_numpy(n, N, rng):
    samples = rng.integers(0, N, size=n)
    return n - len(set(samples.tolist()))


def count_collisions_bidder(n, N, key):
    B = bidder.cipher(period=N, key=key)
    if n <= N:
        samples = [B.at(i) for i in range(n)]
    else:
        full = list(B)
        extra_B = bidder.cipher(period=N, key=key + b':wrap')
        samples = full + [extra_B.at(i) for i in range(n - N)]
    return n - len(set(samples))


def main():
    n_ratios = len(SAMPLE_SIZES)

    heat_numpy = np.zeros((N_DRAWS, n_ratios))
    heat_bidder = np.zeros((N_DRAWS, n_ratios))

    print(f'Computing collision heatmaps ({n_ratios} ratios x {N_DRAWS} draws)...')
    for di in range(N_DRAWS):
        rng = np.random.default_rng(di + 1000)
        for ri, n in enumerate(SAMPLE_SIZES):
            heat_numpy[di, ri] = count_collisions_numpy(int(n), N_POOL, rng)
            key = f'col:d{di}:r{ri}'.encode()
            heat_bidder[di, ri] = count_collisions_bidder(int(n), N_POOL, key)
        if (di + 1) % 10 == 0:
            print(f'  draw {di+1}/{N_DRAWS}')

    vmax = max(heat_numpy.max(), heat_bidder.max(), 1)

    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor(BG)
    gs = fig.add_gridspec(2, 2, height_ratios=[3, 1], hspace=0.3)

    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, :])

    for ax in (ax1, ax2, ax3):
        ax.set_facecolor(BG)
        ax.tick_params(colors=FG)
        for spine in ax.spines.values():
            spine.set_color(SPINE)

    extent = [float(RATIOS[0]), float(RATIOS[-1]), 0, N_DRAWS]

    ax1.imshow(heat_numpy, aspect='auto', origin='lower', cmap='inferno',
               extent=extent, vmin=0, vmax=vmax, interpolation='nearest')
    ax1.set_title('numpy PRNG', color=FG, fontsize=12)
    ax1.set_ylabel('draw index', color=FG)
    ax1.set_xlabel('n / N', color=FG)
    ax1.axvline(1.0, color=FG, linestyle='--', linewidth=0.8, alpha=0.5)

    im = ax2.imshow(heat_bidder, aspect='auto', origin='lower', cmap='inferno',
                    extent=extent, vmin=0, vmax=vmax, interpolation='nearest')
    ax2.set_title('BIDDER cipher', color=FG, fontsize=12)
    ax2.set_xlabel('n / N', color=FG)
    ax2.axvline(1.0, color=FG, linestyle='--', linewidth=0.8, alpha=0.5)
    ax2.text(1.02, 0.5, 'n = N', color=FG, fontsize=9, va='center',
             transform=ax2.get_xaxis_transform())

    cbar = fig.colorbar(im, ax=[ax1, ax2], shrink=0.85, pad=0.02)
    cbar.set_label('collisions (duplicates)', color=FG)
    cbar.ax.tick_params(colors=FG)

    # Bottom panel: mean collisions at draw=median
    mean_numpy = heat_numpy.mean(axis=0)
    mean_bidder = heat_bidder.mean(axis=0)
    ax3.plot(RATIOS, mean_numpy, color='#ffcc5c', linewidth=2.0,
             label='numpy PRNG')
    ax3.plot(RATIOS, mean_bidder, color='#6ec6ff', linewidth=2.0,
             label='BIDDER cipher')
    # birthday prediction: E[collisions] ≈ n - N(1 - ((N-1)/N)^n) ≈ n^2/(2N)
    birthday = SAMPLE_SIZES.astype(float)**2 / (2 * N_POOL)
    birthday = np.clip(birthday, 0, SAMPLE_SIZES - 1)
    ax3.plot(RATIOS, birthday, color='#ff6f61', linewidth=1.2,
             linestyle='--', label='birthday bound  n²/(2N)')
    ax3.axvline(1.0, color=FG, linestyle='--', linewidth=0.8, alpha=0.5)
    ax3.set_xlabel('n / N', color=FG)
    ax3.set_ylabel('mean collisions', color=FG)
    ax3.set_xlim(float(RATIOS[0]), float(RATIOS[-1]))
    ax3.grid(color='#222', linewidth=0.5, alpha=0.5)
    leg = ax3.legend(loc='upper left', facecolor='#111', edgecolor=SPINE)
    for t in leg.get_texts():
        t.set_color(FG)

    fig.suptitle(f'Collision count: {N_DRAWS} draws from pool of {N_POOL}',
                 color=FG, fontsize=14, y=0.98)

    out = os.path.join(HERE, 'collisions.png')
    fig.savefig(out, dpi=250, facecolor=BG, bbox_inches='tight')
    plt.close(fig)
    print(f'-> collisions.png')


if __name__ == '__main__':
    main()
