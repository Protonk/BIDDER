"""
numpy_comparison.py — Re-run all four demo schedules using vanilla
numpy PRNG (no BIDDER), save under data_numpy_* names, and render
numpy_shutter.png and numpy_shutter_digits.png.

Uses a different master seed so the data is genuinely independent
of whatever the current data_*.npz files were generated with.
"""

import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from common import (
    BG, CMAP, FG, SPINE,
    BENFORD_BOUNDARIES_BASE10,
    LOG_MANTISSA_BINS,
    N_WALKERS,
    TARGET_CHECKPOINTS,
    add_uniform,
    bs12_step,
    experiment_path,
    load_checkpoints,
    mul_constant,
    project_to_digit_hist,
    run_schedule,
    save_checkpoints,
    save_figure,
    setup_dark_axes,
)


NUMPY_SEED = 0xCAFE_BABE


DEMOS = [
    (
        'numpy_add_mult_alternating',
        'add/mult alternating  (numpy)',
        lambda: (
            sum(([('add', 500, add_uniform(-1.0, 1.0)),
                  ('mul', 1, mul_constant(2.0))]
                 for _ in range(20)), []),
            1.0,
        ),
    ),
    (
        'numpy_bs12_walk',
        'BS(1,2) walk  (numpy)',
        lambda: (
            [('bs12', 20_000, bs12_step())],
            math.sqrt(2.0),
        ),
    ),
    (
        'numpy_front_loaded',
        'front-loaded freeze  (numpy)',
        lambda: (
            [
                ('mul', 500, mul_constant(2.0)),
                ('add', 2_000, add_uniform(-1.0, 1.0)),
                ('mul', 1, mul_constant(2.0)),
                ('add', 10_000, add_uniform(-1.0, 1.0)),
            ],
            None,  # log-uniform initial, handled below
        ),
    ),
    (
        'numpy_pure_add',
        'pure add  (numpy)',
        lambda: (
            [('add', 20_000, add_uniform(-1.0, 1.0))],
            1.0,
        ),
    ),
]


def run_demos():
    rng_master = np.random.default_rng(NUMPY_SEED)

    for name, title, make_schedule in DEMOS:
        ops, initial = make_schedule()

        if initial is None:
            local_rng = np.random.default_rng(NUMPY_SEED ^ 0xF10ADED)
            initial = np.power(10.0, local_rng.uniform(0.0, 1.0, size=N_WALKERS))

        demo_seed = int(rng_master.integers(0, 2**31))
        ckpts = run_schedule(ops, initial=initial, seed=demo_seed)
        path = experiment_path(f'data_{name}.npz')
        save_checkpoints(path, ckpts)
        print(f'  {name}: final L1={float(ckpts["l1"][-1]):.4f}')


def render_shutter():
    panels = [
        ('numpy_add_mult_alternating', 'add/mult alternating  (numpy)'),
        ('numpy_bs12_walk', 'BS(1,2) walk  (numpy)'),
        ('numpy_front_loaded', 'front-loaded freeze  (numpy)'),
        ('numpy_pure_add', 'pure add  (numpy)'),
    ]
    loaded = [
        (title, load_checkpoints(experiment_path(f'data_{name}.npz')))
        for name, title in panels
    ]
    vmax = np.percentile(
        np.concatenate([c['log_mantissa_hist'].ravel() for _, c in loaded]),
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
            origin='upper', aspect='auto', cmap=CMAP,
            extent=[0.0, 1.0, max_step, 0.0],
            vmin=0.0, vmax=vmax, interpolation='nearest',
        )
        for b in BENFORD_BOUNDARIES_BASE10:
            ax.axvline(b, color=FG, linewidth=0.6, alpha=0.28)
        ax.set_xlim(0.0, 1.0)
        ax.set_title(title, color=FG, fontsize=11)
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
    save_figure(fig, experiment_path('numpy_shutter.png'))


def render_shutter_digits():
    panels = [
        ('numpy_add_mult_alternating', 'add/mult alternating  (numpy)'),
        ('numpy_bs12_walk', 'BS(1,2) walk  (numpy)'),
        ('numpy_front_loaded', 'front-loaded freeze  (numpy)'),
        ('numpy_pure_add', 'pure add  (numpy)'),
    ]
    projected = {}
    vmax = 0.0
    for name, _ in panels:
        ckpts = load_checkpoints(experiment_path(f'data_{name}.npz'))
        digit_hist = project_to_digit_hist(ckpts['log_mantissa_hist'])
        projected[name] = (ckpts['step'], digit_hist)
        vmax = max(vmax, float(digit_hist[1:].max()))

    fig, axes = plt.subplots(2, 2, figsize=(14, 11))
    fig.patch.set_facecolor(BG)
    im = None
    for ax, (name, title) in zip(axes.ravel(), panels):
        setup_dark_axes(ax)
        step, digit_hist = projected[name]
        extent = (0.5, 9.5, 0.0, float(step[-1]))
        im = ax.imshow(
            digit_hist, aspect='auto', origin='lower', extent=extent,
            cmap=CMAP, vmin=0.0, vmax=vmax, interpolation='nearest',
        )
        ax.set_xticks(range(1, 10))
        ax.set_xlabel('first digit')
        ax.set_ylabel('op index')
        ax.set_title(title, color=FG, fontsize=11)
        for d in range(1, 10):
            ax.axvline(d + 0.5, color='#222', linewidth=0.5, alpha=0.7)
    cbar = fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.75, pad=0.02)
    cbar.set_label('digit mass', color=FG)
    cbar.ax.tick_params(colors=FG)
    for spine in cbar.ax.spines.values():
        spine.set_color(SPINE)
    save_figure(fig, experiment_path('numpy_shutter_digits.png'))


def main():
    print('Running demos with vanilla numpy PRNG...')
    run_demos()
    print('Rendering numpy_shutter.png...')
    render_shutter()
    print('Rendering numpy_shutter_digits.png...')
    render_shutter_digits()


if __name__ == '__main__':
    main()
