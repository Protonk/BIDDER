# Brief 2 / closed-form — spike-magnitude derivation

## ⚠️ STATUS UPDATE — superseded by the mega-spike thread

This brief was scoped as if the n-Champernowne CF spike closed form
were fresh territory. **It is not.** The same closed form was already
in the repo at `experiments/acm-flow/cf/MEGA-SPIKE.md` lines
41–49, with empirical b = 10 d = 4 panel in
`cf/EXTENDED-PANEL-RESULT.md`, multi-k extension at
`cf/MULTI-K-RESULT.md`, and a finer sub-leading decomposition
`δ_k(n) = (n − 1)k + offset(n)` plus Family A/B classification by
`ord(b, n)` in `cf/OFFSPIKE-RESULT.md`,
`cf/PRIMITIVE-ROOT-FINDING.md`, and the partial-derivation
attempt in `cf/MECHANISTIC-DERIVATION.md`.

The four-ways framing of what's substrate-transparent vs. open in
that thread is `arguments/MEGA-SPIKE-FOUR-WAYS.md`. Reading it
makes the redundancy here clean: the F(d, b) closed form, the b = 10
d = 4 leading-order panel, and the (P1)–(P4) Mahler-style proof
sketch all parallel content already on the page.

**What this document is preserved as.** A clean instance of the
recurring "BIDDER blindness" pattern recorded in
`memory/abductive_surprise_pattern.md`: a different agent in a
parallel thread independently rederived a result that was already
written elsewhere in the same repo. Preserving the document keeps
the instance available as data; deleting it would lose the
provenance.

**Where the genuinely new content went.** Three pieces from this
thread were not duplicates and have been moved to the mega-spike
thread:

- `cf/CROSS-BASE-RESULT.md` — cross-base validation at
  `b ∈ {3, 4, 6, 8, 10, 12}` showing the closed form's
  `(b − 2)/(b − 1)` prefactor isn't a base-10 artifact. (The b = 10
  thread was b = 10 only by accident of how the experiment grew.)
- `cf/D5-RESULT.md` — d = 5 confirmation extending
  `MULTI-K-RESULT.md` from `k ∈ {2, 3, 4}` to k = 5; pure
  confirmation, no new structure.
- `cf/MU-CONDITIONAL.md` — conditional irrationality
  measure `μ(C_b(n)) = 2 + (b − 1)(b − 2)/b` under the assumption
  that boundary spikes dominate the approximation budget. The
  premise is gated on the same off-spike denominator process as
  `MECHANISTIC-DERIVATION.md` step 3.

The compute artifacts (`cf_spikes_extended.py`, `cf_spikes_d5.py`,
`cf_extended.csv`, `cf_d5.csv`) remain in this folder as the run
artifacts they always were; the new mega-spike docs reference them
by relative path.

For the current state, read in order: `cf/MEGA-SPIKE.md`,
`cf/MECHANISTIC-DERIVATION.md`, `arguments/MEGA-SPIKE-FOUR-WAYS.md`,
then the three new mega-spike docs above.

---

The first principled pass at deriving the empirical spike formula in
`SPIKE-HUNT.md` from the construction. The empirical fit

    spike_digits(n, k)  ≈  (n−1)/n² · 10^(k-1) · (8k + 10/9)

is recovered exactly, in closed form, from the cumulative digit count of
`C_b(n)` through the d-th block. The fit is then the leading-order
prediction of a Mahler-style argument adapted to the sieved arithmetic
progression that defines the n-prime stream. This brief states the
closed form, identifies what a proof needs, and bounds what the
existing data already settles vs. what's open.


## Setup

The object is the n-Champernowne real

    C_b(n)  =  0 . p_1 p_2 p_3 …       (base b, p_K the K-th n-prime)

where for `n ≥ 2`, the K-th n-prime is given by the Hardy closed form
(`core/HARDY-SIDESTEP.md`):

    p_K(n)  =  n · (q · n + r + 1),       q, r = divmod(K − 1, n − 1).

