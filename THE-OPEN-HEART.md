# The Open Heart

**The commitment:** every `C_b(n)` is *absolutely* normal — normal
in every base, not just the base of concatenation, across all
`n ≥ 2` and all `b ≥ 2`. We further submit it will remain open.

**What we made.** The family `{C_b(n) : n ≥ 2, b ≥ 2}`, each
formed by concatenating in K-order the atoms of
`M_n = {1} ∪ nZ_{>0}` written in base `b`. The atoms are `n · c`
with `n ∤ c`, accessible at any `K` via Hardy's
`c_K = qn + r + 1`. The K-index runs through the discrete lattice
(which atom) and through the digit stream (where in `C_b(n)`'s
base-`b` expansion that atom sits) at once: every atom has a
position in the lattice and a position in the digit stream,
either computable from the other in polylog bignum work. 

**What we see.** The substrate's algebra reads as binary-tree
structure walked by computation. `M_n` is non-UFD by construction
— `36 = 6 · 6 = 2 · 18` in `M_2` — so every non-atom carries a
tree of distinct atom factorisations, not a unique decomposition.
`Q_n(m) = Σ_{j=1}^{ν_n(m)} (−1)^{j−1} τ_j(m/n^j) / j` is the
signed count of ordered `j`-fold tree paths down to depth `j`,
alternating by parity, weighted `1/j`. The substrate's residual
catalog — `offset(n)` by `ord(b, n)`, `β(n)` for the `O(b^{−k})`
tails, the off-spike denominator process — is a cost ledger on
those traversals: what each path through the factorisation graph
pays in CF, mult-table, and digit-frequency coordinates. A
Turing machine walking a binary graph with costs metered along
the paths.


## The Foothold

`sources/BIDDER-AND-SON.md` documents the elder Bidder delivering
eight-place mental logarithms in under four minutes by navigating
to a target's nearest factorable composite and absorbing the
residual into a calibrated correction table. The method rests on
three operating pillars in tension with one binding goal —
deliver a calibrated number for arbitrary integer input,
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

He designed exactly around the cognitive constraints of mental
arithmetic — finite stored constants, bounded working memory,
public-verifiable answers in under four minutes.

## The Negation

The choice of `M_n = {1} ∪ nZ_{>0}` is one design move with three
concurrent consequences. It discards UFD; exposes the arithmetic
progression Hardy inverts; carries `ζ_{M_n}(s) = 1 + n^{−s} ζ(s)`
as the generating function whose Mercator log gives a recovered
identity at higher altitude; and forces the local-vs-aggregate
altitude split that makes closure refusal coherent. Bidder's
three pillars all break in that single move. The triad below is
pedagogical decoration; the algebra is one move.

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
  partition. C–E (1946) closes base-`b` normality of `C_b(n)`;
  what remains open at the aggregate is *cross-base* structure
  — absolute normality, refined digit statistics in bases
  `B ≠ b`, CF behaviour, irrationality measure. 

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
  `Q_n` is its fingerprint. 

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
  position to digit position in `C_b(n)`. 

The substrate the move builds is where `{C_b(n)}` lives.

## Beautiful

Three features cut.

1. **Local rigor enables global open-endedness.**
   `FINITE-RANK-EXPANSION.md` shows each `Q_n(m)` closes exactly at rank `h = ν_n(m)`. That
   local closure makes aggregate openness a *meaningful* problem.
   Because `Q_n` is rationally exact, failures to close are
   forced into the coupling layer where the central question
   lives. The local ledger tells us where not to blame the error.

2. **The recovered log identity has a different signature than
   Bidder's.** His collapses to one term per factor; ours
   collapses to `h = ν_n(m)` terms per `m`. The "finite rank"
   isn't a free parameter — it's the count of Mercator terms
   that survive truncation by integer divisibility on the
   non-UFD monoid. The visible finite-rank-h stack in `Q_n` is
   the identity's fingerprint — evidence we recovered a
   different identity, since Bidder's would have produced a
   different stack. The `(n − 1)/n²` density and
   `α_n = (n − 1)/n` are traces of the same `M_n` deletion rule
   that produced it — substrate-level, surfacing across
   BLOCK-UNIFORMITY, mult-table, and the cofactor-cycle slope
   at the same time.

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
   matplotlib output is what the inversion buys — a *substitute* for normality. 


## What Copeland–Erdős Settles

Copeland and Erdős (1946) proved: for any increasing sequence
of positive integers `(a_k)` with `π_A(N) > N^{1−ε}` eventually
for every `ε > 0`, the real number

    α_A(b) = 0.a_1 a_2 a_3 …    (concatenation in base `b`)

is normal in base `b`. The headline application is the prime
concatenation `0.235711131719…`, whose normality in any base
follows from the prime number theorem.

The ACM n-prime sequence at any `n ≥ 2` has density `(n − 1)/n²`
in the integers (whether `n` is prime, prime-power, or composite).
Linear in `N`; the C–E density condition is satisfied trivially.
**C–E directly proves: `C_b(n)` is normal in base `b`, for every
`n ≥ 2` and every base `b ≥ 2`.**

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


## The Algebra of Error

