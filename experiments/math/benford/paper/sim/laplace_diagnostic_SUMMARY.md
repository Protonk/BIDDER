# Laplace diagnostic — MESSES.md §1 informed by sim

Probes the Laplace-transform obstruction from MESSES.md Mess #1.
Two sims: simple random walk (SRW) on ℤ as a textbook baseline,
and BS(1,2) with a no-freeze kernel to keep the E-process honest.

Run: `run_laplace_diagnostic.py`.
Analysis: `analyze_laplace_diagnostic.py`.
Data: `laplace_diagnostic_results/`.
Date: 2026-04-19.

## Part A: SRW on ℤ validates Mess #1's closed-form prediction

N = 10⁶ walkers, n up to 10⁴, q ∈ {0.3, 0.5, 0.7, 0.9}.

| q   | slope log(E[q^{L_n}]) vs log(n) | ratio meas/pred at n = 10⁴ |
|:---:|:-------------------------------:|:--------------------------:|
| 0.3 | −0.502                          | 0.998                      |
| 0.5 | −0.501                          | 0.999                      |
| 0.7 | −0.499                          | 0.998                      |
| 0.9 | −0.471                          | 0.990                      |

Measured E[q^{L_n}] converges to the closed-form prediction
q√2 / ((1 − q)√(πn)) to within 0.2% at large n for q ∈ {0.3, 0.5,
0.7}. The q = 0.9 slope is preasymptotic (subleading corrections
are larger when q is close to 1). Slope of log(E[q^{N_n}]) vs
log(n) matches −0.5 with the same precision.

L_n/√n distribution at n = 10⁴ has mean 0.798 and std 0.596,
matching the predicted half-normal limit (mean √(2/π) ≈ 0.798,
std √(1 − 2/π) ≈ 0.603). The universality-class story in
Mess #1 is quantitatively correct for SRW.

**Implication for Mess #1:** the Laplace obstruction — that
E[q^{L_n}] for null-recurrent walks decays only algebraically as
1/√n, not stretched-exponentially — is verified on the textbook
case. The obstruction is real, not an artifact of the
generating-function calculation.

## Part B: BS(1,2) is not in the SRW universality class

Same setup, BS(1,2) walker from x = √2, R = {|E| ≤ 10}, modified
kernel that skips b-steps for |E| > 20 (physically correct: b-step
changes log|x| by O(1/|x|) when |x| is large).

### E-process is not zero-drift

| n    | E mean | E std | E median | frac E > 0 | frac E < 0 |
|:----:|:------:|:-----:|:--------:|:----------:|:----------:|
| 100  | 1.02   | 1.41  | 1.0      | 0.593      | 0.106      |
| 1000 | 4.71   | 4.10  | 4.0      | 0.864      | 0.034      |
| 10⁴  | 16.31  | 12.84 | 14.0     | 0.957      | 0.011      |

Mean(E) grows as ~0.16 · √n; std grows as ~0.13 · √n. Both scale
as √n, so E is _not_ bounded, but the walker has a persistent
upward bias — at n = 10⁴, only 1.1% of walkers have E < 0.

**Why:** b-steps near |x| = 0 (i.e. large negative E) cause a
snap-back to E near zero — x = 10⁻⁵ + 1 ≈ 1 has log ≈ 0. At
|x| >> 1 (positive E), b-steps are no-ops. This gives an
effective "reflecting barrier" near E = 0 on the negative side
and free random-walk behavior on the positive side. The
resulting E-process looks like a random walk reflected at 0,
with positive mean growing as √n.

The claim in Mess #1 — "it is a zero-drift martingale with
bounded increments, so its local-time statistics at {|E| ≤ E₀}
are in the same universality class [as SRW]" — is not supported
by the sim. The E-process has state-dependent drift that breaks
the zero-drift assumption.

### L_n grows linearly, not as √n

| n    | ⟨L_n⟩    | ⟨L_n⟩/n | ⟨N_returns⟩ | frac in R |
|:----:|:--------:|:-------:|:-----------:|:---------:|
| 100  | 101      | 1.00    | 0.00        | 1.000     |
| 1000 | 1000     | 1.00    | 0.03        | 0.902     |
| 10⁴  | 5995     | 0.60    | 26.7        | 0.400     |

L_n is O(n), not O(√n). Walkers spend a macroscopic fraction of
time in R, consistent with reflecting-at-0 behavior on the
E-process. This is qualitatively different from SRW's L_n ~ √n.