The d-th digit class block of `C_b(n)` consists of all n-primes in
`[b^(d-1), b^d − 1]`. By the smooth case of the block-uniformity lemma
(`core/BLOCK-UNIFORMITY.md`, condition `n² | b^(d-1)`), the count of
n-primes in this block is exactly

    N_d(n)  =  (b − 1) · b^(d-1) · (n − 1) / n²,

so the digit count contributed by the d-th block is

    D_d(n)  =  d · N_d(n)  =  d · (b − 1) · b^(d-1) · (n − 1) / n².

(Outside the smooth case the spread bound says `N_d` differs from this
formula by at most 2 per leading-digit strip; see `BLOCK-UNIFORMITY.md`.)

The cumulative digit count through the end of the d-th block is

    C_d(n)  =  Σ_{j=1}^d D_j(n)  =  (n − 1)/n² · (b − 1) · Σ_{j=1}^d j · b^(j-1).


## The closed form

**Claim.** For `(b, n, d)` smooth, the spike magnitude at the d-block
boundary of the CF expansion of `C_b(n)` is

    spike_digits(n, d)  ≈  D_d(n) − C_{d-1}(n)
                        =  (n − 1)/n² · F(d, b),

where `F(d, b)` is the closed form

    F(d, b)  =  d · (b − 2) · b^(d-1)  +  (b^d − 1) / (b − 1).

For `(b, d) = (10, 4)`, `F = 33111`. The empirical fit
`(n − 1)/n² · 10^(d-1) · (8d + 10/9)` is exactly this `F`, since

    8d · 10^(d-1) + (10/9) · 10^(d-1)  =  (b−2)d · b^(d-1) + b^d/(b − 1)

— and `b^d/(b−1) = (b^d − 1)/(b − 1) + 1/(b−1)`, so the empirical fit
overshoots `F` by `(n−1)/n²/(b−1) = (n−1)/(n²(b−1))`, a constant in `d`.

**Asymptotic ratio to `D_d`.** As `d → ∞`,

    F(d, b) / D_d(n)  ·  n²/(n−1)  =  F(d, b) / [d(b−1) b^(d-1)]
                                   →  (b − 2) / (b − 1).

For `b = 10` this is `8/9`, matching the prefactor reported in
`SPIKE-HUNT.md`. The naive guess `(b−1)/b = 9/10` (full-block fraction
of digits) is **not** the right asymptotic — the cumulative subtraction
`D_d − C_{d-1}` gives `(b−2)/(b−1)` instead.

**Derivation of `F`.**

    Σ_{j=1}^{d-1} j · b^(j-1)
        =  ((d−1) b^d − d · b^(d-1) + 1) / (b − 1)²

(standard derivative-of-geometric formula). Multiplying by `(b−1)`:

    (b−1) · Σ_{j=1}^{d-1} j b^(j-1)
        =  ((d−1) b^d − d b^(d-1) + 1) / (b − 1).

Therefore

    D_d − C_{d-1}
        =  (n−1)/n² · (b−1) · [d · b^(d-1) − Σ_{j=1}^{d-1} j b^(j-1)]
        =  (n−1)/n² · [d (b−1) b^(d-1) − ((d−1)b^d − d b^(d-1) + 1)/(b−1)]
        =  (n−1)/n² · [d (b−2) b^(d-1) + (b^d − 1)/(b − 1)].                   ∎

The right factor is `F(d, b)`. For `(b, d) = (10, 4)`:
`4 · 8 · 1000 + 9999/9 = 32000 + 1111 = 33111`, the empirical asymptotic
constant in `SPIKE-HUNT.md`'s scaled column.


## What this is not, yet

A closed form derived from cumulative-digit bookkeeping is **not** a
proof that the spike at the d-block boundary actually has this size.
The bookkeeping says how many digits would separate two specific
landmarks (end of d-block, end of d−1-block); that the CF partial
quotient at the boundary equals this gap is a Mahler-style claim that
needs its own argument.

What we have, against six monoids at `d = 4`:

