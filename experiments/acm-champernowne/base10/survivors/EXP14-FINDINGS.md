# EXP14 — K = K(W) prime convergence reframe

EXP06 sketched the question: for what `K(W)` does the survivor set
converge to "primes-in-window"? Empirically composite survivors
GREW with W, with a dip at `W ≈ K`. The original paper-trail's
suggestion was `K ≥ max divisor in window = n_0 + W − 1`. This memo
uses Theorem 1's closed form to decompose the survivor set
structurally and explain why **prime convergence is fundamentally
impossible at finite K**, regardless of how `K` scales with `W`.

## Decomposition of survivors

Each survivor of `B(K, n_0)` falls into one of six categories,
classifiable from atom value alone:

| label | description | culling status |
|---|---|---|
| `P_W` | prime in window `[n_0, n_0 + W − 1]` | always survives (1 stream touches it) |
| `C_W` | composite in window | always survives (no other window stream divides it) |
| `T_A_part` | composite with ≥ 2 window-divisors, only one with position ≤ K | culled at higher K (raise threshold to second position) |
| `T_B_low` | composite `c = d·m`, `d ∈ window`, `m < n_0` | **never culled** — only one window-divisor exists |
| `T_B_high` | composite `c = d·m`, `d ∈ window`, `m > n_0 + W − 1` | excluded from B if `K < m`; otherwise survives |
| `other` | edge cases (`m² | c` etc.) | rare |

Each category is closed-form computable from `(c, n_0, W, K)` —
no empirical walk.

## Empirical decomposition

Sweep over `n_0 ∈ {25, 50, 100}`, `W ∈ [2, 400]`, four `K(W)`
scalings:

|         | K = n_0+W−1 | K = W | K = (n_0+W)/2 | K = 2(n_0+W) |
|---|---|---|---|---|
| **purpose** | Type-A threshold | EXP06 suggestion | half-natural | overshoot |

At `n_0 = 100, W = 397`:

| scaling | K | `\|Surv\|` | `P_W` | `C_W` | `T_A_part` | `T_B_low` | `T_B_high` |
|---|---|---|---|---|---|---|---|
| `n_0+W−1` | 496 | 6,904 | 69 | 146 | 182 | **6,254** | 157 |
| `W` | 397 | 20,065 | 69 | 146 | 13,500 | 6,254 | 0 |
| `(n_0+W)/2` | 248 | 17,501 | 69 | 146 | 10,936 | 6,254 | 0 |
| `2(n_0+W)` | 994 | 57,595 | 69 | 146 | 30,950 | 6,254 | 20,080 |

Key observations:

- **`T_B_low` is constant across scalings** at `K ≥ n_0`. The Type-B
  low-q layer cannot be culled by raising `K`; it is invariant once
  `K` is large enough to admit it.

- **`T_B_high` grows with `K`**. As `K` exceeds `n_0 + W − 1`, more
  high-cofactor composites enter `B` as singletons.

- **`T_A_part` shrinks as `K` increases** towards the natural
  threshold. Above `n_0 + W − 1`, `T_A_part` is suppressed (most
  pairs have both positions reached).

- **`P_W` and `C_W` are independent of `K`**. The window is what it
  is; primes and composites in it are always singletons.

The natural scaling `K = n_0 + W − 1` minimizes the total composite
survivor count — but **`T_B_low` accounts for ~90% of survivors at
n_0 = 100**, growing linearly in `W`.

## Why `T_B_low` is irremovable: the structural obstruction

For composite `c = d · m` with `d ∈ [n_0, n_0 + W − 1]` and `m ∈ [2,
n_0 − 1]`, the atom appears in `B` only via stream `d` (at position
`m − ⌊m/d⌋ ≈ m`). No other window-stream `n ≠ d` can emit `c`, since
`n | c` would force `n ∈ {1, d, m, c} ∩ window`. The candidates:

- `n = m`: not in window (`m < n_0`).
- `n = c = d·m`: not in window (`c > n_0 + W − 1` for typical `n_0,
  m, W`).
- Any other divisor of `c` (depends on factorization of `m`): all
  factors of `m` are `< n_0`, hence not in window.

