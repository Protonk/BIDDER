# Extended panel: offset(n) at b = 10, d = 4

The off-spike denominator inflation has the asymptotic form

    δ_k(n) = L_{k−1}(n) − C_{k−1}(n) ~ (n − 1) k + offset(n) − O(b^{−k})

(`OFFSPIKE-RESULT.md`). The per-`n` constant `offset(n)` lands on
clean closed-form values for the original 6-prime panel. The
extended panel — `n ∈ {7, 11, 13}` added — separates the offset
into structured families plus genuine transients.


## Panel at b = 10, d = 4

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

(For `n = 3`, `log_b(b/(b−1)) = log_b(b/n²)` because `n² = b − 1`
exactly. The right framing is `log_b(b/n²)`.)


## Family classification at d = 4

| Family | Closed form | n in panel |
|---|---|---|
| A | offset = log_b(b/n) | 2, 4, 7 |
| B | offset = log_b(b/n²) | 3, 11 |
| D | offset = 0 | 5 |
| F | offset = log_b(1/(b−1)) = −log_b(b−1) | 6 |
| transient | not yet asymptotic at k=4 | 10, 13 |

The membership rule across primes is the multiplicative order
`ord(b, n)`: Family A for `ord = n − 1`, Family B for `ord ∈ {1, 2}`,
intermediate `ord` open. Details in `PRIMITIVE-ROOT-FINDING.md`,
which extends the panel to `n ∈ {17, 19, 23, 29, 31}` and isolates
the rule.


## Slope at d = 4

Asymptotic slope check: per-`k` step from `k = 3` to `k = 4`:

| n | step 3→4 | (n−1) | match |
|---|---|---|---|
| 2 | +1.0008 | 1 | ✓ |
| 3 | +2.0004 | 2 | ✓ |
| 4 | +3.3014 | 3 | off by +0.301 |
| 5 | +4.0004 | 4 | ✓ |
| 6 | +5.0004 | 5 | ✓ |
| 7 | +7.2045 | 6 | off by +1.205 |
| 10 | +9.3014 | 9 | off by +0.301 |
| 11 | +9.5611 | 10 | off by −0.439 |
| 13 | +10.9035 | 12 | off by −1.097 |

The slope `(n − 1)` is reached at `k = 4` for `n ∈ {2, 3, 5, 6}`
(the primes and prime-powers with at least one `d = 1` atom).
For `n ∈ {4, 7, 10, 11, 13}` the explored range is still
transient.

The Family A members `n = 4, 7` and Family B member `n = 11` have
slopes that haven't reached `(n − 1)` at `k = 4` yet, but their
offsets match `log_b(b/n)` and `log_b(b/n²)` respectively to five
decimals. The offset reaches its asymptote *before* the slope, or
the two are coordinated at this resolution.


## Cross-base context

The b = 10 d = 4 panel above is base-specific: `ord(b, n)` shifts
with `b`, so per-`b` family compositions differ. The closed-form
spike scale `S_k = D_k − C_{k−1}` is invariant across bases (its
prefactor structure `(b − 2)/(b − 1)` is confirmed at
`b ∈ {3, 4, 6, 8, 10, 12}`; see `CROSS-BASE-RESULT.md`). The
offset's family classification needs to be redone per `b`.


## Files

- `spike_drift_extended.py` — the extended-panel script.
- `spike_drift_extended.csv` — per-(n, k) data with offset matches.
- `spike_drift_extended_summary.txt` — full text tables.
