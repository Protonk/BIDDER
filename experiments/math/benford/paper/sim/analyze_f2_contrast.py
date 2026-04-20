"""
Analysis for F2-CONTRAST-SIM.

Combines:
- torus L1 hit-time ratios r = n_alt / n_full at matched thresholds
- tree drift estimates and the implied time ratio

Run: sage -python analyze_f2_contrast.py
"""

import math
import os

import numpy as np


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(SIM_DIR, "f2_contrast_results")
TORUS_DIR = os.path.join(BASE_DIR, "torus")
TREE_DIR = os.path.join(BASE_DIR, "tree")

L = 31
M = L * L
N_VALUES = [10**5, 10**6, 10**7]
K_VALUES = [5.0, 3.0, 2.0, 1.2]
TREE_FIT_MIN = 100


def theta_N(N):
    return math.sqrt(2.0 * M / (math.pi * N))


def first_crossing(sample_times, values, threshold):
    idx = np.where(values < threshold)[0]
    if idx.size == 0:
        return None
    return int(sample_times[idx[0]])


def load_torus():
    out = {}
    for N in N_VALUES:
        log_N = int(round(math.log10(N)))
        for walk in ["full", "alt"]:
            path = os.path.join(TORUS_DIR, f"{walk}_N1e{log_N}.npz")
            out[(walk, N)] = np.load(path)
    return out


def fit_slope(times, values, fit_min):
    mask = times >= fit_min
    x = times[mask].astype(np.float64)
    y = values[mask].astype(np.float64)
    x_centered = x - x.mean()
    slope = float(np.dot(x_centered, y - y.mean()) / np.dot(x_centered, x_centered))
    return slope


def main():
    torus = load_torus()

    print("=== Torus ratios: r = n_alt / n_full ===")
    ratio_table = {}
    save_dict = {}
    for N in N_VALUES:
        print(f"\nN = {N:_}  theta_N = {theta_N(N):.4e}")
        print("  k    theta_k      n_full   n_alt    r")
        for k in K_VALUES:
            theta = k * theta_N(N)
            d_full = torus[("full", N)]
            d_alt = torus[("alt", N)]
            n_full = first_crossing(d_full["sample_times"], d_full["l1"], theta)
            n_alt = first_crossing(d_alt["sample_times"], d_alt["l1"], theta)
            if n_full is None or n_alt is None:
                r = None
                r_str = "CENS"
            else:
                r = n_alt / n_full
                r_str = f"{r:.3f}"
                ratio_table[(N, k)] = r
                key = f"torus_N1e{int(round(math.log10(N)))}_k{k}"
                save_dict[f"{key}_n_full"] = float(n_full)
                save_dict[f"{key}_n_alt"] = float(n_alt)
                save_dict[f"{key}_ratio"] = float(r)
            print(f"  {k:3.1f}  {theta:.4e}  {str(n_full):>7s}  {str(n_alt):>6s}  {r_str:>5s}")

    print("\n=== Torus cross-N stability ===")
    for k in K_VALUES:
        rs = [(N, ratio_table[(N, k)]) for N in N_VALUES if (N, k) in ratio_table]
        if not rs:
            continue
        vals = [r for _, r in rs]
        spread = max(vals) / min(vals)
        print(
            f"  k={k:.1f}: "
            + "  ".join(f"N=1e{int(round(math.log10(N)))}->{r:.3f}" for N, r in rs)
            + f"  max/min={spread:.3f}"
        )

    tree_full = np.load(os.path.join(TREE_DIR, "full_tree.npz"))
    tree_alt = np.load(os.path.join(TREE_DIR, "alt_tree.npz"))
    slope_full = fit_slope(tree_full["sample_times"], tree_full["mean_len"], TREE_FIT_MIN)
    slope_alt = fit_slope(tree_alt["sample_times"], tree_alt["mean_len"], TREE_FIT_MIN)
    tree_ratio = slope_full / slope_alt

    print("\n=== Tree drift check ===")
    print(f"  slope_full ~= {slope_full:.5f}")
    print(f"  slope_alt  ~= {slope_alt:.5f}")
    print(f"  implied time ratio r = drift_full / drift_alt ~= {tree_ratio:.5f}")

    save_dict["tree_slope_full"] = slope_full
    save_dict["tree_slope_alt"] = slope_alt
    save_dict["tree_ratio_r"] = tree_ratio

    out_path = os.path.join(BASE_DIR, "analysis.npz")
    np.savez_compressed(out_path, **save_dict)
    print(f"\n-> {out_path}")


if __name__ == "__main__":
    main()
