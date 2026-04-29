# The Undecidable Heart

A claim about the project as a whole. The other `arguments/*` files
read individual constructions through Grand / Mundane / Beautiful /
Contingent. Applied to the project, the reading lands on a thesis
with a sharper edge than any of them.

This repo is the elder Bidder's lattice with each of his three
design pillars actively negated. Aggregate closure refused while
local closure is kept exact. The log identity recovered at a
different altitude. Unique factorisation traded for K-indexed
random access. Not three relaxations — three concurrent
consequences of one design move (the choice of `M_n`), each
driven by one commitment, all in service of one goal.

**The commitment:** every `C_b(n)` is *absolutely* normal — normal
in every base, not just the base of concatenation, across all
`n ≥ 2` and all `b ≥ 2`.

**The goal:** have an open project whose central claim cannot be
imported from a setting where the analogue is already settled.
Copeland–Erdős (1946) settles base-`b` normality of `C_b(n)` (see
§"What Copeland–Erdős Settles" below); the commitment is to the
harder claim, which is open even for the simplest constructively
defined reals (classical Champernowne, π, e — none have proven
absolute normality).

**The edge:** we don't expect to prove the commitment. The
substrate-side route we know to attempt — closing the residuals
the substrate exposes — runs through structures whose extension
to bases `B ≠ b` we don't see. We don't see how alternative
routes (Weyl, ergodic, sieve) close either. The undecidability
we appeal to is internal: a stance about what the sum of what we
see and don't see lets through, not a Gödel-style theorem of
impossibility.

The bilingualism is the engine of the investigation. Whether it
is also the *obstruction* to proof is something we cannot claim
from `N = 1`. π, e, and classical Champernowne all have open
absolute-normality questions and no bilingual structure;
absolute normality is hard regardless. Bilingualism may be
doing real obstruction work in our case, or it may be
decorative — the evidence to discriminate isn't yet in.

**The stakes.** If the commitment is wrong — if every `C_b(n)`
is provably absolutely normal — the construction is not just
"another constructive absolute normal." Becher–Figueira (2002)
and Becher–Heiber–Slaman (2013) and successors give computable
absolute normals with polynomial-time digit oracles, in
parameterised families. The literature is not empty.

What would be unusual about ACM-Champernowne is **a family
designed for something else** — Hardy random access on
n-primes, finite-rank `Q_n` local algebra, the substrate's
residual structure as investigative tool — **turning out to be
absolutely normal as a side effect**. If the side effect proves
out, the substrate's machinery (finite, indexable, with `O(1)`
digit oracle and factorisation by construction) ports with not
much modification to adjacent hard problems: factoring, points
on curves, structured arithmetic on indexed lattices. That is
the backstop stake. Not "no one has produced absolute normals"
— they have. *Closing this with machinery designed for
substrate investigation gives us a transferable method.* The
little black box in *Sneakers* — too useful for its setting —
but the relevant adjacency is "what else can the substrate
touch?" not "what is missing from the absolute-normality
literature?" The manifesto is a bet that we have not built a
transferable substrate-investigation method without realising it.

*Note on genre.* This is a manifesto. The structural argument
that follows orients work; it does not prove unprovability. The
arguments are about why the project expects absolute normality
of the family `{C_b(n)}` to remain open under the construction's
design, not about why it is logically impossible to prove.

This is the flaw, and the foundation. The project commits to a
claim it does not expect to verify. Every result in `arguments/*`
lives in the gap between that commitment and anything we can
prove. The gap is the work.

`sources/BIDDER-AND-SON.md` documents the elder Bidder navigating
toward a target by perceiving its nearest factorable composite and
absorbing the residual into a calibrated correction table. He
delivered eight-place mental logarithms in under four minutes by a
method that *required* closure, leaned on UFD, and used the
numerical log identity as its central tool. We use the same lattice
of multiplicative anatomy. We need the opposite of all three.


## The Object

The elder Bidder's method, as `sources/BIDDER-AND-SON.md` records it,
rests on three operating pillars in tension with one binding goal —
deliver an eight-decimal number for arbitrary integer input,
mentally:

