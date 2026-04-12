"""
tracers_v2.py — Three-panel BS(1,2) tracer view.

Left:   log10|x| vs step  (scale diffusion)
Center: mantissa vs step  (spectral gap, the direct view of convergence)
Right:  complexity vs step (algebraic state, √t growth)

Each walker gets a consistent color across all three panels. Ensemble
mean ± sigma in white. 32 walkers for visual clarity.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from common import (
    BG, FG, SPINE, GREEN,
    BENFORD_BOUNDARIES_BASE10,
    experiment_path, save_figure, setup_dark_axes,
)


N_SHOW = 32
ALPHA = 0.4
LW = 0.7


def main():
    with np.load(experiment_path('data_bs12_tracer.npz')) as data:
        log10_abs_x = data['log10_abs_x']
        complexity = data['complexity'].astype(np.float64)
        steps = data['steps']

    n_walkers, n_ckpts = log10_abs_x.shape
    mantissa = np.mod(log10_abs_x, 1.0)

    # pick N_SHOW walkers with diverse final log10|x| (spread of outcomes)
    final_log = log10_abs_x[:, -1]
    order = np.argsort(final_log)
    pick = order[np.linspace(0, n_walkers - 1, N_SHOW, dtype=int)]

    colors = plt.cm.twilight_shifted(np.linspace(0.1, 0.9, N_SHOW))

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 7.5),
                                         sharey=True)
    fig.patch.set_facecolor(BG)

    for ax in (ax1, ax2, ax3):
        setup_dark_axes(ax)

    # --- Left: log10|x| ---
    for i, w in enumerate(pick):
        ax1.plot(log10_abs_x[w], steps, color=colors[i],
                 linewidth=LW, alpha=ALPHA)
    mean_log = log10_abs_x.mean(axis=0)
    std_log = log10_abs_x.std(axis=0)
    ax1.plot(mean_log, steps, color=FG, linewidth=1.4)
    ax1.fill_betweenx(steps, mean_log - std_log, mean_log + std_log,
                      color=FG, alpha=0.12)
    ax1.set_xlabel('log₁₀ |x|', color=FG, fontsize=11)
    ax1.set_ylabel('step', color=FG, fontsize=11)
    ax1.set_title('scale diffusion', color=FG, fontsize=12)
    ax1.grid(color='#222', linewidth=0.5, alpha=0.5)
    ax1.invert_yaxis()

    # --- Center: mantissa ---
    for i, w in enumerate(pick):
        ax2.plot(mantissa[w], steps, color=colors[i],
                 linewidth=LW, alpha=ALPHA, rasterized=True)
    # Benford digit boundaries as vertical reference lines
    for d in range(1, 10):
        bnd = float(BENFORD_BOUNDARIES_BASE10[d]) if d < 10 else 1.0
        if d < len(BENFORD_BOUNDARIES_BASE10):
            ax2.axvline(bnd, color='#333', linewidth=0.5, alpha=0.6)
    # digit labels
    for d in range(1, 10):
        lo = float(BENFORD_BOUNDARIES_BASE10[d - 1]) if d >= 1 else 0.0
        hi = float(BENFORD_BOUNDARIES_BASE10[d]) if d < 9 else 1.0
        mid = (lo + hi) / 2
        ax2.text(mid, steps[-1] * 1.02, str(d), color='#666',
                 fontsize=8, ha='center', va='top')
    ax2.set_xlim(0, 1)
    ax2.set_xlabel('log₁₀ mantissa  (mod 1)', color=FG, fontsize=11)
    ax2.set_title('mantissa convergence', color=FG, fontsize=12)
    ax2.grid(color='#222', linewidth=0.5, alpha=0.5)

    # --- Right: complexity ---
    for i, w in enumerate(pick):
        ax3.plot(complexity[w], steps, color=colors[i],
                 linewidth=LW, alpha=ALPHA)
    mean_c = complexity.mean(axis=0)
    std_c = complexity.std(axis=0)
    ax3.plot(mean_c, steps, color=FG, linewidth=1.4)
    ax3.fill_betweenx(steps, mean_c - std_c, mean_c + std_c,
                      color=FG, alpha=0.12)
    # sqrt(t) reference
    t_valid = steps > 0
    t_last = float(steps[-1])
    c_last = float(mean_c[-1])
    sqrt_ref = c_last * np.sqrt(steps[t_valid] / t_last)
    ax3.plot(sqrt_ref, steps[t_valid], color=GREEN, linestyle='--',
             linewidth=1.2, alpha=0.7, label='√t')
    ax3.set_xlabel('complexity  (bits)', color=FG, fontsize=11)
    ax3.set_title('group element complexity', color=FG, fontsize=12)
    ax3.grid(color='#222', linewidth=0.5, alpha=0.5)
    leg = ax3.legend(loc='lower right', facecolor='#111', edgecolor=SPINE)
    for t in leg.get_texts():
        t.set_color(FG)

    fig.suptitle('BS(1,2) walk: 32 exact-state tracers, 20 000 steps',
                 color=FG, fontsize=14, y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    save_figure(fig, experiment_path('tracers_v2.png'))


if __name__ == '__main__':
    main()
