# algebra/

Closed-form algebraic work on `Q_n(m)` and the finite-rank
expansion. Code and analyses in this directory are kept rigorous
in the sense that:

1. Every algebraic claim is implemented as a function that returns
   an exact rational (or a numeric value derived from one).
2. Every claim is validated against canonical inputs whose values
   are independently known (the `q_h5_shape_tau_matrix` anchors,
   `Q_p(p^h · 1) = 1/h`, etc.).
3. Every claim that touches the empirical lattices is checked
   against `experiments/acm-champernowne/base10/art/q_distillery/`
   cached data (`q_lattice_4000_h{5,6,7,8}.npy`).
4. Closed-form claims ride on top of two algebraic primitives —
   the master expansion (`algebra/Q-FORMULAS.md`) and the rank
   lemma (`algebra/FINITE-RANK-EXPANSION.md`) — and either reduce
   to them or extend them.

## Files

- `algebra/Q-FORMULAS.md` — formula sheet for `Q_n(m)`, the
  rank-h Mercator expansion of `log(1 + n^{-s} ζ(s))`.
- `algebra/FINITE-RANK-EXPANSION.md` — finite-rank truncation of
  the expansion at `j = ν_n(m)`. The rank lemma's one-line
  proof, the local-vs-aggregate split.
- `algebra/predict_q.py` — exact-rational implementation of the
  master expansion. `q_value_by_class(shape, h, tau_sig) ->
  Fraction` returns the conditional Q value (gcd=1 case).
  `q_general(n, h, k)` returns the general value as a
  `Fraction`. SymPy-free (uses Python's `fractions.Fraction` for
  exactness).
- `algebra/predict_correlation.py` — decomposition of within-row
  autocorrelation as a sum over τ-pair joint densities times
  algebraic Q values. The algebraic part is exact; the joint
  density is computed by direct enumeration.
- `algebra/test_anchors.py` — verifies
  `algebra/predict_q.py:q_value_by_class` against the 8 × 6
  matrix anchors documented in `algebra/Q-FORMULAS.md` and
  rendered in
  `experiments/acm-champernowne/base10/art/q_distillery/q_h5_shape_tau_matrix.png`.
- `algebra/test_within_row_lattice.py` — compares predicted
  within-row autocorrelation against the empirical lattice at
  h ∈ {5, 6, 7, 8}, for several primes n.
- `algebra/WITHIN-ROW-PARITY.md` — first closed-form deliverable:
  the decomposition of the within-row parity profile by τ-pair
  joint density, the mechanism for the even-L vs odd-L gap, and
  validation against the empirical lattice.

## Workflow standard

For each closed-form claim:

1. **State the claim** algebraically as a deterministic function
   from (shape, h, lag, axis, ...) to a number.
2. **Implement the function** in this directory using exact
   `Fraction` arithmetic (Python's `fractions` module). No floats,
   no `mpmath`, no `sympy` — exact rationals all the way through.
3. **Anchor at canonical inputs (ground truth)** — `Q_p(p^h · 1) =
   1/h`, the 8×6 `(shape, tau_sig)` matrix at h = 5, the universal
   `Q_n(n²k) = 1 − d(k)/2` cliff, the master/class-form
   consistency. These values are derived from the master expansion
   and frozen in `test_anchors.py`. Functions that don't reproduce
   anchors exactly do not get to claim agreement on harder inputs.
4. **Format-consistency check** against the cached
   `q_lattice_4000_h{5,6,7,8}.npy` files. The lattice is produced
   by `q_general` in
   `experiments/acm-champernowne/base10/art/q_distillery/q_lattice_full_bleed.py`,
   which implements the *same* master expansion as
   `algebra/predict_q.py` (same `nu_n_k = min(t // a)`, same
   `h_eff` handling, same outer `j` loop, same binomial-product
   structure; the differences are float-vs-Fraction and one
   inlined τ_j sum vs the `tau()` helper). Float-level agreement
   (≤ 1e-7) catches indexing, convention, and overlap-case bugs
   that show up as a different-shape array, but it is *not* an
   independent ground truth. The ground truth is step 3 — the
   matrix anchors at `h = 5`, the prime-row identity, and the
   universal cliff, derived directly from the master expansion
   and frozen.
5. **Document** in a Markdown file: claim, derivation, validation
   results, what it predicts, what it doesn't.
