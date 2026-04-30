"""
survivors_core.py — bundle / survivor primitives for [n_0, n_1] x k.

A *bundle atom* is a pair (n, m) where m is one of the first k n-primes,
listed in read order n = n_0, n_0+1, ..., n_1. A bundle integer survives
iff it occurs in exactly one atom of the bundle.
"""

import sys
sys.path.insert(0, '../../../../core')

from acm_core import acm_n_primes


def bundle_atoms(n0, n1, k):
    """Return [(n, m), ...] in read order across the window."""
    out = []
    for n in range(n0, n1 + 1):
        for p in acm_n_primes(n, k):
            out.append((n, p))
    return out


def survival_mask(atoms):
    """Boolean list — True where the atom's integer is unique in the bundle."""
    counts = {}
    for _, m in atoms:
        counts[m] = counts.get(m, 0) + 1
    return [counts[m] == 1 for _, m in atoms]


def survivors_in_window(n0, n1, k):
    """Survivor integers in order of first appearance."""
    atoms = bundle_atoms(n0, n1, k)
    mask = survival_mask(atoms)
    return [m for (_, m), keep in zip(atoms, mask) if keep]
