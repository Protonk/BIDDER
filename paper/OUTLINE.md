# JStatSoft submission — outline

**Status.** Skeleton. Phase 0 decisions locked (see `WORKSET.md`);
sections named, content gestured at, drafting items live in the
workset.

**Title.** *BIDDER: a keyed reproducible permutation with exact
leading-digit uniformity over arbitrary `(b, d)` blocks.*

**Scope.** `core/` + `generator/` only. Algebra side, wonders,
arguments, experiments — out. The paper is a tool paper, not the
substrate manifesto.

**Locked from Phase 0:** 15-page target; `bidder-stat/` carved repo
for replication; C-primary API surface; single author; §8 comparison
folded into §7.4; benchmarks in a §6.4 table plus §6 paragraph.

**Discipline.** No occlusive salesmanship. Every measure on BIDDER
is turned inside out — the paper plays cards face up the whole way.
Concretely: §3.6 / §4.6 close with "what this covers and what it
does not"; §4.4 names the Riemann-sum identity as bijection-trivial
(not BIDDER-special); §4.5 names the FPC realisation gap with its
measured magnitude (~1× best, ~32× worst); §7.4 includes axes BIDDER
loses on; §9 limitations expand to name every regime where BIDDER is
the wrong tool; each §7 use case ends with "use something else when…";
gaps the paper flags but doesn't fill numerically (FF1 / FF3-1,
`secrets.SystemRandom`, etc.) live in `paper/DEBTS.md` and are named
by ID in the prose.

---

## Decisions (resolved in Phase 0)

- **Repo split.** Carve `core/` + `generator/` + relevant `tests/`
  into a new `bidder-stat/` for the JStatSoft replication archive.
- **Length target.** 15 pages.
- **Primary language presented.** C surface (`bidder_root.h`);
  Python wrapper as a binding example.
- **Comparison.** Folded into §7.4 (no standalone §8).
- **Benchmarks.** §6.4 table + §6 paragraph.
- **Author-list.** Single author, conformed to JStatSoft style.

---

## §1. Abstract

One paragraph, ~150 words. Names the gap (exact uniform digit
distribution on arbitrary `(b, d)`; reproducible without-replacement
sampling on arbitrary `[0, P)`), the tool (substrate + cipher), the
two structural guarantees (block uniformity, `N = P` Riemann-sum
identity), and the use cases the tool unlocks.

## §2. Introduction

Three paragraphs.

- **The gap.** Asymptotic-uniformity claims are the norm; exact
  uniformity over arbitrary `(b, d)` is rare. Most format-preserving
  permutation tooling is locked to power-of-two domains.
- **The construction.** ACM-Champernowne block × Speck32/64
  cycle-walking. The substrate is exact; the cipher provides
  reproducibility and disorder. Neither part is asked to do the
  other's job.
- **The contribution.** A working tool with two structural theorems
  (counting + permutation-invariance), one cipher choice with a
  fallback, a stable API, and six use cases where exactness on
  arbitrary `(b, d)` is load-bearing.

## §3. The block-uniformity substrate

§3 expanded to draft-paragraph granularity as the first non-use-case
template. Theorem-shaped, not demonstration-shaped: each sub-bullet
is one paragraph in the final paper, naming the load-bearing claim,
the proof scope (in-paper vs cited), the anchor that gates it, and
the source-of-record `core/` doc.

- §3.1 **Setup.** Define `M_n = {1} ∪ nZ_{>0}`, its atoms
  (n-primes: multiples of `n` not divisible by `n²`), and the
  base-`b` digit class `[b^(d-1), b^d - 1]`. Notation only; no
  theorems. The triple `(b, n, d)` is the running parameter set
  for the rest of §3 and §4. Source: `core/BLOCK-UNIFORMITY.md`
  §opening.

