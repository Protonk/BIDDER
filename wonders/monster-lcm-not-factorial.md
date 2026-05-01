# Monster: The lcm-not-Factorial Denominator

**Date entered.** 2026-05-01

**Category.** Monster.

## Description

For every `m ∈ M_n` with height `h = ν_n(m) ≥ 1`, the denominator of
`Q_n(m)` divides `lcm(1, 2, …, h)`. Not `h!`. The proof is one
paragraph: each term of the master expansion is an integer divided by
`j`, the integers vary, the `j`s do not, so the common denominator of
the `h` summands is the lcm.

The naive expectation, if you read the master expansion as `Σ …/j`,
is that the denominator divides `h!`. The naive expectation is wrong
in the right direction: `lcm(1, …, h) | h!` strictly for `h ≥ 4`. At
`h = 6` the gap is already `60 | 720` — the lcm form is *twelve times
tighter* than the factorial would be. At `h = 8` the gap is
`840 | 40320` — forty-eight times tighter. Whatever the master
expansion is doing, it is doing it more parsimoniously than the form
of its summation suggests.

The Monster register is the offence. `h!` is the prettier denominator
in every conventional sense: it factors cleanly, it has the
combinatorial reading every algebraist already carries, it is the
denominator a textbook would predict for a sum of `h` rationals each
of denominator dividing `j ≤ h`. `lcm(1, …, h)` is uglier — it does
not factor cleanly, it has no clean combinatorial reading, it grows
sub-factorially with a non-elementary rate (Chebyshev's `ψ(n)`), and
it is the denominator the construction forces. The construction
*will not give back* `h!`-shaped denominators. The substrate is
constitutively unable to be that pretty.

The ugliness is the data. A construction that produced
`h!`-denominators would be loose at the boundary; the
`lcm`-denominator is tight, in the sense that anchor A9 verifies
the bound at 1650 cells with no slack at any of them. The Monster's
shape is exactly: the construction is forced to a form that offends
ordinary aesthetic expectations, *and* the offence traces back to
why the form is correct rather than approximate.

## Evidence

- `algebra/DENOMINATOR-BOUND.md` — statement, one-paragraph proof,
  the explicit `lcm(1..6) = 60` vs `6! = 720` worked example.
- `algebra/tests/test_anchors.py` A9 — 1650 `(n, h, k)` triples with
  the bound applied in the *true* `ν_n(m)`, including the cases
  where `k` carries extra factors of `n`'s primes that lift the
  effective height.
- `algebra/predict_q.py:n_adic_height` — the primitive that computes
  `ν_n(m)` correctly for the composite-overlap cases the bound
  requires.
- `algebra/MASTER-EXPANSION.md` — the source of the `Σ (integer)_j / j`
  shape that makes the `lcm` denominator inevitable.

## Status

Anchored. The bound is sharp at every cell A9 tests. No open
dependencies; the `lcm` denominator is what the master expansion
produces and what the implementation respects.

## Aesthetic note

TODO: aesthetic note (human)

## Provocation

Two questions worth writing down:

- **Is there a substrate operation that smooths the `lcm` to `h!` at
  the cost of weakening some other property?** Probably not — the
  master expansion's structure is tight, and any rewriting that
  enlarged the denominator would be moving away from the construction
  rather than toward it. But the question is the natural one to ask
  when the form offends, and the negative answer (if it is negative)
  is itself a structural fact about what the substrate can be.
- **`lcm(1, …, h)` connects to Chebyshev's `ψ` function and the prime
  number theorem** (`log lcm(1..h) = ψ(h) ∼ h`). The denominator's
  growth rate is therefore connected to the distribution of primes,
  not just to the master expansion's summation shape. Is there a
  reading where `Q_n`'s denominator structure is a fingerprint of
  prime distribution? The connection is suggestive enough to name;
  whether it pays out is open.

## Cross-references

- `marvel-row-ogf-cliff.md` — the same algebra in the opposite
  affective register. The marvel is what the master expansion
  produces that is cleaner than expected; this monster is what it
  produces that is uglier than expected. Both are downstream of the
  same construction; the cabinet keeps them adjacent for that reason.
- `wonder-cost-ladder.md` — the numerical-coordinate of the cost
  ladder partly traces to this denominator structure. At `h = 8`
  the bignum widths required for exact arithmetic are governed by
  `lcm(1..8) = 840` and the integer numerators that compose against
  it; the denominator's growth shape is one ingredient of how
  expensive the height tower becomes.
- `sport-riemann-sum-identity.md` — both are constructions where the
  natural-looking form (`h!` denominator there; statistical estimate
  here) is over-specified and the actual shape (`lcm` denominator;
  exact Riemann sum) falls out of structural facts the form
  predicts only obliquely.

## Discovery context

The bound was first noticed when the exact-rational implementation
of `q_general` started producing denominators consistently smaller
than `h!`. The empirical observation pattern was: `denominator of
Q_n(m)` is a divisor of *something* smaller than the obvious
`h!`-bound. `lcm(1, …, h)` was the first guess and it held; the
proof followed and is one paragraph. Anchor A9 was added to gate the
bound at 1650 cells across `n ∈ [2, 12]`, `h ∈ [1, 6]`,
`k ∈ [1, 25]`, applied in the true `ν_n(m)` (the input `h` plus any
overlap `k` carries against `n`'s primes). The anchor's framing —
"the bound divides `lcm(1, …, ν_n(m))` not `lcm(1, …, h)`" — is
itself a sharper statement than the doc's version, and the framing
came from an audit pass that flagged the discrepancy between
declared input `h` and effective height.
