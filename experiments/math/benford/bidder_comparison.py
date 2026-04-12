"""
bidder_comparison.py — Re-run the BS(1,2) and pure-add demos using
BIDDER's keyed permutation as the randomness source.

Strategy: for each walker, create one BidderBlock whose period covers
all steps, iterate it ONCE to get a full choice/increment array, then
run the walk with numpy. This avoids per-step Python loops over B.at().

Only bs12_walk and pure_add are compared (the two demos where the
generator matters). add_mult_alternating and front_loaded use the
numpy data since their mul steps are deterministic.
"""

import math
import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DIST = os.path.join(ROOT, 'dist')
sys.path.insert(0, DIST)

import bidder

from common import (
    BG, CMAP, FG, SPINE,
    BENFORD_BOUNDARIES_BASE10,
    LOG_MANTISSA_BINS,
    N_WALKERS,
    TARGET_CHECKPOINTS,
    experiment_path,
    load_checkpoints,
    log_mantissa,
    l1_to_uniform,
    project_to_digit_hist,
    save_figure,
    setup_dark_axes,
    _mantissa_hist,
)


N_STEPS_BS12 = 20_000
N_STEPS_PURE_ADD = 20_000


def generate_bs12_choices(n_walkers, n_steps):
    """Generate a (n_steps, n_walkers) choice array in {0,1,2,3}
    using one BidderBlock per walker."""
    choices = np.zeros((n_steps, n_walkers), dtype=np.int8)
    for w in range(n_walkers):
        key = f'bs12:walker:{w}'.encode()
        B = bidder.cipher(period=n_steps, key=key)
        walker_choices = np.array(list(B), dtype=np.int64)
        choices[:, w] = (walker_choices % 4).astype(np.int8)
        if (w + 1) % 2000 == 0:
            print(f'    bs12 choices: {w+1}/{n_walkers} walkers')
    return choices


def generate_add_increments(n_walkers, n_steps, lo, hi):
    """Generate a (n_steps, n_walkers) increment array using
    one BidderBlock per walker, mapping [0, period) -> [lo, hi)."""
    span = hi - lo
    increments = np.zeros((n_steps, n_walkers), dtype=np.float64)
    for w in range(n_walkers):
        key = f'add:walker:{w}'.encode()
        B = bidder.cipher(period=n_steps, key=key)
        raw = np.array(list(B), dtype=np.float64)
        increments[:, w] = lo + span * raw / n_steps
        if (w + 1) % 2000 == 0:
            print(f'    add increments: {w+1}/{n_walkers} walkers')
    return increments


def run_bs12(choices, initial):
    n_steps, n_walkers = choices.shape
    x = np.full(n_walkers, initial, dtype=np.float64)

    checkpoint_steps = np.unique(
        np.linspace(0, n_steps, TARGET_CHECKPOINTS + 1, dtype=np.int64)
    )

    steps_list = []
    histograms = []
    l1_values = []
    leading1 = []
    boundary = float(BENFORD_BOUNDARIES_BASE10[1])

    def record(step_index):
        mantissa = log_mantissa(x, 10.0)
        hist = _mantissa_hist(mantissa, LOG_MANTISSA_BINS)
        steps_list.append(step_index)
        histograms.append(hist.astype(np.float32))
        l1_values.append(np.float32(l1_to_uniform(hist)))
        leading1.append(np.float32(np.mean(mantissa < boundary)))

    record(0)
    ckpt_idx = 1

    for s in range(n_steps):
        c = choices[s]
        plus = c == 0
        minus = c == 1
        mul = c == 2
        div = c == 3
        x[plus] += 1.0
        x[minus] -= 1.0
        x[mul] *= 2.0
        x[div] *= 0.5

        if s + 1 == checkpoint_steps[ckpt_idx]:
            record(s + 1)
            ckpt_idx += 1
            if ckpt_idx >= len(checkpoint_steps):
                break

    return {
        'step': np.asarray(steps_list, dtype=np.int64),
        'log_mantissa_hist': np.asarray(histograms, dtype=np.float32),
        'l1': np.asarray(l1_values, dtype=np.float32),
        'leading_1_frac': np.asarray(leading1, dtype=np.float32),
        'final_abs_x': np.abs(x).astype(np.float64),
        'schedule_summary': np.asarray('bidder cipher bs12'),
    }


