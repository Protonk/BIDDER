# Detrended RDS

source: [`experiments/acm-champernowne/base2/disparity/DETRENDED_RDS.md`](../../../experiments/acm-champernowne/base2/disparity/DETRENDED_RDS.md)  
cited in: [`COLLECTION.md` — The Binary Frontier](../../../COLLECTION.md#chapter-4-the-binary-frontier)  
last reviewed: 2026-04-10

---

**Setup.** A 13-monoid panel spanning `v₂(n) = 0..8`, each
monoid's binary Champernowne stream truncated to a `100,000`-bit
prefix at the last entry boundary. Running digital sum
`RDS(t) = Σ(2b_i − 1)` computed per stream, then detrended
two ways: against the per-monoid closed form (parameterized by
`v₂(n)` alone) and against the per-entry closed form
(parameterized by `v₂(entry)` for each individual n-prime).
Both predictions come from the bit-balance formula in
[`hamming-bookkeeping.md`](hamming-bookkeeping.md); the doc's
contribution is applying it at per-entry resolution and
discovering that the per-monoid reading is wrong.

**Headline.** Two results. (1) *The per-monoid reading was
wrong.* For `n = 12`, the residual end under per-monoid
prediction is `−6264`; under per-entry it is `+11`. For
`n = 6` it is `−7785 vs −934`. For `n = 4`, `−2739 vs +158`.
The per-entry correction collapses the residual by 5–500× for
every composite and every `n = 2^m` with `m ≥ 2`, and the
per-monoid claim turns out to be exact only for `n = 1` and
`n = 2`. This was the correction that forced an update to
[`hamming-bookkeeping.md`](hamming-bookkeeping.md). (2) *The
residual after per-entry detrending is not noise.* Every
monoid in the panel shows coherent slow structure at
`8–13 × √n_bits` amplitude, well above a fair-walk envelope.
For `n = 3` the Morlet decomposition in the wavelet follow-up
resolves this into a single dominant scale at `~27,559` bits
over a Brownian background.

**Control.** Entry-shuffled ACM stream: same set of n-primes
in a random permutation. The shuffled control destroys the
oscillation; the original survives. This places detrended RDS
as the disparity-domain twin of Walsh's "order matters"
finding (see [`walsh.md`](walsh.md)).

**Open.** What does the `n = 3` dominant scale correspond to?
The kink follow-up in
[`kink-investigation.md`](kink-investigation.md) proposed a
three-rung arithmetic lattice reading, then walked it back
under audit. A per-monoid wavelet decomposition of the
residual for the other twelve monoids has not been run, and
a Fourier decomposition with the shuffled control as the null
is the obvious next step.
