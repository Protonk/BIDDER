# The Riemann-Sum Property

At `N = period`, the Monte Carlo estimate from `bidder.cipher` is the
Riemann sum of the integrand — not an approximation of it, not a
statistical estimate of it, but the sum itself. The key cancels out.
Every key gives the same answer.

This note has three layers:

1. **Structural.** At `N = P`, the estimate is exactly the full-grid
   mean `R`, for any permutation and any key.
2. **Quadrature.** The gap `R − I` between that full-grid mean and the
   true integral is a left-endpoint Riemann-sum question.
3. **Finite-population.** For `N < P`, a uniformly random permutation
   has a variance governed by the finite-population correction (FPC).
   The current cipher backend only approximates that ideal.

**What this is not.** `bidder.cipher` is not a "better PRNG." It is
a keyed permutation with one structural guarantee (the Riemann sum
at `N = P`) and one statistical property that depends on the PRP
backend (the intermediate-`N` convergence rate). At `N < P` the
cipher can be *worse* than iid sampling if the PRP quality is low.
The advantage is the guaranteed-exact endpoint, not a blanket
improvement at every sample size.


## Statement

Let `P ≥ 2` and let `π` be any permutation of `{0, 1, …, P − 1}`
(i.e., the output of `bidder.cipher(P, key)` for any `key`). Let
`f : [0, 1) → ℝ` be any function. The Monte Carlo estimate at
sample size `N = P` is

    E = (1/P) Σ_{i=0}^{P-1} f(π(i) / P).

**Claim.** This equals the standard Riemann sum

    R(f, P) = (1/P) Σ_{k=0}^{P-1} f(k / P)

regardless of which permutation `π` is used.


## Notation

For a fixed period `P`, integrand `f`, and key-induced permutation `π`,
it helps to name the three quantities that the rest of the note keeps
separating:

- `E_N(key) = (1/N) Σ_{i=0}^{N-1} f(π(i)/P)` is the prefix mean after
  `N` samples.
- `R = (1/P) Σ_{k=0}^{P-1} f(k/P)` is the full-grid mean, i.e. the
  left-endpoint Riemann sum with `P` bins.
- `I = ∫₀¹ f(x) dx` is the true integral.
- `σ² = (1/P) Σ (f(k/P) − R)²` is the population variance on the grid.

The structural theorem in this document is `E_P(key) = R`. Everything
about quadrature bias concerns `R − I`. Everything about the FPC
concerns the spread of `E_N(key)` around `R` when `N < P`.


## First Example

At `P = 6` with `f(x) = sin(πx)`, three different keys:

```python
import bidder, math

P = 6
for key in [b'alice', b'bob', b'carol']:
    B = bidder.cipher(period=P, key=key)
    seq = [B.at(i) for i in range(P)]
    est = sum(math.sin(math.pi * B.at(i) / P) for i in range(P)) / P
    print(f"  key={key!r:10s}  perm={seq}  estimate={est:.10f}")
```

Output:

```
  key=b'alice'    perm=[2, 1, 5, 4, 3, 0]  estimate=0.6220084679
  key=b'bob'      perm=[0, 5, 3, 1, 2, 4]  estimate=0.6220084679
  key=b'carol'    perm=[0, 1, 4, 3, 2, 5]  estimate=0.6220084679
```

Three different permutations. Three identical estimates. The estimate
is the Riemann sum `R(sin(πx), 6) = 0.6220084679`, which differs from
the true integral `2/π = 0.6366197724` by `1.46 × 10⁻²`. That gap is
the deterministic quadrature bias `|R − I|`, not a statistical artifact.

At `P = 2000`, 200 different keys all produce `0.6366196415`, with
zero spread across keys (up to floating-point noise whose magnitude
varies by platform). The remaining error is the Riemann-sum bias
`1.31 × 10⁻⁷`.


## Proof

The sum over a permutation of a set is the sum over the set.

