"""
Zoom views of the L1 bracketing.

Two extensions of `primality_l1.png`:
  early — atoms 0–500 on log y, captures the dramatic n=2 dip
  mid   — atoms 1000–1500 on linear y, captures the bracketing
          in the flat regime where the log scale compresses it
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


def render(title, fname, xlim, yscale, ylim=None):
    fig, ax = plt.subplots(figsize=(11, 6))
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')
    ax.plot(idx_b, l1_b, color='#ffa642', linewidth=1.6,
            label=f'bundle  (n={len(idx_b)})')
    ax.plot(idx_pm, l1_pm, color='#5cd4ff', linewidth=1.6,
            label=f'surv, prime cofactor  (n={len(idx_pm)})')
    ax.plot(idx_cm, l1_cm, color='#cc66ff', linewidth=1.6,
            label=f'surv, composite cofactor  (n={len(idx_cm)})')
    ax.set_yscale(yscale)
    ax.set_xlim(*xlim)
    if ylim is not None:
        ax.set_ylim(*ylim)
    ax.set_xlabel('atoms processed (read order)',
                  color='white', fontsize=11)
    ax.set_ylabel('L1 deviation from uniform (leading digit 1-9)',
                  color='white', fontsize=11)
    ax.set_title(title, color='white', fontsize=12)
    ax.tick_params(colors='white', which='both')
    for spine in ax.spines.values():
        spine.set_color('#333')
    ax.legend(loc='upper right', facecolor='#1a1a1a',
              edgecolor='#333', labelcolor='white', fontsize=10)
    ax.grid(alpha=0.15, color='#444', which='both')
    plt.tight_layout()
    plt.savefig(fname, dpi=170, facecolor='#0a0a0a',
                bbox_inches='tight')
    print(f"-> {fname}")


# Zoom 1: atoms 0-500, log y (preserves the n=2 dip dynamics).
render(
    f'L1 bracketing through n=2 dip — atoms 0-500  '
    f'([{n_0},{n_1}], k={k})',
    'primality_l1_zoom_early.png',
    xlim=(0, 500), yscale='log')

# Zoom 2: atoms 1000-1500, linear y (decompresses the flat regime).
mask_b = (idx_b >= 1000) & (idx_b <= 1500)
mask_pm = (idx_pm >= 1000) & (idx_pm <= 1500)
mask_cm = (idx_cm >= 1000) & (idx_cm <= 1500)
y_min = min(l1_pm[mask_pm].min(), l1_b[mask_b].min(),
            l1_cm[mask_cm].min())
y_max = max(l1_cm[mask_cm].max(), l1_b[mask_b].max(),
            l1_pm[mask_pm].max())
print(f"  mid window y-range: [{y_min:.4f}, {y_max:.4f}]")

render(
    f'L1 bracketing in the flat regime — atoms 1000-1500  '
    f'([{n_0},{n_1}], k={k})',
    'primality_l1_zoom_mid.png',
    xlim=(1000, 1500), yscale='linear',
    ylim=(y_min - 0.02, y_max + 0.02))

# Reportable spreads in each zoom range.
print()
print("Bracketing gap (composite − prime, on co-evaluated atom indices):")
for lo, hi, label in [(0, 500, 'early'),
                       (1000, 1500, 'mid')]:
    mb = (idx_b >= lo) & (idx_b <= hi)
    mp = (idx_pm >= lo) & (idx_pm <= hi)
    mc = (idx_cm >= lo) & (idx_cm <= hi)
    print(f"  {label:6s} atoms {lo:>4d}-{hi:<4d}: "
          f"bundle range [{l1_b[mb].min():.3f}, {l1_b[mb].max():.3f}]; "
          f"prime-m [{l1_pm[mp].min():.3f}, {l1_pm[mp].max():.3f}]; "
          f"comp-m  [{l1_cm[mc].min():.3f}, {l1_cm[mc].max():.3f}]")
