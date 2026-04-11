# Red-Team Theory

source: [`tests/theory/RED-TEAM-THEORY.md`](../../../tests/theory/RED-TEAM-THEORY.md)  
cited in: [`COLLECTION.md` — The Discipline](../../../COLLECTION.md#chapter-5-the-discipline)  
last reviewed: 2026-04-10

---

**Thesis.** For a prefix estimator built from a permutation of
`↕ P`, the total error decomposes as

```
E_N(key) − I = (E_N(key) − R) + (R − I)
```

Every claim in the repo about BIDDER's Monte Carlo behavior
lives in one of four layers of this decomposition, and the
layers must be isolated so that cipher-quality facts cannot
silently bleed into algebra facts. The red-team posture is the
operative phrase: *not* "demonstrate that the theorem holds,"
but "isolate the claims that look similar from the claims that
are actually the same, and build controls and null benchmarks
before you trust any measurement."

**Case studies.** Four layers, each with its own claim,
failure mode, attack strategy, and pass/fail test file.
(1) **Structural**: `E_P(key) = R` for any key, tested by
`test_riemann_property.py` against favorable and hostile
integrands, with an identity-permutation isolation check. (2)
**Quadrature**: the Euler–Maclaurin rate table, tested by
`test_quadrature_rates.py` as direct grid math, no cipher
involved. (3) **Statistical**: the finite-population correction
as the ideal without-replacement null, tested by
`test_fpc_shape.py` against a `random.shuffle` baseline. (4)
**Coupling**: the cipher's measured deviation from the ideal
null, reported as a gap rather than a theorem. The doc's
"honest gaps" row is the distinctive move: `ABDUCTIVE-KEY.md`
has no theory test and that absence is called a gap rather
than papered over.

**Discipline prescribed.** Three rules that follow from the
decomposition. (1) *Isolate permutation facts from
cipher-quality facts*: anything that holds for every
permutation is structural and proves as algebra; anything that
depends on PRP quality is coupling and must be measured.
(2) *Never let the backend define its own null*: build the
ideal shuffle baseline explicitly and compare the cipher to it.
(3) *A proposed test must say what would count as failure*; if
it cannot, it is not ready for the theory directory. The red
team is not adversarial — it is structural.

**See also.** [`riemann-sum.md`](riemann-sum.md) — the theorem
this doc organizes the attacks on.
[`tests-theory-readme.md`](tests-theory-readme.md) — the
theorem index that ties each layer's claim to its test file.
[`bidder-generator.md`](bidder-generator.md) — where the
Proved / Measured / Not claimed discipline is most visible at
the generator level.
[`pair-programming.md`](pair-programming.md) — the same
discipline applied to conversations rather than theorems.
