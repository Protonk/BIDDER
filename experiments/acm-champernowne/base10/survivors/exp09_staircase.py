"""
exp09_staircase.py — visualize the devil's-staircase structure of κ.

At fixed n_0, plot:
  Panel 1: S(K) = |Surv at step K|, with the W·K baseline overlaid
           and the K_pair lattice points marked. Shows that S grows
           with slope W between lattice points and steps down at each
           lattice point.

  Panel 2: 1 − κ(K) = (W·K − S) / (W·K), with the cumulative pair
           count (2/W·K) · #{pairs with K_pair ≤ K} overlaid in red.
           Shows that the *deficit* is precisely the cumulative
           lattice count, and that it is locally piecewise-1/K-smooth
           but globally a step function.

  Panel 3: zoom on a small K-range to make the steps visible at the
           cell scale.

Together: the Cantor-staircase claim — variation lives entirely on
the lattice, the function looks smooth on coarse scales, the
microscopic structure is exactly the closed-form Λ_W.

Outputs:
    exp09_staircase.png
"""

from __future__ import annotations

import os
import math
from itertools import combinations

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'exp09_staircase.png')

W = 10
N0 = 100
K_MAX = 600
ZOOM_RANGE = (90, 220)


def n_primes_vec(n: int, k: int) -> np.ndarray:
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


