# row_ogf_cliff — the row-OGF cliff under multiplicative scaling

## Target

Type:

    (p, q, e, H_max) → polynomial column
                       col[h - 1] := Q_p(p^h · q^e),    h = 1, …, H_max,
                     with three closed-form claims:
                       (i)   col[h - 1] = (-1)^(h - 1) C(e, h) / e   for h = 1..e;
                       (ii)  col[h - 1] = 0                          for h ∈ [e + 1, H_max];
                       (iii) col[e - 1] = (-1)^(e - 1) (e - 1)! / e!  (= leading
                             coefficient of F(x; p, q^e), forced equal to the
                             kernel-zero boundary value at Ω = h).

`p, q` are distinct primes, `e ≥ 1`, and `Q_p` is evaluated
exact-rationally via `algebra/predict_q.q_general`.

The substrate is a *column* of the Q-lattice indexed by `h`, in
contrast to `kernel_zero` which indexes by `k`. The marvel — per
`wonders/marvel-row-ogf-cliff.md` — is the **cliff at `h = e + 1`**:
the row truncates to exactly zero at the predicted index, with the
final non-zero coefficient forced to be the same multinomial that
appears at the kernel-zero boundary in `KERNEL-ZEROS.md` (ii).

The construction did not promise polynomial-ness; the master
expansion *could* have produced an infinite power series for every
cofactor. The cliff is forced, and this probe is built to test
that forcing.

The expected coordinate of detection in absence of the transducer is
the original `h`-axis: every cell of `col(p, q, e)` matches its
closed-form prediction.

## Transducer

Operation: scalar multiplication on the column,

    col'[h - 1] = c · col[h - 1],    c = 2.

Bound: `c = 2` (parameter-free probe at this `c`; sibling probes at
`c = -1`, `c = 0.5`, etc. would be separate per the framework's
"no run-time tunable parameters" rule).

Information budget: **blind** — sees only the cell vector, not
`p`, `q`, `e`, or `h`. Stack depth: 1.

Why scaling. Two of the three cliff claims above are
scale-invariant:

- (ii) `col[h - 1] == 0` is preserved by `c · 0 = 0`;
- (iii) the leading-coefficient *position* (highest non-zero `h`) is
  preserved, but its *value* scales by `c`.

So scaling preserves the *shape* of the cliff while destroying the
*forced multinomial value* — exactly the dual structure the wonders
doc names. Under `c = 2`, the cliff channel must hold; the leading-
multinomial channel must fail.

## Channels

| name | motivation | role |
|---|---|---|
| `no_op`                       | original `h`-axis predicate `col[h - 1] == Q_p(p^h q^e)` cell-by-cell | control |
| `cliff`                       | scale-invariant: cells at `h ∈ [e + 1, H_max]` are exactly zero (the cliff itself) | primary |
| `leading_multinomial`         | non-invariant: `col[e - 1] == (-1)^(e - 1) / e`, the kernel-zero boundary multinomial that is *forced* to be the row-OGF leading coefficient | primary |
| `qe_closed_form`              | non-invariant: full column matches `(-1)^(h - 1) C(e, h) / e` for `h = 1..H_max` (closed form `(1 - (1 - x)^e) / e`, independent of the master expansion) | primary, sharpest |
| `prime_row_identity_at_h1`    | does `col[0] == 1`? `MASTER-EXPANSION.md` C3 at `h = 1` predicts `c · 1 = c ≠ 1` destroys this | adversarial |

`cliff` is the σ-invariant under scaling — the role `zero_count`
and `value_multiset` played in kernel_zero. The other three
non-control channels are forced to fail by the same scaling that
preserves the cliff. The contrast is the substantive content of
the marvel.

`qe_closed_form` is computed independently of `q_general`: it
evaluates the wonders-doc closed form `(1 - (1 - x)^e)/e` directly.
Under identity, agreement between `no_op` (which compares to
`q_general`) and `qe_closed_form` is the cross-occurrence anchor —
the master expansion and the closed form must agree, witnessing
ROW-OGF.md's qe-closed-form theorem at the substrate.

## Recovery

All five channels use exact criteria — closed-form predictions from
`algebra/`. Tolerance `TOL = 1e-12`, the same TOL kernel_zero
committed to as machine tolerance.

For each channel, given a column `col` and target descriptor
`(p, q, e, H_max)`:

- **`no_op`.** Verdict PRESENT iff
  `|col[h - 1] - float(q_general(p, h, q^e))| < TOL` for every
  `h ∈ [1, H_max]`. Strength = fraction of cells matching.

- **`cliff`.** Let `Cliff = [e, e + 1, …, H_max - 1]` (0-indexed
  positions covering `h ∈ [e + 1, H_max]`). Verdict PRESENT iff
  `|col[i]| < TOL` for every `i ∈ Cliff`. Strength =
  `|{i ∈ Cliff : |col[i]| < TOL}| / |Cliff|`.

- **`leading_multinomial`.** Let `lm = (-1)^(e - 1) / e` (the
  expected leading coefficient at `h = e`). Verdict PRESENT iff
  `|col[e - 1] - lm| < TOL`. Strength = `1` or `0`.

