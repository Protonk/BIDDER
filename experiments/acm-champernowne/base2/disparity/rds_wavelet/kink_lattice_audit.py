"""
kink_lattice_audit.py — package the post-hoc lattice fit's stress
tests so they can be re-run.

The lattice reading in an earlier draft of KINK-INVESTIGATION.md said
the n=3 low-band gap distribution lives on a 3-rung arithmetic lattice
with click `b ≈ 951` and offset `a ≈ 519`, fit residuals `≤ 0.54 %`
of click. The current draft demotes that to a "post-hoc fit
(diagnostic only)" because the fit is not stable under either
modest KDE bandwidth changes or bootstrap resampling of the same
gap sample. This script is the committed form of those audit
calculations, so the bandwidth-instability table and the bootstrap
stats in §Numerical evidence and §D can be reproduced from one
command rather than reread as a one-shot audit run.

What it does, given a gap CSV with `gap_index,delta_t` rows:

  1. Bandwidth sweep: for each `bw_method` in
     {0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.15, scott, silverman},
     run the same `gaussian_kde + find_peaks(prominence ≥ 3% of max)`
     mode finder used by kink_decompression_n3.py, sort the modes,
     OLS-fit a 2-parameter `Δt = a + n·b` line on the first three
     sorted modes, and print (mode_count, first three modes, fitted
     b, max |residual| as % of b).

  2. Bootstrap of the lattice fit at fixed bw=0.10. Resample the
     committed gap sample with replacement N_BOOT times, run the
     same KDE + sort + first-3-mode fit each time, and report:
       - distribution of mode counts
       - mean, std, percentiles of fitted b
       - fraction of resamples with max-residual ≤ a target threshold
         (default 0.54 %, the value the original draft cited).

  3. Grid resolution note: the script also prints the spacing of the
     KDE grid (`(max(gaps) - min(gaps)) / 1199`), so the relationship
     between the cited "5.15-bit residual" and the grid step is
     visible at the top of the audit log.

Usage:

    sage kink_lattice_audit.py kink_gaps_lowband_1M_kde2.csv
    sage kink_lattice_audit.py kink_gaps_lowband_1M_kde2.csv --n-boot 1000 --seed 42

The defaults `--n-boot 300 --seed 20260408` reproduce the numbers
cited in KINK-INVESTIGATION.md §Numerical evidence and §D.
"""

import argparse
import os
import sys
import numpy as np
from scipy import stats as scipy_stats
from scipy.signal import find_peaks


# ── KDE configuration must match kink_decompression_n3.py ──────────

KDE_GRID_SIZE = 1200
KDE_PROMINENCE_FRAC = 0.03
DEFAULT_BW = 0.10


def find_modes(gaps, bw_method):
    """Run gaussian_kde + find_peaks on a 1D gap sample.

    Returns the sorted array of mode locations (mode positions on the
    fixed `[gaps.min(), gaps.max()]` grid). Empty array if KDE failed
    or no modes meet the prominence floor.
    """
    if len(gaps) < 4:
        return np.array([])
    try:
        kde = scipy_stats.gaussian_kde(gaps, bw_method=bw_method)
    except Exception:
        return np.array([])
    grid = np.linspace(gaps.min(), gaps.max(), KDE_GRID_SIZE)
    density = kde(grid)
    if density.max() <= 0:
        return np.array([])
    idx, _ = find_peaks(density,
                        prominence=density.max() * KDE_PROMINENCE_FRAC)
    return np.sort(grid[idx])


def lattice_fit_first3(modes):
    """Fit Δt = a + n·b on the first three sorted modes (n = 0, 1, 2).

    Returns (a, b, max_resid, max_resid_pct). If fewer than 3 modes,
    returns (nan, nan, nan, nan).
    """
    if len(modes) < 3:
        return float('nan'), float('nan'), float('nan'), float('nan')
    L = modes[:3].astype(np.float64)
    n = np.array([0.0, 1.0, 2.0])
    b, a = np.polyfit(n, L, 1)
    pred = a + n * b
    resid = L - pred
    max_resid = float(np.max(np.abs(resid)))
    max_resid_pct = 100.0 * max_resid / b if b != 0 else float('nan')
    return float(a), float(b), max_resid, max_resid_pct