1. **Closure.** Every problem terminates at a calibrated number.
   No tails, no asymptotics, no "approximately X with `O(b^{−k})`
   correction." Mental arithmetic with public verifiability requires
   a final digit answer.
2. **The log identity** `log(ab) = log(a) + log(b)`. The unique
   transformation that converts an unbounded multiplicative target
   space into an additive one reachable by a finite library of
   memorised constants.
3. **Unique factorisation of the integers.** Z is UFD; primes are
   canonical generators; any composite has a unique decomposition
   into memorised prime logs. The library *spans* the problem
   space because UFD gives it a canonical reduction path.

Remove any one and the method falls apart. He designed exactly
around these three.


## Grand

The repo negates each of the three. The negations are not
relaxations — each is a positive design choice driven by what the
project is for, not a passive absence of his constraint. They
cohere because they answer one question together: how do you build
a substrate that admits investigation of a claim you cannot prove?

- **Closure: refused.** `core/FINITE-RANK-EXPANSION.md` enforces
  the refusal at the right altitude. Each `Q_n(m)` is an exact
  rational with denominator dividing `h!`, the Mercator series
  truncating at `j = ν_n(m)`:

      Q_n(m) = [m^{−s}] log(1 + n^{−s} ζ(s))
             = Σ_{j=1}^{ν_n(m)} (−1)^{j−1} τ_j(m / n^j) / j.

  Local closure is sharp — no remainder, no asymptotic. *Aggregate*
  observables don't close: the CF expansion of `C_b(n)` carries
  `O(b^{−k})` tails, the off-spike denominator process is
  unmodelled, the multiplication-table residual at finite `K` is
  unpinned. Local rigor, global open-endedness, in deliberate
  partition. The aggregate has to stay open because the aggregate
  *is* `C_b(n)`'s digit stream — and `C_b(n)` is normal, which
  means the digit stream cannot be sealed off.

- **Log identity: recovered, at higher altitude.** Bidder's
  `log(ab) = log(a) + log(b)` operates on numerical pairs and
  collapses to one term per factor. We need an identity that
  operates on a non-UFD generating function and doesn't collapse
  too far. Mercator on `1 + n^{−s} ζ(s)` is what the math gives:
  same multiplicative-to-additive work, but at the
  generating-function altitude where the absence of an Euler
  product over `M_n` atoms doesn't break the expansion. The
  recovered identity has a different signature — `h = ν_n(m)`
  terms per `m`, not one — and the visible finite-rank-h stack in
  `Q_n` is its fingerprint. Bidder's identity at this altitude
  would over-collapse; ours has just enough terms to carry the
  local structure without erasing it.

- **UFD: traded for K-indexed random access.** `M_n = {1} ∪ nZ_{>0}`
  is built non-UFD: `36 = 6 · 6 = 2 · 18` in `M_2`. The same
  deletion rule that makes the monoid non-UFD makes its atoms
  indexable: after dividing by `n`, the cofactors are positive
  integers with one residue class deleted per period of `n`. That
  shape is exactly Hardy's

      c_K = qn + r + 1,   (q, r) = divmod(K − 1, n − 1).

  One mod-arithmetic line. The trade is concurrent, not causal:
  changing the monoid both discards unique factorisation and
  exposes the arithmetic progression that one divmod inverts. UFD
  for Hardy. UFD for the bilingual K-indexing that ties atom
  position to digit position in `C_b(n)`. UFD for the substrate
  visibility that lets us render at scale. Bidder's problem space
  is UFD by gift of the integers; ours is non-UFD by construction.

The three negations cohere because they are *concurrent
consequences of one design move*: the choice of `M_n = {1} ∪ nZ_{>0}`.
That single move discards UFD; exposes the arithmetic progression
Hardy inverts; carries `ζ_{M_n}(s) = 1 + n^{−s} ζ(s)` as the
generating function whose Mercator log gives the recovered
identity; and forces the local-vs-aggregate altitude split that
makes closure refusal coherent. The triadic framing is
pedagogically useful — three things to think about, three trades
to name — but the algebra is one move that has three concurrent
consequences. Closure refused: so the residuals stay open and the
central claim stays in play. Log identity recovered: so local
structure is exact while the aggregate stays unsealed. UFD traded:
so the substrate is *visible* — indexable, plottable, reachable
by mod arithmetic. Together they build a substrate where the
family `{C_b(n)}` is an object you can study without expecting
to prove the absolute-normality claim that motivates the studying.


