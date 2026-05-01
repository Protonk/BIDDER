"""
q_h5_shape_tau_matrix.py - Q at h=5 as a (shape × tau-signature) matrix.

Q_n(n^5 k) is a function of (shape(n), tau-signature(k)) only, where
shape(n) is the sorted-descending tuple of n's prime exponents and
tau-signature(k) is the sorted-descending tuple of k's prime exponents.
The 29-column scan in q_h5_full_scan.py shows this redundantly: every
n in a shape class collapses to the same flat plateau. The matrix
below condenses that redundancy into 8 rows × 6 columns, one cell per
(shape, tau-signature) pair.

Cells are rendered as a diverging heatmap: warm for Q > 0, cool for
Q < 0, near-black for |Q| small. Cells where Q = 0 exactly are ringed
in gold and marked with a centred dot — they are kernel zeros of the
shape's coefficient pattern applied to the tau-signature's polynomial
in j.

The kernel-zero structure at h=5 is visible in the upper-left corner:

  - Prime row (first row): 5 of 6 columns vanish. The prime-h=5
    coefficient pattern (+1, -2, +2, -1, +1/5) is the alternating
    binomial sum (-1)^(j-1) C(4, j-1) / j, which annihilates every
    polynomial in j of degree 1..4. Every tau-signature except
    const (k=1, tau_j = 1, degree 0) lives in the kernel.

  - p^2 and p^3 rows: vanish at the p column (k = single prime,
    tau_j = j). This is the linear-tau kernel — Sigma c_j · j = 0
    for prime power shapes p^a with a in {1, 2, 3} at h=5.

  - p^4 row: linear-tau kernel breaks (Sigma c_j · j = -1). The
    kernel persists for a <= h-2 in our examples but breaks at
    a = h-1; the matrix records the breakpoint at a single glance.

  - Squarefree multi-prime shapes (pq, p^2q, p^3q, pqr): no
    kernel zeros at h=5. The binomial-product structure with
    multiple factors does not collapse the alternating sum.

Right-side annotation: the coefficient pattern (j=1..5, with sign)
of each row. The reader can compute "max degree of tau-polynomial
killed by this row" by inspection.
"""

import os
from functools import lru_cache
from math import comb

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'q_h5_shape_tau_matrix.png')

H = 5

DARK = '#0a0a0a'

# Diverging palette: warm for +, cool for -, dark midpoint.
WARM_HI = np.array([1.00, 0.66, 0.30])
COOL_HI = np.array([0.30, 0.55, 0.95])
DARK_MID = np.array([0.18, 0.20, 0.24])
ZERO_RING = np.array([1.00, 0.88, 0.45])


# Shape and tau-signature panels, sorted by (Omega, omega, tuple).
SHAPES = [
    (1,),       # prime
    (2,),       # p^2
    (1, 1),     # pq
    (3,),       # p^3
    (2, 1),     # p^2 q
    (1, 1, 1),  # pqr
    (4,),       # p^4
    (3, 1),     # p^3 q
]

TAU_SIGS = [
    (),         # const (k=1)
    (1,),       # p
    (2,),       # p^2
    (1, 1),     # pq
    (3,),       # p^3
    (1, 1, 1),  # pqr
]


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
    return pretty.get(s, ' ')


def tau_label(s):
    pretty = {
        (): 'const',
        (1,): 'p',
        (2,): 'p²',
        (3,): 'p³',
        (1, 1): 'pq',
        (1, 1, 1): 'pqr',
    }
    return pretty.get(s, ' ')


def shape_omega(s):
    return sum(s)


def tau_omega(s):
    return sum(s) if s else 0


@lru_cache(maxsize=None)
def coeff_pattern(shape, h=H):
    out = []
    for j in range(1, h + 1):
        c = 1
        for a in shape:
            c *= comb(a * (h - j) + j - 1, j - 1)
        sign = 1 if j % 2 == 1 else -1
        out.append(sign * c / j)
    return tuple(out)


@lru_cache(maxsize=None)
def tau_values(tau_sig, h=H):
    out = []
    for j in range(1, h + 1):
        v = 1
        for e in tau_sig:
            v *= comb(e + j - 1, j - 1)
        out.append(v)
    return tuple(out)


def q_value(shape, tau_sig, h=H):
    coeff = coeff_pattern(shape, h)
    tau = tau_values(tau_sig, h)
    return sum(c * t for c, t in zip(coeff, tau))


def slog(y, lt=1.0):
    return np.sign(y) * np.log10(1.0 + np.abs(y) / lt)


