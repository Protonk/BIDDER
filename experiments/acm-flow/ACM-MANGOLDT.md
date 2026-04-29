# ACM-Mangoldt flow tomography

## ⚠️ STATUS UPDATE (after Phase 1 destroyers and Phase 2 closure)

**The four-coordinate working hypothesis below was refuted by Phase 1
destroyers**, replaced by the finite-rank `Q_n` framing now in
`core/Q-FORMULAS.md` and `core/FINITE-RANK-EXPANSION.md`. The
relevant corrections:

- The truncated-flow residual `ρ` is **not** the local observable. It
  mostly records cutoff placement and saturation, not arithmetic
  signal (`PHASE1-RESULTS.md`).
- The local arithmetic object is `Q_n(m) = Λ_n(m) / log m`, the
  Mercator-of-`ζ_{M_n}(s) = 1 + n^{-s} ζ(s)` log-coefficient,
  finite-rank-h by integer divisibility (`core/FINITE-RANK-EXPANSION.md`).
- The four "spectral lines" framing below collapses: height, payload
  divisor data, factorisation type of `n`, and overlap vector
  `(t_i)` are exactly the parameters of the master expansion in
  `core/Q-FORMULAS.md`. They are forced by the formula, not
  independent observable coordinates.
- The cutoff coordinate is demoted; only the n=2 `v_2(Y)` line
  survived destroyers, and that's a separate positivity-locus problem
  (`STRUCTURE-HUNT.md` side quest).

**This document is preserved as the historical record of the Phase 1
hypothesis.** Read it for context on what the project tested and how
the experiments were designed. For the current local arithmetic
framing, see `core/Q-FORMULAS.md` and `core/FINITE-RANK-EXPANSION.md`.
For the Phase 1 destroyer results that drove the reframe, see
`PHASE1-RESULTS.md`.

---

The 1196 proof works because it turns a primitive-set question into
a weighted divisibility-flow certificate: edge weight
`Λ(q) / (nq · log²(nq))` on the edge `nq → n`, with exact local
outflow given by the convolution identity
`Σ_{q | n} Λ(q) = log n`, and Mertens-type boundary control on the
near-inflow.

This experiment ports that mechanism to the ACM monoids.


## Working hypothesis (falsifiable)

The first-order Mertens-corrected residual `Δ' = Δ + 1/(m log X)`
decomposes into independently observable coordinates:

| coordinate | role |
|---|---|
| **height** | sets the coarse sign regime of `Λ_n`. |
| **payload divisor richness** | within a height regime, decides which `m` flip negative. |
| **cutoff witness richness** | of `Y = ⌊X/m⌋`, sets the residual mass that survives Mertens. |
| **decimal block certification** | smooth / Family E / uncertified — totalisation effect, lowers residuals but does not determine them. |

The two scans in `CUTOFF-SCAN.md` and `PAYLOAD-SCAN.md` are
designed to break this decomposition by holding one coordinate
fixed and sweeping another. Each is a controlled-source
measurement. If the decomposition holds, every coordinate is a
spectral line that can be read independently from the others.


## Coordinates and their layers

| coordinate | layer | controlling variable | observable |
|---|---|---|---|
| local | L1 | `τ_j(m/n^j)` for `j ≤ height(m)` | `sign(Λ_n(m))` |
| truncation | L4 | scouts on `Y = ⌊X/m⌋` | `ρ = Δ'/Out` per `Y` bucket |
| totalisation | L3 | block type `(n, d)` | `Σ Δ'/Σ Out` per cell, after matching |
| refinement | L4 (subset) | diag/prime-row disagreement on `Y` | residual within witness-rich `Y` |


## The question

Define the **monoid Mangoldt function** `Λ_n` on
`M_n = {1} ∪ nℤ⁺` by Möbius inversion:

    Σ_{d ∣_{M_n} m} Λ_n(d) = log m,   m ∈ M_n,    Λ_n(1) = 0,

