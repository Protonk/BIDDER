# DEBTS

Acknowledged gaps in the paper that the replication archive does
not yet close. The discipline: the paper says, *cards face up*,
where each gap is. Each item here is a thing we could fill
tomorrow without rewriting the paper, only adding to it.

This file exists so the prose can show the gap (with a pointer to
this file) and the work to fill it can be tracked separately. When
a gap is filled, the corresponding paragraph in the paper updates
and the entry here moves to a "Closed" section at the bottom.

Categories: comparator debts, measurement debts, implementation
debts, framing debts, documentation debts.

---

## Comparator debts

These are alternative tools the paper compares BIDDER against in
words but doesn't benchmark numerically. The §7.4 capability
matrix names them; the throughput / FPC-tightness columns are
empty for them.

- [ ] **D2. `secrets.SystemRandom().shuffle()` baseline.**
      Real-randomness ungated comparator. Throughput is similar to
      `random.shuffle` with seed but without keyed reproducibility.
      Add to M3's panel and to §7.4's matrix as the "gold standard
      for unguessable randomness, no reproducibility" axis. BIDDER
      doesn't compete with it on randomness quality and the paper
      should say so directly.

- [ ] **D3. `os.urandom`-driven sort-by-iid-key.** Same role as
      D2 — name it as the unguessable-randomness comparator and
      include in M3's panel. Cheap to add (one extra row in M3's
      script).

## Measurement debts

These are measurements that would tighten the paper's quantitative
claims but are out of Phase 1 scope.

- [ ] **D5. M2 sweep at large `P`.** The current M2 grid stops at
      `P = 10000`. The Speck32 backend takes over at `P ≥ 2²⁶ ≈
      67M`, where the FPC realisation gap may behave differently
      (potentially better, since Speck32 is a stronger PRP than
      the lightweight Feistel). Acceptance: M2's grid extends to
      `P ∈ {10⁵, 10⁶, 10⁷}`, with the §4.5 paragraph naming
      whether the gap reflows at the Feistel→Speck32 transition.

- [ ] **D6. The `P = 1000` bias-cancel anomaly.** M2 reports ratios
      < 1 at `P = 1000` for `f = sin(πx)`, which the paper
      currently describes as "bias-cancelling on this specific
      integrand at this period." A characterisation — does the
      Feistel's symmetry structure interact with `f` symmetric
      about 0.5? does it persist at other `P` values divisible by
      4? — would convert the anomaly from a curiosity to a
      finding. Acceptance: §4.5 names the regime where the
      anomaly applies and the regime where it doesn't.

- [ ] **D7. M1 throughput at additional `P` panels.** M1 has
      twelve points around `2^k`. Adding cycle-walking ratio
      measurements at `(2^k)·m` for `m ∈ {1.1, 1.5, 1.9}` would
      sketch the full ratio-vs-P curve, exposing the throughput-
      optimal `MAX_CYCLE_WALK_RATIO` setting more cleanly. The
      paper currently reports three numbers (best/threshold/worst);
      the curve would show the shape between them.

## Implementation debts

These are changes to the C kernel or wrapper that would close
gaps the paper acknowledges.

- [ ] **D8. Tunable `MAX_CYCLE_WALK_RATIO`.** Currently fixed at
      64 in `coupler.py` and `bidder.h`. Exposing it as a
      parameter would let users trade between simplicity (fixed
      threshold) and throughput (Speck32 only when expected ratio
      is below ~2). The paper's §4.3 / M1 finding that the threshold
      is conservative becomes actionable instead of just observed.

- [ ] **D9. Stronger Feistel rounds option.** The current Feistel
      is 8 rounds with a deliberately lightweight round function.
      An optional 16-round mode (or AES-based round function) would
      give users tighter FPC realisation when they need it.
      Acceptance: §4.5 grows a parameterized FPC-tightness column,
      §7.4's matrix names "Feistel rounds" as a tunable quality
      axis.

## Framing debts

Places where the paper's prose currently underspecifies a claim or
glosses a regime.

- [ ] **D11. Replicate the BIDDER FPC gap with a stronger
      lightweight cipher.** If the §4.5 / M2 finding is "the gap
      is the price of using Speck32 + minimal Feistel," then
      swapping in a heavier-but-still-zero-deps cipher (e.g.,
      ChaCha8-based round function, ~100 lines) and re-running M2
      should show whether the gap shrinks. Acceptance: §4.5 grows
      a sentence on "which design choices the gap depends on."

## Documentation debts

- [ ] **D12. C quickstart in `bidder-stat/README.md`.** The paper
      tells users to "drop into C for throughput" but the README
      doesn't show how. A 20-line `quickstart.c` example calling
      `bdo_block_create` / `bdo_block_at` / `bdo_block_free` plus
      a `Makefile` snippet would close the gap. Acceptance: a user
      can copy from the README into a fresh C file and have it
      compile + link against `libbidder.dylib` / `.so`.

- [ ] **D13. Batched random-access API.** The current C surface
      (`bidder_root.h` and `bidder_opaque.h`) exposes one-index-at-
      a-time `at` calls. Bulk callers write a tight loop. A
      batched variant — e.g., `bidder_block_at_batch(ctx, indices,
      n, out_array)` — would amortise per-call overhead for
      vectorised consumers (numpy users, GPU pipelines). The
      paper's §5.6 / §6.6 acknowledge this; D13 is the
      implementation to-do. Acceptance: a `_batch` variant of each
      `at` function exists in the C surface, the Python wrapper
      exposes a vectorised path, and the M3 / M4 measurements grow
      a "batched" column showing the amortised per-element cost.

