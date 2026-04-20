# MESSES vs. sims — reconciliation

Internal working document. Maps the sim corpus onto the three open
MESSES and the claim gate. Assumes project vocabulary: Route 1',
T_R, ν_R, IC (b), T1a/T1b, θ_N, etc. Candid, not paper prose.

Scope: does the sim evidence speak to Mess #1 (rate conversion),
Mess #2 (target identification, WHERE), Mess #3 (operator
legitimacy, WHEN)? What does it pressure, support, or leave
untouched? Where is the proof architecture (Route 1' as sketched
in FIRST-PROOF §2) empirically licensed, and where is it running
on assumptions the sims actively undermine?

Date: 2026-04-19. Sources: MESSES.md; T1B-EVIDENCE-MAP.md;
tau_R_tail_SUMMARY.md; return_marginal_SUMMARY.md;
laplace_diagnostic_SUMMARY.md; conditional_decay_SUMMARY.md;
b3_SUMMARY.md; s0_SUMMARY.md; m4_SUMMARY.md; ALT-SLOWDOWN-MECHANISM.md;
FIRST-PROOF.md; PNAS-PLAN.md.

---

## Status (2026-04-20): largely executed

Most prescriptive items in this document have landed; it now
functions as the audit trail for why the T1a → T1b shift and
the Route 1' → polynomial-tail-framework shift happened. The
current live docs are:

- `paper/SECOND-PROOF.md` — T1b gap list under the polynomial-
  tail induced-operator framework. Supersedes FIRST-PROOF §2 as
  the live proof target; FIRST-PROOF carries a "Superseded by"
  pointer at its top and is archival.
- `paper/F1-HYPO-PLAN.md` — live working doc narrowing the
  framework choice at β = 1/2. Reading of Melbourne–Terhesiu
  2012, Gouëzel 2004, and Young 1999 since this reconciliation
  was written has settled on **M–T 2012 as the only applicable
  primary**; Gouëzel 2004 requires β > 1 and Young 1999
  requires ∫R dm < ∞, both of which fail at β = 1/2. This
  doc's "Melbourne-Terhesiu / Gouëzel / Sarig / Young-tower"
  language throughout should be read as the menu of candidates
  *as of 2026-04-19*, not the current menu.
- `paper/MESSES.md` — now carries Mess #6 (the Gibbs–Markov
  instantiation question under M–T §11.2), added after this
  reconciliation was written. Mess #6 is about (GM-1) —
  whether the natural excursion-type partition on the skew
  product is Markov under F. The sim corpus does not speak to
  (GM-1); it is a paper-side structural question with a
  falsification protocol in Mess #6.

Status tags for the §"Concrete next moves" items are inline at
the bottom of this doc.

---

## Headline

1. **The MESSES are empirically supported in aggregate, but the
   specific mechanisms MESSES named are not all the right ones.**
   Mess #2 and Mess #3 each have a direct measurement that makes
   the concern quantitative. Mess #1 has split results: the
   textbook obstruction is verified on SRW, but the universality-
   class argument that imports it to BS(1,2) is falsified on
   BS(1,2)'s own E-process.

2. **The sims' cumulative weight points away from Route 1' as
   currently sketched.** Three sub-problems (R2 Feller legitimacy,
   R5 rate conversion, R6 target identification) are all being
   attacked by the sims from the angles the MESSES anticipated.
   R2 and R6 are under the most pressure.

3. **They also point at a replacement framework.** The τ_R tail
   is ≈ 1/√n — the best-behaved polynomial-tail regime — and T1b's
   1/√n asymptotic is exactly what Melbourne-Terhesiu / Gouëzel /
   Sarig / Young-tower induced-operator theory delivers when the
   tail exponent is α = 1/2. The measured tail exponent and the
   claimed theorem asymptotic are the same object. That is the
   piece of encouraging news in this document.

