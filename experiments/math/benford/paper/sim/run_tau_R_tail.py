"""
Mess #3 diagnostic: empirical τ_R tail for BS(1,2).

τ_R is the first return time to R = {|E| ≤ E₀} after leaving it.
Mess #3 warns that the Feller-continuity argument for T_R rests
on a uniform-geometric tail on τ_R that the null-recurrent walk
doesn't deliver. Laplace-diagnostic showed BS(1,2) has positive
E-drift, which puts pressure on even null-recurrent framing.

Return-marginal sim already showed 12.4% of walkers never
returned in 10⁴ steps. This sim measures P(τ_R > n) directly
with longer horizon and histograms all excursion durations (not
just first), to characterize:

- The survival function S(n) = P(τ_R > n), including the
  asymptote P(τ_R = ∞) = fraction of walkers never returning.
- Tail shape: polynomial? stretched-exp? mixture?
- Per-walker first-excursion (IC-specific) duration, vs
  subsequent-excursion pooled (closer to stationary).

Run: sage -python run_tau_R_tail.py
"""

import math
import os
import time
import numpy as np

from run_comparison_walks import (
    initialize, step_a, step_a_inv, step_b,
)


SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SIM_DIR, 'tau_R_tail_results')
os.makedirs(OUT_DIR, exist_ok=True)

N_WALKERS = 10**6
N_MAX = 30000
E0 = 10
SEED = 0xABC_DE7A


def step_bs12(m, E, sign, rng):
    choice = rng.integers(0, 4, size=m.shape[0], dtype=np.int8)
    step_a(m, E, choice == 0)
    step_a_inv(m, E, choice == 1)
    step_b(m, E, sign, choice == 2, +1)
    step_b(m, E, sign, choice == 3, -1)


def main():
    print(f'τ_R tail sim: BS(1,2), N = {N_WALKERS:_}, n_max = {N_MAX}, '
          f'E₀ = {E0}')
    rng = np.random.default_rng(SEED)
    m, E, sign = initialize(N_WALKERS)
    prev_in_R = (np.abs(E) <= E0)  # all True at t=0

    SENTINEL = np.int32(-1)
    # Per-walker:
    first_exit_t = np.full(N_WALKERS, SENTINEL, dtype=np.int32)
    first_return_t = np.full(N_WALKERS, SENTINEL, dtype=np.int32)
    # Exit time of current ongoing excursion (SENTINEL if currently in R)
    current_exit_t = np.full(N_WALKERS, SENTINEL, dtype=np.int32)
    excursion_count = np.zeros(N_WALKERS, dtype=np.int32)

    # Log-spaced bin edges for durations
    bin_edges = np.unique(np.concatenate([
        np.arange(1, 101, dtype=np.int64),
        np.round(np.logspace(2.0, math.log10(N_MAX + 1), 300)).astype(np.int64),
    ]))
    n_bins = bin_edges.size
    # Histograms for:
    #   dur_hist_all      : every completed excursion
    #   dur_hist_post_first: excursions with index ≥ 2 per walker
    dur_hist_all = np.zeros(n_bins, dtype=np.int64)
    dur_hist_post_first = np.zeros(n_bins, dtype=np.int64)

    t0 = time.time()
    for step in range(1, N_MAX + 1):
        step_bs12(m, E, sign, rng)
        in_R_now = np.abs(E) <= E0

        exit_mask = prev_in_R & ~in_R_now
        return_mask = (~prev_in_R) & in_R_now

        if exit_mask.any():
            current_exit_t[exit_mask] = step
            first_mask = exit_mask & (first_exit_t == SENTINEL)
            first_exit_t[first_mask] = step

        if return_mask.any():
            durs = (step - current_exit_t[return_mask]).astype(np.int64)
            # Bin: edges are left-inclusive. Use right-1 so that dur equals
            # an edge falls into the bin starting at that edge.
            idx = np.searchsorted(bin_edges, durs, side='right') - 1
            idx = np.clip(idx, 0, n_bins - 1)
            np.add.at(dur_hist_all, idx, 1)
            # Post-first: walkers whose excursion_count ≥ 1 before this
            # return (i.e., this is their 2nd or later return)
            ec_here = excursion_count[return_mask]
            post_first_idx = idx[ec_here >= 1]
            if post_first_idx.size > 0:
                np.add.at(dur_hist_post_first, post_first_idx, 1)

            # First return: walker had a first exit, no first return yet
            first_ret_mask = return_mask & (first_return_t == SENTINEL) & \
                             (first_exit_t != SENTINEL)
            first_return_t[first_ret_mask] = step

            excursion_count[return_mask] += 1
            current_exit_t[return_mask] = SENTINEL

        prev_in_R = in_R_now
        if step % 2000 == 0 or step == N_MAX:
            dt = time.time() - t0
            frac_in_R = in_R_now.mean()
            in_flight = (current_exit_t != SENTINEL).sum()
            never_exited = (first_exit_t == SENTINEL).sum()
            print(f'  n={step:6d}  frac_in_R={frac_in_R:.3f}  '
                  f'out_and_not_returned={in_flight:>8_}  '
                  f'never_exited={never_exited:>6_}  '
                  f'completed_excs={dur_hist_all.sum():>10_}  '
                  f'({step/max(dt,1e-9):.1f} s/s)', flush=True)
    wall = time.time() - t0
    print(f'  wall: {wall:.1f}s')

    # Summary
    completed = int(dur_hist_all.sum())
    in_flight_end = (current_exit_t != SENTINEL)
    censored_durs = (N_MAX - current_exit_t[in_flight_end]).astype(np.int64)
    never_exited_final = (first_exit_t == SENTINEL).sum()
    print(f'\n  Total completed excursions: {completed:_}')
    print(f'  Walkers in flight at end: {int(in_flight_end.sum()):_} '
          f'({in_flight_end.mean():.3%})')
    print(f'  Walkers that never exited: {int(never_exited_final):_} '
          f'({never_exited_final / N_WALKERS:.3%})')
    first_exits_so_far = (first_exit_t != SENTINEL).sum()
    first_returns_so_far = (first_return_t != SENTINEL).sum()
    print(f'  Walkers with first exit recorded: {int(first_exits_so_far):_} '
          f'({first_exits_so_far / N_WALKERS:.3%})')
    print(f'  Walkers with first return recorded: {int(first_returns_so_far):_} '
          f'({first_returns_so_far / N_WALKERS:.3%})')
    ce_frac = int(in_flight_end.sum()) / N_WALKERS
    print(f'  Empirical P(τ_R > {N_MAX} | exited) approx = '
          f'{int(in_flight_end.sum()) / max(first_exits_so_far, 1):.4f}')

    out_path = os.path.join(OUT_DIR, 'tau_R_tail.npz')
    np.savez_compressed(out_path,
                        bin_edges=bin_edges,
                        dur_hist_all=dur_hist_all,
                        dur_hist_post_first=dur_hist_post_first,
                        first_exit_t=first_exit_t,
                        first_return_t=first_return_t,
                        censored_durs=censored_durs,
                        excursion_count=excursion_count,
                        meta_N=np.int64(N_WALKERS),
                        meta_n_max=np.int64(N_MAX),
                        meta_E0=np.int32(E0),
                        meta_seed=np.int64(SEED))
    print(f'  -> {out_path}')


if __name__ == '__main__':
    main()
