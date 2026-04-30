"""
exp01_olofsson_transplant.py — first experiment from BEURLING.md.

Goal: test whether the Olofsson rigidity template for Beurling primes
   "pole of order n at s = 0  ⇔  |N(x) - [x]| not o((log x)^n)"
transplants to the non-UF M_n monoid.

Phase A — Literal transplant (predicted to be null).
    Compute zeta_{M_n}(s) at s = 0, on the line Re s = 0, and look for
    poles. Compute the set-count deviation N_{M_n}(x) - x/n.
    Expectation: zeta_{M_n}(0) = 1/2 (regular), no pole at s = 0, and
    |N_{M_n}(x) - x/n| ≤ 1 trivially. The Olofsson template's input
    (a pole at s=0) is absent and its output (an arithmetic obstruction)
    is empty. Literal transplant: null.

Phase B — Pivot to the signed Mangoldt analog.
    The structurally interesting object is the signed log-measure of
    zeta_{M_n}, captured in BIDDER as Q_n. Define

        psi_{M_n}(x) := sum_{m in M_n, m <= x} Q_n(m) log m,

    the BIDDER analog of the Chebyshev function. By the residue
    calculation in BEURLING.md, the Mellin transform -zeta'_{M_n}/zeta_{M_n}
    has a simple pole at s = 1 with residue +1, so under
    Wiener-Ikehara-style assumptions

        psi_{M_n}(x)  ~  x   as  x -> infinity.

    Crucially, this prediction is for a *signed* sum: positive
    contributions from low-overlap (n^1 k) terms and negative
    contributions from high-overlap (n^h k) kernel-broken cells.
    Whether the convergence to 1 holds (and at what rate) is the
    BIDDER PNT analog.

Phase C — Plots.
    1. |zeta_{M_n}(0 + it)| vs t, n in {2, 3, 5, 6, 10}.
       Looks for boundary structure on Re s = 0.
    2. psi_{M_n}(x) / x  vs  x for the same n. Tests the residue-1
       prediction empirically.
    3. The signed cumulative sum psi_{M_n}(x) - x as a residual.

Outputs:
    exp01_zeta_boundary_re0.png
    exp01_psi_convergence.png
    exp01_psi_residual.png
    exp01_findings.txt   (machine-readable summary)
"""

from __future__ import annotations

import os
import sys
import time
from math import log

import numpy as np
import mpmath
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from zeta_mn import zeta_mn, log_zeta_mn, psi_mn, n_mn

OUT_BOUNDARY = os.path.join(HERE, 'exp01_zeta_boundary_re0.png')
OUT_PSI_RATIO = os.path.join(HERE, 'exp01_psi_convergence.png')
OUT_PSI_RESIDUAL = os.path.join(HERE, 'exp01_psi_residual.png')
OUT_FINDINGS = os.path.join(HERE, 'exp01_findings.txt')

NS = (2, 3, 5, 6, 10)
PSI_X_MAX = 50000     # how far to push psi_{M_n} cumulation
PSI_SAMPLES = 200     # number of x-points to record on log scale
T_MAX = 60            # imaginary range for boundary plots
T_POINTS = 1200


# --------------------------------------------------------------------------
# Phase A: literal Olofsson transplant
# --------------------------------------------------------------------------

def phase_a_summary():
    """Confirm the literal transplant is null."""
    lines = []
    lines.append('=== Phase A: literal Olofsson transplant ===')
    lines.append('')
    lines.append('Olofsson Prop 3.3 needs a pole of zeta_P at s=0.')
    lines.append('For M_n, zeta_{M_n}(0) = 1 + n^0 * zeta(0) = 1 + (-1/2) = 1/2.')
    lines.append('This is regular: no pole at s = 0. Template input absent.')
    lines.append('')
    lines.append('Set-count deviation:')
    lines.append('  N_{M_n}(x) = 1 + floor(x/n)')
    lines.append('  R(x) := N_{M_n}(x) - x/n - 1 + 1/n  is bounded in [0, 1].')
    lines.append('Template output absent (R is trivially o(1), let alone o((log x)^k)).')
    lines.append('')
    lines.append('Spot-checks:')
    for n in NS:
        z0 = float(zeta_mn(n, mpmath.mpf('0')).real)
        max_dev = 0.0
        for x in (10, 100, 1000, 10000):
            r = n_mn(n, x) - x / n
            if abs(r) > max_dev:
                max_dev = abs(r)
        lines.append(f'  n={n:>3}  zeta_{{M_n}}(0) = {z0:.6f}   '
                     f'max |R(x)| over x in 10..10000 = {max_dev:.4f}')
    lines.append('')
    lines.append('Conclusion: literal transplant null, as expected from BEURLING.md.')
    lines.append('Move to Phase B.')
    return '\n'.join(lines)


