"""
bidder_block.py — Period-only random-access wrapper around Bidder.

Companion to core/API-PLAN.md. Thin Python adapter on top of the
existing alphabet-pinned Bidder primitive (which has C parity in
generator/bidder.c). No new cipher work — only parameter translation
and an output shift from the {1, ..., P} contract that Bidder uses
to the [0, P) contract that period-only callers expect.

Run with python3 (no numpy).
"""

import operator
import os
import sys

# coupler.py lives in the same directory; whoever imported this module
# already has generator/ on sys.path, so a bare `from coupler import Bidder`
# resolves. (coupler.py was renamed from bidder.py to avoid a collision
# with the project-root bidder.py.)
from coupler import Bidder


# Backend cap. base must be in [2, 2^32] in the underlying Bidder, and
# we map period P -> base = P + 1, so the largest period the existing
# cipher backend supports is 2^32 - 1.
MAX_PERIOD_V1 = (1 << 32) - 1


class UnsupportedPeriodError(ValueError):
    """Raised when `period` exceeds `bidder.MAX_PERIOD_V1`. See BIDDER.md."""


class BidderBlock:
    """A keyed permutation of [0, period). See BIDDER.md."""

    def __init__(self, period: int, key: bytes) -> None:
        if type(period) is not int:
            raise TypeError(
                f"period must be int, got {type(period).__name__}")
        if period < 2:
            raise ValueError("period must be >= 2")
        if period > MAX_PERIOD_V1:
            raise UnsupportedPeriodError(
                f"period {period} exceeds maximum of {MAX_PERIOD_V1}")
        if not isinstance(key, (bytes, bytearray)):
            raise TypeError(
                f"key must be bytes or bytearray, got {type(key).__name__}")

        self._period = period
        # Map period P -> Bidder(base=P+1, digit_class=1, key).
        # Underlying block is [1, P]; Bidder.at(i) returns the i-th
        # element of the keyed permutation in {1, ..., P}; we shift to
        # [0, P) by subtracting 1.
        self._bidder = Bidder(base=period + 1, digit_class=1, key=bytes(key))

    def at(self, i: int) -> int:
        """Return the i-th element of the permutation in [0, period).

        Raises:
            TypeError: if i is not integer-shaped.
            ValueError: if i is not in [0, period).
        """
        try:
            i = operator.index(i)
        except TypeError as e:
            raise TypeError(
                f"index must be an integer, got {type(i).__name__}"
            ) from e
        if not (0 <= i < self._period):
            raise ValueError(
                f"index {i} out of range [0, {self._period})")
        # Bidder.at returns in {1, ..., period}; shift to [0, period).
        return self._bidder.at(i) - 1

    @property
    def period(self) -> int:
        return self._period

    @property
    def cipher(self) -> str:
        """Diagnostic name of the underlying cipher backend
        ('speck32' or 'feistel'). Used in tests; not part of the
        correctness contract.
        """
        return 'speck32' if self._bidder._mode == 0 else 'feistel'

    def __iter__(self):
        """Return a fresh independent iterator over [0, period).

        Two simultaneous iter(B) calls give two independent walks;
        they share no state.
        """
        return (self.at(i) for i in range(self._period))

    def __len__(self) -> int:
        return self._period

    def __repr__(self) -> str:
        return (f"BidderBlock(period={self._period}, "
                f"cipher={self.cipher!r})")
