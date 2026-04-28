"""
residual_ablation_grid.py — matched-bucket residual ablation
============================================================

Measure which coordinates independently explain corrected ACM-Mangoldt
flow residuals after matching away the obvious confounders.

Input:
    acm_mangoldt.csv from acm_mangoldt_tomography.py

Output:
    residual_ablation_grid.txt

Usage:
    sage -python residual_ablation_grid.py
"""

import csv
import os
from collections import defaultdict
from math import isqrt
from statistics import median


EPS = 1e-12

BLOCK_ORDER = ['smooth', 'family_E', 'uncertified']
WITNESS_ORDER = ['0', '1', '2', '3-5', '6-9', '10+']
TAU_ORDER = ['0-2', '3-4', '5-8', '9-16', '17+']
N_KIND_ORDER = ['prime', 'composite']
AGREE_ORDER = [0, 1]


def is_prime(n):
    if n < 2:
        return False
    for d in range(2, isqrt(n) + 1):
        if n % d == 0:
            return False
    return True


def witness_bucket(count):
    if count <= 0:
        return '0'
    if count == 1:
        return '1'
    if count == 2:
        return '2'
    if count <= 5:
        return '3-5'
    if count <= 9:
        return '6-9'
    return '10+'


def tau_bucket(tau2):
    if tau2 <= 2:
        return '0-2'
    if tau2 <= 4:
        return '3-4'
    if tau2 <= 8:
        return '5-8'
    if tau2 <= 16:
        return '9-16'
    return '17+'


def mean(values):
    return sum(values) / len(values) if values else 0.0


def frac(num, den):
    return num / den if den else 0.0


def sort_key(parts):
    """Stable arithmetic order for bucketed table keys."""
    order_maps = {
        'block': {v: i for i, v in enumerate(BLOCK_ORDER)},
        'witness': {v: i for i, v in enumerate(WITNESS_ORDER)},
        'tau': {v: i for i, v in enumerate(TAU_ORDER)},
        'n_kind': {v: i for i, v in enumerate(N_KIND_ORDER)},
    }
    out = []
    for p in parts:
        if isinstance(p, int):
            out.append((0, p))
        elif p in order_maps['block']:
            out.append((1, order_maps['block'][p]))
        elif p in order_maps['witness']:
            out.append((2, order_maps['witness'][p]))
        elif p in order_maps['tau']:
            out.append((3, order_maps['tau'][p]))
        elif p in order_maps['n_kind']:
            out.append((4, order_maps['n_kind'][p]))
        else:
            out.append((5, str(p)))
    return tuple(out)


def load_rows(path):
    rows = []
    with open(path, newline='') as f:
        for row in csv.DictReader(f):
            out = {
                'n': int(row['n']),
                'm': int(row['m']),
                'height': int(row['height']),
                'block_type': row['block_type'],
                'Lambda': float(row['Lambda']),
                'Out': float(row['Out']),
                'DeltaMertens': float(row['DeltaMertens']),
                'Y': int(row['Y']),
                'cutoff_witness_count': int(row['cutoff_witness_count']),
                'cutoff_tau2': int(row['cutoff_tau2']),
                'cutoff_spf': int(row['cutoff_spf']),
                'cutoff_diag_prime_disagree':
                    int(row['cutoff_diag_prime_disagree']),
                'payload2': int(row['payload2']),
                'payload2_tau2': int(row['payload2_tau2']),
                'payload2_witness_count': int(row['payload2_witness_count']),
                'payload2_diag_prime_disagree':
                    int(row['payload2_diag_prime_disagree']),
                'payload3': int(row['payload3']),
                'payload3_tau2': int(row['payload3_tau2']),
                'payload3_witness_count': int(row['payload3_witness_count']),
                'payload3_diag_prime_disagree':
                    int(row['payload3_diag_prime_disagree']),
            }
            out['rho'] = out['DeltaMertens'] / out['Out']
            out['n_kind'] = 'prime' if is_prime(out['n']) else 'composite'
            out['cutoff_witness_bucket'] = witness_bucket(
                out['cutoff_witness_count'])
            out['cutoff_tau_bucket'] = tau_bucket(out['cutoff_tau2'])
            out['payload2_tau_bucket'] = tau_bucket(out['payload2_tau2'])
            out['payload3_tau_bucket'] = tau_bucket(out['payload3_tau2'])
            rows.append(out)
    return rows


