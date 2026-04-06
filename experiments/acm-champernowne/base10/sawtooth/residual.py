"""
Residual sawtooth experiment.

Subtract the first-order decade template

    T(n) = 1 + n / 10^(floor(log10(n)) + 1)

from C(n) = acm_champernowne_real(n, 5) to isolate the subleading
contribution of the later concatenated blocks.

The top panel shows the raw residual R(n) = C(n) - T(n).
The bottom panel rescales by 10^floor(log10(n)) so the later decades do
not visually collapse to zero.
"""

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'core'))

import numpy as np
import matplotlib.pyplot as plt
from acm_core import acm_champernowne_real


N = 100_000
COUNT = 5

print(f"Computing residual view for C(n), n=1..{N} ...")
vals = np.empty(N)
for i in range(N):
    vals[i] = acm_champernowne_real(i + 1, COUNT)
    if (i + 1) % 10000 == 0:
        print(f"  {i + 1}/{N}")

ns = np.arange(1, N + 1, dtype=np.int64)
decades = np.floor(np.log10(ns)).astype(int)
pow10 = np.power(10.0, decades + 1)
template = 1.0 + ns / pow10
residual = vals - template
scaled = residual * np.power(10.0, decades)

print("Plotting...")
fig, axes = plt.subplots(2, 1, figsize=(18, 10), sharex=True)
fig.patch.set_facecolor('#0a0a0a')

for ax in axes:
    ax.set_facecolor('#0a0a0a')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#333')
    for exp in range(1, 6):
        ax.axvline(x=10**exp, color='white', linewidth=0.4, alpha=0.2)

axes[0].semilogx(
    ns,
    residual,
    linewidth=0.2,
    color='#ffcc5c',
    alpha=0.85,
    rasterized=True,
)
axes[0].axhline(y=0.0, color='#ff6f61', linewidth=0.9, linestyle='--', alpha=0.8)
axes[0].set_ylabel('R(n)', color='white', fontsize=12)
axes[0].set_title(
    'Residual after subtracting the leading decade template',
    color='white',
    fontsize=14,
    pad=10,
)
axes[0].text(
    1.15,
    residual.max() * 0.92,
    r'$R(n)=C(n)-\left(1+\frac{n}{10^{\lfloor \log_{10} n \rfloor + 1}}\right)$',
    color='white',
    fontsize=11,
)

axes[1].semilogx(
    ns,
    scaled,
    linewidth=0.35,
    color='#6ec6ff',
    alpha=0.95,
    rasterized=True,
)
axes[1].axhline(y=0.0, color='#ff6f61', linewidth=0.9, linestyle='--', alpha=0.8)
axes[1].set_ylabel(r'$10^d R(n)$', color='white', fontsize=12)
axes[1].set_xlabel('n', color='white', fontsize=12)
axes[1].set_title(
    'Decade-scaled residual',
    color='white',
    fontsize=13,
    pad=10,
)

axes[0].set_xlim(1, N)

plt.tight_layout()
plt.savefig('residual.png', dpi=300, facecolor='#0a0a0a', bbox_inches='tight')
print('-> residual.png')
