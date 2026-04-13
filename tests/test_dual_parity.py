"""
test_dual_parity.py — Contract test: bidder (pure Python) vs bidder_c (ctypes).

Runs all comparisons in subprocesses with cwd=dist/ and PYTHONPATH=dist/
so the repo-root bidder.py never enters the import path.

Run: python3 tests/test_dual_parity.py
     (requires: sage -python build.py && make)
"""

import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(REPO_ROOT, 'dist')

failures = 0


def run_in_dist(code: str) -> str:
    """Run a Python snippet with only dist/ on the path."""
    result = subprocess.run(
        [sys.executable, '-c', code],
        cwd=DIST,
        env={**os.environ, 'PYTHONPATH': DIST},
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"subprocess failed (rc={result.returncode}):\n{result.stderr}")
    return result.stdout.strip()


def check(label, code):
    global failures
    try:
        out = run_in_dist(code)
        if out == 'OK':
            print(f'  OK   {label}')
        else:
            print(f'  FAIL {label}: {out}')
            failures += 1
    except RuntimeError as e:
        print(f'  FAIL {label}: {e}')
        failures += 1


# ---- Cipher parity ----

CIPHER_TRIPLES = [
    (10, b'doc', 0),
    (10, b'doc', 9),
    (100, b'root test', 5),
    (100, b'root test', 99),
    (2, b'', 0),
    (2, b'', 1),
    (1000, b'medium', 500),
    (1000, b'medium', 999),
    (50, b'mix', 0),
    (9000, b'instrument-check', 4500),
]


def test_cipher_parity():
    print("--- cipher parity ---")
    for period, key, i in CIPHER_TRIPLES:
        key_repr = repr(key)
        check(
            f'cipher({period}, {key_repr}).at({i})',
            f"""
import bidder, bidder_c
a = bidder.cipher({period}, {key_repr}).at({i})
b = bidder_c.cipher({period}, {key_repr}).at({i})
print('OK' if a == b else f'MISMATCH {{a}} != {{b}}')
""",
        )


# ---- Cipher full-permutation parity ----

PERM_PERIODS = [10, 100, 1000]


def test_cipher_full_permutation():
    print("--- cipher full permutation ---")
    for period in PERM_PERIODS:
        check(
            f'list(cipher({period}, b"perm"))',
            f"""
import bidder, bidder_c
a = list(bidder.cipher({period}, b'perm'))
b = list(bidder_c.cipher({period}, b'perm'))
print('OK' if a == b else f'MISMATCH at {{next(i for i,(x,y) in enumerate(zip(a,b)) if x!=y)}}')
""",
        )


# ---- Sawtooth parity ----

SAWTOOTH_TRIPLES = [
    (2, 1_000_001, 1_000_000),
    (7, 1_000_000, 999_999),
    (100, 50_001, 50_000),
    (3, 777_778, 777_777),
    (13, 13, 12),
    (5, 250_001, 250_000),
    (3, 10, 0),
    (3, 10, 9),
]


def test_sawtooth_parity():
    print("--- sawtooth parity ---")
    for n, count, K in SAWTOOTH_TRIPLES:
        check(
            f'sawtooth({n}, {count}).at({K})',
            f"""
import bidder, bidder_c
a = bidder.sawtooth({n}, {count}).at({K})
b = bidder_c.sawtooth({n}, {count}).at({K})
print('OK' if a == b else f'MISMATCH {{a}} != {{b}}')
""",
        )


# ---- Max-range sawtooth (128-bit result) ----

def test_sawtooth_max_range():
    print("--- sawtooth max range ---")
    check(
        'sawtooth(2^64-1, 2^63-1).at(2^63-2)',
        """
import bidder, bidder_c
n = (1 << 64) - 1
count = (1 << 63) - 1
K = (1 << 63) - 2
a = bidder.sawtooth(n, count).at(K)
b = bidder_c.sawtooth(n, count).at(K)
print('OK' if a == b else f'MISMATCH {a} != {b}')
""",
    )


# ---- Exception parity ----

