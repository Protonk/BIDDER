# Proposed closed forms in and about the Q-algebra

This memo lists closed-form expressions in the same spirit as the
existing `MASTER-EXPANSION.md`, `RANK-LEMMA.md`, `KERNEL-ZEROS.md`,
`ROW-OGF.md`, and `WITHIN-ROW-PARITY.md`: claims that collapse a
formal sum to a finite signed expression by an integer-divisibility
constraint, or that factor an observable into a closed-form
algebraic part and a combinatorial residue.

Each proposal includes: the claim, a short verification sketch (the
math that would prove it), the workflow steps to anchor it
("stated, implemented, anchored, cross-checked, documented"), and
its relation to existing material.

The first three are the strongest — clean statements with numerical
verification already done. The remainder are more speculative and
need more thought.

---

## 1. Prime-row Q values are a polynomial generating function ✓ (landed)

**Status.** Stated, implemented, anchored, written up. See
`ROW-OGF.md`, `predict_q.row_polynomial`, and anchor A10 in
`test_anchors.py`. Proposal 2 below is folded into the same
write-up; Proposal 3 was already covered by `KERNEL-ZEROS.md` and
is now also visible as the trailing-zero / leading-coefficient
structure of the OGF.

**Claim.** For prime `p` and integer `k' ≥ 2` coprime to `p`, the
ordinary generating function

> `F(x; p, k') := Σ_{h ≥ 1} Q_p(p^h k') · x^h`

**is a polynomial in `x` of degree exactly `Ω(k')`** (the number of
prime factors of `k'` with multiplicity). The coefficients depend
only on the τ-signature of `k'`, not on the specific primes.

For `k' = 1` (the only non-polynomial case among coprime cofactors):

> `F(x; p, 1) = −log(1 − x)`,

with `[x^h] F = 1/h`, recovering the prime-row identity
`Q_p(p^h · 1) = 1/h`.

**Proof sketch.** From `MASTER-EXPANSION.md` C3 (prime-`n`
specialisation) for prime `n = p` and `k'` coprime to `p`:

> `Q_p(p^h k') = Σ_{j=1}^h (−1)^(j−1) C(h−1, j−1) τ_j(k') / j`.

Summing over `h ≥ 1` with weight `x^h` and swapping sums:

> `F(x; p, k') = Σ_{j ≥ 1} (−1)^(j−1) τ_j(k') / j · Σ_{h ≥ j} C(h−1, j−1) x^h`
>             ` = Σ_{j ≥ 1} (−1)^(j−1) τ_j(k') / j · (x / (1 − x))^j`.

For `k'` coprime to `p`, `τ_j(k')` is multiplicative on coprime
factors, and `τ_j(q^e) = C(j+e−1, e)` is a polynomial in `j` of
degree `e`. Hence `τ_j(k') / j` is a polynomial in `j` of degree
`Ω(k') − 1`. The alternating sum
`Σ_j (−1)^(j−1) p_d(j) y^j` with `p_d` polynomial of degree `d` is
a rational function of `y` with denominator `(1 + y)^{d+1}`.
Substituting `y = x/(1−x)` so that `1 + y = 1/(1−x)`, the
denominator `(1+y)^{Ω(k')}` exactly cancels the `y^j` powers'
introduced `1/(1−x)^j` factors, leaving a polynomial in `x` of
degree `Ω(k')`. ∎

**Numerical verification** (over `Fraction` via `predict_q.q_general`,
prime `p = 3`):

| `k'` | `Ω(k')` | `[Q_p(p^h k')]_{h=1..6}` | `F(x; p, k')` |
|---|---|---|---|
| `1`  | – | `[1, 1/2, 1/3, 1/4, 1/5, 1/6]` | `−log(1−x)` |
| `2`  | 1 | `[1, 0, 0, 0, 0, 0]`           | `x` |
| `4`  | 2 | `[1, −1/2, 0, 0, 0, 0]`        | `x − x²/2` |
| `8`  | 3 | `[1, −1, 1/3, 0, 0, 0]`        | `x − x² + x³/3` |
| `10` | 2 | `[1, −1, 0, 0, 0, 0]`          | `x − x²` |
| `20` | 3 | `[1, −2, 1, 0, 0, 0]`          | `x − 2x² + x³` |
| `70` | 3 | `[1, −3, 2, 0, 0, 0]`          | `x − 3x² + 2x³` |
| `100`| 4 | `[1, −7/2, 4, −3/2, 0, 0]`     | `x − 7x²/2 + 4x³ − 3x⁴/2` |

