"""
Lucky locus characterisation.

For each (n, d) lucky cell at b = 10 (spread = 0, neither smooth-
sieved nor Family E), determine:

  - q: constant n-prime atom count per leading digit.
  - m_min, m_max: smallest and largest multipliers k for which kn
    lies in the block B_{b,d} = [b^(d-1), b^d - 1].
  - mechanism: 'shifted_family_e' (per-strip *multiples* of n is
    constant; no n²-correction needed) or 'n2_cancellation'
    (per-strip multiples vary, but n²-corrections balance them).

Then test the proposed *Generalised Family E* theorem:

  For W = b^(d-1) and integers (m_min, q) with
  m_max := m_min + q(b-1) - 1, the multiples of n in B_{b,d} are
  exactly q per leading digit iff
    1. m_min · n ≥ W.
    2. m_max · n ≤ bW - 1.
    3. (m_max + 1) · n > bW - 1.
    4. For each k ∈ [m_min, m_max], leading digit of kn equals
       ((k - m_min) // q) + 1, which reduces to
       (⌈k/q⌉ - ⌈m_min/q⌉ + 1).

If additionally n² > bW - 1 (no n² inside the block), the atoms
are exactly the multiples — and the lucky cell is "shifted Family
E." When the conditions above are met but n² inside the block
balances against extra multiples, the cell is "n²-cancellation."
"""

from collections import defaultdict

B = 10
N_MAX = 200
D_MAX = 7


def per_strip_counts(b, n, d):
    W = b**(d - 1)
    n_sq = n * n
    counts_n = []
    counts_atoms = []
    for k in range(1, b):
        lo = k * W
        hi = (k + 1) * W - 1
        c_n = hi // n - (lo - 1) // n
        c_nsq = hi // n_sq - (lo - 1) // n_sq
        counts_n.append(c_n)
        counts_atoms.append(c_n - c_nsq)
    return counts_n, counts_atoms


def is_smooth(b, n, d):
    return (b**(d - 1)) % (n * n) == 0


def is_family_e(b, n, d):
    return d >= 2 and b**(d - 1) <= n <= (b**d - 1) // (b - 1)


def classify_lucky(b, n, d):
    counts_n, counts_atoms = per_strip_counts(b, n, d)
    if not all(c == counts_atoms[0] for c in counts_atoms):
        return None
    q = counts_atoms[0]
    if q == 0:
        return None
    W = b**(d - 1)
    m_min = (W + n - 1) // n
    m_max = (b * W - 1) // n
    is_n_uniform = all(c == counts_n[0] for c in counts_n)
    mechanism = 'shifted_family_e' if is_n_uniform else 'n2_cancellation'
    return {
        'mechanism': mechanism,
        'q': q,
        'm_min': m_min,
        'm_max': m_max,
        'q_predicted': (m_max - m_min + 1) // (b - 1),
        'remainder': (m_max - m_min + 1) % (b - 1),
        'counts_n': counts_n,
        'counts_atoms': counts_atoms,
    }


# Sweep.
shifted = []      # (n, d, info)
n2_cancel = []    # (n, d, info)
for d in range(1, D_MAX + 1):
    for n in range(2, N_MAX + 1):
        if is_smooth(B, n, d) or is_family_e(B, n, d):
            continue
        info = classify_lucky(B, n, d)
        if info is None:
            continue
        if info['mechanism'] == 'shifted_family_e':
            shifted.append((n, d, info))
        else:
            n2_cancel.append((n, d, info))

print(f"Shifted Family E lucky cells: {len(shifted)}")
print(f"n² cancellation lucky cells:  {len(n2_cancel)}")
print()

# Group shifted by (d, q', m_min) where q' is the per-strip
# *multiple-of-n* count (NOT the atom count). q' = counts_n[0]
# in the shifted_family_e regime.
shifted_groups = defaultdict(list)
for n, d, info in shifted:
    q_prime = info['counts_n'][0]
    key = (d, q_prime, info['m_min'])
    shifted_groups[key].append((n, info['q']))

print("Shifted Family E ranges, grouped by (d, qp, m_min) "
      "(qp = multiples per strip, q = atoms per strip):")
print(f"{'d':>3} {'qp':>4} {'m_min':>6} {'m_max':>6} "
      f"{'predicted':>15} {'observed':>15} {'q':>5} "
      f"{'delta':>5} {'count':>6}")
for (d, q_prime, m_min) in sorted(shifted_groups.keys()):
    cells = shifted_groups[(d, q_prime, m_min)]
    ns = [c[0] for c in cells]
    qs = [c[1] for c in cells]
    W = B**(d - 1)
    m_max = m_min + q_prime * (B - 1) - 1

    lower = (B * W - 1) // (m_max + 1) + 1
    upper = (B * W - 1) // m_max
    pred_range = f"[{lower},{upper}]"
    obs_range = f"[{min(ns)},{max(ns)}]"
    # δ = q' - q (multiples of n² per strip).
    deltas = sorted(set(q_prime - q for q in qs))
    delta_s = ','.join(str(d_) for d_ in deltas)
    q_s = ','.join(str(q) for q in sorted(set(qs)))
    print(f"{d:>3} {q_prime:>4} {m_min:>6} {m_max:>6} "
          f"{pred_range:>15} {obs_range:>15} {q_s:>5} "
          f"{delta_s:>5} {len(ns):>6}")

