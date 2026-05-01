# Attractor and Mirage

A methodology note from the `experiments/acm-champernowne/base10/q_distillery/`
FFT-iteration experiments. Two findings, one substrate-side, one
rendering-side. Both required deliberate testing to disentangle.

## Standing Findings (consolidated)

The body of the document below is a chronological narrative of
what was tried during one session, what got refuted, and what
the surviving claims rest on. This section is the TL;DR after
the audits the body records.

### Substrate-side findings (currently surviving)

1. **The lattice value `Q_n(n^h · k)` is determined by
   `(shape(n), τ-signature(k), ν_n(k))`.** Algebraic from the
   master expansion. Verified empirically: σ-relabeling (random
   permutation of primes acting through prime factorisation)
   leaves the lattice bit-for-bit identical, since shape,
   τ-signature, and ν depend on prime exponent multisets, not
   on which specific primes realise them.

2. **The lattice has measurable spatial-correlation structure
   ~700× the random-input baseline at h = 5.** Direct angular
   probe (no FFT iteration): 16-angle `sum|corr|` is 6.77 for
   the original lattice vs 0.0094 for constgauss baseline. The
   substrate's spatial signal is real and large.

3. **Substrate spatial correlations decompose into two 1D
   structures, one per axis.** The visually striking 2D
   patterns (checkerboard at odd h, horizontal stripes at even h)
   are *cross-products* of two 1D correlation profiles on the
   consecutive-integer-indexed lattice. Verified by row/column
   shuffle test: shuffling rows preserves the k-direction
   profile only; shuffling columns preserves the n-direction
   profile only. The 1D pieces are real; the 2D geometric
   richness is partly coordinate artifact.

4. **The 1D profiles show parity-of-lag modulation depending on
   h-parity:**
   - **Odd h (h=5, h=7)**: axial-balanced. Both horizontal and
     vertical 1D correlations have a parity sawtooth (even-lag
     correlation noticeably higher than odd-lag, both positive).
   - **Even h (h=6, h=8)**: horizontal becomes parity-flat at
     high value (~0.6–0.78); vertical becomes parity-flipped —
     even-dy positive, odd-dy *negative* (~−0.13).

5. **Parity modulation persists at lag 1500 (37% of lattice
   size), with no decay to zero, no sign crossing, no
   decoherence.** Substrate-wide parity-of-(n, k) organisation,
   not a local coupling.

6. **Diagonals (45°, 135°) are the weakest near-axial directions
   at every h tested.** Mechanically: diagonal motion changes
   both shape(n) AND τ-signature(k); axial motion changes only
   one.

7. **For prime n at h, the master-expansion coefficient pattern
   has kernel structure that grows with h.** At h, prime-n rows
   are exactly zero for k whose τ-polynomial degree lies in
   `[1, h−1]`. By h = 8, most k ∈ [1, 4000] give Q = 0 at prime
   n; lattice signal at high h comes from composite-n rows.

### Methodological findings

A. **The FFT-magnitude-log iteration is a high-self-signature
   probe.** Random-input pair correlations between iter_5
   angular spectra have median ~+0.48 — the operator's intrinsic
   angular bias. Any "partial closure" claim under iteration
   must clear that bar; most don't.

B. **Direct lag correlation on the raw lattice (no iteration)
   is the right primitive for substrate signal.** It bypasses
   the operator's intrinsic angular biases.

C. **Single-seed comparisons cannot ground claims.** The seed
   std on `sum|corr|` is ~0.001, comparable to differences that
   were briefly called "structural conservation." Multi-seed
   bracketing is required.

D. **Bulk-dominated distributions need different rendering than
   structured ones.** Percentile-clipped colormaps create
   phantom patterns when applied to peaked distributions;
   full-range rendering is honest.

### Refuted en route (preserved as record)

- "Conservation of structural budget across information-discarding
  transforms." Most of the apparent conservation was the
  iteration's intrinsic correlation floor, not substrate content.
- "Anti-diagonal partial closure at iter_5 = 2.3σ." At 16-angle
  resolution, several other angles carry similar excess; the
  4-direction probe was sampling artifact.
