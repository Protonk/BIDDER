# Beurling generalized primes — source reads

Read order:

1. `sources/generalized/Introduction_Beurling_g_primes.pdf`
   (F. Broucke, ENTR Seminar, Ghent, 29 June 2022, 13 slides) —
   compact orientation.
2. `sources/generalized/PNT_Generalized_Integers_Novi_Sad.pdf`
   (J. Vindas, Novi Sad 2010, 38 slides) — Cesàro extension of
   Beurling's PNT and the local pseudo-function Tauberian theorem.
3. `sources/generalized/beurling-generalized-primes.pdf`
   (R. Olofsson, 2010, 15 pp.) — Mertens for Beurling primes,
   plus Beurling's conjecture on `|N(x) - [x]|`.

The original `beurling-original.pdf` was not opened — the secondary
sources cover the canonical 1937 statement directly.

## What a Beurling system is

A **generalized prime system** is a sequence

    P = (p_j)_{j >= 1},     1 < p_1 <= p_2 <= ...,    p_j -> infinity,

of real numbers (not necessarily integers). The associated
**generalized integers** are the multiplicative semigroup of
formal monomials

    N = (n_k)_{k >= 0},     n_k = p_1^{v_1} p_2^{v_2} ... ,

ordered by their real values `1 = n_0 <= n_1 <= n_2 <= ...`. The
counting functions are

    pi_P(x) = #{p_j <= x},    N_P(x) = #{n_k <= x}.

**Crucial point for BIDDER.** Beurling integers obey **unique
factorisation by construction**: each `n_k` is a monomial in the
abstract variables `p_j`, and even if two monomials evaluate to the
same real number they are kept distinct. The Beurling zeta therefore
factors as an Euler product

    zeta_P(s) = sum 1 / n_k^s = prod_{j} (1 - 1 / p_j^s)^{-1},
                                                                 Re s > 1.

This is **not** the situation in `algebra/Q-FORMULAS.md`. The monoid
`M_n = {1} u nZ_{>0}` is not UF (e.g. `36 = 6 . 6 = 2 . 18` in
`M_2`), and `zeta_{M_n}(s) = 1 + n^{-s} zeta(s)` does not factor as a
Euler product over its atoms. So Beurling theory provides
**techniques and reference points**, not direct theorems, for `Q_n`.

## Examples

- `(P, N) = (P, N_{>0})`: classical primes and integers.
- `P = (2.5, 3, 5, 7, ...)` (replace `2 -> 2.5`):
  `N(x) = sum_{j >= 0} (floor(x (2/5)^j) - floor((x/2)(2/5)^j)) = (5/6) x + O(log x)`.
- Number-field analogue: `P = (|P| : P prime ideal of O_K)`,
  `pi_{O_K}(x) ~ x/log x`, `N_{O_K}(x) = rho_K x + O(x^{1 - 2/(d+1)})`.
- The "throw away primes, add irrationals" construction
  `Q = (P \ {p_1, ..., p_m}) u {q_1, ..., q_n}` is the standard
  toolbox for sharpness examples.

## Beurling's PNT and its sharpness

**Theorem (Beurling, 1937).** If `N(x) = rho x + O(x / log^gamma x)`
for some `rho > 0` and `gamma > 3/2`, then `pi(x) ~ x / log x`.

**Theorem (Diamond, 1970).** The exponent `gamma = 3/2` is sharp:
there exists `(P, N)` with `N(x) = rho x + O(x / log^{3/2} x)` and
`pi(x) NOT~ x / log x`.

Diamond's construction is the canonical "Beurling's-bound-is-tight"
example. Bateman–Diamond (1969) is the standard reference.

## Better remainders, larger zero-free regions

| `N(x)` hypothesis | `pi(x)` conclusion | source |
|---|---|---|
| `rho x + O(x^theta)`, `theta < 1` | `Li(x) + O(x exp(-c sqrt(log x)))` | Landau, 1903 ("avant la lettre") |
| `Li(x) + O(x / log^gamma x)`, `gamma > 1` | `N(x) ~ rho x` | Diamond, 1977 |
| `Li(x) + O(x^theta)`, `theta < 1` | `N(x) = rho x + O(x exp(-c' sqrt(log x log log x)))` | Hilberdink–Lapidus, 2006 |
| `Li(x) + O(x^theta)`, optimal const | `c' = sqrt(2(1 - theta))` | Broucke–Debruyne–Vindas, 2020 |

The Landau direction comes from a zero-free region

    zeta_P(sigma + i t) != 0    for    sigma >= 1 - c^2 / log(2 + |t|).

