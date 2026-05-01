# GPT5 Notes — Organizing Plan

## Organizing program

Treat `C_b(n)` as a *rendered surface* of the deletion rule `n ∤ c`. Every
observed feature in the digit stream should be separated into one of four
bins:

1. **Local rank algebra** — visible inside the finite-rank `Q_n` layer.
2. **Base / block geometry** — created by radix structure and concatenation
   boundaries.
3. **Deep-index asymptotic behavior** — features that follow `K` (scale /
   cutoff geometry).
4. **Nonlinear aggregate readout** — created by global maps like continued
   fractions, signed cumulants, autocorrelations, etc.

The interesting discoveries will be **features that refuse to stay in one
bin**.

Framing premise: for `n ≥ 2` the `K`-th `n`-prime is directly indexable by
one divmod, so the same `K`-coordinate names both a lattice atom and a
position in the Champernowne stream. That makes `(n, K)` a legitimate
spectroscopic window rather than just an enumeration parameter. The
question is not "are these prime-like?" but **"how much of the deletion
rule survives after digit concatenation?"**


## Branches to explore

### 1. Phase diagrams over `(n, K)` and `(n, k)`
For each `n`, read the first `K` n-primes, concatenate them, and extract
observables — digit frequencies, block frequencies, running digital sum,
continued-fraction partial quotients, local entropy, autocorrelation,
Walsh/wavelet spectra. Plot those observables as surfaces over `n` and
`K`. Goal: see which features sort by `n`, by factorization type of `n`,
by base relation, and by depth. Not a single "randomness" verdict.

#### Examples

- [`experiments/acm-champernowne/base10/survivors/l1_grid.py`](experiments/acm-champernowne/base10/survivors/l1_grid.py)
  — leading-digit L1-deviation gap as a heatmap on the `(n_0, K)` square.
  A direct digit-frequency surface over `(n, K)`.
- [`experiments/acm-champernowne/base10/art/q_distillery/q_lattice_4000.py`](experiments/acm-champernowne/base10/art/q_distillery/q_lattice_4000.py)
  — 4000×4000 `(n, k)` rendering of `Q_n` at `h = 5`. The rank-algebra
  observable plotted as a literal `(n, k)` surface.
- [`experiments/acm-champernowne/base10/art/q_distillery/q_h5_full_scan.py`](experiments/acm-champernowne/base10/art/q_distillery/q_h5_full_scan.py)
  — `Q_n` at `h = 5` swept across `n ∈ [2, 30]` and ordered by `n`-shape.
  Phase-diagram-by-`n` with the factorization-type sort the next branch
  asks for.
- [`experiments/acm-champernowne/base2/forest/entropy_landscape/entropy_landscape_deep.py`](experiments/acm-champernowne/base2/forest/entropy_landscape/entropy_landscape_deep.py)
  — k-gram entropy deficit as a function of monoid `n` and window size `k`
  (1..16). The "local entropy" surface item, directly.
- [`experiments/acm-champernowne/base2/forest/rle_spectroscopy/rle_spectroscopy.py`](experiments/acm-champernowne/base2/forest/rle_spectroscopy/rle_spectroscopy.py)
  — run-length distribution heatmap across `n = 1..256`. The "block
  frequencies" surface item.
- [`experiments/acm-champernowne/base2/forest/walsh/walsh.py`](experiments/acm-champernowne/base2/forest/walsh/walsh.py)
  — Walsh-Hadamard spectra per monoid `n`. The "Walsh/wavelet spectra"
  item, named on the list.
- [`experiments/acm-champernowne/base2/forest/autocorrelation/echoes_lattice.py`](experiments/acm-champernowne/base2/forest/autocorrelation/echoes_lattice.py)
  — autocorrelation lattice indexed by `n`. The "autocorrelation"
  observable across the `n`-axis.
- [`experiments/acm-champernowne/base10/shutter/rolling_shutter_heatmap.py`](experiments/acm-champernowne/base10/shutter/rolling_shutter_heatmap.py)
  — first-digit-frequency surface across an addition-depth axis. Same
  observable as `survivors/l1_grid` but with depth-of-stream substituted
  for `K`.
- [`experiments/acm-flow/cutoff_ray_scan.py`](experiments/acm-flow/cutoff_ray_scan.py)
  — controlled sweep of the truncation coordinate `Y` at fixed `(n, m)`.
  The `K`-axis version of the program, with `n, m` held still.
