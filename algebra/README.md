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
   the master expansion (`Q-FORMULAS.md`) and the rank lemma
   (`FINITE-RANK-EXPANSION.md`) — and either reduce to them or
   extend them.

## Files

- `Q-FORMULAS.md` — formula sheet for `Q_n(m)`, the rank-h
  Mercator expansion of `log(1 + n^{-s} ζ(s))`.
- `FINITE-RANK-EXPANSION.md` — finite-rank truncation of the
  expansion at `j = ν_n(m)`. The rank lemma's one-line proof,
  the local-vs-aggregate split.
- `predict_q.py` — exact-rational implementation of the master
  expansion. `q_value_by_class(shape, h, tau_sig) -> Fraction`
  returns the conditional Q value (gcd=1 case). `q_general(n, h,
  k)` returns the general value as a `Fraction`. SymPy-free
  (uses Python's `fractions.Fraction` for exactness).
- `predict_correlation.py` — decomposition of within-row
  autocorrelation as a sum over τ-pair joint densities times
  algebraic Q values. The algebraic part is exact; the joint
  density is computed by direct enumeration.
- `test_anchors.py` — verifies `predict_q.q_value_by_class` against
  the 8 × 6 matrix anchors documented in `Q-FORMULAS.md` and
  rendered in
  `experiments/acm-champernowne/base10/art/q_distillery/q_h5_shape_tau_matrix.png`.
- `test_within_row_lattice.py` — compares predicted within-row
  autocorrelation against the empirical lattice at h ∈ {5, 6, 7, 8},
  for several primes n.
- `WITHIN-ROW-PARITY.md` — first closed-form deliverable: the
  decomposition of the within-row parity profile by τ-pair joint
  density, the mechanism for the even-L vs odd-L gap, and
  validation against the empirical lattice.

## Workflow standard

For each closed-form claim:

1. **State the claim** algebraically as a deterministic function
   from (shape, h, lag, axis, ...) to a number.
2. **Implement the function** in this directory.
3. **Anchor at canonical inputs** — `k = 1`, `k = p`, `k = p²`,
   plus matrix anchors. Functions that don't reproduce anchors
   exactly do not get to claim agreement on harder inputs.
4. **Compare to empirical lattice** at h ∈ {5, 6, 7, 8} (cached).
   Differences ≤ 1e-3 in dimensionless quantities count as
   verified; larger differences mean the claim needs refinement
   or the empirical data is being mis-aggregated.
5. **Document** in a Markdown file: claim, derivation, validation
   results, what it predicts, what it doesn't.
