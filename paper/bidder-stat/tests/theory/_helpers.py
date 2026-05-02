"""
_helpers.py — Shared helpers for the theory red-team tests.

Distilled from the experiment family in experiments/bidder/unified/
and experiments/bidder/stratified/ and experiments/bidder/reseed/.
See tests/theory/README.md for the theorem index and provenance.

No numpy, no matplotlib, no sage. Stock python3 only.
"""

import math
import os
import random
import sys

# Wire up repo root so `import bidder` resolves.
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, '..', '..'))
sys.path.insert(0, _REPO)

import bidder  # noqa: E402


# ---------------------------------------------------------------------------
# 1. Integrand registry
# ---------------------------------------------------------------------------
# Source: riemann_proof.py, adversarial_integrands.py, stratified.py

INTEGRANDS = [
    # (name, callable, true_integral, endpoint_note, kind)
    ('sin(pi*x)',
     lambda x: math.sin(math.pi * x),
     2.0 / math.pi,
     'f(0)=f(1)=0',
     'favorable'),

    ('x',
     lambda x: x,
     0.5,
     'f(0)!=f(1)',
     'adversarial'),

    ('x^2(1-x)^2',
     lambda x: x**2 * (1 - x)**2,
     1.0 / 30.0,
     'f,f\' match at endpoints',
     'favorable'),

    ('sqrt(x)',
     lambda x: math.sqrt(x),
     2.0 / 3.0,
     'f(0)!=f(1), f\'(0)=inf',
     'adversarial'),

    ('step_1/3',
     lambda x: 1.0 if x >= 1.0 / 3.0 else 0.0,
     2.0 / 3.0,
     'discontinuous',
     'adversarial'),
]


def get_integrand(name):
    """Look up an integrand by name. Returns (f, I, note, kind)."""
    for n, f, I, note, kind in INTEGRANDS:
        if n == name:
            return f, I, note, kind
    raise KeyError(f"unknown integrand: {name!r}")


# ---------------------------------------------------------------------------
# 2. Direct grid mean / bias helpers
# ---------------------------------------------------------------------------
# Source: riemann_proof.py:116-120, adversarial_integrands.py:97-105

def grid_values(P):
    """Return the grid points [0/P, 1/P, ..., (P-1)/P]."""
    return [k / P for k in range(P)]


def riemann_sum(f, P):
    """Left-endpoint Riemann sum R = (1/P) sum f(k/P)."""
    return sum(f(k / P) for k in range(P)) / P


def riemann_bias(f, P, I_true):
    """Absolute Riemann-sum bias |R - I|."""
    return abs(riemann_sum(f, P) - I_true)


# ---------------------------------------------------------------------------
# 3. Cipher prefix helpers
# ---------------------------------------------------------------------------
# Source: riemann_proof.py:103-114, adversarial_integrands.py:117-128,
#         mc_diagnostic.py:91-99

def cipher_values(P, key):
    """Full permutation as values in [0, 1): [at(i)/P for i in 0..P-1]."""
    B = bidder.cipher(period=P, key=key)
    return [B.at(i) / P for i in range(P)]


def cipher_prefix_mean(f, P, key, N):
    """E_N(key) = (1/N) sum f(at(i)/P) for i in 0..N-1."""
    B = bidder.cipher(period=P, key=key)
    return sum(f(B.at(i) / P) for i in range(N)) / N


def cipher_full_mean(f, P, key):
    """E_P(key) = prefix mean at N = P."""
    return cipher_prefix_mean(f, P, key, P)


def cipher_key_ensemble(f, P, keys, N):
    """Vector of prefix means, one per key."""
    return [cipher_prefix_mean(f, P, key, N) for key in keys]


# ---------------------------------------------------------------------------
# 4. Ensemble summary helpers
# ---------------------------------------------------------------------------
# Source: stratified.py:81-87, stratified.py:153-171

def rmse_about(target, values):
    """Root-mean-square error of values around a target."""
    if not values:
        return 0.0
    return math.sqrt(sum((v - target)**2 for v in values) / len(values))


def spread(values):
    """Max - min of a list of numbers."""
    return max(values) - min(values)


# ---------------------------------------------------------------------------
# 5. Uniform-permutation null helper
# ---------------------------------------------------------------------------
# Source pattern: reseed_test.py:68-98

def shuffle_prefix_means(f_values, N, n_trials, seed):
    """Generate n_trials prefix means of length N from random
    shuffles of f_values. Returns a list of floats.

    f_values: the population [f(0/P), f(1/P), ..., f((P-1)/P)].
    Each trial shuffles f_values and takes the mean of the first N.

    This is the ideal without-replacement null: a uniformly random
    permutation prefix. The FPC formula should match its variance.
    """
    rng = random.Random(seed)
    population = list(f_values)
    means = []
    for _ in range(n_trials):
        rng.shuffle(population)
        means.append(sum(population[:N]) / N)
    return means


# ---------------------------------------------------------------------------
# 6. Permutation sanity helper
# ---------------------------------------------------------------------------
# Source: period_anatomy.py:56-61, period_anatomy.py:172-177

def assert_is_permutation(seq, P):
    """Assert that seq is a permutation of [0, P)."""
    assert len(seq) == P, f"length {len(seq)} != {P}"
    assert sorted(seq) == list(range(P)), (
        f"not a permutation of [0, {P})")


def cipher_is_permutation(P, key):
    """Assert that bidder.cipher(P, key) produces a permutation of [0, P)."""
    B = bidder.cipher(period=P, key=key)
    seq = [B.at(i) for i in range(P)]
    assert_is_permutation(seq, P)
