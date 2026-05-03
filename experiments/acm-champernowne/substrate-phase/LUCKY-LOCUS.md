# Lucky locus: a Generalised Family E theorem

The substrate paper (PAPER.md §5.1) proves four exactness regimes
on the digit-class block `B_{b,d} = [b^(d-1), b^d − 1]`:

- **Clause 1** (integer block-uniformity): trivial fact about ℤ.
- **Clause 2** (smooth-sieved): exact when `n² | b^(d-1)`.
- **Clause 3** (Family E): n-prime atoms are `{n, 2n, …, (b−1)n}`
  for `n ∈ [b^(d-1), ⌊(b^d−1)/(b−1)⌋]`.
- **Clause 4** (universal spread bound): per-leading-digit counts
  differ by at most 2.

The phase diagram (`phase_diagram.png`) revealed 96 *lucky* cells
where spread = 0 *outside* clauses 2 and 3 — cells where the
universal bound is not tight, but neither smoothness nor Family E
applies. WORKSET.md flags this as "lucky-cancellation locus
uncharacterised."

This note characterises the locus by a closed form.

## Setup

Let `W = b^(d-1)` and `n ≥ 2`. For each leading-digit strip
`S_k = [k·W, (k+1)·W − 1]` (k = 1, …, b−1), define:

```
M_k(n) = #{multiples of n in S_k}
A_k(n) = #{n-prime atoms in S_k}
       = M_k(n) − #{multiples of n² in S_k}
```

The cell `(b, n, d)` is **lucky** iff `A_k(n) = q` for all k
(constant atom count per leading digit) and the cell is not in
the smooth or Family E regime.

## Theorem (Generalised Family E)

Let `m_min := ⌈W/n⌉` and `m_max := ⌊(bW − 1)/n⌋` denote the
smallest and largest multipliers k for which `kn ∈ B_{b,d}`. Let
`qp := M_k(n)` (assumed constant in k; this is the multipliers-
per-strip count, distinct from the atoms-per-strip q).

**Statement.** Suppose `(m_min, qp)` satisfy:

```
m_max = m_min + qp · (b − 1) − 1
```

(equivalently: total multiples in block divides evenly into b−1
strips). Then `M_k(n) = qp` for all k = 1, …, b−1 — the
*multiples* of n distribute uniformly across leading digits — for
all integers n in the range

```
n ∈ ( (bW − 1)/(m_max + 1),  (bW − 1)/m_max ]
   ∩  [ ⌈W/m_min⌉,  ⌊W·b/(m_max + 1)⌋ ]
```

restricted to the integer points satisfying the per-strip leading-
digit alignment

```
for k ∈ {m_min, …, m_max}: leading_digit(kn)
                           = ⌈(k − m_min + 1)/qp⌉.
```

**Atom-uniformity.** The cell is lucky (atoms uniform with count
`q = qp − δ`) iff additionally the multiples of n² also distribute
uniformly across strips, with `δ` multiples per strip. Two clean
sub-cases:

- **(a) No n² in block** (`n² > bW − 1`): δ = 0, q = qp.
- **(b) Uniform n² in block**: `#{multiples of n² in B_{b,d}}` is
  divisible by `b − 1` *and* the multiples of n² happen to land
  one-per-strip (or `δ`-per-strip uniformly).

When neither (a) nor (b) holds but `M_k(n)` varies with k *and*
the n²-corrections happen to balance, the cell is in a separate
**n²-cancellation** mechanism (see §"n²-cancellation" below).

## Verification

`analyze_lucky.py` enumerates lucky cells at b = 10, n ∈ [2, 200],
d ∈ [1, 7], classifies each by mechanism, and tests the theorem's
predicted n-range against the observed.

**69 of the 96 lucky cells** are in the Generalised Family E
regime. Distribution by (d, qp, m_min):

```
  d   qp  m_min  m_max       predicted        observed     q   δ  count
  3    1      2     10          [91,99]         [91,99]    1   0      9
  3    2      2     19          [50,52]         [50,52]    2   0      3
  3    2      3     20          [48,49]         [48,49]    2   0      2
  3    3      3     29          [34,34]         [34,34]    3   0      1
  3    3      4     30          [33,33]         [33,33]    3   0      1
  4    5      5     49        [200,204]       [200,200]    5   0      1
  4    5      6     50        [197,199]       [197,199]    5   0      3
  4    6      6     59        [167,169]       [167,169]    6   0      3
  4    6      7     60        [164,166]       [164,166]    6   0      3
  4    7      7     69        [143,144]       [143,144]    7   0      2
  4    7      8     70        [141,142]       [141,142]    7   0      2
  4    8      8     79        [125,126]       [125,126]    8   0      2
  4    8      9     80        [124,124]       [124,124]    8   0      1
  4    9      9     89        [112,112]       [112,112]    9   0      1
  4    9     10     90        [110,111]       [110,111]    9   0      2
  4   10     10     99        [100,101]       [100,101]   10   0      2
  4   77     77    769          [13,13]         [13,13]   71   6      1
  5   97     98    970        [103,103]       [103,103]   96   1      1
  ...
  7  18868  18868 188679        [53,53]         [53,53] 18512 356      1
```

