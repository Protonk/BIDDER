"""
offspike_dynamics.py — block-level structure of the off-spike CF process
=========================================================================

KHINCHIN-RESULT.md establishes that the off-spike CF *marginal* distribution
on C_b(n) is consistent with Gauss-Kuzmin at the resolution of the current
probe. This script asks the next-finer question: at the level of the
*block-total* statistics between consecutive boundary spikes, does the
process match the substrate-driven closed form, or does it deviate?

The boundary-spike formula (MEGA-SPIKE.md) gives the convergent denominator
at boundary indices in closed form:

    L_{k-1} := log_b(q_{i_k - 1}) = C_{k-1} + (n-1) k + offset(n) - O(b^{-k})

Differencing across consecutive boundaries:

    Δ_k := L_{k-1} - L_{k-2} = D_{k-1} + (n-1) + O(b^{-(k-1)})

where D_{k-1} = (k-1) · N_{k-1} is the substrate digit count at d=k-1.
This is a *substrate-only* prediction for the total log-denominator growth
in the inter-spike block ending at the k-th boundary spike.

If the block actually accomplishes that growth via off-spike PQs whose
geometric mean is Khinchin's constant K (so log_b a per PQ averages
log_b K), then the off-spike PQ count predicted under Khinchin is:

    M_k_pred = Δ_k / log_b(K_0)

where K_0 = 2.6854520010... is Khinchin's constant.

Three concrete tests:

  TEST A. Block-total log-denominator growth.
          Observed:  L_{i_k - 1} - L_{i_{k-1} - 1} (computed from the
                     convergent recurrence q_j = a_j q_{j-1} + q_{j-2}).
          Predicted: D_{k-1} + (n-1).
          Expected agreement: tight, to O(b^{-(k-1)}).

  TEST B. Off-spike PQ count between boundaries.
          Observed:  M_k = #{j : i_{k-1} < j < i_k, j off-spike}.
          Predicted: Δ_k / log_b(K_0) ± sqrt(Δ_k · σ²(log_b a)/E[log_b a]³).
          Tests that the block consumes its log-denominator at the
          Khinchin-mean rate.

  TEST C. Sum of log_b a over off-spike PQs in the block.
          Observed:  Σ_{j off-spike in block} log_b(a_j).
          Predicted: Δ_k - log_b(a_{i_{k-1}}) (i.e., total minus the
                     spike PQ at the start of the block).
          Self-consistency check; tight by construction.

Foothold reading:  All three match to within sqrt(M)·noise. The off-spike
                   process between boundaries is a Khinchin random walk
                   with substrate-set boundary conditions.
Perimeter reading: Tests A or B show systematic deviation. The off-spike
                   process has structure not reducible to substrate +
                   Khinchin marginals.

Outputs:
  offspike_dynamics.csv         per-(n, k) block statistics
  offspike_dynamics_summary.txt human-readable test results
"""

import csv
import math
import os
import sys
from math import log2

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'core'))

from acm_core import acm_n_primes

from mpmath import floor as mfloor
from mpmath import mp, mpf
from mpmath import log10 as mp_log10


NS = [2, 3, 4, 5, 6, 10]
B = 10
MAX_PQ = 5000
LOG10_SPIKE = 3.0          # match cf_khinchin_probe.py
PREC_BITS_LO = 80_000
PREC_BITS_HI = 160_000
K_PRIMES = 20_000
HERE = os.path.dirname(os.path.abspath(__file__))

# Canonical per-n offsets for L_{k-1} = C_{k-1} + (n-1)k + offset(n).
# From OFFSPIKE-RESULT.md / PRIMITIVE-ROOT-FINDING.md.
CANONICAL_OFFSET = {
    2: math.log10(5),       # ≈ +0.6990
    3: math.log10(10/9),    # ≈ +0.0458
    4: math.log10(2.5),     # ≈ +0.3979 (transient-flavoured but stable at k≥3)
    5: 0.0,
    6: -1 + math.log10(10/9),  # ≈ -0.9542
    10: math.log10(0.5),    # ≈ -0.3011 (transient-flavoured)
}
OFFSET_TOL = 0.05           # canonical iff |offset_obs - expected| < tol

# Khinchin's constant.
K0 = 2.6854520010653064
LOG_B_K0 = math.log(K0) / math.log(B)  # ≈ 0.4290 for b=10

