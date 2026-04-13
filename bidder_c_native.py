"""
_native.py — ctypes wrapper over libbidder's opaque API.

This file is copied into dist/bidder_c/ by build.py. It loads
libbidder.dylib (or .so) from the same directory and exposes the
same public surface as dist/bidder/:

    cipher(period, key) -> BidderBlock
    sawtooth(n, count)  -> NPrimeSequence
    BidderBlock, NPrimeSequence, MAX_PERIOD_V1, UnsupportedPeriodError

All type checking and exception formatting happens in Python.
The C library returns error codes; this wrapper translates them.
"""

import ctypes
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))

# Load the shared library from the same directory as this file.
if sys.platform == 'darwin':
    _LIB_NAME = 'libbidder.dylib'
else:
    _LIB_NAME = 'libbidder.so'

_lib = ctypes.CDLL(os.path.join(_HERE, _LIB_NAME))

# --- C function signatures ---

_lib.bdo_block_create.argtypes = [
    ctypes.c_uint64, ctypes.c_char_p, ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_int),
]
_lib.bdo_block_create.restype = ctypes.c_void_p

_lib.bdo_block_free.argtypes = [ctypes.c_void_p]
_lib.bdo_block_free.restype = None

_lib.bdo_block_at.argtypes = [
    ctypes.c_void_p, ctypes.c_uint64,
    ctypes.POINTER(ctypes.c_uint32),
]
_lib.bdo_block_at.restype = ctypes.c_int

_lib.bdo_block_period.argtypes = [ctypes.c_void_p]
_lib.bdo_block_period.restype = ctypes.c_uint64

_lib.bdo_block_backend.argtypes = [ctypes.c_void_p]
_lib.bdo_block_backend.restype = ctypes.c_char_p

_lib.bdo_nprime_create.argtypes = [
    ctypes.c_uint64, ctypes.c_uint64,
    ctypes.POINTER(ctypes.c_int),
]
_lib.bdo_nprime_create.restype = ctypes.c_void_p

_lib.bdo_nprime_free.argtypes = [ctypes.c_void_p]
_lib.bdo_nprime_free.restype = None

_lib.bdo_nprime_at.argtypes = [
    ctypes.c_void_p, ctypes.c_uint64,
    ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64),
]
_lib.bdo_nprime_at.restype = ctypes.c_int

_lib.bdo_nprime_n.argtypes = [ctypes.c_void_p]
_lib.bdo_nprime_n.restype = ctypes.c_uint64

_lib.bdo_nprime_count.argtypes = [ctypes.c_void_p]
_lib.bdo_nprime_count.restype = ctypes.c_uint64

# --- Error codes (must match bidder_root.h) ---

_OK = 0
_ERR_NULL = -1
_ERR_PERIOD = -2
_ERR_UNSUPPORTED_PERIOD = -3
_ERR_N = -4
_ERR_COUNT = -5
_ERR_INDEX = -6
_ERR_OVERFLOW = -7
_ERR_BACKEND = -8

# --- Constants ---

MAX_PERIOD_V1 = 0xFFFFFFFF  # 2^32 - 1


class UnsupportedPeriodError(ValueError):
    """Raised when `period` exceeds `bidder.MAX_PERIOD_V1`. See BIDDER.md."""


# --- Validation helpers ---

def _check_int(val, name):
    if type(val) is not int:
        raise TypeError(f"{name} must be int, got {type(val).__name__}")


def _check_uint64(val, name):
    _check_int(val, name)
    if val < 0 or val.bit_length() > 64:
        raise OverflowError(
            f"{name} must fit in a 64-bit unsigned integer, got {val}")


def _check_ssize(val, name):
    _check_int(val, name)
    if val < 0 or val > sys.maxsize:
        raise OverflowError(
            f"{name} must be at most sys.maxsize ({sys.maxsize}), got {val}")


# --- BidderBlock ---

