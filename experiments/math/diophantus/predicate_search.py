"""
Search for closed-form predicates that characterise the
n²-cancellation locus (clause 3″ trigger set).

A *candidate* is a predicate P(b, n, d) that we conjecture identifies
exactly the n²-cancellation cells (up to GFE / smooth membership).
We score a candidate on:

  - false negatives: alignment fires but P is false
  - false positives: P is true but alignment doesn't fire (or cell
    isn't even spread = 0)

Closed-form characterisation requires zero false positives and zero
false negatives in the searched range.

Candidates tested:

  C1: r = s (the simplest predicate)
  C2: (n+1) | (W − ⌊W/n²⌋)             [equivalent to C1 by algebra]
  C3: r = s AND br > n                   [GFE-disjoint version of C1]
  C4: |r − s| ≤ 1
  C5: r ≡ s (mod gcd(r, n) + 1)         [a more specific structure]
"""

from collections import defaultdict
from math import gcd

B = 10
N_MAX = 400
D_MAX = 8


def per_strip_atoms(b, n, d):
    W = b**(d - 1)
    n2 = n * n
    atoms = []
    for k in range(1, b):
        lo = k * W
        hi = (k + 1) * W - 1
        c_n = hi // n - (lo - 1) // n
        c_nsq = hi // n2 - (lo - 1) // n2
        atoms.append(c_n - c_nsq)
    return atoms


def per_strip_n_count(b, n, d):
    W = b**(d - 1)
    return [((k + 1) * W - 1) // n - (k * W - 1) // n
            for k in range(1, b)]


def is_smooth(b, n, d):
    return (b**(d - 1)) % (n * n) == 0


def is_family_e(b, n, d):
    return d >= 2 and b**(d - 1) <= n <= (b**d - 1) // (b - 1)


def is_gfe_extended(b, n, d):
    """Generalised Family E: per-strip n-multiples count is constant."""
    cn = per_strip_n_count(b, n, d)
    return all(c == cn[0] for c in cn)


def alignment_fires(b, n, d):
    """Spread = 0 outside smooth, classical Family E, and GFE
    (i.e., genuine n²-cancellation)."""
    if is_smooth(b, n, d) or is_family_e(b, n, d):
        return False
    atoms = per_strip_atoms(b, n, d)
    if not all(a == atoms[0] for a in atoms) or atoms[0] == 0:
        return False
    return not is_gfe_extended(b, n, d)


def get_rs(b, n, d):
    W = b**(d - 1)
    return W % n, (W // n) % n


def candidates(b, n, d):
    r, s = get_rs(b, n, d)
    W = b**(d - 1)
    return {
        'C1: r = s':
            r == s,
        'C2: (n+1) | (W − ⌊W/n²⌋)':
            (W - W // (n * n)) % (n + 1) == 0,
        'C3: r = s AND br > n':
            r == s and b * r > n,
        'C4: |r − s| ≤ 1':
            abs(r - s) <= 1,
        'C5: r = s AND non-smooth AND non-FamilyE':
            r == s and not is_smooth(b, n, d) and not is_family_e(b, n, d),
    }


# Sweep
hits_aligned = []
all_cells = []
for d in range(1, D_MAX + 1):
    for n in range(2, N_MAX + 1):
        if is_smooth(B, n, d) or is_family_e(B, n, d):
            continue
        align = alignment_fires(B, n, d)
        cands = candidates(B, n, d)
        all_cells.append((n, d, align, cands))
        if align:
            hits_aligned.append((n, d))

print(f"Sweep range: b={B}, n ∈ [2, {N_MAX}], d ∈ [1, {D_MAX}]")
print(f"Cells outside smooth & classical Family E: {len(all_cells)}")
print(f"n²-cancellation cells (spread=0, non-GFE): {len(hits_aligned)}")
print()

# Score each candidate
print("Predicate scoring:")
print(f"{'predicate':<40}  TP    FN    FP   precision  recall")
print("-" * 80)
candidate_names = list(next(iter([c for _, _, _, c in all_cells])).keys())
for name in candidate_names:
    TP = FN = FP = TN = 0
    for n, d, align, cands in all_cells:
        pred = cands[name]
        if align and pred:
            TP += 1
        elif align and not pred:
            FN += 1
        elif not align and pred:
            FP += 1
        else:
            TN += 1
    precision = TP / (TP + FP) if (TP + FP) > 0 else float('nan')
    recall = TP / (TP + FN) if (TP + FN) > 0 else float('nan')
    print(f"{name:<40}  {TP:>3}  {FN:>4}  {FP:>4}  "
          f"{precision:>9.4f}  {recall:>6.4f}")
print()

# For r = s candidate, list FP cells
print("False positives for C5 (r = s AND non-smooth AND non-FamilyE)")
print("  i.e., cells that satisfy r = s but are NOT n²-cancellation:")
print()
print(f"{'n':>4} {'d':>3}  {'r':>5}  {'s':>5}  {'spread':>6}  {'is_GFE':>7}")
for n, d, align, cands in all_cells:
    if cands['C5: r = s AND non-smooth AND non-FamilyE'] and not align:
        r, s = get_rs(B, n, d)
        atoms = per_strip_atoms(B, n, d)
        spread = max(atoms) - min(atoms) if atoms else 0
        gfe = is_gfe_extended(B, n, d)
        print(f"{n:>4} {d:>3}  {r:>5}  {s:>5}  {spread:>6}  {str(gfe):>7}")
