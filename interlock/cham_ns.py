"""
Champernowne encoder for atom sequences, plus leading-digit utilities.

For a sequence (a_1, a_2, …, a_K) of positive integers, build the
Champernowne real

    cham(K) := 1.‖ digits(a_1) ‖ digits(a_2) ‖ … ‖ digits(a_K)

in a chosen base, and read off leading-digit / per-decade statistics.
Lifts the encoding from `core/ACM-CHAMPERNOWNE.md` (which acts on
n-prime sequences) to arbitrary integer sequences. Used by the
`experiments/interlock/` programme to compare atom sequences from
numerical semigroups against ACM and prime baselines.
"""

from fractions import Fraction
from numbers import Integral


_DIGIT_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _validate_base(base):
    if not isinstance(base, Integral) or base < 2:
        raise ValueError("base must be an integer ≥ 2")
    return int(base)


def digits(n, base=10):
    """Digits of n ≥ 0 in given base, most significant first."""
    base = _validate_base(base)
    if not isinstance(n, Integral) or n < 0:
        raise ValueError("n must be non-negative")
    n = int(n)
    if n == 0:
        return [0]
    out = []
    while n:
        out.append(n % base)
        n //= base
    return out[::-1]


def cham_digits(seq, base=10):
    """Concatenated digits of seq, MSF-first per element."""
    out = []
    for a in seq:
        out.extend(digits(a, base))
    return out


def cham_real_string(seq, base=10):
    """The string '1.<concatenated base-`base` digits>' for the sequence."""
    base = _validate_base(base)
    if base > len(_DIGIT_ALPHABET):
        raise ValueError("string rendering supports bases up to 36")
    return '1.' + ''.join(_DIGIT_ALPHABET[d] for d in cham_digits(seq, base))


def cham_real(seq, base=10, prec_digits=18):
    """Exact rational truncation after `prec_digits` post-radix digits."""
    base = _validate_base(base)
    if not isinstance(prec_digits, Integral) or prec_digits < 0:
        raise ValueError("prec_digits must be a non-negative integer")
    digit_list = cham_digits(seq, base)[:prec_digits]
    val = Fraction(1, 1)
    factor = Fraction(1, base)
    for d in digit_list:
        val += d * factor
        factor /= base
    return val


def leading_digit(n, base=10):
    """Most-significant digit of n ≥ 1 in given base."""
    base = _validate_base(base)
    if not isinstance(n, Integral) or n < 1:
        raise ValueError("n must be ≥ 1")
    n = int(n)
    while n >= base:
        n //= base
    return n


def decade(n, base=10):
    """The d ≥ 1 with base^(d-1) ≤ n < base^d."""
    base = _validate_base(base)
    if not isinstance(n, Integral) or n < 1:
        raise ValueError("n must be ≥ 1")
    n = int(n)
    d = 0
    while n > 0:
        d += 1
        n //= base
    return d


def leading_digit_histogram(seq, base=10):
    """Counts indexed [0..base-2] for leading digits 1..base-1."""
    base = _validate_base(base)
    counts = [0] * (base - 1)
    for a in seq:
        counts[leading_digit(a, base) - 1] += 1
    return counts


def per_decade_histograms(seq, base=10):
    """Per-decade leading-digit counts.

    Returns dict { d: counts } where `d` is the decade index (the unique
    d with base^(d-1) ≤ a < base^d) and `counts` is a length-(base-1)
    list indexed by leading-digit-minus-one.
    """
    base = _validate_base(base)
    by_decade = {}
    for a in seq:
        d = decade(a, base)
        if d not in by_decade:
            by_decade[d] = [0] * (base - 1)
        by_decade[d][leading_digit(a, base) - 1] += 1
    return by_decade


# Self-check: anchors against INTERLOCKING-DEFECTS.md §5.
if __name__ == "__main__":
    # First 12 atoms of ⟨3, 5⟩ (matches ns_atoms.py self-check).
    atoms_12 = [3, 5, 6, 8, 10, 11, 12, 13, 14, 16, 17, 19]

    # §5 Champernowne digit string.
    s = cham_real_string(atoms_12, base=10)
    assert s == '1.35681011121314161719', s

    # Exact rational truncation.
    val = cham_real(atoms_12, base=10, prec_digits=20)
    assert val == Fraction(135681011121314161719, 10**20), val

    # Bases above 10 use a single-character digit alphabet, not decimal
    # spelling of each digit.
    assert cham_real_string([10, 35], base=36) == '1.AZ'

    # Leading-digit primitives.
    assert leading_digit(7) == 7
    assert leading_digit(35681) == 3
    assert leading_digit(100) == 1
    assert decade(1) == 1
    assert decade(9) == 1
    assert decade(10) == 2
    assert decade(99) == 2
    assert decade(100) == 3

    # Aggregate histogram of the 12 atoms.
    # Leading digits: 3, 5, 6, 8, 1, 1, 1, 1, 1, 1, 1, 1.
    # Counts (1..9):   8, 0, 1, 0, 1, 1, 0, 1, 0.
    h = leading_digit_histogram(atoms_12)
    assert h == [8, 0, 1, 0, 1, 1, 0, 1, 0], h

    # Per-decade.
    by_dec = per_decade_histograms(atoms_12)
    # Decade 1 [1, 9]: atoms 3, 5, 6, 8 → leading digits 3, 5, 6, 8.
    assert by_dec[1] == [0, 0, 1, 0, 1, 1, 0, 1, 0]
    # Decade 2 [10, 99]: atoms 10..19 (eight of them) → all leading 1.
    assert by_dec[2] == [8, 0, 0, 0, 0, 0, 0, 0, 0]

    print("cham_ns self-check: PASS")
