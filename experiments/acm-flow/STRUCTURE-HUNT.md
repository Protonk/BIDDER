# STRUCTURE-HUNT — after Phase 1

Phase 1 changed the object. The four-coordinate tomography model in
`ACM-MANGOLDT.md` collapsed under destroyers: the truncated-flow
residual `ρ` is mostly cutoff/saturation, while the local arithmetic
signal lives in

    Q_n(m) = Λ_n(m) / log(m)

with exact rational closed form

    Q_n(m) = Σ_{j ≥ 1, n^j | m} (-1)^(j-1) τ_j(m/n^j) / j.

The hunt is now two-layered:

    local algebra closes by finite rank;
    global stream claims are checked by Hardy deep access.

`core/Q-FORMULAS.md` and `core/FINITE-RANK-EXPANSION.md` are the local
side. `experiments/math/hardy/DEEP-TROUBLE-No-4.md` is the global
sampling side.


## Phase 1 Outcomes

See `PHASE1-RESULTS.md` and `MEMO-PHASE1.md`.

| pre-Phase-1 claim | post-destroyer status |
|---|---|
| `ρ` is the spectroscopic observable | refuted; `ρ` does not carry payload signal |
| four-coordinate decomposition | collapsed to finite-rank local algebra plus cutoff side effects |
| cutoff coordinate | demoted; large effect is truncation, tiny residue is mainly n=2 `v_2(Y)` |
| payload graduation on `Λ_n` | evidence; m-shuffle null z ≥ 5 every cell |
| `Λ_n` is the local observable | replaced by exact rational `Q_n = Λ_n/log(m)` |
| prime/composite split at h=3 | evidence; should become a corollary of Q-formulas |


## Current Model

The coordinates are not independent. They are the pieces of one closed
form.

| coordinate | role |
|---|---|
| height `h = ν_n(m)` | finite rank; selects which `τ_j` enter |
| payload divisor data | the values `τ_j(m/n^j)` through rank `h` |
| factorisation of `n` | determines binomial coefficients after multiplicativity |
| payload overlap with `n` | for composite `n`, exact height gives `n ∤ k`, not `gcd(n,k)=1` |

The composite case must use the overlap vector from
`core/Q-FORMULAS.md`: write

    n = ∏ p_i^{a_i},        m = n^h k,
    k = ∏ p_i^{t_i} k',     gcd(k', n) = 1,

with at least one `t_i < a_i`. Prime `n` is the special clean case
where exact height forces `gcd(n,k)=1`.


## Phase 2 — Local Q Lemma

Goal: turn the Phase 1 sign patterns into formula consequences.

### 2.1 — Closed Forms

Status: complete in `core/Q-FORMULAS.md`.

Use `core/Q-FORMULAS.md` as the working formula sheet. For the current
panel `n ∈ {2,3,4,5,6,10}`:

- use the master expansion with overlap vector `(t_i)`;
- keep prime, prime-power, and squarefree multi-prime rows separate;
- tabulate the specialisations used most directly by the panel through
  `h = 4`;
- use the master expansion directly at `h = 5`;
- avoid global sign claims where overlap/high-`t_i` cases can
  transition.

The h=3 prime calculation is the sanity check:

    Q_p(p³k) = 1 - d(k) + τ_3(k)/3,    gcd(p,k)=1,

so the low-payload zero band is algebraic, not merely empirical.

### 2.2 — Exact Verification

Status: complete for the existing `payload_q_scan.csv`.

`q_n_verify.py` asserts Fraction equality against `payload_q_scan.csv`.

Checks:

- master expansion on every row, including h=5;
- displayed specialisations in their declared scope;
- mismatch grouping by `(n_type, h, overlap case)`.

Result:

- input rows: 24203;
- n values present: `{2,3,4,5,6,10}`;
- master expansion mismatches: 0;
- displayed-specialisation mismatches: 0;
- structural errors: 0.

### 2.3 — h=5 Resolution

Status: decided — do not extend `M_MAX` for 2.3.

At `M_MAX = 50000`, some h=5 cells are under-resolved. Two separate
questions should stay separate:

- distribution question: raise `M_MAX` to 10⁶ and rerun the payload
  scan;
