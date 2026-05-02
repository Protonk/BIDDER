"""
Echo barcode — pseudo-RLE for the K-decay structure.

Reduces the three-grid (lowK + largeK + extend) bias data to a
single visual marker per (n_0, peak): position on log-K = peak K,
marker size and color = peak amplitude. Decade vertical guides
make the base-10 alignment immediate.

This is the reduction: each "decay group" is one echo, one mark.
The smooth curves are not shown. The structure to read off is:
  (1) marks line up on decade boundaries
  (2) marks shrink as K grows
  (3) every n_0 has the same number of marks (4) over the
      computed K range
"""

import numpy as np
import matplotlib.pyplot as plt

zL = np.load('l1_grid_lengths_lowK.npz')
zG = np.load('l1_grid_lengths_largeK.npz')
zE = np.load('echo_extend.npz')

# Combined (n_0, K, bias) per row.
def combined_bias_for_n0(n0):
    Ks = []
    bs = []
    if n0 in zL['N0_VALUES']:
        i = int(np.where(zL['N0_VALUES'] == n0)[0][0])
        bias = (zL['L_SURV'][i, :] / zL['N_SURV'][i, :]) / \
               (zL['L_B_SET'][i, :] / zL['N_UNIQUE'][i, :])
        Ks.append(zL['K_VALUES'])
        bs.append((bias - 1) * 100)
    if n0 in zG['N0_VALUES']:
        i = int(np.where(zG['N0_VALUES'] == n0)[0][0])
        K_g = zG['K_VALUES']
        mask = K_g > 2000
        bias = (zG['L_SURV'][i, mask] / zG['N_SURV'][i, mask]) / \
               (zG['L_B_SET'][i, mask] / zG['N_UNIQUE'][i, mask])
        Ks.append(K_g[mask])
        bs.append((bias - 1) * 100)
    K_ext = zE['K_VALUES']
    key = f'bias_n0_{n0}'
    if key in zE.files:
        Ks.append(K_ext[K_ext > 50000])
        bs.append(zE[key][K_ext > 50000])
    if not Ks:
        return None
    K = np.concatenate(Ks)
    b = np.concatenate(bs)
    idx = np.argsort(K)
    return K[idx], b[idx]


# Find peaks per n_0 (use scipy with a permissive prominence,
# then keep peaks with amp > 0.4% so we drop noise wiggles).
from scipy.signal import find_peaks

ROWS = [2, 3, 5, 8, 12]
peak_data = {}  # n_0 -> list of (K, amp)
for n0 in ROWS:
    res = combined_bias_for_n0(n0)
    if res is None:
        continue
    K, bias = res
    peaks, props = find_peaks(bias, prominence=0.1)
    Kp = K[peaks]
    Ap = bias[peaks]
    keep = (Ap > 0.4) & (Kp >= 50)
    Kp = Kp[keep]
    Ap = Ap[keep]
    # Proximity filter: walk in K-order, merge any peak within
    # factor 3 of the previous kept peak (keep the larger).
    sorted_peaks = sorted(zip(Kp.tolist(), Ap.tolist()))
    filtered = []
    for K_val, A_val in sorted_peaks:
        if not filtered or K_val / filtered[-1][0] > 3.0:
            filtered.append((K_val, A_val))
        elif A_val > filtered[-1][1]:
            filtered[-1] = (K_val, A_val)
    peak_data[n0] = filtered

# --- Plot ---
fig, ax = plt.subplots(figsize=(13, 6))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

# Decade vertical guides at K = 10^d for d = 2..6.
for d in range(2, 7):
    ax.axvline(10**d, color='#3a3a3a', linestyle='-',
               linewidth=0.6, alpha=0.7, zorder=0)
    ax.text(10**d, 0.5, f'$10^{d}$', color='#888',
            ha='center', va='top', fontsize=10, zorder=1)

# Per-row spike trains: tiny connecting lines + dots.
y_positions = {n0: i for i, n0 in enumerate(ROWS, start=1)}
amp_max = max(a for peaks in peak_data.values() for _, a in peaks)

for n0, peaks in peak_data.items():
    y = y_positions[n0]
    Ks = [K for K, _ in peaks]
    As = [A for _, A in peaks]
    # Faint connecting line through the train
    ax.plot(Ks, [y] * len(Ks), color='#555', linewidth=0.7,
            alpha=0.5, zorder=1)
    # Dots: size encodes amplitude
    sizes = [(A / amp_max) ** 1.4 * 800 + 60 for A in As]
    sc = ax.scatter(Ks, [y] * len(Ks), s=sizes, c=As,
                    cmap='inferno', vmin=0, vmax=4,
                    edgecolor='white', linewidth=0.9,
                    zorder=3)
    # Amplitude annotations above each dot
    for K, A in peaks:
        ax.annotate(f'{A:+.2f}', (K, y),
                    xytext=(0, 14), textcoords='offset points',
                    color='#ddd', fontsize=8, ha='center',
                    zorder=4)

ax.set_xscale('log')
ax.set_xlim(50, 600000)
ax.set_ylim(0.4, len(ROWS) + 0.6)
ax.set_yticks(list(y_positions.values()))
ax.set_yticklabels([f'n_0 = {n0}' for n0 in ROWS], color='white',
                   fontsize=11)
ax.set_xlabel('K  (log scale)', color='white', fontsize=11)
ax.tick_params(colors='white', which='both')
for spine in ax.spines.values():
    spine.set_color('#333')

ax.set_title(
    'Echo barcode — peak K and amplitude across decades  '
    '(W=9, base 10)\n'
    'Each dot is one detected local maximum of the survivor '
    'mean-dlen bias. Size and color encode amplitude (%).',
    color='white', fontsize=11)

cbar = plt.colorbar(sc, ax=ax, fraction=0.025, pad=0.02)
cbar.set_label('peak amplitude  (%, set basis)',
               color='white', fontsize=10)
cbar.ax.tick_params(colors='white')
cbar.outline.set_edgecolor('#333')

plt.tight_layout()
plt.savefig('echo_barcode.png', dpi=180,
            facecolor='#0a0a0a', bbox_inches='tight')
print("-> echo_barcode.png")

print()
print("Peaks summarized:")
for n0, peaks in peak_data.items():
    pks = "  ".join(f"K={K:>7d} A={A:+.2f}%"
                     for K, A in peaks)
    print(f"  n_0={n0}: {pks}")
