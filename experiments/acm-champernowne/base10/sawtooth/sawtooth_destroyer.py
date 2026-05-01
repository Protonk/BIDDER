"""
sawtooth_destroyer.py — apply a Benford leading-digit destroyer
directly to the BIDDER sawtooth `C(n) = 1.[n][2n][3n][4n][5n]`.

The original sawtooth gets its decade-locked structure from the
algebraic correlation between the leading digits of the five atoms
`n, 2n, 3n, 4n, 5n`. Replace each atom's leading digit with an
independent Benford sample (digit count and trailing digits
preserved) and the construction loses its bin-2 lens:

  - the within-decade sawtooth pattern dies;
  - the running mean drifts away from 7/4 to a Benford-weighted
    attractor;
  - decade self-similarity dies.

Output:
  sawtooth_destroyer.png    raw C(n) and M(n) before/after destroyer
"""

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'core'))
from acm_core import acm_n_primes


N_MAX = 100_000
RNG = np.random.default_rng(20260430)
HERE = os.path.dirname(os.path.abspath(__file__))

BENFORD_P = np.log10(1 + 1.0 / np.arange(1, 10))
BENFORD_P = BENFORD_P / BENFORD_P.sum()


def C_original(n: int) -> float:
    primes = acm_n_primes(int(n), 5)
    digits = ''.join(str(int(p)) for p in primes)
    return float('1.' + digits)


def C_destroyed(n: int, rng: np.random.Generator) -> float:
    primes = acm_n_primes(int(n), 5)
    parts = []
    for p in primes:
        s = str(int(p))
        new_lead = int(rng.choice(np.arange(1, 10), p=BENFORD_P))
        parts.append(str(new_lead) + s[1:])
    return float('1.' + ''.join(parts))


print(f"Computing C(n) and C_destroyed(n) for n ∈ [1, {N_MAX}]...")
ns = np.arange(1, N_MAX + 1)
C_orig = np.empty(len(ns))
C_dest = np.empty(len(ns))
for i, n in enumerate(ns):
    C_orig[i] = C_original(int(n))
    C_dest[i] = C_destroyed(int(n), RNG)
    if (i + 1) % 20000 == 0:
        print(f"  n = {i+1}/{N_MAX}")

M_orig = np.cumsum(C_orig) / np.arange(1, len(ns) + 1)
M_dest = np.cumsum(C_dest) / np.arange(1, len(ns) + 1)

print(f"\nAsymptotic running means at n = {N_MAX}:")
print(f"  M_orig({N_MAX})       = {M_orig[-1]:.6f}    (target 7/4 = 1.75)")
print(f"  M_destroyed({N_MAX})  = {M_dest[-1]:.6f}")
print(f"  shift = {M_dest[-1] - M_orig[-1]:+.6f}")

# Predicted Benford asymptote for C_destroyed:
# Each atom's leading digit is Benford-distributed. The five atoms have
# digit-counts d_1..d_5 (= 1+floor(log10(k·n)) for k=1..5). The leading
# digit contributes value E_B[D] = sum_{d=1..9} d · log10(1 + 1/d).
E_B = float(np.sum(np.arange(1, 10) * BENFORD_P))
print(f"  E_Benford[D]          = {E_B:.4f}")

# ── Figure ─────────────────────────────────────────────────────────
fig, axes = plt.subplots(3, 1, figsize=(14, 11), sharex=True)
fig.patch.set_facecolor('#0a0a0a')

# Panel 1: raw C(n) original
ax = axes[0]
ax.set_facecolor('#0a0a0a')
ax.plot(ns, C_orig, '.', markersize=0.4, color='#ffcc5c', alpha=0.6)
ax.set_xscale('log')
ax.set_ylim(1.0, 2.0)
ax.set_ylabel('C(n)  (original)', color='white')
ax.set_title('Original BIDDER sawtooth: C(n) = 1.[n][2n][3n][4n][5n]',
             color='white', fontsize=11)
ax.axhline(1.75, color='#888', linewidth=0.5, linestyle='--')

# Panel 2: C_destroyed(n)
ax = axes[1]
ax.set_facecolor('#0a0a0a')
ax.plot(ns, C_dest, '.', markersize=0.4, color='#6ec6ff', alpha=0.6)
ax.set_xscale('log')
ax.set_ylim(1.0, 2.0)
ax.set_ylabel('C_destroyed(n)', color='white')
ax.set_title(
    'Benford destroyer: each atom\'s leading digit replaced by Benford sample',
    color='white', fontsize=11)
ax.axhline(1.75, color='#888', linewidth=0.5, linestyle='--')

# Panel 3: running means
ax = axes[2]
ax.set_facecolor('#0a0a0a')
ax.plot(ns, M_orig, color='#ffcc5c', linewidth=1.4,
        label=f'M_orig → {M_orig[-1]:.4f} (target 7/4 = 1.75)')
ax.plot(ns, M_dest, color='#6ec6ff', linewidth=1.4,
        label=f'M_destroyed → {M_dest[-1]:.4f}')
ax.axhline(1.75, color='#888', linewidth=0.7, linestyle='--', label='7/4')
ax.set_xscale('log')
ax.set_xlabel('n', color='white')
ax.set_ylabel('running mean', color='white')
ax.set_title('Running means: original converges to 7/4; destroyed drifts',
             color='white', fontsize=11)
ax.legend(loc='lower right', fontsize=10, framealpha=0.3,
          labelcolor='white', facecolor='#1a1a1a')
ax.grid(True, color='#222', linewidth=0.4, which='both')

for a in axes:
    a.tick_params(colors='white', labelsize=9)
    for spine in a.spines.values():
        spine.set_color('#333')

fig.tight_layout()
fig.savefig(os.path.join(HERE, 'sawtooth_destroyer.png'), dpi=180,
            facecolor='#0a0a0a', bbox_inches='tight')
print("\n-> sawtooth_destroyer.png")

# ── Decade-fold figure: scatter (u, C) for both ────────────────────
log_floor = np.floor(np.log10(ns)).astype(int)
u_vals = ns / 10.0 ** log_floor   # u ∈ [1, 10)

fig2, ax = plt.subplots(figsize=(11, 6))
fig2.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')
ax.plot(u_vals, C_orig, '.', markersize=0.4, color='#ffcc5c', alpha=0.5,
        label='C_orig (decade-folded)')
ax.plot(u_vals, C_dest, '.', markersize=0.4, color='#6ec6ff', alpha=0.3,
        label='C_destroyed (decade-folded)')
for u_break in (2, 2.5, 10/3, 5):
    ax.axvline(u_break, color='#888', linewidth=0.4, linestyle=':', alpha=0.6)
ax.set_xlim(1, 10)
ax.set_ylim(1.0, 2.0)
ax.set_xlabel('u = n / 10^floor(log10 n)', color='white')
ax.set_ylabel('C(n)', color='white')
ax.set_title(
    'Decade fold: original keeps its tooth (yellow), destroyed loses it (blue)\n'
    'dotted verticals: theoretical break-points u ∈ {2, 5/2, 10/3, 5}',
    color='white', fontsize=11)
ax.legend(loc='upper right', fontsize=10, framealpha=0.3,
          labelcolor='white', facecolor='#1a1a1a',
          markerscale=20)
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_color('#333')
ax.grid(True, color='#222', linewidth=0.4)
fig2.tight_layout()
fig2.savefig(os.path.join(HERE, 'sawtooth_destroyer_fold.png'), dpi=180,
             facecolor='#0a0a0a', bbox_inches='tight')
print("-> sawtooth_destroyer_fold.png")