- §3.2 **Integer block-uniformity lemma.** Stated and proved in
  the paper. *Statement:* in base `b`, the integers in
  `[b^(d-1), b^d - 1]` have leading digits exactly equidistributed
  over `{1, …, b-1}`; each digit appears exactly `b^(d-1)` times.
  *Proof, one paragraph:* a `d`-digit base-`b` integer is
  `d_1 d_2 … d_d` with `d_1 ∈ {1, …, b-1}` and the remaining `d-1`
  positions free over `{0, …, b-1}`; each `d_1` accounts for
  `b^(d-1)` integers; the block has `(b-1) · b^(d-1)` integers
  total, exactly `b^(d-1)` per leading digit. ∎ Anchor:
  `tests/test_acm_core.py::test_block_boundary_*`.

- §3.3 **Sieved block-uniformity, smooth family.** Stated and
  proved in the paper. *Statement:* under the smooth hypothesis
  `n² | b^(d-1)`, the n-primes of `nZ_{>0}` in `[b^(d-1), b^d - 1]`
  are exactly equidistributed by leading digit, with
  `b^(d-1)(n-1)/n²` per digit. *Proof outline, one paragraph:*
  each leading-digit strip has length `b^(d-1)` and starts at a
  multiple of `n²`; counting multiples of `n` (`b^(d-1)/n`) and
  multiples of `n²` (`b^(d-1)/n²`) and subtracting gives the per-
  strip n-prime count, independent of which leading-digit strip.
  Anchor: `tests/test_acm_core.py::test_block_uniformity_sieved_sufficient`.
  Source: `core/BLOCK-UNIFORMITY.md` §"Sieved version: n-primes
  inside the block".

- §3.4 **Spread bound and Family E.** One paragraph covering both
  auxiliary results; together they cover the picture when the
  smooth hypothesis fails. *Spread bound (universal):* for any
  `(b, n, d)`, per-leading-digit n-prime counts differ by at most
  2. Proof is the same divmod argument applied to the count of
  multiples of `n` and `n²` in a generic interval. *Family E:* for
  `n ∈ [b^(d-1), ⌊(b^d-1)/(b-1)⌋]`, the n-primes in the digit
  class are exactly `{n, 2n, …, (b-1)n}` — `b-1` of them, one per
  leading digit, exact. The two sufficient families are disjoint
  for `d ≥ 2`. Together they give a cheap two-step audit at the
  digit-block boundary. Anchors:
  `test_block_uniformity_sieved_spread_bound`,
  `test_block_uniformity_sieved_family_e`. Source: `core/BLOCK-UNIFORMITY.md`
  §"A spread bound that always holds" and §"A second sufficient
  family".

- §3.5 **Hardy random-access.** *Statement:* the `K`-th n-prime is
  `p_K = n · c_K` with `c_K = qn + r + 1` where
  `(q, r) = divmod(K-1, n-1)`. *Reading:* the n-primes are an
  arithmetic progression with one residue class deleted per period
  of `n`, so the inverse to "the K-th term" is one divmod and a
  bounded amount of arithmetic — `O(1)` bignum work in `K`, no
  enumeration. Source: `core/HARDY-SIDESTEP.md`.

- §3.6 **What §3 covers and what it does not.** One paragraph
  closing. *What it covers:* the integer lemma is exact at
  digit-class boundaries `[b^(d-1), b^d - 1]`; the sieved lemma is
  exact under the smooth hypothesis `n² | b^(d-1)`; Family E is
  exact in its `n` range; the spread bound (≤ 2) is universal but
  weaker than exact. Hardy's `c_K` is exact and `O(1)` for any
  `K`. *What it does not cover:* discrepancy of `C_b(n)` away from
  block boundaries — that's Schiffer (1986) territory, where the
  best known bound is `Θ(1/log N)`, not exact; the lucky-
  cancellation locus where `n² ∤ b^(d-1)` and Family E doesn't
  apply but exact uniformity still holds (cited but
  uncharacterised — see §9 + DEBTS.md); absolute normality of
  `C_b(n)` across bases (open; out of scope, see §9). What this
  enables in §4: the cipher operates on `[0, P)` for arbitrary `P`
  (`P ≤ 2³² − 1` per §4.2), and §3's exactness claims hold on the
  ranges they cover. The paper's exactness claims live where §3
  covers them, not elsewhere.

## §4. The cipher path

§4 expanded to draft-paragraph granularity, mirroring §3's shape.
Theorem-and-implementation-shaped: each sub-bullet is one paragraph
naming the load-bearing claim or design choice, the proof scope
where applicable, the anchor that gates it, and the M1/M2
dependency where the paragraph awaits a Phase 1 number.

