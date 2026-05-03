"""
Probe: in the n² > W sub-locus, does the count condition
    E_n = ⌊bW/n²⌋
characterise n²-cancellation alignment?

For n² > W, all multiples of n² in B_{b,d} = [W, bW-1] lie at
n², 2n², …, M·n² with M = ⌊(bW-1)/n²⌋. Each lands in strip
k_j = ⌊n²·j/W⌋. Alignment requires:

  (count)      E_n = M
  (positional) {k : extras_n[k] = 1} = {k_j : j = 1..M}

The count condition is a clean integer equation. We test whether
it's:
  - necessary for alignment in the n² > W sub-locus (yes, by
    construction of clause 3″)
  - sufficient (this is what we probe).

Count condition true but positional false ⟹ the count alone
doesn't close the case.
"""

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
    """Count of k ∈ {1, ..., b-1} with extras_n[k] = 1."""
    cn = per_strip_n_count(b, n, d)
    base = min(cn)
    return sum(1 for c in cn if c > base)


def M_n2(b, n, d):
    W = b**(d - 1)
    return (b * W - 1) // (n * n) - (W - 1) // (n * n)


# Sweep
n2_gt_W_aligned = 0
n2_gt_W_count_only = 0  # count condition true but not aligned
n2_gt_W_aligned_count_match = 0  # aligned and count matches
n2_le_W_aligned = 0
total_n2_gt_W = 0
total_n2_le_W = 0
mismatched_in_n2_gt_W = []

for d in range(1, D_MAX + 1):
    for n in range(2, N_MAX + 1):
        if is_smooth(B, n, d) or is_family_e(B, n, d):
            continue
        W = B**(d - 1)
        n2 = n * n
        align = alignment_fires(B, n, d)
        En = E_n(B, n, d)
        M = M_n2(B, n, d)
        count_match = (En == M)
        if n2 > W:
            total_n2_gt_W += 1
            if align:
                n2_gt_W_aligned += 1
                if count_match:
                    n2_gt_W_aligned_count_match += 1
            elif count_match and En > 0:
                # Count matches but cell not aligned (positional fails)
                n2_gt_W_count_only += 1
                mismatched_in_n2_gt_W.append((n, d, En, M))
        else:
            total_n2_le_W += 1
            if align:
                n2_le_W_aligned += 1

print(f"Sweep: b={B}, n ≤ {N_MAX}, d ≤ {D_MAX}")
print()
print(f"Cells with n² > W: {total_n2_gt_W}")
print(f"  alignment fires: {n2_gt_W_aligned}")
print(f"  alignment fires AND count condition holds: "
      f"{n2_gt_W_aligned_count_match}")
print(f"  count condition holds AND E_n>0 BUT alignment fails: "
      f"{n2_gt_W_count_only}")
print()
print(f"Cells with n² ≤ W: {total_n2_le_W}")
print(f"  alignment fires: {n2_le_W_aligned}")
print()

if mismatched_in_n2_gt_W:
    print("Cells in n² > W where count condition holds but alignment "
          "fails (showing first 20):")
    print(f"{'n':>4} {'d':>3}  {'E_n':>4}  {'M_n²':>5}")
    for n, d, En, M in mismatched_in_n2_gt_W[:20]:
        print(f"{n:>4} {d:>3}  {En:>4}  {M:>5}")
    print(f"... total {len(mismatched_in_n2_gt_W)} such cells")

# What if we restrict to count condition being a NECESSARY filter?
# Then in the n² > W sub-locus, alignment ⊂ count_match.
print()
print("Necessary-condition check: do all aligned n² > W cells "
      "satisfy E_n = M_n²?")
print(f"  aligned n² > W cells: {n2_gt_W_aligned}")
print(f"  of which satisfy count condition: "
      f"{n2_gt_W_aligned_count_match}")
print(f"  count condition is " +
      ("necessary in the swept range" if n2_gt_W_aligned == n2_gt_W_aligned_count_match
       else "NOT necessary (some aligned cell has E_n ≠ M_n²)"))
