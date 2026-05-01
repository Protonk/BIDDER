"""
n_fingerprint.py — six readouts per n, four bins, one ladder.

Per-n readouts:
  bin1   max |Q_n(m)| over m ≤ 10⁴ with h ≤ 4   (predict_q.q_general)
  bin2a  base-10 leading-digit L1 of first 10⁴ n-primes
  bin2b  |mean bit-fraction − 0.5| over the same atoms
  bin3   slope of log₁₀(L1) vs log₁₀(K), K ∈ {10³, 2·10³, 5·10³, 10⁴}
  bin4a  S_4(n, 10) closed form (cf/MEGA-SPIKE.md)
  bin4b  ψ_{M_n}(10⁵)/10⁵ − 1                   (beurling/zeta_mn.psi_mn)
"""

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'algebra'))
sys.path.insert(0, os.path.join(ROOT, 'experiments', 'math', 'beurling'))

from predict_q import q_general
from zeta_mn import psi_mn


NS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
      14, 15, 16, 18, 20, 25, 27, 30, 32]
M_MAX = 10_000
H_MAX = 4
PSI_X = 100_000
KS = np.array([1000, 2000, 5000, 10000])

LABELS = ['bin1', 'bin2a', 'bin2b', 'bin3', 'bin4a', 'bin4b']
PRETTY = ['Bin 1\nQ_n env', 'Bin 2a\nL1 base10', 'Bin 2b\nbit dev',
          'Bin 3\nK-slope', 'Bin 4a\nS_4', 'Bin 4b\nψ/x−1']


def n_primes_vec(n, k):
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    return (n * m[m % n != 0][:k]).astype(np.int64)


def nu_n(m, n):
    h = 0
    while m % n == 0:
        h += 1
        m //= n
    return h, m


def bin1_q_envelope(n):
    best = 0.0
    for m in range(n, M_MAX + 1, n):
        h, kk = nu_n(m, n)
        if h > H_MAX:
            continue
        q = abs(float(q_general(n, h, kk)))
        if q > best:
            best = q
    return best


def leading_digits_b10(primes):
    log_floor = np.floor(np.log10(primes)).astype(np.int64)
    return (primes // 10**log_floor).astype(np.int64)


def bin2a_l1(leading):
    counts = np.bincount(leading, minlength=10)[1:10]
    p = counts / counts.sum()
    return float(np.abs(p - 1.0 / 9).sum())


def bin2b_bit_deficit(primes):
    total_ones, total_bits = 0, 0
    for m in primes:
        m_int = int(m)
        total_ones += bin(m_int).count('1')
        total_bits += m_int.bit_length()
    return abs(total_ones / total_bits - 0.5)


def bin3_K_slope(leading):
    L1s = []
    for kk in KS:
        sub = leading[:kk]
        counts = np.bincount(sub, minlength=10)[1:10]
        p = counts / counts.sum()
        L1s.append(float(np.abs(p - 1.0 / 9).sum()))
    slope, _ = np.polyfit(np.log10(KS), np.log10(L1s), 1)
    return float(slope)


def bin4a_cf_spike(n, b=10, k=4):
    return (n - 1) / n**2 * (b**(k - 1) * (k * (b - 2) + b / (b - 1))
                             - 1.0 / (b - 1))


def bin4b_psi_residual(n):
    return float(psi_mn(n, PSI_X)) / PSI_X - 1.0


def spearman(data):
    ranks = np.argsort(np.argsort(data, axis=0), axis=0).astype(float)
    return np.corrcoef(ranks.T)


# ── Run ────────────────────────────────────────────────────────────
print(f"Computing six readouts on {len(NS)} n's "
      f"(M_MAX={M_MAX}, PSI_X={PSI_X})...")

import time
t0 = time.time()
results = []
for n in NS:
    primes = n_primes_vec(n, M_MAX)
    leading = leading_digits_b10(primes)
    r = (n,
         bin1_q_envelope(n),
         bin2a_l1(leading),
         bin2b_bit_deficit(primes),
         bin3_K_slope(leading),
         bin4a_cf_spike(n),
         bin4b_psi_residual(n))
    results.append(r)
    print(f"  n={n:3d}  bin1={r[1]:.4f}  bin2a={r[2]:.4f}  "
          f"bin2b={r[3]:.4f}  bin3={r[4]:+.3f}  bin4a={r[5]:9.1f}  "
          f"bin4b={r[6]:+.5f}   "
          f"t={time.time()-t0:.1f}s")

data = np.array([r[1:] for r in results], dtype=float)
ns_arr = np.array([r[0] for r in results])

# Save table.
with open(os.path.join(HERE, 'n_fingerprint_table.txt'), 'w') as f:
    f.write(f"{'n':>4s}  " + "  ".join(f"{lab:>11s}" for lab in LABELS) + "\n")
    for r in results:
        f.write(f"{r[0]:4d}  "
                f"{r[1]:11.4f}  {r[2]:11.4f}  {r[3]:11.4f}  "
                f"{r[4]:+11.3f}  {r[5]:11.1f}  {r[6]:+11.5f}\n")
print("\n-> n_fingerprint_table.txt")

# Spearman corr.
corr = spearman(data)
print("\nSpearman correlation:")
print("       " + "  ".join(f"{lab:>6s}" for lab in LABELS))
for i, lab in enumerate(LABELS):
    print(f"  {lab:>5s}  " + "  ".join(f"{corr[i, j]:+.3f}"
                                       for j in range(6)))

# ── Correlation heatmap ────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8.0, 7.2))
fig.patch.set_facecolor('#0a0a0a')
ax.set_facecolor('#0a0a0a')
im = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1)
for i in range(6):
    for j in range(6):
        ax.text(j, i, f"{corr[i, j]:+.2f}",
                ha='center', va='center',
                color='white' if abs(corr[i, j]) > 0.5 else '#ccc',
                fontsize=10)