## Mundane

Same five mechanisms as Bidder's method. Each is the negation of
the corresponding Bidderian choice. The mechanics are real — this
is the same multiplicative anatomy doing the same kind of
structural work — but every term has been replaced.

| mechanism | Bidder | repo (negation) |
|---|---|---|
| **latticework** | memorised prime logs (~25 constants) | generated atoms `n · c` with `n ∤ c`, accessed by index |
| **random access** | perception of factorability ("natural instinct") | `c_K = qn + r + 1`, one mod-arithmetic line |
| **log identity** | `log(ab) = log(a) + log(b)` on numerical pairs | Mercator on `1 + n^{−s} ζ(s)`, generating-function altitude |
| **residual mechanism** | scalar correction table (`log(1.001), log(1.0001), …`) | family classifications (`offset(n)` by `ord(b, n)`, `O(b^{−k})` tails, spread bound `≤ 2`) |
| **helper multipliers** | `× 13` to land target near a factorable composite | `M_n / M_Ford` to expose density `α_n = (n − 1)/n`; `T_k − 2 L_{k−1}` to substitute substrate-naive denominator |

Each row reads as a same-mechanism / opposite-direction pair.
Bidder's residuals are scalars to absorb at the end; ours are
families to classify and leave open. Bidder's helpers move the
target toward a known landmark; ours expose structure that the
substrate-naive prediction misses. Bidder's random access is
cognitive; ours is mechanical. The mechanism survives the inversion
at every row.


## Beautiful

Three features cut.

1. **Local rigor enables global open-endedness.**
   `FINITE-RANK-EXPANSION.md` is the project's quietest theorem —
   one line of integer divisibility — and its loudest enabling
   move. Each `Q_n(m)` closes exactly at rank `h = ν_n(m)`. That
   local closure makes aggregate openness a *meaningful* problem
   rather than a measurement defect. Were `Q_n` itself an
   asymptotic, the aggregate non-closure would be sloppiness;
   because `Q_n` is rationally exact, failures to close are
   forced into the coupling layer where the central question
   lives. The local ledger tells us where not to blame the error.
   The aggregate stays open by *design*, not by accident.

2. **The recovered log identity has a different signature than
   Bidder's.** His collapses to one term per factor; ours
   collapses to `h = ν_n(m)` terms per `m`. The "finite rank"
   isn't a free parameter — it's the count of Mercator terms
   that survive truncation by integer divisibility on the
   non-UFD monoid. Read backward: the visible finite-rank-h
   stack in `Q_n` is *evidence* that we recovered a different
   identity, since Bidder's would have produced a different
   stack. The identity is doing the work; the rank stack is its
   fingerprint, the `(n − 1)/n²` density is its scalar trace,
   `α_n = (n − 1)/n` is its mark on Ford-image-counting.

3. **The bilingual K-indexing makes residuals renderable.** Bidder
   kept his correction table in his head — a few dozen scalars at
   fixed multiplicative scales (`1.01, 1.001, 1.0001`). He could
   imagine residuals slice by slice; he could not *see* the
   residual surface across his lattice. The repo can render. Open
   `experiments/acm-champernowne/base2/disparity/detrended_rds_curves.png`:
   the running digital sum of `C_2(n)` versus the closed-form
   expected drift, plotted across `v_2(n) ∈ {0, …, 8}` in fourteen
   panels. Each blue wobble around the red substrate-naive
   prediction *is* the residual surface — the structure Bidder's
   correction table tried to absorb scalar-by-scalar, displayed
   surface-by-surface across the substrate. The Hardy indexing
   gained with the `M_n` move is what permits the rendering: the
   atom stream behind `C_b(n)` is termwise indexable at any `K`,
   plottable across `n`, comparable across `v_2(n)`. The
   matplotlib output is what the inversion buys — not a proof of
   normality, but a *substitute* for one. We navigate residual
   surfaces because we cannot collapse them.

