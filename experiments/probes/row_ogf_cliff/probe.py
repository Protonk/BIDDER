"""
row_ogf_cliff/probe.py — second probe.

See PROBE.md for the spec. This file is the executable definition.

Substrate input: a column of the Q-lattice indexed by h,
    col(p, q, e)[h - 1] = Q_p(p^h * q^e),  h = 1..H_max,
computed via algebra/predict_q.q_general (exact Fraction, then float).

Transducer: scalar multiplication by c, bound to c = 2.

Channels: no_op, cliff, leading_multinomial, qe_closed_form,
prime_row_identity_at_h1.

Recovery: exact criteria from algebra/ROW-OGF.md and
algebra/KERNEL-ZEROS.md (ii). Tolerance TOL = 1e-12.

Run via `sage -python probe.py` (numpy + matplotlib via sage per
AGENTS.md).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from fractions import Fraction
from functools import lru_cache
from math import comb
from typing import Callable, Dict, List, Tuple

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
PROBES_DIR = os.path.dirname(HERE)
EXPERIMENTS_DIR = os.path.dirname(PROBES_DIR)
REPO = os.path.dirname(EXPERIMENTS_DIR)
sys.path.insert(0, os.path.join(REPO, 'algebra'))

from predict_q import q_general  # noqa: E402

TOL = 1e-12

# Panel: (p, q, e) with p, q distinct primes, e in {1, 2, 3, 4}.
# q is fixed per p as the smallest prime != p, so the panel is one-to-one
# in (p, e) and the q values are determined.
DEFAULT_PRIMES = (2, 3, 5, 7)
DEFAULT_EXPONENTS = (1, 2, 3, 4)
DEFAULT_H_MAX = max(DEFAULT_EXPONENTS) + 5  # 9
DEFAULT_C = 2  # bound scaling factor


def companion_q(p: int) -> int:
    """The 'first prime not equal to p' for the panel: 3 if p=2, else 2."""
    return 3 if p == 2 else 2


def panel_cells(primes=DEFAULT_PRIMES, exponents=DEFAULT_EXPONENTS
                ) -> List[Tuple[int, int, int]]:
    """List of (p, q, e) panel cells."""
    return [(p, companion_q(p), e) for p in primes for e in exponents]


# --------------------------------------------------------------------------
# substrate input
# --------------------------------------------------------------------------

@lru_cache(maxsize=None)
def _algebra_column_fraction(p: int, q: int, e: int, H_max: int
                              ) -> Tuple[Fraction, ...]:
    """Exact-Fraction column of Q_p(p^h * q^e) for h=1..H_max."""
    k_prime = q ** e
    return tuple(q_general(p, h, k_prime) for h in range(1, H_max + 1))


def algebra_column(p: int, q: int, e: int, H_max: int) -> np.ndarray:
    """Substrate column computed exact-rationally via q_general, then float'd."""
    return np.array([float(v) for v in _algebra_column_fraction(p, q, e, H_max)],
                    dtype=np.float64)


def synth_uniform_column(H_max: int, seed: int = 0,
                          lo: float = -100.0, hi: float = 100.0
                          ) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.uniform(lo, hi, size=H_max)


# --------------------------------------------------------------------------
# transducers
# --------------------------------------------------------------------------

def transducer_identity(col: np.ndarray) -> np.ndarray:
    return col.copy()


def transducer_scale_2x(col: np.ndarray) -> np.ndarray:
    return DEFAULT_C * col.copy()


TRANSDUCERS: Dict[str, Callable[[np.ndarray], np.ndarray]] = {
    'identity': transducer_identity,
    'scale_2x': transducer_scale_2x,
}


# --------------------------------------------------------------------------
# closed-form predictions
# --------------------------------------------------------------------------

def predicted_qe_closed(e: int, H_max: int) -> np.ndarray:
    """Closed-form column [(-1)^(h-1) C(e, h) / e for h = 1..H_max].

    Equals zero for h > e (since C(e, h) = 0 there). Independent of q
    and p; depends only on e.
    """
    return np.array([(-1) ** (h - 1) * Fraction(comb(e, h), e)
                     if h <= e else Fraction(0)
                     for h in range(1, H_max + 1)],
                    dtype=np.float64)


def predicted_leading_multinomial(e: int) -> float:
    """The forced leading coefficient: (-1)^(e-1) (e-1)! / e! = (-1)^(e-1) / e."""
    return float(Fraction((-1) ** (e - 1), e))


def predicted_cliff_indices(e: int, H_max: int) -> np.ndarray:
    """Cliff positions (0-indexed): h = e+1, e+2, ..., H_max."""
    return np.arange(e, H_max, dtype=np.int64)


# --------------------------------------------------------------------------
# channels
# --------------------------------------------------------------------------

