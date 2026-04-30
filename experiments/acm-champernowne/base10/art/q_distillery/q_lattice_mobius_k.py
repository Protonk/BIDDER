"""
q_lattice_mobius_k.py - Mobius inversion along the k-axis, then
iter_5 angular spectrum.

For each row n of the lattice (fixed n, k varying), apply Mobius
inversion along k:

    new_row[k]  =  Σ_{d | k}  μ(k/d)  ·  row[d]

This is the Dirichlet inverse of the all-ones convolution. The
master expansion's τ_j(m/n^j) is a j-fold Dirichlet self-convolution
of `1`; one Mobius application along k peels one layer of that stack.

Then run iter_5 (FFT-mag-log five times) on the Mobius-inverted
lattice. Compute 16-angle spectrum. Compare to original and to a
constgauss baseline (single seed for first cut).

If the angular structure at iter_5 is responding primarily to
τ-stack content, peeling should change the spectrum. If the FFT
iteration is responding to something else, the spectrum should
look like the original's.

We will find out which it is later, the test is a new one.
"""

import os
import time
from math import atan2, degrees

import numpy as np
from scipy.sparse import lil_matrix, csr_matrix


HERE = os.path.dirname(os.path.abspath(__file__))


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


def iter_5_from_input(input_grid):
    img = slog(input_grid).astype(np.float32)
    for _ in range(5):
        img = fft_log_mag(img)
    return img


def mobius_sieve(N):
    """μ(1), μ(2), …, μ(N)."""
    mu = np.ones(N + 1, dtype=np.int8)
    mu[0] = 0
    primes = []
    is_composite = np.zeros(N + 1, dtype=bool)
    for p in range(2, N + 1):
        if not is_composite[p]:
            primes.append(p)
        for q in primes:
            if p * q > N:
                break
            is_composite[p * q] = True
            if p % q == 0:
                mu[p * q] = 0
                break
            else:
                mu[p * q] = -mu[p]
    return mu


def build_mobius_matrix(K, mu):
    """Sparse K×K matrix M with M[k-1, d-1] = μ(k/d) if d | k else 0."""
    M = lil_matrix((K, K), dtype=np.float64)
    for k in range(1, K + 1):
        d = 1
        while d * d <= k:
            if k % d == 0:
                M[k - 1, d - 1] = mu[k // d]
                other = k // d
                if other != d:
                    M[k - 1, other - 1] = mu[d]
            d += 1
    return csr_matrix(M)


DIRECTIONS = [
    (0, 1), (1, 3), (1, 2), (2, 3), (1, 1), (3, 2), (2, 1), (3, 1),
    (1, 0), (3, -1), (2, -1), (3, -2), (1, -1), (2, -3), (1, -2), (1, -3),
]
LAGS = [1, 2, 4]


def angular_sums(img):
    sums = []
    for dy_u, dx_u in DIRECTIONS:
        s = 0.0
        for L in LAGS:
            s += abs(lag_corr(img, dy_u * L, dx_u * L))
        sums.append(s)
    return sums


def main():
    cache = os.path.join(HERE, 'q_lattice_4000.npy')
    print('Loading lattice...')
    grid = np.load(cache).astype(np.float64)
    K = grid.shape[1]
    print(f'  shape {grid.shape}')

    print(f'Sieving μ up to k = {K}...')
    t0 = time.time()
    mu = mobius_sieve(K)
    print(f'  {time.time() - t0:.2f}s')
    nz = (mu != 0).sum()
    print(f'  μ nonzero count: {nz} / {K + 1}')

    print('Building Mobius matrix...')
    t0 = time.time()
    M = build_mobius_matrix(K, mu)
    print(f'  {time.time() - t0:.2f}s   nnz = {M.nnz}')

    print('Applying Mobius inversion to each row...')
    t0 = time.time()
    # grid_mu[i, k-1] = sum_{d|k} mu(k/d) * grid[i, d-1]
    # Equivalently: grid_mu[i] = M @ grid[i]
    # In bulk: grid_mu = (M @ grid.T).T
    grid_mu = (M @ grid.T).T.astype(np.float32)
    print(f'  {time.time() - t0:.2f}s   '
          f'range [{grid_mu.min():.3g}, {grid_mu.max():.3g}]')

    np.save(os.path.join(HERE, 'q_lattice_mobius_k.npy'), grid_mu)

    # iter_5 on each.
    print('\niter_5 of Mobius-inverted lattice...')
    t0 = time.time()
    iter5_mu = iter_5_from_input(grid_mu)
    print(f'  {time.time() - t0:.1f}s')

    print('iter_5 of original (re-run for direct comparison)...')
    t0 = time.time()
    iter5_orig = iter_5_from_input(grid)
    print(f'  {time.time() - t0:.1f}s')

    print('iter_5 of constgauss baseline (seed 1729)...')
    rng = np.random.default_rng(1729)
    grid_cg = rng.normal(loc=grid.mean(), scale=grid.std(),
                         size=grid.shape).astype(grid.dtype)
    iter5_cg = iter_5_from_input(grid_cg)

    print('\nComputing 16-angle spectra...')
    sums_orig = angular_sums(iter5_orig)
    sums_mu = angular_sums(iter5_mu)
    sums_cg = angular_sums(iter5_cg)

    print('\n=== 16-angle spectrum (sum |corr| over L=1,2,4) ===')
    print(f'{"angle°":>8}  {"(dy, dx)":>10}  {"original":>10}  '
          f'{"mobius-k":>10}  {"constgauss":>12}')
    for (dy, dx), s_o, s_m, s_c in zip(DIRECTIONS, sums_orig,
                                        sums_mu, sums_cg):
        ang = degrees(atan2(dy, dx))
        print(f'{ang:>8.1f}  {str((dy, dx)):>10}  '
              f'{s_o:>10.5f}  {s_m:>10.5f}  {s_c:>12.5f}')

    print('\n=== Excess vs constgauss ===')
    print(f'{"angle°":>8}  {"orig - cg":>12}  {"mu - cg":>12}  '
          f'{"mu - orig":>12}')
    for (dy, dx), s_o, s_m, s_c in zip(DIRECTIONS, sums_orig,
                                        sums_mu, sums_cg):
        ang = degrees(atan2(dy, dx))
        print(f'{ang:>8.1f}  {s_o - s_c:>+12.5f}  '
              f'{s_m - s_c:>+12.5f}  {s_m - s_o:>+12.5f}')

    print('\n=== total |corr| budget ===')
    print(f'  original sum |corr|:    {sum(sums_orig):.5f}')
    print(f'  mobius-k sum |corr|:    {sum(sums_mu):.5f}')
    print(f'  constgauss sum |corr|:  {sum(sums_cg):.5f}')

    # Compare angular shapes (correlation between excess vectors)
    excess_orig = np.array(sums_orig) - np.array(sums_cg)
    excess_mu = np.array(sums_mu) - np.array(sums_cg)
    if excess_orig.std() > 0 and excess_mu.std() > 0:
        corr = np.corrcoef(excess_orig, excess_mu)[0, 1]
        print(f'\nCorrelation between (orig - cg) and (mu - cg) angular '
              f'excess vectors:  {corr:+.3f}')
        print(f'  +1.0 = identical angular pattern (Mobius did not '
              f'change the spectrum shape)')
        print(f'   0.0 = unrelated angular patterns (Mobius produced '
              f'a different structure)')
        print(f'  -1.0 = inverted (Mobius flipped which angles are '
              f'enhanced vs depressed)')


if __name__ == '__main__':
    main()
