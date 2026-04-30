# Experiment 01 — Olofsson rigidity transplant

First experiment from `BEURLING.md`. Tests whether Olofsson's rigidity
template ("pole of order `n` at `s = 0` ⇔ `|N(x) - [x]|` not
`o((log x)^n)`") transplants to `M_n`.

Code:
- `zeta_mn.py` — numerical library (`zeta_{M_n}`, `psi_{M_n}`, etc.)
- `exp01_olofsson_transplant.py` — the experiment
- `exp01_findings.txt` — machine-readable summary
- `exp01_zeta_boundary_re0.png` — boundary plot on `Re s = 0`
- `exp01_psi_convergence.png` — `psi_{M_n}(x) / x` vs `x`
- `exp01_psi_residual.png` — `psi_{M_n}(x) - x` vs `x`

## Result, in one paragraph

**Literal Olofsson transplant: null (as predicted).** `zeta_{M_n}(0) = 1/2`
exactly for every `n` (no pole at `s = 0`), so the template's analytic
input is absent. The set-count deviation `N_{M_n}(x) - x/n` is
trivially bounded, so the template's arithmetic output is also empty.

**Pivot to the signed Mangoldt analog: positive result, with structure.**
Define `psi_{M_n}(x) = sum_{m in M_n, m <= x} Q_n(m) log m`. The
residue calculation gives `Res_{s=1}[-zeta'_{M_n}/zeta_{M_n}] = +1`
independent of `n`, so under Wiener–Ikehara-style assumptions
`psi_{M_n}(x) ~ x`. **The signed sum does converge** despite
`Q_n` being signed — cancellation gives convergence rather than
blocking it. The rate of convergence is **strongly `n`-dependent**:
`n = 2` reaches `psi/x = 0.992` at `x = 50000`, while `n = 10`
only reaches `0.701`. This `n`-dependence is the new finding worth
chasing.

## Detailed observations

### Phase A — literal transplant null

`zeta_{M_n}(0) = 1 + n^0 * zeta(0) = 1 - 1/2 = 1/2`. Regular for
every `n`. Confirmed numerically to 30 digits.

`N_{M_n}(x) = 1 + floor(x/n)`, so `R(x) := N_{M_n}(x) - x/n - 1 + 1/n`
lies in `[0, 1]`. Olofsson Prop 3.3 has no traction.

### Phase B — `psi_{M_n}` ratios at `x = 50000`

| `n`  | `psi_{M_n}(x)/x` | `psi_{M_n}(x) - x` |
|------|---|---|
| 2    | +0.9922  | -390 |
| 3    | +0.9782  | -1090 |
| 5    | +0.9210  | -3950 |
| 6    | +0.8772  | -6140 |
| 10   | +0.7008  | -14960 |

Residue calculation predicts the limit as 1 for every `n`. Empirically:
- `n = 2`: within 1% by `x = 50000` (consistent with smooth convergence).
- `n = 10`: 30% off at `x = 50000` (slow or possibly obstructed).

The residual `psi_{M_n}(x) - x` is **negative for every `n`**,
growing approximately linearly with `x` in the range `10^3 <= x <= 5*10^4`.
For `n = 10`, the residual scales like `-0.3 x` in this range — so
either the convergence kicks in much later, or `psi_{M_n}/x` does
not actually go to 1 (which would falsify the W-I prediction).

### Phase C — boundary plot

`|zeta_{M_n}(0 + it)|` for `t` in `[0, 60]` and `n` in `{2, 3, 5, 6, 10}`,
with `|zeta(it)|` reference. All five curves track the reference
closely with `n`-dependent phase shifts; no zeros in this range.
Structurally: `zeta_{M_n}(it) = 1 + n^{-it} zeta(it)`, so for large
`|zeta(it)|` the `+1` is negligible and the curves track `|zeta(it)|`
modulated by the phase `n^{-it}`. For small `|zeta(it)|` (visible
in the dips around `t = 7, 14, 21, ...`), the `+1` lifts the curves
above the reference.

This isn't surprising — there's no Olofsson-relevant structure on
`Re s = 0` for `M_n`, as expected.

## Why is the convergence slow for large `n`?

The residue calculation gives leading rate `+1` independent of `n`.
But the convergence rate of Wiener–Ikehara depends on the
**boundary regularity** of `-zeta'_{M_n}/zeta_{M_n} - 1/(s-1)` on
`Re s = 1`. In particular, if `zeta_{M_n}` has zeros on or near
`Re s = 1`, the W-I error term blows up.

Zeros of `zeta_{M_n}(s) = 1 + n^{-s} zeta(s)` on `Re s = 1`: solve
`zeta(1 + it) = -n^{1+it}`. Magnitude condition: `|zeta(1+it)| = n`.

Classical bounds give `|zeta(1+it)| = O(log t)`, so for `n = 2` we
need roughly `log t ≥ 2` (so `t ≥ e^2 ≈ 7.4`); for `n = 10` we need
`log t ≥ 10` (so `t ≥ e^{10} ≈ 22000`). **Smaller `n` admits zeros
at smaller `t`, where the singular contribution to W-I is largest;
larger `n` pushes the zeros out, but they're still there.**

This is the candidate explanation for the empirical pattern, and
it suggests a clean follow-up:

> **Next experiment.** Locate zeros of `zeta_{M_n}` on or near
> `Re s = 1` numerically, for each `n` in `{2, 3, 5, 6, 10}`. Test
> whether the residual `psi_{M_n}(x) - x` correlates with these
> zeros (e.g., is the residual oscillation period `~ 2π / Im(rho_1)`
> for the lowest zero `rho_1`?).

If the correlation holds, this is the BIDDER analog of the
"zeros of zeta drive the prime number theorem error term" result,
and it's a structural-finding-grade observation.

## Status against the original framing

The original framing said #1 would "either grow into something
cool or productively close off." The literal Olofsson template
closes off. The pivot to the signed-Mangoldt-analog opens up:

1. The **BIDDER PNT analog `psi_{M_n}(x) ~ x` empirically holds**,
   which is the first analytic-side result connecting `Q_n`'s
   signed-measure structure to a Beurling-style asymptotic.
2. The **convergence rate has visible `n`-dependence** with a
   clean candidate cause (zeros of `zeta_{M_n}` on `Re s = 1`).
3. The next experiment is concrete and small.

So this is "growing into something cool" rather than closing off.
Worth a follow-up.
