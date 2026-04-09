"""
t1_white_noise_control.py — run the kink_decompression_n3 pipeline on
white-noise control streams instead of the n=3 ACM stream.

This is the test KINK-INVESTIGATION.md flags as T1 in §Falsification tests:
"the strongest alternative explanation and the one I would attack
first" — namely the worry that the three-mode lattice in the n=3
band-averaged Morlet notch indicator is a wavelet/detector artifact
rather than a property of the n=3 stream.

The script generates an iid control stream, fixes a fair linear
detrend, runs the same in-band Morlet CWT used by
kink_decompression_n3.py (only the rows in the kink band — the
non-band rows do not enter the notch indicator anyway, so this is a
faithful subset), builds the same notch indicator with the same
smoothing, runs the same scipy find_peaks with the same parameters,
applies the same edge trim and t-fit cutoff, then prints the same
gap-distribution diagnostics and the same KDE-mode + lattice-fit
output that kink_decompression_n3.py prints. The two log blocks line
up row-for-row so they can be compared by eye.

Two stream types are supported:

  --stream rw     Bernoulli random walk: cumsum(2·b - 1) for b ∈ {0,1}
                  This is the closest white analogue to a detrended
                  binary RDS — same {-1, +1} increment alphabet, same
                  cumulative integration step.
  --stream gauss  Gaussian iid: x_t ~ Normal(0, 1)
                  This is the doc's first-listed T1 option.

The default panel of seeds (1, 2, 3, 4) was chosen so that the result
table in KINK-INVESTIGATION.md §Sanity check is reproducible by running

    sage t1_white_noise_control.py --stream rw    --seed 1
    sage t1_white_noise_control.py --stream rw    --seed 2
    sage t1_white_noise_control.py --stream rw    --seed 3
    sage t1_white_noise_control.py --stream rw    --seed 4
    sage t1_white_noise_control.py --stream gauss --seed 1
    sage t1_white_noise_control.py --stream gauss --seed 2

This script does NOT save figures or CSVs by default; the point is the
diagnostic numbers, not the artifacts. Pass --save-csv to dump the
gap sequence next to the same _t1_<stream>_seed<k>.csv suffix.
"""

import os
import sys
import math
import argparse
import numpy as np
from scipy.signal import fftconvolve, find_peaks
from scipy.ndimage import uniform_filter1d
from scipy import stats as scipy_stats


# ── Parameters (must match kink_decompression_n3.py for the lowband
#    1M run) ─────────────────────────────────────────────────────────

TARGET_BITS  = 1_000_000
N_SCALES     = 120
SCALE_MIN    = 2.0
SCALE_MAX    = 50_000.0
W0           = 6.0
KINK_LO      = 500.0
KINK_HI      = 2000.0
SMOOTH       = 20
PROMINENCE   = 0.02
DISTANCE     = 10
EDGE_PAD     = 1000
T_FIT_MIN    = 3000


# ── CLI ───────────────────────────────────────────────────────────

p = argparse.ArgumentParser(
    description='T1 white-noise sanity control for KINK-INVESTIGATION.md')
p.add_argument('--stream', choices=['rw', 'gauss'], default='rw',
               help='control stream type (default rw)')
p.add_argument('--seed', type=int, default=1,
               help='RNG seed (default 1)')
p.add_argument('--target-bits', type=int, default=TARGET_BITS)
p.add_argument('--save-csv', action='store_true',
               help='dump the gap sequence as a CSV next to this script')
args = p.parse_args()

print(f"T1 control: stream={args.stream}  seed={args.seed}  "
      f"target_bits={args.target_bits}")
print(f"  band=[{KINK_LO:.0f}, {KINK_HI:.0f}]  smooth={SMOOTH}  "
      f"prominence={PROMINENCE}  distance={DISTANCE}  edge_pad={EDGE_PAD}")


# ── Build the control stream ──────────────────────────────────────

rng = np.random.default_rng(args.seed)
if args.stream == 'rw':
    bits = rng.integers(0, 2, size=args.target_bits, dtype=np.int8)
    pm   = 2 * bits.astype(np.int64) - 1
    rds  = np.concatenate(([0], np.cumsum(pm))).astype(np.float64)
else:
    rds = rng.standard_normal(args.target_bits).astype(np.float64)

x_axis = np.arange(len(rds), dtype=np.float64)
slope, icpt = np.polyfit(x_axis, rds, 1)
rds_dt = rds - (slope * x_axis + icpt)
n_bits = len(rds_dt)
print(f"  control stream length: {n_bits}")


# ── In-band Morlet CWT ────────────────────────────────────────────
#
# Mirrors kink_decompression_n3.py:
#   - 120 log-spaced scales in [2, 50000]
#   - keep only rows in [KINK_LO, KINK_HI]   (this is what the band
#     mask in kink_decompression_n3.py does)
#   - same Morlet kernel, same w0=6, same fftconvolve path

scales = np.geomspace(SCALE_MIN, SCALE_MAX, N_SCALES)
band_mask = (scales >= KINK_LO) & (scales <= KINK_HI)
band_scales = scales[band_mask]
print(f"  scale-band rows kept: {band_mask.sum()} of {N_SCALES}")


