# Theory Survey

A catalogue of the math and theory docs in this repo, ranked by how
strongly they match a sensitizing kernel derived from five seed
documents. The purpose is to have a pre-sorted shelf to draw from
when assembling a collection of important-looking mathematical and
discursive content.

This survey is one of four related artifacts:

- **SURVEY.md** (this file) — navigation. *Where is X? What shelf?*
- `summaries/` (forthcoming) — content. *What does X say?*
- [`COLLECTION.md`](COLLECTION.md) — argument. *Why does X matter,
  and how does it fit with Y?*
- [`COLLECTION-PLAN.md`](COLLECTION-PLAN.md) — the plans that
  coordinate the summaries and the collection.

The survey is organized on two axes:

- `shelf` = collection priority
- `kind` = document genre

`family` names the source cluster a document belongs to, and
`kernel` records which of the five seed features it most clearly
matches.


## Sensitizing kernel

The seeds are `core/BLOCK-UNIFORMITY.md`, `core/HARDY-SIDESTEP.md`,
`core/RIEMANN-SUM.md`, `core/ABDUCTIVE-KEY.md`, and
`core/ACM-CHAMPERNOWNE.md`. The shorthand below uses:

1. `proof` — demarcated Lemma / Claim / Proof / ∎ structure.
2. `split` — explicit separation of claim types or epistemic layers.
3. `scope` — anti-over-claim disclaimers and boundary notes.
4. `BQN` — exact-math BQN gloss tied to implementation names.
5. `meta` — reflection on the pattern behind the math.


## Shelf overview

| Shelf | Purpose | Main kinds | What the reader gets |
|---|---|---|---|
| A | Core collection | exact theorem, meta-theory, interface bridge, frontier theorem | strongest collection nucleus |
| B | Strong satellites | substantive experimental notes | measurements, derivations, controls, negative results |
| C | Context and scaffolding | plans, indexes, conventions | how the clusters were organized and disciplined |
| D | Gallery and side artifacts | art, visualization, history, bugs | representational and historical context |
| E | Companion code prose | module docstrings, doc verifiers | compact theorem-level prose embedded in code |


## Shelf A — Core collection

### Exact theorem docs

<a id="block-uniformity"></a>
[`core/BLOCK-UNIFORMITY.md`](core/BLOCK-UNIFORMITY.md)  
kind: exact theorem doc | family: core | kernel: 1,2,3,4  
hook: Integer-block lemma, sieved smooth family, Family E, spread bound ≤ 2, unconditional witness `(4, 5, 5)` outside both sufficient families, tests and regression fixtures.

<a id="hardy-sidestep"></a>
[`core/HARDY-SIDESTEP.md`](core/HARDY-SIDESTEP.md)  
kind: exact theorem doc | family: core | kernel: 1,2,3,4  
hook: Closed form `p_K(n) = n·(q·n + r + 1)` for the K-th n-prime, polylog cost, astronomical K witnesses, `n = 1` special-case argument, and the "why Hardy sidestep" naming rationalisation.

<a id="riemann-sum"></a>
[`core/RIEMANN-SUM.md`](core/RIEMANN-SUM.md)  
kind: exact theorem doc | family: core | kernel: 1,2,3,4  
hook: Structural `E_P(key) = R` permutation-invariance proof, Euler-Maclaurin rate table, finite-population correction, and cipher coupling gap treated as measurement rather than theorem.

<a id="abductive-key"></a>
[`core/ABDUCTIVE-KEY.md`](core/ABDUCTIVE-KEY.md)  
kind: exact theorem doc | family: core | kernel: 1,2,3,4,5  
hook: Rank-1 diagonal recovery, cascade and greedy companion extractions, and the long meta-essay on leaky parameterization and "three surprises now."

<a id="acm-champernowne"></a>
[`core/ACM-CHAMPERNOWNE.md`](core/ACM-CHAMPERNOWNE.md)  
kind: exact theorem doc | family: core | kernel: 1,3,4  
hook: The base construction itself: monoid `nZ+`, n-primes, square boundary, Champernowne encoding, literature anchors, and the "what is possible now" aftermath.

### Meta-theory / discipline docs

