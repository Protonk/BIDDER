"""
gap3_phase3.py — Phase 3 of FIRST-PROOF gap 3 simulation plan.

Biased BS(1,2) walk, weights (p_plus, p_minus, p_mul, p_div) =
(0.2, 0.2, 0.4, 0.2). Net multiplicative drift +0.20/step in the
a/a^-1 component.

Question: does L1-to-Benford decay past the reported "floor" at
~0.091 as a power law (once walkers escape the active zone and
only a/a^-1 act on the mantissa, irrational rotation produces
algebraic equidistribution), or does it truly floor?

Representation: (m, E, sign) where |x| = 10^(E+m), m in [0, 1),
E int, sign in {+1, -1}. Avoids float64 overflow when |E| gets
large (biased walk produces |E| ~ 3000 by t = 50_000).

Three-case b-step (add 1 / subtract 1):
  frozen (E > THRESH): identity on mantissa
  snap   (E < -THRESH): snap to (m=0, E=0, sign=sign(delta))
  active (|E| <= THRESH): compute directly

Output:
  paper/sim/data/gap3_phase3.npz / .csv
  paper/sim/fig/gap3_biased.png  (log-linear and log-log panels)
"""

import math
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

from common import (
    BG, FG, GREEN, RED, SPINE, YELLOW, BLUE,
    LOG_MANTISSA_BINS,
    l1_to_uniform,
    save_figure, setup_dark_axes,
)


N_WALKERS = 1_000_000
SEED_LOCAL = 0xB1A5
LOG10_2 = math.log10(2.0)
E_THRESH = 20  # |E| threshold for active vs frozen/snap

CHECKPOINTS = np.array([
    0, 5, 10, 20, 50, 100, 200, 500, 1_000, 2_000, 5_000, 10_000,
    20_000, 35_000, 50_000,
], dtype=np.int64)

WEIGHTS = np.array([0.2, 0.2, 0.4, 0.2], dtype=np.float64)
# choice: 0 = +1 (b), 1 = -1 (b^-1), 2 = *2 (a), 3 = /2 (a^-1)

HERE = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.join(HERE, 'paper', 'sim')
DATA_NPZ = os.path.join(SIM_DIR, 'data', 'gap3_phase3.npz')
DATA_CSV = os.path.join(SIM_DIR, 'data', 'gap3_phase3.csv')
FIG_OUT = os.path.join(SIM_DIR, 'fig', 'gap3_biased.png')


def record_hist(m, E, sign):
    """L1 of log-mantissa histogram to uniform."""
    del E, sign  # mantissa alone is enough (m is log_10 mantissa already)
    hist, _ = np.histogram(m, bins=LOG_MANTISSA_BINS, range=(0.0, 1.0))
    hist_norm = hist.astype(np.float64) / hist.sum()
    return l1_to_uniform(hist_norm)


def a_step(m, E, mask):
    """Multiply by 2: m += log10(2) mod 1, E += carry."""
    sub = np.where(mask)[0]
    if sub.size == 0:
        return
    m_new = m[sub] + LOG10_2
    carry = m_new >= 1.0
    m_new_out = np.where(carry, m_new - 1.0, m_new)
    m[sub] = m_new_out
    E[sub] += carry.astype(np.int64)


def ainv_step(m, E, mask):
    """Divide by 2: m -= log10(2) mod 1, E -= borrow."""
    sub = np.where(mask)[0]
    if sub.size == 0:
        return
    m_new = m[sub] - LOG10_2
    borrow = m_new < 0.0
    m_new_out = np.where(borrow, m_new + 1.0, m_new)
    m[sub] = m_new_out
    E[sub] -= borrow.astype(np.int64)