These three together describe what the negations let through.
Local rigor, identity-signature, and renderability are downstream
of refused closure, recovered identity, and the UFD trade
respectively. Each Beautiful feature is the productive face of
the corresponding negation.


## What Copeland–Erdős Settles

Copeland and Erdős (1946) proved: for any increasing sequence
of positive integers `(a_k)` with `π_A(N) > N^{1−ε}` eventually
for every `ε > 0`, the real number

    α_A(b) = 0.a_1 a_2 a_3 …    (concatenation in base `b`)

is normal in base `b`. The headline application is the prime
concatenation `0.235711131719…`, whose normality in any base
follows from the prime number theorem.

The ACM n-prime sequence at any prime `n` has density
`(n − 1)/n²` in the integers. Linear in `N`; the C–E density
condition is satisfied trivially. **C–E directly proves: `C_b(n)`
is normal in base `b`, for every prime `n` and every base `b ≥ 2`.**

This is a theorem from 1946. It is not on the project's open
list. It is on its load-bearing list, and the project stands on
it. The substrate transparency catalogued in `arguments/*`
describes the *internal structure* of an object whose first-order
normality has been settled for eighty years. See
`sources/COPELAND-ERDOS.md` for the theorem statement and proof
sketch in this project's notation.

What C–E does *not* settle:

- **Absolute normality.** Normal in *every* base, not just the
  base of concatenation. Classical Champernowne is normal in
  base 10 (Champernowne 1933; recovered by C–E 1946); its
  normality in any base ≠ 10 is *open*. ACM-Champernowne
  inherits the same gap: `C_b(n)` is normal in base `b` (proved),
  normality in other bases (open). The empirical observation
  in this project that some CF behaviours are less problematic
  read in bases ≠ `b` is consistent with absolute normality
  being structurally non-trivial, base by base.

- **Refined digit-distribution statistics.** Multi-scale
  correlations, entropy bounds, normality at arbitrary block
  scales. Beyond the `b^{−k}`-frequency claim of C–E.

- **CF behaviour and irrationality measure.** Already conditional
  in `experiments/acm-flow/cf/MU-CONDITIONAL.md`. C–E does not
  address.

- **Substrate-specific structure.** The work in `arguments/*` and
  the empirical phases. C–E does not address.

The project's commitment, refined: **every ACM-Champernowne real
`C_b(n)` is absolutely normal.** Stronger than what C–E delivers.
Open even for the simplest constructively defined reals (classical
Champernowne, π, e — none have proven absolute normality).


## The Undecidable Heart

An *absolute* normality proof for `C_b(n)` would need to show:
for every base `B ≥ 2`, every length-`k` digit string in base `B`
occurs in the base-`B` expansion of `C_b(n)` at frequency
`B^{−k}`, in the limit. C–E gives this for `B = b` (the base of
concatenation). Other bases `B ≠ b` have to be earned separately.

We do not claim the residual list below is the gate any
absolute-normality proof must pass through. The substrate is the
project's *investigative tool* — Hardy-indexed atoms, finite-rank
`Q_n`, BLOCK-UNIFORMITY's residue counting, the bilingual
K-indexing that ties atom position to digit position. The
substrate's output, when used as a tool, is a catalog of residual
structure:

- `offset(n)` by `ord(b, n)` (intermediate `ord` open in
  `PRIMITIVE-ROOT-FINDING.md`),
- `β(n)` for the `O(b^{−k})` tails (per-`n`, currently
  uncharacterised),
- the off-spike denominator process between consecutive boundary
  spikes (load-bearing in `MEGA-SPIKE.md` step 3 and the premise
  of `MU-CONDITIONAL.md`),
- the lucky-cancellation locus in `BLOCK-UNIFORMITY` (22 205
  triples in `b ≤ 12, d ≤ 5`, no rule known).