def _verdict_from_strength(strength: float) -> str:
    if strength >= 1.0 - 1e-15:
        return 'present'
    if strength <= 1e-15:
        return 'absent'
    return 'partial'


def channel_no_op(col: np.ndarray, p: int, q: int, e: int,
                   H_max: int) -> Tuple[str, float]:
    pred = algebra_column(p, q, e, H_max)
    matches = int(np.sum(np.abs(col - pred) < TOL))
    strength = matches / H_max
    return _verdict_from_strength(strength), strength


def channel_cliff(col: np.ndarray, p: int, q: int, e: int,
                   H_max: int) -> Tuple[str, float]:
    cliff = predicted_cliff_indices(e, H_max)
    if cliff.size == 0:
        return 'present', 1.0
    n_zero = int(np.sum(np.abs(col[cliff]) < TOL))
    strength = n_zero / cliff.size
    return _verdict_from_strength(strength), strength


def channel_leading_multinomial(col: np.ndarray, p: int, q: int, e: int,
                                  H_max: int) -> Tuple[str, float]:
    expected = predicted_leading_multinomial(e)
    diff = abs(float(col[e - 1]) - expected)
    return ('present', 1.0) if diff < TOL else ('absent', 0.0)


def channel_qe_closed_form(col: np.ndarray, p: int, q: int, e: int,
                             H_max: int) -> Tuple[str, float]:
    closed = predicted_qe_closed(e, H_max)
    matches = int(np.sum(np.abs(col - closed) < TOL))
    strength = matches / H_max
    return _verdict_from_strength(strength), strength


def channel_prime_row_identity_at_h1(col: np.ndarray, p: int, q: int, e: int,
                                       H_max: int) -> Tuple[str, float]:
    diff = abs(float(col[0]) - 1.0)
    return ('present', 1.0) if diff < TOL else ('absent', 0.0)


CHANNELS: Dict[str, Callable[[np.ndarray, int, int, int, int],
                              Tuple[str, float]]] = {
    'no_op': channel_no_op,
    'cliff': channel_cliff,
    'leading_multinomial': channel_leading_multinomial,
    'qe_closed_form': channel_qe_closed_form,
    'prime_row_identity_at_h1': channel_prime_row_identity_at_h1,
}

CHANNEL_ORDER = ('no_op', 'cliff', 'leading_multinomial',
                 'qe_closed_form', 'prime_row_identity_at_h1')


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------

def run_probe(config: dict, output_dir: str) -> Dict:
    """Run the probe at the given config, write results to output_dir.

    config keys:
        substrate:    'algebra' | 'synth_uniform'
        transducer:   key in TRANSDUCERS
        primes:       list of primes (substrate=algebra)
        exponents:    list of e values (substrate=algebra)
        H_max:        column length
        seed:         seed for synth_uniform
    """
    os.makedirs(output_dir, exist_ok=True)

    H_max = int(config.get('H_max', DEFAULT_H_MAX))
    transducer_name = config['transducer']
    transducer = TRANSDUCERS[transducer_name]
    substrate = config['substrate']

    primes = list(config.get('primes', DEFAULT_PRIMES))
    exponents = list(config.get('exponents', DEFAULT_EXPONENTS))
    cells: List[Tuple[int, int, int]] = [
        (p, companion_q(p), e) for p in primes for e in exponents
    ]
    cols_pre = {}
    cols_post = {}
    results = {}

    for p, q, e in cells:
        if substrate == 'algebra':
            col_pre = algebra_column(p, q, e, H_max)
        elif substrate == 'synth_uniform':
            seed_base = int(config.get('seed', 0))
            col_pre = synth_uniform_column(
                H_max, seed=seed_base + 100 * p + 10 * q + e)
        else:
            raise ValueError(f'unknown substrate: {substrate!r}')

        col_post = transducer(col_pre)
        cols_pre[(p, q, e)] = col_pre
        cols_post[(p, q, e)] = col_post

        cell_results = {}
        for ch in CHANNEL_ORDER:
            verdict, strength = CHANNELS[ch](col_post, p, q, e, H_max)
            cell_results[ch] = {'verdict': verdict, 'strength': strength}
        results[(p, q, e)] = cell_results

    # Save post-transducer output as .npz.
    np.savez_compressed(
        os.path.join(output_dir, 'output.npz'),
        cells=np.array([list(c) for c in cells], dtype=np.int64),
        cols_post=np.stack([cols_post[c] for c in cells]),
        cols_pre=np.stack([cols_pre[c] for c in cells]),
    )

    with open(os.path.join(output_dir, 'config.json'), 'w') as f:
        json.dump(config, f, indent=2, sort_keys=True)

    write_report(os.path.join(output_dir, 'report.md'), config, cells, results)

    figures_dir = os.path.join(output_dir, 'figures')
    os.makedirs(figures_dir, exist_ok=True)
    make_figures(figures_dir, config, cells, results, cols_post)

    return {'cells': cells, 'results': results}


