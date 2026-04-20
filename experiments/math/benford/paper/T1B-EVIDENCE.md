# T1B-EVIDENCE

Paper-side summary of the empirical case for T1b. The detailed
clause-by-clause backstop is `sim/T1B-EVIDENCE-MAP.md`; the
source-faithfulness audit is
`sim/T1B-EVIDENCE-MAP-VERIFY-REPORT.md`.

## Commitment

This note takes T1b as the working theorem shape supported by
the current sim record.

Operational content:

- **Asymptotic.** L₁(P_n, Leb_T) ∼ B(ν) · n^{−1/2} as n → ∞,
  with α = 1/2 ν-universal and B(ν) ν-dependent, for any
  probability ν on ℝ \ {0} with a logarithmic moment and
  ν(ℤ[1/2]) = 0.
- **Pre-asymptotic transient.** For ν concentrated (sharp ICs),
  a stretched-exp transient A(ν) · exp(−c(ν) √n) dominates L₁ on
  n ≲ n*(ν) before crossing to the algebraic tail.
- **Hypotheses.** Symmetric probability measure on the four
  BS(1,2) generators {a, a⁻¹, b, b⁻¹}; ν(ℤ[1/2]) = 0.

PNAS-PLAN's current §2 Theorem 2 block still reflects the older
single-regime framing. Under T1b it should be rewritten as a
two-regime statement: an IC-dependent early stretched-exp
transient, and an asymptotic n^{-1/2} tail with IC-dependent B.

## Empirical anchors

| element | source |
|:--|:--|
| α = 1/2 direct sighting | M3 IC (b): free log-log fit α̂ = 0.525, R²(log n) = 0.9986 on [100, 600] at N = 10⁷ (`sim/m3_SUMMARY.md`, verified against `sim/m3_results.npz`) |
| ML(1/2) return-time consistency | S0: conditional Laplace-match with c_fit stable 0.179–0.195 and max residual shrinking from about 0.018 to 0.006 across n = 100 to 500 (`sim/s0_SUMMARY.md`) |
| τ_R first-excursion survival | First-excursion survival from the M1 IC fits slope −0.495 on [50, 10⁴], consistent with 1/√n (`sim/tau_R_tail_SUMMARY.md`) |
| Per-visit contraction | B3: empirical mode-coupling K̂ has ρ(K̂) = 0.924 from 40M excursions; B3 classifies this as injection-dominated (`sim/b3_SUMMARY.md`) |
| M4 corroboration on √2 | On n ≤ 3000, the √2 run stays measurably above the null floor, but α_local has not stabilized at 1/2 (`sim/m4_SUMMARY.md`) |
| Transient descriptor for the M1 √2 IC | Early-window stretched-exp fits are strong: c_hat = 0.506 on [20, 200] and c_hat = 0.498 on [20, 150] (`sim/m3_SUMMARY.md`, data from `sim/m1_b1_b2_results.npz`) |
| Transient IC-dependence | Observed c_hat ranges by IC class: dyadic 0.335–0.347; non-dyadic rational 0.374–0.543; irrational sharp 0.466–0.498; spread-E mixtures ≈ 0.356; E-uniform delta-m 0.137; near-uniform < 0.05 (`sim/t1b_unit_ball_SUMMARY.md`, `sim/root_two_checks_SUMMARY.md`) |
| Precision robustness | fp16/32/64/128 ladder: sub-fp64 zero-hit rates scale with fp_eps, fp64 is below detection at these volumes, and fp128 matches fp64 on M3 IC (b) (`sim/fp16_SUMMARY.md`, `sim/fp32_SUMMARY.md`, `sim/fp128_SUMMARY.md`) |

Only M3 IC (b) directly fits α on L₁. S0 and B3 are supporting
consistency checks, not independent α-measurements. The τ_R-tail
run is additional return-time evidence of 1/√n-type behavior on
the M1 IC; it supports the same general return-rate picture but
does not itself measure the L₁ exponent.

## Paper-side consequences

- **Theorem 1 wording.** Use the T1b pre-committed wording in
  PNAS-PLAN §"Theorem 1 variants." Include the ν(ℤ[1/2]) = 0 and
  symmetric-measure hypotheses explicitly.
- **Theorem 2 numeric.** State c ≈ 0.498 as the transient
  descriptor for the M1 √2 IC on the standard early window
  [20, 150], or c ≈ 0.506 on [20, 200], and not as a universal
  theorem constant. State the asymptotic as α = 1/2 with
  IC-dependent B.
- **Figure 1 substrate.** Three-walks comparison (BS(1,2) mix /
  pure-add / pure-mul) lives in `paper/FIG1-SUBSTRATE.md` with
  underlying sim at `sim/comparison_walks_SUMMARY.md`. It is an
  illustrative substrate for the M1 observable window, not an
  extra asymptotic proof.
- **§4 mechanism anchors.** The √n visit rate is anchored by
  S0's ML(1/2) match and the τ_R-tail sim's 1/√n first-excursion
  survival. The per-visit contraction is anchored by B3's
  ρ(K̂) = 0.924. The ε coordinate identity (the other §4
  anchor) lives in BINADE-WHITECAPS, not sim.

## What this does not claim