<a id="unordered-conjecture"></a>
[`experiments/acm/diagonal/cantor_walk/UNORDERED-CONJECTURE.md`](experiments/acm/diagonal/cantor_walk/UNORDERED-CONJECTURE.md)  
kind: meta-theory doc | family: diagonal | kernel: 1,2,3,5  
hook: The strongest meta-layer doc in the repo: greedy-extraction proof, "three surprises now," knife-edge / productive triviality taxonomy, recovery-dynamics-transport classification, and a two-sided discipline for future recovery questions.

<a id="pair-programming"></a>
[`guidance/PAIR-PROGRAMMING.md`](guidance/PAIR-PROGRAMMING.md)  
kind: discipline doc | family: meta | kernel: 2,3,5  
hook: Phenomenology of the division of labour that produced the diagonal meta-layer, including the frame-level correction moments and a careful epistemic boundary on felt experience.

<a id="red-team-theory"></a>
[`tests/theory/RED-TEAM-THEORY.md`](tests/theory/RED-TEAM-THEORY.md)  
kind: theory-discipline doc | family: tests | kernel: 2,3,5  
hook: Four-layer decomposition of `E_N - I = (E_N - R) + (R - I)`, with per-layer claim, failure mode, attack, and theory-test link. Strong on isolating permutation facts from cipher-quality facts.

### Interface / theory-bridge docs

<a id="api"></a>
[`core/API.md`](core/API.md)  
kind: interface bridge doc | family: core | kernel: 2,3,4  
hook: Three-layer reference for the cipher-path API, anchored to the `d = 1` integer-block case, with an explicit scope disclaimer on the v1 cipher cap and pointers to the seed theorems the API is not yet using.

<a id="bidder-root"></a>
[`BIDDER.md`](BIDDER.md)  
kind: interface bridge doc | family: root | kernel: 2,3,4  
hook: Root API doc for `bidder.cipher` and `bidder.sawtooth`, bridging cipher and sawtooth paths in the same three-layer format with a clean "what is not yet supported" table.

<a id="bidder-generator"></a>
[`generator/BIDDER.md`](generator/BIDDER.md)  
kind: design bridge doc | family: bidder | kernel: 2,3,5  
hook: Cipher design doc with "Mathematical foundation / Construction / Observed properties / Known limitations / Open questions" discipline and the "factors the problem differently" framing.

<a id="tests-theory-readme"></a>
[`tests/theory/README.md`](tests/theory/README.md)  
kind: theory-index doc | family: tests | kernel: 2,3  
hook: The theorem index tying each proved result to its proof doc, theory test, and experiment witness. The authoritative map between claims and the tests that would falsify them.

### Frontier theorem notes

<a id="binary"></a>
[`experiments/acm-champernowne/base2/BINARY.md`](experiments/acm-champernowne/base2/BINARY.md)  
kind: frontier theorem note | family: base2 | kernel: 1,2,4  
hook: What changes in base 2: leading-digit uniformity collapses, the sawtooth is the SlideRule ε function, and RLE becomes a 2-adic fingerprint. Closed-form tables, BQN, verdict section.

<a id="hamming-bookkeeping"></a>
[`experiments/acm-champernowne/base2/HAMMING-BOOKKEEPING.md`](experiments/acm-champernowne/base2/HAMMING-BOOKKEEPING.md)  
kind: frontier theorem note | family: base2 | kernel: 1,2,4  
hook: Full closed-form derivation of bit-balance for `n = 2^m`, including the "penalty linear, bonus exponential, cross at `m = 1`" argument and the per-entry versus per-monoid correction.

<a id="finite-recurrence"></a>
[`experiments/acm-champernowne/base2/FINITE-RECURRENCE.md`](experiments/acm-champernowne/base2/FINITE-RECURRENCE.md)  
kind: frontier theorem note | family: base2 | kernel: 1,2,3  
hook: Conjecture that no finite automaton recognizes a binary ACM stream, argued from unbounded entry length, periodicity in `k` rather than bit-stream space, and value-dependent constraints.

<a id="kink-investigation"></a>
[`experiments/acm-champernowne/base2/disparity/rds_wavelet/KINK-INVESTIGATION.md`](experiments/acm-champernowne/base2/disparity/rds_wavelet/KINK-INVESTIGATION.md)  
kind: audited frontier note | family: base2 | kernel: 2,3,5  
hook: "Audited down" investigation log with explicit solid / not-solid splits, bandwidth sensitivity table, 300× bootstrap, white-noise controls, falsification tests T1-T7, and a long-form worked example of the retraction discipline.

