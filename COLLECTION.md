# BIDDER Collection

A curated reader's guide to the theory work in this repository.

This file is one of three related artifacts.
[`guidance/network/SURVEY.md`](guidance/network/SURVEY.md) is
the exhaustive survey that sorts every theory doc into shelves
with kernel annotations.
[`guidance/network/surveys/`](guidance/network/surveys/) holds
the per-doc compact surveys for the load-bearing entries —
one file per doc cited in this collection, each structured by
shelf sub-section (claim / mechanism, setup / headline, etc.).
The entries in this file point into `guidance/network/surveys/`
directly. This file — the collection — is the editorial layer:
it commits to a reading of what this body of work is for and
how to enter it. The catalog answers *where is X*, the per-doc
surveys answer *what does X say*, and the collection answers
*why does X matter, and how does it fit with Y*.


## Preface

This repository is an exact-math toolkit plus a body of
meta-discipline about how to build and write exact math. The
toolkit is small and the meta-discipline is larger; the second
half is the more distinctive half of the work.

**The toolkit** is three things that compose into one object:

- a family of multiplicative monoids `nZ+` whose irreducible
  elements (the *n-primes*) have a closed form for every `n ≥ 2`,
  sidestepping the century of analytic apparatus that has grown up
  around the ordinary-prime case `n = 1`
- a positional encoding (the *ACM-Champernowne real*) that turns
  those irreducibles into a scalar whose leading digits are
  *exactly* uniform over a complete digit block, by a counting
  argument from positional notation
- a generator (*BIDDER*) that permutes the integers in a complete
  digit block and extracts leading digits, producing a stream
  whose output distribution is exact rather than approximately
  uniform

**The meta-discipline** is the set of editorial practices the
repo has accreted around these objects. They include an
anti-over-claim register (nearly every doc has a "not claimed"
section), a three-layer presentation format (English / Python /
BQN), a retraction culture where walked-back claims are a
first-class document genre, and a recurring observation that
the repo calls *leaky parameterization* — that the recovery
questions the toolkit invites keep collapsing to trivial
inversions for reasons the toolkit did not intend.

**What this repository is not.** It is not a cryptographic
library; BIDDER is not for secrets and the root README warns so
at the top. It is not a paper draft; the docs are organized by
topic, with cross-references and explicit gaps, not by argument
flow. It is not a tutorial; readers are assumed to know what
they want from a theorem. It is not a random-walk playground;
every experiment carries a control and a falsification criterion.

**What's distinctive, in the sense that other repositories rarely
have it:**

1. The exact substrate is narrow. The block-uniformity lemma is
   one paragraph. The Hardy closed form is one `divmod`. The
   surprises live in the structure of the claims, not in their
   proofs.
2. The meta-layer is load-bearing. A large fraction of the
   repo's content is *about* how the repo was written — the
   pair-programming phenomenology, the red-team tests, the
   correction discipline, the knife-edge caveat about productive
   triviality in constructed spaces. 
3. Cross-language parity is enforced. Python and C
   implementations produce byte-identical output in critical files. 
   BQN blocks are exact-math annotation labeled as such. Code, docs,
   and parallel implementations of either form a triad for comparison.
4. Negative results are first-class. "The sign was wrong," "the
   prediction failed," "audited down" are headline phrasings.

**What the collection does not cover.** The art folders on
Shelf D of the survey (visualizations of the structure for
non-technical readers); the historical sources like
`BIDDER-AND-SON.md` (context, not content); the READMEs and
index docs on Shelf C (scaffolding around the clusters rather
than the clusters themselves); the companion-code prose on
Shelf E (the source docs carry the claims). These live in the
survey as context. The collection is about load-bearing claims
and the argument that ties them together.


## Chapter 1: The Construction

The construction is the smallest part of the repo and the part
everything else rests on. It is a counting argument, a closed
form, and a positional encoding, combined into a single object
— the n-Champernowne real — that the rest of the work probes.

The *counting argument* is the block-uniformity lemma. In base
`b ≥ 2`, the integers in a complete digit class
`{b^(d−1), …, b^d − 1}` have leading base-`b` digits exactly
equidistributed over `{1, …, b − 1}`. The proof is one
paragraph. Each of the `b − 1` classes contains exactly
`b^(d−1)` integers; there is no error term. The same exact
uniformity can hold for the n-prime sieve of the block under
two sufficient families (the *smooth* family `n² | b^(d−1)` and
the disjoint *Family E*), and the exact-uniformity locus is
strictly larger than either family — see the `(4, 5, 5)`
unconditional witness. The sieved lemmas are what would let an
"n-prime BIDDER variant" inherit exact uniformity from a smaller
block; the variant is math-ready and cipher-unbuilt.