- A universal c in exp(−c√n). The measured c values are
  transient descriptors for particular ICs, and they vary across
  the IC panel.
- IC-invariance of B. The few loose B inferences we have differ
  substantially across ICs.
- α = 1/2 directly measured on the √2 IC. M4 supports the tail's
  existence on √2 at high significance (141/151 above q99) but
  does not pin α̂ to 0.5 within the n ≤ 3000 horizon we've run.
- α = 1/2 on dyadic ICs. R2 (restart) and R3 (absorb) conventions
  both hit the N = 10⁷ floor before α would be resolvable.
- Strong asymmetry behavior (d ≳ 0.05). Weak asymmetry (d = 0.01)
  leaves observable-window L₁ unchanged; strong asymmetry is
  untested on a clean computational envelope.
- Cross-group universality. Only BS(1,2) is tested; BS(1,p ≠ 2)
  would need a separate kernel.

## Known tensions

Three post-map sim findings affect how tightly the paper-side
story should be phrased.

- **Laplace-diagnostic** (`sim/laplace_diagnostic_SUMMARY.md`):
  the BS(1,2) E-process on the M1 IC is not literally a
  zero-drift simple random walk surrogate. Any paper-side
  mechanism language should therefore stay with empirical
  return-structure comparisons, not a literal SRW identification.
- **τ_R tail** (`sim/tau_R_tail_SUMMARY.md`): empirically
  supports a 1/√n-type first-excursion return tail on the M1 IC.
  This reinforces S0's return-count evidence but does not extend
  it to a theorem-level uniform statement.
- **Return-marginal** (`sim/return_marginal_SUMMARY.md`): pooled
  post-burn σ̃ concentrated on arc [1 − log₁₀ 2, 1) at
  R = {|E| ≤ 10}. This pressures the proof-route identification
  step π_T ν_R = Leb_T, but it is a proof-architecture issue, not
  a change to the observed T1b phenomenology.

Only the first of these forced a map-side wording change. The
second is supportive context. The third matters to Route 1',
not to the empirical T1b claim itself.

## Conditions for writing the main draft

The current record is enough to draft Theorem 1 and a revised
two-regime Theorem 2, provided the wording stays within the
limits listed above. This note is meant to be the paper-side
entry point; the sim map remains the detailed backstop.

Remaining paper-side substrates identified by the verification
audit:

- **Figure 1 substrate:** done at `paper/FIG1-SUBSTRATE.md`.
- **§7 robustness atlas:** not yet written. Covers precision
  (covered by this doc indirectly via the precision-robustness
  anchor), weak asymmetry (ditto), pure-addition non-convergence
  (substrate in `sim/comparison_walks_SUMMARY.md`), biased
  generators (phase-3 convergence beyond d = 0.01 — evidence
  location unclear), base change (b ∈ [2, 40] — evidence
  location unclear). A separate `paper/ROBUSTNESS-ATLAS.md`
  will handle these; two items there may be genuine evidence
  gaps requiring separate sim work.
- **PNAS-PLAN §2 Theorem 2 rewrite:** separate editing pass,
  not a paper-side doc.

## References

### Primary sim sources (anchors)

- `sim/T1B-EVIDENCE-MAP.md` — master clause-by-clause evidence
  map (refreshed 2026-04-19).
- `sim/m3_SUMMARY.md` — α direct sighting on IC (b).
- `sim/m1_b1_b2_SUMMARY.md` — M1 canonical √2 IC data.
- `sim/m4_SUMMARY.md` — long-horizon √2 corroboration.
- `sim/s0_SUMMARY.md` — ML(1/2) Laplace-match on return counts.
- `sim/b3_SUMMARY.md` — per-visit contraction.
- `sim/t1b_unit_ball_SUMMARY.md` — 13-IC panel, weak asymmetry,
  smooth-IC.
- `sim/root_two_checks_SUMMARY.md` — φ vs √2, rational IC
  restart vs absorb.
- `sim/fp16_SUMMARY.md`, `sim/fp32_SUMMARY.md`,
  `sim/fp128_SUMMARY.md` — precision ladder.

### Post-map context (reinforces or pressures framing)

- `sim/tau_R_tail_SUMMARY.md` — reinforces ML(1/2) return-time
  structure.
- `sim/laplace_diagnostic_SUMMARY.md` — pressures the
  null-recurrent framing (addressed in map clause v refresh).
- `sim/return_marginal_SUMMARY.md` — pressures proof-route
  identification (see `MESSES.md` §Mess #2).
- `sim/conditional_decay_SUMMARY.md` — rules out a-step
  Diophantine as the transient mechanism (map doesn't propose a
  mechanism; non-conflicting).

### Paper-side companions

- `paper/FIG1-SUBSTRATE.md` — Figure 1 three-walks substrate.
- `paper/ALT-SLOWDOWN-MECHANISM.md` — alt-slowdown footnote
  material for §6 kicker (independent of T1b).
- `paper/MESSES.md` — open proof-architecture problems;
  Mess #1/#2/#3 updates (2026-04-19) carry the Mess-era sim
  findings.
- `paper/SECOND-PROOF.md` — live gap list under T1b, including
  the §4 identification step that Mess #2 pressures.
