"""
exp14_prime_convergence_reframe.py — K = K(W) reframe via closed form.

EXP06 sketched the question: for what K(W) does the survivor set
converge to primes-in-window? Empirically composite survivors GREW
with W (with a dip at W ≈ K). The closed form (Theorem 1) lets us
answer the question structurally.

DECOMPOSITION OF SURVIVORS at parameters (n_0, W, K).

Each atom in the bundle B(K, n_0) is either:

  P_W  = prime in window (always a singleton — only its own stream
         touches it).
  C_W  = composite in window (its smallest factor < n_0, so no other
         WINDOW stream touches it; singleton).
  T_A  = composite with ≥ 2 window-divisors that ARE both reached
         within K-positions. CULLED.
  T_A_partial = composite with ≥ 2 window-divisors but only one with
         position ≤ K. SURVIVOR (singleton in B by virtue of partial
         coverage).
  T_B_low  = composite with exactly 1 window-divisor d, smallest
         coprime cofactor q = c/d < n_0. Position in stream d is
         ≈ q < n_0 ≤ K. ALWAYS in B as singleton at K ≥ small q.
         Cannot be culled (only one window-stream contains it).
  T_B_high = composite with exactly 1 window-divisor d, cofactor
         q > n_0 + W − 1. Position is ≈ q > K typically. Excluded
         from B unless K is large.

For prime convergence we want |Surv| / |P_W| → 1. The components
that matter:

  C_W is intrinsic to the window; can't be removed.
  T_A_partial is removable by raising K to the second-largest
         position threshold for c.
  T_B_low is permanent at any K large enough to admit window pairs.
  T_B_high is suppressed at K < max q in (n_0+W-1, range].

This script computes the decomposition for several K(W) scalings:

    K = n_0 + W − 1     "natural" — kills Type-A semiprimes
    K = W               EXP06's "K = W" suggestion
    K = (n_0 + W) / 2   half-natural
    K = 2 (n_0 + W)     overshoot (admits more T_B_high)

Plot:
  Panel 1: |Surv| breakdown vs W at fixed n_0.
  Panel 2: prime fraction vs W at fixed n_0.
  Panel 3: T_B_low contribution vs W (the irremovable composites).
  Panel 4: composite-survivor count comparison across K(W) scalings.

Output:
    exp14_prime_convergence_reframe.png
    exp14_decomposition.txt
"""

from __future__ import annotations

import os
import time
import math
from itertools import combinations

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'exp14_prime_convergence_reframe.png')
OUT_TXT = os.path.join(HERE, 'exp14_decomposition.txt')

N0_LIST = [25, 50, 100]
W_RANGE = list(range(2, 401, 5))   # window widths


def n_primes_vec(n: int, k: int) -> np.ndarray:
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