ax.set_xticks(range(6)); ax.set_xticklabels(PRETTY, color='white', fontsize=9)
ax.set_yticks(range(6)); ax.set_yticklabels(PRETTY, color='white', fontsize=9)
ax.tick_params(colors='white', length=0)
for spine in ax.spines.values():
    spine.set_color('#333')
plt.colorbar(im, ax=ax, fraction=0.045, pad=0.03)
ax.set_title('Spearman rank correlation across 20 n', color='white',
             fontsize=12)
fig.tight_layout()
fig.savefig(os.path.join(HERE, 'n_fingerprint_corr.png'),
            dpi=180, facecolor='#0a0a0a', bbox_inches='tight')
print("-> n_fingerprint_corr.png")

# ── Parallel-coordinates plot ──────────────────────────────────────
ranks = np.argsort(np.argsort(data, axis=0), axis=0).astype(float)
ranks_norm = ranks / (len(NS) - 1)

fig2, ax2 = plt.subplots(figsize=(13, 6.5))
fig2.patch.set_facecolor('#0a0a0a')
ax2.set_facecolor('#0a0a0a')

cmap = plt.cm.viridis
xs = np.arange(6)
for i, n in enumerate(ns_arr):
    color = cmap(i / (len(ns_arr) - 1))
    ax2.plot(xs, ranks_norm[i], '-o', color=color, alpha=0.8,
             linewidth=1.4, markersize=5,
             label=f'n={n}')

ax2.set_xticks(xs)
ax2.set_xticklabels(PRETTY, color='white', fontsize=9)
ax2.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax2.set_yticklabels(['low', '', 'mid', '', 'high'], color='white')
ax2.tick_params(colors='white')
for spine in ax2.spines.values():
    spine.set_color('#333')
ax2.grid(True, color='#222', linewidth=0.5)
ax2.set_ylabel('rank-normalised value', color='white', fontsize=11)
ax2.legend(loc='center left', bbox_to_anchor=(1.01, 0.5),
           fontsize=8, ncol=2, framealpha=0.3,
           labelcolor='white', facecolor='#1a1a1a')
ax2.set_title('Parallel coordinates — n-ladder threading the six readouts',
              color='white', fontsize=12)
fig2.tight_layout()
fig2.savefig(os.path.join(HERE, 'n_fingerprint_parallel.png'),
             dpi=180, facecolor='#0a0a0a', bbox_inches='tight')
print("-> n_fingerprint_parallel.png")
print(f"\ntotal: {time.time()-t0:.1f}s")