4. **The claim gate in PNAS-PLAN already anticipates the worst
   case.** The contingency wording for (R6) failing independently
   of (R4)+(R5) — theorem degrades to "convergence to an
   unidentified ν*" — is the right place to put the empirical
   pressure from return_marginal. The current significance-
   statement draft still overclaims on that clause.

---

## Mess #1 — rate conversion (Laplace obstruction)

### Status after sims

Split. The Mess's central calculation — that for a null-recurrent
walk with ML(1/2) return counts, E[q^{N_n}] decays as 1/√n, not
exp(−c√n) — is **independently verified** on SRW (Part A of
`laplace_diagnostic_SUMMARY.md`). Slopes of log E[q^{L_n}] vs
log n come in at −0.502, −0.501, −0.499 for q ∈ {0.3, 0.5, 0.7}
(pre-asymptotic −0.471 at q = 0.9, where subleading corrections
are larger); the closed-form q√2 / ((1 − q)√(πn)) matches
measured values to within 0.2% at n = 10⁴ for q ∈ {0.3, 0.5,
0.7}. No sim bug, no artifact. The Mess's textbook obstruction
is real.

The transport of that obstruction to BS(1,2) is the part that
breaks. Part B of the same sim measures the BS(1,2) E-process
with no-freeze kernel:

- Mean E grows as ≈ 0.16·√n, std as ≈ 0.13·√n. **The E-process
  is not zero-drift.** At n = 10⁴, only 1.1% of walkers have
  E < 0.
- Local time L_n in R = {|E| ≤ 10} grows approximately linearly
  (L_n/n = 1.00 at n ∈ {100, 1000}, 0.60 at n = 10⁴), not as √n.
- E[q^{L_n}] for BS(1,2) does not follow the SRW closed form.
  The trajectory is transient exp(−cn)-like followed by a plateau.

So MESSES §1's assertion that BS(1,2)'s E-process is "a zero-drift
martingale with bounded increments, so its local-time statistics
at {|E| ≤ E₀} are in the same universality class" is **not
supported**. The specific universality-class argument that made
the 1/√n obstruction automatic for BS(1,2) is empirically wrong.

### But this does not rescue the Laplace route

Two reasons the obstruction persists in weaker form:

1. `tau_R_tail_SUMMARY.md` measures P(τ_R > n) directly on the
   paper kernel at R = {|E| ≤ 10} (same R as laplace_diagnostic
   Part B, longer horizon, different observable) and finds an
   almost exact 1/√n tail: slope −0.495, R² = 1.0000 on
   [50, 10⁴]. That is the classical null-recurrent tail. The
   **τ_R tail on the paper kernel is null-recurrent-shaped**,
   regardless of what the Part-B L_n statistics suggest about
   the transient E-distribution.

2. The conflict between the two sims is explained in
   `tau_R_tail_SUMMARY.md` §"Tying together with prior diagnostics":
   positive E-drift coexists with 1/√n return-time tails
   because individual walkers return almost surely but with
   heavy-tailed return times; the mean position grows because a
   small fraction sits far from R at any given time. The
   laplace_diagnostic Part B's L_n ≈ n reading is a pre-asymptotic
   artifact of the horizons tested (most walkers hadn't made their
   first long excursion yet).

Net: whether or not MESSES §1's *specific* argument for 1/√n is
transportable to BS(1,2), the *conclusion* — that the Laplace
route as written cannot deliver stretched-exp at the law level —
survives, because the τ_R tail is directly measured at 1/√n and
that is what the Laplace-transform machinery chews on.

### What the sims leave open on Mess #1

- **What actually drives the M1/√2 transient's exp(−c√n) shape
  on [20, 200] is not identified.** `conditional_decay_SUMMARY.md`
  tested the cleanest single-mechanism candidate (b-steps passive
  on mantissa; pure a-rotation with Diophantine structure of
  log₁₀ 2) and rejected it decisively: predicted c is 55× smaller
  than measured. The transient has to involve active b-step
  m-mixing, which the sims haven't pinned down mechanistically.
