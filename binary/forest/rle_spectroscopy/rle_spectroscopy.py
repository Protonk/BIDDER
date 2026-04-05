"""
rle_spectroscopy.py — run-length spectrogram of binary Champernowne streams

For each monoid n = 1..256, generate 10,000 bits of binary Champernowne
stream, compute RLE, and plot 0-run and 1-run length distributions as
heatmaps. The 2-adic valuation v_2(n) is shown alongside as a color
strip. Algebraic structure — which monoids share the same v_2 — should
appear as horizontal ridges in the 0-run panel.

Prediction: n-primes of monoid n are all divisible by n, so their
trailing zeros in binary are >= v_2(n). Every entry boundary in the
concatenation therefore has a guaranteed 0-run of length >= v_2(n),
terminated by the leading 1 of the next entry. This should create
visible excess at run-length v_2(n) in the 0-run distribution,
stratified by n's 2-adic depth.
"""

import sys, os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..'))       # binary/
sys.path.insert(0, os.path.join(_here, '..', '..', '..')) # project root

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from binary_core import binary_stream, rle


N_MAX = 256
TARGET_BITS = 10_000
MAX_RUN = 16
PRIMES_PER_N = 2000


def v2(n):
    """2-adic valuation of n."""
    if n == 0:
        return 0
    v = 0
    while n % 2 == 0:
        n //= 2
        v += 1
    return v


# ── Compute ──────────────────────────────────────────────────────────

print("Generating binary streams and computing RLE...")

zero_hist = np.zeros((N_MAX, MAX_RUN), dtype=float)
one_hist  = np.zeros((N_MAX, MAX_RUN), dtype=float)

for idx in range(N_MAX):
    n = idx + 1
    if n % 64 == 0:
        print(f"  n = {n}...")

    bits = binary_stream(n, count=PRIMES_PER_N)[:TARGET_BITS]
    runs = rle(bits)

    zc = np.zeros(MAX_RUN, dtype=int)
    oc = np.zeros(MAX_RUN, dtype=int)

    for val, length in runs:
        k = min(length, MAX_RUN) - 1   # bin index, capped
        if val == 0:
            zc[k] += 1
        else:
            oc[k] += 1

    zt = zc.sum()
    ot = oc.sum()
    if zt > 0:
        zero_hist[idx] = zc / zt
    if ot > 0:
        one_hist[idx] = oc / ot

v2_arr = np.array([v2(n) for n in range(1, N_MAX + 1)])
max_v2 = int(v2_arr.max())


# ── Plot ─────────────────────────────────────────────────────────────

print("Plotting...")

fig = plt.figure(figsize=(22, 13))
fig.patch.set_facecolor('#0a0a0a')

gs = fig.add_gridspec(1, 4, width_ratios=[1, 10, 10, 0.5], wspace=0.06)
ax_v  = fig.add_subplot(gs[0])
ax0   = fig.add_subplot(gs[1])
ax1   = fig.add_subplot(gs[2])
ax_cb = fig.add_subplot(gs[3])

FLOOR = 1e-5

# ── v_2 strip ────────────────────────────────────────────────────────

ax_v.set_facecolor('#0a0a0a')
v2_img = v2_arr.reshape(-1, 1)
ax_v.imshow(v2_img, aspect='auto', cmap='YlOrRd', vmin=0, vmax=max_v2,
            interpolation='nearest', origin='lower',
            extent=[0, 1, 1, N_MAX + 1])
ax_v.set_xticks([])
ax_v.set_ylabel('n', color='white', fontsize=12)
ax_v.set_title('$\\nu_2(n)$', color='white', fontsize=11, pad=10)
ax_v.tick_params(colors='white', labelsize=9)

# mark powers of 2
pow2 = [2**k for k in range(0, 9) if 2**k <= N_MAX]
ax_v.set_yticks(pow2)
ax_v.set_yticklabels([str(p) for p in pow2])

for spine in ax_v.spines.values():
    spine.set_color('#333')

# ── heatmaps ─────────────────────────────────────────────────────────

norm = LogNorm(vmin=1e-4, vmax=1.0)

for ax, data, title in [
    (ax0, zero_hist, '0-runs'),
    (ax1, one_hist, '1-runs'),
]:
    ax.set_facecolor('#0a0a0a')
    safe = np.clip(data, FLOOR, None)
    im = ax.imshow(safe, aspect='auto', cmap='inferno', norm=norm,
                   interpolation='nearest', origin='lower',
                   extent=[0.5, MAX_RUN + 0.5, 1, N_MAX + 1])
    ax.set_xlabel('run length', color='white', fontsize=11)
    ax.set_title(title, color='white', fontsize=13, pad=10)
    ax.set_xticks(range(1, MAX_RUN + 1, 2))
    ax.tick_params(colors='white', labelsize=9)

    # horizontal guides at powers of 2
    for p in pow2:
        ax.axhline(y=p, color='white', linewidth=0.3, alpha=0.25)

    for spine in ax.spines.values():
        spine.set_color('#333')

ax0.set_ylabel('n', color='white', fontsize=12)
ax0.set_yticks(pow2)
ax0.set_yticklabels([str(p) for p in pow2])
ax1.set_yticks([])

# ── colorbar ─────────────────────────────────────────────────────────

cb = fig.colorbar(im, cax=ax_cb)
cb.set_label('frequency', color='white', fontsize=11)
cb.ax.tick_params(colors='white', labelsize=9)

# ── title ────────────────────────────────────────────────────────────

fig.suptitle(
    'RLE Spectroscopy: run-length distributions of binary Champernowne streams',
    color='white', fontsize=15, y=0.97
)

plt.savefig('rle_spectroscopy.png', dpi=200, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> rle_spectroscopy.png")
