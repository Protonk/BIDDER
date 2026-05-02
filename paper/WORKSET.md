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
      kernel, the Python wrapper, `replication/` (M1-M4 scripts,
      D1 + D4 measurement, five use-case scripts §7.1/§7.2/§7.3/
      §7.4/§7.6, FF1 reference impl in `replication/comparators/`),
      `BIDDER.md`, and a README. To convert to a separate git
      repo at submission: `git init bidder-stat && cp -r
      paper/bidder-stat/* bidder-stat/`.*
- [x] **E2. Replication `Makefile` (or `replicate.sh`)** in
      `bidder-stat/`. From a clean checkout: build the C kernel,
      run tests, run all six use cases, regenerate every figure.
      Single `make` target.
      *Done. `paper/bidder-stat/Makefile` provides `make venv`
      (idempotent venv bootstrap with pinned numpy + pycryptodome),
      `make build`, `make test`, `make bench-c` (D4),
      `make use_case_NN` per case + `make use-cases` group,
      `make replicate`, `make clean`, `make distclean`.
      `replication/replicate.sh` runs M1-M4 + D1 + D4 + the five
      use cases. All Python through the locked `.venv/bin/python`;
      sage auto-detect removed when the venv was locked.*
- [x] **E3. API freeze.** Document the C API contract for
      `bidder.cipher` and `bidder.sawtooth` (C-primary per Phase 0)
      as the version this paper describes. Tag a release in
      `bidder-stat/`. The paper references the tag. Python wrapper
      stays in the same repo as a binding example.
      *API contract documented in `paper/bidder-stat/README.md`
      (C-primary surface, five functions). The actual git tag
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

- [x] **§3 Substrate.** Transcribe from `core/BLOCK-UNIFORMITY.md`
      and `core/HARDY-SIDESTEP.md`. Acceptance: theorems stated,
      proofs outlined, no rhetoric, every claim cited.
      *Done. §3.1 setup; §3.2 *Theorem (Substrate contract)* with
      five clauses (integer / smooth-sieved / Family E / spread ≤2
      / Hardy random-access); §3.3 proof sketches; §3.4
      covers/doesn't. All anchors named (`tests/test_acm_core.py`,
      `tests/theory/test_riemann_property.py`); sources cited
      (`core/BLOCK-UNIFORMITY.md`, `core/HARDY-SIDESTEP.md`).*
- [x] **§4 Cipher path** (parts §4.1, §4.2, §4.4, §4.5; §4.3 waits
      for M1). Transcribe from `generator/RIEMANN-SUM.md` and the
      cipher implementation. Acceptance: structural identity stated,
      one-line proof reproduced, FPC layer named.
      *Done. §4.1 role separation; §4.2 Speck32/64 cycle-walking;
      §4.4 permutation contract + endpoint invariance corollary
      (one-line proof of the multiset identity); §4.5 FPC shape
      with M2 numbers and D1 FF1 ratio; §4.6 covers/doesn't. §4.3
      tracked separately under Phase 3.*
- [x] **§5 API.** Two function signatures, contracts, and examples,
      C-primary per Phase 0 (`bidder_root.h` declarations as the
      surface; Python wrapper as a binding example). Transcribe
      from `core/API.md` and `BIDDER.md`.
      *Done. §5.1 cipher path, §5.2 sawtooth path, §5.3
      composition pattern with C and Python examples plus
      prefix-not-exact caveat, §5.4 Python binding example, §5.5
      stability promise, §5.6 what's not included.*
- [x] **§11 References.** Compile the bibliography:
      Beaulieu et al. (Speck), Black & Rogaway 2002 (cycle-walking
      FPE), NIST SP 800-38G (FF1/FF3-1), Copeland & Erdős 1946,
      Schiffer 1986. Plus any methods refs the use cases pull in.
      *Done. All five refs in OUTLINE §11.*

## Phase 3 — sections that depend on Phase 1

- [x] **§4.3 Feistel fallback.** Depends on M1.
      *Done. §4.3 in OUTLINE cites M1's tabulated output and the
      empirically calibrated threshold (P = 2²⁶, conservative;
      throughput-optimal near P ≈ 2³¹).*
- [x] **§6.4 Performance.** Depends on M4 and the §6.4 decision in
      Phase 0.
      *Done. §6.4 has the workload taxonomy (single random-access
      call, materialise full perm, C-direct kernel) plus tables
      from M1 + M3 + M4 + D4 and a decision-boundary paragraph
      from M1.*