Every row truncates at exactly `h = Ω(k')`. The kernel-zero band
is the statement that `F` is polynomial.

**Workflow status.** Verified numerically; analytic proof above is
clean. Implemented as `predict_q.row_polynomial(p, k_prime)`
returning the rational coefficients, anchored against
`q_general(p, h, k_prime)` (anchor A10), and written up in
`ROW-OGF.md`.

**Why this matters.** It compactifies the entire prime-row Q
sequence into a single polynomial, makes the kernel-zero structure
of higher `h` mechanical (it is just "polynomial degree"), and
unifies the existing tables (each row of the prime / prime-power /
multi-prime tables is a coefficient of `F`).

---

## 2. Q-row sum: `Σ_h Q_p(p^h k')` is `1/e` or `0` ✓ (landed, folded into §1)

**Claim.** For prime `p` and `k' ≥ 2` coprime to `p`:

> **`Σ_{h ≥ 1} Q_p(p^h k')` = `1/e`** &nbsp;&nbsp; if `k' = q^e` for some prime `q ≠ p` (single prime, multiplicity `e ≥ 1`),
>
> **= `0`** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; if `ω(k') ≥ 2` (multiple distinct prime factors of `k'`).

(For `k' = 1` the sum is `Σ 1/h`, divergent.)

**Proof sketch.** This is `F(1; p, k')` evaluated from Proposal 1.
For `k' = q^e`:

> `F(x; p, q^e) = Σ_{h=1}^e Q_p(p^h q^e) x^h`,

and direct computation of `F(1; p, q^e)` from the master expansion
gives `1/e` (verified for `e = 1, 2, 3, 4` below).

For `k'` with `ω ≥ 2`: `F(x; p, k')` factors as
`x · (1 − x) · g(x)` for some polynomial `g`, hence `F(1) = 0`.
The factor `(1 − x)` arises because the alternating sum
`Σ (−1)^(j−1) τ_j(k')/j · y^j` has a zero at `y → ∞` of order
≥ 1 when `ω(k') ≥ 2`, equivalent to `(1+y)^Ω` in the denominator
killing the leading-degree terms after substitution.

(Cleaner combinatorial proof is likely available; the
generating-function argument above is mechanical.)

**Numerical verification.**

| `k'` | type | `Σ_h Q_p(p^h k')` |
|---|---|---|
| `2` | `q^1` | `1` (`= 1/1`) |
| `4` | `q^2` | `1/2` |
| `8` | `q^3` | `1/3` |
| `16` | `q^4` | `1/4` |
| `10`, `20`, `70`, `100` | `ω ≥ 2` | `0` |

(All checked via `predict_q.q_general` with `p = 3`. `k' = 1` is the
divergent edge case.)

**Workflow status.** Verified numerically; analytic proof folded
into `ROW-OGF.md` (statement (iv), row sum). Implemented as
`predict_q.row_sum`; anchored as part of A10.

**Why this matters.** It is the "strip-mixed Q" closed form: summing
`Q_p(p^h k')` over `h` (or equivalently over `t` at fixed `k'`)
collapses to a single rational. The result is sharp:
`ω(k') = 1` cases give a non-zero contribution; `ω(k') ≥ 2` cases
contribute zero. This dichotomy is the algebraic shadow of the
prime-vs-composite-cofactor distinction we already see at `h = 5`'s
kernel-zero band, but extended to all `h` simultaneously.

---

## 3. Kernel-zero band, geometric form ✓ (landed; same content as KERNEL-ZEROS.md (i), reorganised as polynomial truncation in §1)

**Claim.** For prime `p` and `k' ≥ 2` coprime to `p`:

> **`Q_p(p^h k') = 0` &nbsp; for all &nbsp; `h > Ω(k')`**.

**Proof.** Immediate from Proposal 1: `F(x; p, k')` has degree
`Ω(k')`, so its `[x^h]` coefficient is zero for `h > Ω(k')`. ∎

**Numerical verification.** All test cases in Proposal 1's table
satisfy this exactly; the kernel-zero rows are the trailing zeros.

