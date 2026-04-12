"""
Rolling-shutter composite of checkpoint log-mantissa densities.
"""

import numpy as np
import matplotlib.pyplot as plt

from common import (
    BENFORD_BOUNDARIES_BASE10,
    CMAP,
    FG,
    BG,
    SPINE,
    experiment_path,
    load_checkpoints,
    save_figure,
    setup_dark_axes,
)


PANELS = [
    ('add_mult_alternating', 'add/mult alternating'),
    ('bs12_walk', 'BS(1,2) walk'),
    ('front_loaded', 'front-loaded freeze'),
    ('pure_add', 'pure add'),
]


def main():
    loaded = [(title, load_checkpoints(experiment_path(f'data_{name}.npz'))) for name, title in PANELS]
    vmax = np.percentile(
        np.concatenate([ckpts['log_mantissa_hist'].ravel() for _, ckpts in loaded]),
        99.5,
    )

    fig = plt.figure(figsize=(14.5, 10.5), constrained_layout=True)
    fig.patch.set_facecolor(BG)
    grid = fig.add_gridspec(2, 3, width_ratios=(1.0, 1.0, 0.055))
    axes = [
        fig.add_subplot(grid[0, 0]),
        fig.add_subplot(grid[0, 1]),
        fig.add_subplot(grid[1, 0]),
        fig.add_subplot(grid[1, 1]),
    ]
    cax = fig.add_subplot(grid[:, 2])
    image = None

    for ax, (title, ckpts) in zip(axes, loaded):
        setup_dark_axes(ax)
        max_step = float(ckpts['step'][-1])
        image = ax.imshow(
            ckpts['log_mantissa_hist'],
            origin='upper',
            aspect='auto',
            cmap=CMAP,
            extent=[0.0, 1.0, max_step, 0.0],
            vmin=0.0,
            vmax=vmax,
            interpolation='nearest',
        )
        for boundary in BENFORD_BOUNDARIES_BASE10:
            ax.axvline(boundary, color=FG, linewidth=0.6, alpha=0.28)
        ax.set_xlim(0.0, 1.0)
        ax.set_title(title, color=FG, fontsize=12)

    axes[0].set_ylabel('op index')
    axes[2].set_ylabel('op index')
    axes[2].set_xlabel('log10 mantissa')
    axes[3].set_xlabel('log10 mantissa')
    axes[0].tick_params(labelbottom=False)
    axes[1].tick_params(labelbottom=False)

    cbar = fig.colorbar(image, cax=cax)
    cbar.ax.tick_params(colors=FG)
    cbar.set_label('density per mantissa bin', color=FG)
    cbar.ax.set_facecolor(BG)
    for spine in cbar.ax.spines.values():
        spine.set_color(SPINE)
    save_figure(fig, experiment_path('shutter.png'))


if __name__ == '__main__':
    main()
