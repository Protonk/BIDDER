# Migrants

Features that refuse to stay in one bin.

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


## Experiments

### 1. Bin-peel of the L1 tracking-gap harmonics

Substrate: the cached `(n_0, K)` heatmap of mean signed gap
`surv_L1 − bundle_L1` (`l1_grid.npz`, copied from
`base10/survivors/`). The zoom view of that heatmap shows three
harmonic feature families: diagonal puffs along `K = n_0 + 1`,
horizontal bands at distinguished `n_0`, and inner vertical /
horizontal striations. Each could be single-bin or pan-bin.

Method: fit four bin-pure predictor templates to `G(n_0, K)` —
one per bin — by least squares, then read the residual.

- **Bin 1 (rank algebra).** Indicator `K ≥ n_0` smoothed by sigmoid:
  the first-collision activation along `K = n_0 + 1`.
- **Bin 2 (base/block).** Decade-crossing template
  `|sin(π · log₁₀(K · n_0))|`, ridged on the hyperbolae `K · n_0 = 10^d`.
- **Bin 3 (K-asymptotic).** Smooth `1/√K` decay, `n_0`-independent.
- **Bin 4 (nonlinear).** CF mega-spike scale `S_k(n_0, b=10)` at `k=4`,
  closed form from `cf/MEGA-SPIKE.md`.

Output: a six-panel figure — `G`, the four fitted components
`α_i · P_i`, and the residual `R = G − Σ α_i P_i`. Read attribution
from where each component carries weight, and read pan-bin features
from where `|R|` stays large after the fit.

Files: `bin_peel.py`, `bin_peel.png`, `bin_attribution.png`,
`EXP1-FINDINGS.md`.

**Result (first pass).** Smooth bin-pure templates explain only 7.8 %
of the gap variance; residual `R` is visually indistinguishable from
`G`. The harmonics are sharp and arithmetic, not smooth — the bin-pure
*smooth* peel is the wrong shape. See `EXP1-FINDINGS.md` for the
numerical readout and the sharper-predictor agenda for iteration 2.

### 2. n-fingerprint alignment across six readouts

Where item 1 sweeps the `(n_0, K)` plane and asks which bin owns each
cell, this one fixes a single `n`-ladder and asks whether the same
`n`-ranking emerges across six readouts that nominally live in
different bins. Aligned rankings = a multi-bin signature of `n`;
disaligned rankings = each readout is reading a different surface of
the substrate. Anomalies — `n` whose rank flips between readouts —
are the genuinely multi-bin entries.

Ladder: `n ∈ {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 18, 20,
25, 27, 30, 32}` — covers prime, prime-power, squarefree, mixed, and
both base-10-smooth and base-10-coprime regimes.

Six per-`n` readouts:

- **Bin 1.** `max_{m ≤ 10⁴, h ≤ 4} |Q_n(m)|`, via
  `algebra/predict_q.q_general`.
- **Bin 2a (base 10).** Leading-digit L1 deviation of the first 10⁴
  `n`-primes.
- **Bin 2b (base 2).** `|mean bit-fraction − 0.5|` over the same atom
  list. (The closed-form deficit `1/(2d)` from `HAMMING-BOOKKEEPING.md`
  rendered as a single empirical scalar.)
- **Bin 3.** Slope of `log₁₀(L1)` vs `log₁₀(K)` on
  `K ∈ {10³, 2·10³, 5·10³, 10⁴}`.
- **Bin 4a (CF).** `S_4(n, 10) = (n−1)/n² · (10³(4·8 + 10/9) − 1/9)`,
  closed form from `cf/MEGA-SPIKE.md`.
- **Bin 4b (signed cumulant).** `ψ_{M_n}(10⁵) / 10⁵ − 1`, via
  `experiments/math/beurling/zeta_mn.psi_mn`.

