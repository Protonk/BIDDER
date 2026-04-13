"""
test_bidder_root.py — Smoke tests for the project-root bidder.py.

Confirms that the root entry point's two construction functions and
re-exports resolve correctly. The deep correctness tests live in
tests/test_bidder_block.py, tests/test_api.py, and tests/test_sawtooth.py;
these are plumbing checks only.

Run: python3 tests/test_bidder_root.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import bidder


# =====================================================================
# Cipher path
# =====================================================================

def test_cipher_returns_bidder_block():
    B = bidder.cipher(100, b'root test')
    assert isinstance(B, bidder.BidderBlock)
    assert B.period == 100
    print("  cipher returns BidderBlock with period: OK")

def test_cipher_small_sweep():
    for P in [2, 10, 1000, 65535]:
        B = bidder.cipher(P, b'sweep')
        assert B.period == P
        assert 0 <= B.at(0) < P
    print("  cipher small sweep: OK")


# =====================================================================
# Sawtooth path
# =====================================================================

def test_sawtooth_returns_nprime_sequence():
    S = bidder.sawtooth(3, 50)
    assert isinstance(S, bidder.NPrimeSequence)
    assert S.period == 50
    assert S.n == 3
    print("  sawtooth returns NPrimeSequence: OK")

def test_sawtooth_small_sweep():
    for n in [2, 3, 5, 7, 10]:
        S = bidder.sawtooth(n, 20)
        assert S.period == 20
        assert S.at(0) == n  # first n-prime is n itself
    print("  sawtooth small sweep: OK")

def test_sawtooth_n_overflow():
    try:
        bidder.sawtooth(1 << 65, 1)
        assert False, "should have raised OverflowError"
    except OverflowError:
        pass
    print("  sawtooth n overflow cap: OK")

def test_sawtooth_count_overflow():
    try:
        bidder.sawtooth(2, sys.maxsize + 1)
        assert False, "should have raised OverflowError"
    except OverflowError:
        pass
    print("  sawtooth count overflow cap: OK")


# =====================================================================
# Re-exports
# =====================================================================

def test_reexports():
    assert hasattr(bidder, 'MAX_PERIOD_V1')
    assert bidder.MAX_PERIOD_V1 == (1 << 32) - 1
    assert hasattr(bidder, 'UnsupportedPeriodError')
    assert issubclass(bidder.UnsupportedPeriodError, ValueError)
    assert hasattr(bidder, 'BidderBlock')
    assert hasattr(bidder, 'NPrimeSequence')
    print("  Re-exports resolve: OK")


# =====================================================================
# Clean import from repo root
# =====================================================================

def test_clean_import():
    """Verify that bidder.py imports cleanly with only the repo root
    on sys.path (the root file wires up its own internal paths).
    """
    import subprocess
    repo_root = os.path.join(os.path.dirname(__file__), '..')
    result = subprocess.run(
        [sys.executable, '-c',
         'import sys; sys.path.insert(0, "."); import bidder; '
         'B = bidder.cipher(10, b"k"); assert B.period == 10; '
         'S = bidder.sawtooth(3, 5); assert S.at(0) == 3; '
         'print("subprocess OK")'],
        capture_output=True, text=True,
        cwd=os.path.abspath(repo_root),
        env={**os.environ, 'PYTHONPATH': ''}
    )
    assert result.returncode == 0, (
        f"subprocess failed:\nstdout: {result.stdout}\nstderr: {result.stderr}")
    assert 'subprocess OK' in result.stdout
    print("  Clean import from repo root (subprocess): OK")


# =====================================================================
# Entry point
# =====================================================================

if __name__ == '__main__':
    print("=== bidder root tests ===\n")

    test_cipher_returns_bidder_block()
    test_cipher_small_sweep()
    test_sawtooth_returns_nprime_sequence()
    test_sawtooth_small_sweep()
    test_sawtooth_n_overflow()
    test_sawtooth_count_overflow()
    test_reexports()
    test_clean_import()

    print("\nAll bidder root tests passed.")
