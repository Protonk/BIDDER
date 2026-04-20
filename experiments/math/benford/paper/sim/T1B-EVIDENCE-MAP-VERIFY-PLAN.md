# T1B-EVIDENCE-MAP verification plan (v2)

Before writing a paper-side synthesis, verify that
`sim/T1B-EVIDENCE-MAP.md`'s evidence chain is sound. The
verification is partitioned into six turns, each with its own
scope, so that context weight is bounded and early blockers
surface cleanly.

## Three distinct audit jobs

These are separate questions and must not be bundled:

1. **Is the map faithful to its own cited sources?** (Turns 2–4.)
   The map makes claims and cites sim summaries; do those
   summaries actually support the claims?
2. **Does the map cover what the paper needs?** (Turn 5.) The
   paper has specific T1b-related claims planned in PNAS-PLAN;
   are they all anchored by the map?
3. **Has newer work made the map stale?** (Turn 6.) Four recent
   sims postdate the map; do their findings support, complicate,
   or contradict the map's claims?

Bundling these produces shallow checking. Separating them keeps
each turn's criteria clean.

## Turn-by-turn plan

### Turn 1: chronology + inventory (scoping)

**Job:** establish the verification base. Nothing is checked yet
— just read and catalogue.

**Steps:**
1. `ls -la` the map and every cited sim summary. Compare
   mtimes. Specifically: does the map predate the four recent
   Mess-era sims (laplace-diagnostic, return-marginal,
   τ_R tail, conditional-decay)? Record the chronology.
