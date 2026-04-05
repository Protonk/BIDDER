"""
Significand carpet — sliding-window significands of n-Champernowne digit streams.

Each row is one monoid n.  A window of W consecutive digits is read as a
fraction in [0, 1) and mapped to a continuous colormap.  Where the window
sits inside one n-prime, the color is smooth and predictable.  Where it
straddles a boundary between consecutive primes, the significand encodes a
blend — creating visible seams in the carpet.

The moiré between the fixed window width and the variable n-prime digit
lengths produces interference fringes invisible in the raw digit fabric.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', '..', '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from acm_core import acm_n_primes

N_ROWS   = 600    # n = 1..600
N_DIGITS = 80     # raw digit positions
W        = 4      # window width

# ── build digit fabric (same as digit_fabric.py) ─────────────────────

print("Building digit strings …")
fabric = np.zeros((N_ROWS, N_DIGITS), dtype=int)

for i, n in enumerate(range(1, N_ROWS + 1)):
    ps = acm_n_primes(n, 40)
    s = ''.join(str(p) for p in ps)
    for j, ch in enumerate(s[:N_DIGITS]):
        fabric[i, j] = int(ch)

# ── sliding-window significand ───────────────────────────────────────

print(f"Computing {W}-digit sliding-window significands …")
N_WIN = N_DIGITS - W + 1           # 77 valid window positions
powers = 10 ** np.arange(W - 1, -1, -1)   # [1000, 100, 10, 1]

sig = np.zeros((N_ROWS, N_WIN))
for j in range(N_WIN):
    sig[:, j] = np.dot(fabric[:, j:j + W], powers) / 10**W

# ── plot ─────────────────────────────────────────────────────────────

print("Plotting …")
fig, ax = plt.subplots(figsize=(20, 14))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

im = ax.imshow(sig, aspect='auto', cmap='inferno', vmin=0, vmax=1,
               interpolation='nearest', origin='lower',
               extent=[0, N_WIN, 1, N_ROWS])

ax.axis('off')

out = os.path.join(os.path.dirname(__file__), 'significand_carpet.png')
plt.savefig(out, dpi=300, facecolor='#0a0a0a', bbox_inches='tight',
            pad_inches=0)
print(f'-> {out}')
