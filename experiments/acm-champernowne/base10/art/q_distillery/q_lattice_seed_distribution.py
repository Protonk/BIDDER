"""
q_lattice_seed_distribution.py - bracket the random-input floor.

For each random transform (tau-rand, rowgauss, constgauss), run iter_5
with N_SEEDS different random seeds. Report the distribution of total
sum|corr| across seeds. Compare to the deterministic original lattice's
iter_5.

Question: is the original (0.00775) clearly outside the random-input
distribution, or within ~1 sigma of the seed-noise band?

If well outside (> 3 sigma): real substrate-specific signal.
If marginal: we cannot claim substrate content from this probe.

Also reports whether rowgauss < constgauss reliably across seeds, or
whether the apparent ordering from one-seed-each was noise.
"""

import os
import time
import numpy as np


HERE = os.path.dirname(os.path.abspath(__file__))
N_SEEDS = 20


def slog(arr, lt=1.0):
    arr = np.asarray(arr, dtype=float)
    return np.sign(arr) * np.log10(1.0 + np.abs(arr) / lt)


def fft_log_mag(img):
    centered = img - img.mean()
    F = np.fft.fftshift(np.fft.fft2(centered))
    return np.log10(np.abs(F) + 1.0).astype(np.float32)


def lag_corr(img, dy, dx):
    h, w = img.shape
    y_start_a = max(0, -dy)
    y_end_a = h + min(0, -dy)
    y_start_b = max(0, dy)
    y_end_b = h + min(0, dy)
    x_start_a = max(0, -dx)
    x_end_a = w + min(0, -dx)
    x_start_b = max(0, dx)
    x_end_b = w + min(0, dx)
    a = img[y_start_a:y_end_a, x_start_a:x_end_a].ravel().astype(np.float64)
    b = img[y_start_b:y_end_b, x_start_b:x_end_b].ravel().astype(np.float64)
    a = a - a.mean()
    b = b - b.mean()
    norm = np.sqrt(np.dot(a, a) * np.dot(b, b))
    if norm == 0:
        return 0.0
    return float(np.dot(a, b) / norm)


def total_budget(img):
    lags = [1, 2, 4, 8, 16, 32]
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    s = 0.0
    for dy_u, dx_u in directions:
        for L in lags:
            s += abs(lag_corr(img, dy_u * L, dx_u * L))
    return s


def per_direction_budget(img):
    lags = [1, 2, 4, 8, 16, 32]
    dir_names = ['x', 'y', '+diag', '-diag']
    dir_units = [(0, 1), (1, 0), (1, 1), (1, -1)]
    out = {}
    for name, (dy_u, dx_u) in zip(dir_names, dir_units):
        s = 0.0
        for L in lags:
            s += abs(lag_corr(img, dy_u * L, dx_u * L))
        out[name] = s
    return out


def iter_5_from_input(input_grid):
    img = slog(input_grid).astype(np.float32)
    for _ in range(5):
        img = fft_log_mag(img)
    return img


def tau_rand_input(grid, seed):
    rng = np.random.default_rng(seed)
    out = np.empty_like(grid)
    for i in range(grid.shape[0]):
        perm = rng.permutation(grid.shape[1])
        out[i] = grid[i, perm]
    return out


def rowgauss_input(grid, seed):
    rng = np.random.default_rng(seed)
    out = np.empty_like(grid)
    for i in range(grid.shape[0]):
        m = float(grid[i].mean())
        s = float(grid[i].std())
        out[i] = rng.normal(loc=m, scale=s,
                            size=grid.shape[1]).astype(grid.dtype)
    return out


def constgauss_input(grid, seed):
    rng = np.random.default_rng(seed)
    glob_m = float(grid.mean())
    glob_s = float(grid.std())
    return rng.normal(loc=glob_m, scale=glob_s,
                      size=grid.shape).astype(grid.dtype)


