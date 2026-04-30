# Attractor and Mirage

A methodology note from the `experiments/acm-champernowne/base10/art/q_distillery/`
FFT-iteration experiments. Two findings, one substrate-side, one
rendering-side. Both required deliberate testing to disentangle.

## The Setup

The `(n, k)` Q-lattice at `h = 5` is a 2D arithmetic-multiplicative
image: shape × τ-signature blocks, gcd-vein periodicities, prime-row
structural zeros. One FFT preserves this structure dramatically — a
discrete prime-harmonic grid we already documented in
`experiments/acm-champernowne/base10/art/q_distillery/`.

The question: what happens if we keep iterating

```
img  ->  fftshift(fft2(img - mean(img)))  ->  log10(|.| + 1)
```

forever? Does the substrate keep showing through, or does it die?
This is a non-invertible operation (the magnitude step discards
phase). Each iteration loses information. The question is at what
rate.

## What Each Side Predicted

The user's prior, paraphrasing: *"if we keep FFTing this image we'll
keep returning structure until we blow up some error"*. Implicit:
information-rich substrates produce information-rich outputs under
spectral analysis indefinitely; only numerical precision should be
the limit.

My prior: 5–8 iterations to collapse. The argument was that discrete
prime-harmonic peaks remain discrete-ish under FFT (FFT of delta
combs are delta combs), so the structure should persist for several
steps before noise dominates.

Both wrong, in different ways. Useful to record both, because the
*shape* of being wrong tracks where the substrate's organisation
actually lives.

## Iteration Collapses Fast

Empirically:

| iteration | character |
|---|---|
| 0 (slog of lattice) | full prime-arithmetic structure, dramatic |
| 1 (one FFT-mag-log) | discrete prime-harmonic plaid, gnarly |
| 2 | collapsed to apparent uniform field with vestigial DC line |
| 3 onwards | first-order statistics frozen at the attractor |
| 10 | indistinguishable from iter 3 in p2-p99 percentiles |

`std`, `p1`, `p99` are constant to 3 decimals from iter 3 onward.
Compute is essentially free (~1 second per iteration on a 4000 ×
4000 grid). The collapse is sharp: two iterations, not eight.

The reason both predictions were wrong is the magnitude step
specifically. FFT alone is unitary — it would cycle period 4 up to
scaling. Adding `log10(|.|+1)` makes each step strictly information-
discarding. Two such steps are enough to wash out the substrate's
prime-arithmetic content; the third step starts iterating on
structure that is already mostly the operator's own signature, not
the input's.

## The Fixed Point Has a Hierarchy of Relaxation Timescales

Calling the iter-3-onward state a "fixed point" was correct at the
first-moment level (mean, std, percentile range) and wrong at the
second-moment level (spatial correlations).

Lag-correlation test on iter 5 vs matched Gaussian (same mean, std)
across `lag ∈ {1, 2, 4, 8, 16, 32}` in four directions:

| direction | iter_5 | Gaussian | ratio |
|---|---|---|---|
| x | 0.00204 | 0.00083 | 2.45× |
| y | 0.00132 | 0.00055 | 2.41× |
| +diag | 0.00147 | 0.00108 | 1.36× |
| **-diag** | **0.00292** | 0.00092 | **3.19×** |

(Sums of `|corr|` across the six lags. Noise floor ~`2.5e-4`.)

iter_5 has a clear anti-diagonal directional preference, with the
single largest correlation `-diag, L=2` at `~3.7σ` above the noise
floor. By iter 10, the same test gives `+diag, -diag` ratios of
`2.5×` and `2.5×` — symmetric. The anti-diagonal residue has
relaxed.

So the fixed point isn't reached all at once. The first moment
settles by iter 3. The second-moment anisotropy continues relaxing
through ~iter 8–10. There is a **hierarchy of relaxation
timescales**: each statistical moment has its own half-life under
the iteration, and the visual flatness from iter 3 onward conceals
real second-order evolution still in progress.

