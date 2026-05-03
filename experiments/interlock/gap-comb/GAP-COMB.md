# Gap-comb mantissa spectroscopy

The first experiment in `game-start/` collapses each atom to a leading
digit. This experiment keeps the log-mantissa phase. For a finite set
`X`, it computes

    C_X(k) = |X|⁻¹ ∑_{x ∈ X} exp(2πi k frac(log₁₀ x)),    k = 1..64.

The comparison is between three spectra: primes, the actual atom set
`A_S`, and the gap-prime model

    P_G = {p ∈ S : p prime} ∪ {g p ∈ S : g ∈ G \ {1}, p prime}.

If the atom stream is prime-like only at the first-digit margin, this
model should not buy much. If the gap set is actually driving the
mantissa geometry, `P_G` should be much closer to `A_S` than primes
alone.

## Empirical readout

`N = 10⁶`, base `10`, harmonics `k = 1..64`.

```
S             F  |G|       |A|   |model|   A-M   M-A     distP     distM    gain     coh
----------------------------------------------------------------------------------------
<3,5>         7    4   155,333   155,328     5     0   0.00121   0.00001   86.43   1.000
<3,7>        11    6   180,596   180,584    12     0   0.00137   0.00002   74.01   1.000
<4,5>        11    6   185,979   185,961    18     0   0.00142   0.00002   58.00   1.000
<5,7>        23   12   241,068   241,024    44     0   0.00156   0.00003   58.33   1.000
<3,5,7>       4    3   142,080   142,078     2     0   0.00112   0.00001  111.94   1.000
```

`distP` is `L2(C_A, C_primes)`. `distM` is `L2(C_A, C_model)`.
`gain = distP / distM`. `coh` is the complex coherence between the
atom-prime residual and the model-prime residual.

The model does not merely fit spectrally. It is set-close: through
`10⁶`, every model element is an atom in these five cases, and the only
differences are atoms not represented by a single gap times a prime.
For `⟨3,5⟩`, these are the already visible gap-stuck composites
`16, 32, 56, 98, 343`.

The phase-comb scan in `gap_comb.txt` computes peaks from
`C_A(k) / C_primes(k) - 1`. The data peaks and model peaks coincide,
but the largest peaks are not literal point estimates of `log₁₀(g)`.
For `⟨3,5⟩`, the non-unit gap phases are

    2:0.3010, 4:0.6021, 7:0.8451

while the largest finite-`K` peaks appear at `0.9736`, `0.6738`,
`0.3691`, `0.9990`, `0.8809`. This says the forward gap-prime model is
the right object; blind peak-picking needs a deconvolution/windowing
step before it can be treated as gap recovery.

## Files

- `gap_comb.py` — experiment script.
- `gap_comb.txt` — spectral distances and phase-comb peak tables.
- `gap_comb.png` — coefficient magnitudes, residual spectra,
  phase-comb scan, and model-fit bars.