- §4.1 **Role separation.** Framing paragraph for the substrate-
  and-cipher split as a design principle. §3 supplies exact
  deterministic structure (counts, random-access); §4 supplies
  opaque reproducible disorder (keyed bijection of `[0, P)`).
  Neither piece is asked to do the other's job — the substrate is
  not asked to randomise, the cipher is not asked to guarantee a
  digit-distribution property. The contract is one-line: the
  cipher produces a bijection; §3's properties survive *any*
  bijection because they are statements about multisets and
  arithmetic progressions, not about ordering. Source: `BIDDER.md`.

- §4.2 **Speck32/64 in cycle-walking mode.** *What Speck is:* a
  lightweight block cipher with a 32-bit block (Speck32/64 = 32-bit
  block, 64-bit key) [Beaulieu et al., 2013]. *Why Speck for
  BIDDER:* small block matches typical `P < 2^32`, open
  specification, fast software impl, zero library dependencies.
  *Cycle-walking:* given a cipher on `[0, 2^32)` and a target
  `[0, P)`, repeat `Encrypt(x)` until the output lands in `[0, P)`;
  the result is a bijection of `[0, P)` [Black & Rogaway, 2002].
  Expected calls per output: `2^32 / P`, ≈ 1 when `P` is not too
  close to `2^32`. Source: `generator/`.

- §4.3 **Feistel fallback** *(depends on M1).* When `P` is close to
  `2^32`, the cycle-walking ratio degrades and throughput depends
  on `P` in an awkward way. Solution: drop to an unbalanced
  Feistel network sized to `[0, P)` directly. *Decision rule:* the
  M1 sweep measures expected calls per output across a
  representative `P` panel and identifies the crossover where
  Feistel's larger per-call cost beats Speck's cycle-walking
  overhead. *In the paper:* one table from M1 with the
  recommended threshold. Anchor: M1's tabulated output (the
  decision is empirically calibrated, no separate proof test).

- §4.4 **Structural Riemann-sum identity at `N = P`.** Stated and
  proved in the paper. *Statement:* for any bijection
  `π : [0, P) → [0, P)` and any `f`,

      (1/P) Σ_{i=0}^{P-1} f(π(i)/P) = (1/P) Σ_{k=0}^{P-1} f(k/P) = R(f, P),

  the left-endpoint Riemann sum. *Proof, one line:*
  `{π(0), …, π(P-1)}` is the same multiset as `{0, …, P-1}` since
  `π` is a bijection, so the sums are equal. *Cards-face-up
  reading:* the identity is a tautology of bijection-hood. Any
  keyed permutation has it — `numpy.random.permutation` with a
  seed has it; `random.shuffle` with a seed has it; `FF1` has it;
  a hand-coded cycle-walking AES has it. BIDDER's contribution at
  `N = P` is *being a keyed reproducible bijection on arbitrary
  `[0, P)`*, not the identity itself. The §4.5 statistical layer
  at `N < P` is where BIDDER's design choices show. Anchor:
  `tests/theory/test_riemann_property.py`. Source:
  `generator/RIEMANN-SUM.md`.

- §4.5 **FPC shape at `N < P`** *(M2 done).* *Ideal-permutation
  statement:* for a uniformly-random permutation of `[0, P)`, the
  prefix-mean variance is `σ²/N · (P − N)/(P − 1)` for `N ≤ P`.
  *BIDDER's realisation:* M2 measures the variance ratio
  (BIDDER / ideal) across a `(P, N)` grid. *Cards-face-up:* the
  gap is significant and `(P, N)`-dependent. Best ratio in the
  measured panel is ~1 at `P = 200`; worst is **~32× at
  `(P, N) = (10000, 5000)`**. There is also a regime around
  `P = 1000` for `f = sin(πx)` where the ratio drops *below* 1
  (bias-cancel anomaly, see DEBTS.md D6). The realisation gap is
  the empirical price for a lightweight cipher (Speck32 + 8-round
  minimal Feistel, no library deps). FF1 with AES would close the
  gap at substantially higher per-call cost (see §7.4 + DEBTS.md
  D1). The cipher's PRP quality enters the paper here, as a
  measurement; the substrate's exactness in §3 and the structural
  identity in §4.4 are unaffected. Anchor:
  `tests/theory/test_fpc_shape.py`. Source:
  `generator/RIEMANN-SUM.md`. Numbers: `paper/measurements/m2_results.md`.