def cell_color(q, slog_max):
    if abs(q) < 1e-9:
        return tuple(DARK_MID)
    sl = slog(q)
    intensity = np.clip(0.18 + 0.82 * abs(sl) / slog_max, 0.18, 1.0)
    target = WARM_HI if q > 0 else COOL_HI
    rgb = DARK_MID * (1 - intensity) + target * intensity
    return tuple(np.clip(rgb, 0.0, 1.0))


def format_q(q):
    if abs(q) < 1e-9:
        return '0'
    if abs(q) < 0.1:
        return f'{q:+.2f}'
    if abs(q) < 1:
        return f'{q:+.2f}'
    if abs(q) < 10 and q != int(q):
        return f'{q:+.2f}'
    if abs(q) < 100 and q != int(q):
        return f'{q:+.1f}'
    if q == int(q):
        return f'{int(q):+d}'
    return f'{q:+.0f}'


def format_coeff_pattern(coeff):
    parts = []
    for c in coeff:
        if abs(c - round(c)) < 1e-9:
            parts.append(f'{int(round(c)):+d}')
        else:
            # Show fractional cleanly
            if abs(c) < 1:
                parts.append(f'{c:+.2f}'.rstrip('0').rstrip('.'))
            else:
                parts.append(f'{c:+.2f}'.rstrip('0').rstrip('.'))
    return ' '.join(parts)


