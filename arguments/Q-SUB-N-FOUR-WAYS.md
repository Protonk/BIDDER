# Q_n Four Ways

A critique of `core/Q-FORMULAS.md`. The question is not "are the formulas
correct" — they are. The question is what the formulas actually *are*,
read literally, as a statement about a generating function and integer
divisibility.

The reading below is partially grand, partially mundane, partially
beautiful, partially obviously contingent. Naming the parts is the
point. Once they are named, the contingent parts can be dropped or
rewritten without disturbing the rest.


## The Object

The monoid `M_n = {1} ∪ nZ_{>0}` has Dirichlet series

    ζ_{M_n}(s)
        = Σ_{m ∈ M_n} m^{-s}
        = 1 + Σ_{h ≥ 1} n^{-hs} · ζ(s) · (1 - n^{-s})        [m = n^h k, n ∤ k]
        = 1 + n^{-s} · ζ(s).

That is the entire object. Apply Mercator,

    log(1 + x) = Σ_{j ≥ 1} (-1)^{j-1} x^j / j,

to `x = n^{-s} ζ(s)`:

    log ζ_{M_n}(s)
        = Σ_{j ≥ 1} (-1)^{j-1} n^{-js} ζ(s)^j / j
        = Σ_{j ≥ 1} (-1)^{j-1} n^{-js} (Σ_x τ_j(x) / x^s) / j
        = Σ_m m^{-s} · [Σ_{j : n^j | m} (-1)^{j-1} τ_j(m / n^j) / j]
        = Σ_m m^{-s} · Q_n(m).

So

    Q_n(m) = [m^{-s}] log ζ_{M_n}(s).

That is the master statement. Q_n is the `M_n`-monoid analog of the
classical fact `Λ(n) / log n = [n^{-s}] log ζ(s)`. Everything else in
`core/Q-FORMULAS.md` is bookkeeping for evaluating that one coefficient
at specific `m`.

