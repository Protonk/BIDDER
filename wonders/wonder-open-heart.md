# Wonder: The Open Heart

**Date entered.** 2026-05-01

**Category.** Wonder.

## Description

A specific image: the Q-lattice rendered as a Poincaré disk after
four orthogonal destructive transforms. Linear scale destroyed
(`slog`). Spatial location destroyed (2D FFT). Phase destroyed
(magnitude only). Euclidean geometry destroyed (Poincaré radial map
`r_disk = tanh(s · r_fft / 2)`). What survives is what the image
shows: a perpendicular bright cross at the disk's centre, a
curvilinear orthogonal arc grid filling the interior, the grid
denser and finer toward the rim, the same shape repeating at every
visible scale.

The four transforms are *each* the kind of operation that other
constructs over the integers tend to surrender to. Random sequences
flood spectrally under FFT. Generic concatenations lose all visible
structure under a hyperbolic distortion. Sparse-density collections
disappear when phase is dropped. The Q-lattice surrenders none of
its structure to any of the four — and the manuscript's reading is
that the surviving shape *is* the algebra: the DC cross is
first-order autocorrelation in `n` and `k` carrying through; the
arc grid is the prime-harmonic content surviving as sharp spectral
lines and compressing under the hyperbolic distortion; the
self-similar repeat at every scale is the signature of a structure
that is the algebra in the way that an X-ray of a bone *is* the
bone's calcification pattern.

What it isn't yet. Observable, not algebraically named. There is no
closed-form expression for which spectral content the orthogonal arc
grid corresponds to; no formal cross-check between the algebra and
the image's structure beyond the manuscript's prose claim that they
are the same thing seen two ways; no proof that the cross-at-every-
scale pattern continues at scales below the visible resolution. The
wonder is the gap between *the image is striking* and *we can name
what makes it survive.*

## Evidence

- `THE-OPEN-HEART.md:239-260` — the prose section that names the
  image and articulates the four-violences reading.
- `experiments/acm-champernowne/base10/q_distillery/q_lattice_4000_fft_poincare.png`
  — the image. Preserved at 32 MB through the Tier C prune precisely
  because this specimen lives in it.
- `experiments/acm-champernowne/base10/q_distillery/q_lattice_fft_poincare.py`
  — the render script (lattice → slog → 2D FFT → magnitude → Poincaré).
- `experiments/acm-champernowne/base10/q_distillery/q_lattice_4000_h6.npy`
  — the underlying lattice (h=6, the live height after Tier B).
- `experiments/acm-champernowne/base10/q_distillery/q_lattice_fft.py`,
  `q_lattice_fft_iterate.py`, `q_lattice_4000_fft_zoom.png` — the
  surrounding family of FFT-side experiments.

## Status

Suggestive. The image is reproducible from the lattice + render script;
the four-violences framing is well-articulated in the manuscript but
not formally cross-checked against the algebra. The interpretation —
"the shape *is* the algebra" — is the wonder's load-bearing claim and
is not yet a theorem.

## Aesthetic note

Look closely at the centre. There are two different asymmetries
visible just by eyeballing. The image's first impression is
symmetry — the perpendicular bars, the orthogonal arc grid, the
regular rim — and the part that registers as wonder is the place
where, on close inspection, the symmetry breaks in two independent
ways. The break is at the heart, but once you notice the break...it's not a symmetrical image AT ALL, is it? The image admits no exact symmetry. None. 

## Provocation

Three movements away from observation, toward something nameable:

- **Identify the arc grid algebraically.** The orthogonal arcs are
  presented as "prime-harmonic content surviving FFT as sharp
  spectral lines, compressing toward the rim under the hyperbolic
  distortion." What is the closed form for the arc family — which
  spectral coordinates, at which frequencies, at which intensities?
  Naming it would convert the wonder into a marvel.
- **A fifth violence.** The four destructive transforms are an
  empirical sequence; the survival of structure under all four is the
  finding. Choose a fifth orthogonal destruction (a different
  non-Euclidean metric, a wavelet decomposition, a permutation-
  invariant pooling) and ask whether the cross-and-arcs pattern still
  survives. If it does, that strengthens the "the shape is the algebra"
  reading; if it dies under the fifth, the four-violences framing is
  partly an artifact of the specific sequence chosen.
- **Cross-check at sub-visible scales.** The pattern repeats at every
  visible scale; whether it repeats at scales below visible resolution
  is open. A targeted high-zoom render at a sub-rim region, or a
  numerical check on the FFT content at frequencies the eye cannot
  resolve, would test the "every magnification" claim formally.

## Cross-references

- `wonder-cost-ladder.md` — the cost ladder asks how much harder the
  algebra gets at each height; the open heart asks what survives the
  algebra being mauled. Two faces of the same question about the
  substrate's structural reserves.
- `prodigy-L1-cliff-n2-h8.md` — the within-row autocorrelation that
  the DC cross visualises in the FFT. The prodigy's parity-flip is a
  piece of the same first-order autocorrelation content.
- `marvel-row-ogf-cliff.md` — the algebra that the image's shape, by
  the manuscript's reading, is. The arc grid would receive its
  closed-form name from the same kind of derivation that produced the
  row-OGF cliff.

## Discovery context

The image was rendered as a stress test of the Q-lattice's structure.
The choice of four-stage transform pipeline (slog → FFT → magnitude →
Poincaré) was chosen to compose four destructions, each killing a
different category of structure, and to ask whether anything visible
survived. The image's striking quality was visible immediately. The
prose section in `THE-OPEN-HEART.md` is the project's first articulation
of what was being seen: not noise, not artifact, but the algebra under
duress.

The image is the sole 32 MB asset deliberately preserved through the
Tier C image-size prune. Other lattice renders were resized to ≤ 1500
px on the longest axis; this one was kept at full resolution. The
preservation was a practical decision (the wonder lives in the
visible detail; degrading the image would have been a real loss), and
the entry notes it because the practical decision and the wonder's
locus point at the same thing without the project needing to claim it
had seen the wonder in advance.
