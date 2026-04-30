"""
Rank Lemma Skylight - the integer staircase that truncates the Mercator
expansion of log(1 + n^{-s} ζ(s)).

For m = n^h k with gcd(k, n) = 1 and h = ν_n(m), the formal series

    log(1 + n^{-s} ζ(s)) = sum_{j >= 1} (-1)^(j-1) (n^{-s} ζ(s))^j / j

contributes to [m^{-s}] only at j <= h, because the j-th term carries
n^{-js} and the coefficient of m^{-s} in n^{-js} ζ(s)^j is tau_j(m/n^j)
exactly when n^j | m, and zero otherwise. The truncation is by integer
divisibility — see algebra/FINITE-RANK-EXPANSION.md (Rank Lemma).

Each panel is one n. Columns are sampled m's, sorted by h then by k, so
the height ν_n(m) ascends in clean steps across the panel. Rows are
j = 1, ..., J_GHOST. Cells are panes:

  - active (j <= h): coloured by the signed Mercator term
    (-1)^(j-1) * coeff(n, h, j) * tau_j(k) / j;
  - ghost (j > h): faded grey, dashed; labelled occasionally with the
    non-integer fraction k / n^(j-h) that makes the term vanish.

The bright staircase is ν_n(m) — the rank lemma made literal. Above
it, the would-be Mercator panes hang as ghosts.
"""

import os
from functools import lru_cache
from math import comb, gcd, log

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.patches import Rectangle


HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'q_rank_lemma_skylight.png')

PANEL_NS = [2, 3, 4, 6, 10, 12]
H_MAX = 6
K_PER_H = 20
J_GHOST = 8

IMG_W = 3200
IMG_H = 2200
DARK = '#0a0a0a'

POS_A = np.array([1.00, 0.80, 0.36])
POS_B = np.array([1.00, 0.44, 0.38])
NEG_A = np.array([0.43, 0.78, 1.00])
NEG_B = np.array([0.72, 0.36, 1.00])
RESIDUE_GLOW = np.array([0.88, 1.00, 0.72])
GHOST_GREY = np.array([0.55, 0.58, 0.62])
STAIR_COLOR = np.array([1.00, 0.85, 0.55])


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


@lru_cache(maxsize=None)
def tau(j, x):
    if j < 1:
        raise ValueError(f'tau index must be >= 1, got {j}')
    if x < 1:
        raise ValueError(f'tau argument must be >= 1, got {x}')
    if j == 1:
        return 1
    prod = 1
    for _p, e in factor_tuple(x):
        prod *= comb(e + j - 1, j - 1)
    return prod


def first_coprimes_to_n(n, count):
    """First `count` positive integers k with gcd(k, n) = 1."""
    out = []
    k = 1
    while len(out) < count:
        if gcd(k, n) == 1:
            out.append(k)
        k += 1
    return out


def signed_term(n, h, k, j):
    """Mercator term (-1)^(j-1) * coeff * tau_j(k) / j for gcd(k, n) = 1.

    With t_i = 0, the binomial-product structure factor reduces to
    prod_i C(a_i (h-j) + j - 1, j - 1).
    """
    coeff = 1
    for _p, a in factor_tuple(n):
        coeff *= comb(a * (h - j) + j - 1, j - 1)
    residue = tau(j, k)
    sign = 1 if j % 2 == 1 else -1
    return sign * coeff * residue / j, coeff, residue, sign


def panel_records(n):
    """m = n^h * k records, sorted by h then k. K_PER_H samples per h."""
    out = []
    ks = first_coprimes_to_n(n, K_PER_H)
    for h in range(1, H_MAX + 1):
        for k in ks:
            out.append({'n': n, 'h': h, 'k': k})
    return out


def panel_geometry(panel_index):
    col = panel_index % 3
    row = panel_index // 3
    panel_w = 920.0
    panel_h = 820.0
    gap_x = 110.0
    gap_y = 150.0
    left = 130.0 + col * (panel_w + gap_x)
    bottom = 170.0 + (1 - row) * (panel_h + gap_y)
    return left, bottom, panel_w, panel_h


