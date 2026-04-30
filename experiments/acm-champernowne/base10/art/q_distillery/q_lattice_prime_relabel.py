"""
q_lattice_prime_relabel.py - test whether the (n, k) Q-lattice's
spectral fingerprint is class-dependent (shape × tau-sig) or
embedding-dependent (specific primes at specific positions).

Per the adversarial critique: pick a random permutation sigma of primes
<= N_MAX, define sigma(n) by prime-factorization action, compute the
new lattice with values Q(sigma(n), sigma(k)). Same (shape × tau-sig)
matrix; different spatial embedding of classes onto the integer line.

Run iter_5 anisotropy test on the relabeled lattice. Compare against
the original iter_5 numbers:
  x      = 0.00204
  y      = 0.00132
  +diag  = 0.00147
  -diag  = 0.00292   (the surprise — 3.19x Gaussian)

If anti-diagonal preference survives sigma roughly intact, the
anisotropy is class-structural. If it shifts direction or magnitude
substantially, it was tracking embedding details (specific prime
positions on the n-axis).
"""

import os
import time
from functools import lru_cache
from math import comb

import numpy as np


HERE = os.path.dirname(os.path.abspath(__file__))
H = 5
N_MAX = 4000
SEED = 1729


@lru_cache(maxsize=None)
def factor_tuple(n):
    if n < 1:
        raise ValueError(f'n must be >= 1, got {n}')
    if n == 1:
        return ()
    out = []
    r = n
    p = 2
    while p * p <= r:
        if r % p == 0:
            e = 0
            while r % p == 0:
                e += 1
                r //= p
            out.append((p, e))
        p += 1 if p == 2 else 2
    if r > 1:
        out.append((r, 1))
    return tuple(out)


