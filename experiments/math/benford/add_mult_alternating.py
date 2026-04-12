"""
Alternating additive collapse and multiplicative kicks.
"""

from common import (
    HAVE_BIDDER,
    N_WALKERS,
    add_uniform,
    bidder_choices,
    bidder_increments,
    experiment_path,
    make_step_from_choices,
    make_step_from_increments,
    mul_constant,
    plot_demo_lines,
    run_schedule,
    save_checkpoints,
)


NAME = 'add_mult_alternating'
N_ADD_PER_CYCLE = 500
N_CYCLES = 20


def main():
    ops = []

    if HAVE_BIDDER:
        print(f'Using BIDDER cipher for {NAME}')
        for cycle in range(N_CYCLES):
            inc = bidder_increments(
                N_WALKERS, N_ADD_PER_CYCLE, -1.0, 1.0,
                name=f'{NAME}_c{cycle}',
            )
            ops.append((
                'add_uniform(-1, 1)', N_ADD_PER_CYCLE,
                make_step_from_increments(inc),
            ))
            ops.append(('mul_constant(2)', 1, mul_constant(2.0)))
    else:
        print(f'Using numpy PRNG for {NAME}')
        for _ in range(N_CYCLES):
            ops.append(('add_uniform(-1, 1)', N_ADD_PER_CYCLE,
                        add_uniform(-1.0, 1.0)))
            ops.append(('mul_constant(2)', 1, mul_constant(2.0)))

    ckpts = run_schedule(ops, initial=1.0)
    save_checkpoints(experiment_path(f'data_{NAME}.npz'), ckpts)
    plot_demo_lines(
        ckpts,
        title='Add/mult alternating: collapse, then kick',
        out_path=experiment_path(f'{NAME}_l1.png'),
    )


if __name__ == '__main__':
    main()