def main():
    n_rows = len(SHAPES)
    n_cols = len(TAU_SIGS)

    Q = np.zeros((n_rows, n_cols))
    for i, s in enumerate(SHAPES):
        for j, t in enumerate(TAU_SIGS):
            Q[i, j] = q_value(s, t)

    print('Q matrix at h=5:')
    print('  shape  | ' + ' | '.join(f'{tau_label(t):>6}' for t in TAU_SIGS))
    for i, s in enumerate(SHAPES):
        row_strs = ' | '.join(f'{Q[i, j]:>+8.3g}' for j in range(n_cols))
        print(f'  {shape_label(s):>5}  | {row_strs}')

    # Color scale: max abs slog of any cell.
    abs_logs = [abs(slog(q)) for q in Q.flat if abs(q) > 1e-9]
    slog_max = max(abs_logs) if abs_logs else 1.0

    # Layout in figure data coords.
    cell_w = 1.00
    cell_h = 0.70
    matrix_left = 1.5
    matrix_top = n_rows * cell_h + 0.45
    coeff_strip_x = matrix_left + n_cols * cell_w + 0.4

    fig = plt.figure(figsize=(15, 9.5), dpi=200, facecolor=DARK)
    ax = fig.add_subplot(111)
    ax.set_facecolor(DARK)
    ax.set_aspect('equal')

    # Cells, row 0 at top.
    for i in range(n_rows):
        for j in range(n_cols):
            x = matrix_left + j * cell_w
            y = (n_rows - 1 - i) * cell_h
            q = Q[i, j]
            color = cell_color(q, slog_max)

            ax.add_patch(Rectangle(
                (x + 0.02, y + 0.025),
                cell_w - 0.04, cell_h - 0.05,
                facecolor=color,
                edgecolor=(0.40, 0.45, 0.50, 0.40),
                linewidth=0.5,
                zorder=2,
            ))

            if abs(q) < 1e-9:
                ax.add_patch(Rectangle(
                    (x + 0.02, y + 0.025),
                    cell_w - 0.04, cell_h - 0.05,
                    facecolor='none',
                    edgecolor=(*ZERO_RING, 0.95),
                    linewidth=2.2,
                    zorder=3,
                ))
                ax.scatter(
                    [x + cell_w * 0.50], [y + cell_h * 0.78],
                    s=42, c=[(*ZERO_RING, 0.95)],
                    edgecolors=[(0.05, 0.05, 0.05, 0.85)],
                    linewidths=0.7, zorder=4,
                )

            txt = format_q(q)
            brightness = sum(color[:3]) / 3.0
            text_color = (
                (0.05, 0.05, 0.06, 0.95) if brightness > 0.55
                else (0.96, 0.97, 1.00, 0.95)
            )
            ax.text(
                x + cell_w * 0.50, y + cell_h * 0.45,
                txt,
                color=text_color,
                fontsize=12,
                ha='center', va='center',
                fontweight='bold',
                family='monospace',
                zorder=5,
            )

    # Row labels (shape names).
    for i, s in enumerate(SHAPES):
        y = (n_rows - 1 - i) * cell_h + cell_h * 0.50
        ax.text(
            matrix_left - 0.16, y + 0.06,
            shape_label(s),
            color=(0.96, 0.97, 1.00, 0.92),
            fontsize=15, fontweight='bold',
            ha='right', va='center',
            family='serif',
            zorder=5,
        )
        ax.text(
            matrix_left - 0.16, y - 0.10,
            f'Ω={shape_omega(s)}',
            color=(0.72, 0.78, 0.86, 0.62),
            fontsize=9,
            ha='right', va='center',
            zorder=5,
        )

    # Row label group title.
    ax.text(
        matrix_left - 0.18, n_rows * cell_h + 0.20,
        'shape(n)',
        color=(0.85, 0.88, 0.92, 0.65),
        fontsize=10, fontweight='bold', fontstyle='italic',
        ha='right', va='center',
        zorder=5,
    )

    # Column labels (tau-signatures).
    for j, t in enumerate(TAU_SIGS):
        x = matrix_left + j * cell_w + cell_w * 0.50
        y = n_rows * cell_h + 0.10
        ax.text(
            x, y,
            tau_label(t),
            color=(0.96, 0.97, 1.00, 0.92),
            fontsize=14, fontweight='bold',
            ha='center', va='bottom',
            family='serif',
            zorder=5,
        )
        ax.text(
            x, y + 0.30,
            f'Ω={tau_omega(t)}',
            color=(0.72, 0.78, 0.86, 0.62),
            fontsize=9,
            ha='center', va='bottom',
            zorder=5,
        )

    # Column group title.
    ax.text(
        matrix_left + n_cols * cell_w * 0.5, n_rows * cell_h + 0.78,
        'τ-signature(k)',
        color=(0.85, 0.88, 0.92, 0.65),
        fontsize=11, fontweight='bold', fontstyle='italic',
        ha='center', va='center',
        zorder=5,
    )

    # Coefficient strip on the right.
    ax.text(
        coeff_strip_x, n_rows * cell_h + 0.15,
        'row coefficient pattern  (j=1..5)',
        color=(0.85, 0.88, 0.92, 0.70),
        fontsize=9, fontweight='bold', fontstyle='italic',
        ha='left', va='bottom',
        zorder=5,
    )
    for i, s in enumerate(SHAPES):
        y = (n_rows - 1 - i) * cell_h + cell_h * 0.45
        coeff = coeff_pattern(s)
        txt = format_coeff_pattern(coeff)
        ax.text(
            coeff_strip_x, y,
            txt,
            color=(0.78, 0.84, 0.92, 0.80),
            fontsize=9.5,
            ha='left', va='center',
            family='monospace',
            zorder=5,
        )

    # Title and subtitle.
    fig.text(
        0.5, 0.965,
        'Q at h = 5  —  shape × τ-signature',
        ha='center', va='top', color=(1.0, 1.0, 1.0, 0.95),
        fontsize=21, fontweight='bold', family='serif',
    )
    fig.text(
        0.5, 0.935,
        'rows: shape of n (sorted prime exponents).   columns: τ-signature of k.   '
        'cell: Q_n(n^5 k) for any n, k of those classes (with gcd(k, n) = 1).',
        ha='center', va='top', color=(0.80, 0.85, 0.92, 0.62),
        fontsize=10.5, fontstyle='italic',
    )
    fig.text(
        0.5, 0.918,
        'gold-ringed cells: Q = 0 exactly — coefficient kernel kills the τ-polynomial in j.',
        ha='center', va='top', color=(*ZERO_RING, 0.78),
        fontsize=10, fontstyle='italic',
    )

    # Reading hint at bottom.
    ax.text(
        matrix_left, -0.45,
        'kernel observations.   prime row: kills τ-poly of degree 1..4 (alternating-binomial identity Σ_{j} (−1)^(j−1) C(4, j−1) j^d = 0 for 0 ≤ d ≤ 3).\n'
        'p² and p³ rows: kill degree 1 only (linear-τ kernel).   p⁴ row: linear kernel breaks.   pq, p²q, p³q, pqr rows: no degree-1..4 kernel zeros at h=5.',
        color=(0.85, 0.90, 0.96, 0.70),
        fontsize=9.5, fontstyle='italic',
        ha='left', va='top',
        linespacing=1.4,
        zorder=5,
    )

    ax.set_xlim(0.0, coeff_strip_x + 4.4)
    ax.set_ylim(-1.1, matrix_top + 0.5)
    ax.set_axis_off()

    plt.subplots_adjust(left=0.02, right=0.98, top=0.90, bottom=0.06)
    plt.savefig(OUT, facecolor=DARK)
    plt.close()
    print(f'-> {OUT}')


if __name__ == '__main__':
    main()
