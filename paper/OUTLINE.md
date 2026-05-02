# BIDDER: Exact Leading-Digit Sampling with Keyed Random Access

*Working title; `WORKSET.md` carries the drafting state and the
JStatSoft Phase 0 decisions (15-page target, `bidder-stat/`
replication archive, C-primary API, §8 folded into §7.4).*

---

## §1. Abstract

We present a tool for exact leading-digit uniformity over
arbitrary digit-block parameters `(b, d)`. The construction is two
pieces: an ACM-Champernowne substrate `M_n = {1} ∪ nZ_{>0}`, on
which a counting argument from positional notation gives exactly
`b^(d-1)` integers per leading digit on `[b^(d-1), b^d − 1]` (and
exactly `b^(d-1)·(n−1)/n²` n-prime atoms per leading digit when
`n² | b^(d-1)`); and a keyed cipher that is a stateless bijection
of `[0, P)` for any `P ∈ [2, 2³² − 1]`, implemented as Speck32/64
cycle-walking with an unbalanced Feistel fallback at small `P`. The
substrate is asked only to be exact; the cipher is asked only to
be a reproducible bijection. Their composition gives streaming
random-access to a deterministic anti-Benford reference, exact-
fold partitioning of arbitrary populations, format-preserving
permutation of small domains, and Monte Carlo with a known
endpoint and a measured FPC realisation gap, where the prefix-
mean variance at `N < P` follows the finite-population correction
`σ²/N · (P − N)/(P − 1)` up to a backend-dependent factor that M2
tabulates. The replication archive (~300 lines of C, two pinned
Python dependencies) reproduces every numerical claim from source.

## §2. Introduction

- **The gap.** Asymptotic-uniformity claims about the digit
  distribution of integer-concatenation streams `C_b(n)` go back to
  Copeland and Erdős (1946), who showed that `C_b(n)` is normal in
  base `b`; subsequent work (Schiffer 1986) gives discrepancy
  bounds of order `1/log N`. These results are about averages over
  growing windows, not about counts on a fixed digit-class block.
  Format-preserving permutation tooling — FF1 and FF3-1 with AES
  (NIST SP 800-38G) — supplies keyed bijections of arbitrary
  domains but is sized for cryptographic-grade pseudorandom
  permutations, requiring an AES library and accepting AES-per-
  call cost. There is no tool in the existing literature that
  simultaneously delivers {exact leading-digit uniformity over
  arbitrary `(b, d)` blocks, keyed reproducibility, streaming
  random-access on arbitrary `P`, and zero library dependencies}.
- **The construction — substrate first.** §3 sets up the ACM
  monoid `M_n`, its n-prime atoms (multiples of `n` not divisible
  by `n²`), and the digit-class block `[b^(d-1), b^d − 1]`. The
  integer block-uniformity claim (§3.2 clause 1) is a one-
  paragraph counting argument from positional notation: each
  leading digit `j ∈ {1, …, b−1}` appears exactly `b^(d-1)`
  times. The sieved version (§3.2 clause 2) extends the result
  to n-prime atoms when the smooth condition `n² | b^(d-1)`
  holds. Hardy random-access (§3.2 clause 5) gives the `K`-th
  n-prime in `O(1)` work via the closed form
  `c_K = q · n + r + 1`. §4 supplies the keyed bijection: a
  Speck32/64 cipher in cycle-walking mode (Black & Rogaway 2002)
  for `P ≥ 2²⁶`, with an unbalanced 8-round Feistel fallback for
  smaller `P`. The contract (§4.4) is *stateless keyed random-
  access on arbitrary `P ∈ [2, 2³² − 1]` without materialising the
  permutation*; endpoint invariance at `N = P` is a bijection-
  trivial corollary that any keyed permutation has.
- **The contribution.** A working tool — ~300 lines of C with no
  third-party dependencies; a Python wrapper as a binding example
  — together with two structural contracts (substrate counting,
  cipher bijection), a measurement panel of throughput and FPC-
  realisation numbers (M1 cycle-walking decision rule; M2 FPC gap
  across a `(P, N)` grid; M3 head-to-head comparison; M4 wrapper
  throughput; D1 FF1 / AES comparator; D4 C-direct kernel
  throughput), a stable C API (five functions in `bidder_root.h`),
  and use cases where exactness on arbitrary `(b, d)` or on
  arbitrary `P` is load-bearing.

