"""
Hybrid figure: L1 curves + digit bars at t=20 and t=200.

Three panels:
  Left:   L1 distance to Benford vs operation count (log y-axis)
  Middle: digit proportions at t=20 for all 3 regimes vs Benford
  Right:  digit proportions at t=200 for all 3 regimes vs Benford

Run: sage -python fig_hybrid3.py
"""

import math
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.join(HERE, '..')
sys.path.insert(0, PARENT)

from common import LOG_MANTISSA_BINS, log_mantissa, project_to_digit_hist

BENFORD = np.array([np.log10(1 + 1/d) for d in range(1, 10)])

C_ADD = '#e41a1c'
C_ALT = '#984ea3'
C_BS  = '#377eb8'


def l1_from_hist(hist):
    uniform = np.full_like(hist, 1.0 / hist.shape[-1])
    return np.sum(np.abs(hist - uniform), axis=-1)


def run_walk(step_fn, n_walkers, n_steps, seed):
    """Run with per-step checkpoints so we can snapshot at any t."""
    rng = np.random.default_rng(seed)
    x = np.full(n_walkers, math.sqrt(2.0), dtype=np.float64)

    steps_out = [0]
    l1_out = []
    hists_out = []

    def record(t):
        m = log_mantissa(x, 10.0)
        hist, _ = np.histogram(m, bins=LOG_MANTISSA_BINS, range=(0.0, 1.0))
        h = hist.astype(np.float64) / hist.sum()
        steps_out.append(t)
        l1_out.append(l1_from_hist(h))
        hists_out.append(h.copy())

    # Record t=0
    m = log_mantissa(x, 10.0)
    hist, _ = np.histogram(m, bins=LOG_MANTISSA_BINS, range=(0.0, 1.0))
    h = hist.astype(np.float64) / hist.sum()
    l1_out.append(l1_from_hist(h))
    hists_out.append(h.copy())

    # Checkpoint every 2 steps for smooth curves
    for t in range(1, n_steps + 1):
        step_fn(rng, x)
        if t % 2 == 0 or t == n_steps or t <= 30:
            m = log_mantissa(x, 10.0)
            hist, _ = np.histogram(m, bins=LOG_MANTISSA_BINS,
                                   range=(0.0, 1.0))
            h = hist.astype(np.float64) / hist.sum()
            steps_out.append(t)
            l1_out.append(l1_from_hist(h))
            hists_out.append(h.copy())

    return (np.array(steps_out), np.array(l1_out),
            np.array(hists_out, dtype=np.float32))


def step_add(rng, x):
    choice = rng.integers(0, 2, size=x.size)
    x[choice == 0] += 1.0
    x[choice == 1] -= 1.0


_alt_counter = [0]

def step_alternating(rng, x):
    _alt_counter[0] += 1
    if _alt_counter[0] % 11 == 0:  # 10 adds then 1 mul
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


def get_snapshot(steps, hists, target_t):
    """Get the digit proportions at the checkpoint closest to target_t."""
    idx = np.argmin(np.abs(steps - target_t))
    return project_to_digit_hist(hists[idx:idx+1])[0]


