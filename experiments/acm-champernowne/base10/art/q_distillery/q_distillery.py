"""
Q Distillery - finite-rank Q_n as structure plus residue.

For m = n^h k with exact height h, core/Q-FORMULAS.md writes

    Q_n(m) = sum_j sign(j) * structure(n, h, t, j) * tau_j(k') / j.

This image renders four canonical vessels - one per factorisation type
of n - as portrait distillation columns. Each vessel stacks six h-bands
top-to-bottom (h=1 at top, h=6 at bottom; bands grow taller with rank
to match the increasing j-stack depth). Inside each band, j-strips
stack from j=1 down to j=h. Within each j-strip, every sampled payload
appears as a colored glyph whose:

    x = log-position of the payload k,
    y = stratum sorted by the binomial-product coefficient
        for that payload's overlap tuple,
    color = signed Mercator contribution (warm = positive, cool = negative),
    size = magnitude of the term tau_j(k') / j scaled by the coefficient.

The stratification is the visual claim: primes collapse to one stratum
per strip (overlap is always (0)), prime-powers split into two strata
(overlap t in {0, 1}), squarefree multi-prime braids across several
strata (overlap pairs combine multiplicatively), and mixed n weaves
the most layered pattern. Threads connect each glyph at j to the
corresponding glyph at j+1, so the cancellation flow is literally
drawn from layer to layer.

Bottom of each h-band: the distillate row, one signed Q_n dot per
sampled payload.
"""

import os
from functools import lru_cache
from math import comb, log

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.path import Path
from matplotlib.patches import PathPatch


HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'q_distillery.png')

# Four canonical examples - one per factorisation category.
# Cuts within-category redundancy (n=3, 5, 10 dropped) so each panel
# can be ~3.6x the area of the original 6-panel grid.
PANEL_NS = [2, 4, 6, 12]
H_MAX = 5  # h=1..5; h=6 added too much vertical and the per-strip
           # density at h=6 was hard to read anyway.
K_SAMPLES = 140
K_MAX = 3600

IMG_W = 2800
IMG_H = 2700
DARK = '#0a0a0a'

# Warm pair (positive sign j odd) and cool pair (negative sign j even).
POS_A = np.array([1.00, 0.80, 0.36])  # gold
POS_B = np.array([1.00, 0.44, 0.38])  # red-orange
NEG_A = np.array([0.43, 0.78, 1.00])  # ice blue
NEG_B = np.array([0.72, 0.36, 1.00])  # violet
RESIDUE_GLOW = np.array([0.88, 1.00, 0.72])
DISTILLATE_POS = np.array([1.00, 0.86, 0.50])
DISTILLATE_NEG = np.array([0.55, 0.78, 1.00])


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
        return 'prime power'
    if all(e == 1 for _p, e in factors):
        return 'squarefree'
    return 'mixed'


def decompose_payload(n, k):
    t = []
    k_prime = k
    for p, _a in factor_tuple(n):
        e = 0
        while k_prime % p == 0:
            e += 1
            k_prime //= p
        t.append(e)
    return tuple(t), k_prime


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


def payloads_for_n(n):
    raw = np.unique(np.round(np.geomspace(1, K_MAX, K_SAMPLES * 4)).astype(int))
    vals = [int(k) for k in raw if k % n != 0]
    if len(vals) < K_SAMPLES:
        k = 1
        seen = set(vals)
        while len(vals) < K_SAMPLES:
            if k % n != 0 and k not in seen:
                vals.append(k)
                seen.add(k)
            k += 1
        vals.sort()
    return vals[:K_SAMPLES]


def coeff_for(n, h, j, overlaps):
    factors = factor_tuple(n)
    coeff = 1
    for (_p, a), t_i in zip(factors, overlaps):
        coeff *= comb(a * (h - j) + t_i + j - 1, j - 1)
    return coeff


def layer_terms(n, h, k):
    overlaps, k_prime = decompose_payload(n, k)
    out = []
    for j in range(1, h + 1):
        coeff = coeff_for(n, h, j, overlaps)
        residue = tau(j, k_prime)
        sign = 1 if j % 2 == 1 else -1
        contribution = sign * coeff * residue / j
        out.append({
            'j': j,
            'coeff': coeff,
            'residue': residue,
            'term': contribution,
            'k_prime': k_prime,
            'overlaps': overlaps,
        })
    return out


