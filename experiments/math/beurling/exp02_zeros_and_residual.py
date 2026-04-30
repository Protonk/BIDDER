"""
exp02_zeros_and_residual.py — find zeros of zeta_{M_n} and test their
connection to the residual psi_{M_n}(x) - x.

Building on exp01:
- Phase A: thorough zero search of zeta_{M_n}(s) = 1 + n^{-s} zeta(s)
  in the critical strip 0 < Re s < 1 and on Re s = 1.
- Phase B: extend psi_{M_n}(x) computation to larger x (10^7) and
  plot psi/x convergence.
- Phase C: compare residual to predictions.
  If zeros rho exist, residual should pick up x^rho / rho contributions
  by Perron's formula.
- Phase D: visualize.

Outputs:
    exp02_zero_landscape.png       (heatmap of |zeta_{M_n}| over the strip)
    exp02_psi_convergence_long.png (psi/x to x = 10^7)
    exp02_residual_log.png         (residual on log scale to see decay/growth)
    exp02_findings.txt
"""

from __future__ import annotations

import os
import sys
import time
import math
from math import log as mlog

import numpy as np
import mpmath
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, 'algebra'))

from zeta_mn import zeta_mn
from predict_q import q_general

OUT_LANDSCAPE = os.path.join(HERE, 'exp02_zero_landscape.png')
OUT_PSI_LONG = os.path.join(HERE, 'exp02_psi_convergence_long.png')
OUT_RESIDUAL = os.path.join(HERE, 'exp02_residual_log.png')
OUT_FINDINGS = os.path.join(HERE, 'exp02_findings.txt')

NS = (2, 3, 5, 6, 10)
PSI_X_MAX = 5_000_000
PSI_SAMPLES = 250
T_MAX_SCAN = 50.0
SIGMA_RANGE = (0.4, 1.05)


# --------------------------------------------------------------------------
# Phase A: zero search
# --------------------------------------------------------------------------

def grid_min(n, sigma_range, t_range, n_sigma, n_t, dps=20):
    """Compute |zeta_{M_n}| on a grid; return min and grid."""
    mpmath.mp.dps = dps
    sigmas = np.linspace(sigma_range[0], sigma_range[1], n_sigma)
    ts = np.linspace(t_range[0], t_range[1], n_t)
    mags = np.zeros((n_sigma, n_t))
    for i, sigma in enumerate(sigmas):
        for j, t in enumerate(ts):
            z = zeta_mn(n, mpmath.mpc(float(sigma), float(t)))
            mags[i, j] = float(abs(z))
    return sigmas, ts, mags


def find_local_minima(mags, sigmas, ts, threshold=0.2):
    """2D local minima below threshold."""
    mins = []
    for i in range(1, len(sigmas) - 1):
        for j in range(1, len(ts) - 1):
            v = mags[i, j]
            if v < threshold:
                if (v <= mags[i - 1, j] and v <= mags[i + 1, j]
                        and v <= mags[i, j - 1] and v <= mags[i, j + 1]):
                    mins.append((sigmas[i], ts[j], v))
    return mins


def refine_zero(n, sigma0, t0, dps=30):
    """Try mpmath.findroot from a starting point."""
    mpmath.mp.dps = dps
    try:
        rho = mpmath.findroot(lambda s: zeta_mn(n, s), mpmath.mpc(float(sigma0), float(t0)))
        return rho
    except (ValueError, ZeroDivisionError, Exception):
        return None


def phase_a_search(logger):
    logger('=== Phase A: zero search ===')
    logger('')
    logger('Scanning |zeta_{M_n}(σ + it)| in the strip σ ∈ [0.4, 1.05], t ∈ [0.1, 50].')
    logger('')

    found_zeros = {}
    for n in NS:
        logger(f'-- n = {n} --')
        sigmas, ts, mags = grid_min(n, SIGMA_RANGE, (0.1, T_MAX_SCAN), 30, 200)
        candidates = find_local_minima(mags, sigmas, ts, threshold=0.1)
        logger(f'  grid minimum: {mags.min():.4f} at '
            f'σ={sigmas[mags.argmin() // mags.shape[1]]:.3f}, '
            f't={ts[mags.argmin() % mags.shape[1]]:.3f}')

        zeros = []
        if candidates:
            logger(f'  {len(candidates)} candidates below 0.1 threshold; refining:')
            for sigma0, t0, m0 in candidates[:10]:
                rho = refine_zero(n, sigma0, t0)
                if rho is not None and abs(zeta_mn(n, rho)) < 1e-8:
                    zeros.append(rho)
                    logger(f'    candidate ({sigma0:.3f}, {t0:.3f}, |zeta|={m0:.4f}) '
                        f'→ ρ = {complex(rho):.4f}')
        else:
            logger('  no candidates below 0.1; no zeros in scanned region.')

        unique_zeros = []
        for rho in zeros:
            if not any(abs(rho - r) < 1e-6 for r in unique_zeros):
                unique_zeros.append(rho)
        unique_zeros.sort(key=lambda r: float(r.imag))
        found_zeros[n] = unique_zeros
        logger(f'  {len(unique_zeros)} unique zeros found.')
        logger('')

    return found_zeros