<a id="cantors-plot"></a>
[`experiments/acm/diagonal/CANTORS-PLOT.md`](experiments/acm/diagonal/CANTORS-PLOT.md)  
kind: frontier garden doc | family: diagonal | kernel: 2,3,5  
hook: The "garden" meta-doc for the diagonal expeditions: the composite lattice as central object, plot-by-plot status, and an explicit worked / surprised / didn't-transfer / degenerate-at-this-scale split.

<a id="early-findings"></a>
[`sources/EARLY-FINDINGS.md`](sources/EARLY-FINDINGS.md)  
kind: first-findings doc | family: sources | kernel: 2,4,5  
hook: The first exact `1111` per-digit count, the `[1.1, 2.0]` sawtooth, the running-mean conjecture, rolling-shutter asymmetry, and the ε connection at mantissa midpoint. Cited by every seed.


## Shelf B — Strong satellites

### Base-2 structure family

[`experiments/acm-champernowne/base2/STRUCTURAL-SIGNATURES.md`](experiments/acm-champernowne/base2/STRUCTURAL-SIGNATURES.md)  
kind: synthesis packet | family: base2 | kernel: 2,3,5  
hook: The binary subtree's synthesis packet: seven-field shape per observable, cross-monoid join table, and the two-family framing of valuation-driven versus order-dependent structure.

<a id="detrended-rds"></a>
[`experiments/acm-champernowne/base2/disparity/DETRENDED_RDS.md`](experiments/acm-champernowne/base2/disparity/DETRENDED_RDS.md)  
kind: corrective measurement note | family: base2 | kernel: 2,3  
hook: Closed-form drift applied per-entry, normalized residual panel, shuffle control, and a correction of the wrong per-monoid reading that earlier docs had to update for.

[`experiments/acm-champernowne/base2/disparity/DISPARITY.md`](experiments/acm-champernowne/base2/disparity/DISPARITY.md)  
kind: status-ledger note | family: base2 | kernel: 2,3  
hook: Working memo with an explicit legend for imported fact, local observation, inference, conjecture, and open question. Good constrained-coding borrowing discipline.

<a id="walsh"></a>
[`experiments/acm-champernowne/base2/forest/walsh/WALSH.md`](experiments/acm-champernowne/base2/forest/walsh/WALSH.md)  
kind: measurement-and-control note | family: base2 | kernel: 2,3  
hook: The 44-cell robust family, tier-3 core `{30, 246, 255}`, control split against length and `v_2`, and the audit-trail-per-npz discipline.

[`experiments/acm-champernowne/base2/disparity/rds_wavelet/KINK_DECOMPRESSION.md`](experiments/acm-champernowne/base2/disparity/rds_wavelet/KINK_DECOMPRESSION.md)  
kind: model-comparison note | family: base2 | kernel: 2,3  
hook: Affine versus power-law versus geometric model comparison with K-dependent winners and a conservative-reading versus stronger-reading split.

[`experiments/acm-champernowne/base2/forest/valuation/VALUATION.md`](experiments/acm-champernowne/base2/forest/valuation/VALUATION.md)  
kind: residual-structure note | family: base2 | kernel: 2  
hook: Three visualizations answering the seed question with a blockwise-z residual test: bulk captured by `v_2`, with localized exceptions at small odd parts.

[`experiments/acm-champernowne/base2/forest/epsilon_teeth/SAWTOOTH-SECANT.md`](experiments/acm-champernowne/base2/forest/epsilon_teeth/SAWTOOTH-SECANT.md)  
kind: corrected result note | family: base2 | kernel: 2,3  
hook: Result note with an explicit "the sign was wrong" correction section and the linearizer interpretation that the ACM algebra pushes the sawtooth toward its secant.

[`experiments/acm-champernowne/base2/forest/epsilon_teeth/SIMPLE-EPSILON.md`](experiments/acm-champernowne/base2/forest/epsilon_teeth/SIMPLE-EPSILON.md)  
kind: pre-registered prediction note | family: base2 | kernel: 2,3  
hook: Prediction note written before running the experiment, including the explicit claim that the second-order residual will be a descending staircase and a section on what would prove it wrong.