(Full table in `analyze_lucky.py` output. d=4 qp=5 m_min=5
"missing" 201–204 is just the sweep boundary at n = 200.)

**All 46 (d, qp, m_min) groups match prediction exactly.** The
Generalised Family E theorem closes the locus for the 69 cells
under its mechanism.

The n=13 d=4 cell (qp=77, m_min=77) is illustrative of the
δ ≠ 0 case: 77 multiples of n=13 per strip, *plus* 6 multiples
of n²=169 in each strip (54 multiples of 169 in [1000, 9999]
distribute as 6 per strip). Atom count = 77 − 6 = 71 per strip.
The cell is lucky because *both* multiples of n and multiples of
n² are uniform.

## n²-cancellation

The remaining 27 lucky cells fall outside the Generalised Family
E regime — `M_k(n)` is *not* constant — but they share a single
structural condition, **Beatty pattern-alignment**, verified
exhaustively in the swept range.

### Structural condition

For a cell `(b, n, d)` to fall in the n²-cancellation locus:

1. `M_k(n) ∈ {⌊W/n⌋, ⌊W/n⌋ + 1}` for all `k` — the per-strip
   multiples-of-n count is spread-1 (Beatty-shape).
2. `M_k(n²) ∈ {c, c+1}` for all `k`, where `c = ⌊(W − 1)/n²⌋ + 1`
   or similar — spread ≤ 1.
3. The strips with the "extra" multiple of `n` are *exactly* the
   strips with the "extra" multiple of `n²`. Formally:
   ```
   M_k(n) − min_j M_j(n)  =  M_k(n²) − min_j M_j(n²)   for all k.
   ```

Condition 3 is **strictly stronger** than the definitional
requirement that `A_k(n) = M_k(n) − M_k(n²)` is constant. Constant
atom count requires only that the *differences* `M_k(n) − M_k(n²)`
are equal across `k`; pattern-equality of the extras is the
sharper condition that the variations themselves coincide
bit-for-bit.

### Verification

`analyze_lucky.py` checks conditions 1–3 on every n²-cancellation
cell in the b = 10, n ∈ [2, 200], d ∈ [1, 7] sweep:

```
   n   d  cn_extras  cnsq_extras  spread(cn)  spread(cnsq)  match?
  19   3  001000100  001000100             1             1  YES
  26   4  010101010  010101010             1             1  YES
  36   4  111011101  111011101             1             1  YES
  39   4  101101101  101101101             1             1  YES
  ...
 198   7  101010101  101010101             1             1  YES

Cells satisfying Beatty pattern-alignment: 27/27
```

The patterns themselves are diverse — `010101010` (period-2),
`001000100` (period-3-like), `111011101` (period-4), `000000001`
(near-uniform with a single late extra) — so this is not an
artifact of one degenerate alignment shape. It is a genuine
arithmetic phenomenon with multiple realisations, all sharing
condition 3.

### What is open

The closed form for **which** integer triples `(b, n, d)` trigger
the alignment is open. Conditions 1 and 2 reduce to bounds on
`(W mod n)` and `(W mod n²)` respectively. Condition 3 is the
delicate one: it is the alignment of two Beatty sequences with
different generating ratios (`W/n` and `W/n²`). The 27 swept
cells suggest the trigger set is sparse — it does not form a
dense parameterised family on the `(b, n, d)` lattice — but a
characterisation of the trigger set itself is left open.

This is harder than the Generalised Family E case (which closes
to an explicit `(qp, m_min)` parameterisation) and likely
requires Diophantine-approximation arguments on `W/n` versus
`W/n²`. The 27 cells in the sweep are sparse but structured: the
mechanism is identified, only the parameterisation is open.

## What this delivers

A **Generalised Family E** characterisation of 69 of the 96
lucky cells in the sweep:

```
The substrate's "exact uniformity" (spread = 0) extends beyond the
paper's clauses 2 and 3 to the (qp, m_min) family above. The
extension is base-aware: the closed-form n-range depends on b, d,
and the integer q'-per-strip parameter, not only on whether
n² | W.
```

The remaining 27 cells (n²-cancellation) are evidence of a
*second*, more delicate mechanism that is not captured by the
Generalised Family E framework and is left as an open
characterisation.

## Out of scope for the paper

Both the Generalised Family E theorem and the n²-cancellation
locus are explicitly out of scope for the JStatSoft submission.
The paper's clause 4 ("spread ≤ 2 universally") is the right
statement at the engineering level; characterising equality and
zero cases would expand the substrate theorem and bloat the scope.
The findings here belong in a follow-up paper on substrate-
exactness loci, or in the experimental wing of this repository as
they currently are.

## Files

- `phase_diagram.py` / `phase_diagram.png` — original visual.
- `analyze_lucky.py` — classification and theorem verification.
- This file — the writeup.
