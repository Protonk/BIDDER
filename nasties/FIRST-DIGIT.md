# first_digit truncation bug

## The bug

`first_digit` in `acm_core.py` extracts the leading significant digit
via `int(10**frac)` where `frac` is the fractional part of log10(x).
When `10**frac` should be exactly an integer but IEEE 754 delivers
something like 7.999999999999999, `int()` truncates to 7.

Affected integers in 1..9999:

    8, 30, 40, 50, 80, 500, 600, 900, 5000, 6000, 9000

The pattern: inputs whose base-10 mantissa is an exact integer.
`log10(8) = 3 * log10(2)` accumulates enough float error that
`10**(log10(8) - floor(log10(8)))` = 7.999999999999999 instead of 8.
Same mechanism for all affected values.

`first_digit_array` has the same bug (same formula, vectorized).

## Blast radius

**BIDDER generator**: not affected. It extracts leading digits via
integer division (`n // base**(d-1)`), not log10.

**Champernowne reals**: not affected. All values are in [1.1, 2.0),
so their mantissas are never exact integers. `first_digit` returns
1 correctly for all of them.

**Experiments**: low risk but not zero. The rolling shutter and
multiplication experiments apply `first_digit` to sums and products
of Champernowne reals. These are unlikely to land on exact integer
mantissas, but a sum of ~6.45 Champernowne reals could hit 10.0
or 100.0 exactly in principle.

## The fix

    int(10**frac + 1e-9)

Adding a small epsilon before truncation nudges values like
7.999999999999999 past the integer boundary without disturbing
legitimate near-boundary values like 1.999 (which should stay
at digit 1, not round up to 2). The float error from the log10
round-trip is ~1 ULP (~10^-15), so 1e-9 is six orders of magnitude
of headroom without reaching the nearest real concern.

Same fix applies to `first_digit_array`:

    np.minimum((10**frac + 1e-9).astype(int), 9)

A naive `+ 0.5` fix breaks values like 1.999 (rounds to digit 2).

## Found by

`test_acm_core.py::test_first_digit_integer_accuracy`, which checks
`first_digit(float(n))` against `int(str(n)[0])` for n = 1..9999.
