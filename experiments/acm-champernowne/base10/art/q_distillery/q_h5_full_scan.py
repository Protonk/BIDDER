"""
q_h5_full_scan.py - Q_n at h = 5 across n in [2, 30].

Extends the four-column merger panel (q_merger_h5) to all n in [2, 30],
sorted by n-shape class. The shape of n is the sorted tuple of prime
exponents in n's factorisation: 2 -> (1,), 4 -> (2,), 6 -> (1,1),
12 -> (2,1), 30 -> (1,1,1), and so on. The shape determines the
binomial-product coefficient pattern of the master expansion at fixed
(h, j); k's tau-signature determines the residue. Q_n(n^5 k) is a
function of (shape(n), tau-signature(k)) only.

Within a shape class, every n produces the same Q at fixed k. The
horizontal connecting segments inside each class are therefore dead
flat by construction; flatness IS the structural identity, made
visible by the layout. Between classes, Q jumps to a new value.

Highlighted k's: six canonical anchors with distinct tau-signatures,
all coprime to lcm(2..30) so every (n, k) pair has gcd 1 and the
master expansion lives entirely in the (t_i = 0) sub-case. Anchors:

    k = 1            [const, Omega = 0]    tau_j = 1
    k = 31           [p,     Omega = 1]    tau_j = j
    k = 31^2 = 961   [p^2,   Omega = 2]    tau_j = j(j+1)/2
    k = 31*37 = 1147 [pq,    Omega = 2]    tau_j = j^2
    k = 31^3 = 29791 [p^3,   Omega = 3]    tau_j = j(j+1)(j+2)/6
    k = 31*37*41     [pqr,   Omega = 3]    tau_j = j^3
              = 47027

Background fog: more k's coprime to lcm(2..30), drawn faint, providing
the typical Q-magnitude landscape.

The headline structural fact at h = 5: at every prime n the
coefficient pattern is (+1, -2, +2, -1, +1/5). As a linear functional
on tau_j viewed as a polynomial in j, this kernel annihilates every
polynomial of degree 1..4. Since tau_j(k) is a polynomial of degree
Omega(k) in j, every k coprime to n with Omega(k) in [1, 4] satisfies
Q_p(p^5 k) = 0 exactly. Five of the six highlighted k's stack on the
zero line across the entire prime block (n = 2, 3, 5, 7, 11, 13, 17,
19, 23, 29). The same kernel partially extends to the p^2 class
(degree-1 still vanishes; higher degrees do not), and breaks
elsewhere - the visualisation lets the reader see exactly where the
zero band ends.
"""

import os
from functools import lru_cache
from math import comb

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection


HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'q_h5_full_scan.png')

H = 5
N_MIN = 2
N_MAX = 30

DARK = '#0a0a0a'
WARM = (1.00, 0.66, 0.30)
COOL = (0.45, 0.78, 1.00)
TICK_COLOR = (0.85, 0.88, 0.92, 0.85)
LABEL_COLOR = (0.95, 0.97, 1.00, 0.95)


@lru_cache(maxsize=None)
def factor_tuple(n):
    out = []
    r = n
    p = 2
    while p * p <= r:
        if r % p == 0:
            e = 0
            while r % p == 0:
                e += 1
                r //= p
            out.append((p, e))
        p += 1 if p == 2 else 2
    if r > 1:
        out.append((r, 1))
    return tuple(out)


def shape(n):
    """Sorted-descending tuple of prime exponents — the n-shape class."""
    return tuple(sorted([e for _p, e in factor_tuple(n)], reverse=True))


def shape_label(s):
    pretty = {
        (1,): 'p',
        (2,): 'p²',
        (3,): 'p³',
        (4,): 'p⁴',
        (1, 1): 'pq',
        (2, 1): 'p²q',
        (3, 1): 'p³q',
        (1, 1, 1): 'pqr',
    }
    return pretty.get(s, '·'.join(f'p^{e}' if e > 1 else 'p' for e in s))


@lru_cache(maxsize=None)
def tau(j, x):
    if j == 1:
        return 1
    prod = 1
    for _p, e in factor_tuple(x):
        prod *= comb(e + j - 1, j - 1)
    return prod


def pn_q(n, h, k):
    """(P, N, Q) where P = sum of |odd-j terms|, N = sum of |even-j|, Q = P - N.
    Assumes gcd(k, n) = 1, so all t_i = 0 and the master expansion reduces."""
    factors = factor_tuple(n)
    P = 0.0
    N = 0.0
    for j in range(1, h + 1):
        coeff = 1
        for (_p, a) in factors:
            coeff *= comb(a * (h - j) + j - 1, j - 1)
        magnitude = coeff * tau(j, k) / j
        if j % 2 == 1:
            P += magnitude
        else:
            N += magnitude
    return P, N, P - N


def slog(y, lt=1.0):
    return np.sign(y) * np.log10(1.0 + np.abs(y) / lt)


def lcm_panel():
    n_range = list(range(N_MIN, N_MAX + 1))
    primes = set()
    for n in n_range:
        for p, _ in factor_tuple(n):
            primes.add(p)
    return sorted(primes)


