"""
adversarial_integrands.py — Quadrature bias diagnostic across integrands.

The Riemann-sum property says bidder.cipher delivers R (the left-
endpoint Riemann sum) at N = P, for any f and any key. But R's
distance from the true integral I depends on f — specifically on
whether f(0) = f(1) (endpoint cancellation).

This script picks four integrands that hit different rows of the
Euler-Maclaurin table and makes three things visible:

  Panel 1: Riemann bias |R - I| vs P for all four integrands.
           sin(pi*x) drops at O(1/P^2); the rest at O(1/P).

  Panel 2: Key-independence at N = P for all four. Every integrand
           shows zero spread across 50 keys, confirming the structural
           property holds even when the quadrature is bad.

  Panel 3: MC error |E_N - I| convergence curves (cipher, single key)
           for all four. Each curve drops toward its own Riemann floor.
           The floor is low for sin(pi*x) and high for f(x) = x.

Run: sage -python experiments/bidder/unified/adversarial_integrands.py
"""

import os
import sys
import math

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, REPO)

import numpy as np
import matplotlib.pyplot as plt
import bidder

YELLOW = '#ffcc5c'
BLUE = '#6ec6ff'
RED = '#ff6f61'
GREEN = '#88d8b0'
PURPLE = '#c49cde'
WHITE = '#ffffff'

COLORS = [YELLOW, BLUE, RED, GREEN]


def style(ax, title, xlabel=None, ylabel=None):
    ax.set_facecolor('#0a0a0a')
    ax.set_title(title, color=WHITE, fontsize=11, pad=10)
    if xlabel:
        ax.set_xlabel(xlabel, color=WHITE, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, color=WHITE, fontsize=10)
    ax.tick_params(colors=WHITE)
    for spine in ax.spines.values():
        spine.set_color('#333')


# ---------------------------------------------------------------------------
# Integrands
# ---------------------------------------------------------------------------

integrands = [
    # (name, f, true_integral, endpoint_note)
    ('sin(πx)',
     lambda x: np.sin(np.pi * x),
     2.0 / np.pi,
     'f(0)=f(1)=0 → O(1/P²)'),

    ('x',
     lambda x: x,
     0.5,
     'f(0)≠f(1) → O(1/P)'),

    ('√x',
     lambda x: np.sqrt(x),
     2.0 / 3.0,
     "f(0)≠f(1), f'(0)=∞ → O(1/P)"),

    ('1_{x≥1/3}',
     lambda x: (x >= 1.0/3.0).astype(float),
     2.0 / 3.0,
     'discontinuous → O(1/P)'),
]


# ---------------------------------------------------------------------------
# Panel 1: Riemann bias |R - I| vs P
# ---------------------------------------------------------------------------

print("Panel 1: Riemann bias vs P ...")

P_values = np.array([20, 50, 100, 200, 500, 1000, 2000, 5000, 10000])
bias_curves = {}

for name, f, I_true, _ in integrands:
    biases = []
    for P in P_values:
        grid = np.arange(P, dtype=float) / P
        R = float(np.mean(f(grid)))
        biases.append(abs(R - I_true))
    bias_curves[name] = np.array(biases)
    print(f"  {name:12s}: bias at P=10000 = {biases[-1]:.4e}")


# ---------------------------------------------------------------------------
# Panel 2: Key-independence at N = P
# ---------------------------------------------------------------------------

print("\nPanel 2: Key-independence (50 keys, P=2000) ...")

P_fixed = 2000
n_keys = 50
key_spreads = {}

for name, f, I_true, _ in integrands:
    estimates = []
    for k in range(n_keys):
        B = bidder.cipher(period=P_fixed, key=f'adv-{name}-{k}'.encode())
        est = sum(float(f(np.array([B.at(i) / P_fixed]))[0])
                  for i in range(P_fixed)) / P_fixed
        estimates.append(est)
    estimates = np.array(estimates)
    spread = estimates.max() - estimates.min()
    key_spreads[name] = (estimates, spread)
    print(f"  {name:12s}: spread = {spread:.2e}  "
          f"mean = {estimates.mean():.10f}")


# ---------------------------------------------------------------------------
# Panel 3: MC convergence |E_N - I| for one key per integrand
# ---------------------------------------------------------------------------

print("\nPanel 3: MC convergence curves ...")

P_mc = 2000
sample_sizes = np.unique(np.geomspace(10, P_mc, num=120).astype(int))
mc_curves = {}