Write `S = {0, 1, …, P − 1}`. Since `π` is a bijection `S → S`,
the multiset `{π(0), π(1), …, π(P − 1)}` is exactly `S`, and

    Σ_{i=0}^{P-1} f(π(i) / P) = Σ_{k ∈ S} f(k / P) = Σ_{k=0}^{P-1} f(k / P).

Dividing both sides by `P` gives `E = R(f, P)`. ∎

The proof is one line. The key determines *which* bijection `π` is
used, but the sum is invariant under permutation, so the key
disappears at `N = P`.


## Claim Types

The document mixes three kinds of statements. It is worth keeping them
separate:

| Layer            | Quantity                     | Status |
|------------------|------------------------------|--------|
| Structural       | `E_P(key) = R`               | exact, for any permutation of `[0, P)` |
| Quadrature       | `R − I`                      | deterministic analysis from `f` and `P` |
| Statistical      | distribution of `E_N(key)` for `N < P` | backend- and key-distribution-dependent; FPC is an ideal benchmark |


## In BQN

The proof is a rearrangement identity. In BQN, let `L` be any
permutation of `↕P` (i.e., a length-`P` list containing each
element of `↕P` exactly once). Then

```bqn
(+´ f¨ (L ÷ P)) ÷ P
```

equals

```bqn
(+´ f¨ ((↕P) ÷ P)) ÷ P
```

because `L` is a reordering of `↕P` and `+´` (fold-add) is
order-independent. This is a general property of fold over
commutative-associative operations — it is not specific to BIDDER,
to `f`, or to `P`.

The Riemann sum of `f` on `[0, 1)` with `P` bins is exactly the
second expression:

```bqn
# Riemann sum: (1/P) × sum of f(k/P) for k in 0..P-1
(+´ f¨ ((↕P) ÷ P)) ÷ P
```


## What the Riemann sum costs

The object here is the **left-endpoint rule**:

    R(f, P) = (1/P) Σ_{k=0}^{P-1} f(k / P)

Its error `|R(f, P) − ∫₀¹ f(x) dx|` depends on `f`, on `P`, and
critically on whether the endpoint values `f(0)` and `f(1)` match.
The Euler–Maclaurin expansion gives the leading terms:

    R − I = −[f(1) − f(0)] / (2P)
            − B₂/(2!) · [f'(1) − f'(0)] / P²
            − B₄/(4!) · [f'''(1) − f'''(0)] / P⁴
            − …

where `Bₖ` are Bernoulli numbers (`B₂ = 1/6`, `B₄ = −1/30`, …).
The leading error term is `O(1/P)` with coefficient
`−(f(1) − f(0)) / 2`. Higher powers of `1/P` appear only when
successive endpoint differences vanish.

| Condition on `f`                                                    | Left-rule error |
|---------------------------------------------------------------------|-----------------|
| Lipschitz (bounded first derivative)                                | `O(1/P)` — the generic case |
| `f(0) = f(1)` (endpoint match)                                     | `O(1/P²)` — the `1/P` term cancels |
| `f^(j)(0) = f^(j)(1)` for `j = 0, …, 2m − 1`                      | `O(1/P^(2m+2))` — the first `m` Euler–Maclaurin corrections cancel |
| `f` periodic and analytic (`f^(j)(0) = f^(j)(1)` for all `j`)       | exponential in `P` |

Boundedness alone is **not** enough. For example, the Dirichlet
function `f = 1_ℚ` is bounded, but every grid point `k/P` is rational,
so `R(f, P) = 1` for all `P` while the Lebesgue integral is `0`.
The left sums do not converge at all.

**Important.** Smoothness alone does not improve the rate beyond
`O(1/P)`. The classic counterexample is `f(x) = x` (analytic,
`C^∞`), for which `R = (P−1)/(2P)` and the error is exactly
`1/(2P)` — stubbornly `O(1/P)` because `f(0) ≠ f(1)`.

**`sin(πx)` is a special case.** Here `f(0) = f(1) = 0`, so the
leading `O(1/P)` term vanishes. The next correction is
`−B₂/(2!) · [f'(1) − f'(0)] / P² = −(1/6)/2 · (−2π) / P² = π/(6P²)`,
giving

    |R − 2/π| = π / (6P²) + O(1/P⁴).

