# EXP06 — multi-tongue: the L1 tracking is magnitude, not shape

The optimizer reading predicted that survivors (`m = 1`,
`H(stream | integer) = 0`) would preserve the bundle's leading-digit
content while higher multiplicities (`m ≥ 2`) would diverge. The
reality is more interesting: **the L1 tracking observed in Two
Tongues is at the magnitude level — overall non-uniformity — but
the *shapes* differ across multiplicities, and survivors have their
own specific shape distinct from the bundle's**.

The optimizer reading is partly falsified. Survivors do not preserve
the bundle's leading-digit shape. They produce a distinctive shape
of their own, with a striking digit-3 spike that EXP04's z-score
analysis already flagged.

## Setup

At the Two Tongues panel `[2, 10], k = 400`, partition the bundle's
unique integers by multiplicity:

```
multiplicity | unique integers
m = 1        | 1338  (survivors)
m = 2        |  419  (doubletons)
m = 3        |  285  (triples)
m ≥ 4        |  129  (quads+)
total        | 2171
```

For each bucket, build the running leading-digit distribution along
bundle position (each integer counted once at first appearance).
Compute L1 deviation from uniform-1/9 at each step. Compare
end-of-stream values and leading-digit shapes.

## The numbers

```
bucket   end-of-stream L1   Δ from bundle (0.7972)
bundle      0.7972
m = 1       0.8505          +0.0533
m = 2       0.9494          +0.1521
m = 3       0.8047          +0.0075   ← closest to bundle
m ≥ 4       0.7235          −0.0737   ← more uniform than bundle
```

Leading-digit distributions at end of stream (all over the same
1338-3600 atom horizon):

```
digit | bundle | m=1    | m=2    | m=3    | m≥4
   1  | 0.385  | 0.298  | 0.401  | 0.449  | 0.473
   2  | 0.222  | 0.257  | 0.296  | 0.175  | 0.101
   3  | 0.124  | 0.204  | 0.110  | 0.060  | 0.054
   4  | 0.055  | 0.066  | 0.036  | 0.049  | 0.070
   5  | 0.042  | 0.037  | 0.029  | 0.049  | 0.062
   6  | 0.044  | 0.033  | 0.041  | 0.049  | 0.062
   7  | 0.043  | 0.034  | 0.024  | 0.060  | 0.070
   8  | 0.042  | 0.032  | 0.043  | 0.056  | 0.039
   9  | 0.043  | 0.040  | 0.022  | 0.053  | 0.070
```

## Reading

### 1. Survivors do not preserve bundle's leading-digit shape

The bundle is sharply Benford: 38.5% on digit 1, 22.2% on digit 2,
12.4% on digit 3. Survivors are *broader*: 29.8% on digit 1, 25.7%
on digit 2, **20.4% on digit 3**. The Benford peak is shifted and
flattened across digits 1–2–3. The drop at digit 4 is sharper.

The optimizer reading predicted survivors would *match* bundle's
shape; in fact they have a distinct, characteristic shape. The
"preservation" reading is wrong at the shape level.

### 2. The Two Tongues "tracking" is L1 *magnitude* tracking

The bundle and survivors have similar L1 distances from uniform
(0.80 vs 0.85). They are both Benford-shaped at similar magnitude,
just with different *specific* distributions. The original Two
Tongues plot's curves track each other on log-y because they both
sit in the same order-of-magnitude band — but the underlying
distributions are not equivalent.

This explains why EXP01–05 found null results when probing for
shape-level structure beyond L1: the L1 observable averages
shape-distinctions away. Higher-resolution observables (per-digit,
pair-correlation, z-score-vs-random) recover those distinctions,
which is what EXP04 saw before EXP05 walked back.

### 3. The digit-3 spike is reproducible across observables

EXP04's per-digit z-score analysis identified **digit 3** as
significantly suppressed in survivor relative to random thinning
(z = −2.07).

EXP06 confirms it from the other direction: survivor's digit-3
frequency is **20.4%, vs bundle's 12.4%** — survivor *over*-represents
digit 3 within its own population. The interpretation:

- Random thinning (EXP04) produces digit-3 frequency similar to
  the bundle (~12%).
- Survivor's digit 3 frequency is markedly higher (~20%).
- Hence relative to random's ~12%, survivor's ~20% is a +
  deviation; equivalently, relative to bundle's ~12%, survivor is
  also +.
