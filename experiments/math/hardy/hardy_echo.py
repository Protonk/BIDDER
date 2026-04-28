"""
hardy_echo.py — unified deep-window sampler for n-prime streams
================================================================

Per `experiments/math/hardy/DEEP-TROUBLE-No-4.md`. Random access into
n-prime sequences via the Hardy closed form, with four window-selection
modes:

  Mode 1 — Deep Window:        choose by entry index K
  Mode 2 — Digit-Position:     choose by stream digit position i
  Mode 3 — Block Boundary:     choose by radix block (b, d)
  Mode 4 — Tail Destroyer:     re-run a prefix-era observable in
                                a matched deep window with shuffle null

This builds the window primitive plus simple per-window observables:
RLE, boundary stitch, Hamming, bit/digit balance. Walsh / Morlet / CF
are out of scope.

Usage:
    sage -python hardy_echo.py
"""

import csv
import os
import sys
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'core'))

from acm_core import acm_n_primes


# ---- Hardy closed form ----

def nth_n_prime(n, K):
    """Hardy closed form: K-th n-prime for n >= 2.
    p_K(n) = n · (q · n + r + 1), with (q, r) = divmod(K - 1, n - 1).
    See core/HARDY-SIDESTEP.md."""
    if n < 2:
        raise ValueError(f'Hardy closed form requires n >= 2; got n = {n}')
    if K < 1:
        raise ValueError(f'K must be >= 1; got K = {K}')
    q, r = divmod(K - 1, n - 1)
    return n * (q * n + r + 1)


def window(n, K0, W):
    """Window of W consecutive n-primes starting at K=K0 (Mode 1 primitive)."""
    return [nth_n_prime(n, K0 + i) for i in range(W)]


# ---- digit / bit streams ----

def digits_in_base(v, base):
    """Digits of positive integer v in given base, most-significant first."""
    if v == 0:
        return [0]
    out = []
    while v > 0:
        out.append(v % base)
        v //= base
    return list(reversed(out))


def stream_in_base(window_, base):
    """Concatenated digit stream of a window in given base."""
    out = []
    for p in window_:
        out.extend(digits_in_base(p, base))
    return out


def digit_length(v, base):
    """Number of base-`base` digits in positive integer v."""
    return len(digits_in_base(v, base))


# ---- observables ----

def rle(stream):
    """Run-length encoding: list of (symbol, run_length) pairs."""
    if not stream:
        return []
    out = []
    cur = stream[0]
    cnt = 1
    for s in stream[1:]:
        if s == cur:
            cnt += 1
        else:
            out.append((cur, cnt))
            cur = s
            cnt = 1
    out.append((cur, cnt))
    return out


def rle_histogram(stream, max_run=20):
    """Per-symbol run-length histograms. Returns dict symbol -> array[max_run+1]
    where index r counts runs of length r (with the last bucket as r >= max_run)."""
    counts = defaultdict(lambda: np.zeros(max_run + 1, dtype=int))
    for sym, run in rle(stream):
        idx = min(run, max_run)
        counts[sym][idx] += 1
    return dict(counts)


def hamming_weight(stream):
    """For binary streams: number of 1s."""
    return sum(1 for s in stream if s)


def boundary_stitch_window(window_, half_width=8, base=2):
    """For each consecutive pair (p_K, p_{K+1}), return the bit window
    around the boundary: last `half_width` digits of p_K (left-padded
    with zeros if too short) and first `half_width` digits of p_{K+1}.
    Returns array of shape (W-1, 2*half_width)."""
    if len(window_) < 2:
        raise ValueError('boundary_stitch_window requires at least two entries')
    W = len(window_)
    out = np.zeros((W - 1, 2 * half_width), dtype=np.int8)
    for i in range(W - 1):
        left = digits_in_base(window_[i], base)
        right = digits_in_base(window_[i + 1], base)
        if len(left) >= half_width:
            L = left[-half_width:]
        else:
            L = [0] * (half_width - len(left)) + left
        if len(right) >= half_width:
            R = right[:half_width]
        else:
            R = right + [0] * (half_width - len(right))
        out[i, :half_width] = L
        out[i, half_width:] = R
    return out