# --------------------------------------------------------------------------
# Phase B: long psi_{M_n} computation
# --------------------------------------------------------------------------

def compute_psi_long(n, x_max, sample_points, logger):
    """psi_{M_n}(x) at log-spaced x up to x_max."""
    xs = np.unique(np.round(np.geomspace(2 * n, x_max, sample_points)).astype(int))
    psi_at_x = {}

    cum = 0.0
    j_max = x_max // n
    cum_at_m = {}  # for each m, value of cum AFTER adding term at m
    t0 = time.time()
    last_print = t0
    for j in range(1, j_max + 1):
        m = j * n
        if m > x_max:
            break
        q = float(q_general(n, 1, j))
        if q != 0:
            cum += q * mlog(m)
        cum_at_m[m] = cum
        # Periodic progress
        now = time.time()
        if now - last_print > 30:
            logger(f'    [n={n}] j={j}, m={m}, cum={cum:.2f}, elapsed={now - t0:.1f}s')
            last_print = now

    # For each sampled x, find the max m <= x with a recorded cum.
    # Since m steps by n, m_max(x) = (x // n) * n.
    psi_at_x = {}
    for x in xs:
        m_max = (int(x) // n) * n
        if m_max < n:
            psi_at_x[int(x)] = 0.0
        else:
            psi_at_x[int(x)] = cum_at_m.get(m_max, cum)

    return np.array(sorted(psi_at_x.keys())), np.array([psi_at_x[int(x)] for x in sorted(psi_at_x.keys())])


def phase_b_psi_long(logger):
    logger('=== Phase B: psi_{M_n}(x) to x = 5e6 ===')
    logger('')
    curves = {}
    for n in NS:
        logger(f'-- n = {n} --')
        t0 = time.time()
        xs, psis = compute_psi_long(n, PSI_X_MAX, PSI_SAMPLES, logger)
        elapsed = time.time() - t0
        ratio_final = psis[-1] / xs[-1]
        logger(f'  computed in {elapsed:.1f}s; psi/x at x={xs[-1]} = {ratio_final:.5f}')
        curves[n] = (xs, psis)
    return curves


# --------------------------------------------------------------------------
# Phase C: visualize
# --------------------------------------------------------------------------

def plot_zero_landscape(n, out_path):
    """Heatmap of |zeta_{M_n}| in the critical strip."""
    sigmas, ts, mags = grid_min(n, (0.3, 1.05), (0.1, 50), 60, 250, dps=20)
    fig, ax = plt.subplots(1, 1, figsize=(13, 7), dpi=130)
    # Use log of magnitude for better contrast.
    log_mags = np.log10(np.maximum(mags, 1e-3))
    im = ax.imshow(
        log_mags.T, origin='lower', aspect='auto',
        extent=(sigmas[0], sigmas[-1], ts[0], ts[-1]),
        cmap='RdBu_r', vmin=-1.5, vmax=1.0,
    )
    ax.set_xlabel(r'$\sigma$')
    ax.set_ylabel(r'$t$')
    ax.set_title(
        rf'$\log_{{10}}|\zeta_{{M_{n}}}(\sigma + it)|$ landscape'
        '\n' + r'(red = small magnitude / candidate zero; blue = large)'
    )
    plt.colorbar(im, ax=ax, label=r'$\log_{10}|\zeta_{M_n}|$')
    # Mark Re s = 1 line
    ax.axvline(1.0, color='black', linestyle='--', linewidth=0.7, alpha=0.7,
               label=r'$\sigma = 1$')
    ax.axvline(0.5, color='gray', linestyle=':', linewidth=0.7, alpha=0.5,
               label=r'$\sigma = 1/2$')
    ax.legend(loc='upper right', fontsize=9)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_psi_long(curves, out_path):
    fig, ax = plt.subplots(1, 1, figsize=(12, 6.5), dpi=140)
    cmap = plt.get_cmap('viridis')
    for i, n in enumerate(NS):
        xs, psis = curves[n]
        ratio = psis / xs
        ax.plot(xs, ratio, color=cmap(i / max(1, len(NS) - 1)),
                label=f'n = {n}', linewidth=1.4)
    ax.axhline(1.0, color='red', linestyle='--', linewidth=1.0,
               label=r'predicted limit = 1')
    ax.set_xscale('log')
    ax.set_xlabel(r'$x$')
    ax.set_ylabel(r'$\psi_{M_n}(x) / x$')
    ax.set_title(
        r'$\psi_{M_n}(x) / x$ to $x = 5 \times 10^6$'
        '\n' + r'Slow convergence to 1; rate decreases with $n$'
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower right', fontsize=10)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_residual_log(curves, out_path):
    """|residual| / x and |residual| / (x/log x) on log-log."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), dpi=140)
    cmap = plt.get_cmap('viridis')

    # Panel 1: |residual| / x
    ax = axes[0]
    for i, n in enumerate(NS):
        xs, psis = curves[n]
        residual = psis - xs
        ax.plot(xs, np.abs(residual) / xs, color=cmap(i / max(1, len(NS) - 1)),
                label=f'n = {n}', linewidth=1.3)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'$x$')
    ax.set_ylabel(r'$|\psi_{M_n}(x) - x| / x$')
    ax.set_title(r'$|\psi - x| / x$ (log-log)')
    ax.grid(True, alpha=0.3, which='both')
    ax.legend(loc='best', fontsize=9)

    # Panel 2: |residual| · log(x) / x  (test for ~1/log x decay)
    ax = axes[1]
    for i, n in enumerate(NS):
        xs, psis = curves[n]
        residual = psis - xs
        rate_test = np.abs(residual) * np.log(xs) / xs
        ax.plot(xs, rate_test, color=cmap(i / max(1, len(NS) - 1)),
                label=f'n = {n}', linewidth=1.3)
    ax.set_xscale('log')
    ax.set_xlabel(r'$x$')
    ax.set_ylabel(r'$|\psi_{M_n}(x) - x| \cdot \log x / x$')
    ax.set_title(r'$|\psi - x| \log x / x$  (flat = $|\psi - x| \sim x/\log x$)')
    ax.grid(True, alpha=0.3, which='both')
    ax.legend(loc='best', fontsize=9)

    plt.suptitle('Residual rate-of-decay diagnostics')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

def main():
    findings = []
    def logger(line=''):
        print(line)
        findings.append(line)

    logger('exp02 — zeros of zeta_{M_n} and the psi residual')
    logger('=' * 66)
    logger('')

    # Phase A: zero search
    found_zeros = phase_a_search(logger)
    logger('')
    logger('Zero search summary:')
    for n in NS:
        zs = found_zeros.get(n, [])
        if zs:
            logger(f'  n = {n}: {len(zs)} zeros, lowest at ρ = {complex(zs[0]):.4f}')
        else:
            logger(f'  n = {n}: no zeros found in scanned strip.')
    logger('')

    # Phase B: long psi
    curves = phase_b_psi_long(logger)
    logger('')
    logger('Long-x psi/x ratios:')
    for n in NS:
        xs, psis = curves[n]
        ratio = psis[-1] / xs[-1]
        logger(f'  n = {n}: psi/x at x={xs[-1]} = {ratio:.5f}, residual = {psis[-1] - xs[-1]:+.1f}')
    logger('')

    # Phase C: plots
    logger('=== Phase C: plotting ===')
    logger(f'  -> {OUT_LANDSCAPE}  (zero landscape, n=10 as representative)')
    plot_zero_landscape(10, OUT_LANDSCAPE)
    logger(f'  -> {OUT_PSI_LONG}  (long psi/x convergence)')
    plot_psi_long(curves, OUT_PSI_LONG)
    logger(f'  -> {OUT_RESIDUAL}  (residual decay diagnostics)')
    plot_residual_log(curves, OUT_RESIDUAL)
    logger('')

    # Phase D: rate analysis
    logger('=== Phase D: rate analysis ===')
    logger('')
    logger('Test: does residual scale like x/log x? (i.e., |psi - x| log x / x ≈ const?)')
    sample_xs = [int(x) for x in np.geomspace(1000, PSI_X_MAX, 6)]
    logger(f'{"n":>3}  ' + '  '.join(f'{x:>10}' for x in sample_xs))
    for n in NS:
        xs, psis = curves[n]
        line = f'{n:>3}  '
        for sx in sample_xs:
            idx = np.argmin(np.abs(xs - sx))
            x_actual = xs[idx]
            res = psis[idx] - x_actual
            rate = abs(res) * mlog(x_actual) / x_actual if x_actual > 1 else 0
            line += f'  {rate:>9.4f}'
        logger(line)
    logger('')
    logger('If this column-ratio approaches a constant per-row, residual is ~ x/log x.')

    with open(OUT_FINDINGS, 'w') as f:
        f.write('\n'.join(findings))
    logger(f'\nFindings file: {OUT_FINDINGS}')


if __name__ == '__main__':
    main()