- [`experiments/acm-flow/payload_scan.py`](experiments/acm-flow/payload_scan.py)
  — fixed-cutoff sweep over payload `m` at fixed `(n, h)`. The dual
  scan: holds `K` saturated and varies the local `n`-coordinate.

### 2. Base–monoid resonance
The base `b` and the algebraic parameter `n` should interact strongly
when `n` is `b`-smooth, weakly-but-not-trivially when `gcd(n, b) = 1`,
and strangely in the "lucky cancellation" leftovers. Block-uniformity
already shows exact leading-digit uniformity arising from at least three
mechanisms (smooth divisibility, Family E minimal blocks, uncharacterised
cancellation triples). Treat this as a **spectral classification
problem**: which apparent uniformities are structural, which are boundary
coincidences, which persist under deeper windows?

#### Examples

- [`core/BLOCK-UNIFORMITY.md`](core/BLOCK-UNIFORMITY.md) — source of the
  smooth / Family E / cancellation-triple trichotomy the branch refers
  to. Sufficient `(b, n, d)` condition for exact equidistribution, and
  the not-yet-characterised counterexamples.
- [`experiments/acm-champernowne/base2/HAMMING-BOOKKEEPING.md`](experiments/acm-champernowne/base2/HAMMING-BOOKKEEPING.md)
  — closed-form bit-balance for `n = 2^m`. The fully-smooth case in
  base 2, derived analytically.
- [`experiments/acm-champernowne/base2/forest/hamming_strata/`](experiments/acm-champernowne/base2/forest/hamming_strata/)
  — sliding-window Hamming weight per `(n, d)` class, testing the
  bit-balance prediction across `v_2(n)` strata. Directly maps the
  b-smooth-depth → resonance-strength axis.
- [`experiments/acm-champernowne/base2/forest/one_bias/one_bias.py`](experiments/acm-champernowne/base2/forest/one_bias/one_bias.py)
  — running 1-bit fraction; explicitly contrasts the `n = 2` race
  (forced trailing 0 vs forced penultimate 1) against odd `n` (no
  forced bits). The b-smooth vs gcd-1 split made an experiment.
- [`experiments/acm-champernowne/base2/forest/valuation/`](experiments/acm-champernowne/base2/forest/valuation/)
  — `v_2(n)` as the organizing axis for binary stream signatures.
  Forest grid, polar fan, and residual-after-depth-prediction views.
- [`experiments/acm-flow/residual_ablation_grid.py`](experiments/acm-flow/residual_ablation_grid.py)
  — bins residuals by `BLOCK_ORDER = ['smooth', 'family_E', 'uncertified']`,
  the exact three-bucket classification the branch names.
- [`experiments/math/benford/base_fingerprint.py`](experiments/math/benford/base_fingerprint.py)
  — L1-to-uniform of `log_b` mantissa swept continuously over `b ∈ [2, 40]`.
  Direct measurement of base-dependence on flow ensembles.
- [`experiments/acm-champernowne/base10/shutter/shutter_dual.py`](experiments/acm-champernowne/base10/shutter/shutter_dual.py)
  — addition-vs-multiplication first-digit panels: addition never
  reaches Benford; multiplication does in ~10 steps. Operation/base
  resonance asymmetry made visible.
- [`experiments/acm-champernowne/base10/stats/uniformity/UNIFORMITY.md`](experiments/acm-champernowne/base10/stats/uniformity/UNIFORMITY.md)
  — exact leading-digit uniformity at every complete base-`b` digit
  block. The structural mechanism that base-monoid resonance must
  explain or break.
- [`experiments/acm-champernowne/base10/sawtooth/sawtooth.py`](experiments/acm-champernowne/base10/sawtooth/sawtooth.py)
  — five-decade sawtooth tied to base-10 decade structure; the
  breakpoints (`u = 2, 5/2, 10/3, 5`) are pure base-`b` artifacts
  reading through the n-prime construction.

### 3. Rank spectroscopy via `Q_n`
The local object `Q_n(m)` closes exactly at rank `h = ν_n(m)` as a finite
signed stack of ordered-divisor counts — clean local algebra, while the
Champernowne stream gives a messy global readout. For each digit-stream
feature, ask explicitly: is it visible in the finite-rank `Q_n` layer,
or only created by concatenation boundaries, radix blocks, CF dynamics,
or finite cutoff?