def morlet_kernel(n_pts, s, w0=W0):
    t = (np.arange(n_pts) - (n_pts - 1) / 2.0) / s
    norm = (np.pi ** -0.25) / np.sqrt(s)
    return norm * np.exp(1j * w0 * t) * np.exp(-t * t / 2.0)


log_band_sum = np.zeros(n_bits, dtype=np.float64)
for s in band_scales:
    n_pts = min(int(10 * s), n_bits)
    if n_pts < 5:
        n_pts = 5
    if n_pts % 2 == 0:
        n_pts += 1
    w  = morlet_kernel(n_pts, s)
    re = fftconvolve(rds_dt, w.real, mode='same')
    im = fftconvolve(rds_dt, w.imag, mode='same')
    log_band_sum += np.log10(re * re + im * im + 1e-12)
log_band = log_band_sum / len(band_scales)


# ── Notch indicator + peak extraction ─────────────────────────────

notch_raw    = -(log_band - log_band.mean())
notch_smooth = uniform_filter1d(notch_raw, size=SMOOTH)

peaks, _ = find_peaks(notch_smooth,
                      prominence=PROMINENCE,
                      distance=DISTANCE)
keep_edges = (peaks >= EDGE_PAD) & (peaks < n_bits - EDGE_PAD)
peaks_kept = peaks[keep_edges]
print(f"  raw peaks: {len(peaks)}  after edge trim: {len(peaks_kept)}")

peaks_fit = peaks_kept[peaks_kept >= T_FIT_MIN].astype(np.float64)
gaps = np.diff(peaks_fit)
n_gaps = len(gaps)
if n_gaps < 30:
    print(f"  WARNING: only {n_gaps} gaps; control panel needs >= 30")
    sys.exit(0)


# ── Same diagnostics as kink_decompression_n3.py ──────────────────

gap_mean = float(np.mean(gaps))
gap_std  = float(np.std(gaps, ddof=1))
gap_skew = float(scipy_stats.skew(gaps))
gap_kurt = float(scipy_stats.kurtosis(gaps))
gap_acf1 = float(np.corrcoef(gaps[:-1], gaps[1:])[0, 1])
print(f"\nGap diagnostics:")
print(f"  count        = {n_gaps}")
print(f"  mean         = {gap_mean:.1f} bits")
print(f"  std          = {gap_std:.1f} bits  (CV = {gap_std/gap_mean:.3f})")
print(f"  skewness     = {gap_skew:+.3f}")
print(f"  excess kurt  = {gap_kurt:+.3f}")
print(f"  lag-1 ACF    = {gap_acf1:+.3f}")

gauss_cdf = lambda x: scipy_stats.norm.cdf(x, loc=gap_mean, scale=gap_std)
ks_g = scipy_stats.kstest(gaps, gauss_cdf)
print(f"  KS vs Normal: D = {ks_g.statistic:.4f}, p = {ks_g.pvalue:.3e}")

bw = 0.10
kde = scipy_stats.gaussian_kde(gaps, bw_method=bw)
grid = np.linspace(gaps.min(), gaps.max(), 1200)
density = kde(grid)
mode_idx, _ = find_peaks(density, prominence=density.max() * 0.03)
mode_locations = grid[mode_idx]
mode_heights = density[mode_idx] / density.max()
print(f"  KDE (bw_method={bw}) modes: {len(mode_locations)} mode(s)")
for loc, h in zip(mode_locations, mode_heights):
    local_window = max(50, int(0.05 * (gaps.max() - gaps.min())))
    n_in_window = int(np.sum(np.abs(gaps - loc) <= local_window))
    print(f"    at Δt = {loc:6.0f} bits   "
          f"(rel height {h:.3f}, "
          f"~{n_in_window} gaps within ±{local_window})")

if len(mode_locations) >= 3:
    L = np.sort(mode_locations)[:3].astype(np.float64)
    n_lat = np.array([0.0, 1.0, 2.0])
    b_lat, a_lat = np.polyfit(n_lat, L, 1)
    max_resid = float(np.max(np.abs(L - (a_lat + n_lat * b_lat))))
    print(f"\n  Lattice fit on first 3 KDE modes (control):")
    print(f"    a = {a_lat:.2f}  b = {b_lat:.2f}  "
          f"max |resid| = {max_resid:.2f} ({100*max_resid/b_lat:.2f}% of b)")
    sorted_locs = np.sort(mode_locations)
    for k in range(min(4, len(sorted_locs))):
        pred = a_lat + k * b_lat
        obs  = float(sorted_locs[k])
        resid = obs - pred
        tag = "fit" if k < 3 else "extrap"
        print(f"      n={k} ({tag:6s}): pred={pred:8.1f}  "
              f"obs={obs:8.1f}  resid={resid:+7.2f}")

if args.save_csv:
    here = os.path.dirname(os.path.abspath(__file__))
    csv_out = os.path.join(
        here, f"kink_gaps_t1_{args.stream}_seed{args.seed}.csv")
    with open(csv_out, 'w') as f:
        f.write('gap_index,delta_t\n')
        for i, g in enumerate(gaps):
            f.write(f'{i},{g}\n')
    print(f"\n  gap CSV: {csv_out}")