The catalog is what we see when we use the substrate. It is not
claimed as the unique route to proof; it is what the substrate
exposes, and what we have organised.

What we do claim: the substrate's *organisation of complexity*
is the differentia. Other constructs over the integers have
residues — random sequences, generic concatenations, sparse-
density collections — but they don't structure them like this.
The project's residuals have visible families, base-dependent
classifications, and substrate-side closed forms at the local
level. That kind of organisation is what makes the substrate
useful as an investigative tool, and (we expect) useful for
projects beyond this one. Other constructs have residues; ours
*structures* them.

What we don't see: a route from the catalog to an
absolute-normality proof. The catalog organises complexity
visibly across `(n, b, d)` *for the base of concatenation*; its
direct extension to bases `B ≠ b` runs through substrate
quantities that don't carry across base in any obvious way. The
`Q_n` local algebra is base-agnostic in its definition, but its
consequences for digit-distribution in non-concatenation bases
require new substrate work the project has not done. We don't
see how that work concludes.

What other routes might do — Weyl-style equidistribution across
multiple bases simultaneously, ergodic arguments on the
concatenation map, exponential-sum bounds, sieve identities
adapted to non-UF monoids — is open. Each could in principle
bypass the substrate catalog. We don't see how. We acknowledge
we haven't shown no one will.

The unprovability claim is a stance about what the sum of what
we see and don't see lets through. The substrate exposes
complexity in a way other constructs over the integers do not;
the catalog is what the project produces; the absence of any
visible route — substrate-side or otherwise — is what the bet
is grounded in. Not "the catalog is the gate." Not "we have
shown no other route can succeed." Just: this is what we have,
this is what we don't see, and the gap between them is what we
expect to remain.

The undecidability is not Gödel-incompleteness. There is no
formal theory whose axioms are independent. It is structural: a
stance about the construction's design and the absence of any
visible proof route, not a theorem about what no proof can do.

`C_b(n)` is computable, in the formal sense — there is a finite
algorithm that emits its `n`-th digit. The digit stream is
generated by Hardy + Champernowne concatenation; nothing about
its existence is in question. What we conjecture cannot be
proven, structurally and (we expect) permanently, is the
*absolute-normality claim* across the family `{C_b(n) : n ≥ 2,
b ≥ 2}`. We have the numbers; we don't expect to prove what
their digits do across all bases in the limit.

### The cheat code

If we are wrong — if every `C_b(n)` is provably absolutely normal
— the construction is *not just* "another constructive absolute
normal." Sierpiński (1917), Stoneham (1973), Becher–Figueira
(2002), Becher–Heiber–Slaman (2013), and successors have produced
computable absolute normals with explicit constructions and, in
some cases, polynomial-time digit oracles. There are
parameterised families. The literature is not empty.

What would be unusual about ACM-Champernowne is *not* "a
parameterised family of absolute normals exists." It is **a
family whose substrate machinery was built for substrate
investigation** — Hardy random access on n-primes, finite-rank
`Q_n` local algebra, the residual structure as a tool — turning
out to be absolutely normal in the bargain. If absolute normality
of every member proves out, we expect the substrate's machinery
(finite, indexable, with `O(1)` digit oracle and factorisation
by construction) would port with not much modification to
adjacent hard problems: factoring in residue classes, points on
curves, structured arithmetic on indexed lattices. We have not
demonstrated the porting; we are reading the shape of the
machinery and saying what it looks positioned to do. The substrate
would become a transferable investigation method, not just an
absolute-normality producer.

That is the backstop stake. Not "no one has produced
parameterised absolute normals" — they have. **Closing this with
machinery designed for substrate investigation gives us a
transferable method.** The little black box from *Sneakers* —
too useful for its setting — but the relevant adjacency is
"what else can the substrate touch?" not "what is missing from
the absolute-normality literature?" The manifesto's commitment
to unprovability is equivalently a commitment that we have not
built such a transferable method without realising it.

