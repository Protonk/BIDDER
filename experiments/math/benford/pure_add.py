"""
Contrapositive demo: pure additive drift never Benford-izes.
"""

from common import (
    add_uniform,
    experiment_path,
    plot_demo_lines,
    run_schedule,
    save_checkpoints,
)


NAME = 'pure_add'


def main():
    ops = [
        ('add_uniform(-1, 1)', 20_000, add_uniform(-1.0, 1.0)),
    ]
    ckpts = run_schedule(ops, initial=1.0)
    save_checkpoints(experiment_path(f'data_{NAME}.npz'), ckpts)
    plot_demo_lines(
        ckpts,
        title='Pure add: sticky mantissas, not Benford',
        out_path=experiment_path(f'{NAME}_l1.png'),
    )


if __name__ == '__main__':
    main()
