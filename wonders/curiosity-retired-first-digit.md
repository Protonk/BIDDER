# Retired Curiosity: The first_digit Pothole

**Date entered.** 2026-05-01 (folded in from `nasties/` proto-cabinet)

**Category.** Curiosity (retired — resolved as a floating-point bug
with a known fix).

**Previously.** `nasties/FIRST-DIGIT.md` — the proto-cabinet, where
this and similar implementation traps lived before the wonder
cabinet existed.

## Description

`first_digit` in `core/acm_core.py` implements LD10 (the
leading-significant-digit operator) as `int(10**frac)` where
`frac` is the fractional part of `log₁₀(x)`. The exact-math
definition is integer-correct. In IEEE 754, the round-trip
`x → log₁₀(x) → 10^(frac)` for inputs whose base-10 mantissa is
itself an integer can deliver `7.999999999999999` instead of
`8` — and `int()` truncates, not rounds. So `first_digit(8)`
returns `7`.

Eleven integers in `[1, 9999]` hit the trap:

    8, 30, 40, 50, 80, 500, 600, 900, 5000, 6000, 9000.

Each one has an exact-integer base-10 mantissa. The pattern:
`log₁₀(8) = 3 · log₁₀(2)` accumulates enough float error that the
inverse round-trip lands just below the integer boundary;
`int()` then loses the digit.

The fix is `int(10**frac + 1e-9)`. The float round-trip error is
~1 ULP (~`10^{-15}`), so `1e-9` is six orders of magnitude of
headroom without disturbing legitimate near-boundary values like
`1.999` (which should stay at digit 1, not round up to 2). Same
fix vectorises for `first_digit_array` as
`np.minimum((10**frac + 1e-9).astype(int), 9)`.

## Why it earned its slot

The vexation has a specific weird shape: the bug fires *only* on
the cleanest possible inputs. `8 = 8 · 10⁰`; `30 = 3 · 10¹`;
`5000 = 5 · 10³`. Every affected integer is a single nonzero
significant digit followed by zeros. The implementation is wrong
*exactly where the math is most pristine* — the cleaner the number,
the more likely the bug. That inversion of expectation, rather than
the bug itself, is what made this nasties-folder-worthy and now
cabinet-shelf-worthy.

The bug is not a live concern in the production paths. BIDDER's
generator extracts leading digits via integer division
(`n // base**(d-1)`), not log10. Champernowne reals all live in
`[1.1, 2.0)`, with mantissas that aren't integers, so `first_digit`
returns `1` correctly for all of them. The pothole is in the
abstract contract layer, not where the project usually drives.

## Evidence

- `core/acm_core.py:first_digit` and `first_digit_array` — the two
  affected functions.
- `tests/test_acm_core.py::test_first_digit_integer_accuracy` —
  the regression test that found the bug, checking
  `first_digit(float(n))` against `int(str(n)[0])` for
  `n = 1..9999`.
- `BQN-AGENT.md` `LD10` — the exact-math definition that
  the float implementation is meant to realise.

## Status

Retired. The bug is documented; the fix (`+ 1e-9`) is recorded;
the regression test gates against re-introduction. The pothole is
a permanent feature of `int(10**frac)`-style implementations of
LD10 across IEEE 754; the *fix* is local. No follow-up probe is
called for.

## Aesthetic note

It's specifically vexing in a weird way. The bug fires only on
the cleanest possible inputs — integers whose base-10 mantissa is
itself an integer — which means the implementation is wrong
exactly where the math is most pristine. `8` should be the easy
case; `8` is the hard case. The simpler the number, the more
likely the bug. The vexation is the inversion of the usual
implementation-defect pattern, where messy inputs are dangerous
and clean ones are safe. Here cleanliness is the trap.

## Provocation

The retired status means there is no live probe to run on this
specimen. One residual question, noted but not held: are there
analogous LD-extraction code paths elsewhere in the codebase that
use the same `int(10**frac)` pattern and haven't yet hit their
test? A grep for `10**frac` or `pow(10, frac)` would find them;
the fix is mechanical.

## Cross-references

- `sport-riemann-sum-identity.md` — both sit at the math/float
  boundary, but in opposite directions. The sport: an exact result
  at `N = P` falls out of "π is a bijection," works in float
  because the argument needs no float arithmetic. The retired
  curiosity: an integer fact (`first_digit(8) = 8`) that *does*
  route through float arithmetic, and the float layer loses the
  integer. The cabinet keeps both as the math-vs-float interface's
  two faces.

## Discovery context

`nasties/FIRST-DIGIT.md` predates this cabinet. The bug was found
by `test_first_digit_integer_accuracy`, the obvious-but-not-trivial
test of the leading-digit function against the string-based
extraction `int(str(n)[0])` — a test that exists *because* the
log10 formulation is suspicious by construction.

The proto-cabinet `nasties/` was the project's way of cataloguing
implementation traps before the wonder cabinet existed; the
first-digit pothole is folded into the cabinet here as a retired
curiosity to honour that lineage and let `nasties/` be retired.
The cabinet's discipline allows specimens to move between
categories; allowing them to move between "live" and "retired"
within a category is a small extension of the same idea, earning
its way in here on the strength of a single specimen with a
proto-cabinet history.
