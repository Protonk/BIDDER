"""
bin_peel.py — fit four bin-pure predictor templates to the cached L1
tracking-gap heatmap and read the residual.

Bins (per MIGRANTS.md):
  1. local rank algebra        — first-collision indicator (K ≥ n_0)
  2. base / block geometry     — base-10 decade-crossing ridges
  3. deep-index asymptotic     — 1/√K decay
  4. nonlinear aggregate       — Mertens envelope 1/log(K·n_0)
                                 (proxy for CF / cumulant convergence rate)

Joint linear LS:    G(n_0, K) ≈ Σ α_i P_i(n_0, K) + R(n_0, K).

Output:
  - bin_peel.png         G, four α_i·P_i panels, residual R.
  - bin_attribution.png  per-cell argmax bin + pan-bin residual map.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, ListedColormap


CACHE = 'l1_grid.npz'
z = np.load(CACHE)
G = z['G']
N0 = z['N0_VALUES']
K = z['K_VALUES']
W = int(z['W'])
print(f"G shape: {G.shape}, n_0 ∈ [{N0[0]}, {N0[-1]}], "
      f"K ∈ [{K[0]}, {K[-1]}], W={W}")

N0g, Kg = np.meshgrid(N0, K, indexing='ij')

# ── Predictors ──────────────────────────────────────────────────────
P1 = 1.0 / (1.0 + np.exp(-(Kg - N0g) / 30.0))           # bin 1
P2 = np.abs(np.sin(np.pi * np.log10(Kg * N0g)))          # bin 2
P3 = 1.0 / np.sqrt(Kg)                                    # bin 3
P4 = 1.0 / np.log(Kg * N0g + 1.0)                         # bin 4

raw_preds = [P1, P2, P3, P4]
labels = ['Bin 1: rank algebra (K ≥ n_0)',
          'Bin 2: decade ridges (K·n_0 = 10^d)',
          'Bin 3: K-asymptotic (1/√K)',
          'Bin 4: Mertens envelope (1/log K·n_0)']

# Normalise to unit max-abs so α magnitudes are comparable.
Pn = [P / np.max(np.abs(P)) for P in raw_preds]

# Predictor cross-correlations (sanity for colinearity).
A = np.stack([P.ravel() for P in Pn], axis=1)
y = G.ravel()
mask = np.isfinite(y)
A_m = A[mask]; y_m = y[mask]

A_centered = A_m - A_m.mean(axis=0, keepdims=True)
A_norm = A_centered / np.linalg.norm(A_centered, axis=0, keepdims=True)
corr = A_norm.T @ A_norm
print("\nPredictor cross-correlation matrix:")
print("         P1       P2       P3       P4")
for i in range(4):
    row = "  ".join(f"{corr[i, j]:+.3f}" for j in range(4))
    print(f"  P{i+1}:  {row}")

# Joint LS fit.
alpha, *_ = np.linalg.lstsq(A_m, y_m, rcond=None)
fit = (A @ alpha).reshape(G.shape)
resid = G - fit

print("\nFit coefficients:")
for i, lbl in enumerate(labels):
    print(f"  α_{i+1}  {lbl:<42s}  α = {alpha[i]:+.5f}")

total_var = float(np.var(y_m))
resid_var = float(np.var(resid.ravel()[mask]))
print(f"\nVariance explained: 1 − {resid_var:.5f} / {total_var:.5f} "
      f"= {1.0 - resid_var/total_var:.3f}")

abs_total = float(np.sum(np.abs(y_m)))
print("\n|αP| / |G| (relative L1 contribution):")
for i, lbl in enumerate(labels):
    e = float(np.sum(np.abs(alpha[i] * Pn[i].ravel()[mask])))
    print(f"  α_{i+1}  {lbl:<42s}  {e/abs_total*100:5.1f}%")
res_e = float(np.sum(np.abs(resid.ravel()[mask])))
print(f"     residual                                  {res_e/abs_total*100:5.1f}%")

comps = [alpha[i] * Pn[i] for i in range(4)]

# ── Six-panel figure ────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.patch.set_facecolor('#0a0a0a')

step_x = K[1] - K[0]; step_y = N0[1] - N0[0]
extent = (K[0] - step_x/2, K[-1] + step_x/2,
          N0[0] - step_y/2, N0[-1] + step_y/2)
vmax = float(np.nanpercentile(np.abs(G), 95))
norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)

resid_rms_ratio = float(np.std(resid.ravel()[mask]) / np.std(y_m))
panels = [(G,        f'G  (observed, |G|@95% = {vmax:.4f})'),
          (comps[0], f'{labels[0]}\nα = {alpha[0]:+.4f}'),
          (comps[1], f'{labels[1]}\nα = {alpha[1]:+.4f}'),
          (resid,    f'R  (residual, σ_R / σ_G = {resid_rms_ratio:.3f})'),
          (comps[2], f'{labels[2]}\nα = {alpha[2]:+.4f}'),
          (comps[3], f'{labels[3]}\nα = {alpha[3]:+.4f}')]

for ax, (data, title) in zip(axes.ravel(), panels):
    ax.set_facecolor('#0a0a0a')
    ax.imshow(data, origin='lower', cmap='RdBu_r', norm=norm,
              extent=extent, aspect='equal', interpolation='nearest')
    ax.set_title(title, color='white', fontsize=10)
    ax.tick_params(colors='white', labelsize=8)
    for spine in ax.spines.values():
        spine.set_color('#333')

fig.suptitle(
    f'Bin-peel of L1 tracking-gap   '
    f'(W = {W}, n_0, K ∈ [{N0[0]}, {N0[-1]}], step = {step_x})',
    color='white', fontsize=13)
fig.tight_layout()
fig.savefig('bin_peel.png', dpi=180, facecolor='#0a0a0a',
            bbox_inches='tight')
print("\n-> bin_peel.png")

# ── Attribution figure ──────────────────────────────────────────────
abs_comps = np.stack([np.abs(c) for c in comps], axis=-1)
max_comp = abs_comps.max(axis=-1)
bin_argmax = np.argmax(abs_comps, axis=-1)
abs_resid = np.abs(resid)

# Pan-bin candidates: cells where |R| exceeds the max component magnitude
# AND is above the global 90th percentile of |G|.
gate = float(np.nanpercentile(abs_resid, 90))
multi_bin = (abs_resid > max_comp) & (abs_resid > gate)
print(f"\nPan-bin gate: |R| > max_i|α_i P_i| AND |R| > {gate:.4f} "
      f"({100 * np.sum(multi_bin) / multi_bin.size:.1f}% of cells)")

fig2, (ax_a, ax_r) = plt.subplots(1, 2, figsize=(15, 6.5))
fig2.patch.set_facecolor('#0a0a0a')

cmap_attr = ListedColormap(['#ffcc5c', '#6ec6ff', '#a3e4a3', '#cf9fff'])
ax_a.imshow(bin_argmax, origin='lower', extent=extent, aspect='equal',
            cmap=cmap_attr, vmin=-0.5, vmax=3.5, interpolation='nearest')
ax_a.set_title(
    'Dominant bin per cell\n'
    '1=rank algebra (yellow)  2=decade (blue)  '
    '3=K-asymp (green)  4=Mertens (violet)',
    color='white', fontsize=10)
ax_a.set_facecolor('#0a0a0a')
ax_a.set_xlabel('K', color='white'); ax_a.set_ylabel('n_0', color='white')

display = np.where(multi_bin, abs_resid, np.nan)
im_r = ax_r.imshow(display, origin='lower', extent=extent, aspect='equal',
                   cmap='magma', interpolation='nearest')
ax_r.set_title(
    'Pan-bin candidates  (|R| beats every fitted component)',
    color='white', fontsize=10)
ax_r.set_facecolor('#0a0a0a')
ax_r.set_xlabel('K', color='white'); ax_r.set_ylabel('n_0', color='white')
plt.colorbar(im_r, ax=ax_r, fraction=0.04, pad=0.02)

for ax in (ax_a, ax_r):
    ax.tick_params(colors='white', labelsize=8)
    for spine in ax.spines.values():
        spine.set_color('#333')

fig2.tight_layout()
fig2.savefig('bin_attribution.png', dpi=180, facecolor='#0a0a0a',
             bbox_inches='tight')
print("-> bin_attribution.png")
