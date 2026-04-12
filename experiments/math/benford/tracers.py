"""
tracers.py — Two-panel view of the bs12 exact-state tracer data.

Left:  log10|x| trajectories for all tracer walkers, ensemble mean +/- sigma.
Right: exact-state group element complexity (bits) with sqrt(t) and linear
       references, demonstrating the sqrt-like growth.
"""

import numpy as np
import matplotlib.pyplot as plt

from common import (
    BG, BLUE, FG, GREEN, RED, SPINE, YELLOW,
    experiment_path, save_figure, setup_dark_axes,
)


def main():
    with np.load(experiment_path('data_bs12_tracer.npz')) as data:
        log10_abs_x = data['log10_abs_x']
        complexity = data['complexity'].astype(np.float64)
        steps = data['steps']

    n_walkers, _ = log10_abs_x.shape

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.5))
    fig.patch.set_facecolor(BG)

    setup_dark_axes(ax1)
    for w in range(n_walkers):
        ax1.plot(steps, log10_abs_x[w], color=YELLOW, alpha=0.22, linewidth=0.7)
    mean_log = log10_abs_x.mean(axis=0)
    std_log = log10_abs_x.std(axis=0)
    ax1.plot(steps, mean_log, color=FG, linewidth=1.6, label='ensemble mean')
    ax1.fill_between(steps, mean_log - std_log, mean_log + std_log,
                     color=FG, alpha=0.18, label='+/- 1 sigma')
    ax1.set_xlabel('step')
    ax1.set_ylabel('log10 |x|')
    ax1.set_title(f'BS(1,2) tracer trajectories  ({n_walkers} walkers)',
                  color=FG, fontsize=12)
    ax1.grid(color='#222', linewidth=0.6, alpha=0.6)
    leg1 = ax1.legend(loc='upper left', facecolor='#111', edgecolor=SPINE)
    for t in leg1.get_texts():
        t.set_color(FG)

    setup_dark_axes(ax2)
    for w in range(n_walkers):
        ax2.plot(steps, complexity[w], color=BLUE, alpha=0.22, linewidth=0.7)
    mean_c = complexity.mean(axis=0)
    std_c = complexity.std(axis=0)
    ax2.plot(steps, mean_c, color=FG, linewidth=1.6, label='ensemble mean')
    ax2.fill_between(steps, mean_c - std_c, mean_c + std_c,
                     color=FG, alpha=0.18, label='+/- 1 sigma')

    # sqrt(t) reference, normalized to pass through (steps[-1], mean_c[-1])
    t_valid = steps > 0
    t_last = float(steps[-1])
    c_last = float(mean_c[-1])
    sqrt_ref = c_last * np.sqrt(steps[t_valid] / t_last)
    linear_ref = c_last * (steps[t_valid] / t_last)
    ax2.plot(steps[t_valid], sqrt_ref, color=GREEN, linestyle='--',
             linewidth=1.3, label='sqrt(t) reference')
    ax2.plot(steps[t_valid], linear_ref, color=RED, linestyle=':',
             linewidth=1.3, label='linear t reference')

    ax2.set_xlabel('step')
    ax2.set_ylabel('group element complexity  (bits)')
    ax2.set_title('BS(1,2) exact-state complexity',
                  color=FG, fontsize=12)
    ax2.grid(color='#222', linewidth=0.6, alpha=0.6)
    leg2 = ax2.legend(loc='upper left', facecolor='#111', edgecolor=SPINE)
    for t in leg2.get_texts():
        t.set_color(FG)

    # log-log fit on complexity vs steps to estimate the growth exponent
    mask = steps >= 100
    log_t = np.log(steps[mask].astype(np.float64))
    log_c = np.log(mean_c[mask])
    slope, intercept = np.polyfit(log_t, log_c, 1)
    print(f'complexity ~ t^{slope:.3f}   (linear would be 1.0, sqrt would be 0.5)')
    ax2.text(
        0.98, 0.04,
        f'mean complexity ~ t^{slope:.3f}',
        color=FG, fontsize=10, va='bottom', ha='right',
        transform=ax2.transAxes,
        bbox=dict(facecolor='#111', edgecolor=SPINE, alpha=0.85),
    )

    plt.tight_layout()
    save_figure(fig, experiment_path('tracers.png'))


if __name__ == '__main__':
    main()
