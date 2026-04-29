# Continued fractions of ACM-Champernowne reals

This directory holds the CF / spike thread for
`C_b(n) = 0 . p_1(n) p_2(n) p_3(n) …` — closed form for the
boundary-spike size, off-spike denominator decomposition, family
classification by `ord(b, n)`, cross-base and d-extension panels,
and the conditional irrationality measure.


## Reading order

1. `MEGA-SPIKE.md` — master document. Master statement
   `log_b(a_{i_k}) = T_k − 2 L_{k−1} + log_b(b/(b−1)) − O(b^{−k})`,
   with `T_k` read from actual atom counts and the smooth-count
   algebra giving the closed-form spike scale `S_k = D_k − C_{k−1}`;
   derivation of the CF correction; pointers to the empirical and
   analytic state.
2. `MULTI-K-RESULT.md` — k ∈ {2, 3, 4} confirmation at b = 10;
   isolation of the universal `log_b(b/(b−1))` constant; geometric
   `b^{−k}` decay of the residual.
3. `OFFSPIKE-RESULT.md` — `δ_k(n) = (n − 1) k + offset(n)`
   decomposition; substrate-driven slope, per-`n` offset.
4. `EXTENDED-PANEL-RESULT.md` — n ∈ {2..13} at b = 10, d = 4;
   Family A / B / D / F + transient classification.
5. `PRIMITIVE-ROOT-FINDING.md` — extended prime-order panel
   `n ∈ {17, 19, 23, 29, 31}`; family selection rule by
   `ord(b, n) ∈ {1, 2, n − 1}`; intermediate ord open.
6. `MECHANISTIC-DERIVATION.md` — partial proof. Slope `(n − 1)`
   from cofactor cycles; offset from substrate divisibility for
   ord = 1; ord = 2 simple chain refuted; intermediate ord open.
   Step 3 (lifting integer divisibility to a convergent denominator
   factor) is the load-bearing missing piece.
7. `CROSS-BASE-RESULT.md` — `(b − 2)/(b − 1)` prefactor structure
   confirmed at b ∈ {3, 4, 6, 8, 10, 12}.
8. `D5-RESULT.md` — d = 5 at b = 10; relative gap ~10× smaller
   than at d = 4 across the panel.
9. `MU-CONDITIONAL.md` — derivable conditional irrationality
   measure `μ(C_b(n)) = 2 + (b − 1)(b − 2) / b` under "spikes
   dominate the approximation budget"; same gap as step 3.

The structural reading of the spike formula — what's grand,
mundane, beautiful, contingent in it — is at
`arguments/MEGA-SPIKE-FOUR-WAYS.md`.


## Compute artifacts

| script | consumed by | data |
|---|---|---|
| `cf_spikes.py` | (foundational empirical scan) | `cf_spikes.csv`, `cf_spikes_n*.png`, `cf_spikes_summary.txt` |
| `cf_spikes_extended.py` | `CROSS-BASE-RESULT.md` | `cf_extended.csv`, `cf_extended_summary.txt`, `cf_extended_run.log` |
| `cf_spikes_d5.py` | `D5-RESULT.md` | `cf_d5.csv`, `cf_d5_summary.txt`, `cf_d5_run.log` |
| `spike_drift_table.py` | `MEGA-SPIKE.md` | `spike_drift_table.csv`, `spike_drift_summary.txt` |
| `spike_drift_multi_k.py` | `MULTI-K-RESULT.md` | `spike_drift_multi_k.csv`, `spike_drift_multi_k_summary.txt` |
| `spike_drift_extended.py` | `EXTENDED-PANEL-RESULT.md`, `PRIMITIVE-ROOT-FINDING.md` | `spike_drift_extended.csv`, `spike_drift_extended_summary.txt` |
| `offspike_inflation.py` | `OFFSPIKE-RESULT.md` | `offspike_inflation.csv`, `offspike_inflation_summary.txt` |

`MAHLER-CHECK.md` documents the pipeline smoke test (Mahler's
`a_4 = 149083` reproduction for the classical Champernowne
constant) used to validate the CF runner.


## Cross-references

- `core/Q-FORMULAS.md`, `core/FINITE-RANK-EXPANSION.md` — local Q_n
  algebra; coupling-layer empirics live here.
- `core/BLOCK-UNIFORMITY.md` — closed-form n-prime block counts that
  give `T_k`.
- `arguments/MEGA-SPIKE-FOUR-WAYS.md` — structural critique.
- `experiments/acm-flow/STRUCTURE-HUNT.md` Phase 3.1 — overall
  position of this work in the project flow.
- `experiments/math/hardy/SURPRISING-DEEP-KEY.md` — instance list
  including the CF mega-spike collapse.


## Open

1. **Step 3 of `MECHANISTIC-DERIVATION.md`.** Pin `q_{i_k − 1}` to
   a specific form involving substrate divisibility. ord = 1 clean,
   ord = 2 simple chain refuted, intermediate ord (n = 13, 23, 31)
   undecided.
2. **Off-spike denominator process.** `L_{k−1}` is fit by
   `C_{k−1} + (n − 1) k + offset(n)` at boundary endpoints; the
   off-spike intermediate convergents between consecutive spikes
   are not modelled.
3. **Conditional μ verification.** `MU-CONDITIONAL.md` derives
   `μ = 2 + (b − 1)(b − 2) / b` conditional on "spikes dominate";
   the conditional is open in the same direction as (2).

Items (1), (2), (3) are the same gap viewed from three angles:
the off-spike CF process between boundary spikes. Closing one
closes the others.
