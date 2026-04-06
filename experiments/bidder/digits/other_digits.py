"""
other_digits.py — Are the other digits uniform?

For base b, digit_class d, the operating block B_d = [b^(d-1), b^d - 1].
Each element has exactly d digits in base b. We extract all d digit
positions and check:

  1. Is each digit position individually uniform? (marginal test)
  2. Is the joint distribution of digit pairs uniform? (independence test)
  3. Does the permutation change any of this? (permuted vs raw)
  4. How does multi-digit extraction affect stratified sampling?

Science first, then art.
"""

import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'generator'))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'core'))

import collections
import numpy as np
import matplotlib.pyplot as plt
from bidder import Bidder


def extract_all_digits(n, base, d):
    """Extract all d digits of n in base b, from leading (pos 0) to trailing (pos d-1)."""
    digits = []
    for _ in range(d):
        digits.append(n % base)
        n //= base
    return list(reversed(digits))  # leading digit first


def full_digit_analysis(base, digit_class, key=b'digit analysis', permuted=True):
    """Extract all digit positions from a full operating block."""
    gen = Bidder(base=base, digit_class=digit_class, key=key)
    period = gen.period
    d = digit_class

    all_digits = np.zeros((period, d), dtype=int)

    for i in range(period):
        idx = gen._permute(i) if permuted else i
        n = gen.block_start + idx
        all_digits[i] = extract_all_digits(n, base, d)

    return all_digits, period, d


def value_range(base, pos):
    return range(1, base) if pos == 0 else range(base)


def occupancy_report(digits, base, positions):
    expected_values = [value_range(base, pos) for pos in positions]
    expected_tuples = list(itertools.product(*expected_values))
    counts = collections.Counter(tuple(row[pos] for pos in positions)
                                 for row in digits)
    expected = len(digits) // len(expected_tuples)
    max_dev = max(abs(counts.get(t, 0) - expected) for t in expected_tuples)
    unseen = sum(1 for t in expected_tuples if counts.get(t, 0) == 0)
    exact = all(counts.get(t, 0) == expected for t in expected_tuples)
    return counts, expected, max_dev, unseen, exact


# =====================================================================
# Analysis 1: Marginal uniformity at each digit position
# =====================================================================

print("=== Marginal uniformity ===\n")

for base, dc in [(10, 2), (10, 3), (10, 4), (16, 2), (16, 3)]:
    raw_digits, period, d = full_digit_analysis(base, dc, permuted=False)
    perm_digits, _, _ = full_digit_analysis(base, dc, permuted=True)
    print(f"base={base}, d={dc}, period={period}")

    for label, digits in [('raw', raw_digits), ('permuted', perm_digits)]:
        for pos in range(d):
            col = digits[:, pos]
            counts = collections.Counter(col.tolist())

            if pos == 0:
                expected = period // (base - 1)
                vals = range(1, base)
                pos_label = f"pos {pos} (leading, {{1..{base-1}}})"
            else:
                expected = period // base
                vals = range(0, base)
                pos_label = f"pos {pos} ({{0..{base-1}}})"

            exact = all(counts.get(v, 0) == expected for v in vals)
            max_dev = max(abs(counts.get(v, 0) - expected) for v in vals)
            print(f"  {label:9s} {pos_label}: expected {expected} each, "
                  f"max deviation {max_dev}, exact={exact}")

    print()


# =====================================================================
# Analysis 2: Joint distribution of digit pairs
# =====================================================================

print("=== Joint (pairwise) uniformity ===\n")

for base, dc in [(10, 3), (10, 4)]:
    raw_digits, period, d = full_digit_analysis(base, dc, permuted=False)
    perm_digits, _, _ = full_digit_analysis(base, dc, permuted=True)
    print(f"base={base}, d={dc}, period={period}")

    for p1 in range(d):
        for p2 in range(p1 + 1, d):
            raw_pairs, expected, raw_max_dev, raw_unseen, raw_exact = (
                occupancy_report(raw_digits, base, (p1, p2)))
            perm_pairs, _, perm_max_dev, perm_unseen, perm_exact = (
                occupancy_report(perm_digits, base, (p1, p2)))
            n_pairs = len(raw_pairs) + raw_unseen
            same_counts = raw_pairs == perm_pairs

            print(f"  pos ({p1},{p2}): expected {expected} each")
            print(f"    raw      : seen {len(raw_pairs)}/{n_pairs}, "
                  f"unseen {raw_unseen}, max_dev={raw_max_dev}, exact={raw_exact}")
            print(f"    permuted : seen {len(perm_pairs)}/{n_pairs}, "
                  f"unseen {perm_unseen}, max_dev={perm_max_dev}, exact={perm_exact}")
            print(f"    raw == permuted counts: {same_counts}")

    raw_tuples, expected, raw_max_dev, raw_unseen, raw_exact = (
        occupancy_report(raw_digits, base, tuple(range(d))))
    perm_tuples, _, perm_max_dev, perm_unseen, perm_exact = (
        occupancy_report(perm_digits, base, tuple(range(d))))
    print(f"  full tuples: expected {expected} each")
    print(f"    raw      : seen {len(raw_tuples)}/{period}, unseen {raw_unseen}, "
          f"max_dev={raw_max_dev}, exact={raw_exact}")
    print(f"    permuted : seen {len(perm_tuples)}/{period}, unseen {perm_unseen}, "
          f"max_dev={perm_max_dev}, exact={perm_exact}")
    print(f"    raw == permuted counts: {raw_tuples == perm_tuples}")

    print()


