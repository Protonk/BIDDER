"""
gap3_phase1.py — Phase 1 of FIRST-PROOF gap 3 simulation plan.

Discriminate exp(-lambda*t) from exp(-c*sqrt(t)) as the asymptotic
shape of L1-to-Benford decay for the symmetric BS(1,2) walk.

Design:
  N = 1e7 walkers (floor ~= 0.004 on 256-bin log-mantissa L1)
  t up to 600, fine log-grid concentrated in [20, 300]
  Fit log(L1) = a - lambda*t   vs   log(L1) = b - c*sqrt(t)
  Compare R^2 and residual structure on the pre-floor portion.

Output:
  paper/sim/data/gap3_phase1.npz   (t, L1)
  paper/sim/data/gap3_phase1.csv   (same, CSV)
  paper/sim/fig/gap3_diagnostic.png  (two-panel: log vs t, log vs sqrt(t))
  paper/sim/fig/gap3_residuals.png   (residuals of both fits)

Also prints the pre-sim check:  R^2 of exp vs stretched fit on [20, 100]
(the window the existing bs12_rate.py used).
"""

import math
import os
import numpy as np
import matplotlib.pyplot as plt

from common import (
    BG, FG, GREEN, RED, SPINE, YELLOW, BLUE,
    LOG_MANTISSA_BINS,
    experiment_path, l1_to_uniform, log_mantissa,
    save_figure, setup_dark_axes,
)


N_WALKERS = 10_000_000
N_STEPS = 600
SEED_LOCAL = 0xDECADE

CHECKPOINTS = np.array([
    0, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100,
    120, 140, 160, 180, 200, 220, 240, 260, 280, 300,
    340, 380, 420, 460, 500, 540, 600,
], dtype=np.int64)

SIM_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'paper', 'sim'
)
DATA_NPZ = os.path.join(SIM_DIR, 'data', 'gap3_phase1.npz')
DATA_CSV = os.path.join(SIM_DIR, 'data', 'gap3_phase1.csv')
FIG_DIAG = os.path.join(SIM_DIR, 'fig', 'gap3_diagnostic.png')
FIG_RESID = os.path.join(SIM_DIR, 'fig', 'gap3_residuals.png')


def run():
    rng = np.random.default_rng(SEED_LOCAL)
    x = np.full(N_WALKERS, math.sqrt(2.0), dtype=np.float64)

    K = CHECKPOINTS.size
    l1 = np.zeros(K, dtype=np.float64)

    def record(idx):
        abs_x = np.abs(x)
        # Guard against exact zeros produced by b-step at x = 1 or x = -1.
        safe = abs_x > 0.0
        mantissa = np.mod(np.log10(abs_x[safe]), 1.0)
        hist, _ = np.histogram(mantissa, bins=LOG_MANTISSA_BINS, range=(0.0, 1.0))
        hist_norm = hist.astype(np.float64) / hist.sum()
        l1[idx] = l1_to_uniform(hist_norm)
        print(f'  t={CHECKPOINTS[idx]:4d}  L1={l1[idx]:.6f}  '
              f'(walkers used: {int(safe.sum()):_}/{N_WALKERS:_})')

    print(f'BS(1,2) symmetric walk: N={N_WALKERS:_}, steps={N_STEPS}')
    print(f'checkpoints: {CHECKPOINTS.tolist()}')
    record(0)
    cursor = 0
    for idx in range(1, K):
        target = int(CHECKPOINTS[idx])
        for _ in range(target - cursor):
            choice = rng.integers(0, 4, size=x.size)
            x[choice == 0] += 1.0
            x[choice == 1] -= 1.0
            x[choice == 2] *= 2.0
            x[choice == 3] *= 0.5
        cursor = target
        record(idx)

    return CHECKPOINTS.copy(), l1


