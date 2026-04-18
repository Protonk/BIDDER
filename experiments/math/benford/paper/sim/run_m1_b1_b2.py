"""
M1 + B1 + B2 consolidated run.

Single simulation producing data for all three sim plans at once:
- ALGEBRAIC M1: L₁(n) dense sampling over [1, 200] and coarse [205, 600]
  for D1 (slope ratio), D2 (linearization), and A4 (fit comparison).
- BENTHIC B1: ensemble Fourier coefficients ĥ(r, n) for r = 1..5,
  per-walker return count at checkpoint times, conditional Fourier
  coefficients by return count.
- BENTHIC B2: in-R vs out-of-R Fourier split at each sample time,
  before-vs-after comparison of ĉ_R.
- S0 input: per-walker return count histogram at {100, 200, 500} for
  ML index post-processing.
- A4c / A1b input: ensemble ‖h‖_{L²} = √(Σ|ĥ(r)|²) for cross-norm
  slope comparison with L₁.

Walker state: (m, E, sign) per walker. m ∈ [0, 1) float64, E int32,
sign ∈ {−1, +1} int8. Three-case b-step: frozen for |E| > 20, snap
to (0, 0) for E < −20, direct float64 computation for |E| ≤ 20.

IC: all walkers start at x = √2 (m = log₁₀√2, E = 0, sign = +1). This
makes x = 0 algebraically impossible under the generator action — the
orbit lies in {2^k · √2 + j : k, j ∈ ℤ}, which excludes 0 by
irrationality of √2 — so no defensive zero-snap is needed.

Active zone R for return counting is {|E| ≤ E_R = 3}, separate from the
computational threshold E_THRESH = 20. We track both the number of
0→1 entries into R (return_counts, for S0/ML-index analysis) and the
cumulative occupation time in R (time_in_R, for diagnostics).

Run: sage -python run_m1_b1_b2.py
"""

import math
import os
import time
import numpy as np


# --- Config -----------------------------------------------------------

N_WALKERS = 10**8          # override to 10**5 for smoke test
N_STEPS = 600
N_BINS = 1000              # L₁ histogram bins on T = [0, 1)
SEED = 0xBADC0DE1

E_THRESH = 20              # computational threshold for frozen/snap
E_R = 3                    # active zone R = {|E| ≤ E_R}

MODES = np.array([1, 2, 3, 4, 5], dtype=np.int32)

# Checkpoints where we compute conditional Fourier by return count
# and save per-walker N_n histogram.
CHECKPOINTS = np.array([25, 50, 100, 150, 200, 300, 500], dtype=np.int32)

# Sample times: every step from 1 to 200, every 5 from 205 to 600.
SAMPLE_TIMES = np.concatenate([
    np.arange(1, 201, dtype=np.int32),
    np.arange(205, 601, 5, dtype=np.int32),
])

# Fourier batching to cap temporary memory
FOURIER_BATCH = 10**7

# Minimum bin size for conditional Fourier coefficients
COND_MIN_BIN = 1000

LOG10_2 = math.log10(2.0)
LOG10_SQRT2 = 0.5 * LOG10_2      # initial m = log₁₀(√2)


# --- Output path ------------------------------------------------------

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(SIM_DIR, 'm1_b1_b2_results.npz')


# --- State helpers ----------------------------------------------------

def initialize(n):
    """All walkers at x = +√2: m = log₁₀(√2), E = 0, sign = +1.
    Choice of √2 (irrational) keeps the orbit in {2^k·√2 + j} and
    therefore away from 0 under the generator action."""
    m = np.full(n, LOG10_SQRT2, dtype=np.float64)
    E = np.zeros(n, dtype=np.int32)
    sign = np.ones(n, dtype=np.int8)
    return m, E, sign


def step_a(m, E, mask):
    """a-step (multiply by 2): m ← m + log10(2) mod 1, E ← E + carry."""
    if not mask.any():
        return
    idx = np.where(mask)[0]
    m_new = m[idx] + LOG10_2
    carry = m_new >= 1.0
    m[idx] = np.where(carry, m_new - 1.0, m_new)
    E[idx] += carry.astype(np.int32)


