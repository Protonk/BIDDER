# Log₂ / Mod-1 Scaffold

This note records the project's coordinate theory and its consequences:
the mod-1 `log₂` circle, the pseudo-log residual `ε`, the displacement
field `Δ^L = −ε` between binary and geometric grids, the density defect
identity, the Fourier decomposition, and the staircase prediction.

The generic antiderivative/Fourier bridge is included only as a short
calculus template at the end. The project-specific content is in the
binary choice of coordinates, the approximation `log₂(1+m) ≈ m`, and
the displacement/staircase consequences that follow from them.

---

## 1. Common coordinate

Let `X > 0` and define

    W = log₂ X.

Write

    N = floor(W),
    T = {W} = W - floor(W) ∈ [0,1).

Then

    X = 2^W = 2^{N+T} = 2^N 2^T.

So:

- `N` is the binade index;
- `T` is the position inside the binade in `log₂` coordinates;
- the mantissa is `M = 2^T`.

Thus mantissa extraction is exactly:

1. move to `log₂` coordinates;
2. reduce modulo `1`;
3. exponentiate back.

In this coordinate, binade boundaries are the integer lattice `ℤ`, and
reducing modulo `1` identifies those boundaries to form the circle
`[0,1)` with endpoints glued.

---

## 2. Periodized density on the circle

If `W` has density `f_W(w)` on `ℝ`, then the density of `T = {W}` on
`[0,1)` is the periodization

    f_T(t) = Σ_{k∈ℤ} f_W(t+k).

Its Fourier series is

    f_T(t) = Σ_{n∈ℤ} c_n e^{j 2π n t},

with coefficients

    c_n = ∫_0^1 f_T(t) e^{-j 2π n t} dt
        = ∫_ℝ f_W(w) e^{-j 2π n w} dw.

So the Fourier coefficients of the periodized density are the
integer-frequency samples of the characteristic function of `W`.

This is the Fourier object attached to the binade lattice.

---

## 3. Reciprocal mantissa

The mantissa `M = 2^T` is reciprocally distributed exactly when `T` is
uniform on `[0,1)`.

Equivalently,

    f_T(t) = 1.

Equivalently,

    c_n = 0    for all n ≠ 0.

In `M`-space this is the density

    f_M(m) = 1 / (m ln 2),    1 ≤ m < 2.

So departure from reciprocality is exactly the non-constant Fourier
content of the periodized `log₂` density.

---

## 4. Canonical binary coordinate change on one binade

On one binade `x ∈ [1,2)`, write

    m = x - 1 ∈ [0,1),
    t = log₂ x ∈ [0,1).

These are related by

    1 + m = 2^t.

Hence the canonical coordinate maps are

    ψ(m) = log₂(1+m),
    φ(t) = 2^t - 1,

with

    ψ = φ^{-1}.

These maps are the coordinate change between linear intra-binade
position `m` and logarithmic intra-binade position `t` selected by
binary representation.

---

## 5. Representation-native density in the log coordinate

Take the continuous idealization of uniform linear density on one
binade:

    f_X(x) = 1,    1 ≤ x < 2.

Under the coordinate change `x = 2^t`, with `dx/dt = 2^t ln 2`, this
becomes

    f_t(t) = 2^t ln 2,    0 ≤ t < 1.

Relative to the reciprocal regime `f_T(t) = 1`, define the defect

    δ(t) = 2^t ln 2 - 1.

This defect has mean zero on `[0,1]`:

    ∫_0^1 δ(t) dt = 0.

The mean-zero property is needed in §7–8: it ensures the accumulated
defect is periodic on the circle.

The defect `δ` is the representation-native departure from
reciprocality, expressed in log-binade coordinates.

---

## 6. Pseudo-log residual

The affine pseudo-log surrogate on `[1,2)` is

    L(x) = x - 1 = m.

The true log-binade coordinate is

    ψ(m) = log₂(1+m).

The residual is therefore

    ε(m) = ψ(m) - m = log₂(1+m) - m.

This is the error of replacing the canonical binary coordinate `ψ` by
the identity map on `[0,1)`.

### Endpoint exactness

At the binade endpoints,

    ε(0) = log₂(1) - 0 = 0,
    ε(1) = log₂(2) - 1 = 0.

