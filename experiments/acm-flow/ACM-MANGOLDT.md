# ACM-Mangoldt flow tomography

The 1196 proof works because it turns a primitive-set question into
a weighted divisibility-flow certificate: edge weight
`Λ(q) / (nq · log²(nq))` on the edge `nq → n`, with exact local
outflow given by the convolution identity
`Σ_{q | n} Λ(q) = log n`, and Mertens-type boundary control on the
near-inflow.

This experiment ports that mechanism to the ACM monoids.


## The question

Define the **monoid Mangoldt function** `Λ_n` on
`M_n = {1} ∪ nℤ⁺` by Möbius inversion:

    Σ_{d ∣_{M_n} m} Λ_n(d) = log m,   m ∈ M_n,    Λ_n(1) = 0,

where `d ∣_{M_n} m` means `d ∈ M_n` and `m/d ∈ M_n`. Equivalently
the coefficients of `−Z'_{M_n}(s) / Z_{M_n}(s)` with
`Z_{M_n}(s) = 1 + n^{−s}ζ(s)`. Closed form:

    Λ_n(m) = log(m) · Σ_{j ≥ 1, n^j | m} (−1)^(j−1) τ_j(m/n^j) / j,

where τ_j is the j-fold ordered divisor function.

**Does Λ_n behave like a positive flow weight, or does fake
primality force signed cancellation?** That is the experiment.

Ordinary `Λ` is nonnegative and lives on prime powers. `Λ_n`
starts by treating fake primes (n-primes) as full log-mass atoms,
then composites with multiple `M_n`-factorisations force
cancellation. The user-supplied first values for n=2:

    Λ_2(2)  = log 2,
    Λ_2(6)  = log 6,
    Λ_2(12) = 0,
    Λ_2(36) = −log 6.

These all reproduce in our pipeline (see the smoke check).

The deeper question: how much of the 1196 proof is "divisibility
poset" and how much is "positivity of ordinary Λ"?


## Three layers

### L1 — Λ_n sign profile

For `n ∈ {2, 3, 4, 5, 6, 10}` and `m ∈ M_n ∩ [n, X]`, compute
`Λ_n(m)`. Tabulate by exact n-height `h = ν_n(m)`. Per height:
count, positive count, negative count, `neg_mass / abs_mass`
ratio. Identify first negative locus.

### L2 — flow defect Δ_n(m; X)

For each `m ∈ M_n ∩ [n, X]`,

    Out_n(m)  =  Σ_{q ∣_{M_n} m} Λ_n(q) / (m · log²m)
              =  log(m) / (m · log²m)   [by the identity above]
              =  1 / (m · log m),

    In_n(m; X) =  Σ_{q ∈ M_n, m·q ≤ X} Λ_n(q) / (mq · log²(mq)),

    Δ_n(m; X) =  In_n(m; X) − Out_n(m).

`Out_n` is closed-form; `In_n` is a truncated tail. `Δ_n` measures
the flow defect at node m under the truncation. For ordinary `Λ`,
the analogous sum has Mertens-type control; here we want to see
whether `Λ_n`'s sign pattern lets the same control survive.

The script also records the first-order Mertens residual

    Δ'_n(m; X) = Δ_n(m; X) + 1/(m log X).

This is only a first subtractor for the boundary defect, not a
debiased statistic. Raw `Δ` remains in every output.

### L3 — block-typed totalisation

Partition `m` by base-10 digit class `d` and classify each `(n, d)`
block via `core/BLOCK-UNIFORMITY.md`:

- **smooth** — `n² ∣ b^(d−1)`. Exact n-prime block size.
- **Family E** — `b^(d−1) ≤ n ≤ ⌊(b^d − 1)/(b−1)⌋`. Exactly one
  n-prime per leading digit.
- **uncertified** — neither. Includes the lucky-cancellation
  cases.

For each `(n, d, type)` cell, compute `Σ Δ_n(m; X)` over `m` in
the cell. The headline question for L3: do the signed defects
**totalise** (small cell-sum, cancellations balance) on certified
blocks, while leaving residual structure on uncertified blocks?
That would be the bridge between the BIDDER positional-arithmetic
side and the divisibility-flow side.

At `X = 10000`, raw `Δ` is negative in every cell. The Mertens
residual shrinks the wall but does not remove it: the block-type
rollup has `ΣΔ'/ΣOut ≈ -0.181` on smooth blocks, `-0.446` on
uncertified blocks, and `-0.575` on the small Family-E cell. That
is evidence for truncation dominance with a remaining certified-block
advantage, not yet a clean block-type theorem; at fixed digit class,
smooth and uncertified cells still overlap.


## Outcomes worth caring about

- **Λ_n positive in some families.** A genuine fake-prime analogue
  of the 1196 random-chain certificate exists in those families.
- **Λ_n heavily signed but Δ totalises on exact blocks.** A signed
  1196 certificate whose cancellations are controlled by positional
  arithmetic — more interesting than the first case.
- **Signed defect correlates with digit-block seams, square
  boundaries, or `ν_p(n)`.** A new bridge between the
  Champernowne / BIDDER world and the divisibility-flow method.
- **No structure beyond noise.** The 1196 mechanism doesn't carry
  to non-UF monoids in any useful way; the sign-table is recorded
  as a property of the monoid and the program goes elsewhere.


## Files

| file | role |
|---|---|
| `acm_mangoldt_tomography.py` | implementation — three layers |
| `ACM-MANGOLDT.md` | this document |
| `acm_mangoldt.csv` | per-row `(n, m, height, d, block_type, Λ, Out, In, Δ, Δ')` |
| `lambda_n{n}.png` | per-n scatter of Λ_n(m) vs m, coloured by sign |
| `delta_n{n}.png` | per-n scatter of Δ_n(m; X) vs m |
| `delta_mertens_n{n}.png` | per-n scatter of Δ'_n(m; X) vs m |
| `summary.txt` | L1 height tables and L3 block totalisations |


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
plots + CSV + summary
```

Pure Python in the Sage environment. No Sage-specific calls.

```
sage -python acm_mangoldt_tomography.py
```

Default `X = 10000`. Bumping is cheap: τ pre-compute is the
bottleneck and scales like `X · log² X`.


## Sanity check

The script asserts the user-supplied values for n=2 before the
main sweep:

    Λ_2(2)  = log 2     ≈  0.693147
    Λ_2(6)  = log 6     ≈  1.791759
    Λ_2(12) = 0
    Λ_2(36) = −log 6    ≈ −1.791759

Mismatch on any of those exits with a non-zero status before
anything else runs.


## Coupling

- **Brief 4 (Multiplication-table on M_n)** — the BPPW-modified
  Monte Carlo on `M_n(N) · Φ(N) / N` is gated on the `Λ_n`
  sign-table and Δ totalisation result here. See
  `EXPERIMENTAL.md` Brief 4 (rewritten).
- **`core/BLOCK-UNIFORMITY.md`** — the smooth and Family-E lemmas
  drive the L3 block partition.
- **`experiments/math/nxn/POSET-FACTOR.md`** — earlier framing
  before the flow-tomography reframe; subsumed by L1 of this
  experiment. Kept as historical scaffold.


## What this is not

- Not Brief 4 itself. Brief 4 is the BPPW Monte Carlo on M_n(N).
- Not Brief 2. CF-spike work lives in
  `experiments/acm-champernowne/base10/cf/`.
- Not the composite-lattice work of `experiments/acm/diagonal/`.