[`experiments/acm-champernowne/base2/forest/entropy_landscape/ENTROPY-LANDSCAPE.md`](experiments/acm-champernowne/base2/forest/entropy_landscape/ENTROPY-LANDSCAPE.md)  
kind: negative-result note | family: base2 | kernel: 2,3  
hook: Two-regime analysis of k-gram entropy deficit and the negative result that no new structure beyond `v_2` emerges in the tested `k ≤ 16`, `n ≤ 200` window.

[`experiments/acm-champernowne/base2/forest/boundary_stitch/BOUNDARY_STITCH.md`](experiments/acm-champernowne/base2/forest/boundary_stitch/BOUNDARY_STITCH.md)  
kind: boundary-effect note | family: base2 | kernel: 1,2  
hook: Forced-stripe proof on the left of the join, speculative right-side gradient prediction, and the "order on the right, disorder on the left" correlation argument.

[`experiments/acm-champernowne/base2/forest/hamming_strata/PREDICTIONS.md`](experiments/acm-champernowne/base2/forest/hamming_strata/PREDICTIONS.md)  
kind: quantitative prediction note | family: base2 | kernel: 1,2,3  
hook: Three quantitative claims with falsification criteria, regime A / regime B derivations, and a note on revision explaining how the corrected math differs from the earlier wrong draft.

### Base-10 structure family

[`experiments/acm-champernowne/base10/sawtooth/SAWTOOTH.md`](experiments/acm-champernowne/base10/sawtooth/SAWTOOTH.md)  
kind: derivation note | family: base10 | kernel: 1,2  
hook: Derivation of why the `C(n)` sawtooth repeats after `10^2`, with breakpoints at `u ∈ {2, 5/2, 10/3, 5}` and a residual view factoring out the first-order decade ramp.

[`experiments/acm-champernowne/base10/stats/uniformity/UNIFORMITY.md`](experiments/acm-champernowne/base10/stats/uniformity/UNIFORMITY.md)  
kind: construction restatement note | family: base10 | kernel: 1,2,3,4  
hook: Self-contained setup, construction, exact uniformity, and generator note. A cleaner restatement of the ACM-CHAMPERNOWNE construction anchored to BLOCK-UNIFORMITY.

### Diagonal ACM family

[`experiments/acm/diagonal/witness_density/README.md`](experiments/acm/diagonal/witness_density/README.md)  
kind: structural measurement note | family: diagonal | kernel: 2  
hook: Plot 3 on the composite lattice `{(k, n) : 2 ≤ k < n}`, with constant-`k·n` bands, the `k·n = 60` hyperbola called out, and the "divisor function in a sieve costume" framing.

[`experiments/acm/diagonal/cheapest_sieve/README.md`](experiments/acm/diagonal/cheapest_sieve/README.md)  
kind: control-split note | family: diagonal | kernel: 2,3  
hook: Plot 9 with the 73% `cost_diag` / `cost_prime` agreement headline, structural disagreements all pointing one way, and the negative result that `cost_k` is a comb of prime-factor strips rather than a curve.

[`experiments/acm/diagonal/complementary_curves/README.md`](experiments/acm/diagonal/complementary_curves/README.md)  
kind: failed-prediction note | family: diagonal | kernel: 2,3  
hook: Plot 8 with the headline that the `(pronic, prime)` prediction failed, plus two structural findings: disjointness is free at this scale and selectors do not transfer to generators.

<a id="cantor-walk-readme"></a>
[`experiments/acm/diagonal/cantor_walk/README.md`](experiments/acm/diagonal/cantor_walk/README.md)  
kind: rate-geometry note | family: diagonal | kernel: 2,5  
hook: Plot 5 on "geometry causes rate": slope matching the rank-1 boundary recovers linearly, Cantor is quadratic, row-by-row is `N×linear`. The picture that turns strict ascent into a rate.

<a id="cascade-key-readme"></a>
[`experiments/acm/diagonal/cascade_key/README.md`](experiments/acm/diagonal/cascade_key/README.md)  
kind: visual realization note | family: diagonal | kernel: 2  
hook: Plot 4 as cascade heatmap: "one key per row, all locks," turning the strict-ascent inequality `k ≤ n_k − 1` into a visible mechanism.


