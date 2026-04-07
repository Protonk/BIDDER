"""
hamming_strata.py — bit-balance of binary Champernowne streams

For each n in 2..N_MAX, group n-primes by bit-length d, compute the
mean fraction of 1-bits per d-bit class. Plot as a heatmap (n vs d,
color = bias from 0.5). Also plot the running 1-fraction across the
stream for representative monoids, and compare empirical vs predicted
biases for the powers of 2.

See PREDICTIONS.md for the math and the three claims being tested:
  1. n=2 matches the universal +1/(2d) baseline exactly.
  2. n=4 has a small *negative* bias of -1/(6d) for d > 4.
  3. n=8 has a much larger negative bias (-11/(14d)), about 1.57x
     n=2's positive magnitude.
"""

import sys, os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..'))             # base2/
sys.path.insert(0, os.path.join(_here, '..', '..', '..', '..', '..', 'core'))  # core/

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from acm_core import acm_n_primes


# ── Parameters ───────────────────────────────────────────────────────

N_MAX = 32
COUNT_PER_N = 300_000
D_MIN = 4
D_MAX = 20
MIN_SAMPLES_PER_CELL = 20

CONVERGE_MONOIDS = [2, 3, 4, 5, 7, 8, 16, 32]


# ── Predicted fraction for n = 2^m ───────────────────────────────────

def predicted_fraction_pow2(m, d):
    """
    Predicted mean 1-fraction for d-bit n-primes when n = 2^m.

    Two regimes:
      - d <= 2m: constraint k mod 2^m != 0 is automatic.
        fraction = (d - m + 1) / (2d) = 1/2 + (1 - m)/(2d)
      - d > 2m: constraint matters.
        fraction = 1/2 + (1/(2d)) * [1 - 2m + m*2^m/(2^m - 1)]
    """
    if d < m + 1:
        return None
    if d <= 2 * m:
        return (d - m + 1) / (2 * d)
    bracket = 1 - 2 * m + m * (2 ** m) / (2 ** m - 1)
    return 0.5 + bracket / (2 * d)


def predicted_baseline(d):
    """Universal +1/(2d) baseline for all d-bit positive integers."""
    return 0.5 + 1.0 / (2 * d)


def v2(n):
    """2-adic valuation: largest m with 2^m | n."""
    m = 0
    x = n
    while x % 2 == 0:
        m += 1
        x //= 2
    return m


# ── Compute per-(n, d) statistics ────────────────────────────────────

print(f"Computing per-(n, d) bit-balance for n=2..{N_MAX}...")
print(f"Using {COUNT_PER_N} n-primes per monoid.")

# stats[n][d] = [sum_of_ones, total_bits, count_of_primes]
stats = {n: {} for n in range(2, N_MAX + 1)}
# partial_d[n] = the (largest) d that may not be fully covered
partial_d = {}

for n in range(2, N_MAX + 1):
    # Pull one extra so we know what bit-length the next n-prime would have.
    primes = acm_n_primes(n, COUNT_PER_N + 1)
    sentinel_d = primes[-1].bit_length()
    last_in_sample_d = primes[-2].bit_length()
    # The bin at last_in_sample_d is potentially partial. The bin at
    # sentinel_d is definitely partial (we have at most one element of it).
    # Conservatively mask everything from last_in_sample_d upward UNLESS
    # the next prime is in a strictly higher bin, in which case
    # last_in_sample_d is fully covered.
    if sentinel_d > last_in_sample_d:
        partial_d[n] = sentinel_d
    else:
        partial_d[n] = last_in_sample_d

    for p in primes[:-1]:
        d = p.bit_length()
        ones = bin(p).count('1')
        if d not in stats[n]:
            stats[n][d] = [0, 0, 0]
        stats[n][d][0] += ones
        stats[n][d][1] += d
        stats[n][d][2] += 1
    d_lo = min(stats[n])
    d_hi = max(stats[n])
    print(f"  n={n:3d}: d range {d_lo}..{d_hi}, partial from d={partial_d[n]}")


# ── Build heatmap matrix ─────────────────────────────────────────────