**Workflow status.** Logically downstream of Proposal 1 but worth
stating standalone because it is the cleanest form of the
kernel-zero band: a single bound `h > Ω(k')` for every coprime
cofactor, equivalent to `KERNEL-ZEROS.md` (i) read at fixed `k'`
rather than fixed `h`.

**Why this matters.** The alternating-binomial identity
`Σ_j (−1)^(j−1) C(h−1, j−1) j^d = 0 for 0 ≤ d ≤ h−2` is the source
of the `h = 5` kernel-zero band; see the proof in
`KERNEL-ZEROS.md`. Proposal 3 makes the dual statement: at *fixed*
`k'`, every `h > Ω(k')` is a kernel zero — the band is
`{(h, k') : h > Ω(k')}`, a single inequality. The two identities
(sum over `j` at fixed `h` vs sum over `h` at fixed `k'`) are the
two readings of the rank-h truncation theorem, and together close
the prime case.

---

## 4. Prime-power row generating function (rewritten after audit)

**Audit history.** An earlier draft of this proposal claimed `F` for
`n = p^a` is rational with denominator a power of `(1 − x)`, then
contradicted itself in a later sentence with a `(1 − x^a)`
denominator, and forgot the `k' = 1` edge case. All three
audit-flagged failures are confirmed:
- `k' = 1` produces a transcendental (logarithmic) OGF, parallel to
  Proposal 1's `k' = 1` edge case (`F(x; p, 1) = −log(1 − x)`).
- The "denominator a power of `(1 − x)`" claim is wrong: concrete
  counterexamples have cyclotomic factors. E.g.,
  `F(x; 4, 0, 3) = (x − x³)/(1 − x³)`, which factors as
  `x(1 + x)/(1 + x + x²)` with `1 + x + x²` the third cyclotomic
  polynomial.
- The "denominator `(1 − x^a)`" claim is also wrong: at `a = 2`,
  the concrete `F` examples don't have `(1 − x²)` denominator
  either.

This proposal is now rewritten with separate handling of the
`k' = 1` and `k' ≥ 2` cases and concrete computed examples in place
of the earlier general conjecture.

### 4a. `k' = 1` (transcendental edge case)

**Object.** For prime `p`, `a ≥ 1`, `0 ≤ t < a`,

> `F(x; p^a, t, 1) := Σ_{h ≥ 1} Q_{p^a}(p^{ah + t}) · x^h`.

**Established case** (`a = 2, t = 0`, any prime `p`):

> `F(x; p², 0, 1) = (1/2) · log( (1 + x + x²) / (1 − x) )`.

**Proof.** Direct from `Q_{p²}(p^{2h}) = 1/h` if `h ≢ 0 (mod 3)`,
`= −1/(2h)` if `h ≡ 0 (mod 3)` (verified up to `h = 12` against
`q_general`). Reorganising:

> `F = −log(1 − x) − (3/2) Σ_{3|h} x^h/h`
> &nbsp;&nbsp;&nbsp;&nbsp;`= −log(1 − x) + (1/2) log(1 − x³)`
> &nbsp;&nbsp;&nbsp;&nbsp;`= −(1/2) log(1 − x) + (1/2) log(1 + x + x²)`.

