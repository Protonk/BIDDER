# Finite Rank Expansion

The local ACM-Mangoldt object `Q_n` is a finite-rank linear combination
of ordered-divisor coefficients, with rank equal to `ν_n(m)`. This is
a theorem of one line, not a conjecture. What remains conjectural is
how the finite-rank local structure couples to global ACM-Champernowne
observables; that is a separate question, addressed below.

For

    M_n = {1} ∪ nZ_{>0},

write

    h = ν_n(m)

for the largest `h` with `n^h | m`. We use **height** and **monoid
rank** for this same number. It is the maximum number of nonunit ACM
factors that can appear in a factorisation of `m`: every nonunit factor
has at least one factor of `n`, so no factorisation can have length
larger than `ν_n(m)`. Conversely, for `m = n^h k` with `h >= 1`,
the factorisation `(nk) · n · ... · n`, with `h-1` copies of `n`,
has length `h`.

The normalized local observable is

    Q_n(m) = Λ_n(m) / log(m).

It is the log-coefficient of the `M_n` monoid's Dirichlet series:

    ζ_{M_n}(s) = Σ_{m ∈ M_n} m^{-s} = 1 + n^{-s} ζ(s),

    Q_n(m) = [m^{-s}] log ζ_{M_n}(s) = [m^{-s}] log(1 + n^{-s} ζ(s)).

This is the `M_n`-monoid analog of `Λ(n)/log n = [n^{-s}] log ζ(s)`.
Mercator expansion of the log gives the formula recorded in
`core/Q-FORMULAS.md`:

    Q_n(m) =
        sum_{j=1}^{ν_n(m)}
            (-1)^(j-1) τ_j(m / n^j) / j.


## Rank Lemma (one-line proof)

The Mercator expansion `log(1 + x) = Σ_{j ≥ 1} (-1)^(j-1) x^j / j`
applied to `x = n^{-s} ζ(s)` gives terms with factor `n^{-js}`. The
coefficient of `m^{-s}` in `n^{-js} ζ(s)^j` is `τ_j(m/n^j)` when
`n^j | m` and zero otherwise. Therefore the sum truncates at
`j = ν_n(m) = h`. The local Q_n object is finite-rank-h by
**integer divisibility**: the j-th term contributes to `[m^{-s}]`
only when `n^j` literally divides `m`.

This is the only structural surprise in the formula. A formally
infinite Mercator series collapses to `h` terms because of how many
times `n` divides `m`. Visible to a clean reader of the formula in
minutes; the kind of integer-divisibility fact catalogued in
`memory/abductive_surprise_pattern.md`.

This document is itself a case study in that pattern. The opening of
this file previously read "Driving conjecture: after the right
normalization, the local ACM-Mangoldt structure is finite-rank." That
framing presented as conjecture what is, mechanically, a one-line
bookkeeping fact about `n^{-js}` and the integers `n^j | m`. The
reframe to "theorem with a one-line proof, plus a separate coupling
conjecture" removes the over-claim and matches what the math actually
says. The lesson is in `core/ABDUCTIVE-KEY.md`: when something in this
project is presented as an ongoing research question, ask first
whether it is mechanically settled by reading the formula.


## BQN Annotation

This is exact-math annotation, not a third implementation. `Rank` is
`ν_n(m)`, `Tau` is the ordered divisor count `τ_j`, and `Qn` is the
finite stack above. The block mirrors the exact formula used in
`experiments/acm-flow/payload_q_scan.py` and expanded in
`core/Q-FORMULAS.md`; it is intentionally small and divisor-enumerating.

```bqn
Divs ← {(0=𝕩|·)⊸/ 1+↕𝕩}

Tau ← {
  j ← 𝕨
  j=1 ? 1 ; +´ { (j-1) Tau 𝕩 }¨ ⌊𝕩÷Divs 𝕩
}

Rank ← {0=𝕨|𝕩 ? 1+𝕨 𝕊 ⌊𝕩÷𝕨 ; 0}

Qn ← {
  h ← 𝕨 Rank 𝕩
  js ← 1+↕h
  sign ← ¯1⋆js-1
  terms ← js Tau¨ ⌊𝕩÷𝕨⋆js
  +´ sign × terms ÷ js
}
```

Read `Qn` from right to left: find the finite rank `h`; build
`j = 1..h`; evaluate `τ_j(m/n^j)`; weight by
`(-1)^(j-1)/j`; sum. The `n = 1` ordinary-prime branch is outside
this monoid-rank formula.


## Rank Reading

The table below illustrates the **prime-n specialisation** of the
master expansion. For prime n at h=3, `τ_2(nk) = 2 d(k)` so the
displayed h=3 entry simplifies to `1 - d(k) + τ_3(k)/3`, matching
the prime row of `core/Q-FORMULAS.md`. For composite n the rank-h
forms are products of binomial-coefficient factors over the primes
of n; see `core/Q-FORMULAS.md` for the full master expansion.