print("\nBuilding heatmap...")

n_rows = N_MAX - 1  # n = 2..N_MAX
d_cols = D_MAX - D_MIN + 1
heatmap = np.full((n_rows, d_cols), np.nan)
counts = np.zeros((n_rows, d_cols), dtype=int)

for n in range(2, N_MAX + 1):
    for d in range(D_MIN, D_MAX + 1):
        if d >= partial_d[n]:
            continue  # partial bin, skip
        if d in stats[n] and stats[n][d][2] >= MIN_SAMPLES_PER_CELL:
            sum_ones, total_bits, cnt = stats[n][d]
            heatmap[n - 2, d - D_MIN] = sum_ones / total_bits - 0.5
            counts[n - 2, d - D_MIN] = cnt


# ── Plot heatmap ─────────────────────────────────────────────────────

print("Plotting heatmap...")

fig, ax = plt.subplots(figsize=(14, 11))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

vmax = np.nanmax(np.abs(heatmap))
norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
im = ax.imshow(
    heatmap, aspect='auto', cmap='RdBu_r', norm=norm,
    extent=[D_MIN - 0.5, D_MAX + 0.5, N_MAX + 0.5, 1.5],
    interpolation='nearest',
)

ax.set_xlabel('bit length $d$', color='white', fontsize=12)
ax.set_ylabel('monoid $n$', color='white', fontsize=12)
ax.set_title(
    'Bit-balance bias (mean 1-fraction $-$ 0.5) of d-bit n-primes\n'
    'red = above 0.5, blue = below 0.5',
    color='white', fontsize=13, pad=12,
)

ax.set_xticks(range(D_MIN, D_MAX + 1))
ax.set_yticks(range(2, N_MAX + 1))
ax.set_yticklabels(
    [f'{n}  ($\\nu_2$={v2(n)})' for n in range(2, N_MAX + 1)],
    fontsize=8,
)
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('#444')

cbar = plt.colorbar(im, ax=ax, pad=0.02)
cbar.set_label('bias from 0.5', color='white', fontsize=11)
cbar.ax.yaxis.set_tick_params(color='white')
plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
cbar.outline.set_edgecolor('#444')

plt.tight_layout()
plt.savefig('hamming_strata_heatmap.png', dpi=200,
            facecolor='#0a0a0a', bbox_inches='tight')
plt.close()
print("-> hamming_strata_heatmap.png")


# ── Plot bias-vs-d curves for powers of 2 ─────────────────────────────

print("Plotting bias curves for powers of 2...")

fig, ax = plt.subplots(figsize=(13, 8))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

POW2_COLORS = {
    2:  '#ffcc5c',
    4:  '#c49bff',
    8:  '#ff6f61',
    16: '#ff9966',
    32: '#88d8b0',
}

for m in range(1, 6):
    n = 2 ** m
    emp_x, emp_y = [], []
    pred_x, pred_y = [], []
    for d in range(D_MIN, D_MAX + 1):
        pred = predicted_fraction_pow2(m, d)
        if pred is not None:
            pred_x.append(d)
            pred_y.append(pred - 0.5)
        if d >= partial_d[n]:
            continue
        if d in stats[n] and stats[n][d][2] >= MIN_SAMPLES_PER_CELL:
            sum_ones, total_bits, _ = stats[n][d]
            emp_x.append(d)
            emp_y.append(sum_ones / total_bits - 0.5)
    color = POW2_COLORS[n]
    ax.plot(pred_x, pred_y, '--', color=color, linewidth=1.6,
            alpha=0.55, label=f'n={n} predicted')
    ax.plot(emp_x, emp_y, 'o', color=color, markersize=8,
            markeredgewidth=0, alpha=0.95, label=f'n={n} empirical')

ax.axhline(y=0, color='white', linewidth=0.5, alpha=0.5)
ax.set_xlabel('bit length $d$', color='white', fontsize=12)
ax.set_ylabel('bias from 0.5', color='white', fontsize=12)
ax.set_title(
    'Bit-balance bias vs $d$ for $n = 2^m$\n'
    'dashed = closed-form prediction, dots = empirical',
    color='white', fontsize=13, pad=12,
)
ax.legend(facecolor='#1a1a1a', edgecolor='#444', labelcolor='white',
          fontsize=9, loc='best', ncol=2)
