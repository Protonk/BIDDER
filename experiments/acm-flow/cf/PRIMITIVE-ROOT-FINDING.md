# offset(n) classification by ord(b, n)

The off-spike denominator offset `offset(n)` separates into families
indexed by the multiplicative order of `b` modulo `n`. For
`ord(b, n) ∈ {1, 2, n − 1}` the offset has a clean closed form;
for intermediate `ord` the resolution at `k = 4` is undecided.

Panel: `n ∈ {2, 3, 4, 5, 6, 7, 11, 13, 17, 19, 23, 29, 31}` at
`b = 10`, classified using a peel-from-above spike classifier
(largest spike → d=4, next-largest with smaller index → d=3, …),
robust to absent d=2 / d=3 mega-spikes for large `n` and to
tail-spikes for small `n`.


## The data

| n  | offset(n) | log_b(b/n) | diff | ord(b, n) | family |
|----|-----------|------------|------|-----------|--------|
|  2 | +0.6989 | +0.6990 | 0.000 | gcd>1 | A |
|  3 | +0.0457 | +0.5229 | −0.477 = −log_b(n) | 1 | B |
|  4 | +0.3979 | +0.3979 | 0.000 | gcd>1 | A |
|  5 | −0.0000 | +0.3010 | −0.301 | gcd>1 | (special) |
|  6 | −0.9543 | +0.2218 | −1.176 | gcd>1 | (special) |
|  7 | +0.1549 | +0.1549 | 0.000 | 6 | A |
| 11 | −1.0828 | −0.0414 | −1.041 = −log_b(n) | 2 | B |
| 13 | −1.5119 | −0.1139 | −1.398 | 6 | (transient?) |
| 17 | −0.2305 | −0.2304 | 0.000 | 16 | A |
| 19 | −0.2788 | −0.2788 | 0.000 | 18 | A |
| 23 | −0.6628 | −0.3617 | −0.301 | 22 | (transient?) |
| 29 | −0.4624 | −0.4624 | 0.000 | 28 | A |
| 31 | −1.4914 | −0.4914 | −1.000 | 15 | (transient?) |


## The rule

The rule is stated for primes `p` with `gcd(p, b) = 1`, the only
case where `ord(b, p)` is defined:

    offset(p) = log_b(b/p)         if ord(b, p) = p − 1     (Family A)
    offset(p) = log_b(b/p²)        if ord(b, p) ≤ 2          (Family B)

Family A members in panel: `n = 7, 17, 19, 29` (primitive-root
primes). Offset matches `log_b(b/n)` to four to five decimals.

Family B members in panel: `n = 3` (ord = 1) and `n = 11` (ord = 2).
Offset matches `log_b(b/n²)`, i.e. Family A shifted by `−log_b(n)`.

Outside the rule's scope (the rows where `gcd(n, b) > 1` or `n` is
composite), the offsets line up empirically:

- `n = 2, 4` land at `log_b(b/n)` — the Family A value, even though
  the rule's coprime hypothesis fails.
- `n = 5` (with `n | b` exactly) lands at offset 0.
- `n = 6` (composite) lands at `log_b(1/(b−1)) = −log_b(b−1)`.

These are observed extensions, not consequences of the rule. Whether
they reflect a broader structure or are case-by-case substrate
accidents is open.


## Intermediate ord

For primes with `ord(b, p)` not in `{1, 2, p − 1}`:

- `n = 13` (ord = 6 = (n−1)/2): offset deviates from Family A by
  `−1.398`.
- `n = 31` (ord = 15 = (n−1)/2): offset deviates by exactly
  `−1.000`.
- `n = 23` (ord = n − 1 = 22): offset deviates from Family A by
  exactly `−log_b(2) = −0.301`. `n = 23` has only one reliable data
  point at `b = 10` — d=2 and d=3 mega-spikes don't exist at this
  base for `n ≥ ~17`.

Different deviations for the same order ratio (n=13 and n=31 both
have ord/(n−1) = 1/2 but deviations −1.398 vs −1.000) say the rule
isn't purely a function of `ord/(n−1)`. Either higher `k` brings
these into Family A or B, or the right asymptote depends on
finer structure.


## Why ord matters: digit-period reading

The connection to `ord(b, n)` is the period of `1/n` in base `b`:

- ord = 1: `1/n = 0.ddd…` with single repeating digit `(b−1)/n`.
  Multiples of `n` in base `b` satisfy the digit-sum divisibility
  test (digit-sum ≡ 0 mod `n`).
- ord = 2: `1/n = 0.dd dd …` with 2-digit repeating block.
  Multiples satisfy the alternating-sum test.
- ord = p−1 (primitive root): `1/n` has maximal period; no
  short-period redundancy.

When `1/n` has short period, the digit string of n-prime multiples
has short-range structure that lets the convergent denominator
absorb extra factors of `n`. The mechanistic chain — substrate
divisibility lifting to convergent denominator factors — is in
`MECHANISTIC-DERIVATION.md`. It works for `ord = 1` (digit-sum
absorption) and fails for `ord = 2` (alternating-sum doesn't lift
to a `n²` factor in the convergent), so the Family B mechanism
is empirically real but not yet derived for the ord=2 case.


## Files

- `spike_drift_extended.py` — script with peel-from-above
  classifier and the `n ∈ {7, 11, 13, 17, 19, 23, 29, 31}` extension.
- `spike_drift_extended.csv` — per-(n, k) data.
- `spike_drift_extended_summary.txt` — text tables.