| rank | local form (prime n) | interpretation |
|---|---|---|
| `h = 1` | `Q_n(m) = 1` | atoms are positive. |
| `h = 2` | `Q_n(n²k) = 1 - τ_2(k)/2` | the first sign cliff is exact. |
| `h = 3` | `1 - τ_2(nk)/2 + τ_3(k)/3` | the factorisation type of `n` first becomes visible. |
| `h >= 4` | finite signed stack through `j = h` | more divisor layers enter, but no new local mechanism is needed. |

This is the proposed near-closure. Once `Λ_n` is replaced by `Q_n`,
the local object is a finite signed stack of divisor layers, graded by
monoid rank. Higher rank may be visually rich, but it is not open-ended
in the local algebra.


## Evidence So Far

The acm-flow Phase 1 destroyers support the split between local
arithmetic and cutoff geometry.

The truncated-flow residual `ρ` is not the local observable. It mostly
records cutoff placement and saturation. Payload divisor data survives
destroyers on `Λ_n`, and survives more cleanly on `Q_n`; in the current
panel every tested `(n,h)` cell with `h <= 4` beats the m-shuffle null
on `Q_n` (`z >= 5`, usually much larger). At `h = 5` the result is
mixed at the present cutoff, which is a resolution warning rather than
a counterexample.

Family-geometry subtraction also points the same way. The apparent
cross-prime scale in `Λ_n` nearly disappears after dividing by `log(m)`.
What remains is organised by rank, payload divisor structure, and the
factorisation type of `n`.


## What It Would Buy

The visual reduction tower has a local endpoint:

    raw stream -> visual residuals -> local Λ_n -> finite-rank Q_n.

The remaining hard structure in ACM-Champernowne lives in the coupling
between this local rank stack and global concatenation effects: radix
block boundaries, Hardy-accessed deep windows, continued-fraction
spikes, multiplication-table counts, and cutoff-sieve residues.

`Q_n` is the log-coefficient of `ζ_{M_n}(s)` at a *single* `m`. Global
observables that aggregate over many `m` (mult-table counts, CF
expansions of digit concatenations, Walsh / wavelet readings) are
governed by different generating-function objects and require their
own analyses. The connection from `Q_n`'s local rank-h structure to
those observables is real but **not at the level of leading
exponents**, and not automatic.

Empirical state at the time of writing:

- **Continued-fraction spikes**
  (`experiments/acm-flow/cf/`). The d=k mega-spike size obeys
  `log_b(a) ≈ T_k − 2 L_{k−1} + log_b(b/(b−1))`, where `T_k` is the
  substrate-transparent boundary digit depth (closed-form via
  `BLOCK-UNIFORMITY`) and `L_{k−1}` is the previous convergent's log
  denominator. The off-spike denominator process drives `L_{k−1}`
  away from the substrate-naive `C_{k−1}` by an amount that is
  asymptotically `(n−1) k + offset(n)`. The slope `(n−1)` is
  cleanly substrate-driven; `offset(n)` is per-n with no unified
  closed form across the prime panel.

- **Multiplication-table counts on M_n**
  (`experiments/acm-flow/mult-table/`). At h=2 for prime n, the
  ratio `M_n(K) / M_Ford(K)` drifts toward `α_n = (n−1)/n` (rather
  than `α_n²`) with slow convergence whose functional form has not
  yet been pinned: the simple `α_n + c_1/log K` leading correction
  does not fit, since the empirical `c_1` grows ~10% per decade
  through `K = 10⁸`. Three candidate shapes remain live —
  `1/log K` with non-subdominant higher-order corrections,
  `(log log K)/(log K)`, or `(log K)^{−γ}` with `0 < γ < 1` — and
  current data cannot pin one. The asymptotic deficit exponent is
  **Ford's c** — there is no asymptotic c-shift; the "c(n) > c"
  reading inferred from finite-K bare-count data is a slowly-vanishing
  prefactor transient, not a real exponent shift.

So the "shadow of rank layers" speculation lives at the prefactor /
sub-leading level, not at the leading exponent level. Walking up
rank by rank exercises the local algebra correctly but couples to
global observables through specific case-by-case translations that
have to be done individually. Phase 4 (α′) — the inclusion-exclusion
calculation of `P(k ⊥ n | k ∈ Ford-image-of-K)` — is the next
analytic chunk if we want a quantitative coupling story at h=2.

(α′) by itself may not close the convergence-rate question. Even
after a Ford-anatomy derivation of the leading correction `c_1(n)`,
the empirical K-dependence may not match a single leading-order
form — sub-leading corrections through `K = 10⁸` are of comparable
magnitude. So (α′) might give the leading-order asymptotic and
leave finite-K behaviour to be modeled separately. The doc should
not treat (α′) as automatically closing the coupling problem.

What we did NOT find: a clean local-to-global mapping where rank-h
Q_n cells directly predict deficit exponents in mult-table or
spike-size regularities at the leading order. That picture was the
initial speculation; the empirical work refined it. The local
algebra is closed and exact; the coupling layer is structured but
finite-K bias is large at experimentally reachable scales, and
asymptotic deficit-exponent shifts inferred from finite-K data have
turned out to be transient. The local Q_n object retains its
analytic claim to importance via the Mercator-of-`ζ_{M_n}` framing;
its couplings are ongoing work.