# Variance of log_b(a) under Gauss-Kuzmin, computed numerically (sum
# truncated at large k; Σ_{k≥K} of (log_b k)² · log_2(1+1/(k(k+2))) tail
# converges as ~(log K)²/K).
def gk_log_b_moments(b, kmax=10**6):
    m1 = 0.0
    m2 = 0.0
    log_b = math.log(b)
    for k in range(1, kmax + 1):
        p = log2(1.0 + 1.0 / (k * (k + 2)))
        lk = math.log(k) / log_b
        m1 += lk * p
        m2 += lk * lk * p
    return m1, m2 - m1 * m1


def cf_partial_quotients(frac_digits, max_pq, prec_bits):
    mp.prec = prec_bits
    x = mpf('0.' + frac_digits)
    a = []
    for _ in range(max_pq):
        frac = x - mfloor(x)
        if frac == 0:
            break
        x = 1 / frac
        ai = int(mfloor(x))
        a.append(ai)
    return a


def stable_prefix_len(a_lo, a_hi):
    k = 0
    upper = min(len(a_lo), len(a_hi))
    while k < upper and a_lo[k] == a_hi[k]:
        k += 1
    return k


def safe_log10(v):
    if v <= 0:
        return 0.0
    try:
        return math.log10(v)
    except (OverflowError, ValueError):
        return float(mp_log10(mpf(v)))


def safe_log_b(v, b):
    return safe_log10(v) / math.log10(b)


def block_count(n, b, d):
    """N_d(n, b): count of d-digit n-primes for the given (n, b).
    Direct enumeration since the smooth closed form fails when
    n^2 does not divide b^{d-1} (e.g. n=2, d=1)."""
    lo = b ** (d - 1) if d > 1 else 1
    hi = b ** d - 1
    # n-primes are n*c with c >= 1 and gcd(c,n)=1 ... actually with
    # n ∤ c. Match acm_core: result.append(n * k) for k where k % n != 0.
    c_lo = (lo + n - 1) // n   # smallest c with n*c >= lo
    if c_lo < 1:
        c_lo = 1
    c_hi = hi // n             # largest c with n*c <= hi
    cnt = 0
    for c in range(c_lo, c_hi + 1):
        if c % n != 0:
            cnt += 1
    return cnt


def cumulative_C(n, b, k_minus_1):
    """C_{k-1} = sum_{d=1}^{k-1} d * N_d(n, b)."""
    return sum(d * block_count(n, b, d) for d in range(1, k_minus_1 + 1))


def compute_one(n):
    primes = acm_n_primes(n, K_PRIMES)
    digits = ''.join(str(p) for p in primes)

    a_lo = cf_partial_quotients(digits, MAX_PQ, PREC_BITS_LO)
    a_hi = cf_partial_quotients(digits, MAX_PQ, PREC_BITS_HI)
    n_validated = stable_prefix_len(a_lo, a_hi)
    a = a_lo[:n_validated]

    # Convergent denominators q_j (Python bignum).
    q_prev, q_curr = 1, 0  # q_{-1}=0 in standard CF; here q_0=1 for the
                           # 0th step convention. We'll track L_j = log_b q_j
                           # for j = 1, 2, ..., len(a).
    # Actually use q_{-1}=0, q_0=1, q_j = a_j * q_{j-1} + q_{j-2}.
    qs = []
    q_minus1, q0 = 0, 1
    qprev, qcurr = q_minus1, q0
    for ai in a:
        qnext = ai * qcurr + qprev
        qs.append(qnext)
        qprev, qcurr = qcurr, qnext

    log_b_a = [safe_log_b(v, B) for v in a]
    log_b_q = [safe_log_b(v, B) for v in qs]

    is_spike = [safe_log10(v) > LOG10_SPIKE for v in a]

    return {
        'n': n,
        'a': a,
        'qs': qs,
        'log_b_a': log_b_a,
        'log_b_q': log_b_q,
        'is_spike': is_spike,
        'n_validated': n_validated,
    }


