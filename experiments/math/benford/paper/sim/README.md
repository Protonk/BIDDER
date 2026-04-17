# Simulation plans and records

This directory collects the simulation plans for the BS(1,2) mantissa
rate-shape question — does the L₁ distance to uniform on the mantissa
circle decay as `exp(−c√n)`, `1/√n`, a mixture, or something else? —
along with the data and figures produced by prior runs.

The question is open because [MESSES.md §1](../MESSES.md) identified a
theoretical objection: the per-return Laplace-transform framework
predicts an algebraic tail `B · n^(−1/2)` on top of any stretched-
exponential transient, and phase-1 simulations can neither confirm nor
rule out the mixture on the observable window. Three complementary
plans triangulate on the answer; each attacks from a different angle.

---

## The program has two purposes

**Scientific discrimination.** Decide empirically among {`exp(−λn)`,
`exp(−c√n)`, `1/√n`, mixture, something else}. The paper's Theorem 1
rate claim is contingent on the outcome.

**Proof triage.** Inform [FIRST-PROOF.md](../FIRST-PROOF.md) gap 2 —
BENTHIC's B3 measures `ρ(M)` of the mode-coupling matrix empirically,
which tells us whether gap 2 (R4)'s spectral-gap target is achievable
before weeks of analytical work. If `ρ(M) ≈ 1`, there's nothing to
prove; if `ρ(M) < 1` with tight CI, there's a number to shoot for.

The two purposes use the same simulation runs but demand different
analyses. That's why three plans.

---

## Plans — a triangle, not a hierarchy

```
                TUKEYS-LADDER
               (shape family)
                     │
                     ↓ gates
                     │
  ALGEBRAIC-SIM-MESS-PLAN ←── coherence ──→ BENTHIC-MINKOWSKI-SIM
  (parameters within family)                (mechanism regime)
```

- **[ALGEBRAIC-SIM-MESS-PLAN.md](ALGEBRAIC-SIM-MESS-PLAN.md)** —
  parametric plan. Tests H_S (stretched-exp) against H_A (algebraic),
  and the MESSES-mixture form `A·exp(−c√n) + B·n^(−α)`, against
  pre-committed discriminants. **Authoritative** for the shared run
  specs (M0, S0, M1–M4, optional M4b) and the default execution
  schedule. Produces numerical estimates of `c, α, A, B` with
  bootstrap CIs once a parametric family is chosen.

- **[TUKEYS-LADDER.md](TUKEYS-LADDER.md)** — nonparametric,
  shape-first plan. Re-expression ladder, the local power-law exponent
  `s_log(n)` via LOESS at three bandwidths, segmented fits over five
  log-spaced windows, direct coefficient-reading plots. Diagnostic
  rather than inferential; **gatekeeper for which parametric family
  applies** before handoff to ALGEBRAIC's parameter-estimation machinery.

- **[BENTHIC-MINKOWSKI-SIM.md](BENTHIC-MINKOWSKI-SIM.md)** —
  mechanism-level plan. Works on the Fourier side in `‖h‖_{L²}`.
  Measures the mode-coupling matrix `M` of the return operator `T_R`
  empirically via runs B1–B3 and reports a regime — rotation-
  dominated, balanced, or injection-dominated — from `ρ(M)` compared
  to `γ₁^{c'}`. **Explainer** for why the observed shape is what it
  is; also supplies the proof-triage reading for FIRST-PROOF.

TUKEYS gates the family; ALGEBRAIC estimates parameters given the
family; BENTHIC sits on an independent axis and supplies mechanism.
The coherence check between BENTHIC's regime and ALGEBRAIC's fit is
what the authority map's adjudication resolves.

---

## Authority map and structured disagreement

Each plan contains an "Authority map" section with concrete
adjudication rules for its own data. The cross-document framing:
**structured disagreement among the three plans is a legitimate
scientific finding, not a failure mode.** The n*-based adjudication
in ALGEBRAIC's map produces specific paper wording for each case;
some disagreements survive adjudication and appear in the paper as
caveated or two-regime claims (see PNAS-PLAN's Theorem 1 variants).

Disagreement categories the three plans are designed to detect:

- TUKEYS says family outside {H_S, H_A, mixture} → ALGEBRAIC's
  fit is meaningless; paper needs more work.
- TUKEYS and ALGEBRAIC agree on family/parameters, BENTHIC regime
  disagrees → n*-based adjudication (ALGEBRAIC rule 4).
- All three agree → paper has a clean rate claim.
- Too noisy for any plan to identify → escalate N.

---

## Reading order

For someone onboarding cold:

1. [MESSES.md §1](../MESSES.md) — the forcing question. *Why* there
   is a three-plan program at all.
2. This README — the three-plan architecture and the two purposes.
3. The individual plans for operational detail.
4. [SIM-REPORT.md](SIM-REPORT.md) for what's already been run
   (symmetric phase-1 and biased phase-3) before the full program
   executes.

If reading for depth on the proof side:
- [FIRST-PROOF.md](../FIRST-PROOF.md) §2 for the open proof gap that
  the program's proof-triage purpose informs.
- [GAP2-LEMMA.md](../GAP2-LEMMA.md) for the withdrawn first attempt
  at gap 2 and why it was withdrawn (context for why B3 matters).

---

## Records

- **[SIM-REPORT.md](SIM-REPORT.md)** — minimal record of simulations
  already run for FIRST-PROOF gaps 3 and 4, preserved so a data
  appendix can be assembled without re-running.
- `data/` — raw outputs from past runs.
- `fig/` — figures produced from those outputs.

**Phase-3 biased-walk data as structural analog.** SIM-REPORT
documents a two-regime decay for biased walks: active-zone
ε-minorization phase, then post-escape Weyl rotation at algebraic
rate. This is the *empirical analog* of what BENTHIC predicts could
happen for the symmetric case under rotation-dominated or mixture
regimes. Not proof, but plausibility evidence that two-regime decay
is physically realizable for this walk family.

---

## Related paper material

- [MESSES.md](../MESSES.md) — outstanding issues flagged during
  proof drafting; §1 is the forcing motivation for these plans.
- [PNAS-PLAN.md](../PNAS-PLAN.md) — top-level paper plan, including
  Theorem 1 variants (T1a single-regime, T1b two-regime, T1c
  mixture) for each decision-rule outcome.
- [FIRST-PROOF.md](../FIRST-PROOF.md) — proof draft that these
  simulations are intended to support and triage.
