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

- [ ] **D1. FF1 / FF3-1 throughput + FPC tightness benchmark.**
      Either install `pyffx` (pure-Python FF1) or write a minimal
      AES-based FF1 reference impl (~150 lines) backed by
      `pycryptodome`. Run the M3 sweep and the M2 (P, N)-grid sweep
      against it. Acceptance: §7.4's matrix gets a numeric column
      for FF1's throughput at `P ∈ {10k, 100k, 1M}` and a numeric
      "FPC tightness ratio" column at one representative `(P, N)`.
      The paper currently states the qualitative conclusion
      (FF1 wins on quality, BIDDER wins on lightness) — D1 turns
      that into a number.

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

- [ ] **D4. C-direct throughput.** M3 / M4 measure throughput
      through the Python ctypes wrapper, which adds ~1 µs / call.
      A C-side benchmark (a small `replication/bench_c.c` that
      times `bdo_block_at` in a tight C loop) would give the
      kernel-level number. Acceptance: §6.4's table grows a "C
      direct" column showing the kernel's per-call cost without
      Python overhead.

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

- [ ] **D10. Section §4.4 deflation.** The structural Riemann-sum
      identity at `N = P` is currently described in the OUTLINE
      with language like "the cipher's apparatus collapses." That
      reads as a BIDDER-special property; it is not. *Any*
      bijection of `[0, P)` has this identity. BIDDER's
      contribution is being a keyed reproducible bijection, not the
      identity itself. A second pass on §4.4 prose at draft time
      should make this explicit. (Will be done at drafting; this
      entry is a reminder.)

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

---

## Closed

(Items move here when their corresponding paper paragraph is
updated to reference the closed measurement / implementation /
framing change.)

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
