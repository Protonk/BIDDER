"""
Hybrid figure: L1 convergence curves + endpoint digit bars.

Left panel:  L1 distance to Benford vs operation count (log y-axis)
Right panel: digit proportions at t=1000 for all 3 regimes vs Benford

Three regimes:
  - addition only (±1)
  - alternating add/mult (10 adds then 1 ×2/÷2, repeat)
  - mixed BS(1,2) (±1, ×2/÷2 each with prob 1/4)

Run: sage -python fig_hybrid.py
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

from common import LOG_MANTISSA_BINS, log_mantissa, project_to_digit_hist

BENFORD = np.array([np.log10(1 + 1/d) for d in range(1, 10)])

# Colors for the three regimes
C_ADD = '#e41a1c'   # red
C_ALT = '#984ea3'   # purple
C_BS  = '#377eb8'   # blue


def l1_from_hist(hist):
    uniform = np.full_like(hist, 1.0 / hist.shape[-1])
    return np.sum(np.abs(hist - uniform), axis=-1)


def run_walk(step_fn, n_walkers, n_steps, n_checkpoints, seed):
    rng = np.random.default_rng(seed)
    x = np.full(n_walkers, math.sqrt(2.0), dtype=np.float64)

    ckpt_interval = max(1, n_steps // n_checkpoints)
    steps_out = []
    l1_out = []
    hists_out = []

    def record(t):
        m = log_mantissa(x, 10.0)
        hist, _ = np.histogram(m, bins=LOG_MANTISSA_BINS, range=(0.0, 1.0))
        h = hist.astype(np.float64) / hist.sum()
        steps_out.append(t)
        l1_out.append(l1_from_hist(h))
        hists_out.append(h.copy())

    record(0)
    for t in range(1, n_steps + 1):
        step_fn(rng, x)
        if t % ckpt_interval == 0 or t == n_steps:
            record(t)

    return (np.array(steps_out), np.array(l1_out),
            np.array(hists_out, dtype=np.float32))


def step_add(rng, x):
    choice = rng.integers(0, 2, size=x.size)
    x[choice == 0] += 1.0
    x[choice == 1] -= 1.0


_alt_counter = [0]
_ALT_ADDS_PER_MUL = 10

def step_alternating(rng, x):
    _alt_counter[0] += 1
    if _alt_counter[0] % (_ALT_ADDS_PER_MUL + 1) == 0:
        choice = rng.integers(0, 2, size=x.size)
        x[choice == 0] *= 2.0
        x[choice == 1] *= 0.5
    else:
        choice = rng.integers(0, 2, size=x.size)
        x[choice == 0] += 1.0
        x[choice == 1] -= 1.0


def step_bs12(rng, x):
    choice = rng.integers(0, 4, size=x.size)
    x[choice == 0] += 1.0
    x[choice == 1] -= 1.0
    x[choice == 2] *= 2.0
    x[choice == 3] *= 0.5


def main():
    N_WALKERS = 50_000
    N_STEPS = 1000
    N_CKPT = 500

    print('Running addition only...')
    s_add, l1_add, h_add = run_walk(step_add, N_WALKERS, N_STEPS, N_CKPT,
                                     seed=0x1111)

    print('Running alternating add/mult...')
    _alt_counter[0] = 0
    s_alt, l1_alt, h_alt = run_walk(step_alternating, N_WALKERS, N_STEPS,
                                     N_CKPT, seed=0x3333)

    print('Running BS(1,2) mixed...')
    s_bs, l1_bs, h_bs = run_walk(step_bs12, N_WALKERS, N_STEPS, N_CKPT,
                                  seed=0x4444)

    # Endpoint digit proportions (last checkpoint)
    dh_add = project_to_digit_hist(h_add[-1:])[-1]
    dh_alt = project_to_digit_hist(h_alt[-1:])[-1]
    dh_bs  = project_to_digit_hist(h_bs[-1:])[-1]

    noise_floor = math.sqrt(2.0 * LOG_MANTISSA_BINS / (math.pi * N_WALKERS))

    # --- Figure: 2 panels, left wider ---
    fig, (ax_l1, ax_bar) = plt.subplots(
        1, 2, figsize=(6.7, 2.8),
        gridspec_kw={'width_ratios': [1.4, 1.0]},
    )
    fig.patch.set_facecolor('white')

    # --- Left panel: L1 curves ---
    ax_l1.set_facecolor('white')
    ax_l1.semilogy(s_add, l1_add, color=C_ADD, linewidth=1.3,
                   label='addition only', zorder=3)
    ax_l1.semilogy(s_alt, l1_alt, color=C_ALT, linewidth=1.3,
                   label='alternating add/mult', zorder=3)
    ax_l1.semilogy(s_bs, l1_bs, color=C_BS, linewidth=1.5,
                   label='mixed (BS(1,2))', zorder=4)
    ax_l1.axhline(noise_floor, color='#999999', linestyle=':', linewidth=0.7,
                  zorder=1)

    ax_l1.set_xlim(0, 1000)
    ax_l1.set_ylim(0.008, 2.5)
    ax_l1.set_xlabel('operation count', fontsize=8)
    ax_l1.set_ylabel('L1 distance to Benford', fontsize=8)
    ax_l1.tick_params(labelsize=7)
    ax_l1.grid(True, which='major', color='#dddddd', linewidth=0.3, zorder=0)
    ax_l1.grid(True, which='minor', color='#eeeeee', linewidth=0.2, zorder=0)
    ax_l1.legend(loc='center right', fontsize=6, frameon=True,
                 facecolor='white', edgecolor='#cccccc', borderpad=0.4,
                 labelspacing=0.3, handlelength=1.5)
    ax_l1.set_title('convergence rate', fontsize=9, fontweight='bold', pad=4)

    # --- Right panel: endpoint digit bars ---
    ax_bar.set_facecolor('white')
    digits = np.arange(1, 10)
    bar_w = 0.22
    offsets = np.array([-1, 0, 1]) * bar_w

    ax_bar.bar(digits + offsets[0], dh_add, bar_w, color=C_ADD,
               alpha=0.8, label='addition', zorder=2)
    ax_bar.bar(digits + offsets[1], dh_alt, bar_w, color=C_ALT,
               alpha=0.8, label='alternating', zorder=2)
    ax_bar.bar(digits + offsets[2], dh_bs, bar_w, color=C_BS,
               alpha=0.8, label='BS(1,2)', zorder=2)

    # Benford targets as markers
    ax_bar.scatter(digits, BENFORD, marker='_', color='black', s=60,
                   linewidths=1.5, zorder=5, label='Benford')

    ax_bar.set_xlim(0.3, 9.7)
    ax_bar.set_ylim(0, 0.35)
    ax_bar.set_xlabel('leading digit', fontsize=8)
    ax_bar.set_ylabel('proportion at t = 1000', fontsize=8)
    ax_bar.set_xticks(digits)
    ax_bar.tick_params(labelsize=7)
    ax_bar.grid(True, which='major', axis='y', color='#dddddd',
                linewidth=0.3, zorder=0)
    ax_bar.legend(loc='upper right', fontsize=5.5, frameon=True,
                  facecolor='white', edgecolor='#cccccc', borderpad=0.3,
                  labelspacing=0.2, handlelength=1.0, ncol=2)
    ax_bar.set_title('digit distribution at t = 1000', fontsize=9,
                     fontweight='bold', pad=4)

    fig.tight_layout(w_pad=1.5)

    out = os.path.join(HERE, 'fig_hybrid.png')
    fig.savefig(out, dpi=300, bbox_inches='tight', facecolor='white')
    print(f'Saved: {out}')
    plt.close(fig)


if __name__ == '__main__':
    main()
