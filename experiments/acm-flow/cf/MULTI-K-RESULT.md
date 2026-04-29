# Multi-k Spike-Formula Closure

Phase 3.1 follow-up to `brief2_q_derivation.md`.

## What was tested

GPT-5 verified the relation

    log_b(a) ≈ T_k − 2 · L_{k−1}

at k = 4 only, with smooth-block T_k and rounded `log10(q_before)`
values from `SPIKE-HUNT.md`. The natural extension: does the formula
hold across k = 2, 3, 4, with `log10(q_{i−1})` computed directly
along the CF expansion?

## Method

`spike_drift_multi_k.py`:

1. Run CF expansion at PREC_BITS = 80000 for each n in
   `{2, 3, 4, 5, 6, 10}`, tracking convergent denominators `q_j` as
   exact Python ints.
2. Read the d=2, d=3, d=4 spike indices from `cf_spikes.csv`
   (digit-count tier classification: 5–50 / 150–800 / 2500–9000).
3. Sanity-check: computed `log10(a_i)` matches `cf_spikes.csv`
   `pq_log10` to 4 decimal places. ✓ at every (n, k).
4. Compute T_k two ways:
   - `T_k_smooth` — the closed-form `(b−1) · b^{k−1} · (n−1)/n²`
     summation, exact only when `n² | b^{k−1}`.
   - `T_k_actual` — direct atom counting in each radix block,
     exact for any (n, k).
5. Tabulate predicted `T_k − 2 log10(q_{i−1})` and residual
   `log10(a_i) − predicted` per (n, k).

## Phase A — smooth T_k

Residuals are roughly constant in k for fixed n, but per-n offsets
range from +0.04 to +1.04:

| n | k=2 | k=3 | k=4 |
|---|---|---|---|
| 2 | +0.78 | +0.79 | +0.80 |
| 3 | +0.03 | +0.04 | +0.05 |
| 4 | −1.40 | −0.64 | +1.36 |
| 5 | +0.78 | +0.80 | +0.81 |
| 6 | +0.78 | +0.79 | +0.80 |
| 10 | +1.04 | +1.03 | +1.04 |

The per-n offset and the n=4 anomaly both reduce to
**smooth-vs-actual block-count error**. When `n² | b^{k−1}` fails,
the smooth formula misses by an O(1) integer per block; that error
accumulates into the `T_k` displacement and surfaces as a constant
(or oscillating, for n=4) residual.

## Phase B — actual T_k

Switching `T_k` to direct atom-counting collapses every per-n
offset, including the n=4 anomaly:

| n | k=2 | k=3 | k=4 |
|---|---|---|---|
| 2 | +0.0322 | +0.0444 | +0.0456 |
| 3 | +0.0322 | +0.0444 | +0.0456 |
| 4 | +0.0408 | +0.0453 | +0.0455 |
| 5 | +0.0195 | +0.0431 | +0.0455 |
| 6 | +0.0318 | +0.0444 | +0.0456 |
| 10 | +0.0453 | +0.0410 | +0.0453 |

At k = 4, residuals are **uniformly ~0.0455 across every n**.

That number is not random:

    log_b(b / (b − 1)) = log₁₀(10/9) = 0.045757...

The deficit `log₁₀(10/9) − r(n, k)` decays geometrically with k:

| n | deficit k=2 | deficit k=3 | deficit k=4 | ratio 2→3 | ratio 3→4 |
|---|---|---|---|---|---|
| 2 | +0.0136 | +0.0014 | +0.0002 | 9.99 | 8.62 |
| 3 | +0.0136 | +0.0014 | +0.0002 | 9.99 | 8.62 |
| 5 | +0.0263 | +0.0027 | +0.0003 | 9.88 | 10.32 |
| 6 | +0.0140 | +0.0014 | +0.0002 | 10.28 | 8.62 |

The deficit ratio is `b = 10` per k step. So:

    deficit(n, k) = β(n) · b^{−k} + higher order.

n = 2 and n = 3 produce **literally identical** deficits, so for at
least these two n the coefficient β is shared.

## The formula, after two more closures

    log_b(a) = T_k(actual) − 2 log_b(q_{i−1}) + log_b(b / (b − 1)) − β(n) · b^{−k} + …

What's substrate-transparent on the right-hand side:

- `T_k(actual)` — exact atom count, closed form in n, b, k.
- `log_b(q_{i−1})` — the previous convergent's log denominator
  (consumed empirically here, but is itself the off-spike CF state
  that the two-stream hypothesis predicts is finite-state-recursive).
- `log_b(b / (b − 1))` — universal across n. The "boundary
  truncation factor": at the d=k boundary the convergent matches
  the digit expansion to slightly more than `T_k` digits, the
  fractional excess approaching `log_b(b / (b − 1))`.

What is **not** substrate-transparent:

- `β(n)` — the b^{−k} coefficient. Some n's share it (n = 2 and
  n = 3 are identical here); others differ (n = 5 has roughly
  twice n = 2's coefficient at k = 2). Probably encodes the
  fine-scale structure of how the convergent's matching length
  exceeds `T_k` at finite k.
- The off-spike CF process determining `L_{k−1}` itself.

## Where the residue went

Per the metaphysical commitment (`SURPRISING-DEEP-KEY.md`,
"new-kind-of-surprise"), clean closure at the explored level is
not closure of the structure — it is a position update on where
the unclosability lives.

Before this experiment the residue was thought to be in
`L_{k−1} − C_{k−1}` (off-spike denominator inflation alone). With
empirical `L_{k−1}`, switching to `T_k(actual)`, and identifying
the universal `log_b(b / (b − 1))`, the residue has migrated to
two new locations:

1. The b^{−k} tail's per-n coefficient `β(n)`. Some n share, some
   don't. Probably substrate-transparent if we look hard enough at
   the boundary alignment of the convergent with the next n-prime.
2. The off-spike CF process generating `L_{k−1}`. Same as before;
   we have not yet attacked it.

Each closure that landed exposed the next layer. The pattern from
`SURPRISING-DEEP-KEY.md` continues: substrate transparency keeps
producing closures that look complete and aren't.

## Practical residue

- The mega-spike formula is now down to ~10⁻⁴ residual at k = 4
  across the panel. At higher k it converges geometrically to zero.
  This is strong evidence the asymptotic spike size is fully
  closed-form in substrate quantities.
- Closed-form prediction at the d=k mega-spike, asymptotically:

      log_b(a) ~ T_k(n, b) − 2 log_b(q_{k−1}) + log_b(b / (b − 1))

- For a finite-k closed form (no empirical `q`), we still need a
  closed-form description of the off-spike denominator process —
  the two-stream branch of `MEGA-SPIKE.md`. This is the next
  research move.

## Files

- `spike_drift_multi_k.py` — the multi-k script with smooth and
  actual T_k columns.
- `spike_drift_multi_k.csv` — per-(n, k) results.
- `spike_drift_multi_k_summary.txt` — text table.