#### Examples

- [`algebra/Q-FORMULAS.md`](algebra/Q-FORMULAS.md) and
  [`algebra/FINITE-RANK-EXPANSION.md`](algebra/FINITE-RANK-EXPANSION.md)
  — the algebraic substrate. Master expansion, Rank Lemma, the
  one-line theorem that `Q_n` closes at `h = ν_n(m)`.
- [`algebra/predict_q.py`](algebra/predict_q.py) +
  [`algebra/test_anchors.py`](algebra/test_anchors.py) — exact-rational
  Q_n machinery plus anchor tests (prime-row identity `Q_p(p^h) = 1/h`,
  the 8×6 shape×tau matrix at `h = 5`, the universal h=2 cliff).
- [`experiments/acm-flow/q_n_verify.py`](experiments/acm-flow/q_n_verify.py)
  — empirically verifies the master expansion against every row of
  `payload_q_scan.csv`. The Q_n closure as a continuously-tested fact.
- [`experiments/acm-flow/payload_q_scan.py`](experiments/acm-flow/payload_q_scan.py)
  — switches the local observable from `Λ_n` to `Q_n` directly,
  declaring "the structure lives in `Q_n`; `log(m)` is just scale."
  The branch question answered, in the small.
- [`experiments/acm-flow/hardy_composite_q.py`](experiments/acm-flow/hardy_composite_q.py)
  — deep composite-Q witnesses: builds `m` of arbitrary rank `h` by
  multiplying atoms, then evaluates Q_n by two structurally
  independent paths and asserts exact `Fraction` equality.
- [`experiments/acm-champernowne/base10/art/q_distillery/q_rank_lemma_skylight.py`](experiments/acm-champernowne/base10/art/q_distillery/q_rank_lemma_skylight.py)
  — the integer staircase `ν_n(m)` made literal. Rows beyond `h`
  hang as ghost panes; the bright staircase IS the rank lemma.
- [`experiments/acm-champernowne/base10/art/q_distillery/q_distillery.py`](experiments/acm-champernowne/base10/art/q_distillery/q_distillery.py)
  + [`Q_DISTILLERY.md`](experiments/acm-champernowne/base10/art/q_distillery/Q_DISTILLERY.md)
  — master expansion as visual distillation across the four
  factorisation types (prime, prime power, squarefree, mixed).
- [`experiments/acm-champernowne/base10/art/q_distillery/q_towers.py`](experiments/acm-champernowne/base10/art/q_distillery/q_towers.py)
  + [`q_cancellation_furnace_h3_ns.py`](experiments/acm-champernowne/base10/art/q_distillery/q_cancellation_furnace_h3_ns.py)
  — pre-cancellation positive vs negative mass. The branch's "signed
  stack" rendered as opposing streams; complexity sits in the
  cancellation, not in the survivor.
- [`experiments/acm-champernowne/base10/art/q_distillery/q_h5_shape_tau_matrix.py`](experiments/acm-champernowne/base10/art/q_distillery/q_h5_shape_tau_matrix.py)
  — the (shape × tau-signature) condensation at `h = 5`, with
  kernel-zero cells gold-ringed. The cleanest classification view
  of the local algebra.
- [`experiments/acm-champernowne/base10/art/q_distillery/q_lattice_h_parity_viz.py`](experiments/acm-champernowne/base10/art/q_distillery/q_lattice_h_parity_viz.py)
  + [`HIGHER-H-EXPECTATIONS.md`](experiments/acm-champernowne/base10/art/q_distillery/HIGHER-H-EXPECTATIONS.md)
  — h-parity of the Q-lattice angular spectrum, with predictions for
  `h = 6, 7, 8` reads. A live test of whether higher-rank algebraic
  structure leaks into a global geometric readout.

### 4. Universality classes by factorization shape of `n`
Prime `n`, prime powers, squarefree composites, and mixed-exponent
composites should not look the same — the local formulas already
distinguish them (prime rows: one binomial factor; prime powers: altered
index structure; multi-prime: products of binomial factors). Don't plot
`n = 2,3,4,5,6,7,8,...` as a flat list; **color/facet by shape** (`p`,
`p^a`, `pq`, `p^a q`, ...). Ridges may be invisible in ordinary numeric
order.