This is the flaw. It is also why the substrate is worth
investigating. If `C_b(n)` were classical-provably absolutely
normal, the three concurrent consequences of the `M_n` move
would still be present — but the substrate's role would
collapse from "investigative tool exposing complexity that
proof cannot reach" to "tool whose machinery is also a proof
of absolute normality, and presumably of more besides." The
first creates an open project. The second creates a transferable
method we did not set out to build. We bet on the first.

The unprovability creates the open structure for the substrate-
driven investigation to populate. Every residual classification,
every closed-form spike formula, every renderable disparity
surface lives in the gap between the commitment and the missing
proof. The four-ways arguments in `arguments/*` catalogue what
occupies the gap.


## Contingent

Most of what reads as Bidder-specific in `BIDDER-AND-SON.md` is
contingent — and so is its analog in this repo.

- **Bidder's specific stored constants** (`log(2), log(3), …`,
  `log(1.01) = 0.0043214`, …). The repo's analog: the specific
  n-panel `{2, 3, 4, 5, 6, 10}`, the specific base `b = 10` cited
  everywhere, the specific Phase numbering. Both are contingent
  on what the practitioner happened to memorise / compute. The
  three-negation claim survives both contingencies.

- **Bidder's helper multipliers** (`× 3, × 7, × 13`). Choices
  whose pedagogical clarity exceeds their structural necessity.
  The repo's analogs (the d=4 cf panel, the ratio-vs-Ford framing
  in mult-table) have the same status — chosen because they
  happen to work, not because the math demanded them.

- **Bidder's "natural instinct" framing.** He considered the
  perception of factorability innate and unteachable. The repo's
  most direct answer is to formalise its own analog: Hardy's
  `c_K = qn + r + 1` is the perception of where the next atom
  sits, written down. The "BIDDER blindness" pattern in
  `core/ABDUCTIVE-KEY.md` and
  `experiments/math/hardy/SURPRISING-DEEP-KEY.md` records every
  time an agent in this repo took an instinct-shaped detour
  around a fact that Hardy already provides for free.

- **The "BIDDER" cipher's naming.** Named after the elder Bidder,
  but the cipher itself is son-shaped — fixed-block bijection,
  uniform across input, target-indifferent. The mathematical work
  on the cipher's substrate is elder-shaped. The naming captures
  the family pedigree; the methodological inheritance is split.

The metaphysical commitment to normality is *not* contingent in
the same sense; see §"The Undecidable Heart." A different
practitioner could work this substrate with a different stance
— believing `C_b(n)` rational, or agnostic — and the math
underneath would be unchanged. But the negation framework is
what makes the *commitment* worth holding in the first place.
Drop the commitment and the project becomes recreational; keep
the commitment and the project becomes the investigation of an
object whose central truth resists proof.


## Father and Son in this Lens

The repo is not purely the elder Bidder. The structural work — each
derived observable (`Q_n`, the spike formula, off-spike denominator)
being its own navigation with its own residual classification — is
elder-shaped. The analytic closed forms — `BLOCK-UNIFORMITY`'s
smooth lemma, the spike formula's universal `log_b(b/(b−1))`, the
conditional `μ = 2 + (b − 1)(b − 2)/b` — are son-shaped: uniform
across the target space, indifferent to which `(n, b)` you pick.

The three-negation framing applies most cleanly to the elder's
content. The son's contribution survives the negations unchanged:
his multi-scale uniform decomposition is already a substrate-driven
approach, not a target-driven one, and his method passes through
the inversion intact. So the project's son-shaped pieces (closed-
form lemmas) are *contiguous* with his work; the elder-shaped
pieces are the *inversion* of his.

The cipher is purely son-shaped. The mathematical project blends.
The three negations are how the elder's content gets inverted; the
son's content joins the project without needing inversion at all.


## Where the Lens Predicts to Look

Bidder's hard cases predict the repo's open frontiers under the
inversion. Each is a *site of the undecidability* — a place where
proof would require closing what the substrate refuses to close.