The vanishing is an interpolation fact: `m` and `log₂(1+m)` agree at
`m = 0` and `m = 1`.

The location of the vanishing is the binade-lattice fact: these are
the seam points selected by the same `log₂ / mod-1` coordinate system.
That is, the pseudo-log's endpoint exactness occurs at the points
where the circle `[0,1)` is glued (§1).

---

## 7. Density defect and pseudo-log residual

From the representation-specific defect,

    δ(t) = 2^t ln 2 - 1 = φ'(t) - 1,

we get the accumulated defect

    E(t) = ∫_0^t δ(w) dw
         = ∫_0^t (2^w ln 2 - 1) dw
         = (2^t - 1) - t
         = φ(t) - t.

Now substitute `m = φ(t)` and `t = ψ(m)`:

    E(t) = φ(t) - t = m - ψ(m) = -ε(m).

Equivalently,

    E(t) = -ε(φ(t)),
    E(ψ(m)) = -ε(m).

So the accumulated representation-native density defect in the `t`
coordinate is exactly the negated pseudo-log residual after the binary
coordinate change.

This is the project-specific instantiation of the generic template
(§15).

---

## 8. Fourier form

Because `δ` has mean zero (§5), the accumulated defect `E` is periodic
on the circle. By the generic Fourier multiplier (§15), for `n ≠ 0`:

    Ê(n) = δ̂(n) / (j 2π n).

Combined with `E(t) = -ε(φ(t))` from §7, this relates the Fourier
coefficients of departure from reciprocality to the pseudo-log
residual.

The multiplier is generic antidifferentiation (§15). What is specific
to this project is that the `δ̂(n)` being divided are the Fourier
coefficients of the binary representation-native defect
`δ(t) = 2^t ln 2 - 1`, and the result after division is tied to `ε`
through the canonical maps `φ` and `ψ`.

---

## 9. The displacement field

In the Poincare half-plane model, dyadic scaling gives the geometric
context for the binary tiling. The binary partition of `[1, 2)` and
the geometric partition of `[1, 2)` are two coordinate views of the
same structure:

- Uniform-width cells (additive subdivision): horocyclic slicing.
- Equal-log-width cells (geometric subdivision): geodesic slicing.

At depth d, define the binary (uniform) grid point

    b_k = 1 + k/2^d,     k = 0, 1, …, 2^d

and the geometric grid point

    g_k = 2^{k/2^d},     k = 0, 1, …, 2^d.

Both grids agree at the endpoints: `b_0 = g_0 = 1`,
`b_{2^d} = g_{2^d} = 2`. At every interior point they disagree. In
pseudo-log space (where the uniform grid is equally spaced by
construction), the displacement is

    Δ^L_k = (k/2^d) − log₂(1 + k/2^d) = −ε(k/2^d).

This is exactly the negated pseudo-log residual evaluated at the
uniform grid point's mantissa.

`Δ^L` depends only on `(d, k)`, not on the FSM, the delta table, or
the number of states. It is a property of the representation. Any
architecture that processes binary significand bits must absorb this
field.

---

## 10. Hyperbolic distance between the grids

In the half-plane model with the y-axis as logarithmic coordinate,
place the geometric grid at heights `y_k = 2^{k/2^d}` and the binary
grid at heights `y_k = 1 + k/2^d`. The hyperbolic distance between
corresponding points is

    d_hyp(k) = |log(b_k / g_k)| = |log((1 + k/2^d) / 2^{k/2^d})|.

This measures the separation between additive and multiplicative
coordinates at cell `k`. The maximum occurs near
`k/2^d ≈ 1/ln 2 − 1 ≈ 0.4427`, the same mantissa value `m*` where
`ε(m)` peaks.

The displacement field inherits the shape of the pseudo-log error:
zero at the endpoints, concave, maximal near `m*`.

---

## 11. The staircase prediction

The minimax objective makes the optimised error equal to the worst
cell's error. As parameters are added, the identity of the binding
cell changes discretely.

`ε` is zero at the domain boundaries (`m = 0` and `m = 1`), maximal
near `m* ≈ 0.44`, and concave. A low-capacity corrector absorbs cells
where `ε` is small (near boundaries) before where it is large (near
the peak). As capacity increases, the absorbed region expands toward
the peak.

