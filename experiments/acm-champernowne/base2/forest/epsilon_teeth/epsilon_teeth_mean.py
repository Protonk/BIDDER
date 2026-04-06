"""
epsilon_teeth_mean.py — sawtooth, concavity bumps, and running mean

Four panels:
  1. Raw sawtooth: log_2(C_2(n)) vs n
  2. Residual above secant (actual) vs theoretical bump
  3. Theoretical bump vs running-mean bump (does the running mean
     recover the same concavity shape?)
  4. Running mean of C_2(n) approaching 7/4 = 1.75
"""

import sys, os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..'))             # base2/
sys.path.insert(0, os.path.join(_here, '..', '..', '..', '..', '..', 'core'))  # core/

import numpy as np
import matplotlib.pyplot as plt
from acm_core import acm_n_primes


N_MAX = 2000
K = 5


def binary_champernowne_real(n, count=K):
    """C_2(n) = 1.{binary concatenation of first count n-primes}."""
    primes = acm_n_primes(n, count)
    value = 1.0
    pos = 1
    for p in primes:
        for ch in bin(p)[2:]:
            value += int(ch) * 2.0**(-pos)
            pos += 1
    return value


def mantissa_2(n):
    """Base-2 mantissa: m such that n = 2^(d-1) * (1+m), m in [0,1)."""
    if n < 1:
        return 0.0
    d = n.bit_length()
    return n / (2.0**(d - 1)) - 1.0


# ── Compute ──────────────────────────────────────────────────────────

print("Computing binary Champernowne reals...")
ns = np.arange(1, N_MAX + 1)
c2 = np.empty(N_MAX)
for i, n in enumerate(ns):
    if n % 500 == 0:
        print(f"  n = {n}...")
    c2[i] = binary_champernowne_real(n)

log_c2 = np.log2(c2)
run_mean = np.cumsum(c2) / np.arange(1, N_MAX + 1)
log_run_mean = np.log2(run_mean)

mantissas = np.array([mantissa_2(int(n)) for n in ns])
bit_lengths = np.array([int(n).bit_length() for n in ns])

# Per-tooth data-fitted secant and residual
secant = np.empty(N_MAX)
residual_above_secant = np.empty(N_MAX)

for d in range(1, int(bit_lengths.max()) + 1):
    mask = bit_lengths == d
    if not np.any(mask):
        continue
    idx = np.where(mask)[0]
    m_vals = mantissas[idx]
    log_vals = log_c2[idx]
    y0 = log_vals[0]
    y1 = log_vals[-1]
    m0 = m_vals[0]
    m1 = m_vals[-1]
    if m1 > m0:
        slope = (y1 - y0) / (m1 - m0)
        secant[idx] = y0 + slope * (m_vals - m0)
    else:
        secant[idx] = y0
    residual_above_secant[idx] = log_vals - secant[idx]

# Theoretical bump: g(m) = log_2((3+m)/2), secant from g(0) to g(1)
g0 = np.log2(1.5)
g1 = 1.0
bump_theoretical = np.log2((3.0 + mantissas) / 2.0) - g0 - (g1 - g0) * mantissas

# Running-mean bump: per-tooth secant of log_2(running_mean), residual
run_mean_secant = np.empty(N_MAX)
run_mean_bump = np.empty(N_MAX)

for d in range(1, int(bit_lengths.max()) + 1):
    mask = bit_lengths == d
    if not np.any(mask):
        continue
    idx = np.where(mask)[0]
    m_vals = mantissas[idx]
    rm_vals = log_run_mean[idx]
    y0 = rm_vals[0]
    y1 = rm_vals[-1]
    m0 = m_vals[0]
    m1 = m_vals[-1]
    if m1 > m0:
        slope = (y1 - y0) / (m1 - m0)
        run_mean_secant[idx] = y0 + slope * (m_vals - m0)
    else:
        run_mean_secant[idx] = y0
    run_mean_bump[idx] = rm_vals - run_mean_secant[idx]


# ── Plot ─────────────────────────────────────────────────────────────

print("Plotting...")

fig, axes = plt.subplots(4, 1, figsize=(18, 16), sharex=True)
fig.patch.set_facecolor('#0a0a0a')