- identity question: exact formula verification already covers h=5
  if the row exists.

Do not use a weak h=5 destroyer z-score as evidence against finite
rank; it is mostly sample-size discipline.

Decision. The identity question is settled by Phase 2.2 (zero
mismatches over 24203 rows, including all present h=5 rows). Cells
with row count below ~50 — `(3,5)`, `(5,5)`, `(6,5)`, `(10,4)` — are
declared under-resolved-by-design; `(10,5)` is absent at this
`M_MAX`. Their weak destroyer z-scores are not evidence against
finite rank and are not to be cited that way. The distribution
question is routed to Phase 5, where the held-out re-scan covers a
different `m` range and naturally widens h=5. Compute that would have
gone into a larger 2.3 scan goes to Phase 2.4 instead, since
Hardy-deep witnesses dominate dense low-depth sampling as a finite-
rank check.

### 2.4 — Hardy Composite-Q Deep Witnesses

Status: complete in `hardy_composite_q.py`.

Outcome on the 27-row panel:

- direct-vs-master mismatches: 0;
- displayed-specialisation mismatches: 0;
- height jumps `h > r` exercised for `n ∈ {4, 6, 10}` at jump = 1 and
  jump = 2;
- depth: largest atom from `K = 10^100` (m has 202 base-10 digits);
  largest rank `r = 8` for `n = 2`.

After 2.2 passes, use Hardy to test the same formulas at unreachable
entry depths.

Protocol:

1. choose `n`, tuple length `r`, and deep indices `K_i`;
2. compute atoms `a_i = p_{K_i}(n)` by Hardy;
3. set `m = ∏ a_i`;
4. compute `h = ν_n(m)`;
5. evaluate Q by the master expansion and by the implementation path;
6. assert exact agreement.

For prime `n`, multiplying `r` atoms gives height `r`. For composite
`n`, residual cofactors can add extra height, so always measure
`ν_n(m)` after multiplication.

This is not a new proof of the formula. It is a deep-access sanity
loop showing the finite-rank implementation works where prefix methods
cannot reach.


## Phase 3 — Global Stream Checks By Hardy

Once local Q is pinned, cross-experiment claims become predictions
about how finite-rank local arithmetic is read by concatenation.
Hardy Echo is the validation layer.

### 3.1 — CF Spike Derivation

`experiments/acm-champernowne/base10/cf/SPIKE-HUNT.md` reports

    (b-1)^2 · b^(k-2) · (n-1) · k / n².

Derive the factor from Q plus radix-block geometry. The target is to
explain both the `(n-1)/n²` density and the block-length factor, not
just fit six points.

### 3.2 — Hardy Mode 3 Block Counts

Use `hardy_echo.py` Mode 3 / `BlockK` to check block counts at large
`d` without materializing the stream.

First panel:

| n | base | d |
|---|---|---|
| 2 | 10 | 20, 50, 100 |
| 5 | 10 | 20, 50 |
| 10 | 10 | 20, 50 |

Smooth blocks should match the block-uniformity prediction exactly.
Non-smooth blocks should be reported separately, not forced into the
smooth formula.

### 3.3 — Hardy Mode 2 Digit-Position Spike Neighborhoods

Use the exact digit-position oracle to sample stream neighborhoods
near predicted block joins and spike locations.

This tests whether the CF spike is actually boundary geometry in the
concatenated real, rather than only a count identity over entries.
The oracle lets us work by digit depth, not prefix length.

### 3.4 — Hardy Mode 4 Tail Destroyers

Run prefix-era visual claims in matched deep windows. Each observable
must declare its destroyer:

| observable type | right destroyer |
|---|---|
| position-side order / gradients | entry shuffle |
| per-entry algebraic invariants | bit-within-entry or digit-within-entry shuffle |
| radix block claims | digit-class or block-class shuffle |

Boundary stitch already showed why this matters: entry shuffle kills
some right-side order structure but preserves the `v_2(n)` trailing
zero barcode because parity is per entry.

Candidate claims:

- binary RLE ridges by `v_2(n)`;
- boundary-stitch trailing-zero barcode and right-side gradient;
- Walsh robust cells;
- Morlet/RDS notches;
- base-10 CF spike neighborhoods.


