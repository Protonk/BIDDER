# Extended Panel — offset(n) does not unify

Phase 3.1 (B), step (a) follow-up: extending the panel to
n ∈ {7, 11, 13} to test whether `offset(n)` follows a unified
closed-form rule across primes.

## What we tested

Per `OFFSPIKE-RESULT.md`, the off-spike denominator inflation has the
asymptotic form

    δ_k(n) = L_{k−1}(n) − C_{k−1}(n) ~ (n − 1) · k + offset(n) − O(b^{−k})

with offsets in the original panel:

    n=2: log_b(b/n)               (Family A)
    n=3: log_b(b/(b−1))           (Family B)
    n=4: log_b(b/n)               (Family A) at k=4
    n=5: 0                        (Family D)
    n=6: log_b(1/(b−1))           (Family F)

Adding three primes (n=7, 11, 13) and recomputing all panel offsets at
k=4 with the index-order spike classifier (top three a_i by digit count,
sorted by index → d=2, 3, 4):

| n | observed offset at k=4 | closed-form match |
|---|---|---|
| 2 | +0.6989 | log_b(b/n) = log_{10}(5) |
| 3 | +0.0457 | log_b(b/n²) = log_{10}(10/9) |
| 4 | +0.3979 | log_b(b/n) = log_{10}(2.5) |
| 5 | −0.0000 | 0 |
| 6 | −0.9543 | log_b(1/(b−1)) = −log_{10}(9) |
| 7 | +0.1549 | log_b(b/n) = log_{10}(10/7) |
| 10 | −0.3011 | (no clean match — transient) |
| 11 | −1.0828 | log_b(b/n²) = log_{10}(10/121) |
| 13 | −1.5119 | (no clean match — transient) |

(Note the n=3 entry sharpens: `log_b(b/(b−1))` = `log_b(b/n²)` for n=3
because `n² = b−1` exactly. The right framing is `log_b(b/n²)`.)

## Three families plus transients

| Family | Closed form | n in panel |
|---|---|---|
| A | offset = log_b(b/n) | 2, 4, 7 |
| B | offset = log_b(b/n²) | 3, 11 |
| D | offset = 0 | 5 |
| F | offset = log_b(1/(b−1)) = −log_b(b−1) | 6 |
| transient | not yet asymptotic at k=4 | 10, 13 |

**No unified rule.** The membership criterion that selects family A
vs B vs D vs F across primes 2, 3, 5, 7, 11 is not visible from this
data:

- Family A (n=2, 4, 7) and Family B (n=3, 11) split the smaller
  primes by no obvious arithmetic property.
- gcd(n, b) doesn't predict family (n=2 ∈ A and n=5 ∈ D both have
  n | b; n=3 ∈ B and n=7 ∈ A both have gcd(n, b)=1).
- gcd(n, b−1) doesn't predict (n=3, 6 share factor 3 but live in
  different families).
- Smoothness `n² | b^{k−1}` doesn't predict.
- "Class" of n (prime, prime-power, multi-prime) doesn't predict
  (n=2, 4, 7 in Family A spans prime, prime-power, prime).

So the offset map is structured per n but does not unify under any
elementary substrate property the panel exposes.

## Step structure (asymptotic slope check)

Slope at k=3→4:

| n | step 3→4 | (n−1) | match |
|---|---|---|---|
| 2 | +1.0008 | 1 | YES |
| 3 | +2.0004 | 2 | YES |
| 4 | +3.3014 | 3 | off by +0.301 |
| 5 | +4.0004 | 4 | YES |
| 6 | +5.0004 | 5 | YES |
| 7 | +7.2045 | 6 | off by +1.205 |
| 10 | +9.3014 | 9 | off by +0.301 |
| 11 | +9.5611 | 10 | off by −0.439 |
| 13 | +10.9035 | 12 | off by −1.097 |

The slope `(n−1)` is reached at k=4 for n ∈ {2, 3, 5, 6} (small n
with n < b and at least 1 atom in d=1 block). For n = 4, 7, 10, 11,
13 the explored range is still in transient regime.

This means **two interesting things**:

