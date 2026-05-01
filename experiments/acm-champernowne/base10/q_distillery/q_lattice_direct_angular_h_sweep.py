"""
q_lattice_direct_angular_h_sweep.py - direct angular spectrum at h = 5, 6, 7, 8.

Build the (n, k) Q-lattice at each h with n_max = k_max = 4000, compute
slog, compute 16-angle direct spatial correlation spectrum, compare
against a single-seed constgauss baseline at the same scale.

Render a polar overlay showing all four h values + their respective
baselines. Plus a scaling plot: total sum|corr| vs h, and the L=1 vs
L=4 anomaly tracked across h.

Caches lattices to npy so re-runs are fast.
"""

import os
import time
from functools import lru_cache
from math import atan2, comb, degrees

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


HERE = os.path.dirname(os.path.abspath(__file__))
H_VALUES = [5, 6, 7, 8]
N_MAX = 4000


@lru_cache(maxsize=None)
def factor_tuple(n):
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


def make_grid(h):
    cache_path = os.path.join(HERE, f'q_lattice_4000_h{h}.npy')
    if os.path.exists(cache_path):
        print(f'  loading cached h={h} grid: {os.path.basename(cache_path)}')
        return np.load(cache_path)
    print(f'  computing h={h} grid (4000 x 4000)...')
    grid = np.zeros((N_MAX - 1, N_MAX), dtype=np.float64)
    t0 = time.time()
    for ni, n in enumerate(range(2, N_MAX + 1)):
        for ki, k in enumerate(range(1, N_MAX + 1)):
            grid[ni, ki] = q_general(n, h, k)
        if (ni + 1) % 500 == 0:
            elapsed = time.time() - t0
            frac = (ni + 1) / (N_MAX - 1)
            eta = elapsed * (1 / frac - 1)
            print(f'    row {ni + 1:>4}/{N_MAX - 1}  '
                  f'{100*frac:5.1f}%  {elapsed:6.1f}s  '
                  f'ETA {eta:6.1f}s', flush=True)
    print(f'  compute total: {time.time() - t0:.1f}s')
    np.save(cache_path, grid)
    print(f'  cached -> {os.path.basename(cache_path)}')
    return grid


def slog(arr, lt=1.0):
    arr = np.asarray(arr, dtype=float)
    return np.sign(arr) * np.log10(1.0 + np.abs(arr) / lt)


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


def constgauss_input(grid, seed):
    rng = np.random.default_rng(seed)
    return rng.normal(loc=float(grid.mean()), scale=float(grid.std()),
                      size=grid.shape).astype(grid.dtype)


DIRECTIONS = [
    (0, 1), (1, 3), (1, 2), (2, 3), (1, 1), (3, 2), (2, 1), (3, 1),
    (1, 0), (3, -1), (2, -1), (3, -2), (1, -1), (2, -3), (1, -2), (1, -3),
]
LAGS = [1, 2, 4]


def angular_corrs(img):
    out = np.zeros((len(DIRECTIONS), len(LAGS)))
    for i, (dy_u, dx_u) in enumerate(DIRECTIONS):
        for j, L in enumerate(LAGS):
            out[i, j] = lag_corr(img, dy_u * L, dx_u * L)
    return out


