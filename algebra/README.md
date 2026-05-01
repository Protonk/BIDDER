# algebra/

Closed-form algebraic work on `Q_n(m)` and the master expansion.
Each piece of content (definition, theorem, evaluated table) lives in
exactly one file; other files refer to it by path and theorem name
without restating it. Every theorem either has a numbered entry in
`test_anchors.py` (A1..A10) or names the in-tree self-check that
exercises it (e.g. `predict_correlation._self_check` for the
within-row decomposition, whose statement is a tautological partition
of the autocorrelation sum).

## Files

### Definitions and primitives

- `OBJECTS.md` — `M_n`, `ζ_{M_n}`, `Q_n`, `h = ν_n(m)`, `τ_j`, `Ω`,
  `ω`, shape, τ-signature. Notation table cross-referencing
  `predict_q.py` and `guidance/BQN-AGENT.md`.
- `MASTER-EXPANSION.md` — the master expansion theorem and proof
  (anchors A4, A5). BQN: `Qn`. Three corollaries (rank truncation,
  prime-row `1/h` identity, integer-language reading).
- `RANK-LEMMA.md` — truncation of the master expansion at
  `j = ν_n(m)` (anchor A4 exercises it).

### Theorems

- `UNIVERSAL-CLIFF.md` — `Q_n(n² k) = 1 - d(k)/2` (anchor A3). BQN: `H2`.
- `DENOMINATOR-BOUND.md` — `denom(Q_n(m)) | lcm(1, …, ν_n(m))`
  (anchor A9).
- `KERNEL-ZEROS.md` — prime-`n` classifier and `Ω(k) = h` boundary
  formula (anchors A7, A8 with the (shape, τ-sig) matrices at
  `h = 5, 6, 7, 8`).
- `ROW-OGF.md` — prime-row generating function `F(x; p, k')`,
  polynomial of degree `Ω(k')` for `k' ≥ 2`, with the
  single-prime-power closed form `(1 - (1-x)^e)/e` and the row sum
  `F(1; p, k') ∈ {1/e, 0}` (anchor A10).
- `WITHIN-ROW-PARITY.md` — class-pair decomposition of the
  within-row autocorrelation. Algebraic factor exact via
  `predict_q.q_value_by_class`; combinatorial factor open
  (`PROPOSED-CLOSED-FORMS.md` Proposal 6).

### Tables

- `TABLES.md` — evaluated specializations of the master expansion:
  prime-`n` rows at low `h`; prime power `n = 4` at low `h`;
  squarefree multi-prime `r = 2` at `h = 2, 3, 4`. The 8 × 6
  (shape, τ-sig) matrices at `h = 5, 6, 7, 8` are tabulated in
  `KERNEL-ZEROS.md` (anchors A2, A8).

### Forward-looking

- `PROPOSED-CLOSED-FORMS.md` — open proposals. Proposals 1–3 landed
  (`ROW-OGF.md` and `KERNEL-ZEROS.md`); 4–7 are open.

### Indexes (legacy redirects)

- `Q-FORMULAS.md` — thin index pointing to successor files.
- `FINITE-RANK-EXPANSION.md` — thin index pointing to successor files.

### Code

- `predict_q.py` — exact-rational implementation of the master
  expansion (`q_value_by_class`, `q_general`) and the prime-row OGF
  (`row_polynomial`, `row_polynomial_qe_closed`, `row_sum`).
- `predict_correlation.py` — within-row autocorrelation by class-pair
  decomposition; algebraic factor exact via `predict_q`, joint
  density by enumeration.
- `test_anchors.py` — anchor harness A1–A10; all PASS gates the
  closed-form work in this directory.
- `test_within_row_lattice.py` — cross-checks `predict_q` against
  `q_lattice_4000_h{5,6,7,8}.npy`.

## Workflow standard

For each closed-form claim:

1. **State** the claim algebraically as a deterministic function from
   `(shape, h, …)` to a number.
2. **Implement** in `predict_q.py` using exact `Fraction` arithmetic.
   No floats, no `mpmath`, no `sympy`.
3. **Anchor** at canonical inputs in `test_anchors.py`. Anchors are
   the contract: a function that fails its anchor cannot claim
   agreement on harder inputs.
4. **Format-consistency check** against the cached
   `q_lattice_4000_h{5,6,7,8}.npy` files where applicable
   (`test_within_row_lattice.py`).
5. **Document** in a single Markdown file using the template in this
   README:

   ```
   # <Theorem name>
   ## Statement
   ## BQN
   ## Proof
   ## Anchor
   ```

   No "what this predicts," no "what this does not predict," no
   "reading," no rhetorical commentary. Open questions go in
   `PROPOSED-CLOSED-FORMS.md`. Empirical data tables (e.g. the
   autocorrelation readout in `WITHIN-ROW-PARITY.md`) appear under
   their own §"Empirical readout" heading and contain numbers, not
   commentary.

## Adding a new theorem

1. Create `<NAME>.md` using the template above.
2. Add an anchor `A<n+1>` to `test_anchors.py`. Update the docstring
   anchor list there.
3. Append the file to this README's file index (one line).
4. If a row in `TABLES.md` is now subsumed, replace the row with a
   pointer to the new theorem.
5. If the new theorem closes an entry in `PROPOSED-CLOSED-FORMS.md`,
   mark that proposal as resolved with a one-line pointer.

## Adding a new table row

A new evaluated specialisation (e.g. a higher-`h` entry, a new shape):
add a row to `TABLES.md`. No new file needed.
