"""
Epsilon heatmap — the secant error surface seen from above.

m on horizontal, b on vertical, epsilon as color.  The valid region
(m >= 1/b) is a right triangle.  The bump ridge appears as a bright
band curving through (m, b) space.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

bases = np.arange(2, 37)
m_pts = 500
m_all = np.linspace(0, 1, m_pts)

# Build the surface: rows = bases, cols = mantissa
surface = np.full((len(bases), m_pts), np.nan)

for i, b in enumerate(bases):
    m0 = 1.0 / b
    valid = m_all >= m0
    m = m_all[valid]

    curve = np.log(1 + m) / np.log(b)
    y0 = np.log(1 + m0) / np.log(b)
    y1 = np.log(2) / np.log(b)
    secant = y0 + (y1 - y0) * (m - m0) / (1.0 - m0)
    surface[i, valid] = curve - secant

# ── plot ─────────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(12, 8))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

im = ax.imshow(surface, aspect='auto', origin='lower', cmap='inferno',
               extent=[0, 1, 2, 36], interpolation='bilinear')

ax.set_xlabel('mantissa  m', color='white', fontsize=11)
ax.set_ylabel('base  b', color='white', fontsize=11)
ax.tick_params(colors='white')
for sp in ax.spines.values():
    sp.set_color('#333')

cbar = plt.colorbar(im, ax=ax, pad=0.02)
cbar.set_label('ε(m, b)', color='white', fontsize=11)
cbar.ax.tick_params(colors='white')

# mark the valid-region boundary m = 1/b
b_line = np.linspace(2, 36, 300)
ax.plot(1.0 / b_line, b_line, '--', color='white', linewidth=0.8, alpha=0.5,
        label='m = 1/b')
ax.legend(fontsize=9, facecolor='#111', edgecolor='#333', labelcolor='#aaa')

plt.tight_layout()
out = 'epsilon_heatmap.png'
plt.savefig(out, dpi=250, facecolor='#0a0a0a', bbox_inches='tight')
print(f'-> {out}')
