# Mahler check — pipeline validation

The CF expansion of `C_10(n)` for `n ≥ 2` is meaningless unless the
pipeline that produces it is computing CFs correctly. We pin the
pipeline against a tabulated case before we trust it on anything new.


## What we check

The classical Champernowne constant

    M = 0.123456789101112131415…

(the concatenation of the positive integers in base 10) has its CF
expansion catalogued. From OEIS A030167:

    M = [0; 8, 9, 1, 149083, 1, 1, 1, 4, …]

The fourth fractional partial quotient `a_4 = 149083` is Mahler's
famous spike — the first PQ his transcendence argument makes explicit.
Reproducing it exactly is a strong test of the pipeline: we hit a
specific 6-digit integer at a specific index, no rounding allowed.


## How

`cf_spikes.py:smoke_test()`:

1. Build the digit string `''.join(str(i) for i in range(1, 4000))` —
   the first ~14 800 digits of M.
2. Parse to `mpmath.mpf` at `PREC_BITS_LO` bits.
3. Run the reciprocal-and-floor loop for 30 steps.
4. Assert the first 8 fractional PQs equal `[8, 9, 1, 149083, 1, 1, 1, 4]`.

Anything weaker than the literal equality fails the test.


## What this certifies

- `mpmath.mpf` round-trips a long base-10 digit string correctly.
- The reciprocal-and-floor loop produces correct PQs at the chosen
  precision — including PQs with up to 6 digits.
- `int(mfloor(x))` extracts the partial quotient without off-by-one or
  truncation drift.

It does **not** certify that the loop is correct at *higher*
precisions (it runs at `PREC_BITS_LO = 80 000` bits) or under the
much larger PQs that appear in the n-Champernowne run. For those we
rely on the cross-precision check in `cf_partial_quotients` /
`stable_prefix_len`: run at `PREC_BITS_LO` and `PREC_BITS_HI = 2 × LO`
and keep only the agreeing prefix.

The Mahler check is the cheap pin. The cross-precision check is the
expensive guardrail. Both run on every invocation of `cf_spikes.py`.


## Why use Mahler specifically

Two reasons:

1. **It's the same kind of object.** M is the b=10 instance of the
   integer Champernowne family; `C_10(n)` is the b=10 instance of the
   n-prime sieve family. They share the digit-block structure that
   creates spikes. Validating on M means our pipeline knows how to
   *find* the kind of spike we're hunting for. A test on a generic
   real (Khinchin-typical PQs, all small) wouldn't exercise the same
   code path.

2. **It's tabulated to many PQs.** A030167 lists thousands of PQs of
   M. If we ever need to extend the smoke test (e.g. after changing
   the precision discipline), the ground truth is already published.


## Failure modes the check rules out

| failure | what would happen | what we'd see |
|---|---|---|
| `mpf` parses digit string wrong | wrong real number, wrong CF | `a_1` wrong (would be 8 ± something) |
| Reciprocal precision loss in loop | early divergence | `a_4 ≠ 149083` |
| Off-by-one in `floor`/`int` | systematic shift in PQ values | small PQs slightly wrong |
| Skipping `a_0 = 0` incorrectly | misalignment by one | `a_1 = 8` becomes `a_2 = 8` |

If any of those held in the n-Champernowne data, we'd be reporting
artifacts. The smoke test makes that unlikely on every run.


## Cost

~0.5s. Always run before the main loop.
