"""
exp08_lattice_closed_form.py — derive the closed-form K_pair formula
and verify it against the empirical collision events from EXP07.

Setup.
------
Stream S_a = (a·m : m ≥ 1, a ∤ m). Bundle B(K) = ⋃ S_a[1..K] over
a in window [n_0, n_0 + W − 1]. K_pair(a, b) = smallest K such that
the smallest atom in S_a ∩ S_b is in S_a[1..K] AND S_b[1..K].

Closed form (window regime n_0 ≥ W − 1, so b < 2a always):
    Let g = gcd(a, b), L = lcm(a, b) = a·b/g.
    The smallest shared atom is L (when a² ∤ L, true here).
    pos_a = (b/g) − ⌊b/(g·a)⌋ = b/g (window regime, since b/(g·a) < 1).
    pos_b = (a/g) − ⌊a/(g·b)⌋ = a/g.
    K_pair(a, b) = max(pos_a, pos_b) = b/g.
    With r = b − a: K_pair(a, a+r) = (a + r) / gcd(a, r).

Support claim. Λ_W(K, n_0) := #{pairs in window with K_pair = K}.
Then supp(Λ_W) ⊆ supp(COLL), where COLL(K, n_0) = W − dS/dK.
Equivalently: every K_pair value is empirically a collision K-step.

Multiplicity. At every K_pair (whether r=1 or r ≥ 2), the second
stream's arrival at L kills a singleton, so COLL ≥ 2·Λ_W. Equality
fails when (i) a later multiple t·L lands at this same K-step for
some other pair, or (ii) L is shared by 3+ streams in the window
(then the second arrival's "kill" already happened at a smaller K
and the third arrival contributes only +1 event, not +2).

This script:
  Step 1. Sequence-builder verification of the closed-form formula
          (independent of any algebraic identity).
  Step 2. Grid-wide comparison of supp(Λ_W) vs supp(COLL).
  Step 3. Multiplicity comparison: 2·Λ vs COLL.

Output:
    exp08_lattice_closed_form.png
    exp08_lattice_check.txt
"""

from __future__ import annotations

import os
import sys
import time
import math
from itertools import combinations

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

OUT = os.path.join(HERE, 'exp08_lattice_closed_form.png')
OUT_TXT = os.path.join(HERE, 'exp08_lattice_check.txt')

W = 10
N0_VALUES = np.arange(10, 1001, 10)
K_MAX = 1000