def collect_records():
    records = []
    for n in PANEL_NS:
        payloads = payloads_for_n(n)
        for h in range(1, H_MAX + 1):
            for idx, k in enumerate(payloads):
                terms = layer_terms(n, h, k)
                q_value = sum(t['term'] for t in terms)
                for term in terms:
                    rec = dict(term)
                    rec.update({
                        'n': n,
                        'h': h,
                        'k': k,
                        'payload_idx': idx,
                        'q': q_value,
                    })
                    records.append(rec)
    return records


def stratum_index_map(n):
    """For each (h, j), enumerate the distinct binomial coefficients
    that arise across overlap tuples present in the payload sample
    of monoid n, sorted ascending. Returns
        strata[(h, j)] = sorted list of distinct coefficient values
    so that a glyph at coefficient c sits at y-rank
        strata[(h, j)].index(c) / max(1, len(strata)-1).
    For prime n the list always has length 1; for prime power length up
    to a; for squarefree multi-prime length scales with overlap tuples.
    """
    strata = {}
    payloads = payloads_for_n(n)
    for h in range(1, H_MAX + 1):
        for j in range(1, h + 1):
            seen = set()
            for k in payloads:
                overlaps, _ = decompose_payload(n, k)
                seen.add(coeff_for(n, h, j, overlaps))
            strata[(h, j)] = sorted(seen)
    return strata


def normalize_logs(records):
    coeff_logs = np.array([log(r['coeff'] + 1.0) for r in records])
    residue_logs = np.array([log(r['residue'] + 1.0) for r in records])
    term_logs = np.array([log(abs(r['term']) + 1.0) for r in records])
    q_logs = np.array([log(abs(r['q']) + 1.0) for r in records])
    return {
        'coeff': max(float(coeff_logs.max()), 1e-9),
        'residue': max(float(residue_logs.max()), 1e-9),
        'term': max(float(term_logs.max()), 1e-9),
        'q': max(float(q_logs.max()), 1e-9),
    }


def blend(a, b, t):
    return a * (1.0 - t) + b * t


def contribution_color(sign, residue_norm, term_norm):
    if sign > 0:
        rgb = blend(POS_A, POS_B, 0.30 + 0.50 * residue_norm)
    else:
        rgb = blend(NEG_A, NEG_B, 0.20 + 0.55 * residue_norm)
    rgb = rgb * (0.72 + 0.55 * term_norm) + RESIDUE_GLOW * (0.10 * residue_norm)
    return np.clip(rgb, 0.0, 1.0)


# Per-h band height: bands grow taller with h to give the j-stack room.
J_STRIP_PX = 44.0
BAND_HEADER_PX = 22.0
BAND_DISTILLATE_PX = 30.0
BAND_INNER_GAP = 6.0
BAND_OUTER_GAP = 16.0

VESSEL_WIDTH_FRAC = 0.78          # vessel width / panel width
VESSEL_PADDING_FRAC = 0.045        # vertical padding inside vessel


def band_height(h):
    return (
        BAND_HEADER_PX
        + h * J_STRIP_PX
        + BAND_INNER_GAP
        + BAND_DISTILLATE_PX
    )


def vessel_total_height():
    bands = sum(band_height(h) for h in range(1, H_MAX + 1))
    gaps = (H_MAX - 1) * BAND_OUTER_GAP
    return bands + gaps


def panel_geometry(panel_index):
    """2x2 layout. Returns the bounding box of the panel."""
    col = panel_index % 2
    row = panel_index // 2
    panel_w = (IMG_W - 240.0) / 2.0
    panel_h = (IMG_H - 200.0) / 2.0
    left = 120.0 + col * panel_w
    bottom = 100.0 + (1 - row) * panel_h
    return left, bottom, panel_w, panel_h


def vessel_geometry(panel_index):
    """Inner vessel bounding box within a panel."""
    pleft, pbottom, pw, ph = panel_geometry(panel_index)
    title_band = 140.0  # full clearance for "n = N" + category subtitle
    inner_top = pbottom + ph - title_band
    vessel_h = vessel_total_height() + 2 * (VESSEL_PADDING_FRAC * vessel_total_height())
    vessel_w = pw * VESSEL_WIDTH_FRAC
    cx = pleft + pw * 0.5
    vleft = cx - vessel_w * 0.5
    vbottom = inner_top - vessel_h
    return vleft, vbottom, vessel_w, vessel_h