- [ ] **D14. SIMD Speck32/64 path.** The C kernel's
      `Speck32_Encrypt` is portable scalar C, one block at a time.
      Speck32/64 is a natural target for SIMD batching (round
      function is bit-rotation + add + xor on 16-bit halves; eight
      blocks fit in a 128-bit register). A SIMD path keyed on a
      `bidder_block_at_batch` (D13) entry point would cut
      per-element cost in the cycle-walking regime. Acceptance: a
      build-time `SIMD=1` variant of the kernel exists; M4 grows a
      SIMD-batched throughput row; §6.4's paragraph names the
      crossover where SIMD beats scalar.

- [ ] **D15. Cross-platform CI.** The build is hand-tested on
      macOS and Linux; Windows is unverified. The C kernel itself
      is portable C99 with no platform-specific calls, but the
      `Makefile` and `bidder_c_native.py` library-loading path are
      not Windows-aware. Acceptance: GitHub Actions CI runs
      `make build && make test` on macOS, Linux, and Windows
      runners; the Python wrapper's library-loading code resolves
      `bidder.dll` on Windows alongside `libbidder.dylib` /
      `libbidder.so`.

- [ ] **D16. Fuzzing harness.** The cipher is exercised by
      property tests (round-trip, bijection-hood at small `P`,
      Family E membership) but not by a fuzzing harness. A
      libFuzzer / AFL entry point that drives `bidder_cipher_init`
      with random `(period, key, key_len)` inputs and checks
      bijection-hood / round-trip / status-code coverage would
      catch corner cases the property tests don't enumerate.
      Acceptance: a `replication/fuzz_bidder.c` harness compiles
      under `clang -fsanitize=fuzzer`; CI runs it for one minute
      per PR; failures are reported as crashes or oracle-mismatches.

---

## Closed

(Items move here when their corresponding paper paragraph is
updated to reference the closed measurement / implementation /
framing change.)

- [x] **D1. FF1 / FF3-1 throughput + FPC tightness benchmark.**
      *Closed 2026-05-02.* `replication/comparators/ff1.py`
      written (~140 lines, NIST SP 800-38G FF1, AES-128 backend
      via pycryptodome) and validated against NIST SP 800-38G
      Appendix A.1 vectors (Samples 1, 2, 3 — all pass on first
      run). `replication/d1_measure.py` runs the throughput sweep
      at `P ∈ {10k, 100k, 1M}` and the FPC ratio at two M2 cells.
      Headline numbers: FF1 ~100,000–147,000 ns/elem through the
      Python wrapper (~19–29× heavier than BIDDER's ~5,000
      ns/elem); FF1 FPC ratio ~0.92 (sampling-consistent with
      ideal 1.0) vs BIDDER 6.8× / 32× at (2000, 1000) and (10000,
      5000). FF3-1 not benchmarked separately (shares AES
      backbone with FF1; capability matrix cites both).
      `paper/measurements/d1_results.md` is the canonical
      results file. §7.4 / §4.5 / §9 / M3 prose updated to drop
      "expected" hedges.

- [x] **D4. C-direct throughput.** *Closed 2026-05-02.*
      `replication/bench_c.c` written; `make bench-c` builds and
      runs the benchmark against `libbidder.dylib`; results land
      in `paper/measurements/d4_results.md`. Headline numbers:
      `bidder_block_at` C-direct ~38 ns/call (Feistel, `P < 2²⁶`),
      ~2112 ns/call (Speck32 cycle-walking at `P ≈ 10⁸`, ratio
      ~43); `bidder_sawtooth_at` ~3 ns/call (one divmod +
      arithmetic). Wrapper overhead = M4_cipher_ns − D4_cipher_ns
      ≈ 900 ns/call (cipher) and ~1300 ns/call (sawtooth). §6.4
      grew a workload-(3) row citing the C-direct numbers; the
      "kernel is sub-µs" claim is now numerically backed.

- [x] **D10. Section §4.4 deflation.** *Closed 2026-05-02.* §4.4
      retitled to "Permutation contract and endpoint invariance."
      The contract (stateless / keyed / arbitrary-period bijection
      with the §7.4 zero-deps + streaming combination) is now the
      load-bearing claim of §4. The Riemann-sum identity at `N = P`
      appears as a one-paragraph corollary explicitly labelled
      bijection-trivial, recorded only because §7.6 cites it.

---

## How to use this file

- Each paper paragraph that acknowledges a gap names the gap by
  ID (e.g. "D1: not benchmarked here; see DEBTS.md") in addition
  to the prose. The reader gets the qualitative conclusion in the
  paragraph and the actionable to-do in this file.
- When a gap is closed, the paragraph's "see DEBTS.md" pointer is
  removed, the new finding is incorporated, and the entry moves
  to the Closed section above.
- Adding a new debt is one bullet; the format is:
  `D<n>. **Title.** Description (1–3 sentences). Acceptance: <one
  sentence on what closes it>.`
