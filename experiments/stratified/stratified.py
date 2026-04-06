"""
stratified.py — Stratified sampling: BIDDER vs randomized controls.

Estimate integrals of known functions by averaging f(x_i) over samples
drawn from several sources:

  1. BIDDER (ensemble over many keys)
  2. numpy uniform PRNG
  3. Repeated fixed strata with the same b-1 alphabet as BIDDER
  4. Midpoints of n equal bins (the classical deterministic baseline)
  5. Jittered one-per-bin sampling (1D Latin-hypercube equivalent)

The comparison is still 1D, but it is now fairer:
  - BIDDER is shown as a key ensemble, not a single realization.
  - The fixed-strata baseline matches BIDDER's alphabet size.
  - Randomized stratified sampling is included alongside raw PRNG.
"""

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'generator'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'core'))

import numpy as np
import matplotlib.pyplot as plt
from bidder import Bidder


def f1(x): return x
def f2(x): return x**2
def f3(x): return np.sin(np.pi * x)
def f4(x): return np.exp(x)
def f5(x): return 1.0 / (1.0 + 25.0 * x**2)


functions = [
    (f1, 0.5,                    'f(x) = x'),
    (f2, 1.0 / 3.0,              'f(x) = x²'),
    (f3, 2.0 / np.pi,            'f(x) = sin(πx)'),
    (f4, np.e - 1.0,             'f(x) = eˣ'),
    (f5, np.arctan(5.0) / 5.0,   'f(x) = 1/(1+25x²)'),
]


def bidder_period(base, digit_class):
    return (base - 1) * (base ** (digit_class - 1))


def bidder_stream(base, digit_class, key):
    gen = Bidder(base=base, digit_class=digit_class, key=key)
    period = gen.period
    return np.fromiter(
        ((gen.next() - 0.5) / (base - 1) for _ in range(period)),
        dtype=np.float64,
        count=period,
    )


def numpy_stream(n, seed):
    return np.random.default_rng(seed).uniform(0.0, 1.0, size=n)


def fixed_strata_stream(base, n):
    strata = (np.arange(base - 1, dtype=np.float64) + 0.5) / (base - 1)
    reps = (n + len(strata) - 1) // len(strata)
    return np.tile(strata, reps)[:n]


def midpoint_stream(n):
    return (np.arange(n, dtype=np.float64) + 0.5) / n


def lhs_jittered_stream(n, seed):
    rng = np.random.default_rng(seed)
    return (np.arange(n, dtype=np.float64) + rng.random(n)) / n


def summarize_errors(estimates, true_val):
    errors = np.abs(estimates - true_val)
    return (
        np.median(errors),
        np.percentile(errors, 10),
        np.percentile(errors, 90),
    )


base = 10
digit_classes = [2, 3, 4]
periods = {dc: bidder_period(base, dc) for dc in digit_classes}
boundaries = [periods[2], periods[3], periods[4]]

sizes = sorted(set(
    list(range(10, 200, 5)) +
    list(range(200, 1000, 20)) +
    list(range(1000, periods[4] + 1, 100)) +
    boundaries
))

max_n = max(sizes)
bidder_keys = [
    hashlib.sha256(f'stratified-key-{i}'.encode('ascii')).digest()
    for i in range(24)
]
numpy_trials = 64
lhs_trials = 64


print(f"Testing {len(sizes)} sample sizes, {len(functions)} functions...")
print(f"  BIDDER keys: {len(bidder_keys)}")
print(f"  numpy trials: {numpy_trials}")
print(f"  jittered-strata trials: {lhs_trials}")

print("Precomputing sample streams...")
bidder_cache = {
    dc: np.vstack([bidder_stream(base, dc, key) for key in bidder_keys])
    for dc in digit_classes
}
numpy_cache = np.vstack([
    numpy_stream(max_n, 10_000 + trial)
    for trial in range(numpy_trials)
])
lhs_cache = np.vstack([
    lhs_jittered_stream(max_n, 20_000 + trial)
    for trial in range(lhs_trials)
])
fixed_cache = {n: fixed_strata_stream(base, n) for n in sizes}
midpoint_cache = {n: midpoint_stream(n) for n in sizes}


def bidder_prefix_matrix(n):
    if n <= periods[2]:
        dc = 2
    elif n <= periods[3]:
        dc = 3
    else:
        dc = 4
    return bidder_cache[dc][:, :n]


