"""
n-Multiples Loom - the integer-language reading of Q_n.

Per algebra/Q-FORMULAS.md (and the integer-language section there),

    Q_n(m) = sum_{j = 1}^{ν_n(m)}
             (-1)^(j-1) · #{ordered j-tuples (n d_1, …, n d_j) with product m} / j .

Each panel fixes one (n, h, k) and m = n^h · k. The j-th row of the loom
contains every ordered j-tuple of multiples-of-n whose product is m,
laid out as cells. Odd-j rows are warm (positive contribution), even-j
rows are cool (negative contribution); cell saturation drops with j to
mirror the Mercator weight 1/j. Each factor is rendered explicitly as
"n·d", so the constraint "every factor is a multiple of n" is on the
page, not in the reader's head.

Below the weave, the balance ledger shows the cancellation directly: a
warm bar of total positive mass, a cool bar of total negative mass, and
a diamond at the signed difference Q_n(m). Prime n at h = 3 with k a
single prime sits the diamond at zero — the low-payload zero band as
perfect cancellation.

Panel: same n's as q_distillery_h3_ns.py at h = 3, with k chosen for
factorisation variety while staying within cell-count budgets.
"""

import os
from functools import lru_cache
from math import comb, gcd

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon


HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'q_loom.png')

# Per-panel: (n, h, k, type_label).
# k chosen coprime to n so the master expansion lives in the (t_i = 0) sub-case.
PANEL_CONFIG = [
    (2, 3, 3, 'prime'),
    (3, 3, 2, 'prime'),
    (4, 3, 1, 'prime_power'),
    (6, 3, 1, 'squarefree'),
    (10, 3, 1, 'squarefree'),
    (12, 3, 1, 'mixed'),
]

IMG_W = 3200
IMG_H = 2200
DARK = '#0a0a0a'

POS_A = np.array([1.00, 0.80, 0.36])
POS_B = np.array([1.00, 0.44, 0.38])
NEG_A = np.array([0.43, 0.78, 1.00])
NEG_B = np.array([0.72, 0.36, 1.00])
DIAMOND_BRIGHT = np.array([1.00, 0.92, 0.65])


@lru_cache(maxsize=None)
def factor_tuple(n):
    if n < 1:
        raise ValueError(f'factor_tuple expects positive n, got {n}')
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


def n_type(n):
    factors = factor_tuple(n)
    omega = len(factors)
    total = sum(e for _p, e in factors)
    if omega == 1 and total == 1:
        return 'prime'
    if omega == 1:
        return 'prime_power'
    if all(e == 1 for _p, e in factors):
        return 'squarefree'
    return 'mixed'


