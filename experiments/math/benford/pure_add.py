"""
Contrapositive demo: pure additive drift never Benford-izes.
"""

from common import (
    HAVE_BIDDER,
    N_WALKERS,
    add_uniform,
    bidder_increments,
    experiment_path,
    make_step_from_increments,
    plot_demo_lines,
    run_schedule,
    save_checkpoints,
)


NAME = 'pure_add'
N_STEPS = 20_000


def main():
    if HAVE_BIDDER:
        print(f'Using BIDDER cipher for {NAME}')
        increments = bidder_increments(N_WALKERS, N_STEPS, -1.0, 1.0, name=NAME)
        step = make_step_from_increments(increments)
    else:
        print(f'Using numpy PRNG for {NAME}')
        step = add_uniform(-1.0, 1.0)

    ops = [('add_uniform(-1, 1)', N_STEPS, step)]
    ckpts = run_schedule(ops, initial=1.0)
    save_checkpoints(experiment_path(f'data_{NAME}.npz'), ckpts)
    plot_demo_lines(
        ckpts,
        title='Pure add: sticky mantissas, not Benford',
        out_path=experiment_path(f'{NAME}_l1.png'),
    )


if __name__ == '__main__':
    main()