def analyze(rec):
    """Partition into inter-canonical-spike blocks and run the tests."""
    n = rec['n']
    a = rec['a']
    log_b_a = rec['log_b_a']
    log_b_q = rec['log_b_q']
    is_spike = rec['is_spike']

    spike_indices = [i for i, s in enumerate(is_spike) if s]  # 0-based

    # Substrate predictions for k = 2..7.
    pred_delta = {k: (k - 1) * block_count(n, B, k - 1) + (n - 1)
                  for k in range(2, 8)}
    pred_C = {k: cumulative_C(n, B, k - 1) for k in range(2, 8)}
    canonical_off = CANONICAL_OFFSET.get(n, 0.0)

    # Pass 1: classify every spike candidate as canonical / sub-canonical.
    spikes = []
    for s in spike_indices:
        L_at = log_b_q[s - 1] if s >= 1 else 0.0
        # Find best-fit k (closest canonical L_{k-1} = C_{k-1} + (n-1)k + offset).
        best_k = min(pred_C.keys(),
                     key=lambda k: abs(L_at - (pred_C[k] + (n - 1) * k
                                               + canonical_off)))
        L_pred_canonical = pred_C[best_k] + (n - 1) * best_k + canonical_off
        canonical = abs(L_at - L_pred_canonical) < OFFSET_TOL
        spikes.append({
            's': s,                       # 0-based PQ index
            'spike_index_1based': s + 1,
            'L_at': L_at,
            'k_best': best_k,
            'offset_from_canonical': L_at - L_pred_canonical,
            'canonical': canonical,
            'log_b_a': log_b_a[s],
        })

    # Pass 2: pair up consecutive canonical spikes; for each canonical
    # block report Δ_obs (canonical-to-canonical), the interior PQs split
    # into "small" (off-spike, log10 ≤ LOG10_SPIKE) and "sub-canonical"
    # (large but not canonical), and per-block test stats.
    canonical_spikes = [sp for sp in spikes if sp['canonical']]
    spike_set = set(sp['s'] for sp in spikes)
    canonical_idx_set = set(sp['s'] for sp in canonical_spikes)

    blocks = []
    prev = None  # previous canonical spike (dict)
    for cur in canonical_spikes:
        s_cur = cur['s']
        s_prev = prev['s'] if prev is not None else -1
        interior_range = range(s_prev + 1, s_cur)  # exclude both endpoints

        # All PQs in interior (between consecutive canonical spikes).
        small = []      # truly off-spike (not in any spike_set)
        subcanon = []   # spike candidates but non-canonical
        for j in interior_range:
            if j in canonical_idx_set:
                continue  # shouldn't happen but be defensive
            if j in spike_set:
                subcanon.append(j)
            else:
                small.append(j)

        M_small = len(small)
        M_sub = len(subcanon)
        sum_small = sum(log_b_a[j] for j in small)
        sum_sub = sum(log_b_a[j] for j in subcanon)

        L_cur = cur['L_at']
        L_prev = prev['L_at'] if prev is not None else 0.0
        Delta_obs = L_cur - L_prev

        # Substrate prediction: difference of two adjacent canonical Ls
        # at k_cur and k_prev. If they are consecutive (k_cur = k_prev+1)
        # this collapses to D_{k_cur-1} + (n-1). For non-consecutive
        # (a canonical spike was missed), the prediction is a multi-step
        # sum.
        k_cur = cur['k_best']
        k_prev = prev['k_best'] if prev is not None else 1
        # L_prev would be 0 if no previous canonical spike — i.e., we're
        # measuring growth from origin. The substrate prediction in that
        # case is L_cur (closed form value) directly.
        if prev is None:
            Delta_pred = (pred_C[k_cur] + (n - 1) * k_cur + canonical_off)
            note = '(from origin)'
        else:
            Delta_pred = ((pred_C[k_cur] + (n - 1) * k_cur + canonical_off)
                          - (pred_C[k_prev] + (n - 1) * k_prev
                             + canonical_off))
            note = f'(k={k_prev}→{k_cur})'

        # Khinchin M prediction for the truly small PQs.
        # Under Gauss-Kuzmin, the small PQs have mean log_b a = m1
        # (Khinchin geometric-mean log) — but conditioned on being
        # off-spike (log10 a ≤ LOG10_SPIKE), the conditional mean is
        # m1 minus the tail. For LOG10_SPIKE = 3, the tail above 10^3
        # contributes negligibly to m1, so we use m1 directly.

        blocks.append({
            'k_cur': k_cur,
            'k_prev': k_prev,
            'spike_index_cur': s_cur + 1,
            'spike_index_prev': (s_prev + 1) if s_prev >= 0 else 0,
            'note': note,
            'L_cur': L_cur,
            'L_prev': L_prev,
            'Delta_obs': Delta_obs,
            'Delta_pred': Delta_pred,
            'M_small': M_small,
            'M_sub': M_sub,
            'sum_small': sum_small,
            'sum_sub': sum_sub,
            'log_b_a_cur_spike': cur['log_b_a'],
        })

        prev = cur

    return blocks, spikes


