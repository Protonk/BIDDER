"""
Figure 1 for PNAS paper: four-panel contrast.

    addition only        |  multiplication only
    alternating add/mult |  mixed arithmetic (BS(1,2))

Shows that:
- Addition alone: no convergence (Schatte)
- Multiplication alone: convergence (Schatte)
- Alternating add then mult: no convergence (!!!)
- Mixed (BS(1,2)): fast convergence

The key insight: it's not enough to have both operations.
The group relation bab⁻¹ = a² is what matters.

Run: sage -python fig_four_panel.py
"""

import math
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.join(HERE, '..')
sys.path.insert(0, PARENT)

from common import (
    LOG_MANTISSA_BINS,
    load_checkpoints,
    log_mantissa,
    project_to_digit_hist,
)

# --- Benford targets ---
BENFORD = np.array([np.log10(1 + 1/d) for d in range(1, 10)])

# --- Colors ---
COLORS = [
    '#e41a1c',  # d=1  red
    '#377eb8',  # d=2  blue
    '#4daf4a',  # d=3  green
    '#984ea3',  # d=4  purple
    '#ff7f00',  # d=5  orange
    '#a65628',  # d=6  brown
    '#f781bf',  # d=7  pink
    '#666666',  # d=8  gray
    '#17becf',  # d=9  cyan
]


