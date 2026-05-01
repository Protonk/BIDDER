"""
kernel_zero/probe.py — first probe.

See PROBE.md for the spec. This file is the executable definition.

Substrate input: one prime row of the Q-lattice,
    row(p, h)[k - 1] = Q_p(p^h * k),  k = 1..K.

Default substrate is the cached float lattice
q_lattice_4000_h{5,6,7,8}.npy. The probe exercises the lattice-vs-
algebra contract: cell values from the float-cached lattice must
match q_general(p, h, k) (exact Fraction, then float) at TOL = 1e-12.

Transducers: identity, reverse (index reversal).

Channels: no_op, zero_count, value_multiset, prime_row_identity_at_k1.

Recovery: exact criteria from algebra/KERNEL-ZEROS.md and
algebra/MASTER-EXPANSION.md. Tolerance TOL = 1e-12 throughout.

Run via `sage -python probe.py` (numpy required, available via sage
per AGENTS.md).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from fractions import Fraction
from functools import lru_cache
from typing import Callable, Dict, List, Tuple

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PROBES_DIR = os.path.dirname(HERE)
EXPERIMENTS_DIR = os.path.dirname(PROBES_DIR)
REPO = os.path.dirname(EXPERIMENTS_DIR)
sys.path.insert(0, os.path.join(REPO, 'algebra'))

from predict_q import q_general  # noqa: E402

TOL = 1e-12

DEFAULT_PRIMES = (2, 3, 5, 7, 11, 13)
DEFAULT_HEIGHTS = (5, 6, 7, 8)
DEFAULT_K = 4000
DEFAULT_LATTICE_DIR = os.path.join(
    EXPERIMENTS_DIR, 'acm-champernowne', 'base10', 'art', 'q_distillery')


# --------------------------------------------------------------------------
# substrate input
# --------------------------------------------------------------------------

def lattice_row(p: int, h: int, lattice_dir: str, K: int) -> np.ndarray:
    """Substrate row from the cached q_lattice_4000_h{h}.npy file."""
    path = os.path.join(lattice_dir, f'q_lattice_4000_h{h}.npy')
    arr = np.load(path, mmap_mode='r')
    if arr.shape[1] < K:
        raise ValueError(f'lattice {path} has {arr.shape[1]} cols, need >= {K}')
    return np.asarray(arr[p - 2, :K], dtype=np.float64).copy()


def algebra_row(p: int, h: int, K: int) -> np.ndarray:
    """Substrate row computed exact-rationally via q_general, then float'd.
    Used for substrates 'algebra' (cross-check) and synthetic null."""
    return np.array([float(q_general(p, h, k)) for k in range(1, K + 1)],
                    dtype=np.float64)


def synth_uniform_row(K: int, seed: int = 0,
                      lo: float = -100.0, hi: float = 100.0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.uniform(lo, hi, size=K)


# --------------------------------------------------------------------------
# transducers
# --------------------------------------------------------------------------

def transducer_identity(row: np.ndarray) -> np.ndarray:
    return row.copy()


def transducer_reverse(row: np.ndarray) -> np.ndarray:
    return row[::-1].copy()


TRANSDUCERS: Dict[str, Callable[[np.ndarray], np.ndarray]] = {
    'identity': transducer_identity,
    'reverse': transducer_reverse,
}


# --------------------------------------------------------------------------
# predicted-set helpers
# --------------------------------------------------------------------------

@lru_cache(maxsize=None)
def _algebra_row_fraction(p: int, h: int, K: int) -> Tuple[Fraction, ...]:
    """Exact-Fraction row of Q_p(p^h k) for k=1..K. Cached per (p, h, K)."""
    return tuple(q_general(p, h, k) for k in range(1, K + 1))


def predicted_zero_indices(p: int, h: int, K: int) -> np.ndarray:
    """Cells (k - 1) where the algebra evaluator returns exact zero,
    i.e., q_general(p, h, k) == Fraction(0). This is the broader
    algebra-defined zero set: it includes the kernel-zero band of
    KERNEL-ZEROS.md (i) for coprime k, plus zeros at non-coprime
    cells k = p^t k' where the height-shifted classifier fires
    (q_general accounts for the effective height h + nu_p(k))."""
    row = _algebra_row_fraction(p, h, K)
    zero = Fraction(0)
    return np.array([i for i, v in enumerate(row) if v == zero],
                    dtype=np.int64)


def predicted_multiset(p: int, h: int, K: int) -> np.ndarray:
    """Sorted ascending multiset of float(q_general(p, h, k)) for k = 1..K."""
    return np.sort(np.array([float(v) for v in _algebra_row_fraction(p, h, K)],
                            dtype=np.float64))


# --------------------------------------------------------------------------
# channels
# --------------------------------------------------------------------------

def _verdict_from_strength(strength: float) -> str:
    if strength >= 1.0 - 1e-15:
        return 'present'
    if strength <= 1e-15:
        return 'absent'
    return 'partial'


def channel_no_op(row: np.ndarray, p: int, h: int) -> Tuple[str, float]:
    Z = predicted_zero_indices(p, h, len(row))
    if Z.size == 0:
        return 'present', 1.0
    n_zero = int(np.sum(np.abs(row[Z]) < TOL))
    strength = n_zero / Z.size
    return _verdict_from_strength(strength), strength


def channel_zero_count(row: np.ndarray, p: int, h: int) -> Tuple[str, float]:
    n_pred = int(predicted_zero_indices(p, h, len(row)).size)
    n_obs = int(np.sum(np.abs(row) < TOL))
    if n_pred == 0:
        return ('present', 1.0) if n_obs == 0 else ('absent', 0.0)
    if n_obs == n_pred:
        return 'present', 1.0
    strength = max(0.0, 1.0 - abs(n_obs - n_pred) / n_pred)
    return _verdict_from_strength(strength), strength


def channel_value_multiset(row: np.ndarray, p: int, h: int) -> Tuple[str, float]:
    M_pred = predicted_multiset(p, h, len(row))
    M_obs = np.sort(row)
    matches = int(np.sum(np.abs(M_pred - M_obs) < TOL))
    strength = matches / M_pred.size
    return _verdict_from_strength(strength), strength


def channel_prime_row_identity_at_k1(row: np.ndarray, p: int, h: int
                                     ) -> Tuple[str, float]:
    expected = float(Fraction(1, h))
    diff = abs(float(row[0]) - expected)
    return ('present', 1.0) if diff < TOL else ('absent', 0.0)


CHANNELS: Dict[str, Callable[[np.ndarray, int, int], Tuple[str, float]]] = {
    'no_op': channel_no_op,
    'zero_count': channel_zero_count,
    'value_multiset': channel_value_multiset,
    'prime_row_identity_at_k1': channel_prime_row_identity_at_k1,
}

CHANNEL_ORDER = ('no_op', 'zero_count', 'value_multiset',
                 'prime_row_identity_at_k1')


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------

def run_probe(config: dict, output_dir: str) -> Dict:
    """Run the probe at the given config, write results to output_dir.

    config keys:
        substrate:    'lattice' | 'algebra' | 'synth_uniform'
        transducer:   key in TRANSDUCERS
        primes:       list of primes
        heights:      list of heights
        K:            row width (default 4000)
        lattice_dir:  path to .npy files (substrate=lattice)
        seed:         seed for synth_uniform
    """
    os.makedirs(output_dir, exist_ok=True)

    K = int(config.get('K', DEFAULT_K))
    transducer_name = config['transducer']
    transducer = TRANSDUCERS[transducer_name]
    substrate = config['substrate']

    primes = list(config.get('primes', DEFAULT_PRIMES))
    heights = list(config.get('heights', DEFAULT_HEIGHTS))
    lattice_dir = config.get('lattice_dir', DEFAULT_LATTICE_DIR)

    cells: List[Tuple[int, int]] = [(p, h) for p in primes for h in heights]
    rows_pre = {}
    rows_post = {}
    results = {}

    for p, h in cells:
        if substrate == 'lattice':
            row_pre = lattice_row(p, h, lattice_dir, K)
        elif substrate == 'algebra':
            row_pre = algebra_row(p, h, K)
        elif substrate == 'synth_uniform':
            seed_base = int(config.get('seed', 0))
            row_pre = synth_uniform_row(K, seed=seed_base + 100 * p + h)
        else:
            raise ValueError(f'unknown substrate: {substrate!r}')

        row_post = transducer(row_pre)
        rows_pre[(p, h)] = row_pre
        rows_post[(p, h)] = row_post

        cell_results = {}
        for ch in CHANNEL_ORDER:
            verdict, strength = CHANNELS[ch](row_post, p, h)
            cell_results[ch] = {'verdict': verdict, 'strength': strength}
        results[(p, h)] = cell_results

    # Save post-transducer output as .npz (per probes/README.md).
    np.savez_compressed(
        os.path.join(output_dir, 'output.npz'),
        cells=np.array([list(c) for c in cells], dtype=np.int64),
        rows_post=np.stack([rows_post[c] for c in cells]),
        rows_pre=np.stack([rows_pre[c] for c in cells]),
    )

    # Save config.
    with open(os.path.join(output_dir, 'config.json'), 'w') as f:
        json.dump(config, f, indent=2, sort_keys=True)

    # Write report.
    write_report(os.path.join(output_dir, 'report.md'), config, cells, results)

    return {'cells': cells, 'results': results}


def write_report(path: str, config: dict, cells: List[Tuple[int, int]],
                 results: dict) -> None:
    by_channel: Dict[str, List[dict]] = {ch: [] for ch in CHANNEL_ORDER}
    for c in cells:
        for ch in CHANNEL_ORDER:
            r = results[c][ch]
            by_channel[ch].append({'cell': c, **r})

    lines = []
    run_name = os.path.basename(os.path.dirname(path)) or '<inline>'
    lines.append(f'# Run {run_name}')
    lines.append('')
    lines.append('## Config')
    lines.append('')
    lines.append('```json')
    lines.append(json.dumps(config, indent=2, sort_keys=True))
    lines.append('```')
    lines.append('')
    lines.append(f'Tolerance TOL = {TOL:g}.')
    lines.append('')
    lines.append('## Channel results (aggregated over all cells)')
    lines.append('')
    lines.append('| channel | n_present | n_partial | n_absent | mean strength | min strength | max strength |')
    lines.append('|---|---|---|---|---|---|---|')
    for ch in CHANNEL_ORDER:
        rows = by_channel[ch]
        n_p = sum(1 for r in rows if r['verdict'] == 'present')
        n_pa = sum(1 for r in rows if r['verdict'] == 'partial')
        n_a = sum(1 for r in rows if r['verdict'] == 'absent')
        ss = [r['strength'] for r in rows]
        lines.append(f'| `{ch}` | {n_p} | {n_pa} | {n_a} | '
                     f'{sum(ss)/len(ss):.6f} | {min(ss):.6f} | {max(ss):.6f} |')
    lines.append('')
    lines.append('## Per-cell verdicts')
    lines.append('')
    lines.append('| (p, h) | ' + ' | '.join(f'`{ch}`' for ch in CHANNEL_ORDER) + ' |')
    lines.append('|---' * (1 + len(CHANNEL_ORDER)) + '|')
    for c in cells:
        verdicts = '|'.join(
            f' {results[c][ch]["verdict"]} ({results[c][ch]["strength"]:.4f}) '
            for ch in CHANNEL_ORDER)
        lines.append(f'| ({c[0]}, {c[1]}) |{verdicts}|')
    lines.append('')
    lines.append('## Anomalies')
    lines.append('')

    expected = expected_verdicts(config)
    anomalies = []
    if expected is not None:
        for c in cells:
            for ch in CHANNEL_ORDER:
                got = results[c][ch]['verdict']
                want = expected[ch]
                if got != want:
                    anomalies.append(
                        f'- ({c[0]}, {c[1]}) `{ch}`: got `{got}` '
                        f'(strength {results[c][ch]["strength"]:.6f}), '
                        f'expected `{want}`')

    if not anomalies:
        lines.append('None.')
    else:
        lines.extend(anomalies)
    lines.append('')

    with open(path, 'w') as f:
        f.write('\n'.join(lines))


def expected_verdicts(config: dict) -> Dict[str, str] | None:
    """Expected per-channel verdict for the three calibration configs.
    Returns None for configs not enumerated in the calibration plan."""
    sub = config.get('substrate')
    trans = config.get('transducer')
    if sub in ('lattice', 'algebra') and trans == 'identity':
        return {ch: 'present' for ch in CHANNEL_ORDER}
    if sub in ('lattice', 'algebra') and trans == 'reverse':
        # Under (A): no_op measures reversal-symmetry of the
        # algebra-zero set; expected 'partial', not 'absent'.
        return {
            'no_op': 'partial',
            'zero_count': 'present',
            'value_multiset': 'present',
            'prime_row_identity_at_k1': 'absent',
        }
    if sub == 'synth_uniform' and trans == 'identity':
        return {ch: 'absent' for ch in CHANNEL_ORDER}
    return None


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def calibration_runs() -> List[Tuple[str, dict]]:
    date = datetime.now().strftime('%Y-%m-%d')
    return [
        (f'{date}_identity', {
            'substrate': 'lattice', 'transducer': 'identity',
            'primes': list(DEFAULT_PRIMES), 'heights': list(DEFAULT_HEIGHTS),
            'K': DEFAULT_K, 'lattice_dir': DEFAULT_LATTICE_DIR}),
        (f'{date}_reverse', {
            'substrate': 'lattice', 'transducer': 'reverse',
            'primes': list(DEFAULT_PRIMES), 'heights': list(DEFAULT_HEIGHTS),
            'K': DEFAULT_K, 'lattice_dir': DEFAULT_LATTICE_DIR}),
        (f'{date}_null', {
            'substrate': 'synth_uniform', 'transducer': 'identity',
            'primes': list(DEFAULT_PRIMES), 'heights': list(DEFAULT_HEIGHTS),
            'K': DEFAULT_K, 'seed': 0}),
    ]


def main():
    runs_dir = os.path.join(HERE, 'runs')
    os.makedirs(runs_dir, exist_ok=True)
    for name, config in calibration_runs():
        out = os.path.join(runs_dir, name)
        print(f'=== running {name} ===')
        run_probe(config, out)
        print(f'    wrote {out}')


if __name__ == '__main__':
    main()