- **The M3 IC (b) direct α̂ = 0.525** is the strongest single
  result in the corpus, and it is *not* a rate-conversion
  statement. It is a direct measurement of the asymptotic
  exponent without going through per-return contraction × return
  count at all. So Mess #1 only matters if the paper's rate
  argument routes through Laplace transform of N_n. The M3 IC
  (b) measurement is a certificate that the asymptotic exists
  and has the right exponent, independently of how one would
  prove it.

### Consequence for Route 1'

**(R5) as written is dead.** E[q^{N_n}] ≤ C exp(−c√n) is false
for any q < 1 when N_n has ML(1/2) scaling (which S0 Laplace
test confirms at the conditional level). The honest rate
derivation from per-return contraction gives 1/√n, not
exp(−c√n). That is T1b's asymptotic, and it is what the sims
support. The Route 1' architecture needs to be rewritten to
deliver 1/√n directly, not to deliver stretched-exp via (R4)×(R5).

This is the one place where the MESSES + sims package is
actually constructive: the new target (T1b, 1/√n) is what
polynomial-tail induced-operator theory gives natively. The
framework mismatch is the problem, not the individual pieces.

---

## Mess #2 — target identification (WHERE)

### Status after sims

**Under direct empirical pressure at the natural R.**
`return_marginal_SUMMARY.md` measured the pooled post-burn
distribution σ̃ of walker states at return events (BS(1,2),
N = 10⁶, n_max = 10⁴, R = {|E| ≤ 10}, K_burn = 5, IC √2). The
findings refute π_T ν_R = Leb_T at that R much more sharply than
MESSES's sketch anticipated:

- 22.0M post-burn returns from 876k walkers. Every single one
  had E = +10 — every return was from above. No return at
  E ∈ {−10, …, +9}. Directly reflects the positive E-drift
  (consistent with `laplace_diagnostic_SUMMARY.md` Part B's
  1.1% fraction at E < 0).
- m at return is supported on the arc [1 − log₁₀ 2, 1) ≈
  [0.699, 1.000), and is uniform on that arc at density
  1/log₁₀ 2 ≈ 3.32.
- L₁(σ̃, Leb_T) = 1.40, 260× the multinomial noise floor.
- |σ̂(1)| = 0.86, |σ̂(2)| = 0.50, |σ̂(5)| = 0.21. Low-r Fourier
  coefficients are order unity. σ̃ is nowhere near Leb_T.

The proposed mechanism (not directly measured; would require
pre-return-state instrumentation): at E₀ = 10 the only channel
returning a walker from E = 11 to E = 10 is a⁻¹ with borrow,
which requires m_pre < log₁₀ 2 and deterministically maps
m_pre → m_pre + (1 − log₁₀ 2). The arc support is therefore
arithmetic, not Diophantine. The b⁻¹ channel has width
O(10⁻¹¹) at E₀ = 10 and is numerically irrelevant.

### What this does and does not prove

**Does:** the pooled return-sample T-marginal σ̃ is far from
Leb_T, with a specific arc-concentration mechanism that is
robust to the usual Diophantine / Weyl argument (the arc isn't
the output of an equidistributing rotation — it's the output of
a single deterministic carry-arithmetic shift).

**Does not:** show σ̃ = ν_R. The sim pools post-burn returns
without verifying stationarity by return index, and 12.4% of
walkers didn't contribute a post-burn sample in n_max = 10⁴.
It also does not sweep E₀: the a⁻¹-with-borrow argument loses
force at small E₀ where the b⁻¹ channel widens.

### Where this leaves MESSES §2's five-item list

