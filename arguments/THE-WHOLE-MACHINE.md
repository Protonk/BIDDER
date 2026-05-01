# The Whole Machine

A Turing machine walking a binary factorisation graph with costs
metered along the paths. Eleven parts.


## 1. Parameters

`(n, b) ∈ ℤ_{≥2} × ℤ_{≥2}`. Same machinery, different machine.


## 2. Monoid

    M_n = {1} ∪ nℤ_{>0},     ζ_{M_n}(s) = 1 + n^{−s} ζ(s).

Non-UFD: `36 = 6 · 6 = 2 · 18` in `M_2`.


## 3. Atoms

    atoms(n) = { n · c : c ≥ 1, n ∤ c }.

```bqn
NPn2 ← {ks ← 1 + ↕𝕩 × 𝕨 ⋄ 𝕨 × (0 ≠ 𝕨 | ks) / ks}
```


## 4. Graph

Use the ordinary ordered-divisor graph on payloads: `x` decomposes as
ordered j-tuples `(e_1, …, e_j)` with `e_1 · … · e_j = x`.
Branching factor at `x` is `τ_2(x) = d(x)`. Payload path counts:

    τ_j(x) = ∏_{p^e || x} C(e + j − 1, j − 1).

The `M_n` factorisation layer reaches this graph after stripping one
`n` from each nonunit factor. Thus the j-layer path count for
`m ∈ M_n` is

    paths_j(m; n) = τ_j(m / n^j)    if n^j | m,
                  = 0              otherwise.

`Tau` in `algebra/FINITE-RANK-EXPANSION.md`.


## 5. Head

K-index, bilingual: lattice ↔ digit-stream, polylog-bignum to convert.

    c_K = qn + r + 1,    (q, r) = divmod(K − 1, n − 1).

```bqn
HardyCK ← {q ← ⌊ (𝕩 - 1) ÷ (𝕨 - 1)
           r ← (𝕨 - 1) | (𝕩 - 1)
           (𝕨 × q) + r + 1}
```


## 6. Tape

    C_b(n) = 0.p_1(n) p_2(n) p_3(n) …    (in base b).

`ChamDigits10` in `guidance/BQN-AGENT.md` for `b = 10`.


## 7. Program

Mercator log of `ζ_{M_n}`, truncated by integer divisibility:

    Q_n(m) = Σ_{j=1}^{ν_n(m)} (−1)^{j−1} τ_j(m / n^j) / j.

`Qn` in `algebra/FINITE-RANK-EXPANSION.md`.


## 8. Closure

`Q_n(m) ∈ ℚ` with denominator dividing `lcm(1, …, h)`,
`h = ν_n(m)`. Thus it also divides `h!`, but `h!` is only a
looser bound.


## 9. Cost ledger

Each path through the graph pays in three coordinates:

| coordinate     | residual |
|---|---|
| CF             | `offset(n)` by `ord(b, n)` in the coprime subcase; `β(n)` for `O(b^{−k})` tails; off-spike denominator process; intermediate-magnitude excess |
| mult-table     | `α_n = (n − 1)/n` limiting density; finite-K drift toward it |
| digit-frequency | `(n − 1)/n²`; lucky-cancellation locus |


## 10. Halting certificate

Copeland–Erdős (1946) closes base-`b` digit-frequency. See
`sources/COPELAND-ERDOS.md`.


## 11. Open commitment

`{C_b(n) : n ≥ 2, b ≥ 2}` is absolutely normal across all bases.
Submitted to remain open.


## Cross-references

- `THE-OPEN-HEART.md` — prose framing.
- `algebra/Q-FORMULAS.md` — `Q_n` formula sheet.
- `algebra/FINITE-RANK-EXPANSION.md` — rank lemma; `Divs`, `Tau`,
  `Rank`, `Qn`.
- `algebra/WITHIN-ROW-PARITY.md` — autocorrelation decomposition.
- `core/HARDY-SIDESTEP.md` — c_K derivation.
- `core/BLOCK-UNIFORMITY.md` — digit-frequency cost ledger.
- `experiments/acm/cf/MEGA-SPIKE.md` — boundary-spike formula.
- `experiments/acm/cf/DENOMINATOR-PROCESS.md` — CF cost
  ledger.
- `experiments/acm/mult-table/` — mult-table cost ledger.
- `guidance/BQN-AGENT.md` — naming.