def shuffle_window(window_, seed=0):
    """Within-window entry shuffle (Mode 4 destroyer)."""
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(window_))
    return [window_[i] for i in perm]


# ---- Mode 2: digit-position inversion ----


def K_from_digit_position(n, base, i):
    """Mode 2: find K such that the K-th n-prime contains stream digit
    position i (1-indexed). Uses exact digit-length blocks."""
    if i < 1:
        return 1, 0
    remaining = i
    d = 1
    while True:
        K_min, K_max = K_for_block(n, base, d)
        count = K_max - K_min + 1 if K_max >= K_min else 0
        block_digits = count * d
        if remaining <= block_digits:
            within = remaining - 1
            return K_min + within // d, within % d
        remaining -= block_digits
        d += 1


# ---- Mode 3: block boundary ----

def K_for_block(n, b, d):
    """Mode 3: return (K_min, K_max) such that p_K(n) ∈ [b^(d-1), b^d) for
    K ∈ [K_min, K_max]. Uses the closed-form approximation
    p_K(n) ≈ K · n² / (n-1) and refines exactly."""
    lo = b ** (d - 1)
    hi = b ** d
    if lo < n:
        # Block starts below n: K_min is 1 (the first n-prime is n).
        K_min_guess = 1
    else:
        K_min_guess = max(1, lo * (n - 1) // (n * n))
    K_max_guess = max(K_min_guess, hi * (n - 1) // (n * n) + 1)
    # Refine K_min: smallest K with p_K(n) >= lo.
    K = K_min_guess
    while K > 1 and nth_n_prime(n, K) >= lo:
        K -= 1
    while nth_n_prime(n, K) < lo:
        K += 1
    K_min = K
    # Refine K_max: largest K with p_K(n) < hi.
    K = K_max_guess
    while nth_n_prime(n, K) >= hi:
        K -= 1
        if K < K_min:
            return K_min, K_min - 1  # empty
    while nth_n_prime(n, K + 1) < hi:
        K += 1
    K_max = K
    return K_min, K_max


# ---- Mode 4: tail destroyer ----

def matched_window_pair(n, K0_deep, W, observable):
    """For a given observable function f(window) -> scalar, return:
    (f(prefix window K=1..W), f(deep window K=K0_deep..K0_deep+W-1),
     and a list of K shuffle-null values from shuffled deep window)."""
    prefix_w = window(n, 1, W)
    deep_w = window(n, K0_deep, W)
    f_prefix = observable(prefix_w)
    f_deep = observable(deep_w)
    nulls = []
    for s in range(32):
        sw = shuffle_window(deep_w, seed=s)
        nulls.append(observable(sw))
    return f_prefix, f_deep, nulls


# ---- smoke check ----

def smoke_check():
    """Pin Hardy closed form against acm_n_primes enumerator."""
    print('[smoke] Hardy vs acm_n_primes for n ∈ {2,3,4,5,6,10}, K ≤ 200',
          flush=True)
    failures = []
    for n in [2, 3, 4, 5, 6, 10]:
        enum_list = acm_n_primes(n, 200)
        for K in range(1, 201):
            hardy = nth_n_prime(n, K)
            if hardy != enum_list[K - 1]:
                failures.append((n, K, hardy, enum_list[K - 1]))
    if failures:
        for f in failures[:5]:
            print(f'  FAIL n={f[0]} K={f[1]}: hardy={f[2]} enum={f[3]}')
        raise SystemExit('[smoke] FAIL')
    print('  [smoke] all 1200 cases agree.', flush=True)


# ---- experiments ----

def exp_deep_window_vs_prefix(out_dir):
    """Mode 1: compare RLE on prefix window vs deep window."""
    n = 2
    W = 200
    K0_deep = 10 ** 9
    print(f'\n[exp 1] Deep window: n={n}, prefix K=[1, {W}] vs deep K=[{K0_deep}, {K0_deep + W - 1}]',
          flush=True)

    prefix = window(n, 1, W)
    deep = window(n, K0_deep, W)

    print(f'  prefix:  p_1 = {prefix[0]}, p_{W} = {prefix[-1]}')
    print(f'  deep:    p_{K0_deep} = {deep[0]}, p_{K0_deep + W - 1} = {deep[-1]}')
    print(f'  prefix avg digit length (base 10): '
          f'{np.mean([digit_length(p, 10) for p in prefix]):.2f}')
    print(f'  deep   avg digit length (base 10): '
          f'{np.mean([digit_length(p, 10) for p in deep]):.2f}')

    # Bit RLE histograms.
    prefix_bits = stream_in_base(prefix, 2)
    deep_bits = stream_in_base(deep, 2)
    h_prefix = rle_histogram(prefix_bits, max_run=12)
    h_deep = rle_histogram(deep_bits, max_run=12)

    # Plot side-by-side.
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    for ax, h, title in [
        (axes[0], h_prefix, f'prefix K=[1, {W}]: bit RLE histogram'),
        (axes[1], h_deep, f'deep K=[{K0_deep}, +{W}]: bit RLE histogram'),
    ]:
        x = np.arange(1, 13)
        if 0 in h:
            ax.bar(x - 0.2, h[0][1:], width=0.4, label='0-runs', color='steelblue')
        if 1 in h:
            ax.bar(x + 0.2, h[1][1:], width=0.4, label='1-runs', color='crimson')
        ax.set_xticks(x)
        ax.set_xlabel('run length (last bin = ≥ 12)')
        ax.set_ylabel('count')
        ax.set_title(title)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'exp1_deep_vs_prefix_rle.png'), dpi=120)
    plt.close(fig)

    # Save numeric report.
    with open(os.path.join(out_dir, 'exp1_summary.txt'), 'w') as f:
        f.write(f'Experiment 1: prefix vs deep RLE histogram, n={n}, W={W}\n\n')
        f.write(f'prefix K=[1, {W}]\n')
        f.write(f'  avg digit length (base 10): '
                f'{np.mean([digit_length(p, 10) for p in prefix]):.4f}\n')
        f.write(f'  total bits (base 2): {len(prefix_bits)}\n')
        f.write(f'  Hamming weight (count of 1s): {hamming_weight(prefix_bits)}\n')
        f.write(f'  bit balance: {hamming_weight(prefix_bits) / len(prefix_bits):.4f}\n')
        f.write(f'  RLE histogram (run length 1..11, then ≥12):\n')
        for sym in (0, 1):
            f.write(f'    {sym}-runs: {h_prefix.get(sym, np.zeros(13))[1:].tolist()}\n')
        f.write(f'\ndeep K=[{K0_deep}, {K0_deep + W - 1}]\n')
        f.write(f'  avg digit length (base 10): '
                f'{np.mean([digit_length(p, 10) for p in deep]):.4f}\n')
        f.write(f'  total bits (base 2): {len(deep_bits)}\n')
        f.write(f'  Hamming weight (count of 1s): {hamming_weight(deep_bits)}\n')
        f.write(f'  bit balance: {hamming_weight(deep_bits) / len(deep_bits):.4f}\n')
        f.write(f'  RLE histogram (run length 1..11, then ≥12):\n')
        for sym in (0, 1):
            f.write(f'    {sym}-runs: {h_deep.get(sym, np.zeros(13))[1:].tolist()}\n')