# --------------------------------------------------------------------------
# Phase B: signed Mangoldt analog
# --------------------------------------------------------------------------

def compute_psi_curve(n, x_max, sample_points):
    """Cumulative signed Mangoldt sum, sampled on log-spaced x.

    Returns (xs, psis) where psis[i] = psi_{M_n}(xs[i]).
    """
    # Sample x on log spacing.
    xs = np.unique(np.round(np.geomspace(2 * n, x_max, sample_points)).astype(int))
    psis = []
    # Cumulate by walking through j = 1..floor(x_max / n) once.
    j_max = x_max // n
    cum = 0.0
    psi_at_x = {}
    next_idx = 0
    next_x = xs[0]
    for j in range(1, j_max + 1):
        m = j * n
        if m > x_max:
            break
        from predict_q import q_general
        q = float(q_general(n, 1, j))
        if q != 0:
            cum += q * log(m)
        # Record any sampled x that is now reached.
        while next_idx < len(xs) and xs[next_idx] < m:
            psi_at_x[int(xs[next_idx])] = cum  # value at xs[next_idx] = previous cum, but...
            # Actually: psi(x) = sum over m <= x. So at x just below m, the sum
            # excludes the current term. Record cumulative *before* adding.
            next_idx += 1
            if next_idx >= len(xs):
                break
            next_x = xs[next_idx]
        if next_idx >= len(xs):
            break
    # Fill any tail: psi(x) for x >= last m in loop
    while next_idx < len(xs):
        psi_at_x[int(xs[next_idx])] = cum
        next_idx += 1
    # Now produce sorted (xs, psis) arrays.
    xs_out = np.array(sorted(psi_at_x.keys()))
    psis_out = np.array([psi_at_x[int(x)] for x in xs_out])
    return xs_out, psis_out


def phase_b_psi(x_max=PSI_X_MAX):
    """Compute psi_{M_n}(x) curves for each n; return summary lines + curves."""
    lines = []
    lines.append('=== Phase B: signed Mangoldt analog ===')
    lines.append('')
    lines.append('Predicted leading rate: psi_{M_n}(x) ~ x, since the residue')
    lines.append('of -zeta\'_{M_n}(s)/zeta_{M_n}(s) at s=1 is +1 (independent of n).')
    lines.append('')
    lines.append(f'Computing psi_{{M_n}}(x) for x in [..{x_max}], n in {NS}.')
    lines.append('')
    lines.append('Final psi/x ratios (closer to 1 = better PNT-analog):')
    curves = {}
    for n in NS:
        t0 = time.time()
        xs, psis = compute_psi_curve(n, x_max, PSI_SAMPLES)
        elapsed = time.time() - t0
        ratio = psis[-1] / xs[-1] if len(xs) > 0 else float('nan')
        lines.append(f'  n={n:>3}  psi/x at x={xs[-1]:>6} = {ratio:+.4f}   '
                     f'({elapsed:.1f}s)')
        curves[n] = (xs, psis)
    return '\n'.join(lines), curves


# --------------------------------------------------------------------------
# Phase C: plots
# --------------------------------------------------------------------------