MESSES §2 listed five mechanical obstructions to the rotation-
invariance sketch (kernel not T-rotation-equivariant inside R,
dense support ≠ specific-rotation-invariance, Fourier closing
move overlaps R4, O(10^{−E₀}) b-step absorption, net-a-count
distribution vs excursion length). The sim **confirms the
qualitative worry** (σ̃ ≠ Leb_T at E₀ = 10) and **sharpens one
specific mechanism**: the concentration is not mild, is not a
Fourier-damping target, and is produced by a single deterministic
step (a⁻¹ with borrow) rather than by any Weyl-invariance story.

The five-item list was about why the rotation-invariance sketch
was aspirational. The sim upgrades that from "aspirational" to
"empirically refuted at the natural R by a specific arithmetic
mechanism." A fix isn't a tightening of the sketch; it's a
different R, a different framework, or a walker-level argument
that bypasses ν_R.

### WHERE ≠ WHEN

MESSES.md's 2026-04-19 update distinguishing WHERE (Mess #2) from
WHEN (Mess #3) is load-bearing and correct: the arc-concentration
of σ̃ is set by single-step carry arithmetic on the return step,
while the τ_R tail is set by walker-level E-process dynamics above
R. The two are orthogonal. A fix for one does not automatically
fix the other. Current Route 1' treats them as aspects of a
single "T_R legitimacy" problem; the sims show they are
independent problems with independent mechanisms.

### Consequence for Route 1'

**(R6) is under the heaviest empirical pressure of any Route 1'
sub-problem.** The natural R fails the identification step by a
specific and clean mechanism, and the failure mode is not soft
(280% of noise floor, order-unity Fourier modes). The
contingency wording in PNAS-PLAN's claim gate and FIRST-PROOF §1
already names this outcome; the sims move (R6) failure from
"possible contingency" to "the current best guess given the
evidence at R = {|E| ≤ 10}." A rescue requires one of:

- (a) different R with a different return-mechanism that doesn't
  land on an arithmetic arc;
- (b) walker-level argument for π_T ν_n → Leb_T that bypasses
  ν_R entirely — note the walker's *unconditional* m-marginal
  DOES equidistribute (M1's φ → 0 across the M3/Run1/Run2/Run3
  panel), even though the return-state marginal doesn't, so
  route (b) is consistent with what we measure;
- (c) bridge operator that sees both the return-state
  distribution and the time-averaged distribution and closes
  the gap between σ̃ and the unconditional m-marginal.

Route (b) is the most promising given the evidence. The paper's
T1b-observable-level convergence is happening; it just isn't
being mediated by ν_R.

---

## Mess #3 — operator legitimacy (WHEN)

### Status after sims

**Qualitatively confirmed, quantitatively sharp.**
`tau_R_tail_SUMMARY.md` measured the first-excursion survival
S(n) = P(τ_R > n) on the paper kernel (N = 10⁶, n_max = 3×10⁴,
R = {|E| ≤ 10}, IC √2):

- Slope = −0.495, R² = 1.0000 on n ∈ [50, 10⁴]. Textbook
  null-recurrent return exponent −1/2 to two decimals.
- S(30 000) = 6.98 × 10⁻³, still tracking 1/√n extrapolation
  within 8%. No visible plateau at the horizon.
- 99.30% of walkers had at least one return by n = 30 000;
  0.70% had not.

The tail is polynomial with exponent 1/2 — the best-behaved
polynomial-tail case. MESSES §3's qualitative objection (the
sketch invokes uniform geometric tail control; the walk is
null-recurrent-like) is now quantitative: the tail is explicitly
1/√n.

### Consequence for Route 1'

**(R2) as written is framework-incompatible.** FIRST-PROOF §2
R2's Feller-continuity argument for T_R assumes "uniform
geometric tail bound on τ_R from x ∈ R"; the measured tail is
polynomial with exponent 1/2. Truncate-and-pass-to-limit uses
the wrong kind of control.

### What this actually buys