def main():
    N_WALKERS = 50_000
    N_STEPS = 1000

    print('Running addition only...')
    s_add, l1_add, h_add = run_walk(step_add, N_WALKERS, N_STEPS,
                                     seed=0x1111)

    print('Running alternating add/mult...')
    _alt_counter[0] = 0
    s_alt, l1_alt, h_alt = run_walk(step_alternating, N_WALKERS, N_STEPS,
                                     seed=0x3333)

    print('Running BS(1,2) mixed...')
    s_bs, l1_bs, h_bs = run_walk(step_bs12, N_WALKERS, N_STEPS,
                                  seed=0x4444)

    noise_floor = math.sqrt(2.0 * LOG_MANTISSA_BINS / (math.pi * N_WALKERS))

    # Snapshots
    T_EARLY = 20
    T_LATE = 200

    dh_add_early = get_snapshot(s_add, h_add, T_EARLY)
    dh_alt_early = get_snapshot(s_alt, h_alt, T_EARLY)
    dh_bs_early  = get_snapshot(s_bs, h_bs, T_EARLY)

    dh_add_late = get_snapshot(s_add, h_add, T_LATE)
    dh_alt_late = get_snapshot(s_alt, h_alt, T_LATE)
    dh_bs_late  = get_snapshot(s_bs, h_bs, T_LATE)

    # --- Figure ---
    fig, (ax_l1, ax_early, ax_late) = plt.subplots(
        1, 3, figsize=(7.5, 2.8),
        gridspec_kw={'width_ratios': [1.3, 1.0, 1.0]},
    )
    fig.patch.set_facecolor('white')

    # --- Panel A: L1 curves ---
    ax_l1.set_facecolor('white')
    ax_l1.semilogy(s_add, l1_add, color=C_ADD, linewidth=1.3,
                   label='addition only', zorder=3)
    ax_l1.semilogy(s_alt, l1_alt, color=C_ALT, linewidth=1.3,
                   label='alternating add/mult', zorder=3)
    ax_l1.semilogy(s_bs, l1_bs, color=C_BS, linewidth=1.5,
                   label='mixed (BS(1,2))', zorder=4)
    ax_l1.axhline(noise_floor, color='#999999', linestyle=':', linewidth=0.7,
                  zorder=1)

    # Mark the snapshot times
    ax_l1.axvline(T_EARLY, color='#888888', linestyle='--', linewidth=0.6,
                  alpha=0.6, zorder=1)
    ax_l1.axvline(T_LATE, color='#888888', linestyle='--', linewidth=0.6,
                  alpha=0.6, zorder=1)
    ax_l1.text(T_EARLY + 8, 2.0, f't={T_EARLY}', fontsize=6, color='#666666',
               va='top')
    ax_l1.text(T_LATE + 8, 2.0, f't={T_LATE}', fontsize=6, color='#666666',
               va='top')

    ax_l1.set_xlim(0, 1000)
    ax_l1.set_ylim(0.008, 2.8)
    ax_l1.set_xlabel('operation count', fontsize=8)
    ax_l1.set_ylabel('L1 distance to Benford', fontsize=8)
    ax_l1.tick_params(labelsize=7)
    ax_l1.grid(True, which='major', color='#dddddd', linewidth=0.3, zorder=0)
    ax_l1.grid(True, which='minor', color='#eeeeee', linewidth=0.2, zorder=0)
    ax_l1.legend(loc='center right', fontsize=5.5, frameon=True,
                 facecolor='white', edgecolor='#cccccc', borderpad=0.4,
                 labelspacing=0.25, handlelength=1.5)
    ax_l1.set_title('convergence', fontsize=9, fontweight='bold', pad=4)

    # --- Panels B & C: digit bars ---
    digits = np.arange(1, 10)
    bar_w = 0.22
    offsets = np.array([-1, 0, 1]) * bar_w

    for ax, dh_add_t, dh_alt_t, dh_bs_t, t_label in [
        (ax_early, dh_add_early, dh_alt_early, dh_bs_early, T_EARLY),
        (ax_late, dh_add_late, dh_alt_late, dh_bs_late, T_LATE),
    ]:
        ax.set_facecolor('white')
        ax.bar(digits + offsets[0], dh_add_t, bar_w, color=C_ADD,
               alpha=0.8, zorder=2)
        ax.bar(digits + offsets[1], dh_alt_t, bar_w, color=C_ALT,
               alpha=0.8, zorder=2)
        ax.bar(digits + offsets[2], dh_bs_t, bar_w, color=C_BS,
               alpha=0.8, zorder=2)
        ax.scatter(digits, BENFORD, marker='_', color='black', s=50,
                   linewidths=1.5, zorder=5)

        ax.set_xlim(0.3, 9.7)
        ax.set_ylim(0, 0.42)
        ax.set_xlabel('leading digit', fontsize=8)
        ax.set_xticks(digits)
        ax.tick_params(labelsize=7)
        ax.grid(True, which='major', axis='y', color='#dddddd',
                linewidth=0.3, zorder=0)
        ax.set_title(f't = {t_label}', fontsize=9, fontweight='bold', pad=4)

    # Only left bar panel gets y-label
    ax_early.set_ylabel('digit proportion', fontsize=8)
    ax_late.set_yticklabels([])

    fig.tight_layout(w_pad=0.8)

    out = os.path.join(HERE, 'fig_hybrid3.png')
    fig.savefig(out, dpi=300, bbox_inches='tight', facecolor='white')
    print(f'Saved: {out}')
    plt.close(fig)


if __name__ == '__main__':
    main()