- "2D checkerboard / stripes ARE the substrate." Refined: 2D
  patterns are cross-products of 1D structures on consecutive-
  integer adjacency.
- "Möbius preservation of angular shape (+0.703) is informative."
  Within range of random-input seed pairs at +0.48 ± 0.17.

## The Setup

The `(n, k)` Q-lattice at `h = 5` is a 2D arithmetic-multiplicative
image: shape × τ-signature blocks, gcd-vein periodicities, prime-row
structural zeros. One FFT preserves this structure dramatically — a
discrete prime-harmonic grid we already documented in
`experiments/acm-champernowne/base10/q_distillery/`.

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
seeds give different per-direction concentrations.

### Further deflation: 16-angle sampling refutes the sharp-peak reading

The "anti-diagonal partial closure at 2.3σ" interpretation
implicitly assumed the 4-direction probe was sampling near *the*
substrate-signal peak. A 16-angle spectrum at iter_5 (lag pairs
covering 0°–180° in increments of ~10–20°, summed over L = 1, 2, 4)
disconfirms that. Excess of original over single-seed constgauss
baseline by angle:

```
135.0°  +0.00079    (anti-diagonal — supposedly the peak)
 33.7°  +0.00077    (essentially identical magnitude)
 26.6°  +0.00050
  0.0°  +0.00041
146.3°  +0.00029
 56.3°  +0.00026
 ... (other angles within ±0.0004 of zero, mixed signs)
 90.0°  -0.00040    (vertical: actually depressed)
108.4°  -0.00038
```

