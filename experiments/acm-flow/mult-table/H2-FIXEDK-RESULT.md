# Fixed-K Cell-Resolved — Q2/Q3 Settled, Q1 Refined

A correction and refinement of `H2-CELL-RESULT.md` after critique
(see `h2_cell_fixedK.py`).

## What was wrong with H2-CELL-RESULT

Three things, all valid critiques from the cross-thread agent:

**Q1 — overclaim on mechanism.** I wrote "the c-shift in the bare
count is the integrated effect of this distributional shift." This
is wrong as a derivation. M_n(N) = Σ_D N_D(N, n); if every cell D
shares the same Ford deficit exponent, summing gives a prefactor
shift, not a c-shift. To produce a c-shift you need the cells to
have **different** deficit exponents that re-weight when occupancy
changes. I did not measure cell-wise deficits.

**Q2 — confounded comparison.** The fixed-N comparison varies three
n-dependent quantities simultaneously: residue density α_n, cofactor
box size √K = √N/n, and image size M_n. The growing ⟨d(k)⟩ at fixed
N could reflect any of these. To isolate the residue effect,
hold K constant.

**Q3 — n=7 reversal.** ⟨d(k)⟩ went 14.45 → 18.25 → 19.84 → 19.74
across n = 2, 3, 5, 7. The dip at n=7 was either finite-K noise or
a shape change — neither is a "plateau."

## The fixed-K experiment

`h2_cell_fixedK.py` runs cell-resolved enumeration at K ∈ {10⁴, 10⁵,
10⁶, 10⁷} for n ∈ {2, 3, 5, 7, 11, 13}. At each K, the cofactor box
√K is the same across n, removing the K-shrinkage confound.

### Q2/Q3 result: monotone in n, no reversal

| n | K=10⁴ | K=10⁵ | K=10⁶ | K=10⁷ |
|---|---|---|---|---|
| 2 | 8.094 | 10.572 | 13.297 | 16.218 |
| 3 | 11.082 | 14.355 | 18.106 | 22.014 |
| 5 | 13.080 | 17.198 | 21.677 | 26.367 |
| 7 | 13.956 | 18.251 | 23.114 | 28.103 |
| 11 | 14.479 | 19.157 | 24.272 | 29.574 |
| 13 | 14.732 | 19.365 | 24.560 | 29.938 |

⟨d(k)⟩ is **monotone increasing in n at every K**. The previous
reversal at n=7 was a finite-K artifact: at fixed N=10⁷, K shrunk
from 2.5M (n=2) to 200k (n=7), and the ⟨d(k)⟩ on a 200k integer
range is genuinely smaller. With K held constant the monotone pattern
is clean.

The rate slows at higher n. n=2 → n=3 increase is +5.97 (at K=10⁷).
n=11 → n=13 increase is +0.36. The monotone-with-saturation reading
of `H2-CELL-RESULT.md` was mostly right, but only AFTER the K
confound is removed.

### Q1 status: my mechanism claim doesn't hold up

Per-cell slope fit of `log(N_D / K)` vs `log(log K)` gives slopes
that vary widely across D (from −7.9 at D=2 to +4.8 at D=32 for n=2).
But these slopes are NOT Ford `c_D` values, because different cells
have qualitatively different asymptotic forms:

- D=2 (k prime): `N_D ~ √K / log K`. Dominant scaling is `K^{−½}`,
  not Ford `(log K)^{−c}`.
- D=3 (k = p²): same as D=2.
- D ≥ 4: cell asymptotics depend on D's divisor anatomy
  (Hardy-Ramanujan / Sathe-Selberg / Ford regimes).

The fit form `log(N_D/K) = const − c_D · log(log K)` assumes a
unified Ford-shape across cells, which is wrong. So the "slope per
cell" doesn't map to Ford `c_D`.

This means I cannot, with the data I have, demonstrate that the
c-shift in the bare count comes from the bin-distribution shift via
per-cell deficit variation. Two possibilities remain:

(i) **The mechanism does work** — but via the qualitative-shape
mixing across D (some cells `√K`-like, some `K(log K)^{−c}`-like).
Re-weighting cells with different shapes shifts the dominant scaling.
The analytic decomposition is non-trivial.

(ii) **The mechanism is something else.** The bin distribution shift
is a parallel observation, not the cause.

I cannot distinguish these.

## What we now have, honestly

Two empirical facts, both real, but not yet known to be linked:

- **Bare count c-shift** (`H2-RESULT-N1E8.md`): drift in M_n / M_2
  away from `(n−1)²/n⁴`, growing with n in rate, characteristic of
  a c-shift `c(n) > c(2)`.
- **d-distribution shift on the image at fixed K** (this doc):
  ⟨d(k)⟩ monotone in n; selection toward divisor-heavy k stronger
  with n.

Whether the second causes the first is **not established**. My
earlier framing in `H2-CELL-RESULT.md` overclaimed.

## Where this leaves Phase 4 / FINITE-RANK-EXPANSION

The `core/FINITE-RANK-EXPANSION.md` speculation — "shadows of rank
layers under different global projections" — has empirical support
at h=2 only in a refined sense:

- Local layer (closed): `Q_n(n²k) = 1 − d(k)/2` is universal across
  prime n. Settled.
- Global signature on the multiplication-table image: the d(k)
  distribution depends on n at fixed K. **Real**.
- Connection to the bare-count c-shift: **open**.

So the speculation isn't refuted, but the cleanest claim it supports
right now is "the d-distribution on coprime-to-n images is structured
in n" — not "the rank-2 Q_n cell structure causes the M_n(N)
deficit-exponent shift." That stronger claim needs the analytic
decomposition I haven't done.

## What I'd do next

(α′) **Analytic decomposition of `M_n(K) = Σ_D N_D(K, n)` by cell
asymptotic shape**, identifying which cells contribute Ford `K(log
K)^{−c}` scaling vs. lower-order scalings. The c-shift mechanism
hypothesis can be tested if we know which cells dominate at large K
and how their dominance depends on n. This is Tenenbaum / Ford
territory; pure thinking, no compute.

(γ) **Direct fit of `c(n)` from `M_n(K)·Φ(K)/K`** at multiple K,
treating M_n as a single observable. The fit slopes I computed in
`h2_predictor_n1e8.py` were estimates from only two K decades; with
fixed K = 10⁴..10⁷ here, we now have cleaner four-decade fits per n.
That gives a better empirical c(n).

(δ) **Composite n cell-resolved at fixed K**, exercising the
rank-2 + rank-3 decomposition for n ∈ {4, 6, 10}.

I'd lean (γ) first because it's a clean re-fit of existing data and
directly addresses what the c-shift's exponent looks like across n.
Then (α′) for the mechanism. (δ) for the rank decomposition.

## Files

- `h2_cell_fixedK.py` — fixed-K cell-resolved enumeration with
  per-cell slope fits.
- `h2_cell_fixedK.csv` — per-(n, K, D) data.
- `h2_cell_fixedK_summary.txt` — full tables and fit results.
- This document: corrected writeup.
