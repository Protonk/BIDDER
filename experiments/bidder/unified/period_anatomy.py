"""
period_anatomy.py — Diagnostic comparison of cipher vs sawtooth structure.

Visualizes what happens inside one period for both bidder.cipher and
bidder.sawtooth, side by side:

Left column:  bidder.cipher(P, key) — a keyed permutation of [0, P).
Right column: bidder.sawtooth(n, count) — deterministic ascending n-primes.

Four rows of diagnostics:

Row 1: Raw output sequence. Cipher is a shuffle; sawtooth is monotone.
Row 2: Output histogram. Cipher is perfectly flat (permutation);
       sawtooth has a characteristic staircase from digit-class boundaries.
Row 3: First-difference series. Cipher diffs are noisy; sawtooth diffs
       are mostly n or 2n with a periodic deletion.
Row 4: Autocorrelation of the output. Cipher has no structure beyond
       lag 0; sawtooth has periodic spikes at multiples of (n-1).

These are diagnostic: the point is to see the structural contrast
between a keyed shuffle (uniform, opaque) and a deterministic
arithmetic progression with deletions (structured, transparent).

Run: sage -python experiments/bidder/unified/period_anatomy.py
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

PERIOD = 500
N_MONOID = 7   # 7-primes: multiples of 7 not divisible by 49
KEY = b'anatomy'

# ---------------------------------------------------------------------------
# Generate
# ---------------------------------------------------------------------------

print("Generating sequences ...")

B = bidder.cipher(period=PERIOD, key=KEY)
S = bidder.sawtooth(n=N_MONOID, count=PERIOD)

cipher_seq = np.array([B.at(i) for i in range(PERIOD)])
saw_seq = np.array([S.at(i) for i in range(PERIOD)])

print(f"  cipher: period={B.period}, range=[{cipher_seq.min()}, {cipher_seq.max()}]")
print(f"  sawtooth: n={S.n}, count={S.count}, "
      f"range=[{saw_seq.min()}, {saw_seq.max()}]")

# ---------------------------------------------------------------------------
# Derived series
# ---------------------------------------------------------------------------

cipher_diff = np.diff(cipher_seq)
saw_diff = np.diff(saw_seq)

# Normalized autocorrelation (subtract mean, divide by variance)
def autocorr(x, max_lag=100):
    x = x - x.mean()
    var = np.sum(x**2)
    if var == 0:
        return np.zeros(max_lag)
    return np.array([np.sum(x[:len(x)-lag] * x[lag:]) / var
                     for lag in range(max_lag)])

cipher_ac = autocorr(cipher_seq.astype(float), max_lag=min(100, PERIOD // 2))
saw_ac = autocorr(saw_seq.astype(float), max_lag=min(100, PERIOD // 2))

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------

print("Plotting ...")

fig, axes = plt.subplots(4, 2, figsize=(20, 18))
fig.patch.set_facecolor('#0a0a0a')

YELLOW = '#ffcc5c'
BLUE = '#6ec6ff'
RED = '#ff6f61'
GREEN = '#88d8b0'


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


# Row 1: Raw sequence
style(axes[0, 0], f'bidder.cipher(period={PERIOD}, key={KEY!r})',
      xlabel='index', ylabel='output')
axes[0, 0].scatter(range(PERIOD), cipher_seq, s=1, c=YELLOW, alpha=0.7)

style(axes[0, 1], f'bidder.sawtooth(n={N_MONOID}, count={PERIOD})',
      xlabel='index', ylabel='output')
axes[0, 1].plot(range(PERIOD), saw_seq, color=BLUE, linewidth=0.5)

# Row 2: Histogram
n_bins = min(50, PERIOD // 4)

style(axes[1, 0], 'Output histogram (cipher)', ylabel='count')
axes[1, 0].hist(cipher_seq, bins=n_bins, color=YELLOW, alpha=0.8,
                edgecolor='none')

style(axes[1, 1], 'Output histogram (sawtooth)', ylabel='count')
axes[1, 1].hist(saw_seq, bins=n_bins, color=BLUE, alpha=0.8,
                edgecolor='none')

# Row 3: First differences
style(axes[2, 0], 'First differences (cipher)', xlabel='index',
      ylabel='Δ')
axes[2, 0].scatter(range(len(cipher_diff)), cipher_diff, s=1,
                   c=RED, alpha=0.6)

style(axes[2, 1], 'First differences (sawtooth)', xlabel='index',
      ylabel='Δ')
axes[2, 1].scatter(range(len(saw_diff)), saw_diff, s=2, c=GREEN,
                   alpha=0.8)
# Annotate the two values
unique_diffs = sorted(set(saw_diff))
if len(unique_diffs) <= 3:
    diff_str = ', '.join(str(int(d)) for d in unique_diffs)
    axes[2, 1].text(0.98, 0.95, f'values: {{{diff_str}}}',
                    transform=axes[2, 1].transAxes,
                    color='white', fontsize=10,
                    ha='right', va='top')

# Row 4: Autocorrelation
max_lag = len(cipher_ac)

style(axes[3, 0], 'Autocorrelation (cipher)', xlabel='lag',
      ylabel='r')
axes[3, 0].bar(range(max_lag), cipher_ac, width=1, color=YELLOW,
               alpha=0.8)
axes[3, 0].axhline(0, color='#555', linewidth=0.5)

style(axes[3, 1], 'Autocorrelation (sawtooth)', xlabel='lag',
      ylabel='r')
axes[3, 1].bar(range(max_lag), saw_ac, width=1, color=BLUE,
               alpha=0.8)
axes[3, 1].axhline(0, color='#555', linewidth=0.5)

plt.subplots_adjust(wspace=0.20, hspace=0.30)
plt.savefig(os.path.join(HERE, 'period_anatomy.png'),
            dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
print("-> period_anatomy.png")

# ---------------------------------------------------------------------------
# Quantitative diagnostics
# ---------------------------------------------------------------------------

print(f"\nCipher diagnostics (period={PERIOD}):")
print(f"  output range:       [{cipher_seq.min()}, {cipher_seq.max()}]")
print(f"  unique outputs:     {len(set(cipher_seq))} (should be {PERIOD})")
print(f"  mean:               {cipher_seq.mean():.2f} (should be ~{(PERIOD-1)/2:.1f})")
print(f"  diff range:         [{cipher_diff.min()}, {cipher_diff.max()}]")
print(f"  autocorr at lag 1:  {cipher_ac[1]:.4f} (should be ~0)")

print(f"\nSawtooth diagnostics (n={N_MONOID}, count={PERIOD}):")
print(f"  output range:       [{saw_seq.min()}, {saw_seq.max()}]")
print(f"  unique outputs:     {len(set(saw_seq))} (should be {PERIOD})")
print(f"  mean:               {saw_seq.mean():.2f}")
print(f"  diff values:        {sorted(set(saw_diff))}")
print(f"  autocorr at lag {N_MONOID-1}:  {saw_ac[N_MONOID-1]:.4f} "
      f"(periodic spike at n-1={N_MONOID-1})")