where `d ∣_{M_n} m` means `d ∈ M_n` and `m/d ∈ M_n`. Equivalently
the coefficients of `−Z'_{M_n}(s) / Z_{M_n}(s)` with
`Z_{M_n}(s) = 1 + n^{−s}ζ(s)`. Closed form:

    Λ_n(m) = log(m) · Σ_{j ≥ 1, n^j | m} (−1)^(j−1) τ_j(m/n^j) / j,

where `τ_j` is the j-fold ordered divisor function.

**Does Λ_n behave like a positive flow weight, or does fake
primality force signed cancellation?** That is the experiment.

Ordinary `Λ` is nonnegative and lives on prime powers. `Λ_n` starts
by treating fake primes (n-primes) as full log-mass atoms, then
composites with multiple `M_n`-factorisations force cancellation.
First values for n=2 (asserted as smoke test):

    Λ_2(2)  = log 2,
    Λ_2(6)  = log 6,
    Λ_2(12) = 0,
    Λ_2(36) = −log 6.


## Layers

### L1 — Λ_n sign profile (local coordinate)

For `n ∈ {2, 3, 4, 5, 6, 10}` and `m ∈ M_n ∩ [n, X]`, compute
`Λ_n(m)`. Tabulate by exact n-height `h = ν_n(m)`. Per height:
count, positive count, negative count, `neg_mass / abs_mass`
ratio. Identify first negative locus per n.

Within each height, classify `m` by payload divisor richness
`τ_2(m/n^h)` (and at h=3 by `τ_2(m/n^3)`). The strongest finding
on this coordinate sits at h ≥ 3, where the alternation in the
closed form involves competing terms.

> **Footnote — the h=2 cliff is a closed-form consequence.**
> At h=2 the closed form reduces to `Λ_n(m)/log m = 1 − τ₂(m/n²)/2`,
> so `Λ_n(m) < 0 ⇔ τ_2(m/n²) ≥ 3`. The L1b/c "τ₂ ≤ 2 → no
> negative; τ₂ ≥ 3 → all negative" tables are therefore an
> analytic identity, not an empirical finding. The empirical
> content of L1 lives at height ≥ 3, where multiple `τ_j` compete
> and the sign reversal is no longer forced. The L1d/e payload-3
> tables show that — small payload τ₂ stays negative-heavy, middle
> buckets flip mostly positive, the high+disagreement tail re-flips
> negative — and that *is* a real finding.

### L2 — flow defect Δ_n(m; X)

For each `m ∈ M_n ∩ [n, X]`,

    Out_n(m)  =  Σ_{q ∣_{M_n} m} Λ_n(q) / (m · log²m)
              =  log(m) / (m · log²m)   [by the convolution identity]
              =  1 / (m · log m),

    In_n(m; X) =  Σ_{q ∈ M_n, m·q ≤ X} Λ_n(q) / (mq · log²(mq)),

    Δ_n(m; X) =  In_n(m; X) − Out_n(m),

    Δ'_n(m; X) =  Δ_n(m; X) + 1/(m log X).

`Out` is closed-form. `In` is a truncated tail. `Δ` measures the
flow defect under the truncation. `Δ'` subtracts the leading
`1/(m log X)` boundary term and is the working residual statistic.
At X=10000 the raw `Δ` is negative in every cell — truncation
dominates. `Δ'` shrinks the wall but does not remove it; the
coordinate decomposition above is what's left.

### L3 — block-typed totalisation (totalisation coordinate)

Partition `m` by base-10 digit class `d`. Classify each `(n, d)`
block via `core/BLOCK-UNIFORMITY.md`:

- **smooth** — `n² ∣ b^(d−1)`. Exact n-prime block size.
- **Family E** — `b^(d−1) ≤ n ≤ ⌊(b^d − 1)/(b−1)⌋`. Exactly one
  n-prime per leading digit.
- **uncertified** — neither. Includes lucky-cancellation cases.

At X = 10000 the block-type rollup gives:

    smooth        ΣΔ'/ΣOut ≈  −0.181   (count=7924)
    uncertified                −0.446  (count=7566)
    family_E                   −0.575  (count=9, single cell)

