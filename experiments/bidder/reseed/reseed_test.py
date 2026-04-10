"""
reseed_test.py — Can we rekey at the period boundary without issue?

Questions:
  1. Does each rekeyed period remain exactly uniform?
  2. Is there a measurable seam at the boundary between periods?
  3. If there is one, how large is it relative to a permutation null?

This version sweeps several (base, digit_class) settings and replaces
the old hand-rolled chi-squared cutoff with a permutation test on the
boundary-vs-interior bigram distribution.
"""

import hashlib
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'generator'))

import numpy as np
import matplotlib.pyplot as plt
from coupler import Bidder


def rekey(old_key, period_num):
    return hashlib.sha256(old_key + struct.pack('<Q', period_num)).digest()


def generate_rekeyed_stream(base, digit_class, seed_key, n_periods):
    key = seed_key
    periods = []

    for period_num in range(n_periods):
        gen = Bidder(base=base, digit_class=digit_class, key=key)
        periods.append(np.fromiter((gen.next() for _ in range(gen.period)),
                                   dtype=np.int16, count=gen.period))
        key = rekey(key, period_num)

    return np.concatenate(periods)


def per_period_uniformity(stream, base, period):
    expected = period // (base - 1)
    blocks = stream.reshape(-1, period)
    exact = True

    for counts in (np.bincount(block, minlength=base) for block in blocks):
        if not np.all(counts[1:base] == expected):
            exact = False
            break

    return exact, expected


def bigram_ids(stream, base):
    alphabet = base - 1
    return (stream[:-1] - 1) * alphabet + (stream[1:] - 1)


def total_variation(boundary_counts, interior_counts):
    boundary = boundary_counts / np.sum(boundary_counts)
    interior = interior_counts / np.sum(interior_counts)
    return 0.5 * np.abs(boundary - interior).sum()


def seam_permutation_test(ids, boundary_mask, alphabet_size, n_perm, seed):
    boundary_ids = ids[boundary_mask]
    interior_ids = ids[~boundary_mask]

    boundary_counts = np.bincount(boundary_ids, minlength=alphabet_size)
    interior_counts = np.bincount(interior_ids, minlength=alphabet_size)
    observed = total_variation(boundary_counts, interior_counts)

    rng = np.random.default_rng(seed)
    total_counts = np.bincount(ids, minlength=alphabet_size)
    n_total = len(ids)
    n_boundary = np.sum(boundary_mask)
    null_stats = np.empty(n_perm, dtype=np.float64)

    for trial in range(n_perm):
        chosen = rng.choice(n_total, size=n_boundary, replace=False)
        chosen_counts = np.bincount(ids[chosen], minlength=alphabet_size)
        rest_counts = total_counts - chosen_counts
        null_stats[trial] = total_variation(chosen_counts, rest_counts)

    p_value = (1 + np.sum(null_stats >= observed)) / (n_perm + 1)
    z_score = (observed - null_stats.mean()) / max(null_stats.std(), 1e-12)

    return {
        'observed_tv': observed,
        'null_stats': null_stats,
        'p_value': p_value,
        'z_score': z_score,
        'boundary_count': int(n_boundary),
        'interior_count': int(np.sum(~boundary_mask)),
    }


def evaluate_setting(base, digit_class, n_periods, seed_key, n_perm):
    probe = Bidder(base=base, digit_class=digit_class, key=seed_key)
    period = probe.period
    stream = generate_rekeyed_stream(base, digit_class, seed_key, n_periods)
    exact, expected = per_period_uniformity(stream, base, period)

    ids = bigram_ids(stream, base)
    boundary_mask = np.zeros(len(ids), dtype=bool)
    boundary_mask[np.arange(1, n_periods) * period - 1] = True
    seam = seam_permutation_test(
        ids, boundary_mask, (base - 1) ** 2, n_perm=n_perm,
        seed=base * 10_000 + digit_class,
    )

    total_counts = np.bincount(stream, minlength=base)[1:base]
    exact_total = np.all(total_counts == expected * n_periods)

    return {
        'base': base,
        'digit_class': digit_class,
        'period': period,
        'n_periods': n_periods,
        'stream': stream,
        'per_period_exact': exact,
        'total_exact': exact_total,
        'expected_per_digit': expected,
        **seam,
    }


print("=== Rekey sweep ===\n")

