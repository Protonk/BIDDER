"""
Shared runner and plotting helpers for the Benford migration experiments.

These scripts run with `sage -python` so numpy and matplotlib are
available without additional packaging.
"""

import os
import sys

import numpy as np
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt


HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
CORE = os.path.join(ROOT, 'core')
GENERATOR = os.path.join(ROOT, 'generator')
DIST = os.path.join(ROOT, 'dist')

for path in (CORE, GENERATOR):
    if path not in sys.path:
        sys.path.insert(0, path)

# BIDDER cipher for experiment randomness — prefer C path, fall back
# to pure Python, fall back to None (numpy-only mode).
try:
    sys.path.insert(0, DIST)
    try:
        import bidder_c as _bidder
    except ImportError:
        import bidder as _bidder
except ImportError:
    _bidder = None
finally:
    if DIST in sys.path:
        sys.path.remove(DIST)

HAVE_BIDDER = _bidder is not None


SEED = 0xB1DDE12
N_WALKERS = 20_000
TARGET_CHECKPOINTS = 200
LOG_MANTISSA_BINS = 256

BG = '#0a0a0a'
FG = 'white'
SPINE = '#333'
YELLOW = '#ffcc5c'
BLUE = '#6ec6ff'
RED = '#ff6f61'
GREEN = '#88d8b0'
CMAP = plt.cm.plasma

BENFORD_PROBS_BASE10 = np.log10(1.0 + 1.0 / np.arange(1, 10))
BENFORD_1 = float(BENFORD_PROBS_BASE10[0])
BENFORD_BOUNDARIES_BASE10 = np.log10(np.arange(1, 11, dtype=np.float64))


def experiment_path(*parts):
    return os.path.join(HERE, *parts)


def data_path(name):
    return experiment_path(f'data_{name}.npz')


def png_path(name):
    return experiment_path(f'{name}.png')


def _initial_array(initial):
    if np.isscalar(initial):
        return np.full(N_WALKERS, float(initial), dtype=np.float64)
    arr = np.asarray(initial, dtype=np.float64)
    if arr.shape != (N_WALKERS,):
        raise ValueError(f"initial array must have shape ({N_WALKERS},), got {arr.shape}")
    return arr.copy()


def ensure_finite_nonzero(x, context):
    if not np.all(np.isfinite(x)):
        raise FloatingPointError(f'{context}: encountered non-finite values')
    if np.any(x == 0.0):
        raise FloatingPointError(f'{context}: encountered exact zero')


def log_mantissa(x, base=10.0):
    """Return log_base(|x|) mod 1."""
    base = float(base)
    if base <= 1.0:
        raise ValueError(f'base must be > 1, got {base}')
    abs_x = np.abs(np.asarray(x, dtype=np.float64))
    if np.any(abs_x <= 0.0):
        raise ValueError('log_mantissa requires strictly non-zero inputs')
    frac = np.log(abs_x) / np.log(base)
    return np.mod(frac, 1.0)


def leading_digit(x, base=10):
    """Return the leading digit of |x| in an integer base."""
    base_int = int(base)
    if base_int != base or base_int < 2:
        raise ValueError(f'leading_digit requires integer base >= 2, got {base}')
    frac = log_mantissa(x, float(base_int))
    digits = np.floor(np.power(float(base_int), frac) + 1e-12).astype(np.int64)
    return np.clip(digits, 1, base_int - 1)


def l1_to_uniform(hist):
    hist = np.asarray(hist, dtype=np.float64)
    return float(np.abs(hist - (1.0 / hist.size)).sum())


def _mantissa_hist(mantissa, bins):
    hist, _ = np.histogram(mantissa, bins=bins, range=(0.0, 1.0))
    hist = hist.astype(np.float64)
    hist /= hist.sum()
    return hist


def add_uniform(lo, hi):
    lo = float(lo)
    hi = float(hi)

    def step_fn(rng, x, n_steps):
        if n_steps <= 0:
            return x
        if n_steps == 1:
            return x + rng.uniform(lo, hi, size=x.size)
        increments = rng.uniform(lo, hi, size=(n_steps, x.size)).sum(axis=0)
        return x + increments

    return step_fn


def add_constant(c):
    c = float(c)

    def step_fn(rng, x, n_steps):
        return x + (c * n_steps)

    return step_fn


def mul_constant(r):
    r = float(r)

    def step_fn(rng, x, n_steps):
        if n_steps <= 0:
            return x
        return x * (r ** n_steps)

    return step_fn


def bs12_step():
    def step_fn(rng, x, n_steps):
        x = x.copy()
        for _ in range(n_steps):
            choice = rng.integers(0, 4, size=x.size)
            plus = choice == 0
            minus = choice == 1
            mul = choice == 2
            div = choice == 3
            x[plus] += 1.0
            x[minus] -= 1.0
            x[mul] *= 2.0
            x[div] *= 0.5
        return x

    return step_fn


