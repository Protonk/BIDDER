"""
q_lattice_iter_analysis.py - is the iter_10 attractor really noise?

Run the iteration to iter 10. Compare against a true Gaussian noise of
matched mean/std on:

  1. radial power spectrum (a Gaussian gives a flat radial profile;
     anything else exposes structure)
  2. value histogram (Gaussian distribution vs. observed)
  3. visual side-by-side render

If iter_10 is statistically indistinguishable from white noise, the
"moire" is display / JPEG artifact. If they differ, real structure.
"""

import os
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


HERE = os.path.dirname(os.path.abspath(__file__))


def slog(arr, lt=1.0):
    arr = np.asarray(arr, dtype=float)
    return np.sign(arr) * np.log10(1.0 + np.abs(arr) / lt)


def fft_log_mag(img):
    centered = img - img.mean()
    F = np.fft.fftshift(np.fft.fft2(centered))
    return np.log10(np.abs(F) + 1.0).astype(np.float32)


def radial_average(power, n_bins=None):
    h, w = power.shape
    cy, cx = h // 2, w // 2
    yy, xx = np.indices((h, w))
    r = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
    r_int = r.astype(np.int32)
    if n_bins is None:
        n_bins = r_int.max() + 1
    counts = np.bincount(r_int.ravel(), minlength=n_bins)
    sums = np.bincount(r_int.ravel(), weights=power.ravel(), minlength=n_bins)
    return sums[:n_bins] / np.maximum(counts[:n_bins], 1)