## Shelf C — Context and scaffolding

### Discipline / planning docs

<a id="bqn-agent"></a>
[`guidance/BQN-AGENT.md`](guidance/BQN-AGENT.md)  
kind: notation discipline doc | family: guidance | kernel: 4  
hook: Canonical BQN names such as `NPn2`, `NthNPn2`, `Digits10`, `ChamDigits10`, `LeadingInt10`, `LD10`, `Benford10`, `BinDigits`, `BStream`, and `V2`. Every core theorem doc sources notation here.

<a id="struct-sig-plan"></a>
[`experiments/acm-champernowne/base2/STRUCT-SIG-PLAN.md`](experiments/acm-champernowne/base2/STRUCT-SIG-PLAN.md)  
kind: writing-discipline plan | family: base2 | kernel: 2,3,5  
hook: Review copy for STRUCTURAL-SIGNATURES prescribing the seven-field shape, source precedence, writing constraints, and staleness rule. A discipline doc for how the synthesis packet should read.

[`experiments/acm-champernowne/base2/forest/valuation/VALUATION-PLAN.md`](experiments/acm-champernowne/base2/forest/valuation/VALUATION-PLAN.md)  
kind: experiment plan | family: base2 | kernel: 2,3  
hook: Substrate-cache-then-three-viz plan with audit-trail discipline lifted from WALSH and an explicit `N_RENDER` versus `N_ANALYTIC` split.

[`experiments/acm-champernowne/base2/forest/violin/VIOLIN-PLAN.md`](experiments/acm-champernowne/base2/forest/violin/VIOLIN-PLAN.md)  
kind: experiment plan | family: base2 | kernel: 2,5  
hook: Three-viz plan for the base-2 sawtooth, with the Gini crossover point `d*` as the sharpest idea: when does the running mean forget which tooth it is in.

[`experiments/acm-champernowne/base2/forest/MALLORN-SEED.md`](experiments/acm-champernowne/base2/forest/MALLORN-SEED.md)  
kind: seed-index plan | family: base2 | kernel: 3  
hook: The nine-expedition forest index that seeds the whole base-2 experiment program.

### Indexes / READMEs

[`experiments/README.md`](experiments/README.md)  
kind: top-level index | family: experiments | kernel: 3  
hook: The classification rule that the top-level directory answers "what is the source?" rather than "what does the visualization look like?"

[`experiments/acm-champernowne/README.md`](experiments/acm-champernowne/README.md)  
kind: family index | family: experiments | kernel: none  
hook: Base10 / base2 split explanation for the ACM-Champernowne subtree.

[`experiments/acm-champernowne/base2/README.md`](experiments/acm-champernowne/base2/README.md)  
kind: family index | family: base2 | kernel: none  
hook: Pointer index to BINARY, FINITE-RECURRENCE, and HAMMING-BOOKKEEPING.

[`experiments/acm-champernowne/base10/README.md`](experiments/acm-champernowne/base10/README.md)  
kind: family index | family: base10 | kernel: none  
hook: Index to sawtooth, shutter, stats, and art on the base-10 side.

[`experiments/bidder/README.md`](experiments/bidder/README.md)  
kind: family index | family: bidder | kernel: none  
hook: Index of BIDDER-output experiment families: dither, reseed, stratified, digits, and art contamination.

[`experiments/math/README.md`](experiments/math/README.md)  
kind: family index | family: math | kernel: none  
hook: One-item index to `arcs/` and the ε landscape.

[`experiments/future/README.md`](experiments/future/README.md)  
kind: family index | family: future | kernel: 3  
hook: A "holding area, not a graveyard" index for unstable ideas.

[`README.md`](README.md)  
kind: root map | family: root | kernel: 2,3,4  
hook: Root README organized around construction, generator, and gallery passes, with pointers into the Tier-A core docs and the theory-test front.

### Agent / parity conventions

[`AGENTS.md`](AGENTS.md)  
kind: repo convention doc | family: guidance | kernel: 3  
hook: Root build and test reference, including the "signposting is for the birds" discipline line that underwrites the repo's document style.

