"""
Tree contrast for F2-CONTRAST-SIM.

The observable is word length only, so we simulate the exact length
process directly rather than storing reduced words:
- full walk: from length > 0, decrement with probability 1/4 and
  increment with probability 3/4; from 0, increment to 1.
- alternating walk: length is deterministic, |X_n| = n.

Run: sage -python run_f2_contrast_tree.py
"""

import math
import os
import time

import numpy as np


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SIM_DIR, "f2_contrast_results", "tree")
os.makedirs(OUT_DIR, exist_ok=True)


N = 10**5
N_MAX = 500
SAMPLE_TIMES = np.arange(1, N_MAX + 1, dtype=np.int32)

SEED_BASE = 0xF2C0BEE


def run_full():
    out_path = os.path.join(OUT_DIR, "full_tree.npz")
    rng = np.random.default_rng(SEED_BASE)
    lengths = np.zeros(N, dtype=np.int16)
    mean_arr = np.zeros(SAMPLE_TIMES.size, dtype=np.float64)
    std_arr = np.zeros(SAMPLE_TIMES.size, dtype=np.float64)
    t0 = time.time()

    print(f"\n=== tree full  N={N:_}  seed={SEED_BASE} ===")
    for step in range(1, N_MAX + 1):
        choice = rng.integers(0, 4, size=N, dtype=np.int8)
        decrement = (lengths > 0) & (choice == 0)
        lengths += 1
        lengths[decrement] -= 2
        mean_arr[step - 1] = float(lengths.mean())
        std_arr[step - 1] = float(lengths.std())
        if step % 100 == 0 or step == 1 or step == N_MAX:
            dt = time.time() - t0
            print(
                f"  n={step:4d}  mean={mean_arr[step - 1]:.4f}  "
                f"std={std_arr[step - 1]:.4f}  ({step / max(dt, 1e-9):.1f} s/s)",
                flush=True,
            )

    np.savez_compressed(
        out_path,
        sample_times=SAMPLE_TIMES,
        mean_len=mean_arr,
        std_len=std_arr,
        meta_N=np.int64(N),
        meta_steps=np.int32(N_MAX),
        meta_seed=np.int64(SEED_BASE),
        meta_walk=np.str_("full"),
    )
    print(f"  -> {out_path}")


def run_alt():
    out_path = os.path.join(OUT_DIR, "alt_tree.npz")
    mean_arr = SAMPLE_TIMES.astype(np.float64)
    std_arr = np.zeros(SAMPLE_TIMES.size, dtype=np.float64)
    print(f"\n=== tree alt  N={N:_}  deterministic ===")
    np.savez_compressed(
        out_path,
        sample_times=SAMPLE_TIMES,
        mean_len=mean_arr,
        std_len=std_arr,
        meta_N=np.int64(N),
        meta_steps=np.int32(N_MAX),
        meta_seed=np.int64(-1),
        meta_walk=np.str_("alt"),
    )
    print(f"  -> {out_path}")


def main():
    print("F2 contrast tree run")
    print(f"  N={N}, N_MAX={N_MAX}")
    run_full()
    run_alt()
    print("\n=== F2 tree contrast complete ===")


if __name__ == "__main__":
    main()
