# The K_pair lattice: closed-form first-collision points for the
# survivor construction

This memo formalizes what EXP07–08 found empirically: the smooth
survival surface `κ(K, n_0)` has its `K`-derivative concentrated on a
discrete, closed-form set — a "fan" of `W − 1` arithmetic-progression
diagonals — with the lattice points themselves given by an elementary
formula in `gcd(a, r)`.

The substantive content is the closed form (§2), the support claim
(§3), the fan decomposition (§4), and a step-function description of
the cumulative deficit `W·K − S(K)` (§5). The Cantor-staircase
analogy that earlier drafts gestured at does not survive scrutiny;
§5.3 calls the structure what it is — a step function with jumps on
a closed-form integer lattice — and stops there.

---

## 1. Setup

Fix `W ≥ 2` and a window `[n_0, n_0 + W − 1]` of `W` consecutive
integers.

The **n-prime stream** of `n` is the increasing sequence
> `S_n = (n·m : m ≥ 1, n ∤ m)`.

The **K-bundle** is the multiset `B_W(K, n_0) = ⋃_n (S_n[1..K])` over
`n` in the window — a collection of `W·K` atoms with multiplicity.

The **survivor set** is `Surv(K, n_0) = {A ∈ B : mult(A; K) = 1}`,
where `mult(A; K) = #{n ∈ window : A ∈ S_n[1..K]}`. Define

> `S(K, n_0) := |Surv(K, n_0)|`,
> `κ(K, n_0) := S / (W·K)`,
> `Δ(K, n_0) := W·K − S = Σ_A mult(A; K) · 1[mult ≥ 2]`     (cumulative deficit).

The deficit identity in the third line is bookkeeping: `W·K =
Σ_A mult(A; K)`, and `S = #{A : mult = 1}`. Subtracting gives the
sum over multi-shared atoms of their multiplicities.

---

## 2. Closed-form K_pair (window regime)

**Definition.** For `a, b` in the window with `a < b`, `K_pair(a, b)`
is the smallest `K` such that `S_a ∩ S_b ≠ ∅` and the smallest atom
of `S_a ∩ S_b` lies in `S_a[1..K]` and `S_b[1..K]`. (When `S_a ∩ S_b
= ∅`, `K_pair` is undefined; this happens iff `a² | b`.)