#### Examples

- [`experiments/acm-champernowne/base10/art/q_distillery/q_h5_full_scan.py`](experiments/acm-champernowne/base10/art/q_distillery/q_h5_full_scan.py)
  — `Q_n` at `h = 5` swept across `n ∈ [2, 30]` and **sorted by shape
  class** (sorted tuple of prime exponents). The within-class plateaus
  are dead flat *by construction*; flatness IS the structural identity,
  rendered visible by the layout.
- [`experiments/acm-champernowne/base10/art/q_distillery/q_h5_shape_tau_matrix.py`](experiments/acm-champernowne/base10/art/q_distillery/q_h5_shape_tau_matrix.py)
  — condensation: 8 rows (shapes) × 6 columns (tau-signatures). The
  full universality-class table at `h = 5` on a single canvas, with
  kernel-zero cells gold-ringed.
- [`experiments/acm-champernowne/base10/art/q_distillery/q_distillery.py`](experiments/acm-champernowne/base10/art/q_distillery/q_distillery.py)
  + [`q_merger_345.py`](experiments/acm-champernowne/base10/art/q_distillery/q_merger_345.py)
  + [`q_merger_h5.py`](experiments/acm-champernowne/base10/art/q_distillery/q_merger_h5.py)
  — four canonical vessels in parallel: `n = 2` (prime), `n = 4`
  (prime power), `n = 6` (squarefree), `n = 12` (mixed). The four
  shape classes the branch enumerates, each with its own column.
- [`algebra/predict_q.py`](algebra/predict_q.py) +
  [`algebra/Q-FORMULAS.md`](algebra/Q-FORMULAS.md) — the master
  expansion's coefficient is `∏_i C(a_i (h - j) + t_i + j - 1, j - 1)`,
  a **product over prime exponents of `n`**. Shape-classification is
  the algebraic substrate, not a presentation choice.
- [`experiments/acm-flow/payload_q_scan.py`](experiments/acm-flow/payload_q_scan.py)
  + [`PHASE1-RESULTS.md`](experiments/acm-flow/PHASE1-RESULTS.md) —
  panel pushed to `h ∈ {2, 3, 4, 5}` to ask: do prime / prime-power /
  multi-prime have explicit divisor-function formulas at each `h`?
  The branch question, run as a phase.
- [`experiments/acm-flow/hardy_composite_q.py`](experiments/acm-flow/hardy_composite_q.py)
  — explicitly distinguishes prime, prime-power, and squarefree-
  multi-prime `n`, because atom cofactors can re-introduce primes
  dividing `n` only in the latter classes. Class-aware deep-rank
  evaluation.
- [`experiments/acm-champernowne/base2/forest/valuation/`](experiments/acm-champernowne/base2/forest/valuation/)
  — organises `n = 1..4096` by 2-adic valuation: 256 odd-rooted
  trunks branching downward as `v_2(n)` grows. Shape-by-prime-
  exponent for `p = 2`, rendered as a literal forest.
- [`experiments/acm-champernowne/base2/forest/rle_spectroscopy/`](experiments/acm-champernowne/base2/forest/rle_spectroscopy/)
  — predicts (and shows) horizontal ridges in the run-length
  heatmap aligned with `v_2(n)`. Odd `n` qualitatively different
  from even `n`; powers of 2 are singular rows.
- [`experiments/acm-champernowne/base2/forest/walsh/WALSH.md`](experiments/acm-champernowne/base2/forest/walsh/WALSH.md)
  — 44 stable Walsh signals split into three populations:
  reproducible from `v_2(n)` + length, from length alone, or from
  neither. A native universality-class result for the binary
  Walsh substrate.
- [`experiments/acm-flow/mult-table/`](experiments/acm-flow/mult-table/)
  — `α_n = (n − 1)/n` and `α_n² = ((n − 1)/n)²` enter the h=2 cell
  predictions, so prime vs composite `n` (via density and cofactor
  geometry) sort the empirical ratios at fixed `K`.

### 5. Autocorrelation along rows
The within-row parity profile already hints that the `k`-axis has
structured correlations. For prime `n = p`, the residue of lag `L mod p`
controls how classes of `k` and `k+L` couple; for `n = 2`, even and odd
lags have sharply different behavior. The spectroscope should pick up:
not just "digits look normal," but **"hidden algebra leaks through lag
structure."**

