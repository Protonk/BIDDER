# Structural Signatures

This note collects a narrow packet of binary ACM findings that look
stable enough to reuse elsewhere in the repo without rereading the
full experiment notes.

It is about **measured signatures**. The broader symbolic-dynamics
boundary condition — that binary ACM streams are not expected to be
finite-state recognizable — is tracked separately in
[FINITE-RECURRENCE.md](FINITE-RECURRENCE.md).

The packet organizes into two families:

- **Valuation-driven local structure**:
  entry-local valuation bookkeeping, and the boundary barcode that
  visibly realizes it.
- **Order-dependent residual structure**:
  the Walsh family and the detrended disparity residual.

The four sections below are therefore four observables, not four
independent fundamentals.

## Cross-monoid join

The table uses the controlled monoid panel from
[disparity/DETRENDED_RDS.md](disparity/DETRENDED_RDS.md) as the row
set.

| `n` | `v_2(n)` | `⟨v_2(entry)⟩` | `Δentry` | stripe | Walsh/shuf | resid/`√t` |
|---:|---:|---:|---:|---:|---:|---:|
| 3   | 0 | 1.00 | +1.00 | 0 | 1.28x (34/44) | 12.10 |
| 5   | 0 | 1.00 | +1.00 | 0 | 1.24x (36/44) | 10.45 |
| 7   | 0 | 1.00 | +1.00 | 0 | 1.21x (37/44) | 8.02 |
| 2   | 1 | 1.00 | +0.00 | 1 | 1.26x (33/44) | 8.64 |
| 6   | 1 | 1.80 | +0.80 | 1 | 1.22x (37/44) | 5.64 |
| 4   | 2 | 2.33 | +0.33 | 2 | 1.25x (29/44) | 8.03 |
| 12  | 2 | 2.82 | +0.82 | 2 | 1.25x (44/44) | 7.70 |
| 8   | 3 | 3.57 | +0.57 | 3 | 1.23x (36/44) | 9.26 |
| 16  | 4 | 4.73 | +0.73 | 4 | 1.24x (38/44) | 9.73 |
| 32  | 5 | 5.84 | +0.84 | 5 | 1.15x (36/44) | 11.12 |
| 64  | 6 | 6.90 | +0.90 | 6 | -- | 11.93 |
| 128 | 7 | 7.95 | +0.95 | 7 | -- | 12.40 |
| 256 | 8 | 8.97 | +0.97 | 8 | -- | 12.66 |

Notes:

- `Δentry = ⟨v_2(entry)⟩ - v_2(n)`. It is zero only for `n = 2`. Every
  other measured row has a positive entry-level lift over the monoid
  label, which is why the per-entry correction in section 1 is not
  optional once you leave `n ∈ {1, 2}`.
- `stripe` is the forced zero-stripe width immediately left of the join
  in boundary windows.
- `Walsh/shuf` is a synthesis metric derived from
  [`forest/walsh/walsh_spectra.npz`](forest/walsh/walsh_spectra.npz)
  and [`forest/walsh/walsh_controls.npz`](forest/walsh/walsh_controls.npz):
  the mean over the 44 robust cells of `P_real[s] / P_shuf[s]`
  (per-cell ratios, then averaged — not ratio of means). The count in
  parentheses is how many of those 44 cells have `P_real[s] > P_shuf[s]`
  for that monoid. Blank cells mean the Walsh panel was only run for
  `n = 2..32`. The replay script
  [`forest/walsh/walsh_shuf_join.py`](forest/walsh/walsh_shuf_join.py)
  prints this column directly from the two `.npz` files; rerunning it
  is the right move whenever the Walsh panel is regenerated.
- `resid/√t` is `|res_pe|max / √n_bits` after per-entry detrending, as
  reported in
  [`disparity/detrended_rds_summary.csv`](disparity/detrended_rds_summary.csv).

The join is not the theory. It is the shared ground. It makes visible
that the valuation family and the order-dependent family are measured
on overlapping but not identical territory.

## 1. Entry-local valuation bookkeeping

**Claim**

Bit-balance sees `v_2(entry)`, not `v_2(n)` alone. The monoid label is
a coarse tag except in the degenerate cases where every entry has the
same valuation.

**Evidence in repo**

- [HAMMING-BOOKKEEPING.md](HAMMING-BOOKKEEPING.md) now states the right
  summary directly: for `n = 1` and `n = 2`, `v_2(monoid)` is a fine
  label; for `n = 2^m` with `m >= 2` and for composite `n`,
  `v_2(entry)` varies and the formula must be applied per-entry.
- [DETRENDED_RDS.md](disparity/DETRENDED_RDS.md) tests this at stream
  level. In its 13-monoid panel, the per-entry correction collapses the
  endpoint residual from `-6264` to `+11` for `n = 12` and from
  `-2739` to `+158` for `n = 4`.
