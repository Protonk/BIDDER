# Collection Plan

A catalogue of the math and theory docs in this repo, ranked by how
strongly they match a sensitizing kernel derived from five seed
documents. The purpose is to have a pre-sorted shelf to draw from when
assembling a collection of important-looking mathematical/discursive
content. Each entry carries a one-line hook.

The seeds are `core/BLOCK-UNIFORMITY.md`, `core/HARDY-SIDESTEP.md`,
`core/RIEMANN-SUM.md`, `core/ABDUCTIVE-KEY.md`, and
`core/ACM-CHAMPERNOWNE.md`. They set the tone and the kernel below
distils what they have in common.


## Sensitizing kernel

Five features recur in the seeds. A doc is "important-looking" in the
sense this plan cares about when it exhibits several of them, not just
because it contains math.

1. **Proof structure.** Demarcated Lemma / Claim / Proof / ∎, usually
   one line to half a page, followed by an informal "why this matters"
   aftermath.
2. **Explicit claim-type separation.** Structural / quadrature / FPC
   (Riemann); smooth / Family E / unconditional (Block-Uniformity);
   abductive / cascade / greedy (Abductive Key). The proved, the
   measured, and the open are pulled apart on purpose.
3. **Scope disclaimers.** "What this is not," "affects X not Y," "not
   a blanket improvement." Anti-over-claim rhetoric, often a standalone
   paragraph near the top.
4. **Exact-math BQN gloss.** Using canonical names from
   `guidance/BQN-AGENT.md`, each block labelled as exact-math
   specification and tied to the Python/C implementation.
5. **Meta-layer.** The doc reflects on the pattern *behind* the math:
   "leaky parameterization," "rank-1 view," "knife-edge: productive
   triviality," "the fourth instance of the same observation."

Tier assignment, loosely:

- **Tier 1** — kernel-matching theorem/proof docs, ≥3 features.
- **Tier 2** — substantive experimental notes with derivations,
  closed forms, or control-split analyses; ≥1 kernel feature plus
  real measurements.
- **Tier 3** — planning, scaffolding, indexing, and forest roots.
- **Tier 4** — art and visualization notes; math is secondary.
- **Tier 5** — companion code (Python module docstrings carrying
  theorem-level prose).


## Tier 1 — Core theorem/proof docs

The five seeds, plus docs in the same register found elsewhere.

- [`core/BLOCK-UNIFORMITY.md`](core/BLOCK-UNIFORMITY.md) — seed.
  Integer-block lemma, sieved-block smooth family, Family E, spread
  bound ≤ 2, unconditional witness `(4, 5, 5)` outside both sufficient
  families, tests and regression fixtures.
- [`core/HARDY-SIDESTEP.md`](core/HARDY-SIDESTEP.md) — seed. Closed
  form `p_K(n) = n·(q·n + r + 1)` for the K-th n-prime, polylog cost,
  astronomical K witnesses, `n=1` special-case argument, "why 'Hardy
  sidestep'" naming rationalisation.
- [`core/RIEMANN-SUM.md`](core/RIEMANN-SUM.md) — seed. Structural
  `E_P(key) = R` permutation-invariance proof, Euler–Maclaurin rate
  table, finite-population correction, cipher coupling gap as a
  measurement not a theorem.
- [`core/ABDUCTIVE-KEY.md`](core/ABDUCTIVE-KEY.md) — seed. Rank-1
  diagonal recovery, the cascade and greedy companion extractions,
  the long meta-essay on leaky parameterization and "three surprises
  now."
- [`core/ACM-CHAMPERNOWNE.md`](core/ACM-CHAMPERNOWNE.md) — seed. The
  base construction (monoid `nZ+`, n-primes, square boundary, the
  Champernowne encoding), ACM literature anchors (Hilbert, James &
  Niven, Geroldinger, Baginski–Chapman), "what is possible now."
- [`core/API.md`](core/API.md) — three-layer reference (English /
  Python / BQN) for the cipher-path API, anchored to the `d=1`
  integer-block case. Explicit scope disclaimer on v1 cipher cap;
  points to both seed theorems as "what the API is not yet using."
