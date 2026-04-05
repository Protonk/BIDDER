"""
single_mul.py — One multiplication in a sea of additions.

10,000 additions, then 1 multiplication, then 10,000 more additions.
Does the single mul leave a permanent scar, or does the additive
flood wash it out?
"""

import sys
sys.path.insert(0, '../../../generator')
sys.path.insert(0, '../../..')

import numpy as np
import matplotlib.pyplot as plt
from hch_speck import HCHSpeck

print("Generating uniform source...")
gen = HCHSpeck(base=10, digit_class=4, key=b'single mul')
raw = np.array(gen.generate(gen.period), dtype=np.float64)
reals = 1.0 + raw / 10.0
log_reals = np.log10(reals)

N = len(reals)
n_trials = 8000
n_pre = 10000
n_post = 10000
n_total = n_pre + 1 + n_post
rng = np.random.default_rng(42)


def first_digits(values):
    log_v = np.log10(values)
    frac = log_v - np.floor(log_v)
    return np.minimum((10**frac).astype(int), 9)


print(f"Running {n_total} steps ({n_pre} add, 1 mul, {n_post} add)...")
heat = np.zeros((n_total, 9))
ops = ['add'] * n_pre + ['mul'] + ['add'] * n_post

idx = rng.integers(0, N, size=n_trials)
values = reals[idx].copy()
log_values = log_reals[idx].copy()

for step in range(n_total):
    idx2 = rng.integers(0, N, size=n_trials)

    if ops[step] == 'add':
        values = values + reals[idx2]
        log_values = np.log10(values)
    else:
        log_values = log_values + log_reals[idx2]
        values = 10**log_values

    fds = first_digits(values)
    for d in range(1, 10):
        heat[step, d - 1] = np.sum(fds == d) / n_trials

    if (step + 1) % 2000 == 0 or step == n_pre or step == n_pre + 1:
        print(f"  step {step+1}/{n_total} ({ops[step]})")


print("Plotting...")
fig, ax = plt.subplots(figsize=(12, 16))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

im = ax.imshow(heat, aspect='auto', cmap='inferno',
               interpolation='bilinear', origin='lower',
               extent=[0.5, 9.5, 0, n_total])
ax.set_xticks(range(1, 10))
ax.set_xlabel('first digit', color='white', fontsize=13)
ax.set_ylabel('step', color='white', fontsize=13)
ax.tick_params(colors='white')

# Mark the multiplication event
ax.axhline(y=n_pre, color='white', linewidth=0.8, linestyle='--', alpha=0.7)
ax.text(9.7, n_pre, 'mul', color='white', fontsize=10, va='center', ha='left')

ax.set_title('10,000 adds — 1 mul — 10,000 adds',
             color='white', fontsize=15, pad=15)

plt.savefig('single_mul.png', dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
print("-> single_mul.png")