# Verification with q' (multiplier count).
print()
print("Verification: predicted vs observed n per (d, q', m_min) group")
print(f"{'group':<37} {'count':>6}  comments")
all_ok = True
for (d, q_prime, m_min) in sorted(shifted_groups.keys()):
    cells = shifted_groups[(d, q_prime, m_min)]
    ns = set(c[0] for c in cells)
    W = B**(d - 1)
    m_max = m_min + q_prime * (B - 1) - 1
    lower = (B * W - 1) // (m_max + 1) + 1
    upper = (B * W - 1) // m_max
    predicted_n = set(range(lower, upper + 1))
    # Restrict to our sweep range [2, N_MAX].
    predicted_n_in_sweep = predicted_n & set(range(2, N_MAX + 1))
    missing = predicted_n_in_sweep - ns
    extra = ns - predicted_n
    label = f"d={d}, qp={q_prime}, m_min={m_min}"
    if missing or extra:
        all_ok = False
        msgs = []
        if missing:
            msgs.append(f"missing {sorted(missing)}")
        if extra:
            msgs.append(f"extra {sorted(extra)}")
        print(f"{label:<37} {len(ns):>6}  {' / '.join(msgs)}")
    else:
        print(f"{label:<37} {len(ns):>6}  predicted = observed")

print()
print(f"All groups match prediction (qp-form): {all_ok}")

# n² cancellation: list the cells.
print()
print("n² cancellation cells (lucky via n² balance):")
print(f"{'n':>4} {'d':>3} {'q':>3} {'counts_n':>30} {'counts_atoms':>30}")
for n, d, info in sorted(n2_cancel, key=lambda x: (x[1], x[0])):
    cn = ' '.join(str(c) for c in info['counts_n'])
    ca = ' '.join(str(c) for c in info['counts_atoms'])
    print(f"{n:>4} {d:>3} {info['q']:>3}   [{cn}]   →   [{ca}]")


# Structural test for the n²-cancellation locus.
#
# Claim: every n²-cancellation cell satisfies a single Beatty
# pattern-alignment condition —
#
#   (i)   counts_n[k] ∈ {⌊W/n⌋, ⌊W/n⌋ + 1}    (spread-1 / Beatty-shape)
#   (ii)  counts_nsq[k] ∈ {c, c+1}              (spread ≤ 1)
#   (iii) the per-strip "extras" of counts_n match the per-strip
#         "extras" of counts_nsq bit-for-bit:
#           cn[k] - min(cn) == cnsq[k] - min(cnsq) for all k.
#
# Condition (iii) is strictly stronger than the definitional
# requirement that counts_atoms is uniform. Pattern-equality of the
# extras (not just equal differences) is a real arithmetic alignment.
def counts_nsq_per_strip(b, n, d):
    W = b**(d - 1)
    n_sq = n * n
    out = []
    for k in range(1, b):
        lo = k * W
        hi = (k + 1) * W - 1
        out.append(hi // n_sq - (lo - 1) // n_sq)
    return out


print()
print("n²-cancellation structural verification (Beatty pattern-alignment):")
print(f"{'n':>4} {'d':>3}  {'cn_extras':<10} {'cnsq_extras':<11}  {'spread(cn)':>10} "
      f"{'spread(cnsq)':>13}  match?")
aligned = 0
for n, d, info in sorted(n2_cancel, key=lambda x: (x[1], x[0])):
    cn = info['counts_n']
    cnsq = counts_nsq_per_strip(B, n, d)
    cn_min, cnsq_min = min(cn), min(cnsq)
    cn_extras = tuple(c - cn_min for c in cn)
    cnsq_extras = tuple(c - cnsq_min for c in cnsq)
    sp_cn = max(cn) - min(cn)
    sp_cnsq = max(cnsq) - min(cnsq)
    is_aligned = (
        cn_extras == cnsq_extras
        and sp_cn == 1
        and sp_cnsq <= 1
    )
    if is_aligned:
        aligned += 1
    pat_cn = ''.join(str(x) for x in cn_extras)
    pat_cnsq = ''.join(str(x) for x in cnsq_extras)
    print(f"{n:>4} {d:>3}  {pat_cn:<10} {pat_cnsq:<11}  {sp_cn:>10} "
          f"{sp_cnsq:>13}  {'YES' if is_aligned else 'NO'}")

print()
print(f"Cells satisfying Beatty pattern-alignment: {aligned}/{len(n2_cancel)}")
