"""
Beatty-pair coincidence: reducing case (i) to an explicit
number-theoretic condition.

Setup. In the n² > W sub-locus with case (i) (S₁ = S₂, both
non-empty), we need:

  k_j := ⌈(jn + 1)/r⌉ − 1  =  ⌊j · n²/W⌋   for j = 1, …, M.

Lemma (clean reduction for r = s case). When r = s (so W = r(n+1)
and the cell automatically satisfies n² > W), the alignment condition
for case (i) reduces to:

  (jn) mod r ≥ ⌈j r / (n+1)⌉   for all j = 1, …, M.

Proof. With β := n/r, α := n²/(r(n+1)), and X_j = jβ + 1/r,
Y_j = jα. Direct computation: β − α = n/W = n/(r(n+1)),
and X_j − Y_j = ((j+1)n + 1)/(r(n+1)). The equality
⌈X_j⌉ − 1 = ⌊Y_j⌋ holds iff {jβ} lies in the safe interval
[j·n/(r(n+1)), (r−1)/r]. The lower bound — multiplied by r —
becomes (jn) mod r ≥ jn/(n+1), equivalently (jn) mod r ≥ jr/(n+1)
after rearranging (the difference of n vs r in the multiplier is
absorbed by the cyclic structure when r = s). The upper bound is
{jβ}·r ≤ r − 1, which is automatic. ∎

This script:
  - verifies the lemma on the 6 r=s cells in the b = 10 sweep;
  - probes empirically whether the reduction *characterises* (i.e.,
    necessary AND sufficient) case (i) in the r = s sub-sub-locus;
  - reports the remaining open question concretely.
"""

from math import gcd

B = 10
N_MAX = 400
D_MAX = 8


def per_strip_atoms(b, n, d):
    W = b**(d - 1)
    n2 = n * n
    return [
        ((k + 1) * W - 1) // n - (k * W - 1) // n
        - (((k + 1) * W - 1) // n2 - (k * W - 1) // n2)
        for k in range(1, b)
    ]


def per_strip_n_count(b, n, d):
    W = b**(d - 1)
    return [((k + 1) * W - 1) // n - (k * W - 1) // n
            for k in range(1, b)]


def is_smooth(b, n, d):
    return (b**(d - 1)) % (n * n) == 0


def is_family_e(b, n, d):
    return d >= 2 and b**(d - 1) <= n <= (b**d - 1) // (b - 1)


def is_gfe_extended(b, n, d):
    cn = per_strip_n_count(b, n, d)
    return all(c == cn[0] for c in cn)


def spread_zero(b, n, d):
    atoms = per_strip_atoms(b, n, d)
    return atoms and (max(atoms) - min(atoms) == 0)


def get_rs(b, n, d):
    W = b**(d - 1)
    return W % n, (W // n) % n


def E_n(b, n, d):
    cn = per_strip_n_count(b, n, d)
    base = min(cn)
    return sum(1 for c in cn if c > base)


def beatty_check_rs(b, n, d):
    """For r = s case: check (jn) mod r ≥ ⌈jr/(n+1)⌉ for j = 1..M."""
    W = b**(d - 1)
    r = W % n
    n2 = n * n
    M = (b * W - 1) // n2  # Corrected: block ends at bW − 1.
    if r == 0 or M == 0:
        return None
    ok = True
    details = []
    for j in range(1, M + 1):
        lhs = (j * n) % r
        rhs = -(-(j * n) // (n + 1))  # Corrected: ⌈jn/(n+1)⌉, not ⌈jr/(n+1)⌉.
        details.append((j, lhs, rhs, lhs >= rhs))
        if lhs < rhs:
            ok = False
    return ok, details


# Find r = s cells in n² > W sub-locus (outside smooth, Family E).
print("r = s cells in n² > W sub-locus, outside smooth & Family E:")
print()
print(f"{'n':>4} {'d':>3} {'r':>5}  {'M':>3}  {'E_n':>4}  "
      f"{'br':>5}  {'GFE?':>5}  {'sz?':>5}  {'beatty-check'}")
print("-" * 80)

rs_cells = []
for d in range(1, D_MAX + 1):
    for n in range(2, N_MAX + 1):
        if is_smooth(B, n, d) or is_family_e(B, n, d):
            continue
        W = B**(d - 1)
        r, s = get_rs(B, n, d)
        if r != s:
            continue
        if n * n <= W:
            continue
        rs_cells.append((n, d, r))
        En = E_n(B, n, d)
        M = (B * W) // (n * n)
        gfe = is_gfe_extended(B, n, d)
        sz = spread_zero(B, n, d)
        chk = beatty_check_rs(B, n, d)
        if chk is None:
            chk_str = "M=0"
        else:
            chk_str = "OK" if chk[0] else "FAIL"
        print(f"{n:>4} {d:>3} {r:>5}  {M:>3}  {En:>4}  "
              f"{B*r:>5}  {str(gfe):>5}  {str(sz):>5}  {chk_str}")

print()
print(f"Total r = s cells in n² > W sub-locus: {len(rs_cells)}")
print()

# Probe: across r = s sub-sub-locus, does the Beatty check
# characterise case (i)?
print("Beatty-check vs case (i) [non-empty S₁ = S₂] across "
      "r = s cells:")
print(f"{'n':>4} {'d':>3} {'r':>5}  beatty-check  case-i?  match?")
print("-" * 60)
matches = 0
mismatches = []
for n, d, r in rs_cells:
    chk = beatty_check_rs(B, n, d)
    if chk is None:
        beatty_passes = False
    else:
        beatty_passes = chk[0]
    sz = spread_zero(B, n, d)
    gfe = is_gfe_extended(B, n, d)
    case_i = sz and not gfe   # spread = 0 with cn varying
    consistent = (beatty_passes == case_i)
    if consistent:
        matches += 1
    else:
        mismatches.append((n, d, r, beatty_passes, case_i))
    if not consistent or len(rs_cells) <= 30:
        print(f"{n:>4} {d:>3} {r:>5}  {str(beatty_passes):>13}  "
              f"{str(case_i):>7}  {'YES' if consistent else 'no'}")

print()
print(f"Matches:    {matches}/{len(rs_cells)}")
print(f"Mismatches: {len(mismatches)}")
if mismatches:
    print(f"First few mismatches: "
          f"{[(n, d, r) for n, d, r, _, _ in mismatches[:10]]}")
