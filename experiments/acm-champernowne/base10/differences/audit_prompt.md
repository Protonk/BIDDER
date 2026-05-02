# Audit prompt — differences/ directory

Hand this prompt to a fresh agent to check the work in
`experiments/acm-champernowne/base10/differences/`. Reply discipline
at the end.

---

You're auditing seven experiments and two structural notes in
`experiments/acm-champernowne/base10/differences/`. The work probes
`δ = C_Bundle − C_Surv` and related observables on the
bundle/survivor relation from `experiments/acm-champernowne/base10/survivors/`.

Read in this order before going further:

1. `DIFFERENCES.md` — directory orientation.
2. `REFRAMING-CHAIN.md` — meta-note on the empirical sequence.
3. `DIFFERENCING-AS-TRANSDUCER.md` — structural reframing #1.
4. `EXP01-FINDINGS.md` through `EXP07-FINDINGS.md` — the seven
   experiments in order.

The directory describes a **reframing chain**: empirical nulls
triggered external reframings, which made new findings visible,
which produced their own walked-back results, driving the next
reframing. This pattern is intentional. The walkbacks are *part of*
the work; do not "fix" them.

## YOUR JOB

For each experiment, check whether the claims hold up against:

- The cited code (`expNN_*.py`) — does the implementation match the
  description?
- The cited numerical results — do the chi-squared, z-score, L1, and
  CF statistics check out?
- The interpretive claims (e.g., "borrow signature," "finite-k
  truncation artifact," "transducer") — are they fair to the
  underlying math, or do they overreach?
- The cross-references — when one experiment cites another, does the
  citation accurately reflect what the cited experiment found?

Reply in chat — not in a file, not by editing — with **eight short
blocks**: one per experiment (EXP01–EXP07) plus one for the
reframing-chain meta-claim. Each block: claims that hold, claims
that don't (be specific about which sentence and what's wrong),
anything important the experiment misses or mis-frames. A few
hundred words total per block at most; less is better.

## WHAT THIS AUDIT IS NOT FOR

- **Re-running the experiments.** Trust the recorded numbers unless
  you suspect a specific computational error. Spot-check, don't
  recompute.
- **Proposing new experiments.** EXP08, EXP09 ideas are not what's
  being asked.
- **"Fixing" walkbacks.** EXP04 found z = +2.21; EXP05 walked it
  back to panel-specific; EXP07 explained it as finite-k artifact.
  These are sequential refinements, not contradictions. Don't argue
  for "EXP04 was right and EXP05 was wrong" or vice versa.
- **Re-interpreting the optimizer / transducer reframings.** Those
  were external (user-supplied). Audit whether the experiments
  *test* the reframings well; don't audit the reframings themselves.
- **Editing the entries** in any way. The audit is a chat reply.

## WHERE TO LOOK CAREFULLY

These are the specific worries the human asks you to check. Some are
"verify the math"; others are "is this claim too strong?".

### EXP01 (digit frequency)

- The overlap/tail split says the last 7,980 digits of `δ` are *just
  bundle's tail* (since `C_Surv` contributes zero there). Verify
  this is mathematically correct given that
  `C_Bundle = 1 + N_b/10^L_b`, `C_Surv = 1 + N_s/10^L_s`, and
  `L_b > L_s`.
- The "0 and 9 spike" interpretation as borrow signature — fair?
- The claim that the overlap region's L1 = 0.106 is "mild" relative
  to the tail's L1 = 0.294 — is the comparison apt?

### EXP02 (continued fraction)

- The CF length 24,923 is reported as "within 0.2% of the Heilbronn
  average `(12 ln 2 / π²) · ln(q) ≈ 24,975`." Verify the Heilbronn
  formula and the arithmetic.
- Khinchin's constant comparison: `K_N = 2.6948` vs constant 2.6854.
  The "+0.0093 deviation" is described as "within typical sampling
  fluctuation." Is that defensible at N=24,923?
- The statement that `q = 2^11,879 · 5^4,894` — verify by checking
  the construction. (`L_bundle = 12,874`, but `q` factors only as
  powers of 2 and 5 from `10^L_bundle`. The split of exponents is
  worth checking.)

### EXP03 (digit-pair correlations)

