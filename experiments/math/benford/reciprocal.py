"""
Optional linear-coordinate comparison against a reciprocal density.
"""

import numpy as np
import matplotlib.pyplot as plt

from common import BG, FG, RED, BLUE, experiment_path, load_checkpoints, save_figure, setup_dark_axes


PANELS = [
    ('add_mult_alternating', 'add/mult alternating'),
    ('bs12_walk', 'BS(1,2) walk'),
    ('front_loaded', 'front-loaded freeze'),
    ('pure_add', 'pure add'),
]


def main():
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.patch.set_facecolor(BG)

    for ax, (name, title) in zip(axes.ravel(), PANELS):
        setup_dark_axes(ax)
        abs_x = load_checkpoints(experiment_path(f'data_{name}.npz'))['final_abs_x']
        median = float(np.median(abs_x))
        lo = median / 10.0
        hi = median * 10.0
        clipped = abs_x[(abs_x >= lo) & (abs_x <= hi)]
        ax.hist(clipped, bins=50, density=True, color=BLUE, alpha=0.35, edgecolor='none')

        grid = np.linspace(lo, hi, 500)
        reciprocal = 1.0 / (grid * np.log(hi / lo))
        ax.plot(grid, reciprocal, color=RED, linewidth=1.8)
        retained = clipped.size / abs_x.size

        ax.set_title(f'{title}\nmedian {median:.3g}   {retained:.0%} in window',
                     color=FG, fontsize=11)
        ax.set_xlabel('|x|  (median / 10  to  median * 10)')
        ax.set_ylabel('windowed density')

    plt.tight_layout()
    save_figure(fig, experiment_path('reciprocal.png'))


if __name__ == '__main__':
    main()