| n  | observed scaled (× n²/(n−1)) | predicted F(4, 10) | gap | gap fraction |
|---:|---:|---:|---:|---:|
| 2  | 33 072 | 33 111 | −39  | 0.12 % |
| 3  | 33 039 | 33 111 | −72  | 0.22 % |
| 4  | 32 997 | 33 111 | −114 | 0.34 % |
| 5  | 32 913 | 33 111 | −198 | 0.60 % |
| 6  | 32 835 | 33 111 | −276 | 0.83 % |
| 10 | 32 311 | 33 111 | −800 | 2.42 % |

`F(4, 10)` is the right asymptotic constant. The 0.12 % – 2.4 % drift
across n is a **sub-leading correction** that grows monotonically with
n and is not captured by the leading-order bookkeeping.

Three candidates for the drift:

1. **Edge effect at the d-to-d+1 transition.** The first n-prime in
   the (d+1)-block is `n · ⌈b^(d-1)/n⌉ + small`, and its specific
   value relative to `b^d` controls a `log b` of the spike. This is
   an `O(1)` digit correction whose dependence on `(n, b)` could
   plausibly explain the ~10–800 digit gap.
2. **Smoothness violations.** For `(b, n, d) = (10, 3, 4)` and
   `(10, 4, 4)` and `(10, 6, 4)`, the smooth condition `n² | b^(d-1)`
   fails. The spread bound says `N_d(n)` deviates from `(n−1)b^(d-1)/n²`
   by at most `±2`, hence `D_d` by at most `±2d`, hence `F` by an
   amount bounded by `O(d)`. This explains a `O(d)` drift but not
   the `O(800)` drift for `n = 10` (which is smooth at d=4).
3. **`n = 10` structural specialness.** Every 10-prime ends in `0`,
   so the digit sequence has a periodic last-digit pattern that
   the bookkeeping doesn't see. The doc flags this as worth its
   own treatment.

The drift is **n-monotone, not block-monotone**: at fixed d=4, gap is
small for small n and grows to 2.4 % at n=10. That's the structure of
a per-monoid edge effect, not a per-block growing residual.


## What a proof would look like

Mahler's transcendence argument for integer Champernowne `M`:
truncate `M` after the d-block and write the result as a rational
`A_d / B_d`. The natural rational extension of the d-block's pattern
(treat the next block as if it continued the AP) agrees with `M` for
some leading prefix of the (d+1)-block, then diverges. The divergence
location bounds how good a rational approximation `A_d / B_d` is to
`M`, and that bound translates to a CF partial quotient.

For `C_b(n)`, the d-block's pattern is the AP `n · k` for
`k ∈ [b^(d-1)/n, b^d/n)` with `n ∤ k`. This AP is periodic with period
`n` in the multiplier `k` and period `n²` in the n-prime sequence.
The natural extension to the (d+1)-block continues the same residue
pattern modulo `n²`. The actual (d+1)-block restarts the AP at
`n · ⌈b^d / n⌉` with a possibly different residue offset.

A proof of the closed form would:

**(P1)** Identify the truncation `T_d(n) = A_d/B_d` of `C_b(n)` after
the d-block as a rational with `B_d` of size `b^{C_d(n)}`.