def step_a_inv(m, E, mask):
    """a⁻¹-step (divide by 2): m ← m − log10(2) mod 1, E ← E − borrow."""
    if not mask.any():
        return
    idx = np.where(mask)[0]
    m_new = m[idx] - LOG10_2
    borrow = m_new < 0.0
    m[idx] = np.where(borrow, m_new + 1.0, m_new)
    E[idx] -= borrow.astype(np.int32)


def step_b(m, E, sign, mask, delta):
    """b-step (delta=+1) or b⁻¹-step (delta=−1) on walkers in mask.
    Three cases: frozen (E > E_THRESH), snap (E < −E_THRESH), active."""
    if not mask.any():
        return

    idx = np.where(mask)[0]
    E_local = E[idx]

    frozen = E_local > E_THRESH
    snap = E_local < -E_THRESH
    active = ~(frozen | snap)

    # Snap: x ≈ 0 ± 1 = ±1 → (m=0, E=0, sign=sign(delta))
    snap_idx = idx[snap]
    if snap_idx.size > 0:
        m[snap_idx] = 0.0
        E[snap_idx] = 0
        sign[snap_idx] = np.int8(1 if delta > 0 else -1)

    # Frozen: no change

    # Active: compute in float64. x = 0 is algebraically impossible
    # from the √2 IC (orbit ⊂ {2^k·√2 + j}, k,j ∈ ℤ), so no zero guard.
    if active.any():
        act_idx = idx[active]
        log_mag = E[act_idx].astype(np.float64) + m[act_idx]
        x = sign[act_idx].astype(np.float64) * np.power(10.0, log_mag)
        x_new = x + float(delta)

        abs_x = np.abs(x_new)
        log_abs = np.log10(abs_x)
        new_E = np.floor(log_abs).astype(np.int32)
        new_m = log_abs - new_E.astype(np.float64)
        new_sign = np.where(x_new > 0.0, np.int8(1), np.int8(-1))

        m[act_idx] = new_m
        E[act_idx] = new_E
        sign[act_idx] = new_sign


def step_walkers(m, E, sign, rng):
    """Apply one symmetric-walk step to all walkers."""
    choice = rng.integers(0, 4, size=m.shape[0], dtype=np.int8)
    step_a(m, E, choice == 0)
    step_a_inv(m, E, choice == 1)
    step_b(m, E, sign, choice == 2, +1)
    step_b(m, E, sign, choice == 3, -1)


# --- Statistics -------------------------------------------------------

def compute_l1(m):
    """L₁ = Σ |freq_j/N − 1/B|. Matches common.py convention."""
    n = m.shape[0]
    hist, _ = np.histogram(m, bins=N_BINS, range=(0.0, 1.0))
    freq = hist.astype(np.float64) / n
    return float(np.sum(np.abs(freq - 1.0 / N_BINS)))


def compute_fourier(m_arr, modes):
    """Compute ĥ(r) = (1/N) Σ exp(-2πi·r·m) for each r in modes.
    Batched to cap temporary memory; within each batch, broadcasts
    over modes (R × chunk) to collapse the per-mode Python loop.
    Returns complex128 array of shape (len(modes),)."""
    n = m_arr.shape[0]
    R = modes.shape[0]
    if n == 0:
        return np.zeros(R, dtype=np.complex128)

    cos_sum = np.zeros(R, dtype=np.float64)
    sin_sum = np.zeros(R, dtype=np.float64)

    two_pi_modes = (2.0 * np.pi * modes.astype(np.float64))[:, None]

    for start in range(0, n, FOURIER_BATCH):
        end = min(start + FOURIER_BATCH, n)
        chunk = m_arr[start:end][None, :]           # shape (1, b)
        arg = two_pi_modes * chunk                  # shape (R, b)
        cos_sum += np.cos(arg).sum(axis=1)
        sin_sum -= np.sin(arg).sum(axis=1)          # e^{-iθ}

    cos_sum /= n
    sin_sum /= n
    return cos_sum + 1j * sin_sum


def compute_fourier_l2(fourier_coefs):
    """‖h‖_{L²} ≈ √(Σ_{r ≠ 0} |ĥ(r)|²). Over modes 1..5 only (truncated)."""
    return float(np.sqrt(np.sum(np.abs(fourier_coefs) ** 2)))


# --- Conditional Fourier at checkpoints ------------------------------

