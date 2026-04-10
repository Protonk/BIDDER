"""
riemann_proof.py — Demonstrate that bidder.cipher at N=period is an
exact Riemann sum, and that this is a structural property of the
permutation rather than a lucky coincidence.

The argument:

    bidder.cipher(P, key) is a permutation of [0, P).
    At N = P, you have visited every integer in [0, P) exactly once.
    The MC estimate is (1/P) * sum(f(k/P) for k in permutation).
    But sum over a permutation of S = sum over S.
    So the estimate is (1/P) * sum(f(k/P) for k in range(P)).
    This is the standard Riemann sum of f on [0, 1) with P equal bins.
    The key cancels out — every key gives the same sum at N = P.

This script demonstrates the claim empirically:

    Panel 1: For 10 different keys, plot the MC integration curve for
             f(x) = sin(pi*x). All 10 curves converge to different
             trajectories but arrive at the SAME value at N = P.
             That value is the Riemann sum, not the true integral —
             but for sin(pi*x) the left-rule error is O(1/P^2) because
             f(0) = f(1) = 0 (endpoint cancellation), so for large P
             the distinction is invisible. Generic integrands with
             f(0) != f(1) converge at the slower rate O(1/P).

    Panel 2: Key-independence at N = P. For 200 different keys, compute
             the MC estimate at N = P. Plot the histogram. It should be
             a single spike (zero variance across keys), because the
             sum over a permutation is the sum over the range regardless
             of the permutation order.

    Panel 3: The Riemann sum vs the true integral as a function of P.
             For sin(pi*x) this shows O(1/P^2) convergence (special case
             with endpoint cancellation). See core/RIEMANN-SUM.md for
             the Euler-Maclaurin analysis of the general case.

    Panel 4: Multiple integrands. Repeat the N = P test for several f:
             sin(pi*x), x^2, exp(-x), sqrt(x), |x - 0.5|. All should
             show key-independence and Riemann-sum convergence.

Run: sage -python experiments/bidder/unified/riemann_proof.py
"""

import os
import sys

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
WHITE = '#ffffff'
COLORS_10 = ['#ffcc5c', '#6ec6ff', '#ff6f61', '#88d8b0',
             '#c49cde', '#ff9966', '#77ddaa', '#dd7799',
             '#99ccff', '#ffdd44']


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
# Integrands with known true values
# ---------------------------------------------------------------------------

integrands = [
    ('sin(πx)',       lambda x: np.sin(np.pi * x),   2.0 / np.pi),
    ('x²',           lambda x: x**2,                  1.0 / 3.0),
    ('exp(−x)',       lambda x: np.exp(-x),            1.0 - np.exp(-1.0)),
    ('√x',           lambda x: np.sqrt(x),             2.0 / 3.0),
    ('|x − 0.5|',    lambda x: np.abs(x - 0.5),       0.25),
]


# ---------------------------------------------------------------------------
# Panel 1: 10 keys, same integrand, convergence to the same N=P value
# ---------------------------------------------------------------------------

P = 2000
f_name, f_func, f_true = integrands[0]  # sin(pi*x)

print(f"Panel 1: 10 keys, f(x) = {f_name}, P = {P}")

sample_sizes = np.unique(np.geomspace(10, P, num=120).astype(int))

key_curves = []
for k in range(10):
    key = f'riemann-{k}'.encode()
    B = bidder.cipher(period=P, key=key)
    full = np.array([f_func(B.at(i) / P) for i in range(P)])
    # Running cumulative mean
    cumsum = np.cumsum(full)
    estimates = cumsum[sample_sizes - 1] / sample_sizes
    errors = np.abs(estimates - f_true)
    key_curves.append(errors)
    final = cumsum[-1] / P
    print(f"  key {k}: N=P estimate = {final:.10f}")

# The Riemann sum (key-independent)
riemann_sum = np.mean([f_func(k / P) for k in range(P)])
riemann_error = abs(riemann_sum - f_true)
print(f"  Riemann sum = {riemann_sum:.10f}, true = {f_true:.10f}, "
      f"error = {riemann_error:.2e}")


# ---------------------------------------------------------------------------
# Panel 2: 200 keys, histogram of N=P estimates
# ---------------------------------------------------------------------------

print(f"\nPanel 2: 200 keys, histogram of N=P estimates")

