# PRNG framework

Notes on what translates from Bailey and Crandall's "Random
Generators and Normal Numbers" (Experimental Mathematics 11:4
(2002), 527-546) to BIDDER's `C_Bundle`, `C_Surv`, and the digit
observables we have been computing in `experiments/`. This file is
forward-looking: it sets up conditional theorems and identifies the
canonical normality observable we have been only partially using.

## What translates

1. **Erdős–Copeland baseline.** The bundle's unique integers in
   sorted order are `O(i)`-growth (the i-th n-prime in stream `n` is
   `n²·i/(n−1) + O(1)`, polynomial in `i` with degree 1 across all
   streams). Concatenating those unique integers in sorted order
   gives a real number that is `b`-normal for every `b ≥ 2` by
   [Copeland and Erdős 1946]; the paper restates this as the class
   of `0.(a₁)_b(a₂)_b(a₃)_b ⋯` numbers with `aₙ = O(n^{1+ε})`.

   This is **not** our `C_Bundle` (which uses stream-first order with
   duplicates, not sorted unique order), but it is the natural
   *control* for any normality claim about our constructions: a
   neighbour with a known normality answer.

2. **The PRNG framing.** Every normality theorem in the paper goes
   through equidistribution of a PRNG iterate
   `xₙ = (b · xₙ₋₁ + rₙ) mod 1`, and equidistribution is established
   via a discrepancy bound. The associated normal constant `α` is
   the limit of the iterate. For `C_Surv` and friends, the
   equidistribution observable is the orbit `{bⁿ · C_Surv}` of
   shifted tails — and our leading-digit L1 is a coarse projection
   of the right object.

3. **Discrepancy is the canonical observable.** Theorem 2.2(11),
   2.2(12) in Bailey–Crandall: `α` is `b`-dense iff `D_N({bⁿα}) → 0`
   in the weak sense, `b`-normal iff `D_N({bⁿα}) → 0` along all
   blocks. The empirical observable is the **star discrepancy** of
   the orbit `{10ⁿ · C_Surv}` for `n = 0, …, L − 1` — easy to
   compute from the digit string. We have been using leading-digit
   L1, which is a projection of this onto the `[k/10, (k+1)/10)`
   intervals. The full star discrepancy strengthens it.

4. **Bailey–Crandall Theorem 4.8 as a template.** Their
   `(b, c, m, n)`-PRNG sequence
   `α_{b,c,m,n} = Σ 1/(c^{nᵢ} b^{mᵢ})` is `b`-normal under joint
   growth conditions on the gap sequences
   `μ_k = m_k − m_{k−1}, ν_k = n_k − n_{k−1}`:
   (i) `(ν_k)` non-decreasing,
   (ii) `μ_k / c^{γ n_k} ≥ μ_{k−1} / c^{γ n_{k−1}}` for some
   `γ > 1/2`.
   The analog statement we want for `C_Surv`: a growth condition on
   `(survival rate, mean-digit-length)(K)` that suffices for
   `b`-normality of `lim C_Surv^{(K)}`.

5. **Theorem 6.2 names the regime our finite-K imprint sits in.**
   `α = Σ P(n)/b^{Q(n)}` with `deg Q > deg P` is `b`-dense but
   *not* `b`-normal — most digits are `0`. This is structurally
   the same observation as our ECHO-STRUCTURE.md: a base-aware
   mechanism cannot have base-blind decay; polynomial-decay
   perturbations to a digit construction give density without
   delivering normality.

## Conditional theorem (template)

**Conjecture (BIDDER survivor-normality).** Let `[n_0, n_1]` be a
window of width `W = n_1 − n_0 + 1 ≥ 2` and let `K_i → ∞`. Define
`C_Surv^{(K)}` as the digit concatenation of the survivor integers
at panel `(n_0, n_1, K)` in their bundle-first-appearance order.
If the joint sequence

```
( |S(K)| / (W·K),    L_surv(K) / |S(K)| )
```

(survival rate at the multiset level, and mean digit-length per
survivor) satisfies a growth condition analogous to
Bailey–Crandall Theorem 4.8 (i)–(ii), then `lim_{K→∞} C_Surv^{(K)}`
exists and is `10`-normal.

