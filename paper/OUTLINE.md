# JStatSoft submission — outline

**Status.** Skeleton. Phase 0 decisions locked (see `WORKSET.md`);
sections named, content gestured at, drafting items live in the
workset.

**Title** (working). *BIDDER: Exact Leading-Digit Sampling with
Keyed Random Access.* Substrate-first ordering: the contribution is
exact leading-digit uniformity over arbitrary `(b, d)` digit-class
blocks (the ACM substrate); the cipher's keyed random access is the
delivery mechanism. Earlier working title (*a keyed reproducible
permutation with exact leading-digit uniformity over arbitrary
`(b, d)` blocks*) led with the cipher half and buried the substrate;
flipped 2026-05-02 per audit.

**Scope.** `core/` + `generator/` only. Algebra side, wonders,
arguments, experiments — out. The paper is a tool paper, not the
substrate manifesto.

**Locked from Phase 0:** 15-page target; `bidder-stat/` carved repo
for replication; C-primary API surface; single author; §8 comparison
folded into §7.4; benchmarks in a §6.4 table plus §6 paragraph.

**Discipline.** No occlusive salesmanship. Every measure on BIDDER
is turned inside out — the paper plays cards face up the whole way.
Concretely: §3.6 / §4.6 close with "what this covers and what it
does not"; §4.4 names BIDDER's permutation contract and presents
endpoint invariance as a bijection-trivial corollary (not
BIDDER-special); §4.5 names the FPC realisation gap with its
measured magnitude (~1× best, ~32× worst); §7.4 includes axes
BIDDER loses on; §9 limitations expand to name every regime where
BIDDER is the wrong tool; gaps the paper flags but doesn't fill
numerically (FF1 / FF3-1, `secrets.SystemRandom`, etc.) live in
`paper/DEBTS.md` and are named by ID in the prose. Where individual
§7 use cases name a comparator, they name only the one whose
presence changes the reader's decision — not a rote "use something
else when…" hedge.

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

One paragraph, ~150 words. *First sentence — the gap, substrate-
first:* exact leading-digit uniformity over arbitrary `(b, d)`
digit-class blocks at any sample size, not asymptotic, not
contingent on power-of-two periods. *Second sentence — the tool:*
an ACM-Champernowne block substrate (counting argument) plus a
Speck32/64 cycle-walking cipher with a Feistel fallback (keyed
random access on arbitrary `[0, P)`). *Third sentence — the
guarantees:* substrate counting (exact leading-digit counts under
`n² | b^(d-1)` and Family E) plus the cipher's stateless keyed-
bijection contract (with endpoint invariance as a corollary).
*Closing — the use cases the tool unlocks.*

## §2. Introduction

Three paragraphs.

- **The gap.** Asymptotic-uniformity claims are the norm; exact
  uniformity over arbitrary `(b, d)` is rare. Most format-preserving
  permutation tooling is locked to power-of-two domains.
- **The construction.** ACM-Champernowne block × Speck32/64
  cycle-walking. The substrate is exact; the cipher provides
  reproducibility and disorder. Neither part is asked to do the
  other's job.
- **The contribution.** A working tool with one substrate
  contract (exact leading-digit counting on `(b, d)` blocks) and
  one cipher contract (stateless keyed bijection of arbitrary
  `[0, P)` for `P ≤ 2³² − 1`), one cipher choice with a fallback,
  a stable C API, and use cases where exactness on arbitrary
  `(b, d)` is load-bearing.

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

- §4.4 **Permutation contract and endpoint invariance.** §4 commits
  BIDDER to a *contract*: for any `period ∈ [2, 2³² − 1]` and any
  key, `bidder_block_at(ctx, ·)` is a stateless bijection of
  `[0, period)` — *stateless* meaning `at(i)` does not mutate
  `ctx` and does not require `at(0), …, at(i-1)` to have been
  called first; *bijection* meaning every output occurs exactly
  once over `i = 0, …, period − 1`; *keyed* meaning identical key
  + period produce identical permutations across runs and
  machines. Composition with §3.5's Hardy random-access
  (`c_K = q·n + r + 1`) inherits the same shape: stateless,
  keyed, deterministic, no precomputation, no enumeration of
  prior atoms. The contract is the load-bearing claim of §4 — not
  any one property comparators lack (FF1 / FF3-1 also produce
  keyed bijections), but the particular *combination* {streaming
  random-access + arbitrary `P ∈ [2, 2³² − 1]` + zero deps + the
  Speck32/Feistel backend} that no other comparator delivers
  simultaneously (§7.4's matrix). *Endpoint invariance
  (corollary).* For any bijection `π : [0, P) → [0, P)` and any
  `f`,

      (1/P) Σ_{i=0}^{P-1} f(π(i)/P) = (1/P) Σ_{k=0}^{P-1} f(k/P) = R(f, P),

  the left-endpoint Riemann sum, since `{π(0), …, π(P-1)}` is the
  same multiset as `{0, …, P-1}`. The identity is bijection-
  trivial — any keyed permutation has it — and is recorded here
  only because §7.6's variance-controlled Monte Carlo cites it as
  the reason BIDDER's variance at `N = P` is machine-ε (no
  cipher-quality argument required at the endpoint). The §4.5
  statistical layer at `N < P` is where the cipher's design
  choices start to matter. Anchor:
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
  minimal Feistel, no library deps). FF1 with AES (D1) lands at
  ratio ~0.92 across the same two cells — sampling-consistent with
  the ideal — at ~19–29× higher per-call cost (§7.4 throughput). The cipher's PRP quality enters the paper here, as a
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