def main():
    cache = os.path.join(HERE, 'q_lattice_4000.npy')
    grid = np.load(cache)
    img = slog(grid).astype(np.float32)

    print('Iterating to iter 10...')
    for i in range(1, 11):
        img = fft_log_mag(img)
    print(f'  iter_10: mean={img.mean():.4f}  std={img.std():.4f}  '
          f'range=[{img.min():.3f}, {img.max():.3f}]')

    rng = np.random.default_rng(42)
    gauss = rng.normal(loc=img.mean(), scale=img.std(),
                       size=img.shape).astype(np.float32)
    print(f'  gauss:    mean={gauss.mean():.4f}  std={gauss.std():.4f}  '
          f'range=[{gauss.min():.3f}, {gauss.max():.3f}]')

    print('\nFFT power spectra...')
    F_img = np.fft.fftshift(np.fft.fft2(img - img.mean()))
    F_gauss = np.fft.fftshift(np.fft.fft2(gauss - gauss.mean()))
    pow_img = np.abs(F_img) ** 2
    pow_gauss = np.abs(F_gauss) ** 2

    radial_img = radial_average(np.log10(pow_img + 1.0))
    radial_gauss = radial_average(np.log10(pow_gauss + 1.0))
    print(f'  iter_10 log-power radial: '
          f'mean={radial_img.mean():.3f}  std={radial_img.std():.3f}')
    print(f'  gauss   log-power radial: '
          f'mean={radial_gauss.mean():.3f}  std={radial_gauss.std():.3f}')
    print(f'  difference at low frequencies (r=1..50): '
          f'{(radial_img[1:51] - radial_gauss[1:51]).mean():+.3f}')
    print(f'  difference at high frequencies (r=1500..2000): '
          f'{(radial_img[1500:2000] - radial_gauss[1500:2000]).mean():+.3f}')

    # --- side-by-side image ---
    print('\nRendering side-by-side comparison...')
    lo_img = float(np.percentile(img, 2))
    hi_img = float(np.percentile(img, 99))
    lo_g = float(np.percentile(gauss, 2))
    hi_g = float(np.percentile(gauss, 99))
    fig, axes = plt.subplots(1, 2, figsize=(20, 10),
                             dpi=150, facecolor='black')
    for ax in axes:
        ax.set_facecolor('black')
        ax.set_axis_off()
    axes[0].imshow(img, cmap='inferno', origin='lower',
                   interpolation='nearest', vmin=lo_img, vmax=hi_img)
    axes[0].set_title('iter_10 attractor', color='white', fontsize=14)
    axes[1].imshow(gauss, cmap='inferno', origin='lower',
                   interpolation='nearest', vmin=lo_g, vmax=hi_g)
    axes[1].set_title('matched Gaussian (same mean, std)',
                      color='white', fontsize=14)
    plt.tight_layout()
    out_sbs = os.path.join(HERE, 'q_lattice_iter_10_vs_gauss.png')
    plt.savefig(out_sbs, facecolor='black', bbox_inches='tight')
    plt.close()
    print(f'  -> {os.path.basename(out_sbs)}')

    # --- radial spectrum plot ---
    fig, ax = plt.subplots(figsize=(12, 6), dpi=150, facecolor='black')
    ax.set_facecolor('#0a0a0a')
    rs = np.arange(len(radial_img))
    ax.plot(rs[1:], radial_img[1:], color=(1.0, 0.66, 0.30),
            lw=1.0, label='iter_10', alpha=0.9)
    ax.plot(rs[1:], radial_gauss[1:], color=(0.45, 0.78, 1.00),
            lw=1.0, label='matched Gaussian', alpha=0.9)
    ax.set_xlabel('radial frequency  (px from DC)',
                  color=(0.85, 0.88, 0.92, 0.92), fontsize=11)
    ax.set_ylabel('log10(power + 1)',
                  color=(0.85, 0.88, 0.92, 0.92), fontsize=11)
    ax.set_title('radial power spectrum:  iter_10 attractor  vs  matched Gaussian',
                 color='white', fontsize=12, fontweight='bold')
    ax.legend(facecolor=(0.05, 0.06, 0.08), edgecolor=(0.30, 0.36, 0.42),
              labelcolor='white', fontsize=10)
    ax.tick_params(colors=(0.78, 0.82, 0.88, 0.85), labelsize=9)
    for spine in ax.spines.values():
        spine.set_color((0.40, 0.45, 0.50, 0.40))
    ax.grid(True, color=(0.30, 0.34, 0.38), alpha=0.18, lw=0.4)
    plt.tight_layout()
    out_rad = os.path.join(HERE, 'q_lattice_iter_10_radial.png')
    plt.savefig(out_rad, facecolor='black', bbox_inches='tight')
    plt.close()
    print(f'  -> {os.path.basename(out_rad)}')

    # --- histogram ---
    fig, ax = plt.subplots(figsize=(12, 6), dpi=150, facecolor='black')
    ax.set_facecolor('#0a0a0a')
    bins = np.linspace(min(img.min(), gauss.min()),
                       max(img.max(), gauss.max()), 200)
    ax.hist(img.ravel(), bins=bins, color=(1.0, 0.66, 0.30, 0.7),
            label='iter_10', density=True)
    ax.hist(gauss.ravel(), bins=bins, color=(0.45, 0.78, 1.00, 0.55),
            label='matched Gaussian', density=True)
    ax.set_xlabel('value', color=(0.85, 0.88, 0.92, 0.92), fontsize=11)
    ax.set_ylabel('density', color=(0.85, 0.88, 0.92, 0.92), fontsize=11)
    ax.set_title('histogram comparison', color='white', fontsize=12, fontweight='bold')
    ax.legend(facecolor=(0.05, 0.06, 0.08), edgecolor=(0.30, 0.36, 0.42),
              labelcolor='white', fontsize=10)
    ax.tick_params(colors=(0.78, 0.82, 0.88, 0.85), labelsize=9)
    for spine in ax.spines.values():
        spine.set_color((0.40, 0.45, 0.50, 0.40))
    plt.tight_layout()
    out_hist = os.path.join(HERE, 'q_lattice_iter_10_hist.png')
    plt.savefig(out_hist, facecolor='black', bbox_inches='tight')
    plt.close()
    print(f'  -> {os.path.basename(out_hist)}')

    # Save the iter_10 array for later inspection.
    np.save(os.path.join(HERE, 'q_lattice_iter_10.npy'), img)


if __name__ == '__main__':
    main()
