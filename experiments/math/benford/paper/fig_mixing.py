"""
Figure 1 for PNAS paper: two-panel contrast of digit-proportion
convergence under pure addition vs. mixed arithmetic (BS(1,2)).

Run: sage -python fig_mixing.py
"""

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

from common import load_checkpoints, project_to_digit_hist

# --- Benford targets ---
BENFORD = np.array([np.log10(1 + 1/d) for d in range(1, 10)])

# --- Color palette: 9 distinguishable colors, colorblind-safe ---
# Using a curated set that works in both color and grayscale ordering
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


def load_digit_proportions(name):
    """Load checkpoint data and return (steps, digit_proportions).
    digit_proportions has shape (n_checkpoints, 9)."""
    path = os.path.join(PARENT, f'data_{name}.npz')
    ckpts = load_checkpoints(path)
    steps = ckpts['step']
    digit_hist = project_to_digit_hist(ckpts['log_mantissa_hist'])
    return steps, digit_hist


def plot_panel(ax, steps, digit_hist, title, show_ylabel=True,
               max_step=1000, ylim=(0, 0.42)):
    """Plot 9 digit-proportion lines with Benford targets."""
    mask = steps <= max_step
    s = steps[mask]
    dh = digit_hist[mask]

    for d in range(9):
        ax.plot(s, dh[:, d], color=COLORS[d], linewidth=1.3,
                label=f'{d+1}', alpha=0.85, zorder=2)

    # Benford targets as thin dashed lines
    for d in range(9):
        ax.axhline(BENFORD[d], color=COLORS[d], linestyle='--',
                   linewidth=0.5, alpha=0.4, zorder=1)

    ax.set_xlim(0, max_step)
    ax.set_ylim(*ylim)
    ax.set_xlabel('operation count', fontsize=8.5)
    if show_ylabel:
        ax.set_ylabel('digit proportion', fontsize=8.5)
    ax.set_title(title, fontsize=9.5, fontweight='bold', pad=4)
    ax.tick_params(labelsize=7.5)
    ax.xaxis.set_major_locator(MaxNLocator(5))

    ax.grid(True, which='major', color='#dddddd', linewidth=0.3,
            alpha=0.7, zorder=0)
    ax.set_facecolor('white')


def main():
    steps_add, dh_add = load_digit_proportions('pure_add')
    steps_bs, dh_bs = load_digit_proportions('bs12_walk')

    # --- Figure: PNAS column width ~8.7cm, we'll do ~17cm (two-column) ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.7, 2.8),
                                    sharey=True)
    fig.patch.set_facecolor('white')

    plot_panel(ax1, steps_add, dh_add, 'addition only',
               show_ylabel=True, max_step=1000)
    plot_panel(ax2, steps_bs, dh_bs, 'mixed arithmetic',
               show_ylabel=False, max_step=1000)

    # Digit legend: compact, top-right of left panel where there's
    # space between the d=1 line and the y-axis top
    handles, labels = ax1.get_legend_handles_labels()
    ax1.legend(handles, labels, loc='upper right', fontsize=5.5,
               frameon=True, facecolor='white', edgecolor='#cccccc',
               ncol=3, borderpad=0.3, labelspacing=0.15,
               handlelength=1.0, columnspacing=0.6,
               title='digit', title_fontsize=6)

    fig.tight_layout(w_pad=1.0)

    out = os.path.join(HERE, 'fig_mixing.png')
    fig.savefig(out, dpi=300, bbox_inches='tight', facecolor='white')
    print(f'Saved: {out}')
    plt.close(fig)


if __name__ == '__main__':
    main()
