"""
walsh_shuf_join.py — replay the Walsh/shuf join metric used in
../../STRUCTURAL-SIGNATURES.md.

The metric is the mean over the 44 robust cells of

    P_real[s] / P_shuf[s]

(per-cell ratios, then averaged — not ratio of means). The count
printed in parentheses is the number of those 44 cells where
P_real[s] > P_shuf[s].

Inputs:
  walsh_spectra.npz   — produced by walsh.py
  walsh_controls.npz  — produced by walsh_upgrade.py

Output: a small table on stdout, one row per monoid n in the panel
(n = 2..32 in the current run). The doc table rounds these to two
decimals.

Run with `sage walsh_shuf_join.py` from this directory.
"""

import os
import numpy as np


_here = os.path.dirname(os.path.abspath(__file__))

spec = np.load(os.path.join(_here, 'walsh_spectra.npz'))
ctrl = np.load(os.path.join(_here, 'walsh_controls.npz'), allow_pickle=True)

spec_ns = list(spec['ns'])
spectra = spec['spectra']           # (n_monoids, 256)

ctrl_ns = [int(n) for n in ctrl['ns']]
indices = ctrl['indices']           # (44,) robust cell indices
shuffle = ctrl['shuffle']           # (n_monoids, 44) shuffle control

print(f"{'n':>4}  {'mean(real/shuf)':>16}  {'above':>10}")
print('-' * 36)
for n in ctrl_ns:
    si = spec_ns.index(n)
    ci = ctrl_ns.index(n)
    real_power = spectra[si, indices]
    shuf_power = shuffle[ci, :]
    ratio_per_cell = real_power / shuf_power
    metric = float(ratio_per_cell.mean())
    above = int(np.sum(real_power > shuf_power))
    print(f"{n:>4d}  {metric:>16.4f}  {above:>6d}/44")