Here the news is genuinely good, which is rare in this
reconciliation. The Melbourne-Terhesiu (2012) / Gouëzel (2004) /
Sarig (2002) / Young (1998 tower) literature treats induced
operators whose return tail is P(τ > n) ~ C/n^α for α ∈ (0, 1)
and gives correlation decay O(n^{−(1−α)}). With α = 1/2 —
*precisely* our empirical finding — the delivered decay is
O(1/√n), exactly T1b's claimed asymptotic. The measured tail
exponent and the claimed theorem asymptotic are the same object.

So Mess #3 is not just a diagnosis; it is also a pointer at the
correct replacement framework. If a Route 2 is written around
polynomial-tail induced-operator theory:

- R2's Feller-continuity concern becomes a citation rather than
  a load-bearing lemma;
- R5's rate-conversion problem disappears, because the
  framework gives law-level 1/√n directly from the tail exponent;
- R6's identification problem remains (Mess #2 doesn't go away).

### What the sims don't show on Mess #3

- **P(τ_R = ∞) not pinned.** Extrapolating 1/√n gives 0 but
  we don't have direct data past n = 3×10⁴.
- **Uniformity in x ∈ R not tested.** The Feller-type argument
  in a replacement framework would want the 1/√n tail to hold
  uniformly over starting points; tau_R_tail runs one IC (√2).
- **E₀ sweep absent.** The 1/√n exponent might be robust
  (expected, because it comes from SRW-like E-variance), but
  isn't directly verified.
- **Exactness of 1/2 vs 1/2 + o(1).** The measured slope is
  −0.495 with R² = 1.0000; the sim can't distinguish 1/2 from,
  say, 0.495 exactly.

---

## Cross-cutting: how the sims interact

### The three-sim interlock

Mess #1 (laplace_diagnostic), Mess #2 (return_marginal), and
Mess #3 (tau_R_tail) were run as separate diagnostics but their
outputs are coupled:

- `tau_R_tail` shows τ_R is heavy-tailed (1/√n).
- `laplace_diagnostic` Part B shows mean E grows as 0.16√n.
  These are consistent only because the heavy tail lets a small
  fraction of walkers sit far from R and drag up the mean. Both
  sims together give a coherent picture of the E-process:
  null-recurrent tail, positive-drift mean, asymmetric geometry
  (reflecting-at-0 on negative side, free on positive side).
- `return_marginal` shows every return happens at E = +10,
  consistent with the upward-drift picture. The walker exits R
  via E = 10 → 11 and re-enters via 11 → 10 (a⁻¹ with borrow,
  which forces the arc). The "entry through the top boundary
  only" pattern is what the E-process asymmetry predicts.

These three sims are **mutually consistent** and jointly pin a
picture of the walker's excursion structure that the FIRST-PROOF
Route 1' sketch did not anticipate. Each sim in isolation just
sharpens a Mess; together they describe a specific regime.

### Asymptotic vs transient tension

M3 IC (b) measured α̂ = 0.525 on [100, 600]. M4 on √2 shows
α_local drifting downward (1.43 → 0.66 over [200, 3000]) with
persistent late-window signal above null. These two together
say: the asymptotic is 1/√n; the approach can be slow; the
transient's shape (stretched-exp on √2) is IC-specific and not
a property of the walk. `conditional_decay_SUMMARY.md` rules
out the cleanest mechanism for the stretched-exp transient
(pure a-rotation / Diophantine) — whatever produces the
transient involves active b-step m-mixing, which is harder to
analyze and which the sims haven't pinned down.

For the MESSES reconciliation the important point is:
**Mess #1 attacks an argument for stretched-exp as an
asymptotic. T1b says stretched-exp is a transient, not an
asymptotic.** The MESSES-era Mess #1 was written when T1a was
still live. With T1a dead and T1b the committed shape, Mess #1
retargets: the paper is no longer trying to prove stretched-exp
at infinity, so the specific 1/√n obstruction on E[q^{N_n}] is
no longer an obstruction to the theorem — it is the theorem.

### What the alternating-step sims don't say