Analysis: Spearman correlation matrix across the six readouts on the
20-`n` ladder. Hypothesis: bins 1, 4a, 4b track each other (substrate
algebra leaking into nonlinear aggregates), while bin 2a / 2b split
along base-`b` smoothness.

Files: `n_fingerprint.py`, `n_fingerprint_table.txt`,
`n_fingerprint_corr.png`, `n_fingerprint_parallel.png`,
`EXP2-FINDINGS.md`.

**Result.** Three populations: a substrate spine of bins 1 / 4a / 4b
mutually correlated at +0.98–1.00 (substrate algebra leaks through
CF and cumulant readouts); base-related bins 2a / 2b refuse to align
(`±0.39` max with the spine); bin 3 sits in the middle at +0.63.
Genuine multi-bin entry: **`n = 9`** has the flattest base-10
leading-digit distribution in the ladder by an order of magnitude — a
feature jointly anchored in rank algebra (prime power) and in being
`b − 1` for base 10.

### 3. Lattice subtraction — κ-derivative as a bin-1 isolator

Predecessor: `experiments/acm-champernowne/base10/survivors/exp07_kappa_derivative.py`
(copied here as `exp07_kappa_derivative.py`). The discrete derivative
of `κ(K, n_0)` exposes the pair-collision lattice that the smooth
κ-surface and the L1 gap heatmap both hide. The lattice is bin-1-pure
(local rank algebra). Where `l1_grid.npz`'s gap is bin 1 × bin 2
mixed, the lattice is bin 1 alone — an isolator.

Charter: load both `l1_grid.npz` and the lattice cache, align the
K-axis, fit `G(n_0, K) ≈ α(n_0) · L(n_0, K)` per row, read the
residual as a bin-2 candidate. Test three claims:

- bin-1-quiet cells should have gap = 0 (support prediction);
- row-density of L should rank-correlate with row-RMS of `|G|`
  (horizontal-band attribution);
- α(n_0) signed coefficient encodes the leading-digit lens.

Files: `exp07_kappa_derivative.py`, `exp07_kappa_derivative.png`,
`exp07_lattice.npz`, `lattice_alignment.py`,
`lattice_alignment.png`, `lattice_alpha_per_row.png`,
`EXP3-FINDINGS.md`.

**Result.** Three claims, three confirmations.
1. **Support is bin-1-determined exactly.** All 718 lattice-quiet
   cells have `|G| = 0` to machine precision.
2. **Row magnitude is bin-1-aligned at ρ = +0.90.** The horizontal
   bands the L1 zoom showed are bin 1 × bin 2 coupling at the row
   scale.
3. **α(n_0) phase-flips sharply at `n_0 ≈ 320`.** This lines up
   with `n_0 ≈ √10⁵`, the intersection of the first-collision
   diagonal `K = n_0 + 1` with the `K · n_0 = 10⁵` decade hyperbola
   — a canonical bin 1 ∩ bin 2 ∩ bin 3 event. Above the threshold
   the bin-1 → bin-2 sign transmission flips. **First sharp
   multi-bin feature located on the substrate.**

The triangles in G that survive the per-row projection (residual
~82% of |G|) are the irreducible bin 1 × bin 2 product structure:
lattice firing modulated by the leading-digit phase of `K · n_0`.


## Audit (`AUDIT.md`)

Local audit run by a sibling agent. Reproducibility PASS — `l1_grid.npz`
byte-matches `../base10/survivors/`, all five scripts regenerate, the
spot-checks (718 quiet cells, row Spearman `+0.8959`, phase-flip at
n_0 = 320, EXP2 monotonicity) all confirmed. Destroyer fairness PASS,
robust under reseed (`ρ ≈ −0.33`, MAE `≈ 294 %`). Synthesis "100 %
explained" framing FAIL — `synthesis.py` recomputes `G` via the same
algorithm as the cached substrate generator and never loads
`exp07_lattice.npz`, so the perfect match is forced. The destroyer
half is the load-bearing experiment; the synthesis half is a code
consistency check. `WEB-AGENT-REPLY.md` revised accordingly at three
locations.


