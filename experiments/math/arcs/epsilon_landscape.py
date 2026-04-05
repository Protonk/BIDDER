"""
Epsilon landscape — 3D surface of the secant error across bases and mantissas.

The error epsilon_b(m) = log_b(1+m) - secant(m) is the concave bump that
measures "compositeness pressure." This script renders it as a 3D surface
over (base, mantissa) space, showing how the bump shape varies with base.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

bases = np.arange(2, 37)  # bases 2..36
m_points = 500

fig = plt.figure(figsize=(14, 10))
fig.patch.set_facecolor('#0a0a0a')
ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor('#0a0a0a')

for b in bases:
    # Mantissa range for base b: [1/b, 1]
    m = np.linspace(1/b, 1, m_points)
    # ln(1+m) is the true curve
    curve = np.log(1 + m) / np.log(b)
    # Secant from (1/b, log_b(1+1/b)) to (1, log_b(2))
    m0, m1 = 1/b, 1.0
    y0, y1 = np.log(1 + m0) / np.log(b), np.log(2) / np.log(b)
    secant = y0 + (y1 - y0) * (m - m0) / (m1 - m0)
    epsilon = curve - secant

    ax.plot(m, np.full_like(m, b), epsilon, color=plt.cm.viridis((b - 2) / 34),
            linewidth=0.8, alpha=0.8)

ax.set_xlabel('mantissa m', color='white', fontsize=10, labelpad=10)
ax.set_ylabel('base b', color='white', fontsize=10, labelpad=10)
ax.set_zlabel('epsilon', color='white', fontsize=10, labelpad=10)
ax.set_title('Epsilon Landscape: secant error across bases',
             color='white', fontsize=14, pad=20)
ax.tick_params(colors='white')
ax.xaxis.pane.fill = False
ax.yaxis.pane.fill = False
ax.zaxis.pane.fill = False
ax.xaxis.pane.set_edgecolor('#333')
ax.yaxis.pane.set_edgecolor('#333')
ax.zaxis.pane.set_edgecolor('#333')
ax.view_init(elev=25, azim=-60)

plt.savefig('epsilon_landscape.png', dpi=300, facecolor='#0a0a0a', bbox_inches='tight')
print("-> epsilon_landscape.png")
