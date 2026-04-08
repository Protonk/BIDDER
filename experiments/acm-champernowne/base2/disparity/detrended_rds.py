"""
detrended_rds.py — Experiment 2 of DISPARITY.md.

For each monoid in a panel spanning v_2 strata, compute the running
digital sum RDS(t), subtract the closed-form expected drift from
HAMMING-BOOKKEEPING (parameterized only by v_2(n) and the per-entry
bit length), and report what residual remains. The control is the
same set of n-prime entries shuffled into a random order — same
closed-form drift, same set of bits, only the ordering changes.

Outputs:
  detrended_rds_curves.png      raw RDS(t) + closed-form expected
  detrended_rds_residuals.png   residual + shuffled control + ±sqrt(t)
  detrended_rds_summary.csv     per-monoid statistics
"""

import sys
import os
import math
import csv
import random
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..'))                              # base2/
sys.path.insert(0, os.path.join(_here, '..', '..', '..', '..', 'core'))    # core/

from acm_core import acm_n_primes


# ── Parameters ──────────────────────────────────────────────────────

TOTAL_BITS = 100_000
SEED = 12345

# (n, expected v_2). Spans v_2 = 0..8 with two or three samples per
# stratum where the small odd parts allow it.
PANEL = [
    (3,   0),
    (5,   0),
    (7,   0),
    (2,   1),
    (6,   1),
    (4,   2),
    (12,  2),
    (8,   3),
    (16,  4),
    (32,  5),
    (64,  6),
    (128, 7),
    (256, 8),
]


# ── Number-theoretic helpers ────────────────────────────────────────

def v2_of(n):
    v = 0
    while n % 2 == 0:
        v += 1
        n //= 2
    return v


def slope_for_entry(m, d):
    """Closed-form per-entry expected RDS contribution from
    HAMMING-BOOKKEEPING. m = v_2(n), d = entry bit length.

    For m = 0 the entry is unconstrained beyond the leading-1, and the
    contribution is +1 (the universal MSB bonus).

    For d <= 2m the bottom-bit constraint k mod 2^m != 0 is automatic
    on the small range of valid k values, and the entry behaves like
    an MSB plus m forced trailing zeros: contribution 1 - m.

    For d > 2m the long-form bias holds and the contribution is
    1 - 2m + m * 2^m / (2^m - 1), independent of d.
    """
    if m == 0:
        return 1.0
    if d <= 2 * m:
        return 1.0 - m
    return 1.0 - 2.0 * m + (m * (2 ** m)) / (2 ** m - 1)


