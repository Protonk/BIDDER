"""
Residual plot — testing the disentanglement reading.

If the wiggles in the L1 trajectory are the system disentangling
from an early intransitive regime, then |L1(n) − L1_asymptote|
should show a slow, structured decay across the atom horizon —
ideally with stream-transition kicks visible as bumps.

Computes step-interpolated L1 curves on a common atom-slot grid,
then plots absolute residuals from each curve's end-of-stream value.
Stream transitions (every 400 atoms in slot order) marked as
guides.
"""

import numpy as np
import matplotlib.pyplot as plt
from sympy import isprime

W = 9
n_0 = 2
n_1 = n_0 + W - 1
k = 400


def n_primes_vec(n, k):
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


parts_per_stream = [(n, n_primes_vec(n, k))
                    for n in range(n_0, n_1 + 1)]
all_atoms = np.concatenate([arr for _, arr in parts_per_stream])
n_atoms = all_atoms.size
stream_tag = np.concatenate([np.full_like(arr, n)
                             for n, arr in parts_per_stream])

unique_vals, first_idx, counts = np.unique(
    all_atoms, return_index=True, return_counts=True)
surv_mask = counts == 1
S = unique_vals[surv_mask]
sources_S = stream_tag[first_idx[surv_mask]]
m_S = S // sources_S
prime_m = np.array([isprime(int(m)) for m in m_S])

prime_m_set = set(int(c) for c, pm in zip(S, prime_m) if pm)
composite_m_set = set(int(c) for c, pm in zip(S, prime_m) if not pm)

lead = np.zeros(n_atoms, dtype=np.int64)
for i, c in enumerate(all_atoms):
    c_int = int(c)
    log_floor = int(np.floor(np.log10(c_int)))
    lead[i] = c_int // 10**log_floor

u9 = np.full(9, 1.0 / 9)


def running_l1(membership):
    seen = set()
    counts_arr = np.zeros(9, dtype=np.int64)
    out_l1, out_idx = [], []
    for i in range(n_atoms):
        c = int(all_atoms[i])
        if c in seen:
            continue
        seen.add(c)
        if not membership(c):
            continue
        counts_arr[lead[i] - 1] += 1
        tot = counts_arr.sum()
        p = counts_arr / tot
        out_l1.append(np.abs(p - u9).sum())
        out_idx.append(i)
    return np.array(out_idx), np.array(out_l1)


idx_b, l1_b = running_l1(lambda c: True)
idx_pm, l1_pm = running_l1(lambda c: c in prime_m_set)
idx_cm, l1_cm = running_l1(lambda c: c in composite_m_set)

asym_b = l1_b[-1]
asym_pm = l1_pm[-1]
asym_cm = l1_cm[-1]
print(f"Asymptotes: bundle {asym_b:.4f}, "
      f"prime-m {asym_pm:.4f}, composite-m {asym_cm:.4f}")


def step_interp(idx, vals, x):
    positions = np.searchsorted(idx, x, side='right') - 1
    out = np.full(len(x), np.nan)
    valid = positions >= 0
    out[valid] = vals[positions[valid]]
    return out


grid = np.arange(n_atoms)
L1_b_full = step_interp(idx_b, l1_b, grid)
L1_pm_full = step_interp(idx_pm, l1_pm, grid)
L1_cm_full = step_interp(idx_cm, l1_cm, grid)

res_b = L1_b_full - asym_b
res_pm = L1_pm_full - asym_pm
res_cm = L1_cm_full - asym_cm

# --- Plot 1: |residual|, log y, linear x ---
fig, ax = plt.subplots(figsize=(14, 7))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

ax.plot(grid, np.abs(res_b), color='#ffa642', linewidth=1.0,
        label=f'bundle  (asym {asym_b:.3f})', alpha=0.9)
ax.plot(grid, np.abs(res_pm), color='#5cd4ff', linewidth=1.0,
        label=f'surv, prime cofactor  (asym {asym_pm:.3f})',
        alpha=0.9)
ax.plot(grid, np.abs(res_cm), color='#cc66ff', linewidth=1.0,
        label=f'surv, composite cofactor  (asym {asym_cm:.3f})',
        alpha=0.9)

# Stream transitions in atom-slot space.
for transition_n, slot in [(n, i * 400) for i, n in
                            enumerate(range(n_0, n_1 + 1))]:
    if slot == 0:
        continue
    ax.axvline(slot, color='#444', linestyle='--', linewidth=0.6,
               alpha=0.7)
    ax.text(slot, 1.5, f'n={transition_n}',
            color='#888', ha='center', va='top', fontsize=9)

