# Tables

Specific evaluations of `Q_n(m)` from the master expansion. Each
table is a finite slice of the algebra in `MASTER-EXPANSION.md`. Every
displayed value is exact; cross-check via
`predict_q.q_general(n, h, k)` returning `Fraction`.

This file holds the tabulated values only. Theorems live in
`MASTER-EXPANSION.md`, `RANK-LEMMA.md`, `UNIVERSAL-CLIFF.md`,
`DENOMINATOR-BOUND.md`, `KERNEL-ZEROS.md`, `ROW-OGF.md`.

## Prime n

For prime `p` and `gcd(p, k) = 1`, the master expansion specialises
as in `MASTER-EXPANSION.md` (C3). Direct expansion at low `h`:

| h | `Q_p(p^h k)`                                    |
|---|---|
| 1 | `1`                                             |
| 2 | `1 - d(k)/2`                                    |
| 3 | `1 - d(k) + τ_3(k)/3`                           |
| 4 | `1 - 3d(k)/2 + τ_3(k) - τ_4(k)/4`               |
| 5 | `1 - 2d(k) + 2τ_3(k) - τ_4(k) + τ_5(k)/5`       |

The `h = 2` row is `UNIVERSAL-CLIFF.md`.
The full prime-row OGF is `ROW-OGF.md`.
The kernel-zero band is `KERNEL-ZEROS.md`.

### h = 3 prime row

| k                       | `Q_p(p³k)` |
|---|---|
| `1`                     | `1/3`      |
| `q`, `q²`, or `qr`      | `0`        |
| larger coprime payloads | non-negative |

The zero rows are `Ω(k) = 1` and `Ω(k) = 2` cases of the kernel-zero
classifier (`KERNEL-ZEROS.md` (i) at `h = 3`).

Anchor: A6 in `test_anchors.py` freezes ten of these displayed cells
across `p ∈ {3, 5, 7}`.

## Prime power n = p^a, a ≥ 2

Write `k = p^t k'`, `0 ≤ t < a`, `gcd(p, k') = 1`. Then

    Q_{p^a}(p^{ah + t} k')
        = Σ_{j=1}^{h} (-1)^{j-1} C(a(h-j) + t + j - 1, j - 1) τ_j(k') / j.

### n = 4 = 2², low h

| h | t | `Q_4` |
|---|---|---|
| 1 | 0 | `1`                                   |
| 1 | 1 | `1`                                   |
| 2 | 0 | `1 - d(k')/2`                         |
| 2 | 1 | `1 - d(k')`                           |
| 3 | 0 | `1 - 3d(k')/2 + τ_3(k')/3`            |
| 3 | 1 | `1 - 2d(k') + τ_3(k')`                |
| 4 | 0 | `1 - 5d(k')/2 + 2τ_3(k') - τ_4(k')/4` |
| 4 | 1 | `1 - 3d(k') + 10τ_3(k')/3 - τ_4(k')`  |

### n = 4 at h = 3

| t | k' | `Q_4` |
|---|---|---|
| 0 | 1 | `-1/6` |
| 0 | q | `-1`   |
| 1 | 1 | `0`    |
| 1 | q | `0`    |

Anchor: A6 freezes six of these `n = 4` cells.

## Squarefree multi-prime n, r ≥ 2

Write `n = p_1 p_2 ⋯ p_r` and `k = p_1^{t_1} ⋯ p_r^{t_r} k'` with
`gcd(k', n) = 1`. The exact-height condition forces some `t_i = 0`.
The master expansion gives

    Q_n(m) = Σ_{j=1}^{h} (-1)^{j-1}
               [∏_{i=1}^{r} C(h + t_i - 1, j - 1)] · τ_j(k') / j.

### r = 2 at h = 2

The cliff applies for every overlap case; see `UNIVERSAL-CLIFF.md`.

### r = 2 at h = 3

| overlap `(t_1, t_2)` | `Q_n` |
|---|---|
| `(0, 0)`               | `1 - 2d(k') + τ_3(k')/3`                                     |
| `(t, 0)`, `t ≥ 1`      | `1 - (t+2) d(k') + ((t+2)(t+1)/2) τ_3(k')/3`                 |
| `(0, t)`, `t ≥ 1`      | symmetric                                                    |

### r = 2 at h = 3, (0, 0) overlap

| k' | `Q_n` |
|---|---|
| `1`  | `-2/3` |
| `q`  | `-2`   |
| `q²` | `-3`   |
| `qr` | `-4`   |

### r = 2 at h = 4

| overlap | `Q_n` |
|---|---|
| `(0, 0)` | `1 - 9d(k')/2 + 3τ_3(k') - τ_4(k')/4` |
| `(t, 0)`, `t ≥ 1` | `1 - 3(t+3) d(k')/2 + ((t+3)(t+2)/2) τ_3(k') - ((t+3)(t+2)(t+1)/24) τ_4(k')` |
| `(0, t)`, `t ≥ 1` | symmetric |

Anchor: A6 freezes eight of the displayed cells across `n ∈ {6, 10}`.

## (shape, τ-signature) matrices

The 8 × 6 matrices at `h = 5, 6, 7, 8` over the eight shapes
`(1,), (2,), (1,1), (3,), (2,1), (1,1,1), (4,), (3,1)` and the six
τ-signatures `(), (1,), (2,), (1,1), (3,), (1,1,1)` are tabulated in
`KERNEL-ZEROS.md` and frozen as anchors A2 (h=5) and A8 (h=6,7,8).

## Pending

The master expansion is universal; the displayed-table coverage in
this file is not. Cells that are not yet tabulated:

- Prime power `n = p^a`, `a = 3` (e.g. `n = 8, 27`).
- Squarefree multi-prime `r ≥ 3` (e.g. `n = 30 = 2·3·5`) at any `h`.
- Mixed-exponent `n` (e.g. `n = 12 = 2² · 3`) at any `h`.
- Squarefree multi-prime `r = 2` at `h ≥ 5`.

Each is reachable: `q_value_by_class(shape, h, tau_sig)` covers the
`gcd(k, n) = 1` cells, and `q_general(n, h, k)` covers overlap cells
where `k` carries factors of `n`'s primes. Adding a row here is the
only remaining step.

Open closed-form proposals (no displayed evaluation yet) are tracked
in `PROPOSED-CLOSED-FORMS.md`.
