"""
Figure 1 candidate: L1 distance to Benford for four regimes.

One panel, four curves:
  - addition only (±1)
  - multiplication only (×2/÷2)
  - alternating add/mult (10 adds, then 1 mul, repeat)
  - mixed arithmetic BS(1,2) (±1, ×2/÷2 each with prob 1/4)

Run: sage -python fig_l1_curves.py
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

# --- Benford reference: uniform on [0,1) in log-mantissa coords ---
UNIFORM_DENSITY = 1.0 / LOG_MANTISSA_BINS


def l1_from_hist(hist):
    """L1 distance from histogram (already normalized) to uniform."""
    uniform = np.full_like(hist, 1.0 / hist.shape[-1])
    return np.sum(np.abs(hist - uniform), axis=-1)


def run_walk(step_fn, n_walkers=20_000, n_steps=2000, n_checkpoints=400,
             seed=None, initial=None):
    """Generic walker: returns (steps, l1) arrays."""
    rng = np.random.default_rng(seed)
    if initial is None:
        initial = math.sqrt(2.0)
    x = np.full(n_walkers, initial, dtype=np.float64)

    ckpt_interval = max(1, n_steps // n_checkpoints)
    steps_out = []
    l1_out = []

    def record(t):
        m = log_mantissa(x, 10.0)
        hist, _ = np.histogram(m, bins=LOG_MANTISSA_BINS, range=(0.0, 1.0))
        h = hist.astype(np.float64) / hist.sum()
        steps_out.append(t)
        l1_out.append(l1_from_hist(h))

    record(0)
    for t in range(1, n_steps + 1):
        step_fn(rng, x)
        if t % ckpt_interval == 0 or t == n_steps:
            record(t)

    return np.array(steps_out), np.array(l1_out)


# --- Step functions (mutate x in place) ---

def step_add(rng, x):
    choice = rng.integers(0, 2, size=x.size)
    x[choice == 0] += 1.0
    x[choice == 1] -= 1.0


def step_mul(rng, x):
    choice = rng.integers(0, 2, size=x.size)
    x[choice == 0] *= 2.0
    x[choice == 1] *= 0.5


_alt_counter = [0]
_ALT_ADDS_PER_MUL = 10

def step_alternating(rng, x):
    """10 adds then 1 mul, repeating."""
    _alt_counter[0] += 1
    if _alt_counter[0] % (_ALT_ADDS_PER_MUL + 1) == 0:
        step_mul(rng, x)
    else:
        step_add(rng, x)


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
    s_add, l1_add = run_walk(step_add, N_WALKERS, N_STEPS, N_CKPT,
                             seed=0x1111)

    print('Running multiplication only...')
    s_mul, l1_mul = run_walk(step_mul, N_WALKERS, N_STEPS, N_CKPT,
                             seed=0x2222)

    print('Running alternating add/mult...')
    _alt_counter[0] = 0
    s_alt, l1_alt = run_walk(step_alternating, N_WALKERS, N_STEPS, N_CKPT,
                             seed=0x3333)

    print('Running BS(1,2) mixed...')
    s_bs, l1_bs = run_walk(step_bs12, N_WALKERS, N_STEPS, N_CKPT,
                           seed=0x4444)

    # --- Noise floor: finite-sample L1 for perfectly uniform draws ---
    noise_floor = math.sqrt(2.0 * LOG_MANTISSA_BINS / (math.pi * N_WALKERS))

    # --- Plot ---
    fig, ax = plt.subplots(1, 1, figsize=(4.5, 3.0))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    ax.semilogy(s_add, l1_add, color='#e41a1c', linewidth=1.3,
                label='addition only', zorder=3)
    ax.semilogy(s_mul, l1_mul, color='#ff7f00', linewidth=0.8,
                label='multiplication only', alpha=0.7, zorder=2)
    ax.semilogy(s_alt, l1_alt, color='#984ea3', linewidth=1.3,
                label='alternating add/mult', zorder=3)
    ax.semilogy(s_bs, l1_bs, color='#377eb8', linewidth=1.5,
                label='mixed (BS(1,2))', zorder=4)

    ax.axhline(noise_floor, color='#999999', linestyle=':', linewidth=0.7,
               label=f'sampling floor (N={N_WALKERS:,})', zorder=1)

    ax.set_xlim(0, 1000)
    ax.set_ylim(0.005, 2.5)
    ax.set_xlabel('operation count', fontsize=9)
    ax.set_ylabel('L1 distance to Benford', fontsize=9)
    ax.tick_params(labelsize=7.5)

    ax.grid(True, which='major', color='#dddddd', linewidth=0.3, zorder=0)
    ax.grid(True, which='minor', color='#eeeeee', linewidth=0.2, zorder=0)

    ax.legend(loc='center right', fontsize=6.5, frameon=True,
              facecolor='white', edgecolor='#cccccc', borderpad=0.4,
              labelspacing=0.3, handlelength=1.5)

    fig.tight_layout()

    out = os.path.join(HERE, 'fig_l1_curves.png')
    fig.savefig(out, dpi=300, bbox_inches='tight', facecolor='white')
    print(f'Saved: {out}')
    plt.close(fig)


if __name__ == '__main__':
    main()