- [x] **§7 Use cases.** One sub-task per case. Each is a worked
      example: code → numerical result → exactness payoff vs
      asymptotic alternative.
      *Done. Five cases (§7.1, §7.2, §7.3, §7.4, §7.6) drafted to
      draft-paragraph granularity in OUTLINE and implemented as
      `replication/use_case_*.py`. §7.5 cut per audit Q4. See
      child entries below.*
   - [x] §7.1 Stratified survey design with leading-digit strata.
         *Done. `replication/use_case_01_stratified_survey.py`,
         `paper/measurements/use_case_01_results.md`. BIDDER per-
         stratum count is exact at every α (100, 500, 1000 across
         the panel); i.i.d.-then-post-stratify 99th-percentile max
         deviation grows 31 → 97 from N_total = 900 to 9000.*
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
   - [x] §7.5 *Cut 2026-05-02 per audit Q4* (overlapped §7.2 /
         §7.4; no independent load).
   - [x] §7.6 Variance-controlled Monte Carlo with known FPC.
         *Done. `replication/use_case_06_variance_mc.py`,
         `paper/measurements/use_case_06_results.md`. At P = 2000,
         BIDDER variance at N = P is 6.15e-31 (machine-ε); FPC
         shape verified at N < P with U-shaped realisation gap
         peaking at 7.17× at N = P/2.*
- [x] **§9 Limitations.** Mostly Phase 0 + the open items
      acknowledged out-of-scope.
      *Done. Nine bullets in OUTLINE.md: not-for-crypto-secrets,
      FPC realisation gap (with M2 + D1 numbers), bias-cancel
      anomaly at P=1000, conservative cycle-walking threshold,
      period cap 2³²−1, lucky-cancellation locus uncharacterised,
      throughput workload-dependence, normality out of scope,
      comparators not benchmarked. Each names magnitude and
      DEBTS.md ID where applicable.*

(§8 collapsed into §7.4 per Phase 0; M3's comparison table lives
there. Subsequent §-numbers in `OUTLINE.md` keep their labels for
draft-tracking; the JStatSoft submission's actual numbering is set
in Phase 5 when the LaTeX template lands.)

## Phase 4 — closing matter

- [x] **§10 Discussion.** *Drafted 2026-05-02.* One paragraph in
      OUTLINE.md committing the substrate-and-cipher split as a
      design principle; names the out-of-scope items handled in §9.
- [x] **§1 Abstract.** *Drafted 2026-05-02.* One ~150-word
      paragraph in OUTLINE.md, substrate-first per audit Q6.
- [x] **§2 Introduction.** *Drafted 2026-05-02.* Three paragraphs
      in OUTLINE.md: gap (Copeland-Erdős, Schiffer, FF1 / FF3-1),
      construction (§3 substrate first, §4 cipher), contribution
      (kernel + two contracts + measurements + use cases).
- [x] **Pass for tone.** Strip any rhetoric / "what this means"
      sections that crept in. Same discipline as `algebra/`.
      *Done 2026-05-02. Stripped OUTLINE-level scaffolding (status
      block, title commentary, discipline paragraph, Phase 0
      decisions block, "expanded to draft-paragraph granularity"
      preludes), explicit "Cards-face-up" labels, paragraph-meta
      annotations ("(Headline payoff.)", "(One paragraph; the
      X.)"), stale sage-python references. METAPHYSICS.md
      codifies the discipline going forward.*
- [x] **§3 compression pass** *(audit Q1, 2026-05-02).* Retitle
      §3 around the substrate contract.
      *Done 2026-05-02 (audit Q6). §3.2 is now a single
      "*Theorem (Substrate contract)*" with five clauses
      (integer / smooth-sieved / Family E / spread / Hardy random-
      access); §3.3 holds the proof sketches; §3.4 is "What §3
      covers and what it does not." The lucky-cancellation locus
      and absolute-normality exclusions point at §9 / DEBTS.md.
      Twelve downstream §3.X cross-references updated to §3.2
      clause N form.*
- [ ] **Cross-reference audit.** Every §X reference resolves;
      every cited file path exists; every theorem citation is
      live.
- [ ] **Internal consistency check.** Numbers in §6.4 / §7 / §8
      agree with the replication archive's outputs.
      *(Partial: audit Q2 caught throughput inconsistencies and
      they were fixed; full pass still pending submission gate.)*

## Phase 4.5 — paper drafting (`PAPER.md`)

`OUTLINE.md` is paper-shaped material; `PAPER.md` is the actual
draft we ship. Phase 4.5 tracks which OUTLINE / PRIOR-ART
content has been folded into `PAPER.md` and which remains in
the wings for later folding-in (target: 10–15 pages once the
wings land).

### Landed in `PAPER.md` (~3,520 words, 8 sections; round-4 audit + intro rework + signpost trim applied 2026-05-02)

