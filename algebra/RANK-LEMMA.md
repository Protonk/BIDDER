# Rank lemma

The master expansion of `Q_n(m)` (`MASTER-EXPANSION.md`) terminates
at `j = ν_n(m)`.

## Statement

For `m ∈ M_n` with `h = ν_n(m)`,

    Q_n(m) = Σ_{j=1}^{h} (-1)^{j-1} τ_j(m / n^j) / j,

with no contribution from any `j > h`.

## Proof

By `MASTER-EXPANSION.md`, the `j`-th term of the master expansion has
Dirichlet coefficient `τ_j(m / n^j)`, which is `0` whenever `n^j ∤ m`.
The condition `n^j | m` holds exactly for `j ≤ ν_n(m) = h`. ∎

(The truncation is corollary C1 of `MASTER-EXPANSION.md`; this file
is the named home for citing it.)

## Anchor

A4 in `test_anchors.py` (master expansion vs. `payload_q_scan.csv`)
exercises the truncation across `n ∈ {2, 3, 4, 5, 6, 10}`, every
height in the CSV, and 24,203 rows. A5 cross-checks at coprime
inputs.

## Implementation

`predict_q.q_general(n, h, k)` runs the sum from `j = 1` to
`j = h_eff = h + min_i ⌊t_i / a_i⌋ = ν_n(m)` for `m = n^h k`. The
truncation at `j = h_eff` is the rank lemma in code.
