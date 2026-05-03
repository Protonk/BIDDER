"""
Structural theorem (n² > W sub-locus) — verification.

Theorem (proved). For (b, n, d) with n² > W = b^(d-1), outside
smooth (n² | W) and classical Family E, the cell has spread = 0
iff one of three cases holds:

  (i)   S₁ = S₂                                  (extras align)
  (ii)  S₁ = ∅           AND  S₂ = {1, …, b−1}    (cn const low,
                                                    cnsq const high)
  (iii) S₁ = {1, …, b−1} AND  S₂ = ∅              (cn const high,
                                                    cnsq const zero)

where

  S₁ := { ⌈(jn + 1)/r⌉ − 1  : j = 1, …, E_n }
        = strips with extras_n[k] = 1       (n-extras Beatty)
  S₂ := { ⌊jn²/W⌋           : j = 1, …, M_{n²} }
        = strips containing a multiple of n² (n²-Beatty; |S₂| = M
          since for n² > W, multiples are spaced > strip-width
          apart and lie in distinct strips)

with r = W mod n, E_n = #{k ∈ {1..b−1} : extras_n[k] = 1}, and
M_{n²} = ⌊(bW − 1)/n²⌋ (the block ends at bW − 1).

Equivalently: spread = 0  ⟺  (extras_n[k] − extras_n²[k]) is
constant in k, where extras_n²[k] = [k ∈ S₂] for n² > W. The
constant ∈ {−1, 0, +1}; the three cases above are c = +1, c = −1,
c = +1 respectively. (Case iii is the symmetric counterpart of
case ii; rare in practice but theoretically present.)

Clause 3″ proper (n²-cancellation outside GFE) is case (i) with
both S₁ and S₂ non-empty. Cases (ii) and (iii) are GFE-extended
cells under the spread-zero umbrella; clause 3″'s scope is case (i).

Proof sketch.
  (a) For n² > W, multiples of n² in B_{b,d} are at j·n² for
      j = 1..M_{n²}, with consecutive multiples spaced ≥ n² > W
      apart. So each multiple lies in a distinct strip; in fact
      strip(j·n²) = ⌊j·n²/W⌋. Hence extras_n²[k] = [k ∈ S₂] and
      |S₂| = M_{n²}.
  (b) extras_n[k] = ⌊((k+1)r − 1)/n⌋ − ⌊(kr − 1)/n⌋ ∈ {0, 1}.
      The j-th k with extras_n[k] = 1 satisfies (k+1)r ≥ jn + 1
      and is the smallest such k, giving k_j = ⌈(jn + 1)/r⌉ − 1.
      Hence S₁ = {k_j : j = 1..E_n} and |S₁| = E_n.
  (c) Clause 3″ alignment = (∀ k: extras_n[k] = extras_n²[k]) =
      (S₁ = S₂ as subsets of {1, …, b − 1}). ∎

Set-coincidence reformulation.
  S₁ is a Beatty sequence with slope β := n/r and offset 1/r.
  S₂ is a Beatty sequence with slope α := n²/W and offset 0.
  Note α < β when r·n < W (i.e., s ≥ r, the "non-GFE" side); and
  β − α = n(rn − W)/(rW), with β − α = n/W exactly when r = s.

This script:
  - enumerates n² > W cells in the b = 10 sweep,
  - directly computes S₁ and S₂ via the closed-form expressions,
  - verifies S₁ = S₂ iff alignment fires (the structural theorem
    on this sub-locus, no other math required).
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


def alignment_fires(b, n, d):
    if is_smooth(b, n, d) or is_family_e(b, n, d):
        return False
    atoms = per_strip_atoms(b, n, d)
    if not atoms or atoms[0] == 0:
        return False
    if not all(a == atoms[0] for a in atoms):
        return False
    return not is_gfe_extended(b, n, d)


def E_n(b, n, d):
    cn = per_strip_n_count(b, n, d)
    base = min(cn)
    return sum(1 for c in cn if c > base)


def S1_closed_form(b, n, d):
    """S₁ = {⌈(jn+1)/r⌉ - 1 : j = 1..E_n}."""
    W = b**(d - 1)
    r = W % n
    if r == 0:
        return set()
    En = E_n(b, n, d)
    return {((j * n + 1) + r - 1) // r - 1 for j in range(1, En + 1)}


def S2_closed_form(b, n, d):
    """S₂ = {⌊j·n²/W⌋ : j = 1..M_{n²}} for n² > W."""
    W = b**(d - 1)
    n2 = n * n
    M = (b * W - 1) // n2
    return {(j * n2) // W for j in range(1, M + 1)}


def S1_direct(b, n, d):
    """Direct construction: strips k where extras_n[k] = 1."""
    cn = per_strip_n_count(b, n, d)
    base = min(cn)
    return {k + 1 for k, c in enumerate(cn) if c > base}


def S2_direct(b, n, d):
    """Direct construction: strips k that contain a multiple of n²."""
    W = b**(d - 1)
    n2 = n * n
    out = set()
    for k in range(1, b):
        lo = k * W
        hi = (k + 1) * W - 1
        if (hi // n2) - ((lo - 1) // n2) > 0:
            out.add(k)
    return out


# Sweep n² > W sub-locus.
# Theorem under test: spread = 0 ⟺ S₁ = S₂ on all cells outside
# smooth and classical Family E in the n² > W sub-locus.

def spread_zero(b, n, d):
    atoms = per_strip_atoms(b, n, d)
    if not atoms:
        return False
    return max(atoms) - min(atoms) == 0

def structural_predicate(s1, s2, b):
    """Three-case structural predicate from the theorem statement.
    Returns True iff (s1 = s2) OR (s1 = ∅, s2 = {1..b-1}) OR
    (s1 = {1..b-1}, s2 = ∅)."""
    full = set(range(1, b))
    if s1 == s2:
        return True
    if s1 == set() and s2 == full:
        return True
    if s1 == full and s2 == set():
        return True
    return False


total = 0
spread_zero_count = 0
predicate_count = 0
both_match_count = 0
case_breakdown = {'(i)': 0, '(ii)': 0, '(iii)': 0}
violations = []
discrepancies = []

print("Verifying structural theorem on n² > W sub-locus")
print("=" * 72)
print()
print("Theorem (proposed):  in n² > W sub-locus, outside smooth")
print("and classical Family E:  spread = 0  ⟺  one of")
print("  (i) S₁ = S₂,  (ii) S₁=∅, S₂={1..b-1},  "
      "(iii) S₁={1..b-1}, S₂=∅")
print()

full_set = set(range(1, B))

for d in range(1, D_MAX + 1):
    for n in range(2, N_MAX + 1):
        if is_smooth(B, n, d) or is_family_e(B, n, d):
            continue
        W = B**(d - 1)
        if n * n <= W:
            continue
        total += 1
        sz = spread_zero(B, n, d)
        s1_cf = S1_closed_form(B, n, d)
        s2_cf = S2_closed_form(B, n, d)
        s1_dr = S1_direct(B, n, d)
        s2_dr = S2_direct(B, n, d)

        if s1_cf != s1_dr:
            discrepancies.append(('S1', n, d, s1_cf, s1_dr))
        if s2_cf != s2_dr:
            discrepancies.append(('S2', n, d, s2_cf, s2_dr))

        pred = structural_predicate(s1_cf, s2_cf, B)
        if sz:
            spread_zero_count += 1
            if pred:
                both_match_count += 1
                if s1_cf == s2_cf:
                    case_breakdown['(i)'] += 1
                elif s1_cf == set() and s2_cf == full_set:
                    case_breakdown['(ii)'] += 1
                elif s1_cf == full_set and s2_cf == set():
                    case_breakdown['(iii)'] += 1
        if pred:
            predicate_count += 1

        if sz != pred:
            violations.append((n, d, sz, pred, s1_cf, s2_cf))

print(f"Cells in n² > W sub-locus, outside smooth & classical Family E:")
print(f"  total:                                  {total}")
print(f"  spread = 0:                             {spread_zero_count}")
print(f"  structural predicate (i ∨ ii ∨ iii):    {predicate_count}")
print(f"  spread = 0  AND  predicate:             {both_match_count}")
print(f"  theorem violations:                     {len(violations)}")
print()
print(f"Spread = 0 case breakdown:")
print(f"  (i)   S₁ = S₂:                          "
      f"{case_breakdown['(i)']}")
print(f"  (ii)  S₁ = ∅, S₂ = {{1..b-1}}:            "
      f"{case_breakdown['(ii)']}")
print(f"  (iii) S₁ = {{1..b-1}}, S₂ = ∅:            "
      f"{case_breakdown['(iii)']}")
print()
if discrepancies:
    print(f"Closed-form / direct discrepancies: {len(discrepancies)}")
    for kind, n, d, cf, dr in discrepancies[:10]:
        print(f"  {kind}: n={n}, d={d}, closed={cf}, direct={dr}")
else:
    print("Closed-form S₁, S₂ expressions verified — 0 discrepancies "
          "vs direct computation.")
print()

if violations:
    print(f"VIOLATIONS ({len(violations)} cells):")
    print(f"{'n':>4} {'d':>3}  {'sz?':>5}  {'pred?':>6}  S₁ // S₂")
    for n, d, sz, pred, s1, s2 in violations[:20]:
        print(f"{n:>4} {d:>3}  {str(sz):>5}  {str(pred):>6}  "
              f"{sorted(s1)} // {sorted(s2)}")
    if len(violations) > 20:
        print(f"... {len(violations) - 20} more")
else:
    print("=" * 72)
    print(f"THEOREM VERIFIED on all {total} cells of the n² > W")
    print(f"sub-locus (outside smooth & classical Family E):")
    print(f"  spread = 0  ⟺  S₁ = S₂ ∨ (S₁,S₂) ∈ {{(∅, full), (full, ∅)}}")