def estimate_count(n, target_bits):
    if n == 1:
        return max(int(target_bits / 13) + 200, 500)
    avg = math.log2(max(n, 2)) + math.log2(max(target_bits // 20, 4))
    return int(target_bits / max(avg, 4)) + 200


# ── Stream generation, truncated to entry boundaries ────────────────

def gen_for_monoid(n, target_bits):
    """Return (bits_uint8, entries_list) where bits is the concatenated
    binary expansion of the entries used. The prefix is truncated at
    the largest entry boundary <= target_bits, so it always ends
    exactly at an entry boundary."""
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


def bits_from_entries(entries):
    bits = []
    for p in entries:
        for c in bin(p)[2:]:
            bits.append(int(c))
    return np.array(bits, dtype=np.int8)


# ── RDS and expected curve ──────────────────────────────────────────

def compute_rds(bits):
    """RDS at every position: RDS[0] = 0, RDS[t] = sum of (2*b - 1)
    for the first t bits. Length len(bits) + 1."""
    pm = 2 * bits.astype(np.int64) - 1
    return np.concatenate(([0], np.cumsum(pm)))


def expected_curve_monoid(entries, m, n_bits):
    """Closed-form expected RDS using v_2(n) for every entry. This is
    the literal reading of HAMMING-BOOKKEEPING's claim that 'monoids
    sharing v_2(n) all behave the same.' For pure 2^m monoids it is
    correct; for composite n with mixed v_2(entry) it under-counts."""
    if not entries:
        return np.zeros(n_bits + 1)
    ds = np.array([p.bit_length() for p in entries], dtype=np.int64)
    slopes = np.array([slope_for_entry(m, int(d)) for d in ds],
                      dtype=np.float64)
    cum_bits = np.concatenate(([0], np.cumsum(ds))).astype(np.float64)
    cum_expected = np.concatenate(([0.0], np.cumsum(slopes)))
    xs = np.arange(n_bits + 1, dtype=np.float64)
    return np.interp(xs, cum_bits, cum_expected)


def expected_curve_per_entry(entries, n_bits):
    """Closed-form expected RDS using v_2(entry) for each entry. This
    is what the per-integer formula in HAMMING-BOOKKEEPING actually
    says, applied to each entry's true 2-adic valuation rather than
    the monoid's. For composite n where v_2(entry) is a mixture, this
    is the correct prediction."""
    if not entries:
        return np.zeros(n_bits + 1)
    ds = np.array([p.bit_length() for p in entries], dtype=np.int64)
    ms = np.array([v2_of(int(p)) for p in entries], dtype=np.int64)
    slopes = np.array([slope_for_entry(int(m), int(d))
                       for m, d in zip(ms, ds)], dtype=np.float64)
    cum_bits = np.concatenate(([0], np.cumsum(ds))).astype(np.float64)
    cum_expected = np.concatenate(([0.0], np.cumsum(slopes)))
    xs = np.arange(n_bits + 1, dtype=np.float64)
    return np.interp(xs, cum_bits, cum_expected)


# ── Main loop ───────────────────────────────────────────────────────

random.seed(SEED)
np.random.seed(SEED)

print(f"Computing detrended RDS for {len(PANEL)} monoids, "
      f"target {TOTAL_BITS} bits each\n")

results = []
for n, expected_m in PANEL:
    m = v2_of(n)
    assert m == expected_m, f"v2({n}) = {m}, expected {expected_m}"

    bits, entries = gen_for_monoid(n, TOTAL_BITS)
    n_bits = len(bits)

    rds = compute_rds(bits)
    expected_mono = expected_curve_monoid(entries, m, n_bits)
    expected_pe = expected_curve_per_entry(entries, n_bits)
    residual_mono = rds - expected_mono
    residual_pe = rds - expected_pe

    # Entry-shuffled control: same set of entries, permuted order
    shuf_entries = list(entries)
    random.shuffle(shuf_entries)
    shuf_bits = bits_from_entries(shuf_entries)
    shuf_rds = compute_rds(shuf_bits)
    shuf_expected_pe = expected_curve_per_entry(shuf_entries, len(shuf_bits))
    shuf_residual_pe = shuf_rds - shuf_expected_pe

    # Long-formula slope using v_2(n) (the naive prediction's slope)
    long_slope = slope_for_entry(m, 100)  # any d > 2m

    # How much do v_2(entry) values vary inside the monoid?
    entry_v2s = [v2_of(int(p)) for p in entries]
    entry_v2_mean = float(np.mean(entry_v2s))
    entry_v2_max = int(max(entry_v2s))

    results.append({
        'n': n, 'm': m, 'long_slope': long_slope,
        'n_bits': n_bits, 'n_entries': len(entries),
        'entry_v2_mean': entry_v2_mean, 'entry_v2_max': entry_v2_max,
        'rds': rds,
        'expected_mono': expected_mono, 'expected_pe': expected_pe,
        'residual_mono': residual_mono, 'residual_pe': residual_pe,
        'shuf_residual_pe': shuf_residual_pe,
    })
    print(f"  n={n:4d}  v_2={m}  ⟨v₂(entry)⟩={entry_v2_mean:.3f}  "
          f"max={entry_v2_max}  bits={n_bits}  entries={len(entries):5d}\n"
          f"           RDS_end={int(rds[-1]):+7d}  "
          f"|res_mono|max={np.abs(residual_mono).max():8.1f}  "
          f"|res_pe|max={np.abs(residual_pe).max():7.1f}  "
          f"|shuf_pe|max={np.abs(shuf_residual_pe).max():7.1f}")


# ── Figure 1: raw RDS panel ─────────────────────────────────────────

DARK = '#0a0a0a'
WHITE = 'white'
RDS_COLOR = '#6ec6ff'        # blue
EXPECTED_COLOR = '#ff6f61'   # red
RESIDUAL_COLOR = '#88d8b0'   # green
SHUFFLE_COLOR = '#777777'    # grey
ENVELOPE_COLOR = '#ffcc5c'   # yellow


def style_axes(ax):
    ax.set_facecolor(DARK)
    ax.tick_params(colors=WHITE, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(WHITE)


N_ROWS, N_COLS = 4, 4
MONO_COLOR = '#c49bff'   # purple — the v_2(n)-only naive prediction

fig, axes = plt.subplots(N_ROWS, N_COLS, figsize=(15, 11), facecolor=DARK)
fig.suptitle(
    'Experiment 2: Running Digital Sum vs. Closed-Form Expected Drift',
    color=WHITE, fontsize=14,
)

for ax_i, ax in enumerate(axes.flat):
    if ax_i >= len(results):
        ax.set_visible(False)
        continue
    r = results[ax_i]
    style_axes(ax)
    xs = np.arange(len(r['rds']))
    ax.plot(xs, r['rds'], color=RDS_COLOR, lw=0.8, label='RDS(t)')
    ax.plot(xs, r['expected_mono'], color=MONO_COLOR, lw=1.0, ls=':',
            label='expected (v₂(n) only)')
    ax.plot(xs, r['expected_pe'], color=EXPECTED_COLOR, lw=1.0, ls='--',
            label='expected (per-entry v₂)')
    ax.set_title(
        f"n={r['n']}  v₂(n)={r['m']}  ⟨v₂(entry)⟩={r['entry_v2_mean']:.2f}",
        color=WHITE, fontsize=10,
    )
    ax.axhline(0, color=WHITE, lw=0.3, alpha=0.4)
    if ax_i == 0:
        ax.legend(loc='upper left', fontsize=7, facecolor=DARK,
                  edgecolor='none', labelcolor=WHITE)

plt.tight_layout(rect=[0, 0, 1, 0.96])
out1 = os.path.join(_here, 'detrended_rds_curves.png')
plt.savefig(out1, dpi=200, facecolor=DARK)
plt.close()
print(f"\nWrote {out1}")


# ── Figure 2: residual panel ────────────────────────────────────────

fig, axes = plt.subplots(N_ROWS, N_COLS, figsize=(15, 11), facecolor=DARK)
fig.suptitle(
    'Experiment 2: Residual = RDS − Per-Entry Expected, with Shuffled-Entry Control',
    color=WHITE, fontsize=14,
)

for ax_i, ax in enumerate(axes.flat):
    if ax_i >= len(results):
        ax.set_visible(False)
        continue
    r = results[ax_i]
    style_axes(ax)
    n_res = len(r['residual_pe'])
    n_shuf = len(r['shuf_residual_pe'])
    n_max = max(n_res, n_shuf)

    # ±sqrt(t) envelope (fair-walk diffusion reference)
    xs_env = np.arange(1, n_max + 1)
    env = np.sqrt(xs_env)
    ax.plot(xs_env, env, color=ENVELOPE_COLOR, lw=0.5, ls=':',
            alpha=0.7, label=r'±√t')
    ax.plot(xs_env, -env, color=ENVELOPE_COLOR, lw=0.5, ls=':', alpha=0.7)

    # Naive (v_2(n)-only) residual as a faint comparison line
    ax.plot(np.arange(n_res), r['residual_mono'], color=MONO_COLOR,
            lw=0.6, alpha=0.65, label='v₂(n) residual')

    # Shuffled per-entry control
    ax.plot(np.arange(n_shuf), r['shuf_residual_pe'], color=SHUFFLE_COLOR,
            lw=0.6, alpha=0.85, label='shuffled (per-entry)')

    # Original per-entry residual (the headline)
    ax.plot(np.arange(n_res), r['residual_pe'], color=RESIDUAL_COLOR,
            lw=0.9, label='residual (per-entry)')

    ax.axhline(0, color=WHITE, lw=0.3, alpha=0.4)
    ax.set_title(
        f"n={r['n']}  v₂(n)={r['m']}",
        color=WHITE, fontsize=10,
    )
    if ax_i == 0:
        ax.legend(loc='upper left', fontsize=6, facecolor=DARK,
                  edgecolor='none', labelcolor=WHITE)

plt.tight_layout(rect=[0, 0, 1, 0.96])
out2 = os.path.join(_here, 'detrended_rds_residuals.png')
plt.savefig(out2, dpi=200, facecolor=DARK)
plt.close()
print(f"Wrote {out2}")


# ── Summary CSV and stdout table ────────────────────────────────────

csv_path = os.path.join(_here, 'detrended_rds_summary.csv')
with open(csv_path, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow([
        'n', 'v_2_n', 'entry_v2_mean', 'entry_v2_max',
        'long_slope_v2n', 'n_bits', 'n_entries', 'sqrt_n_bits',
        'rds_end', 'expected_mono_end', 'expected_pe_end',
        'res_mono_end', 'res_pe_end',
        'res_mono_max_abs', 'res_pe_max_abs', 'shuf_pe_max_abs',
        'res_mono_max_abs_over_sqrt_n',
        'res_pe_max_abs_over_sqrt_n',
        'shuf_pe_max_abs_over_sqrt_n',
    ])
    for r in results:
        n_bits = r['n_bits']
        sqrt_n = math.sqrt(n_bits)
        res_mono = r['residual_mono']
        res_pe = r['residual_pe']
        shuf_pe = r['shuf_residual_pe']
        rm_abs = float(np.abs(res_mono).max())
        rp_abs = float(np.abs(res_pe).max())
        sp_abs = float(np.abs(shuf_pe).max())
        w.writerow([
            r['n'], r['m'], f"{r['entry_v2_mean']:.4f}", r['entry_v2_max'],
            f"{r['long_slope']:+.6f}",
            n_bits, r['n_entries'], f"{sqrt_n:.1f}",
            int(r['rds'][-1]),
            f"{r['expected_mono'][-1]:+.2f}",
            f"{r['expected_pe'][-1]:+.2f}",
            f"{res_mono[-1]:+.2f}",
            f"{res_pe[-1]:+.2f}",
            f"{rm_abs:.2f}",
            f"{rp_abs:.2f}",
            f"{sp_abs:.2f}",
            f"{rm_abs / sqrt_n:.2f}",
            f"{rp_abs / sqrt_n:.2f}",
            f"{sp_abs / sqrt_n:.2f}",
        ])
print(f"Wrote {csv_path}")


print("\n=== Per-monoid summary ===")
print(f"{'n':>5} {'v₂(n)':>6} {'⟨v₂e⟩':>7} "
      f"{'res_mono_end':>13} {'res_pe_end':>11} "
      f"{'|res_pe|max/√n':>16} {'|shuf_pe|max/√n':>17}")
print('-' * 80)
for r in results:
    n_bits = r['n_bits']
    sqrt_n = math.sqrt(n_bits)
    rp = r['residual_pe']
    sp = r['shuf_residual_pe']
    rp_abs = float(np.abs(rp).max())
    sp_abs = float(np.abs(sp).max())
    print(f"{r['n']:5d} {r['m']:6d} {r['entry_v2_mean']:7.3f} "
          f"{r['residual_mono'][-1]:+13.1f} "
          f"{rp[-1]:+11.1f} "
          f"{rp_abs / sqrt_n:16.2f} "
          f"{sp_abs / sqrt_n:17.2f}")

print("\nDone.")