class BidderBlock:
    """A keyed permutation of [0, period). See BIDDER.md."""

    def __init__(self, period, key):
        _check_int(period, "period")
        if period < 2:
            raise ValueError("period must be >= 2")
        if period > MAX_PERIOD_V1:
            raise UnsupportedPeriodError(
                f"period {period} exceeds maximum of {MAX_PERIOD_V1}")
        if not isinstance(key, (bytes, bytearray)):
            raise TypeError(
                f"key must be bytes or bytearray, got {type(key).__name__}")
        key_bytes = bytes(key)

        err = ctypes.c_int(0)
        self._handle = _lib.bdo_block_create(
            ctypes.c_uint64(period),
            key_bytes if key_bytes else None,
            ctypes.c_size_t(len(key_bytes)),
            ctypes.byref(err),
        )
        if self._handle is None or err.value != _OK:
            raise RuntimeError(f"bdo_block_create failed (err={err.value})")
        self._period = period

    def __del__(self):
        h = getattr(self, '_handle', None)
        if h is not None:
            _lib.bdo_block_free(h)

    def at(self, i):
        try:
            i = i.__index__()
        except (TypeError, AttributeError):
            raise TypeError(
                f"index must be an integer, got {type(i).__name__}")
        if not (0 <= i < self._period):
            raise ValueError(
                f"index {i} out of range [0, {self._period})")
        out = ctypes.c_uint32(0)
        rc = _lib.bdo_block_at(self._handle, ctypes.c_uint64(i),
                               ctypes.byref(out))
        if rc != _OK:
            raise RuntimeError(f"bdo_block_at failed (err={rc})")
        return int(out.value)

    @property
    def period(self):
        return self._period

    def __iter__(self):
        for i in range(self._period):
            yield self.at(i)

    def __len__(self):
        return self._period

    def __repr__(self):
        return f"BidderBlock(period={self._period})"

    def __next__(self):
        raise TypeError("'BidderBlock' object is not an iterator")


# --- NPrimeSequence ---

class NPrimeSequence:
    """Ascending enumeration of the first `count` n-primes. See BIDDER.md."""

    def __init__(self, n, count):
        _check_int(n, "n")
        if n < 2:
            raise ValueError("n must be >= 2")
        _check_uint64(n, "n")
        _check_int(count, "count")
        if count < 1:
            raise ValueError("count must be >= 1")
        _check_ssize(count, "count")

        err = ctypes.c_int(0)
        self._handle = _lib.bdo_nprime_create(
            ctypes.c_uint64(n), ctypes.c_uint64(count),
            ctypes.byref(err),
        )
        if self._handle is None or err.value != _OK:
            raise RuntimeError(f"bdo_nprime_create failed (err={err.value})")
        self._n = n
        self._count = count

    def __del__(self):
        h = getattr(self, '_handle', None)
        if h is not None:
            _lib.bdo_nprime_free(h)

    def at(self, K):
        try:
            K = K.__index__()
        except (TypeError, AttributeError):
            raise TypeError(
                f"index must be an integer, got {type(K).__name__}")
        if not (0 <= K < self._count):
            raise ValueError(
                f"index {K} out of range [0, {self._count})")
        lo = ctypes.c_uint64(0)
        hi = ctypes.c_uint64(0)
        rc = _lib.bdo_nprime_at(self._handle, ctypes.c_uint64(K),
                                ctypes.byref(lo), ctypes.byref(hi))
        if rc != _OK:
            raise RuntimeError(f"bdo_nprime_at failed (err={rc})")
        return (int(hi.value) << 64) | int(lo.value)

    @property
    def n(self):
        return self._n

    @property
    def count(self):
        return self._count

    @property
    def period(self):
        return self._count

    def __iter__(self):
        for i in range(self._count):
            yield self.at(i)

    def __len__(self):
        return self._count

    def __repr__(self):
        return f"NPrimeSequence(n={self._n}, count={self._count})"

    def __next__(self):
        raise TypeError("'NPrimeSequence' object is not an iterator")


# --- Public API ---

__all__ = [
    'cipher', 'sawtooth',
    'BidderBlock', 'NPrimeSequence',
    'MAX_PERIOD_V1', 'UnsupportedPeriodError',
]


def cipher(period, key):
    """Construct a keyed permutation of [0, period). See BIDDER.md."""
    return BidderBlock(period, key)


def sawtooth(n, count):
    """Construct an ascending enumeration of the first `count` n-primes.
    See BIDDER.md."""
    return NPrimeSequence(n, count)
