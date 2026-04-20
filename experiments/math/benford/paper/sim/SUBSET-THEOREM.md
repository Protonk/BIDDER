# SUBSET-THEOREM

## What this document is

A rigorous work-up of the argument "does restricting the
step-set of a random walk ever speed up mixing?" as it applies
to comparing BS(1,2) (red) and alternating-mul-add (purple) on
the mantissa circle. Not paper-ready prose; a record for
ourselves of what is and isn't a theorem, so we don't accidentally
overclaim in the paper.

## Setup

Let `G` be a group (or general state space) and let `μ` be a
probability measure on `G` with finite support `S = supp(μ)`.
The random walk driven by `μ` is the Markov chain with transition
kernel

    P_μ(x, y) = Σ_{s ∈ S : xs = y} μ(s).

(In the state-space case, replace `xs` with whatever the step
action is.) Assume the chain has a unique stationary distribution
`π`; for symmetric `μ` on a group, `π` is left-invariant under
`G`-translation and is uniform on `G` if `G` is finite, or
Haar-type if `G` is locally compact.

Given a subset `A ⊆ S` with `μ(A) > 0`, define the **sub-sampled
measure**

    μ'(s) = μ(s) / μ(A)     for s ∈ A
           = 0               otherwise.

Write `P_μ'` for the Markov chain kernel driven by `μ'`. Both
chains are on the same state space.

## The theorem

