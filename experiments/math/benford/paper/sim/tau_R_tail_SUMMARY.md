# τ_R tail — empirical survival is ≈ 1/√n

Mess #3 warns that FIRST-PROOF §2 (R2)'s Feller-continuity
argument for T_R invokes a "uniform geometric tail bound on τ_R
from x ∈ R," while the walk is null-recurrent-like and should
have only polynomial tail decay. This sim measures P(τ_R > n)
directly on the paper's BS(1,2) kernel.

Run: `run_tau_R_tail.py`.
Analysis: `analyze_tau_R_tail.py`.
Data: `tau_R_tail_results/tau_R_tail.npz`.
Date: 2026-04-19.

**Headline:** The first-excursion survival follows
P(τ_R > n) ~ C · n^{-0.495} cleanly over n ∈ [50, 10000] with
R² = 1.0000. Effectively **P(τ_R > n) ~ 1/√n** — the textbook
null-recurrent tail, not the geometric tail the sketch invokes.

## Setup

- N = 10⁶ walkers, BS(1,2) paper kernel, IC x = √2.
- n_max = 30000.
- R = {|E| ≤ 10}.
- Per walker: record first-exit time, first-return time, and
  (via on-the-fly histogram) all subsequent excursion durations.
- Ongoing excursions at n_max recorded as censored samples.

## Headline measurements

Walker-level accounting at n = 30000:

| quantity                               | count     | frac    |
|:---------------------------------------|:---------:|:-------:|
| walkers with first exit and first return | 993,021 | 99.30%  |
| walkers with first exit, no first return | 6,977   | 0.70%   |
| walkers that never exited              | 2         | ~0%     |
| walkers currently out of R at n_max    | 760,948   | 76.10%  |
| total completed excursions (pooled)    | 64.78M    |         |

On average each walker completed ~65 excursions by n = 30000.

## First-excursion survival S(n) = P(τ_R > n)

Conditioning on walkers with at least a first exit (essentially
all 10⁶):

| n      | S(n)       |
|:------:|:----------:|
| 50     | 1.58 × 10⁻¹ |
| 100    | 1.11 × 10⁻¹ |
| 1,000  | 3.26 × 10⁻² |
| 10,000 | 1.12 × 10⁻² |
| 30,000 | 6.98 × 10⁻³ |

Power-law fit on n ∈ [50, 10000]:

    slope = −0.495,   R² = 1.0000,   15 grid points.

SRW reference slope for null-recurrent return: **−0.5**. The
measured slope agrees to two decimals.

Beyond the fit range, S(30000) = 6.98 × 10⁻³ vs predicted
S(30000) ≈ C · 30000^{−0.5} extrapolated from S(10000) = 0.0112:
   predicted = 0.0112 · √(10000/30000) = 0.0112 · 0.577 = 0.00647
   measured  = 0.00698
Within 8% — consistent with the power law continuing to n = 30000.

Taken at face value, this is the cleanest possible form of the
null-recurrent tail on the BS(1,2) return time: leading order
1/√n, no visible asymptotic plateau at 30000, and a quality of
fit that rules out sub-power tails (stretched-exp or
exponential).

## Pooled-excursion survival (biased)

All 64.78M completed excursions (including subsequent visits),
with survival vs duration:

| n      | S_all(n)   | S_post-first(n) |
|:------:|:----------:|:---------------:|
| 50     | 1.49 × 10⁻¹ | 1.49 × 10⁻¹ |
| 100    | 1.01 × 10⁻¹ | 1.01 × 10⁻¹ |
| 1,000  | 2.19 × 10⁻² | 2.18 × 10⁻² |
| 10,000 | 2.26 × 10⁻³ | 2.23 × 10⁻³ |
| 30,000 | ≈ 0         | ≈ 0         |

Power-law fit on n ∈ [50, 10000]: slope = **−0.697**, R² = 0.985.

The pooled distribution decays _faster_ than first-excursion's
1/√n. This is a length-biasing artifact: walkers with many short
excursions contribute many samples to the pool, pulling the
pooled distribution toward short durations. For this reason,
**the first-excursion survival is the right statistic** for
characterizing τ_R's tail as the induced-operator framework
would use it.

## Censored (ongoing) excursions

At n_max = 30000, 760,948 walkers are in the middle of an
excursion. Duration-so-far:

    min / median / mean / max = 0 / 10553 / 11911 / 29839

These are the walkers whose _current_ excursion is taking a long
time. They are distinct from the 0.7% that haven't had a first
return, and distinct from the 23.9% currently in R.

That the current excursion has median duration ~10500 while most
first-excursions return in 4 steps (median) reflects the
power-law tail: a walker cycling in and out many times will,
eventually, enter a rare long excursion, and such long excursions
dominate the current-excursion duration distribution.

## What this means for Mess #3

The Mess identifies the qualitative mismatch: FIRST-PROOF §2's
sketch invokes a "uniform geometric tail bound" while the walk's
actual return times are heavy-tailed. This sim provides the
quantitative picture:

1. **The tail is polynomial with exponent −0.5**, confirming
   the null-recurrent framing in Mess #3 and refuting the
   geometric-tail sketch in FIRST-PROOF §2 R2.