## Open Migrants (next runs, from the audit)

### 4. Non-tautological synthesis from `exp07_lattice.npz`

Build `G_predicted(n_0, K)` from lattice features only — support, count,
multiplicity per cell — combined with a leading-digit phase summary
derived from `(n_0, K)` not from `np.unique` on bundle atoms. No
recomputation of the survivor mask. Test against `G`. The expected
result is partial recovery (well below `ρ = +1`), with the residual
being the irreducible cell-level structure.

### 5. Destroyer seed ensemble

Run `synthesis.py` destroyer mode with `K ≥ 32` independent seeds.
Report mean and σ of `ρ(G, G_destroyed)`, sign-agreement, MAE. Compute
the rank of the observed surface against the destroyed-surface
distribution. The audit reseed at `seed = 123456` matched
(`ρ = −0.3329`); a full ensemble formalises this.

### 6. Phase-flip ladder + base-`b` migration

Build a finer `(n_0, K)` grid near `n_0 ∈ {100, 320, 1000}` and look
for `α(n_0)` sign-flips at `√10^4`, `√10^5`, `√10^6`. Re-run in base
2, 3, 5; the flip should migrate to `n_0 ≈ √b^d`. A bin-2-pure
prediction with no bin-1 freedom — the cleanest direct test of the
diagonal-decade-intersection mechanism.


### 7. Histogram-preserving destroyer (digit-placement vs digit-distribution) — RAN

Proposed by the web agent in the reply round. `placement_destroyer.py`
preserves the per-cell multiset of duplicate leading digits and
randomly permutes which duplicate unique atom gets which digit.

**Result.** Intermediate, with three-layer decomposition.

```
metric          shuffled    destroyed
Spearman ρ      +0.9030      −0.3183
Pearson r       +0.8601      +0.0035
sign agreement   95.4 %       29.5 %
MAE / mean|G|    31.5 %      294.5 %
```

The shuffle preserves 95 % of sign and 86 % of linear structure.
So the cross-cut splits at higher resolution into three layers:

1. Bin 1 (closed-form lattice) — support and row scale.
2. Bin 2 *distribution* (per-cell multiset of duplicate digits) —
   most of sign and magnitude.
3. Bin 2 *placement* (which atom gets which digit) — a real but
   smaller residual (~30 % MAE), concentrated in the low-K active
   wedge.

The full Benford destroyer collapses signal because it kills all
three; the placement destroyer attacks only layer 3 and isolates
its size. See `EXP4-FINDINGS.md` for the full readout and the
three-panel figure.

**Follow-up regression** (`placement_vs_lattice.py`): the placement
residual `|G − G_shuffled|` scales sub-linearly with cumulative
lattice density, `|R| ≈ 10⁻⁴·⁶² · L_cum^0.66` (log-log Pearson
+0.50; cumulative Spearman +0.60 beats per-step +0.41). Mechanism:
larger multiset → more permutation freedom, but adjacent permutations
of similar digits leave running L1 nearly invariant, so freedom
degrades sub-linearly.


### 8. Mechanism-separator destroyers

Two paired destroyers that share the histogram-preserving discipline
of #7 but along different axes:

- **Per-stream label preservation.** Within each `n`-stream, preserve
  every atom's leading digit; shuffle across `K` (positions within
  the stream). Tests whether the lattice structure × atom-to-K
  assignment matters.
- **Per-decade label preservation.** Within each base-10 decade
  `[10^{d-1}, 10^d)`, preserve the multiset of leading digits;
  shuffle across atoms in the decade. Tests whether the decade-block
  geometry alone is sufficient.

Together with #7 they separate three candidate mechanisms: collision
lattice, decade/block geometry, exact atom-to-digit assignment.
