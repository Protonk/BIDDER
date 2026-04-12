"""
Alternating additive collapse and multiplicative kicks.
"""

from common import (
    add_uniform,
    experiment_path,
    mul_constant,
    plot_demo_lines,
    run_schedule,
    save_checkpoints,
)


NAME = 'add_mult_alternating'


def main():
    ops = []
    for _ in range(20):
        ops.append(('add_uniform(-1, 1)', 500, add_uniform(-1.0, 1.0)))
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
