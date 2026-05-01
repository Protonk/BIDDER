"""
exp06_prime_convergence.py — survivor → prime convergence as W grows.

Every prime p in [n_0, n_1] is a survivor at any K ≥ 1: stream p
claims it, no other stream q ≠ p can (would need q | p, ruling out
q < p). So as W = n_1 - n_0 + 1 grows at fixed (n_0, K):

    |Surv| = π([n_0, n_1])  +  |composite survivors|

The composite-survivor count is what shrinks. Question: at what rate?

Composite survivors are integers c with mult(c) := |{n ∈ [n_0, n_1] :
n | c, n² ∤ c}| equal to 1. As [n_0, n_1] grows, more divisors fall
in window for any given c, so most composites flip from mult=1
(survivor) to mult≥2 (culled). The asymptotic survivor set
(W → ∞ at fixed n_0) consists of primes plus composites c whose
only window divisor is c itself or specific small-divisor-count cases.

Sweep:
    n_0 ∈ {2, 5, 10, 25, 50}
    K  ∈ {50, 200}
    W  ∈ [1, 250]

Outputs:
    exp06_prime_convergence.png
"""

from __future__ import annotations

import os
import sys
import time

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

OUT = os.path.join(HERE, 'exp06_prime_convergence.png')

N0_LIST = [2, 5, 10, 25, 50]
K_LIST = [50, 200]
W_RANGE = range(1, 251)


def n_primes_vec(n: int, k: int) -> np.ndarray:
    blocks = (k + n - 2) // (n - 1)
    m = np.arange(1, blocks * n + 1, dtype=np.int64)
    m_valid = m[m % n != 0]
    return (n * m_valid[:k]).astype(np.int64)


def sieve_primes_up_to(N: int) -> np.ndarray:
    """Returns boolean array of size N+1 where True at primes."""
    sieve = np.ones(N + 1, dtype=bool)
    sieve[:2] = False
    for i in range(2, int(N ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = False
    return sieve


def evaluate(n0, n1, k, prime_sieve):
    parts = [n_primes_vec(n, k) for n in range(n0, n1 + 1)]
    m_arr = np.concatenate(parts)
    _, inverse, counts = np.unique(m_arr, return_inverse=True, return_counts=True)
    surv_idx = np.where(counts[inverse] == 1)[0]
    survivors = m_arr[surv_idx]
    n_surv = survivors.size
    # Number of primes in [n_0, n_1] (these are always survivors)
    pi_window = int(prime_sieve[n0:n1 + 1].sum())
    # Composite survivors = total survivors - primes (but primes-in-window are survivors)
    # Actually some survivors might be primes p > n_1 — wait, can a prime
    # outside the window be in the bundle? p = n*m for some n in window.
    # For p prime, n*m = p forces (n, m) = (1, p) or (p, 1), and n ≥ n_0 ≥ 2,
    # so n = p. Thus p must be in the window. So primes in survivors ⊆ primes in window.
    # And primes in window are all survivors (by the earlier argument).
    # So: primes in survivors = primes in window = pi_window.
    n_composite_surv = n_surv - pi_window
    # Sanity
    if n_composite_surv < 0:
        # Shouldn't happen but handle gracefully
        n_composite_surv = 0
    return {
        'n_surv': n_surv,
        'n_atoms': m_arr.size,
        'pi_window': pi_window,
        'n_composite_surv': int(n_composite_surv),
        'max_atom': int(m_arr.max()),
    }


def main():
    # Largest n_1 we'll see is max(N0_LIST) + max(W_RANGE) - 1
    max_n1 = max(N0_LIST) + W_RANGE[-1] - 1
    print(f'Building prime sieve up to {max_n1}')
    prime_sieve = sieve_primes_up_to(max_n1)

    fig, axes = plt.subplots(1, 2, figsize=(18, 7), dpi=140)
    fig.patch.set_facecolor('#0a0a0a')
    for ax in axes:
        ax.set_facecolor('#0a0a0a')

    cmap = plt.get_cmap('viridis')
    color_for = {n0: cmap(i / max(1, len(N0_LIST) - 1))
                 for i, n0 in enumerate(N0_LIST)}

    for ki, K in enumerate(K_LIST):
        ax = axes[ki]
        for n0 in N0_LIST:
            t0 = time.time()
            ws = list(W_RANGE)
            n_surv = []
            pi_w = []
            n_comp = []
            for w in ws:
                n1 = n0 + w - 1
                r = evaluate(n0, n1, K, prime_sieve)
                n_surv.append(r['n_surv'])
                pi_w.append(r['pi_window'])
                n_comp.append(r['n_composite_surv'])
            n_surv = np.array(n_surv)
            pi_w = np.array(pi_w)
            n_comp = np.array(n_comp)
            elapsed = time.time() - t0
            print(f'  K={K}, n_0={n0}: '
                  f'final |Surv|={n_surv[-1]}, π_window={pi_w[-1]}, '
                  f'composite_surv={n_comp[-1]}  ({elapsed:.1f}s)')

            color = color_for[n0]
            ax.plot(ws, n_comp, color=color, linewidth=1.5, alpha=0.92,
                    label=f'n_0 = {n0}')

        ax.set_xlabel('W (window width)', color='white', fontsize=11)
        ax.set_ylabel('|composite survivors|', color='white', fontsize=11)
        ax.set_yscale('log')
        ax.set_xscale('log')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#333')
        ax.grid(True, alpha=0.18, color='#888', which='both')
        ax.legend(loc='upper right', fontsize=9, framealpha=0.4,
                  labelcolor='white', facecolor='#1a1a1a')
        ax.set_title(f'K = {K}', color='white', fontsize=12)

    fig.suptitle(
        'Composite-survivor count vs window width W\n'
        '(primes are always survivors; composites get culled as W grows)',
        color='white', fontsize=13, y=0.995
    )

    plt.tight_layout()
    plt.savefig(OUT, dpi=200, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f'\n-> {OUT}')


if __name__ == '__main__':
    main()
