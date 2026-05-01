# Kernel zeros for prime n

The prime row of the Q-lattice has a sharp `Ω`-axis structure: zero
below `Ω = h`, a multinomial-style boundary value at `Ω = h`. For
non-prime `n`, the kernel-zero locus is sparser and structurally
different.

## Statement

Let `p` be prime, `h ≥ 2`, `k ≥ 2` coprime to `p`, and write
`k = ∏_i q_i^{e_i}`, `Ω(k) = ∑ e_i`.

(i) **Below the kernel.** If `Ω(k) ≤ h - 1`, then `Q_p(p^h · k) = 0`.

(ii) **Boundary.** If `Ω(k) = h`, then

    Q_p(p^h · k) = (-1)^{h-1} (h-1)! / ∏_i e_i!.

(iii) **Carve-out.** `Q_p(p^h · 1) = 1/h` (corollary in
`MASTER-EXPANSION.md`); not a kernel zero.

(iv) **Above.** For `Ω(k) ≥ h + 1`, the value follows the master
expansion in `MASTER-EXPANSION.md`. No accidental zero is observed in
the verified range `h ≤ 8`, `Ω(k) ≤ 13`.

## Proof

Use the prime-`n` specialisation `MASTER-EXPANSION.md` (C3). The
classical finite-difference identity gives, for any polynomial
`R(j)`,

    Σ_{j=1}^{h} (-1)^{j-1} C(h - 1, j - 1) R(j)
        = (-1)^{h-1} Δ^{h-1} R(1),

the `(h-1)`-th forward difference of `R` at `j = 1`. `Δ^{h-1}`
annihilates polynomials of degree at most `h - 2`.

*Polynomial structure of `τ_j(k)/j`.* `τ_j(q^e) = C(e + j - 1, e)` is
a polynomial in `j` of degree `e` with leading coefficient `1/e!`.
Multiplicativity gives `τ_j(k) = ∏_i C(e_i + j - 1, e_i)`, a
polynomial in `j` of degree `Ω(k)` with leading coefficient
`1 / ∏_i e_i!`. The polynomial `τ_j(k)` has a root at `j = 0`
whenever `k ≥ 2` (each factor `C(e_i + j - 1, e_i)` evaluates to
`C(e_i - 1, e_i) = 0` at `j = 0` for `e_i ≥ 1`). Therefore
`R(j) := τ_j(k) / j` is a polynomial in `j` of degree `Ω(k) - 1`.

(Arithmetic note: as integers, `j ∣ τ_j(k)` for every `j ≥ 1` is not
true — e.g. `τ_2(q²) = 3`. The proof uses only the polynomial-root
form, which is what the finite-difference argument requires.)

(i) `Ω(k) ≤ h - 1` implies `deg R ≤ h - 2`, so the kernel identity
gives `Q_p(p^h k) = 0`.

(ii) `Ω(k) = h` implies `deg R = h - 1`. The `(h-1)`-th difference of
a polynomial of degree exactly `h - 1` equals `(h-1)!` times the
leading coefficient, namely `(h-1)! / ∏_i e_i!`. Multiplying by
`(-1)^{h-1}` gives the boundary value. ∎

## BQN

Specialised in `OBJECTS.md`. The general case `Q_p(p^h k)` is
`Qn` from `MASTER-EXPANSION.md` at `𝕨 = p`.

## Boundary multiset values

Boundary value `(-1)^{h-1} (h-1)! / ∏ e_i!` at small `h`, by
partition of `h`:

| h | partition `e`     | `(h-1)! / ∏ e_i!` |
|---|---|---|
| 2 | `(2)`             | `1/2`             |
| 2 | `(1, 1)`          | `1`               |
| 3 | `(3)`             | `1/3`             |
| 3 | `(2, 1)`          | `1`               |
| 3 | `(1, 1, 1)`       | `2`               |
| 4 | `(4)`             | `1/4`             |
| 4 | `(3, 1)`          | `1`               |
| 4 | `(2, 2)`          | `3/2`             |
| 4 | `(2, 1, 1)`       | `3`               |
| 4 | `(1, 1, 1, 1)`    | `6`               |
| 5 | `(5)`             | `1/5`             |
| 5 | `(1, 1, 1, 1, 1)` | `24`              |

The minimum-magnitude boundary value at fixed `h` is `1/h` (at
partition `(h)`); the maximum is `(h-1)!` (at the all-distinct
partition `(1, 1, …, 1)`). Sign is `(-1)^{h-1}`.