The Hilberdink–Lapidus direction is **optimal**: Diamond–Montgomery–Vorhauer
(2006) show that for every `theta > 1/2` there is a `(P, N)` with
`N(x) = rho x + O(x^theta)` and `pi(x) = Li(x) + Omega_pm(x exp(-c sqrt(log x)))`.
RH-strength conclusions need more than multiplicative structure +
`N(x) = rho x + O(x^{1/2})`.

## Well-behaved systems

`P` is **alpha-well-behaved** if `Pi(x) = Li(x) + O(x^{alpha + eps})`
for every `eps > 0` but no `eps < 0`. `N` is **beta-well-behaved**
analogously for `N(x) - rho x`. RH says `(P, N_{> 0})` is `[1/2, 0]`.

| result | statement |
|---|---|
| Hilberdink, 2005 | every `[alpha, beta]`-system has `max(alpha, beta) >= 1/2` |
| Zhang, 2007 | exists `[alpha, beta]`-system with `max(alpha, beta) <= 1/2` |
| Broucke–Vindas, 2021 | exists `[0, 1/2]`-system |
| conjecture | for every `alpha, beta in [0, 1)` with `max >= 1/2`, exists an `[alpha, beta]`-system |

## Cesàro-type extension (Vindas et al., 2010)

The Beurling `O(x / log^gamma x)` hypothesis can be **relaxed** to a
Cesàro estimate: there exists `m in N` with

    integral_0^x [N(t) - at] / t . (1 - t/x)^m dt
        = O(x / log^gamma x),    gamma > 3/2,    x -> infinity.

This is **strictly weaker** than Beurling's hypothesis: there exist
generalised number systems satisfying the Cesàro form but not the
direct `O`-form, so the Vindas extension is a proper enlargement.

The proof routes through:

- **S-asymptotics of distributions** (Pilipović–Stanković):
  `f(x + h) ~ rho(h) g(x)` in `S'(R)` weakly.
- **Local pseudo-function boundary behaviour**: an analytic `G(s)`
  on `Re s > alpha` has it on `Re s = alpha` if its distributional
  boundary value is locally a pseudo-function (Fourier transform in
  `C_0(R)`).
- **Tauberian theorem.** For `lambda_k -> infinity` and `c_k >= 0`
  with `sum_{lambda_k < x} c_k = O(x)`: if

      G(s) = sum_k c_k / lambda_k^s  -  beta / (s - 1)

  has local pseudo-function boundary behaviour on `Re s = 1`, then
  `sum_{lambda_k < x} c_k ~ beta x`.

The Cesàro hypothesis translates, via S-asymptotics, into the
boundary-behaviour hypothesis. The Tauberian step then closes.

## Mertens for Beurling primes (Olofsson, 2010)

**Theorem 1.1.** If `N(x) = A x + o(x)` for `A > 0`, then

    lim_{x -> infinity} (1/log x) prod_{p <= x} (1 - 1/p)^{-1}
        = A e^gamma.

`gamma = 0.5772...` is Euler's constant. By logarithm + Möbius
inversion this is

    M := lim [ sum_{p <= x} 1/p - log log x ]
       = gamma + log A + sum_{k = 2}^{infinity} mu(k) / k . log zeta_P(k).

For rational primes, `A = 1` and `M = 0.2614972128...`
(Meissel–Mertens constant). The proof structure is:

- Mertens-style integration by parts on `int (pi(t) - t/log t) t^{-(s-1)} dt / t^2`.
- Lemma 2.3: `sum_{p <= x} (log p)/p ~ log x` for any Beurling system
  with `N(x) = A x + o(x)` — a weighted PNT-lite that drops out
  without needing the unweighted PNT.
- Tauberian step (Hardy–Wright Theorem 434).

**Heuristic curiosity.** The Eratosthenes-sieve Mertens estimate
gives `pi(x) ~ 2 e^{-gamma} x / log x ~ 1.12 x / log x`, off by
`2 e^{-gamma}` from the actual `x/log x`. This same off-by-`2e^{-gamma}`
discrepancy holds for **every** Beurling system, so the
"sieve-vs-PNT" inconsistency is a structural feature of all
Beurling-prime systems, not a quirk of the rational primes.

## Beurling's conjecture on `|N(x) - [x]|` (Olofsson)

**Conjecture 1.2.** If `P` is a Beurling prime system different from
the rational primes, then `limsup_{x -> inf} |N(x) - [x]| / log x > 0`.

