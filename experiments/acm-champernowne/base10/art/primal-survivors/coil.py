"""
THE COIL — asymptotic bracketing direction as a complex-plane spiral.

Single delicate thread tracing z(W) = (L1_prime_m − L1_bundle) +
i(L1_comp_m − L1_bundle) at the last atom of each W slice, for
W ∈ [5, 50] at fixed n_0=2, K=400. Color encodes W: cool at small
W (the original W=9 pattern), warm at large W (the rotated regime).

The thread approaches the origin around W ≈ 15-20 but does not
pass through. That near-miss is the visual tension.
"""

import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import splprep, splev
from sympy import isprime

K = 400
n_0 = 2
W_VALUES = np.arange(5, 51)


def n_primes_vec(n, k):
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


u9 = np.full(9, 1.0 / 9)


def asymptotic_z(n_0, W, K):
    n_1 = n_0 + W - 1
    parts = [(n, n_primes_vec(n, K))
             for n in range(n_0, n_1 + 1)]
    all_atoms = np.concatenate([arr for _, arr in parts])
    stream_tag = np.concatenate([np.full_like(arr, n)
                                  for n, arr in parts])
    n_atoms = all_atoms.size

    unique_vals, first_idx, counts = np.unique(
        all_atoms, return_index=True, return_counts=True)
    surv_mask = counts == 1
    S = unique_vals[surv_mask]
    sources_S = stream_tag[first_idx[surv_mask]]
    m_S = S // sources_S
    prime_m_arr = np.array([isprime(int(m)) for m in m_S])

    pm_set = set(int(c) for c, pm in zip(S, prime_m_arr) if pm)
    cm_set = set(int(c) for c, pm in zip(S, prime_m_arr) if not pm)

    seen = set()
    cb = np.zeros(9, dtype=np.int64)
    cp = np.zeros(9, dtype=np.int64)
    cc = np.zeros(9, dtype=np.int64)

    for i in range(n_atoms):
        c = int(all_atoms[i])
        if c in seen:
            continue
        seen.add(c)
        log_floor = int(np.floor(np.log10(c)))
        leading = c // 10**log_floor
        cb[leading - 1] += 1
        if c in pm_set:
            cp[leading - 1] += 1
        elif c in cm_set:
            cc[leading - 1] += 1

    pb = cb / cb.sum()
    pp = cp / cp.sum() if cp.sum() > 0 else np.full(9, np.nan)
    pc = cc / cc.sum() if cc.sum() > 0 else np.full(9, np.nan)
    L1_b = float(np.abs(pb - u9).sum())
    L1_p = float(np.abs(pp - u9).sum())
    L1_c = float(np.abs(pc - u9).sum())
    return (L1_p - L1_b) + 1j * (L1_c - L1_b)


print(f"Computing asymptotic z(W) for W ∈ [{W_VALUES[0]}, "
      f"{W_VALUES[-1]}]...")
t0 = time.time()
asy_z = np.zeros(len(W_VALUES), dtype=complex)
for i, W in enumerate(W_VALUES):
    asy_z[i] = asymptotic_z(n_0, int(W), K)
    if (i + 1) % 10 == 0 or i == 0:
        print(f"  W={W} done (t={time.time() - t0:.1f}s)")
print(f"Total: {time.time() - t0:.1f}s")
np.savez('coil_data.npz', W=W_VALUES, z=asy_z)

print()
print(f"{'W':>4} {'Re(z)':>9} {'Im(z)':>9} "
      f"{'|z|':>9} {'arg(deg)':>9}")
for i, W in enumerate(W_VALUES):
    z = asy_z[i]
    print(f"{int(W):>4d} {z.real:>+9.4f} {z.imag:>+9.4f} "
          f"{abs(z):>9.4f} {np.degrees(np.angle(z)):>+9.2f}")

# The "coil" lives in W ∈ [5, 33]. Past W=33 the curve escapes
# upward in a near-linear stretch (|z| grows from 0.08 to 0.53 as
# arg saturates near +98°). That's a different phenomenon — the
# coil is the rotation, not the escape. Render the coiling part
# in full crispness, fade the escape into a hint.
W_COIL_MAX = 33
mask_coil = W_VALUES <= W_COIL_MAX
mask_tail = W_VALUES >= W_COIL_MAX  # overlap at boundary

xy_coil = np.column_stack([asy_z[mask_coil].real,
                            asy_z[mask_coil].imag])
tck, u = splprep(xy_coil.T, s=0.0001, k=3)
u_fine = np.linspace(0, 1, 4000)
sx, sy = splev(u_fine, tck)

xy_tail = np.column_stack([asy_z[mask_tail].real,
                            asy_z[mask_tail].imag])
tck_t, u_t = splprep(xy_tail.T, s=0.0001, k=3)
u_fine_t = np.linspace(0, 1, 1500)
tx, ty = splev(u_fine_t, tck_t)