## Phase 4 — Brief 4 / Multiplication-Table Prediction

The BPPW `M_n(N)·Φ(N)/N` prediction should now be written in terms of
Q signs and finite-rank payload distributions, not raw `Λ_n`.

Use Phase 2 formulas to integrate sign and magnitude over
height/payload/factorisation cells. Then test against the existing
Monte Carlo machinery. If the formula table is exact, any residual is
in the multiplication-table distribution, not in Q.


## Phase 5 — Held-Out Prediction

If Phase 2 verifies, the predictive model is not a fit. It is the
closed form.

Checks:

- rerun `payload_q_scan.py` on a held-out `m` range;
- evaluate Q by formula;
- require exact Fraction equality;
- report distribution summaries only after equality passes.

If equality fails, stop and fix the algebra or implementation. Do not
fit a residual until the exact formula path is exhausted.


## Side Quest — Cutoff `v_n(Y)` Residue

The n=2 dist_n² line is really a `v_2(Y)` distinction:
distance 0 means `4 | Y`, distance 2 means `Y ≡ 2 mod 4`.

Test at higher `Y_max` (`5×10⁵` or `10⁶`) with `v_n(Y)` scouts:

- n=2 should reproduce the evidence-level line;
- n ∈ {3,4,5} must strengthen to evidence level or be demoted.

If it stays n=2-only, cutoff is no longer part of the main
finite-rank hunt. It becomes a separate positivity-locus problem in
the style of `POSET-FACTOR.md`.


## Sequencing

```
Phase 2.1   Q formulas with payload-overlap vector              COMPLETE
Phase 2.2   exact verification on payload_q_scan.csv            COMPLETE
Phase 2.3   h=5 resolution: under-resolved-by-design, route to P5  DECIDED
Phase 2.4   Hardy composite-Q deep witnesses                    COMPLETE

Phase 3.1   CF spike derivation from Q + block geometry         (analytic)
Phase 3.2   Hardy Mode 3 large-d block-count checks             (parameter run)
Phase 3.3   Hardy Mode 2 digit-position spike neighborhoods     (small script)
Phase 3.4   Hardy Mode 4 tail destroyers for visual claims      (per-claim)

Phase 4     Brief 4 / multiplication-table prediction           (analytic + MC)
Phase 5     held-out exact Q verification                       (small script)

Side quest  cutoff v_n(Y) at higher Y_max                       (re-run scan)
```

Phase 2.2 is the gate. With exact Q verification in hand, downstream
work is derivation or deep validation. Without it, downstream is only
fitting.


## Files

| file | role | phase |
|---|---|---|
| `core/Q-FORMULAS.md` | master expansion and specialisations | 2.1 |
| `q_n_verify.py` | exact row-wise formula check | 2.2 |
| `payload_q_scan.py` | Q scan and held-out scans | 2.2, 5 |
| `hardy_composite_q.py` | deep product Q witnesses | 2.4 |
| `brief2_q_derivation.md` | CF spike derivation from Q | 3.1 |
| `hardy_block_spikes.py` | large-d block-count / spike neighborhood checks | 3.2, 3.3 |
| `hardy_tail_destroyers.py` | matched deep-window visual destroyers | 3.4 |
| `brief4_q_prediction.py` | `M_n(N)·Φ(N)/N` from Q sign distribution | 4 |
| `cutoff_vn_y.py` | higher-Y cutoff side quest | side |


## Coupling

- `ACM-MANGOLDT.md` should point to Q and finite rank, not `ρ`, as the
  local arithmetic object.
- `PHASE1-RESULTS.md` is the destroyer record.
- `core/FINITE-RANK-EXPANSION.md` gives the short conjectural spine.
- `core/Q-FORMULAS.md` is the local formula sheet.
- `experiments/math/hardy/DEEP-TROUBLE-No-4.md` and
  `HARDY-ECHO-RESULTS.md` give the deep validation instrument.


## What This Is Not

- Not a commitment to every downstream phase. Phase 2.2 is the gate.
- Not a claim that cutoff residues are gone; they are demoted until
  the `v_n(Y)` side quest says otherwise.
- Not a claim that visuals prove the algebra. The algebra is exact;
  visuals and Hardy windows test how it appears in concatenated
  streams.
