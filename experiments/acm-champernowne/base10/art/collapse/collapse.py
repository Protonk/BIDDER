"""
Collapse plot — rescaled overlay of uniformity sawtooth cycles.

Each cycle runs between consecutive digit-block boundaries
(9 → 99 → 999 → …).  Within each cycle, x is normalized to [0, 1]
and y is divided by the cycle's peak deviation.  If the sawtooth is
self-similar, all curves collapse onto one universal shape.

The theoretical limiting curve is derived analytically:

    max_dev(t) = max_j |9·c_j(t) − 9t| / (9·(1 + 9t))

where c_j(t) = clamp(9t − (j−1), 0, 1) is the fractional contribution
of digit j at normalized position t.  This limit is exact as d → ∞
and independent of the cycle index.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'core'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ── computation ──────────────────────────────────────────────────────

def max_deviation_array(N):
    """Vectorized running max |freq(d) − 1/9| for n = 1 … N."""
    ns = np.arange(1, N + 1)
    exps = np.floor(np.log10(ns)).astype(int)
    digits = (ns // 10**exps).astype(int)
    cum = np.zeros((9, N))
    for d in range(1, 10):
        cum[d - 1] = np.cumsum(digits == d)
    freqs = cum / ns
    return np.max(np.abs(freqs - 1.0 / 9), axis=0)


def theoretical_curve(n_pts=4000):
    """Limiting collapsed shape (d → ∞), independent of cycle index."""
    t = np.linspace(0, 1, n_pts, endpoint=False)[1:]   # skip t=0 (0/0)
    devs = np.zeros((9, len(t)))
    for j in range(1, 10):
        cj = np.clip(9 * t - (j - 1), 0, 1)
        devs[j - 1] = np.abs(9 * cj - 9 * t) / (9 * (1 + 9 * t))
    curve = devs.max(axis=0)
    peak = curve.max()
    return t, curve / peak


# ── parameters ───────────────────────────────────────────────────────

N_CYCLES = 6
N = 10**N_CYCLES - 1          # 999 999

boundaries = [10**d - 1 for d in range(1, N_CYCLES + 1)]
starts     = [1] + [b + 1 for b in boundaries[:-1]]
ends       = boundaries

# ── compute ──────────────────────────────────────────────────────────

print(f"computing deviation for n = 1 … {N:,}")
dev = max_deviation_array(N)

# ── plot ─────────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(10, 5.5))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

cmap = plt.cm.plasma
colors = [cmap(v) for v in np.linspace(0.15, 0.85, N_CYCLES)]

for i, (s, e) in enumerate(zip(starts, ends)):
    seg = dev[s - 1 : e]
    peak = seg.max()
    if peak == 0:
        continue
    t = np.linspace(0, 1, len(seg))
    y = seg / peak

    # thin out long segments for rendering
    MAX_PTS = 5000
    if len(t) > MAX_PTS:
        idx = np.round(np.linspace(0, len(t) - 1, MAX_PTS)).astype(int)
        t, y = t[idx], y[idx]

    ax.plot(t, y, lw=0.7, color=colors[i], alpha=0.85,
            label=f'd={i+1}  ({s:>7,}\u2013{e:>7,})')

# theoretical limit
tt, yy = theoretical_curve()
ax.plot(tt, yy, lw=1.0, color='white', alpha=0.35,
        linestyle='--', label='d\u2009\u2192\u2009\u221e  (theory)')

# chrome
ax.set_xlim(0, 1)
ax.set_ylim(-0.02, 1.05)
ax.set_xlabel('position in cycle (normalized)', color='#666', fontsize=9)
ax.set_ylabel('deviation (peak-normalized)', color='#666', fontsize=9)
ax.tick_params(colors='#444', labelsize=7)
for sp in ax.spines.values():
    sp.set_color('#222')

leg = ax.legend(fontsize=7, facecolor='#111', edgecolor='#333',
                labelcolor='#999', loc='upper right',
                title='cycle (digit class)',
                title_fontproperties={'size': 7})
leg.get_title().set_color('#999')

plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), 'collapse.png')
plt.savefig(out, dpi=250, facecolor='#0a0a0a', bbox_inches='tight')
print(f'-> {out}')
