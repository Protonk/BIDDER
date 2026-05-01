# Denominator bound

The denominator of `Q_n(m)` divides `lcm(1, 2, …, ν_n(m))`.

## Statement

For every `n ≥ 2` and every `m ∈ M_n` with `h = ν_n(m) ≥ 1`,

    Q_n(m) ∈ ℚ,    denom(Q_n(m)) | lcm(1, 2, …, h).

## Proof

By the master expansion (`MASTER-EXPANSION.md`),

    Q_n(m) = Σ_{j=1}^{h} (integer)_j / j,

where `(integer)_j = (-1)^{j-1} ∏_i C(a_i(h-j) + t_i + j - 1, j - 1)
· τ_j(k')` is an integer (each binomial coefficient and each `τ_j` is
an integer). The common denominator of the `h` summands divides
`lcm(1, …, h)`. ∎

The bound `denom | h!` is looser; `lcm(1, …, h) | h!` strictly for
`h ≥ 4` (e.g., `lcm(1..6) = 60` but `6! = 720`).

## Anchor

A9 in `test_anchors.py`: 1650 `(n, h, k)` triples, with the bound
applied in the *true* `ν_n(m)` of `m = n^h k` (which can exceed the
input `h` when `k` carries factors of `n`).