- **Off-spike denominator process** (`MEGA-SPIKE.md` step 3,
  `MU-CONDITIONAL.md` premise). Bidder's "no nearby landmark"
  case in CF coordinates. He responded with helper multipliers
  to transform the target into one near a landmark. The repo's
  analog is the off-spike CF state between consecutive boundary
  spikes, currently unmodelled. The "spikes dominate" conditional
  in `MU-CONDITIONAL.md` is asking whether helper multipliers
  exist for this case — equivalently, whether the off-spike
  denominator admits a substrate-side description that would
  close its contribution to the digit-frequency aggregate.

- **Intermediate-ord primes** (`PRIMITIVE-ROOT-FINDING.md`,
  `n ∈ {13, 23, 31}` at `b = 10`). Targets where the residual
  classification (Family A / B / D / F) doesn't apply at the
  resolution probed. Bidder's analog: a target in a sparse region
  of multiplicative space where no landmark is close enough.
  Whether higher `k` resolves these into a third family or
  whether the sparseness is real is exactly Bidder's question:
  do better helpers exist for these targets, or are they outside
  the residual-table coverage?

- **Lucky-cancellation triples** (`BLOCK-UNIFORMITY.md`, 22 205
  triples in `b ≤ 12, d ≤ 5` outside both sufficient families).
  Bidder's analog: targets that happen to factor cleanly without
  obvious reason. The unifying characterisation is open in both
  directions — Bidder couldn't articulate his perception, the
  repo cannot yet articulate the cancellation. Both are hints
  that the substrate's residual structure has more to give.

Each is a site where the substrate exposes structure we don't
see how to close. We don't claim closing all three is what an
absolute-normality proof requires — §The Undecidable Heart
disclaims the residual list as a gate. We claim each is a
place the substrate's investigative tool shows complexity that
we cannot reduce. The lens predicts that work in this repo
will make progress on each, and *will not finish any* in a way
that propagates across bases. The pattern of progress and
non-finishing across the three is part of what the manifesto's
bet rests on: this is what the substrate exposes, this is
what we cannot close, and the gap is what we expect to
remain. We don't claim foreclosure of alternative routes.


## One-Line Summary

The repo is the elder Bidder's lattice with each of his three
design pillars actively negated, the three concurrent consequences
of one move (the choice of `M_n`). Aggregate closure refused
while local closure stays exact (`Q_n(m) = Σ_{j=1}^{ν_n(m)}
(−1)^{j−1} τ_j(m/n^j)/j` is exact rational; the CF expansion's
`O(b^{−k})` tails stay open). Log identity recovered at the
generating-function altitude — Mercator on `1 + n^{−s} ζ(s)`
where Bidder used `log(ab) = log(a) + log(b)` on numerical pairs.
Unique factorisation traded for K-indexed random access — the
`M_n` move both destroys UFD and exposes Hardy's
`c_K = qn + r + 1` as a one-divmod inverse.

One commitment, one consequence:

- **Commitment.** Every `C_b(n)` is *absolutely* normal — across
  all bases, all `n ≥ 2`, all `b ≥ 2`. C–E (1946) settles the
  base-`b` case for free; the manifesto's commitment is to the
  harder claim, open even for classical Champernowne.
- **Consequence.** We don't expect to prove it. The substrate is
  the project's investigative tool; the catalog of residuals it
  surfaces is what we have, not the gate any proof must pass
  through. We don't see how the catalog extends to bases `B ≠ b`,
  and we don't see how alternative routes (Weyl, ergodic, sieve)
  close either. We don't show no route exists; we say what we see
  and don't see. If a proof is found, the substrate's machinery —
  designed for Hardy indexing on n-primes, not for absolute-
  normality production — would have produced absolute normals as
  a side effect, and the same machinery would port to adjacent
  hard problems (factoring, curves) with not much modification.
  The manifesto is a bet, taken seriously, that we have not built
  a transferable substrate-investigation method without realising
  it.

The substrate transparency catalogued in `arguments/*` is what
the three concurrent consequences of the `M_n` move let through;
the matplotlib renderings of residual surfaces are what the
substrate transparency permits. Bidder kept his correction table
in his head and absorbed residuals scalar-by-scalar; we render
them surface-by-surface across `(n, b, d)`. We render because we
cannot close. We navigate the substrate because we cannot prove
the claim that motivates the work. The flaw is the foundation.