<a id="generator-agents"></a>
[`generator/AGENTS.md`](generator/AGENTS.md)  
kind: implementation convention doc | family: bidder | kernel: 3  
hook: Cross-language parity rules, feature-set discipline, and shared constants for the Python/C pair.


## Shelf D — Gallery and side artifacts

### Art / visualization docs

[`experiments/acm-champernowne/base10/art/PITCH.md`](experiments/acm-champernowne/base10/art/PITCH.md)  
kind: art index | family: base10-art | kernel: 3,5  
hook: Five-piece art index with a "what didn't work" appendix naming why the sawtooth's amplitude is not an interesting axis.

[`experiments/acm-champernowne/base10/shutter/SHUTTER.md`](experiments/acm-champernowne/base10/shutter/SHUTTER.md)  
kind: visualization note | family: base10-art | kernel: 5  
hook: Rolling-shutter first-digit heatmap with the line worth lifting: the shear angle is a number-theoretic constant made physically visible.

[`experiments/acm-champernowne/base10/art/fabric/FABRIC.md`](experiments/acm-champernowne/base10/art/fabric/FABRIC.md)  
kind: art family note | family: base10-art | kernel: 5  
hook: The fabric family as a study in representation, organized as a two-axis taxonomy of encodings and geometries rather than a single image.

[`experiments/acm-champernowne/base10/art/fabric/noising/NOISING.md`](experiments/acm-champernowne/base10/art/fabric/noising/NOISING.md)  
kind: destruction-study note | family: base10-art | kernel: 2  
hook: The real finding is multiscale structure: pure blur weakens gradually, relabeling does nothing, blur plus nonlinear scramble plus blur breaks the fabric quickly.

[`experiments/acm-champernowne/base10/art/fabric/inverted/INVERTED.md`](experiments/acm-champernowne/base10/art/fabric/inverted/INVERTED.md)  
kind: art family note | family: base10-art | kernel: 5  
hook: Inverted-polar significand family with the line worth keeping: inversion is a reallocation of visual resolution.

[`experiments/acm-champernowne/base2/art/rle/RLE.md`](experiments/acm-champernowne/base2/art/rle/RLE.md)  
kind: art family note | family: base2-art | kernel: 3,5  
hook: RLE art set including the deliberate negative lesson that direct radius is too expensive a coordinate for this distribution.

[`experiments/acm-champernowne/base2/art/valuation/VALUATION.md`](experiments/acm-champernowne/base2/art/valuation/VALUATION.md)  
kind: art-side companion note | family: base2-art | kernel: 3  
hook: Four layout variants on V3 residual data, with clear discipline on what to keep across variants: residual is the signal, confidence gates visibility, under-supported rows are context.

[`experiments/acm-champernowne/base10/art/sieves/SIEVES.md`](experiments/acm-champernowne/base10/art/sieves/SIEVES.md)  
kind: art family note | family: base10-art | kernel: none  
hook: Moire sieves and sieve carpet.

[`experiments/acm-champernowne/base10/art/sieves/ULAM-SPIRAL.md`](experiments/acm-champernowne/base10/art/sieves/ULAM-SPIRAL.md)  
kind: visualization note | family: base10-art | kernel: 5  
hook: Golden-angle spiral of sieve density with a useful two-views note: ε landscape highlights isolation, this view highlights composite richness.

[`experiments/math/arcs/ARCS.md`](experiments/math/arcs/ARCS.md)  
kind: bridge image note | family: math-art | kernel: 5  
hook: The ε landscape 3D surface, functioning as the bridge image for ε across bases.

[`experiments/future/wibblywobblies/WIBBLYWOBBLIES.md`](experiments/future/wibblywobblies/WIBBLYWOBBLIES.md)  
kind: vocabulary note | family: future | kernel: 5  
hook: Coins "wibble" versus "wobble" for off-center peak versus asymmetry around the peak, with a tiny conservation-style claim.

### Historical / side artifacts

[`sources/BIDDER-AND-SON.md`](sources/BIDDER-AND-SON.md)  
kind: historical note | family: sources | kernel: 5  
hook: G. P. Bidder versus his son's mental log methods framed as decomposing the target versus decomposing the space. Echoes the repo's broader decomposition discipline.