# Color along the curve: deep teal → pale gold → warm coral.
cmap = LinearSegmentedColormap.from_list('coil', [
    '#1a4d6e',   # deep teal
    '#3da9c4',   # cyan
    '#7dd3e0',   # pale cyan
    '#f5e2a3',   # pale gold
    '#f9b27a',   # warm peach
    '#e8643a',   # coral
    '#a83a25',   # deep coral
])

# Build segments for LineCollection.
pts = np.column_stack([sx, sy])
segs = np.stack([pts[:-1], pts[1:]], axis=1)
seg_t = np.linspace(0, 1, len(segs))

# Tail segments (the post-coil escape, rendered as a faint hint).
pts_t = np.column_stack([tx, ty])
segs_t = np.stack([pts_t[:-1], pts_t[1:]], axis=1)
# Tail color stays at the warm end of the cmap.
seg_tail_t = np.full(len(segs_t), 1.0)

fig, ax = plt.subplots(figsize=(10, 10))
fig.patch.set_facecolor('#050505')
ax.set_facecolor('#050505')

# Wide soft glow.
lc_g3 = LineCollection(segs, cmap=cmap, linewidth=14, alpha=0.06)
lc_g3.set_array(seg_t)
ax.add_collection(lc_g3)

# Medium glow.
lc_g2 = LineCollection(segs, cmap=cmap, linewidth=6, alpha=0.18)
lc_g2.set_array(seg_t)
ax.add_collection(lc_g2)

# Inner glow.
lc_g1 = LineCollection(segs, cmap=cmap, linewidth=2.6, alpha=0.55)
lc_g1.set_array(seg_t)
ax.add_collection(lc_g1)

# Crisp thread.
lc = LineCollection(segs, cmap=cmap, linewidth=1.0, alpha=1.0)
lc.set_array(seg_t)
ax.add_collection(lc)

# Tail (escape) — fade as it leaves the frame. Linewidth and
# alpha taper along the tail so the eye follows it out.
n_tail = len(segs_t)
tail_alpha = np.linspace(0.55, 0.05, n_tail)
tail_lw = np.linspace(0.9, 0.3, n_tail)
for j in range(n_tail):
    ax.add_collection(LineCollection(
        [segs_t[j]], colors=[cmap(1.0)],
        linewidth=tail_lw[j], alpha=tail_alpha[j]))

# Origin: subtle plus.
ax.plot([0, 0], [-0.008, 0.008], color='#666', linewidth=0.6,
        alpha=0.7)
ax.plot([-0.008, 0.008], [0, 0], color='#666', linewidth=0.6,
        alpha=0.7)

# Sparse W markers along the path.
markers = [5, 9, 15, 20, 25, 30, 33]
for W in markers:
    idx = int(np.where(W_VALUES == W)[0][0])
    z = asy_z[idx]
    ax.plot(z.real, z.imag, 'o', color='white', markersize=4,
            markeredgecolor='#050505', markeredgewidth=0.5,
            alpha=0.85, zorder=10)
    # offset label to outside of curve
    arg = np.angle(z)
    rmag = abs(z)
    if rmag > 0.001:
        offset_dx = 0.012 * np.cos(arg)
        offset_dy = 0.012 * np.sin(arg)
    else:
        offset_dx, offset_dy = 0.012, 0.012
    ax.annotate(
        f'W={W}',
        (z.real, z.imag),
        xytext=(z.real + offset_dx, z.imag + offset_dy),
        textcoords='data',
        color='white', fontsize=8.5, alpha=0.7,
        ha='left' if offset_dx >= 0 else 'right',
        va='bottom' if offset_dy >= 0 else 'top',
        zorder=10,
    )

# Frame tight to the coil. The escape tail will run off the top
# of the frame — that's the intended narrative.
all_x = np.concatenate([sx, asy_z[mask_coil].real])
all_y = np.concatenate([sy, asy_z[mask_coil].imag])
xrange = all_x.max() - all_x.min()
yrange = all_y.max() - all_y.min()
span = max(xrange, yrange) * 1.20
xc = (all_x.max() + all_x.min()) / 2
yc = (all_y.max() + all_y.min()) / 2
half = span / 2
ax.set_xlim(xc - half, xc + half)
ax.set_ylim(yc - half, yc + half)

ax.set_aspect('equal')
ax.axis('off')

# Title in the lower-right, small. Let the curve be the focus.
fig.text(0.93, 0.06, 'THE COIL',
         color='#ccc', fontsize=12, ha='right', va='bottom',
         family='serif', weight='bold')
fig.text(0.93, 0.045,
         'z(W) = (L1ₚᵐ − L1_b) + i(L1_cₘ − L1_b)',
         color='#666', fontsize=8, ha='right', va='top',
         style='italic', family='serif')
fig.text(0.93, 0.030,
         'W ∈ [5, 33]   ·   n_0 = 2, K = 400',
         color='#555', fontsize=8, ha='right', va='top',
         family='serif')

plt.savefig('coil.png', dpi=220, facecolor='#050505',
            bbox_inches='tight')
print()
print("-> coil.png")