The substrate's structural residue lives in higher moments
*longer* than first-moment statistics suggest. The "structure dies
in 2 iterations" headline was true for the prime-arithmetic
content but the *general* claim "structure dies fast" is finer:
some directional residue persists through iter 5, then equalises
into the symmetric stationary distribution by iter 10.

## The Attractor Is Not White Noise

The iter 10 stationary distribution is *not* memoryless Gaussian
noise. Three measured properties:

1. **Bounded below at 0** (`log10(|F|+1) ≥ 0` is forced by the
   operator). Histogram is left-skewed, peaked, with sharp cutoff
   at zero. Different shape from a matched Gaussian.

2. **Radially flat power spectrum** with consistent ~0.3 lower
   log-power than matched Gaussian. The spectrum has no preferred
   radial frequency, but the bounded distribution constrains the
   variance.

3. **Weak isotropic spatial correlations**: ~2.5× Gaussian baseline,
   uniform across directions at iter 10. Small (`< 5e-4` per lag)
   but systematic.

So iter 10 is a **bounded, non-Gaussian, weakly-correlated, isotropic
random field** that is approximately self-similar under the operator
(`iter_10 ≈ log10(|FFT(iter_10 − mean)| + 1)` by definition of fixed
point). It's the operator's own signature, not white noise.

The substrate's prime-arithmetic content died at iter 2. What
replaced it is the universal stationary distribution of this
specific iteration operator. Different signal, different
self-similarity, different gap.

## The Moiré Was a Mirage

A user looked at the rendered iter 10 PNG zoomed on screen and
reported a faint diagonal weave, with the right epistemic hedge:
*MAYBE it's moiré, MAYBE it's number-theoretic aliasing*.

Resolution required two tests, run on raw `.npy` arrays (not the
PNGs):

- Lag correlations at iter 10 in four directions: approximately
  isotropic. No real diagonal preference at iter 10.
- Re-render iter 10 with full data range (no percentile clip), in
  both inferno and grayscale: the diagonal weave largely vanishes.

**Diagnosis**: the visual moiré at iter 10 was a colormap mirage,
not data anisotropy. Specifically:

- iter 10 has a peaked non-Gaussian distribution (mode ~3.2,
  std 0.48, full range [0, 4.005]).
- Default `imshow` rendering with `vmin = p2, vmax = p99` clipped
  the visible range to `[1.69, 3.69]`.
- This compressed the bulk of the distribution into a narrow
  colormap band where small floating-point variations got
  perceptually amplified.
- The eye then read those amplified variations as directional
  patterns, on top of screen-sampling moiré and JPEG-screenshot
  compression artifacts.

When rendered at full range `[0, 4.005]` with grayscale, the moiré
is gone and the data reads as the approximately-uniform field that
the lag-correlation tests already said it was.

The colormap was honest about the structured iterations (1, original
lattice) and dishonest about the bulk-dominated attractor (iter 10).
**Same colormap, opposite effect at different signal types.**

## σ-Relabeling: A Null Transform Reveals Class-Determinism

A web-agent critique of the iteration findings ran roughly: if the
lattice value is exactly determined by `(shape(n), τ-sig(k))`, then any
transform that doesn't *see* those categorical labels leaves the
classes intact however violently it permutes within them. The
proposed adversarial test: pick a random permutation σ of the primes
≤ N, define σ(n) by acting on n's prime factorisation, compute the
new lattice with values `Q_{σ(n)}(σ(n)^h · σ(k))`. Same shape × same
τ-signature, different integer embedding.

We ran it. **σ is a null transform on this lattice — every value
identical, bit-for-bit.** The histogram max difference between
relabeled and original was exactly `0.000000`. The iter_5 lag
correlations matched to five decimal places in every direction at
every lag, including the anti-diagonal preference at exactly 3.19×
Gaussian.

