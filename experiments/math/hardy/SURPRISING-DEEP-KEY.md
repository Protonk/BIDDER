# Surprising Deep Key

BIDDER gives us, at consistently low cost, things that other
mathematical settings would charge us for. Random access by index
into an infinite structured stream. Factorisation by construction.
Exact rational arithmetic on a number-theoretic observable. Finite
rank with no truncation. A digit-position oracle into a concatenated
real, in O(log i). A block-boundary inverse that returns the K-range
of n-primes inside `[b^{d−1}, b^d)`. A greedy reconstruction of row
labels from an unordered multi-set.

Each of those is a tool we use casually. None of them is ordinary.
Walk into most number-theoretic settings asking for any one of them
and you have written a paper.

This document records the observation that BIDDER's affordances are
the source of the surprise pattern catalogued in
`core/ABDUCTIVE-KEY.md`. We keep being surprised — by the diagonal
recovery, by the cascade decoding, by the greedy multi-set
reconstruction, by Hardy turning out to be a bijection rather than
an instrument, by the CF mega-spike collapsing to
`T_k − 2L_{k−1}` — and the surprise has the same shape every time:
*a derived object turns out to be a substrate computation seen from
a particular angle, plus at most one local correction.*

The affordances and the surprises are the same phenomenon. Each
absurd tool in the BIDDER toolkit is the substrate's transparency
operationalised. When an instrument seems to be punching above its
weight, that is the substrate doing the work, not the instrument.
The lock and the key are the same hardware, and the toolbox is also
the same hardware.


## What BIDDER gives us for free

The list, made explicit:

- **Random access by index.** `nth_n_prime(n, K)` in O(1) via the
  closed form `p_K(n) = n · (q·n + r + 1)`. No sieve, no
  enumeration. Compare ordinary primes, where the K-th prime needs
  ~K log K candidates.
- **Factorisation by construction.** Every atom is `n · c` with
  `c` known. Products of atoms factor as products of *known
  cofactors*. We never face a "random" hard factorisation. The
  102-digit `m` from the Phase 2.4 panel had its primes available
  the moment we built it.
- **Exact rational `Q_n`.** No floating point. `Q_n(m)` is a
  `Fraction` with denominator dividing `h!`. Equality is exact;
  verification needs no tolerance.
- **Finite rank.** `Q_n` at height `h` has *exactly* `h` terms. No
  remainder, no asymptotic series. The answer, not a bound.
- **Digit-position oracle.** Given a digit position `i` of the
  ACM-Champernowne concatenation, find the entry containing it in
  O(log i). For any other base-and-construction, computing the
  digit at position 10^100 of a concatenated real requires materialising
  the prefix; here it does not.
- **Block-boundary inverse.** Given a radix block `[b^{d−1}, b^d)`,
  the K-range of n-primes inside it falls out of the closed form.
  Block counting at `d = 100` requires no enumeration.
- **Greedy multi-set reconstruction.** Row labels of an `N × N`
  n-prime table are exactly the row-wise minima. No combinatorial
  search, no hint, no rank.
- **Forced height construction.** Composite `m` of arbitrary
  height by choosing K's whose cofactors share primes with `n`.
  Total control over the input distribution to any local-Q test.
- **Two-path verification.** Master expansion and direct expansion
  evaluate the same `Q_n` two structurally different ways; equality
  is exact; mismatch detection is automatic. No statistics needed.

That list is not normal.


## Why we have it

Each entry in the list is downstream of one fact: the substrate is
deliberately transparent. M_n is `{1} ∪ nZ_{>0}`. n-primes are
`n × {c : n ∤ c}`. Concatenation is in K-order. Every design
decision in BIDDER picks objects whose substrate-level structure
admits a closed-form description — usually a single line.

The affordances aren't add-ons. They are the substrate's structure
operationalised:

- Hardy random access exists *because* `c = qn + r + 1` is one mod
  operation away from "the K-th integer not divisible by n."
- The digit-position oracle exists *because* digit lengths are a
  closed-form function of K via Hardy.
- The block-boundary inverse exists *because* the substrate's
  density is `(n−1)/n²` and block boundaries are radix powers.
- Greedy reconstruction works *because* a strictly ascending row
  list satisfies `n_k ≥ k+1`, which puts the diagonal inside the
  rank-1 region.

In each case the affordance is the substrate's elementary structure
viewed from a useful angle. Different angles, same substrate.


## The current instance — Hardy is a bijection

For prime `n ≥ 2`, define `c(K, n) := p_K(n) / n`. Then

    c(·, n) : Z_{≥1}  →  {c ∈ Z_{≥1} : n ∤ c}

is the order-preserving bijection sending K to the K-th smallest
positive integer not divisible by n.