- [`BIDDER.md`](BIDDER.md) — root API doc: `bidder.cipher` and
  `bidder.sawtooth` in the same three-layer format, bridging cipher
  and sawtooth paths. Clean "what is not yet supported" table.
- [`generator/BIDDER.md`](generator/BIDDER.md) — cipher design doc.
  "Mathematical foundation / Construction / Observed properties /
  Known limitations / Open questions" discipline; Speck32/64 with
  Feistel fallback; "factors the problem differently" framing.
- [`experiments/acm/diagonal/cantor_walk/UNORDERED-CONJECTURE.md`](experiments/acm/diagonal/cantor_walk/UNORDERED-CONJECTURE.md)
  — the strongest meta-layer doc in the repo. Greedy-extraction proof,
  "three surprises now" retrospective, the "knife-edge / productive
  triviality / foothold vs perimeter" taxonomy, recovery / dynamics /
  transport classification, two-sided discipline for future recovery
  questions.
- [`guidance/PAIR-PROGRAMMING.md`](guidance/PAIR-PROGRAMMING.md) —
  phenomenological account of the division of labour that produced
  the UNORDERED-CONJECTURE meta-layer. Three-section structure
  (dialogic kickoff / narrative account / "why these were not 'no U'"),
  the three frame-level corrections (greedy theorem moment, rank-1
  overstatement moment, transport bucket and operation-side collapse),
  hot-vs-cold agent distinction, explicit epistemic boundary on what
  can be claimed about felt experience. Unique genre: a meta-layer
  doc about how the other meta-layer docs got written.
- [`experiments/acm-champernowne/base2/BINARY.md`](experiments/acm-champernowne/base2/BINARY.md)
  — what changes in base 2: leading-digit uniformity collapses, the
  sawtooth *is* the SlideRule ε function (not analog), RLE becomes
  a 2-adic fingerprint. Closed-form tables, BQN, verdict section.
- [`experiments/acm-champernowne/base2/HAMMING-BOOKKEEPING.md`](experiments/acm-champernowne/base2/HAMMING-BOOKKEEPING.md)
  — full closed-form derivation of bit-balance for `n = 2^m`, the
  "penalty linear, bonus exponential, cross at `m = 1`" argument,
  per-entry vs per-monoid correction, two companion experiments A/B.
- [`experiments/acm-champernowne/base2/FINITE-RECURRENCE.md`](experiments/acm-champernowne/base2/FINITE-RECURRENCE.md)
  — conjecture that no finite automaton recognises a binary ACM
  stream. Three-point argument (unbounded entry length, periodicity
  in `k` not in bit-stream space, value-dependent constraints);
  productive border with Franaszek / Adler–Coppersmith–Hassner /
  Immink tools.
- [`experiments/acm-champernowne/base2/disparity/rds_wavelet/KINK-INVESTIGATION.md`](experiments/acm-champernowne/base2/disparity/rds_wavelet/KINK-INVESTIGATION.md)
  — "audited down" investigation log. "Status: audited down. …is not
  currently supported" headline; explicit "what is solid / what is
  not solid" split; bandwidth-sensitivity table; 300× bootstrap
  showing the lattice click is not a stable statistic; six white-noise
  controls that kill the strongest artefact reading; falsification
  tests T1–T7 with status; "what this note does not claim" section
  with nine items. A long-form worked example of the retraction
  discipline that `KINK_DECOMPRESSION.md` only summarises.
- [`experiments/acm/diagonal/CANTORS-PLOT.md`](experiments/acm/diagonal/CANTORS-PLOT.md)
  — the "garden" meta-doc for the diagonal expeditions. Composite
  lattice as the central object; plot-by-plot status; "what worked /
  what surprised / what didn't transfer / what's degenerate at this
  scale"; pulls in the knife-edge caveat from UNORDERED-CONJECTURE.
