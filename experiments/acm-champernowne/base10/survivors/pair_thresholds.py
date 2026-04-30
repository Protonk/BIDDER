"""
pair_thresholds.py — k_pair(n, n') and friends.

For two streams n, n', the K at which their first shared element appears
in BOTH streams' first-K n-prime lists. This is the "pair-collision
threshold" — for K below it, no element of stream n is in stream n', so
the survivor filter sees no interaction between the two; for K above
it, the shared element is culled from survivors.

For a window [n_0, n_0 + W - 1] there are W*(W-1)/2 pairs. The set of
K_pair values across these pairs partitions the K-axis into regimes
with different sets of active pair-collisions.

Used by:
    exp03_triangle_slice.py
    exp03_gap_vs_active_pairs.py
"""

from __future__ import annotations

import math
from itertools import combinations


def k_pair(n: int, n_prime: int) -> int:
    """K threshold above which streams n and n' first share an element.

    Stream n = {n*j : n ∤ j, j >= 1}. The first shared element is the
    smallest m that's in both streams; its position in each stream
    determines the K threshold.
    """
    if n == n_prime:
        return 1
    g = math.gcd(n, n_prime)
    L = n * n_prime // g                            # lcm
    # Position of L in stream n: count of valid j' <= L/n.
    pos_n = (L // n) - (L // (n * n))
    pos_np = (L // n_prime) - (L // (n_prime * n_prime))
    return max(pos_n, pos_np)


def window_pairs(n0: int, w: int):
    """All ordered pairs (a, b) with n0 <= a < b <= n0 + w - 1."""
    return list(combinations(range(n0, n0 + w), 2))


def all_k_pairs(n0: int, w: int):
    """List of K_pair values for all C(w,2) pairs in the window."""
    return [k_pair(a, b) for a, b in window_pairs(n0, w)]


def active_pair_count(K: int, n0: int, w: int) -> int:
    """Number of pair-collisions active at (K, n_0) — i.e., pairs whose
    K_pair < K, so their first shared element is included in both
    streams' first-K lists and is therefore culled from survivors."""
    return sum(1 for kp in all_k_pairs(n0, w) if kp < K)


def first_active_K(n0: int, w: int) -> int:
    """Smallest K at which any pair has activated."""
    return min(all_k_pairs(n0, w))


def last_active_K(n0: int, w: int) -> int:
    """K at which the LAST pair activates — above this, all C(w,2)
    pairs are active."""
    return max(all_k_pairs(n0, w))


def _self_check():
    # n=290, n'=291: K_pair should be 290.
    assert k_pair(290, 291) == 290, k_pair(290, 291)
    # n=290, n'=295: K_pair should be 59 (gcd=5).
    assert k_pair(290, 295) == 59, k_pair(290, 295)
    # n=290, n'=292: K_pair = 146 (gcd=2).
    assert k_pair(290, 292) == 146, k_pair(290, 292)
    # Window [290, 299] = 10 streams, C(10,2) = 45 pairs.
    pairs = all_k_pairs(290, 10)
    assert len(pairs) == 45, len(pairs)
    print(f'  K_pair(290, 291) = {k_pair(290, 291)}')
    print(f'  K_pair(290, 295) = {k_pair(290, 295)}')
    print(f'  K_pair(290, 292) = {k_pair(290, 292)}')
    print(f'  Window [290..299]: {len(pairs)} pairs')
    print(f'    min K_pair = {min(pairs)}')
    print(f'    max K_pair = {max(pairs)}')
    print(f'    median K_pair = {sorted(pairs)[22]}')
    print('  All K_pairs sorted:', sorted(pairs))
    print('pair_thresholds self-check: PASS')


if __name__ == '__main__':
    _self_check()
