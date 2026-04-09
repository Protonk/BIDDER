"""
dfa_kink_n3.py — detrended fluctuation analysis on the kink gap
sequence Δt_k.

Loads a gap CSV produced by kink_decompression_n3.py, treats Δt_k as
a 1D time series, and runs DFA on its cumulative integrated profile.

DFA reports the scaling exponent H of the RMS detrended fluctuation
function F(N) ~ N^H, where:

  H ≈ 0.5  → uncorrelated (white) gaps
  H > 0.5  → persistent (long-range positive correlation)
  H < 0.5  → anti-persistent (long-range negative correlation)
  H ≈ 1    → 1/f noise
  H ≈ 1.5  → integrated white noise (Brownian)

A *single* clean slope on log-log axes is the signature of a single
scaling regime — fully summarizable by one exponent. A *break* (two
distinct slopes joined at a characteristic scale) is the signature
of multi-regime / fractal-aperiodic structure: at small windows the
process behaves one way, at large windows another, and no single
exponent describes both.

The CSV path is the only required positional argument.
"""

import sys
import os
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def dfa(profile, window_sizes, order=1):
    """Standard detrended fluctuation analysis.

    profile      : the integrated 'profile' Y(k) = cumsum(x − mean(x))
    window_sizes : iterable of window sizes N (integers)
    order        : polynomial detrend order (1 = linear)

    Returns (window_sizes_used, F_values) — F(N) = RMS over all
    non-overlapping windows of the residual after polynomial detrend.
    """
    N_total = len(profile)
    Ns = []
    Fs = []
    for N in window_sizes:
        N = int(N)
        if N < order + 2 or N > N_total // 2:
            continue
        n_windows = N_total // N
        if n_windows < 2:
            continue
        squared_residuals = []
        for i in range(n_windows):
            seg = profile[i * N:(i + 1) * N]
            x = np.arange(N, dtype=np.float64)
            coefs = np.polyfit(x, seg, order)
            trend = np.polyval(coefs, x)
            resid = seg - trend
            squared_residuals.append(np.mean(resid ** 2))
        F = math.sqrt(float(np.mean(squared_residuals)))
        Ns.append(N)
        Fs.append(F)
    return np.array(Ns, dtype=np.float64), np.array(Fs, dtype=np.float64)


