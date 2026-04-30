"""
predict_correlation.py — within-row Q autocorrelation, with a class-pair
decomposition that separates the algebraic part (exact, from predict_q)
from the combinatorial part (joint density of overlap / tau-signature
classes, computed by direct enumeration).

Setup. Fix n >= 2 and h >= 1. The "row" is the function k -> Q_n(n^h k)
for k = 1, 2, ..., K. The within-row autocorrelation at lag L is

    A(n, h, L; K) := (1/(K - L)) sum_{k=1}^{K - L}
                       Q_n(n^h k) * Q_n(n^h (k + L)).

The empirical lattice files q_lattice_4000_h{5,6,7,8}.npy store exactly
the function k -> Q_n(n^h k) by row index n. So A(n, h, L; K) computed
here from predict_q.q_general matches what the lattice gives, by
construction (both are evaluations of the same master expansion). The
purpose of this module is not to "verify" the lattice — they're the
same object — but to factor A into a sum that exposes which structural
class pairs contribute.

Class signature.

For prime n = p, every k decomposes uniquely as k = p^t k' with gcd(k', p) = 1.
The class of k is the pair

    cls(k) = (t, tau_sig(k')),

where tau_sig is the sorted-descending exponent tuple. Q_n(n^h k) depends
on cls(k) only:

    Q_p(p^h k) = q_value_by_class((1,), h + t, tau_sig(k')).

Class-pair decomposition.

    A(p, h, L; K) = sum_{c1, c2} D(c1, c2) * V(c1) * V(c2),

    D(c1, c2) := #{ k in [1, K - L] : cls(k) = c1, cls(k + L) = c2 } / (K - L),
    V(c) := q_value_by_class((1,), h + c[0], c[1])     (a Fraction).

The sum is finite for any finite K. The algebraic part V is exact; the
combinatorial part D is computed by enumeration. Their product
reproduces the direct autocorrelation exactly.

Reading the parity-of-L structure.

For n = 2 and L odd, no k has both k and k + L odd, so every pair
(k, k + L) crosses parity strata: one side has t = 0, the other t >= 1.
Q_2(2^h * 1) = 1/h while Q_2(2^{h+1}) = 1/(h+1), so even at the
const tau-signature the two strata carry different Q values. For L
even, both k and k + L can be odd, and the dominant class pair is
((0, ()), (0, ())) on which the within-row "kernel zero" anchor
applies.

The L-parity gap thus has a clean algebraic origin: the joint density
D shifts mass between (t, t)-diagonal and (t, t')-off-diagonal class
pairs as L changes parity, and the off-diagonal Q products carry
different magnitudes than the diagonal ones. Magnitudes follow from
predict_q exactly.

Public API.

    direct_autocorr(n, h, L, K_max)
        Direct mean of Q(k) * Q(k + L). Returns float.

    class_decomposition(n, h, L, K_max, top_n=12)
        Enumerate class pairs over k = 1..K_max - L, return:
          - 'autocorr' : float, sum over all pairs (= direct_autocorr)
          - 'pairs'    : list of (count, density, V1, V2, contribution),
                          sorted by |contribution| descending,
                          truncated to top_n.

    autocorr_profile(n, h, L_range, K_max)
        Convenience: dict L -> direct_autocorr(n, h, L, K_max) for L in
        L_range. Used by test_within_row_lattice.py.
"""

from __future__ import annotations

import os
import sys
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from typing import Dict, Iterable, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from predict_q import (
    factor_tuple, q_general, q_value_by_class, shape_of, tau_sig_of,
)


# --------------------------------------------------------------------------
# class extraction
# --------------------------------------------------------------------------

def class_of(n: int, k: int) -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
    """Return ((t_1, ..., t_r), tau_sig(k_prime)) where r = omega(n).

    For prime n = (p,), the first tuple is (nu_p(k),) and the second is
    sorted-descending exponent profile of k / p^{nu_p(k)}.
    """
    n_factors = factor_tuple(n)
    t_list = []
    k_prime = k
    for p, _a in n_factors:
        e = 0
        while k_prime % p == 0:
            e += 1
            k_prime //= p
        t_list.append(e)
    return tuple(t_list), tau_sig_of(k_prime)