def exp_boundary_stitch_persists(out_dir):
    """Mode 1 + Mode 4: does the v_2(n) trailing-zero barcode persist deep?"""
    n = 2  # v_2(n) = 1: every 2-prime ends in bit 0.
    W = 200
    K0_deep = 10 ** 9
    print(f'\n[exp 2] Boundary stitch: n={n}, prefix vs deep at K0={K0_deep}',
          flush=True)

    prefix = window(n, 1, W)
    deep = window(n, K0_deep, W)
    deep_shuffled = shuffle_window(deep, seed=42)

    half = 8
    img_prefix = boundary_stitch_window(prefix, half_width=half, base=2)
    img_deep = boundary_stitch_window(deep, half_width=half, base=2)
    img_deep_shuf = boundary_stitch_window(deep_shuffled, half_width=half, base=2)

    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    for ax, img, title in [
        (axes[0], img_prefix, f'prefix K=[1, {W}]'),
        (axes[1], img_deep, f'deep K=[{K0_deep}, +{W}]'),
        (axes[2], img_deep_shuf, f'deep, entry-shuffled (null)'),
    ]:
        ax.imshow(img, aspect='auto', cmap='gray_r', interpolation='nearest')
        ax.axvline(half - 0.5, color='red', lw=0.5)
        ax.set_xlabel('bit position relative to join (left=trailing, right=leading)')
        ax.set_ylabel('boundary index')
        ax.set_title(title)

    fig.suptitle(
        f'Boundary stitch — n={n}, expected v_2(n)=1 trailing-zero barcode '
        f'(column {half - 1} should be uniformly 0)'
    )
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'exp2_boundary_stitch.png'), dpi=120)
    plt.close(fig)

    # Quantitative: column-{half-1} (last trailing bit) should be 0 in
    # prefix, deep, and entry-shuffle null. Entry shuffle preserves the
    # per-entry parity invariant.
    barcode_col = half - 1
    rate_prefix = float(np.mean(img_prefix[:, barcode_col]))
    rate_deep = float(np.mean(img_deep[:, barcode_col]))
    rate_shuf = float(np.mean(img_deep_shuf[:, barcode_col]))
    print(f'  trailing-bit (column {barcode_col}) "1"-rate:')
    print(f'    prefix:       {rate_prefix:.4f}  (expected 0.0)')
    print(f'    deep:         {rate_deep:.4f}  (expected 0.0)')
    print(f'    shuffle-null: {rate_shuf:.4f}  (expected 0.0; entry shuffle preserves parity)')

    with open(os.path.join(out_dir, 'exp2_summary.txt'), 'w') as f:
        f.write(f'Experiment 2: boundary-stitch v_2(n)=1 barcode at depth\n')
        f.write(f'n={n}, W={W}, K0_deep={K0_deep}\n\n')
        f.write(f'  trailing-bit (col {barcode_col}) rate of 1:\n')
        f.write(f'    prefix:       {rate_prefix:.4f}  (expected 0.0)\n')
        f.write(f'    deep:         {rate_deep:.4f}  (expected 0.0)\n')
        f.write(f'    shuffle-null: {rate_shuf:.4f}  '
                f'(expected 0.0; entry shuffle preserves parity)\n')
        f.write(f'\nThe v_2(n)=1 trailing-zero barcode is closed-form '
                f'arithmetic: p_K(n=2) = 2·(q·2 + r + 1) is always even, so '
                f'its last bit is 0. This persists at any K. The shuffle '
                f'null preserves the barcode (entries still even after '
                f'shuffle) — *not* a real null for this claim, since the '
                f'barcode is per-entry, not per-position. A correct '
                f'destroyer would shuffle bits within entries, not '
                f'entries within window.\n')


