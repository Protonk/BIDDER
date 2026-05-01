# Hardy Echo — first-pass empirical results

`hardy_echo.py` ran. Brief: `DEEP-TROUBLE-No-4.md`. Five
experiments + a smoke check, ~1 second total runtime.


## Smoke check — passes

Hardy closed form vs `acm_n_primes` enumerator: 1200 cases agree
(`n ∈ {2, 3, 4, 5, 6, 10}`, `K ∈ [1, 200]`). The window primitive
is pinned against the working pipeline.


## Exp 1 — Deep window vs prefix window, RLE histogram

`n = 2`, prefix `K ∈ [1, 200]` vs deep `K ∈ [10⁹, 10⁹ + 200]`.

| metric | prefix | deep |
|---|---|---|
| avg base-10 digit length | 2.87 | 10.00 |
| total bits | varies | varies |
| bit balance (fraction of 1s) | varies | varies |

**Visible asymmetry in the deep window**: 1-runs of length 3 appear
much more often than 0-runs of length 3 (~450 vs ~70). At
`K ≈ 10⁹` every entry is `≈ 4 × 10⁹ = 0xEE6B2800...` in binary —
the high bits include a `111` motif that propagates as a
length-3 1-run for every entry. This is a *positional* artifact of
the narrow log-bit-length range at deep K, not an algebraic
property of n-primes. In the prefix window entries span 1..10
bits, so the high-bit structure averages out and no single
run-length stands out.

**Lesson**: at deep K, all entries have nearly the same bit length,
which concentrates positional structure that prefix windows
average out. Mode 1 is not "the same observable, just at a
different K" — it is a *different regime*. Comparisons to prefix
data should match log-bit-length, not just sample size.


## Exp 2 — Boundary-stitch barcode persists; the right destroyer is selective

`n = 2`, `v_2(n) = 1` predicts every `p_K(n)` is even, hence the
last bit of every entry is 0. The boundary-stitch image's
column-7 (last trailing bit before each join) should be uniformly 0.

| view | column-7 "1"-rate |
|---|---:|
| prefix `K ∈ [1, 200]` | 0.0000 |
| deep `K ∈ [10⁹, +200]` | 0.0000 |
| deep, entry-shuffled (null) | 0.0000 |

The barcode persists at depth (predicted by closed-form
arithmetic). **The within-window entry-shuffle null does NOT
destroy it** — every entry is still even after permutation, so
the trailing zero stays.

This is a methodological finding. Mode 4's default destroyer
(within-window entry shuffle) is correct for **position-side**
claims (right-side gradient, between-entry ordering) but wrong
for **algebra-side** claims (per-entry properties like `v_2(n)`
trailing-zero barcode). The right destroyer for the algebra-side
shuffles *bits within entries*, preserving the entry multiset.

The full image (`exp2_boundary_stitch.png`) makes the split
visible: the trailing-zero column persists in all three panels;
the leading-bits region (right of join) is structured in deep, with
a nearly constant high-bit barcode from entries near `4×10⁹`, and
noisy in shuffle-null. The right side responds to the destroyer; the
left side does not.

This refines `DEEP-TROUBLE-No-4.md` Mode 4: the protocol must
specify *which destroyer* matches *which observable type*.


## Exp 3 — Block boundary at depth, BLOCK-UNIFORMITY verified

`n = 2`, base 10, `d ∈ {1..6}`. Mode 3 finds `K ∈ [K_min, K_max]`
such that `p_K(n) ∈ [10^(d−1), 10^d)`.

| d | block | K range | count | predicted (smooth) |
|---|---|---|---:|---:|
| 1 | [1, 10) | [1, 2] | 2 | n/a (`d=1`) |
| 2 | [10, 100) | [3, 25] | 23 | n/a (4 ∤ 10) |
| 3 | [100, 1000) | [26, 250] | 225 | **225** ✓ |
| 4 | [1000, 10000) | [251, 2500] | 2250 | **2250** ✓ |
| 5 | [10000, 100000) | [2501, 25000] | 22500 | **22500** ✓ |
| 6 | [100000, 1000000) | [25001, 250000] | 225000 | **225000** ✓ |