def ordered_factorisations(x, j):
    """All ordered j-tuples (a_1, …, a_j) of positive integers with product x."""
    if j == 1:
        return [(x,)]
    out = []
    for a in range(1, x + 1):
        if x % a == 0:
            for tail in ordered_factorisations(x // a, j - 1):
                out.append((a,) + tail)
    return out


def loom_tuples(n, h, k):
    """For m = n^h · k, return list-of-lists: outer index j ∈ [1, h], inner are
    the ordered j-tuples (n d_1, …, n d_j) with product m."""
    m = n ** h * k
    out = []
    for j in range(1, h + 1):
        x = m // (n ** j)  # integer because j ≤ h
        d_tuples = ordered_factorisations(x, j)
        out.append([tuple(n * d for d in t) for t in d_tuples])
    return out


def q_value(n, h, k):
    """Master expansion at (n, h, k) with gcd(k, n) = 1 ⇒ all t_i = 0."""
    factors = factor_tuple(n)
    total = 0.0
    for j in range(1, h + 1):
        coeff = 1
        for _p, a in factors:
            coeff *= comb(a * (h - j) + j - 1, j - 1)
        residue = 1
        for _p, e in factor_tuple(k):
            residue *= comb(e + j - 1, j - 1)
        sign = 1 if j % 2 == 1 else -1
        total += sign * coeff * residue / j
    return total


def panel_geometry(panel_index):
    col = panel_index % 3
    row = panel_index // 3
    panel_w = 920.0
    panel_h = 850.0
    gap_x = 110.0
    gap_y = 130.0
    left = 130.0 + col * (panel_w + gap_x)
    bottom = 170.0 + (1 - row) * (panel_h + gap_y)
    return left, bottom, panel_w, panel_h


def blend(a, b, t):
    return a * (1.0 - t) + b * t


def row_color(j):
    """Warm for odd j, cool for even j. Saturation drops with j (the 1/j weight)."""
    sat = 1.0 / j ** 0.6  # gentle fade; j=1: 1.00, j=2: 0.66, j=3: 0.52
    if j % 2 == 1:
        rgb = blend(POS_B, POS_A, sat)
    else:
        rgb = blend(NEG_B, NEG_A, sat)
    return np.clip(rgb, 0.0, 1.0), sat


def draw_loom_cell(ax, cx, cy, w, h, n, factors, base_rgb, sat):
    """One cell with text 'n·d_1 · n·d_2 · ... · n·d_j'."""
    cell_rgb = base_rgb * 0.30
    cell_alpha = 0.30 + 0.45 * sat
    rect = FancyBboxPatch(
        (cx - w * 0.5, cy - h * 0.5),
        w, h,
        boxstyle='round,pad=0.0,rounding_size=6',
        linewidth=0.7,
        edgecolor=(base_rgb[0], base_rgb[1], base_rgb[2], 0.55 + 0.30 * sat),
        facecolor=(cell_rgb[0], cell_rgb[1], cell_rgb[2], cell_alpha),
        zorder=3,
    )
    ax.add_patch(rect)

    # Render "n·d" factors separated by ·, with n in glyph color, d in text color.
    parts = []
    for d in factors:
        parts.append(f'{n}·{d}')
    text = '   '.join(parts)
    fs = max(6, min(12, int(w / max(len(text), 1) * 1.45)))
    ax.text(
        cx, cy,
        text,
        color=(1.0, 1.0, 1.0, 0.92),
        fontsize=fs,
        ha='center',
        va='center',
        zorder=4,
        family='monospace',
    )


def render_balance(ax, x_left, x_right, cy, bar_h, pos_mass, neg_mass, q):
    span = pos_mass + neg_mass
    if span < 1e-12:
        return
    width = x_right - x_left
    margin = width * 0.04
    usable = width - 2 * margin
    scale = usable / span
    cool_x = x_left + margin
    zero_x = cool_x + neg_mass * scale
    warm_end = zero_x + pos_mass * scale

    # Cool bar (negative mass) on the left side of zero.
    ax.add_patch(Rectangle(
        (cool_x, cy - bar_h * 0.5),
        zero_x - cool_x, bar_h,
        facecolor=(NEG_A[0], NEG_A[1], NEG_A[2], 0.42),
        edgecolor=(NEG_A[0], NEG_A[1], NEG_A[2], 0.65),
        linewidth=0.7,
        zorder=3,
    ))
    # Warm bar (positive mass) on the right side of zero.
    ax.add_patch(Rectangle(
        (zero_x, cy - bar_h * 0.5),
        warm_end - zero_x, bar_h,
        facecolor=(POS_A[0], POS_A[1], POS_A[2], 0.42),
        edgecolor=(POS_A[0], POS_A[1], POS_A[2], 0.65),
        linewidth=0.7,
        zorder=3,
    ))
    # Zero line.
    ax.plot(
        [zero_x, zero_x],
        [cy - bar_h * 0.85, cy + bar_h * 0.85],
        color=(1.0, 1.0, 1.0, 0.32),
        lw=0.9,
        zorder=4,
    )
    # Diamond at signed Q.
    diamond_x = zero_x + q * scale
    diamond_size = bar_h * 0.62
    diamond_pts = [
        (diamond_x, cy + diamond_size),
        (diamond_x + diamond_size * 0.72, cy),
        (diamond_x, cy - diamond_size),
        (diamond_x - diamond_size * 0.72, cy),
    ]
    if abs(q) < 1e-9:
        diamond_color = DIAMOND_BRIGHT
    elif q > 0:
        diamond_color = POS_A
    else:
        diamond_color = NEG_A
    ax.add_patch(Polygon(
        diamond_pts,
        closed=True,
        facecolor=(diamond_color[0], diamond_color[1], diamond_color[2], 0.95),
        edgecolor=(1.0, 1.0, 1.0, 0.85),
        linewidth=1.2,
        zorder=6,
    ))
    # Q value label below.
    ax.text(
        diamond_x,
        cy - bar_h * 1.65,
        f'Q_n(m) = {q:+.4f}',
        color=(diamond_color[0], diamond_color[1], diamond_color[2], 0.95),
        fontsize=11,
        ha='center',
        va='center',
        family='monospace',
        zorder=7,
    )
    # Tick labels for the bar magnitudes.
    ax.text(
        cool_x,
        cy + bar_h * 1.10,
        f'−Σ even = −{neg_mass:.3g}',
        color=(NEG_A[0], NEG_A[1], NEG_A[2], 0.78),
        fontsize=9,
        ha='left',
        va='center',
        family='monospace',
        zorder=5,
    )
    ax.text(
        warm_end,
        cy + bar_h * 1.10,
        f'+Σ odd = +{pos_mass:.3g}',
        color=(POS_A[0], POS_A[1], POS_A[2], 0.78),
        fontsize=9,
        ha='right',
        va='center',
        family='monospace',
        zorder=5,
    )


def render_panel(ax, panel_idx, n, h, k, label):
    left, bottom, panel_w, panel_h = panel_geometry(panel_idx)
    m = n ** h * k
    rows = loom_tuples(n, h, k)
    q = q_value(n, h, k)

    # Layout: header / weave / ledger.
    header_h = panel_h * 0.10
    ledger_h = panel_h * 0.20
    weave_top = bottom + panel_h - header_h
    weave_bottom = bottom + ledger_h + panel_h * 0.02
    weave_h = weave_top - weave_bottom

    inner_left = left + panel_w * 0.07
    inner_right = left + panel_w * 0.93
    inner_w = inner_right - inner_left

    # Header.
    ax.text(
        left + panel_w * 0.07,
        bottom + panel_h * 0.96,
        f'n={n}  {label}',
        color=(1.0, 1.0, 1.0, 0.55),
        fontsize=14,
        ha='left',
        va='center',
        zorder=8,
    )
    ax.text(
        left + panel_w * 0.93,
        bottom + panel_h * 0.96,
        f'm = {n}^{h}·{k} = {m}',
        color=(1.0, 1.0, 1.0, 0.45),
        fontsize=11,
        ha='right',
        va='center',
        family='monospace',
        zorder=8,
    )

    # Weave rows: j=1 at top, j=h at bottom.
    row_h = weave_h / h
    for j_idx in range(h):
        j = j_idx + 1
        row_top = weave_top - j_idx * row_h
        row_cy = row_top - row_h * 0.5
        cell_h = row_h * 0.66

        n_cells = len(rows[j_idx])
        if n_cells == 0:
            continue

        # Decide cell width: aim for 270 px max, but compress if needed.
        gap_min = 10.0
        max_cell_w = 280.0
        ideal_w = (inner_w - (n_cells - 1) * gap_min) / n_cells
        cell_w = min(ideal_w, max_cell_w)
        gap = max(gap_min, (inner_w - n_cells * cell_w) / max(n_cells - 1, 1)) if n_cells > 1 else 0
        if cell_w * n_cells + gap * max(n_cells - 1, 0) > inner_w:
            cell_w = (inner_w - (n_cells - 1) * gap_min) / n_cells
            gap = gap_min
        total_w = cell_w * n_cells + gap * max(n_cells - 1, 0)
        cells_left = inner_left + (inner_w - total_w) * 0.5

        rgb, sat = row_color(j)

        # j-axis label and row total annotation.
        ax.text(
            inner_left - 14,
            row_cy,
            f'j={j}',
            color=(1.0, 1.0, 1.0, 0.40),
            fontsize=10,
            ha='right',
            va='center',
            zorder=8,
        )
        sign_str = '+' if j % 2 == 1 else '−'
        ax.text(
            inner_right + 14,
            row_cy,
            f'{sign_str} {n_cells}/{j}',
            color=(rgb[0], rgb[1], rgb[2], 0.85),
            fontsize=11,
            ha='left',
            va='center',
            family='monospace',
            zorder=8,
        )

        # Cells.
        for ci, tup in enumerate(rows[j_idx]):
            cx = cells_left + ci * (cell_w + gap) + cell_w * 0.5
            # Each tup entry is n*d_i; recover d_i = entry/n for clean rendering.
            d_factors = [v // n for v in tup]
            draw_loom_cell(ax, cx, row_cy, cell_w, cell_h, n, d_factors, rgb, sat)

    # Balance ledger.
    pos_mass = sum(len(rows[j_idx]) / (j_idx + 1)
                   for j_idx in range(h) if (j_idx + 1) % 2 == 1)
    neg_mass = sum(len(rows[j_idx]) / (j_idx + 1)
                   for j_idx in range(h) if (j_idx + 1) % 2 == 0)
    ledger_cy = bottom + ledger_h * 0.55
    ledger_bar_h = ledger_h * 0.32
    render_balance(
        ax,
        inner_left,
        inner_right,
        ledger_cy,
        ledger_bar_h,
        pos_mass,
        neg_mass,
        q,
    )


def build_art():
    print('Computing looms and Q values...')
    fig = plt.figure(figsize=(16, 11), dpi=200, facecolor=DARK, frameon=False)
    ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    ax.set_axis_off()
    ax.set_facecolor(DARK)
    fig.add_axes(ax)

    for i, (n, h, k, label) in enumerate(PANEL_CONFIG):
        render_panel(ax, i, n, h, k, label)

    # Title and caption above the top row.
    ax.text(
        IMG_W * 0.5,
        IMG_H - 95,
        'n-Multiples Loom',
        color=(1.0, 1.0, 1.0, 0.55),
        fontsize=22,
        ha='center',
        va='center',
        zorder=10,
        family='serif',
    )
    ax.text(
        IMG_W * 0.5,
        IMG_H - 130,
        'rows = j; cells = ordered j-tuples (n·d_1, …, n·d_j) with product m.   '
        'warm = positive (odd j), cool = negative (even j); fade = 1/j.   '
        'ledger diamond = Q_n(m).',
        color=(0.85, 0.88, 0.92, 0.42),
        fontsize=11,
        ha='center',
        va='center',
        zorder=10,
        fontstyle='italic',
    )

    ax.set_xlim(0, IMG_W)
    ax.set_ylim(0, IMG_H)
    ax.set_aspect('equal')

    fig.canvas.draw()
    rgba = np.asarray(fig.canvas.buffer_rgba()).astype(np.float64) / 255.0
    bg = np.array([10, 10, 10], dtype=np.float64) / 255.0
    rgb_out = rgba[:, :, :3] * rgba[:, :, 3:4] + bg * (1.0 - rgba[:, :, 3:4])
    plt.imsave(OUT, np.clip(rgb_out, 0.0, 1.0))
    plt.close(fig)


def main():
    build_art()
    print(f'-> {OUT}')


if __name__ == '__main__':
    main()
