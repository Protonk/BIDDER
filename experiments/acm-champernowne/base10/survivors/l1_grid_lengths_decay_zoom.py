"""
Closer look at the K-decay of the survivor mean-dlen bias.

Loads the cached large-K grid and produces a richer view of the
n_0-stratified decay curves: linear-scale with annotated peaks,
log-log tail to test asymptotic decay rate, and a sweep of all
small-n_0 curves to expose the regime structure.
"""

import numpy as np
import matplotlib.pyplot as plt

z = np.load('l1_grid_lengths_largeK.npz')
N0_VALUES = z['N0_VALUES']
K_VALUES = z['K_VALUES']
W = int(z['W'])
N_U = z['N_UNIQUE']
N_S = z['N_SURV']
L_BS = z['L_B_SET']
L_S = z['L_SURV']

mean_b_set = L_BS / N_U
mean_s = L_S / N_S
set_ratio = mean_s / mean_b_set
bias_pct = (set_ratio - 1) * 100

# Peak locations and asymptotic behavior at small n_0.
print("Peak and tail structure (set basis):")
print(f"{'n_0':>4} {'peak K':>8} {'peak %':>8} "
      f"{'K=2000 %':>10} {'K=50000 %':>10} {'ratio':>8}")
for n0 in [2, 3, 4, 5, 6, 7, 8, 10, 15, 20]:
    if n0 in N0_VALUES:
        i = int(np.where(N0_VALUES == n0)[0][0])
        bias_row = bias_pct[i, :]
        j_peak = int(np.argmax(bias_row))
        peak_K = int(K_VALUES[j_peak])
        peak_b = float(bias_row[j_peak])
        first = float(bias_row[0])
        last = float(bias_row[-1])
        ratio = last / first if first != 0 else float('nan')
        print(f"{n0:>4d} {peak_K:>8d} {peak_b:>+8.3f} "
              f"{first:>+10.3f} {last:>+10.3f} {ratio:>8.3f}")

# --- Plot: 3 panels ---
fig = plt.figure(figsize=(15, 11))
fig.patch.set_facecolor('#0a0a0a')
gs = fig.add_gridspec(2, 2, height_ratios=[1, 1], width_ratios=[1, 1])
ax_main = fig.add_subplot(gs[0, :])  # Top: full-width linear plot
ax_log = fig.add_subplot(gs[1, 0])
ax_peak = fig.add_subplot(gs[1, 1])

curves = [(2, '#ff4444'), (3, '#ff8c42'), (4, '#ffcc33'),
          (5, '#a8e22d'), (6, '#33d6a8'), (7, '#33b5e5'),
          (8, '#7e6bff'), (10, '#cc66ff'), (15, '#ff66cc')]

for n0, color in curves:
    if n0 not in N0_VALUES:
        continue
    i = int(np.where(N0_VALUES == n0)[0][0])
    row = bias_pct[i, :]
    ax_main.plot(K_VALUES, row, color=color, linewidth=1.5,
                 label=f'n_0 = {n0}')
    j_peak = int(np.argmax(row))
    ax_main.plot(K_VALUES[j_peak], row[j_peak], marker='o',
                 color=color, markersize=7,
                 markeredgecolor='white', markeredgewidth=0.7,
                 linestyle='none')

ax_main.axhline(0, color='#444', linewidth=0.8, linestyle='--')
ax_main.set_xlabel('K  (atoms per stream)', color='white', fontsize=11)
ax_main.set_ylabel('mean-dlen ratio − 1  (%, set basis)',
                   color='white', fontsize=11)
ax_main.set_title(
    'K-decay of survivor mean digit-length bias  '
    '(W=9, n_0 fixed; ● marks peak K)',
    color='white', fontsize=12)
ax_main.tick_params(colors='white')
for spine in ax_main.spines.values():
    spine.set_color('#333')
ax_main.legend(loc='upper right', facecolor='#1a1a1a',
               edgecolor='#333', labelcolor='white',
               fontsize=9, ncol=2)
ax_main.grid(alpha=0.15, color='#444')

# --- Log-log tail: only post-peak portion to test decay law ---
for n0, color in curves[:6]:
    if n0 not in N0_VALUES:
        continue
    i = int(np.where(N0_VALUES == n0)[0][0])
    row = bias_pct[i, :]
    j_peak = int(np.argmax(row))
    Ks = K_VALUES[j_peak:]
    bs = row[j_peak:]
    pos = bs > 0
    ax_log.loglog(Ks[pos], bs[pos], color=color,
                  linewidth=1.5, label=f'n_0 = {n0}')

# Reference slope: bias ∝ K^{-1/2}
Kref = np.array([5000, 50000])
for slope, ls, lab in [(-0.5, '--', '∝ K^(−1/2)'),
                        (-1.0, ':', '∝ K^(−1)')]:
    bref = bs[0] * (Kref / Ks[0]) ** slope * 0.7
    ax_log.loglog(Kref, bref, color='#888', linestyle=ls,
                  linewidth=1.0, label=lab)

ax_log.set_xlabel('K  (post-peak)', color='white', fontsize=11)
ax_log.set_ylabel('bias  (%, log)', color='white', fontsize=11)
ax_log.set_title('Post-peak decay (log-log)',
                 color='white', fontsize=11)
ax_log.tick_params(colors='white')
for spine in ax_log.spines.values():
    spine.set_color('#333')
ax_log.set_facecolor('#0a0a0a')
ax_log.legend(loc='lower left', facecolor='#1a1a1a',
              edgecolor='#333', labelcolor='white', fontsize=8)
ax_log.grid(alpha=0.15, color='#444', which='both')

# --- Peak K vs n_0 ---
peaks_n0 = []
peaks_K = []
peaks_amp = []
for n0 in range(2, 21):
    if n0 in N0_VALUES:
        i = int(np.where(N0_VALUES == n0)[0][0])
        row = bias_pct[i, :]
        j_peak = int(np.argmax(row))
        peaks_n0.append(n0)
        peaks_K.append(int(K_VALUES[j_peak]))
        peaks_amp.append(float(row[j_peak]))

ax_peak.set_facecolor('#0a0a0a')
sc = ax_peak.scatter(peaks_n0, peaks_K, c=peaks_amp, s=80,
                     cmap='viridis', edgecolor='white',
                     linewidth=0.7)
ax_peak.set_xlabel('n_0', color='white', fontsize=11)
ax_peak.set_ylabel('peak K', color='white', fontsize=11)
ax_peak.set_title('Peak K vs. n_0  (color = peak bias %)',
                  color='white', fontsize=11)
ax_peak.tick_params(colors='white')
for spine in ax_peak.spines.values():
    spine.set_color('#333')
cbar = plt.colorbar(sc, ax=ax_peak, fraction=0.04, pad=0.02)
cbar.set_label('peak bias (%)', color='white', fontsize=9)
cbar.ax.tick_params(colors='white')
cbar.outline.set_edgecolor('#333')
ax_peak.grid(alpha=0.15, color='#444')

plt.tight_layout()
plt.savefig('l1_grid_lengths_decay_zoom.png', dpi=170,
            facecolor='#0a0a0a', bbox_inches='tight')
print()
print("-> l1_grid_lengths_decay_zoom.png")
