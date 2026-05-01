"""
exp04_best_trajectories.py — show what the deepest L1 dips actually
look like along the read order.

For a handful of standout configs from exp04_topK.txt, plot the
running L1 trajectory and mark the deepest dip. Lets us see whether
the Pareto-best configs have a single deep canyon or oscillate near
zero across a range.

Outputs:
    exp04_best_trajectories.png
"""

import os
import sys
from math import log

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

OUT = os.path.join(HERE, 'exp04_best_trajectories.png')

u9 = np.full(9, 1.0 / 9)


def n_primes_vec(n: int, k: int) -> np.ndarray:
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


def trajectory(n0, w, k):
    """Returns (digit_length_cum, l1_cum) along survivor read order."""
    parts = [n_primes_vec(n, k) for n in range(n0, n0 + w)]
    m_arr = np.concatenate(parts)
    _, inverse, counts = np.unique(m_arr, return_inverse=True, return_counts=True)
    mask = counts[inverse] == 1
    surv_idx = np.where(mask)[0]
    surv = m_arr[surv_idx]
    if surv.size == 0:
        return np.array([]), np.array([])

    log_floor = np.floor(np.log10(surv)).astype(np.int64)
    leading = (surv // 10 ** log_floor).astype(np.int64)
    digit_lens = log_floor + 1
    n_surv = surv.size

    ld = np.zeros((n_surv, 9), dtype=np.int64)
    ld[np.arange(n_surv), leading - 1] = 1
    cum = np.cumsum(ld, axis=0)
    tot = cum.sum(axis=1)
    p = cum / tot[:, None]
    l1 = np.abs(p - u9).sum(axis=1)
    cum_len = np.cumsum(digit_lens)
    return cum_len, l1


CONFIGS = [
    # (n_0, W, k, label, color)
    (11, 3, 10, 'n_0=11, W=3, k=10  (L1=0 at L=18)', '#ffcc5c'),
    (34, 15, 275, 'n_0=34, W=15, k=275  (L1=0.003 at L≈3000)', '#6ec6ff'),
    (20, 3, 470, 'n_0=20, W=3, k=470  (L1<0.01 at L≈3200)', '#ff8888'),
    (9, 15, 500, 'n_0=9, W=15, k=500  (L1=0.10 at L≈12000)', '#ff5588'),
    (32, 20, 500, 'n_0=32, W=20, k=500  (high-length comparison)', '#aaaaaa'),
]

fig, axes = plt.subplots(2, 1, figsize=(14, 10), dpi=140,
                         gridspec_kw={'height_ratios': [3, 2]})
fig.patch.set_facecolor('#0a0a0a')
for ax in axes:
    ax.set_facecolor('#0a0a0a')

ax_log = axes[0]
ax_lin = axes[1]

for n0, w, k, label, color in CONFIGS:
    cum_len, l1 = trajectory(n0, w, k)
    if l1.size == 0:
        continue
    ax_log.plot(cum_len, l1, color=color, linewidth=1.0, alpha=0.85, label=label)
    ax_lin.plot(cum_len, l1, color=color, linewidth=1.0, alpha=0.85, label=label)
    # Mark trajectory min
    j = int(np.argmin(l1))
    ax_log.scatter([cum_len[j]], [max(l1[j], 1e-4)], color=color,
                   s=42, edgecolor='white', linewidth=0.7, zorder=5)
    ax_lin.scatter([cum_len[j]], [l1[j]], color=color,
                   s=42, edgecolor='white', linewidth=0.7, zorder=5)

for ax, ylabel, yscale in [(ax_log, 'L1 deviation (log y)', 'log'),
                            (ax_lin, 'L1 deviation (linear y, zoom)', 'linear')]:
    ax.set_xscale('log')
    ax.set_yscale(yscale)
    ax.set_xlabel('digit length accumulated', color='white', fontsize=11)
    ax.set_ylabel(ylabel, color='white', fontsize=11)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#333')
    ax.grid(True, alpha=0.18, color='#888', which='both')
    ax.legend(loc='upper right', fontsize=8.5, framealpha=0.4,
              labelcolor='white', facecolor='#1a1a1a')

ax_lin.set_ylim(-0.01, 0.2)

fig.suptitle(
    'Survivor-real L1 trajectories at standout configs\n'
    '(dots = trajectory minima; the configs that achieve them at long length)',
    color='white', fontsize=13, y=0.99
)

plt.tight_layout()
plt.savefig(OUT, dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
plt.close()
print(f'-> {OUT}')
