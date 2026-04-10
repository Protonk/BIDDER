# Red-Team Theory

For a prefix estimator built from a permutation of `↕ P`,

```text
E_N(key) - I = (E_N(key) - R) + (R - I)
```

with:

- `E_N(key)` = the prefix mean after `N` outputs under one key
- `R` = the full-grid left-endpoint Riemann sum
- `I` = the true integral of the target function

That decomposition is the theory front.

The first term asks what the permutation does.
The second asks what the grid does.
The current red-team tests exist to keep those two questions separate,
then measure where the actual backend departs from the ideal null.


## The four layers

### 1. Structural layer: why `E_P(key) = R`

At `N = P`, every permutation of `↕ P` visits the same population once.
The order disappears. The key disappears. The cipher quality disappears.

This is the exact theorem in
[core/RIEMANN-SUM.md](../../core/RIEMANN-SUM.md): at full period,
the estimate is not approximately equal to `R`; it is exactly `R`.

What could fail:

- the object is not actually a permutation of `↕ P`
- the estimator is not really averaging over the first `N` outputs
- the implementation has a boundary bug at `N = P`

How we attack it:

- favorable integrands
- hostile integrands
- identity-permutation isolation
- explicit permutation sanity checks

Theory test:
[test_riemann_property.py](./test_riemann_property.py)

Experiment ancestry:

- [experiments/bidder/unified/riemann_proof.py](../../experiments/bidder/unified/riemann_proof.py)
- [experiments/bidder/unified/adversarial_integrands.py](../../experiments/bidder/unified/adversarial_integrands.py)


### 2. Quadrature layer: what `R - I` costs

Once `E_P(key) = R` is fixed, the remaining error at full period is the
left-endpoint quadrature bias. This has nothing to do with keys or
PRPs. It is pure grid math.

The relevant question is not "does the estimate converge?" but
"at what rate does the left rule converge for this class of `f`?"

Current theory focus:

- `f(x) = x` gives exact `1 / (2P)`
- `sin(πx)` gets endpoint cancellation and scales like `π / (6P²)`
- `x²(1-x)²` gets double endpoint cancellation and scales like `1 / (30P⁴)`
- a step function still behaves like `O(1/P)`
- smoothness alone is not enough to force `O(1/P²)`

What could fail:

- the Euler-Maclaurin rows are misstated
- the constants are wrong
- a "friendly" example is being mistaken for a generic one

How we attack it:

- no cipher
- no key
- direct grid sums only
- explicit counterexamples, not just positive examples

Theory test:
[test_quadrature_rates.py](./test_quadrature_rates.py)

Experiment ancestry:

- [experiments/bidder/unified/adversarial_integrands.py](../../experiments/bidder/unified/adversarial_integrands.py)
- [experiments/bidder/unified/riemann_proof.py](../../experiments/bidder/unified/riemann_proof.py)


### 3. Statistical layer: what happens for `N < P` under the ideal null

Before asking what BIDDER does, ask what a uniform random permutation
would do.

For sampling without replacement from the population
`{f(0/P), ..., f((P-1)/P)}`, the variance around `R` is governed by the
finite-population correction:

```text
Var(E_N) = (σ² / N) · (P - N) / (P - 1)
```

This is the correct benchmark for the prefix-mean problem. It is not a
claim about the true integral `I`; it is a claim about fluctuation
around the population mean `R`.

What could fail:

- the FPC formula is being compared to the wrong target
- the null is with-replacement instead of without-replacement
- the endpoint `N = P` is not handled cleanly

How we attack it:

- build the ideal null explicitly with `random.shuffle`
- compare empirical RMSE about `R` against the FPC prediction
- check the endpoint separately

Theory test:
[test_fpc_shape.py](./test_fpc_shape.py)

Direct helper:
[shuffle_prefix_means](./_helpers.py)

Experiment ancestry:

- [experiments/bidder/unified/mc_diagnostic.py](../../experiments/bidder/unified/mc_diagnostic.py)
- [experiments/bidder/reseed/reseed_test.py](../../experiments/bidder/reseed/reseed_test.py)


### 4. Coupling layer: what the actual backend does instead of the ideal null

This is the only layer where the algebra and the cipher meet.

The question is not whether the algebra is correct. The algebra is
already isolated above. The question is how closely the actual keyed
permutation family tracks the ideal without-replacement benchmark.

The current answer is mixed:

- the endpoint is exact because the structural theorem is exact
- the shape tracks the FPC descent toward zero
- the Feistel fallback shows a measurable variance gap at intermediate `N`

What could fail:

- the backend could distort the shape badly
- the endpoint could drift from zero
- the measured gap could be an artifact of a bad baseline

How we attack it:

