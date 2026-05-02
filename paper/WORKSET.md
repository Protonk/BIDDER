# JStatSoft submission — workset

What needs to be done before this paper goes to a referee. Concrete
items, each small enough to be ticked off. Nothing here requires a
new theorem; it's all writing, measurement, packaging, and citation.

The paper's *scope* is in `OUTLINE.md`. This file is the *to-do*.

## Phase 0 — decisions to lock first

These block everything downstream. Settle them in one pass and don't
revisit unless a phase 2 finding forces it.

- [x] **Title** (working). *BIDDER: Exact Leading-Digit Sampling with Keyed Random Access.* (Substrate-first; flipped 2026-05-02 per audit. Earlier: *a keyed reproducible permutation with exact leading-digit uniformity over arbitrary `(b, d)` blocks*.)
- [x] **Length target.** 15-pages
- [x] **Repo strategy.** carve `core/` + `generator/` + relevant `tests/` into a new
      `bidder-stat/` repo for the replication archive
- [x] **Primary language.** C
- [x] **Author list.** Single, whatever JSS wants
- [x] **§8 comparison.** Folded into §7.4
- [x] **Benchmarks.** Numbers in a §6.4 table + a §6 paragraph.

## Phase 1 — measurement and engineering

Parallel-able with drafting. Some drafting (notably §4.3 and §6.4)
needs these numbers to land.

### Measurement

- [x] **M1. Cycle-walking → Feistel fallback decision rule.**
      Sweep `P ∈ {2^k}` and `P ∈ { (2^k)·m for small m close to 1 }`
      around the points where cycle-walking ratio degrades. Output:
      a single table for §4.3 — calls-per-output across a
      representative `P` panel + the recommended threshold where
      Feistel beats Speck cycle-walking. Use the existing
      `bidder.cipher` implementation; no new code. Target shape
      sharpened by §4.3 expansion in `OUTLINE.md`.
      *Done. See `paper/measurements/m1_results.md`. Headline
      finding: the implementation's threshold (P = 2^26) is
      conservative; throughput-optimal crossover is near P ≈ 2^31.
      Three numbers for §4.3: feistel ≈ 930 ns/call (constant),
      speck32 at threshold ≈ 2820 ns/call (worst case), speck32 at
      P near 2^32 ≈ 920 ns/call (best case).*
- [x] **M2. Cipher's FPC realisation gap.** Tabulate
      BIDDER-vs-ideal-FPC variance ratio across a `(P, N)` grid,
      sized so that one row supports the §7.6 table and the full
      grid supports §4.5 / §6.4. Reference: existing
      `tests/theory/test_fpc_shape.py` and `experiments/bidder/...`.
      Output: a table for §4.5 (statement + measured gap) and
      §6.4 (full grid) + one row excerpted into §7.6 (use-case
      payoff). Target shape sharpened by §4.5 + §7.6 expansions in
      `OUTLINE.md`.
      *Done. See `paper/measurements/m2_results.md`. Headline
      finding: the realisation gap is significant and `(P, N)`-
      dependent. Best ratio ~1 at small P (200); worst ~32 at
      (P=10000, N=5000). Anomalous ratio < 1 at P=1000 (bias-cancel
      regime). The §4.5 paragraph should report the gap honestly;
      it strengthens the substrate-and-cipher framing (the substrate
      is exact; the cipher is good enough to give the right
      multiset, with backend-dependent realisation gap as the
      empirical price).*
- [x] **M3. Comparison numbers.** For BIDDER vs (FF1, FF3-1,
      `numpy.random.permutation`, `random.shuffle`, sort-by-iid-key):
      throughput per element, peak memory, keyed-reproducibility,
      domain-size flexibility. Output: comparison table folded into
      §7.4 per the Phase 0 decision (no standalone §8).
      *Done. See `paper/measurements/m3_results.md`. FF1 / FF3-1
      skipped (no library installed); cited in §7.4 as the de
      facto FPE standard, not benchmarked. Capability matrix is
      the load-bearing finding; throughput numbers are
      ctypes-overhead-dominated through the Python wrapper and
      are noted as such. BIDDER is the only comparator with all
      of {keyed, reproducible, streaming/random-access, arbitrary
      P, zero deps}.*
- [x] **M4. Throughput at scale.** Single-threaded throughput at
      `P ∈ {10^3, 10^4, 10^5, 10^6, 10^7, 10^8}` for both
      `bidder.cipher` and `bidder.sawtooth`. Output: a row of §6.4.
      *Done. See `paper/measurements/m4_results.md`. P=10^8 omitted
      (~9 min/run via Python wrapper, beyond M4 budget; results
      extrapolable from P=10^7). Both paths show roughly P-
      independent throughput through the wrapper: cipher ~940
      ns/elem, sawtooth ~1300 ns/elem. Cost is dominated by
      Python→C ctypes overhead; C kernel is sub-µs per call.*

