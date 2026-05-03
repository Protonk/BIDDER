# The Cabinet, First Vitrine

Nine specimens. Two marvels. Prodigy, sport, monster — one each. Two
wonders. Two curiosities (one live, one retired). The cabinet's six
categories are all populated; the curiosity drawer also opened its
retired sub-shelf, folded in from the proto-cabinet `nasties/`. The
categories are not a partition; multiple specimens per category is
the natural shape when the substrate keeps offering more than one
finding of a given kind.

## Marvels

- [The Row-OGF Cliff](marvel-row-ogf-cliff.md) — the alternating
  binomial-tau sum was free to be infinite for every `k'` and chose
  to terminate at `Ω(k') + 1` instead, with the same multinomial
  number appearing at the kernel-zero boundary and as the leading
  coefficient. Anchored.
- [Generalised Family E](marvel-generalised-family-e.md) — the
  lucky-locus closure that turned out to be a sibling of clause 3
  rather than a new mechanism. A `(qp, m_min)` parameterisation
  closes 69 of 96 spread-zero cells outside the proven substrate
  regimes, with the same divmod argument as Family E and clause 3
  recovered as the special case `qp = 1, δ = 0`. All 46 swept
  groups match prediction exactly. Anchored.

## Prodigies

- [The L=1 Sign-Flip Across h-Parity](prodigy-L1-cliff-n2-h8.md) —
  the within-row lag-1 vertical autocorrelation flips sign with the
  parity of `h`. Looked like a sign-convention bug for the better
  part of a session; turned out to be the off-diagonal class-pair
  contribution doing exactly what the master expansion forces it to
  do.

## Sports

- [The N=P Riemann-Sum Identity](sport-riemann-sum-identity.md) —
  `bidder.cipher`'s prefix-mean Monte Carlo estimate equals the
  Riemann sum exactly at `N = P`, independent of key, integrand, or
  cipher internals. The cipher's whole crypto apparatus is irrelevant
  at this one sample size; the result falls out of "π is a bijection"
  in a one-line proof. *"There's no reason that should work."*

## Monsters

- [The lcm-not-Factorial Denominator](monster-lcm-not-factorial.md) —
  `denom(Q_n(m))` divides `lcm(1, …, ν_n(m))`, not `h!`. The lcm
  form is uglier in every conventional sense — does not factor
  cleanly, no combinatorial reading, sub-factorial growth rate via
  Chebyshev's `ψ` — and it is the denominator the construction
  forces. The substrate is constitutively unable to be `h!`-pretty,
  and the offence traces back to why the bound is sharp.

## Curiosities

- [The Two Tongues](curiosity-two-tongues.md) — `C_Surv` tracks
  the bundle's leading-digit L1 deviation cell for cell, including
  through the n=2 dip; the `l1_grid` heatmap shows the agreement
  is generic across `(K, n_0) ∈ [10, 1000]²`. Probed twice. The
  `differences/` chain reframed `C_Surv` as an
  `H(stream | integer) = 0` optimizer and the magnitude tracking
  as its L1-layer footprint. The `dsubn` D_N work carried the
  bracketing forward to star discrepancy and localized a
  mirror-symmetric cofactor decomposition of the parent's orbit
  residual (EXP-DSUBN-04). What's still open: K-stability
  persistence at `K → ∞` and the arithmetic coordinate governing
  the mirror partition. *Deadline: 2026-Q3.*
- [The first_digit Pothole](curiosity-retired-first-digit.md)
  *(retired)* — `first_digit(8)` returned `7` because
  `int(10**frac)` truncated `7.999999999999999`. Eleven integers in
  `[1, 9999]` hit the trap, all with exact-integer base-10
  mantissas — the bug fires exactly where the math is cleanest.
  Folded in from the proto-cabinet `nasties/` as a retired
  curiosity (`nasties/` has since been deleted).

## Wonders

- [The Cost Ladder](wonder-cost-ladder.md) — working at successive
  heights costs roughly an order of magnitude more per rung. There
  is no theory yet for the rate, no instrumentation yet for the
  measurement, and no firm view yet on whether *cost* here is one
  thing or three things in disguise.
- [The Open Heart](wonder-open-heart.md) — the Q-lattice rendered
  through four orthogonal destructive transforms (slog, 2D FFT,
  magnitude-only, Poincaré radial map) refuses to surrender its
  structure. A perpendicular DC cross, an orthogonal arc grid filling
  the disk, the same shape at every visible scale. The manuscript's
  reading is that the shape *is* the algebra; the wonder is the gap
  between observation and theorem.

---

All six categories are populated. A reassignment log, a glossary, a
cross-reference index, a graveyard for aged-out curiosities: each
one comes when an entry forces it, not before. The curiosity shelf
in particular has its first deadline (2026-Q3); when it lands, the
graveyard or the promotion log will earn its file.