#### Examples

TODO:MAKE BULLETS

### 6. Deep-window sampling
The n-prime sequence is random-access for `n ≥ 2` — inspect windows
starting near absurdly large `K` without generating the prefix.
Distinguishes prefix artifacts from asymptotic features.

```
window(n, K, W) = digits of p_K(n), p_{K+1}(n), ..., p_{K+W-1}(n)
```

Compare spectra for fixed `W` while moving `K` across scales:
- feature follows `K` → scale / cutoff geometry
- feature follows `n` → substrate
- feature follows `b` vs `n` → encoding resonance

#### Examples

TODO:MAKE BULLETS

### 7. Continued-fraction spike anatomy
Local closure does not imply aggregate closure: continued fractions,
off-spike denominator processes, finite-`K` multiplication-table
residuals, and cross-base digit statistics remain open globally.
Continued fractions may act as a **nonlinear amplifier** for tiny
block-boundary regularities in the digit stream.

#### Examples

TODO:MAKE BULLETS

### 8. Inverse problems
Turn the spectroscope around. Instead of "what does `n` produce?", ask
"what algebraic parameter left this residue?":
- Given only a digit window, can you infer `n`?
- Given a witness-list surface, can you infer whether `n` was prime,
  prime power, or squarefree?
- Given only autocorrelation or CF features, can you recover
  `gcd(n, b)`, `v_p(n)`, or `ord_b(n)`?

#### Examples

- [`experiments/acm-flow/cf/PRIMITIVE-ROOT-FINDING.md`](experiments/acm-flow/cf/PRIMITIVE-ROOT-FINDING.md)
  — direct hit on the third sub-question: classifies the off-spike
  denominator offset `offset(n)` by `ord(b, n)` and `gcd(n, b)`.
  Given a CF feature, recover the multiplicative-order family.
- [`experiments/acm-flow/cf/MU-CONDITIONAL.md`](experiments/acm-flow/cf/MU-CONDITIONAL.md)
  + [`MEGA-SPIKE.md`](experiments/acm-flow/cf/MEGA-SPIKE.md) —
  inverts the boundary-spike subsequence into a closed-form
  irrationality measure `μ(C_b(n)) = 2 + (b − 1)(b − 2)/b`. CF
  feature → algebraic invariant of the digit stream.
- [`experiments/acm/diagonal/cantor_walk/UNORDERED-CONJECTURE.md`](experiments/acm/diagonal/cantor_walk/UNORDERED-CONJECTURE.md)
  + [`verify_greedy.py`](experiments/acm/diagonal/cantor_walk/verify_greedy.py)
  — pure inverse problem: given the unordered multi-set of cell
  values from an `N × N` n-prime table, recover the row labels by
  greedy reconstruction. Position-as-decoder vs value-as-decoder
  separated cleanly.
- [`experiments/acm-champernowne/base2/forest/walsh/walsh_upgrade.py`](experiments/acm-champernowne/base2/forest/walsh/walsh_upgrade.py)
  + [`WALSH.md`](experiments/acm-champernowne/base2/forest/walsh/WALSH.md)
  — three-population classifier for the 44 stable Walsh signals:
  reproducible from `length-sequence + v_2(n)`, from length alone, or
  from neither. Inverse procedure: given a Walsh feature, identify
  the smallest synthetic control that reproduces it.
- [`experiments/acm-champernowne/base2/forest/valuation/residual_map.py`](experiments/acm-champernowne/base2/forest/valuation/residual_map.py)
  — subtracts the `v_2(n)` row-mean from each cell's mean zero-run
  length; the residual is what `v_2(n)` *cannot* explain. Inverse
  hygiene: name the recoverable invariant, then show what survives
  it.
- [`experiments/acm-champernowne/base2/forest/rle_spectroscopy/rle_spectroscopy.py`](experiments/acm-champernowne/base2/forest/rle_spectroscopy/rle_spectroscopy.py)
  — the run-length heatmap is read as a forward map (`v_2(n)` →
  ridges), but its diagnostic is the inverse: given a ridge, identify
  `v_2(n)`.
- [`experiments/acm-champernowne/base2/STRUCTURAL-SIGNATURES.md`](experiments/acm-champernowne/base2/STRUCTURAL-SIGNATURES.md)
  — synthesis: which observables in the binary stream carry stable
  signal traceable to which algebraic property of `n`. The base-2
  inverse-problem map.