So `c` is a singleton in `B` whenever it's in `B`, and it's in `B`
iff `K ≥ m`. For `m ≤ n_0 − 1` and any `K ≥ n_0 − 1`, this holds.

**No choice of `K` removes `T_B_low`** — collisions can't happen
because the only stream that contains it is the one window-stream
`d`, while the cofactor `m` lives outside the bundle's stream
collection.

Asymptotically:

> `|T_B_low| ≈ |primes in window| · (n_0 − 2)  ≈  W · n_0 / log n_0`.

(More precisely: for each window-divisor `d`, count integers `m ∈
[2, n_0 − 1]` with `d ∤ m`, weighted by whether `c = dm` is genuinely
new — the leading contribution is `π(window) · (n_0 − 2)`, with
corrections for composite `d`.)

## Asymptotic prime fraction

| quantity | scaling |
|---|---|
| `|P_W|` | `W / log n_0` |
| `|C_W|` | `W · (1 − 1/log n_0)` ≈ `W` |
| `|T_B_low|` | `W · n_0 / log n_0` |
| `|P_W| / |Surv|` | `~ log n_0 / n_0` → **0 as n_0 → ∞** |

So the prime fraction asymptotically **decreases** with `n_0` at any
fixed scaling. EXP06's data already showed this (e.g.,
`|Surv|/π_window` ≈ 47 at `n_0 = 2` but ≈ 169 at `n_0 = 50`); now
the structural reason is clear.

To force prime convergence, two impossibilities must be jointly
overcome:

- **Suppress `T_B_low`** — requires `n_0 → 1` (no integers below the
  window).
- **Suppress `C_W`** — requires the window to contain no composites,
  which fails for any but extremely sparse `n_0` choices.

Both fail at any fixed `(n_0, W)` regime. The construction's stream
collection `{S_n : n ∈ [n_0, n_0 + W − 1]}` is a **bounded
divisor-window** filter; it cannot detect cofactors below `n_0`,
which is exactly where `T_B_low` lives.

## What `K(W)` is "best"?

Even though convergence to primes is impossible, we can still ask:
what `K(W)` minimizes `|composite survivors|`?

The natural scaling `K = n_0 + W − 1` does:

- All Type-A semiprimes (both factors in window) are culled
  (`K ≥ K_pair`).
- All `T_B_high` composites (cofactor > `n_0 + W − 1`) are excluded
  from `B` (since `K = n_0 + W − 1 < m`).
- Only `T_B_low`, `C_W`, and any residual `T_A_part` (multi-divisor
  composites where the second-smallest position exceeds `K`) survive.

So `K = n_0 + W − 1` is the **structural Pareto floor**: any larger
`K` admits more `T_B_high` survivors; any smaller `K` admits more
`T_A_part` survivors. The remaining survivors are `P_W ⊔ C_W ⊔
T_B_low`, all structurally dictated by the window's divisor
geometry.

## Reframing EXP06

The original sketch said the convergence question would be correct
"in a regime where K grows with W — say `K = K(W)` such that for
every composite `c` in bundle range, the position-of-`c` in some
stream falls within `K`." EXP14 sharpens this:

- **Yes**, `K = n_0 + W − 1` is the right threshold for Type-A
  composites (the closed-form `K_pair`).
- **But this only applies to composites with ≥ 2 window-divisors.**
  Composites with 1 window-divisor and a cofactor outside the
  window cannot be culled by collisions, only excluded by position.
- **`T_B_low` (cofactor below the window) is permanently a
  singleton**. It's a structural artifact of the window's lower
  edge.

If we wanted true prime convergence, the construction would need to
include streams `{S_n : n = 2, 3, …, n_0 + W − 1}` — an
ever-growing prefix, not a sliding window of fixed width `W`. That
is a different object.

## Files

- `exp14_prime_convergence_reframe.py` — closed-form decomposition
  + scaling sweep
- `exp14_prime_convergence_reframe.png` — 12-panel figure (3
  composition stacks + prime-fraction; 4 composite-count panels per
  scaling; 4 `T_B_low` panels per scaling)
- `exp14_decomposition.txt` — raw numerical receipts
