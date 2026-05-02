# dsubn — orbit equidistribution and star discrepancy

This directory houses BIDDER's normality and equidistribution work
on ACM-Champernowne reals. Named for `D_N`, the star discrepancy
of the orbit `{bⁿ α}` of shifted decimal tails — the canonical
observable for `b`-density and `b`-normality (Bailey–Crandall 2002,
Theorem 2.2(11)–(12)).

## Why this exists

Most of our digit work so far has measured leading-digit L1
deviation. That is a coarse projection of the right object: the
star discrepancy `D_N({bⁿ α})` of the full orbit. Bailey and
Crandall's "Random Generators and Normal Numbers" framework, set
up in `algebra/PRNG-FRAMEWORK.md`, makes the upgrade explicit —
every normality theorem in the paper goes through discrepancy, not
L1, and the proofs use Weyl exponential sums, Korobov–Niederreiter
order arithmetic, and the Erdős–Turán discrepancy bound. This
directory is where we do that work directly.

## Scope

- Empirical `D_N` and related orbit observables for `C_Bundle`,
  `C_Surv`, and stratifications.
- Translations of the Bailey–Crandall machinery (Weyl sums,
  exponential-sum bounds, growth conditions for normality).
- Probes of conjectures in `algebra/PRNG-FRAMEWORK.md` — most
  immediately, the K-scaling of `D_L*` for `C_Surv`.

## What exists today

- The first probe — bracketing at the discrepancy level — lives at
  `base10/survivors/primality/discrepancy.py` and is documented at
  `base10/survivors/primality/PRIMALITY.md` §EXP05. Result: the L1
  bracketing (`prime-m < bundle < comp-m`) carries to `D_N`, and
  `C_Surv_prime_m` is *more* uniform than the Erdős–Copeland
  baseline (ratio 0.60× of `(log L)/√L`).

- `dn_residual.py` / `dn_residual.png` here — visualisation of the
  signed residual `F_N(t) − t` for each construction. The maximum
  vertical excursion of each curve is its star discrepancy `D_N*`.
  Same data as `discrepancy.png` in primality/, but rendered as the
  Kolmogorov–Smirnov-style residual to make the bracketing visually
  legible at the orbit-distribution level (rather than just as a
  scalar `D_N`).

## Cross-references

- `algebra/PRNG-FRAMEWORK.md` — the framework memo. Conditional
  theorem template; identifies what translates from the source.
- `base10/survivors/primality/PRIMALITY.md` — bracketing finding,
  including EXP05 (the discrepancy probe).
- `base10/survivors/ECHO-STRUCTURE.md` — base-10 echo cascade. The
  empirical fact a normality conjecture has to be consistent with.
- `sources/Random Generators and Normal Numbers.pdf` — Bailey and
  Crandall, *Experimental Mathematics* 11:4 (2002), 527–546.