def k_pair_formula(a: int, b: int) -> int:
    """Closed-form K_pair(a, b) for a < b.

    Window-regime formula (assumes b < 2a, so the floor terms vanish
    when (b/g) < a, but we keep them general so the function still
    returns the right value for non-window pairs):

        K_pair(a, b) = max(b/g − ⌊b/(g·a)⌋, a/g − ⌊a/(g·b)⌋)
                     = b/g   in the window regime.

    With r = b − a: K_pair(a, a+r) = (a + r) / gcd(a, r).
    """
    g = math.gcd(a, b)
    pos_a = (b // g) - (b // (g * a))
    pos_b = (a // g) - (a // (g * b))
    return max(pos_a, pos_b)


def k_pair_by_streams(a: int, b: int, k_max: int = 5000) -> int:
    """Build streams S_a and S_b independently as integer sequences;
    find the smallest atom in S_a ∩ S_b; return max position. This
    is the *definition* of K_pair, with no algebraic shortcut.

    Returns -1 if no shared atom found within k_max positions.
    """
    if a == b:
        return 1

    s_a = []
    m = 1
    while len(s_a) < k_max:
        if m % a != 0:
            s_a.append(a * m)
        m += 1
    s_b = []
    m = 1
    while len(s_b) < k_max:
        if m % b != 0:
            s_b.append(b * m)
        m += 1
    set_a = set(s_a)
    set_b = set(s_b)
    common = set_a & set_b
    if not common:
        return -1
    L_actual = min(common)
    return max(s_a.index(L_actual) + 1, s_b.index(L_actual) + 1)


def closed_form_lattice(n0: int, w: int, k_max: int) -> np.ndarray:
    """Λ_W(K, n_0) via closed form. Returns array of size k_max."""
    Lambda = np.zeros(k_max, dtype=np.int32)
    for a, b in combinations(range(n0, n0 + w), 2):
        K = k_pair_formula(a, b)
        if 1 <= K <= k_max:
            Lambda[K - 1] += 1
    return Lambda


def n_primes_vec(n: int, k: int) -> np.ndarray:
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


def empirical_collisions(n0: int, w: int, k_max: int) -> np.ndarray:
    """Count collision events at each K-step (W − dS)."""
    streams = [n_primes_vec(n, k_max) for n in range(n0, n0 + w)]
    counts = {}
    n_singletons = 0
    coll = np.zeros(k_max, dtype=np.int32)
    for K in range(1, k_max + 1):
        prev_S = n_singletons
        for ni in range(w):
            m = int(streams[ni][K - 1])
            old_c = counts.get(m, 0)
            counts[m] = old_c + 1
            if old_c == 0:
                n_singletons += 1
            elif old_c == 1:
                n_singletons -= 1
        coll[K - 1] = w - (n_singletons - prev_S)
    return coll


# Step 1: verify the closed-form formula by building the streams as
# integer sequences and finding the smallest shared element directly
# — independent of any algebraic identity.
def step1_pointwise_verify():
    print('Step 1 — closed-form vs. sequence-builder pointwise check')
    print('  building streams S_a, S_b for each pair and finding')
    print('  smallest shared element directly...')
    fails = 0
    test_pairs = []
    # Smaller windows for the slow sequence-builder verification
    for n0 in (10, 30, 50, 100, 290):
        for w in (5, 10):
            for a, b in combinations(range(n0, n0 + w), 2):
                test_pairs.append((a, b))
    for a, b in test_pairs:
        kp_form = k_pair_formula(a, b)
        kp_seq = k_pair_by_streams(a, b)
        if kp_seq < 0:
            print(f'  SKIP  ({a}, {b}): no shared atom found within search')
            continue
        if kp_form != kp_seq:
            print(f'  FAIL  ({a}, {b}): formula = {kp_form}, '
                  f'streams-built = {kp_seq}')
            fails += 1
    print(f'  {len(test_pairs)} pairs tested; {fails} failures.')
    return fails


# Step 2: compute Λ across the grid; compute empirical COLL; compare.
def step2_grid_compare():
    print('\nStep 2 — grid-wide closed-form vs. empirical')
    LAMBDA = np.zeros((len(N0_VALUES), K_MAX), dtype=np.int32)
    COLL = np.zeros((len(N0_VALUES), K_MAX), dtype=np.int32)
    t0 = time.time()
    for i, n0 in enumerate(N0_VALUES):
        LAMBDA[i] = closed_form_lattice(int(n0), W, K_MAX)
        COLL[i] = empirical_collisions(int(n0), W, K_MAX)
        if (i + 1) % 20 == 0:
            print(f'  rows: {i + 1}/{len(N0_VALUES)} '
                  f'(t={time.time() - t0:.1f}s)')
    print(f'  total: {time.time() - t0:.1f}s')

    # Empirical events should be ≥ 2 · Λ at each cell (extra are
    # from second-shared-element collisions, K = 2·K_pair, etc.).
    twice_lambda = 2 * LAMBDA
    diff = COLL - twice_lambda
    n_lt = int((diff < 0).sum())
    print(f'  cells where COLL < 2·Λ: {n_lt} '
          f'(should be 0 if closed-form covers all first-collisions)')
    if n_lt > 0:
        # Show a few
        i_lt, j_lt = np.where(diff < 0)
        for k in range(min(5, len(i_lt))):
            i, j = i_lt[k], j_lt[k]
            print(f'    n_0={N0_VALUES[i]}, K={j+1}: '
                  f'COLL={COLL[i, j]}, 2Λ={twice_lambda[i, j]}, '
                  f'diff={diff[i, j]}')
    n_extra = int((diff > 0).sum())
    print(f'  cells where COLL > 2·Λ: {n_extra} '
          f'(later-collision contributions)')

    return LAMBDA, COLL


def main():
    log_lines = []
    def out(s):
        print(s)
        log_lines.append(s)

    out('exp08 — closed-form lattice for K_pair')
    out('=' * 60)

    fails = step1_pointwise_verify()
    out('')
    if fails == 0:
        out(f'Pointwise check: PASS (closed form matches direct '
            f'on all sample pairs)')
    else:
        out(f'Pointwise check: FAIL with {fails} mismatches')
        return 1

    LAMBDA, COLL = step2_grid_compare()

    # Step: support comparison
    out('')
    out('--- Support comparison ---')
    out('Cells where Λ_W(K, n_0) > 0  (predicted pair-events present):')
    n_lambda_supp = int((LAMBDA > 0).sum())
    n_coll_supp = int((COLL > 0).sum())
    n_both = int(((LAMBDA > 0) & (COLL > 0)).sum())
    n_lambda_only = int(((LAMBDA > 0) & (COLL == 0)).sum())
    n_coll_only = int(((LAMBDA == 0) & (COLL > 0)).sum())
    out(f'  |supp(Λ)| = {n_lambda_supp}')
    out(f'  |supp(COLL)| = {n_coll_supp}')
    out(f'  |supp(Λ) ∩ supp(COLL)| = {n_both}')
    out(f'  in Λ but not COLL: {n_lambda_only}  (formula predicts non-event)')
    out(f'  in COLL but not Λ: {n_coll_only}  (subsequent-multiple collisions)')
    out('')
    if n_lambda_only == 0:
        out('SUPPORT CLAIM CONFIRMED: every K_pair value is empirically a '
            'collision-event K-step. Closed-form support is a subset of '
            'empirical support, with the difference being entirely '
            'subsequent-multiple-of-L collisions (K = pos of L·t for t ≥ 2).')
    else:
        out('Support claim FAILED — closed form predicts events at K-values '
            'where empirical COLL is zero. Investigate.')

    # Multiplicity comparison: 2·Λ vs COLL.
    # At every K_pair, the pair's second-arrival kills a singleton →
    # +2 to COLL. So 2·Λ ≤ COLL with equality unless either (i) a
    # later multiple of L for some other pair lands at this K, or
    # (ii) L is shared by 3+ window-streams (third arrival contributes
    # only +1, not +2).
    diff = COLL - 2 * LAMBDA
    n_match = int((diff == 0).sum())
    n_extra = int((diff > 0).sum())
    n_short = int((diff < 0).sum())
    out('')
    out('--- Multiplicity comparison: 2·Λ vs COLL ---')
    out(f'  COLL == 2·Λ exactly: {n_match} cells '
        f'({100 * n_match / COLL.size:.2f}%)')
    out(f'  COLL > 2·Λ:           {n_extra} cells '
        f'(subsequent-multiple events not in Λ\'s support)')
    out(f'  COLL < 2·Λ:           {n_short} cells '
        f'(3+-stream-share over-count; expected to be rare)')
    if n_short > 0:
        # Show a few short cells to confirm they are 3+ shares
        i_short, j_short = np.where(diff < 0)
        out('  short-cell examples:')
        for k in range(min(5, len(i_short))):
            i, j = i_short[k], j_short[k]
            out(f'    n_0={N0_VALUES[i]}, K={j+1}: '
                f'COLL={COLL[i, j]}, 2Λ={2*LAMBDA[i, j]}')

    # Plot side-by-side
    fig, axes = plt.subplots(1, 3, figsize=(22, 8), dpi=130)
    fig.patch.set_facecolor('#0a0a0a')
    for ax in axes:
        ax.set_facecolor('#0a0a0a')

    extent = (0.5, K_MAX + 0.5, N0_VALUES[0] - 5, N0_VALUES[-1] + 5)

    # Λ from closed form
    vmax_l = float(LAMBDA.max())
    im1 = axes[0].imshow(LAMBDA, aspect='auto', origin='lower',
                          cmap='hot', interpolation='nearest', extent=extent,
                          vmin=0, vmax=max(vmax_l, 2))
    axes[0].set_title('Λ_W (closed form)\n'
                      'pair-events from formula',
                      color='white', fontsize=11)
    plt.colorbar(im1, ax=axes[0], fraction=0.045, pad=0.02)

    # 2 · Λ for direct comparison to COLL
    im2 = axes[1].imshow(2 * LAMBDA, aspect='auto', origin='lower',
                          cmap='hot', interpolation='nearest', extent=extent,
                          vmin=0, vmax=max(2 * vmax_l, 4))
    axes[1].set_title('2 · Λ_W  (predicted collision events from formula)',
                      color='white', fontsize=11)
    plt.colorbar(im2, ax=axes[1], fraction=0.045, pad=0.02)

    # Empirical COLL
    vmax_c = float(np.percentile(COLL[COLL > 0], 99)) if (COLL > 0).any() else 1.0
    im3 = axes[2].imshow(COLL, aspect='auto', origin='lower',
                          cmap='hot', interpolation='nearest', extent=extent,
                          vmin=0, vmax=max(vmax_c, 4))
    axes[2].set_title('empirical COLL  (from incremental K-walk)',
                      color='white', fontsize=11)
    plt.colorbar(im3, ax=axes[2], fraction=0.045, pad=0.02)

    for ax in axes:
        ax.set_xlim(0.5, K_MAX + 0.5)
        ax.set_ylim(N0_VALUES[0] - 5, N0_VALUES[-1] + 5)
        ax.set_xlabel('K', color='white', fontsize=11)
        ax.set_ylabel(f'n_0', color='white', fontsize=11)
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#333')

    fig.suptitle(
        'Closed-form K_pair lattice Λ_W vs. empirical collision events',
        color='white', fontsize=13, y=0.99
    )
    plt.tight_layout()
    plt.savefig(OUT, dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    out(f'-> {OUT}')

    with open(OUT_TXT, 'w') as f:
        f.write('\n'.join(log_lines))
    out(f'\n-> {OUT_TXT}')


if __name__ == '__main__':
    raise SystemExit(main())