**(P2)** Show that the natural-extension rational `T_d̂(n)` (continue
the d-block's `n²`-period residue pattern indefinitely) agrees with
`C_b(n)` for the first `D_d(n)` digits of the (d+1)-block, then
diverges at a specific location determined by where the d+1-block's
actual residue pattern diverges from the d-block's.

**(P3)** Translate the (P2) divergence location into a CF
inequality of the form
    `|C_b(n) − A_d / B_d|  <  1 / (B_d · b^{D_d(n) − C_{d-1}(n)})`
which by the standard Lagrange/Khinchin theory of continued fractions
forces `a_{i+1} ≥ b^{F(d, b) · (n−1)/n²}` for the next CF partial
quotient `a_{i+1}` past the convergent at index `i` of `T_d`.

**(P4)** Show the matching upper bound:
    `|C_b(n) − A_d / B_d|  >  1 / (B_d · b^{D_d(n) − C_{d-1}(n) + O(1)})`
which forces `a_{i+1} ≤ b^{F(d, b) · (n−1)/n² + O(1)}`.

The two together pin `log_b a_{i+1} = F(d, b) · (n−1)/n² + O(1)` —
i.e., the spike size in digits matches the closed form up to bounded
error, **uniformly in n**.

(P1) is straightforward algebra. (P2) is the load-bearing step — it
needs the AP-and-sieve structure to commute with the digit-positional
truncation in a controlled way. (P3) and (P4) are standard CF theory
once (P2) is in place.

The doc `MAHLER-CHECK.md` certifies that the empirical pipeline can
detect these spikes correctly when they exist; the `cf_spikes.csv`
data confirms the boundary identification via
`2 log q_{i-1} + log a_i = C_d(n)` (the cumulative-digits identity).
That identity is itself evidence for (P2) – (P4) holding empirically
at d ≤ 4.


## Coupling to FINITE-RANK-EXPANSION

The speculation in `core/FINITE-RANK-EXPANSION.md`:

> the continued-fraction spike law and the multiplication-table
> experiments may be shadows of the same rank layers seen through
> different global projections.

The closed form here lets us check this at h = 1.

**Reading.** `(n−1)/n²` is the density of height-1 elements (atoms)
of `M_n` inside an integer block. The leading-order spike
prediction `(n−1)/n² · F(d, b)` factors as:

- `(n−1)/n²` — the rank-1 shadow: density of `A_n` in the block.
- `F(d, b)` — the positional shadow: pure base-`b` cumulative-digit
  bookkeeping, no monoid structure visible.

Higher-rank quantities (`Q_n`, `Λ_n`, the divisor stack from
`core/Q-FORMULAS.md`) **do not enter the leading prediction**. The
n-Champernowne CF spike at the d-block boundary appears, at leading
order, to be an h = 1 / rank-1 phenomenon — driven entirely by the
density of atoms and the positional skeleton of base `b`.

This is the **cf-version of Phase 4 (B′)'s outcome on the multiplication
table.** There, the bare count `M_n(N)` was conjectured to expose `Q_n`
structure and instead exposes only density × Ford anatomy; the rank-h
shadow shows up only in cell-resolved or weighted observables. Here,
the bare spike size at the leading boundary appears to expose only
density × positional bookkeeping.

The 0.12 % – 2.4 % sub-leading drift across n is the only residual
that does not factor through the rank-1 shadow. **If** that drift is
where the rank-h structure leaks in, it would be a fair test of the
FINITE-RANK-EXPANSION speculation. **If** the drift is fully explained
by edge effects at the d-to-d+1 transition (a one-line
positional-arithmetic correction with no monoid algebra in it), the
speculation does not get cf-evidence at all from this brief.

**Not claimed.** The speculation is not refuted. CF spikes are a
specific projection; other projections (off-boundary PQs, the
irrationality measure as a limsup, sub-leading boundary corrections)
may carry rank-h structure. This brief checks the leading-boundary
projection only.


## First step

Two compute steps and one mostly-paper step.

**Compute (A) — sub-leading drift map across (b, n, d).**

`cf_spikes.py` already produces the d=4 spike for `n ∈ {2,3,4,5,6,10}`
in base 10. The closed form `F(d, b) · (n−1)/n²` predicts the
leading constant; the drift table above shows the sub-leading residual
as a function of `n`. Extend the panel:

- More n at fixed (b, d) = (10, 4): `n ∈ {7, 8, 9, 11, 12, 13, 15, 20}`.
  Tests whether the n-monotone drift is monotone all the way out, or
  has a special form at small primes vs. composites vs. n=10's
  trailing-zero structure.
- Other bases at fixed d: b ∈ {3, 4, 6, 8, 12} for n ∈ {2, 3, 5}.
  The closed form predicts asymptotic ratio `(b−2)/(b−1)`, so b=3
  gives `1/2`, b=12 gives `10/11`, etc. Detecting these tests the
  base-b structure of the formula directly.

The compute is single-script with `cf_spikes.py`; bumping the panel
is a one-line edit. Running the b=3 / b=12 panels needs `acm_n_primes`
output in the requested base, which is a digit-conversion at the end —
also a one-line edit.

This data should let us split the drift into:
- a `b`-only piece (positional arithmetic, edge effect at boundary)
- an `n`-only piece (monoid-structural, candidate for rank-h shadow)
- an `(n, b)` interaction (the n=10 / b=10 trailing-zero correction)

**Compute (B) — push to d = 5.**

The `cf_spikes.py` precision wall at `PREC_BITS_LO = 80 000` cuts off
just past d=4 mega-spikes. The d=5 mega-spike is predicted to be
~10 × the d=4 mega in size (`F(5, 10)/F(4, 10) = b · (b−2)/(b−2) +
O(1) ≈ b ≈ 10`, more precisely `F(5,10) = 5·8·10000 + 99999/9 = 411 111`,
so `F(5, 10)/F(4, 10) ≈ 12.4`). At n=2 this is `~100 000` digits;
detecting it needs `PREC_BITS_LO ≈ 800 000` and `K_PRIMES ≈ 2·10⁵`.

A second decade of d-data (six n × two d-values) is what tests
**within-n d-scaling** — the closed form predicts a specific ratio
between successive d's that the d=4-only data cannot.

**Paper (C) — Mahler argument carried out for n-Champernowne.**

Steps (P1) – (P4) above. The hardest part is (P2). The setup has the
classical Mahler structure: AP within the d-block, AP-period mismatch
at the d-to-d+1 transition. The technical work is making the divergence
locus explicit as a function of `(n, b, d)` rather than the
"O(...)" abstraction Mahler used in his 1937 transcendence proof.

(C) is what closes the loop. (A) and (B) constrain the proof
empirically; (C) replaces empirical fits with statements about
behavior at all `d ≥ d_0`.


## "Probably nothing" signals

Three failure modes, in increasing severity:

1. **Sub-leading drift is fully explained by an edge-effect formula
   with no monoid content** (just the position of the first n-prime
   in the (d+1)-block, plus base-b arithmetic). Then the cf spike
   carries zero rank-h information and the closed form is
   complete-but-uninteresting from the FINITE-RANK-EXPANSION angle.
   This is the probably-nothing outcome for the rank-shadow speculation;
   the closed form itself is still substantive.

2. **The closed form is a coincidence of fits at d = 4.** The d = 5
   data falls outside the predicted ratio. Then the bookkeeping
   identity `D_d − C_{d-1}` is not actually the spike size — the
   d = 4 match was a numerological accident and Mahler's argument
   does not carry over cleanly. This would be surprising and would
   prompt re-deriving from the AP structure directly rather than the
   cumulative-count shortcut. Empirical falsifier: d = 5 spike for
   n = 2 in base 10 deviates from `F(5, 10)/4 = 102 778` by more than
   the d = 4 drift would suggest.

3. **The sub-leading drift grows superlinearly in n** when the panel
   is extended. Then the bookkeeping is the leading order but
   higher-order terms are not bounded, and any irrationality-measure
   claim that uses the spike formula has to wait on a closed form for
   the higher-order tail. Falsifier: the (A) panel shows
   `gap(n) / F` growing faster than `O(1)` in `n`.

Outcome (1) is most likely given the structure of the bookkeeping
(it has the right shape for an edge-effect-corrected formula). (2) is
unlikely but the d = 5 check is the standard scale-out validation.
(3) is unlikely given the smoothness/spread bounds.


## Reach goal

A theorem of the form

> **Theorem (closed form).** For every `b ≥ 3, n ≥ 2, d ≥ d_0(b)`,
> the CF of `C_b(n)` has a partial quotient `a_{i_d}` at index
> `i_d = i_d(b, n)` (the "d-th boundary spike index") with
> `log_b a_{i_d} = F(d, b) · (n − 1) / n² + O(1)`,
> where `F(d, b) = d(b−2) b^(d-1) + (b^d − 1)/(b − 1)` and the
> implicit constant depends only on `b`.

And, conditional on the off-boundary partial quotients staying
Khinchin-typical (an additional input the brief does not address), an
irrationality-measure consequence:

> **Corollary (irrationality measure, conditional).** Under the
> Khinchin-typical assumption above, the irrationality measure
> `μ(C_b(n))` is a function of `b` alone (not `n`); explicitly,
> the boundary-spike sequence gives `μ(C_b(n)) = 2 + (b − 2)/(b − 1)
> · ϕ(b) / ψ(b) + O(1/d_0)` for `b → ∞`, with leading value `μ → 10`
> for `b = 10`.

The last line recovers Mahler's `μ = 10` for integer `b = 10`
Champernowne as a specialization (the original being `n = 1`-equivalent
in the boundary-spike sense, modulo the prime-gap apparatus that lives
outside this brief). An explicit per-`b` `μ` for the n-Champernowne
family would be a small but real Diophantine result, and the proof
template is a verbatim adaptation of Mahler 1937's argument with the
sieved AP in place of the all-integers AP.

This brief delivers the closed form's leading order and the proof
sketch. The reach goal is the closed form's full statement (with
sub-leading control) plus the conditional `μ`.