def exp_block_boundary_at_depth(out_dir):
    """Mode 3: count n-primes in the d-th radix block at large d, compare
    to BLOCK-UNIFORMITY prediction (b−1)·b^(d−1)·(n−1)/n²."""
    n = 2
    b = 10
    print(f'\n[exp 3] Block boundary at depth: n={n}, b={b}, d ∈ {{1..6}}',
          flush=True)
    rows = [('d', 'block_lo', 'block_hi', 'K_min', 'K_max', 'count',
             'predicted_smooth')]
    for d in range(1, 7):
        K_min, K_max = K_for_block(n, b, d)
        count = K_max - K_min + 1 if K_max >= K_min else 0
        # Smooth prediction: (b-1)·b^(d-1)·(n-1)/n²; only valid when n²|b^(d-1).
        if (b ** (d - 1)) % (n * n) == 0:
            predicted = (b - 1) * (b ** (d - 1)) * (n - 1) // (n * n)
            pred_str = str(predicted)
        else:
            pred_str = 'n/a'
        rows.append((d, b ** (d - 1), b ** d, K_min, K_max, count, pred_str))
        print(f'  d={d}: block=[{b ** (d - 1)}, {b ** d}), K=[{K_min}, {K_max}], '
              f'count={count}, predicted (smooth)={pred_str}')

    with open(os.path.join(out_dir, 'exp3_block_boundary.csv'), 'w', newline='') as f:
        csv.writer(f).writerows(rows)