`ALT-SLOWDOWN-MECHANISM.md` synthesizes seven sims
(parity_falsifier, projection_check, eps_scan_and_z3,
h3_contrast, f2_contrast, step_buddies, comparison_walks) about
sub-sampling slowdowns on ℤ², ℤ³, H_3, and F_2. These are all
evidence for §6 kicker's footnote ("only the full
additive+multiplicative mix converges in practice") and for the
three-walks figure, not for §2 proof architecture. They are
**silent on all three MESSES**. Worth flagging because they
represent a nontrivial fraction of sim effort; if someone later
asks "what do all these ℤ² / H_3 sims say about T_R?" the
answer is "nothing — they're about a different rhetorical
point."

One minor caveat: the document's §"What this does not explain"
notes that BS(1,2) mantissa's r ≈ 1.15 slowdown doesn't fit the
parity-mode picture. That residual anomaly doesn't bear on the
three MESSES either but is flagged as an open mechanism question.

---

## What the sims leave untouched

Things the sims cannot, by design, speak to:

1. **Whether Route 1's spectral gap (R4) on T_R could be proved
   analytically at all.** B3's ρ(K̂) = 0.924 is numerically
   plausible — spectral radius strictly below 1 — but the
   analytical target must be tight (bound ρ < 0.99 would not be
   strong enough). The sim triage says "not impossible, tight
   required." It does not decide whether anyone can actually
   write the proof.

2. **Whether a different R would resolve Mess #2.** The sim uses
   R = {|E| ≤ 10}. A different R might avoid the arc-concentration
   (different return channels), but that is untested.

3. **T1b's α = 1/2 on the √2 IC directly.** M4 at n = 3000 shows
   persistent signal above null but α_local hasn't stabilized at
   0.5. The beef-box Run 1 (n = 20 000 on √2) would resolve
   this; until then, the √2 IC's α_∞ = 1/2 is an extrapolation,
   not a measurement.

4. **Whether any of this generalizes to BS(1, p) for p ≠ 2.**
   All sims are specifically on BS(1,2). Nothing about the three
   MESSES depends on p = 2 specifically, but the sim corpus
   can't certify the generalization either way.

5. **Smooth-IC universality of α = 1/2.** T1B-UNIT-BALL Run 3
   (smooth Gaussian ν) reaches floor too quickly to measure α;
   the asymptotic exponent under smooth ICs remains inferred
   rather than measured.

---

## Claim-gate implications

The PNAS-PLAN claim gate has two bins. The sims + MESSES change
the picture for several items.

### Goes in (as of claim gate)

- "The symmetric BS(1,2) mixed-arithmetic walk has mantissa
  marginal converging to Benford at stretched-exponential rate
  exp(−c√n)." **This is T1a, which is dead.** The sim corpus
  has moved this to Stays out. T1B-EVIDENCE-MAP already flagged
  the retarget; the claim gate text in PNAS-PLAN §"Goes in"
  hasn't been updated. Outcome: replace with T1b wording
  (asymptotic 1/√n with IC-dependent B, optional IC-specific
  stretched-exp transient for sharp ICs).
- "There exists c(ε, μ) > 0 such that c ≥ c(ε, μ)." **Needs
  rewriting.** Under T1b this becomes "there exists B(ν) such
  that L₁(P_n, Leb_T) ∼ B(ν) · n^{−1/2}." The ε-controls-c story
  is T1a-era and shouldn't survive in its current form.
- "ε is the nonlinear coordinate term." Unaffected.
- "For symmetric measure; biased is a separate case." Unaffected.

### Stays out (as of claim gate)

- "Exponential rate for the mixed walk." Still out; now joined
  by "stretched-exp as the asymptotic for the mixed walk."
- "Any specific decomposition of c." Unaffected.
- "Exact constant identification." B(ν) is measured for two ICs
  (M3 IC (b) ≈ 3, √2 ≈ 0.01 order of magnitude). Do not tabulate
  beyond these.