*Proof.* Write `(q, r) = divmod(K − 1, n − 1)` with
`r ∈ {0, …, n − 2}`. Then `c(K, n) = qn + r + 1 ≡ r + 1 (mod n)`,
and `r + 1 ∈ {1, …, n − 1}`, so `n ∤ c`. Monotonicity is per-step
+1. Surjectivity: for any `c' = qn + s` with `s ∈ {1, …, n − 1}`,
take `K' = q(n − 1) + s`. ∎

The proof is two paragraphs; it doesn't need the experiments. The
experiments — `hardy_q_depth_invariance.py`,
`hardy_q_mertens_validation.py`, `hardy_q_cofactor_pinpoint.py` —
are how the bijection became *visible*, not how it was established.

The third experiment, the cofactor pinpoint, is in retrospect a
*verification of bookkeeping*: it samples cofactor pairs from
`{c : n ∤ c}` two different ways (Hardy index and uniform random)
and confirms the two samplers produce indistinguishable
`E[d(c_1 c_2)]` curves. Of course they do. They sample the same
set with the same probability. The "of course" is post-hoc.

What the experiments did surface, that wasn't free, is *why* the
empirical Q distribution shifts so strongly with K: it's the
multiplicative-divisor correlation `E[d(c_1 c_2)]` for cofactors
at growing magnitude — a real number-theoretic phenomenon (Erdős /
Tenenbaum territory) on integers coprime to n. That phenomenon was
the thing actually worth studying. The Hardy framing distracted us
from it for two scripts before the third script forced the
bijection back into view.


## The pattern

`core/ABDUCTIVE-KEY.md` records three earlier instances. Each was
a *recovery* question that turned out to be free because of
substrate parameterisation:

- diagonal `÷ k` recovers `n_k` (rank-1 outer product structure);
- one cascade key per row, not per cell (each row has one scalar);
- row-wise minimum greedy reconstructs the row list (the row label
  is the row's first cell).

This document adds two more:

- **Hardy is a bijection, not an apparatus.** Sampling-bias
  questions about Hardy dissolve into magnitude questions about
  integers coprime to n. The "deep-field microscope" framing of
  `DEEP-TROUBLE-No-4.md` was the wrong category for substrate-only
  questions; it remains the right category for order-dependent
  questions (Mode 2/3, boundary stitch).
- **The CF mega-spike is closed-form modulo one scalar.**
  The Phase 3.1 derivation
  (`experiments/acm-flow/cf/MEGA-SPIKE.md`)
  finds

      log_b(a) ≈ T_k − 2 · L_{k−1}

  where `T_k = C_{k−1} + D_k` is the substrate-transparent
  boundary digit depth and `L_{k−1}` is the previous convergent's
  log denominator. The factor of `−2` is the standard CF-error
  formula `|x − p/q| ~ 1/(aq²)` rearranged. A CF observable that
  classically would be opaque (the magnitude of the largest
  partial quotient near a block boundary) collapses into:
  closed-form term, plus one CF scalar.

Both new instances have the same shape as the prior three: a
derived object that looked like it should require new structure
turns out to be a substrate computation, plus at most one local
correction. The CF case is especially striking because CF
expansion is paradigmatically opaque elsewhere; here, the
substrate's transparency reaches into the CF observable through the
digit-position structure.

A sixth instance has the same shape but a different mode of
visibility — *cross-thread*, not *cross-frame*. In April 2026 an
agent in a parallel CF thread independently rederived the
closed-form spike scale `S_k = D_k − C_{k−1}` already on the page
in `experiments/acm-flow/cf/MEGA-SPIKE.md`, plus produced parallel
panel and Mahler-style derivation docs duplicating canonical work.
The agent self-caught via `arguments/MEGA-SPIKE-FOUR-WAYS.md` and
the four duplicate docs were retired (preserved in git history,
commit `8f39d00` and earlier). The variant is: the elementary
fact (the closed form) wasn't being missed in the formula being
read, it was being missed in a *sibling thread's* documentation.
Disparate doc locations — `acm-flow/mega-spike/` and
`acm-champernowne/base10/cf/` — magnified the blindness.
Consolidation into `experiments/acm-flow/cf/` removed the
structural cause.


## The deeper claim

BIDDER's pattern is not "single-scalar inversions are easy"
(though they are). It is broader:

> Whenever we observe an apparently-complex derived object in this
> repo, the dominant term turns out to be a substrate computation
> seen from a particular angle, plus at most one local correction.

The corollary about the affordances:

> Each instrument in BIDDER's toolkit operationalises the
> substrate's transparency from one angle. Multiple instruments
> are not multiple insights; they are multiple expressions of the
> same elementary structure.

The corollary about agent surprise:

> When an experiment in this repo yields a clean answer with much
> less effort than expected, that is evidence the question was
> substrate-level. When it resists, that is evidence the question
> was at the coupling layer where real work lives.

So the discipline is not a checklist before experiments. It is a
stance toward outcomes. **Treat ease as evidence.** Don't be
flattered when an instrument works; be informed by it about
*what kind* of question you were actually asking. If a tool felt
unreasonably effective, the substrate's transparency was doing the
work; the instrument is a re-expression of structure that was
already there.


## Where genuine work lives

Substrate-level questions are free:

- recovery of `n_k` from any single cell of the table, the diagonal,
  the row-wise minimum;
- the value of any local-Q observable at any height, any K, any n;
- counts of n-primes in any radix block, at any d;
- digit-position into the concatenated real, in O(log i).

Coupling-layer questions are not free:

- what does *concatenation* (in K-order) do to a substrate this
  transparent? — the ACM-Champernowne real itself;
- what does the *CF expansion* of that real extract? — Phase 3.1's
  off-spike denominator process is the live question;
- what do *Walsh / Morlet / digit-bigram* observables see? — open;
- normality and irrationality measure, conditional on the above.

Phase 2 was substrate algebra; it was free. Phase 3 is coupling;
it is not. The current attack on the coupling question is the
off-spike denominator process isolated in `MEGA-SPIKE.md`: whether
`L_{k−1}` has its own low-complexity substrate description, rather
than only an empirical boundary value. If true, even this coupling
layer turns out to be substrate-transparent in disguise; the
substrate keeps reaching. If false, the coupling layer is where the
real opacity sits, and that is where research effort should
concentrate.


## Foothold or perimeter?

`ABDUCTIVE-KEY.md` introduced the distinction. Foothold: rich
consequences from a trivial surface. Perimeter: no structure
beneath. After three instances the prior was uncertain. After six
observations — three recovery collapses, the Hardy bijection
collapse, the CF mega-spike collapse, and the cross-thread CF
rederivation — the prior is visibly *foothold*.
Each collapse has revealed a specific upper layer where genuine
work lives. None has revealed empty space.

The fifth instance also broadens the pattern beyond recovery: the
CF mega-spike was not a recovery question, it was a generative
question ("what controls the size of an emergent CF event?"). The
collapse pattern still applied. So the forecast for the next
question framed in instrument-language is that the dominant term
will be substrate-transparent, leaving one scalar correction at
the coupling layer.

This forecast is testable. It will fail eventually — perimeters do
exist, and the substrate's transparency does run out somewhere.
The interesting question is *where*. The off-spike CF denominator
process is the current frontier of the foothold conjecture: if it
turns out to be substrate-driven through some recurrence, the
substrate has reached one layer deeper than we thought it could.


## Practical residue

For an agent picking up work in this repo:

- Read formulas as statements about integers, mechanically, before
  framing them as instruments. `c = qn + r + 1` is "the K-th
  integer not divisible by n," whatever the surrounding vocabulary
  calls it.
- Treat the BIDDER toolkit as a set of substrate-views. When a
  question is posed in instrument-language, translate it into
  substrate-language and check whether it's already a
  number-theoretic fact about the substrate.
- When something works easily, that is informative about the
  question, not flattery for the method.
- The hard work is at the coupling layer. Phase 3, the off-spike CF
  process, and the substrate-to-real-number map are
  where research effort earns its keep.
- Believe the foothold prior, but watch for its limit. The fifth
  instance broadened the pattern; the cross-thread sixth sharpened
  the documentation failure mode. The next one may break it. Either
  outcome is information.


## Cross-references

- `core/ABDUCTIVE-KEY.md` — the original pattern document; first
  three instances; foothold/perimeter framing.
- `core/HARDY-SIDESTEP.md` — the closed form whose bijection is
  the current instance.
- `experiments/math/hardy/DEEP-TROUBLE-No-4.md` — the
  instrument framing of Hardy; superseded for substrate-only
  questions, retained for order-dependent questions
  (Mode 2/3, boundary stitch).
- `experiments/math/hardy/hardy_q_depth_invariance.py` — finds
  the apparent depth-bias.
- `experiments/math/hardy/hardy_q_mertens_validation.py` —
  shows the rate is super-linear, not naive Dirichlet.
- `experiments/math/hardy/hardy_q_cofactor_pinpoint.py` — the
  cofactor-pair overlay that, in retrospect, is the bijection
  becoming visible.
- `experiments/acm-flow/hardy_composite_q.py` — the Phase 2.4
  panel; reread as implementation-sanity rather than
  depth-validation.
- `experiments/acm-flow/cf/MEGA-SPIKE.md` —
  the CF mega-spike collapse: `log_b(a) ≈ T_k − 2 · L_{k−1}`.