def sieve_primes_up_to(N: int) -> np.ndarray:
    s = np.ones(N + 1, dtype=bool)
    s[:2] = False
    for i in range(2, int(N ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = False
    return s


def build_bundle(n0: int, w: int, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Return (atoms, stream_index) — m_arr in stream-block order."""
    parts = [n_primes_vec(n, k) for n in range(n0, n0 + w)]
    atoms = np.concatenate(parts)
    stream_idx = np.concatenate([
        np.full(p.size, i, dtype=np.int32) for i, p in enumerate(parts)
    ])
    return atoms, stream_idx


def decompose_survivors(n0: int, w: int, k: int,
                        prime_sieve: np.ndarray) -> dict:
    """Decompose B(K, n_0) survivors into structural categories."""
    atoms, stream_idx = build_bundle(n0, w, k)
    n_atoms = atoms.size
    if n_atoms == 0:
        return {}

    # Build mult and survivor mask.
    uniq, inverse, counts = np.unique(atoms, return_inverse=True,
                                       return_counts=True)
    mult = counts[inverse]                 # multiplicity per atom-instance
    is_singleton = mult == 1

    # We want to characterize each unique atom once. Use the index
    # of its first occurrence.
    _, first_idx = np.unique(atoms, return_index=True)
    survivors = uniq[mult[first_idx] == 1]
    n_surv = survivors.size

    n1 = n0 + w - 1
    # Decompose survivors:
    n_prime_window = 0
    n_composite_window = 0
    n_typeB_low = 0
    n_typeB_high = 0
    n_typeA_partial = 0
    n_other = 0

    # For each survivor c, find its window-divisors and classify.
    # Use np.gcd-style enumeration: divisors of c in [n_0, n_1] are
    # found by iterating d from n_0 to min(c, n_1) and checking d | c.
    # For efficiency we batch by checking which streams emit c.

    # Build dict: atom -> list of stream indices that emitted it.
    atom_streams: dict[int, list[int]] = {}
    for idx in range(n_atoms):
        a = int(atoms[idx])
        atom_streams.setdefault(a, []).append(int(stream_idx[idx]))

    # For each survivor c, atom_streams[c] has length 1 (the one stream
    # that emitted c with position ≤ K).
    for c in survivors:
        c = int(c)
        em_streams = atom_streams[c]
        # The window-divisor that's confirmed in B
        d_in_B = n0 + em_streams[0]  # since stream_idx 0 → n_0, etc.

        # Now find ALL window-divisors of c (whether or not they're in B)
        # and the cofactors c/d.
        all_window_divisors = []
        all_pos = []
        for d in range(n0, n1 + 1):
            if c % d == 0:
                m_val = c // d
                if m_val % d != 0:  # d² ∤ c, so c is a valid stream-d atom
                    all_window_divisors.append(d)
                    all_pos.append(m_val - m_val // d)  # exact position

        n_window_div = len(all_window_divisors)

        # Classify
        if c >= n0 and c <= n1:
            # In-window atom
            if prime_sieve[c]:
                n_prime_window += 1
            else:
                n_composite_window += 1
        else:
            # Out-of-window composite (or large prime, but primes have
            # no window-divisor unless they themselves are in window —
            # handled above).
            if n_window_div >= 2:
                # Type A partial: has multiple window-divisors but
                # only one's position ≤ K.
                n_typeA_partial += 1
            else:
                # Type B: exactly 1 window-divisor.
                d = d_in_B
                m_val = c // d
                # m_val is the cofactor. Could be prime or composite.
                if m_val < n0:
                    n_typeB_low += 1
                elif m_val > n1:
                    n_typeB_high += 1
                else:
                    # m_val is in window — but we said only 1 window-divisor.
                    # This means m_val = c/d is not a divisor (because
                    # m_val² ∤ c is the condition, i.e., m_val | (c/m_val)
                    # would mean d = c/m_val is a multiple of m_val).
                    # Could happen for c = d · m_val with d, m_val both
                    # in window but somehow not both window-divisors of c.
                    # Probably edge case: count as "other".
                    n_other += 1

    return {
        'n_atoms': int(n_atoms),
        'n_surv': int(n_surv),
        'n_prime_window': int(n_prime_window),
        'n_composite_window': int(n_composite_window),
        'n_typeA_partial': int(n_typeA_partial),
        'n_typeB_low': int(n_typeB_low),
        'n_typeB_high': int(n_typeB_high),
        'n_other': int(n_other),
        'max_atom': int(atoms.max()) if atoms.size > 0 else 0,
    }


SCALINGS = [
    ('K = n_0 + W − 1   (Type-A threshold)',
     lambda n0, w: n0 + w - 1),
    ('K = W              (EXP06 suggestion)',
     lambda n0, w: w),
    ('K = (n_0 + W) / 2  (half natural)',
     lambda n0, w: max(1, (n0 + w) // 2)),
    ('K = 2(n_0 + W)     (overshoot)',
     lambda n0, w: 2 * (n0 + w)),
]


def main():
    log = []
    def out(s):
        print(s)
        log.append(s)

    # Build prime sieve up to max possible atom
    max_n0 = max(N0_LIST)
    max_w = max(W_RANGE)
    max_K_used = 2 * (max_n0 + max_w)
    max_atom = max_K_used * (max_n0 + max_w)
    out(f'Building prime sieve up to {max_atom}')
    prime_sieve = sieve_primes_up_to(max_atom + 100)

    out(f'EXP14 — K = K(W) prime convergence reframe')
    out(f'  n_0 ∈ {N0_LIST}, W ∈ [{W_RANGE[0]}, {W_RANGE[-1]}]')

    # Run decomposition for each scaling and each (n_0, W)
    results: dict[tuple[str, int], list[dict]] = {}

    for scaling_name, scaling_fn in SCALINGS:
        out(f'\n--- Scaling: {scaling_name} ---')
        for n0 in N0_LIST:
            t0 = time.time()
            data = []
            for w in W_RANGE:
                k = scaling_fn(n0, w)
                if k < 1:
                    data.append(None)
                    continue
                d = decompose_survivors(n0, w, k, prime_sieve)
                d['K'] = k
                d['W'] = w
                d['n0'] = n0
                data.append(d)
            elapsed = time.time() - t0
            results[(scaling_name, n0)] = data
            last = data[-1]
            if last:
                out(f'  n_0 = {n0}: W = {last["W"]}, K = {last["K"]}, '
                    f'|Surv| = {last["n_surv"]}, primes = '
                    f'{last["n_prime_window"]}, comp_in_window = '
                    f'{last["n_composite_window"]}, '
                    f'typeA_partial = {last["n_typeA_partial"]}, '
                    f'typeB_low = {last["n_typeB_low"]}, '
                    f'typeB_high = {last["n_typeB_high"]}  '
                    f'({elapsed:.1f}s)')

    # ---- Plot ----
    fig = plt.figure(figsize=(20, 14), dpi=130)
    fig.patch.set_facecolor('#0a0a0a')
    gs = fig.add_gridspec(3, 4, hspace=0.32, wspace=0.28)

    n0_focus = N0_LIST[1]  # 50

    # Row 1: composition stacked area chart for the natural scaling
    nat_name, _ = SCALINGS[0]
    for col, n0 in enumerate(N0_LIST):
        ax = fig.add_subplot(gs[0, col])
        ax.set_facecolor('#0a0a0a')
        data = results[(nat_name, n0)]
        ws = [d['W'] for d in data if d]
        primes = [d['n_prime_window'] for d in data if d]
        comp_in = [d['n_composite_window'] for d in data if d]
        tA = [d['n_typeA_partial'] for d in data if d]
        tB_low = [d['n_typeB_low'] for d in data if d]
        tB_high = [d['n_typeB_high'] for d in data if d]
        other = [d['n_other'] for d in data if d]

        ax.stackplot(ws, primes, comp_in, tA, tB_low, tB_high, other,
                     labels=['primes in window',
                             'composites in window',
                             'Type-A partial (≥2 wd, undercounted)',
                             'Type-B low-q (cofactor < n_0)',
                             'Type-B high-q (cofactor > n_1)',
                             'other'],
                     colors=['#33ff66', '#88ccff', '#ffaa66',
                             '#ff6677', '#ff66ee', '#888888'],
                     alpha=0.85)
        ax.set_title(f'n_0 = {n0}   (K = n_0 + W − 1)',
                     color='white', fontsize=11)
        ax.set_xlabel('W', color='white', fontsize=10)
        ax.set_ylabel('|Surv|', color='white', fontsize=10)
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#333')
        ax.grid(True, alpha=0.18, color='#888')
        if col == 0:
            ax.legend(loc='upper left', fontsize=8, framealpha=0.4,
                      labelcolor='white', facecolor='#1a1a1a')
        ax.set_yscale('log')
        ax.set_ylim(bottom=1)

    # Last column: prime fraction vs W (focal n_0)
    ax = fig.add_subplot(gs[0, 3])
    ax.set_facecolor('#0a0a0a')
    data = results[(nat_name, n0_focus)]
    ws = [d['W'] for d in data if d]
    fracs = [d['n_prime_window'] / max(d['n_surv'], 1) for d in data if d]
    ax.plot(ws, fracs, color='#33ff66', linewidth=1.5,
             label=f'primes / |Surv| at n_0 = {n0_focus}')
    ax.set_title(f'Prime fraction vs W   (n_0 = {n0_focus}, K = nat)',
                 color='white', fontsize=11)
    ax.set_xlabel('W', color='white', fontsize=10)
    ax.set_ylabel('|primes| / |Surv|', color='white', fontsize=10)
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('#333')
    ax.grid(True, alpha=0.18, color='#888')
    ax.set_ylim(0, 1)
    ax.legend(loc='upper right', fontsize=9, framealpha=0.4,
              labelcolor='white', facecolor='#1a1a1a')

    # Row 2: composite survivor count across SCALINGS at focal n_0
    for col, (sname, _) in enumerate(SCALINGS):
        ax = fig.add_subplot(gs[1, col])
        ax.set_facecolor('#0a0a0a')
        for n0 in N0_LIST:
            data = results[(sname, n0)]
            ws = [d['W'] for d in data if d]
            n_comp = [d['n_surv'] - d['n_prime_window']
                      for d in data if d]
            ax.plot(ws, n_comp, linewidth=1.4,
                     label=f'n_0 = {n0}',
                     alpha=0.9)
        ax.set_title(sname, color='white', fontsize=10)
        ax.set_xlabel('W', color='white', fontsize=10)
        if col == 0:
            ax.set_ylabel('|composite survivors|',
                          color='white', fontsize=10)
        ax.set_yscale('log')
        ax.set_xscale('log')
        ax.set_ylim(bottom=1)
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#333')
        ax.grid(True, alpha=0.18, color='#888', which='both')
        ax.legend(loc='upper left', fontsize=8, framealpha=0.4,
                  labelcolor='white', facecolor='#1a1a1a')

    # Row 3: T_B_low contribution (the irremovable layer) — as a
    # function of W for each scaling, at focal n_0
    for col, (sname, _) in enumerate(SCALINGS):
        ax = fig.add_subplot(gs[2, col])
        ax.set_facecolor('#0a0a0a')
        for n0 in N0_LIST:
            data = results[(sname, n0)]
            ws = [d['W'] for d in data if d]
            tBlow = [d['n_typeB_low'] for d in data if d]
            ax.plot(ws, tBlow, linewidth=1.4, label=f'n_0 = {n0}',
                     alpha=0.9)
        ax.set_title(f'T_B_low (cofactor < n_0): {sname.split("(")[0]}',
                     color='white', fontsize=10)
        ax.set_xlabel('W', color='white', fontsize=10)
        if col == 0:
            ax.set_ylabel('|T_B_low survivors|',
                          color='white', fontsize=10)
        ax.set_yscale('log')
        ax.set_xscale('log')
        ax.set_ylim(bottom=1)
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#333')
        ax.grid(True, alpha=0.18, color='#888', which='both')
        ax.legend(loc='upper left', fontsize=8, framealpha=0.4,
                  labelcolor='white', facecolor='#1a1a1a')

    fig.suptitle(
        'EXP14 — K = K(W) prime convergence reframe.  '
        'Type-B low-q composites (cofactor < n_0) are an '
        'irremovable layer at any K ≥ small.',
        color='white', fontsize=13, y=0.997
    )
    plt.tight_layout()
    plt.savefig(OUT, dpi=180, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    out(f'\n-> {OUT}')

    with open(OUT_TXT, 'w') as f:
        f.write('\n'.join(log))
    out(f'-> {OUT_TXT}')


if __name__ == '__main__':
    main()