def rho_stats(rows):
    rhos = [r['rho'] for r in rows]
    return {
        'count': len(rows),
        'median': median(rhos) if rhos else 0.0,
        'mean': mean(rhos),
        'neg_frac': frac(sum(1 for v in rhos if v < -EPS), len(rhos)),
        'mean_wc': mean([r['cutoff_witness_count'] for r in rows]),
        'mean_spf': mean([r['cutoff_spf'] for r in rows]),
    }


def lambda_stats(rows):
    count = len(rows)
    pos = sum(1 for r in rows if r['Lambda'] > EPS)
    zero = sum(1 for r in rows if abs(r['Lambda']) <= EPS)
    neg = sum(1 for r in rows if r['Lambda'] < -EPS)
    neg_mass = sum(-r['Lambda'] for r in rows if r['Lambda'] < -EPS)
    abs_mass = sum(abs(r['Lambda']) for r in rows)
    return {
        'count': count,
        'pos_pct': 100.0 * frac(pos, count),
        'zero_pct': 100.0 * frac(zero, count),
        'neg_pct': 100.0 * frac(neg, count),
        'neg_mass_frac': frac(neg_mass, abs_mass),
    }


def grouped(rows, key_fn):
    groups = defaultdict(list)
    for row in rows:
        groups[key_fn(row)].append(row)
    return groups


def write_rho_table(f, title, groups, headers):
    f.write(f'\n=== {title} ===\n\n')
    f.write('  '.join(f'{h:>14}' for h in headers))
    f.write('  ')
    f.write(f'{"count":>7}  {"median rho":>12}  {"mean rho":>12}  '
            f'{"rho<0":>8}\n')
    for key in sorted(groups, key=lambda k: sort_key(k if isinstance(k, tuple)
                                                      else (k,))):
        stats = rho_stats(groups[key])
        parts = key if isinstance(key, tuple) else (key,)
        f.write('  '.join(f'{str(p):>14}' for p in parts))
        f.write('  ')
        f.write(f'{stats["count"]:>7}  {stats["median"]:>+12.4f}  '
                f'{stats["mean"]:>+12.4f}  {stats["neg_frac"]:>8.3f}\n')


def write_lambda_table(f, title, groups, headers):
    f.write(f'\n=== {title} ===\n\n')
    f.write('  '.join(f'{h:>14}' for h in headers))
    f.write('  ')
    f.write(f'{"count":>7}  {"Λ>0 %":>8}  {"Λ=0 %":>8}  '
            f'{"Λ<0 %":>8}  {"neg_mass":>9}\n')
    for key in sorted(groups, key=lambda k: sort_key(k if isinstance(k, tuple)
                                                      else (k,))):
        stats = lambda_stats(groups[key])
        parts = key if isinstance(key, tuple) else (key,)
        f.write('  '.join(f'{str(p):>14}' for p in parts))
        f.write('  ')
        f.write(f'{stats["count"]:>7}  {stats["pos_pct"]:>8.2f}  '
                f'{stats["zero_pct"]:>8.2f}  {stats["neg_pct"]:>8.2f}  '
                f'{stats["neg_mass_frac"]:>9.4f}\n')


def write_block_match_table(f, rows):
    f.write('\n=== Q2: smooth advantage after matching height=2 and '
            'cutoff witness bucket ===\n\n')
    f.write(f'{"Y_wit":>8}  {"smooth n":>8}  {"smooth mean":>12}  '
            f'{"uncert n":>8}  {"uncert mean":>12}  '
            f'{"smooth-uncert":>14}\n')
    groups = grouped(rows, lambda r: (r['cutoff_witness_bucket'],
                                      r['block_type']))
    for bucket in WITNESS_ORDER:
        smooth = groups.get((bucket, 'smooth'), [])
        uncert = groups.get((bucket, 'uncertified'), [])
        if not smooth and not uncert:
            continue
        s_mean = rho_stats(smooth)['mean'] if smooth else 0.0
        u_mean = rho_stats(uncert)['mean'] if uncert else 0.0
        diff = s_mean - u_mean if smooth and uncert else 0.0
        f.write(f'{bucket:>8}  {len(smooth):>8}  {s_mean:>+12.4f}  '
                f'{len(uncert):>8}  {u_mean:>+12.4f}  '
                f'{diff:>+14.4f}\n')
    f.write('\nPositive smooth-uncert means smooth is less negative in '
            'the matched bucket.\n')