- [`experiments/acm-flow/phase1_destroyers.py`](experiments/acm-flow/phase1_destroyers.py)
  + [`experiments/VISUAL-REDUCTION-DISCIPLINE.md`](experiments/VISUAL-REDUCTION-DISCIPLINE.md)
  — destroyer / shuffle / family-geometry-subtraction protocol. Tells
  you which apparent feature of the readout is actually invertible
  back into a named algebraic source vs which is a marginal
  artifact.
- [`experiments/math/hardy/SURPRISING-DEEP-KEY.md`](experiments/math/hardy/SURPRISING-DEEP-KEY.md)
  — names the inverse program at the meta level: every BIDDER
  surprise has the shape "a derived object turns out to be a
  substrate computation seen from a particular angle, plus at most
  one local correction." The pattern this branch is asking us to
  mechanise.
- [`experiments/acm-flow/cf/cf_spikes_extended.py`](experiments/acm-flow/cf/cf_spikes_extended.py)
  + [`CROSS-BASE-RESULT.md`](experiments/acm-flow/cf/CROSS-BASE-RESULT.md)
  — measures CF spike scales across `(b, n, d)` and inverts to the
  closed form `(n − 1)/n²` factor; given a spike-scale measurement,
  recover the algebraic prefactor (and so distinguish prime vs
  composite `n`).

### 9. PNT-analog side channel
The signed Mangoldt-style cumulant `ψ_{M_n}(x)` is a separate but related
spectral object — does the recovered log-coefficient mass sum like `x`
even though the monoid is non-UFD and the weights are signed? The
candidate main term is independent of `n`, but the convergence rate
appears `n`-dependent. **Companion observable**: the digit stream may
show visible `n`-structure exactly where the signed cumulant shows slow
convergence.

#### Examples

- [`experiments/math/beurling/PNT-ANALOGY.md`](experiments/math/beurling/PNT-ANALOGY.md)
  — states the branch's conjecture verbatim: `Λ_{M_n}(m) := Q_n(m) log m`,
  `ψ_{M_n}(x) := Σ_{m ≤ x, m ∈ M_n} Λ_{M_n}(m)`, conjectured `ψ_{M_n}(x) ~ x`
  with main term `+1` independent of `n` (from the residue
  `Res_{s=1}[-ζ'_{M_n}/ζ_{M_n}] = +1`).
- [`experiments/math/beurling/zeta_mn.py`](experiments/math/beurling/zeta_mn.py)
  — numerical substrate: `zeta_mn`, `log_zeta_mn`, `log_deriv_mn`,
  `psi_mn`. The PNT-analog computation as a library, mpmath +
  exact-rational `Q_n`.
- [`experiments/math/beurling/EXP01-FINDINGS.md`](experiments/math/beurling/EXP01-FINDINGS.md)
  + [`exp01_olofsson_transplant.py`](experiments/math/beurling/exp01_olofsson_transplant.py)
  — the literal Olofsson rigidity transplant (null) and the pivot to
  the signed-Mangoldt analog (positive). First run of `ψ_{M_n}(x)/x`,
  with `+1` candidate rate confirmed.
- [`experiments/math/beurling/EXP02-FINDINGS.md`](experiments/math/beurling/EXP02-FINDINGS.md)
  + [`exp02_zeros_and_residual.py`](experiments/math/beurling/exp02_zeros_and_residual.py)
  — extends `ψ_{M_n}/x` to `5×10⁶`, finds zeros of `ζ_{M_n}` in the
  critical strip (some at `Re s < 1/2`), confirms no zeros on
  `Re s = 1`. The branch's "convergence rate `n`-dependent" finding,
  empirically. `ψ_{M_n}(x) ~ x` holds with rate cleanly slower than
  classical PNT and visibly stratified by `n`.
- [`experiments/math/beurling/BEURLING.md`](experiments/math/beurling/BEURLING.md)
  — Beurling generalised-primes framework (Tauberian / Wiener–Ikehara)
  the PNT analog rests on; thesis-level scaffolding for the signed-
  cumulant question.