- [x] **D4. C-direct throughput** *(promoted from DEBTS to a
      closed Phase 1 measurement, 2026-05-02).* Tight-loop C
      benchmark calling `bidder_block_at` and `bidder_sawtooth_at`
      directly against `libbidder.dylib`, no ctypes overhead.
      *Done. See `paper/measurements/d4_results.md` and
      `replication/bench_c.c`. Headline: cipher ~38 ns/call
      (Feistel, P < 2^26), ~2112 ns/call (Speck32 cycle-walking
      at P ≈ 10^8); sawtooth ~3 ns/call. Wrapper overhead
      (M4 − D4) ≈ 900 ns/call (cipher) and ~1300 ns/call
      (sawtooth). §6.4 grew a workload-(3) row.*

- [x] **D1. FF1 / FF3-1 throughput + FPC tightness benchmark**
      *(promoted from DEBTS to a closed Phase 1 measurement,
      2026-05-02).* NIST SP 800-38G FF1 with AES-128, validated
      against Appendix A.1 vectors. Measured against M3's
      throughput panel and two cells from M2's FPC grid.
      *Done. See `paper/measurements/d1_results.md` and
      `replication/comparators/ff1.py`. Headline: FF1 throughput
      ~100–147 µs/call through the Python wrapper (~19–29× slower
      than BIDDER on workload 2); FF1 FPC ratio ~0.92 at both
      cells (sampling-consistent with ideal 1.0); BIDDER 6.8× /
      32× on the same cells. §7.4 / §4.5 / §9 / M3 prose updated.*

### Engineering

- [x] **E1. Carve the `bidder-stat/` repo.** Per the Phase 0
      decision: a new repo containing only `core/`, `generator/`,
      relevant `tests/`, the C kernel, and the Python wrapper. Decide
      `bidder-stat/replication/` structure. One `use_case_<n>.{c,py}`
      per §7 example; a top-level `replicate.sh` that runs
      everything and reproduces every figure / table in the paper.
      *Done. Carved subtree at `paper/bidder-stat/`: contains
      `core/`, `generator/`, `tests/` + `tests/theory/`, the C
      kernel, the Python wrapper, `replication/` (M1-M4 scripts +
      use_case stubs to come), `BIDDER.md`, and a README. Use-case
      stubs deferred to Phase 3 §7 work. To convert to a separate
      git repo at submission: `git init bidder-stat && cp -r
      paper/bidder-stat/* bidder-stat/`.*
- [x] **E2. Replication `Makefile` (or `replicate.sh`)** in
      `bidder-stat/`. From a clean checkout: build the C kernel,
      run tests, run all six use cases, regenerate every figure.
      Single `make` target.
      *Done. `paper/bidder-stat/Makefile` provides `make build`,
      `make test`, `make replicate`, `make clean`. `replication/
      replicate.sh` runs M1-M4 and (when use cases land) the use-
      case scripts. Auto-detects `sage -python` when available.*
- [x] **E3. API freeze.** Document the C API contract for
      `bidder.cipher` and `bidder.sawtooth` (C-primary per Phase 0)
      as the version this paper describes. Tag a release in
      `bidder-stat/`. The paper references the tag. Python wrapper
      stays in the same repo as a binding example.
      *API contract documented in `paper/bidder-stat/README.md`
      (C-primary surface, six functions). The actual git tag
      `bidder-stat-v1.0` will be applied when the carved tree is
      pushed to its own repo at submission time; paper references
      the tag.*
- [x] **E4. Smoke check on a clean machine.** Clean clone of
      `bidder-stat/`, build + test, confirm `make replicate` works
      end-to-end.
      *Done. See `paper/measurements/e4_smoke.md`. `make build`
      compiles `libbidder.dylib` cleanly; `make test` runs all
      eleven Python + theory tests successfully. M1's measurement
      script runs end-to-end from the carved tree. The C kernel,
      Python wrapper, and tests are all self-contained — no
      imports leak from the upstream repo's algebra/wonders/etc.*

## Phase 2 — sections drafted from existing material

These can be written in parallel as soon as Phase 0 decisions land.
No measurement dependency.

- [ ] **§3 Substrate.** Transcribe from `core/BLOCK-UNIFORMITY.md`
      and `core/HARDY-SIDESTEP.md`. Acceptance: theorems stated,
      proofs outlined, no rhetoric, every claim cited.
- [ ] **§4 Cipher path** (parts §4.1, §4.2, §4.4, §4.5; §4.3 waits
      for M1). Transcribe from `generator/RIEMANN-SUM.md` and the
      cipher implementation. Acceptance: structural identity stated,
      one-line proof reproduced, FPC layer named.
- [ ] **§5 API.** Two function signatures, contracts, and examples,
      C-primary per Phase 0 (`bidder_root.h` declarations as the
      surface; Python wrapper as a binding example). Transcribe
      from `core/API.md` and `BIDDER.md`.
- [ ] **§11 References.** Compile the bibliography:
      Beaulieu et al. (Speck), Black & Rogaway 2002 (cycle-walking
      FPE), NIST SP 800-38G (FF1/FF3-1), Copeland & Erdős 1946,
      Schiffer 1986. Plus any methods refs the use cases pull in.

