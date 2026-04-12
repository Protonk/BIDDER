"""
bidder — root entry point for the BIDDER project.

Two construction functions:

    bidder.cipher(period, key)    -> BidderBlock
    bidder.sawtooth(n, count)     -> NPrimeSequence

The cipher path gives a keyed permutation of [0, period).
The sawtooth path gives the first `count` n-primes of monoid nZ+
(n >= 2) in ascending order.

Both objects share interface shape: .at(i), .period, __iter__,
__len__, __repr__. See BIDDER.md for the full contract.
"""

import os
import sys

# Wire up sys.path for the implementation modules. The repo is not
# packaged; this matches the convention in core/api.py and
# tests/test_api.py.
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, 'core'))
sys.path.insert(0, os.path.join(_HERE, 'generator'))

from api import (                     # noqa: E402
    fulfill,
    BidderBlock,
    MAX_PERIOD_V1,
    UnsupportedPeriodError,
)
from sawtooth import NPrimeSequence   # noqa: E402


def cipher(period: int, key: bytes) -> BidderBlock:
    """Return a keyed permutation of [0, period). See BIDDER.md."""
    return fulfill(period, key)


def sawtooth(n: int, count: int) -> NPrimeSequence:
    """Return the first `count` n-primes in ascending order. See BIDDER.md."""
    return NPrimeSequence(n, count)


__all__ = [
    'cipher',
    'sawtooth',
    'BidderBlock',
    'NPrimeSequence',
    'MAX_PERIOD_V1',
    'UnsupportedPeriodError',
]
