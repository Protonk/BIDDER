"""
sawtooth.py — Deterministic n-prime sequence via the Hardy closed form.

The math-layer dual of BidderBlock: same interface shape (.at, .period,
__iter__, __len__), no cipher, no key. Random access is the Hardy
closed form from core/HARDY-SIDESTEP.md — O(1) bignum work per call.

Run with python3 (no numpy, no sage). The closed form is pure integer
arithmetic.
"""

import operator


class NPrimeSequence:
    """Ascending enumeration of the first `count` n-primes. See BIDDER.md."""

    def __init__(self, n: int, count: int) -> None:
        if type(n) is not int:
            raise TypeError(f"n must be int, got {type(n).__name__}")
        if n < 2:
            raise ValueError("n must be >= 2")
        if type(count) is not int:
            raise TypeError(
                f"count must be int, got {type(count).__name__}")
        if count < 1:
            raise ValueError("count must be >= 1")
        self._n = n
        self._count = count

    def at(self, K: int) -> int:
        """Return the K-th n-prime (0-indexed) in ascending order.

        Raises:
            TypeError: if K is not integer-shaped.
            ValueError: if K is not in [0, count).
        """
        try:
            K = operator.index(K)
        except TypeError as e:
            raise TypeError(
                f"index must be an integer, got {type(K).__name__}"
            ) from e
        if not (0 <= K < self._count):
            raise ValueError(
                f"index {K} out of range [0, {self._count})")
        # Hardy closed form (0-indexed):
        #   K-th n-prime = n * (q*n + r + 1)
        #   where q, r = divmod(K, n - 1)
        # See core/HARDY-SIDESTEP.md for the proof.
        q, r = divmod(K, self._n - 1)
        return self._n * (q * self._n + r + 1)

    @property
    def n(self) -> int:
        """The monoid parameter n (>= 2)."""
        return self._n

    @property
    def count(self) -> int:
        """The number of n-primes in the sequence."""
        return self._count

    @property
    def period(self) -> int:
        """Alias for count, matching the BidderBlock interface shape."""
        return self._count

    def __iter__(self):
        """Return a fresh independent iterator over the sequence.

        Two simultaneous iter(S) calls give two independent walks.
        """
        return (self.at(K) for K in range(self._count))

    def __len__(self) -> int:
        return self._count

    def __repr__(self) -> str:
        return f"NPrimeSequence(n={self._n}, count={self._count})"
