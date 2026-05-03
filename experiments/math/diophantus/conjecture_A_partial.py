"""
Investigation B (started): partial proof of Conjecture A.

Conjecture A. In the substrate r = s sub-sub-case with n² > W,
case (i) holds iff r ∤ n.

The proof has two parts:
  (1) Show M < r/gcd(n, r) for all substrate-compatible (n, r)
      with r ∤ n. This kills the obvious j_fail = r/gcd
      obstruction.
  (2) Show the Beatty inequality holds at every j ∈ [1, M],
      assuming (1) and r ∤ n.

This script empirically verifies part (1) across the wider sweep,
and quantifies how much "headroom" there is between M and r/gcd.

Part (1) is reducible to: bg(n+1) < n²  where g = gcd(n, r).
Equivalent: n > (bg + √((bg)² + 4bg)) / 2,
roughly:    n > bg.

The substrate constraint W = r(n+1) = b^(d-1) restricts (n, r)
substantially: r(n+1) must be a power of b, so both r and n+1
are b-smooth (factors only from {primes dividing b}).
"""

from math import gcd

B = 10
N_MAX = 5000
D_MAX = 14


def per_strip_n_count(b, n, d):
    W = b**(d - 1)
    return [((k + 1) * W - 1) // n - (k * W - 1) // n
            for k in range(1, b)]


def is_smooth(b, n, d):
    return (b**(d - 1)) % (n * n) == 0


def is_family_e(b, n, d):
    return d >= 2 and b**(d - 1) <= n <= (b**d - 1) // (b - 1)


# Sweep for substrate r = s cells, check M < r/gcd(n, r).
print(f"Substrate sweep: b={B}, n ≤ {N_MAX}, d ≤ {D_MAX}")
print()
print("Testing part (1) of Conjecture A:")
print("  In substrate context with r=s, n²>W, r ∤ n: M < r/gcd(n, r).")
print()

cells_total = 0
cells_satisfying_1 = 0
violations_1 = []
headroom_distribution = []

for d in range(1, D_MAX + 1):
    W = B**(d - 1)
    for n in range(2, N_MAX + 1):
        if is_smooth(B, n, d) or is_family_e(B, n, d):
            continue
        if n * n <= W:
            continue
        r = W % n
        s = (W // n) % n
        if r != s:
            continue
        if r == 0:
            continue
        if n % r == 0:
            continue  # r | n, falls outside Conjecture A's scope
        cells_total += 1
        g = gcd(n, r)
        M = (B * W - 1) // (n * n)  # Corrected.
        target = r // g  # j_fail
        headroom = target - M
        headroom_distribution.append(headroom)
        if M < target:
            cells_satisfying_1 += 1
        else:
            violations_1.append((n, d, r, g, M, target))

print(f"Substrate r=s cells with r ∤ n: {cells_total}")
print(f"  satisfying M < r/g (part 1):  {cells_satisfying_1}")
print(f"  violations:                    {len(violations_1)}")
print()

if violations_1:
    print("Part (1) violations:")
    print(f"{'n':>5} {'d':>3} {'r':>5} {'g':>3} {'M':>4} {'r/g':>5}")
    for n, d, r, g, M, target in violations_1[:20]:
        print(f"{n:>5} {d:>3} {r:>5} {g:>3} {M:>4} {target:>5}")

# Headroom distribution
print(f"Headroom distribution (r/g − M):")
import collections
headroom_counts = collections.Counter(headroom_distribution)
for h in sorted(headroom_counts.keys())[:15]:
    print(f"  headroom = {h:>4}: {headroom_counts[h]:>5} cells")
if len(headroom_counts) > 15:
    print(f"  ... ({len(headroom_counts) - 15} more headroom values)")
print()

print(f"Min headroom: {min(headroom_distribution)}")
print(f"Mean headroom: "
      f"{sum(headroom_distribution)/len(headroom_distribution):.1f}")

# Check the simpler condition n > bg
print()
print("Checking the simpler bound n > b·g (sufficient for n² > bg(n+1)):")
satisfies_simple = sum(
    1 for d in range(1, D_MAX + 1)
    for n in range(2, N_MAX + 1)
    if not is_smooth(B, n, d) and not is_family_e(B, n, d)
    and n * n > B**(d - 1)
    and (B**(d - 1)) % n == (B**(d - 1) // n) % n  # r = s
    and (B**(d - 1)) % n != 0  # r > 0
    and n % ((B**(d - 1)) % n) != 0  # r ∤ n
    and n > B * gcd(n, (B**(d - 1)) % n)
)
print(f"Cells satisfying n > b·g: {satisfies_simple} / {cells_total}")