The *closed form* is the K-th n-prime. For `n ≥ 2`, the K-th
n-prime is `n · (q · n + r + 1)` where
`q, r = divmod(K − 1, n − 1)`. One divmod, one multiply,
polylog cost in `K`. The title's *sidestep* points at the fact
that Hardy and his successors spent a century on the
distribution of ordinary primes — the K-th ordinary prime is
reachable only in `K^{2/3 + o(1)}` operations, via
Meissel–Lehmer–Lagarias–Odlyzko prime counting — while the
n-prime version for `n ≥ 2` is free. The irregularity Hardy
was describing is a property of the operation `n = 1`, not of
irreducibility in general. Change the monoid, and the search
problem evaporates.

The *positional encoding* is the Champernowne real. Given the
first `K` n-primes of monoid `n`, concatenate their decimal
representations after "1." to form a real number `C_b(n)`. The
scalar packs two kinds of information: the number-theoretic
content of the monoid (which elements are irreducible) and the
typographic cost (how many digits each one requires). Over a
complete digit block, the leading digits of these reals are
exactly uniform by the counting argument. That is the
substrate the generator rests on.

**Entries.**

- [`core/BLOCK-UNIFORMITY.md`](guidance/network/surveys/block-uniformity.md) — the counting lemma; load-bearing for every exact-distribution claim downstream.
- [`core/HARDY-SIDESTEP.md`](guidance/network/surveys/hardy-sidestep.md) — the K-th n-prime in one divmod; why the sidestep is sharp.
- [`core/ACM-CHAMPERNOWNE.md`](guidance/network/surveys/acm-champernowne.md) — the base construction, for vocabulary and literature anchors.
- [`sources/EARLY-FINDINGS.md`](guidance/network/surveys/early-findings.md) — first surprises and open questions, cited by every seed.


## Chapter 2: The Generator

BIDDER is the construction's applied product. The question it
answers is: given the block-uniformity lemma, can we build a
generator whose output distribution is exactly uniform — not
statistically close, exactly — and is the guarantee robust
enough to survive a keyed permutation that provides disorder?

The answer is yes, and the architectural move is to *factor the
problem*. An algebraic substrate (the integer block
`[b^(d−1), b^d − 1]`) provides exact leading-digit uniformity
by the counting argument. A keyed permutation (Speck32/64 in
cycle-walking mode, with a balanced Feistel fallback for small
blocks) provides the disorder. Neither piece is asked to do the
other's job. The substrate does not need randomness; the
permutation does not need to establish uniformity. This
factoring is the architectural insight the generator makes
visible.

The consequences compound. At `N = P` — one full period — the
Monte Carlo estimate from `bidder.cipher` is not an
*approximation* of the Riemann sum; it *is* the Riemann sum,
exactly, for any integrand and any key. The key cancels in the
sum because a sum over a permutation of a set equals the sum
over the set. This is the structural layer of the RIEMANN-SUM
doc, and its proof is one line. Below the period, the cipher's
finite-population-correction behavior is a *measurement* rather
than a theorem, because it depends on the pseudorandom
permutation quality. The current Feistel backend shows a ~1.5–2.5×
variance gap against the ideal shuffle null at intermediate `N`.
The doc records that gap honestly instead of fitting it away,
and carefully separates the structural guarantee (exact at
`N = P`, independent of PRP quality) from the statistical
behavior (PRP-dependent everywhere else).

BIDDER also carries the repo's most compact worked example of
the anti-over-claim discipline. The design doc at
`generator/BIDDER.md` splits its claims into *Proved*,
*Measured*, and *Not claimed* sections. The *Not claimed*
section is the distinctive one: it lists the PRP properties
that would be required for adversarial use — distinguishing
advantage, key independence beyond the structural `E_P = R`
result, side-channel behavior — and explicitly does not claim
them for this composition. The root README and `BIDDER.md` both
warn that BIDDER is not a secret-generation tool. This kind of
discipline, which cares about the boundary between "we built
this" and "we verified this for that use case," is one of the
repo's most characteristic moves, and it lives in the generator
docs in its most explicit form.

**Entries.**

- [`core/RIEMANN-SUM.md`](guidance/network/surveys/riemann-sum.md) — why BIDDER is *useful* for Monte Carlo, not just *correct*.
- [`BIDDER.md`](guidance/network/surveys/bidder-root.md) — the user-facing root API in three layers.
- [`core/API.md`](guidance/network/surveys/api.md) — the detailed cipher-path reference with the `UnsupportedPeriodError` discipline.
- [`generator/BIDDER.md`](guidance/network/surveys/bidder-generator.md) — the cipher design doc and the *Proved / Measured / Not claimed* discipline in its most explicit form.
- [`tests/theory/README.md`](guidance/network/surveys/tests-theory-readme.md) — the theorem index between words and the tests that would falsify them.


