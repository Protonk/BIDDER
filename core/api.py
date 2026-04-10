"""
api.py — Public entry point for the BIDDER period-only API.

Companion to core/API-PLAN.md. v1 is intentionally trivial: a single
function `fulfill(period, key)` that delegates to BidderBlock. The
constructor handles all validation and refusal — fulfill exists as the
public API entry point so that future composition / catalogue work can
extend it without changing call sites.

Run with python3 (no numpy).
"""

import os
import sys

# Put generator/ on sys.path so `import bidder_block` resolves. This
# matches the existing cross-directory import convention in
# tests/test_acm_core.py, core/hardy_sidestep.py, and the experiment
# scripts — the repo is not packaged, and callers that import core/api
# are expected to have put core/ on their own sys.path already.
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, '..', 'generator'))

from bidder_block import (  # noqa: E402
    BidderBlock,
    UnsupportedPeriodError,
    MAX_PERIOD_V1,
)


def fulfill(period: int, key: bytes) -> BidderBlock:
    """Build a BidderBlock for the requested period.

    In v1 this is the BidderBlock constructor under another name. The
    constructor handles all validation and refusal — fulfill exists as
    the public API entry point so that future composition / catalogue
    work can extend it without changing call sites.

    Args:
        period: integer in [2, MAX_PERIOD_V1].
        key:    bytes or bytearray, raw key material.

    Returns:
        BidderBlock with .at(i), .period, iteration, len.

    Raises:
        TypeError: if period or key has the wrong type.
        ValueError: if period < 2.
        UnsupportedPeriodError: if period exceeds MAX_PERIOD_V1.
    """
    return BidderBlock(period, key)
