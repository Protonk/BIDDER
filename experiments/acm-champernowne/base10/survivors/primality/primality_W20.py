"""
EXP03 — wider window test (W=20 at n_0=2, K=400).

Bet: bracketing compresses but stays 2-way; residual decay rate
per stream-segment stays around 0.6; some fracturing at high-d
streams plausible.

Computes for both W=9 (the canonical Two Tongues panel) and W=20:
  - asymptotic L1 levels for bundle, prime-cofactor, composite-cofactor
  - prime-cofactor fractions
  - per-source-d primality table
  - RMS residual decay per stream segment
  - L1 trajectory comparison plot
"""

import numpy as np
import matplotlib.pyplot as plt
from sympy import isprime


def n_primes_vec(n, k):
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


def build_panel(n_0, W, k):
    n_1 = n_0 + W - 1
    parts = [(n, n_primes_vec(n, k))
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

    return {
        'n_0': n_0, 'n_1': n_1, 'W': W, 'k': k,
        'all_atoms': all_atoms, 'stream_tag': stream_tag,
        'n_atoms': n_atoms,
        'unique_vals': unique_vals, 'first_idx': first_idx,
        'counts': counts, 'surv_mask': surv_mask,
        'S': S, 'sources_S': sources_S,
        'm_S': m_S, 'prime_m': prime_m,
    }


def running_l1_for_membership(panel, in_set):
    all_atoms = panel['all_atoms']
    n_atoms = panel['n_atoms']
    seen = set()
    counts_arr = np.zeros(9, dtype=np.int64)
    out_l1, out_idx = [], []
    u9 = np.full(9, 1.0 / 9)
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


def analyze(panel):
    S = panel['S']
    prime_m = panel['prime_m']
    sources_S = panel['sources_S']
    unique_vals = panel['unique_vals']

    bundle_set = set(int(c) for c in unique_vals)
    pm_set = set(int(c) for c, pm in zip(S, prime_m) if pm)
    cm_set = set(int(c) for c, pm in zip(S, prime_m) if not pm)

    idx_b, l1_b = running_l1_for_membership(panel, bundle_set)
    idx_pm, l1_pm = running_l1_for_membership(panel, pm_set)
    idx_cm, l1_cm = running_l1_for_membership(panel, cm_set)

    # Step-interpolate to common grid for residuals.
    grid = np.arange(panel['n_atoms'])

    def step_interp(idx, vals, x):
        positions = np.searchsorted(idx, x, side='right') - 1
        out = np.full(len(x), np.nan)
        valid = positions >= 0
        out[valid] = vals[positions[valid]]
        return out

    L1_b = step_interp(idx_b, l1_b, grid)
    L1_pm = step_interp(idx_pm, l1_pm, grid)
    L1_cm = step_interp(idx_cm, l1_cm, grid)

    return {
        'idx_b': idx_b, 'l1_b': l1_b,
        'idx_pm': idx_pm, 'l1_pm': l1_pm,
        'idx_cm': idx_cm, 'l1_cm': l1_cm,
        'L1_b': L1_b, 'L1_pm': L1_pm, 'L1_cm': L1_cm,
        'asym_b': float(l1_b[-1]),
        'asym_pm': float(l1_pm[-1]),
        'asym_cm': float(l1_cm[-1]),
        'pm_set': pm_set, 'cm_set': cm_set,
    }


# Build both panels
print("Building panels...")
P9 = build_panel(2, 9, 400)
P20 = build_panel(2, 20, 400)
print(f"W=9:  n_atoms={P9['n_atoms']}, "
      f"|unique|={len(P9['unique_vals'])}, "
      f"|S|={len(P9['S'])} ({100 * len(P9['S']) / len(P9['unique_vals']):.1f}%)")
print(f"W=20: n_atoms={P20['n_atoms']}, "
      f"|unique|={len(P20['unique_vals'])}, "
      f"|S|={len(P20['S'])} ({100 * len(P20['S']) / len(P20['unique_vals']):.1f}%)")
print()

print("Analysing...")
A9 = analyze(P9)
A20 = analyze(P20)

# Comparison numbers.
def report(P, A, label):
    pm_count = int(P['prime_m'].sum())
    total = len(P['S'])
    print(f"{label}:")
    print(f"  prime-cofactor fraction:   {pm_count / total:.3f}  "
          f"({pm_count}/{total})")
    print(f"  asymptotes (L1):  bundle {A['asym_b']:.4f}, "
          f"prime-m {A['asym_pm']:.4f}, comp-m {A['asym_cm']:.4f}")
    print(f"  bracketing gap:   prime→bundle {A['asym_b'] - A['asym_pm']:+.4f}, "
          f"bundle→comp {A['asym_cm'] - A['asym_b']:+.4f}, "
          f"total {A['asym_cm'] - A['asym_pm']:+.4f}")


report(P9, A9, "W=9")
report(P20, A20, "W=20")
print()

# Per-source d primality fraction at W=20.
print("Per source d at W=20: prime-cofactor fraction")
print(f"{'d':>3} {'|S_d|':>6} {'prime m':>8} {'frac':>6}")
for d in range(P20['n_0'], P20['n_1'] + 1):
    md = P20['sources_S'] == d
    nd = int(md.sum())
    if nd == 0:
        continue
    pm = int(P20['prime_m'][md].sum())
    print(f"{d:>3} {nd:>6} {pm:>8} {pm / nd:>6.3f}")
print()

# RMS residual per stream segment, both W's.
def per_stream_rms(P, A):
    grid = np.arange(P['n_atoms'])
    res_b = A['L1_b'] - A['asym_b']
    res_pm = A['L1_pm'] - A['asym_pm']
    res_cm = A['L1_cm'] - A['asym_cm']
    rows = []
    for n_s in range(P['n_0'], P['n_1'] + 1):
        lo = (n_s - P['n_0']) * P['k']
        hi = lo + P['k']
        seg = (grid >= lo) & (grid < hi)
        rb = float(np.sqrt(np.nanmean(res_b[seg] ** 2)))
        rp = float(np.sqrt(np.nanmean(res_pm[seg] ** 2)))
        rc = float(np.sqrt(np.nanmean(res_cm[seg] ** 2)))
        rows.append((n_s, lo, hi, rb, rp, rc))
    return rows


rms9 = per_stream_rms(P9, A9)
rms20 = per_stream_rms(P20, A20)

print("RMS |residual| per stream segment — W=9:")
print(f"{'stream':>10} {'bundle':>10} {'prime-m':>10} {'comp-m':>10}")
for n_s, lo, hi, rb, rp, rc in rms9:
    print(f"   n={n_s:<3d}    {rb:>10.4f} {rp:>10.4f} {rc:>10.4f}")
print()

print("RMS |residual| per stream segment — W=20:")
print(f"{'stream':>10} {'bundle':>10} {'prime-m':>10} {'comp-m':>10}")
for n_s, lo, hi, rb, rp, rc in rms20:
    print(f"   n={n_s:<3d}    {rb:>10.4f} {rp:>10.4f} {rc:>10.4f}")
print()

# --- Plot: L1 trajectory at W=20 ---
fig, ax = plt.subplots(figsize=(13, 6))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')
ax.plot(A20['idx_b'], A20['l1_b'], color='#ffa642',
        linewidth=1.4, label=f"bundle  (n={len(A20['idx_b'])})")
ax.plot(A20['idx_pm'], A20['l1_pm'], color='#5cd4ff',
        linewidth=1.4,
        label=f"surv, prime cofactor  (n={len(A20['idx_pm'])})")
ax.plot(A20['idx_cm'], A20['l1_cm'], color='#cc66ff',
        linewidth=1.4,
        label=f"surv, composite cofactor  (n={len(A20['idx_cm'])})")
for slot in range(400, P20['n_atoms'], 400):
    ax.axvline(slot, color='#444', linestyle='--',
               linewidth=0.4, alpha=0.5)
ax.set_yscale('log')
ax.set_xlabel('atoms processed (read order)', color='white')
ax.set_ylabel('L1 deviation from uniform (leading digit 1-9)',
              color='white')
ax.set_title(
    f"L1 trajectory at W=20  ([2, 21], k=400)  "
    f"— stream transitions every 400 atoms",
    color='white')
ax.tick_params(colors='white', which='both')
for spine in ax.spines.values():
    spine.set_color('#333')
ax.legend(loc='upper right', facecolor='#1a1a1a',
          edgecolor='#333', labelcolor='white', fontsize=10)
ax.grid(alpha=0.15, color='#444', which='both')
plt.tight_layout()
plt.savefig('primality_W20.png', dpi=170, facecolor='#0a0a0a',
            bbox_inches='tight')
print("-> primality_W20.png")

# --- Comparison plot: residual decay envelope per stream segment ---
fig, ax = plt.subplots(figsize=(13, 6))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')

s9 = [r[0] for r in rms9]
b9 = [r[3] for r in rms9]
p9 = [r[4] for r in rms9]
c9 = [r[5] for r in rms9]

s20 = [r[0] for r in rms20]
b20 = [r[3] for r in rms20]
p20 = [r[4] for r in rms20]
c20 = [r[5] for r in rms20]

ax.semilogy(s9, b9, 'o-', color='#ffa642', linewidth=1.5,
            markersize=7, label='W=9 bundle')
ax.semilogy(s9, p9, 's-', color='#5cd4ff', linewidth=1.5,
            markersize=7, label='W=9 prime-m')
ax.semilogy(s9, c9, 'D-', color='#cc66ff', linewidth=1.5,
            markersize=7, label='W=9 comp-m')

ax.semilogy(s20, b20, 'o--', color='#ffa642', linewidth=1.0,
            markersize=5, alpha=0.55, label='W=20 bundle')
ax.semilogy(s20, p20, 's--', color='#5cd4ff', linewidth=1.0,
            markersize=5, alpha=0.55, label='W=20 prime-m')
ax.semilogy(s20, c20, 'D--', color='#cc66ff', linewidth=1.0,
            markersize=5, alpha=0.55, label='W=20 comp-m')

ax.set_xlabel('stream segment n', color='white', fontsize=11)
ax.set_ylabel('RMS |residual|  (log y)', color='white', fontsize=11)
ax.set_title(
    'Residual decay per stream segment — W=9 vs W=20',
    color='white', fontsize=12)
ax.tick_params(colors='white', which='both')
for spine in ax.spines.values():
    spine.set_color('#333')
ax.legend(loc='upper right', facecolor='#1a1a1a',
          edgecolor='#333', labelcolor='white', fontsize=9, ncol=2)
ax.grid(alpha=0.15, color='#444', which='both')
plt.tight_layout()
plt.savefig('primality_W9_vs_W20_residuals.png', dpi=170,
            facecolor='#0a0a0a', bbox_inches='tight')
print("-> primality_W9_vs_W20_residuals.png")