### Contingency fires

PNAS-PLAN claim gate already carries the key contingency:

> If (R4)+(R5) close but (R6) does not, the theorem degrades to
> "mantissa marginal converges to an unidentified probability ν*
> on T at stretched-exponential rate" — still a convergence
> theorem, but *not a Benford theorem*. In that case the
> significance statement and the §4 mechanism presentation must
> be rewritten to drop the Benford-identification claim, and the
> title changes.

The sims make this contingency more rather than less likely at
the natural R. The degraded wording should also drop
"stretched-exponential" (T1a-era phrasing) and use 1/√n.

The significance statement's "converging to the Benford
distribution at stretched-exponential rate" is currently a
double overclaim: (i) Benford is the identification claim
Mess #2 pressures; (ii) stretched-exp is the T1a asymptotic
Mess #1 pressures. Neither half survives the sim corpus cleanly.

---

## Proof-architecture implications

Concrete items that follow from the reconciliation, in rough
order of priority:

1. **Route 1' as written is stale.** (R2) uses the wrong tail;
   (R5) targets the wrong asymptotic shape; (R6) fails at the
   natural R. Three of six sub-problems are either dead or under
   heavy pressure. (R1), (R1.5), (R3), (R4) are not directly
   contradicted by the sims.

2. **A Route 2 (polynomial-tail induced-operator theory) is
   natively compatible with the measured τ_R tail AND with T1b's
   asymptotic.** Melbourne-Terhesiu / Gouëzel / Sarig / Young-tower
   framework takes P(τ > n) ~ C/n^α and returns correlation decay
   O(n^{−(1−α)}). At α = 1/2 that is 1/√n. No (R5)-style
   conversion needed; no geometric-tail (R2) lemma needed.

3. **Mess #2 doesn't go away under Route 2.** Whatever framework
   proves the rate, π_T ν_R = Leb_T is still an independent
   identification claim, and σ̃ at R = {|E| ≤ 10} is empirically
   far from Leb_T. The fix options from the return_marginal
   summary (different R, walker-level argument, bridge operator)
   apply regardless of which rate framework is used.

