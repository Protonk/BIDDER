"""
EXP04 — the bracketing surface.

Compute z(n, W) = (L1_prime_m − L1_bundle) + i (L1_comp_m − L1_bundle)
across atom_index n and window width W, at fixed n_0=2, K=400.

|z(n, W)| is the tangle-magnitude surface (height).
arg z(n, W) is the bracketing-direction phase.

Sample W ∈ [5, 30] step 1. The W=9 → W=20 bracketing flip should
appear as arg z rotating across W. The asymptotic z value (last
atom of each slice) traces a curve in the complex plane.
"""

import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from sympy import isprime

K = 400
n_0 = 2
W_VALUES = np.arange(5, 31)
N_MAX = K * int(W_VALUES.max())


def n_primes_vec(n, k):
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


u9 = np.full(9, 1.0 / 9)


def build_z(n_0, W, K):
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
    prime_m = np.array([isprime(int(m)) for m in m_S])

    bundle_set = set(int(c) for c in unique_vals)
    pm_set = set(int(c) for c, pm in zip(S, prime_m) if pm)
    cm_set = set(int(c) for c, pm in zip(S, prime_m) if not pm)

    def running_l1(in_set):
        seen = set()
        counts_arr = np.zeros(9, dtype=np.int64)
        out_l1, out_idx = [], []
        for i in range(n_atoms):
            c = int(all_atoms[i])
            if c in seen:
                continue
            seen.add(c)
            if c not in in_set:
                continue
            log_floor = int(np.floor(np.log10(c)))
            leading = c // 10**log_floor
            counts_arr[leading - 1] += 1
            tot = counts_arr.sum()
            p = counts_arr / tot
            out_l1.append(np.abs(p - u9).sum())
            out_idx.append(i)
        return np.array(out_idx), np.array(out_l1)

    idx_b, l1_b = running_l1(bundle_set)
    idx_pm, l1_pm = running_l1(pm_set)
    idx_cm, l1_cm = running_l1(cm_set)

    def step_interp(idx, vals, x):
        positions = np.searchsorted(idx, x, side='right') - 1
        out = np.full(len(x), np.nan)
        valid = positions >= 0
        out[valid] = vals[positions[valid]]
        return out

    grid = np.arange(n_atoms)
    L1_b = step_interp(idx_b, l1_b, grid)
    L1_pm = step_interp(idx_pm, l1_pm, grid)
    L1_cm = step_interp(idx_cm, l1_cm, grid)

    return n_atoms, L1_pm - L1_b, L1_cm - L1_b


print(f"Building z surface for W ∈ [{W_VALUES[0]}, "
      f"{W_VALUES[-1]}], K={K}, n_0={n_0}...")
t0 = time.time()
Z_real = np.full((len(W_VALUES), N_MAX), np.nan)
Z_imag = np.full((len(W_VALUES), N_MAX), np.nan)
for i, W in enumerate(W_VALUES):
    n_atoms, zr, zi = build_z(n_0, int(W), K)
    Z_real[i, :n_atoms] = zr
    Z_imag[i, :n_atoms] = zi
    if (i + 1) % 5 == 0 or i == 0:
        print(f"  W={W} done (t={time.time() - t0:.1f}s)")

print(f"Total compute: {time.time() - t0:.1f}s")
np.savez('primality_surface.npz',
         Z_real=Z_real, Z_imag=Z_imag,
         W_VALUES=W_VALUES, K=K, n_0=n_0)
print("-> primality_surface.npz")

Z = Z_real + 1j * Z_imag
Z_mag = np.abs(Z)
Z_arg = np.angle(Z)

# Asymptotic z per W (last valid atom).
asy_z = np.zeros(len(W_VALUES), dtype=complex)
for i, W in enumerate(W_VALUES):
    n_atoms_w = int(W) * K
    asy_z[i] = Z[i, n_atoms_w - 1]

print()
print("Asymptotic z(W) — at the last atom of each slice:")
print(f"{'W':>4} {'Re(z)':>9} {'Im(z)':>9} "
      f"{'|z|':>9} {'arg(deg)':>9}")
for i, W in enumerate(W_VALUES):
    z_w = asy_z[i]
    print(f"{int(W):>4d} {z_w.real:>+9.4f} {z_w.imag:>+9.4f} "
          f"{abs(z_w):>9.4f} {np.degrees(np.angle(z_w)):>+9.2f}")

# --- Plot: 2x2 grid ---
fig = plt.figure(figsize=(15, 12))
fig.patch.set_facecolor('#0a0a0a')
gs = fig.add_gridspec(2, 2, height_ratios=[1.4, 1],
                      width_ratios=[1, 1])

ax_mag = fig.add_subplot(gs[0, 0])
ax_arg = fig.add_subplot(gs[0, 1])
ax_complex = fig.add_subplot(gs[1, 0])
ax_W_curves = fig.add_subplot(gs[1, 1])

# Common heatmap extent.
extent = (0, N_MAX,
          W_VALUES[0] - 0.5, W_VALUES[-1] + 0.5)


def style(ax, title, xlabel='atoms processed', ylabel='W'):
    ax.set_facecolor('#0a0a0a')
    ax.set_xlabel(xlabel, color='white', fontsize=11)
    ax.set_ylabel(ylabel, color='white', fontsize=11)
    ax.set_title(title, color='white', fontsize=11)
    ax.tick_params(colors='white', which='both')
    for spine in ax.spines.values():
        spine.set_color('#333')


# (0,0) Magnitude
mag_floor = 1e-3
Z_mag_clipped = np.where(np.isnan(Z_mag), np.nan,
                          np.maximum(Z_mag, mag_floor))
