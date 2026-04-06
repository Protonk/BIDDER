"""
Uniformity demo — leading-digit deviation at three sample sizes.

Base 10, N = 64 / 2048 / 65536. At each n, track the maximum
deviation of any digit's cumulative frequency from 1/9. The
sawtooth wobbles toward zero as N grows, with exact zeros at
every complete digit-block boundary (9, 99, 999, 9999, ...).
"""

import sys
sys.path.insert(0, '../../../core')

import numpy as np
import matplotlib.pyplot as plt


def leading_digit(n):
    """Leading base-10 digit of positive integer n."""
    while n >= 10:
        n //= 10
    return n


def max_deviation(N):
    """Compute running max |freq(d) - 1/9| over n = 1..N."""
    counts = np.zeros(10, dtype=int)
    dev = np.empty(N)
    target = 1.0 / 9
    for i in range(1, N + 1):
        d = leading_digit(i)
        counts[d] += 1
        fracs = counts[1:] / i  # digits 1..9
        dev[i - 1] = np.max(np.abs(fracs - target))
    return dev


Ns = [64, 2048, 65536]

print("Computing deviations...")
fig, axes = plt.subplots(3, 1, figsize=(16, 12), sharex=False)
fig.patch.set_facecolor('#0a0a0a')

for ax, N in zip(axes, Ns):
    ax.set_facecolor('#0a0a0a')
    print(f"  N = {N}...")
    ns = np.arange(1, N + 1)
    dev = max_deviation(N)

    ax.semilogx(ns, dev, linewidth=0.6, color='#ffcc5c', alpha=0.9)

    # Mark digit-block boundaries where deviation hits zero
    for boundary in [9, 99, 999, 9999]:
        if boundary <= N:
            ax.axvline(x=boundary, color='white', linewidth=0.3, alpha=0.3)
            ax.plot(boundary, dev[boundary - 1], 'o',
                    color='#ff6f61', markersize=5, zorder=5)

    ax.axhline(y=0, color='#6ec6ff', linewidth=0.8, alpha=0.4)
    ax.set_ylabel('max deviation', color='white', fontsize=10)
    ax.set_title(f'N = {N:,}', color='white', fontsize=12, pad=8)
    ax.set_xlim(1, N)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#333')

    print(f"    final max deviation: {dev[-1]:.6f}")

axes[-1].set_xlabel('n', color='white', fontsize=12)
plt.tight_layout()
plt.savefig('uniformity_wobble.png', dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
print("-> uniformity_wobble.png")
