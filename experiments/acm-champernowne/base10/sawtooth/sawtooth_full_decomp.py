"""
sawtooth_full_decomp.py — full destroyer ladder on C(n).

Walks ORIG → six progressively-more-destructive transformations.
Each level kills one more piece of the construction, exposing what
that piece contributes.

Levels (most → least preserved):

  ORIG     full structure                              (baseline)
  PERMUTE  multiset of the 5 leading digits preserved per n,
           but randomly permuted among the 5 atoms
  BENFORD  each atom's leading digit replaced by an independent
           Benford sample (kills both distribution and placement
           of leading digits)
  BIN1     keep n exactly; replace 2n, 3n, 4n, 5n each with an
           independent random integer of the matching digit count
           (kills the multiplicative algebra; preserves n itself
           and the digit-count pattern)
  ATOM     every atom = independent random integer of its target
           digit count (kills algebra + everything that depends
           on n's specific value)
  UNIFORM  C(n) = U[1, 2) (kills everything)

Outputs:
  sawtooth_decomp_folds.png    decade-folded scatter, 6 panels
  sawtooth_decomp_means.png    running means + summary stats
  sawtooth_decomp_summary.txt  numeric readout
"""

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'core'))
from acm_core import acm_n_primes


N_MAX = 30_000
RNG = np.random.default_rng(20260430)
HERE = os.path.dirname(os.path.abspath(__file__))

BENFORD_P = np.log10(1 + 1.0 / np.arange(1, 10))
BENFORD_P /= BENFORD_P.sum()


def _digits(p):
    return str(int(p))


def C_orig(n):
    primes = acm_n_primes(int(n), 5)
    return float('1.' + ''.join(_digits(p) for p in primes))


def C_permute(n, rng):
    """Multiset of leading digits preserved; placement randomised."""
    primes = acm_n_primes(int(n), 5)
    digits = [_digits(p) for p in primes]
    leads = [int(s[0]) for s in digits]
    rng.shuffle(leads)
    return float('1.' + ''.join(str(L) + s[1:]
                                  for L, s in zip(leads, digits)))


def C_benford(n, rng):
    """Each atom's leading digit Benford-resampled."""
    primes = acm_n_primes(int(n), 5)
    parts = []
    for p in primes:
        s = _digits(p)
        new_lead = int(rng.choice(np.arange(1, 10), p=BENFORD_P))
        parts.append(str(new_lead) + s[1:])
    return float('1.' + ''.join(parts))


def C_bin1(n, rng):
    """Keep n exactly; replace atoms 2..5 with random integers of
    matching digit count (kills algebra)."""
    primes = acm_n_primes(int(n), 5)
    parts = [_digits(primes[0])]
    for p in primes[1:]:
        d = len(_digits(p))
        rand_int = int(rng.integers(10 ** (d - 1), 10 ** d))
        parts.append(str(rand_int))
    return float('1.' + ''.join(parts))


def C_atom(n, rng):
    """Each atom = random integer of its target digit count."""
    primes = acm_n_primes(int(n), 5)
    parts = []
    for p in primes:
        d = len(_digits(p))
        rand_int = int(rng.integers(10 ** (d - 1), 10 ** d))
        parts.append(str(rand_int))
    return float('1.' + ''.join(parts))


def C_uniform(n, rng):
    return 1.0 + float(rng.random())


LEVELS = [
    ('ORIG',    C_orig,    None,            '#ffcc5c'),
    ('PERMUTE', C_permute, RNG,             '#a3e4a3'),
    ('BENFORD', C_benford, RNG,             '#6ec6ff'),
    ('BIN1',    C_bin1,    RNG,             '#cf9fff'),
    ('ATOM',    C_atom,    RNG,             '#ff8888'),
    ('UNIFORM', C_uniform, RNG,             '#cccccc'),
]

print(f"Computing all six levels for n ∈ [1, {N_MAX}]...")
ns = np.arange(1, N_MAX + 1)
data = {name: np.empty(len(ns)) for name, _, _, _ in LEVELS}
for i, n in enumerate(ns):
    for name, fn, rng, _ in LEVELS:
        if rng is None:
            data[name][i] = fn(int(n))
        else:
            data[name][i] = fn(int(n), rng)
    if (i + 1) % 5000 == 0:
        print(f"  n = {i+1}/{N_MAX}")