def fit_exp(t, log_l1):
    """Fit log(L1) = a - lambda*t.  Return (lam, a, r2, residuals)."""
    slope, intercept = np.polyfit(t, log_l1, 1)
    pred = slope * t + intercept
    resid = log_l1 - pred
    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((log_l1 - log_l1.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float('nan')
    return -slope, intercept, r2, resid


def fit_stretched(t, log_l1):
    """Fit log(L1) = b - c*sqrt(t).  Return (c, b, r2, residuals)."""
    sqrt_t = np.sqrt(t)
    slope, intercept = np.polyfit(sqrt_t, log_l1, 1)
    pred = slope * sqrt_t + intercept
    resid = log_l1 - pred
    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((log_l1 - log_l1.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float('nan')
    return -slope, intercept, r2, resid


def report_fits(label, t, l1, floor):
    mask = (t >= 20) & (l1 > 2 * floor)
    t_fit = t[mask].astype(np.float64)
    log_l1 = np.log(l1[mask])
    print(f'\n-- {label}  (n={mask.sum()} points, t in [{int(t_fit[0])}, {int(t_fit[-1])}]) --')
    if mask.sum() < 3:
        print('  too few points for a fit')
        return None
    lam, a_exp, r2_exp, resid_exp = fit_exp(t_fit, log_l1)
    c, b_str, r2_str, resid_str = fit_stretched(t_fit, log_l1)
    print(f'  exp:       lambda = {lam:.5f}   R^2 = {r2_exp:.5f}   '
          f'resid stddev = {resid_exp.std():.4f}')
    print(f'  stretched: c      = {c:.5f}   R^2 = {r2_str:.5f}   '
          f'resid stddev = {resid_str.std():.4f}')
    return {
        't_fit': t_fit, 'log_l1': log_l1,
        'lam': lam, 'a_exp': a_exp, 'r2_exp': r2_exp, 'resid_exp': resid_exp,
        'c': c, 'b_str': b_str, 'r2_str': r2_str, 'resid_str': resid_str,
    }


def main():
    os.makedirs(os.path.dirname(DATA_NPZ), exist_ok=True)
    os.makedirs(os.path.dirname(FIG_DIAG), exist_ok=True)

    t, l1 = run()

    floor = math.sqrt(2.0 * LOG_MANTISSA_BINS / (math.pi * N_WALKERS))
    print(f'\nnoise floor (N={N_WALKERS:_}, B={LOG_MANTISSA_BINS}): {floor:.5f}')

    np.savez_compressed(DATA_NPZ, t=t, l1=l1, floor=floor)
    with open(DATA_CSV, 'w') as f:
        f.write('t,L1\n')
        for ti, li in zip(t, l1):
            f.write(f'{int(ti)},{li:.8e}\n')
    print(f'-> {os.path.basename(DATA_NPZ)}')
    print(f'-> {os.path.basename(DATA_CSV)}')

    # Pre-sim check: fits on [20, 100] only (existing bs12_rate.py window).
    print('\n=== PRE-SIM CHECK: fits on [20, 100] ===')
    mask_pre = (t >= 20) & (t <= 100)
    pre = report_fits('[20, 100] window (pre-sim check)',
                      t[mask_pre], l1[mask_pre], floor)

    # Full phase-1 fit on all pre-floor data.
    print('\n=== PHASE 1: fits on full pre-floor window ===')
    full = report_fits('pre-floor (L1 > 2*floor, t >= 20)',
                       t, l1, floor)

    # Diagnostic plot.
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(BG)

    ax1 = axes[0]
    setup_dark_axes(ax1)
    nonzero = l1 > 0
    ax1.semilogy(t[nonzero], l1[nonzero], 'o-', color=YELLOW, linewidth=1.6,
                 markersize=4, label=f'empirical L1 (N={N_WALKERS:_})')
    if full is not None:
        grid = np.linspace(full['t_fit'][0], full['t_fit'][-1], 200)
        ax1.semilogy(grid, np.exp(full['a_exp'] - full['lam'] * grid),
                     '--', color=RED, linewidth=1.6,
                     label=f"exp fit: lambda={full['lam']:.4f}  R2={full['r2_exp']:.4f}")
        ax1.semilogy(grid, np.exp(full['b_str'] - full['c'] * np.sqrt(grid)),
                     ':', color=BLUE, linewidth=1.6,
                     label=f"stretched fit: c={full['c']:.3f}  R2={full['r2_str']:.4f}")
    ax1.axhline(floor, color='#666', linestyle='-', linewidth=0.9,
                label=f'noise floor {floor:.4f}')
    ax1.set_xlabel('step t')
    ax1.set_ylabel('L1 to uniform log-mantissa')
    ax1.set_title('log(L1) vs. t  (straight = exponential)',
                  color=FG, fontsize=11)
    ax1.grid(which='both', color='#222', linewidth=0.6, alpha=0.6)
    leg1 = ax1.legend(loc='lower left', facecolor='#111', edgecolor=SPINE,
                      fontsize=9)
    for txt in leg1.get_texts():
        txt.set_color(FG)

    ax2 = axes[1]
    setup_dark_axes(ax2)
    sqrt_t = np.sqrt(t.astype(np.float64))
    ax2.semilogy(sqrt_t[nonzero], l1[nonzero], 'o-', color=YELLOW,
                 linewidth=1.6, markersize=4, label=f'empirical L1')
    if full is not None:
        grid_sqrt = np.linspace(np.sqrt(full['t_fit'][0]),
                                np.sqrt(full['t_fit'][-1]), 200)
        ax2.semilogy(grid_sqrt, np.exp(full['b_str'] - full['c'] * grid_sqrt),
                     ':', color=BLUE, linewidth=1.6,
                     label=f"stretched fit: c={full['c']:.3f}  R2={full['r2_str']:.4f}")
        ax2.semilogy(grid_sqrt,
                     np.exp(full['a_exp'] - full['lam'] * grid_sqrt ** 2),
                     '--', color=RED, linewidth=1.6,
                     label=f"exp fit: lambda={full['lam']:.4f}  R2={full['r2_exp']:.4f}")
    ax2.axhline(floor, color='#666', linestyle='-', linewidth=0.9,
                label=f'noise floor {floor:.4f}')
    ax2.set_xlabel('sqrt(t)')
    ax2.set_ylabel('L1 to uniform log-mantissa')
    ax2.set_title('log(L1) vs. sqrt(t)  (straight = stretched exp)',
                  color=FG, fontsize=11)
    ax2.grid(which='both', color='#222', linewidth=0.6, alpha=0.6)
    leg2 = ax2.legend(loc='lower left', facecolor='#111', edgecolor=SPINE,
                      fontsize=9)
    for txt in leg2.get_texts():
        txt.set_color(FG)

    fig.suptitle('Gap 3 phase 1: discriminating exp(-lambda*t) from exp(-c*sqrt(t))',
                 color=FG, fontsize=13)
    plt.tight_layout()
    save_figure(fig, FIG_DIAG)

    # Residual plot.
    if full is not None:
        fig2, axr = plt.subplots(1, 1, figsize=(10, 6))
        fig2.patch.set_facecolor(BG)
        setup_dark_axes(axr)
        axr.axhline(0, color='#444', linewidth=0.8)
        axr.plot(full['t_fit'], full['resid_exp'], 'o-', color=RED,
                 linewidth=1.5, markersize=5,
                 label=f"exp residuals (stddev {full['resid_exp'].std():.4f})")
        axr.plot(full['t_fit'], full['resid_str'], 's-', color=BLUE,
                 linewidth=1.5, markersize=5,
                 label=f"stretched residuals (stddev {full['resid_str'].std():.4f})")
        axr.set_xlabel('step t')
        axr.set_ylabel('residual of log(L1)')
        axr.set_title('Fit residuals: structureless = correct model',
                      color=FG, fontsize=12)
        axr.grid(color='#222', linewidth=0.6, alpha=0.6)
        leg = axr.legend(loc='best', facecolor='#111', edgecolor=SPINE)
        for txt in leg.get_texts():
            txt.set_color(FG)
        plt.tight_layout()
        save_figure(fig2, FIG_RESID)


if __name__ == '__main__':
    main()