- [`sources/EARLY-FINDINGS.md`](sources/EARLY-FINDINGS.md) — first
  findings doc. The exact `1111` per digit count, the `[1.1, 2.0]`
  sawtooth, running-mean conjecture `M(n) → 31/20` from below, the
  rolling-shutter asymmetry between multiplication and addition, the
  ε connection at mantissa midpoint. Cited by every seed.
- [`tests/theory/RED-TEAM-THEORY.md`](tests/theory/RED-TEAM-THEORY.md)
  — four-layer decomposition of `E_N − I = (E_N − R) + (R − I)`.
  Per-layer claim / failure mode / attack / theory-test link.
  "Isolate permutation facts from cipher-quality facts."
- [`tests/theory/README.md`](tests/theory/README.md) — theorem index.
  Each row is (proved result ↔ proof doc ↔ theory test ↔ experiment).
  The repo's authoritative map between claims and the tests that
  would falsify them.


## Tier 2 — Substantive experimental notes

Measurement-driven docs that carry derivations, closed forms, or
control-split analyses strong enough to matter in isolation.

- [`experiments/acm-champernowne/base2/STRUCTURAL-SIGNATURES.md`](experiments/acm-champernowne/base2/STRUCTURAL-SIGNATURES.md)
  — the binary subtree's synthesis packet. Seven-field shape per
  observable (Claim / Evidence / Relation / Statistical confidence /
  Semantic confidence / Falsification / Next check); cross-monoid
  join table; two-family framing (valuation / order-dependent).
- [`experiments/acm-champernowne/base2/disparity/DETRENDED_RDS.md`](experiments/acm-champernowne/base2/disparity/DETRENDED_RDS.md)
  — closed-form drift applied per-entry, `|res_pe|max / √n_bits`
  panel, shuffle control, wavelet follow-up. Corrects a wrong
  per-monoid reading that HAMMING-BOOKKEEPING had to be updated for.
- [`experiments/acm-champernowne/base2/disparity/DISPARITY.md`](experiments/acm-champernowne/base2/disparity/DISPARITY.md)
  — "status legend" working memo: imported fact / local observation /
  inference / conjecture / open question. Borrows constrained-coding
  language (8b/10b, 64b/66b, RLL, sequence-state) without mistaking
  imports for theorems.
- [`experiments/acm-champernowne/base2/forest/walsh/WALSH.md`](experiments/acm-champernowne/base2/forest/walsh/WALSH.md)
  — 44-cell robust family, tier-3 core `{30, 246, 255}`, control
  split `length + v_2 / length-only / neither reproduces`,
  audit-trail-per-npz discipline, methodological note on
  coefficient-level vs bucket-level reading.
- [`experiments/acm-champernowne/base2/disparity/rds_wavelet/KINK_DECOMPRESSION.md`](experiments/acm-champernowne/base2/disparity/rds_wavelet/KINK_DECOMPRESSION.md)
  — affine vs power-law vs geometric model comparison, K-dependent
  winner, "conservative reading" vs "stronger reading" separation,
  anti-persistent `CV ≈ 0.5` Gaussian-with-memory description of
  the gap sequence.
- [`experiments/acm-champernowne/base2/forest/valuation/VALUATION.md`](experiments/acm-champernowne/base2/forest/valuation/VALUATION.md)
  — three visualizations (Forest Grid / Spiral Chains / Residual Map)
  answering the seed's question with a blockwise-z residual test:
  "bulk captured by `v_2`, localized exceptions at small odd parts."
