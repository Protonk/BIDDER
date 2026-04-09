"""
Empirical verification of the trivial-greedy theorem for unordered
multi-set recovery (see UNORDERED-CONJECTURE.md "Abductive addendum").

For a battery of row lists -- typical, sparse, dense, adversarial,
edge-case -- build the n-prime table, take the multi-set V of all
N^2 cell values (no order, no labels), and run greedy
reconstruction. Assert the recovered row list equals the original.

Run with `sage verify_greedy.py`.
"""


def j_index(n, k_prime):
    """k'-th positive integer not divisible by n."""
    return k_prime + (k_prime - 1) // (n - 1)


def n_prime_value(n, k_prime):
    """k'-th n-prime, equal to j_{k'} * n."""
    return n * j_index(n, k_prime)


def build_multiset(rows):
    """Return the multi-set V (as a list, since we want multiplicity)
    of all N^2 cell values for the n-prime table on the given row
    list. The returned list has no row/column labels -- it is the
    'unordered' input the receiver gets."""
    N = len(rows)
    V = []
    for n_k in rows:
        for k_prime in range(1, N + 1):
            V.append(n_prime_value(n_k, k_prime))
    return V


def greedy_reconstruct(V, N):
    """Reconstruct the row list from the unordered multi-set V.

    Algorithm:
      for i = 1, 2, ..., N:
          n_i = min(V)
          remove one copy of each cell of row i from V
      return [n_1, ..., n_N]
    """
    V = list(V)  # mutable copy; original is preserved
    rows = []
    for _ in range(N):
        n_i = min(V)
        rows.append(n_i)
        for k_prime in range(1, N + 1):
            v = n_prime_value(n_i, k_prime)
            V.remove(v)  # raises ValueError if missing
    assert len(V) == 0, "leftover values after N iterations: %s" % V
    return rows


# --- Test cases: typical, sparse, dense, adversarial, edge ---

test_cases = [
    # (description, row_list)
    ("smallest non-trivial",        [2, 3]),
    ("contiguous N=3",               [2, 3, 4]),
    ("contiguous N=5 (Example 1)",   [2, 3, 4, 5, 6]),
    ("primes N=5",                   [3, 5, 7, 11, 13]),
    ("sparse N=6 (Example 2)",       [2, 5, 10, 13, 17, 21]),
    ("very sparse N=5 (Example 3)",  [3, 7, 11, 100, 1000]),
    ("geometric, powers of 2",       [2, 4, 8, 16, 32, 64, 128, 256]),
    ("multiples of 3",               [3, 6, 9, 12, 15, 18, 21, 24, 27]),
    ("n_2 a multiple of n_1",        [2, 6]),
    ("dense w/ heavy collisions",    [2, 4, 6, 8, 10, 12]),
    ("contiguous N=20",              list(range(2, 22))),
    ("primes N=10",                  [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]),
    ("Fibonacci-ish",                [2, 3, 5, 8, 13, 21, 34, 55, 89]),
    ("two close + one far",          [2, 3, 100]),
    ("adjacent + power of 2",        [2, 3, 4, 8, 16]),
]


print("Verifying greedy reconstruction on %d test cases..." % len(test_cases))
print()

for desc, rows in test_cases:
    N = len(rows)
    V = build_multiset(rows)
    assert len(V) == N * N
    recovered = greedy_reconstruct(V, N)
    assert recovered == rows, (
        "MISMATCH on %s: input=%s, recovered=%s" % (desc, rows, recovered)
    )
    print("  PASS  N=%2d  %-32s  rows=%s"
          % (N, desc, rows[:6] + (["..."] if len(rows) > 6 else [])))

print()
print("All %d test cases recovered exactly." % len(test_cases))
print("Trivial-greedy theorem holds empirically across the battery.")