def test_exception_parity():
    print("--- exception parity ---")

    check(
        'cipher(period=True) -> TypeError',
        """
import bidder, bidder_c
errs = []
for mod in (bidder, bidder_c):
    try:
        mod.cipher(True, b'x')
        errs.append('no error')
    except TypeError:
        errs.append('TypeError')
    except Exception as e:
        errs.append(type(e).__name__)
print('OK' if errs == ['TypeError', 'TypeError'] else f'MISMATCH {errs}')
""",
    )

    check(
        'cipher(period=1) -> ValueError',
        """
import bidder, bidder_c
errs = []
for mod in (bidder, bidder_c):
    try:
        mod.cipher(1, b'x')
        errs.append('no error')
    except ValueError:
        errs.append('ValueError')
    except Exception as e:
        errs.append(type(e).__name__)
print('OK' if errs == ['ValueError', 'ValueError'] else f'MISMATCH {errs}')
""",
    )

    check(
        'cipher(period=2**32) -> UnsupportedPeriodError',
        """
import bidder, bidder_c
errs = []
for mod in (bidder, bidder_c):
    try:
        mod.cipher(2**32, b'x')
        errs.append('no error')
    except mod.UnsupportedPeriodError:
        errs.append('UnsupportedPeriodError')
    except Exception as e:
        errs.append(type(e).__name__)
print('OK' if errs == ['UnsupportedPeriodError', 'UnsupportedPeriodError'] else f'MISMATCH {errs}')
""",
    )

    check(
        'cipher(key=bytearray) accepted',
        """
import bidder, bidder_c
vals = []
for mod in (bidder, bidder_c):
    try:
        vals.append(mod.cipher(10, bytearray(b'a\\x00b')).at(0))
    except Exception as e:
        vals.append(type(e).__name__ + ': ' + str(e))
print('OK' if vals[0] == vals[1] else f'MISMATCH {vals}')
""",
    )

    check(
        'cipher huge index -> ValueError',
        """
import bidder, bidder_c
errs = []
for mod in (bidder, bidder_c):
    try:
        mod.cipher(10, b'x').at(1 << 70)
        errs.append('no error')
    except ValueError as e:
        errs.append('ValueError: ' + str(e))
    except Exception as e:
        errs.append(type(e).__name__ + ': ' + str(e))
print('OK' if errs[0] == errs[1] and errs[0].startswith('ValueError: index ') else f'MISMATCH {errs}')
""",
    )

    check(
        'sawtooth huge index -> ValueError',
        """
import bidder, bidder_c
errs = []
for mod in (bidder, bidder_c):
    try:
        mod.sawtooth(3, 10).at(1 << 70)
        errs.append('no error')
    except ValueError as e:
        errs.append('ValueError: ' + str(e))
    except Exception as e:
        errs.append(type(e).__name__ + ': ' + str(e))
print('OK' if errs[0] == errs[1] and errs[0].startswith('ValueError: index ') else f'MISMATCH {errs}')
""",
    )


# ---- Input cap parity ----

def test_input_cap_parity():
    print("--- input cap parity ---")

    check(
        'sawtooth(n=1<<65) -> OverflowError',
        """
import bidder, bidder_c
errs = []
for mod in (bidder, bidder_c):
    try:
        mod.sawtooth(1 << 65, 1)
        errs.append('no error')
    except OverflowError:
        errs.append('OverflowError')
    except Exception as e:
        errs.append(type(e).__name__)
print('OK' if errs == ['OverflowError', 'OverflowError'] else f'MISMATCH {errs}')
""",
    )

    check(
        'sawtooth(count=sys.maxsize+1) -> OverflowError',
        """
import sys, bidder, bidder_c
errs = []
for mod in (bidder, bidder_c):
    try:
        mod.sawtooth(2, sys.maxsize + 1)
        errs.append('no error')
    except OverflowError:
        errs.append('OverflowError')
    except Exception as e:
        errs.append(type(e).__name__)
print('OK' if errs == ['OverflowError', 'OverflowError'] else f'MISMATCH {errs}')
""",
    )


# ---- Entry point ----

def main():
    global failures

    # Pre-check: both packages importable from dist/
    try:
        run_in_dist("import bidder; import bidder_c; print('OK')")
    except RuntimeError as e:
        print(f"Cannot import both packages from dist/:\n{e}")
        print("Run 'make && sage -python build.py' first.")
        sys.exit(1)

    print("=== dual parity tests ===\n")

    test_cipher_parity()
    test_cipher_full_permutation()
    test_sawtooth_parity()
    test_sawtooth_max_range()
    test_exception_parity()
    test_input_cap_parity()

    print()
    if failures:
        print(f"{failures} failure(s)")
        sys.exit(1)
    print("All dual parity tests passed.")


if __name__ == '__main__':
    main()