**Theorem 1 (window regime).** Assume `n_0 ≥ W` so every window pair
satisfies `b < 2a` strictly (the case `b = 2a` is excluded; at
`n_0 = W − 1` the pair `(W − 1, 2(W − 1))` would lie on the boundary
and the proof's strict inequality fails). Let `g = gcd(a, b) =
gcd(a, b − a)` and `L = lcm(a, b) = a·b/g`. Then `S_a ∩ S_b` is
nonempty, its smallest element is `L`, and

> **`K_pair(a, b) = b − 1`**     if `g = 1`,
> **`K_pair(a, b) = b / g`**     if `g ≥ 2`.

Equivalently, with `r = b − a`,

> **`K_pair(a, a + r) = a + r − 1`**         if `gcd(a, r) = 1`,
> **`K_pair(a, a + r) = (a + r) / gcd(a, r)`** if `gcd(a, r) ≥ 2`,
>
> for `r ∈ {1, …, W − 1}`.

*Proof.* Write `L = a · (b/g)`. To show `L ∈ S_a` we need `a ∤ (b/g)`.
Since `gcd(a, b) = g`, write `a = g·α`, `b = g·β` with `gcd(α, β) =
1`. Then `b/g = β`, and `a | β` would mean `g·α | β`, hence `α | β`;
combined with `gcd(α, β) = 1` this forces `α = 1`, i.e., `a = g`,
i.e., `a | b`. In the window regime `b < 2a`, this would force `b = a`
(impossible since `a < b`). So `a ∤ (b/g)` and `L ∈ S_a`.

By the same argument with `(a, b)` swapped, `L ∈ S_b`. Any common
multiple of `a` and `b` is a multiple of `L`, so `L` is the smallest
shared atom.

Position of `L` in `S_a`: count `m ∈ {1, …, L/a}` with `a ∤ m`. We
have `L/a = b/g`, and the number of multiples of `a` in `{1, …, b/g}`
is `⌊b/(g·a)⌋`. The two cases:

- `g = 1`: `b/(g·a) = b/a`, and `1 ≤ b/a < 2` (since `a < b < 2a`),
  so `⌊b/a⌋ = 1`. Position `= b − 1`.
- `g ≥ 2`: `b/(g·a) ≤ b/(2a) < 1`, so `⌊b/(g·a)⌋ = 0`. Position
  `= b/g`.

Position of `L` in `S_b`: by symmetry, count `m ∈ {1, …, a/g}` with
`b ∤ m`. Since `a/g ≤ a < b`, the floor term `⌊a/(g·b)⌋ = 0` always.
Position `= a/g`.

`K_pair = max(pos_a, pos_b)`. Since `b > a`, `pos_a ≥ pos_b` in both
cases (for `g = 1`: `b − 1 ≥ a = a/g`, with equality iff `r = 1`;
for `g ≥ 2`: `b/g > a/g`). So `K_pair = pos_a`, giving the two-case
formula above. ∎

**Stated identity (general form, with caveat).** For arbitrary
`a < b` with `a² ∤ b`, the same expression yields the right answer
but the floor terms can be nonzero:

> `K_pair(a, b) = max( b/g − ⌊b/(g·a)⌋ , a/g − ⌊a/(g·b)⌋ )`,    `g = gcd(a, b)`.

The script's `k_pair_formula` uses this form. When `a² | b`, the
streams are disjoint and `K_pair` is undefined; the formula then
returns a meaningless finite integer (e.g., for `a = 2, b = 8`,
the formula returns `2`, not `b/g = 4`, but no actual collision
occurs). The window regime excludes this case.

**Verification.** `exp08_lattice_closed_form.py:step1` builds `S_a`
and `S_b` as integer sequences (independently of the formula), finds
the smallest shared atom, and computes its position by counting.
275/275 sample pairs across `n_0 ∈ {10, 30, 50, 100, 290}` and
`W ∈ {5, 10}` agree with `k_pair_formula`. (Source:
`exp08_lattice_check.txt:4`.)

---

## 3. The lattice Λ_W and its support

**Definition.** Define the **K_pair lattice** as the multiset
> `Λ_W(K, n_0) := #{ (a, b) : a < b in window, K_pair(a, b) = K }`.

Each window contributes `C(W, 2)` pair-points; their `K_pair` values
collide on diagonals (§4).

**Theorem 2 (support).** Let `COLL(K, n_0) := W − [S(K) − S(K − 1)]`
be the collision-event count at K-step `K`. Then

> **`supp(Λ_W) ⊆ supp(COLL)`**.

*Proof.* Fix a pair `(a, b)` with `K_pair = K_*`. By definition
both `S_a[1..K_*]` and `S_b[1..K_*]` contain `L = lcm(a, b)`, with
`K_*` minimal. So at least two of the W stream-arrivals during
K-steps `1..K_*` emit `L` (one each from streams `a` and `b`),
and at least one of those two emissions occurs *at* K-step `K_*`.

Two sub-cases (both yield `COLL(K_*) ≥ 1`):

- *Both* emissions of `L` from the pair happen at `K_*`
  (`pos_a(L) = pos_b(L) = K_*`; this is the `r = 1` coprime case,
  where both equal `a`). Within the K_*-batch, `mult(L)` goes
  `0 → 1 → 2`: one arrival is a fresh singleton (`+1` to the
  singleton delta), one is a singleton-kill (`−1`). Net pair
  contribution to `S(K_*) − S(K_* − 1)` is `0` rather than the
  fresh-singleton `+2` it would have been; so `dS ≤ W − 2` and
  `COLL ≥ 2`.
- One emission is at `K_*` and the earlier one was at some
  `K_1 < K_*`. Then `mult(L)` was already `≥ 1` before the
  K_*-batch. The K_*-arrival raises `mult(L)` by `1`,
  contributing `−1` (if `1 → 2`) or `0` (if `≥ 2 → ≥ 3`) to the
  singleton delta. So `dS ≤ W − 1`, `COLL ≥ 1`.

In either sub-case `COLL(K_*) ≥ 1`, so `COLL(K_*) > 0` whenever
`Λ_W(K_*) > 0`. ∎

**Multi-share complication.** The proof uses only the weak claim
`COLL(K_*) ≥ 1`, which is enough for support. The strong claim
`COLL(K_*) ≥ 2` (a `+2` contribution from a `1 → 2` transition)
fails when `mult(L)` was already `≥ 2` before `K_*` — i.e., when `L`
is shared by `k ≥ 3` window-streams and *two* of those streams have
positions for `L` strictly less than `K_*`, leaving the K_*-arrival
to be the third (or later). In that case the K_*-arrival raises
`mult` from `≥ 2` to `≥ 3`, contributing `0` (not `−1`) to the
singleton delta and `+1` (not `+2`) to `COLL`. The single short-cell
at `n_0 = 20, K = 8` is exactly this regime: streams 28 (`pos = 6`)
and 24 (`pos = 7`) have already pushed atom `168` to `mult = 2`
before stream 21 arrives at `pos = 8 = K_*`.

**Empirical confirmation.** Across the full grid (`n_0 ∈ {10, 20, …,
1000}` × `K ∈ {1, …, 1000}`):

| metric | value |
|---|---|
| `|supp(Λ_W)|` | 1919 |
| `|supp(COLL)|` | 11760 |
| `|supp(Λ_W) ∩ supp(COLL)|` | 1919 (= 100% of Λ-support) |
| in `Λ_W` but not `COLL` | 0 |
| in `COLL` but not `Λ_W` | 9841 (subsequent-multiple events) |

Source: `exp08_lattice_check.txt:8-12`.

**Multiplicity.** `2·Λ_W` is the **naive pairwise prediction**:
each pair contributes `+2` if its `K_pair`-arrival turns a singleton
(`mult 1 → 2`) into a duplicate, with the no-collision baseline
`dS = +W`. The prediction holds with equality when no other event
fires at the same K-step. Two failure modes:

- `2·Λ_W < COLL` when a later multiple `t·L` for some other pair
  (`t ≥ 2`) lands at the same K-step, adding events to `COLL`
  outside `Λ_W`'s support.
- `2·Λ_W > COLL` when `L` is shared by `k ≥ 3` window-streams and
  the K_pair-arrival raises `mult` from `≥ 2` to `≥ 3`, contributing
  only `+1` (not `+2`) to `COLL`.

Both are real on the empirical grid; the second is rare.

| metric | value |
|---|---|
| `2·Λ_W = COLL` | 89.25% of grid cells |
| `2·Λ_W < COLL` (later multiples) | 10.74% |
| `2·Λ_W > COLL` (3+-share over-count) | 1 cell, at `n_0 = 20, K = 8` |

The single short cell is `168 = 21·8 = 24·7 = 28·6` in window
`[20, 29]`: pair `(21, 24)` has `K_pair = 8`, but at `K = 8` atom
168 already had `mult = 2` (from streams 28 at `K = 6` and 24 at
`K = 7`), so stream 21's arrival contributes `+1` not `+2`.

Source: `exp08_lattice_check.txt:16-21`.

---

## 4. Fan decomposition

The window-regime formula from §2 splits the lattice into `W − 1`
diagonal families indexed by `r ∈ {1, …, W − 1}`. Within family `r`,
contributions further split by `g = gcd(a, r)` (which can be any
divisor of `r`):

- pairs with `gcd(a, r) = 1` lie on the line `K = a + r − 1`, a ray
  of slope `1` shifted by `r − 1` from the line `K = a` (so the
  `r = 1` coprime sub-family sits on `K = a`, not `K = a + 1`);
- pairs with `gcd(a, r) = g ≥ 2` lie on the line `K = (a + r) / g`,
  a ray of slope `1/g` in `(n_0, K)`-space.

So the K_pair lattice is a **fan** of diagonal rays: a slope-`1`
family (from coprime `(a, r)`) at offsets `r − 1`, plus slope-`1/d`
rays for each `d ∈ {2, …, W − 1}` accumulating contributions from
every `r` divisible by `d`.

The visually loud diagonals in the EXP07 `∂κ/∂K` heatmap are exactly
these rays. The slope-1 family is not a single ray: it is a **band**
of width `W − 1` cells, with sub-rays at `K = a + r − 1` for each
`r ∈ {1, …, W − 1}` with `gcd(a, r) = 1`. The leading edge of this
band is `K = a` (the `r = 1` sub-ray); the trailing edge is `K = a +
W − 2`. Multiplicity grows from `1` at the leading edge to up to
`W − 1` at the trailing edge (peaking when every `r ∈ {1, …, W − 1}`
yields `gcd = 1` with `a = K − r + 1`).

EXP07 drew a guide at `K = n_0 + 1`; that line sits **inside** the
slope-1 band (one cell in from the leading edge, on the `r = 2`,
`g = 1` sub-ray when `n_0` is odd). It is a reasonable guide for
"around here is the slope-1 family", but it is neither the band's
leading edge nor the only sub-ray. EXP10 (`exp10_full_resolution_lattice.py`)
renders the band at unit resolution and shows this structure
explicitly; see `EXP10-FINDINGS.md`.

The slope-`1/d` rays for `d ≥ 2` sit at `K = (a + r) / d` with
`d | gcd(a, r)`, accumulating contributions from every `r` divisible
by `d`. They appear at `K ≈ n_0 / d` in the heatmap.

---

## 5. Step-function structure of S(K) at fixed n_0

This section describes how `S(K)` (or equivalently `Δ(K) = W·K − S`)
behaves as `K` grows at fixed `n_0`. Most claims here are direct
unpackings of the K-walk definition; the substantive content is the
closed-form description of when events happen.

### 5.1. Three nested closed-form predictions

Each prediction estimates `Δ(K)` from the same closed-form
ingredients. They are not separate theorems; they are
progressively-tighter approximations: (a) is a pairwise first-event
heuristic that can over- or under-count, (b) is exact except in
3+-share cells, and (c) is the definition of `Δ` and exact by
construction.

**(a) First-events pairwise overcount** (just `2·Λ_W`):

> `F(K) := 2 · |{ (a, b) : a < b in window, K_pair(a, b) ≤ K }|`.

This is **not** a lower bound on `Δ`. In the no-3+-share case each
pair contributes `+2` at its `K_pair` and `F(K) = Δ(K)` exactly
(over the first-events epoch); but in 3+-share cells the pairwise
sum overcounts, since the shared atom contributes only `mult` to
`Δ` while the count `2 · #{pairs at this atom}` is `2·C(k, 2) =
k(k−1) > k` for `k ≥ 3`. Concrete witness: at `n_0 = 20, K = 8`
(triple-share at atom `168`), `F(8) = 12` but `Δ(8) = 11`. So `F`
is best read as a pairwise first-event heuristic, equal to `Δ` on
the no-3+-share majority and overcounting elsewhere; it also
undercounts at large `K` because it omits all `t ≥ 2` contributions.

**(b) Pairwise (pair, t) prediction.** For pair `(a, b)`, the t-th
shared atom is `t·L`. Its position in `S_a` is

> `pos_a(t) = ⌊t·L / a⌋ − ⌊t·L / a²⌋ = (t·b/g) − ⌊t·b / (g·a)⌋`,

and analogously `pos_b(t)`. Set `K_event(a, b, t) = max(pos_a(t),
pos_b(t))`. Then:

> `Δ_pairwise(K) := 2 · |{ (a, b, t) : K_event(a, b, t) ≤ K }|`.

This is exact unless an atom is shared by 3+ window-streams (each
3-share contributes `k(k − 2)` of phantom events, all at the third+
arrivals; see §3 multi-share complication).

**(c) Atom-centric prediction.** Sort all (stream, K-position) pairs
by `K`. As you encounter atom `A` for the `i`-th time at K-step
`K_i`, contribute `0` (`i = 1`), `+2` (`i = 2`), or `+1` (`i ≥ 3`)
to `Δ`. This is `Δ(K)` by construction (it is the K-walk that
defines `S`); it is exact to machine precision but is not a
*prediction* in any nontrivial sense — it is the definition.

**Empirical residuals at `n_0 = 100, W = 10, K = 600`** (from
`exp09_staircase.py`):

| prediction | max `|Δ_pred − Δ|` over `K ∈ [1, 600]` | median |
|---|---|---|
| (a) first-events | 0.115 (in 1−κ units) | 0.088 |
| (b) pairwise | 0.0044 | 0.0015 |
| (c) atom-centric | < 10⁻¹⁰ (definitional) | < 10⁻¹⁰ |

The pairwise residual is nonzero only at K-steps where a 3+-shared
atom has its third+ arrival. For W=10 windows in this `n_0` range,
that's 9 cells out of 600.

### 5.2. Where the steps live

`Δ(K)` is non-decreasing in `K`. From (b)/(c) above, `Δ` is constant
between K-steps where any atom transitions from singleton to
non-singleton (or between non-singleton multiplicity values), and
jumps at exactly those K-steps. The set of jump K-steps is:

> `Jump(n_0) = ⋃_{a, b ∈ window, a ≠ b}` `{ K_event(a, b, t) : t ≥ 1 }`.

Each `K_event(a, b, t) = max(t·b/g − ⌊t·b/(g·a)⌋, t·a/g − ⌊t·a/(g·b)⌋)`
is closed-form. **Within a single pair `(a, b)`**, the sequence
`(K_event(a, b, t))_{t ≥ 1}` is *not* a single arithmetic progression
in `t`: the floor `⌊t·b/(g·a)⌋` introduces periodic +1 corrections,
giving consecutive increments that alternate between `b/g` and
`b/g − 1` according to the residue `t·b mod g·a`.

*Concrete example.* For pair `(a, b) = (100, 101)` (`g = 1`, `b/g =
101`, `b/(g·a) = 101/100`), the increment pattern is `100, 100, …,
100, 99, 100, 100, …` — every `a/(b − a) = 100` steps the floor
`⌊t·b/a⌋` jumps by 2 instead of 1, dropping the increment by 1. The
sequence is a finite union of arithmetic progressions (one per
residue class of `t` modulo `g·a`), or equivalently a closed-form
floor sequence — but not a single AP.

### 5.3. What this is, and what it is not

It is: a step function `Δ(K)` whose jumps live on a closed-form
integer set, the K_pair lattice and its multi-`t` extensions. The
exception set has positive asymptotic density (`≈ Σ_{(a,b)} g/b`
events per unit `K`), not measure zero.

It is *not* a Cantor function or a devil's staircase. The classical
analogy fails on the measure-theoretic side: Cantor's staircase has
all variation on a measure-zero fractal, and `dκ/dK = 0` Lebesgue-
a.e. Our staircase has variation on a positive-density structured
integer set; "smoothness" of `κ` in the EXP05 heatmap is the
W·K-denominator integrating positive-density jump points in each
heatmap cell, not singular continuity in any rigorous sense.

What is real and worth keeping: the smooth-looking `κ` heatmap
(EXP05) and the spike-supported `∂κ/∂K` heatmap (EXP07) are images
of the same underlying object at different resolutions. The
underlying object is given closed-form by Theorem 1 + the
fan-decomposition (§4). That the closed form is elementary
(gcds, floors, divisor sums) is the finding.

### 5.4. Visual proof

`exp09_staircase.png` shows the structure at fixed `n_0 = 100,
W = 10`:

- **Top:** `S(K)` (orange) tracks `W·K` (gray) with macroscopic
  slope ≈ `W`. Lattice K-steps (red verticals) cluster around
  `K ∈ [100, 108]` (the `r = 1` family at this `n_0`: pairs
  `(100, 101), …, (108, 109)`, each coprime with `K_pair = a`) and
  at multiples thereof.
- **Middle:** `1 − κ(K)` empirical (blue, thick) is overlaid by
  the atom-centric reconstruction (green, residual `< 10⁻¹⁰` —
  definitional). The pairwise `(pair, t)` prediction (yellow
  dashes) tracks closely; the first-events pairwise count (pink
  dotted), which counts only `t = 1` events, tracks early but
  flatlines (no `t ≥ 2` contributions) and ends at ≈ 10% of
  empirical at `K = 600` — undercount on the high side, since at
  this `n_0` no 3+-shares overcount it the other way.
- **Bottom:** zoom on `K ∈ [90, 220]` showing the staircase
  explicitly: between red verticals, `S(K)` increases with slope
  `W` (every new atom is a fresh singleton). At a red vertical the
  slope is suppressed: each `1 → 2` arrival at this K-step subtracts
  `1` from `dS` (a singleton-kill on top of the `+1` fresh
  contribution from that stream), and each `≥ 2 → ≥ 3` arrival
  subtracts `1` (the fresh contribution that didn't happen). So
  `S(K_*) − S(K_* − 1) = W − 2·#{1→2 arrivals} − #{≥2→≥3 arrivals}`,
  which is usually positive and can dip to `0` or below in dense
  collision K-steps. The visible staircase is `Δ` jumping upward;
  `S` follows the complementary slope-suppressed trajectory.

---

## 6. Naming

Call the structure the **`K_pair` lattice of the window** (or
**collision lattice** when contrasting with the smooth survival
surface). Its support is the discrete subset of `(K, n_0)`-space at
which `Δ(K)` jumps, given closed-form (window regime, `g = gcd(a, r)`)
by

> `K_pair(a, a + r) = a + r − 1`        if `g = 1`,
> `K_pair(a, a + r) = (a + r) / g`      if `g ≥ 2`,

with extensions at `t·L` multiples for `t ≥ 2` controlled by the
same `gcd(a, r)` data through the position formula in §5.1(b).

---

## 7. Pseudo-code

```
K_pair(a, b)                   // window regime
  g := gcd(a, b - a)
  := (b - 1)      if g == 1
  := (a + (b-a)) / g    if g >= 2
  // unified form, also valid for general (a, b) with a² ∤ b:
  // K_pair = max(b/g - floor(b/(g*a)), a/g - floor(a/(g*b)))

K_event(a, b, t)               // t-th shared-atom position
  L  := a * b / gcd(a, b)
  := max( floor(t*L/a) − floor(t*L/a²), floor(t*L/b) − floor(t*L/b²) )

Δ_pairwise(K, n_0, W)
  := 2 * |{ (a, b, t) : a < b in window, t ≥ 1, K_event ≤ K }|

Δ_atom_centric(K, n_0, W)      // exact by construction
  counts := {}
  Δ := 0
  for each (a, position) in window×[1..K] sorted by K_arrival:
    atom := a-th stream's position-th element
    let c = counts[atom] before increment; counts[atom] += 1
    Δ += 0 if c==0, +2 if c==1, +1 if c≥2
  return Δ
```

---

## 8. Files

- `exp07_kappa_derivative.py` — empirical lattice via incremental
  K-walk (heatmap; this is where the visible spike-support
  pattern comes from).
- `exp08_lattice_closed_form.py` — closed-form `K_pair` derivation,
  sequence-builder verification (Step 1), and grid-wide support /
  multiplicity comparison (Step 2). Source for the numbers in §3.
- `exp08_lattice_check.txt` — full numerical receipts from the
  above.
- `exp08_lattice_closed_form.png` — three-panel side-by-side of
  `Λ_W`, `2·Λ_W`, and empirical `COLL`.
- `exp09_staircase.py` / `exp09_staircase.png` — `S(K)` staircase,
  three-prediction overlay, and zoom (proof figure for §5.4).