def b_or_binv_step(m, E, sign, mask, delta):
    """Add delta (+1 or -1) to x = sign * 10^(E + m), in-place on (m, E, sign).

    Three zones:
      E > THRESH: frozen (mantissa and sign unchanged)
      E < -THRESH: snap to (0, 0, sign(delta))
      else: compute x + delta explicitly in float64
    """
    sub = np.where(mask)[0]
    if sub.size == 0:
        return

    E_sub = E[sub]
    frozen = E_sub > E_THRESH
    snap = E_sub < -E_THRESH
    active = ~(frozen | snap)

    # Snap: tiny |x|, x + delta ≈ delta, so (m, E) = (0, 0), sign = sign(delta).
    snap_idx = sub[snap]
    m[snap_idx] = 0.0
    E[snap_idx] = 0
    sign[snap_idx] = np.int8(1 if delta > 0 else -1)

    # Active: compute in float64.
    act_idx = sub[active]
    if act_idx.size == 0:
        return
    log_mag = E[act_idx].astype(np.float64) + m[act_idx]
    x = sign[act_idx].astype(np.float64) * np.power(10.0, log_mag)
    x_new = x + float(delta)

    # Edge case: x_new == 0 (sign=-1 was fine, but 10^E+m + 1 >= 1 > 0 always so
    # only if sign=-1 and x=-1, which we treat as snap-to-origin).
    zero = x_new == 0.0
    if zero.any():
        # snap to (0, 0, +1) (arbitrary, probability zero in practice)
        zidx = act_idx[zero]
        m[zidx] = 0.0
        E[zidx] = 0
        sign[zidx] = np.int8(1)
        # exclude from further processing
        nonzero = ~zero
        log_abs = np.log10(np.abs(x_new[nonzero]))
        E_new = np.floor(log_abs).astype(np.int64)
        m_new = log_abs - E_new.astype(np.float64)
        sign_new = np.where(x_new[nonzero] > 0.0, np.int8(1), np.int8(-1))
        nz_idx = act_idx[nonzero]
        m[nz_idx] = m_new
        E[nz_idx] = E_new
        sign[nz_idx] = sign_new
    else:
        log_abs = np.log10(np.abs(x_new))
        E_new = np.floor(log_abs).astype(np.int64)
        m_new = log_abs - E_new.astype(np.float64)
        sign_new = np.where(x_new > 0.0, np.int8(1), np.int8(-1))
        m[act_idx] = m_new
        E[act_idx] = E_new
        sign[act_idx] = sign_new


def run():
    rng = np.random.default_rng(SEED_LOCAL)

    # Initial: all walkers at x = sqrt(2) => m = log10(sqrt(2)), E = 0, sign = +1
    m = np.full(N_WALKERS, math.log10(math.sqrt(2.0)), dtype=np.float64)
    E = np.zeros(N_WALKERS, dtype=np.int64)
    sign = np.ones(N_WALKERS, dtype=np.int8)

    K = CHECKPOINTS.size
    l1 = np.zeros(K, dtype=np.float64)
    mean_E = np.zeros(K, dtype=np.float64)
    active_frac = np.zeros(K, dtype=np.float64)

    def record(idx):
        l1[idx] = record_hist(m, E, sign)
        mean_E[idx] = float(E.mean())
        active_frac[idx] = float((np.abs(E) <= E_THRESH).mean())
        print(f'  t={CHECKPOINTS[idx]:6d}  L1={l1[idx]:.6f}  '
              f'<E>={mean_E[idx]:.2f}  active={active_frac[idx]*100:.1f}%',
              flush=True)

    print(f'Biased BS(1,2) walk: N={N_WALKERS:_}, weights={WEIGHTS.tolist()}',
          flush=True)
    print(f'checkpoints: {CHECKPOINTS.tolist()}', flush=True)
    record(0)

    cursor = 0
    for idx in range(1, K):
        target = int(CHECKPOINTS[idx])
        n_steps = target - cursor
        for _ in range(n_steps):
            choice = rng.choice(4, size=N_WALKERS, p=WEIGHTS)
            a_step(m, E, choice == 2)
            ainv_step(m, E, choice == 3)
            b_or_binv_step(m, E, sign, choice == 0, +1)
            b_or_binv_step(m, E, sign, choice == 1, -1)
        cursor = target
        record(idx)

    return CHECKPOINTS.copy(), l1, mean_E, active_frac