def generate_mul_only(n_walkers=20_000, n_steps=1000, n_checkpoints=200,
                      seed=0xBEEF):
    """Random ×2 / ÷2 with equal probability. Pure multiplicative walk."""
    rng = np.random.default_rng(seed)
    x = np.full(n_walkers, math.sqrt(2.0), dtype=np.float64)

    checkpoint_interval = max(1, n_steps // n_checkpoints)
    steps_out = [0]
    # Record initial histogram
    m = log_mantissa(x, 10.0)
    hist, _ = np.histogram(m, bins=LOG_MANTISSA_BINS, range=(0.0, 1.0))
    hists = [hist.astype(np.float64) / hist.sum()]

    for t in range(1, n_steps + 1):
        choice = rng.integers(0, 2, size=n_walkers)
        x[choice == 0] *= 2.0
        x[choice == 1] *= 0.5
        if t % checkpoint_interval == 0 or t == n_steps:
            m = log_mantissa(x, 10.0)
            hist, _ = np.histogram(m, bins=LOG_MANTISSA_BINS,
                                   range=(0.0, 1.0))
            hists.append(hist.astype(np.float64) / hist.sum())
            steps_out.append(t)

    return np.array(steps_out), np.array(hists, dtype=np.float32)


def generate_alternating_strict(n_walkers=20_000, n_steps=1000,
                                n_checkpoints=200, adds_per_cycle=10,
                                seed=0xCAFE):
    """Strictly alternating: adds_per_cycle additions of ±1, then one
    ×2 or ÷2, repeat. Operations are present but sequenced, not mixed."""
    rng = np.random.default_rng(seed)
    x = np.full(n_walkers, math.sqrt(2.0), dtype=np.float64)

    checkpoint_interval = max(1, n_steps // n_checkpoints)
    steps_out = [0]
    m = log_mantissa(x, 10.0)
    hist, _ = np.histogram(m, bins=LOG_MANTISSA_BINS, range=(0.0, 1.0))
    hists = [hist.astype(np.float64) / hist.sum()]

    t = 0
    while t < n_steps:
        # Additive phase
        for _ in range(min(adds_per_cycle, n_steps - t)):
            t += 1
            choice = rng.integers(0, 2, size=n_walkers)
            x[choice == 0] += 1.0
            x[choice == 1] -= 1.0
            if t % checkpoint_interval == 0 or t == n_steps:
                m = log_mantissa(x, 10.0)
                hist, _ = np.histogram(m, bins=LOG_MANTISSA_BINS,
                                       range=(0.0, 1.0))
                hists.append(hist.astype(np.float64) / hist.sum())
                steps_out.append(t)
            if t >= n_steps:
                break
        if t >= n_steps:
            break
        # One multiplicative step
        t += 1
        choice = rng.integers(0, 2, size=n_walkers)
        x[choice == 0] *= 2.0
        x[choice == 1] *= 0.5
        if t % checkpoint_interval == 0 or t == n_steps:
            m = log_mantissa(x, 10.0)
            hist, _ = np.histogram(m, bins=LOG_MANTISSA_BINS,
                                   range=(0.0, 1.0))
            hists.append(hist.astype(np.float64) / hist.sum())
            steps_out.append(t)

    return np.array(steps_out), np.array(hists, dtype=np.float32)


def generate_bs12(n_walkers=20_000, n_steps=1000, n_checkpoints=200,
                  seed=0xBADD):
    """Symmetric BS(1,2): ±1, ×2, ÷2 each with probability 1/4."""
    rng = np.random.default_rng(seed)
    x = np.full(n_walkers, math.sqrt(2.0), dtype=np.float64)

    checkpoint_interval = max(1, n_steps // n_checkpoints)
    steps_out = [0]
    m = log_mantissa(x, 10.0)
    hist, _ = np.histogram(m, bins=LOG_MANTISSA_BINS, range=(0.0, 1.0))
    hists = [hist.astype(np.float64) / hist.sum()]

    for t in range(1, n_steps + 1):
        choice = rng.integers(0, 4, size=n_walkers)
        x[choice == 0] += 1.0
        x[choice == 1] -= 1.0
        x[choice == 2] *= 2.0
        x[choice == 3] *= 0.5
        if t % checkpoint_interval == 0 or t == n_steps:
            m = log_mantissa(x, 10.0)
            hist, _ = np.histogram(m, bins=LOG_MANTISSA_BINS,
                                   range=(0.0, 1.0))
            hists.append(hist.astype(np.float64) / hist.sum())
            steps_out.append(t)

    return np.array(steps_out), np.array(hists, dtype=np.float32)


def generate_pure_add(n_walkers=20_000, n_steps=1000, n_checkpoints=200,
                      seed=0xDEAD):
    """Pure addition: ±1 with equal probability."""
    rng = np.random.default_rng(seed)
    x = np.full(n_walkers, math.sqrt(2.0), dtype=np.float64)

    checkpoint_interval = max(1, n_steps // n_checkpoints)
    steps_out = [0]
    m = log_mantissa(x, 10.0)
    hist, _ = np.histogram(m, bins=LOG_MANTISSA_BINS, range=(0.0, 1.0))
    hists = [hist.astype(np.float64) / hist.sum()]

    for t in range(1, n_steps + 1):
        choice = rng.integers(0, 2, size=n_walkers)
        x[choice == 0] += 1.0
        x[choice == 1] -= 1.0
        if t % checkpoint_interval == 0 or t == n_steps:
            m = log_mantissa(x, 10.0)
            hist, _ = np.histogram(m, bins=LOG_MANTISSA_BINS,
                                   range=(0.0, 1.0))
            hists.append(hist.astype(np.float64) / hist.sum())
            steps_out.append(t)

    return np.array(steps_out), np.array(hists, dtype=np.float32)


def digit_proportions_from_hist(log_mantissa_hist):
    """Convert 256-bin log-mantissa histograms to 9-digit proportions."""
    return project_to_digit_hist(log_mantissa_hist)


def plot_panel(ax, steps, digit_hist, title, show_ylabel=True,
               show_xlabel=True, max_step=1000, ylim=(0, 0.42)):
    """Plot 9 digit-proportion lines with Benford targets."""
    mask = steps <= max_step
    s = steps[mask]
    dh = digit_hist[mask]

    for d in range(9):
        ax.plot(s, dh[:, d], color=COLORS[d], linewidth=1.1,
                label=f'{d+1}', alpha=0.85, zorder=2)

    for d in range(9):
        ax.axhline(BENFORD[d], color=COLORS[d], linestyle='--',
                   linewidth=0.5, alpha=0.35, zorder=1)

    ax.set_xlim(0, max_step)
    ax.set_ylim(*ylim)
    if show_xlabel:
        ax.set_xlabel('operation count', fontsize=7.5)
    if show_ylabel:
        ax.set_ylabel('digit proportion', fontsize=7.5)
    ax.set_title(title, fontsize=8.5, fontweight='bold', pad=3)
    ax.tick_params(labelsize=6.5)
    ax.xaxis.set_major_locator(MaxNLocator(4))

    ax.grid(True, which='major', color='#dddddd', linewidth=0.3,
            alpha=0.7, zorder=0)
    ax.set_facecolor('white')


def main():
    print('Generating pure addition...')
    s_add, h_add = generate_pure_add()
    dh_add = digit_proportions_from_hist(h_add)

    print('Generating multiplication only...')
    s_mul, h_mul = generate_mul_only()
    dh_mul = digit_proportions_from_hist(h_mul)

    print('Generating alternating add/mult...')
    s_alt, h_alt = generate_alternating_strict()
    dh_alt = digit_proportions_from_hist(h_alt)

    print('Generating BS(1,2) mixed...')
    s_bs, h_bs = generate_bs12()
    dh_bs = digit_proportions_from_hist(h_bs)

    # --- 2x2 figure ---
    fig, axes = plt.subplots(2, 2, figsize=(6.7, 4.8), sharex=True,
                             sharey=True)
    fig.patch.set_facecolor('white')

    plot_panel(axes[0, 0], s_add, dh_add, 'addition only',
               show_ylabel=True, show_xlabel=False)
    plot_panel(axes[0, 1], s_mul, dh_mul, 'multiplication only',
               show_ylabel=False, show_xlabel=False)
    plot_panel(axes[1, 0], s_alt, dh_alt, 'alternating add / mult',
               show_ylabel=True, show_xlabel=True)
    plot_panel(axes[1, 1], s_bs, dh_bs, 'mixed (BS(1,2))',
               show_ylabel=False, show_xlabel=True)

    # Digit legend in the addition panel (top-left) where there's room
    handles, labels = axes[0, 0].get_legend_handles_labels()
    axes[0, 0].legend(handles, labels, loc='upper right', fontsize=5,
                      frameon=True, facecolor='white', edgecolor='#cccccc',
                      ncol=3, borderpad=0.3, labelspacing=0.15,
                      handlelength=1.0, columnspacing=0.5,
                      title='digit', title_fontsize=5.5)

    fig.tight_layout(h_pad=0.8, w_pad=0.8)

    out = os.path.join(HERE, 'fig_four_panel.png')
    fig.savefig(out, dpi=300, bbox_inches='tight', facecolor='white')
    print(f'Saved: {out}')
    plt.close(fig)


if __name__ == '__main__':
    main()