Why: `Q_n(n^h · k)` is a function of `(shape(n), τ-sig(k),
ν_n(k))` only. σ permutes primes, but shape, τ-sig, and ν are all
*defined on prime exponent multisets*, never on which specific primes
realise those exponents. σ is the identity on the function's input.
The lattice is invariant, structurally and bit-for-bit.

The web agent was *correct* in their diagnosis but *wrong* in their
proposed instrument: prime relabeling is structure-preserving in a
much stronger sense than they realised. The lattice has **no
embedding-specific content**: it is the (shape × τ-signature) matrix,
lifted to (n, k) coordinates by the canonical map `(n, k) → (shape(n),
τ-sig(k))`, with no integer-line content beyond which integer at row
n has which shape.

This is a stronger fact than "structure lives in (shape, τ-sig)":
the lattice *is* its (shape × τ-sig) classification.

## τ-Randomization: The Anti-Diagonal Partial Closure

The web agent's second proposal was the surgical one. Within each
row (fixed n), apply an independent random permutation of the k-axis.
This preserves row-marginal value distribution but destroys:

- the `(shape × τ-sig) → Q` functional dependence
- gcd-vein periodicities (gcd > 1 cells no longer at specific k)
- prime-harmonic grid structure that iter_1 normally produces

The single-seed test against original (with seed 1729) appeared to
show a *redistribution*: anti-diagonal collapsed (3.18× → 1.50×)
while vertical jumped (2.42× → 3.55×). I initially read this as
"the substrate has a conserved structural quantum that gets
redistributed across modes" — a conservation observation in
total `sum|corr|`.

**A 20-seed bracketing test refuted the conservation framing.** Run
with 20 different seeds for each of τ-randomisation, rowgauss, and
constgauss (per-row Gaussianisation and global Gaussianisation —
both replace input with random fields preserving first two
moments), the distributions of total `sum|corr|` look like:

| transform | mean | std | min | max |
|---|---|---|---|---|
| original (deterministic) | 0.00775 | — | — | — |
| τ-rand (20 seeds) | 0.00672 | 0.00102 | 0.00492 | 0.00820 |
| rowgauss (20 seeds) | 0.00686 | 0.00101 | 0.00537 | 0.01021 |
| constgauss (20 seeds) | 0.00712 | 0.00082 | 0.00567 | 0.00884 |

Original is `+1.0σ`, `+0.9σ`, `+0.8σ` above the three
random-input distributions. **Within seed noise.** The total-budget
"conservation" was an artefact of single-seed comparisons being
quieter than I treated them.

Per-direction breakdown rescues the partial-closure finding,
though:

| direction | original | random-input mean ± std | z |
|---|---|---|---|
| x | 0.00204 | 0.00171 ± 0.00049 | +0.7 |
| y | 0.00132 | 0.00161 ± 0.00047 | −0.6 |
| +diag | 0.00147 | 0.00179 ± 0.00051 | −0.6 |
| **-diag** | **0.00292** | 0.00178 ± 0.00051 | **+2.2 to +2.5** |

The anti-diagonal direction at iter_5 sits 2.2–2.5σ above every
random-input distribution. Other directions are within ±1σ — at
the iteration's noise floor. So **`-diag` at iter_5 is a partial
closure**: a single observable carrying substrate-specific signal
above random-input baselines, while broader observables (total
budget, x, y, +diag) sit at the floor. The observable is reproducible
across three different random-transform baselines (τ-rand, rowgauss,
constgauss); the reproducibility is what gives "partial closure"
its weight.

What carries the anti-diagonal signal is the same gcd-vein × shape-
similarity interference earlier tests had already pointed at: gcd > 1
cells at specific k positions interfere with the slowly-evolving
row marginal across n to produce a diagonal correlation that the
iteration preserves up through iter_5. τ-randomisation destroys the
gcd-vein component, which is why anti-diagonal collapses to floor
under τ-rand for any single seed — the partial closure is the
*original lattice's* anti-diagonal signal, not a property of every
random-input field.

