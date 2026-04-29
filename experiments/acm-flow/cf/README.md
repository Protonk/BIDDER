# Continued fractions of ACM-Champernowne reals

Single home for the CF / spike thread on `C_b(n) = 0 . p_1(n) p_2(n) p_3(n) …`.
Consolidates work that previously lived in
`experiments/acm-champernowne/base10/cf/` (the original Brief 2 scan)
and `experiments/acm-flow/mega-spike/` (the closed-form thread).

The flat layout matches the prior `mega-spike/` style; the README does
the role-marking work that subfolders would otherwise do. The
"mega-spike" name has been retired at the folder level — it remains
a useful narrative shorthand for the d=k boundary specialisation, but
the work as a whole is CF, not specifically mega-spike.


## Reading order (canonical thread)

1. `MEGA-SPIKE.md` — the closed-form spike scale and the
   two-stream framing. The formula
   `log_b(a_k) ≈ T_k − 2 L_{k−1} + log_b(b/(b−1))` first lands here.
2. `MULTI-K-RESULT.md` — k ∈ {2, 3, 4} confirmation; isolates the
   `log_b(b/(b−1))` boundary-truncation factor.
3. `OFFSPIKE-RESULT.md` — `δ_k(n) = L_{k−1} − C_{k−1} = (n−1)k + offset(n)`
   decomposition; substrate-driven slope plus per-n scalar.
4. `EXTENDED-PANEL-RESULT.md` — n ∈ {2,3,4,5,6,7,10,11,13} at b=10, d=4.
5. `PRIMITIVE-ROOT-FINDING.md` — `ord(b, n)` family classification:
   Family A (`offset = log_b(b/n)`) vs Family B (`offset = log_b(b/n²)`)
   for ord ∈ {n−1} vs ord ∈ {1, 2}; intermediate ord open.
6. `MECHANISTIC-DERIVATION.md` — partial proof; step 3 (link from
   substrate divisibility to convergent denominator factor) is the
   open analytic gap. ord=1 clean, ord=2 simple chain refuted, ord
   intermediate undecided.
7. `../../../arguments/MEGA-SPIKE-FOUR-WAYS.md` — Grand / Mundane /
   Beautiful / Contingent reading of the closed-form work; names
   `L_{k−1}` (the off-spike denominator process) as the load-bearing
   unmodelled scalar.
8. `CROSS-BASE-RESULT.md` — cross-base validation; `(b−2)/(b−1)`
   prefactor structure confirmed for b ∈ {3, 4, 6, 8, 12}.
9. `D5-RESULT.md` — d=5 push at b=10; extends multi-k from {2,3,4}
   to {2,3,4,5}.
10. `MU-CONDITIONAL.md` — derivable conditional irrationality measure
    `μ(C_b(n))` from the spike formula; depends on the off-spike
    denominator question that `L_{k−1}` carries.


## Status table