The binding cell — the worst unabsorbed cell — advances in discrete
jumps. This predicts a staircase in the `(C, gap)` curve:

- **Stair locations** are set by `ε`: which cells have similar
  displacement and must be absorbed simultaneously.
- **Stair heights** are set by the architecture's absorptive
  efficiency per parameter.

Near the `ε` peak, many cells cluster at similar displacement (`ε` is
concave and flat-topped near `m*`). An architecture must absorb them
roughly simultaneously. This predicts a wide plateau followed by a
cliff when enough parameters cover the cluster.

The plateau/cliff pattern in the existing wall data is consistent with
this picture: cheap initial gains correspond to absorbing
steep-gradient boundary cells; the cliff corresponds to hitting the
flat-topped cluster near `m*`.

---

## 12. Combinatorial ordering invariance

A smooth exchange rate would require discovering its functional form
empirically and then arguing that the form is architecture-invariant.
A staircase is easier to use.

The stair heights may differ between architectures, but the stair
locations are set by `Δ^L`: architectures processing the same binary
representation confront the same displacement profile and therefore
the same binding-cell ordering, at least after normalisation by
absorptive capacity.

This weakens the claim from "the rate has a recognisable functional
form" to "the combinatorial structure of the rate is
representation-intrinsic." Architecture-invariance then requires only
that different architectures respect the same binding-cell ordering,
not that they achieve the same numerical efficiency.

---

## 13. Spectral-spatial duality

The displacement field `Δ^L = −ε` is the same function whose
accumulated form `E(t) = ∫₀ᵗ (2^w ln 2 − 1) dw` appears in §§7–8 above
as the representation-native density defect and its Fourier
decomposition. The Fourier coefficients satisfy
`Ê(n) = δ̂(n)/(j2πn)`, decomposing the forcing into frequency
components on the binade circle.

If a correction architecture absorbs low-frequency displacement before
high-frequency, the stair locations in §11 correspond to frequency
thresholds: the spectral and spatial views of the staircase are dual
descriptions of the same absorption ordering.

---

## 14. Experimental validation

The displacement field prediction is tested in
[`experiments/tiling/TILING.md`](../experiments/tiling/TILING.md):

- `R0(c*)` correlates with `R0(Δ^L)` at `r = 0.80–0.89` across the
  partition zoo (T3).
- Three adversary partitions failed to break the correlation.
- Basis identification confirms `ε(m_mid)` as the first-order
  predictor (holdout corr `0.86`).
- Width-preserving position scrambles do not degrade the `ε`
  predictor.

---

## 15. Generic calculus template

Let `φ: [0,1] → [0,1]` be a `C^1` increasing bijection with

    φ(0) = 0,
    φ(1) = 1.

Define the source-coordinate defect

    δ_φ(t) = φ'(t) - 1,

and its accumulated error

    E_φ(t) = ∫_0^t δ_φ(w) dw.

Then

    E_φ(t) = φ(t) - t.

For `n ≠ 0`, the Fourier coefficients satisfy

    Ê_φ(n) = δ̂_φ(n) / (j 2π n).

This is a generic calculus/Fourier fact for endpoint-fixing
coordinate changes.

If one transports uniform measure `dt` on the source interval through
the change of variable `y = φ(t)`, then:

- in source coordinates, the Jacobian weight is `φ'(t) dt`;
- in target coordinates, the pushed-forward density is

      1 / φ'(φ^{-1}(y)).

This section is only a template. By itself it does not distinguish
the binary case. In the binary case, `φ(t) = 2^t - 1`,
`ψ(m) = log₂(1+m)`, `ε(m) = ψ(m) - m`, and the instantiation is §7.

## Background sources

The reciprocal density characterisation in §3 is due to Sripad &
Snyder (1978), Proposition 2. The dyad-boundary continuity condition
underlying §§5–6 is due to Lacroix & Hartwig (1992), §IV. The mod-1
convergence criterion used implicitly in §2 is due to Miller &
Nigrini (2007), Theorem 1.1. Detailed reading notes for all three are
in [REFERENCES](REFERENCES.md).