Smooth blocks are the least-residual cohort, uncertified the
worst. Family E is one cell at (n=10, d=2) and not statistically
informative on its own. The smooth advantage *survives* matching
on cutoff witness bucket but is small (0.009–0.048 in mean ρ
inside shared buckets); see Tier 2.

### L4 — cutoff-side scouts (truncation coordinate)

For each m, record scout features of `Y = ⌊X/m⌋`:

- divisor count `τ_2(Y)`
- non-trivial witness count
- distance to nearest multiple of `n²`
- phase `Y mod n²`
- whether the diagonal and prime-row witnesses disagree

The strongest single covariate is `τ_2(Y)`. L4d shows clean
monotone progression in `ρ`:

    smooth blocks       τ_2(Y) 0–2 → ρ ≈ −0.13
                              3–4 → ρ ≈ −0.20
                              5–8 → ρ ≈ −0.24
                              9–16 → ρ ≈ −0.28
    uncertified blocks  τ_2(Y) 0–2 → ρ ≈ −0.20
                              3–4 → ρ ≈ −0.28
                              5–8 → ρ ≈ −0.44
                              9–16 → ρ ≈ −0.46
                              17+ → ρ ≈ −0.59

At every matched `τ_2(Y)` bucket, the smooth offset is less
negative than the uncertified offset; the magnitude of the gap
*grows* with `τ_2(Y)` (≈ 0.06 at `τ_2(Y) ∈ [0, 2]`, ≈ 0.08 at
`[3, 4]`, ≈ 0.21 at `[5, 8]`) before saturating in `[9, 16]` at
≈ 0.18. The smooth advantage is therefore τ_2(Y)-dependent, not
a fixed offset; whether it survives matching at finer resolution
is the Tier-2 question handled in the matched ablation. Cutoff
witness count gives the same ranking with slightly less resolution;
`τ_2(Y)` also catches square-heavy cases that witness count
misses.

The cutoff-phase and distance-to-`n²` tables (L4a, L4b) show
variability across n with no clean monotone-ray structure at
X=10000. They remain in the output but are not the primary
truncation observable; the controlled scan in `CUTOFF-SCAN.md`
is the right tool to re-examine ray structure once `Y` can be
swept independently of `m`.


## Reporting discipline

Every `ρ = Δ'/Out` aggregate must report:

- mean ρ
- median ρ
- sign-fraction (count of `ρ < 0`)

If mean and median diverge in any bucket, flag it: the residual
is then carried by a small high-leverage tail, not by the bulk.
Smooth-block effects are small enough that this distinction
matters; do not aggregate without medians and sign-fractions.

This discipline is **not yet** in `acm_mangoldt_tomography.py`.
Adding median and sign-fraction columns to the L4c/L4d/L3b
aggregators is the prerequisite for any further claim on the
relative magnitude of coordinates. The two scan scripts should
adopt the same discipline at write-time. The matched ablation
report already follows this discipline for `ρ` tables.


## Statistical method discipline

Reporting (above) is descriptive. When a test is needed
(graduation, falls, persistence claims), the workhorse is
**Chatterjee's ξ correlation coefficient** (Chatterjee 2021;
`scipy.stats.chatterjeexi` is available in the current Sage
environment; otherwise use a local numpy implementation rather
than adding a dependency).

Key properties:

- `ξ ∈ [0, 1]`, asymmetric in its arguments.
- `ξ = 0` iff X and Y are independent (asymptotically).
- `ξ = 1` iff Y is a measurable function of X.
- **Shape-agnostic** — detects U-shapes, oscillation, monotone,
  sigmoidal, periodic alike. No directional preference. This is
  exactly the property the doc audit (above) demanded: ξ does
  not bake any shape into the result before data is seen.

Defaults:

| question | test |
|---|---|
| does `ρ` depend on a raw scout (`τ_2(Y)`, witness count, …)? | `ξ(scout, ρ)` with explicit tie handling; see below |
| ranking of scouts by predictive power for `ρ`? | sort scouts by `ξ(scout, ρ)` descending |
| does `ρ` shape track sign-fraction shape? | `ξ(bucket-mean-ρ, bucket-sign-fraction)` at bucket level (Pearson is also fine when bucket count is small and a co-located shape is the visual claim) |
| does sign-fraction depend on bucket (categorical Y)? | χ² of independence |
| smooth vs uncertified at fixed bucket (binary X)? | Mann-Whitney U or two-sample t-test |
| is a *specific* shape (U vs monotone) the right one — *after* ξ confirms structure? | pre-specified polynomial contrasts: linear + quadratic |

**Tie protocol.** `τ_2`, witness count, and bucket labels are
integer-valued with massive tie clusters; SciPy's `chatterjeexi`
breaks predictor ties arbitrarily, and on heavy-tie data that
swings ξ enough to flip scout rankings. The default for any ξ
report is therefore:

1. compute `ξ` under K independent random tie-breakings of the
   predictor (K ≥ 32; bump to ~100 for borderline calls);
2. report `ξ_mean`, `ξ_range = max − min` across the K seeds,
   and the K + base seed in the output table;
3. if `ξ_range` is comparable to the gap between competing scouts,
   the ranking is **not decisive** — fall back to Kruskal-Wallis
   on the binned data, or report bucket means with explicit
   hedge.

A single ξ value on bucket labels is never a standalone graduation
test. The cutoff scan, where (n, m) is fixed and the Y-sweep makes
predictor ties dominant, is where this protocol bites hardest.

Avoid as defaults:

- linear / OLS regression of `ρ` on a covariate (assumes
  monotone);
- Pearson / Spearman / Kendall correlation at the *observation*
  level (Spearman/Kendall assume monotone; Pearson assumes
  linear);
- OLS R² as variance-explained — replaced by ξ for scout
  ranking;
- Cochran-Armitage / Jonckheere-Terpstra (explicit monotone
  alternatives).

This discipline is **not yet** in any analysis script. Whichever
script first runs a graduation test should declare its method
choice in its header docstring against this table.


## Outcomes ranked

**Tier 1 — survives controlled scan (target of the next briefs).**
- Cutoff `τ_2(Y)` × block-type produces a `ρ` progression in the
  bucket-aggregate L4d data: monotone within both rows, with smooth
  less negative than uncertified at every matched `τ_2(Y)`, and
  the gap itself τ_2(Y)-dependent. The per-`(n, m)` shape is the
  open question — sieve-ray oscillation, a U-shape analogous to
  the payload coordinate, or genuine monotone tracking are all
  viable. `CUTOFF-SCAN.md` is the controlled measurement that
  distinguishes them.
- Payload divisor richness reverses sign in a U-shape at h=3
  (negative ends, positive middle), beyond what the h=2 closed
  form forces. `PAYLOAD-SCAN.md` is the controlled measurement.

**Tier 2 — survives matching, smaller than headline.**
- Smooth-block totalisation, after matching on cutoff witness
  bucket, leaves a 0.009–0.048 advantage in mean `ρ`. Real, but
  secondary; do not promote without medians and sign-fractions.

**Tier 3 — demoted.**
- Diag/prime-row disagreement: candidate refinement inside
  witness-rich cutoff regimes. After matching on block type and
  cutoff witness bucket, its extra residual signal is small and
  reverses in one tiny bucket. Witness count currently explains
  most of what it was hoped to explain.


## Next experiments

Two controlled scans, sharing the L1–L4 infrastructure.

| brief | scan |
|---|---|
| `CUTOFF-SCAN.md` | fix `(n, m)`, sweep `X = mY` across `Y`. Bucket by scouts on `Y`. Tests whether `Y`-compositeness drives residual negativity when `m` is held fixed. |
| `PAYLOAD-SCAN.md` | fix `(n, Y-witness-bucket)`, vary `m` across payload buckets, especially height 3. Uses height 2 as a smoke check and tests whether payload divisor richness controls `Λ_n` locally at fixed cutoff environment. |

Each promotes a Tier-1 matched-association result into a
controlled-source measurement. Reporting discipline (above)
applies.


## Sanity check

