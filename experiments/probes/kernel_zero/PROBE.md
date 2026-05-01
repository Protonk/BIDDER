# kernel_zero — kernel-zero band under coordinate permutation

## Target

Type:

    (p, h, K) → predicate-set
                {k ∈ [1, K] : Q_p(p^h · k) = 0}
              with Q_p evaluated exact-rationally via
              algebra/predict_q.q_general.

The substrate input is a single prime row of the Q-lattice:

    row(p, h)[k - 1] := Q_p(p^h · k),    k = 1, …, K.

Concretely, `q_lattice_4000_h{5,6,7,8}.npy[p - 2, :]` for `p ∈ {2, 3,
5, 7, 11, 13}` and `K = 4000`. The probe tests the lattice-vs-algebra
contract at machine tolerance: every cell of the cached float lattice
must agree with `q_general(p, h, k)` (exact `Fraction`, then float)
within TOL = 1e-12.

The algebra-defined zero set decomposes as:

- coprime cells: `{k ∈ [2, K] : gcd(k, p) = 1, Ω(k) ≤ h - 1}` per
  `KERNEL-ZEROS.md` (i);
- non-coprime cells: `{k = p^t · k' : t ≥ 1, gcd(k', p) = 1, Ω(k') ≤
  h + t - 1}` — same classifier at the effective height
  `h + ν_p(k)` from the master expansion.

The probe does not separate these; it uses the union via
`q_general`. The kernel-zero classifier explains *why* the cells
are zero. The probe checks *whether* the lattice agrees.

The expected coordinate of detection in absence of the transducer is
the original `k`-axis: at every algebra-zero position, the lattice
cell is zero; at every other position, the lattice cell matches
`float(q_general)` within TOL.

## Transducer

Operation: deterministic permutation of the `k`-axis,

    σ(k) = K + 1 - k,    row'[k - 1] = row[σ(k) - 1].

Index reversal. Parameter-free given `K`. The transducer is
**self-inverse** (`σ ∘ σ = id`), which is incidental but worth noting
when reading the no_op channel under reversal.

Information budget: **blind** — the transducer sees only the row of
cell values, not `k`, not `p`, not `h`. Stack depth: 1.

## Channels

| name | motivation | role |
|---|---|---|
| `no_op`                    | original k-axis predicate from `KERNEL-ZEROS.md` (i) applied cell-by-cell | control |
| `zero_count`               | permutation-invariant: number of zeros in the row, against count predicted by `Ω(k) ≤ h - 1, gcd(k, p) = 1, k ≥ 2` | primary |
| `value_multiset`           | permutation-invariant: multiset of all cell values, against multiset of `q_general(p, h, k)` for `k = 1..K` | primary |
| `prime_row_identity_at_k1` | does cell at position 1 still equal `1/h`? `MASTER-EXPANSION.md` C2 predicts σ destroys this | adversarial |

The two primary channels are σ-invariants; the no-op is what σ
should kill on its predicted predicate; the adversarial is a
position-locked observation σ should also kill.

## Recovery

All four channels use exact criteria — closed-form predictions from
`algebra/`, not empirical thresholds.

Numerical tolerance `TOL = 1e-12` is applied to all comparisons. The
lattice files are float; algebra/ is `Fraction`; comparison is
`abs(float(predicted) - cell) < TOL`. The choice of `1e-12` is
deliberate: above-machine tolerance hides any structured residual
signal that might exist between the float lattice and the exact
algebra. `1e-12` is ~5000× machine ε for double precision, tight
enough to catch structured residual at any non-ULP level.

For each channel, given a row and target descriptor `(p, h)`:

- **`no_op`.** Let `Z = {k ∈ [1, K] : q_general(p, h, k) ==
  Fraction(0)}` (the algebra-defined zero set). Verdict PRESENT iff
  `|row[k - 1]| < TOL` for every `k ∈ Z`. Strength =
  `|{k ∈ Z : |row[k - 1]| < TOL}| / |Z|`.

- **`zero_count`.** Let `n_pred = |Z|`, `n_obs = |{k : |row[k-1]| <
  TOL}|`. Verdict PRESENT iff `n_obs == n_pred`. Strength =
  `max(0, 1 - |n_obs - n_pred| / max(n_pred, 1))`.

- **`value_multiset`.** Let `M_pred = sorted(float(q_general(p, h,
  k)) for k = 1..K)` and `M_obs = sorted(row)`. Verdict PRESENT iff
  `|M_pred[i] - M_obs[i]| < TOL` for every `i`. Strength =
  `|{i : |M_pred[i] - M_obs[i]| < TOL}| / K`.

- **`prime_row_identity_at_k1`.** Verdict PRESENT iff `|row[0] -
  float(1/h)| < TOL`. Strength = `1` or `0`.

## Anchor

The probe must reproduce the following on the cached lattice files
`q_lattice_4000_h{5,6,7,8}.npy[p - 2, :]` for `p ∈ {2, 3, 5, 7, 11,
13}` (24 (p, h) cells) under the **identity transducer**:

- `no_op`: PRESENT, strength 1.0.
- `zero_count`: PRESENT, strength 1.0.
- `value_multiset`: PRESENT, strength 1.0.
- `prime_row_identity_at_k1`: PRESENT, strength 1.0.

The anchor leans on `algebra/tests/test_anchors.py` A2 (h=5 matrix), A7
(kernel-zero classifier), A8 (h=6,7,8 matrices). If A1..A10 pass and
the lattice files match the master expansion at machine precision
(`< 1e-9` per `test_within_row_lattice.py`), the anchor here must
pass at `< 1e-12` modulo lattice-side ULP.

## Calibrations

- **Identity** (transducer = identity, substrate = cached lattice
  rows): see Anchor.
- **Known-recovery** (transducer = index reversal, substrate = cached
  lattice rows): predicted `no_op` PARTIAL — strength equals the
  reversal-symmetry of the algebra-zero set,
  `|{k ∈ Z : K + 1 - k ∈ Z}| / |Z|`, which is high at small `p`
  (zeros dense) and lower at larger `p`. Predicted `zero_count`
  PRESENT (σ-invariant), `value_multiset` PRESENT (σ-invariant),
  `prime_row_identity_at_k1` ABSENT (cell at position 1 now holds
  the value originally at position K).
- **Null** (transducer = identity, substrate = synthetic row of
  i.i.d. uniform draws over `[-100, 100]` at fixed seed `0`): all
  four channels predicted ABSENT.