4. **The walker-level argument (option b for Mess #2) is the
   cleanest rescue for the Benford identification.** The walker's
   unconditional m-marginal does equidistribute (measured across
   M1/M3/M4/Run1/Run2/Run3/R1-R3; every IC tested reaches the
   vicinity of the N-appropriate null floor). If we could prove
   π_T ν_n → Leb_T directly without going through ν_R, Mess #2
   is bypassed. Route 2 + walker-level identification is a
   coherent architecture. It is *not* what FIRST-PROOF §2
   currently sketches.

5. **The B3 spectral number is the one piece of infrastructure
   that survives a framework change.** ρ(K̂) = 0.924 <  1 is
   empirical evidence for a per-return contraction, which any
   framework (Route 1' or Route 2 or a Young-tower version) will
   want as input. B3 is reusable.

---

## Concrete next moves, in priority order

From the reconciliation, not from triage of beef-box runs.

1. **Retarget FIRST-PROOF §2.** *[Executed, 2026-04-19, via
   `paper/SECOND-PROOF.md`.]* Rewrite from "prove stretched-
   exp via (R4)×(R5)" to "prove 1/√n via polynomial-tail induced-
   operator framework." (R2) becomes a citation. (R5) is
   absorbed. (R6) stays, and the sketch should use walker-level
   π_T ν_n → Leb_T rather than ν_R identification if possible.

2. **Update the PNAS-PLAN claim gate.** *[Executed; see
   `paper/PNAS-PLAN.md` for the T1b-synced claim gate and
   significance-statement wording.]* "Goes in" should read
   T1b (1/√n asymptotic, IC-dependent coefficient, IC-specific
   stretched-exp transient for sharp ICs). The significance
   statement's "stretched-exponential rate exp(−c√n)" becomes
   "algebraic rate n^{−1/2} with IC-dependent coefficient."

3. **Fold MESSES updates into FIRST-PROOF §2.** *[Moot.
   FIRST-PROOF is archival with a "Superseded by SECOND-PROOF"
   pointer; SECOND-PROOF is the live doc and its §3 + §4
   already reflect the MESSES pressure.]* MESSES.md's
   2026-04-19 updates on Mess #2 and Mess #3 reference the sims
   directly but the FIRST-PROOF sketch hasn't been synced. Either
   FIRST-PROOF §2 references MESSES as the status-of-Route-1'
   document, or it absorbs the pressure and restates the sketch.
   Right now the two documents are drifting.

4. **Decide whether to finish the Route 1' rescue attempts or
   commit to Route 2.** *[Committed: SECOND-PROOF is written
   against polynomial-tail induced-operator theory (M–T 2012
   primary). Route 1' is retired to FIRST-PROOF.]* The
   reconciliation above doesn't force the choice, but it does
   show that three of Route 1's six sub-problems are empirically
   contested. A Route 2 sketch doesn't yet exist. Writing one
   is the highest-leverage piece of mathematical work.

5. **Instrument one pre-return-state sim for return_marginal.**
   *[Open.]* The m_pre equidistribution assumption (mechanism
   sketch for σ̃'s arc concentration) is the cleanest prediction
   that would upgrade "σ̃ ≈ σ with arithmetic arc" to "ν_R is
   derivable in closed form at E₀ = 10." Small sim, big rigor
   payoff on Mess #2.

6. **(If the paper commits to Route 2 being walker-level.)**
   *[Open; tracked in SECOND-PROOF §4 as the main identification
   route.]* Prove π_T ν_n → Leb_T without T_R. The sim evidence
   for this is strong (every IC tested reaches floor; M1/M4 on
   √2 pass θ_N; M3 ICs (a) and (c) reach the N = 10⁷ floor by
   n ≈ 150 and n ≈ 330 respectively). A walker-level argument
   is what all of this empirically licenses.

Not covered above (post-2026-04-19):

7. **Falsify or confirm (GM-1) on the minimal two-step
   excursion.** *[Open; tracked in MESSES.md Mess #6 and
   referenced from SECOND-PROOF §3 (F1) and F1-HYPO-PLAN §§4–5.]*
   Paper-side calculation, not a sim. Decides whether the M–T
   §11.2 Gibbs–Markov route survives or the F1-HYPO-PLAN Option B
   (Meyn–Tweedie polynomial ergodicity) takes over.

---

## One-paragraph executive summary

The simulation corpus has made the three MESSES quantitative, and
in aggregate the news for Route 1' is worse than the MESSES
alone suggested. Mess #3 is confirmed by a direct 1/√n τ_R tail
measurement (R² = 1.0000 on two decades); Mess #2 is confirmed
by a direct measurement of σ̃ on an arc of length log₁₀ 2 at
260× noise floor at R = {|E| ≤ 10}; Mess #1's specific
universality-class argument is falsified on BS(1,2), but the
underlying obstruction survives via the directly-measured
polynomial τ_R tail. The encouraging item is that T1b's 1/√n
asymptotic and the measured 1/√n τ_R tail are the same object
in Melbourne-Terhesiu / Gouëzel / Young-tower polynomial-tail
induced-operator theory, so a Route 2 written in that framework
would deliver the T1b asymptotic natively without needing the
(R5) Laplace-transform step. Mess #2 survives any rate
framework, and the cleanest rescue is a walker-level argument
π_T ν_n → Leb_T that bypasses ν_R; the sims empirically support
this direction. The PNAS-PLAN claim gate's "goes in" list
currently reads T1a; the sims have moved the theorem to T1b and
the claim-gate text hasn't been resynced. FIRST-PROOF §2 and
MESSES.md are drifting apart and should be reconciled before
any further drafting.
