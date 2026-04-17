"""
tracers_v2.py — Three-panel BS(1,2) tracer view.

Left:   log10|x| vs step  (scale diffusion, null-recurrent √t envelope,
                           active zone R marked)
Center: mantissa vs step  (mantissa equidistribution, density underlay)
Right:  complexity vs step (group element complexity, √t growth)

The three panels are three views of the same √t:
  - Left's √t dispersion of log₁₀|x| gives the local time N_n ~ √n at R.
  - Right's √t complexity growth is the null-recurrent walk's sublinear
    speed on the Cayley graph.
  - Both feed the FIRST-PROOF §2 (R5) return-count estimate that turns
    per-return contraction into the stretched-exp law-level rate.

Each walker gets a consistent color across all three panels. Ensemble
mean ± sigma in white. 32 walkers shown for visual clarity; all 64 feed
the density underlay on the mantissa panel.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from common import (
    BG, FG, SPINE, GREEN, YELLOW,
    BENFORD_BOUNDARIES_BASE10,
    experiment_path, save_figure, setup_dark_axes,
)


N_SHOW = 32
ALPHA = 0.4
LW = 0.7
E0 = 2  # active zone R = {|log₁₀|x|| ≤ E0}; matches FIRST-PROOF §2 test case.


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

    # --- Left: log10|x| with √t envelope and active zone R ---
    for i, w in enumerate(pick):
        ax1.plot(log10_abs_x[w], steps, color=colors[i],
                 linewidth=LW, alpha=ALPHA)
    mean_log = log10_abs_x.mean(axis=0)
    std_log = log10_abs_x.std(axis=0)
    ax1.plot(mean_log, steps, color=FG, linewidth=1.4)
    ax1.fill_betweenx(steps, mean_log - std_log, mean_log + std_log,
                      color=FG, alpha=0.12)

    # √t envelope: fit scale to match final empirical σ.
    t_last = float(steps[-1])
    sigma_last = float(std_log[-1])
    t_safe = np.maximum(steps.astype(np.float64), 1.0)
    sqrt_env = sigma_last * np.sqrt(t_safe / t_last)
    ax1.plot(mean_log + sqrt_env, steps, color=GREEN, linestyle='--',
             linewidth=1.1, alpha=0.8, label='±σ·√(t / t_max)')
    ax1.plot(mean_log - sqrt_env, steps, color=GREEN, linestyle='--',
             linewidth=1.1, alpha=0.8)

    # Active zone R = {|log₁₀|x|| ≤ E0} — the set where T_R contracts.
    # Use a translucent band with bright edges so it reads under the tracers.
    ax1.axvspan(-E0, E0, color='#00d4a8', alpha=0.10, zorder=0)
    ax1.axvline(E0, color='#00d4a8', linestyle='-', linewidth=1.4, alpha=0.9, zorder=3)
    ax1.axvline(-E0, color='#00d4a8', linestyle='-', linewidth=1.4, alpha=0.9, zorder=3)
    ax1.text(0, steps[0] + (steps[-1] - steps[0]) * 0.02,
             f'active zone R : |log₁₀|x|| ≤ {E0}',
             color='#00d4a8', fontsize=9, ha='center', va='top',
             alpha=1.0, zorder=5,
             bbox=dict(facecolor=BG, edgecolor='none', alpha=0.7, pad=2))

    # Return-event markers: dots at checkpoints where walker transitions
    # from outside R to inside R. Checkpoint granularity (every 100 steps),
    # so these undercount true returns but give a visual density of
    # R-returns along each trajectory.
    for i, w in enumerate(pick):
        trace = log10_abs_x[w]
        in_R = np.abs(trace) <= E0
        # indices where we enter R from outside
        entries = np.where(~in_R[:-1] & in_R[1:])[0] + 1
        if len(entries) > 0:
            ax1.scatter(trace[entries], steps[entries],
                        color=colors[i], s=10, alpha=0.85,
                        marker='o', zorder=4,
                        edgecolors='white', linewidths=0.3)

    ax1.set_xlabel('log₁₀ |x|', color=FG, fontsize=11)
    ax1.set_ylabel('step', color=FG, fontsize=11)
    ax1.set_title('scale diffusion  (±√t envelope, R-returns dotted)',
                  color=FG, fontsize=11)
    ax1.grid(color='#222', linewidth=0.5, alpha=0.5)
    ax1.invert_yaxis()
    leg1 = ax1.legend(loc='lower left', facecolor='#111', edgecolor=SPINE,
                      fontsize=8)
    for t in leg1.get_texts():
        t.set_color(FG)

    # --- Center: mantissa with density underlay ---
    # 2D histogram of (m, step) across ALL walkers as a dim background.
    n_m_bins = 50
    n_t_bins = min(n_ckpts, 100)
    all_m = mantissa.flatten()
    all_t = np.tile(steps, n_walkers)
    H, mb, tb = np.histogram2d(all_m, all_t,
                               bins=[n_m_bins, n_t_bins],
                               range=[[0.0, 1.0], [0.0, t_last]])
    # Normalize each time-column to a density (emphasize shape, not count).
    col_sums = H.sum(axis=0, keepdims=True)
    col_sums[col_sums == 0] = 1.0
    H_density = H / col_sums
    # Tone the density underlay toward a cool, unobtrusive colormap
    # so the tracer lines and digit-boundary grid stay legible over it.
    ax2.imshow(H_density.T,
               extent=(0.0, 1.0, t_last, 0.0),
               aspect='auto', cmap='bone', alpha=0.55,
               interpolation='bilinear', zorder=0)

    for i, w in enumerate(pick):
        ax2.plot(mantissa[w], steps, color=colors[i],
                 linewidth=LW, alpha=ALPHA, rasterized=True, zorder=2)

    # Benford digit boundaries as vertical reference lines
    for d in range(1, 10):
        if d < len(BENFORD_BOUNDARIES_BASE10):
            bnd = float(BENFORD_BOUNDARIES_BASE10[d])
            ax2.axvline(bnd, color='#444', linewidth=0.5, alpha=0.6, zorder=1)
    # digit labels
    for d in range(1, 10):
        lo = float(BENFORD_BOUNDARIES_BASE10[d - 1]) if d >= 1 else 0.0
        hi = float(BENFORD_BOUNDARIES_BASE10[d]) if d < 9 else 1.0
        mid = (lo + hi) / 2
        ax2.text(mid, steps[-1] * 1.02, str(d), color='#666',
                 fontsize=8, ha='center', va='top')
    ax2.set_xlim(0, 1)
    ax2.set_xlabel('log₁₀ mantissa  (mod 1)', color=FG, fontsize=11)
    ax2.set_title('mantissa equidistribution  (density underlay, all walkers)',
                  color=FG, fontsize=11)
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

    fig.suptitle('BS(1,2) walk: scale √t → returns → complexity √t '
                 '(three views of the null-recurrent shape, 32 tracers, 20 000 steps)',
                 color=FG, fontsize=12, y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    save_figure(fig, experiment_path('tracers_v2.png'))


if __name__ == '__main__':
    main()
