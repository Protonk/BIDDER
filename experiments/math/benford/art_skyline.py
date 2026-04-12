"""
art_skyline.py — The ε skyline.

Each demo rendered as a nighttime city across water. Each building is
one walker: x position is its final mantissa, height is log10|x|.
Brightness encodes leading-digit-1 time fraction. The reflection is
the theoretical 1/x density, mirrored and blurred.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from common import (
    BG, FG, SPINE,
    BENFORD_BOUNDARIES_BASE10,
    experiment_path, load_checkpoints, log_mantissa,
    save_figure,
)


DEMOS = [
    ('bs12_walk', 'BS(1,2) walk'),
    ('pure_add', 'pure add'),
]

N_BUILDINGS = 600
SEED = 42
BUILDING_WIDTH = 0.0012
WATER_ALPHA = 0.3
WATER_BLUR_STEPS = 8


def draw_skyline(ax, mantissa, height, brightness, title, color_base):
    ax.set_facecolor(BG)

    h_max = max(height.max(), 1.0)
    h_norm = height / h_max

    sort_idx = np.argsort(-height)
    mantissa = mantissa[sort_idx]
    h_norm = h_norm[sort_idx]
    height = height[sort_idx]
    brightness = brightness[sort_idx]

    for i in range(len(mantissa)):
        m = mantissa[i]
        h = h_norm[i]
        b = brightness[i]

        r, g, bl = color_base
        lum = 0.15 + 0.85 * b
        c = (r * lum, g * lum, bl * lum)

        bld_h = h * 0.45
        ax.add_patch(Rectangle(
            (m - BUILDING_WIDTH / 2, 0), BUILDING_WIDTH, bld_h,
            facecolor=c, edgecolor='none', alpha=0.85,
            zorder=2,
        ))

        window_count = max(1, int(bld_h * 30))
        if b > 0.25:
            wy = np.linspace(bld_h * 0.05, bld_h * 0.95, window_count)
            for y in wy:
                wx = m + np.random.uniform(-BUILDING_WIDTH * 0.3,
                                           BUILDING_WIDTH * 0.3)
                ws = BUILDING_WIDTH * 0.15
                if np.random.random() < b:
                    ax.add_patch(Rectangle(
                        (wx - ws/2, y - ws/2), ws, ws,
                        facecolor=(1.0, 0.95, 0.7, 0.6 * b),
                        edgecolor='none', zorder=3,
                    ))

        # reflection
        for blur in range(WATER_BLUR_STEPS):
            frac = (blur + 1) / WATER_BLUR_STEPS
            ref_h = bld_h * (1.0 - frac * 0.6)
            ref_alpha = 0.12 * (1.0 - frac)
            jitter = np.random.uniform(-0.002, 0.002)
            ax.add_patch(Rectangle(
                (m - BUILDING_WIDTH / 2 + jitter, -ref_h),
                BUILDING_WIDTH, ref_h,
                facecolor=c, edgecolor='none', alpha=ref_alpha,
                zorder=1,
            ))

    # waterline
    ax.axhline(0, color='#334455', linewidth=0.8, zorder=5, alpha=0.6)

    # 1/x reference in reflection zone
    x_ref = np.linspace(0.01, 0.99, 300)
    ref_curve = -0.08 / (x_ref * np.log(1.0 / 0.01))
    ref_curve = ref_curve / abs(ref_curve.min()) * 0.15
    ax.plot(x_ref, ref_curve, color='#ff6f61', linewidth=1.0, alpha=0.5,
            zorder=6, linestyle='--')

    ax.set_xlim(-0.02, 1.02)
    sky_top = 0.55
    water_bottom = -0.2
    ax.set_ylim(water_bottom, sky_top)
    ax.set_xticks([0.0, 0.301, 0.5, 1.0])
    ax.set_xticklabels(['0', 'log₁₀2', '0.5', '1'])
    ax.set_yticks([])
    ax.set_xlabel('mantissa', color=FG, fontsize=10)
    ax.set_title(title, color=FG, fontsize=14, pad=12)

    for spine in ax.spines.values():
        spine.set_color(SPINE)
    ax.tick_params(colors=FG)


def main():
    rng = np.random.default_rng(SEED)

    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    fig.patch.set_facecolor(BG)

    colors = [(0.42, 0.78, 1.0), (1.0, 0.80, 0.35)]

    for ax, (name, title), color_base in zip(axes, DEMOS, colors):
        ckpts = load_checkpoints(experiment_path(f'data_{name}.npz'))

        if 'final_logx' in ckpts:
            logx = ckpts['final_logx']
            mantissa_vals = np.mod(logx, 1.0)
            height_vals = np.abs(logx)
        else:
            abs_x = ckpts['final_abs_x']
            abs_x = np.maximum(abs_x, 1e-15)
            mantissa_vals = log_mantissa(abs_x, 10.0)
            height_vals = np.log10(abs_x)
            height_vals = np.abs(height_vals)

        leading_1_boundary = float(BENFORD_BOUNDARIES_BASE10[1])
        is_digit_1 = mantissa_vals < leading_1_boundary

        all_hist = ckpts['log_mantissa_hist'].astype(np.float64)
        K = all_hist.shape[0]
        # approximate per-walker digit-1 fraction as ensemble stat
        digit_1_timeseries = np.array([
            float(np.sum(all_hist[k, :int(leading_1_boundary * 256)]))
            for k in range(K)
        ])
        mean_d1_frac = float(digit_1_timeseries.mean())

        # subsample walkers
        n_total = len(mantissa_vals)
        idx = rng.choice(n_total, size=min(N_BUILDINGS, n_total), replace=False)
        m_sub = mantissa_vals[idx]
        h_sub = height_vals[idx]
        # brightness: jitter around mean digit-1 fraction with per-walker noise
        b_sub = np.clip(
            mean_d1_frac + rng.normal(0, 0.08, size=len(idx)),
            0.05, 1.0,
        )

        draw_skyline(ax, m_sub, h_sub, b_sub, title, color_base)

    plt.tight_layout(pad=3.0)
    save_figure(fig, experiment_path('art_skyline.png'))


if __name__ == '__main__':
    main()
