"""
crossing_angles_deep.py — crossing angles between sawtooth and running mean

Uses the approximation C_2(n) ≈ 1 + n/2^d for speed, allowing us to
go to large n and collect many crossings. Two families emerge:
  - saw↑: sawtooth rising through the mean (mid-tooth). Angles halve.
  - saw↓: sawtooth dropping through the mean (tooth boundary). Angles
    converge to arctan(1/4) ≈ 14.04°.
"""

import sys, os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..'))             # binary/
sys.path.insert(0, os.path.join(_here, '..', '..', '..', 'core'))  # core/

import numpy as np
import matplotlib.pyplot as plt


N_MAX = 500_000  # go deep

print("Computing approximate sawtooth and running mean...")
ns = np.arange(1, N_MAX + 1, dtype=float)

# Bit lengths
bit_lengths = np.floor(np.log2(ns)).astype(int) + 1

# Approximate C_2(n) ≈ 1 + n / 2^d
c2 = 1.0 + ns / (2.0 ** bit_lengths)

# Running mean
run_mean = np.cumsum(c2) / np.arange(1, N_MAX + 1, dtype=float)

# Difference
diff = c2 - run_mean

# Find crossings
print("Finding crossings...")
sign_changes = np.where(diff[:-1] * diff[1:] < 0)[0]

crossings_up = []    # saw↑: sawtooth rises through mean
crossings_down = []  # saw↓: sawtooth drops through mean

for i in sign_changes:
    # Interpolate crossing position
    t = diff[i] / (diff[i] - diff[i + 1])
    n_cross = ns[i] + t

    # Slopes via central difference
    if i >= 1 and i < N_MAX - 2:
        saw_slope = (c2[i + 1] - c2[i - 1]) / 2.0
        mean_slope = (run_mean[i + 1] - run_mean[i - 1]) / 2.0
    else:
        saw_slope = c2[min(i + 1, N_MAX - 1)] - c2[i]
        mean_slope = run_mean[min(i + 1, N_MAX - 1)] - run_mean[i]

    # Angle
    denom = 1.0 + saw_slope * mean_slope
    if abs(denom) < 1e-15:
        angle = 90.0
    else:
        angle = np.degrees(np.arctan(abs(saw_slope - mean_slope) / denom))

    if diff[i] < 0:  # was below, now above → saw↑
        crossings_up.append((n_cross, angle))
    else:             # was above, now below → saw↓
        crossings_down.append((n_cross, angle))

print(f"  saw↑: {len(crossings_up)} crossings")
print(f"  saw↓: {len(crossings_down)} crossings")

# Theoretical limit for saw↓
limit_angle = np.degrees(np.arctan(0.25))

# ── Plot ─────────────────────────────────────────────────────────────

print("Plotting...")

fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(16, 10),
                                      gridspec_kw={'height_ratios': [1, 1]})
fig.patch.set_facecolor('#0a0a0a')

# ── Top panel: both families vs crossing n (log x) ───────────────────

ax = ax_top
ax.set_facecolor('#0a0a0a')

if crossings_down:
    n_down, ang_down = zip(*crossings_down)
    ax.plot(n_down, ang_down, 'o-', color='#ff6f61', markersize=4,
            linewidth=1.0, alpha=0.9, label='saw↓ (tooth boundary)')

if crossings_up:
    n_up, ang_up = zip(*crossings_up)
    ax.plot(n_up, ang_up, 's-', color='#88d8b0', markersize=4,
            linewidth=1.0, alpha=0.9, label='saw↑ (mid-tooth)')

ax.axhline(y=limit_angle, color='#ffcc5c', linewidth=0.8, alpha=0.5,
           linestyle='--', label=f'arctan(1/4) = {limit_angle:.2f}°')

ax.set_xscale('log')
ax.set_xlabel('n at crossing', color='white', fontsize=11)
ax.set_ylabel('angle (degrees)', color='white', fontsize=11)
ax.set_title('Crossing angles: sawtooth vs. running mean',
             color='white', fontsize=14, pad=10)
ax.legend(loc='right', fontsize=9, framealpha=0.3,
          facecolor='#1a1a1a', edgecolor='#333', labelcolor='white')
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('#333')

# ── Bottom panel: both families vs crossing index ────────────────────

ax = ax_bot
ax.set_facecolor('#0a0a0a')

if crossings_down:
    ax.semilogy(range(1, len(ang_down) + 1), ang_down, 'o-',
                color='#ff6f61', markersize=4, linewidth=1.0, alpha=0.9,
                label='saw↓ (converges to limit)')

if crossings_up:
    ax.semilogy(range(1, len(ang_up) + 1), ang_up, 's-',
                color='#88d8b0', markersize=4, linewidth=1.0, alpha=0.9,
                label='saw↑ (halves each time)')

ax.axhline(y=limit_angle, color='#ffcc5c', linewidth=0.8, alpha=0.5,
           linestyle='--', label=f'limit = {limit_angle:.2f}°')

ax.set_xlabel('crossing index (within family)', color='white', fontsize=11)
ax.set_ylabel('angle (degrees, log scale)', color='white', fontsize=11)
ax.set_title('Two families: one vanishes, one persists',
             color='white', fontsize=14, pad=10)
ax.legend(loc='center right', fontsize=9, framealpha=0.3,
          facecolor='#1a1a1a', edgecolor='#333', labelcolor='white')
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('#333')

plt.tight_layout()
plt.savefig('crossing_angles_deep.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> crossing_angles_deep.png")

# ── Table ────────────────────────────────────────────────────────────

print("\nsaw↓ crossings (tooth boundaries — converging):")
print(f"  {'#':>3s}  {'n':>10s}  {'angle':>10s}  {'ratio to prev':>14s}")
for k, (n, a) in enumerate(crossings_down):
    ratio = f"{crossings_down[k-1][1] / a:.4f}" if k > 0 else ""
    print(f"  {k+1:3d}  {n:10.1f}  {a:10.4f}°  {ratio:>14s}")

print(f"\nsaw↑ crossings (mid-tooth — halving):")
print(f"  {'#':>3s}  {'n':>10s}  {'angle':>10s}  {'ratio to prev':>14s}")
for k, (n, a) in enumerate(crossings_up):
    ratio = f"{crossings_up[k-1][1] / a:.4f}" if k > 0 else ""
    print(f"  {k+1:3d}  {n:10.1f}  {a:10.4f}°  {ratio:>14s}")