**Status.** The condition is not yet stated precisely; the
`(b, c, m, n)`-PRNG family differs from the survivor sequence in
ways that need careful translation. Empirical inputs from
`experiments/`:

- ECHO-STRUCTURE.md — base-10 echo cascade with geometric ratio
  ~0.80 per K-decade. The growth condition has to allow this slow
  staircase decay.
- primality/PRIMALITY.md — bracketing direction rotates with `W`,
  passing through near-degenerate `|z| → 0` configurations around
  `W = 15–20`. Suggests the conjecture is `W`-conditional, not
  uniform across windows.

## K-scaling result (revises the conjecture)

The K-scaling sweep at
`experiments/acm-champernowne/dsubn/k_scaling.py` over
K ∈ {100, 200, 400, 800, 1600, 3200, 6400} measured `D_L*`(K) for
all five constructions at `[2, 10]`. Result:

- `D_L*` does not decay smoothly with K. Values fluctuate in
  `[0.05, 0.16]` across the entire K range, with non-monotone
  oscillation suggestive of K-decade echo influence.
- The Erdős–Copeland-rate benchmark `(log L)/√L` is being
  outpaced at large K. By K = 6400 every construction (including
  the *known* 10-normal `C_Bundle_sorted` Champernowne) sits at
  > 2× the `(log L)/√L` benchmark.
- Bracketing washes out — at K = 6400 the cofactor primality split
  collapses to within 0.025 across all subsets, where at K = 400
  it spanned 0.05.

**Revised conjecture.** `D_L*(K) → 0` as K → ∞ holds (consistent
with the data), but the rate is constrained from below by the
K-decade echo amplitude (geometric ratio ~0.80 per decade per
ECHO-STRUCTURE.md), not by `(log L)/√L`. The Erdős–Copeland-rate
form of the conjecture is too strong; the echo cascade is the
empirical obstruction.

This restates the lesson in ECHO-STRUCTURE.md at the discrepancy
level: a base-aware mechanism cannot have a base-blind decay.

## What the discrepancy probe should show

For `C_Surv` at the Two Tongues panel `[2, 10], K = 400` and its
primality stratifications:

- `D_N(C_Surv)` vs `D_N(C_Bundle)` — both should be small and shrink
  with `K`. The bracketing structure on the L1 axis should appear at
  the `D_N` axis, with composite-cofactor `C_Surv` showing higher
  `D_N` than the bundle and prime-cofactor `C_Surv` showing lower.
- `D_N(C_Bundle_sorted)` — the Erdős–Copeland baseline. Should be
  the smallest of all (asymptotically `O((log N)/√N)`).

The L1 magnitude observable is one projection of the orbit
`{10ⁿ α}`; `D_N` is the sup-over-intervals projection. Bailey–
Crandall's theorems live in the `D_N` world; ours have so far lived
in the L1 world.

## Cross-references

- `MASTER-EXPANSION.md` — our Mercator-from-`log ζ_{M_n}`; parallel
  to the paper's Mercator-from-`log` structures.
- `ROW-OGF.md` — `F(x; p, k') = Σ Q_p(p^h k') · x^h`; structurally
  a Bailey–Crandall-style Mercator OGF over `h`.
- `experiments/acm-champernowne/base10/survivors/ECHO-STRUCTURE.md`
  — the empirical fact a growth-condition normality theorem has to
  be consistent with.
- `experiments/acm-champernowne/base10/survivors/primality/PRIMALITY.md`
  — the bracketing observation; the prime-cofactor / composite-
  cofactor split is the "two-PRNG difference" view in our setting.
- `experiments/acm-champernowne/base10/survivors/primality/discrepancy.py`
  — the empirical `D_N` probe described in §"What the discrepancy
  probe should show".

## Source

Bailey, D. H. and Crandall, R. E. *Random Generators and Normal
Numbers.* Experimental Mathematics 11:4 (2002), 527–546.
`sources/Random Generators and Normal Numbers.pdf`.
