# STRUCTURE-HUNT — what we go looking for after Phase 1

**Phase 1 ran. The four-coordinate decomposition in `ACM-MANGOLDT.md`
collapsed to two and changed observable.** This document is the
post-Phase-1 plan. The pre-Phase-1 version (with cutoff × payload
matrices, ρ-prediction, etc.) is preserved in git history and was
written against a model the destroyers refuted.


## Phase 1 outcomes

See `PHASE1-RESULTS.md` and `MEMO-PHASE1.md`. In short:

| pre-Phase-1 claim | post-destroyer status |
|---|---|
| ρ is the spectroscopic observable | refuted; ρ doesn't carry payload signal |
| four-coordinate decomposition | collapsed to two (height + payload divisor data) |
| cutoff coordinate (general) | falls at scale 0.1; tiny n=2 residue at scale 10⁻⁵ that is *secretly* a `v_2(Y)` distinction (dist=0 ↔ 4|Y, dist=2 ↔ 2 mod 4 for n=2) |
| payload graduation on Λ_n | evidence; m-shuffle null z ≥ 5 every cell |
| Λ_n is the local observable | replaced by `Q_n(m) = Λ_n(m)/log(m)` (`payload_q_scan.py`) — exact rational, removes log(m) scale, family-geometry residual cuts 4× |
| prime/composite-n split at h=3 | evidence; family-geometry subtraction by `n_type` cancels almost all bucket variation |


## The post-Phase-1 model

**Local observable:** `Q_n(m) = Λ_n(m) / log(m)`, exact rational from
the closed form

    Q_n(m) = Σ_{j ≥ 1, n^j | m} (-1)^(j-1) τ_j(m/n^j) / j.

**Coordinates:**

| coordinate | role |
|---|---|
| height `h = ν_n(m)` | sets the regime; selects which `τ_j` enter the sum |
| payload divisor data | multivariate `(τ_2(m/n²), τ_3(m/n³), …, τ_h(m/n^h))` — the closed form is exactly a linear combination of these |
| n-factorisation type | `prime / prime_power / multi_prime`; predicts which coefficient pattern Q_n exhibits |

The coordinates are *not* independent — they're connected through
the closed form. The empirical question becomes: how cleanly do
explicit divisor-function formulas describe each `(h, n_type, payload
divisor data)` regime?

**Side quest — cutoff coordinate.** Demoted but not eliminated. The
n=2 dist_n² residue earned evidence (z ≈ ±4) at scale 10⁻⁵; for
n ∈ {3, 4, 5} it's at sketch level (z ≈ ±1–2). Probably not a
generic cutoff coordinate but a `v_2(Y)` shadow specific to n=2.
Worth re-running at higher Y_max to see if other n's strengthen.


## Phase 2 — explicit closed forms (the lemma)

The prime/composite split at h=3 should become a **lemma**, not a
panel. The closed form already expresses Q_n as a divisor-sum
combination; for each `(h, n_type)` we should derive the explicit
predictor and verify against the data.

### 2.1 — derive Q_n(m) for `(h, n_type)`, all small h

For `n_type ∈ {prime, prime_power, multi_prime}` and `h ∈ {2, 3, 4, 5}`:

- substitute `m = n^h · k`, `gcd(n, k) = 1`;
- expand `τ_j(n^(h-j) · k)` using multiplicativity on coprime
  factors and `τ_j(p^a) = C(a + j − 1, j − 1)` for `n = p` prime;
- collect Q_n(m) as a polynomial in the divisor data of `k`.

Concrete h=3 prime n (n∤k) hand calculation already done:
`Q_n(n³ k) = 1 − d(k) + τ_3(k)/3`. Verifies the observed zeros at
`d(k) = 2` (k prime) and `d(k) = 3` (k = p²). Same approach for the
other (h, n_type) cells.

The output: a small table of explicit formulas per `(h, n_type)`,
plus a script that evaluates each formula on `m`-samples and asserts
agreement with `payload_q_scan.csv` to within Fraction equality.

If the formulas match exactly, the lemma is proven (modulo writing
it cleanly).

### 2.2 — within-prime residual

`payload_q_summary.txt` reports mean |family-geometry residual| =
0.31 on the prime category. With the closed forms in 2.1, this
residual should drop to numerical zero (since formulas predict Q
exactly given the divisor data). What remains tells us whether the
n-specific signal within "prime n" is structural or sampling.

### 2.3 — h ≥ 4 sample-size discipline

At `M_MAX = 50000`, h=5 panels for n ∈ {5, 6} have ≤13 m-points
and the destroyer crashes (z < 1). Either bump `M_MAX` to 10⁶
(τ-table grows linearly; cheap) or accept that h=5 is below
resolution at the current scale. Document the choice in the
script.


## Phase 3 — cross-experiment validation

Now that the local observable is Q_n with explicit formulas, the
cross-checks become predictions, not analogies.

### 3.1 — Brief 2 (CF spikes)

`experiments/acm-champernowne/base10/cf/SPIKE-HUNT.md` reports the
mega-spike magnitude scales as `(b−1)² · b^(k−2) · (n−1) · k / n²`.
Derive that formula from Q_n's closed form on the n-Champernowne
real and the Mahler-style boundary approximation. If the derivation
goes through, Brief 2's empirical fit becomes a corollary of the
Phase 2 lemma. If it doesn't, we learn what's different about the
CF setting.