def compute_term_norm():
    max_log = 1.0
    for n in PANEL_NS:
        ks = first_coprimes_to_n(n, K_PER_H)
        for h in range(1, H_MAX + 1):
            for k in ks:
                for j in range(1, h + 1):
                    t, _, _, _ = signed_term(n, h, k, j)
                    max_log = max(max_log, log(abs(t) + 1.0))
    return max_log


def blend(a, b, t):
    return a * (1.0 - t) + b * t


def active_color(sign, term_norm, residue_norm):
    if sign > 0:
        rgb = blend(POS_A, POS_B, 0.25 + 0.55 * residue_norm)
    else:
        rgb = blend(NEG_A, NEG_B, 0.20 + 0.60 * residue_norm)
    rgb = rgb * (0.78 + 0.55 * term_norm) + RESIDUE_GLOW * (0.10 * residue_norm)
    return np.clip(rgb, 0.0, 1.0)


def render_panel(ax, n, panel_idx, term_norm_max):
    left, bottom, panel_w, panel_h = panel_geometry(panel_idx)
    records = panel_records(n)
    n_cols = len(records)

    inner_left = left + panel_w * 0.085
    inner_right = left + panel_w * 0.96
    inner_bottom = bottom + panel_h * 0.10
    inner_top = bottom + panel_h * 0.90

    col_w = (inner_right - inner_left) / n_cols
    row_h = (inner_top - inner_bottom) / J_GHOST

    pad_x = col_w * 0.05
    pad_y = row_h * 0.07

    # Soft skylight glow at the top of the panel where the ghost zone lives.
    glow_band_bottom = inner_bottom + H_MAX * row_h
    glow_band_top = inner_top
    n_grad = 24
    for k in range(n_grad):
        frac = k / max(n_grad - 1, 1)
        y0 = glow_band_bottom + (glow_band_top - glow_band_bottom) * frac
        y1 = glow_band_bottom + (glow_band_top - glow_band_bottom) * (frac + 1.0 / n_grad)
        a = 0.05 * (1.0 - frac)
        ax.fill_between(
            [inner_left, inner_right],
            y0, y1,
            color=(0.20, 0.27, 0.36, a),
            zorder=0.5,
            linewidth=0,
        )

    active_rects = []
    active_facecolors = []
    ghost_rects = []
    ghost_facecolors = []

    boundary_x = []
    boundary_y = []

    for col, rec in enumerate(records):
        h = rec['h']
        k = rec['k']
        x0 = inner_left + col * col_w + pad_x
        cell_w = col_w - 2 * pad_x

        cx = inner_left + (col + 0.5) * col_w
        boundary_x.append(cx)
        boundary_y.append(inner_bottom + h * row_h)

        for j in range(1, J_GHOST + 1):
            y0 = inner_bottom + (j - 1) * row_h + pad_y
            cell_h = row_h - 2 * pad_y
            if j <= h:
                term, _, residue, sign = signed_term(n, h, k, j)
                t_norm = log(abs(term) + 1.0) / term_norm_max
                r_norm = min(log(residue + 1.0) / 6.0, 1.0)
                rgb = active_color(sign, t_norm, r_norm)
                alpha = float(np.clip(0.45 + 0.45 * t_norm, 0.30, 0.95))
                active_rects.append(Rectangle((x0, y0), cell_w, cell_h))
                active_facecolors.append((rgb[0], rgb[1], rgb[2], alpha))
            else:
                fade = max(0.16 - 0.014 * (j - h - 1), 0.06)
                ghost_rects.append(Rectangle((x0, y0), cell_w, cell_h))
                ghost_facecolors.append((GHOST_GREY[0], GHOST_GREY[1], GHOST_GREY[2], fade))

    if ghost_rects:
        gc = PatchCollection(ghost_rects, match_original=False)
        gc.set_facecolor(ghost_facecolors)
        gc.set_edgecolor((0.55, 0.60, 0.65, 0.18))
        gc.set_linewidth(0.35)
        gc.set_linestyle('--')
        gc.set_zorder(1.6)
        ax.add_collection(gc)

    if active_rects:
        ac = PatchCollection(active_rects, match_original=False)
        ac.set_facecolor(active_facecolors)
        ac.set_edgecolor('none')
        ac.set_zorder(3)
        ax.add_collection(ac)

    # The integer staircase ν_n(m).
    pts = list(zip(boundary_x, boundary_y))
    segments = [[pts[i], pts[i + 1]] for i in range(len(pts) - 1)]
    glow = LineCollection(
        segments,
        colors=(STAIR_COLOR[0], STAIR_COLOR[1], STAIR_COLOR[2], 0.10),
        linewidths=10.0,
        zorder=3.7,
    )
    line = LineCollection(
        segments,
        colors=(STAIR_COLOR[0], STAIR_COLOR[1], STAIR_COLOR[2], 0.62),
        linewidths=2.4,
        zorder=4.0,
    )
    ax.add_collection(glow)
    ax.add_collection(line)

    # j-axis labels on the left.
    for j in range(1, J_GHOST + 1):
        y = inner_bottom + (j - 0.5) * row_h
        is_ghost = j > H_MAX
        col_rgba = (1.0, 1.0, 1.0, 0.42) if not is_ghost else (0.7, 0.74, 0.78, 0.26)
        ax.text(
            inner_left - col_w * 1.6,
            y,
            f'j={j}',
            color=col_rgba,
            fontsize=10,
            ha='right',
            va='center',
            zorder=8,
        )

    # h-block separators and labels.
    for h in range(1, H_MAX):
        x = inner_left + h * K_PER_H * col_w
        ax.plot(
            [x, x],
            [inner_bottom - row_h * 0.20, inner_top + row_h * 0.05],
            color=(0.62, 0.66, 0.70, 0.10),
            lw=0.5,
            zorder=2.5,
        )
    for h in range(1, H_MAX + 1):
        x = inner_left + (h - 0.5) * K_PER_H * col_w
        ax.text(
            x,
            inner_bottom - row_h * 0.55,
            f'h={h}',
            color=(1.0, 1.0, 1.0, 0.34),
            fontsize=9,
            ha='center',
            va='center',
            zorder=8,
        )

    # Panel header.
    ax.text(
        left + panel_w * 0.07,
        bottom + panel_h * 0.965,
        f'n={n}  {n_type(n)}',
        color=(1.0, 1.0, 1.0, 0.50),
        fontsize=14,
        ha='left',
        va='center',
        zorder=8,
    )

    # Annotate one ghost cell per h-block with its non-integer m/n^j = k/n^(j-h).
    for h in range(1, H_MAX + 1):
        col_in_block = K_PER_H // 2
        col_idx = (h - 1) * K_PER_H + col_in_block
        if col_idx >= len(records):
            continue
        rec = records[col_idx]
        k = rec['k']
        j = h + 1
        if j > J_GHOST:
            continue
        diff = j - h
        cx = inner_left + (col_idx + 0.5) * col_w
        cy = inner_bottom + (j - 0.5) * row_h
        if diff == 1:
            txt = f'{k}/{n}'
        else:
            txt = f'{k}/{n}^{diff}'
        ax.text(
            cx,
            cy,
            txt,
            color=(0.78, 0.82, 0.86, 0.62),
            fontsize=7,
            ha='center',
            va='center',
            zorder=6,
            fontstyle='italic',
        )


def build_art():
    print('Computing global term norm...')
    term_norm = compute_term_norm()

    print('Rendering panels...')
    fig = plt.figure(figsize=(16, 11), dpi=200, facecolor=DARK, frameon=False)
    ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    ax.set_axis_off()
    ax.set_facecolor(DARK)
    fig.add_axes(ax)

    for i, n in enumerate(PANEL_NS):
        render_panel(ax, n, i, term_norm)

    # Title and caption above the top row.
    ax.text(
        IMG_W * 0.5,
        IMG_H - 95,
        'Rank Lemma Skylight',
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
        'active panes: signed Mercator term  (-1)^(j-1) · τ_j(m/n^j) / j .   '
        'ghost panes: j > ν_n(m), where m/n^j ∉ ℤ.   '
        'staircase = ν_n(m) — the rank lemma.',
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