- In the join table above, `Δentry` is zero only for `n = 2`. Every
  other measured monoid in the panel carries a positive entry-level
  lift over the monoid label.

**Relation to other observables**

This is the anchor observable for the valuation family. The boundary
barcode in section 2 is its local visible realization. The detrended
residual in section 4 depends on subtracting this first-order drift
correctly.

**Statistical confidence**

High. This is the strongest claim in the packet because it has both a
closed-form derivation and a controlled stream-level check.

**Semantic confidence**

High. The mechanism is explicit: the trailing-zero penalty and the
bottom-bit constraint bonus depend on the valuation of each integer.

**Falsification**

Any controlled panel where per-entry detrending fails systematically
while the per-monoid `v_2(n)` detrender succeeds would force retraction.
So would a per-`(n, d)` cell analysis that contradicts the closed form.

**Next check**

Rerun [`detrended_rds.py`](disparity/detrended_rds.py) on a broader odd
and composite panel at the same `100_000`-bit target and append the same
`Δentry` and residual columns to the CSV summary.

## 2. Boundary barcode

This section has two sub-claims with very different epistemic status,
and the seven-field shape is applied to each in turn rather than mashed
together.

**Claim (forced part, by construction)**

For `n = 2^m`, every entry is divisible by `2^m`, so the rightmost `m`
columns immediately left of the join are exactly zero. For mixed even
`n` with `v_2(n) = m`, the same forced stripe of width `m` holds. For
odd `n`, no column left of the join is forced. Column `0` is always
the leading `1` of the incoming entry.

**Claim (speculative part)**

Boundary windows may also carry directional or comma-code-like
structure beyond the forced trailing zeros — a right-side gradient
that depends on position within the bit-length class, and a run-length
distinctness sufficient for self-synchronization. These are raised in
[BOUNDARY_STITCH.md](forest/boundary_stitch/BOUNDARY_STITCH.md) but
not yet measured under controls.

**Evidence in repo**

- The forced part follows directly from the n-prime definition
  ([HAMMING-BOOKKEEPING.md §Setup](HAMMING-BOOKKEEPING.md)) and is the
  boundary-local view of section 1.
- [BOUNDARY_STITCH.md](forest/boundary_stitch/BOUNDARY_STITCH.md)
  states the local rule and motivates the speculative parts under
  *What Might Surprise Us*.
- The rendered panel
  [boundary_stitch.png](forest/boundary_stitch/boundary_stitch.png)
  shows the forced effect on a mixed panel of odd, even, and
  power-of-two monoids.
- Column-mean check from
  [`boundary_stitch.py`](forest/boundary_stitch/boundary_stitch.py)
  on its default panel (display window `[-3, +3]`):
  `n = 2` and `n = 6` have column `-1 = 0.000`;
  `n = 4` and `n = 12` have columns `-2, -1 = 0.000`;
  `n = 8, 16, 32, 64` have columns `-3, -2, -1 = 0.000` within the
  displayed window;
  odd `n = 3, 5` have column `-1 ≈ 0.499`.
  This is a sanity check on the visualization pipeline, not a
  measurement of the forced claim — the forced columns are guaranteed
  by construction.

**Relation to other observables**

The forced part is the boundary-local projection of section 1, not a
separate first principle. It is a plausible local ingredient in the
order-sensitive signatures of sections 3 and 4, though the speculative
parts have not been measured against those.

**Statistical confidence**

For the forced part: by construction, no statistical claim to make.
For the speculative parts: not yet measured under controls.

**Semantic confidence**

High for the interpretation of the dark left stripe as forced trailing
zeros from `2^m | nk`. Lower for the comma-code reading and the
right-side gradient.

**Falsification**

For the forced part, the only failure mode is a buggy pipeline — a
script that misindexes the window, mis-converts integers to bits, or
computes the join wrong. The column-mean check above is the standing
sanity test against that. The forced claim itself cannot be falsified
empirically; it follows from `2^m | nk`.
For the speculative parts: a controlled comparison of `m`-zero run
counts at boundaries versus non-boundary interior windows that fails
to separate them would close the comma-code reading. A stitch image
that shows no right-side gradient across a full bit-length class
would close the directional reading.

**Next check**

Extend [`boundary_stitch.py`](forest/boundary_stitch/boundary_stitch.py)
with an interior-window control and measure the false-positive rate
for `m`-zero runs at boundaries versus non-boundary windows for
`n = 2^m`. This is the test that would promote the speculative
self-synchronization reading from "raised" to "measured."

## 3. Order-sensitive Walsh signature

**Claim**

