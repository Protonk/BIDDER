"""
Atom enumerator for (S, ·), where S is a numerical semigroup.

Implements the gap-determination predicate from
interlock/INTERLOCKING-DEFECTS.md §4:

    m ∈ A_S  ⟺  ∀ d | m with 2 ≤ d ≤ m/2:   d ∈ G  or  m/d ∈ G

with G = ℕ \\ S. S is built additively from coprime positive
generators; atoms of (S, ·) are read off by trial division against
the membership set.
"""

from functools import reduce
from math import gcd
from numbers import Integral


def _normalize_generators(generators):
    """Validated generator tuple."""
    try:
        gens = tuple(generators)
    except TypeError as exc:
        raise ValueError("generators must be an iterable of integers") from exc
    if not gens:
        raise ValueError("generators must be positive integers")
    if any(not isinstance(g, Integral) or g <= 0 for g in gens):
        raise ValueError("generators must be positive integers")
    return tuple(int(g) for g in gens)


def numerical_semigroup(generators, N):
    """S ∩ [0, N] as a frozenset of integers."""
    if not isinstance(N, Integral) or N < 0:
        raise ValueError("N must be a non-negative integer")
    generators = _normalize_generators(generators)
    g0 = reduce(gcd, generators)
    if g0 != 1:
        raise ValueError(
            f"generators must have gcd 1 (else complement is infinite), "
            f"got gcd = {g0}"
        )
    members = [False] * (N + 1)
    members[0] = True
    for gen in generators:
        for i in range(gen, N + 1):
            if members[i - gen]:
                members[i] = True
    return frozenset(i for i, present in enumerate(members) if present)


def gap_set(S, N):
    """G ∩ [0, N], ascending."""
    return [i for i in range(N + 1) if i not in S]


def frobenius_number(S, N):
    """max(G ∩ [0, N]). Returns -1 if every i ∈ [0, N] is in S."""
    for i in range(N, -1, -1):
        if i not in S:
            return i
    return -1


def multiplicity(S):
    """min(S \\ {0})."""
    nonzero = [s for s in S if s > 0]
    if not nonzero:
        raise ValueError("S has no positive element")
    return min(nonzero)


def is_atom(m, S):
    """Gap-determination predicate.

    Requires m ∈ S and m ≥ 2. Returns True iff every divisor pair
    (d, m/d) with 2 ≤ d ≤ m/d has at least one factor outside S.
    """
    if m < 2 or m not in S:
        return False
    d = 2
    while d * d <= m:
        if m % d == 0 and d in S and (m // d) in S:
            return False
        d += 1
    return True


def atoms(generators, N):
    """A_S ∩ [2, N], ascending."""
    S = numerical_semigroup(generators, N)
    return [m for m in range(2, N + 1) if is_atom(m, S)]


# Self-check: anchors against INTERLOCKING-DEFECTS.md.
if __name__ == "__main__":
    # §1 — ⟨3, 5⟩ semigroup data.
    S35 = numerical_semigroup([3, 5], 30)
    assert gap_set(S35, 30) == [1, 2, 4, 7]
    assert frobenius_number(S35, 30) == 7
    assert multiplicity(S35) == 3

    # §2 — atom verdicts through 30.
    expected = [
        3, 5, 6, 8, 10, 11, 12, 13, 14, 16, 17,
        19, 20, 21, 22, 23, 26, 28, 29,
    ]
    assert atoms([3, 5], 30) == expected

    # §5 — first 12 atoms and the Champernowne digit string.
    first_12 = expected[:12]
    assert first_12 == [3, 5, 6, 8, 10, 11, 12, 13, 14, 16, 17, 19]
    assert ''.join(map(str, first_12)) == '35681011121314161719'

    # §3 — gap-stuck composites that survive as atoms vs. those that don't.
    S35_400 = numerical_semigroup([3, 5], 400)
    for m in [8, 16, 32, 56, 98, 343]:
        assert is_atom(m, S35_400), f"{m} should be atom"
    for m in [64, 112, 196]:
        assert not is_atom(m, S35_400), f"{m} should be reducible"
    S35_2500 = numerical_semigroup([3, 5], 2500)
    assert not is_atom(2401, S35_2500), "2401 = 7·343 reducible via (49, 49)"

    # §4 — ⟨3, 7⟩ multiplicatively closed despite m(S)² < F(S).
    S37 = numerical_semigroup([3, 7], 200)
    assert frobenius_number(S37, 200) == 11
    assert multiplicity(S37) == 3
    s_low = [i for i in range(2, 15) if i in S37]
    for a in s_low:
        for b in s_low:
            if a * b <= 200:
                assert a * b in S37, f"⟨3,7⟩ closure fails: {a}·{b}"

    print("ns_atoms self-check: PASS")
