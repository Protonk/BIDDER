# EXP05 — parameter sweep: the survivor signature is panel-specific

EXP04 found that at the Two Tongues panel `[n_0=2, W=9, k=400]`, the
survivor filter's δ-signature differs from random thinning at z =
+2.21 (L1) and +2.53 (χ²). The natural follow-up was: *does this
hold across other panels?* This experiment runs 10 panels around the
Two Tongues center and finds: **no, the signal is panel-specific**.
Most panels have |z| ≲ 1; only `n_0 = 2` with modest `W` shows the
EXP04-like signal.

## Setup

Three sweeps around `(n_0=2, W=9, k=400)`, with 20 random seeds per
panel:

- **k**: {100, 200, 400, 800} at `(n_0=2, W=9)`
- **n_0**: {2, 10, 30, 100} at `(W=9, k=400)`
- **W**: {3, 9, 15, 21} at `(n_0=2, k=400)`

For each panel: compute the survivor's δ digit-frequency signature,
generate 20 random subsets matching the survivor's atom count
(preserving order), and compute z-score of survivor vs the random
distribution. Two scoring statistics: L1 from uniform, χ² with 9 dof.

## The numbers

```
k sweep (n_0=2, W=9):
   k    z_L1    z_χ²    surv_rate
  100   −0.31   −0.37    38.1%
  200   −0.51   −0.49    37.3%
  400   +1.89   +2.19    37.2%   ← Two Tongues
  800   +0.66   +0.45    37.2%

n_0 sweep (W=9, k=400):
   n_0   z_L1    z_χ²    surv_rate
    2   +1.89   +2.19    37.2%   ← Two Tongues
   10   +1.42   +0.59    53.1%
   30   −0.02   −0.13    70.1%
  100   −0.12   −0.37    88.2%

W sweep (n_0=2, k=400):
    W   z_L1    z_χ²    surv_rate
    3   +1.32   +2.05    72.7%
    9   +1.89   +2.19    37.2%   ← Two Tongues
   15   −0.37   −0.35    29.6%
   21   +1.08   +0.86    28.5%
```

## Reading

### 1. The Two Tongues z-score doesn't replicate

Across 10 panels, only one (`n_0=2, W=9, k=400` — the Two Tongues
panel itself) sits at z above the 2σ threshold on χ². Two more
panels (`n_0=2, W=3` and Two Tongues) are above 2σ on χ² specifically.
Most others are within ±1σ of zero. The earlier reading from EXP04
("the survivor filter is detectably special") is *panel-specific*,
not a generic property.

### 2. The signal decays as the filter weakens

Survival rate is the cleanest predictor:

- **Low survival rate (28–38%)**: signal can be visible (`(2, 9, 400)`,
  `(2, 3, 400)`).
- **Moderate (53–73%)**: signal is weak (`(2, 3, 400)` despite high
  rate is borderline; `(10, 9, 400)` is `+1.42`).
- **High (>70%)**: signal vanishes (`(30, 9, 400)`, `(100, 9, 400)`).

This makes sense structurally: at high survival rate, the survivor
filter is barely a filter — most atoms survive, the survivor and
random subsets share most atoms, and their δ-signatures converge by
construction.

### 3. The signal is non-monotone in `k`

The k-sweep is the most surprising. At `k = 100, 200`: z is *negative*
(survivor's L1 is *less* than random's mean). At `k = 400`: signal
peaks. At `k = 800`: signal weakens again. Three readings, not
mutually exclusive:

- The Two Tongues panel is at a **local maximum** in `k`-space; the
  signature has a peak that small-k samples haven't reached and
  larger-k samples have averaged away.
- The signal's *direction* depends on `k` (negative at small k means
  random produces *more* L1 deviation than survivor). This could be
  a finite-K artifact where small-k random subsets accidentally
  produce strong signatures by selection variance.
- Combined with the n_0 sweep, the strongest signal lives in a
  narrow region of parameter space rather than across a wide one.

### 4. The W-sweep is the most ambiguous

`W = 9` (Two Tongues) and `W = 3` both show positive χ²-z. `W = 15`
is null. `W = 21` is mildly positive again. Survival rates differ
substantially (`W=3`: 72.7%, `W=9`: 37.2%, `W=15`: 29.6%, `W=21`:
28.5%), but the z-score doesn't track survival rate monotonically.
This sweep doesn't isolate a clear axis along which the signal
changes.

## What this means for EXP04 and the cabinet

EXP04's framing was: "the survivor filter is distinguishable from
random thinning at the digit-frequency level." That framing was
correct *at the Two Tongues panel*. It is **not** correct as a
generic statement about the survivor construction across parameter
space.

The cabinet's Two Tongues curiosity is partly de-sharpened. The L1
tracking remains solid (it's an aggregated visual reading at one
panel, and wasn't promising panel-invariance). But the more refined
"survivor differs from random at z ≈ 2" claim from EXP04 is brittle
across parameters.

Two readings, both defensible:

- **The Two Tongues panel is special.** The combination
  `(n_0=2, W=9, k=400)` happens to sit at a local maximum of
  signature strength. The cabinet entry's panel choice was
  fortunate; pulling the signal out of *any* panel might have been
  much harder.
- **The signal is weak everywhere; we got lucky at one panel.**
  With 10 panels and 5% chance per panel of hitting >2σ by chance,
  one positive is consistent with no real signal at all. The
  Two Tongues result might be a single statistical fluctuation.

The first reading is more interesting and probably partly true —
the structural explanation (signal vanishes at high survival rate)
suggests there *is* a regime where survivor specifically imprints,
and Two Tongues sits in it. The second reading is the disciplined
null hypothesis to keep in mind.

## What this opens

- **Denser sampling of the (low-n_0, modest-W) corner.**
  If the signal is real, it lives at small n_0 with W somewhere
  around 9. A finer grid in this region — `n_0 ∈ {2, 3, 4, 5, 7}`
  × `W ∈ {5, 7, 9, 11, 13}` × `k = 400` — would localise the peak.

- **More seeds per panel.** EXP04 used 50 seeds at the Two Tongues
  panel and got z = +2.21. EXP05 used 20 seeds and got z = +1.89 at
  the same panel. The sweep's z-scores would tighten ~1.5× with 50
  seeds. It's possible some near-zero panels would resolve to
  z ≈ ±1.5 with more seeds, sharpening or weakening the picture.

- **Non-z observable.** Maybe z-score on L1/χ² is too coarse. The
  *per-digit* z from EXP04 specifically picked out digit 0 (z=+1.92)
  and digit 3 (z=−2.07) as anomalous. A per-digit panel sweep would
  ask whether digit-0/3 specifically anomaly across panels — even
  when the aggregate L1/χ² doesn't.

- **The structural prediction.** Under the "signal needs low survival
  rate" hypothesis, panels with survival rate ≲ 40% should show
  signal. The current sweep has only 4 such panels (Two Tongues, the
  three large-W panels at n_0=2). Three of them show modest positive
  z (+1.89, −0.37, +1.08); one (W=15) is null. Not a clean
  prediction-confirmation either way; needs more sampling.

## Files

- `exp05_parameter_sweep.py` — script.
- `exp05_parameter_sweep.png` — four-panel figure: z vs k, z vs n_0,
  z vs W, summary table.