ax.set_yscale('log')
ax.set_xlabel('atoms processed (read order)',
              color='white', fontsize=11)
ax.set_ylabel('|L1(n) − asymptote|',
              color='white', fontsize=11)
ax.set_title(
    'L1 residuals from 3-line asymptote  '
    f'([{n_0},{n_1}], k={k})  '
    '— disentangling intransitivity, with stream transitions',
    color='white', fontsize=11)
ax.tick_params(colors='white', which='both')
for spine in ax.spines.values():
    spine.set_color('#333')
ax.legend(loc='lower left', facecolor='#1a1a1a',
          edgecolor='#333', labelcolor='white', fontsize=10)
ax.grid(alpha=0.15, color='#444', which='both')

plt.tight_layout()
plt.savefig('primality_l1_residuals.png', dpi=170,
            facecolor='#0a0a0a', bbox_inches='tight')
print("-> primality_l1_residuals.png")

# --- Plot 2: log-log to test power-law decay ---
fig, ax = plt.subplots(figsize=(14, 7))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

# Bin to smooth: take running rms over windows of 50 atoms
def rms_smooth(arr, w=50):
    out = np.full_like(arr, np.nan)
    for i in range(w, len(arr)):
        out[i] = np.sqrt(np.nanmean(arr[i - w:i] ** 2))
    return out


smooth_b = rms_smooth(np.abs(res_b))
smooth_pm = rms_smooth(np.abs(res_pm))
smooth_cm = rms_smooth(np.abs(res_cm))

ax.loglog(grid, smooth_b, color='#ffa642', linewidth=1.4,
          label='bundle', alpha=0.9)
ax.loglog(grid, smooth_pm, color='#5cd4ff', linewidth=1.4,
          label='surv prime cofactor', alpha=0.9)
ax.loglog(grid, smooth_cm, color='#cc66ff', linewidth=1.4,
          label='surv composite cofactor', alpha=0.9)

for slot in [400, 800, 1200, 1600, 2000, 2400, 2800, 3200]:
    ax.axvline(slot, color='#444', linestyle='--', linewidth=0.5,
               alpha=0.5)

# Reference power laws
xref = np.array([100, 3000])
for slope, ls, lab in [(-0.5, '--', '∝ n^(−1/2)'),
                        (-1.0, ':', '∝ n^(−1)')]:
    yref = 0.5 * (xref / 100) ** slope
    ax.loglog(xref, yref, color='#777', linestyle=ls,
              linewidth=0.9, label=lab)

ax.set_xlabel('atoms processed (read order)',
              color='white', fontsize=11)
ax.set_ylabel('rms |residual| (50-atom window)',
              color='white', fontsize=11)
ax.set_title(
    'Residual decay envelope — log-log  '
    '(power-law slope tests)',
    color='white', fontsize=11)
ax.tick_params(colors='white', which='both')
for spine in ax.spines.values():
    spine.set_color('#333')
ax.legend(loc='lower left', facecolor='#1a1a1a',
          edgecolor='#333', labelcolor='white', fontsize=10)
ax.grid(alpha=0.15, color='#444', which='both')
plt.tight_layout()
plt.savefig('primality_l1_residuals_loglog.png', dpi=170,
            facecolor='#0a0a0a', bbox_inches='tight')
print("-> primality_l1_residuals_loglog.png")

# Numerical summary: residual rms per stream interval.
print()
print("RMS |residual| per stream-segment of bundle's atom slots:")
print(f"{'segment':>20} {'bundle':>10} {'prime-m':>10} "
      f"{'comp-m':>10}")
for n_s, lo, hi in [(2, 0, 400), (3, 400, 800), (4, 800, 1200),
                     (5, 1200, 1600), (6, 1600, 2000),
                     (7, 2000, 2400), (8, 2400, 2800),
                     (9, 2800, 3200), (10, 3200, n_atoms)]:
    seg = (grid >= lo) & (grid < hi)
    rb = np.sqrt(np.nanmean(res_b[seg] ** 2))
    rp = np.sqrt(np.nanmean(res_pm[seg] ** 2))
    rc = np.sqrt(np.nanmean(res_cm[seg] ** 2))
    print(f"  stream n={n_s} ({lo}-{hi})  {rb:>10.4f} "
          f"{rp:>10.4f} {rc:>10.4f}")
