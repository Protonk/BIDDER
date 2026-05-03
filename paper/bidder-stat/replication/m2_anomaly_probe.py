"""
m2_anomaly_probe.py — Investigation of the P=1000 sub-1.0 anomaly.

The baseline panel from m2_fpc_gap.py reports FPC realisation ratios
for sin(πx) at P ∈ {200, 500, 1000, 2000, 5000, 10000} that grow
monotonically with P at fixed N/P — except at P=1000, where ratios
drop to 0.10–0.21. This script probes the anomaly along two axes:

  (P-sweep)     P ∈ {990, 995, 999, 1000, 1001, 1005, 1010} on sin(πx).
                Discriminates: is P=1000 a point anomaly (H1: integrand-
                specific symmetry), or does it persist across nearby
                periods (H2: P-specific feature)?

  (Integrand sweep) f ∈ {sin(πx), cos(πx), x, x², step} at P=1000.
                Discriminates H1: does the anomaly disappear under
                non-sin integrands?

  (Structure sweep) P ∈ {999, 1000, 1001, 1024} on sin(πx) — the
                same scale, sharply different factorisations:
                999=3³·37, 1000=2³·5³, 1001=7·11·13, 1024=2¹⁰.
                Discriminates whether the anomaly is tied to a
                particular factorisation/2-adic structure.

All cells: 5000 keys (vs baseline's 2000), giving relative SE on the
variance ratio of √(2/5000) ≈ 0.020 — small enough to distinguish
ratio ≈ 0.15 from ratio ≈ 1.5 by ~70 standard errors.
"""

import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)

import bidder_c_native as bidder

N_KEYS = 5000
RATIOS = [0.10, 0.25, 0.50, 0.75, 0.90]
KEY_PREFIX = b'M2-anomaly-'


# -- Integrands ---------------------------------------------------------

def f_sin(x):       return math.sin(math.pi * x)
def f_cos(x):       return math.cos(math.pi * x)
def f_lin(x):       return x
def f_quad(x):      return x * x
def f_step(x):      return 1.0 if x >= 0.5 else 0.0

INTEGRANDS = {
    'sin(pi*x)':  f_sin,
    'cos(pi*x)':  f_cos,
    'x':          f_lin,
    'x^2':        f_quad,
    'step':       f_step,
}


# -- Helpers ------------------------------------------------------------

def population_stats(P, f):
    vals = [f(k / P) for k in range(P)]
    R = sum(vals) / P
    sigma2 = sum((v - R) ** 2 for v in vals) / P
    return R, sigma2


def fpc_var(N, P, sigma2):
    if N >= P:
        return 0.0
    return sigma2 / N * (P - N) / (P - 1)


def measure_cell(P, N, R, n_keys, f, key_tag):
    """Return sample variance of the prefix mean about R, over n_keys
    keyed BIDDER permutations of [0, P)."""
    sumsq = 0.0
    for k in range(n_keys):
        key = KEY_PREFIX + key_tag + b'-' + k.to_bytes(8, 'little')
        block = bidder.cipher(P, key)
        s = 0.0
        for i in range(N):
            s += f(block.at(i) / P)
        d = s / N - R
        sumsq += d * d
    return sumsq / n_keys


def sweep(P_list, f_name, key_tag, label):
    """Run a P-sweep on a single integrand."""
    f = INTEGRANDS[f_name]
    print(f'\n=== {label} (f = {f_name}, n_keys = {N_KEYS}) ===\n')
    pop = {P: population_stats(P, f) for P in P_list}
    grid = {}
    t0 = time.perf_counter()
    for P in P_list:
        R, sigma2 = pop[P]
        for ratio in RATIOS:
            N = max(1, int(round(ratio * P)))
            cell_t0 = time.perf_counter()
            measured = measure_cell(P, N, R, N_KEYS, f, key_tag)
            ideal = fpc_var(N, P, sigma2)
            r = measured / ideal if ideal > 0 else float('nan')
            grid[(P, N)] = {
                'measured': measured, 'ideal': ideal, 'ratio': r,
                'time': time.perf_counter() - cell_t0,
            }
            print(f'  P={P:>5}  N={N:>5}  ratio={r:.3f}  '
                  f'(meas={measured:.3e}, ideal={ideal:.3e}, '
                  f'{grid[(P, N)]["time"]:.1f}s)')
    print(f'  -- {time.perf_counter() - t0:.1f}s')
    return grid