### 3.2 — Brief 4 (BPPW MC on M_n)

The brief is gated on the `Λ_n` (now Q_n) sign-table. The Phase 2
formulas give the sign of Q_n in closed form for each
`(h, n_type, payload data)` cell. The BPPW M_n(N)·Φ(N)/N prediction
should follow from integrating Q_n's sign distribution against the
multiplication-table count.

### 3.3 — Cross-base

Closed form is base-agnostic. h, payload τ_2 are base-agnostic. So
Q_n itself is base-agnostic; only the *cutoff residue* coordinate
might be base-dependent (since `dist_n²` interacts with the
positional sieve). With the cutoff coordinate now demoted, cross-
base doesn't add Phase 1 surprise; it's a routine sanity check.


## Phase 4 — predictive model

If Phase 2's formulas match the data exactly, the predictive model
is *not* a fit — it's the closed form. Phase 4 becomes:

- evaluate Q_n on a held-out range of `m`;
- compare prediction (formula) to observation (`payload_q_scan` re-run);
- residual should be exactly zero, modulo Fraction arithmetic.

A clean zero residual converts Phase 2 from "lemma" to "theorem."

If Phase 2's formulas leave residual at certain `(h, n_type)`
cells, Phase 4 fits a polynomial extension and we look at *that*
residual's structure.


## Phase 5 — missing lines (if any)

After Phase 2–4 land, the remaining residuals (if any) point to
coordinates not in the model:

- `ν_p(n)` for each prime `p | n` (within prime_power and
  multi_prime)
- ω(payload) — the number of distinct prime factors of the payload
- the n=2 cutoff `v_2(Y)` shadow at scale 10⁻⁵, retested at
  larger Y_max to see if it's a real spectral line or finite-size
  artifact

Each is a small probe with the same destroyer + subtraction
discipline.


## Side quest — cutoff `v_2(Y)` residue

The n=2 dist_n² coherent line is *secretly* a `v_2(Y)` distinction
(distance=0 means 4 | Y, distance=2 means 2 mod 4 ≡ Y is exactly
2 mod 4). The "n²-distance" framing was the wrong scout name. The
right scout is `v_2(Y)`, and the question is whether the residue
appears at all `n` (with `v_n(Y)` analog) or only at n=2.

Test: at higher `Y_max` (5×10⁵ or 10⁶), rerun `cutoff_ray_scan` for
a couple of cells and check whether `v_n(Y)` produces evidence-level
z for n ∈ {3, 4, 5}, or whether the signal stays an n=2-only
phenomenon.

If it stays n=2-only, the cutoff coordinate is fully demoted to a
Lambda-on-A_n positivity-locus question, which is a different
research direction (`POSET-FACTOR.md`'s framing).


## Sequencing

```
Phase 2.1   derive Q_n closed forms per (h, n_type)         (analytic)
Phase 2.2   verify against payload_q_scan.csv               (small script)
Phase 2.3   bump M_MAX for h=5 if desired                   (parameter change)
Phase 3.1   Brief 2 derivation                              (analytic)
Phase 3.2   Brief 4 prediction                              (BPPW MC + analytic)
Phase 3.3   cross-base sanity check                         (re-run scan)
Phase 4     held-out predictive verification                (small script)
Phase 5     missing-lines probes                            (per-candidate)

Side quest  v_2(Y) at higher Y_max                          (re-run scan)
```

Phase 2.1 is the gate. With closed forms in hand, everything
downstream becomes either derivation or verification. Without
them, downstream is fitting and the spectroscopy claim stays
empirical.


## Files (planned, beyond Phase 1)

| file | role | phase |
|---|---|---|
| `q_n_formulas.md` | closed forms per (h, n_type) | 2.1 |
| `q_n_verify.py` | per-m formula vs Q_n(m) check | 2.2 |
| `brief2_q_derivation.md` | CF spike formula from Q_n | 3.1 |
| `brief4_q_prediction.py` | M_n(N)·Φ(N)/N from Q_n sign | 3.2 |
| `cutoff_v2_y.py` | re-run cutoff at higher Y_max with `v_n(Y)` scout | side |


## Coupling

- **`ACM-MANGOLDT.md`** — needs trim to two-coordinate model on Q_n.
  Current version still names ρ as the working residual statistic.
- **`PHASE1-RESULTS.md`** — destroyer outcomes; tighten h=3 wording
  ("no negative mass; low payload mostly zero, higher buckets turn
  positive" — not "all zero at τ_2 ≤ 4").
- **`MEMO-PHASE1.md`** — already calibrated.
- **`payload_q_scan.py` / `payload_q_*.png`** — new Phase-1.5
  artifacts on Q_n.


## What this is not

- Not a commitment to all five phases. Phase 2.1 is the gate;
  everything after assumes formulas in hand.
- Not a claim that Q_n is the *final* observable. If h=4, 5
  formulas leave residual, more coordinates remain. The discipline
  doc's caution applies: "an almost finite scout palette at this
  scale" — Q_n's clean structure at h ≤ 4 is finite-spectrum
  evidence at this M_MAX, not a theorem about all m.