def k_coprime_to_panel(count, forbidden_primes):
    out = []
    k = 1
    while len(out) < count:
        if all(k % p != 0 for p in forbidden_primes):
            out.append(k)
        k += 1
    return out


def main():
    # n's grouped by shape class, sorted by (Omega, omega, shape).
    n_range = list(range(N_MIN, N_MAX + 1))
    ns_with_shape = [(n, shape(n)) for n in n_range]

    def shape_rank(s):
        return (sum(s), len(s), s)

    shape_classes_sorted = sorted(set(s for _, s in ns_with_shape), key=shape_rank)
    shape_groups = []
    sorted_ns = []
    for s in shape_classes_sorted:
        ns_in_class = sorted(n for n, s2 in ns_with_shape if s2 == s)
        shape_groups.append((s, ns_in_class))
        sorted_ns.extend(ns_in_class)

    print(f'{len(sorted_ns)} n in [{N_MIN}, {N_MAX}] across '
          f'{len(shape_groups)} shape classes:')
    for s, ns_in_class in shape_groups:
        print(f'  {shape_label(s):>4}: {ns_in_class}')

    # Canonical highlights with distinct tau-signatures, coprime to all
    # n in [2, 30].
    HIGHLIGHTS = [
        (1,            'k=1 [const]',        (1.00, 0.84, 0.30)),
        (31,           'k=31 [p]',           (0.50, 1.00, 0.70)),
        (31 * 31,      'k=31² [p²]',         (0.95, 0.55, 1.00)),
        (31 * 37,      'k=31·37 [pq]',       (0.40, 0.85, 1.00)),
        (31 * 31 * 31, 'k=31³ [p³]',         (1.00, 0.55, 0.55)),
        (31 * 37 * 41, 'k=31·37·41 [pqr]',   (1.00, 0.85, 0.55)),
    ]
    highlight_ks = [k for k, _, _ in HIGHLIGHTS]

    forbidden_primes = lcm_panel()
    fog_ks = k_coprime_to_panel(40, forbidden_primes)
    fog_ks = [k for k in fog_ks if k not in highlight_ks]
    print(f'fog k count = {len(fog_ks)}')

    all_ks = highlight_ks + fog_ks
    log_ks = np.log(np.array(all_ks, dtype=float))
    lk_min, lk_max = log_ks.min(), log_ks.max()
    lk_norm = ((log_ks - lk_min) / (lk_max - lk_min)
               if lk_max > lk_min else np.zeros_like(log_ks))
    column_half_w = 0.34

    x_centers = np.arange(len(sorted_ns), dtype=float)

    def x_pos(n_idx, k):
        k_idx = all_ks.index(k)
        return (x_centers[n_idx] - column_half_w
                + 2 * column_half_w * lk_norm[k_idx])

    fig = plt.figure(figsize=(20, 11), dpi=180, facecolor=DARK)
    ax = fig.add_subplot(111)
    ax.set_facecolor(DARK)

    # Subtle vertical tinting per shape class.
    cum = 0
    for grp_idx, (_s, ns_in_class) in enumerate(shape_groups):
        x_l = cum - 0.5
        x_r = cum + len(ns_in_class) - 0.5
        tint = (0.10, 0.13, 0.18, 0.55) if grp_idx % 2 == 0 else (0.06, 0.08, 0.11, 0.55)
        ax.axvspan(x_l, x_r, color=tint, zorder=0.2)
        cum += len(ns_in_class)

    # ---- background fog towers and Q dots ----
    bg_warm_segs = []
    bg_cool_segs = []
    bg_q_x, bg_q_y = [], []
    for k in fog_ks:
        for n_idx, n in enumerate(sorted_ns):
            P, N, Q = pn_q(n, H, k)
            x = x_pos(n_idx, k)
            bg_warm_segs.append([(x, 0.0), (x, slog(P))])
            bg_cool_segs.append([(x, 0.0), (x, -slog(N))])
            bg_q_x.append(x)
            bg_q_y.append(slog(Q))

    ax.add_collection(LineCollection(
        bg_warm_segs, colors=[(*WARM, 0.07)], linewidths=0.45, zorder=2,
    ))
    ax.add_collection(LineCollection(
        bg_cool_segs, colors=[(*COOL, 0.07)], linewidths=0.45, zorder=2,
    ))
    ax.scatter(bg_q_x, bg_q_y, s=1.6, c=[(1.0, 1.0, 1.0, 0.10)],
               zorder=3, linewidths=0)

    # ---- highlighted k's ----
    for k_canon, label, color in HIGHLIGHTS:
        # Legend stub.
        ax.scatter([], [], s=80, c=[(*color, 1.0)],
                   edgecolors=[(0.0, 0.0, 0.0, 0.95)], linewidths=1.0,
                   label=label)

        # Towers at every n.
        for n_idx, n in enumerate(sorted_ns):
            P, N, _ = pn_q(n, H, k_canon)
            x = x_pos(n_idx, k_canon)
            ax.plot([x, x], [0, slog(P)],
                    color=(*WARM, 0.55), lw=1.7,
                    solid_capstyle='round', zorder=4)
            ax.plot([x, x], [0, -slog(N)],
                    color=(*COOL, 0.55), lw=1.7,
                    solid_capstyle='round', zorder=4)

        # Within each shape class: flat horizontal segment connecting the
        # Q dots, since shape determines coefficient pattern and k is
        # fixed. Flatness IS the structural identity.
        for s, ns_in_class in shape_groups:
            seg_xs, seg_ys = [], []
            for n in ns_in_class:
                n_idx = sorted_ns.index(n)
                _, _, Q = pn_q(n, H, k_canon)
                seg_xs.append(x_pos(n_idx, k_canon))
                seg_ys.append(slog(Q))
            if len(seg_xs) > 1:
                ax.plot(seg_xs, seg_ys,
                        color=(*color, 0.55),
                        lw=1.5, zorder=6, solid_capstyle='round')
            ax.scatter(seg_xs, seg_ys, s=70, c=[(*color, 1.0)],
                       edgecolors=[(0.0, 0.0, 0.0, 0.95)], linewidths=0.8,
                       zorder=8)

    # Zero line.
    ax.axhline(0.0, color=(0.95, 0.97, 1.00, 0.35), lw=0.7, zorder=1)

    # Vertical separators between shape classes.
    cum = 0
    for s, ns_in_class in shape_groups[:-1]:
        cum += len(ns_in_class)
        ax.axvline(cum - 0.5, color=(0.45, 0.50, 0.58, 0.35),
                   lw=0.7, ls=':', zorder=0.6)

    # x-axis: n labels.
    ax.set_xticks(x_centers)
    ax.set_xticklabels([str(n) for n in sorted_ns],
                       fontsize=9.5, color=TICK_COLOR)
    ax.tick_params(axis='x', length=0)

    # Shape class labels above the columns.
    cum = 0
    label_y = slog(2200)
    for s, ns_in_class in shape_groups:
        center = cum + (len(ns_in_class) - 1) / 2
        ax.text(center, label_y, shape_label(s),
                color=(1.0, 1.0, 1.0, 0.62),
                fontsize=12, ha='center', va='bottom',
                fontstyle='italic', fontweight='bold')
        cum += len(ns_in_class)

    # y-axis (symlog).
    tick_values = [-1000, -100, -10, -1, 0, 1, 10, 100, 1000]
    tick_locs = [slog(v) for v in tick_values]
    tick_labels = [f'{v:+d}' if v != 0 else '0' for v in tick_values]
    ax.set_yticks(tick_locs)
    ax.set_yticklabels(tick_labels, fontsize=9, color=TICK_COLOR)
    ax.set_ylim(slog(-2000), slog(2700))
    ax.set_xlim(-0.7, len(sorted_ns) - 0.3)

    for spine in ax.spines.values():
        spine.set_color((0.40, 0.45, 0.50, 0.40))
        spine.set_linewidth(0.7)
    ax.grid(True, axis='y', color=(0.30, 0.34, 0.38),
            alpha=0.14, lw=0.4, zorder=0.3)

    # Title and subtitle.
    fig.text(
        0.5, 0.965,
        'Q_n at h = 5 across n ∈ [2, 30] — sorted by n-shape',
        ha='center', va='top', color=(1.0, 1.0, 1.0, 0.95),
        fontsize=20, fontweight='bold', family='serif',
    )
    fig.text(
        0.5, 0.935,
        'columns grouped by n-shape (sorted-exponent signature).   '
        'flat segments within each class = same Q for every n of that shape.   '
        'segment heights jump only at class boundaries.',
        ha='center', va='top', color=(0.80, 0.85, 0.92, 0.62),
        fontsize=10.5, fontstyle='italic',
    )

    # Legend.
    ax.legend(
        loc='lower right', fontsize=9.5, framealpha=0.85,
        facecolor=(0.05, 0.06, 0.08, 0.85),
        edgecolor=(0.30, 0.36, 0.42, 0.50),
        labelcolor=(0.92, 0.95, 1.00, 1.0),
        ncol=2,
    )

    # Reading hint — call out the structural zero band.
    ax.text(
        0.012, 0.05,
        'prime block (n = 2, 3, 5, 7, 11, 13, 17, 19, 23, 29):\n'
        '5 of 6 highlighted k vanish exactly at Q = 0.\n'
        'kernel of (+1, −2, +2, −1, +1/5) on j-polynomials kills\n'
        'τ_j(k) of degree 1..4; only k = 1 (degree 0) survives.',
        transform=ax.transAxes, fontsize=9.5,
        color=(0.95, 0.96, 1.00, 0.72), fontstyle='italic',
        ha='left', va='bottom',
        linespacing=1.4,
    )

    plt.subplots_adjust(left=0.04, right=0.985, top=0.905, bottom=0.06)
    plt.savefig(OUT, facecolor=DARK)
    plt.close()
    print(f'-> {OUT}')


if __name__ == '__main__':
    main()