The series is universal across primes `p` (the master expansion at
shape `(2,)` and `k_prime = 1` doesn't see the specific prime).

**General `(a, t)`.** Empirically (from `q_general`):
- `a = 3, t = 0` (i.e. `n = 8, 27, …`): the Q sequence does NOT
  have a clean `1/h` modulation; `Q_8(8^h)` for `h = 1..10` is
  `1, 1/2, −2/3, 7/12, 8/15, −4/3, 8/7, 23/24, −29/9, 44/15`. A
  closed form likely involves `log` of cyclotomic polynomials at
  step `a`, but has not been worked out.
- Other `(a, t)` cases: case-by-case; no uniform closed form.

**Status.** Specific `(a = 2, t = 0)` case closed. Other cases open;
the conjecture is that each `(a, t, k' = 1)` cell admits a closed
form of the type `Σ c_d log Φ_d(x) / (1 − x)` for cyclotomic
polynomials `Φ_d` and rational coefficients `c_d`, with the divisor
set and coefficients determined by `(a, t)`. Not proven.

### 4b. `k' ≥ 2` (rational, with cyclotomic denominators)

**Object.** Same `F(x; p^a, t, k')` for `k' ≥ 2` coprime to `p`.

**Empirical structure** (from `q_general`):
- `a = 2, t = 0, k' = 3` (Ω = 1, single prime cofactor):
  `Q_4(4^h · 3)` for `h = 1..` is `1, 0, −1, 1, 0, −1, 1, 0, −1, …`,
  period 3. **`F(x; 4, 0, 3) = (x − x³)/(1 − x³) = x(1 + x)/(1 + x + x²)`.**
  Same closed form holds for any single prime `q ≠ 2` substituted
  for `3` (verified `q ∈ {5, 7}`).
- `a = 2, t = 0, k' = 9 = 3²` (Ω = 2):
  `Q_4(4^h · 9)` for `h = 1..10` is
  `1, −1/2, −3/2, 3, −3/2, −5/2, 5, −5/2, −7/2, 7, …`. Pattern
  visible by groups of 3 but with growing magnitudes; no clean
  period or single-cyclotomic closed form found yet.
- `a = 2, t = 0, k' = 15 = 3·5` (Ω = ω = 2):
  `1, −1, −2, 5, −3, −4, 9, −5, −6, 13`. Linear growth in three
  arithmetic-progression sub-sequences; the OGF is rational but
  more complex.

**What the audit's counterexample shows.** Even for the simplest
non-trivial case (`Ω(k') = 1`), the OGF denominator is the
cyclotomic factor `1 + x + x²`, not `(1 − x)` or `(1 − x²)`. Higher
`Ω` introduces further cyclotomic factors. The general structure
is conjecturally:

> `F(x; p^a, t, k') = (numerator polynomial) / Φ_{?}(x)^{Ω(k')}`
> &nbsp;&nbsp;&nbsp;&nbsp;or a product of cyclotomic factors,

but the index of the cyclotomic and the way `Ω` controls its power
are NOT settled by the available examples.

**Status.** Open; the prime-row collapse to a polynomial does NOT
extend to `a ≥ 2`. The right closed form likely organises by
cyclotomic factors `Φ_d(x)` at indices related to `a` (e.g.,
`Φ_3(x) = 1 + x + x²` at `a = 2`), but a uniform statement requires
more worked examples and a general argument.

**What this means for the algebra programme.** The "prime-row
polynomial" structure (Proposal 1) is special to `a = 1`. At
`a ≥ 2`, the OGF is generally rational with cyclotomic denominators
(or transcendental at `k' = 1`). This is structurally different —
the rank-h truncation does not give bounded-degree polynomial
behaviour in `h`.

---

## 5. Squarefree multi-prime row generating function (notation fixed)

**Audit history.** Earlier draft used inconsistent variable lists
(`F(x_1, …, x_r; n, k')` in the head but `z^h` in the body, with `z`
not in the argument list) and a meaningless "exact-height condition"
phrasing (`(t_1, t_2) ≠ (t_1 ≥ 1, t_2 ≥ 1)`). Both fixed below.

**Object.** For squarefree `n = p_1 p_2 … p_r` (`r ≥ 2`) and `k'`
coprime to `n`, define the `(r + 1)`-variate generating function

> `F(z, x_1, …, x_r; n, k') := Σ_{h ≥ 1} Σ_{(t_1, …, t_r)} Q_n(n^h · p_1^{t_1} ⋯ p_r^{t_r} · k') · z^h · x_1^{t_1} ⋯ x_r^{t_r}`,

where the `t_i`-sum runs over all non-negative integer tuples
`(t_1, …, t_r) ∈ ℤ_{≥0}^r` excluding the case `t_i ≥ 1` for every
`i` simultaneously. (That case absorbs into a higher `h` row by the
exact-height condition: `n | ∏ p_i^{t_i}` iff every `t_i ≥ 1`,
which would shift `h → h + 1`.)

Equivalently: the `t_i`-support is `{(t_1, …, t_r) : ∃ i, t_i = 0}`.

**Conjectured form.** `F` is a rational function in
`(z, x_1, …, x_r)` whose denominator factors involve the prime-power
analogs of the prime-row `(1 + y)^Ω` collapse, but with a
multivariate `y_i = z · x_i / (1 − z · x_i)` substitution.

**Status.** Not worked out. The `r = 2, h = 3` slice in
`TABLES.md` §"Squarefree multi-prime n, r ≥ 2" would be a specific
evaluation of this OGF; the rest is open.

**Why it would matter.** The displayed tables in `TABLES.md`
organise by `(h, t_1, …, t_r, k')` row by row. A single rational
function would unify these slices and make the `h ≥ 5` and `r ≥ 3`
cases mechanical. Connection to Proposal 1: at `r = 1`, this should
reduce to the prime-row polynomial with the substitution
`z · x → x / (1 − x)`.

---

## 6. Class-pair density `D(c1, c2; n, L, K)` short-K asymptotic

**Claim (most ambitious).** The combinatorial factor in
`WITHIN-ROW-PARITY.md`'s decomposition,

> `D(c1, c2; n, L, K) = #{k ∈ [1, K − L] : cls(k) = c1, cls(k + L) = c2} / (K − L)`,

has a closed-form short-`K` expansion (small `K`, `L` close to `K`)
that captures the leading non-uniform contribution.

For `n = p` prime and `cls = (t, τ-sig of k')`, the joint
distribution of `(cls(k), cls(k + L))` factors at the `t`-axis
(`p`-adic height) according to the residue classes of `k` and
`k + L` modulo `p`, plus a coupled distribution on the
τ-signatures of the cofactors `k', (k+L)'`.

**Status.** The `t`-axis factorization (residue-class densities for
`p | L` vs `p ∤ L`) is mechanical from the master expansion: pairs
with both `k, k + L` divisible by `p` have density `1/p` when
`p | L` and `0` when `p ∤ L`; this is a finite-residue-class count.
What is missing is the τ-signature joint density on the cofactors
`k', (k+L)'`, which is a shifted-divisor-density problem. Even a
leading-order (Tenenbaum III §4) closed form for the squarefree
case would give the algebraic decomposition predictive power for
the lag-`L` autocorrelation profile beyond exact enumeration.

**Why it would matter.** Closes the open piece of the
within-row-parity decomposition: every factor in
`A(n, h, L; K) = Σ D(c1, c2) V(c1) V(c2)` would be closed-form,
and the L-parity gap predictions would have analytic content
beyond enumeration.

---

## 7. Shape-axis OGF (reframed after audit)

**Audit history.** The earlier draft proposed varying `n` over
primes at fixed `k` and conjectured "closed-form structure". The
audit correctly observed that this is mostly trivial: for primes
`p` not dividing `k`, `Q_p(p^h k)` depends only on `h` and the
τ-signature of `k`, so the prime-column subsequence is constant
across all primes coprime to `k`, with finitely many exceptions
(primes dividing `k`). The "interesting" column-axis problem
requires a richer substrate. Reframed below.

**Reframed object.** Walk `n` not through primes but through the
**shape lattice**: `n` indexed by partition (its sorted exponent
tuple `shape(n)`). At fixed `k` coprime to all primes encountered
(say `k = 1`, or `k` chosen far enough below the smallest prime
of any tested `n`), the value `Q_n(n^h k)` depends only on
`shape(n)` plus `(h, τ-sig(k))`. The shape-axis generating
function

> `S(σ; h, τ) := Q_n(n^h k)`     where `shape(n) = σ`, `τ-sig(k) = τ`,

is a function of partition `σ` (with `h` and `τ` parameters). The
8 × 6 matrices in `KERNEL-ZEROS.md` are a finite slice of this:
shapes through `(3, 1)` × τ-sigs through `(1, 1, 1)` at `h ∈
{5, 6, 7, 8}`. Fully closed-form per cell (anchor A8); the open
question is **whether `S(σ; h, τ)` has a closed form as a function
of partitions `σ`**.

**Concrete sub-question.** Restrict to single-row shapes
`σ = (a)` (i.e., `n = p^a`) and trace `S((a); h, τ)` as `a` varies.
Even just for `τ = ()` (`k = 1`):

| `a` | `Q_{p^a}(p^a)` (h=1) | `Q_{p^a}(p^{2a})` (h=2) | … |
|---|---|---|---|
| 1 | 1     | 1/2  | 1/3 | (the prime row) |
| 2 | 1     | 1/2  | -1/6 | (period-3 modulation) |
| 3 | 1     | 1/2  | -2/3 | (irregular) |
| 4 | 1     | 1/2  | … | (TBD) |

The h = 1, 2 columns are universal `1/h`. From h = 3 onward, the
sequence depends on `a`. A closed form expressing `Q_{p^a}(p^{ah})`
as a function of `a` (with `h` fixed) would parallel
KERNEL-ZEROS.md's "boundary value (-1)^(h-1) (h-1)!/∏ e_i!" for
the prime-n row, but for the shape `(a)`-axis instead of the
τ-sig axis.

**Status.** The 8 × 6 matrices give `S` exact-rationally at the
listed cells. A closed-form description of `S(σ)` as a function
of partition `σ` is open. The problem is harder than Proposals 1
or 4 because the shape-axis is not a simple integer lattice but a
lattice of partitions; the relevant generating function is a
symmetric-function expression in indeterminates, not a univariate
OGF.

**Connection to existing work.** `WITHIN-ROW-PARITY.md` already
decomposes the within-row autocorrelation by class signature,
where the algebraic factor `V(c; h)` is exact-rational. A shape-
axis analog would decompose a between-shape correlation (or just
an enumeration over shapes) similarly. The 2D spatial
autocorrelation observed in `arguments/ATTRACTOR-AND-MIRAGE.md`
mixes both axes, so a full closed-form description requires
joint treatment of (τ-sig, shape).

**Why it would matter.** Completes the 2D picture of the Q-lattice
algebra. Currently we have row-axis closed forms (Proposals 1–3)
and the within-row autocorrelation decomposition. The shape-axis
analog would give the symmetric counterpart, characterising how
the Q-lattice varies as `n`'s shape (rather than `k`'s τ-sig)
moves through the partition lattice.