- **`qe_closed_form`.** Let `closed[h - 1] = (-1)^(h - 1) C(e, h) / e`
  for `h = 1..H_max` (zero for `h > e`). Verdict PRESENT iff
  `|col[h - 1] - closed[h - 1]| < TOL` for every `h`. Strength =
  fraction of cells matching the closed form.

- **`prime_row_identity_at_h1`.** Verdict PRESENT iff
  `|col[0] - 1| < TOL`. Strength `1` or `0`.

## Anchor

The probe must reproduce the following on the algebra-evaluated
column for every cell in the `qe` panel under the **identity
transducer**:

- `no_op`: PRESENT, strength 1.0.
- `cliff`: PRESENT, strength 1.0.
- `leading_multinomial`: PRESENT, strength 1.0.
- `qe_closed_form`: PRESENT, strength 1.0.
- `prime_row_identity_at_h1`: PRESENT, strength 1.0.

The anchor leans on:

- `algebra/tests/test_anchors.py` A10 — degree, leading coefficient,
  and `qe`-closed-form contracts (`A10a`, `A10b`, `A10c`, `A10d`),
- A7 — kernel-zero classifier, equivalent statement read along the
  `h`-axis at fixed `k'`,
- A1 — prime-row identity at `h = 1`,
- the cross-occurrence of the multinomial in `KERNEL-ZEROS.md` (ii)
  and `ROW-OGF.md` leading-coefficient claim, both forced by the
  same finite-difference identity.

If A1, A7, and A10 pass and the probe's substrate is computed by
`q_general` exact-rationally, the anchor here must pass at TOL=1e-12.

## Panel

`qe` panel only — single-prime cofactors, where the wonders-doc
closed form is sharpest. Cells `(p, q, e)` with:

    p ∈ {2, 3, 5, 7},
    q = 3 if p = 2 else 2,
    e ∈ {1, 2, 3, 4}.

Sixteen cells. `H_max = max(e) + 5 = 9` rows per cell, giving five
cliff-band cells per (p, q, e) for the `cliff` channel to discriminate.

A separate sibling probe (`row_ogf_cliff_multi`, not built here)
would handle multi-prime cofactors `ω(k') ≥ 2`, where the
`qe_closed_form` channel does not apply but `cliff` and
`leading_multinomial` still do (with the leading coefficient
formula generalised to `(-1)^(Ω - 1)(Ω - 1)!/∏ e_i!`).

## Calibrations

- **Identity** (transducer = identity, substrate = algebra column):
  see Anchor.

- **Known-recovery** (transducer = scaling `c = 2`, substrate =
  algebra column): predicted `cliff` PRESENT (`c · 0 = 0`,
  scale-invariant); `no_op` PARTIAL with strength
  `(H_max - e) / H_max` per cell (only the cliff cells still match,
  since non-cliff cells are off by factor `c`); `leading_multinomial`
  ABSENT (`c · ((-1)^(e-1)/e) ≠ (-1)^(e-1)/e` for `c ≠ 1`);
  `qe_closed_form` PARTIAL with the same strength as `no_op` (the
  closed form's zero cells in the cliff still match, non-zero cells
  are off by `c`); `prime_row_identity_at_h1` ABSENT (`col[0] = c`).

- **Null** (transducer = identity, substrate = synthetic row of
  i.i.d. uniform draws over `[-100, 100]` at fixed seed `0`): all
  five channels predicted ABSENT.

## Figures

Each run writes three figures into `runs/<date>_<config>/figures/`,
mirroring the kernel_zero pipeline.

- **`verdict_matrix.png`** — 16 × 5 heatmap of channel strengths.
  Identity uniform yellow, null uniform purple, scaling shows the
  predicted partial+invariant+destroyed pattern.
- **`column_diff.png`** — log10 `|col_post - algebra(p, q^e, h)|`
  heatmap, 16 rows × `H_max` columns. Identity uniformly black
  (substrate matches algebra at exact zero); scaling shows
  perturbation at non-cliff positions.
- **`cliff_signature.png`** — the marvel observable. Per cell, a
  line plot of `col` versus `h`, with a vertical marker at the
  predicted cliff `h = e + 1`. Identity shows non-zero values
  left of the cliff and exact zero right of it; scaling shows the
  same shape with values doubled left of the cliff.

## Inheritance from kernel_zero

This probe shares `kernel_zero`'s shape and adapts it:

- Same numpy + matplotlib pipeline; same TOL = 1e-12 commitment;
  same harness layout (`probe.py`, `anchors.py`, `runs/`).
- Same five-component spec (Target / Transducer / Channels /
  Recovery / Anchor) plus calibration discipline.
- Same expected_verdicts table for identity / known-recovery / null.

What differs:

- Substrate axis: `h` instead of `k`.
- Substrate type: algebra column (not cached lattice) — so no
  lattice-vs-algebra contract; the substrate is exact by
  construction.
- Transducer family: scaling instead of permutation.
- Anchor surface: A1, A7, A10 instead of A2, A7, A8.
- The `qe_closed_form` channel checks an *independent* closed-form
  prediction, not `q_general`. This is the cross-occurrence test the
  marvel doc highlights.

When the second probe lands, the harness commonalities between
kernel_zero and row_ogf_cliff become factorable into
`probes/_harness.py` per `probes/README.md` § "Directory layout".