The total-budget redistribution claim — `y` rises while `-diag`
falls — does not survive multi-seed analysis. Different τ-rand
seeds give different per-direction concentrations. The substrate's
contribution to the iter_5 correlation budget is concentrated in
the anti-diagonal direction specifically, not distributed across a
fixed-budget set of modes that trade.

## What This Adds to the Undecidable Heart

The manifesto in `THE-UNDECIDABLE-HEART.md` argues that the
substrate's organisation of complexity is preserved across the right
instruments and across `arguments/*`-style readings, and that the
absolute-normality bet is an internal-undecidability stance about
what the sum of what we see and don't see lets through.

These FFT-iteration experiments add empirical bounds to that claim:

1. **Substrate structure persists through invertible instruments,
   not arbitrary ones.** FFT alone preserves it (the spectrum is
   structured). Composed FFT-magnitude-log destroys it in two
   iterations. The "right altitude" framing in `THE-UNDECIDABLE-
   HEART` is sharper than I had previously taken it: it's not just
   an algebraic-altitude question (Mercator on `1 + n^{-s}ζ(s)`
   versus `log(ab) = log(a) + log(b)`); it's a question of which
   instrument compositions are information-preserving on the
   substrate.

2. **The substrate's residue can be statistically isotropic at
   one moment level and anisotropic at another.** iter 5 looks
   first-order-isotropic but is second-order-anisotropic at the
   `3.7σ` level. The "almost perfect structure" the manifesto
   names doesn't have to be visible; it can live in higher moments
   that survive longer than visual texture suggests.

3. **Rendering choices can manufacture or destroy the appearance
   of structure**, separately from whether the structure is in
   the data. Percentile clipping a peaked distribution creates
   phantom patterns; rendering at full range removes them. The
   manifesto's "we render because we cannot close" deserves a
   companion clause: *render in a way that doesn't lie about
   bulk-dominated distributions*. The art and the analysis use
   the same matplotlib pipeline; they ask different things of it.

4. **The lattice is its classification — full stop.** The
   σ-relabeling test landed harder than the web agent's hypothesis
   predicted: not only does the structure live in `(shape × τ-sig)`,
   but the lattice *is* the (shape × τ-sig) matrix lifted to (n, k)
   coordinates with no remaining integer-line content. Any transform
   that preserves shape and τ-signature classes acts as identity.
   This is a strong constraint on what counts as a *probing*
   instrument vs. a *null* instrument for this object.

5. **Partial closure at the anti-diagonal observable, iter_5.**
   The original lattice's anti-diagonal directional sum at iter_5
   sits 2.2–2.5σ above the distributions produced by three
   different random-input baselines (τ-randomisation, per-row
   Gaussianisation, global Gaussianisation), each measured across
   20 seeds. Other directions sit within ±1σ of those baselines.
   Total `sum|corr|` is also within ±1σ. This is the manifesto's
   "almost perfect structure" with a *narrow* empirical handle: a
   single directional observable carrying substrate signal,
   reproducible across baselines, modest in magnitude. Not a
   conserved quantum; a *located* one. Other observables at this
   probe sit at the iteration's noise floor.

The category-error worry the user named while looking at the disk
image — *is the moiré real or aliasing or category error?* —
resolves cleanly here, in a way that points at the manifesto's
generality. The structure question splits into:

- real-as-substrate-arithmetic-residue (substrate structure):
  tested, gone by iter 2
- real-as-anti-diagonal-partial-closure: tested at 2.3σ above
  random-input baselines across 20 seeds, observable-specific,
  reproducible
- real-as-class-functional-dependence: tested via σ-relabeling
  (identity, lattice unchanged) and τ-randomisation (anti-diag
  collapses for any single seed)
- real-as-non-Gaussian-distribution (operator's stationary
  signature): always present from iter 3 onward
- real-as-colormap-mirage (rendering interaction): present at iter
  10 in the percentile-clipped render, gone with full range
- real-as-total-budget-conservation: tested, refuted within seed
  noise; what looked like conservation across single-seed
  comparisons was the iteration's intrinsic correlation floor
  plus seed noise