@lru_cache(maxsize=None)
def q_for_class(n_shape: Tuple[int, ...],
                h: int,
                t_tuple: Tuple[int, ...],
                tau_sig: Tuple[int, ...]) -> Fraction:
    """Q_n(n^h k) given n_shape (sorted-desc), the overlap t-tuple
    aligned with n's primes (note: NOT sorted), and tau_sig of k_prime.

    Because q_value_by_class assumes sorted-descending shape, we pass a
    permuted version. For prime n there's no permutation to do.

    For squarefree n with all a_i = 1, the t-tuple permutation does
    not matter. For general n, the master expansion is computed from
    the master_q-style sum, so we re-derive directly using the same
    formula structure as predict_q.q_general.
    """
    # Re-derive using the master expansion in (t, k_prime) form.
    # h_eff = h + min(t_i // a_i)
    if not n_shape:
        raise ValueError('n_shape must be non-empty')
    if len(t_tuple) != len(n_shape):
        raise ValueError(f'len(t_tuple) {len(t_tuple)} != len(n_shape) {len(n_shape)}')
    nu_n_of_k = min(t // a for a, t in zip(n_shape, t_tuple))
    h_eff = h + nu_n_of_k

    from math import comb
    total = Fraction(0)
    for j in range(1, h_eff + 1):
        bin_prod = 1
        for a, t_i in zip(n_shape, t_tuple):
            bin_prod *= comb(a * (h - j) + t_i + j - 1, j - 1)
        tau_j = 1
        for e in tau_sig:
            tau_j *= comb(e + j - 1, j - 1)
        sign = 1 if j % 2 == 1 else -1
        total += Fraction(sign * bin_prod * tau_j, j)
    return total


# --------------------------------------------------------------------------
# direct autocorrelation
# --------------------------------------------------------------------------

def direct_autocorr(n: int, h: int, L: int, K_max: int) -> float:
    """Direct mean of Q(k) * Q(k + L) for k = 1..K_max - L."""
    if L < 1:
        raise ValueError(f'L must be >= 1, got {L}')
    if K_max <= L:
        raise ValueError(f'K_max must be > L, got K_max={K_max}, L={L}')
    s = 0.0
    n_pairs = K_max - L
    for k in range(1, n_pairs + 1):
        q1 = float(q_general(n, h, k))
        q2 = float(q_general(n, h, k + L))
        s += q1 * q2
    return s / n_pairs


def _q_row_floats(n: int, h: int, K_max: int) -> List[float]:
    return [float(q_general(n, h, k)) for k in range(1, K_max + 1)]


def autocorr_profile(n: int, h: int, L_range: Iterable[int], K_max: int) -> Dict[int, float]:
    """Return {L: A(n, h, L; K_max)} for L in L_range, with O(K_max)
    Q evaluations total."""
    row = _q_row_floats(n, h, K_max)
    out = {}
    for L in L_range:
        if L < 1 or L >= K_max:
            raise ValueError(f'L={L} out of range for K_max={K_max}')
        n_pairs = K_max - L
        s = 0.0
        for k in range(n_pairs):
            s += row[k] * row[k + L]
        out[L] = s / n_pairs
    return out


def autocorr_profile_from_row(row: List[float], L_range: Iterable[int]) -> Dict[int, float]:
    """Same as autocorr_profile but takes a precomputed numeric row.
    Used to compare against q_lattice_4000_h*.npy directly."""
    K = len(row)
    out = {}
    for L in L_range:
        if L < 1 or L >= K:
            raise ValueError(f'L={L} out of range for row length {K}')
        n_pairs = K - L
        s = 0.0
        for k in range(n_pairs):
            s += row[k] * row[k + L]
        out[L] = s / n_pairs
    return out


# --------------------------------------------------------------------------
# class-pair decomposition
# --------------------------------------------------------------------------

def class_decomposition(n: int,
                        h: int,
                        L: int,
                        K_max: int,
                        top_n: int = 12) -> Dict:
    """Enumerate class pairs and report the autocorrelation as a sum of
    contributions class-pair by class-pair."""
    if L < 1 or K_max <= L:
        raise ValueError(f'bad args: L={L}, K_max={K_max}')
    n_shape_sorted = shape_of(n)  # for sanity reporting
    n_factors = factor_tuple(n)
    a_tuple = tuple(a for _p, a in n_factors)

    n_pairs = K_max - L

    # Precompute classes and Q values.
    cls_arr = []
    q_arr = []
    for k in range(1, K_max + 1):
        c = class_of(n, k)  # (t_tuple, tau_sig(k_prime))
        cls_arr.append(c)
        # cls_arr's t_tuple is aligned with n's prime list (not sorted by a).
        q = q_for_class(a_tuple, h, c[0], c[1])
        q_arr.append(float(q))

    pair_count: Dict[Tuple, int] = defaultdict(int)
    pair_qprod: Dict[Tuple, float] = {}
    for k in range(n_pairs):
        c1 = cls_arr[k]
        c2 = cls_arr[k + L]
        key = (c1, c2)
        pair_count[key] += 1
        if key not in pair_qprod:
            pair_qprod[key] = q_arr[k] * q_arr[k + L]

    rows = []
    total = 0.0
    for key, count in pair_count.items():
        density = count / n_pairs
        qprod = pair_qprod[key]
        contribution = density * qprod
        total += contribution
        rows.append({
            'class_pair': key,
            'count': count,
            'density': density,
            'q_prod': qprod,
            'contribution': contribution,
        })
    rows.sort(key=lambda r: -abs(r['contribution']))

    return {
        'n': n,
        'h': h,
        'L': L,
        'K_max': K_max,
        'n_pairs': n_pairs,
        'autocorr': total,
        'pairs': rows[:top_n],
        'all_pairs': rows,
    }


# --------------------------------------------------------------------------
# self-check: class decomposition sums to direct autocorrelation
# --------------------------------------------------------------------------

def _self_check():
    fails = 0
    cases = [
        (2, 5, 1, 600),
        (2, 5, 2, 600),
        (2, 6, 1, 600),
        (3, 5, 1, 600),
        (3, 5, 3, 600),
        (5, 5, 4, 600),
        (5, 5, 5, 600),
        (7, 5, 7, 600),
    ]
    for n, h, L, K_max in cases:
        direct = direct_autocorr(n, h, L, K_max)
        decomp = class_decomposition(n, h, L, K_max, top_n=4)
        diff = abs(direct - decomp['autocorr'])
        ok = diff < 1e-9
        tag = 'OK' if ok else 'FAIL'
        print(f'  {tag}  n={n} h={h} L={L} K_max={K_max}: '
              f'direct={direct:+.4e} decomp={decomp["autocorr"]:+.4e} diff={diff:.2e}')
        if not ok:
            fails += 1
    print('predict_correlation self-check:', 'PASS' if fails == 0 else f'FAIL ({fails})')
    return fails


if __name__ == '__main__':
    raise SystemExit(_self_check())
