# Audit

## Reproducibility

PASS. From `migrants/`, all five requested commands terminated under
`sage -python` and regenerated their declared `.png`, `.npz`, and table
outputs. The printed numbers match `WEB-AGENT-REPLY.md`: EXP1 variance
explained `0.078`; EXP2 Spearman `bin4a/bin4b = +1.000`; EXP3 row
Spearman `+0.896`; synthesis `rho(G,G_synth)=+1.0000` and destroyer
`rho=-0.3183`, MAE `294.5%`. `l1_grid.npz` byte-matches
`../base10/survivors/l1_grid.npz`
(`sha256 2f9cf843a79fd0f53566e6c9390daac6a0599f47a8f82772703caff1be0d821e`).

## Synthesis Tautology

FAIL on framing. `WEB-AGENT-REPLY.md:25-36` says the synthesis applies a
singleton mask inferred from the lattice and closes the bin-1 x bin-2
claim. It does not. `synthesis.py:54-95` recomputes the gap directly:
concatenate bundle atoms, `np.unique`, singleton mask, integer leading
digits, cumulative L1, warmup mean. That is the same algorithm as the
cached substrate generator in `_l1_grid_reference.py:48-81`. The script
only loads `l1_grid.npz` afterward for comparison (`synthesis.py:115-117`);
it never loads `exp07_lattice.npz`.

So `rho(G,G_synth)=+1.0000` is forced. It is a substrate reproduction
sanity check, not independent evidence that the proposed factor explains
the surface. The destroyer half is the honest experiment.

## Numerical Spot Checks

PASS. The support claim is real: there are exactly 718 cells with
cumulative lattice `L=0`, all have `|G| < 1e-12`, and the converse also
holds. This matches `EXP3-FINDINGS.md:8-18`.

PASS. Row Spearman recomputes to `+0.8958535854`, matching
`lattice_alignment.py:59-62` and `EXP3-FINDINGS.md:23-35`.

PASS, with one caveat. The sharp alpha drop is at index 31,
`n0=320`: alpha goes from `+0.00002976` at `310` to `-0.00004265` at
`320`. `sqrt(10^5)=316.23`, distance `3.77` from 320, versus `16.23`
from 300 and `16.77` from 333. Earlier near-zero sign wiggles exist, but
the real discontinuity is the claimed one. This supports
`EXP3-FINDINGS.md:38-60`.

PASS. `n_fingerprint_table.txt:2-21` has bin4a strictly decreasing and
bin4b strictly decreasing over the ladder. The `+1.000` Spearman is
therefore forced by monotonicity, and `EXP2-FINDINGS.md:69-79` states
that honestly.

## Destroyer Fairness

PASS. The destroyer randomises leading digits per duplicated unique atom,
not per position: `new_unique_leading[is_dup] = RNG.choice(...)` and then
`leading = new_unique_leading[inv]` (`synthesis.py:66-75`). That preserves
bundle coherence. `BENFORD_P` is normalized in `synthesis.py:50-51`;
checked sum is `1.0000000000000002`.

Reseed test with `RNG = 123456`: `rho(G,G_destroyed)=-0.3329`, sign
agreement `0.289`, MAE/mean `294.1%`. Similar, not identical, and still
destructive. This does not look cherry-picked.

## Rewrite The Last Paragraph

Replace `WEB-AGENT-REPLY.md:101-103` with:

> EXP1's smooth bin-pure templates explain only 7.8% because they are the
> wrong shape. The exact synthesis should be treated as a sanity check
> that the substrate computation reproduces `G`, not as an independent
> 100% explanation. The evidence worth carrying forward is narrower and
> stronger: bin 1 determines support exactly, row-level lattice density
> predicts gap scale at Spearman `+0.90`, the leading-digit phase flips
> sharply near `sqrt(10^5)`, and Benford-randomising duplicate leading
> digits destroys the surface. Verdict: bin-1 support plus bin-2 phase is
> the right cross-cutting mechanism; the exact reconstruction claim is
> code consistency, not proof.

The same caveat should also hit `WEB-AGENT-REPLY.md:3-8` and `:25-36`.

## Run Next

1. Build a non-tautological synthesis using only `exp07_lattice.npz`
   support/count features plus leading-digit phase summaries, with no
   `np.unique` recomputation of the survivor mask.
2. Run a seed ensemble for the destroyer and report mean, standard
   deviation, and tail rank of the observed surface.
3. Test the phase-flip ladder directly: finer grid near `n0=100`,
   `320`, and `1000`, plus a base-b migration run.
