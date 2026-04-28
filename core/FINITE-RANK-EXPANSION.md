# Finite Rank Expansion

Driving conjecture: after the right normalization, the local
ACM-Mangoldt structure is finite-rank. The complicated global pictures
come from how these finite local layers are concatenated, cut off, and
read in a radix stream; they are not evidence that the local arithmetic
requires an infinite hierarchy.

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

The exact formula, recorded and expanded in `core/Q-FORMULAS.md`, is

    Q_n(m) =
        sum_{j=1}^{ν_n(m)}
            (-1)^(j-1) τ_j(m / n^j) / j.

The upper limit is the point. The expansion stops at rank `h` because
`n^j` no longer divides `m` above that height.


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

| rank | local form | interpretation |
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

If this is the right organising principle, then the visual reduction
tower has a local endpoint:

    raw stream -> visual residuals -> local Λ_n -> finite-rank Q_n.

The remaining hard structure in ACM-Champernowne would then live in the
coupling between this local rank stack and global concatenation effects:
radix block boundaries, Hardy-accessed deep windows, continued-fraction
spikes, and cutoff-sieve residues.

Speculation: the continued-fraction spike law and the
multiplication-table experiments may be shadows of the same rank layers
seen through different global projections. That is not proven; it is
the next target because the larger alternatives have started to fall
away.
