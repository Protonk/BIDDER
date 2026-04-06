"""
Filament — expressionist collapse visualization.

Each sawtooth cycle is rendered as a luminous spectral-colored trace.
Additive blending fuses overlapping curves into white heat where they
agree; where early cycles diverge, the filament splits into colored
threads — chromatic aberration at the edge of convergence.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'core'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter


# ── data (same computation as collapse.py) ────────────────────────────

def max_deviation_array(N):
    """Running max |freq(d) − 1/9| for n = 1…N."""
    ns = np.arange(1, N + 1)
    exps = np.floor(np.log10(ns)).astype(int)
    digits = (ns // 10**exps).astype(int)
    cum = np.zeros((9, N))
    for d in range(1, 10):
        cum[d - 1] = np.cumsum(digits == d)
    return np.max(np.abs(cum / ns - 1.0 / 9), axis=0)


N_CYCLES = 6
N = 10**N_CYCLES - 1

print(f"computing deviation  n = 1…{N:,}")
dev = max_deviation_array(N)

boundaries = [10**d - 1 for d in range(1, N_CYCLES + 1)]
starts = [1] + [b + 1 for b in boundaries[:-1]]
ends = boundaries

cycles = []
for s, e in zip(starts, ends):
    seg = dev[s - 1 : e]
    peak = seg.max()
    if peak == 0:
        continue
    t = np.linspace(0, 1, len(seg))
    y = (seg / peak) ** 0.4           # power < 1 opens up the sub-peaks
    MAX_PTS = 5000
    if len(t) > MAX_PTS:
        idx = np.round(np.linspace(0, len(t) - 1, MAX_PTS)).astype(int)
        t, y = t[idx], y[idx]
    cycles.append((t, y))


# ── palette: spectral, balanced so all six sum to neutral white ──────

spectral = [
    (1.0,  0.0,  0.15),   # d=1  red
    (0.9,  0.6,  0.05),   # d=2  orange
    (0.3,  1.0,  0.05),   # d=3  chartreuse
    (0.0,  1.0,  0.55),   # d=4  spring green
    (0.0,  0.2,  1.0),    # d=5  blue
    (0.6,  0.0,  1.0),    # d=6  violet
]  # R, G, B each sum to ≈ 2.8 → neutral white on overlap

# glow stack: wide bloom → sharp core
glow = [
    (18.0, 0.035),
    (8.0,  0.08),
    (3.0,  0.20),
    (1.0,  0.45),
]


# ── additive render ──────────────────────────────────────────────────

W, H, DPI = 3200, 900, 100
FW, FH = W / DPI, H / DPI
XLIM = (-0.005, 1.005)
YLIM = (-0.03, 1.06)

canvas = None

print(f"rendering {len(cycles)} spectral layers …")
for i, (t, y) in enumerate(cycles):
    fig = plt.figure(figsize=(FW, FH), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(XLIM)
    ax.set_ylim(YLIM)
    ax.set_facecolor('black')
    fig.patch.set_facecolor('black')
    ax.axis('off')

    for lw, inten in glow:
        c = tuple(ch * inten for ch in spectral[i])
        ax.plot(t, y, lw=lw, color=c, solid_capstyle='round')

    fig.canvas.draw()
    cw, ch = fig.canvas.get_width_height()
    buf = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
    buf = buf.reshape(ch, cw, 4)[:, :, :3].astype(np.float64) / 255.0

    if canvas is None:
        canvas = np.zeros_like(buf)
    canvas += buf
    plt.close(fig)
    print(f"  d={i+1}  ({cw}×{ch})")


# ── post-processing ──────────────────────────────────────────────────

# three-level bloom: tight halo + mid glow + wide atmospheric
bloom_inner = gaussian_filter(canvas, sigma=[4, 8, 0])
bloom_mid   = gaussian_filter(canvas, sigma=[12, 30, 0])
bloom_outer = gaussian_filter(canvas, sigma=[30, 80, 0])
canvas = canvas + 0.5 * bloom_inner + 0.3 * bloom_mid + 0.15 * bloom_outer

# gamma lift — makes dim outlier wisps more visible
canvas = np.clip(canvas, 0, 1)
canvas = np.power(canvas, 0.7)


# ── save ──────────────────────────────────────────────────────────────

out = os.path.join(os.path.dirname(__file__), 'filament.png')
plt.imsave(out, np.clip(canvas, 0, 1).astype(np.float32))
print(f'-> {out}')
