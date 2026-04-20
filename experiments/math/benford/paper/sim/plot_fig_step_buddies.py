"""
Plot the SUBSET-STEP-BUDDIES 2x2 small-multiples figure.

Produces `paper/fig/fig_step_buddies.png`.

Run: sage -python plot_fig_step_buddies.py
"""

import glob
import math
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.abspath(os.path.join(SIM_DIR, '..', 'fig'))
os.makedirs(FIG_DIR, exist_ok=True)

BUDDIES_DIR = os.path.join(SIM_DIR, 'comparison_walks_results', 'step_buddies')
THETA_N_1E8 = 2.717e-3


def theta_N(N):
    return THETA_N_1E8 * math.sqrt(1e8 / N)


def load_traces(walk, N):
    log_N = int(round(math.log10(N)))
    pattern = os.path.join(BUDDIES_DIR, f'{walk}_N1e{log_N}_s*.npz')
    files = sorted(glob.glob(pattern))
    traces = []
    times = None
    for f in files:
        d = np.load(f, allow_pickle=True)
        if times is None:
            times = d['sample_times']
        traces.append(d['l1'])
    return times, traces


N_VALUES = [10**4, 10**5, 10**6, 10**7]

fig, axes = plt.subplots(2, 2, figsize=(9.5, 7.5), sharex=True, sharey=True)

panel_positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
for i, N in enumerate(N_VALUES):
    ax = axes[panel_positions[i]]
    times_r, traces_r = load_traces('bs12', N)
    times_p, traces_p = load_traces('alt', N)

    # Red (BS(1,2)): solid, thin if 3 seeds else medium.
    lw_r = 1.1 if len(traces_r) > 1 else 1.8
    for tr in traces_r:
        ax.loglog(times_r, tr, color='#c0392b', linestyle='-',
                  linewidth=lw_r, alpha=0.85, zorder=3)

    # Purple (alternating): dash-dot.
    lw_p = 1.1 if len(traces_p) > 1 else 1.8
    for tr in traces_p:
        ax.loglog(times_p, tr, color='#8e44ad', linestyle='-.',
                  linewidth=lw_p, alpha=0.85, zorder=3)

    # Panel floor line.
    floor = theta_N(N)
    ax.axhline(floor, color='#999', linestyle='-', linewidth=0.8,
               alpha=0.6, zorder=1)

    # N label in upper-right corner.
    log_N = int(round(math.log10(N)))
    ax.text(0.97, 0.95, f'$N = 10^{log_N}$', transform=ax.transAxes,
            ha='right', va='top', fontsize=13, color='#333')

    ax.set_xlim(0.9, 500)
    ax.set_ylim(1e-3, 3.0)
    ax.grid(True, which='major', alpha=0.2, linewidth=0.5)
    ax.grid(True, which='minor', alpha=0.08, linewidth=0.3)

# Shared axis labels.
fig.supxlabel('step $n$', fontsize=12)
fig.supylabel(r'$L_1(P_n,\ \mathrm{Leb}_T)$', fontsize=12)

plt.tight_layout()
out_path = os.path.join(FIG_DIR, 'fig_step_buddies.png')
plt.savefig(out_path, dpi=160, bbox_inches='tight')
plt.close()
print(f'-> {out_path}')
