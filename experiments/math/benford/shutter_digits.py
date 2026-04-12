"""
First-digit shutter: 2x2 composite in discrete digit coordinates.

Each panel stacks checkpointed first-digit occupancy over op index.
Digit projection is exact against the piecewise-constant assumption
on the 256-bin base-10 log-mantissa histogram that the demos record.
"""

import numpy as np
import matplotlib.pyplot as plt

from common import (
    BG, CMAP, FG, SPINE,
    experiment_path,
    load_checkpoints,
    project_to_digit_hist,
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
    projected = {}
    vmax = 0.0
    for name, _ in PANELS:
        ckpts = load_checkpoints(experiment_path(f'data_{name}.npz'))
        digit_hist = project_to_digit_hist(ckpts['log_mantissa_hist'])
        projected[name] = (ckpts['step'], digit_hist)
        # Ignore the first checkpoint when choosing the color range:
        # demos that start from a delta would otherwise pin vmax at 1.0.
        vmax = max(vmax, float(digit_hist[1:].max()))

    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    fig.patch.set_facecolor(BG)

    im = None
    for ax, (name, title) in zip(axes.ravel(), PANELS):
        setup_dark_axes(ax)
        step, digit_hist = projected[name]
        extent = (0.5, 9.5, 0.0, float(step[-1]))
        im = ax.imshow(
            digit_hist,
            aspect='auto',
            origin='lower',
            extent=extent,
            cmap=CMAP,
            vmin=0.0,
            vmax=vmax,
            interpolation='nearest',
        )
        ax.set_xticks(range(1, 10))
        ax.set_xlabel('first digit')
        ax.set_ylabel('op index')
        ax.set_title(title, color=FG, fontsize=12)
        for d in range(1, 10):
            ax.axvline(d + 0.5, color='#222', linewidth=0.5, alpha=0.7)

    cbar = fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.75, pad=0.02)
    cbar.set_label('digit mass', color=FG)
    cbar.ax.tick_params(colors=FG)
    for spine in cbar.ax.spines.values():
        spine.set_color(SPINE)

    save_figure(fig, experiment_path('shutter_digits.png'))


if __name__ == '__main__':
    main()