### E[q^{L_n}] does not follow 1/√n

For q ∈ {0.3, 0.5, 0.7}, E[q^{L_n}] decays very fast initially
(tracking q^L with L growing linearly), then plateaus at a small
positive value (dominated by the 60% of walkers who escape R by
n = 10⁴ and stop accumulating L). For q = 0.9, the decay slope
is −0.46 — close to SRW's −0.50 but over a much narrower regime.

The "null-recurrent → 1/√n" prediction does _not_ describe the
BS(1,2) E[q^{L_n}] behavior. Neither does stretched-exp, nor
straight exponential. The actual behavior is a transient
exp(−cn)-like decay followed by a plateau — a distinct mechanism.

## What this informs about the three frameworks

Mess #1 raises two options:

> (a) a finite-time transient that has not yet relaxed to the
>     asymptotic algebraic regime, or
> (b) produced by a mechanism not captured by the per-return
>     spectral-gap framework.

The sim does not decide (a) vs (b) directly (it measures L_n,
not φ). What it does show is that the universality-class
justification for treating BS(1,2)'s local time as SRW's local
time is **empirically off**. The E-process has a strong positive
drift and L_n scales linearly with n, neither of which is in the
framework Mess #1 invoked.

Two implications:

1. **Mess #1's conclusion weakens but doesn't evaporate.** The
   closed-form 1/√n obstruction is a theorem about null-recurrent
   walks (verified on SRW). If BS(1,2)'s E-process is not in that
   regime, the obstruction does not necessarily apply. That's not
   the "the Laplace route works" outcome — it's a "we need a
   different analysis" outcome. The per-return framework is still
   ill-suited to BS(1,2), but not for the reasons Mess #1 gave.

2. **The per-step framework also fails on different grounds than
   the Mess noted.** Mess #1 notes the per-step framework's bound
   was `exp(−β·E[L_n]) ≤ exp(−β·c_R·√n)` assuming E[L_n] ~ √n.
   Sim shows E[L_n] ~ n for BS(1,2), so that bound would give
   straight exponential — stronger than stretched-exp. But the
   measured φ(ν, n) decays as stretched-exp ~ exp(−0.55√n), not
   as exp(−cn). So the per-step bound is actually loose, not
   tight. The observed stretched-exp has a mechanism that's
   intermediate between linear-L_n bound and √n-L_n bound —
   still not identified.

## Where this leaves the proof architecture

- **SRW validation:** Mess #1's computation is correct for
  textbook null-recurrent walks. No sim bug, no artifact.
- **BS(1,2) specifics:** the E-process has structure that
  neither Mess #1's per-return argument nor the (withdrawn)
  GAP2-LEMMA per-step argument captures correctly. The actual
  mechanism driving φ(ν, n) ~ exp(−0.55√n) remains unidentified
  by both frameworks.
- **Mess #1's status:** still open — the Laplace route can't
  deliver stretched-exp. But the SPECIFIC reason ("E is
  null-recurrent SRW, so 1/√n obstruction applies verbatim") is
  not the right reason. BS(1,2) has its own structure.
- **New question raised:** what _is_ driving φ's stretched-exp
  decay in BS(1,2), given the E-process isn't null-recurrent?
  Likely answer (not tested): the mantissa-projection's
  contraction is not governed by L_n at all; it's governed by
  the number of "effective rotations" (a-steps) the walker has
  taken, which grows linearly with n, giving a walker-level
  decay rate. The √n shape in φ might come from E-fluctuations
  around the drifting mean creating a distribution of "effective
  mantissa rotation counts" with √n-scale variance.

That last is a hypothesis, not a result. Testing it would
require measuring the mantissa TV decay conditional on a-count
bins — separate sim.

## What's saved

- `laplace_diagnostic_results/srw_z.npz` — SRW on ℤ, sample
  times, E[q^L], E[q^N], L/N snapshots at n ∈ {100, 300, 1000,
  3000, 10000}.
- `laplace_diagnostic_results/bs12.npz` — BS(1,2), same structure
  plus E snapshots.

## What's not done

- Conditional φ decay given a-step count or E-excursion depth.
  Would test the "effective rotation count" hypothesis above.
- Longer-n sims to see if E[q^{L_n}] for BS(1,2) eventually
  settles into a clear asymptotic form.
- Higher-N runs to tighten the q = 0.9 slope measurement (or
  push to q → 1 regime where subleading corrections matter).