2. **The exponent is exactly 1/2 (empirically).** This is the
   best-behaved polynomial tail: it matches the exponent for
   simple-random-walk return times in 1D, and it fits the
   Melbourne-Terhesiu / Gouëzel / Sarig framework for induced
   operators with tail P(τ > n) ~ C/n^α (α = 1/2 here) giving
   polynomial correlation decay O(1/n^{1−α}) = O(1/√n).

3. **This is aligned with T1b.** The paper's asymptotic shape is
   1/√n. The polynomial-tail induced-operator theory _delivers_
   1/√n decay natively. The right proof architecture for T1b is
   the polynomial-tail framework from that literature, not the
   geometric-tail + stretched-exp framework in Route 1'.

4. **Route 1' needs to be rewritten.** The current sketch's R2
   appeals to truncation + uniform geometric convergence. The
   correct framework is: induced operator with polynomial return
   tail, apply Melbourne-Terhesiu / Gouëzel machinery, get
   polynomial decay. This is a structural rewrite, not a patch.

## What this does not show

- **P(τ_R = ∞) not pinned.** The survival S(n) at n = 30000 is
  6.98 × 10⁻³. Extrapolating 1/√n to n = ∞ gives S(∞) = 0, i.e.
  P(τ_R = ∞) = 0 (walker almost surely returns). But we don't
  have data at n > 30000 to verify the tail doesn't flatten. A
  longer sim or an analytic argument would settle this.
- **Uniformity in x ∈ R not tested.** The Feller-continuity
  argument would need the 1/√n tail to hold _uniformly_ for all
  starting points x ∈ R, not just the M1 IC. This sim tests one
  IC.
- **Exactness of 1/√n exponent vs some other exponent near 1/2.**
  The fit gives slope −0.495 with R² = 1.0000; we report this as
  ≈ 1/√n but haven't demonstrated the exponent is exactly 1/2 as
  opposed to (say) 0.495 or 0.5 + o(1) correction.

## Tying together with prior diagnostics

- **Laplace diagnostic** showed BS(1,2) has positive mean E-drift
  (mean E grows as 0.16√n). That observation seemed to put
  pressure on a "null-recurrent" framing, but this sim shows
  that _at the τ_R-tail level_ the walker IS null-recurrent-like
  (P(τ > n) ~ 1/√n). The positive E-drift coexists with 1/√n
  return-time tails: individual walkers return almost surely
  but with heavy-tailed return times; the mean position grows
  because a small fraction is far from R at any given time.
- **Return-marginal** sim showed pooled post-burn σ̃ concentrated
  on arc [1 − log₁₀ 2, 1). That's the distribution of
  _entry-state's m_, not the distribution of τ_R itself. Both
  results can coexist: τ_R has 1/√n tail; the walker returns
  via a⁻¹-with-borrow which puts m into the arc regardless of
  how long the excursion was.

## For FIRST-PROOF / PNAS-PLAN

The Mess #3 footnote should be updated:

- τ_R tail is polynomial, ≈ 1/√n empirically.
- FIRST-PROOF §2 R2's truncated-return-operator sketch assumes
  uniform geometric tail; that assumption is empirically wrong.
- The correct framework is the literature on induced operators
  with polynomial return-tail (Melbourne-Terhesiu, Gouëzel,
  Sarig, Young's tower constructions).
- The measured 1/√n polynomial tail is _compatible_ with T1b's
  claimed 1/√n asymptotic, via that literature's standard
  result that tail exponent α = 1/2 gives correlation decay
  O(1/n^{1 - α}) = O(1/√n).
- Proof-architecture consequence: Route 1' should be rewritten
  around polynomial-tail induced-operator theory rather than
  geometric-tail truncation. This may also soften or resolve
  Mess #1 (the Laplace obstruction), since the polynomial-tail
  framework gives the right asymptotic natively.

This is a _structural clarification_ of the proof gap, with the
encouraging feature that the measured tail exponent matches the
theorem's claimed asymptotic. The path to T1b through the
induced-operator theory is not a patch — it is a different
framework, and the current Route 1' sketch does not use it.

## What's saved

- `tau_R_tail_results/tau_R_tail.npz` — bin edges, duration
  histograms (all and post-first), first-exit/first-return
  per walker, censored ongoing-excursion durations.

## Caveats

- **IC-conditional fit.** The 1/√n slope is for first excursions
  from the M1 IC (x = √2). Subsequent excursions and other ICs
  not independently fit. The uniform-in-x claim needed for R2
  is not tested.
- **Finite horizon.** n_max = 30000 is large enough to see the
  1/√n tail over 2+ decades but not large enough to rule out
  deviation at much larger n.
- **Single value of E₀.** R = {|E| ≤ 10}. Different E₀ might
  show different tail exponents; not tested.

## Not done

- **Sweep of E₀.** E₀ ∈ {3, 5, 10, 20} to check whether the
  exponent is robust. Expected: yes, because the 1/√n arises
  from SRW-like E-drift variance.
- **Different ICs.** Uniform on T × {0}, m = 0 (sharp at
  integer boundary), etc., to probe the uniform-in-x-∈-R claim.
- **Longer n_max.** Probe whether the tail deviates from 1/√n
  at n > 30000, or whether P(τ_R = ∞) > 0.
- **Theoretical tail calculation.** The 1/√n shape is consistent
  with SRW-on-ℤ for the E-process. A direct derivation from the
  BS(1,2) generator structure would confirm exactness of 1/2.