def main():
    p = argparse.ArgumentParser(
        description='Bandwidth sweep + bootstrap audit of the kink '
                    'lattice fit (KINK-INVESTIGATION.md §D).')
    p.add_argument('csv_path',
                   help='gap CSV (gap_index,delta_t header)')
    p.add_argument('--n-boot', type=int, default=300,
                   help='number of bootstrap resamples (default 300)')
    p.add_argument('--seed', type=int, default=20260408,
                   help='RNG seed for the bootstrap (default 20260408)')
    p.add_argument('--threshold-pct', type=float, default=0.54,
                   help='target lattice-fit tightness as %% of b '
                        '(default 0.54, the originally cited value)')
    p.add_argument('--save-csv', action='store_true',
                   help='write a per-resample bootstrap CSV next to '
                        'the input')
    args = p.parse_args()

    # Load the gap sample
    raw = np.loadtxt(args.csv_path, delimiter=',', skiprows=1)
    gaps = raw[:, 1].astype(np.float64)
    K = len(gaps)
    print(f"Loaded {K} gaps from {args.csv_path}")
    print(f"  min={gaps.min():.0f}  max={gaps.max():.0f}  "
          f"mean={gaps.mean():.1f}  std={gaps.std(ddof=1):.1f}")

    grid_step = (gaps.max() - gaps.min()) / (KDE_GRID_SIZE - 1)
    print(f"  KDE grid: {KDE_GRID_SIZE} points across "
          f"[{gaps.min():.0f}, {gaps.max():.0f}]  →  "
          f"step ≈ {grid_step:.2f} bits per cell")
    print(f"  (any cited mode-position residual smaller than ~"
          f"{grid_step:.1f} bits is at the grid resolution)")

    # ── 1. Bandwidth sweep ─────────────────────────────────────────

    print("\n=== Bandwidth sweep ===")
    print(f"  prominence threshold = {KDE_PROMINENCE_FRAC*100:.1f}% "
          f"of max density (matches kink_decompression_n3.py)\n")
    header = (f"  {'bw':>10}  {'#modes':>7}  "
              f"{'first three modes':>30}  "
              f"{'fitted b':>10}  {'max |r| / b':>12}")
    print(header)
    print("  " + "-" * (len(header) - 2))

    bw_list = [0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.15,
               'scott', 'silverman']
    for bw in bw_list:
        modes = find_modes(gaps, bw)
        if len(modes) >= 3:
            a, b, _, mr_pct = lattice_fit_first3(modes)
            first3 = ', '.join(f'{m:6.0f}' for m in modes[:3])
            b_str = f'{b:9.1f}'
            mr_str = f'{mr_pct:10.2f} %'
        elif len(modes) > 0:
            first3 = ', '.join(f'{m:6.0f}' for m in modes)
            b_str = '       —'
            mr_str = '          —'
        else:
            first3 = '(none)'
            b_str = '       —'
            mr_str = '          —'
        bw_label = f'{bw:>10}' if isinstance(bw, str) \
            else f'{bw:10.3f}'
        print(f"  {bw_label}  {len(modes):>7d}  "
              f"{first3:>30}  {b_str:>10}  {mr_str:>12}")

    # ── 2. Bootstrap at bw=0.10 ────────────────────────────────────

    print(f"\n=== Bootstrap of first-3-mode lattice fit "
          f"at bw={DEFAULT_BW} ===")
    print(f"  N_BOOT = {args.n_boot}  seed = {args.seed}\n")

    rng = np.random.default_rng(args.seed)

    mode_counts = np.zeros(args.n_boot, dtype=int)
    fitted_b    = np.full(args.n_boot, np.nan)
    fitted_a    = np.full(args.n_boot, np.nan)
    max_resid_pct = np.full(args.n_boot, np.nan)
    has_3_modes = np.zeros(args.n_boot, dtype=bool)

    for i in range(args.n_boot):
        sample = rng.choice(gaps, size=K, replace=True)
        modes = find_modes(sample, DEFAULT_BW)
        mode_counts[i] = len(modes)
        if len(modes) >= 3:
            has_3_modes[i] = True
            a, b, _, mr_pct = lattice_fit_first3(modes)
            fitted_a[i] = a
            fitted_b[i] = b
            max_resid_pct[i] = mr_pct

    n_valid = int(has_3_modes.sum())
    print(f"  resamples with ≥ 3 modes: {n_valid}/{args.n_boot} "
          f"({100*n_valid/args.n_boot:.1f}%)")
    print(f"  mode count distribution:")
    unique, counts = np.unique(mode_counts, return_counts=True)
    for u, c in zip(unique, counts):
        bar = '#' * int(60 * c / args.n_boot)
        print(f"    {u:>2d} modes: {c:>4d}  {bar}")
    print(f"  mode count range: [{mode_counts.min()}, "
          f"{mode_counts.max()}]")

    if n_valid > 0:
        b_valid = fitted_b[has_3_modes]
        a_valid = fitted_a[has_3_modes]
        mr_valid = max_resid_pct[has_3_modes]
        print(f"\n  fitted b (over {n_valid} valid resamples):")
        print(f"    mean   = {b_valid.mean():8.2f} bits")
        print(f"    std    = {b_valid.std(ddof=1):8.2f} bits")
        print(f"    min    = {b_valid.min():8.2f} bits")
        print(f"    p5     = {np.percentile(b_valid, 5):8.2f} bits")
        print(f"    p25    = {np.percentile(b_valid, 25):8.2f} bits")
        print(f"    median = {np.median(b_valid):8.2f} bits")
        print(f"    p75    = {np.percentile(b_valid, 75):8.2f} bits")
        print(f"    p95    = {np.percentile(b_valid, 95):8.2f} bits")
        print(f"    max    = {b_valid.max():8.2f} bits")
        print(f"\n  fitted a (over {n_valid} valid resamples):")
        print(f"    mean   = {a_valid.mean():8.2f} bits")
        print(f"    std    = {a_valid.std(ddof=1):8.2f} bits")
        print(f"\n  max-residual / b distribution "
              f"(over {n_valid} valid resamples):")
        print(f"    mean   = {mr_valid.mean():.3f} %")
        print(f"    median = {np.median(mr_valid):.3f} %")
        print(f"    min    = {mr_valid.min():.3f} %")
        print(f"    p25    = {np.percentile(mr_valid, 25):.3f} %")
        print(f"    p75    = {np.percentile(mr_valid, 75):.3f} %")
        print(f"    max    = {mr_valid.max():.3f} %")

        n_under_threshold = int(np.sum(mr_valid <= args.threshold_pct))
        print(f"\n  resamples with max |r|/b ≤ {args.threshold_pct} %:"
              f"  {n_under_threshold}/{args.n_boot}  "
              f"({100*n_under_threshold/args.n_boot:.1f}%)")
        print(f"  (the original draft cited 0.54 % for the committed "
              f"sample; this column says how often a same-bw bootstrap "
              f"matches that.)")

    # ── 3. Optional CSV dump ───────────────────────────────────────

    if args.save_csv:
        here = os.path.dirname(os.path.abspath(args.csv_path))
        out = os.path.join(here, 'kink_lattice_audit_bootstrap.csv')
        with open(out, 'w') as f:
            f.write('resample_index,n_modes,a,b,max_resid_pct\n')
            for i in range(args.n_boot):
                f.write(f'{i},{mode_counts[i]},'
                        f'{fitted_a[i] if has_3_modes[i] else ""},'
                        f'{fitted_b[i] if has_3_modes[i] else ""},'
                        f'{max_resid_pct[i] if has_3_modes[i] else ""}\n')
        print(f"\n  bootstrap CSV: {out}")


if __name__ == '__main__':
    main()