- [`experiments/acm-champernowne/base2/forest/epsilon_teeth/SAWTOOTH-SECANT.md`](experiments/acm-champernowne/base2/forest/epsilon_teeth/SAWTOOTH-SECANT.md)
  — result note with an explicit "the sign was wrong" correction
  section and the linearizer interpretation ("the ACM algebra pushes
  the sawtooth toward its secant").
- [`experiments/acm-champernowne/base2/forest/epsilon_teeth/SIMPLE-EPSILON.md`](experiments/acm-champernowne/base2/forest/epsilon_teeth/SIMPLE-EPSILON.md)
  — prediction note written before running the experiment: "the
  second-order residual will be a descending staircase," with an
  explicit "what would prove this wrong" section.
- [`experiments/acm-champernowne/base2/forest/entropy_landscape/ENTROPY-LANDSCAPE.md`](experiments/acm-champernowne/base2/forest/entropy_landscape/ENTROPY-LANDSCAPE.md)
  — two-regime analysis of k-gram entropy deficit; negative finding
  that no new structure beyond `v_2` emerges in `k ≤ 16`, `n ≤ 200`.
- [`experiments/acm-champernowne/base2/forest/boundary_stitch/BOUNDARY_STITCH.md`](experiments/acm-champernowne/base2/forest/boundary_stitch/BOUNDARY_STITCH.md)
  — forced-stripe proof (`v_2(n)` columns of zeros immediately left
  of the join), speculative right-side gradient prediction, "order on
  the right, disorder on the left" correlation argument.
- [`experiments/acm-champernowne/base2/forest/hamming_strata/PREDICTIONS.md`](experiments/acm-champernowne/base2/forest/hamming_strata/PREDICTIONS.md)
  — three quantitative claims with falsification criteria, regime A /
  regime B derivations, and a "note on revision" paragraph recording
  the earlier wrong draft and how the corrected math differs.
- [`experiments/acm-champernowne/base10/sawtooth/SAWTOOTH.md`](experiments/acm-champernowne/base10/sawtooth/SAWTOOTH.md)
  — derivation of why the `C(n)` sawtooth repeats after `10^2`
  (breakpoints at `u ∈ {2, 5/2, 10/3, 5}`); residual view factoring
  out the first-order decade ramp.
- [`experiments/acm-champernowne/base10/stats/uniformity/UNIFORMITY.md`](experiments/acm-champernowne/base10/stats/uniformity/UNIFORMITY.md)
  — self-contained setup / construction / exact uniformity / generator
  note. A cleaner restatement of the ACM-CHAMPERNOWNE construction
  anchored to BLOCK-UNIFORMITY.
- [`experiments/acm/diagonal/witness_density/README.md`](experiments/acm/diagonal/witness_density/README.md)
  — plot 3: the composite lattice `{(k, n) : 2 ≤ k < n}` as a scatter,
  five viridis bands of constant `k·n`, the `k·n = 60` hyperbola
  called out with its five witnesses. "Divisor function in a sieve
  costume," with the brute-force assertion harness the script
  runs before rendering. The substrate for plots 6, 8, 9.
- [`experiments/acm/diagonal/cheapest_sieve/README.md`](experiments/acm/diagonal/cheapest_sieve/README.md)
  — plot 9: the 73% `cost_diag` / `cost_prime` agreement headline,
  the 215-of-221 structural-disagreements analysis with every
  disagreement pointing the same direction (`diag_k > prime_k`),
  the "`cost_prime` is a prime-row-map *detector*" framing, the
  negative result that `cost_k` is a comb of prime-factor strips
  rather than a curve. "What this teaches / what it does not teach"
  discipline.
- [`experiments/acm/diagonal/complementary_curves/README.md`](experiments/acm/diagonal/complementary_curves/README.md)
  — plot 8: "The headline finding: the prediction failed" — the
  `(pronic, prime)` prediction from plot 9 lands at rank 12 of 28.
  Two structural findings: disjointness is free at this scale
  (`O(1/√x) ≈ 1%`), and selectors (`cost_prime`) don't transfer to
  generators (`n_k = p_k`). Negative result with the mechanism
  named.
- [`experiments/acm/diagonal/cantor_walk/README.md`](experiments/acm/diagonal/cantor_walk/README.md)
  — plot 5: "geometry causes rate" note. Walks with slope matching
  the rank-1 boundary recover linearly, Cantor is quadratic,
  row-by-row is `N`×linear. The picture that turns strict ascent
  into a rate.
- [`experiments/acm/diagonal/cascade_key/README.md`](experiments/acm/diagonal/cascade_key/README.md)
  — plot 4: cascade heatmap. "One key per row, all locks"; visual
  realization of the strict-ascent inequality `k ≤ n_k − 1`.


## Tier 3 — Planning, scaffolding, and forest roots

Not theorem-bearing on their own but essential context for the
cluster they sit in.

- [`guidance/BQN-AGENT.md`](guidance/BQN-AGENT.md) — canonical BQN
  names (`NPn2`, `NthNPn2`, `Digits10`, `ChamDigits10`, `LeadingInt10`,
  `LD10`, `Benford10`, `BinDigits`, `BStream`, `V2`). Every Tier-1
  doc sources notation here; this is feature 4 in its purest form.
- [`experiments/acm-champernowne/base2/STRUCT-SIG-PLAN.md`](experiments/acm-champernowne/base2/STRUCT-SIG-PLAN.md)
  — review copy for STRUCTURAL-SIGNATURES: the seven-field shape,
  scope, source-precedence rules, writing constraints, staleness
  rule. A discipline document that prescribes how the synthesis
  packet should read.
- [`experiments/acm-champernowne/base2/forest/valuation/VALUATION-PLAN.md`](experiments/acm-champernowne/base2/forest/valuation/VALUATION-PLAN.md)
  — substrate-cache-then-three-viz plan; audit-trail discipline
  lifted from WALSH; explicit `N_RENDER` vs `N_ANALYTIC` split.
- [`experiments/acm-champernowne/base2/forest/violin/VIOLIN-PLAN.md`](experiments/acm-champernowne/base2/forest/violin/VIOLIN-PLAN.md)
  — three-viz plan for the base-2 sawtooth: raw diagnostic, binade
  fans, and binade Gini coefficients. The Gini crossover point `d*`
  as "when does the running mean forget which tooth it's in" is the
  sharpest idea in the plan.
- [`experiments/acm-champernowne/base2/forest/MALLORN-SEED.md`](experiments/acm-champernowne/base2/forest/MALLORN-SEED.md)
  — the nine-expedition forest index; seeds all the base-2 experiments.
- [`experiments/README.md`](experiments/README.md) — the top-level
  classification rule: "the top-level directory answers 'what is the
  source?' not 'what does the visualization look like?'"
- [`experiments/acm-champernowne/README.md`](experiments/acm-champernowne/README.md)
  — base10 / base2 split explanation.
- [`experiments/acm-champernowne/base2/README.md`](experiments/acm-champernowne/base2/README.md)
  — pointer to BINARY / FINITE-RECURRENCE / HAMMING-BOOKKEEPING.
- [`experiments/acm-champernowne/base10/README.md`](experiments/acm-champernowne/base10/README.md)
  — sawtooth / shutter / stats / art index.
- [`experiments/bidder/README.md`](experiments/bidder/README.md) —
  BIDDER-output experiment families (dither / reseed / stratified /
  digits / art-contamination).
- [`experiments/math/README.md`](experiments/math/README.md) —
  one-item index: `arcs/` and the ε landscape.
- [`experiments/future/README.md`](experiments/future/README.md) —
  "holding area, not a graveyard" for unstable ideas.
- [`README.md`](README.md) — root README. Construction / generator /
  art passes; points at every Tier-1 core doc.
- [`AGENTS.md`](AGENTS.md) — root build/test reference. Carries the
  "Signposting is for the birds" discipline line: "Agents and humans
  can read 400-600 word documents without constant semaphore."
- [`generator/AGENTS.md`](generator/AGENTS.md) — cross-language parity
  rules, feature set, shared constants. Meta-discipline for the
  C/Python pair.


## Tier 4 — Art and visualization notes

Math content is secondary to the visualization story. Useful as
context, not usually as theorem fodder.

- [`experiments/acm-champernowne/base10/art/PITCH.md`](experiments/acm-champernowne/base10/art/PITCH.md)
  — the five-piece art index (shutter / fabric / moire sieves / sieve
  carpet / ε landscape) with a "what didn't work" appendix (polar
  rosette, phase winding) naming why the sawtooth's *amplitude* is
  not an interesting axis.
- [`experiments/acm-champernowne/base10/shutter/SHUTTER.md`](experiments/acm-champernowne/base10/shutter/SHUTTER.md)
  — rolling-shutter first-digit heatmap. "The shear angle
  `arctan(log₁₀(1.55)) ≈ 10.8°` is a number-theoretic constant made
  physically visible." Short but the phrase is worth lifting.
- [`experiments/acm-champernowne/base10/art/fabric/FABRIC.md`](experiments/acm-champernowne/base10/art/fabric/FABRIC.md)
  — the fabric family: digit-field as cloth, "warp, weft, selvedge"
  framing. "The folder is a study in representation" — a two-axis
  taxonomy of encodings × geometries rather than a single image.
- [`experiments/acm-champernowne/base10/art/fabric/noising/NOISING.md`](experiments/acm-champernowne/base10/art/fabric/noising/NOISING.md)
  — destruction experiments on the fabric. The real finding:
  "the fabric is multiscale"; pure blur weakens gradually, pure
  relabeling does nothing, but blur + nonlinear scramble + blur
  breaks it quickly. Feature 2 in miniature (three attacks,
  separated).
- [`experiments/acm-champernowne/base10/art/fabric/inverted/INVERTED.md`](experiments/acm-champernowne/base10/art/fabric/inverted/INVERTED.md)
  — inverted-polar significand family (significand_inverted /
  smoke_ring / chrysalis / splat / bent / shattered / strata).
  "Inversion is a reallocation of visual resolution."
- [`experiments/acm-champernowne/base2/art/rle/RLE.md`](experiments/acm-champernowne/base2/art/rle/RLE.md)
  — RLE art set including a deliberate negative lesson (`corona_attempt`
  as "for RLE, direct radius is too expensive a coordinate").
- [`experiments/acm-champernowne/base2/art/valuation/VALUATION.md`](experiments/acm-champernowne/base2/art/valuation/VALUATION.md)
  — art-side companion to the forest VALUATION: four layout variants
  (treefan rose / stratum triangle / stratum fan / hyperbolic chord)
  on the V3 residual data. "What to keep across variants" discipline:
  residual is the signal, confidence gates visibility, under-supported
  rows are context.
- [`experiments/acm-champernowne/base10/art/sieves/SIEVES.md`](experiments/acm-champernowne/base10/art/sieves/SIEVES.md)
  — moire sieves and sieve carpet.
- [`experiments/acm-champernowne/base10/art/sieves/ULAM-SPIRAL.md`](experiments/acm-champernowne/base10/art/sieves/ULAM-SPIRAL.md)
  — golden-angle spiral of sieve density `|{n ∈ 2..N : k is n-prime}|`.
  The "two views of the same phenomenon" note: ε landscape highlights
  where primes are most isolated, this highlights where composites
  are richest.
- [`experiments/math/arcs/ARCS.md`](experiments/math/arcs/ARCS.md) —
  ε landscape 3D surface; the bridge image for ε across bases.
- [`experiments/future/wibblywobblies/WIBBLYWOBBLIES.md`](experiments/future/wibblywobblies/WIBBLYWOBBLIES.md)
  — short note coining "wibble" vs "wobble" for off-center peak vs
  asymmetry around the peak, with a conservation claim
  `wobble × wibble ≥ floor`. Tiny but vocabulary worth lifting.
- [`sources/BIDDER-AND-SON.md`](sources/BIDDER-AND-SON.md) — historical
  record of G. P. Bidder's mental log method vs his son's, framed as
  "decomposing the target" vs "decomposing the space." Not current
  theory, but the father/son contrast echoes the leaky-parameterization
  discipline elsewhere and the source is the repo's namesake.
- [`nasties/FIRST-DIGIT.md`](nasties/FIRST-DIGIT.md) — FP truncation
  bug in `first_digit` (`int(10**frac)` undercounts at exact integer
  mantissas). Not theory, but it is the origin of the `+1e-9` guard
  that every BQN `LD10` usage carries as a caveat.


## Tier 5 — Companion code (module prose)

Python module docstrings carrying theorem-level content. They read as
compact companion docs to the Tier-1 proof files.

- [`core/hardy_sidestep.py`](core/hardy_sidestep.py) — module
  docstring and `nth_n_prime` docstring restate the closed form and
  the cost argument; side-by-side with HARDY-SIDESTEP.md.
- [`core/acm_core.py`](core/acm_core.py) — ~60-line module header
  with definitions (n-primality, n-prime, n-Champernowne, log-space
  decomposition), the ACM literature connection, and the mapping from
  Python names to the BQN canonical names in BQN-AGENT.md.
- [`core/sawtooth.py`](core/sawtooth.py) — module docstring presents
  `NPrimeSequence` as "the math-layer dual of `BidderBlock`" with
  random access via the Hardy closed form; pure integer arithmetic.
- [`core/api_doc_examples.py`](core/api_doc_examples.py) — the
  markdown-code-block verifier. Not theory, but the discipline is
  notable: Python example blocks in API.md, RIEMANN-SUM.md, and
  BIDDER.md are rewritten as assertions before execution so the
  docs cannot drift from the code. Relevant as a Tier-1-support
  mechanism.
- [`experiments/bidder/unified/riemann_proof.py`](experiments/bidder/unified/riemann_proof.py)
  — the experiment ancestry for `tests/theory/test_riemann_property.py`.
  Module docstring restates the permutation-invariance argument in
  five sentences and enumerates the four visual panels.
- [`experiments/bidder/unified/adversarial_integrands.py`](experiments/bidder/unified/adversarial_integrands.py)
  — module docstring maps four integrands to rows of the
  Euler–Maclaurin table and says which rate each one hits.
- [`experiments/bidder/unified/mc_diagnostic.py`](experiments/bidder/unified/mc_diagnostic.py)
  — module docstring contrasts cipher, sawtooth, and numpy PRNG on
  the two panels and names the birthday-bound collision count as
  the distinguishing feature.
- [`experiments/bidder/unified/period_anatomy.py`](experiments/bidder/unified/period_anatomy.py)
  — four-row diagnostic contrast (raw / histogram / first-difference
  / autocorrelation) between cipher and sawtooth output.


## Coverage gaps

Mostly cleared. What remains:

- **Dead cross-reference.** `core/api.py` cites `core/API-PLAN.md`
  as its companion doc, but no such file exists under `core/` or
  anywhere else in the tree (`Glob "core/API-PLAN.md"` returns
  nothing). Either the file was moved/deleted and the docstring
  was not updated, or it is a planned doc that was never written.
- **Broader `.py` docstring pass.** I opened the `core/` files and
  spot-checked the `experiments/bidder/unified/` scripts. Still
  unread: experiment scripts under `experiments/bidder/reseed/`,
  `experiments/bidder/stratified/`, `experiments/bidder/dither/`,
  `experiments/bidder/art/contamination/`,
  `experiments/bidder/digits/`, and the entire
  `experiments/acm/…` and
  `experiments/acm-champernowne/base2/forest/*/*.py` tree
  (`walsh.py`, `hamming_strata.py`, `rle_spectroscopy.py`,
  `valuation/*.py`, etc.). The forest scripts that drive the
  synthesis docs are plausible Tier-5 candidates worth a quick
  scan if the collection goes wide. The `contamination/`
  scripts are probably Tier 4 (art-side).
- [`experiments/acm-champernowne/base2/forest/walsh/walsh_upgrade_results.md`](experiments/acm-champernowne/base2/forest/walsh/walsh_upgrade_results.md)
  — opened; numerical tables only, no prose. Audit companion to
  `WALSH.md`, not a collection candidate on its own.
- **`experiments/acm-champernowne/base2/STRUCT-SIG-PLAN.md` vs
  `STRUCTURAL-SIGNATURES.md` relationship.** Both read in the first
  pass. The plan doc prescribes the final doc's seven-field shape
  verbatim. Worth noting that the *plan for a doc* is itself a
  discipline document with kernel features, but this isn't a gap —
  just a classification refinement.
