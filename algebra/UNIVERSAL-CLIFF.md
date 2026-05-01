# Universal h = 2 cliff

A single closed form for `Q_n` at height `h = 2`, valid for every
shape of `n` whenever the height is exactly 2.

## Statement

For every `n ≥ 2` and every `k ≥ 1` with `gcd(k, n) = 1`,

    Q_n(n² · k) = 1 - d(k) / 2,

where `d(k) = τ_2(k)` is the divisor count.

The hypothesis `gcd(k, n) = 1` is exactly the condition `ν_n(n²k) =
2`. When `k` carries factors of `n`, the height of `n²k` exceeds 2
and the formula no longer applies (e.g. `Q_2(2² · 2) = Q_2(8) = 1/3`,
not `1 - d(2)/2 = 0`).

## Proof

Apply the master expansion (`MASTER-EXPANSION.md`) at `h = 2` with
`gcd(k, n) = 1` (so every `t_i = 0`):

- `j = 1`: `∏_i C(a_i, 0) · τ_1(k) / 1 = 1`.
- `j = 2`: `-∏_i C(1, 1) · τ_2(k) / 2 = -d(k) / 2`.

The two terms add to `1 - d(k)/2`. The shape `(a_1, …, a_r)` of `n`
does not appear in either term. ∎

## BQN

```bqn
H2 ← {1 - (2 Tau 𝕩) ÷ 2}
```

`Tau` is in `OBJECTS.md`. `H2` returns the cliff value at the
coprime payload `𝕩 = k`; the caller is responsible for ensuring
`gcd(𝕩, n) = 1`.

## Anchor

A3 in `test_anchors.py`: every `(n, k)` with `2 ≤ n ≤ 20`,
`1 ≤ k ≤ 30`, `gcd(k, n) = 1` (347 pairs).
