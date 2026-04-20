# F2-CONTRAST-SIM

Measuring the sub-sampling slowdown of "alternating" on groups
other than BS(1,2), to see how much of the BS(1,2) 1.15× figure
is group-specific. Primary comparison: `ℤ²` torus. Secondary
comparison: F_2 tree with the drift-rate observable.

## Scope revision

Two rounds of GPT5 review (2026-04-19) identified six
structural problems across earlier drafts. Revisions:

1. **Bipartite parity on the torus (even L).** Original draft's
   primary observable was L₁ to uniform on `L²` cells. With step
   set `{(±1, 0), (0, ±1)}` and even L, each step flips
   `(x + y) mod 2`, so walkers live on one parity class of size
   `L²/2` at every step — hence `L₁ ≥ 1` always. First fix:
   parity-conditioned L₁.

2. **Parity problem goes deeper for alternating (even L).** On
   even L, alternating has an additional conservation: at
   n ≡ 0 mod 4 walkers live on the `(even, even)` quarter-class
   of `L²/4` cells; at n ≡ 2 mod 4 they live on `(odd, odd)`;
   at odd n they live on mixed-parity quarters. So comparing
   alternating to uniform on a `L²/2` half-class *still* gives
   `L₁ ≥ 1`. **Second fix, and the correct one: use odd L.** On
   odd L, the torus ℤ/L has no bipartite structure (the cycle
   `0 → 1 → ... → L-1 → 0` is odd-length), so neither walk is
   support-restricted. Both walks converge to uniform on the
   full `L²` cells. No parity conditioning needed.

3. **Alternating is faster, not equal, on F_2.** Under strict
   parity alternation, consecutive letters are always of
   different type (`a`-type then `b`-type), so no free
   cancellation ever occurs: word length is deterministically
   `n`. Full walk has drift 1/2 (Kesten). So alternating has
   drift 1 vs full's 1/2 — **alternating takes half as many
   steps as full to reach any given word length on F_2** (time
   ratio `r = n_alt/n_full = 0.5`). Revised framing: Option B
   is an empirical witness to the lazy-walk speedup direction,
   not a neutral check.

4. **Can't isolate `bab⁻¹ = a²` with `ℤ²`.** Moving from BS(1,2)
   to the `ℤ²` torus changes five things at once. A result near
   1.0 on the torus would show "small alternation penalty on
   this proxy," not "the BS relation specifically causes the
   1.15×." Revised claim: this plan produces a *contrast*
   between groups, not an *isolation* of one relation's role.

5. **The commutator relation isn't mild.** `[a, b] = e`
   fundamentally changes cancellation and path counting. `ℤ²`
   is a different abelian group, not a minor perturbation of
   F_2.

