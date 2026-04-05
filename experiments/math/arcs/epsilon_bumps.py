"""
Epsilon bump overlay — all 35 base cross-sections superimposed.

Each curve is epsilon_b(m) vs m for one base, colored by base.
Shows the bump shape change, height decay, and valid-range shrinkage
as base increases from 2 to 36.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

bases = np.arange(2, 37)
m_pts = 1000

fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

cmap = plt.cm.plasma
norm = plt.Normalize(vmin=2, vmax=36)

for b in bases:
    m0 = 1.0 / b
    m = np.linspace(m0, 1.0, m_pts)

    curve = np.log(1 + m) / np.log(b)
    y0 = np.log(1 + m0) / np.log(b)
    y1 = np.log(2) / np.log(b)
    secant = y0 + (y1 - y0) * (m - m0) / (1.0 - m0)
    epsilon = curve - secant

    color = cmap(norm(b))
    lw = 2.0 if b <= 4 else (1.0 if b <= 10 else 0.5)
    alpha = 0.95 if b <= 10 else 0.7
    ax.plot(m, epsilon, color=color, linewidth=lw, alpha=alpha)

# label a few key bases
for b, ha, va, offset in [(2, 'left', 'bottom', (5, 3)),
                           (10, 'left', 'bottom', (5, 2)),
                           (36, 'right', 'top', (-5, -3))]:
    m0 = 1.0 / b
    m = np.linspace(m0, 1.0, m_pts)
    curve = np.log(1 + m) / np.log(b)
    y0 = np.log(1 + m0) / np.log(b)
    y1 = np.log(2) / np.log(b)
    secant = y0 + (y1 - y0) * (m - m0) / (1.0 - m0)
    eps = curve - secant
    ip = np.argmax(eps)
    ax.annotate(f'b={b}', (m[ip], eps[ip]), fontsize=9, color='white',
                ha=ha, va=va, xytext=offset, textcoords='offset points')

ax.set_xlabel('mantissa  m', color='white', fontsize=11)
ax.set_ylabel('ε(m)', color='white', fontsize=11)
ax.tick_params(colors='white')
for sp in ax.spines.values():
    sp.set_color('#333')

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
cbar = plt.colorbar(sm, ax=ax, pad=0.02)
cbar.set_label('base  b', color='white', fontsize=11)
cbar.ax.tick_params(colors='white')

plt.tight_layout()
out = 'epsilon_bumps.png'
plt.savefig(out, dpi=250, facecolor='#0a0a0a', bbox_inches='tight')
print(f'-> {out}')