def bs12_step_biased(p_plus, p_minus, p_mul, p_div):
    probs = np.asarray([p_plus, p_minus, p_mul, p_div], dtype=np.float64)
    if abs(probs.sum() - 1.0) > 1e-12:
        raise ValueError(f'probabilities must sum to 1, got {probs.sum()}')

    def step_fn(rng, x, n_steps):
        x = x.copy()
        for _ in range(n_steps):
            choice = rng.choice(4, size=x.size, p=probs)
            plus = choice == 0
            minus = choice == 1
            mul = choice == 2
            div = choice == 3
            x[plus] += 1.0
            x[minus] -= 1.0
            x[mul] *= 2.0
            x[div] *= 0.5
        return x

    return step_fn


def bidder_choices(n_walkers, n_steps, name='bs12'):
    """Pre-generate a (n_steps, n_walkers) int8 choice array using
    one BidderBlock per walker. Returns choices in {0, 1, 2, 3}.
    Requires HAVE_BIDDER."""
    if _bidder is None:
        raise RuntimeError('bidder not available')
    choices = np.empty((n_steps, n_walkers), dtype=np.int8)
    for w in range(n_walkers):
        B = _bidder.cipher(period=n_steps, key=f'{name}:w{w}'.encode())
        raw = np.array(list(B), dtype=np.int64)
        choices[:, w] = (raw % 4).astype(np.int8)
        if (w + 1) % 5000 == 0:
            print(f'  bidder choices: {w+1}/{n_walkers}')
    return choices


def bidder_increments(n_walkers, n_steps, lo, hi, name='add'):
    """Pre-generate a (n_steps, n_walkers) float64 increment array
    using one BidderBlock per walker. Maps [0, period) to [lo, hi).
    Requires HAVE_BIDDER."""
    if _bidder is None:
        raise RuntimeError('bidder not available')
    lo, hi = float(lo), float(hi)
    span = hi - lo
    increments = np.empty((n_steps, n_walkers), dtype=np.float64)
    for w in range(n_walkers):
        B = _bidder.cipher(period=n_steps, key=f'{name}:w{w}'.encode())
        raw = np.array(list(B), dtype=np.float64)
        increments[:, w] = lo + span * raw / n_steps
        if (w + 1) % 5000 == 0:
            print(f'  bidder increments: {w+1}/{n_walkers}')
    return increments


def make_step_from_choices(choices):
    """Wrap a pre-generated (n_steps, n_walkers) choice array into a
    step_fn compatible with run_schedule."""
    cursor = [0]

    def step_fn(rng, x, n_steps):
        x = x.copy()
        for s in range(n_steps):
            c = choices[cursor[0]]
            cursor[0] += 1
            plus = c == 0
            minus = c == 1
            mul = c == 2
            div = c == 3
            x[plus] += 1.0
            x[minus] -= 1.0
            x[mul] *= 2.0
            x[div] *= 0.5
        return x

    return step_fn


def make_step_from_increments(increments):
    """Wrap a pre-generated (n_steps, n_walkers) increment array into
    a step_fn compatible with run_schedule."""
    cursor = [0]

    def step_fn(rng, x, n_steps):
        chunk = increments[cursor[0]:cursor[0] + n_steps]
        cursor[0] += n_steps
        return x + chunk.sum(axis=0)

    return step_fn


def _schedule_summary(ops):
    return ', '.join(f'{count} x {name}' for name, count, _ in ops)


def run_schedule(ops, initial, target_checkpoints=TARGET_CHECKPOINTS, seed=SEED):
    """Run the schedule and record checkpoint histograms."""
    total_ops = sum(count for _, count, _ in ops)
    if total_ops <= 0:
        raise ValueError('schedule must contain at least one step')

    rng = np.random.default_rng(seed)
    x = _initial_array(initial)
    ensure_finite_nonzero(x, 'initial state')

    checkpoint_steps = np.unique(
        np.linspace(0, total_ops, target_checkpoints + 1, dtype=np.int64)
    )

    steps = []
    histograms = []
    l1_values = []
    leading1 = []

    def record(step_index):
        ensure_finite_nonzero(x, f'checkpoint {step_index}')
        mantissa = log_mantissa(x, 10.0)
        hist = _mantissa_hist(mantissa, LOG_MANTISSA_BINS)
        steps.append(step_index)
        histograms.append(hist.astype(np.float32))
        l1_values.append(np.float32(l1_to_uniform(hist)))
        leading1.append(np.float32(np.mean(mantissa < BENFORD_BOUNDARIES_BASE10[1])))

    record(0)
    checkpoint_idx = 1
    op_index = 0

    for _, count, step_fn in ops:
        remaining = int(count)
        while remaining > 0:
            target = int(checkpoint_steps[checkpoint_idx])
            chunk = min(remaining, target - op_index)
            x = step_fn(rng, x, chunk)
            op_index += chunk
            remaining -= chunk
            if op_index == target:
                record(op_index)
                checkpoint_idx += 1

    return {
        'step': np.asarray(steps, dtype=np.int64),
        'log_mantissa_hist': np.asarray(histograms, dtype=np.float32),
        'l1': np.asarray(l1_values, dtype=np.float32),
        'leading_1_frac': np.asarray(leading1, dtype=np.float32),
        'final_abs_x': np.abs(x).astype(np.float64),
        'schedule_summary': np.asarray(_schedule_summary(ops)),
    }