def integrand_sweep(P, key_tag, label):
    """Run all integrands at a single P."""
    print(f'\n=== {label} (P = {P}, n_keys = {N_KEYS}) ===\n')
    grid = {}
    t0 = time.perf_counter()
    for f_name, f in INTEGRANDS.items():
        R, sigma2 = population_stats(P, f)
        if sigma2 == 0.0:
            # Degenerate population (constant integrand on grid).
            for ratio in RATIOS:
                N = max(1, int(round(ratio * P)))
                grid[(f_name, N)] = {'ratio': float('nan'),
                                     'measured': 0.0, 'ideal': 0.0,
                                     'time': 0.0}
                print(f'  f={f_name:>10}  N={N:>5}  ratio=NaN (sigma2=0)')
            continue
        for ratio in RATIOS:
            N = max(1, int(round(ratio * P)))
            cell_t0 = time.perf_counter()
            tag_int = key_tag + b'-' + f_name.encode()
            measured = measure_cell(P, N, R, N_KEYS, f, tag_int)
            ideal = fpc_var(N, P, sigma2)
            r = measured / ideal if ideal > 0 else float('nan')
            grid[(f_name, N)] = {
                'measured': measured, 'ideal': ideal, 'ratio': r,
                'time': time.perf_counter() - cell_t0,
            }
            print(f'  f={f_name:>10}  N={N:>5}  ratio={r:.3f}  '
                  f'(meas={measured:.3e}, ideal={ideal:.3e}, '
                  f'{grid[(f_name, N)]["time"]:.1f}s)')
    print(f'  -- {time.perf_counter() - t0:.1f}s')
    return grid


# -- Main ---------------------------------------------------------------

