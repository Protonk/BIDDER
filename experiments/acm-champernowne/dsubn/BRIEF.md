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

- `residual_kshape.py` / `residual_kshape.png` — EXP-DSUBN-01.
  Tests whether the t-shape of `F_N(t) − t` is K-invariant per
  construction. Result: **the prime-cofactor and composite-cofactor
  sides of the bracketing are structurally different**. Prime-m
  has K-invariant residual shape (mean Pearson ρ = 0.91); comp-m
  has K-dependent shape that even sign-flips between some K pairs
  (mean ρ = 0.24, min ρ = −0.79). This refines the bracketing
  finding from "different amplitudes" to "different K-stability of
  the entire t-profile" — the prime-cofactor sub-population is the
  structurally cleaner target for any future normality proof.

- `shuffle_kshape.py` / `shuffle_kshape.png` — EXP-DSUBN-02.
  Discharges the destroyer for EXP-DSUBN-01 per
  `experiments/VISUAL-REDUCTION-DISCIPLINE.md`. Holds the atom set
  fixed; varies only ordering (raw / entry-shuffled / d-matched).
  Result: the K-invariance is *not* an entry-order property —
  prime-m ρ = 0.91 / 0.91 / 0.91 across the three orderings;
  comp-m ρ = 0.24 / 0.24 / 0.21. The K-stable shape that prime-m
  has and comp-m lacks is a property of the atom set's
  marginal-of-orbit distribution, not of structural ordering. The
  EXP-DSUBN-01 claim downgrades from "structurally different
  ordering" to "structurally different atom-set marginals."

- `refinement_kshape.py` / `refinement_kshape.png` — EXP-DSUBN-03.
  Subtracts the pooled `C_Surv` parent from each cofactor
  refinement. The refinement-deviation `F_N^{prime-m} − F_N^{surv}`
  (and the comp-m analogue) is small (~0.04 peak vs F values 0-1)
  and K-noisy under both raw and entry-shuffle (ρ ≈ 0, min ρ ≈
  −0.65). Reference parent: `C_Surv` itself has ρ = +0.73,
  intermediate between prime-m's +0.91 and comp-m's +0.24.
  **Implication.** The K-stability difference between prime-m
  and comp-m is *not* a structural property of the cofactor
  refinements — both refinements add similar small K-noisy
  perturbations to a parent that is already K-stable. The
  D_N*-normalization in EXP-DSUBN-01 amplifies those small
  perturbations: in prime-m they happen to align with the
  parent's K-stable shape (lifting ρ from 0.73 to 0.91); in
  comp-m they anti-align (collapsing ρ from 0.73 to 0.24).
  C_Surv is the K-stable object the bracketing has been tracking
  all along. The "structurally cleaner target" framing for
  prime-cofactor was promoting normalization-amplified noise to a
  structural claim.

- `k_scaling.py` / `k_scaling.png` — sweeps K ∈ {100, …, 6400} and
  measures `D_L*(K)` for the five constructions. Empirical result:
  `D_L*` does not decay smoothly with K, fluctuates in [0.05,
  0.16] across the K range, and is *outpaced* by `(log L)/√L` at
  large K (every construction including the known-normal
  `C_Bundle_sorted` Champernowne sits at 2-4× the benchmark by
  K = 6400). The bracketing across cofactor-primality also washes
  out as K → ∞. See `algebra/PRNG-FRAMEWORK.md` §"K-scaling result"
  for the conjecture revision: the echo cascade obstructs Erdős–
  Copeland-rate convergence and is the empirical lower bound on
  `D_L*`'s decay.

## Cross-references

- `algebra/PRNG-FRAMEWORK.md` — the framework memo. Conditional
  theorem template; identifies what translates from the source.
- `base10/survivors/primality/PRIMALITY.md` — bracketing finding,
  including EXP05 (the discrepancy probe).
- `base10/survivors/ECHO-STRUCTURE.md` — base-10 echo cascade. The
  empirical fact a normality conjecture has to be consistent with.
- `sources/Random Generators and Normal Numbers.pdf` — Bailey and
  Crandall, *Experimental Mathematics* 11:4 (2002), 527–546.
