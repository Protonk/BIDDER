"""
hardy_sidestep.py — Closed-form K-th n-prime, with bignum demonstrations.

Companion to core/HARDY-SIDESTEP.md.

The thesis: for n >= 2, the K-th n-prime has a closed form whose cost
is O(M(log K + log n)) bit operations on bignums — polylogarithmic in K.
Locating an irreducible at index K = 2^4096 takes microseconds.

For n = 1 (ordinary primes) the best known exact methods (e.g.
primecount, via Meissel-Lehmer-Lagarias-Odlyzko prime counting plus
local sieving) reach the K-th prime in roughly K^(2/3 + o(1)) ops —
sublinear, but still super-polylogarithmic, and at K = 2^4096 still
unreachable. The closed form for n >= 2 is exponentially faster in
log K.

Run with sage -python: this script imports acm_core, which imports
numpy. Bignums themselves are CPython built-in.
"""

import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# Default int->str cap is 4300 digits in modern CPython. We routinely
# print much larger answers; raise the cap before any large str(int).
sys.set_int_max_str_digits(1_000_000)

from acm_core import acm_n_primes


# ---------------------------------------------------------------------------
# Closed form
# ---------------------------------------------------------------------------

def nth_n_prime(n, K):
    """Return the K-th n-prime in O(1) bignum operations.

    Requires n >= 2 (the n = 1 case is ordinary primes; no closed form).
    Requires K >= 1.

    Derivation: the positive integers k with n does not divide k are
    1, 2, ..., n-1, n+1, ..., 2n-1, 2n+1, ..., a strict arithmetic
    progression with one residue removed per period of length n.
    There are exactly (n-1) valid k per period. So the K-th valid k
    sits in period q = (K-1) // (n-1) at offset r = (K-1) % (n-1):

        k = q*n + r + 1
        K-th n-prime = n * k = n^2 * q + n * (r + 1)

    Two divisions, two multiplications, one addition. No search.
    """
    if n < 2:
        raise ValueError("closed form requires n >= 2")
    if K < 1:
        raise ValueError("K must be >= 1")
    q, r = divmod(K - 1, n - 1)
    return n * (q * n + r + 1)


# ---------------------------------------------------------------------------
# Verification: closed form vs the enumerating sieve in acm_core
# ---------------------------------------------------------------------------

def verify_against_enumeration(n_max=12, K_max=200):
    failures = []
    for n in range(2, n_max + 1):
        primes = acm_n_primes(n, K_max)
        for K in range(1, K_max + 1):
            expected = primes[K - 1]
            actual = nth_n_prime(n, K)
            if expected != actual:
                failures.append((n, K, expected, actual))
    return failures


# ---------------------------------------------------------------------------
# Astronomical demos: locate the K-th n-prime for absurd K
# ---------------------------------------------------------------------------

def demo_huge(n, K, label):
    t0 = time.perf_counter_ns()
    p = nth_n_prime(n, K)
    elapsed_us = (time.perf_counter_ns() - t0) / 1000.0
    bits = p.bit_length()
    s = str(p)
    head = s[:14]
    tail = s[-14:] if len(s) > 28 else ''
    print(f"  n = {n:<5}  K = {label}")
    print(f"    answer: {bits}-bit integer ({len(s)} decimal digits)")
    print(f"    head:   {head}...")
    if tail:
        print(f"    tail:   ...{tail}")
    print(f"    time:   {elapsed_us:.2f} us")
    print()


# ---------------------------------------------------------------------------
# Cost contrast: n = 2 (closed form) vs n = 1 (trial division)
# ---------------------------------------------------------------------------

def cost_contrast():
    """
    Walk K up two orders of magnitude per step. For n=2 the closed
    form stays microseconds. For n=1 the naive sieve in acm_core
    chokes well before K = 10^6. We measure both at the same K and
    print the ratio.
    """
    print(f"  {'K':>10} | {'n=2 closed (us)':>18} | {'n=1 sieve (us)':>18} | {'ratio':>14}")
    print(f"  {'-'*10}-+-{'-'*18}-+-{'-'*18}-+-{'-'*14}")

    for K in [100, 1000, 10_000, 50_000]:
        t0 = time.perf_counter_ns()
        nth_n_prime(2, K)
        t_n2 = (time.perf_counter_ns() - t0) / 1000.0

        t0 = time.perf_counter_ns()
        acm_n_primes(1, K)
        t_n1 = (time.perf_counter_ns() - t0) / 1000.0

        ratio = t_n1 / t_n2 if t_n2 > 0 else float('inf')
        print(f"  {K:>10} | {t_n2:>18.2f} | {t_n1:>18.2f} | {ratio:>14.0f}x")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("HARDY SIDESTEP — closed form vs search")
    print("=" * 60)

    print("\n[1] verification: closed form vs enumeration sieve")
    print("    (n in 2..12, K in 1..200 -> 2200 checks)")
    failures = verify_against_enumeration(n_max=12, K_max=200)
    if failures:
        print(f"    FAILED: {len(failures)} mismatches")
        for f in failures[:5]:
            print(f"      n={f[0]} K={f[1]}: closed={f[3]} enum={f[2]}")
        sys.exit(1)
    print("    OK (2200/2200)")

    print("\n[2] astronomical K — locate the K-th n-prime")
    demo_huge(2,       2 ** 4096,        "2^4096")
    demo_huge(3,       10 ** 100,        "10^100  (googol)")
    demo_huge(7,       2 ** 8192,        "2^8192")
    demo_huge(101,     2 ** 16384,       "2^16384")
    demo_huge(2 ** 32, 2 ** 4096,        "2^4096 (and n itself is 2^32)")

    print("[3] cost contrast at common K (n=2 closed vs n=1 sieve)")
    cost_contrast()
    print()


if __name__ == '__main__':
    main()
