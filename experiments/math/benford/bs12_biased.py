"""
bs12_biased.py — BS(1,2) random walk with biased generator weights.

Weights: +1 : -1 : *2 : /2 = 0.20 : 0.20 : 0.40 : 0.20.
Net mult drift of +0.20 per step sends |x| to astronomical scales
within a few thousand steps, so the walker is tracked as log10|x|
directly. When |x| is above 10^15 the +/-1 steps are treated as
no-ops in log space (their contribution is below float64 precision).
"""

import math
import numpy as np

from common import (
    BENFORD_BOUNDARIES_BASE10,
    LOG_MANTISSA_BINS,
    N_WALKERS,
    SEED,
    experiment_path,
    l1_to_uniform,
    plot_demo_lines,
    save_checkpoints,
)


NAME = 'bs12_biased'
N_STEPS = 20_000
TARGET_CHECKPOINTS = 200
P_PLUS, P_MINUS, P_MUL, P_DIV = 0.20, 0.20, 0.40, 0.20
PROBS = np.array([P_PLUS, P_MINUS, P_MUL, P_DIV])
LOG10_2 = math.log10(2.0)
SMALL_THRESHOLD = 15.0  # above this, +/-1 is negligible in log space


def run():
    rng = np.random.default_rng(SEED ^ 0xB1A5)
    logx = np.full(N_WALKERS, 0.5 * LOG10_2, dtype=np.float64)

    checkpoint_steps = np.unique(
        np.linspace(0, N_STEPS, TARGET_CHECKPOINTS + 1, dtype=np.int64)
    )
    K = checkpoint_steps.size
    step_record = np.zeros(K, dtype=np.int64)
    log_mantissa_hist = np.zeros((K, LOG_MANTISSA_BINS), dtype=np.float32)
    l1_arr = np.zeros(K, dtype=np.float32)
    leading_1_frac = np.zeros(K, dtype=np.float32)

    boundary_digit_2 = float(BENFORD_BOUNDARIES_BASE10[1])

    def record(idx, step_index):
        mantissa = np.mod(logx, 1.0)
        hist, _ = np.histogram(mantissa, bins=LOG_MANTISSA_BINS, range=(0.0, 1.0))
        total = float(hist.sum())
        hist_norm = (hist.astype(np.float64) / total) if total > 0 else hist.astype(np.float64)
        log_mantissa_hist[idx] = hist_norm.astype(np.float32)
        l1_arr[idx] = np.float32(l1_to_uniform(hist_norm))
        leading_1_frac[idx] = np.float32(np.mean(mantissa < boundary_digit_2))
        step_record[idx] = step_index

    record(0, 0)
    ckpt_idx = 1
    op = 0
    while op < N_STEPS:
        target = int(checkpoint_steps[ckpt_idx])
        for _ in range(target - op):
            choice = rng.choice(4, size=logx.size, p=PROBS)
            mul_mask = choice == 2
            div_mask = choice == 3
            logx[mul_mask] += LOG10_2
            logx[div_mask] -= LOG10_2

            pm_mask = (choice == 0) | (choice == 1)
            small = pm_mask & (logx < SMALL_THRESHOLD)
            if small.any():
                sub_idx = np.where(small)[0]
                x_sub = np.power(10.0, logx[sub_idx])
                sign = np.where(choice[sub_idx] == 0, 1.0, -1.0)
                x_new = np.abs(x_sub + sign)
                x_new = np.maximum(x_new, 1e-15)
                logx[sub_idx] = np.log10(x_new)
        op = target
        record(ckpt_idx, op)
        ckpt_idx += 1

    return {
        'step': step_record,
        'log_mantissa_hist': log_mantissa_hist,
        'l1': l1_arr,
        'leading_1_frac': leading_1_frac,
        'final_logx': logx.copy(),
        'schedule_summary': np.asarray(
            f'{N_STEPS} x bs12_biased({P_PLUS},{P_MINUS},{P_MUL},{P_DIV})'
        ),
    }


def main():
    ckpts = run()
    save_checkpoints(experiment_path(f'data_{NAME}.npz'), ckpts)

    final_l1 = float(ckpts['l1'][-1])
    final_leading_1 = float(ckpts['leading_1_frac'][-1])
    mean_log = float(ckpts['final_logx'].mean())
    spread = float(ckpts['final_logx'].std())
    print(f'final L1 to uniform: {final_l1:.4f}')
    print(f'final leading-digit-1 fraction: {final_leading_1:.4f} '
          f'(Benford: {LOG10_2:.4f})')
    print(f'final log10|x|: mean={mean_log:.1f}  sigma={spread:.1f}')

    plot_demo_lines(
        ckpts,
        title=f'Biased BS(1,2) walk  ({P_PLUS}, {P_MINUS}, {P_MUL}, {P_DIV})',
        out_path=experiment_path(f'{NAME}_l1.png'),
    )


if __name__ == '__main__':
    main()