2. Read `sim/T1B-EVIDENCE-MAP.md` once, end-to-end. The map is
   organized into five clauses (i)–(v). Expected rough shape
   (verifier should not take these summaries as authoritative;
   the map itself is the source):
   - (i) Equidistribution — multi-run table with caveats.
   - (ii) Asymptotic rate α = 1/2 — one direct sighting plus
     consistency-check runs. Spans several sim summaries.
   - (iii) Pre-asymptotic stretched-exp transient (IC-specific).
   - (iv) Rational exception (algebraic dichotomy).
   - (v) Symmetry clause (weak asymmetry doesn't break T1b).
3. For each clause, list the load-bearing claims and cite the
   sim summary(ies) each claim appeals to. Classify claims as
   quantitative (number + CI) or qualitative (regime label).

**Output:** Section 1 of `T1B-EVIDENCE-MAP-VERIFY-REPORT.md` with
- chronology note (map date vs post-map sim dates),
- clause-keyed claim inventory (~20-40 bullet-ish entries).

**Stop gate — concrete branching based on chronology:**

- **Branch A (base is current):** map dates ≥ all major M/S/B-run
  summary dates AND postdates the four Mess-era sims
  (laplace-diagnostic, return-marginal, τ_R tail,
  conditional-decay). Proceed normally to Turn 2.
- **Branch B (map predates Mess-era sims only):** map dates ≥
  M/S/B summaries but predates Mess-era sims. Proceed to
  Turn 2, but **Turn 6 becomes mandatory** (not skippable) —
  the map cannot have absorbed post-dating findings and
  drift is likely.
- **Branch C (map predates its own cited sources):** map
  predates one or more cited M/S/B-run summaries by a
  non-trivial interval. Base is too stale to verify profitably;
  stop and recommend a map refresh _before_ any internal audit.
  Do not run Turns 2–4.

**Est. effort:** ~20 min.

### Turn 2: internal verification, clauses (i), (iv), (v)

**Job:** confirm the easier clauses' claims against their cited
summaries.

**Scope:**
- (i) Equidistribution — multi-run table with caveats.
- (iv) Rational exception — algebraic dichotomy + fp64
  sufficiency claims.
- (v) Symmetry clause — weak asymmetry tests.

These three are bundled because they are shorter, each cites a
narrower sim set, and none of them is the rate claim (which is
the hardest and gets its own turn).

**Steps per claim:**
1. Open the cited summary.
2. Find the specific passage supporting the claim.
3. Check quantitative content (numbers, CIs) and qualitative
   framing (regime label, direction of inequality).
4. Classify: ✓ verified / ⚠ needs review / ✗ stale-or-wrong.

**Output:** Section 2 of the report — per-claim ✓/⚠/✗ table
covering clauses (i), (iv), (v) with one-line justification each.

**Stop gate:** if any claim is ✗ and the ✗ is load-bearing (not
just a stale numeric), pause and surface before Turn 3.

**Est. effort:** ~25 min.

### Turn 3: internal verification, clause (ii) + clause (ii) spot-checks

**Job:** verify the hardest clause — the α = 1/2 asymptotic rate
— which has one direct sighting plus consistency checks and
pulls in multiple sim summaries (M1, M3, M4, S0, B3, and
supporting framing from the map). All raw-data spot-checks for
clause (ii) live in this turn, so that clause-ii work is not
split across turns.

**Steps:**
- Same as Turn 2 but focused only on clause (ii).
- For each claim in clause (ii), trace the full evidence chain
  into the cited summary(ies).
- Raw-data spot-checks for clause (ii) numerics:
  - α fit estimate and R² against M3/M4 `.npz` (whichever the
    map cites as the direct sighting).
  - ML(1/2) Laplace-match pass against `s0_results.npz`.
  - ρ(K̂) = 0.924 per-visit contraction against
    `b3_results.npz` (if cited under clause (ii)).
- Each spot-check is a one-line Python check against the data,
  not a re-fit.

**Output:** Section 3 of the report — per-claim ✓/⚠/✗ for
clause (ii), with spot-check confirmations attached to the
relevant claims. Note whether the "direct sighting" is
genuinely direct or a derived fit.

**Stop gate:** if clause (ii) comes back ✗ on a load-bearing
claim (e.g., the α exponent estimate itself, or the R² on the
direct sighting), pause. The paper's theorem shape commitment
depends on this clause.

**Est. effort:** ~45 min.

### Turn 4: internal verification, clause (iii) + clause (iii) spot-checks

**Job:** verify clause (iii) — the pre-asymptotic stretched-exp
transient, IC-specific. All raw-data spot-checks for clause
(iii) live here; clause (ii) spot-checks belong in Turn 3 and
are not revisited.

**Scope:**
- (iii) Pre-asymptotic transient claims (shape, IC dependence,
  crossover).
- Spot-check transient c ≈ 0.498 against
  `m1_b1_b2_results.npz` (one-line Python).
- Spot-check any clause (iii) IC-range numerics against
  `t1b_unit_ball/` `.npz` files (dyadic / rational / smooth IC
  runs), if the map cites specific IC-range numbers.

**Output:** Section 4 of the report — per-claim ✓/⚠/✗ for clause
(iii), plus spot-check confirmations for clause (iii) numerics.

**Stop gate:** none specifically — if anomalies, note them and
they get resolved in the report recommendation.

**Est. effort:** ~25 min.

---

**Internal audit milestone.** After Turns 1–4, the first audit
question is answered: "is the map faithful to its own cited
sources?" The answer is a per-clause ✓/⚠/✗ table with spot-check
confirmations.

**Decision to proceed:**
- If internal audit is clean (mostly ✓, no load-bearing ✗),
  proceed to Turns 5 and 6 (in either order).
- If internal audit has a load-bearing ✗, stop and propose a map
  refresh; do not proceed to external audits until the map is
  repaired.

### Turn 5: PNAS-PLAN coverage audit (external)

**Job:** does the map cover what the paper plans to say? This is
_external_ to the map — it checks coverage against PNAS-PLAN,
not fidelity to sources.

**Scope discipline upfront:** PNAS-PLAN.md is 807 lines and
contains outdated theorem-variant language in places. Restrict
attention to the specific sections below; do not over-read or
follow tangents into the rhetorical-arc scaffolding or the
audience/register discussion.

**Exact PNAS-PLAN sections to check (by title):**

1. **`## The rhetorical arc → ### 2. Theorems, compactly stated`.**
   Theorem 1 base wording, plus the immediately following
   subsection **`### Theorem 1 variants — pre-committed wording`**
   (T1a / T1b / T1c). Map must cover the T1b variant
   commitment.
2. **Theorem 2 block within the same `### 2.` section.** The
   empirical rate c value. Map must cover a specific numeric
   value for c compatible with the current M1 fit.
3. **`### 4. Mechanism / proof`.** Specifically the two
   empirical anchors listed under "What this section needs to
   carry when drafted": the coordinate identity (ψ, ε) and the
   visit rate (E[L_n] ~ c_R √n). Map must cover the √n visit
   rate empirically; the coordinate identity is
   BINADE-WHITECAPS territory, not sim territory, and is not
   required to be in the map.
4. **`### 5. Figures with captions`.** Figure 1 (three-walks
   log-log). Check if the map references the three-walks
   substrate. If not, note which existing sim summary covers
   it (likely `comparison_walks_SUMMARY.md`) and flag as a gap
   relative to paper needs.
5. **`### 7. Robustness and sensitivity`.** Four bullets
   (biased generators, IC dependence, base change, pure
   addition). Check coverage in the map.

**Steps:**
For each of the five targets above:
- Mark: covered by the map ✓, covered elsewhere in `sim/` (note
  which summary) ↻, or gap ✗.
- For ↻ items, note the right summary and flag it as candidate
  for paper-side promotion under a different doc (not
  T1B-EVIDENCE).
- For ✗ items, note whether evidence exists at all or a new
  sim is required.

**Explicitly out of scope for Turn 5:**
- The remainder of PNAS-PLAN (§1 intro, §3 group setup, §6
  Hamming diagnosis, §8 conclusion, rhetorical arc, audience,
  failure modes, references section).
- The outdated "c = 0.55" and related stale numerics in
  PNAS-PLAN (these are already flagged as stale; coverage
  audit uses the _currently_ supported numeric, e.g. 0.498).

**Output:** Section 5 of the report — coverage table with five
rows (one per target), each ✓/↻/✗ with one-line justification.

**Est. effort:** ~25 min.

### Turn 6: Mess drift audit (external)

**Job:** has newer work (post-map sims) made the map stale?

**Steps:**
For each of the four post-map Mess-era sims, check whether the
map's claims are consistent, silent, or contradicted. Use the
finding summaries as scoped below — do not import a stronger
claim than the underlying sim summary supports.

1. **Laplace-diagnostic** (`sim/laplace_diagnostic_SUMMARY.md`).
   Scoped finding: the BS(1,2) E-process shows positive mean
   drift at the measured horizon, and local time L_n grows
   linearly in calendar time for this IC — neither fits the
   "zero-drift null-recurrent SRW" universality claim
   verbatim. Check whether the map relies on that strict
   universality. If the map only appeals to √n local-time
   structure (which is compatible with other regimes), this
   may be silent-acceptable.

   2. **Return-marginal** (`sim/return_marginal_SUMMARY.md`).
       Scoped finding: the **pooled post-burn return-sample
       m-marginal σ̃** is concentrated on the arc
       [1 − log₁₀ 2, 1) × {E = 10} at R = {|E| ≤ 10}. This
       pressures `Route 1'`'s identification step π_T ν_R = Leb_T
       but **does not by itself identify the invariant law**
       (stationarity not verified, E₀ dependence not tested).
   Check whether the map makes identification-step claims
   that this pressure affects; treat σ̃ as evidence about
   pooled returns, not a settled statement about ν_R.

3. **τ_R tail** (`sim/tau_R_tail_SUMMARY.md`). Scoped finding:
   **first-excursion** τ_R from the **M1 IC (x = √2)** has
   empirical survival slope ≈ −0.495 on n ∈ [50, 10⁴]
   (R² = 1.0000). This is an IC-specific, first-excursion
   statement — not a uniform-in-x ∈ R theorem-level tail
   bound. Check whether the map's τ_R claims are at this
   narrower level or at the broader level; treat the broader
   level as not-yet-supported empirically.

4. **Conditional-decay** (`sim/conditional_decay_SUMMARY.md`).
   Scoped finding: the specific analytic hypothesis H (b-steps
   don't move m conditional on a-count K; transient stretched-
   exp is pure a-step Diophantine on T) was **rejected at
   Test A** — its predicted TV shape does not match the
   measured transient at the c ≈ 0.498, γ = 0.5 operating
   point (best-fit γ under H is 0.15; at γ = 0.5 the predicted
   c is 0.009 vs measured 0.498). This is a narrower statement
   than "transient mechanism is not a-step": it rules out
   the clean a-only hypothesis, does not rule out a-step
   involvement in a broader mechanism. Check whether the map
   proposes a transient mechanism compatible with H; if not,
   the result is silent.

**Output:** Section 6 of the report — one-paragraph status per
sim: consistent / silent / contradicted, and if contradicted,
what specifically needs updating.

**Scope discipline:** this turn explicitly extends beyond the
map's cited sources. Silence is acceptable if the map's scope
excludes the relevant area; contradiction requires action.

**Est. effort:** ~25 min.

---

## Final recommendation (end of Turn 6)

Synthesize the six sections into one of four outcomes:

1. **Proceed.** Internal audit clean, paper-needs coverage
   complete, no drift from newer work. Write paper-side doc
   directly from the map.
2. **Refresh then proceed.** Minor internal ⚠ items or mess
   drift items can be resolved by short edits to the map before
   writing the paper-side doc.
3. **Pause.** A load-bearing ✗ was found (internal audit) or
   newer work contradicts the map's core. Fix the underlying
   issue before any paper-side doc.
4. **Redirect.** PNAS-PLAN's needs don't align with the map's
   organization; write the paper-side doc from PNAS-PLAN
   backward rather than map-forward.

## Overall scope discipline

- **No new sims.** Gaps become notes, not new runs.
- **No rewrites during verification.** Verification produces
  only the report sections. Any rewrites to T1B-EVIDENCE-MAP
  happen after the final recommendation.
- **Stop gates are real.** A ✗ in Turn 2 or 3 is a pause,
  not a "noted, continuing."
- **Scope separation is enforced turn-by-turn.** Turns 2–4 are
  faithfulness-only (no extension). Turns 5 and 6 explicitly
  extend but in orthogonal directions (paper needs vs newer
  sims) and do not touch each other's scope.

## Output format

The verification produces a single file
`sim/T1B-EVIDENCE-MAP-VERIFY-REPORT.md` with six sections, one
per turn. Each section is dated and self-contained. Turns may
produce their section at different times; the report is an
append-only log until the final recommendation.

## What this plan does not do

- Does not commit to writing `paper/T1B-EVIDENCE.md`. That
  decision is the final recommendation's output.
- Does not re-litigate T1b vs T1a vs T1c. The current T1b
  commitment from `sim/README.md` is inherited.
- Does not propose new sims to close gaps. Gaps are surfaced
  as plan-level observations.

## Effort summary

| Turn | Job                                               | Est. |
|:----:|:--------------------------------------------------|:----:|
| 1    | Chronology + inventory (Branch A/B/C decision)    | 20m  |
| 2    | Internal audit: clauses (i)(iv)(v)                | 25m  |
| 3    | Internal audit: clause (ii) + clause (ii) spot-checks | 45m |
| 4    | Internal audit: clause (iii) + clause (iii) spot-checks | 25m |
| 5    | External audit: PNAS-PLAN coverage (5 exact targets) | 25m |
| 6    | External audit: Mess drift (scope-bounded)        | 25m  |

Total: ~165 min, distributed across six separable turns. Each
turn can be executed independently and produces its own report
section. The verifier can pause after any turn if that turn's
output warrants a plan revision.