def main():
    if len(sys.argv) < 2:
        print("usage: dfa_kink_n3.py <gap_csv> [out_suffix]")
        sys.exit(1)

    csv_path = sys.argv[1]
    suffix = sys.argv[2] if len(sys.argv) >= 3 else ''

    # Load CSV (header: gap_index,delta_t)
    raw = np.loadtxt(csv_path, delimiter=',', skiprows=1)
    gaps = raw[:, 1].astype(np.float64)
    K = len(gaps)
    print(f"Loaded {K} gaps from {csv_path}")
    print(f"  mean = {gaps.mean():.1f}  std = {gaps.std(ddof=1):.1f}")

    # Build the DFA profile: cumulative integrated centered series
    profile = np.cumsum(gaps - gaps.mean())

    # Log-spaced window sizes from 4 up to K // 4
    N_min = 4
    N_max = max(N_min + 1, K // 4)
    n_windows = 24
    window_sizes = np.unique(
        np.round(np.geomspace(N_min, N_max, n_windows)).astype(int)
    )

    Ns, Fs = dfa(profile, window_sizes, order=1)
    print(f"\nDFA computed at {len(Ns)} window sizes "
          f"in [{int(Ns.min())}, {int(Ns.max())}]")

    log_N = np.log10(Ns)
    log_F = np.log10(Fs)

    # Single global slope
    slope_global, intercept_global = np.polyfit(log_N, log_F, 1)
    print(f"\nSingle-regime fit:")
    print(f"  H_global = {slope_global:.4f}  "
          f"(intercept = {intercept_global:.3f})")

    # Two-regime fit by trying every possible break point
    best_break = None
    best_total_rss = float('inf')
    best_H1 = best_H2 = None
    if len(Ns) >= 6:
        for split in range(3, len(Ns) - 2):
            x1, y1 = log_N[:split], log_F[:split]
            x2, y2 = log_N[split:], log_F[split:]
            s1, i1 = np.polyfit(x1, y1, 1)
            s2, i2 = np.polyfit(x2, y2, 1)
            r1 = y1 - (i1 + s1 * x1)
            r2 = y2 - (i2 + s2 * x2)
            total_rss = float(np.sum(r1 ** 2) + np.sum(r2 ** 2))
            if total_rss < best_total_rss:
                best_total_rss = total_rss
                best_break = split
                best_H1 = float(s1)
                best_H2 = float(s2)
                best_i1 = float(i1)
                best_i2 = float(i2)

        rss_global = float(
            np.sum((log_F - (intercept_global + slope_global * log_N)) ** 2)
        )
        improvement = rss_global / best_total_rss if best_total_rss > 0 else float('inf')
        N_break = float(10 ** log_N[best_break])

        print(f"\nTwo-regime fit (best break at index {best_break}):")
        print(f"  H1 (small N, N < {N_break:.0f}) = {best_H1:.4f}")
        print(f"  H2 (large N, N ≥ {N_break:.0f}) = {best_H2:.4f}")
        print(f"  RSS_single = {rss_global:.5f}")
        print(f"  RSS_two    = {best_total_rss:.5f}")
        print(f"  improvement factor = {improvement:.2f}×")

    # Render figure
    here = os.path.dirname(os.path.abspath(csv_path))
    out_png = os.path.join(here, f'dfa_kink_n3{suffix}.png')

    DARK = '#0a0a0a'
    WHITE = 'white'
    ACCENT = '#ffcc5c'
    SIGNAL = '#6ec6ff'
    GUIDE = '#88d8b0'
    GEOM = '#ff6f61'

    fig, ax = plt.subplots(figsize=(10, 8), facecolor=DARK)
    ax.set_facecolor(DARK)

    ax.loglog(Ns, Fs, 'o', color=ACCENT, markersize=7,
              label=f'F(N) DFA-1, K = {K}')

    # Single global fit
    fit_line = 10 ** (intercept_global + slope_global * log_N)
    ax.loglog(Ns, fit_line, color=SIGNAL, lw=1.5,
              label=f'single slope H = {slope_global:.3f}')

    # Reference lines
    H_white = 0.5
    ref_white = 10 ** (intercept_global + H_white * (log_N - log_N.mean())
                       + slope_global * log_N.mean())
    # Plot reference H=0.5 line, anchored at midpoint of data
    mid_x = log_N[len(log_N) // 2]
    mid_y = log_F[len(log_F) // 2]
    ax.loglog(Ns, 10 ** (mid_y + H_white * (log_N - mid_x)),
              color=GUIDE, lw=0.9, ls='--',
              label='reference H = 0.5 (white)')

    # Two-regime fit
    if best_break is not None and (improvement > 1.05 or len(Ns) >= 8):
        x1 = log_N[:best_break]
        x2 = log_N[best_break:]
        ax.loglog(10 ** x1, 10 ** (best_i1 + best_H1 * x1),
                  color=GEOM, lw=1.4, ls='-',
                  label=f'small-N: H1 = {best_H1:.3f}')
        ax.loglog(10 ** x2, 10 ** (best_i2 + best_H2 * x2),
                  color=GEOM, lw=1.4, ls='-',
                  label=f'large-N: H2 = {best_H2:.3f}')
        ax.axvline(10 ** log_N[best_break], color=WHITE,
                   lw=0.8, ls=':', alpha=0.7,
                   label=f'break at N ≈ {N_break:.0f}')

    ax.set_xlabel('window size  N  (gap indices)',
                  color=WHITE, fontsize=12)
    ax.set_ylabel('F(N) — RMS detrended fluctuation',
                  color=WHITE, fontsize=12)
    ax.set_title(
        f'DFA of kink gap sequence  '
        f'(K = {K}, single H = {slope_global:.3f})',
        color=WHITE, fontsize=13)
    ax.tick_params(colors=WHITE)
    ax.legend(loc='upper left', fontsize=9, framealpha=0.0,
              labelcolor=WHITE)
    for sp in ax.spines.values():
        sp.set_color(WHITE)
    ax.grid(True, which='both', alpha=0.15, color=WHITE)

    plt.tight_layout()
    plt.savefig(out_png, dpi=160, facecolor=DARK)
    plt.close()
    print(f"\n  -> {out_png}")


if __name__ == '__main__':
    main()