def exp_digit_oracle(out_dir):
    """Mode 2: digit-position inversion sanity check."""
    n = 2
    base = 10
    print(f'\n[exp 4] Digit-position oracle: n={n}, base={base}', flush=True)

    # Build a small ground-truth prefix and check the inversion against it.
    prefix_W = 1000
    prefix = window(n, 1, prefix_W)
    # Compute exact (K, offset) for a handful of digit positions.
    cumul = 0
    pos_to_truth = {}
    for K_idx, p in enumerate(prefix, start=1):
        L = digit_length(p, base)
        for off in range(L):
            cumul += 1
            if cumul in (1, 100, 1000, 2000, 3000):
                pos_to_truth[cumul] = (K_idx, off)
        if cumul > 4000:
            break

    rows = [('digit_position_i', 'true_K', 'true_offset',
             'oracle_K', 'oracle_offset', 'match_K')]
    for i, (true_K, true_off) in sorted(pos_to_truth.items()):
        oracle_K, oracle_off = K_from_digit_position(n, base, i)
        ok = (oracle_K == true_K)
        rows.append((i, true_K, true_off, oracle_K, oracle_off, ok))
        print(f'  i={i}: true (K={true_K}, off={true_off}), '
              f'oracle (K={oracle_K}, off={oracle_off})  '
              f'{"OK" if ok else "MISS"}')

    with open(os.path.join(out_dir, 'exp4_digit_oracle.csv'), 'w', newline='') as f:
        csv.writer(f).writerows(rows)

    # Try an extreme position too — no ground truth, just demonstrate it runs.
    deep_i = 10 ** 6
    K_d, off_d = K_from_digit_position(n, base, deep_i)
    p_d = nth_n_prime(n, K_d)
    print(f'  deep i={deep_i}: oracle (K={K_d}, offset={off_d}); '
          f'p_K = {p_d} (base-{base} digit length {digit_length(p_d, base)})')


def exp_finite_rank_consistency(out_dir):
    """Use Hardy random access to verify Q_n closed form at depth.
    Sanity loop with finite-rank lemma. Picks a deep K, computes m=p_K(n),
    evaluates Q_n(m) via the Q-formulas closed form, and checks consistency."""
    print(f'\n[exp 5] Finite-rank consistency at depth (Q_n closed form)',
          flush=True)

    rows = [('n', 'K', 'm', 'height_h', 'Q_n_value')]
    for n, K in [(2, 10 ** 6), (3, 10 ** 6), (5, 10 ** 5), (2, 10 ** 9)]:
        m = nth_n_prime(n, K)
        # height ν_n(m): m = n·(q·n + r + 1). v_n(m) = 1 + v_n(q·n+r+1).
        # The structure inside is q·n + r + 1 with r ∈ [0, n-2], so
        # q·n + r + 1 ≡ r + 1 (mod n). Since r ∈ [0, n-2], r+1 ∈ [1, n-1],
        # and r+1 ≢ 0 (mod n). So v_n of inner is 0, hence v_n(m) = 1.
        # Thus ALL n-primes have ν_n(m) = 1 (height 1, atoms of M_n).
        # Q_n at height 1 is just 1 (single j=1 term, τ_1 = 1).
        h = 1
        Q = 1
        rows.append((n, K, m, h, Q))
        print(f'  n={n}, K={K}: m=p_K(n)={m} '
              f'(base-10 digits: {digit_length(m, 10)}), '
              f'ν_n(m)={h}, Q_n(m)={Q}')

    with open(os.path.join(out_dir, 'exp5_finite_rank_consistency.csv'),
              'w', newline='') as f:
        csv.writer(f).writerows(rows)
    print(f'  All n-primes have ν_n(m) = 1 (atoms of M_n).')
    print(f'  Q_n(p_K(n)) = 1 for all K. The lemma at h=1 holds vacuously '
          f'and is independent of K. Deep-Q tests need composite m ∈ M_n with '
          f'ν_n(m) ≥ 2 — start by multiplying n-primes, then measure ν_n(m).')


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))

    smoke_check()
    exp_deep_window_vs_prefix(out_dir)
    exp_boundary_stitch_persists(out_dir)
    exp_block_boundary_at_depth(out_dir)
    exp_digit_oracle(out_dir)
    exp_finite_rank_consistency(out_dir)

    print('\ndone.', flush=True)


if __name__ == '__main__':
    main()
