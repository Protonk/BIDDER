"""
crossing_angles.py — angles between sawtooth and running mean at crossings

Find where C_2(n) crosses M(n) (the running mean), compute the slope
of each curve at the crossing, and report the angle between them.
"""

import sys, os

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..'))
sys.path.insert(0, os.path.join(_here, '..', '..', '..'))

import numpy as np
from acm_core import acm_n_primes


N_MAX = 8000
K = 5


def binary_champernowne_real(n, count=K):
    primes = acm_n_primes(n, count)
    value = 1.0
    pos = 1
    for p in primes:
        for ch in bin(p)[2:]:
            value += int(ch) * 2.0**(-pos)
            pos += 1
    return value


print("Computing binary Champernowne reals...")
ns = np.arange(1, N_MAX + 1, dtype=float)
c2 = np.empty(N_MAX)
for i, n in enumerate(ns):
    if int(n) % 2000 == 0:
        print(f"  n = {int(n)}...")
    c2[i] = binary_champernowne_real(int(n))

run_mean = np.cumsum(c2) / np.arange(1, N_MAX + 1)

# Difference: positive when sawtooth > mean
diff = c2 - run_mean

# Find zero crossings (sign changes)
crossings = []
for i in range(len(diff) - 1):
    if diff[i] * diff[i + 1] < 0:
        # Linear interpolation for fractional crossing point
        t = diff[i] / (diff[i] - diff[i + 1])
        n_cross = ns[i] + t * (ns[i + 1] - ns[i])
        crossings.append((i, t, n_cross))

print(f"\nFound {len(crossings)} crossings in n = 1..{N_MAX}")

# Compute slopes at each crossing
# Sawtooth slope: d(C_2)/dn ≈ (C_2(n+1) - C_2(n-1)) / 2
# Running-mean slope: d(M)/dn ≈ (M(n+1) - M(n-1)) / 2
# Angle = arctan(|slope1 - slope2| / (1 + slope1 * slope2))

print(f"\nFirst 12 crossings:")
print(f"  {'#':>3s}  {'n_cross':>10s}  {'saw slope':>12s}  {'mean slope':>12s}  {'angle (deg)':>12s}  {'direction':>10s}")

for k, (i, t, n_cross) in enumerate(crossings[:12]):
    # Slopes via central difference (or one-sided at boundaries)
    if i >= 1 and i < N_MAX - 1:
        saw_slope = (c2[i + 1] - c2[i - 1]) / 2.0
        mean_slope = (run_mean[i + 1] - run_mean[i - 1]) / 2.0
    elif i == 0:
        saw_slope = c2[1] - c2[0]
        mean_slope = run_mean[1] - run_mean[0]
    else:
        saw_slope = c2[i] - c2[i - 1]
        mean_slope = run_mean[i] - run_mean[i - 1]

    # Angle between the two tangent lines
    # tan(theta) = |m1 - m2| / (1 + m1 * m2)
    denom = 1.0 + saw_slope * mean_slope
    if abs(denom) < 1e-15:
        angle_deg = 90.0
    else:
        tan_theta = abs(saw_slope - mean_slope) / denom
        angle_deg = np.degrees(np.arctan(tan_theta))

    # Direction: sawtooth crossing up or down through the mean
    direction = "saw↑" if diff[i] < 0 else "saw↓"

    print(f"  {k+1:3d}  {n_cross:10.2f}  {saw_slope:12.6f}  {mean_slope:12.6f}  {angle_deg:12.4f}  {direction:>10s}")