**Theorem 1.3.** For every `c > 0` there exists a Beurling prime
system other than the rational primes with `|N(x) - [x]| < c log x`
for all `x >= 1`.

**Construction (Theorem 1.3).** Replace two primes `p_i, p_j` with
the irrational `q = p_i p_j / (p_i + p_j - 1)`. Counting via
inclusion–exclusion gives `|N(x) - [x]| < (2/log q) log x + 6`, and
`q` can be made as large as we want.

**Proposition 3.1.** `|N(t) - [t]| = o(1)` iff `Q = P`. So
`log x` (Theorem 1.3) is the right threshold; the conjecture says
it cannot be beaten.

The proof strategy for the conjecture (still open) routes through
boundary behaviour of `zeta_P(s) - zeta(s)`: the hypothesis
`R(t) = N(t) - [t] = o(\log t)^n` forces `(zeta_P - zeta)/s` to have
no pole of order `n` at `s = 0`. The conjecture would follow if one
could rule out arbitrary-order poles on `Re s = 0`.

**Beurling–Möbius identity** (Vindas, slide 36): under the Beurling
hypothesis (`gamma > 3/2`),

    sum_{k = 1}^{infinity} mu(n_k) / n_k = 0,
    lim_{x -> infinity} (1/x) sum_{n_k < x} mu(n_k) = 0.

## Pointers worth keeping

| reference | what it gives |
|---|---|
| Beurling 1937, *Acta Math.* 68:255 | original statement; in French |
| Bateman–Diamond 1969, MAA Studies 6:152 | textbook treatment of Beurling theory |
| Diamond 1970, *Illinois J. Math.* 14:12 | sharpness of `gamma = 3/2` |
| Diamond 1977 | converse: `pi -> N` direction |
| Hilberdink 2005 | `max(alpha, beta) >= 1/2` |
| Hilberdink–Lapidus 2006 | `pi -> N` with sub-exponential remainder |
| Diamond–Montgomery–Vorhauer 2006 | optimality of zero-free region |
| Zhang 2007 | first `<= 1/2` system |
| Vindas et al. 2010 (Novi Sad) | Cesàro extension; Tauberian via pseudo-functions |
| Olofsson 2010 | Mertens for Beurling primes; conjecture on `|N - [.]|` |
| Broucke–Vindas 2021 | `[0, 1/2]`-system construction |
| Broucke–Debruyne–Vindas 2020 | optimal constant `sqrt(2(1 - theta))` |
| Lagarias 1999 *Forum Math.* 11:295 | Delone-property Beurling integers (classification) |
| Pilipović–Stanković | S-asymptotics machinery used in Tauberian step |

## What this is for, in BIDDER

`M_n` is not a Beurling system (no UF, no Euler product over atoms).
But two things directly transfer:

1. **The Cesàro/pseudo-function Tauberian package** (Vindas et al.)
   takes weak hypotheses on a counting function and converts them
   into asymptotic statements via local boundary behaviour of the
   associated zeta. `zeta_{M_n}(s) = 1 + n^{-s} zeta(s)` is analytic
   on `Re s > 1` with a simple pole at `s = 1`; whether it has
   useful boundary behaviour on `Re s = 1` is a question we have
   not investigated and these tools are the right toolbox if we
   want to push past the formal master expansion in
   `algebra/Q-FORMULAS.md`.

2. **Olofsson's `|N - [.]|` rigidity heuristic** — that systems
   different from `P` cannot be `o(1)` close to the integer count,
   and the threshold is `log x` — gives a template for asking the
   same question of `M_n`. The empirical Phase-2 multiplication-table
   work in `experiments/acm-flow/mult-table/` records `(n - 1) k`-style
   linear deviations from the substrate-naïve count; the Beurling
   line of thinking suggests the right next-order term to look for
   is `O(log x)` after the leading correction, not `o(1)`.

What does **not** transfer cleanly: the unique-factorisation
assumption is load-bearing in nearly every Beurling proof we read
(Mertens, the Cesàro Tauberian step, the boundary-behaviour
arguments). Adapting any of these to `M_n` requires re-deriving
each step inside the non-UF arithmetic semigroup framework
(Beurling generalised primes is **the wrong literature** for the
non-UF question — that points at Diamond–Zhang on arithmetic
semigroups and Knopfmacher's *Abstract Analytic Number Theory*).
The Beurling sources are useful for technique transfer (Tauberian
machinery, pseudo-function methods) and for understanding the
ceilings on what UF + remainder hypotheses can deliver — they tell
us where the Beurling rails end, which is where the genuinely
non-UF work has to begin.
