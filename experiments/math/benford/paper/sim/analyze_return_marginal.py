"""
Analyze return-marginal sim: summarize π_T ν_R's empirical
distribution and its Fourier coefficients.

Run: sage -python analyze_return_marginal.py
"""

import math
import os
import numpy as np


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SIM_DIR, 'return_marginal_results')


def main():
    path = os.path.join(OUT_DIR, 'return_marginal.npz')
    d = np.load(path, allow_pickle=True)
    m_density = d['m_density']
    E_hist = d['E_hist']
    fourier_modes = d['fourier_modes']
    sigma_hat = d['sigma_hat_re'] + 1j * d['sigma_hat_im']
    total = int(d['total_samples'])
    contributed = int(d['walkers_contributed'])
    N = int(d['meta_N'])
    E0 = int(d['meta_E0'])

    print(f'π_T ν_R empirical analysis')
    print(f'  N walkers = {N:_}, total return samples (post-burn) = {total:_}')
    print(f'  walkers contributing ≥ 1 sample: {contributed:_} '
          f'({contributed / N:.1%})')
    print()

    B = m_density.size
    print(f'  m-histogram ({B} bins):')
    print(f'    density min/median/mean/max = {m_density.min():.4f} / '
          f'{np.median(m_density):.4f} / {m_density.mean():.4f} / '
          f'{m_density.max():.4f}')
    L1 = float(np.sum(np.abs(m_density - 1.0)) / B)
    noise = math.sqrt(2 * B / (math.pi * max(total, 1)))
    print(f'    L₁(density, 1) = {L1:.6e}')
    print(f'    multinomial noise floor (mean L₁) = {noise:.6e}')
    print(f'    ratio meas / noise = {L1 / noise:.3f}')
    print(f'    → if ≈ 1.0: empirical density is consistent with uniform')
    print(f'    → if >> 1: structural deviation')
    print()

    # 20-bin coarsening to check for low-frequency bias
    coarse = m_density.reshape(20, B // 20).mean(axis=1)
    print(f'  Coarsened 20-bin density (each should be ≈ 1.0 under Leb):')
    for j in range(20):
        m_left = j / 20.0
        m_right = (j + 1) / 20.0
        bar = '#' * int(round(30 * coarse[j]))
        print(f'    [{m_left:.2f}, {m_right:.2f}):  {coarse[j]:.4f}  {bar}')
    print()

    # E-histogram
    print(f'  E-histogram at return (values in [-{E0}, {E0}]):')
    for j, v in enumerate(E_hist):
        E_val = j - E0
        frac = float(v) / max(total, 1)
        print(f'    E = {E_val:>+3d}: count {int(v):>8d}  frac {frac:.4f}')
    print()

    # Fourier coefficients
    one_over_sqrt_M = 1.0 / math.sqrt(max(total, 1))
    print(f'  Fourier coefficients |σ̂(r)|:')
    print(f'    (noise floor per component under Leb: ~ {one_over_sqrt_M:.4e})')
    print(f'    {"r":>4s}  {"|σ̂(r)|":>12s}  {"ratio/noise":>12s}  arg(σ̂)')
    for i, r in enumerate(fourier_modes.tolist()):
        mag = abs(sigma_hat[i])
        ratio = mag / one_over_sqrt_M
        arg = math.degrees(math.atan2(sigma_hat[i].imag, sigma_hat[i].real))
        flag = '  ← structure?' if ratio > 3.0 else ''
        print(f'    {r:>4d}  {mag:>12.4e}  {ratio:>12.3f}  '
              f'{arg:>+7.2f}°{flag}')


if __name__ == '__main__':
    main()
