# Sawtooth-Secant: Results

## The Identity Holds

The binary Champernowne sawtooth log_2(C_2(n)) matches the
theoretical bump of log_2((3+m)/2) to within 1/2^d, where d is
the bit-length class. The epsilon function captures the sawtooth's
concavity almost perfectly.


## The Staircase

The second-order residual (actual bump minus theoretical bump) is
a descending staircase:

| d | n range | mean residual | ratio to prev |
|---|---------|---------------|---------------|
| 5 | 16-31 | -0.00132 | 1.970 |
| 6 | 32-63 | -0.00067 | 1.981 |
| 7 | 64-127 | -0.00033 | 1.996 |
| 8 | 128-255 | -0.00017 | 1.998 |
| 9 | 256-511 | -0.000084 | 1.999 |
| 10 | 512-1023 | -0.000042 | 2.000 |

The halving ratio converges to exactly 2.000. The residual scales
as 1/2^d. The max within every tooth is exactly 0 (at the endpoints).


## The Sign Was Wrong

Predicted: positive staircase (later entries add to the fraction,
increasing concavity). Actual: negative staircase.

The correction: the per-tooth secant is fitted to the actual data,
which already includes the later entries' contributions. The later
entries raise C_2(n) at all points, but they raise it more at the
start of each tooth (where n is small and 2n is relatively large
compared to n) than at the end. This steepens the data-fitted
secant relative to the theoretical secant, reducing the apparent
concavity. The later entries fill in the curve, making it more
linear than the pure function.


## What This Means

The ACM algebra acts as a **linearizer**. It pushes the sawtooth
toward its secant, reducing the concavity. The algebra makes the
curve straighter, not more curved. The linearizing effect halves
at each tooth boundary with ratio converging to exactly 2.

The epsilon identity is about positional notation — how we write
numbers in binary — not about which numbers the monoid selects.
The Champernowne real's scalar value is too coarse to see the
algebra. The ACM structure lives in the stream's statistics:

- Run-length distributions (experiment 1): v_2 ridges
- Boundary patterns (experiment 3): the v_2 barcode, k mod n
  statistics in adjacent bits
- Bit balance (experiment 2): sieve residual scales with mean v_2

The scalar tells us about notation. The stream tells us about
algebra.