def style_ax(ax):
    ax.set_facecolor('#0a0a0a')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#333')
    for d in range(1, 13):
        bnd = 2**d
        if bnd <= N_MAX:
            ax.axvline(x=bnd, color='white', linewidth=0.3, alpha=0.2)

# Panel 1: raw sawtooth
ax = axes[0]
style_ax(ax)
ax.plot(ns, log_c2, linewidth=0.5, color='#ffcc5c', alpha=0.9)
ax.set_ylabel('$\\log_2(C_2(n))$', color='white', fontsize=11)
ax.set_title('Binary Champernowne sawtooth', color='white',
             fontsize=13, pad=10)

# Panel 2: actual residual vs theoretical bump
ax = axes[1]
style_ax(ax)
ax.plot(ns, residual_above_secant, linewidth=0.5, color='#ffcc5c',
        alpha=0.9, label='actual residual above secant')
ax.plot(ns, bump_theoretical, linewidth=0.8, color='#ff6f61',
        alpha=0.7, label='theoretical bump of $\\log_2((3+m)/2)$')
ax.axhline(y=0, color='white', linewidth=0.3, alpha=0.25)
ax.set_ylabel('residual above secant', color='white', fontsize=11)
ax.set_title('Sawtooth concavity vs. theoretical bump',
             color='white', fontsize=13, pad=10)
ax.legend(loc='upper right', fontsize=9, framealpha=0.3,
          facecolor='#1a1a1a', edgecolor='#333', labelcolor='white')

# Panel 3: theoretical bump vs running-mean bump
ax = axes[2]
style_ax(ax)
ax.plot(ns, bump_theoretical, linewidth=0.8, color='#ff6f61',
        alpha=0.7, label='theoretical bump')
ax.plot(ns, run_mean_bump, linewidth=0.5, color='#6ec6ff',
        alpha=0.9, label='running mean bump')
ax.axhline(y=0, color='white', linewidth=0.3, alpha=0.25)
ax.set_ylabel('bump amplitude', color='white', fontsize=11)
ax.set_title('Theoretical bump vs. running-mean bump',
             color='white', fontsize=13, pad=10)
ax.legend(loc='upper right', fontsize=9, framealpha=0.3,
          facecolor='#1a1a1a', edgecolor='#333', labelcolor='white')

# Panel 4: running mean approaching 7/4
ax = axes[3]
style_ax(ax)
ax.plot(ns, run_mean, linewidth=0.8, color='#6ec6ff', alpha=0.9,
        label='running mean of $C_2(n)$')
ax.axhline(y=1.75, color='#ff6f61', linewidth=0.8, alpha=0.5,
           linestyle='--', label='$7/4 = 1.75$')
ax.set_xlabel('n', color='white', fontsize=11)
ax.set_ylabel('running mean', color='white', fontsize=11)
ax.set_title('Running mean of binary Champernowne reals',
             color='white', fontsize=13, pad=10)
ax.legend(loc='lower right', fontsize=9, framealpha=0.3,
          facecolor='#1a1a1a', edgecolor='#333', labelcolor='white')

plt.tight_layout()
plt.savefig('epsilon_teeth_mean.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> epsilon_teeth_mean.png")


# ── Summary ──────────────────────────────────────────────────────────

print(f"\nRunning mean at n={N_MAX}: {run_mean[-1]:.6f}  (limit: 1.75)")
print(f"log_2(running mean) at n={N_MAX}: {log_run_mean[-1]:.6f}")

print("\nPer-tooth bump comparison (theoretical vs running-mean):")
print(f"  {'d':>3s}  {'n range':>14s}  {'theo peak':>10s}  {'rm peak':>10s}  {'ratio':>8s}")
for d in range(3, int(bit_lengths.max()) + 1):
    mask = bit_lengths == d
    if not np.any(mask):
        continue
    idx = np.where(mask)[0]
    tp = bump_theoretical[idx].max()
    rp = run_mean_bump[idx].max()
    ratio = rp / tp if tp > 0 else 0
    n_lo = int(ns[idx[0]])
    n_hi = int(ns[idx[-1]])
    print(f"  {d:3d}  {n_lo:>6d}-{n_hi:<6d}  {tp:10.6f}  {rp:10.6f}  {ratio:8.4f}")
