"""
Benford first, then frozen by scale.
"""

import numpy as np

from common import (
    HAVE_BIDDER,
    N_WALKERS,
    SEED,
    add_uniform,
    bidder_increments,
    experiment_path,
    make_step_from_increments,
    mul_constant,
    plot_demo_lines,
    run_schedule,
    save_checkpoints,
)


NAME = 'front_loaded'


def main():
    rng = np.random.default_rng(SEED ^ 0xF10ADED)
    initial = np.power(10.0, rng.uniform(0.0, 1.0, size=N_WALKERS))

    ops = [('mul_constant(2)', 500, mul_constant(2.0))]

    if HAVE_BIDDER:
        print(f'Using BIDDER cipher for {NAME}')
        inc1 = bidder_increments(N_WALKERS, 2_000, -1.0, 1.0,
                                 name=f'{NAME}_add1')
        ops.append(('add_uniform(-1, 1)', 2_000,
                     make_step_from_increments(inc1)))
        ops.append(('mul_constant(2)', 1, mul_constant(2.0)))
        inc2 = bidder_increments(N_WALKERS, 10_000, -1.0, 1.0,
                                 name=f'{NAME}_add2')
        ops.append(('add_uniform(-1, 1)', 10_000,
                     make_step_from_increments(inc2)))
    else:
        print(f'Using numpy PRNG for {NAME}')
        ops.append(('add_uniform(-1, 1)', 2_000, add_uniform(-1.0, 1.0)))
        ops.append(('mul_constant(2)', 1, mul_constant(2.0)))
        ops.append(('add_uniform(-1, 1)', 10_000, add_uniform(-1.0, 1.0)))

    ckpts = run_schedule(ops, initial=initial)
    save_checkpoints(experiment_path(f'data_{NAME}.npz'), ckpts)
    plot_demo_lines(
        ckpts,
        title='Front-loaded: Benford first, then frozen by huge scale',
        out_path=experiment_path(f'{NAME}_l1.png'),
    )


if __name__ == '__main__':
    main()
