"""
detrended_rds_n3.py — single-panel RDS(t) plot for n = 3.

Large standalone version of the n = 3 sub-panel from
detrended_rds_curves.png, intended for close inspection of the
running digital sum's structure. Both the v_2(n)-only expected
drift and the per-entry expected drift are overlaid.
"""

import sys
import os
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..'))                              # base2/
sys.path.insert(0, os.path.join(_here, '..', '..', '..', '..', '..', 'core'))    # core/

from acm_core import acm_n_primes


# ── Parameters ──────────────────────────────────────────────────────

N = 3
TARGET_BITS = 100_000


# ── Helpers (mirroring detrended_rds.py) ────────────────────────────

def v2_of(n):
    v = 0
    while n % 2 == 0:
        v += 1
        n //= 2
    return v


def slope_for_entry(m, d):
    if m == 0:
        return 1.0
    if d <= 2 * m:
        return 1.0 - m
    return 1.0 - 2.0 * m + (m * (2 ** m)) / (2 ** m - 1)


def estimate_count(n, target_bits):
    avg = math.log2(max(n, 2)) + math.log2(max(target_bits // 20, 4))
    return int(target_bits / max(avg, 4)) + 200


def gen_for_monoid(n, target_bits):
    count = estimate_count(n, target_bits)
    while True:
        primes = acm_n_primes(n, 2 * count)
        cum = 0
        used = []
        for p in primes:
            d = p.bit_length()
            if cum + d > target_bits:
                break
            cum += d
            used.append(p)
        if len(used) > 0 and cum >= target_bits - 200:
            bits = []
            for p in used:
                for c in bin(p)[2:]:
                    bits.append(int(c))
            return np.array(bits, dtype=np.int8), used
        count *= 2


def compute_rds(bits):
    pm = 2 * bits.astype(np.int64) - 1
    return np.concatenate(([0], np.cumsum(pm)))


def expected_curve_monoid(entries, m, n_bits):
    ds = np.array([p.bit_length() for p in entries], dtype=np.int64)
    slopes = np.array([slope_for_entry(m, int(d)) for d in ds],
                      dtype=np.float64)
    cum_bits = np.concatenate(([0], np.cumsum(ds))).astype(np.float64)
    cum_expected = np.concatenate(([0.0], np.cumsum(slopes)))
    return np.interp(np.arange(n_bits + 1, dtype=np.float64),
                     cum_bits, cum_expected)


def expected_curve_per_entry(entries, n_bits):
    ds = np.array([p.bit_length() for p in entries], dtype=np.int64)
    ms = np.array([v2_of(int(p)) for p in entries], dtype=np.int64)
    slopes = np.array([slope_for_entry(int(m), int(d))
                       for m, d in zip(ms, ds)], dtype=np.float64)
    cum_bits = np.concatenate(([0], np.cumsum(ds))).astype(np.float64)
    cum_expected = np.concatenate(([0.0], np.cumsum(slopes)))
    return np.interp(np.arange(n_bits + 1, dtype=np.float64),
                     cum_bits, cum_expected)


# ── Main ────────────────────────────────────────────────────────────

m = v2_of(N)
bits, entries = gen_for_monoid(N, TARGET_BITS)
n_bits = len(bits)

rds = compute_rds(bits)
expected_mono = expected_curve_monoid(entries, m, n_bits)
expected_pe = expected_curve_per_entry(entries, n_bits)

entry_v2s = [v2_of(int(p)) for p in entries]
entry_v2_mean = float(np.mean(entry_v2s))
entry_v2_max = int(max(entry_v2s))

mono_slope = slope_for_entry(m, 100)   # any d > 2m, here m = 0 so always 1.0

print(f"n = {N}")
print(f"  v_2(n) = {m}")
print(f"  bits = {n_bits}")
print(f"  entries = {len(entries)}")
print(f"  ⟨v_2(entry)⟩ = {entry_v2_mean:.4f}  (max = {entry_v2_max})")
print(f"  RDS(end) = {int(rds[-1]):+d}")
print(f"  expected_mono(end) = {expected_mono[-1]:+.2f}")
print(f"  expected_pe(end)   = {expected_pe[-1]:+.2f}")
print(f"  residual_mono(end) = {rds[-1] - expected_mono[-1]:+.2f}")
print(f"  residual_pe(end)   = {rds[-1] - expected_pe[-1]:+.2f}")


# ── Plot ────────────────────────────────────────────────────────────

DARK = '#0a0a0a'
WHITE = 'white'
RDS_COLOR = '#6ec6ff'    # blue — observed RDS
MONO_COLOR = '#c49bff'   # purple — v_2(n)-only naive prediction
PE_COLOR = '#ff6f61'     # red — per-entry prediction

fig, ax = plt.subplots(figsize=(16, 9), facecolor=DARK)
ax.set_facecolor(DARK)

xs = np.arange(len(rds))

ax.plot(
    xs, expected_mono,
    color=MONO_COLOR, lw=1.4, ls=':',
    label=f'expected, v₂(n) = {m} only  '
          f'(constant slope {mono_slope:+.3f}/entry)',
)
ax.plot(
    xs, expected_pe,
    color=PE_COLOR, lw=1.4, ls='--',
    label=f'expected, per-entry v₂  '
          f'(⟨v₂(entry)⟩ = {entry_v2_mean:.3f})',
)
ax.plot(
    xs, rds,
    color=RDS_COLOR, lw=1.0,
    label='RDS(t)',
)

ax.axhline(0, color=WHITE, lw=0.4, alpha=0.4)

ax.set_xlabel('bit position  t', color=WHITE, fontsize=13)
ax.set_ylabel(r'RDS(t) = $\sum_{i \leq t} (2 b_i - 1)$',
              color=WHITE, fontsize=13)
ax.set_title(
    f'Running Digital Sum for n = {N}   '
    f'(v₂(n) = {m},  {len(entries)} entries,  {n_bits} bits)',
    color=WHITE, fontsize=15, pad=14,
)

ax.tick_params(colors=WHITE, labelsize=11)
for spine in ax.spines.values():
    spine.set_color(WHITE)
ax.grid(True, alpha=0.12, color=WHITE)

ax.legend(
    loc='upper left', fontsize=11,
    facecolor=DARK, edgecolor='#444444', labelcolor=WHITE,
    framealpha=0.9,
)

plt.tight_layout()
out = os.path.join(_here, 'detrended_rds_n3.png')
plt.savefig(out, dpi=200, facecolor=DARK)
print(f"\nWrote {out}")