def expected_verdicts(config: dict) -> Dict[str, str] | None:
    sub = config.get('substrate')
    trans = config.get('transducer')
    if sub == 'algebra' and trans == 'identity':
        return {ch: 'present' for ch in CHANNEL_ORDER}
    if sub == 'algebra' and trans == 'scale_2x':
        # Under scaling c = 2:
        # - cliff is scale-invariant (c * 0 = 0).
        # - leading_multinomial scales by c, off the predicted value.
        # - no_op and qe_closed_form: only cliff cells match; non-cliff cells
        #   are off by factor c. Strength = (H_max - e) / H_max per cell;
        #   that's strictly between 0 and 1 for every panel cell, so PARTIAL.
        # - prime_row_identity_at_h1: col[0] = c != 1.
        return {
            'no_op': 'partial',
            'cliff': 'present',
            'leading_multinomial': 'absent',
            'qe_closed_form': 'partial',
            'prime_row_identity_at_h1': 'absent',
        }
    if sub == 'synth_uniform' and trans == 'identity':
        return {ch: 'absent' for ch in CHANNEL_ORDER}
    return None


# --------------------------------------------------------------------------
# report writer
# --------------------------------------------------------------------------

def write_report(path: str, config: dict, cells: List[Tuple[int, int, int]],
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
    lines.append('| (p, q, e) | ' + ' | '.join(f'`{ch}`' for ch in CHANNEL_ORDER) + ' |')
    lines.append('|---' * (1 + len(CHANNEL_ORDER)) + '|')
    for c in cells:
        verdicts = '|'.join(
            f' {results[c][ch]["verdict"]} ({results[c][ch]["strength"]:.4f}) '
            for ch in CHANNEL_ORDER)
        lines.append(f'| ({c[0]}, {c[1]}, {c[2]}) |{verdicts}|')
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
                        f'- ({c[0]}, {c[1]}, {c[2]}) `{ch}`: got `{got}` '
                        f'(strength {results[c][ch]["strength"]:.6f}), '
                        f'expected `{want}`')

    if not anomalies:
        lines.append('None.')
    else:
        lines.extend(anomalies)
    lines.append('')

    with open(path, 'w') as f:
        f.write('\n'.join(lines))


# --------------------------------------------------------------------------
# figures
# --------------------------------------------------------------------------

def _strength_grid(cells: List[Tuple[int, int, int]],
                   results: dict) -> np.ndarray:
    grid = np.zeros((len(cells), len(CHANNEL_ORDER)), dtype=np.float64)
    for i, c in enumerate(cells):
        for j, ch in enumerate(CHANNEL_ORDER):
            grid[i, j] = results[c][ch]['strength']
    return grid


def figure_verdict_matrix(figures_dir: str,
                           cells: List[Tuple[int, int, int]],
                           results: dict, run_name: str) -> None:
    grid = _strength_grid(cells, results)
    n_cells, n_channels = grid.shape

    fig, ax = plt.subplots(figsize=(7, 8), dpi=150, facecolor='white')
    im = ax.imshow(grid, aspect='auto', cmap='viridis',
                   vmin=0.0, vmax=1.0, interpolation='nearest')
    ax.set_xticks(range(n_channels))
    ax.set_xticklabels(CHANNEL_ORDER, rotation=45, ha='right', fontsize=8)
    ax.set_yticks(range(n_cells))
    ax.set_yticklabels([f'({p},{q},{e})' for p, q, e in cells], fontsize=7)
    ax.set_xlabel('channel')
    ax.set_ylabel('(p, q, e)')
    for i in range(n_cells):
        for j in range(n_channels):
            s = grid[i, j]
            txt = f'{s:.3f}' if s not in (0.0, 1.0) else f'{s:.0f}'
            color = 'white' if s < 0.5 else 'black'
            ax.text(j, i, txt, ha='center', va='center',
                    fontsize=6, color=color)
    cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cbar.set_label('strength', fontsize=9)
    ax.set_title(f'{run_name}: channel × cell verdicts', fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'verdict_matrix.png'),
                bbox_inches='tight')
    plt.close(fig)