settings = [
    (10, 2, 400),
    (10, 3, 250),
    (10, 4, 120),
    (16, 2, 300),
    (16, 3, 140),
]
n_perm = 800
seed_key = b'reseed test'

results = []
for base, digit_class, n_periods in settings:
    result = evaluate_setting(base, digit_class, n_periods, seed_key, n_perm)
    results.append(result)
    print(
        f"base={base:>2}, d={digit_class}, period={result['period']}, "
        f"periods={n_periods}, exact_per_period={result['per_period_exact']}, "
        f"exact_total={result['total_exact']}"
    )
    print(
        f"  seam TV={result['observed_tv']:.5f}, "
        f"null median={np.median(result['null_stats']):.5f}, "
        f"p={result['p_value']:.4f}, z={result['z_score']:.2f}, "
        f"boundary bigrams={result['boundary_count']}"
    )


print("\n=== Canonical prefix diversity ===\n")

canonical = next(
    result for result in results
    if result['base'] == 10 and result['digit_class'] == 3
)
period = canonical['period']
blocks = canonical['stream'].reshape(canonical['n_periods'], period)
prefixes = [tuple(block[:20].tolist()) for block in blocks[:5]]
all_different = len(set(prefixes)) == len(prefixes)

for idx, prefix in enumerate(prefixes):
    print(f"  Period {idx}: {list(prefix)}")
print(f"  First five prefixes all different: {all_different}")


print("\nPlotting...")

fig, axes = plt.subplots(2, 1, figsize=(18, 11),
                         gridspec_kw={'height_ratios': [2.2, 1.2]})
fig.patch.set_facecolor('#0a0a0a')

# Top panel: running deviation for the canonical setting
ax = axes[0]
ax.set_facecolor('#0a0a0a')
target = 1.0 / (canonical['base'] - 1)
counts_running = np.zeros(canonical['base'], dtype=np.int64)
deviation = np.empty(len(canonical['stream']), dtype=np.float64)

for idx, digit in enumerate(canonical['stream']):
    counts_running[digit] += 1
    fracs = counts_running[1:canonical['base']] / (idx + 1)
    deviation[idx] = np.max(np.abs(fracs - target))

ns = np.arange(1, len(canonical['stream']) + 1)
ax.plot(ns, deviation, linewidth=0.35, color='#ffcc5c', alpha=0.9)

for period_num in range(1, canonical['n_periods']):
    ax.axvline(x=period_num * canonical['period'], color='white',
               linewidth=0.2, alpha=0.18)

ax.set_ylabel('max deviation', color='white', fontsize=11)
ax.set_title(
    f"Running deviation across {canonical['n_periods']} rekeyed periods "
    f"(base {canonical['base']}, d={canonical['digit_class']})",
    color='white', fontsize=13, pad=10
)
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('#333')

# Bottom panel: seam statistic across the sweep
ax = axes[1]
ax.set_facecolor('#0a0a0a')

labels = [f"b={r['base']}, d={r['digit_class']}" for r in results]
x = np.arange(len(results))
observed = np.array([r['observed_tv'] for r in results])
null_med = np.array([np.median(r['null_stats']) for r in results])
null_p10 = np.array([np.percentile(r['null_stats'], 10) for r in results])
null_p90 = np.array([np.percentile(r['null_stats'], 90) for r in results])

ax.fill_between(x, null_p10, null_p90, color='#6ec6ff', alpha=0.18,
                label='permutation null (10th-90th pct)')
ax.plot(x, null_med, color='#6ec6ff', linewidth=1.2, label='null median')
ax.scatter(x, observed, color='#ff6f61', s=45, zorder=3, label='observed seam TV')

for idx, result in enumerate(results):
    y = max(observed[idx], null_p90[idx])
    ax.text(x[idx], y * 1.05 + 1e-4, f"p={result['p_value']:.3f}",
            color='white', fontsize=8, ha='center')

ax.set_xticks(x)
ax.set_xticklabels(labels, color='white')
ax.set_ylabel('total variation', color='white', fontsize=11)
ax.set_title('Boundary-vs-interior seam test across settings',
             color='white', fontsize=12, pad=8)
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('#333')
ax.legend(fontsize=9, framealpha=0.3, labelcolor='white',
          facecolor='#1a1a1a', loc='upper right')

plt.tight_layout()
plt.savefig('reseed_test.png', dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
print("-> reseed_test.png")