6. **Unified direction convention.** Throughout this plan, the
   slowdown quantity is the **time ratio** `r = n_alt / n_full`
   at matched thresholds, as used in step-buddies: `r > 1` means
   alternating is slower; `r < 1` means faster. Drift rates
   (Option B) are reported but converted to the same time-ratio
   orientation for the summary table:

       r = drift_full / drift_alt   (since more drift ⇒ fewer steps)

   Under this convention, F_2's drift result `(drift_full,
   drift_alt) = (1/2, 1)` corresponds to `r = 0.5`.

With these revisions the plan produces useful data about how
sub-sampling slowdown varies across groups, without claiming to
isolate a single relation as the cause, and without the
periodic-support pathology that afflicted the earlier drafts.

## What we can actually learn

Three concrete empirical quantities, contrasted. Convention:
`r = n_alt / n_full` (time ratio at matched threshold); `r > 1`
means alternating slower, `r < 1` means alternating faster.

| walk / observable              | time ratio `r`      | source |
|:-------------------------------|:--------------------|:-------|
| BS(1,2) / L₁ to uniform on T   | ~1.15 (slowdown)    | step-buddies (measured) |
| ℤ² odd-L torus / L₁ to uniform | ?                   | this plan, Option A |
| F_2 tree / drift rate          | **0.5 (speedup)**   | this plan, Option B (predicted) |

The trio demonstrates that the sub-sampling penalty is
group-dependent: on BS(1,2) a modest slowdown, on F_2 a speedup,
and on `ℤ²` an outcome we will measure rather than assume. That
is the conversational take-away — not a causal claim about which
specific relation does what.

## Option A — ℤ² torus

### Setup

State: each walker is an `(x, y)` coordinate pair, `x, y ∈
{0, 1, ..., L-1}`, with wrap-around arithmetic.

Two walks, both from `(0, 0)`:

- **Full:** step uniform on `{(+1, 0), (-1, 0), (0, +1), (0, -1)}`.
- **Alternating:** odd step uniform on `{(+1, 0), (-1, 0)}`;
  even step uniform on `{(0, +1), (0, -1)}`. Stateless, using
  `step_index` parity.

### Observable (no parity conditioning needed on odd L)

On odd L, the torus ℤ/L × ℤ/L is not bipartite under the
`{(±1, 0), (0, ±1)}` step set. Both walks converge to uniform
on the full `L²` cells. No quarter-class or half-class
restrictions: walkers can occupy any cell at any sufficiently
large n.

Compute `L₁` relative to uniform on all `L²` cells at every
sample time: `L₁(P_n) = Σ_{cell} |freq_cell - 1/L²|`.

Sanity check: at very small `n`, both walks are still close to
the IC and have support only on a small neighborhood of `(0,0)`.
`L₁ ≈ 2 - 2·|support_n|/L²`, which is close to 2 while
`|support_n| ≪ L²`. Fine.

### Parameters

    L = 31 (odd prime; L² = 961 cells, comparable to earlier
        plan's 450-cell class at L=30)
    Walker counts: N ∈ {10⁵, 10⁶, 10⁷}
    One seed each (single-seed is adequate; ℤ² symmetry
        averages out per-walker variation quickly)
    n_max = 2000
    Sample: every 10 steps, n ∈ {10, 20, ..., 2000}

### Noise floor estimate

For `N` walkers on `M = L² = 961` cells, expected null-L₁ is
`≈ √(2M/(πN))`. At N = 10⁵: `≈ 0.078`. At N = 10⁶:
`≈ 0.025`. At N = 10⁷: `≈ 0.0078`. Enough headroom below the
initial `L₁ ≈ 2` to measure a convergence curve at every N.

### Analysis

Identical methodology to `analyze_step_buddies.py`: compute
`n(θ_k)` for `k ∈ {5, 3, 2, 1.2}` where `θ_k = k · θ_N(N)` is
measured against the full-torus noise floor. Tabulate `r(N, k) =
n_alt(θ_k) / n_full(θ_k)`.

### Expected outcome (honest prediction)

No strong prior. ℤ² is abelian and its walk factorizes in a
way BS(1,2)'s doesn't (see Option A notes below), so I'd guess
the ratio is close to 1 but have no theorem forcing it. **Plan
to run and report whatever comes out.**

Specific predictions are:

- `r ≈ 1.0`: consistent with "the slowdown penalty on BS(1,2) is
  specific to its non-abelian structure" — a softer version of
  the previous draft's claim.
- `r > 1.05` but `< 1.15`: the abelian structure helps but
  doesn't eliminate the penalty.
- `r ≈ 1.15` or higher: surprise; the 1.15× isn't BS(1,2)-
  specific and the alternation constraint itself is the
  primary cause. This would be a meaningful update to our
  theoretical framing.
- `r < 0.95`: alternation is faster on `ℤ²`, matching the F_2
  tree direction. Also informative.

## Option B — F_2 tree, drift rate

### Setup

Walkers are reduced words in `{a, a⁻¹, b, b⁻¹}*`. At each step,
append the chosen generator and free-reduce (pop both if the new
last two letters are inverses).

- **Full walk:** generator uniform on `{a, a⁻¹, b, b⁻¹}`.
- **Alternating:** odd-step generator uniform on `{a, a⁻¹}`;
  even-step uniform on `{b, b⁻¹}`. Stateless parity.

### Observable

Walker word length `|X_n|` at each time. Compute ensemble mean
`E[|X_n|]` and report its slope (drift rate).

### Parameters

    N = 10⁵ walkers
    n_max = 500
    Seed: single, deterministic
    Output: per-sample-time mean and std of |X_n|

### Prediction (algebraic)

- **Full walk:** drift 1/2 (Kesten result for 4-regular tree).
  `E[|X_n|] ≈ n/2` for large `n`.
- **Alternating:** drift 1 (no free cancellation possible
  because consecutive generators are always of different
  types). `E[|X_n|] = n` deterministically.

Converting to the time-ratio convention used throughout: at a
target word length `L`, `n_full(L) ≈ 2L` and `n_alt(L) = L`.
So `r = n_alt / n_full = 0.5`. Alternating is 2× faster on F_2
in the time-to-word-length sense.

This is the lazy-walk speedup from `sim/SUBSET-THEOREM.md`
manifesting concretely: full-walk's 2-step contains 25% identity
pairs (free cancellation of `a⁻¹a`, etc.); alternating's 2-step
contains 0% identity pairs (consecutive letters are always of
different type and thus can't cancel). Removing identity pairs
speeds things up.

### Decision rule

Option B's outcome is essentially predicted from Kesten's
theorem and free-reduction combinatorics. Running it
empirically is mostly a sanity check that our implementation
reproduces the drift values. If the empirical drift rates are
within ~5% of the predicted `(1/2, 1)`, the sim works. If not,
debug.

## Cost

Option A, `L = 31`, `n_max = 2000`, 3 (N, walk) pairs × 2 walks
= 6 runs. On the local M1, the `N = 10⁷` runs took about 258 s
(full) and 153 s (alternating); total torus runtime was about
7.6 min.

Option B: about 1 min. The implemented run uses the exact
word-length process directly, not literal reduced-word storage,
so memory is trivial.

**Total observed runtime on the local M1: about 8.5 min.**

## Connection to paper-level framing

If Option A gives `r ≈ 1.0`, the paper can carry a softened
footnote:

> The slowdown factor of alternating-step sub-sampling is
> group-dependent. On BS(1,2) we measure ~1.15×; on the related
> ℤ² torus walk, the same sub-sampling produces no measurable
> slowdown. This difference is consistent with the qualitative
> picture that sub-sampling penalties arise from non-trivial
> group relations that the alternation constraint forces the
> walk to exploit only partially, though isolating the
> `bab⁻¹ = a²` relation specifically as the cause would require
> more targeted controls.

If Option A gives `r` further from 1.0 (either direction), the
footnote becomes the measured value with an honest "group
structure matters in ways we don't fully characterize here"
caveat.

Option B's result, being essentially algebraic, goes into the
same footnote as a third data point:

> On the free group F_2 the corresponding alternation walk
> accelerates relative to the full walk (drift rate 2× the
> random-mix drift), because enforced type-alternation in a
> group with no cancellation relations eliminates backtracking
> entirely — the lazy-walk speedup mechanism. The direction of
> the sub-sampling penalty is not universal; its sign and
> magnitude are group-specific.

Three data points across three groups. Conversational story
intact, causal attribution appropriately softened.

## What this plan does NOT do

- Does not isolate the `bab⁻¹ = a²` relation as the specific
  cause of BS(1,2)'s 1.15× slowdown. That would require
  targeted controls we don't have.
- Does not make `ℤ²` a close proxy for F_2 — the commutator
  relation is structurally important, not a small perturbation.
- Does not claim a universal direction for sub-sampling
  penalties; the point of the plan is to show they are
  group-dependent.
- Does not produce a figure by default. The result is a three-
  row table of slowdown factors; if interesting enough we
  could add a panel to the step-buddies figure.

## Implementation outline

1. `run_f2_contrast_torus.py` — Option A, ~30 min coding.
   Inherits analysis structure from `run_step_buddies.py`.
2. `run_f2_contrast_tree.py` — Option B, ~30 min coding.
   Walker state is a list of ints (generator IDs, 0-3);
   free-reduce on append.
3. `analyze_f2_contrast.py` — combines Option A ratio analysis
   with Option B drift-rate fit. Reports the three-group
   summary table.
4. Summary doc once results are in, following the
   `step_buddies_SUMMARY.md` template.

No figure by default. If results land clean, consider adding to
the step-buddies figure as a fifth panel (or a separate
multi-panel-with-labeled-groups figure).
