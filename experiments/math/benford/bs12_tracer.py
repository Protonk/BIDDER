"""
bs12_tracer.py — Exact-state tracer for a small BS(1,2) ensemble.

Each walker's value is tracked as (N, num, q) with
    x = 2^N * sqrt(2) + num / 2^q
where N is an integer, num is a Python bignum, q >= 0 is an integer.
The walker starts at x = sqrt(2), i.e. (N, num, q) = (0, 0, 0).

Generator actions (applied to the value x):
    +1 : num += 2^q
    -1 : num -= 2^q
    *2 : N += 1,  then q -= 1 if q > 0 else num *= 2
    /2 : N -= 1,  q += 1

Records at 100-step intervals:
    log10|x|        via log-scale combination, no float overflow
    complexity      bit-length proxy: |N| + max(bit_length(|num|), q)
    net_N           the net mult-vs-div count

Output: data_bs12_tracer.npz, shape (N_TRACERS, n_checkpoints).
"""

import math
import numpy as np

from common import SEED, experiment_path


N_TRACERS = 64
N_STEPS = 20_000
RECORD_EVERY = 100
LOG10_2 = math.log10(2.0)


def compute_log10_abs(N, num, q):
    """log10|2^N * sqrt(2) + num/2^q|, safe for arbitrarily large N, num, q."""
    log_A = N * LOG10_2 + 0.5 * LOG10_2  # log10(2^N * sqrt(2))
    if num == 0:
        return log_A
    abs_num = abs(num)
    log_B = math.log10(abs_num) - q * LOG10_2  # log10(|num/2^q|)
    if log_A > log_B + 15:
        return log_A
    if log_B > log_A + 15:
        return log_B
    sign = 1 if num > 0 else -1
    ratio = sign * 10.0 ** (log_B - log_A)
    return log_A + math.log10(abs(1.0 + ratio))


def complexity(N, num, q):
    bits_num = abs(num).bit_length() if num != 0 else 0
    return abs(N) + max(bits_num, q)


def main():
    master_rng = np.random.default_rng(SEED ^ 0xBA1C1E)
    n_checkpoints = N_STEPS // RECORD_EVERY + 1
    steps = np.arange(n_checkpoints, dtype=np.int64) * RECORD_EVERY

    log10_abs_x = np.zeros((N_TRACERS, n_checkpoints), dtype=np.float64)
    complexity_arr = np.zeros((N_TRACERS, n_checkpoints), dtype=np.int64)
    net_N_arr = np.zeros((N_TRACERS, n_checkpoints), dtype=np.int64)

    for w in range(N_TRACERS):
        seed = int(master_rng.integers(0, 2**31 - 1))
        walker_rng = np.random.default_rng(seed)
        choices = walker_rng.integers(0, 4, size=N_STEPS)

        N, num, q = 0, 0, 0
        log10_abs_x[w, 0] = compute_log10_abs(N, num, q)
        complexity_arr[w, 0] = complexity(N, num, q)
        net_N_arr[w, 0] = N

        for s in range(N_STEPS):
            c = int(choices[s])
            if c == 0:
                num = num + (1 << q)
            elif c == 1:
                num = num - (1 << q)
            elif c == 2:
                N += 1
                if q > 0:
                    q -= 1
                else:
                    num = num * 2
            else:
                N -= 1
                q += 1
            s1 = s + 1
            if s1 % RECORD_EVERY == 0:
                idx = s1 // RECORD_EVERY
                log10_abs_x[w, idx] = compute_log10_abs(N, num, q)
                complexity_arr[w, idx] = complexity(N, num, q)
                net_N_arr[w, idx] = N

        if (w + 1) % 8 == 0:
            print(f'  walker {w + 1}/{N_TRACERS} done '
                  f'(final complexity {complexity_arr[w, -1]} bits, '
                  f'|log10|x||={abs(log10_abs_x[w, -1]):.1f})')

    out = experiment_path('data_bs12_tracer.npz')
    np.savez_compressed(
        out,
        log10_abs_x=log10_abs_x,
        complexity=complexity_arr,
        net_N=net_N_arr,
        steps=steps,
    )
    print(f'-> data_bs12_tracer.npz  ({N_TRACERS} walkers, {N_STEPS} steps)')


if __name__ == '__main__':
    main()