The same statement has a clean integer-language reading. `τ_j(m / n^j)`
counts ordered `j`-tuples `(d_1, ..., d_j)` with
`d_1 · ... · d_j = m / n^j`, equivalently ordered `j`-tuples
`(n d_1, ..., n d_j)` with product `m` where every factor is a
multiple of `n`. So:

    Q_n(m)
        = Σ_{j = 1}^{ν_n(m)}
            (-1)^{j-1} · (# ordered factorisations of m into j multiples of n) / j.

`Q_n(m)` is a signed Möbius-style count of ordered factorisations of
`m` into multiples of `n`, alternating by tuple length, weighted
`1/j`. The master expansion in `core/Q-FORMULAS.md` is just this
count reorganised by sorting `m` into `(h, t_1, ..., t_r, k')` and
using multiplicativity of `τ_j`. The two readings — generating-function
log-coefficient, and signed factorisation count — are the same fact in
two languages. The first is the analytic-number-theoretic frame, the
second is the combinatorial frame; pick whichever serves the next
move.


## Grand

`Q_n` is a real arithmetic object, not a curiosity. It is the
log-coefficient of an explicit zeta-like generating function. The
formal structure is the standard one:

- the underlying monoid (`M_n` instead of `Z_{>0}`),
- the monoid's Dirichlet series (`1 + n^{-s} ζ(s)` instead of `ζ(s)`),
- its log-coefficient (the analog of `Λ / log`).

Formal manipulations carry over. Mercator expansion of the log,
Dirichlet-series algebra, log-derivative coefficient extraction —
these all work for `ζ_{M_n}(s) = 1 + n^{-s} ζ(s)` exactly as they do
for `ζ(s)`, with `1 + n^{-s} ζ(s)` substituted in. The master
statement `Q_n(m) = [m^{-s}] log ζ_{M_n}(s)` is exactly the analog of
`Λ(n)/log n = [n^{-s}] log ζ(s)`.

But there is a real caveat. `ζ_{M_n}(s) = 1 + n^{-s} ζ(s)` is **not**
a Dirichlet series with an Euler product over the atoms of `M_n`. The
underlying monoid `M_n` is not a UF monoid (the atoms 6 and 6 multiply
to 36, but so do 2 and 18, both atom factorisations of the same
non-atom; M_n has UF defects). Consequently `ζ_{M_n}(s)` doesn't
factor as `Π (1 − p^{-s})^{-1}` over a set of "primes of M_n", and
arguments that depend on the Euler product — which is most of
classical analytic number theory — don't transplant for free. That
includes:

- Tauberian theorems beyond the formal-Mercator level;
- analytic continuation and residue calculations beyond the obvious
  pole at `s = 1`;
- Erdős/Selberg/elementary-method arguments that lean on
  multiplicativity at the prime level;
- sieve identities that exploit Möbius inversion on a UF lattice.

Each of these has a generalisation suitable for non-UF arithmetic
monoids (the literature on "arithmetic monoids" / "Beurling primes"
covers this), but the generalisations are individual theorems with
their own conditions, not a free package.

So the grand part is real: `Q_n` is a genuine analytic-number-theoretic
object, the natural Mangoldt-analog of a specific zeta-like generating
function. But "anything Λ/log allows" is true at the formal level
and qualified at the analytic level. Extracting analytic content
from `Q_n` requires individual translation work, not free analogy.


## Mundane

Given the master statement, the rest of `core/Q-FORMULAS.md` is forced.
Nothing in it requires a theorem deeper than the multiplicativity of
`τ_j` and the binomial identity `τ_j(p^e) = C(e + j - 1, j - 1)`.

| feature in `Q-FORMULAS.md` | source |
|---|---|
| alternating signs `(-1)^{j-1}` | Mercator. |
| `1/j` weights | Mercator. |
| `τ_j(m / n^j)` | the Dirichlet coefficient of `ζ(s)^j`. |
| binomial-product coefficients `∏_i C(a_i(h-j) + t_i + j - 1, j - 1)` | `τ_j` factored multiplicatively at the prime-power components of `n`. |
| the prime / prime-power / multi-prime trichotomy at `h = 3` | the *number* of binomial factors and their parameters, controlled by `ω(n)` and the exponents in `n`. |
| the displayed `h = 3`, `h = 4` tables | small-numerics evaluation of the master expansion. |

There is no new mathematics in the master expansion. There is
`ν_n(m)`, `t_i`, the `τ`-signature of the coprime payload `k'`, all in
service of evaluating `[m^{-s}] log(1 + n^{-s} ζ(s))` at specific `m`.


## Beautiful

Two features are pretty.

1. **Finite rank by an integer fact.** The Mercator expansion is
   formally infinite. It terminates exactly because `n^{-js}` is a
   power of `n^{-s}`, and `ν_n(m)` is a literal integer. The `j`-th
   term contributes to `m^{-s}` only when `n^j | m`, i.e. `j ≤ ν_n(m)`.
   A transcendental-looking series collapses to `h` terms because of
   how many times `n` divides `m`. This is the only genuinely
   surprising structural feature of `Q_n`. It is also exactly the
   freshman-readable kind of fact that the BIDDER blindness pattern
   (`memory/abductive_surprise_pattern.md`) warns about: a property
   that any reader of the formula would see in minutes, that took
   work to recognise.

2. **The trichotomy is `τ_j` factoring at the primes of `n`.** When
   `n` is prime, `τ_j` localised at `n` is one binomial. When `n` is
   a prime power, one binomial with `a` in the index. When `n` is
   multi-prime, a *product* of binomials. The "panel split" between
   prime, prime-power, and squarefree-multi-prime n at `h = 3` is
   exactly which binomial-coefficient structure shows up. It is
   pretty in the same way that Pascal's triangle row symmetries are
   pretty: not deep, but visibly clean.


## Contingent

Much of the rest is presentation. Presentation does real organisational
work, so "contingent" here means "could have been chosen otherwise
without changing the mathematics," not "valueless."

- **The `M_n` monoid framing.** `M_n` is the multiples of `n` with `1`
  adjoined. The unit adjunction is load-bearing for the rank lemma —
  without it, `log ζ_{M_n}(s)` is `-s log n + log ζ(s)`, which has no
  finite-rank truncation. The monoid structure does real work beyond
  vocabulary: it gives "atoms" (rank-1 elements `n·k` with
  `gcd(k, n) = 1`), "rank" / "height" `ν_n(m)` as the maximum
  factorisation length in `M_n`, and the rank truncation `j ≤ ν_n(m)`
  as a statement about the monoid's factorisation depth. Without
  these notions, "the series terminates at h" has no name to attach
  to. So the monoid setup with rank and atoms is a load-bearing
  structural carrier, not just organisational. What's contingent is
  the *specific vocabulary* — "n-prime", "M_n monoid" — many fields
  have their own names for the same objects (e.g. arithmetic-monoid
  literature, Beurling primes, generalized integers). The arithmetic
  underneath is `1 + n^{-s} ζ(s)`; the monoid framing names its
  factorisation theory.

- **The "n-prime" choice.** Atoms are picked as multiples of `n` not
  divisible by `n²`. Any height-1 condition would do, with shifted
  indices; the current choice is the simplest one.

- **The Q vs Λ normalization.** `Q_n(m) = Λ_n(m) / log m`. The
  unnormalized `Λ_n` is the more invariant generating-function object;
  the normalized `Q_n` is cleaner asymptotically (atoms map to `1`).
  Choosing which to display is a choice of preferred limit; the math
  is the same either way.

- **The h = 3, h = 4 tables.** Worked examples, not theorems. Anyone
  with the master expansion and a binomial expansion can regenerate
  them. They earn their place pedagogically; they do not earn it
  mathematically.

- **The h = 3 sign profiles** ("prime ≥ 0", "prime-power often
  negative", "multi-prime negative-dominated"). These are sign
  patterns of small specific binomial sums — facts about `τ_2` vs
  `τ_3` evaluated on the first few coprime payloads. They are not
  ACM-specific.

- **The "panel reading" framing** (now revised). The earlier wording
  in `Q-FORMULAS.md` ("Thus the split is no longer merely empirical.
  The experiment found the visible shadow of the binomial-product
  coefficients.") presented the trichotomy as an empirical phenomenon
  retroactively explained by the formula. The current wording calls
  the trichotomy a specialisation of `τ_j` at the primes of `n`,
  which is what it is. This was the costless drop: the rewrite
  removes a discovery framing without removing any mathematical
  content, and it directs attention away from the panel split as a
  candidate for further depth.


## Single-m vs Coupling-Layer

A scope warning that the analogy to `Λ / log` doesn't immediately
make. `Q_n(m)` is the log-coefficient of `ζ_{M_n}(s)` at a *single*
`m`. It is not the log-coefficient at a *pair* of `m`'s, a
*concatenation* of digit expansions of many `m`'s, or a *count* of
distinct values across an aggregate. Those are different
generating-function objects.

Two coupling-layer observables this project has explored:

- **Continued fractions of the ACM-Champernowne real**
  (`experiments/acm-flow/mega-spike/`). The CF expansion of
  `0 . p_1 p_2 p_3 …` is a feature of the digit concatenation, not
  of `Q_n` at single atoms. The mega-spike formula
  `log_b(a) ≈ T_k − 2 L_{k−1} + log_b(b/(b−1))` involves substrate
  digit positions and convergent denominators; `Q_n`'s value at any
  specific atom is `1` (atoms are rank-1) and doesn't enter directly.
  The connection from `Q_n`'s rank algebra to CF spike behaviour is
  via the `M_n` digit-block geometry, not via `Q_n` itself.

- **Multiplication-table count on `M_n`**
  (`experiments/acm-flow/mult-table/`). `M_n(N)` counts distinct
  products `c_1 · c_2` for cofactors coprime to `n`. The relevant
  generating function is Ford's multiplication-table theorem on
  `Z_{>0}` restricted to a residue class — *not* `log ζ_{M_n}(s)`.
  `Q_n`'s rank-2 cell `Q_n(n²k) = 1 − d(k)/2` appears as a per-cell
  Q value, but the count itself integrates over many `m` and depends
  on the d-distribution on Ford's image of coprime-to-n integers,
  which is its own analytic question (Phase 4 (α′)).

The empirical work in those directories shows the connection from
`Q_n` to coupling-layer observables is structured but not automatic.
At experimentally reachable scales, finite-K bias dominates;
asymptotic deficit-exponent shifts inferred from finite-K mult-table
data turned out to be transient prefactor effects.

The conceptual move: don't read `Q_n` as predicting coupling-layer
observables directly. Read it as the local algebraic object whose
rank-h structure *informs* coupling-layer observables through
generating-function-level translations that have to be done case
by case. The rank truncation is a fact about a single `m`; what
shadow that fact casts in any global aggregate is a separate
calculation.


## One-Line Summary

`core/Q-FORMULAS.md` is the rank-`h` Mercator expansion of
`log(1 + n^{-s} ζ(s))`, evaluated coefficient-wise, with `τ_j`
factored multiplicatively at the primes of `n`. The grand part is
that `1 + n^{-s} ζ(s)` is a real arithmetic generating function. The
beautiful part is that the rank truncates by integer divisibility.
The mundane part is that, given the generating function, the rest
is bookkeeping. The contingent part is most of the presentation.