The 135° excess is the largest, but **33.7° is essentially
indistinguishable in magnitude**, and `26.6°, 0°, 146.3°, 56.3°`
all show meaningful excess too. The cluster within ±25° of 135°
has mean excess +0.00011 with only 2 of 5 angles above zero. The
far cluster has mean +0.00004 with 4 of 11 above zero. The
"partial closure at the anti-diagonal" interpretation is a
4-direction-sampling artifact: the probe happened to land at one
of several similar-magnitude excess points, and 33.7° (which the
4-direction probe didn't sample) carries indistinguishable signal.

Worse, the 4-direction probe's `y` direction at 90° comes back as
*depressed* (-0.00040) below baseline at 16-angle resolution. The
original 4-direction reading "y is elevated at 2.4×" was an
artifact of the wrong (non-iterated) Gaussian baseline.

What survives after the angular interrogation: the original
lattice's iter_5 angular spectrum is qualitatively distinguishable
from constgauss's (some angles positive excess, some negative),
but no single direction carries an unambiguous substrate signal
at this probe and resolution. The single-angle excess magnitudes
(~0.0008) are comparable to single-seed std of the constgauss
baseline (~0.001), so even the largest excesses need multi-seed
across 16 angles before any directional claim survives the
standard the document calls for elsewhere.

This is the harness pattern recurring inside our own audit: the
angular sampling was itself a probe choice that wasn't interrogated
until committed to. The 4-direction result, which seemed clean at
the time, was sampling artifact.

## Möbius Inversion Along k: A Different Probe (Exploratory)

A complementary test, named in the web agent's third proposal
several iterations ago and finally run: apply Möbius inversion
along the k-axis to each row of the lattice, then run iter_5 and
the 16-angle spectrum. Möbius is the Dirichlet inverse of the
all-ones function; the master expansion's `τ_j(m / n^j)` is a
j-fold Dirichlet self-convolution of `1`, so one Möbius application
along k peels one layer of that stack. The mechanical question:
does the angular structure we see at iter_5 trace to τ-stack
content?

Result, single-seed and exploratory:

| | total `sum|corr|` |
|---|---|
| original lattice iter_5 | 0.01415 |
| Möbius-along-k iter_5 | 0.01436 |
| constgauss baseline (seed 1729) | 0.01239 |

Total budget unchanged (Möbius did not deflate the iteration's
correlation budget). The angular *shape*, however, shifted
non-trivially:

```
Correlation between (orig − cg) and (mu − cg) angular excess vectors:
  +0.703
```

`+1.0` would mean Möbius did nothing to the spectrum's shape;
`0.0` would mean Möbius produced unrelated structure; `+0.703`
means partial overlap. Möbius preserved ~half the angular
variance and changed the other half. The sharpest individual
shifts were sign-flips at 90° and 153° and elevations at 71.6°
and 108.4° — angles that weren't notable before Möbius become
prominent after, and vice versa.

**Tentative reading**: the angular structure at iter_5 isn't
purely τ-stack content (Möbius didn't flatten it) and isn't
fully independent of τ-stack content (Möbius did change which
angles carry excess). It's partly Dirichlet-stacking, partly
something else.

**The control: constgauss-vs-constgauss seed-pair correlations.**
Run iter_5 on 12 different constgauss seeds. Compute each one's
16-angle excess vector against a fixed reference constgauss
(seed 1729, the same baseline used in the Möbius test). Compute
the 66 pairwise Pearson correlations among those 12 excess
vectors. The result:

| | value |
|---|---|
| mean | +0.467 |
| median | +0.484 |
| std | 0.166 |
| min / max | +0.079 / +0.810 |
| IQR | +0.351 / +0.564 |

**The Möbius `+0.703` sits at the ~80th percentile, ~+1.3σ above
median, but well within the random-input distribution.** Two
random constgauss inputs produce iter_5 angular spectra correlated
at this level routinely. The Möbius result does not clear the
random-input bar.

**What this calibrates**: the FFT-mag-log iteration imposes about
half the angular variation from its own stationary-distribution
shape, regardless of input. The operator has a strong angular
self-signature (median pair correlation +0.48). Substrate
contributions above this construct floor are difficult to detect
with this probe at moderate magnitude.

**What this does not refute**: that the substrate has angular
structure. It refutes that *the FFT-mag-log iteration's iter_5
angular spectrum* is a clean enough probe to isolate it. The
operator's intrinsic correlation between any two random-input
runs is high enough (~0.5 median) that moderate-magnitude
substrate contributions are masked. A different probe with lower
intrinsic angular self-correlation might separate substrate from
operator more cleanly. The session has not yet found such a
probe; the next experiment after this section drops FFT
iteration entirely and computes the angular spectrum of the raw
lattice directly.

The Möbius experiment is recorded here as **uninformative at this
resolution**, not as a finding. Multi-seed bracketing of Möbius
itself, or a probe with smaller operator self-bias, would be
needed to revisit.

## Direct Angular Spectrum: Backing Off FFT Entirely

The right move — once we recognised the FFT-mag-log iteration as a
high-self-signature probe — was to drop FFT and look at spatial
correlations of the raw lattice directly. We should have run this
first. The result:

```
                          16-angle sum|corr| over L = 1, 2, 4
original lattice (slog)   6.77211
constgauss (12 seeds)     0.00944 ± 0.00098
                          ----
z(original vs constgauss) +6896
```

The raw lattice's spatial-correlation budget is **three orders of
magnitude above the random-input baseline**. Every single angle is
above z ≈ 800. The peak is z ≈ 3870 at 0° (horizontal lag) and
z ≈ 3800 at 90° (vertical lag).

The dominant directions in the raw lattice are *axial* — 0° and
90°. The diagonals (45° and 135°) are the *weakest* near-axial
directions: sum |corr| ≈ 0.28 vs ≈ 0.90–1.00 for horizontal /
vertical. Off-axial angles (18°, 26°, 56°, 71°, etc.) sit
between, with sum |corr| roughly 0.21–0.46.

### What this implies for the rest of the session

**The FFT-mag-log iteration was destroying the signal it was
trying to detect.** All the analyses based on iter_5 — the
"partial closure at 135°", the multi-seed bracketing, the 16-angle
spectrum on iter_5, the Möbius peeling — were measuring a few
percent of structure that survived an enormously
information-discarding probe.

**The substrate's preferred directions are axial, not diagonal.**
Mechanically reasonable: adjacent k at fixed n share τ-signature
context; adjacent n often share shape class. Diagonal motion
requires both n and k to vary in correlated ways, a less natural
constraint.

**The iter_5 "anti-diagonal partial closure" was an inversion.**
At raw-lattice level, 135° is among the *weakest* angles. The
iter_5 spectrum saw it as elevated — meaning the FFT iteration
not only loses information but appears to *invert* directional
preferences. The mechanism is conjectural (FFT rotates real-space
horizontal/vertical structure into frequency-space
horizontal/vertical, then magnitude-log nonlinearity blends them);
the empirical fact is that **iter_5 directional preference and
raw-lattice directional preference disagree about which angles
are elevated**.

### The methodological self-check this raises

The session went straight to FFT iteration as the probe of choice
without first establishing that the raw lattice has measurable
spatial structure at all. The right opening move would have been
the experiment in this section: compute lag correlations on the
raw lattice, see the substrate's signal directly, and only then
ask which iterations or transformations preserve / destroy it.

I did not propose this experiment until prompted by the user.
The justifications I gave for going through FFT first ("Mandelbrot
analog", "what does the FFT look like") were aesthetically
appealing but methodologically backwards: they prioritised an
interesting probe over a *calibrating* one. The harness section
above lists "the probe was assumed clean" as a harness error
caught only late; this experiment is the calibration that should
have come first and didn't.

The raw-lattice direct angular spectrum is the closest thing the
session has to a clean substrate signal. It does not say anything
about absolute normality; it says the substrate has measurable
spatial-correlation structure at small lags, with a known angular
profile (axial-dominant, diagonal-weakest), three orders of
magnitude above random-input baseline.

### h-parity alternation in the angular shape

Running the same direct-angular probe at h = 5, 6, 7, 8 revealed
an h-parity dependence in the substrate's spatial-correlation
structure. Numbers (sum |corr| over L = 1, 2, 4):

```
                  total    0° (horiz)   90° (vert)   45°    135°
h = 5  (odd)       6.77       0.90       1.01       0.28    0.28
h = 6  (even)     10.60       2.01       0.66       0.55    0.55
h = 7  (odd)       5.97       1.02       0.93       0.27    0.27
h = 8  (even)      8.61       1.87       0.54       0.41    0.41
```

**Three patterns survive at the magnitude where single-seed
constgauss baselines (~0.009) are negligible noise relative to the
signal:**

1. **Total budget alternates with h-parity.** Even h gives
   ~10.6 / 8.6; odd h gives ~6.8 / 6.0. Even h is consistently
   ~1.5–1.7× larger than the adjacent odd h. Not a monotone climb
   with rank.

2. **The dominant axis flips between odd and even h.** Even h is
   strongly horizontal-dominant: 0° at 1.87–2.01, 90° at
   0.54–0.66. Odd h is roughly axial-balanced: 0° at 0.9–1.0,
   90° at 0.93–1.01. The substrate's preferred direction in the
   (n, k) lattice rotates with h-parity.

3. **L = 1 vertical correlation flips sign at even h.** Adjacent
   rows in (n, k) at even h are *slightly anti-correlated*
   (vertical L=1 ≈ −0.14 at h=6 and h=8); at odd h they are
   positively correlated (vertical L=1 ≈ +0.25 at h=5 and h=7).
   The L = 4 vertical correlation is positive at all h. So at
   even h, vertical correlation rises *from negative* with lag.

**Mechanism — first-order reading**: the master expansion has
`(-1)^(j-1)` alternating signs. The deepest-rank term `j = h` has
sign `(-1)^(h-1)` — positive at odd h, negative at even h. When
the alternating sum redistributes its content into spatial
correlations after slog compression, the parity of the deepest
contribution apparently selects which axis carries the dominant
spatial coherence. Complete mechanistic accounting would require
tracking which specific terms of the expansion produce
correlations along which axes; the empirical fact stands ahead of
that accounting.

**What survives universally across h tested**: substrate signal
is 685×–1125× the constgauss baseline at every h; the diagonal
directions (45°, 135°) remain the weakest near-axial angles at
every h (substantially weaker than the four cardinal directions);
the L=1<L=4 lag-anomaly persists at every h, with magnitude
varying by parity but the sign-of-rise consistent.

This is the rank-tower coherence the Grand Program section asked
for, in specific quantitative form. Coherence isn't the same
shape at every h; it's the same *kind of shape* (octagonal,
axial-dominant, diagonal-weakest) modulated by an h-parity
alternation that traces back to the master expansion's
alternating signs.

### The 2D autocorrelation, and what we created with our coordinate
choice

A 2D autocorrelation map of slog(lattice) at h ∈ {5, 6, 7, 8}
showed two visually striking pattern types: a clean Z/2 × Z/2
**checkerboard** at odd h, and **horizontal stripes** at even h.
Initial reading: the substrate has rich 2D spatial structure,
qualitatively different by parity.

A shuffle test asks the harness-vs-system question on this
finding directly. For each h, randomise either the row order
(n-axis) or the column order (k-axis) of the lattice, recompute
2D autocorrelation. Result:

- **Even h (h=6, h=8)**: row-shuffle collapses the pattern
  almost completely — only a single bright horizontal line at
  `dy = 0` survives, with all other `dy` rows going dark.
  Column-shuffle barely touches the pattern. The "horizontal
  stripes" were *almost entirely n-direction structure*; the
  k-direction (dx) content was nearly uniform.
- **Odd h (h=5, h=7)**: row-shuffle leaves a single bright
  horizontal line at `dy = 0` (carrying the k-direction
  structure); column-shuffle leaves a single bright vertical
  line at `dx = 0` (carrying the n-direction structure). Either
  shuffle removes most of the 2D pattern. The 2D checkerboard
  was the *cross-product* of two 1D correlation structures, one
  along each axis.

The parity story refined:

- **Substrate has 1D correlation structure along each axis**,
  decomposable. Each survives the shuffle of the perpendicular
  axis.
- **At odd h, both 1D structures are substantial**. At even h,
  the n-direction structure dominates and the k-direction
  structure is small.
- **The 2D pattern (checkerboard / stripes) is the cross-product
  of those 1D structures**, presented on the integer-indexed
  (n, k) lattice. The "checkerboard appearance" at odd h is a
  visual cross-product of the two 1D structures landing on
  consecutive-integer parity adjacencies. Strip the second axis
  and what's left is one strong 1D structure.

This is the harness-vs-system audit applied to the 2D
finding. The 1D substrate structures are real; the 2D pattern's
geometric richness is partly an artifact of (consecutive-integer
adjacency) × (cross-product of 1D content). We had been
calling the 2D pattern itself the substrate finding; what
survives the audit is the 1D-decomposition with parity-dependent
emphasis between axes.

The Methodological self-check applies again, less severe than
the iter_5 partial-closure debacle but in the same shape: I had
been treating the 2D autocorrelation map as the substrate's
content. The user pushed back ("are we huffing farts"); a
shuffle test resolved which parts were real versus artifact;
the document now records the refined claim. None of the
attractive geometric pattern would have been corrected without
the user's intervention.

### Long-range persistence: parity modulation is not local

The 1D autocorrelation profiles per axis, parity-split, were then
extended to lag = 1500 (37% of the 4000 lattice size, with
proper FFT zero-padding to avoid wrap-around). The user's
explicit framing: this *did not have to* persist. Three patterns
that could have refuted "global parity-coupling" but didn't:

1. **Decay to zero**: the parity gap could have closed at some
   characteristic lag. It didn't.
2. **Sign flip**: the negative odd-dy correlation at even h could
   have crossed zero at long lags. It didn't.
3. **Decoherence**: at long lags, autocorrelations could have
   become small noise. They didn't — they stayed at clearly-
   separated levels.

Specific lag-1500 values:

```
                  horiz[1]  horiz[100]  horiz[500]  horiz[1500]    vert[1]   vert[1500]
h = 5 (odd)        +0.16     +0.48       +0.43       +0.41        +0.25      +0.37
h = 6 (even)       +0.59     +0.72       +0.65       +0.51        −0.14      +0.39
h = 7 (odd)        +0.20     +0.51       +0.46       +0.41        +0.30      +0.29
h = 8 (even)       +0.57     +0.67       +0.60       +0.47        −0.14      +0.34
```

Especially clean: at all four h values, **odd-dx horizontal
correlation at odd h sits ≈ +0.18 from L=1 to L=1500**, holding
the factor-of-3 gap below the even-h horizontal value (≈ +0.5).
At even h vertical, **odd-dy stays negative at every L tested**,
hovering near −0.13 with small variation.

This means the substrate's parity-coupling is a **substrate-wide
organising principle**, not a short-range correlation that
happens to look striking at small lags. Two cells at parity-
coupled positions correlate (or anti-correlate, at even h
vertical) regardless of lattice distance, all the way out to a
substantial fraction of lattice size.

Mechanically: the lattice value at (n, k) depends on the
parity of n and parity of k through shape × τ-signature × gcd
content, in a way that is consistent across the whole integer
range we sampled. The parity organisation is not a local
arithmetic accident; it's a feature of how the master
expansion's content distributes itself globally.



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

5. **Angular structure at iter_5 distinguishable from constgauss
   baseline by qualitative shape, but not concentrated at any
   single mode.** The 16-angle spectrum on the original lattice's
   iter_5 versus single-seed constgauss baseline shows several
   non-axial angles (135°, 33.7°, 26.6°, 0°, 146.3°, 56.3°) with
   positive excess, several others (90°, 108°) with negative
   excess. The "anti-diagonal partial closure at 2.3σ" claim from
   earlier in the session was a 4-direction-sampling artifact: the
   probe landed near one of multiple similar-magnitude excess
   points. At 16-angle resolution, the partial closure isn't a
   single mode — and individual-angle excess magnitudes (~0.0008)
   are comparable to single-seed baseline std (~0.001), so even
   the qualitative-shape claim needs multi-seed across all angles
   to survive the document's own standards. The substrate is doing
   something angular at iter_5; we have not yet localised it.

The category-error worry the user named while looking at the disk
image — *is the moiré real or aliasing or category error?* —
resolves cleanly here, in a way that points at the manifesto's
generality. The structure question splits into:

- real-as-substrate-arithmetic-residue (substrate structure):
  tested, gone by iter 2
- real-as-anti-diagonal-partial-closure: refuted on probe
  interrogation — at 16-angle resolution, the 135° excess is
  matched by 33.7° excess, with several other angles also
  elevated; the 4-direction probe's "single mode" reading was
  sampling artifact
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

Scripts in `experiments/acm-champernowne/base10/q_distillery/`:

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

3. **Angular structure at iter_5 is qualitatively distinguishable
   from constgauss baseline, but not localised.** The 16-angle
   spectrum on the original lattice's iter_5 shows several
   non-axial angles with positive excess and several with
   negative excess; magnitudes are comparable to single-seed
   baseline std. The earlier "partial closure at the anti-diagonal"
   reading was a 4-direction sampling artifact. The substrate is
   doing something angular at iter_5 — we have not localised it.
   Whether multi-seed-bracketed comparison at 16+ angles preserves
   any signal as "real substrate content" is an open empirical
   question, not a settled one.

The deeper note in line with `THE-UNDECIDABLE-HEART`: each
instrument is a deliberate choice, and the substrate's persistence
through one instrument is no guarantee of persistence through
arbitrary instrument compositions. The bilingualism is real but
not free; the right altitude question generalises beyond algebra
to instrument-stacking.

The session's headline collapse-in-two iteration was correct. The
hierarchy of relaxation timescales was the surprise. The
"anti-diagonal partial closure" claim that briefly stood as the
positive finding was itself refuted by 16-angle probe interrogation:
several non-axial angles carry similar-magnitude excess, the
4-direction probe was sampling artifact, and earlier revisions of
this document made a localisation claim that the data does not
support. What the substrate is doing angularly at iter_5 is
detectable but not localised; whether it survives multi-seed
bracketing across a fine-angle spectrum is open.

This is the document's own enactment of the manifesto's stance.
We render because we cannot close. We deflate as we look. Each
positive claim has had an audit step; each audit so far has
narrowed the claim further. The substrate-shaped partial closures
named in the next section are *targets*, not findings — proposed
locations where stable observables might exist if the next
construct or rank or probe finds them. The session's findings
proper are the algebraic ones (lattice IS its classification, σ is
null, the kernel-zero structure of the matrix), the negative ones
(no probe-survived spatial-correlation localisation in this
session), and the methodological one (the audits matter, and the
audits we have not run probably matter too).

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

- Colormap-mirage explanation (verified by full-range re-render
  — conditional on inferno; a perceptually uniform colormap might
  behave differently).

**Harness-conditional, refuted on probe interrogation**:

- Anti-diagonal partial closure at iter_5 (refuted by 16-angle
  sampling; the 135° "peak" is matched by similar-magnitude
  excess at 33.7° and several other non-axial angles; the
  4-direction probe was sampling artifact, and earlier revisions
  of this document claimed substrate localisation that cannot be
  defended at finer angular resolution).

**Harness-conditional, not yet audited for harness independence**:

- The relaxation timescale hierarchy (one realisation).
- The iter_10 attractor's specific shape (one realisation).
- The hierarchy of "what dies under which transform" (most
  comparisons single-seed).
- The qualitative-angular-shape claim that *survives* after the
  16-angle deflation (excess at multiple non-axial angles, deficit
  at 90°/108°) is itself single-seed and at magnitudes comparable
  to baseline std.

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

## Closed-Form Work To Be Done Before More Empirics

The session has been heavy on rendering and empirical probes,
light on closed-form algebra. The Standing Findings are
empirical patterns; tightening them into algebraic statements
would (a) make the rank-tower extension more useful as a
structure-destruction probe and (b) give us specific predictions
to test against new lattices rather than re-discovering patterns
each round.

Tractable items, ordered by how directly each would tighten an
existing finding:

1. **Closed form for the within-row 1D parity profile.** Pick
   prime n. Compute, as a function of h, the within-row
   autocorrelation profile `corr(Q(n, k), Q(n, k + L))` averaged
   over k. The empirical observation is: at odd h, even-L gives
   ≈ +0.4, odd-L gives ≈ +0.18 (factor of 3 gap); at even h,
   parity-flat near +0.7. The closed form should reveal *which
   τ-signature-class pairs* dominate the average, and why their
   contribution differs by L parity.

2. **Closed form for adjacent-row covariance at even h.** Why
   does `<Q(n, k) Q(n+1, k)>_k` come out negative at even h and
   positive at odd h? Compute for n = 2, 3 (both prime, simple
   case); generalise to (composite, composite) row pairs which
   dominate the lattice signal. Track which (j, shape) terms
   contribute the negative covariance and why h-parity flips
   the sign.

3. **Composite-shape kernel structure.** We have prime-n kernel
   ([1, h−1] τ-polynomial degree). What's the analogous kernel
   for shape p²? pq? p²q? Each has a coefficient pattern with
   its own annihilation properties. A `(shape, h, killed-degree
   set)` table would generalise the prime-n kernel result.

4. **The L = 1 < L = 4 monotone rise.** Pure curiosity: most
   natural signals decay with lag; ours rises in axial
   directions. Mechanism likely involves alternating-sign τ_j
   contributions whose phases align constructively at L = 4 and
   destructively at L = 1. Concrete: compute `Σ_k τ_j(k) τ_j(k +
   L)` for small L, see how it varies with L, propagate through
   the master expansion's signed sum.

5. **Why even-h horizontal becomes parity-flat while vertical
   becomes parity-flipped.** Asymmetric effect on the two axes
   — they're not transformed identically by the parity flip.
   Track which terms produce the parity-flat horizontal and
   which produce the parity-flipped vertical. The asymmetry is
   the mechanistic puzzle.

The standing findings together suggest a candidate organising
frame: **the lattice carries substrate-wide parity-of-(n, k)
coupling whose direction-by-direction expression depends on h's
parity through the master expansion's deepest-term sign**.
Closed-form work would either substantiate this organising
claim or expose it as too coarse — and the rank tower extension
afterwards would test the predictions either gives.

The user's instinct (consolidate > closed-form > rank tower)
makes sense for this reason: rank-tower extension is a powerful
structure-destruction probe (each h is its own object, and
differences across h destroy whatever is h-specific while
preserving what is rank-universal). Using it without algebraic
handles wastes its power. Each h we add without closed-form
context is more empirical surface area to render and audit; with
closed-form context, each h becomes a *test* of what the algebra
predicted.

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