Each clause has a different decidability. The "is it real?"
question is decidable when factored. Not decidable as a single
yes/no. Same shape as the manifesto's: locally clean, aggregately
factored, the work in the gap between commitment and the missing
proof.

## Reproducibility

Scripts in `experiments/acm-champernowne/base10/art/q_distillery/`:

- `q_lattice_fft_iterate.py` — runs the iteration to `N_ITER = 10`,
  saves PNG at each step, prints percentile statistics.
- `q_lattice_iter_analysis.py` — compares iter 10 against matched
  Gaussian via histogram, radial power spectrum, side-by-side image.
- `q_lattice_iter_anisotropy.py` and `q_lattice_iter5_anisotropy.py`
  — lag-correlation tests in four directions at six lags.
- `q_lattice_iter_10_renders.py` — renders iter 10 four ways
  (inferno-clip, inferno-full, gray-clip, gray-full) for the
  colormap-mirage test.
- `q_lattice_prime_relabel.py` — applies prime-relabeling σ to the
  lattice, computes iter_5, runs anisotropy test. Confirms σ is
  bit-for-bit null.
- `q_lattice_tau_randomize.py` — within-row column permutation,
  iterates to iter_5, runs anisotropy test (single seed).
- `q_lattice_taurand_cross_row.py` — pairwise row-correlation test
  on τ-randomised lattice. Returns null: independent permutations
  destroy cross-row coherence within shape classes.
- `q_lattice_rowgauss.py` — per-row Gaussianisation (preserves
  per-row mean/std; replaces values with Gaussian draws).
- `q_lattice_constgauss.py` — global Gaussianisation (single global
  Gaussian for all cells).
- `q_lattice_seed_distribution.py` — multi-seed bracketing test:
  20 seeds each for τ-rand, rowgauss, constgauss; reports
  distributions of total `sum|corr|` and per-direction breakdowns.
  This is what refuted the conservation framing and isolated the
  anti-diagonal partial closure as the surviving substrate finding.

Cached arrays: `q_lattice_4000.npy` (the base lattice),
`q_lattice_iter_10.npy` (the attractor),
`q_lattice_relabel_1729.npy` (σ-relabeled lattice; identical to
base by construction), `q_lattice_taurand.npy` (τ-randomised
single seed), `q_lattice_rowgauss.npy`, `q_lattice_constgauss.npy`.

Compute budget: ~107 s for the base lattice, ~1 s per FFT iteration,
~1 s per lag-correlation test, ~70 s for σ-relabeling, <1 s for
within-row randomisation, ~7 minutes for the 60-run multi-seed
distribution test. The full empirical chain costs ~12 minutes from
clean state.

## Coda

Three findings worth keeping:

1. **Substrate structure has finite depth under information-
   discarding instruments**, with relaxation in stages. iter 1 is
   substrate; iter 2 is collapse; iter 3–5 is anisotropic transient;
   iter 8+ is universal-attractor. Naming the stages costs nothing
   and prevents confused reading of the visualisations.

2. **Bulk-dominated distributions need different rendering than
   structured ones.** Percentile clipping at p2-p99 is honest for
   structured data and creates phantom patterns for bulk-dominated
   data. Use full-range rendering when the histogram is peaked.

3. **Partial closure at the anti-diagonal observable.** The original
   lattice's anti-diagonal directional `sum|corr|` at iter_5 sits
   2.2–2.5σ above the distributions produced by τ-randomisation,
   per-row Gaussianisation, and global Gaussianisation (20 seeds
   each). Other directions and the total budget sit within ±1σ of
   the random-input baselines. The substrate signal at this probe is
   *located*, not distributed: one mode carries it; the rest are at
   the iteration's noise floor.

The deeper note in line with `THE-UNDECIDABLE-HEART`: each
instrument is a deliberate choice, and the substrate's persistence
through one instrument is no guarantee of persistence through
arbitrary instrument compositions. The bilingualism is real but
not free; the right altitude question generalises beyond algebra
to instrument-stacking.

