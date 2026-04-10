"""
mc_diagnostic.py — Monte Carlo / stratified sampling diagnostics.

Two panels comparing bidder.cipher, bidder.sawtooth, and numpy PRNG
as noise sources for the two use cases the root API targets:

Panel 1 (top): 2D equidistribution (pairs test).
    Take outputs at(2i) and at(2i+1) as (x, y) pairs, map to the unit
    square, and scatter. A good source fills the square uniformly; a
    bad one shows lattice lines or clumping. The cipher should look
    like noise; the sawtooth should show visible structure.

Panel 2 (bottom): Monte Carlo integration convergence.
    Estimate integral of sin(pi*x) on [0, 1] (true value = 2/pi) at
    increasing sample sizes. bidder.cipher is a permutation (zero
    collisions — every sample is unique), so it should converge at
    least as fast as numpy PRNG (which has birthday collisions) and
    should show lower variance at the period boundary (where coverage
    is exactly uniform).

    Also shows: collision count as a function of N. The cipher always
    has 0 collisions; numpy PRNG accumulates ~N^2/(2*period) by the
    birthday bound.

Run: sage -python experiments/bidder/unified/mc_diagnostic.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, REPO)

import numpy as np
import matplotlib.pyplot as plt
import bidder


# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

PERIOD = 2000
N_MONOID = 5
KEY = b'mc diagnostic'
TRUE_INTEGRAL = 2.0 / np.pi   # integral of sin(pi*x) on [0,1]


# ---------------------------------------------------------------------------
# Panel 1: 2D equidistribution (pairs test)
# ---------------------------------------------------------------------------

print("Generating pairs ...")

B = bidder.cipher(period=PERIOD, key=KEY)
S = bidder.sawtooth(n=N_MONOID, count=PERIOD)

n_pairs = PERIOD // 2

# Cipher: map [0, period) to [0, 1)
cipher_x = np.array([B.at(2 * i) for i in range(n_pairs)]) / PERIOD
cipher_y = np.array([B.at(2 * i + 1) for i in range(n_pairs)]) / PERIOD

# Sawtooth: map n-primes to [0, 1) via min/max normalization
saw_raw_x = np.array([S.at(2 * i) for i in range(n_pairs)], dtype=float)
saw_raw_y = np.array([S.at(2 * i + 1) for i in range(n_pairs)], dtype=float)
saw_min, saw_max = saw_raw_x.min(), saw_raw_y.max()
saw_x = (saw_raw_x - saw_min) / (saw_max - saw_min)
saw_y = (saw_raw_y - saw_min) / (saw_max - saw_min)

# Numpy PRNG
rng = np.random.default_rng(42)
np_x = rng.uniform(0, 1, n_pairs)
np_y = rng.uniform(0, 1, n_pairs)


# ---------------------------------------------------------------------------
# Panel 2: MC integration convergence + collision count
# ---------------------------------------------------------------------------

print("Running MC integration sweep ...")

sample_sizes = np.unique(np.geomspace(10, PERIOD, num=80).astype(int))

# Integrand: sin(pi * x)
def f(x):
    return np.sin(np.pi * x)


def mc_errors_cipher(period, key, sizes):
    """MC estimate using bidder.cipher. Zero collisions by construction."""
    B = bidder.cipher(period=period, key=key)
    full = np.array([B.at(i) for i in range(period)]) / period
    errors = []
    for N in sizes:
        estimate = np.mean(f(full[:N]))
        errors.append(abs(estimate - TRUE_INTEGRAL))
    return np.array(errors)


def mc_errors_numpy(period, seed, sizes, n_trials=20):
    """MC estimate using numpy PRNG (with replacement). Average over
    n_trials to smooth the variance."""
    errors = []
    for N in sizes:
        trial_errors = []
        for t in range(n_trials):
            rng_t = np.random.default_rng(seed * 1000 + t)
            samples = rng_t.uniform(0, 1, N)
            estimate = np.mean(f(samples))
            trial_errors.append(abs(estimate - TRUE_INTEGRAL))
        errors.append(np.mean(trial_errors))
    return np.array(errors)


def collision_counts_numpy(period, seed, sizes, n_trials=20):
    """Expected number of collisions (birthday paradox) when sampling
    N values from [0, period) with replacement."""
    counts = []
    for N in sizes:
        trial_collisions = []
        for t in range(n_trials):
            rng_t = np.random.default_rng(seed * 1000 + t)
            draws = rng_t.integers(0, period, size=N)
            trial_collisions.append(N - len(set(draws)))
        counts.append(np.mean(trial_collisions))
    return np.array(counts)


cipher_errs = mc_errors_cipher(PERIOD, KEY, sample_sizes)
numpy_errs = mc_errors_numpy(PERIOD, 42, sample_sizes)
numpy_collisions = collision_counts_numpy(PERIOD, 42, sample_sizes)


# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------

print("Plotting ...")

YELLOW = '#ffcc5c'
BLUE = '#6ec6ff'
RED = '#ff6f61'
GREEN = '#88d8b0'

fig = plt.figure(figsize=(22, 20))
fig.patch.set_facecolor('#0a0a0a')

gs = fig.add_gridspec(3, 3, hspace=0.30, wspace=0.25,
                      height_ratios=[1.0, 0.8, 0.8])


def style(ax, title, xlabel=None, ylabel=None):
    ax.set_facecolor('#0a0a0a')
    ax.set_title(title, color='white', fontsize=12, pad=10)
    if xlabel:
        ax.set_xlabel(xlabel, color='white', fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, color='white', fontsize=10)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#333')


# --- Row 1: 2D pairs ---

ax1 = fig.add_subplot(gs[0, 0])
style(ax1, f'bidder.cipher pairs (P={PERIOD})', xlabel='at(2i)/P',
      ylabel='at(2i+1)/P')
ax1.scatter(cipher_x, cipher_y, s=2, c=YELLOW, alpha=0.5)
ax1.set_xlim(0, 1)
ax1.set_ylim(0, 1)
ax1.set_aspect('equal')

ax2 = fig.add_subplot(gs[0, 1])
style(ax2, f'bidder.sawtooth pairs (n={N_MONOID})', xlabel='at(2i)',
      ylabel='at(2i+1)')
ax2.scatter(saw_x, saw_y, s=2, c=BLUE, alpha=0.5)
ax2.set_xlim(0, 1)
ax2.set_ylim(0, 1)
ax2.set_aspect('equal')

ax3 = fig.add_subplot(gs[0, 2])
style(ax3, 'numpy PRNG pairs', xlabel='u_i', ylabel='u_{i+1}')
ax3.scatter(np_x, np_y, s=2, c=GREEN, alpha=0.5)
ax3.set_xlim(0, 1)
ax3.set_ylim(0, 1)
ax3.set_aspect('equal')

# --- Row 2: MC integration convergence ---

ax4 = fig.add_subplot(gs[1, :2])
style(ax4, f'MC integration error: ∫ sin(πx) dx on [0,1]  (true = 2/π ≈ {TRUE_INTEGRAL:.4f})',
      xlabel='sample size N', ylabel='|error|')
ax4.loglog(sample_sizes, cipher_errs, color=YELLOW, linewidth=1.5,
           label='bidder.cipher (permutation)', alpha=0.9)
ax4.loglog(sample_sizes, numpy_errs, color=GREEN, linewidth=1.5,
           label='numpy PRNG (with replacement, avg 20 trials)', alpha=0.9)
# Reference line: O(1/sqrt(N))
ref_N = sample_sizes.astype(float)
ref = 0.3 / np.sqrt(ref_N)
ax4.loglog(sample_sizes, ref, color='#555', linewidth=1, linestyle='--',
           label='O(1/√N) reference')
ax4.axvline(PERIOD, color=RED, linewidth=1, linestyle=':',
            label=f'period boundary (N={PERIOD})')
ax4.legend(facecolor='#1a1a1a', edgecolor='#333', labelcolor='white',
           fontsize=9)

# --- Row 3: Collision count ---

ax5 = fig.add_subplot(gs[2, :2])
style(ax5, 'Collisions: unique samples lost to birthday duplicates',
      xlabel='sample size N', ylabel='collisions (= N − |unique|)')
# Cipher: always 0
ax5.plot(sample_sizes, np.zeros_like(sample_sizes), color=YELLOW,
         linewidth=2, label='bidder.cipher (always 0)')
ax5.plot(sample_sizes, numpy_collisions, color=GREEN, linewidth=1.5,
         label='numpy PRNG (avg 20 trials)')
# Theoretical birthday bound: N^2 / (2*P)
birthday = sample_sizes.astype(float)**2 / (2 * PERIOD)
ax5.plot(sample_sizes, birthday, color='#555', linewidth=1,
         linestyle='--', label='N²/(2P) birthday bound')
ax5.axvline(PERIOD, color=RED, linewidth=1, linestyle=':',
            label=f'period boundary (N={PERIOD})')
ax5.legend(facecolor='#1a1a1a', edgecolor='#333', labelcolor='white',
           fontsize=9)

# --- Row 3, right: chi-squared on 2D bins for the pairs ---

ax6 = fig.add_subplot(gs[1:, 2])
style(ax6, 'χ² on 10×10 bins of pairs', ylabel='χ² statistic')

def chi2_2d(x, y, bins=10):
    """Chi-squared statistic for uniformity of 2D points in [0,1)^2."""
    H, _, _ = np.histogram2d(x, y, bins=bins, range=[[0, 1], [0, 1]])
    expected = len(x) / (bins * bins)
    return np.sum((H - expected)**2 / expected)

sources = [
    ('cipher', cipher_x, cipher_y, YELLOW),
    ('sawtooth', saw_x, saw_y, BLUE),
    ('numpy', np_x, np_y, GREEN),
]
chi2_vals = []
labels = []
colors = []
for name, x, y, color in sources:
    c2 = chi2_2d(x, y, bins=10)
    chi2_vals.append(c2)
    labels.append(name)
    colors.append(color)

bars = ax6.bar(labels, chi2_vals, color=colors, alpha=0.8, edgecolor='none')
# Reference line: expected chi2 for 100 bins is 99 (df = bins^2 - 1)
ax6.axhline(99, color='#555', linewidth=1, linestyle='--',
            label='expected χ² (df=99)')
ax6.legend(facecolor='#1a1a1a', edgecolor='#333', labelcolor='white',
           fontsize=9)
for bar, val in zip(bars, chi2_vals):
    ax6.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
             f'{val:.1f}', ha='center', va='bottom', color='white',
             fontsize=10)

plt.savefig(os.path.join(HERE, 'mc_diagnostic.png'),
            dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
print("-> mc_diagnostic.png")

# ---------------------------------------------------------------------------
# Quantitative summary
# ---------------------------------------------------------------------------

print(f"\n2D pairs chi-squared (10x10 bins, {n_pairs} pairs, df=99):")
for name, val in zip(labels, chi2_vals):
    print(f"  {name:10s}: χ² = {val:7.1f}  "
          f"{'OK' if 60 < val < 140 else 'SUSPECT'}")

print(f"\nMC integration at N={PERIOD} (period boundary):")
print(f"  true value:     {TRUE_INTEGRAL:.6f}")
print(f"  bidder.cipher:  error = {cipher_errs[-1]:.6f}")
print(f"  numpy PRNG:     error = {numpy_errs[-1]:.6f}")

print(f"\nCollisions at N={PERIOD}:")
print(f"  bidder.cipher:  0 (by construction)")
print(f"  numpy PRNG:     ~{numpy_collisions[-1]:.0f} "
      f"(birthday bound: {PERIOD**2/(2*PERIOD):.0f})")