- §4.6 **What §4 covers and what it does not.** One paragraph
  closing. *What it covers:* a keyed reproducible bijection on
  arbitrary `[0, P)` for `P ∈ [2, 2³² − 1]`, with the structural
  Riemann-sum identity at `N = P` (which any bijection has — see
  §4.4) and the FPC shape at `N < P` (with measured gap — see
  §4.5). No library dependencies; the cipher fits in a few hundred
  lines of C. *What it does not cover:* cryptographic-strength
  PRP quality (Speck32 has a small block; the 8-round Feistel is
  lightweight by design — DEBTS.md D9 names a path to a stronger
  variant). Tight FPC realisation across `(P, N)` (M2's measured
  gap reaches ~32×; FF1 / FF3-1 with AES would close it — DEBTS.md
  D1). Periods above `2³² − 1` (single-precision design choice;
  not addressed). The cipher's job is to land on the right
  multiset; §3's substrate makes that multiset exactly what the
  user wants. Where the cipher is asked to do anything statistical
  beyond bijection-hood — §4.5 — the paper reports a measured
  number, not a guarantee.

## §5. API

C-primary per Phase 0: `bidder_root.h` declarations are the surface;
the Python wrapper appears as a binding example in §5.4.

- §5.1 `bidder_cipher(period, key, ...)`. C signature, contract,
  examples.
- §5.2 `bidder_sawtooth(n, count, ...)`. C signature, contract,
  examples.
- §5.3 Composition: `cipher` + `sawtooth` for "exact uniform
  leading-digit Monte Carlo over `[b^(d−1), b^d − 1]`."
- §5.4 Python binding example (`bidder.py`).
- §5.5 Backwards-compatibility / stability promise. Tied to the
  `bidder-stat/` release tag named in Phase 1 E3.

## §6. Implementation

- §6.1 C core (`bidder_root.c`, `bidder_opaque.c`), Python wrapper,
  no third-party deps in the wrapper. Brief paragraph on how the
  cycle-walking Speck32/64 and Feistel fallback are wired together.
- §6.2 Build, install, test in `bidder-stat/`. (Reference
  `Makefile` + `bidder.py`.)
- §6.3 Test suite layout — proof tests (theorem == implementation)
  vs property tests vs benchmark tests. Cite `tests/theory/` and
  `tests/test_acm_core.py`.
- §6.4 Performance: §6.4 table of throughput numbers + a §6
  paragraph on cycle-walking overhead and the Feistel decision
  boundary. (Locked Phase 0.)

## §7. Use cases

Six worked examples. Each ~half a page. Code + numerical result + the
exactness payoff vs the asymptotic alternative.

§7.6 is expanded below as the **template** for the other five (one
bullet per intended paragraph; load-bearing claim, comparator,
number, figure or table, code pointer, payoff sentence, plus a
"use something else when…" sentence per the cards-face-up rule).
§7.1–§7.5 inherit this shape when they're expanded next; each will
include its own "use something else when" sentence naming the
regime where another tool is the better choice.

- §7.1 **Stratified survey design** with leading-digit strata at
  base `b ≠ 2`.