def main():
    cache = os.path.join(HERE, 'q_lattice_4000.npy')
    print('Loading lattice cache...')
    grid = np.load(cache)
    print(f'  shape {grid.shape}')

    print('\nDeterministic baseline: original lattice iter_5')
    t0 = time.time()
    iter5_orig = iter_5_from_input(grid)
    orig_total = total_budget(iter5_orig)
    orig_per_dir = per_direction_budget(iter5_orig)
    print(f'  total = {orig_total:.5f}   ({time.time() - t0:.1f}s)')
    print(f'  per dir: ' + '  '.join(f'{k}={v:.5f}' for k, v in orig_per_dir.items()))

    seeds = list(range(1000, 1000 + N_SEEDS))

    transforms = [
        ('tau-rand', tau_rand_input),
        ('rowgauss', rowgauss_input),
        ('constgauss', constgauss_input),
    ]

    results = {}

    for tname, tfn in transforms:
        print(f'\n=== {tname} across {N_SEEDS} seeds ===')
        totals = []
        per_dirs = {'x': [], 'y': [], '+diag': [], '-diag': []}
        t_overall = time.time()
        for i, seed in enumerate(seeds):
            t0 = time.time()
            inp = tfn(grid, seed)
            iter5 = iter_5_from_input(inp)
            tot = total_budget(iter5)
            pd = per_direction_budget(iter5)
            totals.append(tot)
            for k in pd:
                per_dirs[k].append(pd[k])
            print(f'  seed {seed:>4}: total = {tot:.5f}  '
                  f'(x={pd["x"]:.5f}, y={pd["y"]:.5f}, '
                  f'+d={pd["+diag"]:.5f}, -d={pd["-diag"]:.5f})  '
                  f'[{time.time() - t0:.1f}s]')
        results[tname] = {
            'total': np.array(totals),
            'per_dir': {k: np.array(v) for k, v in per_dirs.items()},
        }
        print(f'  ({time.time() - t_overall:.1f}s for all {N_SEEDS} seeds)')

    # ---- summary ----
    print('\n=== distribution of total |corr| budget ===')
    print(f'{"transform":>12}  {"mean":>9}  {"std":>9}  {"min":>9}  '
          f'{"max":>9}  {"range":>9}')
    print(f'{"original":>12}  {orig_total:>9.5f}  {"-":>9}  {"-":>9}  '
          f'{"-":>9}  {"-":>9}')
    for tname, r in results.items():
        b = r['total']
        print(f'{tname:>12}  {b.mean():>9.5f}  {b.std():>9.5f}  '
              f'{b.min():>9.5f}  {b.max():>9.5f}  '
              f'{b.max()-b.min():>9.5f}')

    print('\n=== where does original sit in each random-transform distribution? ===')
    print(f'{"transform":>12}  {"original":>10}  {"trans mean":>10}  '
          f'{"diff":>10}  {"trans std":>10}  {"z (orig)":>10}')
    for tname, r in results.items():
        b = r['total']
        diff = orig_total - b.mean()
        z = diff / max(b.std(), 1e-12)
        print(f'{tname:>12}  {orig_total:>10.5f}  {b.mean():>10.5f}  '
              f'{diff:>+10.5f}  {b.std():>10.5f}  {z:>+10.2f}')

    print('\n=== rowgauss vs constgauss: is the ordering reliable? ===')
    rg = results['rowgauss']['total']
    cg = results['constgauss']['total']
    diff = rg.mean() - cg.mean()
    pooled_se = np.sqrt(rg.var() / N_SEEDS + cg.var() / N_SEEDS)
    z_rgcg = diff / max(pooled_se, 1e-12)
    print(f'  rowgauss mean   = {rg.mean():.5f}  std = {rg.std():.5f}')
    print(f'  constgauss mean = {cg.mean():.5f}  std = {cg.std():.5f}')
    print(f'  difference (rg - cg) = {diff:+.5f}   pooled SE = {pooled_se:.5f}   '
          f'z = {z_rgcg:+.2f}')
    if abs(z_rgcg) < 1.5:
        print('  -> rowgauss vs constgauss indistinguishable (single-seed ordering was noise)')
    else:
        print('  -> rowgauss vs constgauss ordering is reliable')

    print('\n=== per-direction distribution (mean ± std across seeds) ===')
    print(f'{"transform":>12}  ' + '  '.join(f'{d:>14}' for d in ['x', 'y', '+diag', '-diag']))
    print(f'{"original":>12}  ' + '  '.join(
        f'{orig_per_dir[d]:>14.5f}' for d in ['x', 'y', '+diag', '-diag']
    ))
    for tname, r in results.items():
        line = f'{tname:>12}  '
        for d in ['x', 'y', '+diag', '-diag']:
            v = r['per_dir'][d]
            line += f'{v.mean():>+7.5f}±{v.std():.5f}  '
        print(line)


if __name__ == '__main__':
    main()
