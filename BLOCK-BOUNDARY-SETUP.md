# Block Boundary Applications (Speculative)

These are early-stage ideas for where the ACM-Champernowne system's
exact uniformity at block boundaries might be practically useful.
Nothing here is proven or tested. This is an experimental space for
figuring out what the construction buys you.

The core property: for the ACM-Champernowne source in base b, the
leading-digit distribution over n = 1, ..., b^d - 1 is exactly
uniform over {1, ..., b-1}. At these block boundaries the error is
not small — it is zero. Between boundaries, the error follows a
deterministic sawtooth whose shape is known in closed form.


## Batch allocation

If you are distributing N items among buckets and you can choose N,
set N = b^d - 1 for a base b matching your bucket count. Every
bucket receives exactly the same number of items. No residual, no
rounding correction, no off-by-one.

Candidate domains: clinical trial arm assignment, electoral
allocation methods, round-robin scheduling with fairness
constraints, network load balancing across a fixed number of nodes.

The base is a free parameter. 9 buckets: base 10. 255 buckets:
base 256. The block boundaries can be tuned to match the
application's batch sizes.


## Deterministic error budgets

In a system with a uniformity tolerance, the conventional approach
is to draw from a PRNG and bound the deviation statistically
(confidence intervals, chi-squared tests). The ACM source replaces
statistical bounds with a deterministic function: at any sample
size n, the maximum deviation from exact uniformity is a known
function of n and b, computable without simulation.

This lets you write uniformity guarantees into a specification
rather than a test report. The guarantee is structural (follows
from the construction) rather than empirical (follows from
testing).


## Free stratification

Stratified sampling reduces variance by ensuring proportional
coverage of each stratum. The ACM source auto-stratifies at block
boundaries: every leading-digit stratum is hit exactly equally
without needing stratification machinery. Between boundaries, the
sawtooth tells you exactly how far the strata have drifted.

This matters in quasi-Monte Carlo settings where the goal is
variance reduction over plain random sampling. The ACM source
may offer a new family of low-discrepancy sequences with
algebraically predictable uniformity checkpoints.


## Base matching for power-of-two systems

Many computational systems have bucket counts that are powers of 2.
Setting b = 2^k aligns block boundaries with natural batch sizes:

| Base   | Buckets | Block boundaries          |
|--------|---------|---------------------------|
| 16     | 15      | 15, 255, 4095, ...        |
| 64     | 63      | 63, 4095, 262143, ...     |
| 256    | 255     | 255, 65535, 16777215, ... |

At each boundary, the distribution over all non-zero digits is
exactly uniform. For hash tables, color quantization, network
sharding, or any system with 2^k - 1 output classes, the block
boundaries align with standard sizing conventions.


## Small-block ciphers (speculative)

A small-block cipher (e.g. FPE — format-preserving encryption)
encrypts within a small domain: credit card numbers, SSNs, short
tokens. These ciphers need permutations over small alphabets that
look uniform under statistical testing.

The ACM source's exact uniformity at block boundaries might serve
as a building block or test oracle for such ciphers. If the cipher's
output distribution over a domain of size b-1 should be uniform,
the ACM construction provides a reference sequence that IS uniform
at predictable checkpoints — useful for validation, and possibly
for constructing the permutation itself.

This is the most speculative item here. Whether the ACM structure
can meaningfully improve on existing FPE constructions (FF1, FF3-1)
is unknown.


---

*Status: all items speculative. No implementation or testing yet.
This document exists to record ideas worth investigating, not
claims worth defending.*
