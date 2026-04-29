# Mega-Spike Four Ways

A critique of `experiments/acm-flow/cf/MECHANISTIC-DERIVATION.md`
and the surrounding `cf/` documentation. The question is not
"is the formula correct" — within its window of validity, it is. The
question is what the formula actually *is*, read literally, as a
statement about a single CF observable in a concatenated real.

The reading below sorts the spike formula into substrate-transparent
bookkeeping (most of it), one genuinely surprising reach (substrate
density propagating through a CF observable), and one unmodelled
scalar (`L_{k−1}`, the off-spike denominator process) that is being
asked to carry more weight than it can.


## The Object

The base-b ACM-Champernowne real for `n ≥ 2` is

    x = C_b(n) = 0 . p_1(n) p_2(n) p_3(n) ...

with atoms `p_K(n) = n · c_K`, `c_K = q_K n + r_K + 1`,
`(q_K, r_K) = divmod(K-1, n-1)`.

For the convergent `p_i / q_i` of `x`, the standard CF identity is

    | x − p_i / q_i | = 1 / (q_i · (a_{i+1} q_i + q_{i−1})).

Take logs, write `α := q_{i−1}/q_i ∈ (0, 1)`, drop the `O(1/a_{i+1})`
term:

    log_b(a_{i+1}) ≈ L_match(i) − 2 log_b(q_i)

where `L_match(i) := −log_b |x − p_i/q_i|` is the convergent's
log-matching length to `x`.

Now specialise to the convergent `p_{i_k − 1} / q_{i_k − 1}`
immediately before the d=k radix-block boundary. Empirically,

    L_match(i_k − 1) = T_k + log_b(b / (b−1)),

where `T_k = Σ_{d=1}^k d · N_d(n,b)` is the cumulative digit count
through the d=k block. In smooth blocks,
`N_d(n,b) = (b−1) b^{d−1} (n−1)/n²` is the n-prime count from
`core/BLOCK-UNIFORMITY.md`; otherwise the actual atom count is used.
Substituting and writing `L_{k−1} := log_b(q_{i_k − 1})`:

    log_b(a_k) ≈ T_k − 2 L_{k−1} + log_b(b/(b−1)).

That is the master statement. Everything else in `cf/` is
either evaluating this formula at a panel of `(n, k)`, fitting
`L_{k−1}` against substrate-known quantities, or attempting to
mechanistically derive the residual.

The same statement has a substrate-language reading. The convergent
`p_{i_k − 1}/q_{i_k − 1}` matches `x` for `T_k` digits plus a fractional
`log_b(b/(b−1)) ≈ 0.046` digit's worth of agreement at the boundary.
The `−2 L_{k−1}` is the `q²` in the CF-error denominator. The
"spike" — a large partial quotient `a_k` — is what happens when a
*small* convergent denominator `q_{i_k − 1}` accidentally matches a
*long* digit prefix `T_k`: the CF has to absorb the surplus matching
length into the next partial quotient.


## Grand

The spike formula is a real instance of substrate transparency reaching
into a CF observable. CF expansions are paradigmatically opaque:
for almost any concatenated real you would not know the size of
`a_k` to within a constant, because both `L_match` and `q` are
nontrivial functions of the entire prefix.

Here:

- `T_k` is substrate-counted: closed-form in smooth blocks because
  n-prime density is `(n−1)/n²` and block boundaries are radix powers
  (`core/BLOCK-UNIFORMITY.md`), exact by atom count otherwise.
- `log_b(b/(b−1))` is the residual-fraction boundary-truncation
  factor — universal, derived in three lines.
- `−2 L_{k−1}` is the standard CF error formula; nothing about
  ACM-Champernowne is doing work in that term.

So two of the three terms are substrate transparency, plus a textbook
identity. That a CF observable in a concatenated real has *any* such
decomposition is the grand part. For Champernowne's real,
Liouville-type partial-quotient blowups at the radix boundaries are
known classically; for ACM-Champernowne the analogue holds with the
density `(n−1)/n²` substituted in, and the analogue is empirically
sharp at the precision of the panel.