mag_max = np.nanmax(Z_mag_clipped)
im = ax_mag.imshow(Z_mag_clipped, aspect='auto', origin='lower',
                    cmap='inferno', interpolation='nearest',
                    extent=extent,
                    norm=LogNorm(vmin=mag_floor, vmax=mag_max))
style(ax_mag, '|z|  — tangle magnitude (log)')
cb = plt.colorbar(im, ax=ax_mag, fraction=0.04, pad=0.02)
cb.set_label('|z|', color='white', fontsize=9)
cb.ax.tick_params(colors='white')
cb.outline.set_edgecolor('#333')
# stream-transition guides
for slot in range(K, N_MAX, K):
    ax_mag.axvline(slot, color='#444', linewidth=0.4, alpha=0.4)

# (0,1) Phase
im2 = ax_arg.imshow(Z_arg, aspect='auto', origin='lower',
                     cmap='twilight', interpolation='nearest',
                     extent=extent, vmin=-np.pi, vmax=np.pi)
style(ax_arg, 'arg z  — bracketing direction (rad)')
cb = plt.colorbar(im2, ax=ax_arg, fraction=0.04, pad=0.02)
cb.set_label('arg z (rad)', color='white', fontsize=9)
cb.ax.tick_params(colors='white')
cb.outline.set_edgecolor('#333')
for slot in range(K, N_MAX, K):
    ax_arg.axvline(slot, color='#444', linewidth=0.4, alpha=0.4)

# (1,0) Asymptotic z trajectory in the complex plane.
ax_complex.set_facecolor('#0a0a0a')
ax_complex.axhline(0, color='#444', linewidth=0.5, alpha=0.6)
ax_complex.axvline(0, color='#444', linewidth=0.5, alpha=0.6)
sc = ax_complex.scatter(asy_z.real, asy_z.imag,
                         c=W_VALUES, cmap='viridis',
                         s=70, edgecolor='white', linewidth=0.7,
                         zorder=3)
ax_complex.plot(asy_z.real, asy_z.imag, color='#666',
                 linewidth=1.0, alpha=0.7, zorder=2)
for i, W in enumerate(W_VALUES):
    if int(W) in (5, 9, 12, 15, 20, 25, 30):
        ax_complex.annotate(f'W={int(W)}',
                             (asy_z[i].real, asy_z[i].imag),
                             xytext=(7, 5),
                             textcoords='offset points',
                             color='white', fontsize=9)
style(ax_complex,
      'Asymptotic z(W) trajectory in complex plane',
      xlabel='Re(z) = L1_prime_m − L1_bundle',
      ylabel='Im(z) = L1_comp_m − L1_bundle')
cb = plt.colorbar(sc, ax=ax_complex, fraction=0.04, pad=0.02)
cb.set_label('W', color='white', fontsize=9)
cb.ax.tick_params(colors='white')
cb.outline.set_edgecolor('#333')
ax_complex.grid(alpha=0.15, color='#444', which='both')
ax_complex.set_aspect('equal')

# (1,1) |z|(W) and arg z(W) at asymptote
ax_W_curves.set_facecolor('#0a0a0a')
ax_W_curves.plot(W_VALUES, np.abs(asy_z),
                  color='#5cd4ff', linewidth=1.6, marker='o',
                  markersize=5, label='|asy z|')
ax_W_curves.set_xlabel('W', color='white', fontsize=11)
ax_W_curves.set_ylabel('|z|', color='#5cd4ff', fontsize=11)
ax_W_curves.tick_params(axis='y', colors='#5cd4ff')
ax_W_curves.tick_params(colors='white', which='both')
for spine in ax_W_curves.spines.values():
    spine.set_color('#333')
ax_W_curves.set_facecolor('#0a0a0a')
ax_W_curves.set_title(
    '|asy z|(W) and arg(asy z)(W)  '
    '— bracketing magnitude & direction',
    color='white', fontsize=11)
ax_W_curves.grid(alpha=0.15, color='#444', which='both')

ax_W_curves2 = ax_W_curves.twinx()
ax_W_curves2.set_facecolor('#0a0a0a')
ax_W_curves2.plot(W_VALUES, np.degrees(np.angle(asy_z)),
                   color='#cc66ff', linewidth=1.6, marker='s',
                   markersize=5, label='arg z (deg)')
ax_W_curves2.set_ylabel('arg z (degrees)', color='#cc66ff',
                         fontsize=11)
ax_W_curves2.tick_params(colors='#cc66ff', which='both')
for spine in ax_W_curves2.spines.values():
    spine.set_color('#333')
ax_W_curves2.axhline(0, color='#cc66ff', linewidth=0.5,
                      linestyle=':', alpha=0.5)

# Combined legend.
lines1, labels1 = ax_W_curves.get_legend_handles_labels()
lines2, labels2 = ax_W_curves2.get_legend_handles_labels()
ax_W_curves.legend(lines1 + lines2, labels1 + labels2,
                    loc='upper right', facecolor='#1a1a1a',
                    edgecolor='#333', labelcolor='white',
                    fontsize=10)

plt.suptitle(
    f'Bracketing surface  (n_0={n_0}, K={K}, W ∈ '
    f'[{W_VALUES[0]}, {W_VALUES[-1]}])  — '
    'z = (prime-m − bundle) + i(comp-m − bundle)',
    color='white', fontsize=13)
plt.tight_layout()
plt.savefig('primality_surface.png', dpi=160,
            facecolor='#0a0a0a', bbox_inches='tight')
print("-> primality_surface.png")