[`nasties/FIRST-DIGIT.md`](nasties/FIRST-DIGIT.md)  
kind: bug-origin note | family: nasties | kernel: none  
hook: FP truncation bug in `first_digit`, and the origin of the `+1e-9` guard that later `LD10` usage carries as a caveat.


## Shelf E — Companion code prose

### Core module prose

[`core/hardy_sidestep.py`](core/hardy_sidestep.py)  
kind: companion module prose | family: core-code | kernel: 3  
hook: Module and function docstrings restating the Hardy closed form and its cost argument side by side with HARDY-SIDESTEP.md.

[`core/acm_core.py`](core/acm_core.py)  
kind: companion module prose | family: core-code | kernel: 4  
hook: Long module header with definitions, ACM literature connection, and the mapping from Python names to canonical BQN names.

[`core/sawtooth.py`](core/sawtooth.py)  
kind: companion module prose | family: core-code | kernel: 3  
hook: Module docstring presenting `NPrimeSequence` as the math-layer dual of `BidderBlock`, with random access via the Hardy closed form.

<a id="api-doc-examples"></a>
[`core/api_doc_examples.py`](core/api_doc_examples.py)  
kind: discipline-support module | family: core-code | kernel: 3  
hook: Markdown code-block verifier that rewrites example blocks from API.md, RIEMANN-SUM.md, and BIDDER.md as assertions before execution so the docs cannot drift from the code.

### Experiment module prose

[`experiments/bidder/unified/riemann_proof.py`](experiments/bidder/unified/riemann_proof.py)  
kind: experiment companion module | family: bidder-code | kernel: 2  
hook: The experiment ancestry for `test_riemann_property.py`, with a module docstring restating the permutation-invariance argument and enumerating the four visual panels.

[`experiments/bidder/unified/adversarial_integrands.py`](experiments/bidder/unified/adversarial_integrands.py)  
kind: experiment companion module | family: bidder-code | kernel: 2  
hook: Module docstring mapping four integrands to rows of the Euler-Maclaurin table and naming which rate each one hits.

[`experiments/bidder/unified/mc_diagnostic.py`](experiments/bidder/unified/mc_diagnostic.py)  
kind: experiment companion module | family: bidder-code | kernel: 2  
hook: Module docstring contrasting cipher, sawtooth, and numpy PRNG, with the birthday-bound collision count named as the distinguishing feature.

[`experiments/bidder/unified/period_anatomy.py`](experiments/bidder/unified/period_anatomy.py)  
kind: experiment companion module | family: bidder-code | kernel: 2  
hook: Four-row diagnostic contrast between cipher and sawtooth output: raw, histogram, first-difference, and autocorrelation.


## Coverage gaps

### Not yet surveyed

A broader `.py` docstring pass is still open. The `core/` files were
opened and `experiments/bidder/unified/` was spot-checked, but still
unread are experiment scripts under:

- `experiments/bidder/reseed/`
- `experiments/bidder/stratified/`
- `experiments/bidder/dither/`
- `experiments/bidder/art/contamination/`
- `experiments/bidder/digits/`
- `experiments/acm/...`
- `experiments/acm-champernowne/base2/forest/*/*.py`

The forest scripts driving the synthesis docs are plausible Shelf-E
candidates worth a quick scan if the collection goes wide. The
`contamination/` scripts are probably Shelf D.

### Classification notes

[`experiments/acm-champernowne/base2/forest/walsh/walsh_upgrade_results.md`](experiments/acm-champernowne/base2/forest/walsh/walsh_upgrade_results.md)  
kind: audit companion | family: base2 | kernel: none  
hook: Opened and classified as numerical tables only. Useful audit companion to `WALSH.md`, not a collection candidate on its own.

[`experiments/acm-champernowne/base2/STRUCT-SIG-PLAN.md`](experiments/acm-champernowne/base2/STRUCT-SIG-PLAN.md) versus [`experiments/acm-champernowne/base2/STRUCTURAL-SIGNATURES.md`](experiments/acm-champernowne/base2/STRUCTURAL-SIGNATURES.md)  
kind: classification refinement | family: base2 | kernel: 2,5  
hook: The plan doc prescribes the final doc's seven-field shape almost verbatim. Worth noting that a plan for a doc can itself carry kernel features, even when it stays on Shelf C rather than Shelf B.