The companion script `experiments/bidder/unified/riemann_proof.py`
confirms this:

| P       | Riemann error for sin(πx) | P² × error |
|--------:|---------------------------|------------|
| 50      | 2.09 × 10⁻⁴              | 0.523      |
| 200     | 1.31 × 10⁻⁵              | 0.524      |
| 1000    | 5.24 × 10⁻⁷              | 0.524      |
| 2000    | 1.31 × 10⁻⁷              | 0.524      |
| 20000   | 1.31 × 10⁻⁹              | 0.524      |

The column `P² × error` converges to `π/6 ≈ 0.5236`, confirming
the Euler–Maclaurin prediction.


## What this means for Monte Carlo

Standard MC with a PRNG samples *with replacement*. At `N` draws
from `[0, P)`, the birthday paradox predicts `~N²/(2P)` collisions
— samples wasted on values already visited. At `N = P`, a PRNG has
visited only about `P(1 − 1/e) ≈ 63%` of the range; the other 37%
are lost to duplicates.

`bidder.cipher` samples *without replacement* (it is a permutation).
At `N = P` the coverage is 100% and the estimate is the Riemann sum.
The practical implication:

- **If you know your sample budget `N` in advance,** set
  `period = N`. The cipher gives you the exact Riemann sum at the
  end of the sweep, for any integrand, regardless of the key.
- **Before `N = P`,** the cipher and a PRNG have comparable MC
  error. The cipher's advantage appears as `N` approaches `P` and
  the coverage-completeness effect kicks in (the "dropoff" visible
  in the convergence plots).
- **The Riemann-sum floor is not a ceiling.** You can choose a
  larger `P` to get a tighter Riemann sum. At `P = 20000` the
  floor for `sin(πx)` is `1.3 × 10⁻⁹`.

Important: the without-replacement advantage concerns the fluctuation of
`E_N(key)` around `R`. It does **not** remove the deterministic
quadrature bias `|R − I|`. To reduce that bias, you need a larger `P`
or stronger endpoint-cancellation conditions on `f`.

The Riemann-sum property is structural — it follows from the
definition of "permutation" and does not depend on the cipher's
internals, the key schedule, or the block structure. Any keyed
permutation of `[0, P)` has this property; BIDDER's contribution
is making such a permutation available via `bidder.cipher` with a
practical API.


## In BQN (the full picture)

Putting the pieces together. The integer-block lemma from
`core/BLOCK-UNIFORMITY.md` gives the set:

```bqn
↕ P
```

The keyed permutation (opaque to BQN) reorders it. The MC estimate
at `N = P` is:

```bqn
# f applied to each element, divided by P, then summed and averaged.
# The permutation cancels in the sum:
(+´ f¨ ((↕P) ÷ P)) ÷ P
```

This is the Riemann sum. The error is a property of `f` and `P`,
not of the permutation. The generic rate for the left-endpoint rule
is `O(1/P)`:

```bqn
# Generic left-rule error: (f(1) - f(0)) ÷ 2×P
# Improved to O(1/P²) only when f(0) = f(1) (endpoint match).
# For f(x) = sin(πx): ≈ (π ÷ 6) × P⋆¯2.
```

The `NthNPn2` closed form from `core/HARDY-SIDESTEP.md` is
unrelated — it gives random access into the *sawtooth* path, not
the cipher path. The Riemann-sum property is purely about the
cipher's permutation structure and does not invoke any n-prime
machinery.


## The finite-population correction

The convergence behavior at `N < P` connects to a standard result
from survey statistics: the **finite-population correction** (FPC)
for sampling without replacement.

### The framework

`bidder.cipher(P, key)` is a permutation of `{0, 1, …, P − 1}`.
The first `N` outputs are `N` distinct indices from `{0, 1, …, P−1}`
— sampling grid points without replacement, carrying values
`f(k/P)` at each sampled grid point `k`.
This is true by construction and does not depend on the quality of
the cipher's PRP approximation.