---

## Recommended order (post-audit)

1. **Proposals 1–3 (prime-row OGF, sum, kernel-zero band)** —
   ✓ landed (`Q-FORMULAS.md` §"Row generating function";
   `predict_q.row_polynomial`, `row_sum`; anchor A10).
2. **Proposal 4 (prime-power OGF)** — open, harder than the
   earlier draft suggested. The `a = 2, t = 0, k' = 1` case has a
   clean log-of-cyclotomic closed form (`(1/2) log((1+x+x²)/(1−x))`);
   `a = 2, t = 0, k' = q` has a rational closed form
   `(x − x³)/(1 − x³)`; higher cases need case-by-case work and
   the right organising principle (cyclotomic `Φ_d(x)` factors)
   has not been pinned down in general.
3. **Proposal 5 (squarefree multi-prime OGF)** — open; needs
   Proposal 4 worked out first to suggest the multivariate form.
4. **Proposal 6 (`D` density)** — the deepest open question, in
   the Tenenbaum / shifted-divisor literature; partial closed
   forms (residue-class factor) are easy, the full density is the
   research-grade target.
5. **Proposal 7 (shape-axis OGF)** — open; reframed away from the
   trivial prime-only case to the partition-lattice structure
   over shapes.

## Audit log

A first audit (after the initial draft of this document) found the
following:

- **Proposal 4** was wrong as stated. Two contradictory denominator
  claims and a missed `k' = 1` edge case. Rewritten in §4a/§4b
  above with empirical data from `q_general` replacing the
  speculative form.
- **Proposal 5** had broken notation (`z` not in argument list,
  ill-formed exact-height condition). Notation fixed in §5 above.
- **Proposal 7** was vague and trivialised in the prime-only
  sub-case (column varies over primes ∤ k → constant). Reframed in
  §7 above as a shape-lattice question.
- **Proposal 6** was not flagged. Stands as posed.
- **Proposals 1–3** verified sound.

## Connection to LATTICE-CLOSED-FORM.md

The K_pair lattice work in
`experiments/acm-champernowne/base10/survivors/LATTICE-CLOSED-FORM.md`
is methodologically the same move at a different object: collapse
a formal sum (the search for the smallest shared atom of two
streams) to a finite expression in `gcd` and floors, by exploiting
integer divisibility (`a ∤ (b/g)` in the window regime). The
proposals above transfer this style back to the Q-algebra side.

The shared structure across all these closed forms:

> **Generating-function-collapse-by-divisibility.** A formal sum
> over an unbounded index (Mercator's `j`, or `t` in `t·L`, or `h`
> in `Q_p(p^h k')`) is constrained by integer divisibility to a
> finite or rational expression in elementary arithmetic.

This is the abductive-key pattern in
`memory/abductive_surprise_pattern.md`: the surprise dissolves
once the divisibility constraint is read explicitly. None of these
proposals require new analytic ideas; they require careful
expansion and bookkeeping.