# Running means and summary stats.
M = {name: np.cumsum(data[name]) / np.arange(1, len(ns) + 1)
     for name in data}

print("\nSummary at n = N_MAX:")
print(f"  {'level':<10s}  {'M_final':>10s}  {'std(C)':>10s}  "
      f"{'max(|C - 1.5|)':>15s}")
for name, _, _, _ in LEVELS:
    arr = data[name]
    print(f"  {name:<10s}  {M[name][-1]:10.5f}  "
          f"{float(arr.std()):10.5f}  {float(np.abs(arr - 1.5).max()):15.5f}")

with open(os.path.join(HERE, 'sawtooth_decomp_summary.txt'), 'w') as f:
    f.write(f"sawtooth full decomposition, n ∈ [1, {N_MAX}]\n")
    f.write(f"{'level':<10s}  {'M_final':>10s}  {'std(C)':>10s}\n")
    for name, _, _, _ in LEVELS:
        arr = data[name]
        f.write(f"{name:<10s}  {M[name][-1]:10.5f}  "
                f"{float(arr.std()):10.5f}\n")
print("-> sawtooth_decomp_summary.txt")

# ── Decade-fold scatter, 6 panels ──────────────────────────────────
log_floor = np.floor(np.log10(ns)).astype(int)
u_vals = ns / 10.0 ** log_floor

fig, axes = plt.subplots(3, 2, figsize=(14, 12), sharex=True, sharey=True)
fig.patch.set_facecolor('#0a0a0a')

for ax, (name, _, _, color) in zip(axes.ravel(), LEVELS):
    ax.set_facecolor('#0a0a0a')
    ax.plot(u_vals, data[name], '.', markersize=0.5, color=color, alpha=0.5)
    for u_break in (2, 2.5, 10/3, 5):
        ax.axvline(u_break, color='#666', linewidth=0.4,
                   linestyle=':', alpha=0.5)
    ax.set_xlim(1, 10)
    ax.set_ylim(1.0, 2.0)
    ax.set_title(f'{name}   M = {M[name][-1]:.4f}, '
                 f'std = {float(data[name].std()):.4f}',
                 color='white', fontsize=11)
    ax.tick_params(colors='white', labelsize=8)
    for spine in ax.spines.values():
        spine.set_color('#333')
    ax.grid(True, color='#222', linewidth=0.3)

for ax in axes[-1]:
    ax.set_xlabel('u = n / 10^floor(log10 n)', color='white')
for ax in axes[:, 0]:
    ax.set_ylabel('C(n)', color='white')

fig.suptitle(
    'Decade-fold of C(n) under destroyer ladder — '
    'each level kills one more substrate piece',
    color='white', fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(HERE, 'sawtooth_decomp_folds.png'), dpi=180,
            facecolor='#0a0a0a', bbox_inches='tight')
print("-> sawtooth_decomp_folds.png")

# ── Running means + std bands ──────────────────────────────────────
fig2, ax = plt.subplots(figsize=(12, 6.5))
fig2.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

for name, _, _, color in LEVELS:
    ax.plot(ns, M[name], color=color, linewidth=1.3,
            label=f'{name} → {M[name][-1]:.4f}')

ax.axhline(1.5, color='#888', linewidth=0.7, linestyle='--',
           label='uniform asymptote (1.5)')
ax.axhline(1.0 + np.sum(np.arange(1, 10) * BENFORD_P) / 10,
           color='#666', linewidth=0.5, linestyle=':',
           label=f'Benford-leading asymptote ({1.0 + np.sum(np.arange(1, 10) * BENFORD_P) / 10:.4f})')

ax.set_xscale('log')
ax.set_xlabel('n', color='white')
ax.set_ylabel('running mean of C(n)', color='white')
ax.set_title(
    f'Running means: substrate spectrum under destroyer ladder (n ≤ {N_MAX})',
    color='white', fontsize=11)
ax.legend(loc='lower right', fontsize=9, framealpha=0.4,
          labelcolor='white', facecolor='#1a1a1a', ncol=2)
ax.tick_params(colors='white', labelsize=9)
for spine in ax.spines.values():
    spine.set_color('#333')
ax.grid(True, color='#222', linewidth=0.4, which='both')

fig2.tight_layout()
fig2.savefig(os.path.join(HERE, 'sawtooth_decomp_means.png'), dpi=180,
             facecolor='#0a0a0a', bbox_inches='tight')
print("-> sawtooth_decomp_means.png")