def save_checkpoints(path, ckpts):
    np.savez_compressed(path, **ckpts)


def load_checkpoints(path):
    with np.load(path, allow_pickle=False) as data:
        out = {key: data[key] for key in data.files}
    out['schedule_summary'] = str(out['schedule_summary'])
    return out


def setup_dark_axes(ax):
    ax.set_facecolor(BG)
    ax.tick_params(colors=FG)
    for spine in ax.spines.values():
        spine.set_color(SPINE)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    return ax


def save_figure(fig, out_path):
    fig.patch.set_facecolor(BG)
    fig.savefig(out_path, dpi=250, facecolor=BG, bbox_inches='tight')
    plt.close(fig)
    print(f'-> {os.path.basename(out_path)}')


def plot_demo_lines(ckpts, title, out_path):
    fig, ax1 = plt.subplots(figsize=(11, 6))
    fig.patch.set_facecolor(BG)
    setup_dark_axes(ax1)

    step = ckpts['step']
    safe_l1 = np.clip(ckpts['l1'].astype(np.float64), 1e-6, None)
    line1 = ax1.plot(
        step,
        safe_l1,
        color=YELLOW,
        linewidth=2.2,
        label='L1 to uniform log-mantissa',
    )[0]
    ax1.set_yscale('log')
    ax1.set_xlabel('op index')
    ax1.set_ylabel('L1 to uniform log-mantissa')

    ax2 = ax1.twinx()
    setup_dark_axes(ax2)
    ax2.patch.set_alpha(0.0)
    line2 = ax2.plot(
        step,
        ckpts['leading_1_frac'],
        color=BLUE,
        linewidth=2.0,
        label='fraction with leading digit 1',
    )[0]
    ref = ax2.axhline(
        BENFORD_1,
        color=GREEN,
        linestyle='--',
        linewidth=1.2,
        alpha=0.85,
        label='Benford P(1)',
    )
    ax2.set_ylabel('fraction with leading digit 1')
    ax2.set_ylim(0.0, 1.0)

    ax1.set_title(title, color=FG, fontsize=13)
    ax1.grid(color='#222', linewidth=0.6, alpha=0.6)

    handles = [line1, line2, ref]
    labels = [h.get_label() for h in handles]
    leg = ax1.legend(handles, labels, loc='upper right', facecolor='#111', edgecolor=SPINE)
    for text in leg.get_texts():
        text.set_color(FG)

    plt.tight_layout()
    save_figure(fig, out_path)


def base_histogram(abs_x, base, bins):
    mantissa = log_mantissa(abs_x, base)
    hist = _mantissa_hist(mantissa, bins)
    return mantissa, hist


def _digit_projection_matrix(n_bins):
    """Exact projection from a uniform log10-mantissa histogram (n_bins
    on [0, 1)) to a 9-entry first-digit histogram. Each row sums to 1;
    rows that straddle a log10(d) boundary split their mass proportionally."""
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    widths = edges[1:] - edges[:-1]
    digit_edges = np.log10(np.arange(1, 11, dtype=np.float64))
    matrix = np.zeros((n_bins, 9), dtype=np.float64)
    for d in range(9):
        lo = np.maximum(edges[:-1], digit_edges[d])
        hi = np.minimum(edges[1:], digit_edges[d + 1])
        overlap = np.clip(hi - lo, 0.0, None)
        matrix[:, d] = overlap / widths
    return matrix


DIGIT_PROJECTION_MATRIX = _digit_projection_matrix(LOG_MANTISSA_BINS)


def project_to_digit_hist(log_mantissa_hist):
    """Project (K, LOG_MANTISSA_BINS) base-10 log-mantissa histograms
    into (K, 9) first-digit histograms."""
    return np.asarray(log_mantissa_hist, dtype=np.float64) @ DIGIT_PROJECTION_MATRIX