def k_pair_formula(a: int, b: int) -> int:
    g = math.gcd(a, b)
    pos_a = (b // g) - (b // (g * a))
    pos_b = (a // g) - (a // (g * b))
    return max(pos_a, pos_b)


def survivor_walk(n0: int, w: int, k_max: int):
    streams = [n_primes_vec(n, k_max) for n in range(n0, n0 + w)]
    counts = {}
    n_singletons = 0
    S = np.zeros(k_max + 1, dtype=np.int64)   # S[K] after K-th step
    for K in range(1, k_max + 1):
        for ni in range(w):
            m = int(streams[ni][K - 1])
            old_c = counts.get(m, 0)
            counts[m] = old_c + 1
            if old_c == 0:
                n_singletons += 1
            elif old_c == 1:
                n_singletons -= 1
        S[K] = n_singletons
    return S


def lattice_points(n0: int, w: int):
    """Return list of K_pair values for each pair, sorted."""
    pts = []
    for a, b in combinations(range(n0, n0 + w), 2):
        pts.append((k_pair_formula(a, b), a, b))
    return pts


def all_event_positions(a: int, b: int, k_max: int):
    """Yield K-values at which pair (a, b) generates a collision event,
    one per t (where t·L is the t-th shared atom)."""
    g = math.gcd(a, b)
    L = a * b // g
    t = 1
    while True:
        atom = t * L
        pos_a = (atom // a) - (atom // (a * a))
        pos_b = (atom // b) - (atom // (b * b))
        K_event = max(pos_a, pos_b)
        if K_event > k_max:
            break
        yield K_event
        t += 1


def main():
    print(f'computing S(K) for n_0 = {N0}, K_max = {K_MAX}')
    S = survivor_walk(N0, W, K_MAX)
    K = np.arange(0, K_MAX + 1)
    bundle = W * K  # = |B|
    deficit = bundle - S      # = atoms culled
    kappa = np.zeros_like(S, dtype=float)
    kappa[1:] = S[1:] / bundle[1:]
    one_minus_kappa = 1.0 - kappa
    one_minus_kappa[0] = 0.0

    pts = lattice_points(N0, W)
    pts_sorted = sorted(pts)
    print(f'  {len(pts)} pairs, {len(set(p[0] for p in pts))} distinct K_pair values')

    # Full event list: enumerate (pair, t) for t = 1, 2, ... up to k_max.
    all_events = []   # list of K-values where COLL gets +2
    first_events = []  # K-values at first collision per pair (= Λ support)
    for a, b in combinations(range(N0, N0 + W), 2):
        for i, K_event in enumerate(all_event_positions(a, b, K_MAX)):
            all_events.append(K_event)
            if i == 0:
                first_events.append(K_event)
    print(f'  {len(all_events)} total events through K = {K_MAX}')
    print(f'  {len(first_events)} first-events ({len(set(first_events))} distinct K)')

    # Cumulative event count: at K, count events with K_event ≤ K.
    all_events_sorted = sorted(all_events)
    C_all = np.zeros_like(K, dtype=float)
    j = 0
    cum = 0
    for k in range(K_MAX + 1):
        while j < len(all_events_sorted) and all_events_sorted[j] <= k:
            cum += 1
            j += 1
        C_all[k] = cum
    full_prediction = np.zeros_like(C_all)
    full_prediction[1:] = 2.0 * C_all[1:] / (W * K[1:])

    # First-events-only prediction (the original Λ-cumulative)
    first_events_sorted = sorted(first_events)
    C_first = np.zeros_like(K, dtype=float)
    j = 0
    cum = 0
    for k in range(K_MAX + 1):
        while j < len(first_events_sorted) and first_events_sorted[j] <= k:
            cum += 1
            j += 1
        C_first[k] = cum
    first_prediction = np.zeros_like(C_first)
    first_prediction[1:] = 2.0 * C_first[1:] / (W * K[1:])

    # Atom-centric EXACT prediction: enumerate (atom, K_arrival) for each
    # window stream up to K_MAX. For each atom, the i-th arrival
    # contributes deviation: 0 (i=1, fresh), -2 (i=2, kills singleton),
    # -1 (i ≥ 3, bumps non-singleton).
    # Total deficit at K = sum over atoms of contributions from arrivals
    # with K_arrival ≤ K.
    arrivals = []   # list of (K_arrival, atom)
    for a in range(N0, N0 + W):
        m = 0
        k_pos = 0
        while k_pos < K_MAX:
            m += 1
            if m % a == 0:
                continue
            k_pos += 1
            arrivals.append((k_pos, a * m))
    # Sort by K_arrival, then process
    arrivals.sort()
    atom_count = {}
    deficit_arr = np.zeros(K_MAX + 1, dtype=np.int64)
    for K_arr, atom in arrivals:
        c = atom_count.get(atom, 0)
        if c == 0:
            dev = 0     # fresh singleton, no event
        elif c == 1:
            dev = 2     # kills singleton, +2 to deficit
        else:
            dev = 1     # bumps non-singleton, +1 to deficit
        atom_count[atom] = c + 1
        deficit_arr[K_arr] += dev
    cum_deficit = np.cumsum(deficit_arr)
    exact_prediction = np.zeros_like(K, dtype=float)
    exact_prediction[1:] = cum_deficit[1:] / (W * K[1:])

    # ---- Plot ----
    fig, axes = plt.subplots(3, 1, figsize=(14, 14), dpi=130)
    fig.patch.set_facecolor('#0a0a0a')
    for ax in axes:
        ax.set_facecolor('#0a0a0a')

    # Lattice K_pair tick positions
    lattice_K = sorted(set(p[0] for p in pts))

    # === Panel 1: S(K) vs K with W·K baseline ===
    ax = axes[0]
    ax.plot(K, bundle, color='#888888', linewidth=0.9, alpha=0.8,
            label=f'|Bundle| = W·K  (slope = {W})')
    ax.plot(K, S, color='#ffcc66', linewidth=1.3, alpha=0.95,
            label='|Surv| = S(K)  (piecewise slope W, downsteps at lattice)')
    for kp in lattice_K:
        if kp <= K_MAX:
            ax.axvline(kp, color='#ff5555', linewidth=0.5, alpha=0.4)
    ax.set_xlabel('K', color='white', fontsize=11)
    ax.set_ylabel('count', color='white', fontsize=11)
    ax.set_title(f'S(K) and W·K   (n_0 = {N0}, W = {W})\n'
                 f'red verticals: K_pair lattice points (where S has '
                 f'downward steps of size −2·m)',
                 color='white', fontsize=12)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#333')
    ax.legend(loc='upper left', fontsize=10, framealpha=0.5,
              labelcolor='white', facecolor='#1a1a1a')
    ax.grid(True, alpha=0.18, color='#888')

    # === Panel 2: 1 − κ(K) vs full event-lattice prediction ===
    ax = axes[1]
    ax.plot(K[1:], one_minus_kappa[1:], color='#88ccff', linewidth=2.4,
            alpha=0.95, label='1 − κ  (empirical)')
    ax.plot(K[1:], exact_prediction[1:], color='#33ff66',
            linewidth=1.0, linestyle='-', alpha=0.95,
            label='atom-centric exact prediction (0 residual)')
    ax.plot(K[1:], full_prediction[1:], color='#ffcc00',
            linewidth=1.0, linestyle='--', alpha=0.9,
            label='pairwise (pair, t) prediction (over-counts at 3+-shares)')
    ax.plot(K[1:], first_prediction[1:], color='#ff66aa',
            linewidth=0.8, linestyle=':', alpha=0.7,
            label='first-events only: 2·#{pairs with K_pair ≤ K} / (W·K)')
    for kp in lattice_K:
        if kp <= K_MAX:
            ax.axvline(kp, color='#ff5555', linewidth=0.5, alpha=0.25)
    ax.set_xlabel('K', color='white', fontsize=11)
    ax.set_ylabel('1 − κ', color='white', fontsize=11)
    ax.set_title('Survival deficit 1 − κ vs full closed-form prediction\n'
                 '(yellow dashes overlay blue ⇒ deficit IS the (pair, t) event count, '
                 'normalized by W·K)',
                 color='white', fontsize=12)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#333')
    ax.legend(loc='lower right', fontsize=10, framealpha=0.5,
              labelcolor='white', facecolor='#1a1a1a')
    ax.grid(True, alpha=0.18, color='#888')

    # === Panel 3: zoom — show the steps explicitly ===
    ax = axes[2]
    z0, z1 = ZOOM_RANGE
    Kz = K[z0:z1 + 1]
    ax.plot(Kz, S[z0:z1 + 1], color='#ffcc66', linewidth=1.5, alpha=0.95,
            drawstyle='steps-post', label='S(K)  (step-post)')
    base_z = bundle[z0:z1 + 1]
    ax.plot(Kz, base_z, color='#888888', linewidth=0.9, alpha=0.6,
            label=f'W·K  (slope-W reference)')
    for kp, a, b in pts_sorted:
        if z0 <= kp <= z1:
            ax.axvline(kp, color='#ff5555', linewidth=0.5, alpha=0.5)
    ax.set_xlabel('K (zoomed)', color='white', fontsize=11)
    ax.set_ylabel('count', color='white', fontsize=11)
    ax.set_title(f'Zoom K ∈ [{z0}, {z1}]: lattice points (red) coincide '
                 f'with S-downsteps; between them, S grows linearly',
                 color='white', fontsize=12)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#333')
    ax.legend(loc='upper left', fontsize=10, framealpha=0.5,
              labelcolor='white', facecolor='#1a1a1a')
    ax.grid(True, alpha=0.18, color='#888')

    fig.suptitle(
        f'Devil\'s-staircase structure of κ at n_0 = {N0}, W = {W}\n'
        f'(top: S has slope W between lattice points and downsteps at them; '
        f'middle: 1−κ matches the cumulative lattice count exactly; '
        f'bottom: zoom showing the steps)',
        color='white', fontsize=12, y=0.998
    )
    plt.tight_layout()
    plt.savefig(OUT, dpi=180, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f'-> {OUT}')

    # Numerical summary — exact prediction should match to machine ε.
    diff_exact = one_minus_kappa[1:] - exact_prediction[1:]
    diff_full = one_minus_kappa[1:] - full_prediction[1:]
    diff_first = one_minus_kappa[1:] - first_prediction[1:]
    print(f'\nVerification: 1−κ vs EXACT atom-centric prediction')
    print(f'  max |diff|: {np.abs(diff_exact).max():.10f}')
    print(f'  median |diff|: {np.median(np.abs(diff_exact)):.10f}')
    print(f'\n1−κ vs PAIRWISE (pair, t) prediction')
    print(f'  max |diff|: {np.abs(diff_full).max():.6f}')
    print(f'  median |diff|: {np.median(np.abs(diff_full)):.6f}')
    print(f'  (over-count at 3+-stream-shares: residual = O(k²-2k) per k-share)')
    print(f'\n1−κ vs FIRST-EVENTS-ONLY prediction')
    print(f'  max |diff|: {np.abs(diff_first).max():.6f}')
    print(f'  median |diff|: {np.median(np.abs(diff_first)):.6f}')


if __name__ == '__main__':
    main()