The smooth-block prediction `(b−1)·b^(d−1)·(n−1)/n²` from
`core/BLOCK-UNIFORMITY.md` matches the actual count exactly at
`d ∈ {3, 4, 5, 6}` for `n = 2` in base 10. The non-smooth `d = 2`
gives 23 (computable by inclusion-exclusion: multiples of 2 in
[10, 99] minus multiples of 4 = 45 − 22 = 23).

This is the verification harness Phase 3.1 of
`experiments/acm/flow/STRUCTURE-HUNT.md` needs. Pushing `d` to
50 or 100 is one parameter change.


## Exp 4 — Digit-position oracle (Mode 2), exact by block inversion

The oracle uses `K_for_block(n,b,d)` to walk whole digit-length blocks,
then divides the residual offset inside the containing block. At
`n = 2`, base 10, with ground-truth from a 1000-entry prefix:

| i | true (K, off) | oracle (K, off) | match |
|---:|---|---|---:|
| 1 | (1, 0) | (1, 0) | ✓ |
| 100 | (43, 0) | (43, 0) | ✓ |
| 1000 | (320, 0) | (320, 0) | ✓ |
| 2000 | (570, 0) | (570, 0) | ✓ |
| 3000 | (820, 0) | (820, 0) | ✓ |

The oracle is exact on this smoke panel and scales with digit depth
rather than with `K`.


## Exp 5 — Finite-rank consistency at depth (atoms-only limitation)

Tested `Q_n(p_K(n))` for `(n, K) ∈ {(2, 10⁶), (3, 10⁶), (5, 10⁵), (2, 10⁹)}`.

For *every* sample, `ν_n(m) = 1` and `Q_n(m) = 1`.

**Why**: n-primes are *atoms* of `M_n` by construction. Their
height is always 1, and the closed-form sum at h=1 is just
`τ_1(m/n)/1 = 1`. The lemma at h=1 holds vacuously and is
independent of K.

**Implication**: Hardy random access on its own does not test
the finite-rank lemma at higher rank. To verify Q_n at h ≥ 2 at
deep K, sample two (or more) deep n-primes and multiply. For prime
`n`, `m = p_{K_1}(n) · p_{K_2}(n)` has height 2; for composite `n`,
compute `ν_n(m)` after multiplication because residual cofactors can
add extra height. The Q_n closed form then applies at the measured
height.

The doc speculation is now corrected to specify this composite-
sampling protocol.


## What this round establishes

- The Hardy closed form is pinned (smoke check).
- Mode 1 (deep window) is operational, with the caveat that
  "deep" is its own regime — the digit-length distribution is
  narrow, which concentrates positional structure differently
  than prefix data.
- Mode 3 (block boundary) verifies BLOCK-UNIFORMITY exactly at
  depth. The instrument is ready for Phase 3.1 verification of
  the CF-spike formula.
- Mode 4 (tail destroyer) needs the destroyer match the
  observable type — algebra-side vs position-side claims need
  different shuffles.
- Mode 2 (digit oracle) is exact by block inversion.
- Finite-rank consistency at depth needs composite sampling, not
  atom sampling.


## Files

| file | role |
|---|---|
| `hardy_echo.py` | the tool |
| `DEEP-TROUBLE-No-4.md` | brief |
| `HARDY-ECHO-RESULTS.md` | this document |
| `exp1_deep_vs_prefix_rle.png` | Mode 1 RLE comparison |
| `exp1_summary.txt` | numeric report |
| `exp2_boundary_stitch.png` | Mode 1 + 4 boundary-stitch image |
| `exp2_summary.txt` | barcode rate report + destroyer note |
| `exp3_block_boundary.csv` | Mode 3 block counts |
| `exp4_digit_oracle.csv` | Mode 2 oracle vs ground truth |
| `exp5_finite_rank_consistency.csv` | atoms-only Q_n=1 sanity |


## Next moves

1. **Mode 4 destroyer taxonomy.** Add three named destroyers:
   `entry_shuffle` (current), `bit_within_entry_shuffle` (algebra-
   side), `digit_class_shuffle` (block-side). Each observable
   declares which destroyers apply.
2. **Composite-sample Q test.** Verify `Q_n(p_{K_1}(n) · p_{K_2}(n))`
   against the closed form at deep `K_i`. This is the actual
   self-consistency loop the speculation section claims.
3. **Push Mode 3 to large d.** Test BLOCK-UNIFORMITY at d=20,
   d=50 for n=2; d=20 for n=5, n=10 (smooth). One parameter
   change.