The script asserts the user-supplied values for n=2 before the
main sweep:

    Λ_2(2)  = log 2     ≈  0.693147
    Λ_2(6)  = log 6     ≈  1.791759
    Λ_2(12) = 0
    Λ_2(36) = −log 6    ≈ −1.791759

Mismatch on any of those exits with a non-zero status before
anything else runs.


## Files

| file | role |
|---|---|
| `acm_mangoldt_tomography.py` | implementation — L1–L4, scout features |
| `residual_ablation_grid.py` | matched-bucket ablation for `ρ = Δ'/Out` |
| `cutoff_ray_scan.py` | L1 of `CUTOFF-SCAN.md` (planned) |
| `payload_scan.py` | L1 of `PAYLOAD-SCAN.md` (planned) |
| `ACM-MANGOLDT.md` | this document |
| `CUTOFF-SCAN.md` | brief — cutoff-coordinate controlled scan |
| `PAYLOAD-SCAN.md` | brief — payload-coordinate controlled scan |
| `acm_mangoldt.csv` | per-row flow data plus cutoff and payload scout columns |
| `lambda_n{n}.png` | per-n scatter of `Λ_n(m)` vs m, coloured by sign |
| `delta_n{n}.png` | per-n scatter of `Δ_n(m; X)` vs m |
| `delta_mertens_n{n}.png` | per-n scatter of `Δ'_n(m; X)` vs m |
| `summary.txt` | L1 height tables, L3 block totalisations, L4 scout rollups |
| `residual_ablation_grid.txt` | matched-bucket ablation tables |


## Pipeline

```
acm_n_primes(n, K)         core/acm_core.py        (referenced)
   ↓
τ_j(k) for k ≤ X,
j ≤ ⌈log_2 X⌉              Dirichlet convolution τ_{j+1} = τ_j ∗ 1
   ↓
Λ_n(m) via closed form     exact via Fraction, then float
   ↓
Out_n, In_n, Δ_n, Δ'_n     floats, no precision drama
   ↓
height tally, block tally  per (n, h) and (n, d, type)
   ↓
scout tally                cutoff phase/distance, witness count, τ_2,
                           payload2/payload3 sign buckets
   ↓
matched ablation           ρ by fixed height/block/Y-witness buckets,
                           Λ sign by payload τ_2 buckets
   ↓
plots + CSV + summary
```

Pure Python in the Sage environment. No Sage-specific calls.

```
sage -python acm_mangoldt_tomography.py
sage -python residual_ablation_grid.py
```

Default `X = 10000`. Bumping is cheap: τ pre-compute is the
bottleneck and scales like `X · log² X`.


## Coupling

- **Brief 4 (Multiplication-table on M_n)** — the BPPW-modified
  Monte Carlo on `M_n(N) · Φ(N) / N` is gated on the `Λ_n`
  sign-table and `Δ` totalisation result here. See
  `EXPERIMENTAL.md` Brief 4 (rewritten).
- **`core/BLOCK-UNIFORMITY.md`** — the smooth and Family-E lemmas
  drive the L3 block partition.
- **`experiments/acm-champernowne/base10/art/sieves/SIEVES.md`** —
  the Sieve Carpet supplies the cutoff-side diagnostic; the
  controlled cutoff scan is the way to test ray structure
  without the `m`-dependence confound.
- **`experiments/acm-champernowne/base10/art/sieves/ULAM-SPIRAL.md`** —
  sieve density is a useful L1 compositeness-pressure covariate.
- **`experiments/acm/diagonal/cheapest_sieve/README.md`** — supplies
  the scout vocabulary: smallest-prime-factor / earliest-catch
  behaviour, witness count, balanced divisor frontier, prime-row
  proximity.
- **`experiments/math/nxn/POSET-FACTOR.md`** — earlier framing
  before the flow-tomography reframe; subsumed by L1 of this
  experiment. Kept as historical scaffold.


## What this is not

- Not Brief 4 itself. Brief 4 is the BPPW Monte Carlo on `M_n(N)`.
- Not Brief 2. CF-spike work lives in
  `experiments/acm-flow/cf/`.
- Not the composite-lattice work of `experiments/acm/diagonal/`.