## Chapter 3: The Recovery Thread

This is the repo's most distinctive cluster, and the one
carrying the strongest meta-layer. It starts with a single
observation — that the diagonal of an ACM irreducible table,
divided pointwise by position, recovers its row labels — and
ends with a discipline for proposing recovery experiments in
constructed spaces at all. The theorems are elementary. The
editorial work is what earns the chapter.

The *observation* is this. Build an `N × N` table whose
`(k, k')` entry is the `k'`-th `n_k`-prime, with
`n_1 < n_2 < … < n_N` strictly ascending and every `n_k ≥ 2`.
Then the diagonal `D_k = k · n_k`, divided by `k`, gives back
`n_k`. One line, elementary — the first `n_k − 1` n-primes of
monoid `n_k` are `n_k, 2n_k, …, (n_k − 1)n_k`, and strict
ascent guarantees the diagonal cell `(k, k)` stays inside that
rank-1 region. The proof is half a page. But when the author
first worked with the table, the inference did not come. It
took a seemingly unrelated question about Cantor's diagonal
to surface it. The `ABDUCTIVE-KEY.md` doc records this in its
"note on visibility" section: the lemma is elementary, the
observation is not.

Once surfaced, the same pattern *kept happening*. The **cascade
key** (plot 4): once `n_k` is decoded from the diagonal cell,
every later cell of row `k` decodes too, because `j_{k'}` is a
function of `k'` and `n_k` alone. The framing shifted from
"later patches have their own keys" to "one key, all locks."
The **greedy extraction** (UNORDERED-CONJECTURE): an algorithm
that reconstructs the row list from the *unordered multi-set*
of cell values, with zero hints, in `O(N²)`, because the row
labels are literally the row-wise minima of the multi-set.
The **Hardy closed form** from the previous chapter is a
fourth instance of the same observation in a different channel
— the K-th n-prime recovered from `(n, K)` alone, no
enumeration.

Each time, the recovery question was framed as if the author
did not know the n-prime structure, and each time the structure
made the question free. After the third instance, the pattern
got a name: **leaky parameterization**. The n-prime row is
parameterized by a single scalar `n_k`, and single-scalar
inversions are all trivial. The hard problem is not recovering
`n_k`; it is free in at least four channels. The hard problem
is noticing in advance that the construction has this much
structure — so that future recovery questions don't get briefed
as experiments they already have free solutions to.

