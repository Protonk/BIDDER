"""
Investigation A (continued): probe the conjecture

  (Conjecture A.) For r = s sub-sub-case in the n² > W sub-locus,
  the Beatty inequality holds for all j = 1, …, M iff r ∤ n.

The j = 1 boundary condition gives r ∤ n as necessary. The conjecture
says it is also sufficient. The mechanism: the first j at which
(jn) mod r = 0 is j = r/gcd(n, r). For r ∤ n: this j is at least 2.
For M < this j: no zero hits, so the condition can hold.

This script:
  1. Extends the substrate-context sweep (b = 10, larger d, n)
     to find cells where M is close to r — testing whether j > 1
     failures emerge.
  2. Probes the conjecture *outside the substrate context*: for
     arbitrary (n, r, b) with r ∤ n, does alignment hold for all j
     up to some j_max we care about? This decouples the inequality
     from the (b, d) → (n, r) substrate constraint.
  3. Looks for explicit counter-examples or supporting structure.
"""

from math import gcd

# --- Substrate-context sweep with larger range. ---

print("=" * 72)
print("Part 1: substrate-context sweep, looking for j > 1 failures")
print("=" * 72)
print()


def first_break(n, r, M):
    n_plus_1 = n + 1
    for j in range(1, M + 1):
        # Corrected: ⌈jn/(n+1)⌉, not ⌈jr/(n+1)⌉.
        if (j * n) % r < -(-(j * n) // n_plus_1):
            return j
    return None


def per_strip_n_count(b, n, d):
    W = b**(d - 1)
    return [((k + 1) * W - 1) // n - (k * W - 1) // n
            for k in range(1, b)]


def per_strip_atoms(b, n, d):
    W = b**(d - 1)
    n2 = n * n
    return [
        ((k + 1) * W - 1) // n - (k * W - 1) // n
        - (((k + 1) * W - 1) // n2 - (k * W - 1) // n2)
        for k in range(1, b)
    ]


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


# Search across a large b = 10 sweep.
B = 10
N_MAX = 5000
D_MAX = 14

print(f"Searching b={B}, n ≤ {N_MAX}, d ≤ {D_MAX}...")

j_higher_failures = []
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
        M = (B * W - 1) // (n * n)  # Corrected.
        if M == 0:
            continue
        fb = first_break(n, r, M)
        if fb is not None and fb > 1:
            j_higher_failures.append((n, d, r, M, fb))

print(f"Cells with first-failure at j > 1: {len(j_higher_failures)}")
if j_higher_failures:
    print(f"{'n':>5} {'d':>3} {'r':>5} {'M':>4} {'j*':>3}")
    for n, d, r, M, fb in j_higher_failures[:20]:
        print(f"{n:>5} {d:>3} {r:>5} {M:>4} {fb:>3}")
    if len(j_higher_failures) > 20:
        print(f"... {len(j_higher_failures) - 20} more")
else:
    print("None. j = 1 (r ∤ n) is the only operative condition in")
    print("the swept range for r = s in the substrate context.")
print()

# --- Decoupled (n, r, b) sweep: just the inequality. ---

print("=" * 72)
print("Part 2: decoupled probe — the Beatty inequality in isolation")
print("=" * 72)
print()
print("Question: for (n, r, b) with r ∤ n, r < n, does")
print("  (jn) mod r ≥ ⌈jr/(n+1)⌉ for j = 1..b−1")
print("hold? (Stripping the substrate constraint that W = r(n+1).)")
print()


def beatty_ladder_check(n, r, j_max):
    """Check inequality for j = 1..j_max. Return first failing j or
    None."""
    np1 = n + 1
    for j in range(1, j_max + 1):
        # Corrected: ⌈jn/(n+1)⌉.
        if (j * n) % r < -(-(j * n) // np1):
            return j
    return None


# Sweep (n, r) with r ∤ n, r < n, for various n.
N_RANGE = range(3, 200)
J_MAX = 20  # check all j up to 20

print(f"Sweeping n ∈ {list(N_RANGE)[:3]}…{list(N_RANGE)[-3:]} "
      f"with r ∈ {{1, …, n−1}}, r ∤ n, j up to {J_MAX}.")
print()

violations_by_jstar = {}
total_pairs = 0
for n in N_RANGE:
    for r in range(1, n):
        if n % r == 0:
            continue
        total_pairs += 1
        fb = beatty_ladder_check(n, r, J_MAX)
        if fb is not None and fb > 1:
            violations_by_jstar.setdefault(fb, []).append((n, r))

print(f"Pairs tested:                {total_pairs}")
print(f"Pairs with first-fail at j*:")
for jstar in sorted(violations_by_jstar.keys())[:10]:
    cnt = len(violations_by_jstar[jstar])
    sample = violations_by_jstar[jstar][:3]
    print(f"  j* = {jstar:>2}: {cnt:>5} pairs, e.g. {sample}")
print()

if 2 in violations_by_jstar:
    print("Decoupled probe: yes — there ARE (n, r) with r ∤ n that")
    print("fail at j = 2 or higher. The substrate-context observation")
    print("(j = 1 catches all) is therefore SWEEP-DEPENDENT, not a")
    print("universal theorem.")
else:
    print("Even decoupled, no j > 1 failures in this range.")