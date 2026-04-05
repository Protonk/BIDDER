"""
Bigram weave — consecutive digit pairs as warp and weft of a textile.

Each cell encodes the pair (d_p, d_{p+1}): current digit and next digit.

    Red   = d_p / 9          (warp — current digit)
    Blue  = d_{p+1} / 9      (weft — next digit)
    Green = |d_p - d_{p+1}| / 9   (twist — local contrast)

The 100-value effective palette reveals the Markov structure of the digit
stream — which transitions the sieve nZ+ permits and which it forbids.
Regions of low contrast (similar consecutive digits) go dark magenta;
high-contrast boundaries glow with green-shifted hues.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', '..', '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from acm_core import n_primes

N_ROWS   = 600    # n = 1..600
N_DIGITS = 80     # raw digit positions

# ── build digit fabric (same as digit_fabric.py) ─────────────────────

print("Building digit strings …")
fabric = np.zeros((N_ROWS, N_DIGITS), dtype=int)

for i, n in enumerate(range(1, N_ROWS + 1)):
    ps = n_primes(n, 40)
    s = ''.join(str(p) for p in ps)
    for j, ch in enumerate(s[:N_DIGITS]):
        fabric[i, j] = int(ch)

# ── bigram channels ──────────────────────────────────────────────────

print("Computing bigram weave …")
d_curr = fabric[:, :-1].astype(np.float64)   # (600, 79)
d_next = fabric[:, 1:].astype(np.float64)    # (600, 79)

red   = d_curr / 9.0                         # warp
blue  = d_next / 9.0                         # weft
green = np.abs(d_curr - d_next) / 9.0        # twist

rgb = np.stack([red, green, blue], axis=-1)   # (600, 79, 3)

# ── plot ─────────────────────────────────────────────────────────────

print("Plotting …")
fig, ax = plt.subplots(figsize=(20, 14))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

ax.imshow(rgb, aspect='auto', interpolation='nearest', origin='lower',
          extent=[0, N_DIGITS - 1, 1, N_ROWS])

ax.set_xlabel('digit position', color='white', fontsize=12)
ax.set_ylabel('n', color='white', fontsize=12)
ax.set_title('Bigram Weave: digit-pair transitions in n-Champernowne strings',
             color='white', fontsize=14, pad=15)
ax.tick_params(colors='white')

out = os.path.join(os.path.dirname(__file__), 'bigram_weave.png')
plt.savefig(out, dpi=300, facecolor='#0a0a0a', bbox_inches='tight')
print(f'-> {out}')
