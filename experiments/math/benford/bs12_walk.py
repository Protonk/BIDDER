"""
BS(1,2)-style walk with additive and multiplicative moves.
"""

import math

from common import (
    bs12_step,
    experiment_path,
    plot_demo_lines,
    run_schedule,
    save_checkpoints,
)


NAME = 'bs12_walk'


def main():
    ops = [
        ('bs12_step', 20_000, bs12_step()),
    ]
    ckpts = run_schedule(ops, initial=math.sqrt(2.0))
    save_checkpoints(experiment_path(f'data_{NAME}.npz'), ckpts)
    plot_demo_lines(
        ckpts,
        title='BS(1,2) walk: mixed adds, doubles, halves',
        out_path=experiment_path(f'{NAME}_l1.png'),
    )


if __name__ == '__main__':
    main()
