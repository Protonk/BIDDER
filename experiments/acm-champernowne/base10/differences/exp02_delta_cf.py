"""
exp02_delta_cf.py — continued-fraction expansion of δ = C_Bundle − C_Surv.

Same parameters as EXP01. The CF view is orthogonal to the
digit-frequency view: it captures how well δ can be approximated by
rationals of bounded denominator, regardless of decimal positions.

For the rational δ with denominator q dividing 10^L_b, the CF is
finite (length bounded by ~log_φ(q) ≈ 4.785 · log_10(q)). The
question is whether δ behaves like a typical rational of that
denominator size, or whether the construction's structure leaves a
CF fingerprint.

Four extracted observables:
  - partial-quotient distribution vs Gauss–Kuzmin
  - convergent denominator growth (log)
  - running Khinchin geometric mean vs Khinchin's constant
  - top 10 largest partial quotients with positions

Run: sage -python experiments/acm-champernowne/base10/differences/exp02_delta_cf.py
"""

from __future__ import annotations

import math
import os
import sys
from collections import Counter
from fractions import Fraction

sys.set_int_max_str_digits(1_000_000)

import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = HERE
for _ in range(4):
    REPO = os.path.dirname(REPO)
sys.path.insert(0, os.path.join(REPO, 'core'))
sys.path.insert(0, os.path.join(REPO, 'experiments', 'acm-champernowne',
                                'base10', 'survivors'))

from survivors_core import bundle_atoms, survival_mask  # noqa: E402


N0, N1, K = 2, 10, 400

KHINCHIN = 2.6854520010653064453

BG = '#fafafa'
FG = '#1a1a2e'
PRIM = '#1f4e79'
ACCENT = '#c0392b'
GAUSSK = '#b8860b'
GUIDE = '#aaaaaa'


def digits_to_real(s: str) -> Fraction:
    if not s:
        return Fraction(1)
    return Fraction(1) + Fraction(int(s), 10 ** len(s))


def cf_expansion(num: int, den: int) -> list[int]:
    """Continued fraction [a_0; a_1, a_2, ...] of num/den."""
    a = []
    while den != 0:
        q = num // den
        a.append(q)
        num, den = den, num - q * den
    return a


def gauss_kuzmin(k: int) -> float:
    return math.log2((k + 1) ** 2 / (k * (k + 2)))


def log_bigint(x: int) -> float:
    """math.log on arbitrary-precision int, falling back to bit-length
    scaling if direct float conversion overflows."""
    if x <= 0:
        return float('-inf')
    try:
        return math.log(x)
    except OverflowError:
        bits = x.bit_length()
        return (bits - 1) * math.log(2)


