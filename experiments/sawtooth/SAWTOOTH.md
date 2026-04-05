# Sawtooth

Five-decade view of the raw `C(n)` sawtooth, the running mean `M(n)`,
and a residual plot that removes the first-order decade template.

Run: `sage -python sawtooth.py` and `sage -python residual.py`


## Why the teeth repeat after 10^2

`sawtooth.py` plots `champernowne_real(n, 5)`. For `n > 5`, the first
five `n`-primes are just

`n, 2n, 3n, 4n, 5n`.

So the plotted value is

`C(n) = 1.[n][2n][3n][4n][5n]`

with the decimal strings concatenated.

Inside a decade, write `n = 10^d u` with `u in [1, 10)`. The only
structural events are when one of `2n, 3n, 4n, 5n` crosses a power of
10 and gains a digit. Those breakpoints occur at the same relative
locations in every decade:

- `u = 2`
- `u = 5/2`
- `u = 10/3`
- `u = 5`

On a log x-axis, each decade gets the same width, so those same
relative breakpoints land in the same places visually. That is why the
yellow sawtooth starts looking decade-repetitive once the low-`n`
startup regime is gone. By `10^2`, all five concatenated blocks are
already multi-digit, so the small-number irregularities are no longer
dominant.


## Residual View

The dominant repeated contribution is the first block:

`1 + n / 10^(floor(log10(n)) + 1)`

which is `1 + u/10` inside each decade.

Define the residual

`R(n) = C(n) - (1 + n / 10^(floor(log10(n)) + 1))`

This removes the first-order decade ramp and leaves the subleading
structure contributed by the later concatenated blocks. `residual.py`
plots:

- `R(n)` itself
- the decade-scaled residual `10^floor(log10(n)) * R(n)`

The second panel factors out the trivial 10x amplitude drop per decade,
so the remaining subleading pattern can be compared across scales.
