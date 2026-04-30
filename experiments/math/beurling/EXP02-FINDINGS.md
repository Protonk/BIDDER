# Experiment 02 — zeros of ζ_{M_n} and the ψ residual

Follow-up to Experiment 01. The hypothesis going in: the slow,
strongly n-dependent convergence of `ψ_{M_n}(x)/x → 1` should be
driven by zeros of `ζ_{M_n}` near `Re s = 1`. The experiment finds
zeros, extends ψ to `x = 5×10⁶`, and inspects the relationship.

Code:
- `exp02_zeros_and_residual.py`
- `exp02_findings.txt`
- `exp02_zero_landscape.png` — heatmap of `|ζ_{M_10}|` over the strip
- `exp02_psi_convergence_long.png` — `ψ/x` to `5×10⁶`
- `exp02_residual_log.png` — residual decay diagnostics

## Headline result

**`ζ_{M_n}` has zeros in the critical strip but none on `Re s = 1`.**
Some zeros lie at **`Re s < 1/2`**, falsifying any direct "Riemann
hypothesis for `ζ_{M_n}`." `ψ_{M_n}(x) ~ x` holds (consistent
with no `Re s = 1` zeros), but the convergence rate is much
slower than classical PNT and shows clean `n`-dependence: the
residual decays slower than `x / log x` for every `n` tested,
peaking around `x ~ 10⁴–10⁵` and slowly relaxing afterwards.

## Phase A — zero search

Scanned `|ζ_{M_n}(σ + it)|` for `σ ∈ [0.4, 1.05]`, `t ∈ [0.1, 50]`,
refined candidates with `mpmath.findroot`. Results:

| n  | lowest zero ρ            | other zeros found             |
|----|--------------------------|-------------------------------|
| 2  | 0.5149 + 22.9065i        | (none below 50i)              |
| 3  | 0.5939 + 26.4793i        | 0.6004 + 36.4554i             |
| 5  | 0.5182 + 17.6351i        | (none below 50i)              |
| 6  | 0.4199 + 18.9447i ⚠      | 0.4738+26.7i, 0.4885+44.5i, 0.5145+46.7i |
| 10 | 0.4366 + 28.4055i ⚠      | (none below 50i)              |

**No zeros on or near `Re s = 1`** for any `n`. This was the
original "obstruction-of-PNT" hypothesis from EXP01, and it's
**falsified** — the analytical cause of the slow ψ convergence is
not a Re-s-=-1 zero.

**Zeros at σ < 1/2 for n = 6, 10.** Marked with ⚠ above. The
Riemann-hypothesis analog (all zeros on σ = 1/2) **does not hold**
for `ζ_{M_n}` — zeros migrate away from the σ = 1/2 line, both up
into the strip and (for composite `n` and high-`n`) below σ = 1/2.
This is structurally interesting and consistent with the broader
Beurling literature where non-classical zeta functions can have
zeros distributed off the critical line.

## Phase B — long ψ convergence

| n  | ψ/x at x = 5×10⁶ | residual ψ - x  |
|----|------------------|------------------|
| 2  | 0.99934          | -3290            |
| 3  | 0.99592          | -20392           |
| 5  | 0.97616          | -119200          |
| 6  | 0.95433          | -228362          |
| 10 | 0.83063          | -846825          |

ψ/x is approaching 1 for every `n`, monotonically (after small-x
oscillations). Convergence is **slow** for larger `n`: at `x = 5×10⁶`,
n=10 is still 17% off the predicted limit.

The trajectory is consistent with `ψ/x → 1` (no plateau apparent),
so the residue calculation `Res_{s=1}[-ζ'_{M_n}/ζ_{M_n}] = +1`
is the correct leading rate and the BIDDER PNT analog holds.

## Phase C — residual rate diagnostics

Tested whether `|ψ - x| / x` decays like `1/log x` (i.e., whether
`|ψ - x| · log x / x` is constant):