| doc | role | one-line |
|---|---|---|
| `MEGA-SPIKE.md` | canonical (formula's first home) | closed-form spike scale + two-stream framing |
| `MULTI-K-RESULT.md` | canonical | k ∈ {2,3,4} confirmation; `log_b(b/(b−1))` constant |
| `OFFSPIKE-RESULT.md` | canonical | `δ_k(n) = (n−1)k + offset(n)` |
| `EXTENDED-PANEL-RESULT.md` | canonical | n-panel at b=10, d=4 |
| `PRIMITIVE-ROOT-FINDING.md` | canonical | Family A/B by `ord(b,n)` |
| `MECHANISTIC-DERIVATION.md` | canonical (partial) | step 3 is the open gap |
| `CROSS-BASE-RESULT.md` | canonical (new) | b ∈ {3,4,6,8,12} validation |
| `D5-RESULT.md` | canonical (new) | d=5 confirmation at b=10 |
| `MU-CONDITIONAL.md` | canonical (new) | conditional `μ → b` derivation |
| `brief2_q_derivation.md` | canonical (early) | first closed-form pass with denominator-inflation residual |
| `BRIEF2-INITIAL-FINDING.md` | superseded (historical) | original Brief 2 scan; was `acm-champernowne/base10/cf/README.md` |
| `BRIEF2-CLOSED-FORM.md` | superseded (rederivation) | independent rederivation of `MEGA-SPIKE.md`'s closed form |
| `MAHLER-DERIVATION.md` | superseded (rederivation) | parallel Mahler-style sketch of the same step-3 gap |
| `SPIKE-CLOSED-FORM-PANEL.md` | superseded (rederivation) | b=10 panel duplicating `EXTENDED-PANEL-RESULT.md` |
| `SPIKE-D5-RESULT.md` | superseded (rederivation) | d=5 result; canonical version is `D5-RESULT.md` |
| `SPIKE-HUNT.md` | empirical predecessor | original empirical CF spike scan that started Brief 2 |
| `MAHLER-CHECK.md` | validator | pipeline smoke test (Mahler's `a_4 = 149083` reproduction) |

The four "rederivation" docs are kept as a documented instance of
BIDDER mathematical-blindness (`memory/abductive_surprise_pattern.md`,
`core/ABDUCTIVE-KEY.md`): an agent in a different thread independently
rederived work already on the page in `MEGA-SPIKE.md`. Each has a
status preamble pointing to the canonical equivalent. Deleting them
would lose the provenance trail.


## Compute artifacts

| script | consumed by | data |
|---|---|---|
| `cf_spikes.py` | `BRIEF2-INITIAL-FINDING.md`, `SPIKE-HUNT.md` | `cf_spikes.csv`, `cf_spikes_n*.png`, `cf_spikes_summary.txt` |
| `cf_spikes_extended.py` | `CROSS-BASE-RESULT.md` (and superseded `SPIKE-CLOSED-FORM-PANEL.md`) | `cf_extended.csv`, `cf_extended_summary.txt`, `cf_extended_run.log` |
| `cf_spikes_d5.py` | `D5-RESULT.md` (and superseded `SPIKE-D5-RESULT.md`) | `cf_d5.csv`, `cf_d5_summary.txt`, `cf_d5_run.log` |
| `spike_drift_table.py` | `MEGA-SPIKE.md`, `brief2_q_derivation.md` | `spike_drift_table.csv`, `spike_drift_summary.txt` |
| `spike_drift_multi_k.py` | `MULTI-K-RESULT.md` | `spike_drift_multi_k.csv`, `spike_drift_multi_k_summary.txt` |
| `spike_drift_extended.py` | `EXTENDED-PANEL-RESULT.md`, `PRIMITIVE-ROOT-FINDING.md` | `spike_drift_extended.csv`, `spike_drift_extended_summary.txt` |
| `offspike_inflation.py` | `OFFSPIKE-RESULT.md` | `offspike_inflation.csv`, `offspike_inflation_summary.txt` |


## Cross-references

- `core/Q-FORMULAS.md`, `core/FINITE-RANK-EXPANSION.md` — local Q_n
  algebra; coupling-layer empirics live here.
- `core/BLOCK-UNIFORMITY.md` — closed-form n-prime block counts that
  give `T_k`.
- `arguments/MEGA-SPIKE-FOUR-WAYS.md` — critique of the closed-form
  thread.
- `experiments/acm-flow/STRUCTURE-HUNT.md` Phase 3.1 — overall
  position of this work in the project flow.
- `experiments/math/hardy/SURPRISING-DEEP-KEY.md` — instance list
  including the CF mega-spike collapse.


## Open

1. **Step 3 of `MECHANISTIC-DERIVATION.md`.** Pin `q_{i_k − 1}` to a
   specific form involving substrate divisibility. ord=1 clean, ord=2
   simple chain refuted, intermediate ord (n=13, 23, 31) undecided.
   Cross-thread convergence — the parallel sketch in superseded
   `MAHLER-DERIVATION.md` names the same gap at looser resolution —
   strengthens this as *the* load-bearing open problem.
2. **Off-spike denominator process.** `L_{k−1}` is currently fit by
   `C_{k−1} + (n−1)k + offset(n)`; the off-spike intermediate
   convergents are not modelled. The "two-stream hypothesis" names
   the gap; it does not fill it.
3. **Conditional μ verification.** `MU-CONDITIONAL.md` derives a
   value of μ under "spikes dominate the approximation budget";
   the conditional is open in the same direction as (2).