def main():
    print(f'Khinchin geometric mean log_b(K_0) = {LOG_B_K0:.6f}  (b={B})')
    m1, var = gk_log_b_moments(B, kmax=200_000)
    print(f'Gauss-Kuzmin moments of log_b(a):  mean={m1:.6f}  var={var:.6f}')

    csv_rows = [(
        'n', 'k_prev', 'k_cur',
        'spike_idx_prev', 'spike_idx_cur',
        'L_prev', 'L_cur', 'Delta_obs', 'Delta_pred', 'resid',
        'M_small', 'sum_small', 'mean_small', 'M_pred_kh', 'M_z',
        'M_subcanonical', 'sum_subcanonical',
        'log_b_a_at_cur_spike',
    )]
    summary = []
    spike_rows = [(
        'n', 'spike_idx', 'L_at', 'log_b_a', 'k_best',
        'offset_from_canonical', 'canonical',
    )]

    for n in NS:
        print(f'\n=== n = {n} ===', flush=True)
        rec = compute_one(n)
        print(f'  validated PQs: {rec["n_validated"]}, '
              f'spikes(>10^{LOG10_SPIKE:.0f}): {sum(rec["is_spike"])}',
              flush=True)
        blocks, spikes = analyze(rec)

        # Per-spike rows (whether canonical or not).
        for sp in spikes:
            spike_rows.append((
                n, sp['spike_index_1based'],
                f'{sp["L_at"]:.6f}', f'{sp["log_b_a"]:.6f}',
                sp['k_best'], f'{sp["offset_from_canonical"]:+.6f}',
                int(sp['canonical']),
            ))

        # Per-block (canonical-to-canonical) rows.
        for blk in blocks:
            Delta_obs = blk['Delta_obs']
            Delta_pred = blk['Delta_pred']
            resid = Delta_obs - Delta_pred
            M_small = blk['M_small']
            sum_small = blk['sum_small']
            mean_small = (sum_small / M_small) if M_small > 0 else 0.0
            # Khinchin M prediction from sum_small (truly off-spike PQs
            # only — sub-canonical excluded since they are large outliers
            # the marginal Khinchin doesn't predict at this rate).
            if M_small > 0 and sum_small > 0:
                M_pred_kh = sum_small / m1
                M_var_kh = sum_small * var / m1**3
                M_sd_kh = math.sqrt(M_var_kh) if M_var_kh > 0 else 0.0
                M_z = (M_small - M_pred_kh) / M_sd_kh if M_sd_kh > 0 else float('nan')
            else:
                M_pred_kh = float('nan')
                M_z = float('nan')

            print(f'  block {blk["note"]}: '
                  f'i={blk["spike_index_prev"]}→{blk["spike_index_cur"]}  '
                  f'Δ_obs={Delta_obs:>10.4f}  '
                  f'Δ_pred={Delta_pred:>10.4f}  '
                  f'resid={resid:>+9.4f}  '
                  f'M_small={M_small:>4}  '
                  f'M_sub={blk["M_sub"]:>3}  '
                  f'sum_small={sum_small:>7.3f}  '
                  f'mean_small={mean_small:>6.4f}  '
                  f'M_kh={M_pred_kh:>6.1f}  z={M_z:+.2f}')

            csv_rows.append((
                n, blk['k_prev'], blk['k_cur'],
                blk['spike_index_prev'], blk['spike_index_cur'],
                f'{blk["L_prev"]:.6f}', f'{blk["L_cur"]:.6f}',
                f'{Delta_obs:.6f}', f'{Delta_pred:.6f}', f'{resid:+.6f}',
                M_small, f'{sum_small:.6f}', f'{mean_small:.6f}',
                f'{M_pred_kh:.2f}' if not math.isnan(M_pred_kh) else 'nan',
                f'{M_z:+.4f}' if not math.isnan(M_z) else 'nan',
                blk['M_sub'], f'{blk["sum_sub"]:.6f}',
                f'{blk["log_b_a_cur_spike"]:.6f}',
            ))
            summary.append({
                'n': n, 'k_prev': blk['k_prev'], 'k_cur': blk['k_cur'],
                'spike_idx_prev': blk['spike_index_prev'],
                'spike_idx_cur': blk['spike_index_cur'],
                'Delta_obs': Delta_obs, 'Delta_pred': Delta_pred,
                'resid': resid,
                'M_small': M_small, 'sum_small': sum_small,
                'mean_small': mean_small,
                'M_pred_kh': M_pred_kh, 'M_z': M_z,
                'M_sub': blk['M_sub'], 'sum_sub': blk['sum_sub'],
                'note': blk['note'],
            })

    csv_path = os.path.join(HERE, 'offspike_dynamics.csv')
    with open(csv_path, 'w', newline='') as f:
        csv.writer(f).writerows(csv_rows)
    print(f'\nwrote {csv_path}')

    spike_csv_path = os.path.join(HERE, 'offspike_spikes.csv')
    with open(spike_csv_path, 'w', newline='') as f:
        csv.writer(f).writerows(spike_rows)
    print(f'wrote {spike_csv_path}')

    # Summary text.
    out = [
        '# Off-spike denominator dynamics — canonical-block tests',
        f'# b = {B}, panel n = {NS}',
        f'# log_b(K_0) = {LOG_B_K0:.6f}  '
        f'(geometric-mean log of Khinchin partial quotient)',
        f'# Gauss-Kuzmin: E[log_b a] = {m1:.6f},  Var[log_b a] = {var:.6f}',
        f'# canonical iff |L_obs - (C_{{k-1}} + (n-1)k + offset(n))| < {OFFSET_TOL}',
        '',
        '## Test A: canonical-to-canonical Δ_obs vs substrate prediction',
        '##   Δ_obs := L_canonical_cur - L_canonical_prev',
        '##   Δ_pred := (C_{k_cur-1} + (n-1)k_cur) - (C_{k_prev-1} + (n-1)k_prev)',
        '##           = D_{k_cur-1} + (n-1)  if k_cur = k_prev + 1',
        '',
        f'  {"n":>3}  {"k_prev→k_cur":>13}  {"i_prev→i_cur":>14}  '
        f'{"Δ_obs":>11}  {"Δ_pred":>11}  {"resid":>10}',
    ]
    for row in summary:
        out.append(
            f'  {row["n"]:>3}  {row["k_prev"]:>5} →{row["k_cur"]:>5}      '
            f'{row["spike_idx_prev"]:>5} →{row["spike_idx_cur"]:>5}    '
            f'{row["Delta_obs"]:>11.4f}  {row["Delta_pred"]:>11.4f}  '
            f'{row["resid"]:>+10.4f}'
        )

    out.append('')
    out.append('## Test B: small-PQ block stats (sub-canonical spikes excluded)')
    out.append('##   M_small = #{ off-spike PQs with log10 a ≤ 3 in block interior }')
    out.append('##   sum_small = Σ log_b(a_j) over small PQs')
    out.append('##   mean_small = sum_small / M_small  (compare to E[log_b a]_GK ≈ '
               f'{m1:.4f})')
    out.append('##   M_z = z-score of M_small vs Khinchin renewal prediction')
    out.append('')
    out.append(
        f'  {"n":>3}  {"k_prev→k_cur":>13}  {"M_small":>7}  {"M_sub":>5}  '
        f'{"sum_small":>10}  {"mean_small":>10}  {"M_kh":>7}  {"M_z":>6}'
    )
    for row in summary:
        out.append(
            f'  {row["n"]:>3}  {row["k_prev"]:>5} →{row["k_cur"]:>5}      '
            f'{row["M_small"]:>7}  {row["M_sub"]:>5}  '
            f'{row["sum_small"]:>10.4f}  {row["mean_small"]:>10.4f}  '
            f'{row["M_pred_kh"]:>7.1f}  {row["M_z"]:>+6.2f}'
        )

    # Canonical-block residual stats.
    out.append('')
    out.append('## Test A summary')
    resids = [row['resid'] for row in summary]
    if resids:
        out.append(f'  n_blocks         = {len(resids)}')
        out.append(f'  mean residual    = {sum(resids)/len(resids):+.6f}')
        out.append(f'  max |residual|   = {max(abs(r) for r in resids):.6f}')

    out.append('')
    out.append('## Test B summary (small-PQ Khinchin renewal prediction)')
    zs = [row['M_z'] for row in summary if not math.isnan(row['M_z'])]
    means = [row['mean_small'] for row in summary if row['M_small'] > 0]
    if zs:
        out.append(f'  n_blocks         = {len(zs)}')
        out.append(f'  mean z           = {sum(zs)/len(zs):+.4f}')
        out.append(f'  max |z|          = {max(abs(z) for z in zs):.4f}')
    if means:
        out.append(
            f'  pooled mean_small = {sum(means)/len(means):.6f}  '
            f'(GK predicts {m1:.6f})'
        )

    summary_path = os.path.join(HERE, 'offspike_dynamics_summary.txt')
    with open(summary_path, 'w') as f:
        f.write('\n'.join(out) + '\n')
    print(f'wrote {summary_path}')
    print()
    print('\n'.join(out))


if __name__ == '__main__':
    main()
