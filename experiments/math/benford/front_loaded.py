"""
Benford first, then frozen by scale.
"""

import numpy as np

from common import (
    add_uniform,
    N_WALKERS,
    SEED,
    experiment_path,
    mul_constant,
    plot_demo_lines,
    run_schedule,
    save_checkpoints,
)


NAME = 'front_loaded'


def main():
    rng = np.random.default_rng(SEED ^ 0xF10ADED)
    initial = np.power(10.0, rng.uniform(0.0, 1.0, size=N_WALKERS))

    ops = [
        ('mul_constant(2)', 500, mul_constant(2.0)),
        ('add_uniform(-1, 1)', 2_000, add_uniform(-1.0, 1.0)),
        ('mul_constant(2)', 1, mul_constant(2.0)),
        ('add_uniform(-1, 1)', 10_000, add_uniform(-1.0, 1.0)),
    ]
    ckpts = run_schedule(ops, initial=initial)
    save_checkpoints(experiment_path(f'data_{NAME}.npz'), ckpts)
    plot_demo_lines(
        ckpts,
        title='Front-loaded: Benford first, then frozen by huge scale',
        out_path=experiment_path(f'{NAME}_l1.png'),
    )


if __name__ == '__main__':
    main()
