"""
BS(1,2)-style walk with additive and multiplicative moves.
"""

import math

from common import (
    HAVE_BIDDER,
    N_WALKERS,
    bidder_choices,
    bs12_step,
    experiment_path,
    make_step_from_choices,
    plot_demo_lines,
    run_schedule,
    save_checkpoints,
)


NAME = 'bs12_walk'
N_STEPS = 20_000


def main():
    if HAVE_BIDDER:
        print(f'Using BIDDER cipher for {NAME}')
        choices = bidder_choices(N_WALKERS, N_STEPS, name=NAME)
        step = make_step_from_choices(choices)
    else:
        print(f'Using numpy PRNG for {NAME}')
        step = bs12_step()

    ops = [('bs12_step', N_STEPS, step)]
    ckpts = run_schedule(ops, initial=math.sqrt(2.0))
    save_checkpoints(experiment_path(f'data_{NAME}.npz'), ckpts)
    plot_demo_lines(
        ckpts,
        title='BS(1,2) walk: mixed adds, doubles, halves',
        out_path=experiment_path(f'{NAME}_l1.png'),
    )


if __name__ == '__main__':
    main()
