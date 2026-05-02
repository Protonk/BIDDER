# Differences — the C_Bundle − C_Surv perpendicular

The `survivors/` directory committed to one shape of question:
*how does the survivor filter perturb the bundle's leading-digit
frequency?* The trajectory closed in EXP12 (linear predictor at 87%)
→ EXP13 (exact closed-form residue at machine ε) → EXP14 (prime
convergence proven impossible for fixed-window K-scaling).

`differences/` opens the perpendicular question: *what is C_Bundle −
C_Surv as a real number?* The L1 view treats `C_Bundle` and `C_Surv`
as digit-frequency *generators*. Treating them as actual reals — and
their difference `δ` as another real — exposes a positional residual
that the frequency view averages out.

The shape of the question is closer to the project's halting open
commitment (absolute normality of `{C_b(n)}`) than to the
combinatorial classification work in `survivors/`. `C_Surv` is a
sibling of `C_b(n)` — same construction footprint, structured filter
on top — and number-theoretic questions about it are open in the
same register.

## Experiments

- **EXP01** — `EXP01-FINDINGS.md`, `exp01_delta_digits.py` /
  `exp01_delta_digits.png`. Compute `δ = C_Bundle − C_Surv` at the
  Two Tongues panel parameters. Split the analysis into the
  *overlap region* (first 4,894 digits — where bundle and survivor
  are genuinely fighting) and the *tail* (last 7,980 digits — just
  bundle's last digits, since `C_Surv` contributes zero there).
  Headline: the full δ's digit-frequency bias is dominated by
  bundle's tail (Benford-like inheritance); the overlap region is
  closer to uniform with a distinct *subtraction-with-borrows*
  signature (digits 0 and 9 spike). The L1-tracking story extends
  to the digit-frequency observable on δ.

- **EXP02** — `EXP02-FINDINGS.md`, `exp02_delta_cf.py` /
  `exp02_delta_cf.png`. Continued-fraction expansion of δ at the
  same parameters. Headline: δ's CF is **generic** by every metric.
  Length 24,923 — within 0.2% of the Heilbronn average. Partial-
  quotient distribution matches Gauss–Kuzmin to within sampling
  noise at every value of `k`. Khinchin geometric mean converges
  to 2.6948 (constant 2.6854; deviation +0.0093). Top partial
  quotients sit at positions with no structural correspondence.
  The CF view returns null content above L1-tracking.

The combined EXP01+EXP02 reading: at this one panel, two orthogonal
observables (decimal digit frequency, rational-approximation
hierarchy) both find no structure beyond the L1-tracking that the
cabinet's Two Tongues curiosity records.

## The transducer note

Why both perpendicular observables came back null is its own thing —
not a property of the relation, but of the operation. See
`DIFFERENCING-AS-TRANSDUCER.md`. Briefly: subtracting two
digit-concatenated streams of different lengths aligns them by digit
position rather than by atom, and from the first divergence onward
the digit-position subtraction compares unrelated atoms. The output
is generic by construction, regardless of what structure the
relation carries. The relation lives in atom-aligned observables
(L1-tracking, position maps, multiplicity distributions); the δ
experiments characterise what `C_Bundle − C_Surv` *is*, but they
cannot speak to the relation.

This note is meant to be cited the next time a differencing-flavoured
specimen comes up — as a reminder that this class of observable is
a transducer, not a transparent window.

## EXP03 (pair correlations) — a partial recovery

- **EXP03** — `EXP03-FINDINGS.md`, `exp03_delta_digrams.py` /
  `exp03_delta_digrams.png`. Following the user's intuition that *if
  the transducer is only mostly destructive, residual content has to
  land somewhere*, this experiment looks at consecutive-digit pairs
  in δ's overlap region. χ² over the 10×10 joint is 110 (vs 81 dof
  critical 119 at p<0.001) — borderline significant; mutual
  information 0.016 bits. Bundle's overlap-region pair χ² is 237
  (significantly higher), so the transducer reduces pair structure
  by ~2.25× but doesn't eliminate it. Top anomalies: `(0, 9)` and
  `(8, 9)` over-represented (single-position borrow signatures);
  `(9, 9)` suppressed (long borrow chains don't form); `(1, 0)`
  and `(0, 1)` carry diluted bundle-inheritance. The conservation
  intuition is empirically supported: residual structure survives
  the transducer, in pair correlations rather than single-digit
  frequencies.

## EXP04 (random-subset control) — the survivor filter is distinguishable

- **EXP04** — `EXP04-FINDINGS.md`,
  `exp04_random_subset_control.py` /
  `exp04_random_subset_control.png`. Run 50 random subsets of size
  1338 from the 3600 bundle atoms (preserving order), build their
  δ-signatures, compare to the survivor's. Random thinning *also*
  produces a borrow signature (L1 = 0.068, non-zero); the survivor's
  signature (L1 = 0.106) is significantly larger at z = +2.21 (χ²
  z = +2.53). Per-digit, digit 0 spikes more in survivor than random
  (z = +1.92), digit 3 is suppressed (z = −2.07). The previous
  "L1-tracking is the whole story" reading sharpens: the L1 story is
  partly generic (random thinning matches it modulo borrow excess)
  and partly survivor-specific (the survivor's δ pushes further from
  uniform than random's). The cabinet's Two Tongues curiosity is
  partly answered: structured filter is *not* equivalent to uniform-
  random thinning at this observable.

## EXP05 (parameter sweep) — the signal is panel-specific

- **EXP05** — `EXP05-FINDINGS.md`,
  `exp05_parameter_sweep.py` / `exp05_parameter_sweep.png`. Three
  sweeps around the Two Tongues center: k ∈ {100, 200, 400, 800},
  n_0 ∈ {2, 10, 30, 100}, W ∈ {3, 9, 15, 21}, with 20 random seeds
  per panel. Result: the z-score from EXP04 is **panel-specific**.
  Across 10 panels, only the Two Tongues panel itself crosses the
  2σ threshold on χ² (`(2, 3, 400)` is also above on χ² alone). Most
  others are within ±1σ of zero. The signal decays cleanly with
  survival rate — at n_0 ≥ 30 (survival rate >70%) the signal
  vanishes, because the filter is barely a filter when most atoms
  survive. Either Two Tongues sits at a local maximum where the
  filter imprints most strongly, or the original z = +2.21 was
  partly a single-panel statistical fluctuation. The cabinet's
  curiosity loses some of EXP04's sharpening; the L1 tracking
  remains as observed at the original panel, but its claim of
  generic survivor-vs-random distinction does not extend.

## EXP06 (multi-tongue) — L1 tracking is magnitude, not shape

- **EXP06** — `EXP06-FINDINGS.md`,
  `exp06_multitongues.py` / `exp06_multitongues.png`. Tests the
  optimizer reading by extending Two Tongues from `{bundle,
  survivors}` to `{bundle, m=1, m=2, m=3, m≥4}` — partitioning
  bundle integers by multiplicity. Result: the optimizer reading is
  partly falsified. End-of-stream L1 deviations are *not* preserved:
  bundle 0.80, m=1 0.85, m=2 0.95, m=3 0.80, m≥4 0.72. Triples
  (m=3) coincidentally match bundle's L1 most closely; survivors
  (m=1) have *broader* peak (digit 1 at 30%, digit 2 at 26%, digit
  3 at **20%** — vs bundle's 38%, 22%, 12%). The Two Tongues
  "tracking" is at the L1 *magnitude* level (overall non-uniformity)
  — both bundle and survivors are Benford-skewed at similar
  magnitudes, but with distinct shapes. EXP04's digit-3 anomaly is
  reproduced from this angle: survivor's digit-3 frequency is
  significantly elevated relative to bundle. The cabinet's curiosity
  reading should be sharpened: each multiplicity bucket has its own
  characteristic leading-digit shape; the L1 magnitude tracking
  conceals significant shape differences. The richness lives at the
  shape level.

## EXP07 (source-stream stratification) — the digit-3 spike is a finite-k artifact

- **EXP07** — `EXP07-FINDINGS.md`,
  `exp07_source_stream_stratification.py` /
  `exp07_source_stream_stratification.png`. Stratifies survivors by
  source stream `d ∈ [2..10]`. Result: digit-3 frequency per stream
  is wildly varied — `d=2..6` gives 0–8%, `d=7` gives 16%, but
  `d=8, 9, 10` give **36%, 41%, 49%**. The aggregate spike traces
  almost entirely to high-d streams. **Mechanism**: there are no
  *true* d=10-only survivors (the structural constraints —
  `4|c, 16|c, 25|c, 64|c` — force `m` divisible by 160, contradicting
  `10 ∤ m`). The 136 apparent d=10 survivors are integers `c = 10m`
  whose alternative-stream atom (typically n=5) had rank > k=400 and
  was truncated away. The cofactor `m` is constrained to `(250, 500]`
  by the rank-truncation arithmetic, and that range's leading digits
  cluster on 2-3-4 — yielding the 49% digit-3 frequency. Same
  mechanism applies to `d=8, 9`. **The EXP06 "rich shape" reading is
  largely a finite-k truncation artifact**, not a property of the
  survivor construction in the limit. The reframing chain is now:
  differences-as-transducer → random-control panel-specific →
  multiplicity-shapes → source-stream-finite-k. Each step walked back
  the previous reading by adding a structural mechanism the previous
  step missed.

## Cross-references

- `experiments/acm-champernowne/base10/survivors/SURVIVORS.md` —
  the parent construction (bundle, survivors, `C_Surv`).
- `wonders/curiosity-two-tongues.md` — the cabinet curiosity that
  motivates this perpendicular: L1 tracks; what doesn't?
- `THE-OPEN-HEART.md` — the absolute-normality framing that this
  inherits.