def main():
    os.makedirs(os.path.dirname(DATA_NPZ), exist_ok=True)
    os.makedirs(os.path.dirname(FIG_OUT), exist_ok=True)

    t, l1, mean_E, active_frac = run()

    floor = math.sqrt(2.0 * LOG_MANTISSA_BINS / (math.pi * N_WALKERS))
    print(f'\nnoise floor (N={N_WALKERS:_}, B={LOG_MANTISSA_BINS}): {floor:.5f}')

    np.savez_compressed(DATA_NPZ, t=t, l1=l1, mean_E=mean_E,
                        active_frac=active_frac, floor=floor)
    with open(DATA_CSV, 'w') as f:
        f.write('t,L1,mean_E,active_frac\n')
        for ti, li, Ei, af in zip(t, l1, mean_E, active_frac):
            f.write(f'{int(ti)},{li:.8e},{Ei:.4f},{af:.6f}\n')
    print(f'-> {DATA_NPZ}')
    print(f'-> {DATA_CSV}')

    # Shape diagnostic: fit power-law tail on late-time points.
    # Power-law: log(L1) = a - alpha*log(t) => straight line on log-log.
    # Floor: log(L1) flat at late t.
    # Stretched exp: log(L1) = -c*sqrt(t).

    late_mask = t >= 500
    if late_mask.sum() >= 3:
        log_t_late = np.log(t[late_mask].astype(np.float64))
        log_l1_late = np.log(l1[late_mask])

        # Power-law fit
        slope_pl, int_pl = np.polyfit(log_t_late, log_l1_late, 1)
        pred_pl = slope_pl * log_t_late + int_pl
        r2_pl = 1.0 - np.sum((log_l1_late - pred_pl)**2) / max(
            np.sum((log_l1_late - log_l1_late.mean())**2), 1e-30)
        alpha_pl = -slope_pl

        # Stretched exp fit
        sqrt_t_late = np.sqrt(t[late_mask].astype(np.float64))
        slope_str, int_str = np.polyfit(sqrt_t_late, log_l1_late, 1)
        pred_str = slope_str * sqrt_t_late + int_str
        r2_str = 1.0 - np.sum((log_l1_late - pred_str)**2) / max(
            np.sum((log_l1_late - log_l1_late.mean())**2), 1e-30)
        c_str = -slope_str

        print(f'\n=== LATE-TIME FITS (t >= 500) ===')
        print(f'  power-law:     alpha = {alpha_pl:.4f}   R^2 = {r2_pl:.4f}')
        print(f'  stretched exp: c     = {c_str:.4f}   R^2 = {r2_str:.4f}')

    # Two-panel plot.
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(BG)

    ax1 = axes[0]
    setup_dark_axes(ax1)
    nonzero = l1 > 0
    ax1.loglog(t[nonzero], l1[nonzero], 'o-', color=YELLOW, linewidth=1.6,
               markersize=5, label=f'empirical L1 (N={N_WALKERS:_})')
    if late_mask.sum() >= 3:
        grid_late = np.linspace(t[late_mask][0], t[late_mask][-1], 100)
        ax1.loglog(grid_late, np.exp(int_pl) * grid_late**slope_pl,
                   '--', color=RED, linewidth=1.4,
                   label=f'power-law fit (t>=500): alpha={alpha_pl:.3f}, R2={r2_pl:.3f}')
    ax1.axhline(floor, color='#666', linestyle=':', linewidth=0.9,
                label=f'noise floor {floor:.4f}')
    ax1.set_xlabel('step t')
    ax1.set_ylabel('L1 to uniform log-mantissa')
    ax1.set_title('log-log:  straight line = power-law decay',
                  color=FG, fontsize=11)
    ax1.grid(which='both', color='#222', linewidth=0.5, alpha=0.6)
    leg1 = ax1.legend(loc='lower left', facecolor='#111', edgecolor=SPINE,
                      fontsize=9)
    for tx in leg1.get_texts():
        tx.set_color(FG)

    ax2 = axes[1]
    setup_dark_axes(ax2)
    ax2.semilogy(t[nonzero], l1[nonzero], 'o-', color=YELLOW, linewidth=1.6,
                 markersize=5, label=f'empirical L1')
    ax2.axhline(floor, color='#666', linestyle=':', linewidth=0.9,
                label=f'noise floor {floor:.4f}')
    ax2.set_xlabel('step t')
    ax2.set_ylabel('L1 to uniform log-mantissa')
    ax2.set_title('log-linear:  straight line = exponential decay',
                  color=FG, fontsize=11)
    ax2.grid(which='both', color='#222', linewidth=0.5, alpha=0.6)
    leg2 = ax2.legend(loc='upper right', facecolor='#111', edgecolor=SPINE,
                      fontsize=9)
    for tx in leg2.get_texts():
        tx.set_color(FG)

    fig.suptitle('Gap 3 phase 3: biased BS(1,2) walk, weights (0.2, 0.2, 0.4, 0.2)',
                 color=FG, fontsize=13)
    plt.tight_layout()
    save_figure(fig, FIG_OUT)


if __name__ == '__main__':
    main()