For an ideal uniform random permutation (one drawn uniformly from
all `P!` possibilities), the prefix of length `N` is a uniformly
random size-`N` subset of the population. The variance of the sample
mean is

    Var[estimate] = (σ² / N) · (P − N) / (P − 1)

where `σ² = (1/P) Σ (f(k/P) − R)²` is the population variance and
`R` is the Riemann sum (population mean). The factor
`(P − N) / (P − 1)` is the FPC.

In BQN, the FPC factor for a given `(N, P)`:

```bqn
(P - N) ÷ (P - 1)
```

### What the FPC predicts

Three regimes:

- **`N ≪ P`:** FPC ≈ 1. The variance is `≈ σ²/N`, the same as
  sampling with replacement (iid). The permutation property does
  not help noticeably.
- **`N → P`:** FPC → 0. The variance drops toward zero as the
  coverage of the population approaches 100%.
- **`N = P`:** FPC = 0. Variance = 0. The estimate equals the
  population mean (the Riemann sum) with certainty. This is the
  key-independence result already proved above.

This shape — flat at small `N`, steep dropoff near `P`, zero at
`P` — matches the qualitative behavior visible in the MC convergence
plot from `experiments/bidder/unified/mc_diagnostic.py`.

### What the cipher actually achieves

The FPC formula applies exactly to a *uniformly random* permutation.
The cipher's permutation is not uniformly random — it is a keyed PRP
(pseudorandom permutation) produced by the Speck32/64 or Feistel
backend. The approximation quality matters.

Empirical measurement at `P = 2000` over 500 keys, for
`f(x) = sin(πx)`. Both the FPC prediction and the empirical column
measure the root-mean-square deviation of the prefix mean from the
**population mean `R`** (the Riemann sum), not from the true
integral `I`. The distinction matters: at `N = P` the prefix mean
equals `R` exactly (the Riemann-sum property), so the RMSE about
`R` is zero; the residual error `|R − I|` (the Riemann-sum bias,
`1.31 × 10⁻⁷` at `P = 2000` for `sin(πx)`) is a separate quantity
that the FPC does not address.

| N     | FPC      | FPC predicted std | Cipher RMSE about `R` | Ratio |
|------:|---------:|------------------:|----------------------:|------:|
| 50    | 0.976    | 4.30 × 10⁻²       | 5.29 × 10⁻²           | 1.2   |
| 200   | 0.901    | 2.07 × 10⁻²       | 3.65 × 10⁻²           | 1.8   |
| 500   | 0.750    | 1.19 × 10⁻²       | 2.67 × 10⁻²           | 2.2   |
| 1000  | 0.500    | 6.88 × 10⁻³       | 1.70 × 10⁻²           | 2.5   |
| 1500  | 0.250    | 3.97 × 10⁻³       | 8.95 × 10⁻³           | 2.3   |
| 1900  | 0.050    | 1.58 × 10⁻³       | 2.34 × 10⁻³           | 1.5   |
| 2000  | 0.000    | 0                  | 0                      | —     |

The cipher follows the FPC's *shape* (dropping toward zero as
`N → P`), but at intermediate `N` the empirical RMSE is ~1.5–2.5×
higher than the FPC prediction. This is evidence that the
key-induced prefix distribution deviates from ideal simple-random-
sampling behavior for this integrand and period; it is not, by
itself, a metric on the overall distance between the cipher's
permutation distribution and the uniform distribution over `S_P`.
Other integrands, periods, or statistics could show different gaps.

The gap does **not** affect the endpoint. At `N = P` the RMSE about
`R` is exactly zero regardless of PRP quality, because the Riemann-
sum property is structural (proved above), not statistical. The
total error relative to the true integral `I` at `N = P` is the
Riemann-sum bias `|R − I|`, which depends on `f` and `P` (see
the convergence table above) but not on the key.

