"""
Investigation A: boundary conditions on the Beatty inequality.

For r = s sub-sub-case in the n² > W sub-locus, alignment iff:

    (jn) mod r  ≥  ⌈jr/(n+1)⌉      for all j = 1, …, M.

Each fixed `j` gives a single inequality on (n, r) — call it C_j.
Failing any C_j kills alignment, so the conjunction
C_1 ∧ C_2 ∧ … ∧ C_M is necessary and sufficient. The "ladder of
necessary conditions" is C_1, C_1 ∧ C_2, … : a sieve that gets
strictly tighter with each j.

This script:
  - extracts each C_j in simplified form (case-split where needed),
  - tests it on the r = s cells in the swept range,
  - reports the smallest j at which each non-aligning cell first
    fails (the "break point" — a preview of Investigation C),
  - identifies clean closed-form structures.
"""

from math import gcd

B = 10
N_MAX = 2000
D_MAX = 10


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


def C_j(j, n, r):
    """Predicate for the j-th boundary condition.

    Returns (lhs, rhs, holds): the values of (jn) mod r,
    ⌈jr/(n+1)⌉, and whether the condition holds."""
    lhs = (j * n) % r
    rhs = -(-(j * r) // (n + 1))
    return lhs, rhs, lhs >= rhs


def first_break(n, r, n_plus_1, M):
    """First j ∈ {1, …, M} at which C_j fails. Returns None if all
    pass."""
    for j in range(1, M + 1):
        if (j * n) % r < -(-(j * r) // n_plus_1):
            return j
    return None


def collect_rs_cells():
    cells = []
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
            M = (B * W) // (n * n)
            cells.append((n, d, r, M, W))
    return cells


cells = collect_rs_cells()
print(f"r = s cells in n² > W sub-locus: {len(cells)}")
print()

# The j=1 condition is the cleanest. Closed form: r ∤ n.
print("=" * 72)
print("Theorem A1 (j = 1 boundary). Necessary condition: r ∤ n.")
print("=" * 72)
print()
print("Proof. j = 1 condition is n mod r ≥ ⌈r/(n+1)⌉. Since")
print("0 ≤ r ≤ n, we have r/(n+1) < 1, so ⌈r/(n+1)⌉ = 1 (for r ≥ 1).")
print("Thus n mod r ≥ 1, equivalently r ∤ n. ∎")
print()

# Verify on cells
print("Verification on r = s cells:")
print(f"{'n':>4} {'d':>3} {'r':>5}  {'r∤n?':>5}  {'sz?':>5}  "
      f"{'consistent?':>11}")
for n, d, r, M, W in cells:
    cond = (n % r) != 0
    sz = spread_zero(B, n, d)
    gfe = is_gfe_extended(B, n, d)
    case_i = sz and not gfe
    consistent = case_i <= cond  # case_i ⟹ cond (necessary)
    print(f"{n:>4} {d:>3} {r:>5}  {str(cond):>5}  {str(case_i):>5}  "
          f"{'yes' if consistent else 'NO'}")

print()

# j = 2 condition.
print("=" * 72)
print("Theorem A2 (j = 2 boundary). Necessary case-split:")
print("=" * 72)
print()
print("  j=2 condition: 2n mod r ≥ ⌈2r/(n+1)⌉.")
print()
print("  Case A (2r ≤ n+1): ⌈⌉ = 1, condition is r ∤ 2n.")
print("  Case B (2r > n+1):  ⌈⌉ = 2, condition is 2n mod r ≥ 2.")
print()
print("  Combined with j=1 (r ∤ n):")
print("    If r odd: r ∤ 2n ⟺ r ∤ n, so j=2 in Case A is redundant.")
print("    If r = 2: r | 2n always, so r=2 fails j=2. Excluded.")
print("    If r even, r ≥ 4: r ∤ 2n is strictly stronger than r ∤ n.")
print()

print("Verification on r = s cells:")
print(f"{'n':>4} {'d':>3} {'r':>5}  {'case':>4}  {'C_2':>5}  "
      f"{'sz?':>5}  {'consistent?':>11}")
for n, d, r, M, W in cells:
    case = "A" if 2 * r <= n + 1 else "B"
    if case == "A":
        c2 = (2 * n) % r != 0
    else:
        c2 = (2 * n) % r >= 2
    sz = spread_zero(B, n, d)
    gfe = is_gfe_extended(B, n, d)
    case_i = sz and not gfe
    consistent = case_i <= c2
    print(f"{n:>4} {d:>3} {r:>5}  {case:>4}  {str(c2):>5}  "
          f"{str(sz):>5}  {'yes' if consistent else 'NO'}")
print()

# j = 3 condition.
print("=" * 72)
print("Theorem A3 (j = 3 boundary). Three-case-split:")
print("=" * 72)
print()
print("  j=3 condition: 3n mod r ≥ ⌈3r/(n+1)⌉.")
print()
print("  Case A (3r ≤ n+1):     ⌈⌉ = 1, condition r ∤ 3n.")
print("  Case B (n+1 < 3r ≤ 2(n+1)):  ⌈⌉ = 2, condition 3n mod r ≥ 2.")
print("  Case C (3r > 2(n+1)):  ⌈⌉ = 3, condition 3n mod r ≥ 3.")
print()

print("Verification on r = s cells:")
print(f"{'n':>4} {'d':>3} {'r':>5}  {'case':>4}  {'C_3':>5}  "
      f"{'sz?':>5}  {'consistent?':>11}")
for n, d, r, M, W in cells:
    n_plus_1 = n + 1
    if 3 * r <= n_plus_1:
        case = "A"
        c3 = (3 * n) % r != 0
    elif 3 * r <= 2 * n_plus_1:
        case = "B"
        c3 = (3 * n) % r >= 2
    else:
        case = "C"
        c3 = (3 * n) % r >= 3
    sz = spread_zero(B, n, d)
    gfe = is_gfe_extended(B, n, d)
    case_i = sz and not gfe
    consistent = case_i <= c3
    print(f"{n:>4} {d:>3} {r:>5}  {case:>4}  {str(c3):>5}  "
          f"{str(sz):>5}  {'yes' if consistent else 'NO'}")
print()

# Cumulative: how many cells fail j=1, j=2, j=3 conditions?
print("=" * 72)
print("Cumulative sieve: which non-aligning cells are caught by C_j")
print("=" * 72)
print()
print(f"{'n':>4} {'d':>3} {'r':>5} {'M':>3}  {'sz?':>5}  case_i  "
      f"{'first fail j*':>12}")
for n, d, r, M, W in cells:
    fb = first_break(n, r, n + 1, M)
    sz = spread_zero(B, n, d)
    gfe = is_gfe_extended(B, n, d)
    case_i = sz and not gfe
    print(f"{n:>4} {d:>3} {r:>5} {M:>3}  {str(sz):>5}  {str(case_i):>6}  "
          f"{str(fb):>12}")
print()

# Sieve analysis on M >= 1 cells (the only ones where the Beatty
# inequality has any j to check).
m_pos_cells = [c for c in cells if c[3] >= 1]
m_pos_non_align = [
    (n, d, r, M, W) for (n, d, r, M, W) in m_pos_cells
    if first_break(n, r, n + 1, M) is not None
]
m_pos_caught_j1 = [
    (n, d, r, M, W, fb) for (n, d, r, M, W) in m_pos_cells
    if (fb := first_break(n, r, n + 1, M)) is not None and fb == 1
]
m_pos_caught_j_higher = [
    (n, d, r, M, W, fb) for (n, d, r, M, W) in m_pos_cells
    if (fb := first_break(n, r, n + 1, M)) is not None and fb > 1
]

print(f"r = s, n² > W cells with M ≥ 1: {len(m_pos_cells)}")
print(f"  fail at j = 1   (r | n):            "
      f"{len(m_pos_caught_j1)}")
print(f"  fail first at j > 1:                "
      f"{len(m_pos_caught_j_higher)}")
print(f"  pass all j = 1..M (case (i) holds): "
      f"{len(m_pos_cells) - len(m_pos_non_align)}")
print()

if m_pos_caught_j_higher:
    print("Cells where j = 1 passes but a later C_j fails — these")
    print("are the cells where the j-ladder genuinely sharpens past")
    print("the j = 1 sieve.")
    print()
    print(f"{'n':>5} {'d':>3} {'r':>5} {'M':>4}  {'first j*':>9}")
    for n, d, r, M, W, fb in m_pos_caught_j_higher[:30]:
        print(f"{n:>5} {d:>3} {r:>5} {M:>4}  {fb:>9}")
    if len(m_pos_caught_j_higher) > 30:
        print(f"... {len(m_pos_caught_j_higher) - 30} more")
else:
    print("No cells fail at j > 1 in this sweep. The j = 1 sieve")
    print("(r ∤ n) appears to be the only operative boundary "
          "condition for r = s.")
