"""
escalating_bidder_mul.py — Fully bidderized version of escalating_mul.

Same schedule (10k adds, 1 mul, 10k adds, 4 muls, 10k adds, 5 muls,
10k adds), but both the uniform source AND the partner-index sampling
use BIDDER's keyed permutation instead of numpy PRNG.

The source is Bidder(base=10, digit_class=4) as before. The partner
indices at each step come from a BidderBlock of period=N, one cipher
per step, so each step pairs every trial with a distinct source
element (without-replacement) instead of IID draws (with-replacement).
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..', '..', '..', '..')
sys.path.insert(0, os.path.join(ROOT, 'generator'))
sys.path.insert(0, os.path.join(ROOT, 'core'))
DIST = os.path.join(ROOT, 'dist')
sys.path.insert(0, DIST)

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from coupler import Bidder

try:
    import bidder_c as bidder_mod
except ImportError:
    import bidder as bidder_mod

print("Generating uniform source (BIDDER)...")
gen = Bidder(base=10, digit_class=4, key=b'escalating mul')
raw = np.array([gen.next() for _ in range(gen.period)], dtype=np.float64)
reals = 1.0 + raw / 10.0
log_reals = np.log10(reals)

N = len(reals)
n_trials = 8000
n_add = 10000

ops = []
ops += ['add'] * n_add
ops += ['mul'] * 1
ops += ['add'] * n_add
ops += ['mul'] * 4
ops += ['add'] * n_add
ops += ['mul'] * 5
ops += ['add'] * n_add

n_total = len(ops)

mul_events = []
cum_muls = 0
for i, op in enumerate(ops):
    if op == 'mul':
        cum_muls += 1
        if i + 1 >= n_total or ops[i + 1] != 'mul':
            mul_events.append((i, cum_muls))


def first_digits_from_log_values(log_values):
    frac = log_values - np.floor(log_values)
    return np.minimum((10**frac + 1e-9).astype(int), 9)


# Pre-generate initial indices and per-step partner indices using BIDDER.
# Initial: one cipher of period=N, take first n_trials elements.
# Per-step: one cipher per step of period=N, take first n_trials elements.
# This gives without-replacement sampling at each step.

print("Generating BIDDER index ciphers...")
B_init = bidder_mod.cipher(period=N, key=b'escalating:init')
init_indices = np.array([B_init.at(i) % N for i in range(n_trials)],
                        dtype=np.int64)

print(f"Pre-generating {n_total} step ciphers...")
step_indices = np.empty((n_total, n_trials), dtype=np.int64)
for s in range(n_total):
    B_step = bidder_mod.cipher(period=N, key=f'escalating:s{s}'.encode())
    # Use list(B_step) for the full permutation, take first n_trials
    perm = np.array(list(B_step), dtype=np.int64)
    step_indices[s] = perm[:n_trials]
    if (s + 1) % 5000 == 0:
        print(f"  step ciphers: {s+1}/{n_total}")

print(f"Running {n_total} steps...")
heat = np.zeros((n_total, 9))

values = reals[init_indices].copy()
log_values = log_reals[init_indices].copy()

for step in range(n_total):
    idx2 = step_indices[step]

    if ops[step] == 'add':
        values = values + reals[idx2]
        log_values = np.log10(values)
    else:
        log_values = log_values + log_reals[idx2]
        values = 10**log_values

    fds = first_digits_from_log_values(log_values)
    for d in range(1, 10):
        heat[step, d - 1] = np.sum(fds == d) / n_trials

    if (step + 1) % 5000 == 0:
        print(f"  step {step+1}/{n_total}")

benford = np.array([np.log10(1 + 1/d) for d in range(1, 10)])

print("Plotting...")
fig, ax = plt.subplots(figsize=(12, 20))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

im = ax.imshow(heat, aspect='auto', cmap='inferno',
               interpolation='bilinear', origin='lower',
               extent=[0.5, 9.5, 0, n_total])
ax.set_xticks(range(1, 10))
ax.set_xlabel('first digit', color='white', fontsize=13)
ax.set_ylabel('step', color='white', fontsize=13)
ax.tick_params(colors='white')

for step, cum in mul_events:
    ax.axhline(y=step, color='white', linewidth=0.6, linestyle='--',
               alpha=0.6)
    ax.text(9.7, step, f'{cum} mul', color='white', fontsize=9,
            va='center', ha='left')

ax.set_title('Escalating multiplication (BIDDER cipher): 1, then 5, then 10 total',
             color='white', fontsize=14, pad=15)

out = os.path.join(HERE, 'escalating_bidder_mul.png')
plt.savefig(out, dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
print(f"-> escalating_bidder_mul.png")