- §7.2 **Benford-test null distribution** as a deterministic
  reference. Working title: *Anti-Benford reference for Benford-
  detector calibration*. Substrate-leveraged use case (§3.2 +
  §3.3 do the work; the cipher's role is incidental).
   - **Problem.** A forensic auditor or quantitative
     statistician is calibrating a Benford detector
     (chi-squared test, mean-absolute-deviation, KS variant)
     and needs to characterise the detector's response on a
     *known anti-Benford* reference — the "data is uniformly
     distributed across leading digits" extreme, the opposite
     end from Benford-conforming. Standard practice: simulate
     i.i.d. uniform samples, accept sampling-noise-driven
     deviation in the leading-digit histogram. Cards-face-up
     problem: the analyst wants a reference with *zero*
     deviation in the leading-digit counts at any size, so
     the detector's response is purely a function of the
     detector, not of the reference's sampling noise.
   - **Substrate guarantee, integer level.** Cite §3.2: in
     base `b`, the integers in `[b^(d-1), b^d − 1]` have
     leading-digit counts of exactly `b^(d-1)` per digit
     `j ∈ {1, …, b−1}`. Counting argument from positional
     notation; no error term. The full block has
     `(b−1) · b^(d-1)` integers; partitioned by leading
     digit, each bin has exactly `b^(d-1)`. (Headline payoff.)
   - **Substrate guarantee, sieved level.** Cite §3.3: when
     the analyst wants n-prime atoms rather than raw
     integers (e.g., to reuse BIDDER's `bidder.sawtooth`
     output as a corpus), the sieved lemma under the smooth
     hypothesis `n² | b^(d-1)` gives exactly
     `b^(d-1)(n − 1)/n²` n-primes per leading digit. Outside
     smooth, the spread bound (§3.4) caps per-digit
     imbalance at 2 — sampling-noise-free even when
     exactness fails. Family E provides exact uniformity in
     a disjoint range. (One paragraph naming the smooth-vs-
     spread-bound regime.)
   - **Comparator.** i.i.d. uniform samples from
     `Uniform({1, …, b·b^(d-1)−1})`. At sample size
     `N = (b−1)·b^(d-1)` (matching the block's atom count),
     each leading-digit bin has expected count `b^(d-1)` but
     with sampling standard deviation
     `√(N · (1/(b−1)) · ((b−2)/(b−1)))`. The Pearson
     chi-squared statistic with `b−2` degrees of freedom
     (for `b−1` bins) has mean `b−2` and standard deviation
     `√(2(b−2))` under the null — never exactly zero. (One
     paragraph; the i.i.d. comparator's measurement noise.)
   - **Figure.** Two-panel histogram of leading-digit
     frequencies at one fixed `(b, d)` (suggested: `b = 10,
     d = 4` so the block is `[1000, 9999]` with N = 9000).
     *Left panel:* BIDDER atoms — nine bars all at exactly
     `1000 / 9000 = 11.11%`, indicated as exact. *Right
     panel:* i.i.d. uniform sample of size 9000 — nine bars
     wobbling within ±√(9000 · (1/9)(8/9)) / 9000 ≈ ±0.33%
     around 11.11%. Generated by `use_case_02_benford_null`.
   - **Table.** Pearson chi-squared statistic on the BIDDER
     corpus and on i.i.d. samples across `(b, d) ∈ {(10, 3),
     (10, 4), (10, 5), (8, 5), (16, 4)}`. *BIDDER row:*
     chi-squared = 0 exactly at every cell. *i.i.d. row:*
     chi-squared distributed as `χ²(b−2)` under the null;
     reported as mean and one-sigma band over 1000 trials.
     The contrast is sharp: zero vs `b − 2` ± `√(2(b − 2))`.
   - **Code.**
     `bidder-stat/replication/use_case_02_benford_null.{c,py}`.
     ~25 lines C + ~30 lines Python (the histogram plot is
     matplotlib; the chi-squared trial loop is the bulk).
     `make use_case_02` reproduces the figure and the table
     from a single command.
   - **Payoff.** One sentence: the analyst gets a
     deterministic anti-Benford reference with zero sampling
     noise on the leading-digit counts at any block size, so
     the detector's response on this reference reflects the
     detector's properties alone — not the reference's
     finite-sample variance. The substrate's exactness has
     visible cash value here.
   - **Use something else when.** If sampling noise in the
     reference is acceptable — when the detector's
     calibration tolerates `O(1/√N)` deviation in the bin
     counts — use i.i.d. uniform; one `numpy.random.integers`
     call, no substrate machinery. If the calibration needs
     a Benford-*conforming* reference (rather than the
     anti-Benford extreme), use an i.i.d. sampler from
     Benford's distribution; BIDDER is a uniform-leading-
     digit tool, not a Benford-conforming one. If the
     analyst is testing for *any* deviation rather than the
     specific direction Benford-vs-uniform, the choice
     between BIDDER and i.i.d. for the reference matters
     less and the simpler path wins.
- §7.3 **Reproducible cross-validation** with exact fold sizes on
  non-power-of-two `n`.
- §7.4 **Format-preserving permutation** of a small-`P` domain
  where FF1/FF3 would be overkill. *(Absorbs the head-to-head
  comparison table per the Phase 0 fold of §8.)* The matrix has
  axes BIDDER wins on (keyed, reproducible, streaming/random-
  access, arbitrary `P`, zero deps) **and axes BIDDER loses on:**
  - *Cryptographic PRP strength.* BIDDER's Speck32 (small block)
    and 8-round minimal Feistel are not cryptographically strong.
    FF1 / FF3-1 with AES are. Anyone needing PRP-grade randomness
    should use FF1 / FF3-1, not BIDDER.
  - *FPC realisation tightness.* M2 measures BIDDER's variance
    ratio against ideal as ~1×–32× across `(P, N)`. FF1 with AES
    is expected to land near 1× across the same panel; not
    benchmarked here (DEBTS.md D1 is the to-do).
  - *Real-randomness baselines.* `secrets.SystemRandom().shuffle`
    and `os.urandom`-driven sort-by-key are gold-standard for
    unguessable output; BIDDER doesn't compete with them on
    randomness quality (DEBTS.md D2, D3).

  Comparators benchmarked numerically in M3:
  `numpy.random.permutation`, `random.shuffle`, sort-by-iid-key,
  i.i.d. with replacement. BIDDER's positioning: lighter than
  FF1/FF3 tooling, streaming where the in-memory comparators are
  not, deliberately non-cryptographic. The matrix shows where
  each comparator wins.
- §7.5 **Deterministic test corpora** for digit-statistic
  algorithms.

- §7.6 **Variance-controlled Monte Carlo** with known FPC, so the
  without-replacement variance is computable rather than
  estimated.
   - **Problem.** An analyst running prefix-mean Monte Carlo on a
     finite population `[0, P)` wants the estimator's variance to
     be a known closed-form quantity (the FPC) rather than
     estimated, exactly zero at `N = P` so the budget can be
     planned without uncertainty, reproducible across runs (same
     key → same sequence), and streamed (no need to materialize all
     `P` samples in memory). No single existing tool delivers all
     four. (Motivating paragraph.)
   - **Structural guarantee at `N = P`.** Cite §4.4: the prefix
     mean equals the left-endpoint Riemann sum exactly, for any
     key, any `f`. Variance across keys at `N = P` is machine-ε.
     Comparator: an i.i.d. estimator has variance `σ²/P` at
     `N = P`, never zero. (One paragraph; the headline payoff.)
   - **Statistical shape at `N < P`.** Cite §4.5: prefix-mean
     variance follows `σ²/N · (P − N)/(P − 1)` for an ideal
     uniform permutation. BIDDER realises this shape with a
     backend-dependent gap; the gap is what M2 tabulates across
     a `(P, N)` grid. (One paragraph; the FPC layer.)
   - **Comparators (the §8-fold lives here in narrative form).**
     i.i.d. with replacement: loses FPC, suboptimal variance at
     every `N`. `numpy.random.permutation` with seed: ideal but
     in-memory, doesn't stream, awkward at large `P`. FF1/FF3 in
     cycle-walking mode: streaming and keyed but heavyweight
     framework. Sort-by-i.i.d.-key: `O(N log N)` extra memory and
     not deterministic across implementations. BIDDER: streaming +
     keyed + arbitrary `P` + measurable FPC realisation. (One
     paragraph; the head-to-head.)
   - **Figure.** Three-curve variance-vs-`N` plot at one chosen
     `(P, f, key family)`: BIDDER measured, ideal FPC theory,
     i.i.d. baseline. BIDDER and ideal FPC overlay closely; both
     drop to zero at `N = P`; the i.i.d. line tracks `σ²/N`
     throughout and lands at `σ²/P` at `N = P`. (Generated by
     `use_case_06_variance_mc`.)
   - **Table.** Single `(P, N)` grid showing BIDDER's measured
     variance / ideal FPC ratio. One row pulled from M2's full
     output. The remainder of M2 lives in §6.4 / appendix.
   - **Code.** `bidder-stat/replication/use_case_06_variance_mc.{c,py}`.
     ~30 lines C + ~20 lines Python. `make use_case_06`
     reproduces the figure and the M2 row from a single command.
   - **Payoff.** One sentence: no other single tool gives all of
     {known closed-form variance, exact at `N = P`, streaming,
     keyed-reproducible, arbitrary `P`} simultaneously; BIDDER
     does, at a measured FPC-realisation cost reported by M2.
   - **Use something else when** (template paragraph for every §7
     use case): if your application needs FPC realisation tighter
     than ~5× the ideal at moderate `P`, use FF1 with AES instead
     (DEBTS.md D1). If your application needs cryptographically
     unguessable output, use `secrets.SystemRandom().shuffle()`
     (DEBTS.md D2). BIDDER's contribution is in the regime where
     none of {known variance, exact at `N = P`, streaming, keyed-
     reproducible, arbitrary `P`, zero deps} can be sacrificed
     simultaneously; outside that regime, the comparators above
     are better fits.

*(Open: are these the six? Is one too crypto-adjacent? Audit /
forensic-accounting example as a swap candidate.)*

*(Note for `WORKSET.md` reciprocity: this expansion sharpens M2's
target. M2 is no longer just "tabulate gap-from-ideal across some
grid"; it is "tabulate the BIDDER-vs-ideal-FPC variance ratio on a
`(P, N)` grid, sized so one row supports the §7.6 table and the
full grid supports §6.4.")*

## §8. (folded into §7.4)

The standalone comparison section was folded into §7.4 per the
Phase 0 decision. The four comparators —
`numpy.random.permutation`, `random.shuffle` with seed, FF1/FF3-1,
sort-by-i.i.d.-key — appear in §7.4 as a single table covering
throughput, peak memory, keyed-reproducibility, and domain-size
flexibility. §-numbers below keep their labels for draft-tracking;
the JStatSoft submission's actual numbering is set in Phase 5.

## §9. Limitations

The cards-face-up rule applies here especially: every limitation
named with the magnitude of the gap and a pointer to the to-do
that would close it (DEBTS.md).

- **Not for cryptographic secrets.** Speck32 is a small block
  (32 bits); the 8-round Feistel is non-cryptographic by design.
  Anyone needing PRP-grade randomness should use FF1 / FF3-1 with
  AES, or a CSPRNG-backed shuffle.

- **FPC realisation gap is significant and `(P, N)`-dependent.**
  M2 measures variance ratios from ~1× (small `P`) up to ~32× at
  `(P, N) = (10000, 5000)`. The gap is the empirical price of
  the lightweight cipher choice. (DEBTS.md D1 names a comparator-
  benchmark to-do; D11 a stronger-cipher experiment.)

- **Bias-cancel anomaly at `P = 1000` for `f = sin(πx)`.** M2
  reports variance ratios *below* 1 at this period, indicating
  systematic bias that happens to align with the integrand's
  symmetry. The mechanism is uncharacterised. We don't have a
  model for which `(P, f)` cells exhibit this; the data is the
  data. (DEBTS.md D6.)

- **Cycle-walking → Feistel threshold is conservative.** The
  implementation switches at `P = 2²⁶` (`MAX_CYCLE_WALK_RATIO =
  64`). M1 shows that at the threshold, Speck32 with cycle-walking
  is ~3× slower than Feistel. The throughput-optimal threshold is
  near `P = 2³¹`. The fixed threshold trades a known
  ~2³¹-wide region of suboptimal Speck32 throughput for code
  simplicity. (DEBTS.md D8 — exposing the threshold as a
  parameter.)

- **Period cap `P ≤ 2³² − 1`.** Single-precision design choice;
  `bidder_root.h` types the period as `uint64_t` but the cipher
  cap is the cycle-walking domain (Speck32's `2³²`). Users
  needing larger `P` are out of scope.

- **Lucky-cancellation locus.** The smooth condition
  `n² | b^(d-1)` and Family E together cover only a fraction of
  the `(b, n, d)` triples where exact uniformity holds. A
  brute-force sweep (`b ≤ 12, d ≤ 5`) finds 22,205 triples that
  give exact uniformity but lie outside both families;
  `core/BLOCK-UNIFORMITY.md` documents this and notes no closed
  form is known. The paper inherits this limitation: §3's exact
  claims cover the smooth and Family E regions; outside them the
  spread bound (≤ 2) is the best the paper offers.

- **Throughput numbers are wrapper-dominated.** M3 / M4 measure
  ~1 µs / call through the Python ctypes wrapper; the C kernel is
  sub-microsecond. Users wanting peak throughput should call the
  C kernel directly. (DEBTS.md D4 — C-direct benchmark to-do; D12
  — quickstart-from-C documentation.)

- **Absolute normality of `C_b(n)` is out of scope.** The
  ACM-Champernowne digit-stream is normal in its base of
  concatenation (Copeland–Erdős 1946); normality across other
  bases is open and not addressed by this paper. The paper's
  exactness claims are about the *integer / sieved block lemma*,
  not about the digit-stream as a real number.

- **Comparators not benchmarked numerically.** §7.4 / M3 cite
  FF1, FF3-1, `secrets.SystemRandom`, and `os.urandom`-based
  shuffles as comparators but only run M3 against subset that
  excludes them. The qualitative conclusions (FF1 wins on
  cryptographic strength + FPC tightness; `secrets.SystemRandom`
  wins on unguessable randomness) are committed in the paper;
  numbers are deferred to DEBTS.md (D1, D2, D3).

## §10. Discussion

One short paragraph. The substrate-and-cipher split as a design
principle: keep the algebra exact, keep the cipher opaque, don't
ask either to do the other's job.

## §11. References

- Copeland & Erdős (1946). The base-`b` normality of `C_b(n)`.
- Schiffer (1986). Discrepancy of Champernowne-type concatenations.
- Beaulieu, Treatman-Clark, Shors, Weeks, Smith & Wingers (2013).
  *The Simon and Speck Families of Lightweight Block Ciphers.*
  IACR Cryptology ePrint Archive 2013/404. Cited from §4.2 (the
  cipher choice).
- Black & Rogaway (2002). *Ciphers with Arbitrary Finite Domains.*
  CT-RSA 2002, LNCS 2271, 114–130. The cycle-walking construction
  for format-preserving encryption. Cited from §4.2 (cycle-walking)
  and §4.3 (Feistel fallback).
- NIST SP 800-38G (2016, errata 2019). Recommendation for Block
  Cipher Modes of Operation: Methods for Format-Preserving
  Encryption (FF1/FF3-1). Cited from §7.4 / §9.
- *(Decide: cite the algebra-side primary docs, or only published
  literature? JStatSoft accepts repo-internal references.)*

The §9 limitations and §7.4 comparators reference unbenchmarked
tools (FF1, FF3-1, `secrets.SystemRandom`, `os.urandom`); the
paper commits qualitative conclusions for these and defers
numerical benchmarks to `paper/DEBTS.md` (D1, D2, D3). The cards-
face-up rule applies: §9 names the gap; DEBTS.md tracks the
work.

---

## Replication archive

Lives in the carved `bidder-stat/` repo per Phase 0. Contents:

- `bidder.py` + `bidder_root.c` + `bidder_root.h` + Speck reference
  impl.
- `tests/theory/` (the three structural-claim tests).
- `tests/test_acm_core.py` (the block-uniformity tests).
- `bidder-stat/replication/use_case_<n>.{c,py}` for each of the six
  use cases.
- Top-level `Makefile` (or `replicate.sh`) that builds, runs tests,
  and reproduces every figure in the paper.

---

## What's not in this paper

- The algebra of `Q_n` and the row-OGF cliff. *Out.*
- The wonders cabinet. *Out.*
- The CF / mult-table empirics. *Out.*
- Any claim that touches absolute normality, `μ`, or
  cross-base behaviour. *Out.*
- The probes framework. *Out.*

If a section starts to require any of those, it is the wrong
section for this paper. The paper is the tool, the proofs that gate
the tool, and the use cases that buy the tool. Nothing else.