## §3. The block-uniformity substrate

- §3.1 **Setup.** Let `b ≥ 2` be a base, `d ≥ 1` an integer,
  `n ≥ 2` an integer. The *digit-class block* is the integer
  interval `B_{b,d} := [b^(d-1), b^d − 1]` (the `d`-digit
  base-`b` integers). The *ACM monoid* is `M_n := {1} ∪ nZ_{>0}`;
  its *n-prime atoms* are integers `m ∈ nZ_{>0}` with `n² ∤ m`.
  These are the running parameter set for the rest of §3 and §4.
  Source: `core/BLOCK-UNIFORMITY.md` §opening.

- §3.2 **Theorem (Substrate contract).** Fix `(b, n, d)` with
  `b ≥ 2`, `d ≥ 1`, `n ≥ 2`. The following hold simultaneously
  for the digit-class block `B_{b,d} = [b^(d-1), b^d − 1]`:

   1. **(Integer block-uniformity.)** The integers in `B_{b,d}`
      have leading-digit counts exactly `b^(d-1)` per digit
      `j ∈ {1, …, b−1}`.

   2. **(Smooth-sieved uniformity.)** If `n² | b^(d-1)`, the
      n-prime atoms of `M_n` lying in `B_{b,d}` have leading-
      digit counts exactly `b^(d-1)·(n−1)/n²` per digit.

   3. **(Family E.)** For `n ∈ [b^(d-1), ⌊(b^d−1)/(b−1)⌋]`, the
      n-prime atoms in `B_{b,d}` are exactly `{n, 2n, …, (b−1)n}`
      — one per leading digit. (Disjoint from clause 2 for
      `d ≥ 2`.)

   4. **(Universal spread bound.)** For any `(b, n, d)`, per-
      leading-digit n-prime counts in `B_{b,d}` differ by at
      most 2.

   5. **(Hardy random-access.)** The `K`-th n-prime atom of `M_n`
      is `p_K = n · c_K` with `c_K = q·n + r + 1` where
      `(q, r) = divmod(K − 1, n − 1)`. Computing `p_K` from `K`
      is one divmod and `O(1)` bignum work; no enumeration.

  Anchors: `tests/test_acm_core.py` for clauses 1–4; the C
  kernel's `bidder_sawtooth_at` plus
  `tests/theory/test_riemann_property.py` for clause 5. Source:
  `core/BLOCK-UNIFORMITY.md` and `core/HARDY-SIDESTEP.md`.

- §3.3 **Proof sketches.** Clause 1: a `d`-digit base-`b`
  integer is `d_1 d_2 … d_d` with `d_1 ∈ {1, …, b−1}` and the
  remaining `d−1` positions free over `{0, …, b−1}`; each `d_1`
  accounts for `b^(d-1)` integers. Clause 2: under
  `n² | b^(d-1)`, each leading-digit strip of length `b^(d-1)`
  starts at a multiple of `n²`; multiples of `n` per strip are
  `b^(d-1)/n`, multiples of `n²` are `b^(d-1)/n²`; subtracting
  gives the per-strip n-prime count, independent of strip.
  Clause 3: for `n` in the named range, the only n-prime atoms
  ≤ `b^d − 1` are `n, 2n, …, (b−1)n`, and these have leading
  digits `1, 2, …, b−1` exactly. Clause 4: the same divmod
  argument applied to a generic interval bounds the count
  difference by 2. Clause 5: the n-primes are an arithmetic
  progression with one residue class deleted per period of `n`,
  so the inverse to "the K-th term" is one divmod and constant
  arithmetic.

- §3.4 **What §3 covers and what it does not.**
  *Covered:* clauses 1–3 are exact on their respective regimes;
  clause 4 is universal but weaker than exact; clause 5 is exact
  and `O(1)` for any `K`.
  *Not covered:* discrepancy of `C_b(n)` away from block
  boundaries — Schiffer (1986) gives `Θ(1/log N)`, not exact; the
  *lucky-cancellation locus* where `n² ∤ b^(d-1)` and Family E
  doesn't apply but exact uniformity still holds (a brute-force
  sweep at `b ≤ 12, d ≤ 5` finds 22,205 such triples; no closed
  form known — `core/BLOCK-UNIFORMITY.md`, §9, DEBTS.md);
  absolute normality of `C_b(n)` across bases (open; out of
  scope). The cipher in §4 composes with the substrate contract
  on the ranges where the contract holds; it does not extend the
  contract. The paper's exactness claims live where the contract
  covers them, not elsewhere.