def draw_vessel_outline(ax, panel_index, n):
    pleft, pbottom, pw, ph = panel_geometry(panel_index)
    vleft, vbottom, vw, vh = vessel_geometry(panel_index)
    cx = vleft + vw * 0.5

    # Portrait flask: narrow neck at top, body widens slightly at the
    # bottom (where deeper distillation lives).
    neck = vw * 0.30
    upper = vw * 0.42
    lower = vw * 0.50
    y_top = vbottom + vh
    y_bot = vbottom
    y_shoulder = vbottom + vh * 0.86
    y_belly = vbottom + vh * 0.18

    verts = [
        (cx - neck, y_top),
        (cx - upper, y_top - vh * 0.07),
        (cx - upper, y_shoulder),
        (cx - lower, y_belly),
        (cx - lower * 0.9, y_bot),
        (cx + lower * 0.9, y_bot),
        (cx + lower, y_belly),
        (cx + upper, y_shoulder),
        (cx + upper, y_top - vh * 0.07),
        (cx + neck, y_top),
        (cx - neck, y_top),
    ]
    codes = [
        Path.MOVETO,
        Path.CURVE3,
        Path.CURVE3,
        Path.CURVE3,
        Path.CURVE3,
        Path.LINETO,
        Path.CURVE3,
        Path.CURVE3,
        Path.CURVE3,
        Path.CURVE3,
        Path.CLOSEPOLY,
    ]
    patch = PathPatch(
        Path(verts, codes),
        facecolor=(0.025, 0.030, 0.035, 0.55),
        edgecolor=(0.55, 0.66, 0.72, 0.30),
        linewidth=1.3,
        zorder=1,
    )
    ax.add_patch(patch)

    # Title bar above the vessel - two lines, well-separated, with
    # generous clearance from the vessel below.
    ax.text(
        pleft + pw * 0.5,
        pbottom + ph - 50.0,
        f'n = {n}',
        color=(1.0, 1.0, 1.0, 0.95),
        fontsize=26,
        fontweight='bold',
        ha='center',
        va='center',
        zorder=10,
    )

    # Category subtitle - colored by category for quick visual binding.
    cat = n_type(n)
    cat_colors = {
        'prime':       (1.00, 0.86, 0.50),  # warm gold
        'prime power': (1.00, 0.66, 0.42),  # warm orange
        'squarefree':  (0.62, 0.86, 1.00),  # cool blue
        'mixed':       (0.78, 0.62, 1.00),  # cool violet
    }
    ax.text(
        pleft + pw * 0.5,
        pbottom + ph - 88.0,
        cat,
        color=(*cat_colors[cat], 0.90),
        fontsize=15,
        fontstyle='italic',
        ha='center',
        va='center',
        zorder=10,
    )


def band_layout(panel_index):
    """For each h in 1..H_MAX, return the (y_bottom, y_top) of its
    band inside the vessel. h=1 at top, h=H_MAX at bottom."""
    vleft, vbottom, vw, vh = vessel_geometry(panel_index)
    pad = VESSEL_PADDING_FRAC * vessel_total_height()
    inner_top = vbottom + vh - pad
    bands = {}
    cursor = inner_top
    for h in range(1, H_MAX + 1):
        bh = band_height(h)
        cursor -= bh
        bands[h] = (cursor, cursor + bh)
        cursor -= BAND_OUTER_GAP
    return bands


def jstrip_y(band_bot, band_top, h, j):
    """Within a band, j=1 at the top of the j-stack, j=h at the bottom.
    Returns y center of the j-strip."""
    # Layout: header (top) | j-strips (middle) | distillate (bottom)
    distillate_zone = BAND_DISTILLATE_PX + BAND_INNER_GAP
    jstack_top = band_top - BAND_HEADER_PX
    jstack_bot = band_bot + distillate_zone
    strip_h = (jstack_top - jstack_bot) / h
    y_center = jstack_top - strip_h * (j - 0.5)
    return y_center, strip_h