- compare cipher RMSE about `R` to the ideal FPC benchmark
- keep the gap as a measurement, not a theorem
- never let the backend define its own null

Theory test:
[test_fpc_shape.py](./test_fpc_shape.py)

Experiment ancestry:

- [experiments/bidder/unified/mc_diagnostic.py](../../experiments/bidder/unified/mc_diagnostic.py)
- [experiments/bidder/stratified/stratified.py](../../experiments/bidder/stratified/stratified.py)


## Test map

| Layer | Claim | What would falsify it | Proof doc | Theory test | Status |
|---|---|---|---|---|---|
| Structural | `E_P(key) = R` for any key, any integrand | key spread at `N = P`; non-permutation output; identity case failing | `core/RIEMANN-SUM.md §Proof` | `test_riemann_property.py` | active |
| Quadrature | the left-rule rates and constants are the ones stated | wrong asymptotic constant; false generic smoothness claim; hostile examples breaking the table | `core/RIEMANN-SUM.md §What the Riemann sum costs` | `test_quadrature_rates.py` | active |
| Statistical | the ideal without-replacement null obeys the FPC formula around `R` | shuffle baseline failing against FPC; endpoint mishandled | `core/RIEMANN-SUM.md §The finite-population correction` | `test_fpc_shape.py` | active |
| Coupling | the backend tracks the FPC shape but need not match the ideal magnitude | large interior distortion; endpoint drift; no measurable relation to FPC | `core/RIEMANN-SUM.md §What the cipher actually achieves` | `test_fpc_shape.py` | active |


## Why these are red-team tests

They are not demonstrations. They are attempts to separate claims that
look similar from claims that are actually the same.

The red-team posture in this directory is:

- isolate permutation facts from cipher-quality facts
- isolate grid bias from prefix-variance claims
- use hostile integrands, not just pleasant ones
- build the ideal null explicitly instead of treating the backend as
  its own baseline
- keep proof, executable theorem test, and visualization as three
  distinct things

That is why the same theorem may appear in three places:

- a proof doc under `core/`
- a pass/fail theory test under `tests/theory/`
- a visual experiment under `experiments/bidder/`


## Shared helper provenance

[_helpers.py](./_helpers.py) exists because the three tests are not
really independent. They reuse one small family of ideas:

- integrand registry
- direct grid sums and biases
- prefix-mean measurement under keys
- RMSE / spread summaries
- explicit uniform-permutation null construction
- permutation sanity checks

Those helpers were lifted and tightened from:

- [experiments/bidder/unified/riemann_proof.py](../../experiments/bidder/unified/riemann_proof.py)
- [experiments/bidder/unified/adversarial_integrands.py](../../experiments/bidder/unified/adversarial_integrands.py)
- [experiments/bidder/unified/mc_diagnostic.py](../../experiments/bidder/unified/mc_diagnostic.py)
- [experiments/bidder/stratified/stratified.py](../../experiments/bidder/stratified/stratified.py)
- [experiments/bidder/reseed/reseed_test.py](../../experiments/bidder/reseed/reseed_test.py)
- [experiments/bidder/unified/period_anatomy.py](../../experiments/bidder/unified/period_anatomy.py)


## Adjacent theory outside this directory

The bidder theory front is not the whole theorem surface of the repo.

The adjacent exact arithmetic results live elsewhere:

- [core/BLOCK-UNIFORMITY.md](../../core/BLOCK-UNIFORMITY.md)
  with executable checks in
  [tests/test_acm_core.py](../test_acm_core.py)
- [core/HARDY-SIDESTEP.md](../../core/HARDY-SIDESTEP.md)
  with executable checks in
  [core/hardy_sidestep.py](../../core/hardy_sidestep.py) and
  [tests/test_sawtooth.py](../test_sawtooth.py)

Those theorems feed the larger project, but they are not part of the
`E_N - I` decomposition that organizes this directory.


## Known gaps

- [core/ABDUCTIVE-KEY.md](../../core/ABDUCTIVE-KEY.md) has no theory
  test here.
- The backend has no independent PRP-security proof in this exact
  composition.
- [core/BLOCK-UNIFORMITY.md](../../core/BLOCK-UNIFORMITY.md) still does
  not characterize the full exact-uniformity locus for the sieved case.
- The finite-automaton boundary condition for binary ACM streams is not
  yet represented as a theorem test.


## How to add a new theory test

Start from a quantity, not from a script.

1. Name the quantity and the decomposition it belongs to.
2. Say what would falsify the claim.
3. Separate algebra from backend behavior if both are present.
4. Link the proof doc under `core/`.
5. Link the experiment ancestry under `experiments/`.
6. Put shared logic in [_helpers.py](./_helpers.py) only if at least
   two theory tests will reuse it.

If a proposed test cannot say what would count as failure, it is not
ready to live in this directory.
