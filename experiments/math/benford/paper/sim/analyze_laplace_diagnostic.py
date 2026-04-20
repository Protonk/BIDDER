"""
Analyze Mess #1 Laplace-diagnostic runs.

For SRW on ℤ:
  - Compare measured E[q^{L_n}] to closed-form prediction
    q√2 / ((1 − q)√(πn)).
  - Fit log(E[q^{L_n}]) vs log(n): slope should be −0.5.

For BS(1,2):
  - Compare measured E[q^{L_n}] to SRW prediction (BS(1,2) is in
    same universality class for null-recurrent exponent walk).
  - Check if E[q^{N_n}] also follows 1/√n.
  - Report N_n/√n distribution shape at the latest snapshot —
    compare mean/std/quantiles to arcsine(1/2) (mean 1/π, std
    √((π−2)/(2π²)) ≈ 0.244).

Run: sage -python analyze_laplace_diagnostic.py
"""

import math
import os
import numpy as np


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
LAP_DIR = os.path.join(SIM_DIR, 'laplace_diagnostic_results')


def load(name):
    path = os.path.join(LAP_DIR, f'{name}.npz')
    if not os.path.exists(path):
        print(f'missing: {path}')
        return None
    return np.load(path, allow_pickle=True)


def predicted_EqL_srw(n, q):
    """Closed-form prediction from MESSES.md §1 for SRW."""
    return q * math.sqrt(2.0) / ((1 - q) * math.sqrt(math.pi * n))


def fit_slope(log_n, log_y):
    """Linear fit y = a + b*log_n; return b (slope)."""
    x = np.asarray(log_n)
    y = np.asarray(log_y)
    ok = np.isfinite(y)
    x, y = x[ok], y[ok]
    if x.size < 2:
        return float('nan')
    n = x.size
    xb = x.mean()
    yb = y.mean()
    num = ((x - xb) * (y - yb)).sum()
    den = ((x - xb) ** 2).sum()
    return float(num / den) if den > 0 else float('nan')


def report(label, d, predict_fn=None):
    if d is None:
        return
    print(f'\n======== {label} ========')
    times = d['sample_times']
    qs = d['q_values'].tolist()
    EqL = d['EqL']
    EqN = d['EqN']
    print(f'q values: {qs}')
    print(f'sample times: {times.min()} to {times.max()}, {times.size} points\n')

    # Table of measured E[q^L] vs prediction
    print(f'{"q":>5s}  {"n":>6s}  {"E[q^L] meas":>12s}  {"E[q^L] pred":>12s}  '
          f'ratio(m/p)  {"E[q^N] meas":>12s}')
    for qi, q in enumerate(qs):
        # sparsify printing to ~7 rows per q
        step_idx = np.linspace(0, times.size - 1, 7).astype(int)
        for i in step_idx:
            n = int(times[i])
            meas = EqL[i, qi]
            pred = predict_fn(n, q) if predict_fn else float('nan')
            ratio = meas / pred if (pred > 0) else float('nan')
            measN = EqN[i, qi]
            print(f'{q:>5.2f}  {n:>6d}  {meas:>12.4e}  {pred:>12.4e}  '
                  f'{ratio:>10.3f}  {measN:>12.4e}')
        # slope fit
        # Fit on latter half of sample times (asymptotic regime)
        mid = times.size // 2
        log_n = np.log(times[mid:].astype(float))
        log_y_L = np.log(np.maximum(EqL[mid:, qi], 1e-300))
        log_y_N = np.log(np.maximum(EqN[mid:, qi], 1e-300))
        slope_L = fit_slope(log_n, log_y_L)
        slope_N = fit_slope(log_n, log_y_N)
        print(f'   >> q={q}: slope log(E[q^L]) vs log(n) = {slope_L:.3f}  '
              f'(predicted -0.5);  slope E[q^N] = {slope_N:.3f}')
        print()


def snapshot_stats(d, label, snap_time, normalize='sqrt'):
    if d is None:
        return
    L = d[f'L_snap_{snap_time}']
    N = d[f'N_snap_{snap_time}']
    norm = math.sqrt(snap_time) if normalize == 'sqrt' else 1.0
    Ln = L.astype(float) / norm
    Nn = N.astype(float) / norm
    print(f'\n--- {label}  snapshot n = {snap_time} ---')
    print(f'  L/√n:  mean={Ln.mean():.4f}  std={Ln.std():.4f}  '
          f'quantiles 0.1/0.5/0.9 = {np.quantile(Ln, 0.1):.3f} / '
          f'{np.quantile(Ln, 0.5):.3f} / {np.quantile(Ln, 0.9):.3f}')
    print(f'  N/√n:  mean={Nn.mean():.4f}  std={Nn.std():.4f}  '
          f'quantiles 0.1/0.5/0.9 = {np.quantile(Nn, 0.1):.3f} / '
          f'{np.quantile(Nn, 0.5):.3f} / {np.quantile(Nn, 0.9):.3f}')
    # P(N ≤ a) ~ C·a/√n; check the low tail
    for a in [1, 2, 5]:
        frac = float((N <= a).mean())
        pred = (a / math.sqrt(snap_time)) * (1.0 / math.sqrt(math.pi / 2))
        print(f'    P(N ≤ {a})  meas={frac:.5f}   a/√n scale ~ {pred:.5f}')


def main():
    srw = load('srw_z')
    bs = load('bs12')

    report('SRW on ℤ — E[q^L] vs prediction', srw, predicted_EqL_srw)
    # BS(1,2): no closed-form prediction (structural universality argument
    # says same 1/√n shape; show measured and compare to SRW-scaling).
    report('BS(1,2) — E[q^L] (1/√n expected structurally)', bs, None)

    # N/√n distribution
    for t in [100, 1000, 10000]:
        snapshot_stats(srw, 'SRW', t)
        snapshot_stats(bs, 'BS(1,2)', t)


if __name__ == '__main__':
    main()
