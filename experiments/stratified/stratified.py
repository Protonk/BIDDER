"""
stratified.py — Stratified sampling: HCH vs numpy vs Sobol-like.

Estimate integrals of known functions by averaging f(x_i) over samples
drawn from three sources:

  1. HCH generator (exact stratum coverage at block boundaries)
  2. numpy PRNG (random sampling)
  3. Systematic stratification (divide [0,1] into N equal bins, sample
     one point per bin — the classical method)

The HCH generator in base b assigns each sample to one of b-1 strata
{1, ..., b-1}. At a block boundary, each stratum has been visited
exactly the same number of times — free stratification. At non-boundary
counts, the coverage is deterministically uneven (the sawtooth).

We track the estimation error |estimate - true| as a function of N for
all three methods, over several test functions with known integrals.

Test functions on [0, 1]:
  f1(x) = x           integral = 0.5
  f2(x) = x^2         integral = 1/3
  f3(x) = sin(pi*x)   integral = 2/pi
  f4(x) = exp(x)      integral = e - 1
  f5(x) = 1/(1+25x^2) integral = atan(5)/5  (Runge-like, peaked)
"""

import sys
sys.path.insert(0, '../../generator')
sys.path.insert(0, '../..')

import numpy as np
import matplotlib.pyplot as plt
from hch import HCH


# --- Test functions ---

def f1(x): return x
def f2(x): return x**2
def f3(x): return np.sin(np.pi * x)
def f4(x): return np.exp(x)
def f5(x): return 1.0 / (1.0 + 25.0 * x**2)

functions = [
    (f1, 0.5,                    'f(x) = x'),
    (f2, 1.0/3.0,                'f(x) = x²'),
    (f3, 2.0/np.pi,              'f(x) = sin(πx)'),
    (f4, np.e - 1.0,             'f(x) = eˣ'),
    (f5, np.arctan(5.0) / 5.0,   'f(x) = 1/(1+25x²)'),
]


# --- Sampling methods ---

def hch_samples(base, digit_class, key, n):
    """
    Generate n samples in [0, 1) from the HCH generator.

    Each output digit d in {1, ..., base-1} maps to the interval
    [(d-1)/(b-1), d/(b-1)). Within each stratum, we place the
    sample at the midpoint (deterministic stratification).
    """
    gen = HCH(base=base, digit_class=digit_class, key=key)
    raw = [gen.next() for _ in range(n)]
    b = base
    # Map digit d to midpoint of stratum [(d-1)/(b-1), d/(b-1))
    return np.array([(d - 0.5) / (b - 1) for d in raw])


def numpy_samples(n, seed):
    """n uniform random samples in [0, 1)."""
    return np.random.default_rng(seed).uniform(0, 1, size=n)


def systematic_samples(n):
    """
    Classical stratified: divide [0,1] into n equal bins,
    take the midpoint of each.
    """
    return (np.arange(n) + 0.5) / n


# --- Run estimation ---

base = 10
dc = 4  # period = 9000
period = 9000

# Sample sizes to test: include block boundaries and non-boundaries
# Block boundaries for base 10: 9, 90, 900, 9000
sizes = sorted(set(
    list(range(10, 200, 5)) +
    list(range(200, 1000, 20)) +
    list(range(1000, 9001, 100)) +
    [9, 90, 900, 9000]  # exact boundaries
))

print(f"Testing {len(sizes)} sample sizes, {len(functions)} functions...")

results = {}  # (func_name, method) -> list of (n, error)

for fi, (func, true_val, name) in enumerate(functions):
    print(f"  {name}...")
    for method in ['hch', 'numpy', 'systematic']:
        errors = []
        for n in sizes:
            if method == 'hch':
                # Pick digit_class so period >= n
                if n <= 90:
                    d_c = 2
                elif n <= 900:
                    d_c = 3
                else:
                    d_c = 4
                xs = hch_samples(base, d_c, b'strat', n)
            elif method == 'numpy':
                xs = numpy_samples(n, seed=42 + fi)
            else:
                xs = systematic_samples(n)

            estimate = np.mean(func(xs))
            errors.append((n, abs(estimate - true_val)))

        results[(name, method)] = errors


# --- Also: run numpy 100 times and take the median error envelope ---
print("  numpy variance envelope...")
numpy_envelope = {}
for fi, (func, true_val, name) in enumerate(functions):
    envelope = []
    for n in sizes:
        errs = []
        for trial in range(100):
            xs = numpy_samples(n, seed=trial * 1000 + fi)
            errs.append(abs(np.mean(func(xs)) - true_val))
        envelope.append((n, np.median(errs), np.percentile(errs, 10),
                         np.percentile(errs, 90)))
    numpy_envelope[name] = envelope


# --- Plot ---
print("Plotting...")

fig, axes = plt.subplots(2, 3, figsize=(24, 14))
fig.patch.set_facecolor('#0a0a0a')

# Mark block boundaries
boundaries = [9, 90, 900, 9000]

for fi, (func, true_val, name) in enumerate(functions):
    ax = axes[fi // 3, fi % 3]
    ax.set_facecolor('#0a0a0a')

    # numpy envelope (10th-90th percentile)
    env = numpy_envelope[name]
    ns_env = [e[0] for e in env]
    med = [e[1] for e in env]
    p10 = [e[2] for e in env]
    p90 = [e[3] for e in env]
    ax.fill_between(ns_env, p10, p90, color='#6ec6ff', alpha=0.15)
    ax.loglog(ns_env, med, color='#6ec6ff', linewidth=0.8, alpha=0.5,
              label='numpy (median, 100 trials)')

    # HCH
    hch_data = results[(name, 'hch')]
    ns_h = [e[0] for e in hch_data]
    errs_h = [e[1] for e in hch_data]
    ax.loglog(ns_h, [max(e, 1e-16) for e in errs_h],
              color='#ffcc5c', linewidth=1.2, label='HCH')

    # Systematic
    sys_data = results[(name, 'systematic')]
    ns_s = [e[0] for e in sys_data]
    errs_s = [e[1] for e in sys_data]
    ax.loglog(ns_s, [max(e, 1e-16) for e in errs_s],
              color='#ff6f61', linewidth=1.0, alpha=0.7, label='systematic')

    # Mark block boundaries
    for bnd in boundaries:
        if bnd <= max(ns_h):
            ax.axvline(x=bnd, color='white', linewidth=0.3, alpha=0.3)

    # 1/sqrt(N) reference
    ns_ref = np.array(ns_h, dtype=float)
    ax.loglog(ns_ref, 0.3 / np.sqrt(ns_ref), color='white',
              linewidth=0.5, linestyle=':', alpha=0.3, label='1/√N')

    ax.set_title(name, color='white', fontsize=13, pad=10)
    ax.tick_params(colors='white')
    ax.set_ylim(1e-6, 1)
    for spine in ax.spines.values():
        spine.set_color('#333')

axes[0, 0].set_ylabel('|estimate - true|', color='white', fontsize=11)
axes[1, 0].set_ylabel('|estimate - true|', color='white', fontsize=11)
axes[1, 0].set_xlabel('N samples', color='white', fontsize=11)
axes[1, 1].set_xlabel('N samples', color='white', fontsize=11)
axes[0, 0].legend(fontsize=9, framealpha=0.3, labelcolor='white',
                  facecolor='#1a1a1a', loc='lower left')

# Hide the 6th panel
axes[1, 2].set_visible(False)

plt.subplots_adjust(wspace=0.12, hspace=0.2)
plt.savefig('stratified.png', dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
print("-> stratified.png")
