"""
Echo test — does the post-peak bias have additional local maxima?

Combines the lowK (K ∈ [10, 2000] step 10) and largeK (K ∈ [2000,
50000] step 500) caches. For each n_0, identifies the main peak,
then searches for additional local maxima past it with a prominence
filter to reject noise.

A "deep echoes" reading predicts: every n_0 has ≥ 1 echo, and the
echoes appear at multiple K-scales.

Reports echo count and locations per n_0. No plotting.
"""

import numpy as np
from scipy.signal import find_peaks

zL = np.load('l1_grid_lengths_lowK.npz')
zG = np.load('l1_grid_lengths_largeK.npz')

K_low = zL['K_VALUES']
K_high = zG['K_VALUES']
N0_low = zL['N0_VALUES']
N0_high = zG['N0_VALUES']

bias_low = (zL['L_SURV'] / zL['N_SURV']) / \
           (zL['L_B_SET'] / zL['N_UNIQUE'])
bias_low = (bias_low - 1) * 100
bias_high = (zG['L_SURV'] / zG['N_SURV']) / \
            (zG['L_B_SET'] / zG['N_UNIQUE'])
bias_high = (bias_high - 1) * 100

# Combine caches at non-overlapping K. Low covers [10, 2000]; high
# covers [2000, 50000]. Use low for K ≤ 2000, high for K > 2000.
mask_high = K_high > 2000
K_high_use = K_high[mask_high]


def combined(n0):
    if n0 not in N0_low or n0 not in N0_high:
        return None
    iL = int(np.where(N0_low == n0)[0][0])
    iH = int(np.where(N0_high == n0)[0][0])
    K = np.concatenate([K_low, K_high_use])
    b = np.concatenate([bias_low[iL, :], bias_high[iH, mask_high]])
    return K, b


# Prominence threshold: 5% of the global peak amplitude per row.
# This is permissive enough to catch real echoes while rejecting
# fluctuations of 0.01-0.05% scale near the noise floor.
def echo_search(K, bias, prom_frac=0.05, min_abs_prom=0.05):
    j_main = int(np.argmax(bias))
    main_K = int(K[j_main])
    main_amp = float(bias[j_main])
    threshold = max(prom_frac * abs(main_amp), min_abs_prom)
    # Search post-main slice only.
    K_post = K[j_main:]
    b_post = bias[j_main:]
    peaks, props = find_peaks(b_post, prominence=threshold)
    echo_K = K_post[peaks]
    echo_amp = b_post[peaks]
    echo_prom = props['prominences']
    return main_K, main_amp, list(zip(echo_K, echo_amp, echo_prom))


print("Echo search past the main peak (set basis):")
print(f"{'n_0':>4} {'main K':>7} {'main %':>7} {'#echoes':>8} "
      f"{'echo (K, %, prom)':>40}")
print("-" * 80)
echo_count_total = 0
n0_with_echoes = 0
echo_K_all = []
for n0 in range(2, 13):
    res = combined(n0)
    if res is None:
        continue
    K, bias = res
    main_K, main_amp, echoes = echo_search(K, bias)
    if echoes:
        echo_count_total += len(echoes)
        n0_with_echoes += 1
        echo_K_all.extend(e[0] for e in echoes)
    echo_str = "  ".join(f"({K_e}, {a_e:+.3f}, {p_e:.3f})"
                          for K_e, a_e, p_e in echoes) or "—"
    print(f"{n0:>4d} {main_K:>7d} {main_amp:>+7.3f} "
          f"{len(echoes):>8d}   {echo_str}")

# Also test n_0 ∈ [13..50] from largeK alone (no lowK data there).
print()
print("Echo search using largeK alone (K ∈ [2000, 50000]):")
print(f"{'n_0':>4} {'main K':>7} {'main %':>7} {'#echoes':>8} "
      f"{'echo (K, %, prom)':>40}")
print("-" * 80)
for n0 in [15, 20, 25, 30, 40, 50]:
    iH = int(np.where(N0_high == n0)[0][0])
    K = K_high
    bias = bias_high[iH, :]
    main_K, main_amp, echoes = echo_search(K, bias)
    echo_count_total += len(echoes)
    if echoes:
        n0_with_echoes += 1
        echo_K_all.extend(e[0] for e in echoes)
    echo_str = "  ".join(f"({K_e}, {a_e:+.3f}, {p_e:.3f})"
                          for K_e, a_e, p_e in echoes) or "—"
    print(f"{n0:>4d} {main_K:>7d} {main_amp:>+7.3f} "
          f"{len(echoes):>8d}   {echo_str}")

print()
print(f"Summary: {echo_count_total} echoes detected across rows; "
      f"{n0_with_echoes} of {len(range(2, 13)) + 6} rows have ≥1 echo")
if echo_K_all:
    K_arr = np.array(echo_K_all)
    print(f"Echo K range: [{K_arr.min()}, {K_arr.max()}]")
    print(f"Echo K log10 distribution: "
          f"mean log10(K) = {np.mean(np.log10(K_arr)):.2f}, "
          f"std = {np.std(np.log10(K_arr)):.2f}")