def main():
    results = {}
    for h in H_VALUES:
        print(f'\n=== h = {h} ===')
        grid = make_grid(h)
        print(f'  range [{grid.min():.3g}, {grid.max():.3g}]')

        print('  computing angular correlations on slog(original)...')
        t0 = time.time()
        img_o = slog(grid).astype(np.float32)
        c_o = angular_corrs(img_o)
        s_o = np.abs(c_o).sum(axis=1)
        print(f'    {time.time() - t0:.1f}s   total |corr| = {s_o.sum():.4f}')

        print('  computing constgauss baseline (seed 1729)...')
        t0 = time.time()
        grid_cg = constgauss_input(grid, 1729)
        img_cg = slog(grid_cg).astype(np.float32)
        c_cg = angular_corrs(img_cg)
        s_cg = np.abs(c_cg).sum(axis=1)
        print(f'    {time.time() - t0:.1f}s   total |corr| = {s_cg.sum():.4f}')

        results[h] = {
            'corrs_orig': c_o,
            'sums_orig': s_o,
            'corrs_cg': c_cg,
            'sums_cg': s_cg,
        }

    # ---- print summary table ----
    print('\n=== summary across h ===')
    print(f'{"h":>3}  {"orig total":>11}  {"cg total":>11}  '
          f'{"ratio":>8}  {"orig 0°":>9}  {"orig 90°":>9}  '
          f'{"orig 45°":>9}  {"orig 135°":>9}')
    for h in H_VALUES:
        r = results[h]
        s_o = r['sums_orig']
        s_cg = r['sums_cg']
        print(f'{h:>3}  {s_o.sum():>11.4f}  {s_cg.sum():>11.4f}  '
              f'{s_o.sum() / max(s_cg.sum(), 1e-12):>8.0f}x  '
              f'{s_o[0]:>9.4f}  {s_o[8]:>9.4f}  '
              f'{s_o[4]:>9.4f}  {s_o[12]:>9.4f}')

    # L = 1 vs L = 4 at 0° and 90° across h
    print('\n=== axial lag-anomaly across h (Pearson at 0° and 90°) ===')
    print(f'{"h":>3}  '
          f'{"0° L=1":>9}  {"0° L=4":>9}  {"L4/L1 (0°)":>11}  '
          f'{"90° L=1":>9}  {"90° L=4":>9}  {"L4/L1 (90°)":>11}')
    for h in H_VALUES:
        c = results[h]['corrs_orig']
        c0_1, c0_4 = c[0, 0], c[0, 2]
        c90_1, c90_4 = c[8, 0], c[8, 2]
        print(f'{h:>3}  '
              f'{c0_1:>+9.4f}  {c0_4:>+9.4f}  '
              f'{c0_4 / max(abs(c0_1), 1e-12):>11.2f}  '
              f'{c90_1:>+9.4f}  {c90_4:>+9.4f}  '
              f'{c90_4 / max(abs(c90_1), 1e-12):>11.2f}')

    # ---- plot ----
    fig = plt.figure(figsize=(15, 10), facecolor='#0a0a0a', dpi=180)

    # Polar overlay
    ax_pol = fig.add_axes([0.04, 0.05, 0.55, 0.90], polar=True,
                          facecolor='#0a0a0a')
    ax_pol.set_theta_zero_location('E')
    ax_pol.set_theta_direction(1)

    h_colors = {
        5: (1.00, 0.66, 0.30),
        6: (1.00, 0.45, 0.30),
        7: (0.85, 0.30, 0.55),
        8: (0.55, 0.30, 0.95),
    }

    angles_rad = np.array([np.arctan2(dy, dx) for dy, dx in DIRECTIONS])

    for h in H_VALUES:
        s_o = results[h]['sums_orig']
        # mirror to 360°
        ang_full = np.concatenate([angles_rad, angles_rad + np.pi])
        s_full = np.concatenate([s_o, s_o])
        order = np.argsort(ang_full)
        ang_full = ang_full[order]
        s_full = s_full[order]
        ang_full = np.concatenate([ang_full, [ang_full[0] + 2 * np.pi]])
        s_full = np.concatenate([s_full, [s_full[0]]])

        log_s = np.log10(s_full + 1e-6)
        col = h_colors[h]
        ax_pol.plot(ang_full, log_s, color=(*col, 0.95), lw=2.0,
                    label=f'h = {h}  (total {s_o.sum():.3f})')
        ax_pol.fill(ang_full, log_s, color=(*col, 0.10))

    # constgauss reference (h = 5; other h are similar)
    s_cg = results[5]['sums_cg']
    ang_full = np.concatenate([angles_rad, angles_rad + np.pi])
    s_full = np.concatenate([s_cg, s_cg])
    order = np.argsort(ang_full)
    ang_full = ang_full[order]
    s_full = s_full[order]
    ang_full = np.concatenate([ang_full, [ang_full[0] + 2 * np.pi]])
    s_full = np.concatenate([s_full, [s_full[0]]])
    log_cg = np.log10(s_full + 1e-6)
    ax_pol.plot(ang_full, log_cg, color=(0.45, 0.78, 1.00, 0.85),
                lw=1.5, ls='--',
                label=f'constgauss (h=5, seed 1729)')

    ax_pol.set_yticks([-3, -2, -1, 0, 1])
    ax_pol.set_yticklabels(
        [r'$10^{-3}$', r'$10^{-2}$', r'$10^{-1}$', r'$10^{0}$', r'$10^{1}$'],
        color=(0.78, 0.82, 0.88, 0.88), fontsize=9,
    )
    ax_pol.set_ylim(-3.5, 1.0)
    ax_pol.set_xticks(np.deg2rad([0, 45, 90, 135, 180, 225, 270, 315]))
    ax_pol.set_xticklabels(['0°', '45°', '90°', '135°', '180°',
                             '225°', '270°', '315°'],
                            color=(0.92, 0.95, 1.00, 0.92), fontsize=11)
    ax_pol.tick_params(colors=(0.78, 0.82, 0.88, 0.78))
    ax_pol.grid(True, color=(0.30, 0.34, 0.38), alpha=0.30, lw=0.5)
    ax_pol.legend(loc='lower center',
                  bbox_to_anchor=(0.5, -0.13),
                  ncol=3, fontsize=9, frameon=False,
                  labelcolor=(0.92, 0.95, 1.00, 1.0))
    ax_pol.set_title(
        '16-angle direct spatial spectrum across h = 5, 6, 7, 8\n'
        r'$\sum|\mathrm{corr}|$ over $L \in \{1, 2, 4\}$  ·  '
        r'log radial scale',
        color=(0.96, 0.97, 1.00, 0.95), fontsize=12, pad=22,
    )

    # ---- scaling panel: total budget vs h ----
    ax_scale = fig.add_axes([0.66, 0.55, 0.31, 0.38],
                            facecolor='#0a0a0a')
    totals = [results[h]['sums_orig'].sum() for h in H_VALUES]
    ax_scale.plot(H_VALUES, totals, 'o-',
                  color=(1.00, 0.66, 0.30, 0.95), lw=2.0, ms=10)
    ax_scale.set_xlabel('h', color=(0.85, 0.88, 0.92, 0.92), fontsize=10)
    ax_scale.set_ylabel(r'total $\sum|\mathrm{corr}|$',
                        color=(0.85, 0.88, 0.92, 0.92), fontsize=10)
    ax_scale.set_xticks(H_VALUES)
    for x, y in zip(H_VALUES, totals):
        ax_scale.annotate(f'{y:.3f}', xy=(x, y),
                          xytext=(0, 8), textcoords='offset points',
                          color=(1.00, 0.84, 0.30, 0.95),
                          fontsize=9, ha='center')
    ax_scale.tick_params(colors=(0.78, 0.82, 0.88, 0.85), labelsize=9)
    for spine in ax_scale.spines.values():
        spine.set_color((0.40, 0.45, 0.50, 0.40))
    ax_scale.grid(True, color=(0.30, 0.34, 0.38), alpha=0.18, lw=0.4)
    ax_scale.set_title(
        'total budget vs rank',
        color=(0.96, 0.97, 1.00, 0.92), fontsize=10, pad=8,
    )

    # ---- L-anomaly panel ----
    ax_lag = fig.add_axes([0.66, 0.05, 0.31, 0.42],
                          facecolor='#0a0a0a')
    for h in H_VALUES:
        c = results[h]['corrs_orig']
        col = h_colors[h]
        ax_lag.plot(LAGS, c[0], 'o-', color=(*col, 0.92), lw=1.6,
                    ms=8, label=f'h={h}, 0°')
        ax_lag.plot(LAGS, c[8], 's--', color=(*col, 0.92), lw=1.6,
                    ms=8)
    ax_lag.axhline(0, color=(0.95, 0.97, 1.00, 0.30), lw=0.7)
    ax_lag.set_xlabel('lag L', color=(0.85, 0.88, 0.92, 0.92), fontsize=10)
    ax_lag.set_ylabel('Pearson corr',
                      color=(0.85, 0.88, 0.92, 0.92), fontsize=10)
    ax_lag.set_xticks(LAGS)
    ax_lag.tick_params(colors=(0.78, 0.82, 0.88, 0.85), labelsize=9)
    for spine in ax_lag.spines.values():
        spine.set_color((0.40, 0.45, 0.50, 0.40))
    ax_lag.grid(True, color=(0.30, 0.34, 0.38), alpha=0.18, lw=0.4)
    ax_lag.legend(loc='upper left', fontsize=8, frameon=False,
                  labelcolor=(0.92, 0.95, 1.00, 1.0), ncol=2)
    ax_lag.set_title(
        'lag profile at 0° (solid) and 90° (dashed) across h',
        color=(0.96, 0.97, 1.00, 0.92), fontsize=10, pad=8,
    )

    out = os.path.join(HERE, 'q_lattice_direct_angular_h_sweep.png')
    plt.savefig(out, facecolor='#0a0a0a', dpi=180,
                bbox_inches='tight', pad_inches=0.15)
    plt.close()
    sz = os.path.getsize(out) / 1024
    print(f'\n-> {os.path.basename(out)}  ({sz:.0f} KB)')


if __name__ == '__main__':
    main()
