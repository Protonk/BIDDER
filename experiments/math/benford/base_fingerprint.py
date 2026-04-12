"""
Base fingerprint: L1-to-uniform of log_b mantissa as base varies.

Sweeps b continuously over [2, 40] on the final-step ensembles from
pure_add (the non-converging flow) and bs12_walk (the converging flow).
bs12_walk is flat across every base in the scan, which is the real
"base-agnostic Benford" signature. pure_add rises monotonically with
base, because its terminal |x| sits in a narrow band whose log_b width
shrinks as b grows; this is a trivial ensemble-width artifact, not a
resonance at any particular base.
"""

import numpy as np
import matplotlib.pyplot as plt

from common import (
    BG, BLUE, FG, GREEN, RED, SPINE, YELLOW,
    experiment_path,
    l1_to_uniform,
    load_checkpoints,
    log_mantissa,
    save_figure,
    setup_dark_axes,
)


DEMOS = [
    ('pure_add', 'pure add', YELLOW),
    ('bs12_walk', 'BS(1,2) walk', BLUE),
    ('bs12_biased', 'BS(1,2) biased (0.2, 0.2, 0.4, 0.2)', GREEN),
]

BASES = np.linspace(2.0, 40.0, 381)
BINS = 64


def fingerprint_curve(abs_x, bases, bins):
    out = np.zeros(len(bases), dtype=np.float64)
    for i, b in enumerate(bases):
        mantissa = log_mantissa(abs_x, base=float(b))
        hist, _ = np.histogram(mantissa, bins=bins, range=(0.0, 1.0))
        total = hist.sum()
        if total == 0:
            continue
        out[i] = l1_to_uniform(hist.astype(np.float64) / total)
    return out


def fingerprint_curve_logx(logx, bases, bins):
    """Compute L1-to-uniform across bases from pre-computed log10|x|."""
    out = np.zeros(len(bases), dtype=np.float64)
    for i, b in enumerate(bases):
        mantissa = np.mod(logx / np.log10(b), 1.0)
        hist, _ = np.histogram(mantissa, bins=bins, range=(0.0, 1.0))
        total = hist.sum()
        if total == 0:
            continue
        out[i] = l1_to_uniform(hist.astype(np.float64) / total)
    return out


def main():
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor(BG)
    setup_dark_axes(ax)

    curves = {}
    for name, label, color in DEMOS:
        ckpts = load_checkpoints(experiment_path(f'data_{name}.npz'))
        if 'final_logx' in ckpts:
            curve = fingerprint_curve_logx(ckpts['final_logx'], BASES, BINS)
        else:
            abs_x = ckpts['final_abs_x']
            abs_x = abs_x[abs_x > 0.0]
            curve = fingerprint_curve(abs_x, BASES, BINS)
        curves[name] = curve
        ax.plot(BASES, curve, color=color, linewidth=2.0, label=label)

    for b_int in range(2, 41):
        ax.axvline(b_int, color='#1a1a1a', linewidth=0.5, alpha=0.8)
    ax.axvline(10, color=RED, linestyle='--', linewidth=1.0, alpha=0.6)
    ax.text(
        10.15, 0.02, 'b=10',
        color=RED, fontsize=9, va='bottom',
        transform=ax.get_xaxis_transform(),
    )

    ax.text(
        0.35, 0.92,
        'bs12_walk: flat everywhere  (base-agnostic)\n'
        'pure_add: monotonic rise  (log_b width shrinks with b)',
        color=FG, fontsize=10, va='top', ha='left',
        transform=ax.transAxes,
    )

    ax.set_xlim(2.0, 40.0)
    ax.set_ylim(bottom=0.0)
    ax.set_xlabel('base b')
    ax.set_ylabel('L1 to uniform  (log_b mantissa, 64 bins)')
    ax.set_title('Base fingerprint of final-step ensembles',
                 color=FG, fontsize=13)
    ax.grid(color='#222', linewidth=0.6, alpha=0.6)

    leg = ax.legend(loc='upper right', facecolor='#111', edgecolor=SPINE)
    for text in leg.get_texts():
        text.set_color(FG)

    plt.tight_layout()
    save_figure(fig, experiment_path('base_fingerprint.png'))


if __name__ == '__main__':
    main()