- [`algebra/Q-FORMULAS.md`](algebra/Q-FORMULAS.md) +
  [`algebra/FINITE-RANK-EXPANSION.md`](algebra/FINITE-RANK-EXPANSION.md)
  — `Q_n` is the master-expansion coefficient of `log ζ_{M_n}`, so the
  signed weight `Λ_{M_n} = Q_n · log m` is forced by these formulas.
  The local algebra that the global cumulant is integrating over.
- [`experiments/acm-flow/acm_mangoldt_tomography.py`](experiments/acm-flow/acm_mangoldt_tomography.py)
  + [`ACM-MANGOLDT.md`](experiments/acm-flow/ACM-MANGOLDT.md) — the
  flow-tomography apparatus that produced `Λ_n` per-`m` data and
  framed `Δ_n(m; X)` as the truncated cumulant. Predecessor of the
  Beurling ψ work.
- [`experiments/math/hardy/hardy_q_mertens_validation.py`](experiments/math/hardy/hardy_q_mertens_validation.py)
  + [`hardy_q_depth_invariance.py`](experiments/math/hardy/hardy_q_depth_invariance.py)
  — depth-shift mechanism for `Q_n` distributions traced to the
  Dirichlet–Mertens summatory `(1/N) Σ_{j ≤ N} d(j) = log N + (2γ−1)
  + O(N^{−1/2})`. Convergence-rate plumbing for the cumulant.
- [`experiments/math/hardy/hardy_q_cofactor_pinpoint.py`](experiments/math/hardy/hardy_q_cofactor_pinpoint.py)
  — disambiguates magnitude-only vs Hardy-specific structure in the
  cofactor-pair distribution; `E[d(c_1 c_2)]` at growing magnitude is
  the classical-multiplicative-NT term that controls how fast
  `ψ_{M_n}/x → 1`.
- [`experiments/acm-champernowne/base2/STRUCTURAL-SIGNATURES.md`](experiments/acm-champernowne/base2/STRUCTURAL-SIGNATURES.md)
  + [`forest/walsh/WALSH.md`](experiments/acm-champernowne/base2/forest/walsh/WALSH.md)
  — the **companion observable**: per-monoid binary-stream signatures
  with stable `n`-stratified Walsh signals. The direct candidates for
  "digit-stream `n`-structure" to align against the Beurling ψ
  convergence rate.

### 10. Kernel-zero bands and higher-rank cancellations
At higher `h`, the finite-rank formulas can produce structured
cancellation bands — not "noise disappearing," but algebraic shadows of
alternating divisor stacks. Look for whether those zero bands leave a
visible trace in the Champernowne digit spectrum, especially when
plotting by `(n, h, τ-signature)` rather than raw integer order.

#### Examples

TODO:MAKE BULLETS


## Reply to Web Agent

Once the migrant survey closes (we have three runs landed:
`EXP1-FINDINGS.md`, `EXP2-FINDINGS.md`, `EXP3-FINDINGS.md`), promote
**one** combined experiment back to the web agent that drafted the
organising program above. The reply should be a single self-contained
deliverable.

**Format requirements:**

- **Two images.** One should show the headline finding directly (the
  observed signal). One should show the migrant claim — either as a
  decomposition into bin components or as a synthesised prediction
  matched against the observed signal. Side-by-side or paired panels
  are fine; the goal is for the agent to read the cross-bin coupling
  off the image without re-running anything.
- **Dense, productive text.** Not a tour of the directory. State the
  finding, give the numerical evidence, name the bins involved, point
  to the substrate files used, and close with the prediction the
  finding makes about the rest of the four-bin program. Keep it under
  ~600 words.
- **Substrate transparency.** Every quantity in the figure must be
  reproducible from the named substrate files (`l1_grid.npz`,
  `exp07_lattice.npz`, etc.). The agent must be able to re-derive
  any line of the text from the materials in `migrants/`.

**What the deliverable must include:**

1. The cross-cutting finding in one sentence.
2. The substrate observable and the bin attribution.
3. The numerical hooks: the correlations, support claims, fit
   coefficients, and any sharp-feature locations in `(n_0, K)` or
   `n` coordinates.
4. The next-step prediction: what other location in the four-bin
   program should now show a matching signal.
5. The destroyer: what shuffle / re-randomization would kill the
   finding if it were artifact, and what survived it.

**What the deliverable must NOT do:**

- Re-summarise the organising program. The agent wrote it.
- Walk through every migrant. Promote *one* combined finding.
- Promise future experiments without committing.