def checkpoint_conditional(m, return_counts, modes, min_bin):
    """For each k with ≥ min_bin walkers having return_counts = k,
    compute conditional Fourier coefficients. Returns list of
    (k, bin_size, fourier_coefs) tuples and the full histogram."""
    max_k = int(return_counts.max())
    counts_hist = np.bincount(return_counts, minlength=max_k + 1)

    result = []
    for k in range(max_k + 1):
        if counts_hist[k] >= min_bin:
            mask = return_counts == k
            m_bin = m[mask]
            fourier = compute_fourier(m_bin, modes)
            result.append((k, int(counts_hist[k]), fourier))
    return result, counts_hist


# --- Main loop --------------------------------------------------------

def main():
    print(f'M1+B1+B2 consolidated run')
    print(f'  N = {N_WALKERS:_}, steps = {N_STEPS}, B = {N_BINS}')
    print(f'  modes = {MODES.tolist()}, E_R = {E_R}, E_THRESH = {E_THRESH}')
    print(f'  sample times: {SAMPLE_TIMES.size}')
    print(f'  checkpoints: {CHECKPOINTS.tolist()}')
    print()

    rng = np.random.default_rng(SEED)

    # Initialize
    t0 = time.time()
    m, E, sign = initialize(N_WALKERS)
    print(f'init: {time.time()-t0:.2f}s, memory ~{(m.nbytes + E.nbytes + sign.nbytes) / 1e9:.2f} GB state')

    # Per-walker return bookkeeping.
    # return_counts[i] counts 0→1 transitions of (|E| ≤ E_R): the number
    #   of excursion entries into R. This is the N_n used by S0/MESSES.
    # time_in_R[i] counts total steps with |E| ≤ E_R: the occupation
    #   time, kept for diagnostics and the in-R Fourier normalization.
    # prev_in_R[i] tracks the previous step's membership for edge detection.
    return_counts = np.zeros(N_WALKERS, dtype=np.int32)
    time_in_R = np.zeros(N_WALKERS, dtype=np.int32)
    # IC (E=0) is in R with E_R ≥ 0, so walkers start inside.
    prev_in_R = np.ones(N_WALKERS, dtype=bool)

    # Recorded arrays per sample time
    n_sample = len(SAMPLE_TIMES)
    l1_arr = np.zeros(n_sample, dtype=np.float64)
    h_full = np.zeros((n_sample, len(MODES)), dtype=np.complex128)
    h_R = np.zeros((n_sample, len(MODES)), dtype=np.complex128)
    h_R_after = np.zeros((n_sample, len(MODES)), dtype=np.complex128)
    n_R_arr = np.zeros(n_sample, dtype=np.int64)
    l2_norm = np.zeros(n_sample, dtype=np.float64)

    # Conditional Fourier storage
    conditional_records = []      # list of (checkpoint_n, k, bin_size, fourier)
    return_counts_hists = {}      # checkpoint_n → histogram of return_counts
    time_in_R_hists = {}          # checkpoint_n → histogram of time_in_R

    sample_set = set(SAMPLE_TIMES.tolist())
    checkpoint_set = set(CHECKPOINTS.tolist())

    sample_idx = 0
    t_step_start = time.time()

    for n in range(1, N_STEPS + 1):
        # Pre-step snapshot for B2 in-R walkers (only if this step is sampled)
        is_sample = n in sample_set
        if is_sample:
            in_R_before = np.abs(E) <= E_R
            m_R_before = m[in_R_before]
            c_R_before = compute_fourier(m_R_before, MODES)
            n_R_before = m_R_before.shape[0]

        # Apply step
        step_walkers(m, E, sign, rng)

        # Update return_counts (0→1 entries) and time_in_R (occupation)
        in_R_now = np.abs(E) <= E_R
        entered_R = in_R_now & ~prev_in_R
        return_counts[entered_R] += 1
        time_in_R[in_R_now] += 1
        prev_in_R = in_R_now

        # Record at sample times
        if is_sample:
            # ĉ_R_after: Fourier over the SAME walkers who were in R before
            c_R_after = compute_fourier(m[in_R_before], MODES)

            # Full ensemble ĥ(r)
            h = compute_fourier(m, MODES)

            l1_arr[sample_idx] = compute_l1(m)
            h_full[sample_idx] = h
            h_R[sample_idx] = c_R_before
            h_R_after[sample_idx] = c_R_after
            n_R_arr[sample_idx] = n_R_before
            l2_norm[sample_idx] = compute_fourier_l2(h)

            if sample_idx % 50 == 0 or n == N_STEPS:
                dt = time.time() - t_step_start
                rate = n / max(dt, 1e-9)
                eta = (N_STEPS - n) / max(rate, 1e-9)
                print(f'  n={n:4d}  L₁={l1_arr[sample_idx]:.5f}  '
                      f'|ĥ(1)|={abs(h[0]):.4f}  '
                      f'n_R={n_R_before:_}  '
                      f'({rate:.1f} steps/s, ETA {eta:.0f}s)',
                      flush=True)

            sample_idx += 1

            # Conditional Fourier at checkpoint times (binned by return count)
            if n in checkpoint_set:
                cond, hist = checkpoint_conditional(m, return_counts, MODES,
                                                    COND_MIN_BIN)
                for k, bin_size, fourier in cond:
                    conditional_records.append((int(n), k, bin_size, fourier))
                return_counts_hists[int(n)] = hist
                max_t = int(time_in_R.max())
                time_in_R_hists[int(n)] = np.bincount(time_in_R, minlength=max_t + 1)
                print(f'    checkpoint n={n}: {len(cond)} bins ≥ {COND_MIN_BIN} walkers '
                      f'(max N_n={int(return_counts.max())}, max time={max_t})',
                      flush=True)

    total_time = time.time() - t_step_start
    print(f'\nTotal walk time: {total_time:.1f}s = {total_time/60:.2f} min')
    print(f'Rate: {N_STEPS/total_time:.1f} steps/s')
    print(f'Total walker-steps: {N_WALKERS * N_STEPS:,}')
    print(f'Throughput: {N_WALKERS * N_STEPS / total_time:.2e} walker-steps/s')

    # --- Save results -------------------------------------------------

    # Flatten conditional records for npz
    if conditional_records:
        cond_n = np.array([r[0] for r in conditional_records], dtype=np.int32)
        cond_k = np.array([r[1] for r in conditional_records], dtype=np.int32)
        cond_binsize = np.array([r[2] for r in conditional_records], dtype=np.int64)
        cond_fourier = np.array([r[3] for r in conditional_records],
                                 dtype=np.complex128)
    else:
        cond_n = np.zeros(0, dtype=np.int32)
        cond_k = np.zeros(0, dtype=np.int32)
        cond_binsize = np.zeros(0, dtype=np.int64)
        cond_fourier = np.zeros((0, len(MODES)), dtype=np.complex128)

    # Flatten return-count and time-in-R histograms (ragged; pad).
    def _pad_stack(hists):
        keys = sorted(hists.keys())
        if not keys:
            return np.zeros(0, dtype=np.int32), np.zeros((0, 0), dtype=np.int64)
        L = max(len(hists[k]) for k in keys)
        out = np.zeros((len(keys), L), dtype=np.int64)
        for i, k in enumerate(keys):
            h = hists[k]
            out[i, :len(h)] = h
        return np.array(keys, dtype=np.int32), out

    hist_keys_rc, hist_stack_rc = _pad_stack(return_counts_hists)
    hist_keys_tr, hist_stack_tr = _pad_stack(time_in_R_hists)

    np.savez_compressed(
        OUT_PATH,
        sample_times=SAMPLE_TIMES,
        l1=l1_arr,
        h_full=h_full,
        h_R=h_R,
        h_R_after=h_R_after,
        n_R=n_R_arr,
        l2_norm=l2_norm,
        modes=MODES,
        cond_n=cond_n,
        cond_k=cond_k,
        cond_binsize=cond_binsize,
        cond_fourier=cond_fourier,
        hist_checkpoints=hist_keys_rc,
        hist_return_counts=hist_stack_rc,
        hist_time_in_R=hist_stack_tr,
        hist_checkpoints_tr=hist_keys_tr,
        # Metadata
        meta_N=np.int64(N_WALKERS),
        meta_steps=np.int32(N_STEPS),
        meta_bins=np.int32(N_BINS),
        meta_E_R=np.int32(E_R),
        meta_E_THRESH=np.int32(E_THRESH),
        meta_seed=np.int64(SEED),
    )
    print(f'-> {OUT_PATH}')


if __name__ == '__main__':
    main()