for name, f, I_true, _ in integrands:
    B = bidder.cipher(period=P_mc, key=b'adversarial')
    # Precompute full output
    full = np.array([float(f(np.array([B.at(i) / P_mc]))[0])
                     for i in range(P_mc)])
    cumsum = np.cumsum(full)
    errors = np.abs(cumsum[sample_sizes - 1] / sample_sizes - I_true)
    mc_curves[name] = errors
    print(f"  {name:12s}: error at N=P = {errors[-1]:.4e}")


# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------

print("\nPlotting ...")

fig, axes = plt.subplots(1, 3, figsize=(24, 7))
fig.patch.set_facecolor('#0a0a0a')

# --- Panel 1: Riemann bias ---
ax1 = axes[0]
style(ax1, 'Riemann bias |R − I| vs P', xlabel='P', ylabel='|R − I|')
for i, (name, _, _, note) in enumerate(integrands):
    ax1.loglog(P_values, bias_curves[name], 'o-', color=COLORS[i],
               linewidth=1.5, markersize=4, label=f'{name}  ({note})')
# Reference slopes
ref_P = P_values.astype(float)
ax1.loglog(P_values, 0.5 / ref_P, '--', color='#555', linewidth=1,
           label='O(1/P)')
ax1.loglog(P_values, 5.0 / ref_P**2, ':', color='#555', linewidth=1,
           label='O(1/P²)')
ax1.legend(facecolor='#1a1a1a', edgecolor='#333', labelcolor=WHITE,
           fontsize=8, loc='lower left')

# --- Panel 2: Key-independence ---
ax2 = axes[1]
style(ax2, f'Key-independence: {n_keys} keys at N = P = {P_fixed}',
      ylabel='estimate at N = P')
x_pos = np.arange(len(integrands))
for i, (name, _, I_true, _) in enumerate(integrands):
    estimates, spread = key_spreads[name]
    # All estimates are identical (or near-identical), so plot a bar
    # at the mean, plus a thin error bar for the spread
    mean = estimates.mean()
    ax2.bar(i, mean, color=COLORS[i], alpha=0.8, width=0.6)
    # True integral marker
    ax2.plot([i - 0.3, i + 0.3], [I_true, I_true], color=WHITE,
             linewidth=2, linestyle='-')
    # Annotate spread
    ax2.text(i, mean + 0.02,
             f'spread\n{spread:.0e}',
             ha='center', va='bottom', color=WHITE, fontsize=8)
ax2.set_xticks(x_pos)
ax2.set_xticklabels([name for name, _, _, _ in integrands],
                     color=WHITE, fontsize=9)
# Legend for the white line
from matplotlib.lines import Line2D
ax2.legend([Line2D([0], [0], color=WHITE, linewidth=2)],
           ['true integral I'],
           facecolor='#1a1a1a', edgecolor='#333', labelcolor=WHITE,
           fontsize=9)

# --- Panel 3: MC convergence ---
ax3 = axes[2]
style(ax3, f'MC error |E_N − I| (cipher, P = {P_mc})',
      xlabel='sample size N', ylabel='|E_N − I|')
for i, (name, _, _, _) in enumerate(integrands):
    ax3.semilogy(sample_sizes, mc_curves[name], color=COLORS[i],
                 linewidth=1.2, label=name, alpha=0.9)
# Riemann floors
for i, (name, _, I_true, _) in enumerate(integrands):
    grid = np.arange(P_mc, dtype=float) / P_mc
    f_func = integrands[i][1]
    R = float(np.mean(f_func(grid)))
    floor = abs(R - I_true)
    if floor > 0:
        ax3.axhline(floor, color=COLORS[i], linewidth=0.8,
                     linestyle=':', alpha=0.5)
ax3.axvline(P_mc, color=RED, linewidth=1, linestyle=':',
            alpha=0.5, label=f'N = P = {P_mc}')
ax3.legend(facecolor='#1a1a1a', edgecolor='#333', labelcolor=WHITE,
           fontsize=8)

plt.subplots_adjust(wspace=0.25)
plt.savefig(os.path.join(HERE, 'adversarial_integrands.png'),
            dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
print("-> adversarial_integrands.png")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print(f"""
Summary
-------
The structural property (key-independence, E_P = R) holds for all
four integrands — including the adversarial ones. The spread across
{n_keys} keys is zero (up to float noise) in every case.

The quadrature quality differs:
  sin(πx):    |R-I| = O(1/P²)   because f(0) = f(1) = 0
  x:          |R-I| = 1/(2P)     because f(0) ≠ f(1)
  √x:         |R-I| = O(1/P)     because f(0) ≠ f(1) and f'(0) = ∞
  1_{{x≥1/3}}: |R-I| = O(1/P)     because f is discontinuous

The cipher always delivers R. Whether R is close enough to I is a
quadrature question, not a cipher question.
""")