To be explicit about which layer the gap lives in: the structural
layer (zero collisions, `E_P = R`) is unaffected by anything in
this table. The gap is entirely in the statistical layer — it
measures how far the Feistel PRP's key-induced prefix distribution
is from the ideal simple-random-sample distribution *for this
integrand and period*. See the claim-types table above for the
full separation.

### What survives without any PRP assumption

Three properties that hold for *any* permutation of `[0, P)`,
regardless of how it was generated:

1. **Zero collisions at every `N`.** The first `N` outputs are `N`
   distinct values. No draws are wasted on duplicates. This is the
   definition of "permutation." For a PRNG sampling with replacement,
   the expected collision count at `N` draws is `≈ N²/(2P)` (the
   birthday bound), reaching `~0.37P` wasted draws at `N = P`.

2. **Riemann sum at `N = P`.** The estimate equals the population
   mean. Proved above; does not depend on the key or the PRP.

3. **Approximately unbiased estimator** (for a good PRP and bounded
   `f`). If the key is drawn uniformly from the key space and `f` is
   bounded on `[0, 1)`, the expected value of the prefix mean is
   approximately `R`. The deviation `|E_key[estimate] − R|` is at
   most `2‖f‖_∞ · ε` where `ε` is the PRP's distinguishing advantage
   (the factor of 2 arises from shifting a `[−‖f‖_∞, ‖f‖_∞]`-valued
   test into `[0, 1]` for the standard reduction; it drops to
   `‖f‖_∞ · ε` if `f ≥ 0`). For unbounded `f` this bound does not
   apply. For the structural claims (1) and (2), no
   unbiasedness assumption is needed.

### The practical takeaway

- **Set `period = N` when you know your sample budget.** The Riemann
  sum at the end of the sweep is exact and key-independent. This is
  the cipher's strongest guarantee and it holds for any integrand,
  any key, any PRP.
- **At `N < period`, the cipher is better than replacement sampling
  in collisions** (zero vs birthday-bound), which means no draws are
  wasted. The convergence rate depends on PRP quality: for a perfect
  PRP it matches the FPC; for the current Feistel backend it is
  ~2× worse at intermediate `N`. Improving the PRP (e.g., by using
  Speck32 at block sizes where it is available, or a higher-round
  Feistel) would narrow the gap.
- **The FPC is the benchmark, not a guarantee.** It tells you what a
  perfect without-replacement sampler would achieve. The cipher
  approximates it. The approximation is honest: the table above shows
  both the prediction and the reality.


## Companion code

### Theory tests (pass/fail)

- `tests/theory/test_riemann_property.py` — structural layer:
  key-independence across favorable and adversarial integrands,
  direct-R match, identity-permutation isolation, permutation sanity.
- `tests/theory/test_quadrature_rates.py` — quadrature layer:
  each row of the Euler–Maclaurin table as an assertion. No cipher.
- `tests/theory/test_fpc_shape.py` — statistical layer + coupling:
  FPC vs `random.shuffle` baseline, cipher shape, coupling gap
  measurement.

See `tests/theory/README.md` for the full theorem index.

### Experiments (visual)

- `experiments/bidder/unified/riemann_proof.py` — four-panel
  diagnostic. 10 keys converging to the same N=P value; 200-key
  histogram showing zero spread; Riemann error vs P; five integrands
  confirming key-independence.
- `experiments/bidder/unified/adversarial_integrands.py` — quadrature
  bias across four integrands (sin, x, √x, step). Visualizes the
  Euler–Maclaurin rates and confirms key-independence under hostile f.
- `experiments/bidder/unified/mc_diagnostic.py` — MC convergence
  curves, 2D equidistribution, collision counts. Shows the
  dropoff from O(1/√N) to the Riemann floor as N → P.


## See also

- `core/API.md` — the cipher-path API reference.
- `core/BLOCK-UNIFORMITY.md` — the integer-block lemma that defines
  the set `↕ P`.
- `BIDDER.md` — the root API doc, including the `bidder.cipher`
  entry point.
- `guidance/BQN-AGENT.md` — canonical BQN names.