def build_art(records, norms):
    panel_by_n = {n: i for i, n in enumerate(PANEL_NS)}
    payload_by_n = {n: payloads_for_n(n) for n in PANEL_NS}
    strata_by_n = {n: stratum_index_map(n) for n in PANEL_NS}

    # log-x positions per (n, payload_idx) - shared across all h, j
    log_kmax = log(K_MAX)
    x_positions_by_n = {}
    for n in PANEL_NS:
        ks = payload_by_n[n]
        x_positions_by_n[n] = np.array([log(k) / log_kmax for k in ks])

    fig = plt.figure(
        figsize=(IMG_W / 200, IMG_H / 200),
        dpi=200,
        facecolor=DARK,
        frameon=False,
    )
    ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    ax.set_axis_off()
    ax.set_facecolor(DARK)
    fig.add_axes(ax)

    # Pre-compute glyph data and stratum lines.
    # Glyph: dot at (x, y_strip + stratum_offset) per (h, j, payload).
    # No threads - they smeared out the strata structure that's the
    # visual claim. Per-strip horizontal stratum lines instead, so the
    # number of strata is visible even where dots are sparse.
    glyph_x = []
    glyph_y = []
    glyph_color = []
    glyph_size = []

    stratum_segments = []
    stratum_colors = []
    stratum_widths = []

    distillate_x = []
    distillate_y = []
    distillate_color = []
    distillate_size = []

    band_outlines = []
    header_labels = []
    j_labels = []

    for i, n in enumerate(PANEL_NS):
        bands = band_layout(i)
        vleft, vbottom, vw, vh = vessel_geometry(i)
        x_norms = x_positions_by_n[n]
        x_lo = vleft + vw * 0.10
        x_hi = vleft + vw * 0.90
        x_spread = x_hi - x_lo

        strata = strata_by_n[n]
        payloads = payload_by_n[n]

        for h in range(1, H_MAX + 1):
            band_bot, band_top = bands[h]

            # Faint band outline.
            band_outlines.append(((vleft + vw * 0.08, band_bot),
                                   (vleft + vw * 0.92, band_bot),
                                   (vleft + vw * 0.92, band_top),
                                   (vleft + vw * 0.08, band_top)))

            # Header label.
            header_labels.append(
                (vleft + vw * 0.10,
                 band_top - BAND_HEADER_PX * 0.55,
                 f'h = {h}',
                 strata[(h, 1)] if (h, 1) in strata else None,
                 h)
            )

            # Per-strip stratum lines - draw before glyphs so they sit
            # behind. One line per coefficient stratum, spaced across
            # the strip's vertical range. Line tint indicates sign (warm
            # for j odd, cool for j even).
            for j in range(1, h + 1):
                coeff_levels = strata[(h, j)]
                y_center, strip_h = jstrip_y(band_bot, band_top, h, j)
                strip_range = strip_h * 0.88
                if len(coeff_levels) == 1:
                    stratum_ys = [y_center]
                else:
                    stratum_ys = [
                        y_center
                        + (rank / (len(coeff_levels) - 1) - 0.5) * strip_range
                        for rank in range(len(coeff_levels))
                    ]
                tint = POS_A if j % 2 == 1 else NEG_A
                line_alpha = 0.10 if len(coeff_levels) == 1 else 0.16
                for sy in stratum_ys:
                    stratum_segments.append([
                        (vleft + vw * 0.10, sy),
                        (vleft + vw * 0.90, sy),
                    ])
                    stratum_colors.append((*tint, line_alpha))
                    stratum_widths.append(0.45)
                # Tiny "j=N" label at the left edge of each strip.
                j_labels.append(
                    (vleft + vw * 0.075, y_center, f'j{j}',
                     POS_A if j % 2 == 1 else NEG_A)
                )

            # Per-payload glyphs through j=1..h. (No threads - they
            # smeared the strata; the strata themselves are the visual.)
            for idx in range(len(payloads)):
                k = payloads[idx]
                overlaps, _ = decompose_payload(n, k)
                x = x_lo + x_spread * x_norms[idx]
                k_prime_value = k // n_pow_overlap(n, overlaps)

                for j in range(1, h + 1):
                    coeff = coeff_for(n, h, j, overlaps)
                    residue = tau(j, k_prime_value)
                    sign = 1 if j % 2 == 1 else -1
                    term = sign * coeff * residue / j

                    coeff_levels = strata[(h, j)]
                    if len(coeff_levels) == 1:
                        stratum_norm = 0.5
                    else:
                        rank = coeff_levels.index(coeff)
                        stratum_norm = rank / (len(coeff_levels) - 1)

                    y_center, strip_h = jstrip_y(band_bot, band_top, h, j)
                    y = y_center + (stratum_norm - 0.5) * strip_h * 0.88

                    residue_norm = log(residue + 1.0) / norms['residue']
                    term_norm = log(abs(term) + 1.0) / norms['term']

                    rgb = contribution_color(sign, residue_norm, term_norm)
                    alpha = np.clip(0.40 + 0.55 * term_norm, 0.28, 0.95)
                    size = 4.0 + 22.0 * term_norm + 8.0 * residue_norm

                    glyph_x.append(x)
                    glyph_y.append(y)
                    glyph_color.append((*rgb, alpha))
                    glyph_size.append(size)

                # Distillate dot at the bottom of the band, per payload.
                q_value = sum(
                    (1 if jj % 2 == 1 else -1)
                    * coeff_for(n, h, jj, overlaps)
                    * tau(jj, k_prime_value) / jj
                    for jj in range(1, h + 1)
                )
                q_norm = log(abs(q_value) + 1.0) / norms['q']
                q_rgb = DISTILLATE_POS if q_value >= 0 else DISTILLATE_NEG
                distillate_x.append(x)
                distillate_y.append(band_bot + BAND_DISTILLATE_PX * 0.5)
                distillate_color.append(
                    (*q_rgb * (0.62 + 0.38 * q_norm),
                     0.50 + 0.45 * q_norm)
                )
                distillate_size.append(8.0 + 38.0 * q_norm)

    # Draw outlines first.
    for vert in band_outlines:
        xs = [v[0] for v in vert] + [vert[0][0]]
        ys = [v[1] for v in vert] + [vert[0][1]]
        ax.plot(xs, ys, color=(0.40, 0.50, 0.55, 0.10), lw=0.7, zorder=1.2)

    # Vessels.
    for i, n in enumerate(PANEL_NS):
        draw_vessel_outline(ax, i, n)

    # Stratum lines (faint horizontal guides under glyphs).
    if stratum_segments:
        ax.add_collection(LineCollection(
            stratum_segments,
            colors=stratum_colors,
            linewidths=stratum_widths,
            capstyle='butt',
            antialiased=True,
            zorder=2.5,
        ))

    # Glyphs (the strata).
    if glyph_x:
        ax.scatter(
            glyph_x, glyph_y,
            s=glyph_size,
            c=glyph_color,
            marker='o',
            linewidths=0,
            zorder=5,
        )

    # Distillate dots.
    if distillate_x:
        ax.scatter(
            distillate_x, distillate_y,
            s=distillate_size,
            c=distillate_color,
            marker='o',
            linewidths=0,
            edgecolors='none',
            zorder=6,
        )

    # h-band labels.
    for x, y, txt, _strata_for_j1, h in header_labels:
        ax.text(
            x, y, txt,
            color=(1.0, 1.0, 1.0, 0.55),
            fontsize=12,
            ha='left',
            va='center',
            zorder=8,
        )

    # j-strip labels (left edge of each strip).
    for x, y, txt, tint in j_labels:
        ax.text(
            x, y, txt,
            color=(*tint, 0.55),
            fontsize=8,
            ha='right',
            va='center',
            zorder=8,
        )

    # Title (omitted - the per-vessel n labels carry the structure).

    # Legend strip at the very bottom.
    legend_y = 36
    legend_specs = [
        ('warm = positive (j odd)', POS_A),
        ('cool = negative (j even)', NEG_A),
        ('y in strip = coefficient stratum', np.array([0.85, 0.92, 1.0])),
        ('size = |term| at that layer', np.array([1.0, 0.95, 0.80])),
    ]
    legend_x = IMG_W * 0.13
    legend_step = (IMG_W * 0.74) / (len(legend_specs) - 1)
    for idx, (label, rgb) in enumerate(legend_specs):
        cx = legend_x + idx * legend_step
        ax.scatter(
            [cx - 100], [legend_y],
            s=80, c=[(*rgb, 0.85)],
            linewidths=0, zorder=10,
        )
        ax.text(
            cx - 80, legend_y, label,
            color=(0.85, 0.90, 0.95, 0.75),
            fontsize=11, ha='left', va='center', zorder=10,
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


def n_pow_overlap(n, overlaps):
    """Compute n^something giving the overlap-prime contribution to k.
    Specifically, return the product of p_i^(t_i) over factors of n."""
    factors = factor_tuple(n)
    out = 1
    for (p, _a), t in zip(factors, overlaps):
        out *= p ** t
    return out


def main():
    print('Collecting finite-rank Q layers...')
    records = collect_records()
    print(f'Rendering {len(records)} signed layers across {len(PANEL_NS)} vessels...')
    norms = normalize_logs(records)
    build_art(records, norms)
    print(f'-> {OUT}')


if __name__ == '__main__':
    main()