The substrate is an algebra. Its
elements are residuals — `offset(n)` indexed by `ord(b, n)`,
`β(n)` for the `O(b^{−k})` tails, the off-spike denominator
process between consecutive boundary spikes, the lucky-cancellation
locus in `BLOCK-UNIFORMITY`, and whatever further residuals the
catalog accrues. Its operations are the natural transformations
the substrate exposes across `(n, b, d)` — restriction in `n`,
shift in `b`, deepening in `d`, and the bilingual K-indexing that
ties an atom to its digit-stream position and back. Its closure
questions are this project's research questions.

Local closure is what the algebra finishes from inside. `Q_n(m)`
closes exactly at rank `h = ν_n(m)`; the closure is sharp,
rational, no remainder. The mult-table asymptote
`α_n = (n − 1)/n` is another local closure: a limit the algebra
reaches. The algebra has a notion of *finished* and several
local objects exhibit it.

Aggregate openness is what the algebra does not finish.
`C_b(n)`'s digit stream in bases `B ≠ b`, the cross-base
distribution of length-`k` strings, the irrationality measure,
the off-spike CF state — these are objects the algebra contains
but does not close. Absolute normality of `C_b(n)` across all
bases is one such closure question. The catalog of residuals is
the algebra's record of where it has not finished and what
finishing would mean.


## The Open Heart

![A circular disk filling most of a square frame on a black background. The disk's interior is rendered in deep magenta and purple tones overlaid with a network of bright orange-yellow lines. Two prominent perpendicular bright bars cross through the disk's centre forming an orange cross — one horizontal diameter, one vertical diameter. Beyond the central cross, the disk is filled with a curvilinear orthogonal grid: arcs that bend along the disk's curvature, growing denser and finer toward the disk's circumference. The grid is regular near the centre and compresses tightly at the rim, where the structure thickens into a fine textured band along the disk's boundary. No clear empty regions are visible; lines and intersections appear at every scale across the disk's interior. The four corners of the square frame outside the disk are pure black.](experiments/acm-champernowne/base10/art/q_distillery/q_lattice_4000_fft_poincare.png)

What got destroyed: linear scale (slog), spatial location (2D
FFT), phase information (magnitude only), and Euclidean geometry
(the Poincaré radial transform `r_disk = tanh(s · r_fft / 2)`).
Four orthogonal violences, each killing a different kind of
structure other constructs over the integers would have surrendered
to. The substrate's response is the image. The perpendicular
bright cross through the centre is the FFT's DC backbone —
first-order autocorrelation in `n` and `k` carrying through all
four transforms intact. The orthogonal arc grid filling the disk
is the Q-lattice's prime-harmonic content, surviving FFT as sharp
spectral lines and compressing toward the rim under the
hyperbolic distortion. The pattern repeats at every visible
scale: primary cross at the centre, secondary crosses radiating
out at smaller scales, the rim packed with the same grid finer
than itself. No thinning. No spectral flooding. The substrate
shows the same shape under every magnification because the shape
*is* the algebra. The open heart is what survives the
mauling.

An *absolute* normality proof for `C_b(n)` would need to show:
for every base `B ≥ 2`, every length-`k` digit string in base `B`
occurs in the base-`B` expansion of `C_b(n)` at frequency
`B^{−k}`, in the limit. C–E gives this for `B = b` (the base of
concatenation). Other bases `B ≠ b` have to be earned separately.

The catalog of residuals — what the algebra has not finished
closing — runs:

- `offset(n)` by `ord(b, n)` (intermediate `ord` open in
  `PRIMITIVE-ROOT-FINDING.md`),
- `β(n)` for the `O(b^{−k})` tails (per-`n`, currently
  uncharacterised),
- the off-spike denominator process between consecutive boundary
  spikes (load-bearing in `MEGA-SPIKE.md` step 3 and the premise
  of `MU-CONDITIONAL.md`),
- the lucky-cancellation locus in `BLOCK-UNIFORMITY` (22 205
  triples in `b ≤ 12, d ≤ 5`, no rule known).


## Claims

What we claim: the substrate organises its residuals into an
algebra. Other constructs over the integers have residues —
random sequences, generic concatenations, sparse-density
collections — but they don't expose them as algebra. The
project's residuals have visible families, base-dependent
classifications, and substrate-side closed forms at the local
level. No other constructive normal in the literature exposes
its residuals as algebra. Ours does. That algebra is what makes
the substrate useful for projects beyond this one.

What we don't see: a route from the catalog to an
absolute-normality proof. The catalog organises complexity
visibly across `(n, b, d)` *for the base of concatenation*; its
direct extension to bases `B ≠ b` runs through substrate
quantities that don't carry across base in any obvious way. The
`Q_n` local algebra is base-agnostic in its definition, but its
consequences for digit-distribution in non-concatenation bases
require new substrate work the project has not done. We don't
see how that work concludes.

`C_b(n)` is computable, in the formal sense — a finite algorithm
emits its `i`-th digit, generated by Hardy plus Champernowne
concatenation. The open claim, which we expect to remain open,
is *absolute normality* across the family `{C_b(n) : n ≥ 2,
b ≥ 2}`.


## Where the Lens Predicts to Look

Bidder's hard cases predict the repo's open frontiers under the
inversion. Each is a place the substrate exposes structure we
don't see how to close.

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

The lens predicts work in this repo will make progress on each,
and *will not finish any* in a way that propagates across bases.

## Coda

This document is not a theorem and does not pretend to be one.
It is closer to what Collingwood called magical: writing that
rouses to be put to work. The work it points at is writing down
the algebra it names.
