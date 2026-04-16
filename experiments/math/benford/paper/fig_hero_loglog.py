"""
Hero figure (log-log): L1 distance to Benford for three regimes.

Log-log axes make the rate distinction visible as shape:
  - addition only: flat (no convergence)
  - alternating add/mult: straight line (algebraic decay)
  - mixed BS(1,2): concave down (exponential convergence)

Run: sage -python fig_hero_loglog.py
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

from common import LOG_MANTISSA_BINS, log_mantissa

C_ADD = '#e41a1c'   # red
C_ALT = '#984ea3'   # purple
C_BS  = '#377eb8'   # blue


def l1_from_hist(hist):
    uniform = np.full_like(hist, 1.0 / hist.shape[-1])
    return np.sum(np.abs(hist - uniform), axis=-1)


def run_walk(step_fn, n_walkers, n_steps, seed):
    rng = np.random.default_rng(seed)
    x = np.full(n_walkers, math.sqrt(2.0), dtype=np.float64)

    steps_out = []
    l1_out = []

    # Skip t=0 (log(0) undefined); record every step up to 30,
    # then every 2 steps for smoothness
    for t in range(1, n_steps + 1):
        step_fn(rng, x)
        if t <= 30 or t % 2 == 0 or t == n_steps:
            m = log_mantissa(x, 10.0)
            hist, _ = np.histogram(m, bins=LOG_MANTISSA_BINS,
                                   range=(0.0, 1.0))
            h = hist.astype(np.float64) / hist.sum()
            steps_out.append(t)
            l1_out.append(l1_from_hist(h))

    return np.array(steps_out), np.array(l1_out)


def step_add(rng, x):
    choice = rng.integers(0, 2, size=x.size)
    x[choice == 0] += 1.0
    x[choice == 1] -= 1.0


_alt_counter = [0]

def step_alternating(rng, x):
    _alt_counter[0] += 1
    if _alt_counter[0] % 11 == 0:
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

    print('Running addition only...')
    s_add, l1_add = run_walk(step_add, N_WALKERS, N_STEPS, seed=0x1111)

    print('Running alternating add/mult...')
    _alt_counter[0] = 0
    s_alt, l1_alt = run_walk(step_alternating, N_WALKERS, N_STEPS,
                              seed=0x3333)

    print('Running BS(1,2) mixed...')
    s_bs, l1_bs = run_walk(step_bs12, N_WALKERS, N_STEPS, seed=0x4444)

    noise_floor = math.sqrt(2.0 * LOG_MANTISSA_BINS / (math.pi * N_WALKERS))

    # --- Figure ---
    fig, ax = plt.subplots(1, 1, figsize=(5.0, 3.2))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Curves — BS(1,2) heaviest, it's the protagonist
    ax.loglog(s_add, l1_add, color=C_ADD, linewidth=1.4, zorder=3)
    ax.loglog(s_alt, l1_alt, color=C_ALT, linewidth=1.4, zorder=3)
    ax.loglog(s_bs, l1_bs, color=C_BS, linewidth=1.8, zorder=4)

    # Noise floor
    ax.axhline(noise_floor, color='#999999', linestyle=':', linewidth=0.8,
               zorder=1)
    ax.text(1.2, noise_floor * 0.70, 'finite-sample L$_1$ floor',
            fontsize=7, color='#888888', ha='left', va='top')

    # Direct curve labels
    # Addition: below the red line, right side where it's flat
    ax.text(395, 1.0, 'addition\nonly',
            fontsize=9, color=C_ADD, va='top', ha='left',
            fontweight='medium', linespacing=0.85)

    # Alternating: line break between "alternating" and "add/mult"
    alt_y = l1_alt[np.argmin(np.abs(s_alt - 100))]
    ax.text(90, alt_y * 1.4, 'alternating\nadd/mult',
            fontsize=9, color=C_ALT, va='bottom', ha='left',
            fontweight='medium', linespacing=0.85)

    # BS(1,2): label ends to the left of the blue line
    bs_y = l1_bs[np.argmin(np.abs(s_bs - 30))]
    ax.text(28, bs_y * 0.40, 'mixed (BS(1,2))',
            fontsize=9, color=C_BS, va='top', ha='right',
            fontweight='medium')

    ax.set_xlim(1, 1000)
    ax.set_ylim(0.02, 2.8)
    ax.set_xlabel('operation count', fontsize=10)
    ax.set_ylabel('L$_1$ distance to Benford', fontsize=10)
    ax.set_title('Convergence to Benford requires mixing',
                 fontsize=10, fontweight='bold', pad=6)
    ax.tick_params(labelsize=8)

    ax.grid(True, which='major', color='#dddddd', linewidth=0.3, zorder=0)
    ax.grid(True, which='minor', color='#eeeeee', linewidth=0.2, zorder=0)

    fig.tight_layout()

    out = os.path.join(HERE, 'fig_hero_loglog.png')
    fig.savefig(out, dpi=300, bbox_inches='tight', facecolor='white')
    print(f'Saved: {out}')
    plt.close(fig)


if __name__ == '__main__':
    main()
