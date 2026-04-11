# Hardy Sidestep

source: [`core/HARDY-SIDESTEP.md`](../../../core/HARDY-SIDESTEP.md)  
cited in: [`COLLECTION.md` — The Construction](../../../COLLECTION.md#chapter-1-the-construction)  
last reviewed: 2026-04-10

---

**Claim.** For `n ≥ 2` and `K ≥ 1`, the K-th n-prime is

```
p_K(n) = n · (q · n + r + 1)
```

where `q, r = divmod(K − 1, n − 1)`. One `divmod`, one multiply,
polylog cost in `K + n`. The contrast is with the ordinary-prime
case `n = 1`, where the best known methods reach the K-th prime
in roughly `K^{2/3 + o(1)}` operations via Meissel–Lehmer
prime counting plus local sieving — super-polylogarithmic, and
at `K = 2^4096` still out of reach.

**Mechanism.** The valid `k`-values (those with `n ∤ k`) form an
arithmetic progression with one residue removed per period of
length `n`: `1, 2, …, n−1, n+1, …, 2n−1, 2n+1, …`. There are
exactly `n − 1` valid `k` per period, so the K-th valid `k` sits
in period `q = ⌊(K − 1) / (n − 1)⌋` at offset `r = (K − 1) mod
(n − 1)`, giving `k_K = q·n + r + 1`. Multiplying by `n` gives
the K-th n-prime. Proof is one line of high-school arithmetic.

**Depends on.** The definition of n-primes from
[`acm-champernowne.md`](acm-champernowne.md). Nothing else.

**Supports.** The `sawtooth` path of
[`bidder-root.md`](bidder-root.md) (random access into any
monoid's n-prime sequence); the fourth instance of leaky
parameterization in [`abductive-key.md`](abductive-key.md)'s
meta-essay (four channels for recovering `n_k`); the
math-ready-but-cipher-unbuilt n-prime BIDDER variant.

**Status.** Proved. The closed form is verified against the
enumerating sieve in `core/acm_core.py` for all `(n, K)` with
`2 ≤ n ≤ 12` and `1 ≤ K ≤ 200` (2,200 cases). Single-shot
timings at astronomical `K` (e.g. `n = 2`, `K = 2^4096`, answer
1,234 digits wide, microseconds of work) are documented as
computational witnesses. The "why Hardy sidestep" naming
rationalization is the distinctive passage: the gap between
consecutive n-primes is always exactly `n` or `2n` by
construction, so there is nothing irregular for the analytic
apparatus to describe.
