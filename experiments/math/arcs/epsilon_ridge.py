"""
Epsilon ridge — peak height and peak position vs base.

Top panel: max epsilon for each base (how tall is the bump?).
Bottom panel: mantissa at the peak (where is the bump?).
Both share the horizontal base axis.  This is the executive summary
of the 3D surface — two curves that answer "how tall?" and "where?".
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

bases = np.arange(2, 37)
m_pts = 2000

peak_eps = np.zeros(len(bases))
peak_m   = np.zeros(len(bases))

for i, b in enumerate(bases):
    m0 = 1.0 / b
    m = np.linspace(m0, 1.0, m_pts)

    curve = np.log(1 + m) / np.log(b)
    y0 = np.log(1 + m0) / np.log(b)
    y1 = np.log(2) / np.log(b)
    secant = y0 + (y1 - y0) * (m - m0) / (1.0 - m0)
    epsilon = curve - secant

    ip = np.argmax(epsilon)
    peak_eps[i] = epsilon[ip]
    peak_m[i] = m[ip]

# ── plot ─────────────────────────────────────────────────────────────

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8), sharex=True,
                                gridspec_kw={'hspace': 0.08})
fig.patch.set_facecolor('#0a0a0a')

for ax in (ax1, ax2):
    ax.set_facecolor('#0a0a0a')
    ax.tick_params(colors='white')
    for sp in ax.spines.values():
        sp.set_color('#333')

# top: peak height
ax1.plot(bases, peak_eps, 'o-', color='#ff6f61', markersize=5,
         linewidth=1.2, markeredgecolor='none')
ax1.set_ylabel('peak  ε', color='white', fontsize=11)
ax1.set_title('Ridge properties of the epsilon surface',
              color='white', fontsize=13, pad=10)

# fit a power law for reference: eps ~ A / b^alpha
from numpy.polynomial import polynomial as P
log_b = np.log(bases)
log_e = np.log(peak_eps)
coeffs = np.polyfit(log_b, log_e, 1)
alpha = -coeffs[0]
A = np.exp(coeffs[1])
b_fit = np.linspace(2, 36, 200)
ax1.plot(b_fit, A * b_fit**(-alpha), '--', color='#ffcc5c', linewidth=0.8,
         alpha=0.7, label=f'~ b$^{{-{alpha:.2f}}}$')
ax1.legend(fontsize=9, facecolor='#111', edgecolor='#333', labelcolor='#aaa')

# bottom: peak position
ax2.plot(bases, peak_m, 's-', color='#6ec6ff', markersize=5,
         linewidth=1.2, markeredgecolor='none')
ax2.axhline(0.5, color='#888', linewidth=0.6, linestyle=':', alpha=0.5)
ax2.set_ylabel('peak  m', color='white', fontsize=11)
ax2.set_xlabel('base  b', color='white', fontsize=11)
ax2.text(34, 0.505, 'm = 0.5', color='#888', fontsize=8, va='bottom')

plt.tight_layout()
out = 'epsilon_ridge.png'
plt.savefig(out, dpi=250, facecolor='#0a0a0a', bbox_inches='tight')
print(f'-> {out}')