def run_pure_add(increments, initial):
    n_steps, n_walkers = increments.shape
    x = np.full(n_walkers, initial, dtype=np.float64)

    checkpoint_steps = np.unique(
        np.linspace(0, n_steps, TARGET_CHECKPOINTS + 1, dtype=np.int64)
    )

    steps_list = []
    histograms = []
    l1_values = []
    leading1 = []
    boundary = float(BENFORD_BOUNDARIES_BASE10[1])

    def record(step_index):
        mantissa = log_mantissa(x, 10.0)
        hist = _mantissa_hist(mantissa, LOG_MANTISSA_BINS)
        steps_list.append(step_index)
        histograms.append(hist.astype(np.float32))
        l1_values.append(np.float32(l1_to_uniform(hist)))
        leading1.append(np.float32(np.mean(mantissa < boundary)))

    record(0)
    ckpt_idx = 1

    for s in range(n_steps):
        x += increments[s]
        # BIDDER's grid-quantized increments can sum to exact zero;
        # nudge to keep log_mantissa happy.
        zeros = x == 0.0
        if zeros.any():
            x[zeros] = 1e-300

        if s + 1 == checkpoint_steps[ckpt_idx]:
            record(s + 1)
            ckpt_idx += 1
            if ckpt_idx >= len(checkpoint_steps):
                break

    return {
        'step': np.asarray(steps_list, dtype=np.int64),
        'log_mantissa_hist': np.asarray(histograms, dtype=np.float32),
        'l1': np.asarray(l1_values, dtype=np.float32),
        'leading_1_frac': np.asarray(leading1, dtype=np.float32),
        'final_abs_x': np.abs(x).astype(np.float64),
        'schedule_summary': np.asarray('bidder cipher pure_add'),
    }


def render_comparison():
    """2x2 shutter: top row = bidder, bottom row = numpy (existing data).
    Left column = bs12, right column = pure_add."""
    panels = [
        ('data_bidder_bs12_walk.npz', 'BS(1,2) walk  (bidder cipher)'),
        ('data_bidder_pure_add.npz', 'pure add  (bidder cipher)'),
        ('data_bs12_walk.npz', 'BS(1,2) walk  (numpy PRNG)'),
        ('data_pure_add.npz', 'pure add  (numpy PRNG)'),
    ]
    loaded = [
        (title, load_checkpoints(experiment_path(f)))
        for f, title in panels
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
    save_figure(fig, experiment_path('bidder_shutter.png'))


def main():
    bs12_path = experiment_path('data_bidder_bs12_walk.npz')
    if os.path.exists(bs12_path):
        print('bs12 data already exists, skipping generation.')
    else:
        print('Generating bs12 choice arrays with BIDDER cipher...')
        choices = generate_bs12_choices(N_WALKERS, N_STEPS_BS12)
        print('Running bs12 walk...')
        ckpts = run_bs12(choices, initial=math.sqrt(2.0))
        np.savez_compressed(bs12_path, **ckpts)
        print(f'  bs12_walk: final L1={float(ckpts["l1"][-1]):.4f}')
        del choices

    print('Generating pure_add increment arrays with BIDDER cipher...')
    increments = generate_add_increments(N_WALKERS, N_STEPS_PURE_ADD, -1.0, 1.0)

    print('Running pure_add...')
    ckpts = run_pure_add(increments, initial=1.0)
    np.savez_compressed(experiment_path('data_bidder_pure_add.npz'), **ckpts)
    print(f'  pure_add: final L1={float(ckpts["l1"][-1]):.4f}')

    del increments

    print('Rendering bidder_shutter.png (bidder vs numpy, 2x2)...')
    render_comparison()


if __name__ == '__main__':
    main()