def main():
    overall_t0 = time.perf_counter()

    # Sweep 1: neighbour P on sin(pi*x).
    P_NEIGHBOURS = [990, 995, 999, 1000, 1001, 1005, 1010]
    g_neigh = sweep(P_NEIGHBOURS, 'sin(pi*x)', b'neigh',
                    'Sweep 1: neighbour P on sin(pi*x)')

    # Sweep 2: integrand at P=1000.
    g_integ = integrand_sweep(1000, b'integ',
                              'Sweep 2: integrands at P=1000')

    # Sweep 3: structure (factorisation) on sin(pi*x).
    P_STRUCTURE = [999, 1000, 1001, 1024]
    g_struct = sweep(P_STRUCTURE, 'sin(pi*x)', b'struct',
                     'Sweep 3: factorisation structure on sin(pi*x)')

    # Sweep 4: re-measure baseline P=1000 sin(pi*x) at 5000 keys
    # using the *same* key prefix as the original baseline. If this
    # comes out close to the baseline 2000-key numbers, H3 (measurement
    # artifact) is confirmed dead.
    print(f'\n=== Sweep 4: P=1000 sin(pi*x) at 5000 keys, baseline keys ===\n')
    f = INTEGRANDS['sin(pi*x)']
    R, sigma2 = population_stats(1000, f)
    g_h3 = {}
    for ratio in RATIOS:
        N = max(1, int(round(ratio * 1000)))
        # Use the original key naming so the first 2000 keys exactly
        # reproduce the baseline.
        sumsq = 0.0
        cell_t0 = time.perf_counter()
        for k in range(N_KEYS):
            key = b'M2-key-' + k.to_bytes(8, 'little')
            block = bidder.cipher(1000, key)
            s = 0.0
            for i in range(N):
                s += f(block.at(i) / 1000)
            d = s / N - R
            sumsq += d * d
        measured = sumsq / N_KEYS
        ideal = fpc_var(N, 1000, sigma2)
        r = measured / ideal if ideal > 0 else float('nan')
        g_h3[N] = {'measured': measured, 'ideal': ideal, 'ratio': r,
                   'time': time.perf_counter() - cell_t0}
        print(f'  P=1000  N={N:>5}  ratio={r:.3f}  '
              f'(meas={measured:.3e}, ideal={ideal:.3e}, '
              f'{g_h3[N]["time"]:.1f}s)')

    print(f'\n\n=== Overall: {time.perf_counter() - overall_t0:.1f}s ===\n')

    # -- Write markdown -----------------------------------------------

    md_path = os.path.join(HERE, 'm2_anomaly_results.md')
    with open(md_path, 'w') as md:
        md.write('# M2 Anomaly Probe — P=1000 sub-1.0 investigation\n\n')
        md.write(f'Generated by `m2_anomaly_probe.py`. n_keys = '
                 f'{N_KEYS} per cell. Relative Monte-Carlo SE on the '
                 f'variance ratio is sqrt(2/n_keys) ≈ '
                 f'{math.sqrt(2/N_KEYS):.3f}.\n\n')

        md.write('## Sweep 1: neighbour P on sin(pi*x)\n\n')
        md.write('| P \\\\ N/P | ' + ' | '.join(
            f'{int(r*100)}%' for r in RATIOS) + ' |\n')
        md.write('|---' * (1 + len(RATIOS)) + '|\n')
        for P in P_NEIGHBOURS:
            row = [f'{P}']
            for ratio in RATIOS:
                N = max(1, int(round(ratio * P)))
                cell = g_neigh[(P, N)]
                row.append(f'{cell["ratio"]:.3f}')
            md.write('| ' + ' | '.join(row) + ' |\n')
        md.write('\n')

        md.write('## Sweep 2: integrands at P=1000\n\n')
        md.write('| f \\\\ N/P | ' + ' | '.join(
            f'{int(r*100)}%' for r in RATIOS) + ' |\n')
        md.write('|---' * (1 + len(RATIOS)) + '|\n')
        for f_name in INTEGRANDS:
            row = [f_name]
            for ratio in RATIOS:
                N = max(1, int(round(ratio * 1000)))
                cell = g_integ[(f_name, N)]
                if math.isnan(cell['ratio']):
                    row.append('NaN')
                else:
                    row.append(f'{cell["ratio"]:.3f}')
            md.write('| ' + ' | '.join(row) + ' |\n')
        md.write('\n')

        md.write('## Sweep 3: factorisation structure on sin(pi*x)\n\n')
        md.write('| P \\\\ N/P | ' + ' | '.join(
            f'{int(r*100)}%' for r in RATIOS) + ' |\n')
        md.write('|---' * (1 + len(RATIOS)) + '|\n')
        for P in P_STRUCTURE:
            row = [f'{P}']
            for ratio in RATIOS:
                N = max(1, int(round(ratio * P)))
                cell = g_struct[(P, N)]
                row.append(f'{cell["ratio"]:.3f}')
            md.write('| ' + ' | '.join(row) + ' |\n')
        md.write('\n')

        md.write('## Sweep 4: P=1000 sin(pi*x) at 5000 keys '
                 '(baseline key prefix)\n\n')
        md.write('| N | N/P | measured Var | ideal FPC Var | ratio |\n')
        md.write('|---|---|---|---|---|\n')
        for ratio in RATIOS:
            N = max(1, int(round(ratio * 1000)))
            cell = g_h3[N]
            md.write(f'| {N} | {ratio:.2f} | {cell["measured"]:.3e} | '
                     f'{cell["ideal"]:.3e} | {cell["ratio"]:.3f} |\n')
        md.write('\n')

    print(f'Wrote {md_path}')


if __name__ == '__main__':
    main()
