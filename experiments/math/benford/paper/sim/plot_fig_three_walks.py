"""
Three-walk comparison figure:
  (1) pure multiplicative — {a, a⁻¹} only
  (2) alternating add/mul — forced mul/add alternation, random sign
  (3) BS(1,2) mix — random {a, a⁻¹, b, b⁻¹}

All from x₀ = +√2. Log-log L₁(n) vs n.

Produces `paper/fig/fig_three_walks_loglog.png`.

Run: sage -python plot_fig_three_walks.py
"""

import math
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.abspath(os.path.join(SIM_DIR, '..', 'fig'))
os.makedirs(FIG_DIR, exist_ok=True)

# Load data.
m1 = np.load(os.path.join(SIM_DIR, 'm1_b1_b2_results.npz'))
t_bs = m1['sample_times']
l1_bs = m1['l1']

mul = np.load(os.path.join(SIM_DIR, 'comparison_walks_results', 'pure_mul_results.npz'))
t_mul = mul['sample_times']
l1_mul = mul['l1']

alt = np.load(os.path.join(SIM_DIR, 'comparison_walks_results', 'alternating_results.npz'))
t_alt = alt['sample_times']
l1_alt = alt['l1']

m0 = np.load(os.path.join(SIM_DIR, 'm0_results.npz'))
theta_N_1e8 = float(m0['theta_N'])
theta_N_1e6 = theta_N_1e8 * math.sqrt(100.0)


fig, ax = plt.subplots(figsize=(8.0, 5.5))

ax.loglog(t_bs, l1_bs, color='#c0392b', linewidth=2.2,
          label=r'$\mathrm{BS}(1,2)$ (random $a$ or $b$)', zorder=4)
ax.loglog(t_alt, l1_alt, color='#8e44ad', linewidth=1.8, linestyle='-.',
          label=r'Alternating (mul, add, mul, add, …)', zorder=3)
ax.loglog(t_mul, l1_mul, color='#2980b9', linewidth=1.8, linestyle='--',
          label=r'Pure multiplicative ($a, a^{-1}$ only)', zorder=3)

# Noise floor lines.
ax.axhline(theta_N_1e8, color='#aaa', linestyle='-', linewidth=0.7,
           alpha=0.6, zorder=1)
ax.axhline(theta_N_1e6, color='#aaa', linestyle='-', linewidth=0.7,
           alpha=0.6, zorder=1)
ax.text(1.2, theta_N_1e8 * 1.25, r'$\theta_N\,(N=10^8)$',
        color='#666', fontsize=8, ha='left', va='bottom')
ax.text(1.2, theta_N_1e6 * 1.25, r'$\theta_N\,(N=10^6)$',
        color='#666', fontsize=8, ha='left', va='bottom')

# Observable window — extended to the right edge of the plot since
# real datasets often have n >> 10^3 samples.
ax.axvspan(50, 2000, alpha=0.06, color='gray', zorder=0)
ax.text(320, 2.5, 'observable window',
        fontsize=9, color='#555', ha='center', style='italic')

# Annotations.
ax.annotate(r'BS(1,2): hits $\theta_N(10^8)$' + '\nby $n \\approx 200$–600',
            xy=(300, 5e-3), xytext=(7, 2e-2),
            color='#c0392b', fontsize=10,
            arrowprops=dict(arrowstyle='->', color='#c0392b', alpha=0.7, lw=0.9))

ax.annotate('Alternating:\nhits $\\theta_N(10^6)$\nby $n \\approx 180$,\nthen floor-limited',
            xy=(300, 2.7e-2), xytext=(600, 0.20),
            color='#8e44ad', fontsize=9.5,
            arrowprops=dict(arrowstyle='->', color='#8e44ad', alpha=0.7, lw=0.9))

ax.annotate('Pure mul:\ncountable mantissa support\n→ $L_1$ stuck near 2',
            xy=(1000, 1.85), xytext=(20, 0.55),
            color='#2980b9', fontsize=9.5,
            arrowprops=dict(arrowstyle='->', color='#2980b9', alpha=0.7, lw=0.9))

ax.set_xlabel('step $n$', fontsize=11)
ax.set_ylabel(r'$L_1(P_n,\ \mathrm{Leb}_T)$', fontsize=11)
ax.set_title(r'$\mathrm{BS}(1,2)$ vs alternating vs pure multiplicative:'
             '\nrate of convergence to Benford from $x_0 = \\sqrt{2}$',
             fontsize=11)
ax.set_xlim(0.9, 2e3)
ax.set_ylim(1.5e-3, 4.0)
ax.grid(True, which='major', alpha=0.22, linewidth=0.6)
ax.grid(True, which='minor', alpha=0.08, linewidth=0.4)

ax.legend(loc='lower left', fontsize=9.5, framealpha=0.92)

plt.tight_layout()
out_path = os.path.join(FIG_DIR, 'fig_three_walks_loglog.png')
plt.savefig(out_path, dpi=160, bbox_inches='tight')
plt.close()
print(f'-> {out_path}')

# Data summary
print()
print('=== data summary ===')
print(f'BS(1,2): N={int(m1["meta_N"]):_}, t=[{t_bs[0]}, {t_bs[-1]}], L₁={l1_bs.min():.3e}–{l1_bs.max():.3e}')
print(f'pure_mul: N={int(mul["meta_N"]):_}, t=[{t_mul[0]}, {t_mul[-1]}], L₁={l1_mul.min():.3e}–{l1_mul.max():.3e}')
print(f'alternating: N={int(alt["meta_N"]):_}, t=[{t_alt[0]}, {t_alt[-1]}], L₁={l1_alt.min():.3e}–{l1_alt.max():.3e}')
