# PRIMAL-STARTS — five starting points

Five wildly different artistic explorations of the primality
findings in `../../survivors/primality/`. Starting points, not
finished pieces. The brief: be different from each other in form,
aesthetic, and observable. Goodness is welcome but not required.

## 1. THE COIL

A single delicate thread spiralling clockwise on the complex plane.

- **Substrate**: asymptotic `z(W) = (L1_prime_m − L1_bundle) +
  i(L1_comp_m − L1_bundle)` for W ∈ [5, 50+], from
  `../../survivors/primality/primality_surface.npz`. Possibly
  extended further to see whether the spiral grows or settles.
- **Aesthetic**: minimal, negative-space-dominant. The thread
  traces W as time. Colour shifts subtly along the trail (cool at
  small W, warm at large W). Stream-transition kicks visible as
  tiny perturbations in the curl. The thread approaches the
  origin at W ≈ 15–20 but does not pass through — the visual
  tension lives in that near-miss.
- **Form**: vector-style line drawing on a near-black ground.
  Could be ink-on-paper with a halo of ghost-trails for the
  pre-asymptote z(n, W) values at each W.
- **The move**: reduces the entire bracketing-rotation finding to
  a single elegant curve.

## 2. THREE TONGUES, BURIED

Three large flat colour regions stacked vertically, with a wound
through them.

- **Substrate**: the L1 trajectories at [2,10] k=400 for bundle,
  prime-cofactor survivors, composite-cofactor survivors, but
  rendered as *filled regions* not curves. Each curve is a
  horizontal band whose vertical position is the L1 value at each
  atom_index.
- **Aesthetic**: Rothko-style three large monochromatic bands —
  composite-m at top, bundle middle, prime-m bottom. At
  atom_index ≈ 250 a thin vertical chasm cuts through all three
  bands: the n=2 dip rendered as a wound. Stream transitions
  appear as faint vertical seams.
- **Form**: large flat colour regions with sparse dramatic
  anomalies. Closer to painting than chart. Big canvas.
- **The move**: turns the bracketing structure into atmosphere
  rather than measurement.

## 3. PRIME ATLAS

A celestial chart of survivor integers.

- **Substrate**: every survivor `c` at [2,10] k=400 (1338 of them)
  with its source d and cofactor primality. Compute prime
  factorisation per c.
- **Aesthetic**: each survivor is a star at coordinates
  `(log10(c), source_d)`. Star size: `log(c)`. Hue: warm for
  prime-cofactor, cool for composite-cofactor. Connect stars
  that share a prime factor with thin grey edges — those become
  the "constellations." Deep navy ground. Stars cluster
  horizontally by source d; the constellations bridge across
  bands.
- **Form**: dense scatter on a dark-sky background, in the style
  of a hand-drawn planispheric atlas. Could include star-chart
  ornamentation (compass rose, decade-boundary meridians).
- **The move**: makes the structural relationships between
  survivors visible as a network rather than statistics.

## 4. ECHO CATHEDRAL

Geometric architecture of the K-decade echoes.

- **Substrate**: the four detected peaks per n_0 from
  `../../survivors/echo_extend.npz` and the original lowK / largeK
  caches, across n_0 ∈ {2, 3, 5, 8, 12}.
- **Aesthetic**: render each peak as a vertical column on a log-K
  plane. Column height = peak amplitude. Column x-position = peak
  K on a log axis. Decade gridlines (K = 10², 10³, 10⁴, 10⁵, 10⁶)
  drawn as floor-lines of the cathedral. Stack the n_0 rows as
  parallel aisles, with each aisle's columns aligned to decades.
  Looking up the columns at the decade gridlines reveals the
  self-similarity directly.
- **Form**: isometric or axonometric architectural rendering in
  white-on-black, like Borromini studies or technical drawings of
  impossible buildings. Could be drafted lines, no fill.
- **The move**: turns the geometric self-similarity of the echo
  spacing into a literal geometric structure.

## 5. SURVIVOR TAPE

A long horizontal strip reading left to right.

- **Substrate**: the 1338 survivors at [2,10] k=400 in
  bundle-order (their first-appearance positions), each carrying
  three attributes: value c, source d, cofactor primality.
- **Aesthetic**: each survivor is a vertical tick on a horizontal
  strip. Tick height: full for prime-cofactor, half for
  composite-cofactor. Tick colour: one of nine colours encoding
  source d ∈ [2..10]. Tick x-position: bundle-order index. Reads
  left-to-right like punched tape, a music staff, or a DNA
  electrophoresis gel. Sparse early, dense in heavy-collision
  regions, with the n=2 dip visible as a vertical density change
  at atom ~250.
- **Form**: long-aspect-ratio panel (e.g. 12:1), mostly
  horizontal. Could be a printed scroll. Faint horizontal rules
  at fixed y-levels for stream transitions.
- **The move**: makes the survivor sequence linear and legible at
  the level of each individual integer, with primality and source
  encoded directly into the mark.

## What unites these

All five are derived from the same construction (`B_{[2,10], 400}`
and its primality stratification) but no two share a form. The
goal is to find which artistic register the construction wants to
sit in — a single elegant curve, an atmospheric painting, a
diagrammatic atlas, an architectural rendering, or a linear
inscription. Each will reveal something the others can't.

## 6. THE SHELLS  (added)

Concentric rings — `D_N*` mapped to ring fuzz.

- **Substrate**: orbit `{10ⁿ α} ∈ [0, 1]` for each of the five
  constructions, plus the star discrepancy `D_N*` of each.
- **Aesthetic**: five concentric rings on a near-black field. Each
  ring is the orbit projected onto the unit circle (angle = 2π α_n).
  Radial spread σ proportional to `D_N*` — sharper rings for lower
  discrepancy. Colour encodes construction; angular brightness/
  sparsity shows the orbit's actual non-uniformity.
- **Form**: dot cloud on five nested annuli. Innermost: prime-
  cofactor survivors (sharpest). Outermost: composite-cofactor
  survivors (fuzziest).
- **The move**: makes star discrepancy a literal visual variable —
  ring thickness IS `D_N*`. The bracketing finding (composite >
  bundle > prime) becomes ring-quality, instantly legible.

Files: `the_shells.py`, `the_shells.png`.