# =====================================================================
# Analysis 3: Multi-digit extraction for stratified sampling
# =====================================================================

print("=== Multi-digit stratified sampling ===\n")

def integrate_multdigit(func, true_val, base, dc, key, n_samples):
    """Integrate using all d digits from each Bidder evaluation."""
    digits, period, d = full_digit_analysis(base, dc, key)
    # Use first n_samples evaluations, extract all d digits as samples
    samples = []
    for i in range(min(n_samples, period)):
        for pos in range(d):
            dig = digits[i, pos]
            if pos == 0:
                # Leading digit in {1, ..., b-1} -> map to stratum center
                x = (dig - 0.5) / (base - 1)
            else:
                # Other digit in {0, ..., b-1} -> map to stratum center
                x = (dig + 0.5) / base
            samples.append(x)
    samples = np.array(samples[:n_samples * d])
    return np.mean(func(samples))

def f_test(x): return np.sin(np.pi * x)
true_val = 2.0 / np.pi

for base, dc in [(10, 3), (10, 4)]:
    gen = Bidder(base=base, digit_class=dc, key=b'strat multi')
    period = gen.period
    d = dc

    # Single-digit: d evaluations, 1 sample each
    single_samples = np.array([(v - 0.5) / (base - 1)
                               for v in [gen.next() for _ in range(period)]])
    est_single = np.mean(f_test(single_samples))

    # Multi-digit: period/d evaluations, d samples each
    est_multi = integrate_multdigit(f_test, true_val, base, dc,
                                    b'strat multi', period // d)

    print(f"base={base}, d={dc}, period={period}")
    print(f"  True value:     {true_val:.10f}")
    print(f"  Single-digit:   {est_single:.10f}  "
          f"(error {abs(est_single - true_val):.2e}, {period} evals)")
    print(f"  Multi-digit:    {est_multi:.10f}  "
          f"(error {abs(est_multi - true_val):.2e}, {period//d} evals)")
    print()


# =====================================================================
# Visualization: digit-position heatmaps
# =====================================================================

print("Plotting science view...")

base, dc = 10, 4
digits, period, d = full_digit_analysis(base, dc, key=b'viz', permuted=True)

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.patch.set_facecolor('#0a0a0a')
fig.suptitle(f'Digit position analysis: base {base}, d={dc}, period={period}',
             color='white', fontsize=15, y=0.98)

# Panel 1: Marginal histograms for each position
ax = axes[0, 0]
ax.set_facecolor('#0a0a0a')
bar_width = 0.2
colors = ['#ff6f61', '#ffcc5c', '#88d8b0', '#6ec6ff']
for pos in range(d):
    col = digits[:, pos]
    if pos == 0:
        vals = range(1, base)
        expected = period // (base - 1)
    else:
        vals = range(0, base)
        expected = period // base
    counts = [np.sum(col == v) for v in vals]
    x = np.array(list(vals)) + (pos - 1.5) * bar_width
    ax.bar(x, counts, width=bar_width, color=colors[pos],
           alpha=0.8, label=f'pos {pos}')
    ax.axhline(y=expected, color=colors[pos], linewidth=0.5,
               linestyle='--', alpha=0.5)
ax.set_xlabel('digit value', color='white')
ax.set_ylabel('count', color='white')
ax.set_title('Marginal counts per position', color='white', fontsize=12)
ax.legend(fontsize=9, framealpha=0.3, labelcolor='white', facecolor='#1a1a1a')
ax.tick_params(colors='white')

# Panel 2: Joint heatmap (pos 0 vs pos 1)
ax = axes[0, 1]
ax.set_facecolor('#0a0a0a')
joint = np.zeros((base, base))
for i in range(period):
    joint[digits[i, 0], digits[i, 1]] += 1
im = ax.imshow(joint[1:, :], aspect='auto', cmap='inferno',
               interpolation='nearest', origin='lower',
               extent=[-0.5, base - 0.5, 0.5, base - 0.5])
ax.set_xlabel('pos 1 digit', color='white')
ax.set_ylabel('pos 0 digit (leading)', color='white')
ax.set_title('Joint: pos 0 vs pos 1', color='white', fontsize=12)
ax.tick_params(colors='white')
plt.colorbar(im, ax=ax, pad=0.02).ax.tick_params(colors='white')

# Panel 3: Joint heatmap (pos 1 vs pos 2)
ax = axes[1, 0]
ax.set_facecolor('#0a0a0a')
joint12 = np.zeros((base, base))
for i in range(period):
    joint12[digits[i, 1], digits[i, 2]] += 1
im2 = ax.imshow(joint12, aspect='auto', cmap='inferno',
                interpolation='nearest', origin='lower',
                extent=[-0.5, base - 0.5, -0.5, base - 0.5])
ax.set_xlabel('pos 2 digit', color='white')
ax.set_ylabel('pos 1 digit', color='white')
ax.set_title('Joint: pos 1 vs pos 2', color='white', fontsize=12)
ax.tick_params(colors='white')
plt.colorbar(im2, ax=ax, pad=0.02).ax.tick_params(colors='white')

# Panel 4: Running deviation per position
ax = axes[1, 1]
ax.set_facecolor('#0a0a0a')
for pos in range(d):
    col = digits[:, pos]
    if pos == 0:
        n_vals = base - 1
    else:
        n_vals = base
    target = 1.0 / n_vals
    running_counts = np.zeros(base, dtype=int)
    dev = np.empty(period)
    start = 1 if pos == 0 else 0
    for i in range(period):
        running_counts[col[i]] += 1
        fracs = running_counts[start:base] / (i + 1)
        dev[i] = np.max(np.abs(fracs - target))
    ax.semilogx(np.arange(1, period + 1), dev,
                linewidth=0.4, color=colors[pos], alpha=0.8,
                label=f'pos {pos}')
ax.set_xlabel('outputs', color='white')
ax.set_ylabel('max deviation', color='white')
ax.set_title('Running deviation per position', color='white', fontsize=12)
ax.legend(fontsize=9, framealpha=0.3, labelcolor='white', facecolor='#1a1a1a')
ax.tick_params(colors='white')

plt.tight_layout()
plt.savefig('other_digits_science.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> other_digits_science.png")


# =====================================================================
# Art: the digit fabric of ALL positions, interleaved
# =====================================================================

print("Plotting art view...")

base_art, dc_art = 10, 4
digits_art, period_art, d_art = full_digit_analysis(base_art, dc_art,
                                                      key=b'art')

# Interleave: for each Bidder evaluation, lay out all d digits in sequence.
# Row = evaluation index, column = digit position within that evaluation.
# Then tile multiple evaluations per row for width.
n_evals = 600
n_cols = d_art  # 4 digits per evaluation

fabric = digits_art[:n_evals, :]  # (600, 4)

# Also build a wider fabric: 50 evaluations per row, 4 digits each = 200 cols
evals_per_row = 50
n_rows = n_evals // evals_per_row
wide_fabric = np.zeros((n_rows, evals_per_row * d_art), dtype=int)
for r in range(n_rows):
    for c in range(evals_per_row):
        idx = r * evals_per_row + c
        if idx < period_art:
            wide_fabric[r, c * d_art:(c + 1) * d_art] = digits_art[idx]

digit_colors_rgb = np.array([
    [0.102, 0.102, 0.180],  # 0 — deep navy
    [0.906, 0.298, 0.235],  # 1 — red
    [0.902, 0.494, 0.133],  # 2 — orange
    [0.945, 0.769, 0.059],  # 3 — gold
    [0.180, 0.800, 0.443],  # 4 — green
    [0.102, 0.737, 0.612],  # 5 — teal
    [0.204, 0.596, 0.859],  # 6 — blue
    [0.608, 0.349, 0.714],  # 7 — purple
    [0.914, 0.118, 0.561],  # 8 — magenta
    [0.926, 0.941, 0.945],  # 9 — near-white
])

from matplotlib.colors import ListedColormap
cmap = ListedColormap(digit_colors_rgb)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 14),
                                gridspec_kw={'width_ratios': [1, 4]})