def figure_column_diff(figures_dir: str,
                        cells: List[Tuple[int, int, int]],
                        cols_post: Dict[Tuple[int, int, int], np.ndarray],
                        run_name: str, H_max: int) -> None:
    n_cells = len(cells)
    diff = np.zeros((n_cells, H_max), dtype=np.float64)
    for i, (p, q, e) in enumerate(cells):
        pred = algebra_column(p, q, e, H_max)
        diff[i, :] = np.abs(cols_post[(p, q, e)] - pred)

    floor = max(diff.max() * 1e-30, 1e-30)
    log_diff = np.log10(np.maximum(diff, floor))
    vmax = max(float(log_diff.max()), -12.0)
    vmin = -16.0

    fig, ax = plt.subplots(figsize=(8, 6), dpi=150, facecolor='white')
    im = ax.imshow(log_diff, aspect='auto', cmap='inferno',
                   vmin=vmin, vmax=vmax, interpolation='nearest')
    ax.set_xticks(range(H_max))
    ax.set_xticklabels([str(h) for h in range(1, H_max + 1)], fontsize=8)
    ax.set_yticks(range(n_cells))
    ax.set_yticklabels([f'({p},{q},{e})' for p, q, e in cells], fontsize=7)
    ax.set_xlabel('h')
    ax.set_ylabel('(p, q, e)')
    cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cbar.set_label('log10 |col_post - algebra(p, q^e, h)|', fontsize=9)
    pct_exact = float(100.0 * (diff == 0).sum() / diff.size)
    pct_at_tol = float(100.0 * (diff < 1e-12).sum() / diff.size)
    ax.set_title(f'{run_name}: column vs algebra '
                 f'({pct_exact:.2f}% exact, {pct_at_tol:.2f}% < TOL)',
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(figures_dir, 'column_diff.png'),
                bbox_inches='tight')
    plt.close(fig)


def figure_cliff_signature(figures_dir: str,
                            cells: List[Tuple[int, int, int]],
                            cols_post: Dict[Tuple[int, int, int], np.ndarray],
                            run_name: str, H_max: int) -> None:
    """Per cell, the column itself plotted vs h, with the cliff at h=e+1
    marked by a vertical line. The marvel observable: non-zero left of
    cliff, exact zero right of it (under identity)."""
    n_cells = len(cells)
    n_cols = 4
    n_rows = (n_cells + n_cols - 1) // n_cols
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, 2.5 * n_rows),
                              dpi=150, facecolor='white')
    axes = np.atleast_2d(axes).reshape(n_rows, n_cols)
    h_axis = np.arange(1, H_max + 1)
    for i, (p, q, e) in enumerate(cells):
        r, c = divmod(i, n_cols)
        ax = axes[r, c]
        col = cols_post[(p, q, e)]
        ax.axhline(0.0, color='gray', lw=0.5)
        ax.axvline(e + 0.5, color='red', lw=1.0, linestyle='--',
                   label=f'cliff at h={e+1}')
        ax.plot(h_axis, col, 'o-', ms=4, color='C0')
        ax.set_title(f'(p={p}, q={q}, e={e}, Ω={e})', fontsize=8)
        ax.set_xlabel('h', fontsize=7)
        ax.set_ylabel('col[h-1]', fontsize=7)
        ax.set_xticks(h_axis)
        ax.tick_params(axis='both', labelsize=6)
        ax.grid(True, alpha=0.2)
        ax.legend(loc='best', fontsize=6)
    # Hide unused axes.
    for j in range(n_cells, n_rows * n_cols):
        r, c = divmod(j, n_cols)
        axes[r, c].set_axis_off()
    fig.suptitle(f'{run_name}: cliff signatures', fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(os.path.join(figures_dir, 'cliff_signature.png'),
                bbox_inches='tight')
    plt.close(fig)


def make_figures(figures_dir: str, config: dict,
                  cells: List[Tuple[int, int, int]], results: dict,
                  cols_post: Dict[Tuple[int, int, int], np.ndarray]) -> None:
    H_max = int(config.get('H_max', DEFAULT_H_MAX))
    run_name = os.path.basename(os.path.dirname(figures_dir))
    sub = config.get('substrate')
    figure_verdict_matrix(figures_dir, cells, results, run_name)
    if sub == 'algebra':
        figure_column_diff(figures_dir, cells, cols_post, run_name, H_max)
        figure_cliff_signature(figures_dir, cells, cols_post, run_name, H_max)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def calibration_runs() -> List[Tuple[str, dict]]:
    date = datetime.now().strftime('%Y-%m-%d')
    return [
        (f'{date}_identity', {
            'substrate': 'algebra', 'transducer': 'identity',
            'primes': list(DEFAULT_PRIMES),
            'exponents': list(DEFAULT_EXPONENTS),
            'H_max': DEFAULT_H_MAX}),
        (f'{date}_scale_2x', {
            'substrate': 'algebra', 'transducer': 'scale_2x',
            'primes': list(DEFAULT_PRIMES),
            'exponents': list(DEFAULT_EXPONENTS),
            'H_max': DEFAULT_H_MAX}),
        (f'{date}_null', {
            'substrate': 'synth_uniform', 'transducer': 'identity',
            'primes': list(DEFAULT_PRIMES),
            'exponents': list(DEFAULT_EXPONENTS),
            'H_max': DEFAULT_H_MAX, 'seed': 0}),
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