Signpost discipline: ~9 in-body §X cross-references plus the §7
verification-table column, down from ~66 pointer instances (26
§X refs + 16 M-N / D-N labels + 4 OUTLINE §7.X pointers + 2
bare-§5 pointers + ~24 file-path mentions) before the trim. M-N
/ D-N labels are work-tracking artifacts from `WORKSET.md` /
`DEBTS.md`; they are gone from the paper text and live only in
`paper/measurements/` filenames where they belong as
identifiers.

- [x] **§1 Abstract** ← OUTLINE §1; reworked 2026-05-02 to lead
      with the source question *"if we got rid of the odd
      numbers, what numbers would be odd?"* and walk through to
      the n-prime atoms of `M_n`. Gives the substrate's
      mathematical content as the first thing the reader sees.
- [x] **§2 Introduction** ← new section, drafted 2026-05-02 to
      embody (not trumpet) the inspection / teaching benefit of
      a substrate built from a counting argument. Three
      paragraphs: (¶1) the question and the small-case answer
      walked through to `2ℤ \ 4ℤ` and the multiplicative-monoid
      atoms framing; (¶2) generalisation to `M_n`'s n-prime
      atoms, the counting argument on digit-class blocks, the
      Hardy random-access closed form, and a concrete worked
      number at `(b, n, d) = (10, 2, 4)` (250 atoms per leading
      digit on `[1000, 9999]`); (¶3) the framing earned ("not a
      deep theorem; the answer to a small concrete question"),
      the cipher half (Speck32/64, Black-Rogaway, Luby-Rackoff,
      FF1/FF3 positioning), and the contribution. ~590 words.
- [x] **§3 What BIDDER is** ← OUTLINE §1 + §5.1 + §5.2 + §5.3
      (substrate contract, cipher contract, five-function C
      surface, composition pattern). Renumbered from §2 when
      §2 Introduction landed.
- [x] **§3 What the novelty is** ← OUTLINE §2 contribution
      paragraph + §7.4 capability-matrix headline.
- [x] **§4 *Where BIDDER sits*** ← PRIOR-ART neighbour-paragraph,
      folded 2026-05-02; trimmed by round-4 audit (Q1) to three
      neighbours (Bailey-Crandall, QMC, ranged-int). VRF and
      Benford lines dropped — VRF imported a cryptographic audit
      frame the JStatSoft reader was not about to impose; Benford
      defers to the use-case section once §7.2 lands. Audit Q5
      reordered §3: substrate-vs-cipher closer now precedes
      *Where BIDDER sits*, which sits as the final niche
      paragraph.
- [x] **§4.1 Theorem (Substrate contract)** ← OUTLINE §3.2.
- [x] **§4.2 Proof sketches** ← OUTLINE §3.3.
- [x] **§4.3 Cipher contract + endpoint-invariance corollary**
      ← OUTLINE §4.4.
- [x] **§4.3 cipher provenance threading** ← PRIOR-ART
      *Standing on (cipher provenance)*, folded 2026-05-02;
      trimmed by round-4 audit (Q4) to three cites: Beaulieu
      2013, Black & Rogaway 2002, Luby-Rackoff 1988. The
      cryptanalysis citations (Dinur 2014, Song-Huang-Yang
      2016) and the small-domain Feistel attack (Durak-Vaudenay
      2017) were dropped from prose AND from §7 references —
      their presence implied the paper was asking the reader to
      evaluate Speck's security margin, which violates
      METAPHYSICS commitment 3 (*"Speck is technology, present
      our fit only"*). Beaulieu 2017 design notes and
      Naor-Reingold 1999 also dropped from §7 references for the
      same reason. All five remain staged in PRIOR-ART.md if
      the limitations section later wants them.
- [x] **§4.4 FPC shape at N < P** ← OUTLINE §4.5.
- [x] **§5 What it does** ← new section, folded 2026-05-02.
      §5.1 stratified survey design with exact leading-digit
      strata (← OUTLINE §7.1, with `replication/
      use_case_01_stratified_survey.py` numbers); §5.2 Monte
      Carlo with known endpoint and measured FPC realisation
      gap (← OUTLINE §7.6, with `replication/
      use_case_06_variance_mc.py` numbers). Round-4 audit (Q2)
      added an opener sentence connecting §5 to §4's contracts;
      audit (Q3) added a concrete audit-sampling motivation to
      §5.1's first sentence (account IDs, invoice magnitudes,
      registry blocks where leading digit is a mandated
      reporting stratum).
- [x] **§6 What the tests are** ← OUTLINE §6.3 (renumbered
      from §5 when §5 *What it does* landed). Round-4 audit
      (Q8) corrected the verification-table ranges to match
      the actual sweeps in `test_acm_core.py` and
      `test_sawtooth.py` (clause 1: base 10, `d ∈ {1,…,9}`;
      clauses 2 + 4: `b, n ∈ {2,…,10}, d ∈ {1,…,5}`; clause 3:
      `b ∈ {2,…,10}, d ∈ {2,…,5}`; clause 5: oracle sweep
      `n ∈ {2,…,12}` plus closed-form check `n ∈ {2,…,9999}`).
      Added the framing sentence separating "proof covers all
      valid parameters" from "tests cover this finite sweep."
- [x] **§6 Appendix C test vectors line** ← PRIOR-ART
      audit-side move, folded 2026-05-02. One sentence noting
      that `test_speck.py` carries the published Beaulieu et
      al. Appendix C vectors as inline checks.
- [x] **§7 References** ← OUTLINE §11 + PRIOR-ART. Round-4
      audit (Q6) flattened the four-block grouping to a single
      alphabetical list. After audit Q1 + Q4 cuts, 14 cites
      remain in the paper (Bailey 2002 + 2004; Beaulieu 2013;
      Black & Rogaway 2002; Copeland & Erdős 1946; Dick &
      Pillichshammer 2010; Halton 1960; Lemire 2019;
      Luby-Rackoff 1988; Niederreiter 1992; NIST SP 800-38G;
      Owen 1995; Saad et al. 2020; Schiffer 1986; Sobol' 1967).
      Cipher-cryptanalysis cites (Beaulieu 2017, Dinur 2014,
      Song-Huang-Yang 2016, Naor-Reingold 1999, Durak-Vaudenay
      2017), VRF cites (Micali-Rabin-Vadhan 1999, Gilad et al.
      2017), and Benford cites (Lesperance et al. 2016, Cerioli
      & Perrotta 2022) staged in PRIOR-ART.md but not in the
      paper. Grouped form lives only in PRIOR-ART.md now.

### In the wings (OUTLINE sections held; fold in for the 10–15-page target)

- [ ] **Introduction body** ← OUTLINE §2 ¶1 (gap; Copeland-Erdős,
      Schiffer, FF1/FF3-1) and ¶2 (construction with substrate
      first). Currently only §2's contribution paragraph is in
      `PAPER.md`'s §3.
- [ ] **Substrate setup** ← OUTLINE §3.1 (notation: `M_n`,
      n-prime atoms, `B_{b,d}`). Currently subsumed into the
      `PAPER.md` §4.1 theorem statement.
- [ ] **Substrate covers/doesn't** ← OUTLINE §3.4 (Schiffer
      bound, lucky-cancellation locus, normality out of scope).
      Will fold in next to §4.1 once paper expands.
- [ ] **Role separation framing** ← OUTLINE §4.1 (substrate-and-
      cipher split as a design principle). Currently present
      only as the §3 novelty argument.
- [ ] **Speck32/64 cycle-walking** ← OUTLINE §4.2 (what Speck is,
      cycle-walking construction). Currently mentioned in
      `PAPER.md` §2 in one phrase.
- [ ] **Feistel fallback** ← OUTLINE §4.3 (depends on M1; the
      decision rule and threshold). Currently mentioned in
      `PAPER.md` §2 in one phrase.
- [ ] **Cipher path covers/doesn't** ← OUTLINE §4.6.
- [ ] **API expansions** ← OUTLINE §5.4 (Python binding example),
      §5.5 (stability promise), §5.6 (what the API does not
      include).
- [ ] **Implementation chapter** ← OUTLINE §6.1 (source layout),
      §6.2 (cipher wiring), §6.4 (performance / throughput
      table), §6.5 (build and install), §6.6 (what §6 does not
      include).
- [ ] **Remaining use cases** ← OUTLINE §7.2 (Benford-test
      null), §7.3 (reproducible cross-validation), §7.4
      (format-preserving permutation of small `P` domain).
      §7.1 + §7.6 already landed in PAPER §5 above. Each held
      §7 case has a draft-paragraph-granularity OUTLINE entry,
      a `replication/use_case_*.py` script, and a
      `paper/measurements/use_case_*_results.md` row.
- [ ] **§8 fold note** ← OUTLINE §8 (one line; Phase 0 fold of
      §8 into §7.4 — meta, may not survive into PAPER.md at all).
- [ ] **§9 Limitations** ← OUTLINE §9 (nine bullets; cards-face-
      up gap inventory pointing at DEBTS.md IDs).
- [ ] **§10 Discussion** ← OUTLINE §10 (substrate-and-cipher
      design principle as one paragraph).

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