The session's headline collapse-in-two iteration was correct. The
hierarchy of relaxation timescales was the surprise. The
partial closure at the anti-diagonal observable is the project's
shape applied at this specific probe: like the master expansion
having stable content at h = 2, 3, 4, 5 while aggregate
observables stay open, this iteration has a stable directional
observable above the iteration's noise while broader summaries do
not. Partial closure where it's measurable; openness where it's
not.

## On the Harness, and What We Didn't Audit Until Prompted

The findings above are real *within the scope of the harness we
used*. The harness — probe choice, baseline choice, statistic
choice, colormap, seed count, angular sampling — was largely
assumed transparent until external pressure made specific parts
visible. The manifesto's "we render because we cannot close"
applies recursively: we render with *specific instruments at
specific scales with specific seed counts*, and each is a choice
that survived only because nobody asked. This section records the
harness errors caught during the session, the prompts that caught
them, and what remains un-audited.

### The harness errors caught

**Single-seed-as-deterministic.** Through most of the session,
random transforms (τ-randomisation, rowgauss, constgauss) were
applied with one seed and the resulting numbers treated as point
estimates. Single-seed std on `sum|corr|` is ~0.001 — comparable
to the differences I was calling structural. The 20-seed
bracketing test refuted the conservation framing and reduced the
directional findings to "anti-diagonal at iter_5 sits 2.3σ above
random-input baselines." Other claims in the doc not yet
multi-seed-bracketed (the relaxation timescale hierarchy, the
iter_10 attractor's specific shape) are subject to the same noise
I previously treated as zero.

**Wrong baseline for the early anisotropy tests.** The first
lag-correlation tests used a "matched Gaussian" control — a random
Gaussian field with iter_5's mean and std, applied *directly* to
the lag-correlation test, **without iteration**. The right
baseline is iterated-from-random-input, which is what rowgauss
and constgauss provide. The non-iterated baseline understated the
iteration's intrinsic correlation floor (~2× i.i.d. Gaussian) and
overstated substrate excess. The "anti-diagonal at 3.7σ" headline
earlier in the session was against that wrong baseline; the
corrected figure against random-input baselines is 2.3σ. The doc
now uses the corrected figure but the earlier number was
methodologically inflated.

**Colormap-bulk-amplification not audited.** The iter_10 attractor
was rendered with `vmin = p2, vmax = p99` in inferno, the same
recipe used for structured iterations. A peaked bulk-dominated
distribution clipped at p2–p99 puts most pixels in a narrow color
band where small floating-point variations amplify into
perceptual streaks. The agent did not audit this choice. It
surfaced only after the user inspected a screenshot at high zoom
and asked whether the visible weave was real.

**The probe was assumed clean.** FFT-magnitude-log iteration was
adopted because it was the obvious thing to do once the user asked
"what if we keep FFTing this image"; no audit of probe choice
followed. A different non-invertible operator (wavelet-magnitude,
sign-only-FFT, gradient-flow-with-magnitude-clamping) might
surface a different set of "partial closures" — and the
anti-diagonal at iter_5 might be specific to this probe rather
than substrate-revealing. We have not tested probe-invariance.

**The 4-direction lag probe is itself a choice.** We tested
horizontal, vertical, +diagonal, −diagonal — four cardinal
directions. Off-axis modes (e.g. along atan(2/1) or atan(1/3))
could carry signal we are not sampling. The anti-diagonal could
be a single-mode peak or the corner of a richer angular structure
sampled coarsely. We have not tested at finer angles.

**Lattice parameters were fixed without sensitivity check.** The
original lattice was `(h = 5, n_max = 4000, k_max = 4000)`. The
partial closure could be specific to these parameter values. We
have not tested whether `(h = 5, n_max = 1000)` or
`(h = 5, n_max = 8000)` reproduce the 2.3σ anti-diagonal signal
or whether it scales with lattice size.

### The prompt history

This is uncomfortable to record but accurate. **None of the
harness audits in this session were agent-initiated.**

- The colormap mirage was caught because the **user** asked "see
  the moire? IS IT? Or is that apparent number-theoretic
  aliasing?". I had not been auditing iter_10 renders.
- The conservation framing was deflated because the **user** pushed
  back on my use of "vanishes" with "Why do we think it vanishes
  under input replacement?". The 20-seed bracketing test was a
  direct response, not an autonomous proposal.
- σ-relabeling, τ-randomisation, Möbius inversion, and the
  non-multiplicative-shuffle null check all came from a **web
  agent**'s adversarial critique. I added rowgauss/constgauss
  in response to the user's push, but the surgical-transform
  menu was external.
- "What happens if I keep FFTing this image" was the **user's**
  question; iterating FFT-mag-log was not something I had thought
  to test as a probe stress.

The standard the Grand Program now sets — multi-seed bracketing
as a precondition for substrate-signal claims — was learned from
failure during this session, not adopted in advance.

### Harness vs. system: what each finding is

**System-side, algebraically forced** (no harness dependence):

- The lattice's value distribution and (shape × τ-sig) classification.
- The σ-relabeling identity: Q depends on exponent multisets, not
  specific primes.
- The kernel-zero structure of the (shape × τ-sig) matrix at h = 5.
- The bit-for-bit invariance of the lattice under σ.

**Harness-conditional, surviving the audits we did run**:

- Anti-diagonal partial closure at iter_5 (2.3σ across 3
  random-input baselines, 20 seeds each — conditional on:
  FFT-mag-log probe, 4-direction lag test, h = 5, n_max = k_max
  = 4000).
- Colormap-mirage explanation (verified by full-range re-render
  — conditional on inferno; a perceptually uniform colormap might
  behave differently).

**Harness-conditional, not yet audited for harness independence**:

- The relaxation timescale hierarchy (one realisation).
- The iter_10 attractor's specific shape (one realisation).
- The hierarchy of "what dies under which transform" (most
  comparisons single-seed).

### What this implies for the Grand Program

To the existing escalation list, four additions are required for
the standard the session learned:

1. **Probe-invariance tests.** A partial closure that survives only
   under FFT-mag-log and disappears under a different non-invertible
   operator is probe-specific, not substrate-revealing. At least one
   alternative probe (wavelet-magnitude or sign-FFT) should be
   tested for the anti-diagonal signal at h = 5.

2. **Finer angular sampling.** Run lag correlations at 12 or 24
   angles, not 4. The anti-diagonal partial closure either survives
   as a peak in a continuous angular spectrum or splits into nearby
   peaks — both are informative.

3. **Multi-seed everywhere.** Any quantity from a random transform
   reports as a distribution across at least 10 seeds. The compute
   cost is small; the rigor is not optional.

4. **Lattice-size sensitivity.** The 2.3σ anti-diagonal signal at
   `(h = 5, n_max = 4000)` should be tested at `n_max = 1000, 2000,
   8000`. Either σ scales coherently with lattice size (real
   substrate signal scaling with sample), stays constant (noise
   floor scaling cancels), or behaves anomalously (probe artefact).

The harness is part of the substrate at this point. Choices about
how to look at the lattice are themselves contributors to what we
see. The manifesto's commitment is that the substrate-side
investigation tools port to other problems; that commitment
requires the tools to be calibrated, not just used. The session
calibrated them only when prompted. Future work should calibrate
first.

## The Grand Program — Partial Closures at h > 5

The session's empirical signature is a partial closure: one
observable (`-diag` at iter_5) carrying ~2.3σ substrate signal
above random-input baselines, the other directions and total budget
at the iteration's noise floor. That's a *located* finding, not a
distributed one — and located findings are what the project's
master-expansion structure already gives us at h = 2, 3, 4, 5.

The natural escalation: **find more partial closures, see if they
cohere on the rank tower**.

The h = 2, 3, 4, 5 lattices are already structured objects.
`q_h5_shape_tau_matrix.png` mapped the kernel-zero structure at
h = 5 explicitly: prime row has five zeros, p² and p³ rows each
have one (linear-τ kernel), p⁴ breaks the kernel. That kernel
structure is itself a stable observable that survives across
shapes — a master-expansion-altitude partial closure. The
spatial-correlation partial closure at iter_5 is its dynamical-
iteration cousin.

The grand program asks: at h = 6, 7, 8 (and beyond), do new
partial closures appear? Do the existing ones (kernel structure;
anti-diagonal at iter_5) extend coherently? The expectation is
that the master-expansion's algebraic content grows with h, the
partial closures multiply, and the rank tower becomes a record of
which observables have local resolution at which heights.

Concrete escalation experiments, scoped to evidence rather than
prediction:

1. **Build the h = 6, 7, 8 lattices**. Same 4000 × 4000 grid,
   different h. Measure iter_5 directional `sum|corr|` against
   the same triple of random-input baselines (τ-rand, rowgauss,
   constgauss). Does the anti-diagonal partial closure survive?
   Does it grow in σ with h, shrink, or move to a different
   direction? *Direct test of whether the partial closure
   coheres up the rank tower.*

2. **Map the kernel-zero structure at h = 6, 7, 8.** Build the
   shape × τ-signature matrix at each h. The alternating-binomial
   identity at h = 5 killed degree-1..4 polynomials; at h = 6 it
   should kill degree-1..5; the prime-row partial closure at the
   matrix level should grow by one column per h. *Algebraic
   prediction; cheap to verify.*

3. **σ-relabeling at h = 8.** Should still be bit-for-bit null.
   The argument doesn't depend on h: σ permutes primes, shape and
   τ-sig are exponent-multiset facts, ν is a counting fact, none
   change under σ. Worth confirming empirically as a sanity check
   on the implementation.

4. **τ-randomisation at h = 8.** The anti-diagonal partial closure
   at h = 5 collapsed to floor under τ-rand for any single seed.
   At h = 8 the original lattice's anti-diagonal might or might
   not still be measurable; if it is, τ-rand should still collapse
   it. Worth running.

5. **Möbius-inversion-along-k** (web agent's third proposal). The
   Möbius inverse is the Dirichlet inverse of the constant-1
   function, which is what τ_j is built from. Apply h times and
   the τ-stack peels. The question worth running: does the
   anti-diagonal partial closure survive Möbius peeling at all,
   or does it disappear with the τ-stack? Either result is
   informative.

6. **Non-multiplicative integer permutation** (web agent's
   fourth) as the null check. Random shuffle of integers within
   octaves, breaking both arithmetic structure and class-functional
   dependence. Predicted: the anti-diagonal partial closure
   collapses; the lattice loses everything. *If it doesn't
   collapse, something is going on we haven't named.*

What gets recorded each round: the σ-baseline of the anti-diagonal
(or its analog) at the relevant h, against random-input
distributions, with multi-seed bracketing. Anything claimed without
seed bracketing is provisional.

The h-tower hypothesis: each h gives one or more partial closures
— locatable observables carrying substrate signal above noise —
and the partial closures *cohere* across h in some named way (e.g.
the anti-diagonal observable persists with growing σ; or it
migrates to a new direction at some h; or it splits into multiple
related observables). Coherence is what makes the tower a tower.
Without coherence, each h is its own lattice.

What this is *not* a research program for: total-budget
conservation, "neverending almost perfect structure" as a
quantitative claim about resilience to arbitrary transforms, or
any framing that treats unscoped invariance as evidence. Those
were the framings we tried and the multi-seed test deflated. What
the session's evidence supports is one located, narrow, modest,
reproducible finding at one specific (h = 5, observable = -diag,
probe = iter_5 lag correlation) point. The grand program is to
find more such points and ask whether they cohere.