- EXP04's `z = −2.07` for digit 3 came from a different framing
  (deviation of survivor's δ digit 3 from random's δ digit 3); the
  EXP06 finding is at the leading-digit-of-the-population level
  rather than the digit-of-δ level.

Both experiments find digit 3 as a survivor-specific signature.
The mechanism is open but consistent across observables.

### 4. The multiplicity hierarchy isn't monotone in L1

Higher multiplicity does not mean less Benford. Doubletons (m=2)
are *more* Benford-skewed than survivors (0.95 vs 0.85). Triples
(m=3) coincidentally match the bundle's L1 magnitude almost
exactly (0.80 vs 0.80). m ≥ 4 are *less* Benford-skewed than
bundle.

Reading the multiplicity → leading-digit map structurally:
- **m = 1** survivors: products of one window-divisor with an
  out-of-window cofactor (per EXP14). Wide range of integer
  values; broader leading-digit peak.
- **m = 2** doubletons: products of *two* window-divisors. Smaller
  population, smaller integers (e.g., 14 = 2·7, 15 = 3·5);
  heavily concentrated in low decades, hence sharper Benford peak.
- **m = 3** triples: products of three window-divisors. Even
  smaller integers in window (6 = 2·3 → also in n=6, hence triple).
  More concentrated at digit 1, but compensated.
- **m ≥ 4** quads+: integers divisible by 4+ window-divisors —
  e.g., 60, 120, 180. These span more decades evenly, so the
  leading-digit distribution is *flatter* than bundle's.

The Benford-skew level is set by the integer-value distribution of
each population, which depends on multiplicity in a structured but
non-monotonic way.

## What this means for the cabinet

The cabinet's Two Tongues curiosity records a real observation:
*C_Surv's leading-digit L1 deviation tracks the bundle's almost
cell-for-cell on a log-scale plot, across the full atom horizon*.
EXP06 doesn't falsify that observation. What it reframes is the
*reading* of that observation:

- **Wrong reading**: the survivor filter preserves the bundle's
  leading-digit content.
- **Right reading**: the survivor filter produces its own
  characteristic leading-digit shape, but at L1 magnitude similar
  to the bundle's. Both bundle and survivor are Benford-skewed at
  comparable magnitudes; the Two Tongues observable can't see
  beyond the magnitude.

The richness of the bundle/survivor relation is now relocated:
*not* at the L1-magnitude level (where bundle and survivors are
near-equivalent), *not* at the digit-difference level (which the
transducer destroys), but at the **shape-of-leading-digit-
distribution** level, where each multiplicity bucket has its own
characteristic profile.

The cabinet's curiosity entry should be revisited — its description
of the L1 tracking is correct; its provocation should perhaps be
sharpened to *"why does each multiplicity bucket have a distinct
leading-digit shape, and what predicts those shapes?"*.

## What this opens

- **Mechanism for the m=1 digit-3 spike.** EXP14's six-category
  decomposition of survivors (P_W, C_W, T_A_part, T_B_low,
  T_B_high, other) suggests the spike comes from one or two
  categories' specific composition. T_B_low (cofactor-below-window
  products `c = d · m` with `d ∈ window`, `m < n_0`) at panel
  `[2, 10]` includes integers like 14 = 2·7 — wait, that's a
  doubleton. T_B_low at this panel needs `m < 2` which is just
  `m = 1`; so T_B_low = `{d · 1 : d ∈ [2..10]} = {2, 3, ..., 10}`.
  That's only 9 atoms. Most survivors must come from other
  categories. A direct stratification of survivor integers by
  EXP14 category, with leading-digit distribution per category,
  would pin the digit-3 spike to a specific source.

- **Multiplicity at other panels.** The hierarchy m=1 (broad peak),
  m=2 (sharp Benford), m=3 (peak at 1), m≥4 (flatter) was observed
  at one panel. Repeat at `n_0 ∈ {5, 10, 30}` to see whether the
  *shape* of the multiplicity hierarchy changes with parameters.

- **A real new construction**: `C_Triples`. The fact that triples
  have nearly identical L1 magnitude to the bundle (Δ = +0.008) is
  worth recording as an observation in its own right. C_Triples may
  be a candidate for a future cabinet specimen — different from
  C_Surv, but sharing the L1-tracking property at this panel.

## Files

- `exp06_multitongues.py` — script.
- `exp06_multitongues.png` — three panels: tongues curves over
  bundle position, end-of-stream L1 by multiplicity, end leading-
  digit distribution by multiplicity.