Binary ACM streams carry a real higher-order Walsh family. Under the
current robustness ladder there are 44 robust cells, all 44 die under
entry-order shuffle, and the family splits into three populations:
`length + v_2`, `length-only`, and `neither control reproduces`.

**Evidence in repo**

- [WALSH.md](forest/walsh/WALSH.md) already gives the portable claims in
  exactly this form and identifies the stable core `30, 246, 255`.
- The same note shows that entry order is the dominant discriminator:
  shuffling the same entries destroys all 44 robust cells.
- In the join table above, the monoid-level `Walsh/shuf` metric is
  above `1` for every measured row in the shared panel, ranging from
  `1.15x` to `1.28x`, with `29` to `44` of the 44 robust cells above
  shuffle for each measured monoid. `n = 4` is the lowest count at
  `29/44`, four cells below the next-lowest measured monoid; consistent
  with `n = 4` being the smallest mixed-`v_2(entry)` monoid in the
  panel, and worth watching as the panel is extended.

**Relation to other observables**

This is the spectral observable for the order-dependent family. It
corroborates section 4 in a different domain. Sections 1 and 2 explain
some of the Walsh family, but not all of it.

**Statistical confidence**

High. The result sits on a multi-stage robustness bar and explicit
controls (`shuffle`, `length`, `v_2`, phase, chunk size).

**Semantic confidence**

Medium-low. We know that order matters and that the family decomposes
usefully under controls. We do not yet know what many of the surviving
cells encode.

**Falsification**

A rerun on the same panel and normalization that fails to recover the
44-cell family, or shows shuffle leaving comparable power in a large
fraction of those cells, would force a rewrite.

**Next check**

Rerun [`walsh.py`](forest/walsh/walsh.py) and the existing Walsh
post-process at `k = 4` and `k = 5` so boundary-straddling chunks
separate cleanly from interior chunks. That is the missing control the
current `k = 8` note cannot provide.

## 4. Detrended disparity residual

**Claim**

After subtracting the per-entry closed-form drift, a coherent
low-frequency residual survives. Shuffle often weakens it sharply. In
the current `n = 3` wavelet follow-up, strict geometric spacing of the
strongest excursions is disfavored under the present detector.

**Evidence in repo**

- [DETRENDED_RDS.md](disparity/DETRENDED_RDS.md) establishes the core
  result directly: after per-entry detrending the residual is not noise
  and typically reaches `8–13 · √n_bits`, while shuffled controls are
  often much smoother.
- In the shared panel, the measured residual size
  `|res_pe|max / √t` ranges from `5.64` to `12.66`.
- The same note shows concrete shuffle collapses, for example
  `n = 4: 8.03 -> 1.23` and `n = 12: 7.70 -> 0.63`.
- [KINK_DECOMPRESSION.md](disparity/rds_wavelet/KINK_DECOMPRESSION.md)
  now states the conservative follow-up result: under the present
  detector, extracted notch positions are much less consistent with
  strict geometric spacing in `t` than with a slower growth law. The
  source note also reports an affine-fit summary, but only as caveat
  and follow-up; the headline this packet lifts is the anti-geometric
  one.

**Relation to other observables**

This is the time-domain companion to section 3. It depends on section 1
for the right detrender. It is not independent of the Walsh story; it
is a different readout of the same order-sensitive family.

**Statistical confidence**

High for the existence of a post-detrending residual and for the claim
that shuffle weakens it on the current panel. Medium for the detailed
spacing law: the kink analysis is `n = 3` only and explicitly
detector-specific.

**Semantic confidence**

Medium for the existence of a slow order-dependent signal. Low for what
its dominant scale or notch geometry means.

**Falsification**

Longer prefixes or broader panels that drive the per-entry-detrended
residual into the fair-walk envelope would force retreat. So would a
detector sweep that makes the `n = 3` ratio panels flat and genuinely
geometric.

**Next check**

Add an event-extraction mode to
[`detrended_rds_n3.py`](disparity/rds_wavelet/detrended_rds_n3.py) that
records residual extrema and compares them to power-of-two crossings.
If the alignment looks real, rerun
[`kink_decompression_n3.py`](disparity/rds_wavelet/kink_decompression_n3.py)
on `[1k, 5k]` and `[5k, 25k]`.

## What this packet does not yet explain

- It does not reduce the order-dependent family to the valuation
  family. Walsh and detrended disparity both say something survives
  after the first-order valuation story is accounted for.
- It does not show that the boundary barcode alone explains the
  spectral or disparity signatures.
- It does not turn the `n = 3` kink note into a general spacing law.
  The anti-geometric result is real; the broader spacing model is still
  open.
- It does not extend automatically to other bases or to BIDDER output.

## Staleness

This note is stale whenever the portable-claims block, "What this
establishes" block, or equivalent compact summary of one of its source
notes changes materially.
