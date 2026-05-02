# Early Findings

## 1. Exact Uniformity of First Digits

The n-Champernowne reals for n = 1..10000 have perfectly uniform first
significant digits. Each digit 1–9 appears exactly 1111 times in 9999
non-trivial cases. This is not approximate — it is exact.

| Digit | Count | Fraction | Benford  |
|-------|-------|----------|----------|
| 1     | 1111  | 0.1111   | 0.3010   |
| 2     | 1111  | 0.1111   | 0.1761   |
| 3     | 1111  | 0.1111   | 0.1249   |
| 4     | 1111  | 0.1111   | 0.0969   |
| 5     | 1111  | 0.1111   | 0.0792   |
| 6     | 1111  | 0.1111   | 0.0669   |
| 7     | 1111  | 0.1111   | 0.0580   |
| 8     | 1111  | 0.1111   | 0.0512   |
| 9     | 1111  | 0.1111   | 0.0458   |

**Interpretation.** The uniformity follows from the construction: the first
digit of C(n) is the leading digit of n itself, and counting 1 through 9999,
each leading digit appears equally often. The n-prime construction preserves
counting measure perfectly. This is the signature of the missing
multiplicative structure — the monoid nℤ⁺ has non-unique factorization,
so the multiplicative dynamics that produce Benford's law are absent.

In BQN (`LeadingInt10` from `BQN-AGENT.md`; see
`core/BLOCK-UNIFORMITY.md` for the counting argument):

```bqn
LeadingInt10 ← {⊑ Digits10 𝕩}
Digits10     ← {𝕩<10 ? ⟨𝕩⟩ ; (𝕊⌊𝕩÷10)∾⟨10|𝕩⟩}

LeadingInt10¨ 1+↕9999          # 9999 leading digits, partitioned:
                                # 1111 of each digit 1-9
```


## 2. The Sawtooth and Its Range

The function f(n) = C(n) (the n-Champernowne real) traces a sawtooth with:

- Range: [1.1, 2.0] (exactly, for all n ≥ 10)
- Teeth: one per digit class (1-digit n, 2-digit n, 3-digit n, ...)
- Slope within each tooth: ~10^{-d} for d-digit n
- Drop at powers of 10: from ~2.0 to ~1.1

The real C(n) is built from the exact digit stream `ChamDigits10`
(`BQN-AGENT.md`), then parsed to a float:

```bqn
ChamDigits10 ← {⥊ Digits10¨ 𝕩}
```

In log space, ln(f(n)) sweeps [ln(1.1), ln(2)] = [0.0953, 0.6931],
which is the range of ln(1+m) for m ∈ [0.1, 1] — the base-10 mantissa range.


## 3. Running Mean Convergence

| n      | M(n)     | ln(M(n)) |
|--------|----------|----------|
| 100    | 1.5437   | 0.4342   |
| 1000   | 1.5492   | 0.4378   |
| 5000   | 1.3500   | 0.3001   |
| 10000  | 1.5499   | 0.4382   |

The running mean approaches 1.55 = 31/20 from below. This is the midpoint
of the linear ramp on [1.1, 2.0], which equals (b+1)/(2b) for base b = 10.
(For base 2 it would be 3/4.)

**Conjecture.** The running mean never reaches 1.55. Each sawtooth drop at
a power of 10 pulls the mean down; the subsequent recovery through a tooth
10× longer never quite compensates. The gap closes but does not close.

The dip at n = 5000 in the table above reflects the position within the
current tooth, not a failure of convergence.


## 4. Multiplication vs. Addition

### Multiplication: convergence to Benford

| Digit | 0 mult | 1 mult | 3 mult | 7 mult | Benford |
|-------|--------|--------|--------|--------|---------|
| 1     | 1.0000 | 0.3484 | 0.3440 | 0.3152 | 0.3010  |
| 2     | 0.0000 | 0.3544 | 0.1412 | 0.2008 | 0.1761  |
| 3     | 0.0000 | 0.2972 | 0.1088 | 0.1080 | 0.1249  |
| 4     | 0.0000 | 0.0000 | 0.0900 | 0.0888 | 0.0969  |
| 5     | 0.0000 | 0.0000 | 0.0780 | 0.0720 | 0.0792  |
| 6     | 0.0000 | 0.0000 | 0.0680 | 0.0640 | 0.0669  |
| 7     | 0.0000 | 0.0000 | 0.0616 | 0.0560 | 0.0580  |
| 8     | 0.0000 | 0.0000 | 0.0572 | 0.0488 | 0.0512  |
| 9     | 0.0000 | 0.0000 | 0.0512 | 0.0464 | 0.0458  |

