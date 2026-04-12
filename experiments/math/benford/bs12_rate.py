"""
bs12_rate.py — Dedicated high-resolution run to measure the convergence
rate of bs12_walk's L1 to uniform log-mantissa.

The standard bs12_walk run plateaus at the finite-sample noise floor
(~sqrt(2 * bins / (pi * N_walkers))) within a few hundred steps, which
hides the rate. This script runs a larger ensemble (1_000_000 walkers)
for a shorter horizon (1_000 steps) with dense checkpoints (500), so
the decay is visible across roughly a decade above the floor.
"""

import math
import numpy as np
import matplotlib.pyplot as plt

from common import (
    BG, FG, GREEN, RED, SPINE, YELLOW,
    LOG_MANTISSA_BINS,
    experiment_path, l1_to_uniform, log_mantissa,
    save_figure, setup_dark_axes,
)


N_WALKERS = 1_000_000
N_STEPS = 1_000
N_CHECKPOINTS = 500
SEED_LOCAL = 0xBADDEC


def run():
    rng = np.random.default_rng(SEED_LOCAL)
    x = np.full(N_WALKERS, math.sqrt(2.0), dtype=np.float64)

    checkpoint_steps = np.unique(
        np.linspace(0, N_STEPS, N_CHECKPOINTS + 1, dtype=np.int64)
    )
    K = checkpoint_steps.size
    l1 = np.zeros(K, dtype=np.float64)
    step_record = np.zeros(K, dtype=np.int64)

    def record(idx, step_index):
        mantissa = log_mantissa(x, 10.0)
        hist, _ = np.histogram(mantissa, bins=LOG_MANTISSA_BINS, range=(0.0, 1.0))
        hist_norm = hist.astype(np.float64) / hist.sum()
        l1[idx] = l1_to_uniform(hist_norm)
        step_record[idx] = step_index

    record(0, 0)
    ckpt_idx = 1
    op = 0
    while op < N_STEPS:
        target = int(checkpoint_steps[ckpt_idx])
        for _ in range(target - op):
            choice = rng.integers(0, 4, size=x.size)
            plus = choice == 0
            minus = choice == 1
            mul = choice == 2
            div = choice == 3
            x[plus] += 1.0
            x[minus] -= 1.0
            x[mul] *= 2.0
            x[div] *= 0.5
        op = target
        record(ckpt_idx, op)
        ckpt_idx += 1

    return step_record, l1


def main():
    step, l1 = run()

    noise_floor = math.sqrt(2.0 * LOG_MANTISSA_BINS / (math.pi * N_WALKERS))
    print(f'noise floor (N={N_WALKERS:_}, B={LOG_MANTISSA_BINS}): {noise_floor:.5f}')

    # The curve is exponential, not power-law: fit log(L1) vs t.
    # Canonical window: skip the first 20 steps (delta-fanout transient)
    # and cap at step 100 to stay well above the noise floor. Single-mode
    # exponential R^2 is ~0.99 on this window; lambda shifts ~10% with
    # window width, hinting at multi-mode structure that we do not try
    # to fit here.
    fit_mask = (step >= 20) & (step <= 100)
    t_fit = step[fit_mask].astype(np.float64)
    log_l1 = np.log(l1[fit_mask])
    slope, intercept = np.polyfit(t_fit, log_l1, 1)
    lam = -slope
    C = float(np.exp(intercept))
    residuals = log_l1 - (slope * t_fit + intercept)
    ss_res = float(np.sum(residuals ** 2))
    ss_tot = float(np.sum((log_l1 - log_l1.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float('nan')
    half_life = math.log(2.0) / lam if lam > 0 else float('inf')

    print(f'fit window: {int(t_fit[0])}..{int(t_fit[-1])} '
          f'({int(fit_mask.sum())} points)')
    print(f'lambda = {lam:.5f}   (exponential decay rate, per step)')
    print(f'C      = {C:.4f}')
    print(f'R^2    = {r2:.4f}')
    print(f'half-life = {half_life:.2f} steps')

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(BG)

    ax1 = axes[0]
    setup_dark_axes(ax1)
    nonzero = l1 > 0
    ax1.loglog(step[nonzero], l1[nonzero], color=YELLOW, linewidth=1.8,
               label=f'empirical L1  (N={N_WALKERS:_})')
    ref_t0 = t_fit[0]
    ref_l0 = l1[fit_mask][0]
    ax1.loglog(step[step > 0], ref_l0 * (step[step > 0] / ref_t0) ** -0.5,
               color=GREEN, linestyle=':', linewidth=1.3,
               label='slope -1/2 reference (power law)')
    ax1.axhline(noise_floor, color='#666', linestyle='-', linewidth=0.9,
                label=f'noise floor  {noise_floor:.3f}')
    ax1.set_xlabel('step')
    ax1.set_ylabel('L1 to uniform log-mantissa')
    ax1.set_title('log-log:  curve bends away from any power law',
                  color=FG, fontsize=11)
    ax1.grid(which='both', color='#222', linewidth=0.6, alpha=0.6)
    leg1 = ax1.legend(loc='lower left', facecolor='#111', edgecolor=SPINE)
    for t in leg1.get_texts():
        t.set_color(FG)

    ax2 = axes[1]
    setup_dark_axes(ax2)
    ax2.semilogy(step[nonzero], l1[nonzero], color=YELLOW, linewidth=1.8,
                 label=f'empirical L1')
    grid = np.linspace(t_fit[0], t_fit[-1], 200)
    ax2.semilogy(grid, C * np.exp(-lam * grid), color=RED, linestyle='--',
                 linewidth=1.8,
                 label=f'fit  L1 ~ {C:.2g} exp(-{lam:.4f} t)')
    ax2.axhline(noise_floor, color='#666', linestyle='-', linewidth=0.9,
                label=f'noise floor  {noise_floor:.3f}')
    ax2.set_xlabel('step')
    ax2.set_ylabel('L1 to uniform log-mantissa')
    ax2.set_title('lin-log:  straight line = exponential decay',
                  color=FG, fontsize=11)
    ax2.set_xlim(0, step[-1])
    ax2.grid(which='both', color='#222', linewidth=0.6, alpha=0.6)
    leg2 = ax2.legend(loc='upper right', facecolor='#111', edgecolor=SPINE)
    for t in leg2.get_texts():
        t.set_color(FG)

    ax2.text(
        0.02, 0.04,
        f'lambda = {lam:.4f} / step\n'
        f'half-life = {half_life:.1f} steps\n'
        f'R^2 = {r2:.3f}   (fit: {int(t_fit[0])}..{int(t_fit[-1])})',
        color=FG, fontsize=10, va='bottom', ha='left',
        transform=ax2.transAxes,
        bbox=dict(facecolor='#111', edgecolor=SPINE, alpha=0.85),
    )

    fig.suptitle('BS(1,2) walk: exponential convergence to Benford',
                 color=FG, fontsize=13)
    plt.tight_layout()
    save_figure(fig, experiment_path('bs12_rate.png'))


if __name__ == '__main__':
    main()
