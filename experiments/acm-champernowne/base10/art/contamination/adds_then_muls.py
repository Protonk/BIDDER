"""
adds_then_muls.py — 1000 additions, then 10 multiplications.

The rolling shutter runs for 1000 steps, then 10 muls
re-assert Benford. One graph.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..', '..', 'generator'))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..', '..', 'core'))

import numpy as np
import matplotlib.pyplot as plt
from coupler import Bidder

print("Generating uniform source...")
gen = Bidder(base=10, digit_class=4, key=b'adds then muls')
raw = np.array([gen.next() for _ in range(gen.period)], dtype=np.float64)
reals = 1.0 + raw / 10.0
log_reals = np.log10(reals)

N = len(reals)
n_trials = 8000
n_adds = 1000
n_muls = 10
n_total = n_adds + n_muls
rng = np.random.default_rng(42)


def first_digits_from_log_values(log_values):
    frac = log_values - np.floor(log_values)
    return np.minimum((10**frac + 1e-9).astype(int), 9)


print(f"Running {n_total} steps ({n_adds} add, {n_muls} mul)...")
heat = np.zeros((n_total, 9))

idx = rng.integers(0, N, size=n_trials)
values = reals[idx].copy()
log_values = log_reals[idx].copy()

for step in range(n_total):
    idx2 = rng.integers(0, N, size=n_trials)

    if step < n_adds:
        values = values + reals[idx2]
        log_values = np.log10(values)
    else:
        log_values = log_values + log_reals[idx2]
        values = 10**log_values

    fds = first_digits_from_log_values(log_values)
    for d in range(1, 10):
        heat[step, d - 1] = np.sum(fds == d) / n_trials

print("Plotting...")
fig, ax = plt.subplots(figsize=(10, 16))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

im = ax.imshow(heat, aspect='auto', cmap='inferno',
               interpolation='bilinear', origin='lower',
               extent=[0.5, 9.5, 0, n_total])
ax.set_xticks(range(1, 10))
ax.set_xlabel('first digit', color='white', fontsize=13)
ax.set_ylabel('step', color='white', fontsize=13)
ax.tick_params(colors='white')

ax.axhline(y=n_adds, color='white', linewidth=0.8, linestyle='--', alpha=0.7)
ax.text(9.7, n_adds, 'mul begins', color='white', fontsize=10,
        va='bottom', ha='left')

ax.set_title('1,000 adds then 10 muls',
             color='white', fontsize=15, pad=15)

plt.savefig('adds_then_muls.png', dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
print("-> adds_then_muls.png")