fig.patch.set_facecolor('#0a0a0a')

# Left: narrow fabric (eval x position)
ax1.set_facecolor('#0a0a0a')
ax1.imshow(fabric, cmap=cmap, vmin=0, vmax=9,
           interpolation='nearest', aspect='auto', origin='lower')
ax1.set_xlabel('digit position', color='white', fontsize=11)
ax1.set_ylabel('evaluation', color='white', fontsize=11)
ax1.set_xticks(range(d_art))
ax1.set_xticklabels(['lead', 'd₁', 'd₂', 'd₃'])
ax1.set_title('Digits per evaluation', color='white', fontsize=13, pad=10)
ax1.tick_params(colors='white')

# Right: wide fabric (interleaved stream)
ax2.set_facecolor('#0a0a0a')
ax2.imshow(wide_fabric, cmap=cmap, vmin=0, vmax=9,
           interpolation='nearest', aspect='auto', origin='lower')
ax2.set_xlabel('interleaved digit stream', color='white', fontsize=11)
ax2.set_ylabel('row', color='white', fontsize=11)
ax2.set_title('Multi-digit fabric (4 digits per evaluation, 50 per row)',
              color='white', fontsize=13, pad=10)
ax2.tick_params(colors='white')

# Mark every 4th column in the wide fabric (evaluation boundaries)
for c in range(0, evals_per_row * d_art, d_art):
    ax2.axvline(x=c - 0.5, color='white', linewidth=0.1, alpha=0.2)

plt.tight_layout()
plt.savefig('other_digits_art.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> other_digits_art.png")
