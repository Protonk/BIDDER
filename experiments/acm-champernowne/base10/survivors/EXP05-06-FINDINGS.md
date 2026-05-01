# EXP05 + EXP06 — survival rate phase diagram and prime convergence

Two follow-ups on the survivors construction. Both yielded
unexpected results that change how we should think about the
bundle/survivor pair.

## EXP05 — survival rate κ vs leading-digit gap

**Hypothesis going in.** The triangular fingers in the L1-gap
heatmap are projections through a leading-digit lens of structure
that lives in the underlying set-membership object κ = |Surv|/|Bundle|.

**Result.** **The triangles are NOT in κ.** The κ heatmap is
essentially smooth: a monotonic gradient from κ = 1 (top-left, no
collisions) to κ ≈ 0.37 (bottom-right, maximum collisions in the
scanned window). No fingers, no triangles, no fine structure
visible at the global colour scale.

**The triangles are in the leading-digit projection itself.**

Quantitative correlation: `(1 - κ)` vs `|gap|`: **+0.57**. Moderate
positive — more culling tends to give bigger gap. But the *spatial
structure* (fingers, sharp triangles) lives in the gap, not in
the underlying set-membership.

**Mechanistic interpretation, revised.** The pair-collision impulse
mechanism from EXP03 is still right about *what is culled when* —
that's clean in the κ heatmap as a smooth gradient. The triangles
in gap arise because pair collisions cull integers whose values
cluster near specific magnitudes (`K · n_0 ≈ n_0²` for the
gcd=1 pair-cluster), and integers in a narrow magnitude range have
correlated leading digits. So a large simultaneous cull at
`K ≈ n_0` produces a localised leading-digit imbalance — the
"impulse." The smooth κ-gradient says "X% of atoms are gone";
the triangle structure in gap says "the X% that are gone had
correlated leading digits."

**Consequence.** Anyone reading the original gap heatmap as
revealing intrinsic phase structure of the survivor set was
seeing two things superposed: the smooth κ-decline (the genuine
structure) and the leading-digit clustering at decadal positions
(the lens-induced fingers). The triangles are real, but they're
lens artefacts, not substrate.

## EXP06 — survivor → prime convergence?

**Hypothesis going in.** Every prime in `[n_0, n_1]` is always a
survivor (no other stream can claim it). So as W = `n_1 - n_0 + 1`
grows at fixed `n_0`, `K`, the survivor set should converge to
"primes in window plus a thinning composite tail."

**Result.** Not what happens at finite `K`. At any `K` we tested,
**composite survivors grow with W**, not decay. There is a
striking dip at `W ≈ K`, after which the count rebounds and
continues to grow.

| `(K, n_0)` | composite survivors @ W=1 | dip min | @ W = 250 |
|-----|------|--------|--------|
| (50, 2)   | 49 | ~150 at W ≈ 50  | 2467 |
| (50, 50)  | 49 | ~600 at W ≈ 5   | 3163 |
| (200, 2)  | 199 | ~? at W ≈ 200 | 4167 |
| (200, 50) | 199 | ~? at W ≈ 150 | 7913 |

**Explanation of the dip at `W ≈ K`.** The "last" pair-collision
threshold for window `[n_0, n_0 + W - 1]` is `K_pair(n_0, n_1)
≈ n_1 = n_0 + W - 1`. When `K` equals this threshold, all gcd=1
pairs in the window simultaneously activate — the EXP03 impulse,
but now expressed as a brutal one-shot cull of composites in the
specific magnitude range `K · n_0 ≈ K²`. At W slightly past
`K - n_0`, ~93% of composites die in this wave (κ = 0.066 at the
dip bottom for K=50, n_0=2). Then as W grows further, the bundle's
integer range extends to higher magnitudes and new composites
(with fewer divisors in window) enter the survivor set.

**Why the rebound has no apparent ceiling.** The bundle's integer
range scales roughly as `K · n_1 = K · (n_0 + W - 1)`. As W grows,
new integer territory opens at the high end. Composites in that
territory have potentially many divisors in the window, but if
their smallest divisor `≥ n_0` is unique (e.g., semiprime `c = pq`
with `p < n_0 ≤ q`, certain prime powers `p^k`), they survive.
The density of such "uniquely-claimed" composites doesn't decay
to zero as the bundle's range grows.

**The original convergence-to-primes intuition was wrong at
finite `K`.** It would be correct in a regime where `K` grows with
`W` — say `K = K(W)` such that for every composite `c` in bundle
range, the position-of-`c` in some stream falls within `K`. With
`K` fixed, only "early" atoms of each stream are visible, and
composites that fail to appear early in multiple streams are
permanent survivors.

**Survivor/prime ratio.** Empirical at W = 250:
- (K=50, n_0=2): |Surv|/π_window = 2521/54 ≈ **47**
- (K=200, n_0=50): |Surv|/π_window = 7960/47 ≈ **169**

The survivors are dominated by composites by 1.5–2 orders of
magnitude. Convergence to primes is not the right framing for this
observable at finite K.

## Combined takeaway

The two experiments together change the picture:

- **κ is the right substrate; gap is a derived projection.** The
  EXP03 "pair-collision impulse" mechanism explains κ cleanly
  (impulse → step-down in κ at each `K_pair`). It explains gap
  via the additional fact that culled integers have correlated
  leading digits.

- **Survivors are not "almost-primes."** At any finite K, they're
  a mix dominated by composites, with the prime fraction
  controlled by the K/W ratio. Real prime convergence requires
  K growing alongside W.

- **The dip at `W ≈ K`** is a single coherent collision wave
  predicted exactly by the EXP03 mechanism: when the "last" pair
  in the window first activates, ~30 pairs (gcd=1 ones) activate
  near-simultaneously, killing the bulk of the bundle's
  composites.

## What's worth running next

- **κ on log/derivative scale.** The smooth κ surface might
  hide the lattice in a derivative — `∂κ/∂K` should show
  step-functions at each `K_pair`, even though κ itself looks
  smooth. Could give the cleanest possible visualization of the
  collision lattice.

- **K = K(W) joint sweep.** The right convergence question is:
  for `K(W) = α · W^β`, which `(α, β)` make survivors actually
  converge to primes? The EXP03 mechanism suggests you need
  `K` growing fast enough that all composites' first-stream
  appearances fall within `K`. For c = pq, the position is
  `q/gcd(p,q) ≈ q`. So `K ≥ max divisor in window` is required.
  Try `K = W` (one prediction) or `K = W · n_0 / 2` (another).

  **→ Resolved in EXP14** (`EXP14-FINDINGS.md`): no scaling works.
  The natural threshold `K = n_0 + W − 1` kills Type-A composites
  but leaves a `T_B_low` residue (composites with one window-
  divisor and a cofactor below `n_0`) that is **structurally
  irremovable** — only one window-stream contains them, so they
  cannot be culled by collision at any `K`. Asymptotically
  `|T_B_low| ~ W · n_0 / log n_0`, dominating the survivor set
  and forcing the prime fraction to `~ log n_0 / n_0 → 0`.
  Convergence to primes-in-window is impossible at any finite
  `K` with this construction; it would require expanding the
  stream collection to `{S_n : n ∈ [2, n_0 + W − 1]}`, a
  different (sliding-prefix, not sliding-window) object.