- The `(0, 9)` and `(8, 9)` borrow-signature interpretation — is the
  arithmetic of single-position borrows in subtraction-with-digit-
  shifts what the entry claims it is?
- The `(9, 9)` *suppression* interpretation as "long borrow chains
  don't form" — is that the correct conclusion from the deviation
  sign?
- The bundle's pair χ² = 237 is reported as ~2.25× δ's χ² = 110.
  The "transducer reduces pair structure by ~2.25×" framing is
  doing interpretive work — does it fairly match what the numbers
  say?

### EXP04 (random subset control)

- 50 seeds of size-1338 subsets from 3600 atoms (preserving order):
  does this match what the cabinet entry's curiosity-two-tongues.md
  description of the relation actually wants tested?
- The z-score `+2.21` for L1 — verify the mean and std of the
  random distribution from the printed numbers.
- Per-digit z-scores: digit 3 at z = −2.07 is highlighted. Cross-
  check this against EXP06's finding that survivor's digit-3
  *frequency* (not z-from-random) is 20%.

### EXP05 (parameter sweep)

- 20 seeds per panel (vs EXP04's 50). The entry notes this. Is the
  walkback ("panel-specific") robust against this lower seed count?
- The `k=400` peak in the k-sweep is non-monotonic in `k`
  (`−0.31, −0.51, +1.89, +0.66`). The entry flags this. Is the
  non-monotonicity a real signal of "Two Tongues sits at a local
  max" or noise?
- The "z decays with survival rate" interpretation — does the data
  support this monotonically, or is it a partial trend?

### EXP06 (multi-tongue)

- Per-bucket counting: each integer once at first appearance vs
  bundle counting each atom (so doubletons count twice). The entry
  flags this asymmetry. Is the comparison fair?
- The claim "L1 tracking is at magnitude level, not shape" — is
  this clearly demonstrated by the leading-digit distributions
  shown? Or is "magnitude" being used loosely?
- The `m=3` "coincidence" (Δ = +0.008 from bundle's L1) — verify
  arithmetically and check whether it's flagged as coincidence or
  as a structural finding.

### EXP07 (source-stream)

- The structural argument that no true `d=10`-only survivors exist:
  the entry derives `160 | m` AND `10 ∤ m` as a contradiction.
  Verify this derivation step by step. Specifically:
  - "c not in stream 4 ⟹ 16 | c ⟹ 8 | m" — check.
  - "c not in stream 5 ⟹ 25 | c ⟹ 5 | m" — check.
  - "c not in stream 8 ⟹ 64 | c ⟹ 32 | m" — check.
  - LCM(32, 5) = 160. Right?
  - 160 = 16 · 10, so 10 | 160 | m, contradicting 10 ∤ m. Right?
- The cofactor-band argument for `d=10` survivors: m ∈ (250, 500].
  The entry claims this gives 49% digit-3 frequency. Verify by
  counting m ∈ [300, 399] coprime to 10 within the (250, 500]
  range, and check that the proportion matches.
- The same mechanism is claimed for `d = 8, 9` "with different
  constraints." Spot-check `d = 9`: is there an analogous structural
  impossibility argument? If yes, briefly verify; if no, flag the
  claim as under-supported.

### DIFFERENCING-AS-TRANSDUCER.md

- The "transducer" framing is doing significant interpretive work.
  Is it fair? Specifically: the note claims that differencing on
  *misaligned* streams produces generic output by construction.
  Verify this is what the EXP01-02 results actually showed, vs a
  free interpretation.
- The note says the L1 tracking *doesn't* go through the transducer.
  Is that defensible given that L1 is also a digit-position-derived
  observable?

### REFRAMING-CHAIN.md (meta-claim)

- Read the meta-note. Does the recorded chain match what the
  experiments and notes actually show? Or has the narrative been
  tidied up post-hoc?
- The claim that "each reframing came from outside the empirical
  loop" — is this verifiable from the file timestamps and content,
  or is it an editorial position?

## REPLY FORMAT

Eight blocks in chat. For each: name, claims that hold up, claims
that don't (specific sentences, specific source disagreements),
things missed. Plus one block at the end naming any temptation you
had to do something this prompt told you not to do (re-run
experiments, propose new ones, fix walkbacks, edit files). That's
data about whether the prompt is communicating its discipline.