ax.tick_params(colors='white')
ax.grid(True, alpha=0.1, color='white')
for spine in ax.spines.values():
    spine.set_color('#444')

plt.tight_layout()
plt.savefig('hamming_strata_pow2.png', dpi=200,
            facecolor='#0a0a0a', bbox_inches='tight')
plt.close()
print("-> hamming_strata_pow2.png")


# ── Verification table ───────────────────────────────────────────────

print("\n=== VERIFICATION: powers of 2 ===")
print(f"{'n':>4} {'m':>3} {'d':>3} {'empirical':>12} {'predicted':>12} "
      f"{'diff':>12}  count")
print("-" * 64)

for m in range(1, 6):
    n = 2 ** m
    for d in range(max(m + 2, D_MIN), D_MAX + 1, 2):
        if d >= partial_d[n]:
            continue
        if d in stats[n] and stats[n][d][2] >= MIN_SAMPLES_PER_CELL:
            sum_ones, total_bits, cnt = stats[n][d]
            emp = sum_ones / total_bits
            pred = predicted_fraction_pow2(m, d)
            print(f"{n:>4} {m:>3} {d:>3} {emp:>12.6f} {pred:>12.6f} "
                  f"{emp - pred:>+12.6f}  {cnt}")


# ── Convergence plot: running 1-fraction vs cumulative bits ──────────

print("\nComputing convergence curves...")

CONVERGE_COLORS = {
    2:  '#ffcc5c',
    3:  '#88d8b0',
    4:  '#c49bff',
    5:  '#a3d9ff',
    7:  '#ffb3ba',
    8:  '#ff6f61',
    16: '#ff9966',
    32: '#bae1ff',
}


def running_fraction(n, count, n_samples=600):
    """
    Stream the n-primes, accumulate ones and bits, sample at log
    intervals. Returns (cum_bits_array, fraction_array).
    """
    primes = acm_n_primes(n, count)
    sample_indices = np.unique(
        np.geomspace(10, count, n_samples).astype(int)
    )
    sample_set = set(int(s) for s in sample_indices)

    ones_total = 0
    bits_total = 0
    out_x, out_y = [], []
    for i, p in enumerate(primes, start=1):
        d = p.bit_length()
        ones_total += bin(p).count('1')
        bits_total += d
        if i in sample_set:
            out_x.append(bits_total)
            out_y.append(ones_total / bits_total)
    return np.array(out_x), np.array(out_y)


fig, ax = plt.subplots(figsize=(15, 9))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

for n in CONVERGE_MONOIDS:
    print(f"  n={n}...")
    x, y = running_fraction(n, COUNT_PER_N)
    ax.plot(x, y, '-', color=CONVERGE_COLORS[n], linewidth=1.7,
            alpha=0.95, label=f'n={n}  ($\\nu_2$={v2(n)})')

ax.axhline(y=0.5, color='white', linewidth=0.7, alpha=0.7,
           linestyle='--', label='0.5')
ax.set_xscale('log')
ax.set_xlabel('cumulative bits consumed', color='white', fontsize=12)
ax.set_ylabel('running 1-fraction', color='white', fontsize=12)
ax.set_title(
    'Running 1-fraction across binary Champernowne streams\n'
    'most n approach 0.5 from above; high-$\\nu_2(n)$ approach from below',
    color='white', fontsize=13, pad=12,
)
ax.legend(facecolor='#1a1a1a', edgecolor='#444', labelcolor='white',
          fontsize=10, loc='upper right')
ax.tick_params(colors='white')
ax.grid(True, alpha=0.1, color='white')
for spine in ax.spines.values():
    spine.set_color('#444')

plt.tight_layout()
plt.savefig('hamming_strata_convergence.png', dpi=200,
            facecolor='#0a0a0a', bbox_inches='tight')
plt.close()
print("-> hamming_strata_convergence.png")

print("\nDone.")