1. The fact that Family A (n=2, 4, 7) and Family B (n=3, 11) have
   members where slope hasn't reached `(n−1)` yet (n=4, 7, 11)
   means their "offset at k=4" might not be the true asymptote.
   The matches `log_b(b/n)` for n=4, 7 and `log_b(b/n²)` for n=11
   are precise to 5 decimals each — that's strong evidence that
   these ARE the asymptotic offsets (not coincidence), but the
   slope hasn't fully settled. So either the offset reaches its
   asymptote *before* the slope, or there's a coordinated structure
   we're not seeing.

2. n=10 and n=13 are still in genuine transient: neither slope nor
   offset has settled. Higher k is needed to determine their family.

## Where the residue migrated

Following the discipline from `SURPRISING-DEEP-KEY.md` (treat clean
closure at one level as a position update on where unclosability
lives next):

- The slope `(n−1)` closes universally where the asymptote is reached
  — substrate-driven, identified.
- The offset(n) at k=4 closes individually per n — closed-form match
  to 5 decimals each — but the n → family map does not unify. The
  residue from the slope migration has migrated to a *combinatorial
  classification problem*: which n belongs to which family.
- The transient regime for n ∈ {4, 7, 10, 11, 13} carries
  finite-k structure that we haven't characterised. The b^{−k} tail
  story from `MULTI-K-RESULT.md` suggests these eventually reach
  their family's asymptote, but the rate depends on n in ways the
  panel doesn't determine.

## Why this is informative even without a unified rule

Per the metaphysical commitment, ACM-Champernowne is normal /
irrational, so unclosability lives somewhere. The expected outcome
from extending the panel was one of:

(a) A unified offset(n) closed form pops out across primes.
    Verdict: **NO**. The data is precise enough to rule out simple
    unified expressions like `log_b(b/n)`, `log_b(b/n²)`, etc.
    applied universally.

(b) The offset(n) varies per n with no recognisable structure.
    Verdict: **PARTIAL**. Each individual n's offset is a clean
    closed form, but the rule selecting which closed form for which
    n is unknown. The structure is *combinatorial* — a partition of
    primes into families A, B, D, F — not analytic.

(c) Some n's are still transient at k=4 and the asymptote is unclear.
    Verdict: **YES** for n=10, 13. These need higher k.

So the residue has localised: not in a missing analytic term, but
in the **family classification of primes**, which is the kind of
structure that could be a reflection of the substrate's prime
distribution mod (b, b-1, etc.) but doesn't appear from this data
to be a single elementary rule.

## What this is, in the spirit of `SURPRISING-DEEP-KEY.md`

The substrate-transparency that gave us slope `(n−1)` did NOT extend
all the way to a unified offset(n). The pattern of substrate-leakage
is genuinely thinner here than in the prior cases (Hardy bijection,
mega-spike `T_k − 2 L_{k−1}`, etc.). We have closure of one term
in the asymptotic expansion and per-n closure of the next term, but
no closure of the meta-rule.

This is the first instance in the `ABDUCTIVE-KEY` catalogue where
the substrate's transparency is *visibly running out*. Whether this
is the perimeter or just a deeper foothold is undetermined — the
combinatorial classification might itself be substrate-driven and
just not visible in our 9-element panel.

The directional read for the foothold prior:
**still foothold, less confidently**. The `(n−1)` slope is a real
elementary closure. The per-n offset closures are also elementary,
just not yet unified. The unification might exist at a thicker
analytic layer (e.g. dependence on `b mod n`, the order of `b mod n²`,
or some Dirichlet-character structure that the panel doesn't sample
densely enough to expose).

## Next moves (for future work)

a. **Higher k for n = 10, 13.** Settle whether they reach their
   family at k=5 or 6. Costly.

b. **Wider prime panel.** Compute n = 17, 19, 23, … to densely
   sample family membership. Maybe a Dirichlet-character-style
   pattern emerges.

c. **Mechanistic CF derivation of slope `(n−1)`.** Independent of
   offset; probably easier to attack in isolation.

d. **Drop the offset question.** Accept the family partition as
   per-n empirical data, build downstream work (Phase 4) on the
   asymptotic spike formula with empirical offset table.

## Files

- `spike_drift_extended.py` — the extended-panel script
- `spike_drift_extended.csv` — per-(n, k) data with offset matches
- `spike_drift_extended_summary.txt` — full text tables
