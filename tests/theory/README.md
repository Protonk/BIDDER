# Theory verification index

Each row: one proved result, where to find the proof, where to find
the theory test, where to find the visualization.

Tests in this directory probe the *theory*, not the *implementation*.
The helpers in `_helpers.py` were distilled from the experiment family
in `experiments/bidder/unified/`, `experiments/bidder/stratified/`, and
`experiments/bidder/reseed/`.

Run all theory tests:

    python3 tests/theory/test_riemann_property.py
    python3 tests/theory/test_quadrature_rates.py
    python3 tests/theory/test_fpc_shape.py


## Theorem index

| Result | Proof | Theory test | Experiment |
|---|---|---|---|
| `E_P = R` (permutation-invariance) | `core/RIEMANN-SUM.md §Proof` | `test_riemann_property.py` | `riemann_proof.py`, `adversarial_integrands.py` |
| Left-rule rates (Euler–Maclaurin) | `core/RIEMANN-SUM.md §What the Riemann sum costs` | `test_quadrature_rates.py` | `adversarial_integrands.py`, `riemann_proof.py` |
| FPC for ideal permutations | `core/RIEMANN-SUM.md §Finite-population correction` | `test_fpc_shape.py` (via `_helpers.py:shuffle_prefix_means`, the ideal null built here) | `mc_diagnostic.py` (background; does not encode the ideal null directly) |
| Cipher coupling gap | `core/RIEMANN-SUM.md §What the cipher actually achieves` | `test_fpc_shape.py` | `mc_diagnostic.py`, `stratified.py` |
| Integer block uniformity | `core/BLOCK-UNIFORMITY.md §Lemma` | `tests/test_acm_core.py::test_block_boundary_*` | `uniformity_demo.py` |
| Sieved block (smooth) | `core/BLOCK-UNIFORMITY.md §Sieved version` | `tests/test_acm_core.py::test_block_uniformity_sieved_sufficient` | — |
| Sieved block (Family E) | `core/BLOCK-UNIFORMITY.md §A second sufficient family` | `tests/test_acm_core.py::test_block_uniformity_sieved_family_e` | — |
| Spread bound ≤ 2 | `core/BLOCK-UNIFORMITY.md §A spread bound` | `tests/test_acm_core.py::test_block_uniformity_sieved_spread_bound` | — |
| Hardy closed form | `core/HARDY-SIDESTEP.md` | `tests/test_sawtooth.py` + `core/hardy_sidestep.py` | `acm_sawtooth.py` (downstream illustration) |
| Abductive key | `core/ABDUCTIVE-KEY.md` | — | — |

The last row (abductive key) has no test and no experiment. This is
an honest gap.


## What the theory tests cover

### `test_riemann_property.py` — structural layer

The permutation-invariance theorem: `E_P(key) = R` for any key.
Tested across favorable and adversarial integrands, multiple P
values, 20 keys per configuration, plus an identity-permutation
isolation check and a permutation-sanity guard.

### `test_quadrature_rates.py` — quadrature layer

Each row of the Euler–Maclaurin convergence table becomes an
assertion. `f(x) = x` at exact `1/(2P)`, `sin(πx)` at `π/(6P²)`,
`x²(1−x)²` at `O(1/P⁴)`, step function bounded at `O(1/P)`, plus
a counterexample check that `f(x) = x` does NOT converge at
`O(1/P²)`. No cipher involved — pure grid math.

### `test_fpc_shape.py` — statistical layer + coupling

The finite-population correction, tested against both a
`random.shuffle` baseline (the ideal without-replacement null) and
the cipher backend. The FPC formula matches the shuffle baseline
to within sampling noise. The cipher follows the FPC shape but with
a ~1.5–2.5× gap at intermediate N attributable to PRP quality. The
endpoint is exactly zero for both. The coupling gap is measured and
reported, not asserted away.


## Shared helpers

`_helpers.py` contains the distilled common logic:

- **Integrand registry** — 5 named integrands (sin, x, x²(1-x)²,
  √x, step) with true integrals and endpoint notes.
- **Grid / Riemann helpers** — `riemann_sum`, `riemann_bias`,
  `grid_values`.
- **Cipher prefix helpers** — `cipher_full_mean`,
  `cipher_key_ensemble`, `cipher_values`.
- **Ensemble summaries** — `rmse_about`, `spread`.
- **Shuffle null** — `shuffle_prefix_means` (the ideal
  without-replacement baseline, first encoded here).
- **Permutation sanity** — `assert_is_permutation`,
  `cipher_is_permutation`.

All stdlib-only. No numpy, no sage, no matplotlib.