results = {}

for func, true_val, name in functions:
    print(f"  {name}...")
    bidder_summary = []
    numpy_summary = []
    lhs_summary = []
    fixed_errors = []
    midpoint_errors = []

    for n in sizes:
        bidder_estimates = np.mean(func(bidder_prefix_matrix(n)), axis=1)
        numpy_estimates = np.mean(func(numpy_cache[:, :n]), axis=1)
        lhs_estimates = np.mean(func(lhs_cache[:, :n]), axis=1)

        bidder_summary.append((n,) + summarize_errors(bidder_estimates, true_val))
        numpy_summary.append((n,) + summarize_errors(numpy_estimates, true_val))
        lhs_summary.append((n,) + summarize_errors(lhs_estimates, true_val))

        fixed_estimate = np.mean(func(fixed_cache[n]))
        midpoint_estimate = np.mean(func(midpoint_cache[n]))
        fixed_errors.append((n, abs(fixed_estimate - true_val)))
        midpoint_errors.append((n, abs(midpoint_estimate - true_val)))

    results[(name, 'bidder')] = bidder_summary
    results[(name, 'numpy')] = numpy_summary
    results[(name, 'lhs')] = lhs_summary
    results[(name, 'fixed')] = fixed_errors
    results[(name, 'midpoint')] = midpoint_errors


print("Plotting...")

fig, axes = plt.subplots(2, 3, figsize=(24, 14))
fig.patch.set_facecolor('#0a0a0a')


def plot_ensemble(ax, data, color, label):
    ns = [row[0] for row in data]
    med = [max(row[1], 1e-16) for row in data]
    p10 = [max(row[2], 1e-16) for row in data]
    p90 = [max(row[3], 1e-16) for row in data]
    ax.fill_between(ns, p10, p90, color=color, alpha=0.14)
    ax.loglog(ns, med, color=color, linewidth=1.2, label=label)


for fi, (_, _, name) in enumerate(functions):
    ax = axes[fi // 3, fi % 3]
    ax.set_facecolor('#0a0a0a')

    plot_ensemble(ax, results[(name, 'bidder')], '#ffcc5c',
                  f'BIDDER (median, {len(bidder_keys)} keys)')
    plot_ensemble(ax, results[(name, 'numpy')], '#6ec6ff',
                  f'numpy (median, {numpy_trials} trials)')
    plot_ensemble(ax, results[(name, 'lhs')], '#88d8b0',
                  f'jittered strata (median, {lhs_trials} trials)')

    fixed_data = results[(name, 'fixed')]
    ax.loglog(
        [row[0] for row in fixed_data],
        [max(row[1], 1e-16) for row in fixed_data],
        color='#ff6f61',
        linewidth=1.0,
        label=f'fixed {base - 1}-strata midpoints',
    )

    midpoint_data = results[(name, 'midpoint')]
    ax.loglog(
        [row[0] for row in midpoint_data],
        [max(row[1], 1e-16) for row in midpoint_data],
        color='white',
        linewidth=0.8,
        alpha=0.5,
        linestyle='--',
        label='midpoints of n bins',
    )

    for boundary in boundaries:
        if boundary <= max_n:
            ax.axvline(x=boundary, color='white', linewidth=0.3, alpha=0.25)

    ns_ref = np.array(sizes, dtype=np.float64)
    ax.loglog(ns_ref, 0.3 / np.sqrt(ns_ref), color='white',
              linewidth=0.5, linestyle=':', alpha=0.3, label='1/√N')

    ax.set_title(name, color='white', fontsize=13, pad=10)
    ax.tick_params(colors='white')
    ax.set_ylim(1e-8, 1)
    for spine in ax.spines.values():
        spine.set_color('#333')

axes[0, 0].set_ylabel('|estimate - true|', color='white', fontsize=11)
axes[1, 0].set_ylabel('|estimate - true|', color='white', fontsize=11)
axes[1, 0].set_xlabel('N samples', color='white', fontsize=11)
axes[1, 1].set_xlabel('N samples', color='white', fontsize=11)
axes[0, 0].legend(fontsize=8, framealpha=0.3, labelcolor='white',
                  facecolor='#1a1a1a', loc='lower left')

axes[1, 2].set_visible(False)

plt.subplots_adjust(wspace=0.12, hspace=0.2)
plt.savefig('stratified.png', dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
print("-> stratified.png")