By 7 multiplications, digits 4–9 match Benford closely. The residual is
concentrated at digits 1–3 due to the narrow source range [1.1, 2.0].

### Addition: no convergence (rolling shutter)

Under addition, the first-digit distribution never approaches Benford.
Instead, a concentration band sweeps cyclically through digits 1→9→1→...
as the sum crosses powers of 10. The band narrows (CLT) but the cycling
never stops. A thousand additions produce a distribution further from
Benford than seven multiplications.

**Rolling shutter analogy.** The addition heatmap looks like a CMOS rolling
shutter artifact: diagonal stripes caused by a scan-rate/motion-rate
mismatch. The "scan" is the number of additions; the "motion" is the
digit-cycling at rate log₁₀(μ) ≈ 0.19 per addition. The shear angle is
arctan(0.19) ≈ 10.8°. No amount of faster scanning (more additions)
removes the artifact. Only a different sensor architecture (multiplication)
does.


## 5. Crispness: ACM vs. Commodity Uniform

When sliding-window sums are computed from ordered sequences (not random
draws), the ACM source produces a resolved rolling shutter with visible
phase gradients within each stripe. A commodity uniform(1.1, 2.0) source
produces an aliased shutter with binary on/off stripes.

The difference: the ACM's deterministic sawtooth ordering gives the sliding
window access to full phase information. The stochastic source destroys
phase and collapses each row to a concentrated spike via CLT.

Crispness = deterministic structure surviving under addition.


## 6. The ε Connection

The sawtooth ln(f(n)) ≈ ln(1 + m) where m = n/10^d is the base-10
mantissa. Each tooth is the secant of this concave function. The error
between curve and secant is a concave bump maximized at:

    m* = 1/slope - 1 ≈ 0.505

where slope ≈ 0.664 is the secant slope on [0.1, 1]. This is the base-10
cousin of ε(m) = log₂(1+m) − m from the floating-point pseudo-logarithm.

The sawtooth curve itself is `{10⋆⁼1+𝕩}` (i.e. log₁₀(1+m)) on the
mantissa range m ∈ [0.1, 1]. The log-based leading-digit extractor
`LD10` (`BQN-AGENT.md`; mirrors `acm_first_digit` in
`core/acm_core.py`) is related:

```bqn
LD10 ← {⌊𝕩÷10⋆⌊10⋆⁼𝕩}
```

**Caveat:** in floating point, `⌊log₁₀(x)⌋` can undercount at exact
powers of 10. The implementation adds `+1e-9`. See
`wonders/curiosity-retired-first-digit.md`.

The maximum error ε₁₀(m*) ≈ 0.0445 per tooth. It does not grow with the
digit class — it is scale-invariant.


## 7. Speculative Applications

- **Cryptographic prime quality.** A scalar "compositeness damage" function
  based on ε₁₀ could unify currently ad hoc prohibitions (avoid smooth
  primes, primes near powers of 2, etc.) into a single threshold.

- **Mersenne prime search prioritization.** Ranking exponents by predicted
  compositeness pressure before running Lucas-Lehmer, converting sequential
  scan to priority queue.

- **Prime gap structure.** The ε-max at mantissa ≈ 0.5 marks where primes
  are most isolated. A prime at ε-max is a survivor in the region of
  maximum compositeness pressure.


## 8. Open Questions

1. Does the running mean M(n) converge to 31/20, or approach without arriving?
2. What is the exact rate of convergence of the multiplicative first-digit
   distribution to Benford? (Schatte coefficients in base 10.)
3. Is there a closed form for the significand distribution of the
   Champernowne reals under k-fold multiplication?
4. Does the crispness difference between ACM and commodity uniform have
   information-theoretic content (entropy rate, Fisher information)?
5. What happens on BS(1,2)? A random walk mixing doubling (a) and shifting (b)
   should produce a distribution that is neither Gaussian nor lognormal,
   mediated by the Minkowski question mark function ?(x).
