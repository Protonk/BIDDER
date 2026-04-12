"""
Polar shutter: first-digit dial vs time for the two contrasting demos.

Angle is first-digit sector (1..9, read clockwise from top).
Radius is op index (centre = initial state, edge = final state).
"""

import numpy as np
import matplotlib.pyplot as plt

from common import (
    BG, CMAP, FG, SPINE,
    experiment_path,
    load_checkpoints,
    project_to_digit_hist,
    save_figure,
)


PANELS = [
    ('add_mult_alternating', 'add/mult alternating'),
    ('bs12_walk', 'BS(1,2) walk'),
]


def main():
    projected = {}
    vmax = 0.0
    for name, _ in PANELS:
        ckpts = load_checkpoints(experiment_path(f'data_{name}.npz'))
        digit_hist = project_to_digit_hist(ckpts['log_mantissa_hist'])
        projected[name] = digit_hist
        vmax = max(vmax, float(digit_hist[1:].max()))

    fig, axes = plt.subplots(1, 2, figsize=(14, 7),
                             subplot_kw={'projection': 'polar'})
    fig.patch.set_facecolor(BG)

    mesh = None
    for ax, (name, title) in zip(axes, PANELS):
        ax.set_facecolor(BG)
        digit_hist = projected[name]
        K = digit_hist.shape[0]

        theta_edges = np.linspace(0.0, 2.0 * np.pi, 10)
        r_edges = np.linspace(0.0, 1.0, K + 1)
        mesh = ax.pcolormesh(
            theta_edges, r_edges, digit_hist,
            cmap=CMAP, vmin=0.0, vmax=vmax, shading='flat',
        )

        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        angles_deg = np.arange(0, 360, 40) + 20
        ax.set_thetagrids(angles_deg, labels=[str(d) for d in range(1, 10)])
        ax.set_yticks([])
        ax.tick_params(colors=FG)
        ax.set_title(title, color=FG, fontsize=13, pad=18)
        ax.grid(color='#333', alpha=0.4)
        ax.spines['polar'].set_color(SPINE)

    cbar = fig.colorbar(mesh, ax=axes.tolist(), shrink=0.75, pad=0.08)
    cbar.set_label('digit mass', color=FG)
    cbar.ax.tick_params(colors=FG)
    for spine in cbar.ax.spines.values():
        spine.set_color(SPINE)

    save_figure(fig, experiment_path('shutter_polar.png'))


if __name__ == '__main__':
    main()