## §4. The cipher path

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
  specification. *Cycle-walking:* given a cipher on `[0, 2^32)`
  and a target `[0, P)`, repeat `Encrypt(x)` until the output
  lands in `[0, P)`; the result is a bijection of `[0, P)`
  [Black & Rogaway, 2002]. Expected calls per output: `2^32 / P`,
  ≈ 1 when `P` is not too close to `2^32`. Source: `generator/`.

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
  machines. Composition with §3.2 clause 5's Hardy random-access
  (`c_K = q·n + r + 1`) inherits the same shape: stateless,
  keyed, deterministic, no precomputation, no enumeration of
  prior atoms. The contract is the load-bearing claim of §4 — not
  any one property comparators lack (FF1 / FF3-1 also produce
  keyed bijections), but the particular *combination* {streaming
  random-access + arbitrary `P ∈ [2, 2³² − 1]` + zero deps + the
  Speck32/Feistel backend} that no other comparator delivers
  simultaneously (§7.4's matrix). All exactness claims downstream
  use only this bijection contract; cipher quality enters only in
  §4.5. *Endpoint invariance (corollary).* For any bijection
  `π : [0, P) → [0, P)` and any `f`,

      (1/P) Σ_{i=0}^{P-1} f(π(i)/P) = (1/P) Σ_{k=0}^{P-1} f(k/P) = R(f, P),

  the left-endpoint Riemann sum, since `{π(0), …, π(P-1)}` is the
  same multiset as `{0, …, P-1}`. The identity is bijection-
  trivial — any keyed permutation has it — and is recorded here
  only because §7.6's Monte Carlo with known endpoint cites it as
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
  (BIDDER / ideal) across a `(P, N)` grid. The gap is significant
  and `(P, N)`-dependent. Best ratio in the
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

- §4.6 **What §4 covers and what it does not.**
  *What it covers:* a keyed reproducible bijection on
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

C-primary: `bidder_root.h` is the canonical surface; `bidder_opaque.h`
(heap-allocated handles, FFI-friendly) is the basis for the Python
binding in §5.4.

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
  n-1)` where `K = i + 1` (cite §3.2 clause 5). Constant work in `i`; no
  enumeration. *Range cap:* the result must fit in `uint64_t`;
  otherwise `BIDDER_ROOT_ERR_OVERFLOW`. The cap is the one
  intentional difference from the Python implementation
  (`bidder.sawtooth`), which uses arbitrary-precision integers
  and continues past `2⁶⁴`.

- §5.3 **Composition pattern.** The headline use of the API is
  composing cipher + sawtooth for keyed exact-uniform-leading-
  digit Monte Carlo on a digit-class block. With `b ≥ 2`, `d ≥ 1`,
  and the smooth condition `n² | b^(d-1)` from §3.2 clause 2, the n-primes
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

  Where `P` is chosen as the smooth-block atom count from §3.2 clause 2.
  At `N = P`, the keyed permutation visits every n-prime atom in
  the block exactly once; the structural Riemann-sum identity
  (§4.4) applies; the leading-digit distribution is exact.
  *Caveat on prefixes.* For `N < P`, the loop visits a keyed
  prefix of the permuted block. Prefixes are *not* guaranteed
  leading-digit exact: §3's exactness claims hold on complete
  digit-class blocks (or certified sieved blocks), not on
  arbitrary prefixes of permuted blocks. Applications that need
  exact leading-digit counts at `N < P` must sample stratified by
  digit (per §7.1).

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

- §5.6 **What the API does not include.**
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

- §6.1 **Source layout.** *C kernel:* `bidder_root.{c,h}` is the
  user-facing surface (five functions; see §5); `bidder_opaque.{c,h}`
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

- §6.2 **Cipher wiring.** How the cycle-walking Speck32/64 path
  and the Feistel fallback compose at runtime.
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
  substrate-contract clauses (§3.2 clauses 1–4: integer, smooth-
  sieved, Family E, spread bound). These tests are theorem ==
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
  ~38 ns/call (Feistel, `P < 2²⁶`) or ~3 ns/call (sawtooth).
  Where the cipher operates in the Speck32/64 cycle-walking
  regime (`P ≥ 2²⁶`) the per-call cost rises with the cycle-
  walking ratio `2³² / P` — ~2112 ns/call at `P ≈ 10⁸`, the
  D4 panel's Speck32 point — and the "sub-µs per call" framing
  applies only to the Feistel region. *Decision-boundary
  paragraph.*
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
  `bidder-stat/`: `make venv` bootstraps a locked Python
  environment (numpy + pycryptodome, pinned in `requirements.txt`);
  `make build` compiles the C kernel into `libbidder.dylib`
  (macOS) / `libbidder.so` (Linux); `make test` runs the
  eleven-file test suite against the venv; `make replicate` runs
  M1–M4, D1, D4, and the four §7 use-case scripts, regenerating
  every table the paper cites. *No configure step, no third-party
  C deps in the kernel, two pinned Python deps for the comparison
  row.* The `Makefile` is ~80 lines; the C compile is one
  `cc -O2 -fPIC -dynamiclib` command. A reviewer with `cc` and
  Python 3 can clone, type `make venv && make replicate`, and
  reproduce every number in the paper in a few minutes. E4
  verifies this on a clean checkout
  (`paper/measurements/e4_smoke.md`). Cross-platform CI is not
  set up — the build is hand-tested on macOS and Linux only;
  Windows users would need to adapt the `Makefile` (the C kernel
  itself is portable C99).

- §6.6 **What §6 does not include.** *No SIMD path.* The kernel
  is portable scalar C; Speck32/64 is the obvious target for SIMD
  batching but the paper does not include such a variant
  (DEBTS.md D14). *No batched random-access API.*
  `bidder_block_at` and `bidder_sawtooth_at` are one-index-at-a-
  time; bulk callers write a tight loop (DEBTS.md D13, motivated
  by the wrapper-overhead numbers in §6.4). *No thread-safety
  guarantee on shared handles.* The current implementation does
  not mutate the `ctx` in `at` calls (so concurrent reads happen
  to be safe in practice), but the paper does not promise this
  across versions; concurrent callers should use one `ctx` per
  thread. *No cross-platform CI.* The build is hand-tested on
  macOS and Linux; Windows is unverified (DEBTS.md D15). *No
  fuzzing harness.* The cipher is exercised by property tests
  (round-trip, bijection-hood at small `P`, Family E membership);
  a libFuzzer / AFL harness is not bundled (DEBTS.md D16).

## §7. Use cases

Worked examples, each ~half a page: code + numerical result +
exactness payoff vs the asymptotic alternative. Five cases:
§7.1, §7.2, §7.3, §7.4, §7.6. §7.4 absorbs the head-to-head FPE
comparison (folded §8 per Phase 0).

- §7.1 **Stratified survey design with exact leading-digit
  strata.** Substrate-leveraged use case (§3.2 clauses 1–2 do the
  work; the cipher delivers per-stratum random access).
   - **Problem.** A survey designer drawing a sample of size
     `N_total` from a finite population whose elements are
     indexed by the digit-class block `B_{b,d}` wants strata
     defined by leading digit. Standard practice: post-stratify
     after sampling (drawing i.i.d. samples and discarding those
     that overshoot a stratum's quota), or proportional-allocate
     with `N_total · π_j` per stratum and accept binomial
     deviation in the realised counts. The designer wants
     *exact* per-stratum counts (`N_j` records with leading
     digit `j`, no over- or under-shoot) so that downstream
     stratified-sample variance estimators are valid without
     post-hoc weight adjustment.
   - **Substrate contract.** Cite §3.2 clause 1: in base `b`,
     the integers in `B_{b,d}` partition exactly into
     leading-digit strata of size `b^(d-1)` each. Choosing
     `N_j = ⌊α_j · b^(d-1)⌋` for design weights `α_j ∈ [0, 1]`
     gives an allocation realisable as a per-stratum prefix of
     a keyed permutation of stratum `j`. (Cite §3.2 clause 2 for
     the n-prime variant.)
   - **Per-stratum random access.** Cite §4.4: BIDDER provides a
     keyed bijection of `[0, b^(d-1))` per stratum, so the `i`-th
     record in stratum `j` is `b^(d-1)·(j-1) + bidder.cipher.at(i)`
     for `i ∈ [0, N_j)`. Each stratum's prefix samples are keyed-
     reproducible, exact-sized, and streaming. The full sample of
     size `Σ_j N_j` is the union of `b-1` keyed prefixes, one per
     stratum.
   - **Comparator.** Proportional-allocation by post-stratify-
     after-i.i.d.-sampling: realised stratum sizes are
     `Binomial(N_total, π_j)` with standard deviation
     `√(N_total · π_j · (1 − π_j))` per stratum. At
     `N_total = 9000`, `π_j = 1/9`, the per-stratum std is ~31;
     the maximum over 9 strata is typically ~70–100 records.
     BIDDER's per-stratum count is `N_j` exactly.
   - **Table.** Realised stratum sizes for
     `(b, d) = (10, 4)` with proportional allocation `α_j = 0.1`
     across panels `N_total ∈ {900, 9000, 90000}`. *BIDDER row:*
     stratum sizes are `N_j` exactly at every cell. *i.i.d.-then-
     post-stratify row:* mean ± std and max-deviation across
     1000 trials, scaling as `√N_total`.
   - **Code.**
     `bidder-stat/replication/use_case_01_stratified_survey.py`
     (~140 lines Python through the C kernel via the wrapper).
     `make use_case_01` reproduces the table.
     Headline numbers: BIDDER per-stratum count is exact at every
     α (100, 500, 1000 across the panel); i.i.d.-then-post-
     stratify 99th-percentile max deviation across 9 strata
     grows from 31 (α = 0.1, N_total = 900) to 97 (α = 1.0,
     N_total = 9000).
   - **Payoff.** One sentence: exact per-stratum counts enable
     stratified-sample variance estimators to use design weights
     directly, without post-hoc adjustment for realised stratum
     sizes — a ~`√N_total`-magnitude correction the i.i.d.-then-
     post-stratify approach would otherwise carry.
- §7.2 **Benford-test null distribution** as a deterministic
  reference. Working title: *Anti-Benford reference for Benford-
  detector calibration*. Substrate-leveraged use case (§3.2
  clauses 1–2 do the work; the cipher's role is incidental).
   - **Problem.** A forensic auditor or quantitative
     statistician is calibrating a Benford detector
     (chi-squared test, mean-absolute-deviation, KS variant)
     and needs to characterise the detector's response on a
     *known anti-Benford* reference — the "data is uniformly
     distributed across leading digits" extreme, the opposite
     end from Benford-conforming. Standard practice: simulate
     i.i.d. uniform samples, accept sampling-noise-driven
     deviation in the leading-digit histogram. The analyst wants
     a reference with *zero* deviation in the leading-digit
     counts at any size, so the detector's response is purely a
     function of the detector, not of the reference's sampling
     noise.
   - **Substrate guarantee, integer level.** Cite §3.2
     clause 1: in base `b`, the integers in
     `[b^(d-1), b^d − 1]` have leading-digit counts of exactly
     `b^(d-1)` per digit `j ∈ {1, …, b−1}`. Counting argument
     from positional notation; no error term. The full block has
     `(b−1) · b^(d-1)` integers; partitioned by leading digit,
     each bin has exactly `b^(d-1)`.
   - **Substrate guarantee, sieved level.** Cite §3.2 clause 2:
     when the analyst wants n-prime atoms rather than raw
     integers (e.g., to reuse BIDDER's `bidder.sawtooth` output
     as a corpus), the smooth condition `n² | b^(d-1)` gives
     exactly `b^(d-1)(n − 1)/n²` n-primes per leading digit.
     Outside smooth, clause 4 (the spread bound) caps per-digit
     imbalance at 2 — sampling-noise-free even when exactness
     fails. Clause 3 (Family E) provides exact uniformity in a
     disjoint range.
   - **Comparator.** i.i.d. uniform samples from
     `Uniform({1, …, b·b^(d-1)−1})`. At sample size
     `N = (b−1)·b^(d-1)` (matching the block's atom count),
     each leading-digit bin has expected count `b^(d-1)` but
     with sampling standard deviation
     `√(N · (1/(b−1)) · ((b−2)/(b−1)))`. The Pearson
     chi-squared statistic with `b−2` degrees of freedom
     (for `b−1` bins) has mean `b−2` and standard deviation
     `√(2(b−2))` under the null — never exactly zero.
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
     noise on the leading-digit counts on a *complete* digit-
     class block (or certified sieved block), so the detector's
     response on this reference reflects the detector's
     properties alone — not the reference's finite-sample
     variance. The substrate's exactness has visible cash value
     here.
   - **Caveat on prefixes.** §3's exact counts hold on complete
     digit-class blocks. A keyed prefix `N < P` of a permuted
     block is *not* guaranteed leading-digit exact; for exact
     prefix samples at `N < P`, sample stratified by digit
     (§7.1).
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
     tools give three of four.   - **Cipher guarantee.** Cite §4.1 (role separation) and §4.4
     (bijection-hood). BIDDER produces a keyed bijection
     `π : [0, n) → [0, n)` for any `n ∈ [2, 2³² − 1]`. *Exact-
     fold construction:* the assignment
     `fold(i) := ⌊π(i) · k / n⌋` partitions `[0, n)` into `k`
     disjoint folds. Fold cardinalities are
     `|{m ∈ [0, n) : ⌊m · k / n⌋ = j}|`, which equals `⌊n/k⌋`
     or `⌈n/k⌉` independent of *which* records land in *which*
     fold. The bijection is what turns approximate-by-hash
     into exact.   - **Where the §4.5 gap does not enter.** Cross-validation
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
  substrate is unused but trivially compatible). The capability
  matrix is the section's single most informative artifact and
  the load-bearing finding for the whole §7.
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
       - **Cipher contract.** Cite §4.4: `bidder_block_at` is a
     stateless keyed bijection of `[0, P)` for any `P ∈ [2,
     2³² − 1]`. Streaming + random-access + arbitrary-`P` are
     simultaneously available; same `(key, P)` produces the same
     permutation across runs and machines. The §3 substrate is
     unused here — the use case wants any keyed bijection of an
     arbitrary domain — but the same `bidder.cipher` machinery
     used by §7.6 is the load-bearing primitive.
   - **Capability matrix** *(from M3).* Five
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
   - **Scope.** The §7.4 use case fits non-adversarial
     reproducible-permutation work where cryptographic-grade PRP
     and tight FPC realisation are not load-bearing. Where they
     are, see §9 (PRP strength, FPC realisation gap, comparator
     baselines).
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
     becomes a number: BIDDER's Feistel kernel (`P < 2²⁶`) is
     ~38 ns/call, sub-µs and substantially lighter than FF1's
     per-call cost under any wrapper. The Speck32 cycle-walking
     regime (`P ≥ 2²⁶`) costs ~2112 ns/call at the panel's
     `P ≈ 10⁸` point and scales with `2³² / P`; even there BIDDER
     remains lighter than FF1's ~100 µs Python figure. Numbers:
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
     C-direct Feistel kernel (~38 ns/call, `P < 2²⁶`) is sub-µs
     and ~19–29× lighter per call than FF1 (AES-128) through the
     same wrapper (D1), and the Speck32 regime (~2112 ns/call at
     `P ≈ 10⁸`) remains lighter than FF1 — appropriate when
     keyed-bijection-on-arbitrary-`P` is load-bearing but
     cryptographic-strength PRP is not.
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
- §7.6 **Monte Carlo with known endpoint and measured FPC
  realisation gap.** An analyst running prefix-mean Monte Carlo
  on a finite population `[0, P)` who wants the estimator's
  variance pinned at the endpoint (`N = P` is exactly zero, no
  estimation), the shape at `N < P` known up to a measured gap
  from ideal-permutation FPC (rather than estimated from data),
  reproducibility across runs (same key → same sequence), and
  streaming (no materialised permutation of `[0, P)` in memory).
  No single existing tool delivers all four.
   - **Structural guarantee at `N = P`.** Cite §4.4: the prefix
     mean equals the left-endpoint Riemann sum exactly, for any
     key, any `f`. Variance across keys at `N = P` is machine-ε.
     Comparator: an i.i.d. estimator has variance `σ²/P` at
     `N = P`, never zero.
   - **Statistical shape at `N < P`.** Cite §4.5: prefix-mean
     variance follows `σ²/N · (P − N)/(P − 1)` for an ideal
     uniform permutation. BIDDER realises this shape with a
     backend-dependent gap; the gap is what M2 tabulates across
     a `(P, N)` grid.
   - **Comparators.** i.i.d. with replacement: loses FPC,
     suboptimal variance at every `N`. `numpy.random.permutation`
     with seed: ideal but in-memory, doesn't stream, awkward at
     large `P`. FF1/FF3 in cycle-walking mode: streaming and keyed
     but heavyweight framework. Sort-by-i.i.d.-key: `O(N log N)`
     extra memory and not deterministic across implementations.
     BIDDER: streaming + keyed + arbitrary `P` + measurable FPC
     realisation.
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
     {known endpoint at `N = P`, measured FPC realisation gap at
     `N < P`, streaming, keyed-reproducible, arbitrary `P`}
     simultaneously; BIDDER does, with the realisation gap
     tabulated in M2.
   - **Comparator note.** FF1 with AES is the right tool when
     tight FPC realisation is required: D1 measures FF1 at ratio
     ~0.92 (sampling-consistent with the ideal) at the same M2
     cells where BIDDER is 6.8× and 32×, at ~19–29× higher per-
     call cost. Cryptographic-strength randomness is a separate
     concern handled in §9, not by the §7.6 use case.

## §8. (folded into §7.4)

The standalone comparison section was folded into §7.4 per the
Phase 0 decision. JStatSoft renumbering happens at template
conversion (Phase 5).

## §9. Limitations

Each limitation names the magnitude of the gap and points at the
to-do that would close it (`DEBTS.md`).

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
  Three workloads, three rows (§6.4): wrapper single random-
  access call ~940 ns/call (M4); wrapper materialise-full-perm
  ~5400 ns/elem at `P = 10⁶` (M3); C-direct kernel ~38 ns/call
  Feistel (`P < 2²⁶`) and ~2112 ns/call Speck32 cycle-walking at
  `P ≈ 10⁸` (D4); sawtooth ~3 ns/call (backend-independent).
  Users wanting peak throughput call the C surface directly; the
  Python wrapper costs ~900 ns/call in ctypes overhead. The
  "sub-µs per call" claim applies only to the Feistel region;
  the Speck32 cycle-walking region's per-call cost scales with
  `2³² / P`. (DEBTS.md D12 — C quickstart documentation still
  pending.)

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

The substrate-and-cipher split is the design principle the rest of
the paper instantiates. The substrate is asked to be *exact* —
counting arguments, no error term, no asymptotics — and the cipher
is asked to be *opaque and reproducible*: a keyed bijection of
`[0, P)`, nothing more. Neither piece is asked to do the other's
job. The substrate doesn't randomise; the cipher doesn't guarantee
a digit-distribution property. Where the two compose (§5.3 — the
canonical "exact-uniform-leading-digit Monte Carlo on a smooth
`(b, n, d)` block"), the substrate's exactness claims survive
because they are claims about multisets and arithmetic
progressions, invariant under any bijection. The principle is
recoverable in other settings: when an algebraic structure already
delivers the property an application needs, a cipher's job is to
be a bijection over the structure, not to recreate the property
inside the cipher. What this paper does not address — algebraic
structure of `Q_n`, normality of `C_b(n)` across bases, or
characterisation of the lucky-cancellation locus where exact
uniformity holds outside the smooth and Family E regimes — is
acknowledged in §9 and out of scope here.

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

---

## Replication archive

Lives in the carved `bidder-stat/` repo per Phase 0. Contents:

- `bidder.py` + `bidder_root.c` + `bidder_root.h` + Speck reference
  impl.
- `tests/theory/` (the three structural-claim tests).
- `tests/test_acm_core.py` (the block-uniformity tests).
- `bidder-stat/replication/use_case_<n>.py` for each §7 use
  case (§7.1, §7.2, §7.3, §7.4, §7.6). Plus
  `replication/d1_measure.py` (FF1 comparator, closes D1) and
  `replication/bench_c.c` (C-direct kernel, closes D4).
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
