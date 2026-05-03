"""
Trajectory and alignment-region analysis for the n²-cancellation
locus.

For each (b, n, d) cell where the substrate phase diagram shows
spread = 0 outside clauses 2 and 3 (96 cells in the b=10 sweep), we
have:

  W = b^(d-1)
  r = W mod n              (so n divides W - r, r ∈ {1, ..., n-1})
  r' = W mod n²            (with r' ≡ r mod n; write r' = r + s·n)

The per-strip multiples count is

  c_n[k]  = floor(W/n)  + extras_n[k]
  c_n²[k] = floor(W/n²) + extras_n²[k]

where extras_n[k] ∈ {0, 1} (Beatty-shape, because spread of c_n is ≤
1 universally), and similarly for n². The atom count is
c_n[k] - c_n²[k]; uniform iff extras_n[k] = extras_n²[k] for all k
(THIS is the alignment hypothesis of clause 3″).

  x_k  := (kr) mod n         ∈ {0, ..., n-1}
  Q'_k := floor((kr' mod n²)/n)  ∈ {0, ..., n-1}

Then (kr' mod n²) = Q'_k · n + x_k, and the dynamics are:

  x_{k+1}  = (x_k + r) mod n
  Q'_{k+1} = (Q'_k + s + carry_k) mod n,    carry_k = [x_k + r ≥ n]
  x_1 = r,  Q'_1 = s.

The extras conditions reduce to:

  extras_n[k]  = 1  iff  x_k ∈ S_n = {0} ∪ {n-r+1, ..., n-1}     |S_n|=r
  extras_n²[k] = 1  iff  (Q'_k, x_k) "lifts" into S_n²

Working out the lift gives an "aligned region" A ⊂ Z_n × Z_n: the
pairs (Q', x) where extras_n equals extras_n². The alignment
hypothesis fires for a cell iff (x_k, Q'_k) ∈ A for k = 1..b-1.

This script:
  (i)   enumerates the 27 n²-cancellation cells in the b=10 sweep,
  (ii)  computes (r, s) and the (x_k, Q'_k) trajectory for each,
  (iii) verifies the trajectory lies in A (sanity check),
  (iv)  looks for closed-form structure in (b, n, d, r, s).
"""

from sympy import isprime
from collections import defaultdict

B = 10
N_MAX = 200
D_MAX = 7


def per_strip_counts_n_and_nsq(b, n, d):
    W = b**(d - 1)
    n2 = n * n
    cn, cn2 = [], []
    for k in range(1, b):
        lo = k * W
        hi = (k + 1) * W - 1
        cn.append(hi // n - (lo - 1) // n)
        cn2.append(hi // n2 - (lo - 1) // n2)
    return cn, cn2


def is_smooth(b, n, d):
    return (b**(d - 1)) % (n * n) == 0


def is_family_e(b, n, d):
    return d >= 2 and b**(d - 1) <= n <= (b**d - 1) // (b - 1)


def collect_n2_cancel_cells():
    cells = []
    for d in range(1, D_MAX + 1):
        for n in range(2, N_MAX + 1):
            if is_smooth(B, n, d) or is_family_e(B, n, d):
                continue
            cn, cn2 = per_strip_counts_n_and_nsq(B, n, d)
            atoms = [a - b_ for a, b_ in zip(cn, cn2)]
            if not all(c == atoms[0] for c in atoms) or atoms[0] == 0:
                continue
            if all(c == cn[0] for c in cn):
                continue  # GFE; M_k(n) already constant
            cells.append((B, n, d, cn, cn2, atoms))
    return cells


def trajectory(b, n, d):
    """Compute (x_k, Q'_k) for k=1..b-1, plus (r, r', s)."""
    W = b**(d - 1)
    r = W % n
    r2 = W % (n * n)
    s = (r2 - r) // n  # well-defined since r2 ≡ r (mod n)
    assert (r2 - r) % n == 0, f"sanity: {r=}, {r2=}, n={n}"
    pts = []
    x = r
    Qp = s
    for k in range(1, b):
        pts.append((x, Qp))
        carry = 1 if x + r >= n else 0
        x = (x + r) % n
        Qp = (Qp + s + carry) % n
    return r, r2, s, pts


def in_aligned_region(Qp, x, n, r, s):
    """Decide whether (Qp, x) is in the aligned region A. Returns:
       0 if extras_n = extras_n² (aligned),
       +1 if extras_n high, extras_n² low (bad: N high),
       -1 if extras_n low, extras_n² high (bad: N² high)."""
    extras_n = 1 if (x == 0 or x >= n - r + 1) else 0
    # extras_n² requires lift y = Qp*n + x; condition y = 0 or
    # y ≥ n² - r' + 1 = n*(n-s) - r + 1 with r' = r + s*n.
    y = Qp * n + x
    threshold = n * n - (r + s * n) + 1  # = n*(n-s) - r + 1
    extras_n2 = 1 if (y == 0 or y >= threshold) else 0
    return extras_n - extras_n2


def reconstruct_extras(pts, n, r, s):
    """For each trajectory point, recover (extras_n, extras_n²)."""
    out = []
    for (x, Qp) in pts:
        en = 1 if (x == 0 or x >= n - r + 1) else 0
        y = Qp * n + x
        thr = n * n - (r + s * n) + 1
        en2 = 1 if (y == 0 or y >= thr) else 0
        out.append((en, en2))
    return out


def main():
    cells = collect_n2_cancel_cells()
    print(f"n²-cancellation cells in sweep: {len(cells)}\n")
    print(f"{'n':>4} {'d':>3} {'r':>5} {'r2':>7} {'s':>5} "
          f"{'r=s?':>5} {'r=s+1?':>7} {'gcd(r,n)':>9} "
          f"{'gcd(s,n)':>9}  pattern")
    misalign_count = 0
    flag_summary = defaultdict(int)
    for (b, n, d, cn, cn2, atoms) in cells:
        r, r2, s, pts = trajectory(b, n, d)
        en_pattern = ''.join(str(reconstruct_extras(pts, n, r, s)[k][0])
                              for k in range(len(pts)))
        en2_pattern = ''.join(str(reconstruct_extras(pts, n, r, s)[k][1])
                               for k in range(len(pts)))
        misaligned = sum(in_aligned_region(Qp, x, n, r, s) != 0
                          for (x, Qp) in pts)
        misalign_count += misaligned
        rs_eq = 'YES' if r == s else 'no'
        rs_eq1 = 'YES' if r == s + 1 else 'no'
        from math import gcd
        gcd_rn = gcd(r, n)
        gcd_sn = gcd(s, n)
        # Match pattern from analyze_lucky output
        assert en_pattern == en2_pattern, (
            f"alignment violation at ({n=}, {d=}): "
            f"en={en_pattern}, en2={en2_pattern}")
        flag = 'eq' if r == s else ('eq+1' if r == s + 1 else 'other')
        flag_summary[flag] += 1
        print(f"{n:>4} {d:>3} {r:>5} {r2:>7} {s:>5} "
              f"{rs_eq:>5} {rs_eq1:>7} {gcd_rn:>9} {gcd_sn:>9}  "
              f"{en_pattern}")
    print()
    print(f"Total trajectory misalignments (should be 0): "
          f"{misalign_count}")
    print()
    print("r-vs-s flag counts:")
    for f, c in sorted(flag_summary.items()):
        print(f"  {f:<8}  {c}")


if __name__ == '__main__':
    main()