def primes_up_to(N):
    sieve = np.ones(N + 1, dtype=bool)
    sieve[:2] = False
    for i in range(2, int(N ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = False
    return [int(p) for p in np.where(sieve)[0]]


def make_relabel(sigma):
    """Build a memoised n -> sigma(n) function via prime factorisation."""
    cache = {1: 1}
    def relabel(n):
        if n in cache:
            return cache[n]
        out = 1
        for p, e in factor_tuple(n):
            out *= sigma[p] ** e
        cache[n] = out
        return out
    return relabel


def q_general(n, h, k):
    n_facts = factor_tuple(n)
    if not n_facts:
        return 0.0
    k_facts = factor_tuple(k)
    k_dict = dict(k_facts)
    nu_n_k = min((k_dict.get(p, 0) // a) for p, a in n_facts)
    h_eff = h + nu_n_k
    n_prime_set = set(p for p, _ in n_facts)
    Q = 0.0
    for j in range(1, h_eff + 1):
        tau = 1
        for p, a in n_facts:
            e_p = k_dict.get(p, 0)
            exp_in_x = (h - j) * a + e_p
            tau *= comb(exp_in_x + j - 1, j - 1)
        for kp, ke in k_facts:
            if kp not in n_prime_set:
                tau *= comb(ke + j - 1, j - 1)
        sign = 1 if j % 2 == 1 else -1
        Q += sign * tau / j
    return Q


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


def main():
    rng = np.random.default_rng(SEED)
    primes = primes_up_to(N_MAX)
    print(f'{len(primes)} primes <= {N_MAX}')
    perm = rng.permutation(primes)
    sigma = dict(zip(primes, [int(p) for p in perm]))

    print(f'\nSample sigma mappings (seed {SEED}):')
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
        print(f'  sigma({p}) = {sigma[p]}')
    relabel = make_relabel(sigma)

    print(f'\nComputing relabeled lattice {N_MAX-1} x {N_MAX}...')
    t0 = time.time()
    grid = np.zeros((N_MAX - 1, N_MAX), dtype=np.float32)
    for ni, n in enumerate(range(2, N_MAX + 1)):
        n_re = relabel(n)
        for ki, k in enumerate(range(1, N_MAX + 1)):
            k_re = relabel(k)
            grid[ni, ki] = q_general(n_re, H, k_re)
        if (ni + 1) % 400 == 0:
            elapsed = time.time() - t0
            frac = (ni + 1) / (N_MAX - 1)
            eta = elapsed * (1 / frac - 1)
            print(f'  row {ni+1}/{N_MAX-1}  {100*frac:5.1f}%  '
                  f'{elapsed:6.1f}s   ETA {eta:6.1f}s', flush=True)
    print(f'compute total: {time.time() - t0:.1f}s')

    # Sanity: value distribution should match original.
    print(f'\nrelabeled grid stats:')
    print(f'  range [{grid.min():.3g}, {grid.max():.3g}]   '
          f'mean {grid.mean():.4f}  std {grid.std():.4f}')

    cache_path = os.path.join(HERE, f'q_lattice_relabel_{SEED}.npy')
    np.save(cache_path, grid)
    print(f'  cached -> {os.path.basename(cache_path)}')

    # Compare to original lattice value-distribution
    orig_path = os.path.join(HERE, 'q_lattice_4000.npy')
    if os.path.exists(orig_path):
        orig = np.load(orig_path)
        print(f'\noriginal grid stats:')
        print(f'  range [{orig.min():.3g}, {orig.max():.3g}]   '
              f'mean {orig.mean():.4f}  std {orig.std():.4f}')
        # Histograms should match (same multiset of Q values).
        bins = np.linspace(min(grid.min(), orig.min()),
                           max(grid.max(), orig.max()), 100)
        h_re, _ = np.histogram(grid, bins=bins)
        h_or, _ = np.histogram(orig, bins=bins)
        max_diff = np.abs(h_re - h_or).max() / max(orig.size, 1)
        print(f'  histogram max abs(p_re - p_orig): {max_diff:.6f}  '
              f'(should be ~0 if value distribution is preserved)')

    # FFT iterate to iter_5
    print('\nIterating to iter_5...')
    img = slog(grid).astype(np.float32)
    for i in range(1, 6):
        img = fft_log_mag(img)
    iter5 = img
    np.save(os.path.join(HERE, f'q_lattice_relabel_{SEED}_iter05.npy'), iter5)
    print(f'  iter_5 (relabeled): mean {iter5.mean():.4f}  '
          f'std {iter5.std():.4f}')

    # Anisotropy test
    rng2 = np.random.default_rng(42)
    gauss = rng2.normal(loc=iter5.mean(), scale=iter5.std(),
                        size=iter5.shape).astype(np.float32)

    lags = [1, 2, 4, 8, 16, 32]
    directions = [
        ('x       (0, +L)', 0, 1),
        ('y       (+L, 0)', 1, 0),
        ('+diag  (+L, +L)', 1, 1),
        ('-diag  (+L, -L)', 1, -1),
    ]
    n_eff = (iter5.shape[0] - 1) * (iter5.shape[1] - 1)
    print(f'\nnoise floor ~= {1/np.sqrt(n_eff):.2e}')

    print('\n=== iter_5 RELABELED lag correlations ===')
    print(f'{"":>20} ' + ' '.join(f'{f"L={L}":>11}' for L in lags))
    sums_re = {}
    for name, dy_unit, dx_unit in directions:
        row = []
        s = 0.0
        for L in lags:
            c = lag_corr(iter5, dy_unit * L, dx_unit * L)
            row.append(f'{c:>+11.5f}')
            s += abs(c)
        sums_re[name] = s
        print(f'{name:>20} ' + ' '.join(row))

    print('\n=== matched Gaussian (control) ===')
    print(f'{"":>20} ' + ' '.join(f'{f"L={L}":>11}' for L in lags))
    sums_g = {}
    for name, dy_unit, dx_unit in directions:
        row = []
        s = 0.0
        for L in lags:
            c = lag_corr(gauss, dy_unit * L, dx_unit * L)
            row.append(f'{c:>+11.5f}')
            s += abs(c)
        sums_g[name] = s
        print(f'{name:>20} ' + ' '.join(row))

    # Comparison vs original iter_5 (numbers from earlier run).
    orig_sums = {
        'x       (0, +L)': 0.00204,
        'y       (+L, 0)': 0.00132,
        '+diag  (+L, +L)': 0.00147,
        '-diag  (+L, -L)': 0.00292,
    }
    print(f'\n=== comparison: ORIGINAL vs RELABELED iter_5 (sum |corr|) ===')
    print(f'{"direction":>20}  {"original":>10}  {"relabeled":>10}  '
          f'{"gauss":>10}   {"orig/gauss":>10}  {"re/gauss":>10}')
    for name in sums_re:
        print(f'{name:>20}  '
              f'{orig_sums[name]:>10.5f}  '
              f'{sums_re[name]:>10.5f}  '
              f'{sums_g[name]:>10.5f}   '
              f'{orig_sums[name]/sums_g[name]:>10.2f}x  '
              f'{sums_re[name]/sums_g[name]:>10.2f}x')


if __name__ == '__main__':
    main()