## (shape, τ-signature) matrices

Eight shapes × six τ-signatures, every cell exact, frozen via
`q_value_by_class` and anchored.

Shapes: `(1,), (2,), (1,1), (3,), (2,1), (1,1,1), (4,), (3,1)`.
τ-signatures: `(), (1,), (2,), (1,1), (3,), (1,1,1)`.

The labels are: `p, p^2, pq, p^3, p^2 q, pqr, p^4, p^3 q` for shapes
and `1, q, q^2, qr, q^3, qrs` for τ-sigs.

### h = 5

| shape \ tau_sig | 1 | q | q^2 | qr | q^3 | qrs |
|---|---|---|---|---|---|---|
| p     | 1/5   | 0   | 0    | 0    | 0    | 0     |
| p^2   | 1/5   | 0   | -3/2 | -3   | -6   | -27   |
| pq    | 6/5   | 6   | 12   | 18   | 16   | 30    |
| p^3   | 8/15  | 0   | -5   | -10  | -56/3 | -82  |
| p^2 q | 36/5  | 24  | 42   | 60   | 52   | 84    |
| pqr   | 126/5 | 90  | 180  | 270  | 280  | 690   |
| p^4   | 19/20 | -1  | -13  | -25  | -43  | -181  |
| p^3 q | 86/5  | 50  | 80   | 110  | 88   | 98    |

Anchor A2 in `test_anchors.py`.

### h = 6

| shape \ tau_sig | 1 | q | q^2 | qr | q^3 | qrs |
|---|---|---|---|---|---|---|
| p     | 1/6   | 0   | 0    | 0    | 0    | 0     |
| p^2   | -1/12 | -1  | -5/2 | -4   | -3   | -4    |
| pq    | 5/3   | 0   | -15  | -30  | -50  | -210  |
| p^3   | -4/3  | -7  | -17  | -27  | -26  | -61   |
| p^2 q | -5/6  | -40 | -160 | -280 | -390 | -1420 |
| pqr   | 140/3 | 0   | -315 | -630 | -1050 | -4410 |
| p^4   | -55/12 | -21 | -97/2 | -76 | -74  | -174  |
| p^3 q | -70/3 | -180 | -575 | -970 | -1280 | -4410 |

### h = 7

| shape \ tau_sig | 1 | q | q^2 | qr | q^3 | qrs |
|---|---|---|---|---|---|---|
| p     | 1/7    | 0    | 0    | 0    | 0    | 0     |
| p^2   | 1/7    | 1    | 5    | 9    | 15   | 61    |
| pq    | -20/7  | -20  | -50  | -80  | -70  | -140  |
| p^3   | 8/7    | 11   | 47   | 83   | 395/3 | 519  |
| p^2 q | -265/7 | -145 | -235 | -325 | -95  | 695   |
| pqr   | -2400/7 | -1680 | -4200 | -6720 | -7560 | -21840 |
| p^4   | 165/28 | 48   | 186  | 324  | 495  | 1902  |
| p^3 q | -825/7 | -315 | -135 | 45   | 1285 | 8205  |

### h = 8

| shape \ tau_sig | 1 | q | q^2 | qr | q^3 | qrs |
|---|---|---|---|---|---|---|
| p     | 1/8    | 0    | 0      | 0     | 0     | 0      |
| p^2   | 1/8    | 0    | -5/2   | -5    | -15   | -75    |
| pq    | -35/8  | 0    | 70     | 140   | 280   | 1260   |
| p^3   | 23/24  | -1   | -67/2  | -66   | -518/3 | -836  |
| p^2 q | 245/8  | 420  | 3535/2 | 3115  | 4655  | 17745  |
| pqr   | -5775/8 | 0   | 8400   | 16800 | 33600 | 151200 |
| p^4   | 21/8   | -20  | -206   | -392  | -891  | -4130  |
| p^3 q | 3017/8 | 2709 | 18333/2 | 15624 | 21294 | 75474 |

## Anchor

A7 in `test_anchors.py`: classifier across `h ∈ [2, 8]`, every
partition of every `Ω ∈ [1, 13]` (2604 cases). A8: the matrices
above, all 144 cells.

## Scope

The classifier above is for prime `n` only. The non-prime kernel-zero
locus is open; see `PROPOSED-CLOSED-FORMS.md` Proposal 4.
