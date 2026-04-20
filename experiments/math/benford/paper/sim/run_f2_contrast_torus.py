"""
Torus contrast for F2-CONTRAST-SIM.

Odd-L torus on Z/L x Z/L, comparing the full nearest-neighbor walk
against a forced alternating x/y walk. Saves L1-to-uniform traces at
matched walker counts for the cross-group contrast with BS(1,2).

Run: sage -python run_f2_contrast_torus.py
"""

import math
import os
import time

import numpy as np


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SIM_DIR, "f2_contrast_results", "torus")
os.makedirs(OUT_DIR, exist_ok=True)


L = 31
M = L * L
N_VALUES = [10**5, 10**6, 10**7]
N_MAX = 2000
SAMPLE_TIMES = np.arange(10, N_MAX + 1, 10, dtype=np.int32)

SEED_BASE = 0xF2C0A57
WALK_IDX = {"full": 0, "alt": 1}

DX_LUT = np.array([1, -1, 0, 0], dtype=np.int16)
DY_LUT = np.array([0, 0, 1, -1], dtype=np.int16)
STEP_LUT = np.array([1, -1], dtype=np.int16)


def compute_seed(walk, N):
    log_N = int(round(math.log10(N)))
    return SEED_BASE + WALK_IDX[walk] * 10**6 + log_N * 10**4


def initialize(n):
    return np.zeros(n, dtype=np.int16), np.zeros(n, dtype=np.int16)


def step_full(x, y, rng):
    choice = rng.integers(0, 4, size=x.shape[0], dtype=np.int8)
    np.add(x, DX_LUT[choice], out=x, casting="unsafe")
    np.add(y, DY_LUT[choice], out=y, casting="unsafe")
    np.remainder(x, L, out=x)
    np.remainder(y, L, out=y)


def step_alternating(x, y, rng, step_index):
    choice = rng.integers(0, 2, size=x.shape[0], dtype=np.int8)
    delta = STEP_LUT[choice]
    if step_index % 2 == 1:
        np.add(x, delta, out=x, casting="unsafe")
        np.remainder(x, L, out=x)
    else:
        np.add(y, delta, out=y, casting="unsafe")
        np.remainder(y, L, out=y)


def compute_l1(x, y):
    cells = x * L + y
    hist = np.bincount(cells, minlength=M)
    freq = hist.astype(np.float64) / x.shape[0]
    return float(np.sum(np.abs(freq - 1.0 / M)))


def run_walk(walk, N):
    seed = compute_seed(walk, N)
    out_path = os.path.join(OUT_DIR, f"{walk}_N1e{int(round(math.log10(N)))}.npz")

    print(f"\n=== torus {walk}  N={N:_}  seed={seed} ===")
    rng = np.random.default_rng(seed)
    x, y = initialize(N)
    l1_arr = np.zeros(SAMPLE_TIMES.size, dtype=np.float64)
    sample_idx = 0
    t0 = time.time()

    for step in range(1, N_MAX + 1):
        if walk == "full":
            step_full(x, y, rng)
        else:
            step_alternating(x, y, rng, step)

        if step == int(SAMPLE_TIMES[sample_idx]):
            l1_arr[sample_idx] = compute_l1(x, y)
            if sample_idx % max(1, SAMPLE_TIMES.size // 8) == 0 or step == N_MAX:
                dt = time.time() - t0
                print(
                    f"  n={step:4d}  L1={l1_arr[sample_idx]:.4e}  "
                    f"({step / max(dt, 1e-9):.1f} s/s)",
                    flush=True,
                )
            sample_idx += 1

    wall = time.time() - t0
    print(f"  wall: {wall:.1f}s")

    np.savez_compressed(
        out_path,
        sample_times=SAMPLE_TIMES,
        l1=l1_arr,
        meta_L=np.int32(L),
        meta_M=np.int32(M),
        meta_N=np.int64(N),
        meta_steps=np.int32(N_MAX),
        meta_seed=np.int64(seed),
        meta_walk=np.str_(walk),
    )
    print(f"  -> {out_path}")


def main():
    print("F2 contrast torus run")
    print(f"  L={L}, M={M}, N_MAX={N_MAX}")
    print(f"  N values={N_VALUES}")
    for N in N_VALUES:
        run_walk("full", N)
        run_walk("alt", N)
    print("\n=== F2 torus contrast complete ===")


if __name__ == "__main__":
    main()