§5 expanded to draft-paragraph granularity. C-primary per Phase 0:
`bidder_root.h` is the canonical surface; `bidder_opaque.h`
(heap-allocated handles, FFI-friendly) is mentioned only as the
basis for the Python binding in §5.4. Each sub-bullet below names
what's in the paragraph and what's deliberately excluded.

- §5.1 **Cipher path.** Three functions from `bidder_root.h`:

      int bidder_cipher_init(bidder_block_ctx *ctx, uint64_t period,
                             const uint8_t *key, size_t key_len);
      int bidder_block_at(const bidder_block_ctx *ctx, uint64_t i,
                          uint32_t *out);
      const char *bidder_block_backend(const bidder_block_ctx *ctx);

  *Contract.* `period ∈ [2, BIDDER_ROOT_MAX_PERIOD_V1 = 2³² − 1]`.
  `key` may be `NULL` only when `key_len == 0` (degenerate-key
  case accepted, not recommended). `bidder_block_at` is stateless
  on the `ctx` — same `(ctx, i)` always yields the same `*out` —
  so callers can run multiple iterators or random-access calls
  against one `ctx`. Returns one of the `BIDDER_ROOT_*` status
  codes; `BIDDER_ROOT_OK` is success, `BIDDER_ROOT_ERR_INDEX` for
  `i >= period`, etc. *Diagnostic:* `bidder_block_backend` returns
  the static string `"speck32"` or `"feistel"` for the backend
  selected at `init` based on `period` (M1's threshold).

- §5.2 **Sawtooth path.** Two functions from `bidder_root.h`:

      int bidder_sawtooth_init(nprime_sequence_ctx *ctx,
                                uint64_t n, uint64_t count);
      int bidder_sawtooth_at(const nprime_sequence_ctx *ctx,
                              uint64_t i, uint64_t *out);

  *Contract.* `n ≥ 2`, `count ≥ 1`. `bidder_sawtooth_at` returns
  the `i`-th n-prime (0-indexed) in ascending order via the
  closed form `c_K = q·n + r + 1` with `(q, r) = divmod(K-1,
  n-1)` where `K = i + 1` (cite §3.5). Constant work in `i`; no
  enumeration. *Range cap:* the result must fit in `uint64_t`;
  otherwise `BIDDER_ROOT_ERR_OVERFLOW`. The cap is the one
  intentional difference from the Python implementation
  (`bidder.sawtooth`), which uses arbitrary-precision integers
  and continues past `2⁶⁴`.

- §5.3 **Composition pattern.** The headline use of the API is
  composing cipher + sawtooth for keyed exact-uniform-leading-
  digit Monte Carlo on a digit-class block. With `b ≥ 2`, `d ≥ 1`,
  and the smooth condition `n² | b^(d-1)` from §3.3, the n-primes
  of `nZ_{>0}` lying in `[b^(d-1), b^d − 1]` number exactly
  `(b−1) · b^(d-1) · (n−1) / n²`, with leading-digit counts
  exactly `b^(d-1) · (n−1) / n²` per digit. The pattern, in
  C-direct form:

      bidder_block_ctx cipher;
      nprime_sequence_ctx saw;
      bidder_cipher_init(&cipher, P, key, key_len);
      bidder_sawtooth_init(&saw, n, P);
      for (uint64_t i = 0; i < N; ++i) {
          uint32_t j;  bidder_block_at(&cipher, i, &j);
          uint64_t a;  bidder_sawtooth_at(&saw, j, &a);
          /* a is in [b^(d-1), b^d - 1] for the smooth (b, n, d);
             leading digit of a is exactly uniform across the block. */
          process(a);
      }

  Where `P` is chosen as the smooth-block atom count from §3.3.
  At `N = P`, the keyed permutation visits every n-prime atom in
  the block exactly once; the structural Riemann-sum identity
  (§4.4) applies; the leading-digit distribution is exact.

- §5.4 **Python binding example** (`bidder.py` and
  `bidder_c_native.py`). The Python wrappers expose the same
  shape as a binding example, not the primary API:

      import bidder
      b = bidder.cipher(P, key)            # BidderBlock
      s = bidder.sawtooth(n, P)            # NPrimeSequence
      for i in range(N):
          atom = s.at(b.at(i))
          process(atom)

  `bidder.py` is the pure-Python implementation; `bidder_c_native.py`
  is the ctypes wrapper over `bidder_opaque.h`. Both expose the same
  Python-level interface. *Throughput note:* the Python wrappers
  add ~1 µs / call of ctypes / interpreter overhead on top of the
  C kernel's sub-µs cost (M3, M4). Users wanting peak throughput
  use the C surface directly; the Python wrappers are for
  prototyping, scripting, and exploratory use.

- §5.5 **Stability promise.** The C surface above is the version
  this paper describes, tagged `bidder-stat-v1.0` at the
  `bidder-stat/` repo. *Stability levels:* (1) ABI-stable across
  patch releases (1.0.x); (2) minor releases (1.x) may *add* to
  the surface but will not change existing function signatures,
  argument semantics, or error-code values; (3) major releases
  (2.x) may break compatibility; the paper covers v1 only. The
  Python wrapper inherits the same promise indirectly: changes
  visible at the Python level track the C surface's stability.

- §5.6 **What the API does not include** (cards-face-up).
  - *No batched random-access.* `bidder_block_at` and
    `bidder_sawtooth_at` operate on one index at a time. Bulk
    callers write a tight loop. (DEBTS.md D13.)
  - *Thread-safety on shared handles is not promised, only
    documented as plausible.* `bidder_block_at` does not mutate
    its `ctx`; concurrent reads from a single `ctx` would not
    race in the current implementation. The paper documents this
    but does not enforce it across versions.
  - *No streaming iterator beyond random-access.* The primitive
    is `at(i)`; iteration is built by the caller. The Python
    wrapper provides `__iter__` for convenience.
  - *No reseeding mid-stream.* Once initialised, the key is
    fixed for the `ctx`'s lifetime. Different keys require a
    fresh `bidder_cipher_init` on a separate `ctx`.
  - *No bignum sawtooth in C.* The C `bidder_sawtooth_at` returns
    `uint64_t`; values that would exceed that report
    `BIDDER_ROOT_ERR_OVERFLOW`. The Python `bidder.sawtooth`
    continues with arbitrary-precision integers — this is the
    one capability difference between the C and Python paths,
    and the paper notes it explicitly so a reader doesn't infer
    parity.

## §6. Implementation

§6 expanded to draft-paragraph granularity, mirroring §3 / §4 / §5.
Each sub-bullet is one paragraph in the final paper. The section is
implementation-shaped (source layout, wiring, tests, performance,
build) rather than theorem-shaped; numbers come from M1 + M4, the
test inventory comes from E4's smoke check.

- §6.1 **Source layout.** *C kernel:* `bidder_root.{c,h}` is the
  user-facing surface (six functions; see §5); `bidder_opaque.{c,h}`
  exposes heap-allocated handle types for FFI use; the kernel is
  `~300` lines of C plus the Speck32/64 reference implementation
  and the unbalanced 8-round Feistel fallback. *Generator:*
  `generator/bidder.{c,h}` holds the cycle-walking driver and the
  block-of-`[0, P)` iterator. *Python wrappers:* `bidder.py` is the
  pure-Python implementation (used as the test oracle and the
  binding example in §5.4); `bidder_c_native.py` is the ctypes
  wrapper over `bidder_opaque.h` exposing the same Python-level
  shape. *No third-party C deps.* The kernel compiles against libc
  alone; the Python wrappers depend on the standard library plus
  numpy for the M1–M4 measurement scripts (numpy is not required to
  use the wrappers).

- §6.2 **Cipher wiring.** One paragraph on how the cycle-walking
  Speck32/64 path and the Feistel fallback compose at runtime.
  *Selection.* `bidder_cipher_init` reads `period` and the
  `MAX_CYCLE_WALK_RATIO` constant (currently fixed at 64; DEBTS.md
  D8) and selects the backend: cycle-walking Speck32/64 when
  `2³² / period ≤ 64` (i.e., `period ≥ 2²⁶`), 8-round unbalanced
  Feistel sized to the period otherwise. The selected backend is
  reported by `bidder_block_backend(ctx)` (a static `"speck32"` or
  `"feistel"` string; §5.1). *Key derivation.* The user-supplied
  `(key, key_len)` is hashed with SHA-256 (the only standard-
  library crypto primitive needed; reference implementation
  bundled in the kernel) and the digest is used as the cipher key
  material — Speck32/64 takes 64 bits; the Feistel round function
  takes 128 bits. *Cycle-walking loop.* `bidder_block_at` calls
  `Speck32_Encrypt` repeatedly until the output lands in
  `[0, period)`; the expected number of calls is
  `2³² / period`, bounded by 64 by construction of the threshold.
  *Feistel path.* The unbalanced Feistel is parameterised on the
  period's bit-width; the round function is a small SHA-256-based
  PRF, deliberately lightweight (DEBTS.md D9 names a stronger-rounds
  variant). The two backends share the `bidder_block_at` signature
  and contract; callers do not need to know which backend ran.

- §6.3 **Test-suite layout.** Three layers, each with a different
  load. *Layer 1 — unit and property tests* (`tests/test_api.py`,
  `tests/test_bidder.py`, `tests/test_bidder_block.py`,
  `tests/test_bidder_root.py`, `tests/test_sawtooth.py`,
  `tests/test_speck.py`): exercise the Python wrappers against the
  C kernel and against the pure-Python oracle, plus property tests
  (bijection-hood at small `P`, Speck round-trip equality, sawtooth
  monotonicity). *Layer 2 — substrate proofs*
  (`tests/test_acm_core.py`): the block-uniformity tests for the
  integer lemma (§3.2), the sieved smooth lemma (§3.3), Family E
  (§3.4), and the spread bound (§3.4). These tests are theorem ==
  implementation: a failure means a §3 claim is wrong, not that the
  cipher is misbehaving. *Layer 3 — structural and statistical
  theory* (`tests/theory/test_riemann_property.py`,
  `tests/theory/test_quadrature_rates.py`,
  `tests/theory/test_fpc_shape.py`): the §4.4 Riemann-sum identity
  at `N = P` (exact equality, machine-ε), Euler-Maclaurin
  convergence rates for representative integrands (`f = x`,
  `sin(πx)`, `x²(1−x)²`, step), and the §4.5 FPC-shape statistical
  test (the test that gates M2's measurements). Total: eleven test
  files; E4 confirms all pass on a clean checkout.

- §6.4 **Performance: throughput table** *(M1 + M3 + M4 + D4
  done).* *Workload taxonomy.* Three workload types are reported
  separately because they measure different things and a reader
  comparing rows across them will draw the wrong conclusion:
  (1) **single random-access call** — one `bidder_block_at(ctx,
  i)` for a single index, the M4-style measurement, the cost of
  BIDDER's API per call. (2) **materialise full permutation** —
  `[bidder.cipher.at(i) for i in range(P)]` through the Python
  wrapper, the M3-style measurement, which builds an `O(P)`
  Python list on top of `P` ctypes calls; the workload that lets
  BIDDER be compared head-to-head with `numpy.random.permutation`.
  (3) **C-direct kernel** — `bidder_block_at` called from C in a
  tight loop, no ctypes overhead, the D4 measurement. Each row in
  the table is tagged with its workload type; readers comparing
  BIDDER to `numpy.random.permutation` should compare workload
  (2) on both sides, not workload (1) to a workload-(2)
  comparator. *Table.* Three rows per path: workload (1) M4
  numbers — cipher ~940 ns/elem, sawtooth ~1300 ns/elem,
  P-independent; workload (2) M3 numbers — cipher ~5400 ns/elem
  at `P = 10⁶`, comparators (numpy ~270 ns/elem, random.shuffle
  ~1900 ns/elem, sort-by-iid-key ~407 ns/elem) listed in §7.4;
  workload (3) D4 numbers — Feistel kernel ~38 ns/call
  (`P < 2²⁶`), Speck32/64 cycle-walking ~2100 ns/call at
  `P ≈ 10⁸` (cycle-walking ratio ~43, scaling with `2³² / P`),
  sawtooth ~3 ns/call (one divmod + arithmetic, backend-
  independent). *Wrapper-overhead reading.* Subtracting workload
  (3) from workload (1) gives the ctypes round-trip cost: cipher
  ~940 − 38 ≈ 900 ns/call, sawtooth ~1300 − 3 ≈ 1300 ns/call.
  The Python wrapper is convenience, not throughput; users
  needing peak throughput call the C surface directly and get
  Feistel ~38 ns/call (kernel) or ~3 ns/call (sawtooth) — sub-µs
  per call as the paper claims. *Decision-boundary paragraph.*
  M1 names the Feistel decision boundary: the implementation's
  threshold (`P = 2²⁶`) is conservative; throughput-optimal
  crossover is near `P ≈ 2³¹`; in the conservative region
  (`2²⁶ ≤ P < 2³¹`), Speck32/64 cycle-walking runs ~3× slower
  than Feistel would on the same `P` (~2820 vs ~930 ns/call
  through the wrapper, scaled accordingly C-direct). Numbers:
  `paper/measurements/m1_results.md`,
  `paper/measurements/m3_results.md`,
  `paper/measurements/m4_results.md`,
  `paper/measurements/d4_results.md`.

- §6.5 **Build and install.** From a clean checkout of
  `bidder-stat/`: `make build` compiles the C kernel into
  `libbidder.dylib` (macOS) / `libbidder.so` (Linux); `make test`
  runs the eleven-file test suite (auto-detects `sage -python` for
  the numpy-dependent suites, falls back to `python3` for the
  C-only tests); `make replicate` runs M1–M4 plus the per-use-case
  scripts and regenerates every figure and table in the paper from
  source. *No configure step, no third-party C deps, no Python
  package install.* The `Makefile` is ~30 lines; the C compile is
  one `cc -O2 -fPIC -dynamiclib` command. The intent is that a
  reviewer with `cc` and a Python with numpy can clone, type
  `make replicate`, and reproduce every number in the paper in a
  few minutes. E4 verifies this on a clean checkout
  (`paper/measurements/e4_smoke.md`). Cross-platform CI is not
  set up — the build is hand-tested on macOS and Linux only;
  Windows users would need to adapt the `Makefile` (the C kernel
  itself is portable).

- §6.6 **What §6 does not include.** Cards-face-up. *No SIMD
  path.* The kernel is portable scalar C; the Speck32/64
  reference is the obvious target for SIMD batching but the paper
  does not include such a variant (DEBTS.md D14). *No batched
  random-access API.* `bidder_block_at` and `bidder_sawtooth_at`
  are one-index-at-a-time; bulk callers write a tight loop
  (DEBTS.md D13, motivated by the wrapper-overhead numbers in
  §6.4). *No thread-safety guarantee on shared handles.* The
  current implementation does not mutate the `ctx` in `at` calls
  (so concurrent reads happen to be safe in practice), but the
  paper does not promise this across versions; concurrent callers
  should use one `ctx` per thread. *No cross-platform CI.* The
  build is hand-tested on macOS and Linux; Windows is unverified
  (the C kernel itself is portable C99 — DEBTS.md D15). *No
  fuzzing harness.* The cipher is exercised by property tests
  (round-trip, bijection-hood at small `P`, Family E membership);
  a libFuzzer / AFL harness is not bundled (DEBTS.md D16). These
  exclusions are deliberate Phase 1 scope cuts; they don't change
  what §6 covers, only what it does not.

## §7. Use cases

Six worked examples. Each ~half a page. Code + numerical result + the
exactness payoff vs the asymptotic alternative.

§7.2, §7.3, §7.4, §7.6 are expanded below to draft-paragraph
granularity (one bullet per intended paragraph; load-bearing claim,
comparator, number, figure or table, code pointer, payoff
sentence). §7.1, §7.5 are gestures awaiting expansion. The §9
limitations and the §7.4 capability matrix carry the cards-face-up
weight for "where BIDDER isn't the right tool"; individual use
cases name a comparator only where its presence changes the
reader's decision. §7.4 is structurally distinct from the other
three expanded cases: it absorbs the head-to-head comparison from
the (now folded) §8, so it carries three comparator notes rather
than one.

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
     `bidder-stat/replication/use_case_02_benford_null.py`
     (~120 lines Python through the C kernel via the wrapper).
     `make use_case_02` reproduces the table.
     Figures (matplotlib, author-side only) live with the PDF.
     Headline numbers: BIDDER χ² = 0 exactly at every (b, d) cell;
     i.i.d. mean / std track the χ²(b-2) prediction across
     1000 trials.
   - **Payoff.** One sentence: the analyst gets a
     deterministic anti-Benford reference with zero sampling
     noise on the leading-digit counts at any block size, so
     the detector's response on this reference reflects the
     detector's properties alone — not the reference's
     finite-sample variance. The substrate's exactness has
     visible cash value here.
   - **Comparator note.** A Benford-*conforming* reference (as
     opposed to the anti-Benford extreme this use case
     constructs) is the i.i.d. sampler from Benford's
     distribution; BIDDER does not provide that and should not
     be miscast as a Benford-conforming tool.
- §7.3 **Reproducible cross-validation** with exact fold sizes on
  non-power-of-two `n`. Cipher-leveraged use case (§4.1 / §4.4 do
  the work; the §3 substrate's leading-digit guarantee is not
  exercised here, and the §4.5 FPC realisation gap does not
  apply since we are partitioning records, not estimating
  variances).
   - **Problem.** A statistician running `k`-fold
     cross-validation on a dataset of size `n` wants four
     properties simultaneously: *reproducible* folds (same key
     → same partition), *exact* fold sizes (each fold has
     `⌊n/k⌋` or `⌈n/k⌉` elements; no sampling deviation),
     *streaming* assignment (no materialised permutation of
     `[0, n)` in memory), and *arbitrary* `n` (the dataset is
     not sized for power-of-two-friendly tooling). Standard
     tools give three of four. (Motivating paragraph.)
   - **Cipher guarantee.** Cite §4.1 (role separation) and §4.4
     (bijection-hood). BIDDER produces a keyed bijection
     `π : [0, n) → [0, n)` for any `n ∈ [2, 2³² − 1]`. *Exact-
     fold construction:* the assignment
     `fold(i) := ⌊π(i) · k / n⌋` partitions `[0, n)` into `k`
     disjoint folds. Fold cardinalities are
     `|{m ∈ [0, n) : ⌊m · k / n⌋ = j}|`, which equals `⌊n/k⌋`
     or `⌈n/k⌉` independent of *which* records land in *which*
     fold. The bijection is what turns approximate-by-hash
     into exact. (Headline payoff.)
   - **Where the §4.5 gap does not enter.** Cross-validation
     uses the fold partition for *evaluation* (training on
     `k − 1` folds, testing on the remaining one), not for
     variance estimation of an integral. The §4.5 FPC
     realisation gap and the §4.4 Riemann-sum identity at
     `N = P` do not enter §7.3's correctness; only the
     bijection property (any keyed bijection of `[0, n)`
     would do, but BIDDER is the bijection that's *also*
     streaming-on-arbitrary-`n`-with-zero-deps).
   - **Comparators.**
     - `numpy.random.permutation(n)` with seed: works for
       fold construction (shuffle, then contiguously
       partition). Reproducible; exact sizes. Loses on
       streaming — materialises `[0, n)`, infeasible at
       `n` larger than RAM.
     - Hash-based bucket assignment (`fold(i) := hash(record_i)
       mod k` for some stable hash). Streaming and
       reproducible (with a fixed hash). Loses on exact
       sizes — fold cardinalities deviate by
       `O(√(n · (k−1) / k²))` (binomial sampling). At
       `n = 10⁶, k = 10`, typical deviation is ~316; max
       across folds is ~950.
     - BIDDER cipher: streaming + reproducible + exact +
       arbitrary `n` + zero deps. The trade-off: ~1 µs / call
       through the Python wrapper vs ~100 ns for a fast hash
       (M3, M4) — ~10× per-record cost for exact sizes.
   - **Figure.** Bar plot of realised fold sizes for
     `(n, k) = (10000, 7)` (so `n / k = 1428.57…`, exposing
     the `⌊⌋ / ⌈⌉` split). Three series: BIDDER (every bar
     either 1428 or 1429, exact); hash-based with 1000 trials
     showing the empirical bin distribution (bars wobble
     around 1428.6 with one-σ band at ±14); `numpy.random.permutation`-
     plus-contiguous-partition (matches BIDDER's exact 1428 /
     1429 — both win on size, but only BIDDER is streaming).
     Generated by `use_case_03_cross_validation`.
   - **Table.** Maximum fold-size deviation across `(n, k) ∈
     {(1000, 5), (10000, 7), (100000, 10), (1000000, 10),
     (1000000, 100)}`. *BIDDER row:* `0` when `k | n`, `1`
     when `k ∤ n`. *Hash row:* mean and 99th-percentile max
     deviation over 1000 trials with `xxhash` (or any stable
     fast hash).
   - **Code.** `bidder-stat/replication/use_case_03_cross_validation.py`
     (~100 lines Python through the C kernel via the wrapper).
     `make use_case_03` runs the panel.
     Headline: BIDDER fold sizes are exactly in `{⌊n/k⌋, ⌈n/k⌉}`
     at every panel cell (max deviation = 0); SHA-256 hash
     baseline grows worst-deviation ~ `O(sqrt(n/k))` (46 at
     n = 1k, 1113 at n = 1M).
   - **Payoff.** One sentence: keyed-reproducible exact-fold-
     size partition on arbitrary `n`, with streaming
     assignment (no materialised permutation), at the cost of
     ~10× per-record overhead vs hash-based — appropriate
     when exact fold sizes are load-bearing for the CV
     protocol (balanced CV variance bounds, regulatory
     fairness audits, cross-implementation reproducibility
     where deviation patterns from different hashes must not
     drift).
   - **Comparator note.** Hash-based bucket assignment is the
     simpler choice when `O(√n/k)` fold-size deviation is
     acceptable; `numpy.random.permutation` with a seed plus
     contiguous partition is the simpler choice when the dataset
     fits in memory. BIDDER's win is the regime where exact +
     streaming + reproducible + arbitrary `n` must hold together.
- §7.4 **Format-preserving permutation of a small-`P` domain.**
  Cipher-leveraged use case (§4.4 is what's load-bearing; §3
  substrate is unused but trivially compatible). *Absorbs the
  head-to-head comparison table per the Phase 0 fold of §8;* the
  capability matrix is the section's single most informative
  artifact and the load-bearing finding for the whole §7.
   - **Problem.** A practitioner needs a keyed reproducible
     bijection of a small-`P` domain. Examples: anonymising
     customer IDs in `[0, 10⁶)` for a deterministic test corpus;
     randomising row order in a finite dataset for staged
     processing where the same key must reproduce the order on
     re-run; deterministically permuting a fixed-size token
     vocabulary across runs of an experiment. FF1 and FF3-1 with
     AES are the reference FPE tools (NIST SP 800-38G), but they
     require an AES library and are sized for cryptographic-
     strength PRP guarantees. For applications that need keyed-
     bijection-on-arbitrary-`P` without the cryptographic-grade
     PRP requirement, the FF1/FF3 framework is overkill;
     for applications that need cryptographic strength, BIDDER is
     not a substitute. The use case is the regime in between.
     (Motivating paragraph.)
   - **Cipher contract.** Cite §4.4: `bidder_block_at` is a
     stateless keyed bijection of `[0, P)` for any `P ∈ [2,
     2³² − 1]`. Streaming + random-access + arbitrary-`P` are
     simultaneously available; same `(key, P)` produces the same
     permutation across runs and machines. The §3 substrate is
     unused here — the use case wants any keyed bijection of an
     arbitrary domain — but the same `bidder.cipher` machinery
     used by §7.6 is the load-bearing primitive. (One paragraph;
     the contract.)
   - **What BIDDER does not provide.** Cards-face-up. Speck32 has
     a 32-bit block and is designed for lightweight (not
     cryptographic-grade) applications; the 8-round Feistel is
     by-construction lightweight. Anyone needing PRP-grade
     unguessability should use FF1 / FF3-1 with AES (NIST SP
     800-38G); D1 measures FF1's FPC realisation ratio at ~0.92
     across two cells (sampling-consistent with the ideal 1.0)
     vs BIDDER's 6.8–32× — FF1 is **7–34× tighter on FPC** at
     the cells measured. Anyone needing CSPRNG-grade randomness
     should use `secrets.SystemRandom().shuffle()`. The use case
     is the regime where these properties are not load-bearing —
     small-domain, reproducible-permutation work where the
     application is not adversarial.
   - **Capability matrix** *(headline artifact, from M3).* Five
     axes: keyed; reproducible; streaming / random-access;
     arbitrary `P`; extra dependencies. Six rows: BIDDER (cipher);
     `numpy.random.permutation`; `random.shuffle`; sort-by-iid-
     key; i.i.d. with replacement; FF1 / FF3-1 (cited, not
     benchmarked). BIDDER is the only row with all of {keyed,
     reproducible, streaming/random-access, arbitrary `P`, zero
     deps}; FF1 / FF3-1 match BIDDER on every axis except
     dependencies (AES + FPE library); the in-memory comparators
     match on keyed + reproducible but lose on streaming; i.i.d.
     with replacement matches on streaming but is not a
     permutation. The matrix is reproduced from
     `paper/measurements/m3_results.md` and is the §7 case where
     the load-bearing finding is qualitative (the *combination*
     of properties), not a single numerical comparison.
   - **Throughput across three workloads** *(M3 + M4 + D4 + D1
     numbers).* Per the §6.4 taxonomy: *workload (1) — single
     random-access call (M4):* BIDDER ~940 ns/elem through the
     wrapper, comparators not measured at this workload (M3
     materialises full permutations). *Workload (2) — materialise
     full permutation (M3 + D1):* BIDDER cipher ~5400 ns/elem at
     `P = 10⁶`; FF1 (AES-128, cycle-walking) ~100,000 ns/elem at
     `P = 10⁶`, ~122,000 ns/elem at `P = 10⁵`, ~147,000 ns/elem
     at `P = 10⁴` (cycle-walking ratio higher at smaller `P`);
     numpy ~270 ns/elem; random.shuffle ~1900 ns/elem;
     sort-by-iid-key ~407 ns/elem. FF1 is **~19–29× heavier than
     BIDDER through the same Python wrapper**; the numpy /
     random.shuffle / sort-by-key comparators win this workload
     because they materialise the permutation natively in
     optimised C / Python. *Workload (3) — C-direct kernel (D4):*
     BIDDER ~38 ns/call (Feistel, `P < 2²⁶`); ~2112 ns/call
     (Speck32 cycle-walking at `P ≈ 10⁸`); FF1 with AES not
     benchmarked C-direct in this paper, but the ~100 µs Python
     figure includes ~20 AES round-trips per FF1 round × 10
     rounds, so a C-direct FF1 would be a small fraction of the
     Python number. The C-direct row is where "lightweight"
     becomes a number: BIDDER's Feistel kernel is sub-µs and
     remains substantially lighter than FF1's per-call cost
     under any wrapper. Numbers:
     `paper/measurements/d1_results.md`.
   - **Code.** `bidder-stat/replication/use_case_04_fpe.py`
     (~110 lines Python through the C kernel). The thinnest of
     the §7 use cases: open `bidder.cipher(P, key)`, iterate
     `block.at(i)` over `i = 0, …, N − 1` to obtain the
     permutation. The use case verifies bijection + determinism
     at 6 small-P points and renders the §7.4 capability matrix
     plus the three-workload throughput row from M3 + D1 + D4
     outputs (it does not re-run those measurements). `make
     use_case_04` builds and prints the matrix.
   - **Payoff.** One sentence: BIDDER is the only comparator
     delivering all of {keyed, reproducible, streaming + random-
     access, arbitrary `P` ∈ [2, 2³² − 1], zero deps}; the
     C-direct Feistel kernel (~38 ns/call) is sub-µs and ~19–29×
     lighter per call than FF1 (AES-128) through the same wrapper
     (D1) — appropriate when keyed-bijection-on-arbitrary-`P` is
     load-bearing but cryptographic-strength PRP is not.
   - **Comparator note.** Three decision-changing comparators.
     *FF1 / FF3-1 with AES* is the right tool when cryptographic-
     grade PRP is required and FPC realisation tighter than ~7×
     of ideal is needed (D1 measures FF1 at ratio ~0.92 vs
     BIDDER at ratio 6.8–32 across two M2 cells); the cost is
     ~19–29× higher per-call throughput than BIDDER (NIST SP
     800-38G). *`numpy.random.permutation` with a seed* is the
     right tool when the dataset fits in memory and streaming is
     not required (M3's workload-(2) winner). *`secrets.SystemRandom
     ().shuffle()`* is the right tool when CSPRNG-grade
     unguessability matters and reproducibility does not. BIDDER's
     win is the regime where keyed + reproducible + streaming +
     arbitrary `P` + zero deps must hold simultaneously.
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
   - **Code.** `bidder-stat/replication/use_case_06_variance_mc.py`
     (~80 lines, Python through the C kernel via the wrapper).
     `make use_case_06` runs it and writes
     `use_case_06_results.md`. Headline numbers (P = 2000,
     n_keys = 200): BIDDER variance at N = P is 6.15e-31
     (machine-ε; floating-point round-off); FPC realisation
     ratio peaks at 7.17 at N = P/2; i.i.d. baseline never drops
     below σ²/P.
   - **Payoff.** One sentence: no other single tool gives all of
     {known closed-form variance, exact at `N = P`, streaming,
     keyed-reproducible, arbitrary `P`} simultaneously; BIDDER
     does, at a measured FPC-realisation cost reported by M2.
   - **Comparator note.** FF1 with AES is the right tool when
     tight FPC realisation is required: D1 measures FF1 at ratio
     ~0.92 (sampling-consistent with the ideal) at the same M2
     cells where BIDDER is 6.8× and 32×, at ~19–29× higher per-
     call cost. Cryptographic-strength randomness is a separate
     concern handled in §9, not by the §7.6 use case.

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
  M2 measures BIDDER variance ratios from ~1× (small `P`) up to
  ~32× at `(P, N) = (10000, 5000)`. D1 measures FF1 (AES-128) on
  the same cells at ratio ~0.92 (sampling-consistent with the
  ideal), at ~19–29× higher per-call cost. The gap is the
  empirical price of BIDDER's lightweight cipher choice. (DEBTS.md
  D11 names a stronger-cipher experiment with a heavier-but-still-
  zero-deps round function.)

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

- **Throughput numbers are workload-dependent and wrapper-aware.**
  Three workloads, three rows (§6.4): single random-access call
  through the Python wrapper ~940 ns/call (M4); materialise full
  permutation through the wrapper ~5400 ns/elem at `P = 10⁶`
  (M3); C-direct kernel ~38 ns/call (Feistel) or ~3 ns/call
  (sawtooth) (D4 — closed). Users wanting peak throughput call
  the C surface directly; the Python wrapper costs ~900 ns/call
  in ctypes overhead. (DEBTS.md D12 — C quickstart documentation
  still pending.)

- **Absolute normality of `C_b(n)` is out of scope.** The
  ACM-Champernowne digit-stream is normal in its base of
  concatenation (Copeland–Erdős 1946); normality across other
  bases is open and not addressed by this paper. The paper's
  exactness claims are about the *integer / sieved block lemma*,
  not about the digit-stream as a real number.

- **Comparators not benchmarked numerically.** §7.4 / M3 cite
  `secrets.SystemRandom` and `os.urandom`-based shuffles as
  comparators but do not benchmark them; the qualitative
  conclusion (these are CSPRNG-grade for unguessable randomness;
  BIDDER doesn't compete with them on randomness quality) is
  committed in the paper. Numbers deferred: DEBTS.md D2, D3. FF1
  is benchmarked (D1, closed): tighter FPC at higher per-call
  cost; FF3-1 is cited but not separately benchmarked since it
  shares FF1's AES backbone.

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
- `bidder-stat/replication/use_case_<n>.py` for each expanded §7
  use case (currently §7.2, §7.3, §7.4, §7.6 — §7.1 and §7.5
  pending). Plus `replication/d1_measure.py` (FF1 comparator,
  closes D1) and `replication/bench_c.c` (C-direct kernel,
  closes D4).
- Top-level `Makefile` (and `replicate.sh`) that builds, runs
  tests, runs M1–M4 + D4 + D1 + the use cases, and reproduces
  every table referenced in the paper. Figures (matplotlib,
  author-side) live with the PDF.

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
