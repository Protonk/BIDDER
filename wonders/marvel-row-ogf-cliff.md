# Marvel: The Row-OGF Cliff

**Date entered.** 2026-05-01

**Category.** Marvel.

## Description

For prime `p` and `k' ≥ 2` coprime to `p`, the prime-row generating
function

    F(x; p, k') = Σ_{h ≥ 1} Q_p(p^h k') · x^h

is a polynomial of degree exactly `Ω(k')`. The leading coefficient is
`(−1)^{Ω−1} (Ω−1)! / ∏ e_i!`, which is the same multinomial value that
appears at the kernel-zero boundary `Ω(k') = h`. The row sum
`F(1; p, k')` collapses to `1/e` when `k' = q^e` is a single prime
power, and to `0` otherwise.

For the single-prime-cofactor case the closed form is sharper still:

    F(x; p, q^e) = (1 − (1 − x)^e) / e,    [x^h] F = (−1)^{h−1} C(e, h) / e.

The row stops being a polynomial only at `k' = 1`, where `F` is the
divergent `−log(1 − x)` and `[x^h] F = 1/h` is the prime-row identity.

The construction made no promise of polynomial-ness; the master
expansion is an alternating binomial-times-tau sum that *could* have
produced an infinite power series for every `k'`. The cliff at
`Ω(k') + 1` is forced by the kernel-zero theorem, and `ROW-OGF.md`
derives the leading coefficient directly from the kernel-zero
boundary theorem (ii) — so the same multinomial number is *forced*
to appear at both places, not coincident there. The marvel is
downstream of that derivation: the row truncates at exactly the
predicted degree, the leading coefficient is exactly the predicted
multinomial, and for single-prime cofactors the entire row collapses
to the closed form `(1 − (1 − x)^e)/e`.

## Evidence

- `algebra/ROW-OGF.md` — statement, proof, and the
  `(1 − (1 − x)^e)/e` closed form.
- `algebra/KERNEL-ZEROS.md` §"Statement" (ii) — the boundary
  multinomial that becomes the OGF leading coefficient.
- `algebra/tests/test_anchors.py` A10 — closed-form match across
  primes and exponents (`A10a`: 180 cross-checks); degree and
  leading-coefficient contract (`A10b`, `A10c`: 901 cases each);
  row-sum closed form (`A10d`: 901 cases).
- `algebra/predict_q.py:253` — `row_polynomial`, `row_polynomial_qe_closed`,
  `row_sum`.

## Status

Anchored. Two implementations of the row at `q^e` cofactors —
`row_polynomial` from the master expansion and
`row_polynomial_qe_closed` from the closed form `(1 − (1 − x)^e)/e` —
agree on every test cell (anchor A10a, 180 cases). No open dependencies.

## Aesthetic note

TODO: aesthetic note (human)

## Provocation

`algebra/PROPOSED-CLOSED-FORMS.md` Proposal 4 — composite-`p` row OGFs.
The polynomial cliff is prime-row-only; for composite `p` the OGF
becomes a cyclotomic-denominator object, not polynomial. Whether the
cyclotomic structure has its own clean closed form is open. The
prime-row marvel is what motivates asking.

## Cross-references

- `wonder-cost-ladder.md` — the prime-row row sum collapsing to `1/e`
  or `0` is part of why the cost of *summing* a row is bounded; the
  cost ladder is about other coordinates of cost climbing the height
  tower.
- (forthcoming `monster-denominator-bound`) — same algebra paying out
  tighter than expected, in the opposite aesthetic register.

## Discovery context

The closed form `(1 − (1 − x)^e)/e` was first written down as a
direct evaluation: take the master expansion at shape `(1,)`,
`tau_sig = (e,)`, treat `j` as the coefficient index, sum the binomial
series. The cleanness of the result was visible immediately. The
agreement between `row_polynomial` (master expansion) and
`row_polynomial_qe_closed` (the closed form) on every `q^e` cofactor,
across primes `p`, is what promoted this from "closed form for one
case" to "row-OGF cliff for every prime cofactor."