**Theorem (Dirichlet-form comparison for sub-sampled walks).**
Assume both `P_μ` and `P_μ'` are reversible with the same
stationary distribution `π`. Then

    gap(P_μ)  ≥  μ(A) · gap(P_μ'),

where `gap(P) = 1 − λ₂(P)` is the spectral gap of `P` (i.e., `1`
minus the second-largest eigenvalue in absolute value).

Equivalently, the sub-sampled walk can mix **at most `1/μ(A)`
times faster** than the full walk in the spectral-gap sense. The
reverse direction — a direct bound "`P_μ` mixes at least `1/μ(A)`
times faster than `P_μ'`" — is **not** a theorem and can fail
(see below).

## Proof

The Dirichlet form for any reversible kernel `P` with stationary
`π` is

    E_P(f, f) = (1/2) Σ_{x,y ∈ G} π(x) P(x, y) (f(x) − f(y))².

The spectral gap equals the infimum of `E_P(f, f)` over
functions `f : G → ℝ` with `Var_π(f) = 1`:

    gap(P) = inf { E_P(f, f) : Var_π(f) = 1 }.

**Step 1: Pointwise domination of the kernel.** For any `x ≠ y`,

    P_μ(x, y) = Σ_{s ∈ S : xs = y} μ(s)
             ≥ Σ_{s ∈ A : xs = y} μ(s)                      (drop terms with s ∉ A)
             = μ(A) · Σ_{s ∈ A : xs = y} (μ(s) / μ(A))
             = μ(A) · P_μ'(x, y).

So `P_μ(x, y) ≥ μ(A) · P_μ'(x, y)` for every `x ≠ y`, pointwise.

**Step 2: Lift to the Dirichlet form.** For any fixed `f`,

    E_{P_μ}(f, f) = (1/2) Σ_{x,y} π(x) P_μ(x, y) (f(x) − f(y))²
                 ≥ (1/2) Σ_{x,y} π(x) · μ(A) · P_μ'(x, y) · (f(x) − f(y))²
                 = μ(A) · E_{P_μ'}(f, f).

**Step 3: Take inf over `f` with `Var_π(f) = 1`.**

    gap(P_μ) = inf E_{P_μ}(f, f)
            ≥ inf μ(A) · E_{P_μ'}(f, f)
            = μ(A) · gap(P_μ').        ∎

## Interpretation

The theorem says the two spectral gaps are within a factor of
`1/μ(A)` of each other. Translating to mixing times (which scale
inversely with gap), this gives

    τ_mix(P_μ')  ≥  μ(A) · τ_mix(P_μ),

equivalently

    τ_mix(P_μ) / τ_mix(P_μ')  ≤  1 / μ(A).

The sub-sampled walk `μ'` is **at most `1/μ(A)` times faster**
than `μ`. It is **not** required to be slower.

## Where the naive "sub-sampling always slows" claim fails

The theorem bounds the ratio but does not orient it. There is no
general result that `μ'` is slower than `μ`. Two counterexamples:

**Lazy-walk counterexample.** Take `G = ℤ/2` and let `μ` put mass
`1/2` on the non-trivial generator and mass `1/2` on the identity.
This is a "lazy" walk that stays put with probability 1/2 each
step. Let `A = {non-identity}`, so `μ'` is the **deterministic
non-lazy walk** (moves with probability 1 each step). The non-lazy
walk mixes in one step; the lazy walk takes two steps on average.
**Sub-sampling sped mixing up by 2×.** This is the extreme case of
`μ(A) = 1/2` in the theorem's bound.

**Bottleneck counterexample.** Take `G` to be a "barbell" — two
cliques joined by a narrow bridge — with `μ` uniform on all edges.
The full walk mixes slowly because of the bottleneck (it takes a
long time to cross the bridge). Restrict to edges *within one
clique* — `μ'` is now a walk on a complete graph, which mixes in
constant time. **Sub-sampling sped mixing up dramatically**
because the sub-sampled walk lives on a faster-mixing subgraph.

So the claim "sub-sampling cannot speed mixing" is false. What's
true is the **two-sided, bounded** comparison of the theorem
above.

## When does the naive intuition hold?

The naive claim "`μ'` is slower than `μ`" holds when the
**complement** measure `μ|_{A^c}` (re-normalized) is not on its
own a **worse** walk than `μ|_A`. Roughly: the `A^c` part should
be making some positive contribution to mixing, not just dead
weight or a trap.

More formally, consider the decomposition

    μ = μ(A) · μ' + μ(A^c) · μ'',

where `μ''` is the normalized restriction to `A^c`. Then

    P_μ  =  μ(A) · P_μ' + μ(A^c) · P_μ''.

So `P_μ` is a **convex combination** of `P_μ'` and `P_μ''`. If
`P_μ''` has **worse** mixing properties than `P_μ'` (e.g.,
mostly identity, or mostly looping), then mixing `P_μ'` with it
under convex combination gives a slower chain — so `P_μ` is
slower than `P_μ'` and sub-sampling **speeds** things up. If
instead `P_μ''` has **better** mixing properties than `P_μ'` —
which happens when `μ'` is restrictive in a way that loses
productive structure — then sub-sampling **slows** things down.

For concrete BS(1,2) / alternating, both μ' (the {a, a⁻¹}-part)
and μ'' (the {b, b⁻¹}-part) are genuinely useful for mixing on
their own, but the b-part is more productive than the a-part
because of the `bab⁻¹ = a²` relation. So restricting to
alternating forces purple to use the less-productive pairs only,
which slightly slows mixing. Quantitatively: the step-buddies
run measures purple about **1.15×** slower than red at matched
walker counts and matched relative-floor thresholds (see
§Application below and `step_buddies_SUMMARY.md`). The relevant
theorem bound is the factor-of-4 ceiling from the 2-step
reduction below, not a 2× bound — the 2× bound would apply only
if purple were a direct time-homogeneous sub-sampling of red,
which it isn't.

## Application: BS(1,2) red vs alternating purple

Strictly, purple is not a sub-sampling of red in the theorem's
sense — purple is **time-inhomogeneous** (odd-step measure differs
from even-step measure), whereas the theorem addresses a
time-homogeneous `μ'`. To apply the theorem we have to pass to
the 2-step walk.

**Two-step reduction.** Let `μ_red^{*2}` denote the 2-step
convolution of red's single-step measure; similarly for purple.
Then:

- `μ_red^{*2}` is supported on all 16 ordered pairs of generators
  from {a, a⁻¹, b, b⁻¹}, with equal weight 1/16 each.
- `μ_purple^{*2}` is supported on the 4 mul-then-add pairs
  {(a,b), (a,b⁻¹), (a⁻¹,b), (a⁻¹,b⁻¹)}, with equal weight 1/4
  each.

So `μ_purple^{*2}` is a sub-sampling of `μ_red^{*2}` onto the
4-element subset `A = {(a,b), (a,b⁻¹), (a⁻¹,b), (a⁻¹,b⁻¹)}`
with `μ_red^{*2}(A) = 4/16 = 1/4`.

Applying the theorem to the 2-step walks:

    gap(P_{μ_red^{*2}})  ≥  (1/4) · gap(P_{μ_purple^{*2}}).

In terms of single-step mixing time,

    τ_mix(purple) / τ_mix(red)  ≤  1 / (1/4)  =  4

when comparing at the 2-step granularity. (The 2-step bound is
looser than a single-step bound would be because we've "paid the
price" of reducing over two steps.)

**Empirical slowdown.** Measured via the step-buddies run
(`run_step_buddies.py`, 2026-04-19; results in
`step_buddies_SUMMARY.md`): at matched walker counts `N` and at
thresholds `θ_k = k · θ_N(N)` for `k ∈ {5, 3, 2, 1.2}`, the
ratio `n_purple(θ_k) / n_red(θ_k)` is consistently in the range
**1.10 to 1.22** across `N ∈ {10⁴, 10⁵, 10⁶, 10⁷}` — i.e., purple
takes about **1.15× as many steps** as red to reach the same
fractional depth above floor. Stable within ±10% across both `N`
and `k`.

Well within the theorem's factor-of-4 ceiling (<30% of the
allowance). The tight ratio band means the walk-on-walk slowdown
is essentially a single constant for the measurable regime, not
a k-dependent or N-dependent function.

**Historical note.** An earlier "~1.5×" number appears in some
of our records. The actual source, verified by direct
recomputation from the saved `.npz` arrays: purple at `N = 10⁶`
hits its own noise floor `θ_N(10⁶) ≈ 0.0272` at about `n = 181`,
while red (from M1 at `N = 10⁸`) hits **that same absolute
threshold** 0.0272 at about `n = 127`. The ratio 181 / 127 ≈
1.43, which is what "1.5×" was rounding. This is a **cross-`N`
same-threshold** comparison — purple is at its own plateau,
red is still in mid-descent at a much-higher-relative-to-floor
point — so it over-states the structural slowdown by a factor
reflecting the sampling-noise-floor difference between the two
runs, not just the walks' dynamics.

The matched-`N` matched-relative-threshold measurement (step-
buddies run, same N for both walks, same `k · θ_N` threshold)
gives ~1.15×. That is the correct empirical claim. The "1.5×"
number should not be cited as a slowdown; it conflates the
measurement setups.

The factor ~1.15× is determined by how productive the excluded
step-pairs (same-type ones like `a²` and reverse-order ones like
`(b, a)`) are relative to purple's allowed (mul, add) pairs. For
BS(1,2), the excluded pairs are only slightly more productive on
average than the allowed ones, because the group's relation
`bab⁻¹ = a²` means the two step orderings are not independent
but tightly coupled — a modest effect, consistent with a modest
measured slowdown.

## What the paper can cite

The theorem above can be referenced cleanly:

- "Restricting a random-walk step measure to a sub-set can at
  most change mixing times by a factor of `1/μ(A)`" — this is
  the theorem, citable as a Dirichlet-form comparison.
- "The alternating walk on BS(1,2) is at most 4× faster or
  slower than the full walk in spectral-gap sense, and measured
  empirically to be about 1.15× slower at matched walker counts
  and matched relative-floor thresholds across `N ∈ {10⁴..10⁷}`"
  — this is the application.

**What the paper should NOT say:**

- "Sub-sampling cannot speed mixing" — not a theorem; false in
  general.
- "Purple is strictly slower than red" — only empirically true
  at the level of our L₁ statistic, not provable as a general
  mixing-time ordering.
- "The alternating walk fails to converge" — it does converge;
  just at a bounded-factor slower rate than the full walk.

## One-sentence takeaway for ourselves

"Restricting the step set gives a walk whose spectral gap is
bounded (two-sidedly) within a factor of `1/μ(A)` of the full
walk's gap; for BS(1,2) with `A = {mul-then-add pairs}`, that
factor is at most 4, and empirically about 1.15×, stable across
walker counts 10⁴–10⁷ and threshold depths 1.2× to 5× above
noise floor."

## Open questions we parked

- Is there a stronger bound than the Dirichlet-form `1/μ(A)` for
  walks on amenable groups like BS(1,2)? (Plausibly yes, via more
  refined spectral-theory arguments on the von Neumann algebra.
  Not pursued here.)
- How does the bound interact with the L₁ statistic specifically,
  versus spectral-gap / TV mixing time? (The measured ~1.15× is
  in the L₁-hit-time sense at matched-relative thresholds, not a
  spectral-gap measurement. These should be comparable up to
  polylogarithmic factors, but we haven't worked that out.)
- Does the bound extend to the time-inhomogeneous purple walk
  directly without passing to the 2-step reduction? (Probably yes
  via time-averaged Dirichlet forms, but again not pursued.)