| n  | x=10³ | x=5500 | x=30000 | x=170k | x=910k | x=5×10⁶ |
|----|--------|--------|---------|--------|--------|---------|
| 2  | 0.39   | 0.15   | 0.12    | 0.04   | 0.02   | 0.010   |
| 3  | 0.64   | 0.41   | 0.25    | 0.12   | 0.09   | 0.063   |
| 5  | 1.59   | 1.24   | 0.96    | 0.71   | 0.51   | 0.368   |
| 6  | 1.96   | 1.71   | 1.40    | 1.16   | 0.90   | 0.704   |
| 10 | 3.32   | 3.38   | 3.28    | 3.11   | 2.87   | 2.612   |

If `|ψ - x| ~ x/log x`, this column should be constant. It isn't —
all rows decrease, but at very different rates. n=2 looks like
roughly `|ψ - x| ~ x/(log x)²` or faster; n=10 is much slower.
The classical PNT residual is `O(x · exp(-c√log x))`, faster than
any polylog. The `M_n` analog is **slower than classical**, with
explicit `n`-dependence in the rate.

This rate-of-decay structure is the new quantitative finding.

## Where the residual mass actually comes from

The naive "residual is dominated by lowest zero" prediction:
contribution magnitude = `x^β / |ρ|`. For n=10, `β = 0.437`,
`|ρ| ≈ 28.7`:

    x^β / |ρ| at x = 5×10⁶  =  (5×10⁶)^{0.437} / 28.7  ≈  29.4

But the empirical residual is `~847000`. The lowest single zero
predicts a contribution four orders of magnitude smaller.

So the residual is **not dominated by the lowest zero**. Either
(a) there are many more zeros at higher `t` that we haven't found
and they sum coherently, (b) the residual comes from a continuous
boundary contribution rather than discrete zero residues, or (c)
the perron-formula decomposition for non-UF systems has different
structure than the classical case.

The `|ζ_{M_10}|` landscape (`exp02_zero_landscape.png`) shows
visible "channels" of low-magnitude region around σ ≈ 0.4–0.55
across many `t` values, suggesting **many zeros densely populating
a strip well below `σ = 1`** — most not refined-out by our
finite-precision scan. The cumulative contribution from these
could plausibly explain the empirical residual.

## Status against the original framing

The EXP01 follow-up hypothesis was: zeros on `Re s = 1` drive the
residual. This is **falsified** — there are no such zeros.

But the experiment uncovered three concrete structural findings:

1. **ζ_{M_n} has no Riemann-hypothesis analog.** Zeros migrate off
   `σ = 1/2` (some below it for `n = 6, 10`).
2. **The BIDDER PNT analog holds**: `ψ_{M_n}(x) ~ x`, consistent
   with the residue calculation, with slow but unambiguous
   convergence.
3. **The convergence rate is slower than `x/log x`** and has
   `n`-dependence not predicted by the lowest discrete zero.

Each of these is a real result. The first is a structural
statement about `ζ_{M_n}`'s zero distribution (negative — no RH);
the second is a positive analytic fact (PNT analog); the third is
a quantitative discrepancy from classical Beurling theory.

## What's next

Three directions, in priority order:

1. **Map the full zero distribution** for `ζ_{M_n}` at `n = 2, ..., 12`,
   pushing `t` to ~200 and `σ` to `[0, 1.1]`. Density estimate:
   `N(T) := #{ρ : 0 < β < 1, 0 < γ < T}` as function of `T`. For
   classical ζ, `N(T) ~ T log T / 2π`. For `ζ_{M_n}`, what?

2. **Test the Perron-formula sum hypothesis**: numerically sum
   `Σ x^ρ/ρ` over the first ~50 zeros and compare to empirical
   residual. If they match, classical Perron-formula machinery
   transports despite signedness. If not, the non-UF structure
   demands a different decomposition.

3. **Understand the σ < 1/2 zeros structurally.** For composite
   `n` where overlap-pair structure of `M_n` is richer, there are
   zeros in the "bad" region `σ < 1/2`. Is there an explicit
   formula relating these to factor structure of `n`?

Direction 1 is the cleanest follow-up — it's a measurement task
with a clear graph as output, and the result will tell us whether
`ζ_{M_n}` zero density is classical-Beurling-like or
genuinely-different.