n_keys = 200
final_estimates = []
for k in range(n_keys):
    key = f'hist-{k}'.encode()
    B = bidder.cipher(period=P, key=key)
    est = sum(f_func(B.at(i) / P) for i in range(P)) / P
    final_estimates.append(est)

final_estimates = np.array(final_estimates)
print(f"  mean = {final_estimates.mean():.10f}")
print(f"  std  = {final_estimates.std():.2e}")
print(f"  min  = {final_estimates.min():.10f}")
print(f"  max  = {final_estimates.max():.10f}")
print(f"  all identical? {np.all(final_estimates == final_estimates[0])}")


# ---------------------------------------------------------------------------
# Panel 3: Riemann sum error as a function of P
# ---------------------------------------------------------------------------

print(f"\nPanel 3: Riemann sum error vs P")

P_values = [50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]
riemann_errors = []
for p in P_values:
    rs = np.mean([f_func(k / p) for k in range(p)])
    riemann_errors.append(abs(rs - f_true))
    print(f"  P = {p:6d}: Riemann error = {riemann_errors[-1]:.2e}")

riemann_errors = np.array(riemann_errors)


# ---------------------------------------------------------------------------
# Panel 4: Multiple integrands at N = P = 2000, 50 keys each
# ---------------------------------------------------------------------------

print(f"\nPanel 4: Multiple integrands, 50 keys each, P = {P}")

multi_results = []
for f_name_i, f_func_i, f_true_i in integrands:
    estimates_i = []
    for k in range(50):
        key = f'multi-{f_name_i}-{k}'.encode()
        B = bidder.cipher(period=P, key=key)
        est = sum(f_func_i(B.at(i) / P) for i in range(P)) / P
        estimates_i.append(est)
    estimates_i = np.array(estimates_i)
    riemann_i = np.mean([f_func_i(k / P) for k in range(P)])
    multi_results.append({
        'name': f_name_i,
        'true': f_true_i,
        'riemann': riemann_i,
        'estimates': estimates_i,
        'all_equal': np.all(estimates_i == estimates_i[0]),
    })
    print(f"  {f_name_i:12s}: true={f_true_i:.6f}  riemann={riemann_i:.6f}  "
          f"all_keys_equal={multi_results[-1]['all_equal']}")


# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------

print("\nPlotting ...")

fig = plt.figure(figsize=(22, 18))
fig.patch.set_facecolor('#0a0a0a')
gs = fig.add_gridspec(2, 2, hspace=0.28, wspace=0.25)

# --- Panel 1: 10 keys converging ---
ax1 = fig.add_subplot(gs[0, 0])
style(ax1, f'10 keys, same integrand: f(x) = {integrands[0][0]}',
      xlabel='sample size N', ylabel='|MC estimate − true|')

for k, errs in enumerate(key_curves):
    ax1.semilogy(sample_sizes, errs, color=COLORS_10[k],
                 linewidth=1, alpha=0.7, label=f'key {k}')

ax1.axvline(P, color=RED, linewidth=1.5, linestyle=':',
            label=f'N = P = {P}')
ax1.axhline(riemann_error, color=WHITE, linewidth=1, linestyle='--',
            alpha=0.5, label=f'Riemann floor ({riemann_error:.1e})')
ax1.legend(facecolor='#1a1a1a', edgecolor='#333', labelcolor=WHITE,
           fontsize=7, ncol=2)

# --- Panel 2: Histogram of N=P estimates ---
ax2 = fig.add_subplot(gs[0, 1])
style(ax2, f'{n_keys} keys: MC estimate at N = P = {P}',
      xlabel=f'estimate of ∫ {integrands[0][0]} dx',
      ylabel='count')

# Data has near-zero spread (all keys produce the same sum), so a
# standard histogram would fail. Use a narrow fixed range centered on
# the Riemann sum and a single bin to show the spike.
hw = max(abs(f_true - riemann_sum) * 3, 1e-5)
center = riemann_sum
ax2.hist(final_estimates, bins=1,
         range=(center - hw, center + hw),
         color=YELLOW, edgecolor='none', alpha=0.8)
ax2.axvline(f_true, color=RED, linewidth=2, linestyle='-',
            label=f'true = {f_true:.6f}')
ax2.axvline(riemann_sum, color=WHITE, linewidth=2, linestyle='--',
            label=f'Riemann = {riemann_sum:.6f}')