def plot_boundary(out_path):
    """|zeta_{M_n}(0 + it)| vs t for various n."""
    fig, ax = plt.subplots(1, 1, figsize=(11, 6), dpi=140)

    ts = np.linspace(0.05, T_MAX, T_POINTS)
    cmap = plt.get_cmap('viridis')
    for i, n in enumerate(NS):
        vals = []
        for t in ts:
            z = zeta_mn(n, mpmath.mpc(0, t))
            vals.append(float(abs(z)))
        ax.plot(ts, vals, color=cmap(i / max(1, len(NS) - 1)),
                label=f'n = {n}', linewidth=1.2, alpha=0.85)

    # Reference: |zeta(it)| (Riemann zeta on critical-line-shifted)
    ref = [float(abs(mpmath.zeta(mpmath.mpc(0, t)))) for t in ts]
    ax.plot(ts, ref, color='black', linestyle='--', linewidth=1.0, alpha=0.6,
            label=r'$|\zeta(it)|$ (reference)')

    ax.set_xlabel(r'$t$  (with $s = it$)')
    ax.set_ylabel(r'$|\zeta_{M_n}(0 + it)|$')
    ax.set_title(
        r'Boundary behaviour of $\zeta_{M_n}$ on $\mathrm{Re}\,s = 0$'
        '\nNo poles (regular at $s = 0$); oscillation tracks $|\zeta(it)|$ scaled by $n^{-it}$ phase'
    )
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=9)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_psi_ratio(curves, out_path):
    """psi_{M_n}(x) / x  vs x."""
    fig, ax = plt.subplots(1, 1, figsize=(11, 6), dpi=140)
    cmap = plt.get_cmap('viridis')
    for i, n in enumerate(NS):
        xs, psis = curves[n]
        ratio = psis / xs
        ax.plot(xs, ratio, color=cmap(i / max(1, len(NS) - 1)),
                label=f'n = {n}', linewidth=1.2)

    ax.axhline(1.0, color='red', linestyle='--', linewidth=1.0,
               label=r'predicted limit = 1')
    ax.set_xscale('log')
    ax.set_xlabel(r'$x$')
    ax.set_ylabel(r'$\psi_{M_n}(x) / x$')
    ax.set_title(
        r'BIDDER PNT analog: $\psi_{M_n}(x) = \sum_{m \in M_n,\ m \leq x} Q_n(m) \log m$'
        '\n' + r'Residue at $s = 1$ predicts $\psi_{M_n}(x)/x \to 1$'
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=9)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_psi_residual(curves, out_path):
    """psi_{M_n}(x) - x  as residual."""
    fig, ax = plt.subplots(1, 1, figsize=(11, 6), dpi=140)
    cmap = plt.get_cmap('viridis')
    for i, n in enumerate(NS):
        xs, psis = curves[n]
        residual = psis - xs
        ax.plot(xs, residual, color=cmap(i / max(1, len(NS) - 1)),
                label=f'n = {n}', linewidth=1.2)
    ax.axhline(0.0, color='black', linewidth=0.6, alpha=0.5)
    ax.set_xscale('log')
    ax.set_xlabel(r'$x$')
    ax.set_ylabel(r'$\psi_{M_n}(x) - x$')
    ax.set_title(
        r'Residual: $\psi_{M_n}(x) - x$'
        '\n(Beurling PNT analog: should be $o(x)$ if WI applies)'
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=9)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def main():
    findings = []

    print('Phase A: literal Olofsson transplant ...')
    summary_a = phase_a_summary()
    print(summary_a)
    findings.append(summary_a)
    findings.append('')

    print()
    print('Phase B: signed Mangoldt analog ...')
    summary_b, curves = phase_b_psi()
    print(summary_b)
    findings.append(summary_b)
    findings.append('')

    print()
    print('Phase C: rendering plots ...')
    print('  -> boundary on Re s = 0')
    plot_boundary(OUT_BOUNDARY)
    print(f'  -> {OUT_BOUNDARY}')
    print('  -> psi convergence')
    plot_psi_ratio(curves, OUT_PSI_RATIO)
    print(f'  -> {OUT_PSI_RATIO}')
    print('  -> psi residual')
    plot_psi_residual(curves, OUT_PSI_RESIDUAL)
    print(f'  -> {OUT_PSI_RESIDUAL}')

    findings.append('=== Plots ===')
    findings.append(f'  {OUT_BOUNDARY}')
    findings.append(f'  {OUT_PSI_RATIO}')
    findings.append(f'  {OUT_PSI_RESIDUAL}')

    with open(OUT_FINDINGS, 'w') as f:
        f.write('\n'.join(findings))
    print(f'\nFindings: {OUT_FINDINGS}')


if __name__ == '__main__':
    main()