def main():
    print(f'building bundle for [{N0}, {N1}], k = {K} ...')
    atoms = bundle_atoms(N0, N1, K)
    mask = survival_mask(atoms)

    bundle_str = ''.join(str(m) for _, m in atoms)
    surv_str = ''.join(str(m) for (_, m), keep in zip(atoms, mask) if keep)

    c_bundle = digits_to_real(bundle_str)
    c_surv = digits_to_real(surv_str)
    delta = c_bundle - c_surv
    abs_delta = delta if delta > 0 else -delta

    p, q = abs_delta.numerator, abs_delta.denominator
    print(f'  |δ| = p / q')
    print(f'  numerator p:  {len(str(p)):,} digits')
    print(f'  denominator q: {len(str(q)):,} digits')

    # Factor q as 2^a · 5^b · residue
    q_test = q
    a_count = 0
    while q_test % 2 == 0:
        q_test //= 2
        a_count += 1
    b_count = 0
    while q_test % 5 == 0:
        q_test //= 5
        b_count += 1
    print(f'  q = 2^{a_count} · 5^{b_count} · {q_test}')

    print(f'\n  computing continued fraction ...')
    cf = cf_expansion(p, q)
    print(f'  CF length N: {len(cf)} partial quotients (incl. a_0)')
    log_phi_q = math.log(q, (1 + math.sqrt(5)) / 2)
    print(f'  log_φ(q) bound: {log_phi_q:.0f}')
    print(f'  ratio N / log_φ(q): {len(cf) / log_phi_q:.3f}')

    print(f'\n  first 30 partial quotients: {cf[:30]}')

    a_list = cf[1:]  # drop a_0 (integer part)
    n = len(a_list)

    counts = Counter(a_list)
    print(f'\n  partial-quotient distribution (vs Gauss–Kuzmin):')
    print(f'    k  |  count   |  freq   |  GK pred')
    print(f'   ----+----------+---------+----------')
    for k in range(1, 11):
        cnt = counts.get(k, 0)
        freq = cnt / n
        gk = gauss_kuzmin(k)
        print(f'   {k:>3}  | {cnt:>8} | {freq:.4f}  | {gk:.4f}')
    tail_count = sum(c for k, c in counts.items() if k >= 11)
    tail_freq = tail_count / n
    tail_gk = sum(gauss_kuzmin(k) for k in range(11, 1000))
    print(f'   ≥11  | {tail_count:>8} | {tail_freq:.4f}  | {tail_gk:.4f}')

    log_a = np.array([log_bigint(a) for a in a_list])
    cum_log = np.cumsum(log_a)
    running_K = np.exp(cum_log / np.arange(1, n + 1))

    print(f'\n  running Khinchin geometric mean:')
    for ckpt in (100, 1000, 5000, n):
        if ckpt <= n:
            print(f'    n = {ckpt:>6}: K_n = {running_K[ckpt - 1]:.4f}')
    print(f'    Khinchin constant: {KHINCHIN:.4f}')
    print(f'    deviation: {running_K[-1] - KHINCHIN:+.4f}')

    top_k = sorted(enumerate(a_list, start=1), key=lambda x: -x[1])[:10]
    print(f'\n  top 10 largest partial quotients:')
    for rank, (pos, val) in enumerate(top_k, start=1):
        s = str(val)
        if len(s) > 30:
            s = f'{s[:20]}…({len(s)} digits)'
        print(f'    #{rank:>2}  position a_{pos}  = {s}')

    # Convergents
    print(f'\n  computing convergent denominators ...')
    p_prev, q_prev = 1, 0
    p_cur, q_cur = cf[0], 1
    convergent_denoms = [q_cur]
    for a in cf[1:]:
        p_next = a * p_cur + p_prev
        q_next = a * q_cur + q_prev
        convergent_denoms.append(q_next)
        p_prev, q_prev = p_cur, q_cur
        p_cur, q_cur = p_next, q_next
    print(f'  final q_N has {len(str(q_cur)):,} digits (matches q)')

    # Plot — 4 panels
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), facecolor=BG)

    # TL: distribution
    ax = axes[0, 0]
    ax.set_facecolor(BG)
    k_max_plot = 12
    emp = np.array([counts.get(k, 0) / n for k in range(1, k_max_plot + 1)])
    gk = np.array([gauss_kuzmin(k) for k in range(1, k_max_plot + 1)])
    x = np.arange(1, k_max_plot + 1)
    ax.bar(x - 0.2, emp, width=0.4, color=PRIM, edgecolor=FG,
           linewidth=0.4, label='empirical (δ)', zorder=3)
    ax.bar(x + 0.2, gk, width=0.4, color=GAUSSK, edgecolor=FG,
           linewidth=0.4, alpha=0.85, label='Gauss–Kuzmin', zorder=3)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('bottom', 'left'):
        ax.spines[side].set_color(FG)
        ax.spines[side].set_alpha(0.4)
    ax.tick_params(colors=FG)
    ax.set_xticks(x)
    ax.set_xlabel('partial quotient value $a_i$', color=FG, fontsize=10)
    ax.set_ylabel('frequency', color=FG, fontsize=10)
    ax.set_title('partial-quotient distribution', color=FG, fontsize=11, pad=8)
    ax.legend(loc='upper right', facecolor='#f0f0f0', fontsize=9)

    # TR: convergent denominators
    ax = axes[0, 1]
    ax.set_facecolor(BG)
    log_qs = np.array([log_bigint(q) for q in convergent_denoms[1:]])
    ax.plot(np.arange(1, len(log_qs) + 1), log_qs / math.log(10),
            color=PRIM, linewidth=0.8)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('bottom', 'left'):
        ax.spines[side].set_color(FG)
        ax.spines[side].set_alpha(0.4)
    ax.tick_params(colors=FG)
    ax.set_xlabel('CF position $k$', color=FG, fontsize=10)
    ax.set_ylabel('$\\log_{10}(q_k)$', color=FG, fontsize=10)
    ax.set_title(f'convergent denominators (CF length {len(cf):,})',
                 color=FG, fontsize=11, pad=8)

    # BL: running Khinchin
    ax = axes[1, 0]
    ax.set_facecolor(BG)
    ax.semilogx(np.arange(1, n + 1), running_K, color=PRIM, linewidth=1.0,
                label='running $K_n$')
    ax.axhline(KHINCHIN, color=ACCENT, linestyle='--', linewidth=1.2,
               label=f'Khinchin constant ≈ {KHINCHIN:.4f}')
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('bottom', 'left'):
        ax.spines[side].set_color(FG)
        ax.spines[side].set_alpha(0.4)
    ax.tick_params(colors=FG)
    ax.set_xlabel('n (CF prefix length)', color=FG, fontsize=10)
    ax.set_ylabel('$K_n = (a_1 \\cdots a_n)^{1/n}$', color=FG, fontsize=10)
    ax.set_title(f'running Khinchin geometric mean  (final = {running_K[-1]:.4f})',
                 color=FG, fontsize=11, pad=8)
    ax.legend(loc='upper right', facecolor='#f0f0f0', fontsize=9)

    # BR: top 10 largest partial quotients
    ax = axes[1, 1]
    ax.set_facecolor(BG)
    ax.axis('off')
    lines = ['Top 10 largest partial quotients', '']
    lines.append(f"{'rank':>4}  {'position i':>10}  {'a_i':<32}")
    lines.append('-' * 50)
    for rank, (pos, val) in enumerate(top_k, start=1):
        s = str(val)
        if len(s) > 28:
            s = s[:18] + f'…({len(s)} dig)'
        lines.append(f'{rank:>4}  {pos:>10}  {s:<32}')
    ax.text(0.04, 0.96, '\n'.join(lines), transform=ax.transAxes,
            color=FG, fontsize=10, va='top', ha='left',
            family='monospace')
    ax.set_title('largest partial quotients', color=FG, fontsize=11, pad=8)

    fig.suptitle(
        f'EXP02 — continued-fraction expansion of |δ = C_Bundle − C_Surv|  '
        f'at [{N0}, {N1}], k = {K}',
        color=FG, fontsize=13, fontweight='semibold', y=0.995,
    )

    fig.text(0.5, 0.015,
             f'(δ rational with q ≈ 10^{int(math.log10(q))}; '
             f'CF length {len(cf):,}; log_φ(q) ≈ {log_phi_q:.0f}; '
             f'q = 2^{a_count} · 5^{b_count} · {q_test})',
             color=GUIDE, fontsize=8.5, ha='center', style='italic')

    fig.tight_layout(rect=[0, 0.03, 1, 0.965])
    out = os.path.join(HERE, 'exp02_delta_cf.png')
    fig.savefig(out, dpi=150, facecolor=BG)
    print(f'\n-> {out}')


if __name__ == '__main__':
    main()