# Annotate: all values are identical
spread = final_estimates.max() - final_estimates.min()
ax2.text(0.98, 0.95,
         f'spread across {n_keys} keys:\n{spread:.2e}\n'
         f'({"zero — key cancels" if spread == 0 else "near-zero"})',
         transform=ax2.transAxes, color=WHITE, fontsize=10,
         ha='right', va='top',
         bbox=dict(boxstyle='round', facecolor='#1a1a1a', edgecolor='#333'))
ax2.legend(facecolor='#1a1a1a', edgecolor='#333', labelcolor=WHITE,
           fontsize=9)

# --- Panel 3: Riemann error vs P ---
ax3 = fig.add_subplot(gs[1, 0])
style(ax3, f'Riemann sum error vs P for f(x) = {integrands[0][0]}',
      xlabel='P (period = number of bins)', ylabel='|Riemann sum − true|')

ax3.loglog(P_values, riemann_errors, 'o-', color=YELLOW, linewidth=1.5,
           markersize=5, label='Riemann error')
# O(1/P^2) reference
ref_P = np.array(P_values, dtype=float)
ref = riemann_errors[0] * (P_values[0] / ref_P)**2
ax3.loglog(P_values, ref, color='#555', linewidth=1, linestyle='--',
           label='O(1/P²) reference')
ax3.legend(facecolor='#1a1a1a', edgecolor='#333', labelcolor=WHITE,
           fontsize=9)

# --- Panel 4: Multiple integrands bar chart ---
ax4 = fig.add_subplot(gs[1, 1])
style(ax4, f'Key-independence across 5 integrands (P={P}, 50 keys each)',
      ylabel='estimate at N = P')

x_pos = np.arange(len(integrands))
bar_width = 0.35

true_vals = [r['true'] for r in multi_results]
riemann_vals = [r['riemann'] for r in multi_results]
names = [r['name'] for r in multi_results]

bars1 = ax4.bar(x_pos - bar_width/2, true_vals, bar_width,
                color=RED, alpha=0.8, label='true integral')
bars2 = ax4.bar(x_pos + bar_width/2, riemann_vals, bar_width,
                color=YELLOW, alpha=0.8, label=f'all 50 keys at N=P={P}')

ax4.set_xticks(x_pos)
ax4.set_xticklabels(names, color=WHITE, fontsize=9)
ax4.legend(facecolor='#1a1a1a', edgecolor='#333', labelcolor=WHITE,
           fontsize=9)

# Annotate each pair with the error
for i, r in enumerate(multi_results):
    err = abs(r['riemann'] - r['true'])
    ax4.text(i, max(r['true'], r['riemann']) + 0.01,
             f'Δ={err:.1e}', ha='center', va='bottom',
             color=WHITE, fontsize=8)

plt.savefig(os.path.join(HERE, 'riemann_proof.png'),
            dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
print("-> riemann_proof.png")

# ---------------------------------------------------------------------------
# The argument, printed
# ---------------------------------------------------------------------------

print(f"""
════════════════════════════════════════════════════════════════
THE ARGUMENT
════════════════════════════════════════════════════════════════

bidder.cipher(P, key) returns a permutation π of [0, P).

At N = P, the MC estimate is:

    (1/P) Σ f(π(i) / P)  for i = 0..P-1

But Σ over a permutation of S = Σ over S. So:

    (1/P) Σ f(k / P)  for k = 0..P-1

This is the Riemann sum of f on [0, 1) with P equal-width bins.
The key disappears — every key gives the same sum at N = P.

Empirical confirmation:
  - {n_keys} different keys all produced {final_estimates[0]:.10f}
  - Spread across keys: {spread:.2e}
  - True integral:      {f_true:.10f}
  - Riemann sum:        {riemann_sum:.10f}
  - Riemann error:      {riemann_error:.2e}

The Riemann-sum error is O(1/P) for generic f (left-endpoint rule).
For sin(πx) it is O(1/P²) because f(0) = f(1) = 0 (endpoint
cancellation; see Euler–Maclaurin in core/RIEMANN-SUM.md).
At P = {P} the error is {riemann_error:.2e}.
At P = 20000 it would be {riemann_errors[-1]:.2e}.
The floor is structural, not statistical — it does not depend
on the key, only on P and the integrand.
════════════════════════════════════════════════════════════════
""")