## Tractability

(A) is a one-afternoon compute (panel extension within `cf_spikes.py`).
(B) is overnight per n at PREC_BITS_LO = 800 000. (C) is mostly paper
work; the reductions are Mahler 1937 specialized to the AP-sieved
case, and the technical depth is a few pages, not a year.

The full reach goal is a theorem-and-proof writeup: closed form,
edge-effect correction, conditional `μ`. Estimate: a week of focused
work if the d = 5 numerical confirmation lands clean.


## Files (proposed)

This document covers the brief and derivation only. Implementation
artifacts to add:

- `cf_spikes_extended.py` — extended panel of (b, n, d) covering
  the (A) compute step.
- `SPIKE-CLOSED-FORM.md` — derivation writeup with the (P1)–(P4)
  proof sketch fleshed out and the d = 5 numerical confirmation.
- `cf_spikes_d5.py` — the d = 5 enumeration with bumped precision
  budget.

Existing artifacts to lean on:
- `cf_spikes.py` — the d = 4 panel pipeline (already validates against
  Mahler 1937's classical Champernowne via `MAHLER-CHECK.md`).
- `core/acm_core.py` / `core/hardy_sidestep.py` — the n-prime stream
  (random access via Hardy's closed form is what makes the d = 5
  push tractable).
- `core/BLOCK-UNIFORMITY.md` — the smoothness/spread structure that
  tells us where `D_d(n)` is exact vs. `±2d`-bounded.


## Coupling to other briefs

- **Brief 1** (Copeland-Erdős positioning): independent. The
  block-uniformity lemma is shared input but the literature task
  doesn't constrain this brief.
- **Brief 4** (multiplication table on `M_n`): both briefs probe the
  FINITE-RANK-EXPANSION speculation through different observables.
  Brief 4's Phase 4 (B′) outcome — the bare count exposes only
  density × Ford anatomy at h = 2, with rank-h structure visible only
  in cell-resolved or weighted observables — is the structural
  precedent. This brief expects an analogous outcome at the cf
  boundary spike: leading order is density × positional bookkeeping;
  rank-h structure (if any) lives in the sub-leading drift or in
  off-boundary PQs.
- **Brief 3** (Erdős-Borwein E): independent.

The cleanest read across briefs is: ACM-Champernowne reals expose
their construction's leading-order density and positional structure
in any "global counting" observable; rank-h algebra, when it appears,
appears in conditional, weighted, or sub-leading projections. Brief 4
provided one instance; this brief tests the same thesis on a
different observable.