def write_disagreement_table(f, rows):
    f.write('\n=== Q4: diag/prime disagreement inside block type and '
            'cutoff witness bucket ===\n\n')
    f.write(f'{"block_type":>14}  {"Y_wit":>8}  {"dp":>8}  '
            f'{"count":>7}  {"median rho":>12}  {"mean rho":>12}  '
            f'{"mean wc":>8}  {"mean spf":>9}\n')
    groups = grouped(rows, lambda r: (r['block_type'],
                                      r['cutoff_witness_bucket'],
                                      r['cutoff_diag_prime_disagree']))
    for block in BLOCK_ORDER:
        for bucket in WITNESS_ORDER:
            for dp in AGREE_ORDER:
                chunk = groups.get((block, bucket, dp), [])
                if not chunk:
                    continue
                stats = rho_stats(chunk)
                label = 'disagree' if dp else 'agree'
                f.write(f'{block:>14}  {bucket:>8}  {label:>8}  '
                        f'{stats["count"]:>7}  '
                        f'{stats["median"]:>+12.4f}  '
                        f'{stats["mean"]:>+12.4f}  '
                        f'{stats["mean_wc"]:>8.2f}  '
                        f'{stats["mean_spf"]:>9.2f}\n')


def write_joint_table(f, rows):
    f.write('\n=== Q5: height=2 joint read, payload tau2 versus cutoff '
            'witness richness ===\n\n')
    f.write(f'{"p2_tau":>8}  {"Y_wit":>8}  {"count":>7}  '
            f'{"mean rho":>12}  {"rho<0":>8}  {"Λ<0 %":>8}  '
            f'{"neg_mass":>9}\n')
    groups = grouped(rows, lambda r: (r['payload2_tau_bucket'],
                                      r['cutoff_witness_bucket']))
    for tau in TAU_ORDER:
        for bucket in WITNESS_ORDER:
            chunk = groups.get((tau, bucket), [])
            if not chunk:
                continue
            rstats = rho_stats(chunk)
            lstats = lambda_stats(chunk)
            f.write(f'{tau:>8}  {bucket:>8}  {len(chunk):>7}  '
                    f'{rstats["mean"]:>+12.4f}  '
                    f'{rstats["neg_frac"]:>8.3f}  '
                    f'{lstats["neg_pct"]:>8.2f}  '
                    f'{lstats["neg_mass_frac"]:>9.4f}\n')


def write_summary(path, rows, source_path):
    h2 = [r for r in rows if r['height'] == 2]

    with open(path, 'w') as f:
        f.write('ACM-Mangoldt residual ablation grid\n')
        f.write('===================================\n\n')
        f.write(f'source: {os.path.basename(source_path)}\n')
        f.write(f'rows: {len(rows)}\n')
        f.write('target: rho = DeltaMertens / Out\n')
        f.write('matching style: bucketed arithmetic coordinates, not a '
                'global regression\n')

        q1 = grouped(h2, lambda r: (r['block_type'],
                                    r['cutoff_witness_bucket']))
        write_rho_table(
            f,
            'Q1: height=2 residual by block type and cutoff witness bucket',
            q1,
            ['block_type', 'Y_wit'])

        write_block_match_table(f, h2)

        q3 = grouped(h2, lambda r: (r['n_kind'],
                                    r['payload2_tau_bucket']))
        write_lambda_table(
            f,
            'Q3: height=2 Lambda sign by n kind and payload2 tau2',
            q3,
            ['n_kind', 'p2_tau'])

        write_disagreement_table(f, rows)
        write_joint_table(f, h2)


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(out_dir, 'acm_mangoldt.csv')
    out_path = os.path.join(out_dir, 'residual_ablation_grid.txt')
    if not os.path.exists(source_path):
        raise SystemExit('missing acm_mangoldt.csv; run '
                         'sage -python acm_mangoldt_tomography.py first')

    rows = load_rows(source_path)
    write_summary(out_path, rows, source_path)
    print(f'wrote {out_path}')


if __name__ == '__main__':
    main()