The UNORDERED-CONJECTURE doc closes with the *knife-edge:
productive triviality* section, which is the chapter's most
careful move. The leaky parameterization is either a *foothold*
(rich consequences from a trivial surface presentation, the way
`(AB)^T = B^T A^T` is one symbol-pushing line and underlies
most of matrix theory) or a *perimeter* (no structure beneath
the surface, every "result" a relabeling of the parameterization
in new sentences). The repo is operating in a *constructed*
space — the author defined the n-prime table on purpose — so
the perimeter risk is sharper here than in discovered spaces
like the integers. The discipline prescribed: before briefing
a future recovery experiment in this area, write the half-line
description of what the trivial extraction would be and check
whether it already works. Classify each question as *recovery*
(will collapse), *dynamics* (may be hard), or *transport*
(hard or vacuous; check carefully). Apply the two-sided check
— *input side* ("is the answer already in the definition?")
and *output side* ("does the chosen observable factor through
a tiny invariant?") — and only trust a result if both come
back "no."

This thread carries meta-layer as load-bearing content. A
reader who takes nothing else from the repo should still take
the knife-edge section.

**Entries.**

- [`core/ABDUCTIVE-KEY.md`](guidance/network/surveys/abductive-key.md) — the rank-1 diagonal recovery and the "note on visibility." The chapter's anchor.
- [`experiments/acm/diagonal/cantor_walk/UNORDERED-CONJECTURE.md`](guidance/network/surveys/unordered-conjecture.md) — the longest and densest meta-layer doc in the repo; the knife-edge and the three surprises.
- [`experiments/acm/diagonal/CANTORS-PLOT.md`](guidance/network/surveys/cantors-plot.md) — the garden map for the diagonal expeditions.
- [`experiments/acm/diagonal/cascade_key/README.md`](guidance/network/surveys/cascade-key-readme.md) — "one key, all locks" as visible geometry.
- [`experiments/acm/diagonal/cantor_walk/README.md`](guidance/network/surveys/cantor-walk-readme.md) — strict ascent as a rate, not just a condition.


## Chapter 4: The Binary Frontier

The base-2 side of the repo is the active frontier and also
the cluster where the anti-over-claim and retraction
disciplines are most visibly exercised. Binary Champernowne
is a different mathematical object from the base-10
construction — not a variant, a genuinely different beast —
and the base-2 docs work out what that means piece by piece.

Four things have to be understood in order.

**What collapses.** The leading-digit uniformity that drives
BIDDER as a generator is a foundational theorem in base
`b ≥ 3`, where the alphabet `{1, …, b − 1}` has multiple
symbols. In base 2 the alphabet is `{1}` — one symbol,
trivially and uninformatively uniform — and the entire
leading-digit framework has nothing to grab onto. `BINARY.md`
names the verdict: base 2 is "not a better generator; a
better lens for the pure mathematics." The projection from
the integer block to its leading digit, which is BIDDER's
distinctive step, maps everything to `1` in binary and
destroys the information content. The generator dissolves.

**What sharpens.** The sawtooth function `log₂(C₂(n))` is not
an *analog* of the floating-point `ε(m) = log₂(1 + m) − m`
function from the SlideRule project — it *is* that function,
exactly. The connection that required a translation in base 10
is an identity in base 2. The entire `forest/` subtree of
base-2 experiments starts from this observation, because
once the sawtooth is exactly ε, anything known about ε applies
verbatim to the binary Champernowne stream without a base
conversion.

**What emerges.** The binary Champernowne stream has a
bit-balance closed form (`HAMMING-BOOKKEEPING.md`) that
depends only on `v₂(entry)` — the 2-adic valuation of each
individual n-prime, not of the monoid label. The "penalty
linear, bonus exponential, cross at `m = 1`" argument gives
the closed form directly. Several base-2 experiments then
test how well `v₂(n)` predicts structure that `v₂(entry)`
is actually the right parameter for. The `DETRENDED_RDS` doc
corrects an earlier per-monoid reading to per-entry and
shows the correction is large (the residual for `n = 12`
drops from `−6264` to `+11` under the per-entry prediction).
The valuation-forest experiment finds that 2-adic depth
captures most of the signal but localized exceptions
concentrate at small odd parts. The Walsh experiment finds a
44-cell robust coefficient-level family where **all 44 die
under entry-order shuffle** — entry order is the dominant
discriminator, and `v₂(n)` explains only a minority of the
brightest cells. All four point at the same fact from
different angles: the binary stream carries order-dependent
structure that marginal `v₂(n)` bookkeeping does not fully
explain.

**What is conjectured and audited.** The `FINITE-RECURRENCE`
conjecture claims no finite automaton can recognize a binary
ACM stream. The three-point argument: entry lengths are
unbounded, so no fixed state count can track the current
entry; the natural periodicity in `k`-space is destroyed by
the variable-length stretching into bit-stream space; two of
the three quantities controlling local structure (`v₂` of the
entry, position within bit-length class, residue mod `n`)
are themselves unbounded. The `KINK-INVESTIGATION` doc is the
long-form worked example of the retraction discipline in
action: an earlier, stronger reading of the `n = 3` wavelet
scalogram as a three-rung arithmetic lattice was walked back
after a bandwidth sensitivity table, a 300× bootstrap, six
white-noise controls, and a nine-item "what this note does
not claim" section. The headline phrasing "audited down" is
the line to lift. This is the chapter where the repo most
visibly shows how it treats its own mistakes.

**Entries.**

- [`experiments/acm-champernowne/base2/BINARY.md`](guidance/network/surveys/binary.md) — what collapses, sharpens, emerges in base 2; the chapter's vocabulary anchor.
- [`experiments/acm-champernowne/base2/HAMMING-BOOKKEEPING.md`](guidance/network/surveys/hamming-bookkeeping.md) — bit-balance closed form and the per-entry correction.
- [`experiments/acm-champernowne/base2/disparity/DETRENDED_RDS.md`](guidance/network/surveys/detrended-rds.md) — the disparity-domain twin of Walsh's "order matters" finding.
- [`experiments/acm-champernowne/base2/forest/walsh/WALSH.md`](guidance/network/surveys/walsh.md) — the 44-cell robust family and the audit-trail-per-`npz` policy.
- [`experiments/acm-champernowne/base2/FINITE-RECURRENCE.md`](guidance/network/surveys/finite-recurrence.md) — the structural boundary condition the chapter's measurements live inside.
- [`experiments/acm-champernowne/base2/disparity/rds_wavelet/KINK-INVESTIGATION.md`](guidance/network/surveys/kink-investigation.md) — the retraction discipline in its sharpest worked form.


## Chapter 5: The Discipline

Four chapters of theorems, applications, recoveries, and
frontiers, and the single practice that ties them together is
*instrumentation under tension*. The repo's most
characteristic move is not rigour, not honesty, and not even
the retraction culture of the previous section — it is the
quieter structural decision to build each load-bearing claim
in multiple independent channels and then force the channels
to check each other. The channels are not adversaries. They
are the pair of surfaces a chimney-climber wedges themselves
between. The image for this chapter is Kuzco and Pacha in
*The Emperor's New Groove*, braced back-to-back against
opposing rock walls in the crevasse scene, each unable to
stay up alone and each only making progress because the
*other* is pushing in the opposite direction. Neither is
trying to knock the other down. The opposition is
directional — one pushes against his wall, the other pushes
against his — and the two *together* stay up because each
transmits the other's weight into its own surface. Remove
either and both fall. That is the discipline. It is held up
by opposition that is explicitly collaborative.

Four triads show up repeatedly in the repo, each a different
chimney in the same climb.

**BQN / English / Python.** Every load-bearing math claim in
the core docs appears in prose (for intent), in Python (for
behavior), and in BQN (for exact-math specification). The
three layers are not redundant. When a proof is written only
in prose, nothing forces the prose to match the
implementation. Once the Python example is rewritten as an
assertion by `core/api_doc_examples.py`, English and
behavior cannot drift without the verifier catching it. Once
the canonical BQN `NthNPn2 ← {𝕨 × 1 + ((𝕨-1)|𝕩-1) + 𝕨 × ⌊(𝕩-1)÷𝕨-1}`
sits next to the Python `nth_n_prime`, the exact-math
specification and the implementation each hold the other up.
`guidance/BQN-AGENT.md`'s framing — *DOCS :: C :: PYTHON* as
a triangle with BQN as a fourth vertex that stays honest the
same way the other three do — is the compact statement of
this triad, extended by one.

**C / Python / English.** Both the core math layer
(`core/acm_core.py` and `core/acm_core.c`) and the generator
(`generator/coupler.py` and `generator/bidder.c`) have
parallel C and Python implementations. For the generator the
parity rule is enforced directly by `tests/test_bidder.py`
with hardcoded expected values; the core has per-
implementation tests against the same expected values via
`tests/test_acm_core.py` and `tests/test_acm_core_c.c`.
Neither implementation is "the real one" in either layer.
The C and the Python are wedged against each other precisely
because either alone could be wrong in a way only the
cross-check can surface. The *cost* is that every change
costs twice; the *value* is that neither can drift on its
own. `generator/AGENTS.md` carries the rule in its most
explicit form: both implementations must produce byte-
identical output for identical inputs, and any change to one
must be mirrored in the other.

**Human / cold-agent / in-session-agent.**
`guidance/PAIR-PROGRAMMING.md` documents this triad at
length. The in-session agent — any model, at the time of
writing any given section — is fluent in the framings the
conversation has built and blind to them as a result. The
cold agent arrives without the session's idiolect and
surfaces things the in-session agent had the capacity to
catch but didn't, because foreign vocabulary cannot be
absorbed by an existing framing and forces a translation
where loose language fails. The human supplies the global
consistency checks and the temporal pattern recognition
neither agent does spontaneously. Each of the three is
downstream of a different bias, and each compensates for the
others'. The doc's most careful observation is that this is
*not* a smarter-model effect — the math in every caught
mistake was elementary, and a fresh instance of the same
model would catch comparable things. The relevant axis is
in-session versus out-of-session, not capability.

**Theorem / test / experiment.**
`tests/theory/RED-TEAM-THEORY.md` is the most compact form
of this triad. For every proved result there is (1) the
proof doc under `core/`, (2) a pass/fail test under
`tests/theory/` that attacks the claim at each layer of the
decomposition `E_N − I = (E_N − R) + (R − I)`, and (3) a
visual experiment under `experiments/bidder/` that renders
the behavior for inspection. Three artifacts per theorem,
each doing a different kind of check. The red-team posture
is not "try to break it" in an adversarial sense; it is
*isolate the claims that look similar from the claims that
are actually the same, and instrument each layer
independently so the layers cannot silently bleed into each
other*.

The word for what the four triads do — collectively and
individually — is *bracing*, not *audit* and not *verify*.
Those words suggest a one-way check, where an inspector
stands outside and evaluates the artifact. Bracing is
two-way, or four-way, or seven-way. Each channel is as
dependent on the others as it is checking them. The BQN
specification would have no anchor without the Python
implementation; the Python would be invisibly wrong without
the spec. The C would drift from Python without the parity
test; the Python would drift from C equally. The cold agent
cannot do its work without the in-session agent's
elaboration to react to; the in-session agent cannot catch
its own framings without the cold agent's foreign
vocabulary. The theorem would be a stand-alone claim without
the test; the test would be a bag of numbers without the
theorem. Nothing in the list is one-way.

The correction/retraction discipline from the cross-cuts
section is the *visible product* of this chimney-climbing.
Retractions happen when the channels disagree.
`KINK-INVESTIGATION` was audited down because the bandwidth
sweep disagreed with the earlier fit — two instrumentations
of the same data produced different answers and the
disagreement was load-bearing. `DETRENDED_RDS` corrected
`HAMMING-BOOKKEEPING`'s per-monoid reading because the
disparity-domain measurement disagreed with the per-monoid
bit-balance closed form, and the cross-check surfaced the
correction. `SAWTOOTH-SECANT`'s "the sign was wrong" section
exists because the analytic prediction disagreed with the
empirical staircase. In each case the correction is not an
embarrassment; it is the discipline *working*. A repo with
only one channel per claim could not have produced those
corrections, because there would be nothing for a claim to
disagree with. The retraction culture is not an ethical
stance. It is what this kind of instrumentation looks like
when it finds something.

**Entries.**

- [`guidance/PAIR-PROGRAMMING.md`](guidance/network/surveys/pair-programming.md) — the human / cold-agent / in-session-agent triad; the repo's most careful doc about how the work got done.
- [`tests/theory/RED-TEAM-THEORY.md`](guidance/network/surveys/red-team-theory.md) — the four-layer decomposition and the theorem / test / experiment triad.
- [`guidance/BQN-AGENT.md`](guidance/network/surveys/bqn-agent.md) — the *DOCS :: C :: PYTHON* triangle with BQN as a fourth vertex.
- [`generator/AGENTS.md`](guidance/network/surveys/generator-agents.md) — the C / Python parity rule in its most compact enforcement.
- [`core/api_doc_examples.py`](guidance/network/surveys/api-doc-examples.md) — the mechanism that pins English to Python in the three-layer docs.

*Related.* The seven-field shape prescribed by [`experiments/acm-champernowne/base2/STRUCT-SIG-PLAN.md`](guidance/network/surveys/struct-sig-plan.md) for synthesis notes is this chapter's discipline applied per-observable — a chimney with seven walls instead of two.


## Reading paths

Five linear sequences through the chapters, each with a framing
line. The sequences disagree on purpose; their disagreement is
information about the corpus.

**Math-first (5 docs, ~1 hour).** Stop here if you only want
the exact-math substrate.

1. [`core/ACM-CHAMPERNOWNE.md`](core/ACM-CHAMPERNOWNE.md) — the
   construction
2. [`core/BLOCK-UNIFORMITY.md`](core/BLOCK-UNIFORMITY.md) — the
   counting lemma
3. [`core/HARDY-SIDESTEP.md`](core/HARDY-SIDESTEP.md) — the
   closed form
4. [`core/RIEMANN-SUM.md`](core/RIEMANN-SUM.md) — the
   generator's theoretical basis
5. [`core/ABDUCTIVE-KEY.md`](core/ABDUCTIVE-KEY.md) — the
   recovery observation

**Engineer-first (5 docs, ~45 minutes).** Stop here if you
want to use the library. Skip the recovery thread unless you
have reason.

1. [`BIDDER.md`](BIDDER.md) — the root API
2. [`core/API.md`](core/API.md) — the detailed reference
3. [`generator/BIDDER.md`](generator/BIDDER.md) — the design
   doc and its Proved/Measured/Not claimed discipline
4. [`tests/theory/README.md`](tests/theory/README.md) — what's
   tested
5. [`core/BLOCK-UNIFORMITY.md`](core/BLOCK-UNIFORMITY.md) —
   the theorem the API rests on

**Skeptic-first (7 docs, ~2 hours).** Read in this order if
you want to see how the repo treats its own claims before you
trust any of them.

1. [`tests/theory/RED-TEAM-THEORY.md`](tests/theory/RED-TEAM-THEORY.md)
   — the four-layer decomposition of `E_N − I`
2. [`generator/BIDDER.md`](generator/BIDDER.md) — the
   Proved / Measured / Not claimed discipline in compact form
3. [`core/RIEMANN-SUM.md`](core/RIEMANN-SUM.md) — where the
   algebra stops and the measurement begins
4. [`experiments/acm-champernowne/base2/disparity/rds_wavelet/KINK-INVESTIGATION.md`](experiments/acm-champernowne/base2/disparity/rds_wavelet/KINK-INVESTIGATION.md)
   — the retraction discipline in action
5. [`experiments/acm-champernowne/base2/disparity/DETRENDED_RDS.md`](experiments/acm-champernowne/base2/disparity/DETRENDED_RDS.md)
   — per-entry correction of an earlier wrong reading
6. [`experiments/acm-champernowne/base2/forest/walsh/WALSH.md`](experiments/acm-champernowne/base2/forest/walsh/WALSH.md)
   — the audit-trail-per-`npz` policy
7. [`experiments/acm/diagonal/cantor_walk/UNORDERED-CONJECTURE.md`](experiments/acm/diagonal/cantor_walk/UNORDERED-CONJECTURE.md)
   — the knife-edge caveat about productive triviality

**Meta-first (4 docs, ~1.5 hours).** Read in this order if
you care more about the discipline than the theorems.

1. [`experiments/acm/diagonal/cantor_walk/UNORDERED-CONJECTURE.md`](experiments/acm/diagonal/cantor_walk/UNORDERED-CONJECTURE.md)
   — the knife-edge, the three surprises, the
   recovery/dynamics/transport taxonomy
2. [`core/ABDUCTIVE-KEY.md`](core/ABDUCTIVE-KEY.md) — the
   rank-1 view essay and its "note on visibility"
3. [`guidance/PAIR-PROGRAMMING.md`](guidance/PAIR-PROGRAMMING.md)
   — the phenomenology of how the above got written
4. [`experiments/acm/diagonal/CANTORS-PLOT.md`](experiments/acm/diagonal/CANTORS-PLOT.md)
   — the garden context

**One hour (3 docs).** You will have the construction, the
application, and the most distinctive editorial.

1. [`core/BLOCK-UNIFORMITY.md`](core/BLOCK-UNIFORMITY.md) —
   the foundational theorem
2. [`BIDDER.md`](BIDDER.md) — the applied product
3. [`experiments/acm/diagonal/cantor_walk/UNORDERED-CONJECTURE.md`](experiments/acm/diagonal/cantor_walk/UNORDERED-CONJECTURE.md)
   — the meta-layer


## Cross-cuts

Four threads that the shelf structure of the survey cannot
surface, because each one cuts across families and kernel
features. These are promoted to first-class sections precisely
because the survey's genre-based sorting hides them.

### Leaky parameterization

The n-prime row is parameterized by a single scalar `n_k`,
and single-scalar inversions are all trivially easy. This
observation has produced at least four "obvious in
retrospect" results in the repo:

- the **abductive key** — diagonal divided by position
  recovers the row list (`ABDUCTIVE-KEY.md`)
- the **cascade key** — one diagonal cell unlocks the entire
  row via `j_{k'}(n_k) · n_k` (cascade_key/)
- the **greedy extraction** — the row labels are the row-wise
  minima of the unordered multi-set (UNORDERED-CONJECTURE.md)
- the **Hardy closed form** — the K-th n-prime is one divmod
  (HARDY-SIDESTEP.md)

Each was framed as a hard problem. Each collapsed. The
`UNORDERED-CONJECTURE` doc records the pattern and names the
discipline: before briefing a recovery experiment, write the
half-line description of what the trivial extraction would
be and check whether it works. The "knife-edge: productive
triviality" section then raises the worry that the leakiness
might be a *perimeter* rather than a *foothold* — that every
"result" derived from the parameterization might be a
relabeling of the definition in new sentences, rather than a
genuine consequence. The repo is operating in a constructed
space, so the perimeter risk is sharper than usual and the
safer default is to prefer the perimeter reading in doubt.

This cross-cut is concentrated in Chapter 3 but touches
Chapter 1 (HARDY-SIDESTEP is instance four in a different
channel) and Chapter 2 (BIDDER is conspicuously *not*
parameterized this way — the block is the integer interval,
not an n-prime enumeration — which is why the
leaky-parameterization worry does not bite the generator
side).

### Correction / retraction discipline

The repo treats walked-back claims as a first-class document
genre. Eight docs carry explicit retraction or
prediction-failed language as their headline feature:

- **`KINK-INVESTIGATION`** — "audited down" status; stronger
  earlier reading walked back against a bandwidth sweep and
  bootstrap
- **`DETRENDED_RDS`** — corrects `HAMMING-BOOKKEEPING`'s
  per-monoid claim to per-entry
- **`SAWTOOTH-SECANT`** — "the sign was wrong" correction
  section with the mechanism named
- **`hamming_strata/PREDICTIONS`** — "note on revision"
  paragraph explaining how the corrected math differs from
  an earlier wrong draft
- **`complementary_curves`** — "the prediction failed"
  headline; the `(pronic, prime)` expected winner landed at
  rank 12 of 28
- **`ENTROPY-LANDSCAPE`** — the negative result "no new
  structure beyond `v₂`" as headline
- **`cheapest_sieve`** — the `cost_slope` → `cost_prime`
  replacement after a build-phase check caught the
  degeneracy
- **`KINK_DECOMPRESSION`** — conservative-reading vs
  stronger-reading split with the conservative side
  headlined

This is probably the single most distinctive editorial
practice in the repo. The surface observation is that the
repo doesn't hide its mistakes; the deeper observation is
that the *form* of a retraction — an explicit section
naming the earlier claim, the mechanism that made it wrong,
and the corrected reading — is part of the writing
discipline, not just a honesty tax. Retractions here are
*structured*, and the structure is what lets a reader
distinguish a genuine walk-back from a defensive hedge. The
`KINK-INVESTIGATION` doc is the longest worked example; the
others are shorter but share the same seven-field anatomy.

### The three-layer presentation format

`BIDDER.md` (root), `core/API.md`, `BIDDER.md`, and several
support docs present each claim in three layers: English,
Python, BQN. English is for readers. Python is the actual
signature and a runnable example — rewritten as an assertion
by `core/api_doc_examples.py` before execution, so the docs
cannot drift from the code. BQN is the exact-math annotation
using canonical names from `guidance/BQN-AGENT.md`, labeled
explicitly as specification rather than implementation. The
BQN name `NthNPn2 ← {𝕨 × 1 + ((𝕨-1)|𝕩-1) + 𝕨 × ⌊(𝕩-1)÷𝕨-1}`
is the spec; `nth_n_prime` in `core/hardy_sidestep.py` is
the implementation; the two are tested against each other.

The layers are not redundant; they are complementary. English
carries intent. Python carries behavior. BQN carries
mathematical content. A claim stated only in one layer is
weaker than a claim stated in all three, because each layer
exposes a different kind of drift — prose ambiguity, runtime
bugs, mathematical over-claim — and the three together make
each kind visible to the others. The `BQN-AGENT.md`
discipline ("BQN is annotation — if it drifts from the
implementation, the implementation wins and the BQN gets
updated") is the compact form of this principle.

### The "constructed space" epistemic caveat

The repo constructed the n-prime table on purpose. In
*discovered* spaces — the integers, the primes, real-world
digit distributions — the structure we find is not ours and
tells us something. In *constructed* spaces, we defined the
object ourselves, and any "structure" we discover risks
being structure we put in by definition.

This caveat, recorded in the "knife-edge" section of
`UNORDERED-CONJECTURE`, is one of the most careful moves
in the repo, and it applies broadly. Any claim in Chapter 4
could in principle be a relabeling of the construction
rather than an independent finding; the doc culture's
insistence on controls, shuffles, alternative nulls, and
audit trails is partly about protecting against this
specific risk. The Walsh experiment's shuffle control (all
44 robust cells die under entry-order permutation) is the
sharpest positive result that survives the caveat: the
shuffle is *not* part of the construction, so the fact
that shuffle kills the cells is a statement about the
stream that is not tautological. `DETRENDED_RDS`'s shuffle
null plays the same role for the disparity-domain
residual.

The caveat's negative form is worth holding onto: when a
result in a constructed space looks too clean, check whether
it is cleaner than the construction itself allows. If the
answer is "no, the cleanness was in the definition," you
have a relabeling, not a result.


## Selection rule

The collection lists ~22 docs across five chapters. The survey
in [`guidance/network/SURVEY.md`](guidance/network/SURVEY.md) lists ~70. The rule for inclusion:

> A doc earns a slot in the collection if the collection's
> argument depends on it, or if reading it materially changes
> what you expect from the rest.

What this rule excludes:

- **Most of Shelf C.** Scaffolding, plans, and READMEs; the
  discipline they enforce is already captured by citing its
  artifacts in Chapter 2 (the `Proved/Measured/Not claimed`
  discipline) and Chapter 5 (the seven-field shape, the
  pair-programming phenomenology).
- **All of Shelf D.** The art and visualization docs carry
  takeaway lines that are worth lifting but do not change the
  chapters' arguments. They live in the survey as context.
- **All of Shelf E.** The companion code prose; the source
  docs carry the claims and the code is the test, not the
  entry point.
- **Most of Shelf B's base-2 cluster.** The base-2 subtree
  has ~11 measurement docs; the collection includes five
  (`BINARY`, `HAMMING-BOOKKEEPING`, `DETRENDED_RDS`, `WALSH`,
  `KINK-INVESTIGATION`). The other six are redundant angles
  on the same order-dependence finding and live in the
  survey.
- **Most of Shelf B's diagonal cluster.** The five plot
  READMEs from the diagonal garden are collectively a strong
  chapter but individually are measurement notes; the
  collection includes two (`cascade_key`, `cantor_walk`) plus
  the garden doc (`CANTORS-PLOT`) that provides context for
  the rest.

The collection is not trying to be exhaustive. It is trying
to be load-bearing. A reader who reads the collection's ~22
docs and none of the other ~50 should come away with the
repo's argument about itself. A reader who reads the survey
instead will come away with a complete map of what's there
— a different product for a different purpose.
