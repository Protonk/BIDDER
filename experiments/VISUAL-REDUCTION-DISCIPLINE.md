# Visual Reduction Discipline

The project keeps finding the same lesson in different costumes:
an ACM-Champernowne stream can look normal in a flat one-dimensional
scan while carrying a tower of hidden structure. A useful chart is not
one that looks intricate. A useful chart removes one obvious background
and shows what survives.

The hierarchy below orders views by how much hidden information they
are allowed to use. Lower layers see only the sequence. Higher layers
know boundaries, monoids, factorisation coordinates, controls, and
flow cutoffs. A higher layer is not automatically more truthful, but
it makes a stronger claim and therefore owes a stronger null.


## The hierarchy

| layer | question | typical charts | what it can claim |
|---|---|---|---|
| raw sequence | does it look random? | digit stream, prefix frequencies, finite normality tests | anomaly detection only |
| positional background | how much is just radix notation? | sawtooth, mantissa/epsilon plots, digit-length classes | positional drift and block geometry |
| marginal distribution | are symbols balanced? | digit histograms, bit balance, Hamming weight, k-gram entropy | bias and short-window dependence |
| compression morphology | what shapes occur too often? | RLE histograms, RLE spectroscopy, ridgelines | local grammar after universal decay |
| boundary syntax | can joins be recovered? | boundary stitch, join windows, comma-style tests | entry-boundary algebra and transition rows |
| multiscale signal | at what scales does structure breathe? | autocorrelation, Morlet scalograms, wavelet variance | scale-local energy, with artifact risk |
| Boolean spectrum | which correlations survive marginals? | Walsh-Hadamard spectra, phase/chunk sweeps | higher-order order-dependent structure |
| family geometry | how does the signal move with n? | valuation forest, entropy landscape, residual maps | monoid laws and residual exceptions |
| arithmetic tomography | which coordinate causes the signal? | sieve scouts, matched buckets, flow residual scans | separated local/cutoff/block coordinates |
| certification | what does this imply about the real? | CF spikes, Mahler checks, algebraic smoke tests | narrow arithmetic certificates only |


## Read each layer against its background

The raw digit stream subtracts nothing. It is good for the first
"this almost looks normal" reaction and bad at explanation.

Positional-background views subtract the numeral system. In binary,
the epsilon identity is mostly the shape of writing integers in base
2. In decimal, digit-length blocks and sawteeth are the first-order
geometry. Do not call this ACM algebra until the positional term has
been removed.

Marginal views subtract the zeroth-order bias. Hamming bookkeeping
belongs here: for binary streams, the `v_2(n)` contribution to bit
balance has closed-form content. Entropy and k-gram charts are useful
only when read against that known drift and an appropriate shuffle or
synthetic control.

Compression views subtract the generic distribution of shapes. RLE is
not just compression here: in base 2, forced trailing zeros make
zero-runs a structural fingerprint. Raw RLE mass is dominated by
short runs; the algebra lives in excess or depletion against the
geometric run-length background.

Boundary views use information the flat stream hides. Boundary stitch
showed that joins are two-faced: trailing bits carry algebraic
constraints such as `v_2(n)`, while leading bits carry position inside
a bit-length class. Transition rows are not noise to be averaged away.
They are often the object.

Multiscale views are powerful and dangerous. Morlet and related
wavelet charts can expose decompressed structure in running-sum
residuals, but they also introduce detector periods, band-edge
effects, and edge artifacts. A wavelet picture graduates only after
controls show that the signal is not a scale/detector artifact.

Boolean-spectral views ask for structure that marginals cannot see.
The Walsh result is the model: robust coefficient cells, phase and
chunk-size checks, and an entry-order shuffle null. The important
claim was not merely "there are bright coefficients"; it was that
the robust family died under shuffle, so entry order carried the
signal.

Family-geometry views turn single-stream evidence into laws over
monoids. The valuation forest is the right pattern: show how much
`v_2(n)` explains, then subtract the depth-only prediction and look
for coherent residuals. The residual map matters because it tells us
where the master coordinate falls short.

Arithmetic tomography is the current frontier. It does not ask
whether a coordinate is associated with a signal. It asks what remains
after the obvious confounders are held fixed. In the ACM-Mangoldt
work, height and payload richness belong to the local `Lambda_n`
side; `Y = floor(X/m)` belongs to the cutoff side; smooth versus
uncertified blocks belong to totalisation; cheapest-sieve scouts
measure compositeness pressure.

Certification is last because it is the easiest place to overclaim.
Continued-fraction spikes, Mahler smoke tests, and algebraic probes
can certify narrow facts about a finite computation. They do not, by
themselves, prove rationality, algebraicity, normality failure, or
non-Liouville behavior. Treat them as certificates of a stated finite
claim unless a proof has actually been supplied.


## The subtraction rule

Every strong visual claim should say which background has been removed.

| view | default background to remove |
|---|---|
| running mean | finite-prefix and digit-length drift |
| sawtooth | radix/mantissa geometry |
| bit balance | closed-form positional or `v_2` drift |
| Hamming / entropy | bit-bias and length-class controls |
| RLE | geometric run-length decay |
| boundary stitch | interior-window baseline |
| wavelet / Morlet | shuffled, synthetic, and detector controls |
| Walsh | marginals plus entry-order shuffle |
| valuation forest | depth-only `v_2` prediction |
| flow residual | Mertens truncation term |
| matched buckets | held-fixed confounder coordinates |

If the structure vanishes after the appropriate subtraction, the
picture was mostly background. If it survives, the chart has earned
the next question.


## Reporting discipline

Do not reduce a rich object to one scalar unless the scalar is the
question. Keep the underlying arrays or CSVs whenever possible.
The Walsh audit is the example: the summary was plausible, but the
per-coefficient arrays were needed to see that the brightest robust
cells were not just `v_2(n)` rewritten.

For bucketed residuals, report mean, median, sign-fraction, and count.
If the mean and median disagree, the picture is tail-driven. That is
not a flaw, but it changes the claim.

For finite-looking spectra, state the scale. A dark tail in a run-
length spectrogram means "rare below this sample size and cap", not
"impossible." An almost finite scout palette at `X = 10000` has the
same status.

For visual structure, always ask which operation would destroy it:
entry-order shuffle, boundary erasure, radix-preserving synthetic
streams, `v_2`-matched controls, cutoff matching, or payload matching.
A chart that survives the right destroyer is evidence. A chart with
no destroyer is a sketch.


## Compact ladder

```text
raw stream
-> positional background
-> marginal bias
-> local morphology
-> boundary syntax
-> multiscale signal
-> spectral correlations
-> family geometry
-> arithmetic tomography
-> Diophantine certification
```

The working standard is simple: beautiful structure is allowed to
suggest a coordinate, but only controlled reduction is allowed to name
one.