But there is a real caveat. `L_{k−1}` is *not* substrate-transparent.
It is the log denominator of the convergent immediately before the
boundary, i.e., the output of the off-spike CF process up to the
boundary. The empirical fit

    L_{k−1} = C_{k−1} + (n − 1) k + offset(n) − O(b^{−k}),

with `C_{k−1} = T_{k−1}`, splits `L_{k−1}` into a substrate-transparent
piece (`C_{k−1}`), a substrate-suggestive linear-in-k piece
(`(n−1) k`, with a heuristic cofactor-cycle argument), and a per-n
empirical scalar `offset(n)` whose mechanism is partially open
(clean for `ord(b, n) = 1`; refuted for `ord = 2`; not pinned for
intermediate ord). The grand part is real, but the formula has
*one* unmodelled scalar at its heart, and `MECHANISTIC-DERIVATION.md`
itself flags step 3 — "convergent denominator equals `b^{C_{k−1} +
(n−1)k + 1} / n^{j(n)}`" — as the missing piece.


## Mundane

Given the standard CF identity, the rest is forced.

| feature in the spike formula | source |
|---|---|
| `−2 L_{k−1}` | the `q²` in `\|x − p/q\| = 1/(q·(a q + q_prev))`. |
| `T_k` | smooth-block n-prime count `(b−1) b^{d−1} (n−1)/n²` summed digit-weighted. |
| `log_b(b/(b−1))` | residual-fraction `≈ (b−1)/b · b^{−T_k}` past the d=k boundary; "average leading-digit" heuristic at the next position. |
| `O(b^{−k})` tail | the dropped `log_b(1 + α/a_{i+1})` and finite-k boundary alignment. |
| the `(n−1)/n²` density factor | n-primes are multiples of n whose cofactor is not divisible by n; density is `(1/n) · ((n−1)/n)`. |
| the cumulative digit count `T_k = Σ d · N_d` | summation. |

There is no new mathematics in the master statement. `BLOCK-UNIFORMITY`
provides `N_d`, summation gives `T_k`, the textbook CF identity
provides everything else.

The "derivation" parts of `MECHANISTIC-DERIVATION.md` that *are*
mundane:

- the `(n−1)/n²` factor;
- the `log_b(b/(b−1))` boundary-truncation factor;
- the cofactor-cycle decomposition into `(n−1)`-length cycles;
- the digit-sum divisibility test for ord=1 and the alternating-sum
  constraint for ord=2.

These are substrate facts. They do real organisational work in the
documentation but they are not where the open analytic content is.


## Beautiful

Three features are pretty.

1. **A CF observable has a closed form.** This is the unreasonable
   reach. CF expansion mixes digits in a deeply non-local way, and
   the size of a large partial quotient is normally only available
   through computing the convergent. Here, two of three log-terms in
   `log_b(a_k)` are substrate-transparent, and the third (`L_{k−1}`)
   has a substrate-suggestive linear decomposition. The substrate's
   transparency operationalises one layer past where it had any
   right to.

2. **The cofactor cycle gives the slope `(n−1)`.** Cofactors of
   n-primes are the integers not divisible by n in order; within any
   window of `n` consecutive integers exactly `n−1` survive; cofactors
   come in cycles of length `n−1`; the convergent before the d=k
   mega-spike captures one full cycle past the d=(k−1) boundary. The
   link from "cycle disruption" to "convergent denominator stops
   growing" is heuristic, but the identification of the *slope* with
   the deletion density is structural.
   `(n−1)/n` appears as the multiplication-table asymptote
   `α_n = M_n(K)/M_Ford(K)` in `mult-table/` and as the slope of
   `δ_k(n)` here; both are the same density viewed from different
   angles.

3. **Digit-sum / alternating-sum divisibility shows up as substrate
   absorption.** For ord=1, multiples of n in base b satisfy
   digit-sum ≡ 0 (mod n); for ord=2, alternating-sum ≡ 0 (mod n).
   These tests are elementary substrate facts, but the empirical
   check in `MECHANISTIC-DERIVATION.md` confirms `n^j | M` for the
   integer formed by concatenating atoms, with `j` matching the
   family classification — for ord=1. (For ord=2 the divisibility
   chain *fails*; see contingent below.)


## Contingent

Most of the surrounding presentation is contingent. Presentation
does real organisational work, so "contingent" here means "could
have been chosen otherwise without changing the mathematics" or
"upgrades a single residual into a category."

- **The "mega-spike" framing.** A spike is a CF specialisation
  (one partial quotient near a radix boundary). The "mega-" prefix
  picks out the d=k convergent in particular. Off-spike PQs, mixed
  spikes, and the spike-spectrum aggregate are different observables.
  The naming is fine but it elevates one CF specialisation to a
  research category; the formula speaks only to the d=k convergent.

- **The d=k specialisation.** The empirical formula is reported at
  `k ∈ {2, 3, 4}` for `n` values where the d=k spike exists (formula
  predicts negative spike size for large n at small k). The
  k-dependence has been verified in `MULTI-K-RESULT.md`. The
  formula's *structure* doesn't depend on k=k; it is a statement
  about any d=k convergent in a regime where one PQ dominates.

- **The per-n offset table.** `offset(n)` is reported per n in
  `EXTENDED-PANEL-RESULT.md` and `PRIMITIVE-ROOT-FINDING.md`. The
  values cluster: `log_b(b/n)` for ord = n−1 (Family A) and
  `log_b(b/n²)` for ord ≤ 2 (Family B). Intermediate ord values
  (n = 13, 23, 31) deviate by amounts that don't fit either row.
  The presentation organises the panel into A / B / "transient"
  bins; that organisation is real for n where ord ∈ {1, 2, n−1}
  and *speculative* for the rest. Whether the intermediate-ord
  deviations are finite-k transients or genuine third-family
  behaviour is undecided. Calling them "(transient?)"
  in the table is the right hedge.

- **The off-spike denominator programme.** The spike formula needs
  `L_{k−1}` as data; it does not require the full off-spike process
  to be low-complexity. Treating that process as a separate object is
  useful because it is exactly where the remaining scalar lives, but
  it should not be mistaken for an extra premise of the boundary-spike
  formula.

- **The Family B "mechanism" via M divisibility.** Empirically
  refuted for n=11 (ord=2) in `MECHANISTIC-DERIVATION.md` itself:
  the integer M formed by concatenating atoms through d=k is only
  divisible by `n^1`, yet the convergent denominator absorbs `n^2`.
  The clean derivation works for ord=1 (n=3); the ord=2 case is
  documented as open. The "Family A: one factor of n; Family B:
  two factors of n" classification is empirically real; the
  *mechanism* attributing the second factor to digit-sum-style
  divisibility is contingent, half-derived, and partly known to be
  wrong.

- **Residual bookkeeping.** Several mega-spike docs note where the
  residual has moved (b^{−k} tails, intermediate-ord behaviour,
  off-spike CF). This is useful project hygiene, but it is not
  mathematical content; the formula is true or false independent of
  where one chooses to lodge the residual.


## Single-Spike vs Aggregate

A scope warning. The formula `log_b(a_k) ≈ T_k − 2 L_{k−1} +
log_b(b/(b−1))` is the *log-size of one specific partial quotient*
(the d=k boundary convergent). It is not:

- the *spectrum* of partial quotients of `x`;
- the *typical* PQ size at off-spike positions;
- the *irrationality measure* of `x` (which depends on the
  distribution of large PQ events along `i`, not the size of any
  single one);
- the *normality* of `x` (a digit-frequency statement about the
  expansion, governed by an entirely different generating-function
  object than the CF expansion).

Empirical state at the time of writing:

- **Off-spike CF behaviour.** `OFFSPIKE-RESULT.md` and the
  `δ_k(n) = (n−1) k + offset(n)` regression give a per-n linear
  drift in the off-spike denominator, with the slope substrate-driven
  and the intercept `offset(n)` partially closed-form (Family A /
  Family B classification by `ord(b, n)`). Off-spike PQ *sizes*
  (as opposed to denominators) are Khinchin-typical at the
  precision tested. The formula above does not predict them.

- **Spike spectrum across many k.** `MULTI-K-RESULT.md` extends the
  spike formula to k ∈ {2, 3, 4} in panel; the per-(n, k) fit is
  sharp. But the *aggregate* of spike events across k — their
  density along the index axis i, their pairwise correlations,
  their interaction with off-spike events — is an aggregate CF
  question, not a corollary of the single-spike formula.

- **Irrationality measure / normality.** The largest PQ events
  control the irrationality measure of `x`. The spike formula at
  boundary k gives a derivable conditional lower bound:

      μ(x) ≥ 2 + log_b(a_k) / L_{k−1}  ≈  T_k / L_{k−1}

  (the `+2` cancels against the `−2 L_{k−1}` in `log_b a_k`). In
  leading order `T_k = Θ(k b^k)` with constant
  `(n−1) b / (n² (b−1))`, and `L_{k−1} = T_{k−1} + O(k) = Θ((k−1)
  b^{k−1})`. So `T_k / L_{k−1} → b · k/(k−1) → b`, and under
  the assumption that boundary spikes dominate the approximation
  budget, μ(x) → b. The assumption is exactly the off-spike
  denominator question — whether intermediate convergents achieve
  better approximation rates than the boundary events. Computing
  the rate, the per-base prefactor (which depends on which
  convergent the comparison is run against — pre-spike, post-spike,
  or mid-cycle), and verifying the assumption are clean follow-ups
  all gated on `L_{k−1}`. Normality is independent of the CF
  expansion's PQ sizes; classical Champernowne has known
  Liouville-like CF behaviour and is normal in base 10. The spike
  formula is consistent with normality; it does not bear on it.

The conceptual move: read `log_b(a_k) ≈ T_k − 2 L_{k−1} +
log_b(b/(b−1))` as the local CF observable at one boundary, controlled
by two substrate-transparent quantities and one unmodelled scalar.
The aggregate CF behaviour, the spectrum across i, the irrationality
measure, and the normality question are different observables and
require their own analyses.


## Where the Real Work Lives

Three places, in increasing order of difficulty:

1. **Step 3 of the mechanistic derivation.** Show that
   `q_{i_k − 1} = b^{C_{k−1} + (n−1)k + 1} / n^{j(n)}` to within
   `O(b^{−k})`. Step 1 (best-rational characterisation) is standard
   CF theory. Step 2 is clean for ord = 1, but for ord = 2 the simple
   divisibility argument *fails* empirically and the right replacement
   is open. Step 3 is the missing analytic link.
   A parallel Mahler-style derivation in
   `experiments/acm-flow/cf/` has independently
   named the same gap at looser `O(d · n)` resolution; cross-thread
   convergence on this step strengthens its identification as
   *the* load-bearing open problem of the spike-formula thread,
   rather than an artifact of one author's frame.

2. **Intermediate-ord cases.** n ∈ {13, 23, 31} deviate from both
   Family A and Family B at k = 4. Whether higher k pulls them
   into a clean third family or whether they remain
   transient-finite-k artifacts is undecided. Either
   resolution is informative.

3. **The off-spike denominator process.** This is what `L_{k−1}` is.
   It is fit by `C_{k−1} + (n−1) k + offset(n)`; the
   `(n−1) k` slope has a heuristic cofactor-cycle argument; the
   `offset(n)` is partially classified by `ord(b, n)`; nothing about
   the *off-spike intermediate convergents* (the i indices between
   consecutive boundary spikes) is modelled. Naming the
   off-spike process isolates this gap; it does not fill it.


## One-Line Summary

`log_b(a_k) ≈ T_k − 2 L_{k−1} + log_b(b/(b−1))` is the standard CF
error identity rearranged into log-of-`a`, with `T_k` substituted
via `BLOCK-UNIFORMITY` and `log_b(b/(b−1))` derived as the
boundary-truncation factor. The grand part is that a CF observable
in a concatenated real has any such decomposition. The beautiful
part is that the substrate's `(n−1)/n²` density propagates through
to control the dominant CF observable at boundaries. The mundane
part is that two of the three terms are bookkeeping. The contingent
part is the surrounding category structure — "mega-spike",
Family A/B, off-spike denominator process — built around a single
load-bearing unmodelled scalar `L_{k−1}` that is not yet a derived
quantity.