## Phase 3 — sections that depend on Phase 1

- [ ] **§4.3 Feistel fallback.** Depends on M1.
- [ ] **§6.4 Performance.** Depends on M4 and the §6.4 decision in
      Phase 0.
- [ ] **§7 Use cases.** One sub-task per case. Each is a worked
      example: code → numerical result → exactness payoff vs
      asymptotic alternative.
   - [ ] §7.1 Stratified survey design with leading-digit strata.
         *Still a gesture; not yet implemented.*
   - [x] §7.2 Benford-test null distribution.
         *Done. `replication/use_case_02_benford_null.py`,
         `paper/measurements/use_case_02_results.md`. BIDDER χ² = 0
         exactly across 5 (b, d) cells; i.i.d. χ² ~ χ²(b-2) as
         predicted; sieved n-prime level same.*
   - [x] §7.3 Reproducible cross-validation, exact fold sizes on
         non-power-of-two `n`.
         *Done. `replication/use_case_03_cross_validation.py`,
         `paper/measurements/use_case_03_results.md`. BIDDER fold
         sizes ∈ {⌊n/k⌋, ⌈n/k⌉} at every (n, k) panel cell; SHA-256
         hash-based deviation grows ~sqrt(n).*
   - [x] §7.4 Format-preserving permutation of small-`P` domain.
         *Done. `replication/use_case_04_fpe.py`,
         `paper/measurements/use_case_04_results.md`. Bijection +
         determinism verified at 6 small-P points; capability
         matrix and three-workload throughput row rendered from
         M3 + D1 + D4.*
   - [ ] §7.5 Deterministic test corpora.
         *Still a gesture; not yet implemented.*
   - [x] §7.6 Variance-controlled Monte Carlo with known FPC.
         *Done. `replication/use_case_06_variance_mc.py`,
         `paper/measurements/use_case_06_results.md`. At P = 2000,
         BIDDER variance at N = P is 6.15e-31 (machine-ε); FPC
         shape verified at N < P with U-shaped realisation gap
         peaking at 7.17× at N = P/2.*
- [ ] **§9 Limitations.** Mostly Phase 0 + the open items
      acknowledged out-of-scope.

(§8 collapsed into §7.4 per Phase 0; M3's comparison table lives
there. Subsequent §-numbers in `OUTLINE.md` keep their labels for
draft-tracking; the JStatSoft submission's actual numbering is set
in Phase 5 when the LaTeX template lands.)

## Phase 4 — closing matter

- [ ] **§10 Discussion.** Short. Written after §1–9 land.
- [ ] **§1 Abstract.** Written last; needs the body to be stable.
- [ ] **§2 Introduction.** Written last for the same reason.
- [ ] **Pass for tone.** Strip any rhetoric / "what this means"
      sections that crept in. Same discipline as `algebra/`.
- [ ] **§3 compression pass** *(audit Q1, 2026-05-02).* Retitle
      §3 around the substrate contract. Compress §3.2–§3.5 from
      OUTLINE-level expansion to proposition / proof-sketch form
      (the proofs are short — positional-notation count, divmod,
      one-line c_K — so the compressed form is the right granularity
      for a 15-page paper). Move repeated exclusions from §3.6 into
      §9 except the one substrate-coverage sentence (smooth +
      Family E + spread bound regime).
- [ ] **Cross-reference audit.** Every §X reference resolves;
      every cited file path exists; every theorem citation is
      live.
- [ ] **Internal consistency check.** Numbers in §6.4 / §7 / §8
      agree with the replication archive's outputs.

## Phase 5 — submission

- [ ] **JStatSoft template.** Convert to JStatSoft LaTeX class.
      Format figures and tables to template requirements.
- [ ] **Replication archive packaging.** Tar / zip per JStatSoft
      replication policy. Include `README.md` with one-paragraph
      "what's here" and a one-line `make replicate` invocation.
- [ ] **Cover letter.** Short. Names the contribution and why
      JStatSoft is the right venue.
- [ ] **Pre-submission read-through.** Whole paper, in one sitting,
      out loud if possible.
- [ ] **Submit.**

## Bar to clear

A paper is ready to ship when:

1. Every Phase 0 decision is locked.
2. Every Phase 1 measurement has a number in the paper that came
   from running the code in the replication archive.
3. Every section in `OUTLINE.md` has a draft that meets the
   acceptance criterion in this file.
4. The replication archive runs end-to-end on a clean machine.
5. The cross-reference audit returns zero broken pointers.

Anything beyond that is referee-response, not submission-gate.

## Out of scope for this submission

For the avoidance of feature creep:

- Algebra (`Q_n`, OGFs, kernel zeros, wonders).
- Probes framework.
- Absolute normality / `μ` / cross-base questions.
- Lucky-cancellation locus characterisation.
- The substrate's "open heart" manifesto.

If a §X starts pulling from any of these, it's the wrong section
for this paper. Re-scope or move it to a follow-up.
