"""
art_groove.py — The Poincaré groove.

Each demo's mantissa evolution rendered as a vinyl record: radius is
time (center = step 0, edge = final step), angular groove depth is
the 256-bin mantissa histogram at that checkpoint. Uniform density
gives a perfect circle; concentrated density gives an eccentric wobble.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from common import (
    BG, FG, SPINE,
    experiment_path, load_checkpoints, save_figure,
)


DEMOS = [
    ('add_mult_alternating', 'add/mult alternating'),
    ('bs12_walk', 'BS(1,2) walk'),
    ('front_loaded', 'front-loaded freeze'),
    ('pure_add', 'pure add'),
]

N_GROOVES = 60
WOBBLE_SCALE = 0.45
GROOVE_LW = 0.7


def main():
    fig, axes = plt.subplots(2, 2, figsize=(14, 14),
                             subplot_kw={'projection': 'polar'})
    fig.patch.set_facecolor(BG)

    # Global max deviation across ALL demos for comparable wobble
    all_data = {}
    global_max_dev = 0.0
    for name, _ in DEMOS:
        ckpts = load_checkpoints(experiment_path(f'data_{name}.npz'))
        hist = ckpts['log_mantissa_hist'].astype(np.float64)
        l1 = ckpts['l1'].astype(np.float64)
        K, B = hist.shape
        uniform = 1.0 / B
        indices = np.linspace(0, K - 1, N_GROOVES, dtype=int)
        for k in indices:
            dev = np.abs(hist[k] - uniform).max()
            global_max_dev = max(global_max_dev, dev)
        all_data[name] = (hist, l1, K, B, indices)
    if global_max_dev < 1e-10:
        global_max_dev = 1.0

    theta = np.linspace(0, 2 * np.pi, 256, endpoint=False)
    theta_closed = np.append(theta, theta[0])
    r_min = 0.18
    r_max = 0.92
    r_gap = (r_max - r_min) / N_GROOVES

    for ax, (name, title) in zip(axes.ravel(), DEMOS):
        ax.set_facecolor(BG)
        hist, l1, K, B, indices = all_data[name]
        uniform = 1.0 / B

        for gi, k in enumerate(indices):
            t_frac = gi / max(N_GROOVES - 1, 1)
            r_base = r_min + (r_max - r_min) * t_frac

            deviation = (hist[k] - uniform) / global_max_dev
            wobble = r_base + WOBBLE_SCALE * r_gap * deviation * N_GROOVES
            wobble_closed = np.append(wobble, wobble[0])

            # color by L1: high L1 = bright yellow, low L1 = dim purple
            l1_frac = min(1.0, l1[k] / 0.5) if l1[k] > 0 else 0.0
            color = plt.cm.plasma(0.15 + 0.8 * l1_frac)
            alpha = 0.4 + 0.5 * l1_frac

            ax.plot(theta_closed, wobble_closed,
                    color=color, linewidth=GROOVE_LW, alpha=alpha)

        # label hole
        hole = plt.Circle((0, 0), r_min * 0.6, transform=ax.transData,
                          color='#151515', zorder=10)
        ax.add_patch(hole)
        # rim
        rim_theta = np.linspace(0, 2 * np.pi, 200)
        ax.plot(rim_theta, np.full_like(rim_theta, r_max + r_gap),
                color='#333', linewidth=1.0, alpha=0.5)

        ax.set_rticks([])
        ax.set_thetagrids([])
        ax.spines['polar'].set_visible(False)
        ax.grid(False)
        ax.set_title(title, color=FG, fontsize=13, pad=15)
        ax.set_ylim(0, 1.05)

    plt.tight_layout(pad=2.0)
    save_figure(fig, experiment_path('art_groove.png'))


if __name__ == '__main__':
    main()
