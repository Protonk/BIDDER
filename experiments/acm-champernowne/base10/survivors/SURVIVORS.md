# Survivors

A bundle of `n`-prime streams over a window `[n_0, n_1]`, each truncated at
`k`, can be filtered down to the integers that appear *exactly once* across
the bundle. Concatenating those integers' digits, in order of first
appearance, produces a Champernowne real of the survivors:

`C_Surv_{[n_0, n_1], k}`.

The bundle and the survivor real are two digit sequences over the same
underlying construction. This experiment compares them.


## Construction

For `n >= 2` the `n`-primes are multiples of `n` not divisible by `n^2`:
`{n*m : m >= 1, n ∤ m}`. The list is the first `k` such numbers. Across the
window, read the lists in order `n_0, n_0+1, ..., n_1`. A *survivor* is a
number that occurs in exactly one position in that read order.

Equivalently, writing

`V(m) := {n ∈ [n_0, n_1] : n | m, n^2 ∤ m}`

a number `m` is a survivor in the `k → ∞` limit iff `|V(m)| = 1`. With
finite `k` the survivor set is the truncated version: `m` appears in list
`n` only if it lies among the first `k` `n`-primes, so `m` survives iff it
has rank `≤ k` in *exactly one* list `n ∈ V(m) ∩ [n_0, n_1]`.

Worked example, `[n_0, n_1] = [2, 4]`, `k = 5`:

- `n=2`: 2, 6, 10, 14, 18
- `n=3`: 3, 6, 12, 15, 21
- `n=4`: 4, 8, 12, 20, 24

Concatenated read: `2, 6, 10, 14, 18, 3, 6, 12, 15, 21, 4, 8, 12, 20, 24`.
Doubletons: `6` and `12`. Survivors in order of first appearance:

`Surv_{[2,4], 5} = 2, 10, 14, 18, 3, 15, 21, 4, 8, 20, 24`.

The Champernowne real of those eleven survivors is

`C_Surv_{[2,4], 5} = 1.2 10 14 18 3 15 21 4 8 20 24`
                  ` = 1.21014183152148 2024`

(spaces and the leading `1.` are presentation; the digit stream is the
concatenation).


## How `Surv` varies with `n` and `k`

Two competing flows govern `|Surv|`.

- **Fresh additions.** Each list extends by one entry as `k` grows. The
  new entry is unique by default, so it enters as a survivor.
- **Collisions cull.** Once `k` is large enough that two lists `n, n'` in
  the window both contain a shared element `m`, that element flips from
  "appears once" to "appears twice" and is culled. The smallest collision
  inside `[n_0, n_1]` is the smallest `m` with `|V(m) ∩ [n_0, n_1]| ≥ 2`;
  for a contiguous window starting at `n_0`, generically near
  `n_0(n_0+1)`, with degeneracies whenever `n^2 | m`.

Net effect: `|Surv|` is non-monotone in `k`. It rises by ~`(n_1 − n_0 + 1)`
per step from fresh additions, with occasional drops at collision
thresholds. As `k → ∞` it stabilises to the `|V(m)| = 1` set.

Sliding the window at fixed width does two things at once: each new `n`
contributes its own list-bottom (private, almost always a survivor — primes
in range survive by construction since `V(p) = {p}`), and each new `n`
puts itself into `V(m)` for all its multiples in range, killing previously
single-listed `m`'s. `n_0` itself always survives.


## The Champernowne lens

`k` adjusts the length of each `n`-sequence and, because later `n`-primes
are larger integers, also the number of digits per atom. Sliding the
window region (fixed width) shifts the leading digits of the bundle
(higher `n` → higher leading digits in the early atoms) and changes the
total digit count.

The bundle and `C_Surv` are two digit sequences over the same data: one
is the union, one is the singleton-membership filter of the union. The
two visualisations below probe how the filter deforms the digit-level
structure.


## Proposal 1 — Gated Champernowne Strip

Three horizontal strips, vertically stacked, sharing a common cell width
of one decimal digit.

1. **Bundle strip.** The concatenation
   `C(n_0) ∥ C(n_0+1) ∥ ... ∥ C(n_1)`, each `n` truncated at `k`. Cells
   coloured by digit value (0–9 → 10 hues). Atoms (the digit groups
   belonging to one `n`-prime) separated by hairlines; a thin band above
   marks the contributing `n`.
2. **Gated bundle.** Same geometry, but every atom whose underlying
   integer fails survival is desaturated to grey. Survivors keep their
   colours. Same x-coordinates as strip 1, so the kill-pattern is
   directly readable.
3. **C_Surv strip.** The surviving atoms stitched end-to-end with no
   gaps — the actual Champernowne real of the survivors, shorter than
   the bundle by exactly the killed mass.

Sliders: `k` extends every band (new atoms appear at each band's right
edge; previously-lit atoms blink off as collision thresholds are
crossed). Window-centre at fixed width shifts the whole stack and
reorganises leading-digit content.

What it reads off: where survival mass concentrates by `n`, the
event-driven (not smooth) mass loss as `k` grows, and the difference in
leading-digit profile between bundle and `C_Surv` as the window slides.


## Proposal 2 — Two Tongues (Running L1-Deviation)

A single x-axis = atoms processed (`1, 2, ..., (n_1 − n_0 + 1) · k`).
Two curves on log-y:

- **Bundle tongue.** After processing the first `N` atoms in read order,
  compute the L1 distance of the running digit-frequency vector from
  uniform: `||p_N − u||_1`. Plot for both leading-digit (Benford-relevant,
  `u = 1/9 · 1` over digits 1–9) and all-digit (`u = 1/10 · 1` over
  digits 0–9). This is the bundle's uniformity residual — the same
  residual the algebra/Q-formula docs unpack.
- **Survivor tongue.** Same `N`-axis, same metric, but computed only over
  digits in atoms that have survived given the bundle prefix up to `N`.

Both curves on log-y, with vertical guides at the lcm collision
thresholds where atoms flip lit→grey in Proposal 1.

Variation under sliders: `k` extends the x-axis and one watches whether
the two tongues converge, diverge, or hold a fixed gap. Sliding the
window changes per-segment slope (small-`n` bundles equilibrate faster;
large-`n` bundles' atoms have more digits and tug the trace).

What it reads off: whether the survivor filter preserves the bundle's
exact-by-construction uniformity, distorts it predictably, or breaks it.


## Tracking-Gap Heatmap

A follow-on probe of how tightly `C_Surv`'s L1 curve tracks the bundle's
across the parameter space. For each `(K, n_0)` with fixed window width
`W = 9`, summarise the two leading-digit L1 curves with one signed
scalar — the post-warmup mean of `surv_L1 − bundle_L1`. Plot as a
diverging heatmap, x = `K`, y = `n_0`. Positive = survivor filter makes
the leading-digit distribution *less* uniform than the bundle; negative
= more uniform; zero = perfect tracking. The original Two Tongues
parameters are highlighted.

What it reads off: where in `(K, n_0)`-space the survivor filter
detaches from the bundle, and whether the deviation has a sign bias.

- `l1_grid.py` — heatmap generator.
- `l1_grid.png` — output figure.


## Files

- `SURVIVORS.md` — this document.
- `survivors_core.py` — `survivors_in_window(n0, n1, k)` and helpers.
- `two_tongues.py` — Proposal 2 implementation.
- `two_tongues.png` — output figure.
- `l1_grid.py`, `l1_grid.png` — tracking-gap heatmap.
