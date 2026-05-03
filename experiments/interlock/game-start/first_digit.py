"""
First-digit fingerprint of A_⟨3,5⟩.

`interlock/INTERLOCKING-DEFECTS.md` §"What's open" item 1: build
A_⟨3,5⟩ ∩ [2, N], compute the leading-digit histogram, and compare
against the prime baseline and the M_n atom baselines (which are
exactly uniform per the substrate clauses).

Output:
- first_digit.png       — five-panel comparison plot.
- first_digit_summary.txt — counts, frequencies, and TVDs.
"""

import os
import sys
import time

import numpy as np
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'interlock'))

from ns_atoms import numerical_semigroup, is_atom            # noqa: E402
from cham_ns import leading_digit_histogram, per_decade_histograms  # noqa: E402

N = 1_000_000


def atoms_fast(generators, N):
    """A_S ∩ [2, N] via a reducibility sieve over (S × S) pairs.

    O(|{(a, b) : a ≤ b ∈ S \\ {0, 1}, a·b ≤ N}|), much faster than
    the trial-division path in `interlock/ns_atoms.py` for large N.
    """
    S = numerical_semigroup(generators, N)
    s_list = sorted(s for s in S if s >= 2)
    reducible = bytearray(N + 1)
    for i, a in enumerate(s_list):
        if a * a > N:
            break
        for b in s_list[i:]:
            prod = a * b
            if prod > N:
                break
            reducible[prod] = 1
    return [m for m in range(2, N + 1) if m in S and not reducible[m]]


def primes_up_to(N):
    sieve = bytearray([1]) * (N + 1)
    sieve[0] = sieve[1] = 0
    for p in range(2, int(N ** 0.5) + 1):
        if sieve[p]:
            sieve[p * p::p] = bytearray(len(sieve[p * p::p]))
    return [i for i in range(N + 1) if sieve[i]]


def m_n_atoms(n, N):
    """Atoms of M_n = {n·k : k ≥ 1, n ∤ k} ∩ [n, N]."""
    return [n * k for k in range(1, N // n + 1) if k % n != 0]


def aggregate_decades(by_dec):
    """Sum per-decade histograms into one length-9 vector."""
    total = [0] * 9
    for h in by_dec.values():
        for i in range(9):
            total[i] += h[i]
    return total


def tvd(p, q):
    return float(0.5 * np.sum(np.abs(np.asarray(p) - np.asarray(q))))


def main():
    print(f"Generating sequences up to N = {N:,} ...")

    t0 = time.perf_counter()
    A_NS = atoms_fast([3, 5], N)
    print(f"  A_⟨3,5⟩          : {len(A_NS):>7,}  ({time.perf_counter() - t0:5.1f} s)")

    # Sanity: agree with ns_atoms predicate on a small bound.
    S_check = numerical_semigroup([3, 5], 200)
    assert [m for m in A_NS if m <= 200] == [m for m in range(2, 201) if is_atom(m, S_check)]

    t0 = time.perf_counter()
    PRIMES = primes_up_to(N)
    print(f"  primes ≤ N       : {len(PRIMES):>7,}  ({time.perf_counter() - t0:5.1f} s)")

    seqs = [
        ('A_⟨3,5⟩',     A_NS),
        ('primes',     PRIMES),
        ('M_2-atoms',  m_n_atoms(2, N)),
        ('M_3-atoms',  m_n_atoms(3, N)),
        ('M_5-atoms',  m_n_atoms(5, N)),
    ]
    for name, seq in seqs[2:]:
        print(f"  {name:<16} : {len(seq):>7,}")

    print("\nComputing histograms ...")
    by_seq = {}
    for name, seq in seqs:
        by_dec = per_decade_histograms(seq)
        agg = aggregate_decades(by_dec)
        freqs = np.array(agg, dtype=float) / sum(agg)
        by_seq[name] = {'agg': agg, 'freqs': freqs, 'by_dec': by_dec}

    uniform = np.full(9, 1 / 9)
    benford = np.array([np.log10(1 + 1 / d) for d in range(1, 10)])

    # TVD table.
    print(f"\n{'sequence':<14} {'count':>8} {'TVD(unif)':>10} {'TVD(Benf)':>10} "
          f"{'TVD(NS)':>9}")
    print('-' * 56)
    ns_freqs = by_seq['A_⟨3,5⟩']['freqs']
    summary = ["First-digit fingerprint of A_⟨3,5⟩",
               f"N = {N}",
               "",
               f"{'sequence':<14} {'count':>8} {'TVD(unif)':>10} {'TVD(Benf)':>10} "
               f"{'TVD(NS)':>9}",
               '-' * 56]
    for name, _ in seqs:
        f = by_seq[name]['freqs']
        n = sum(by_seq[name]['agg'])
        line = (f"{name:<14} {n:>8,} "
                f"{tvd(f, uniform):>10.4f} {tvd(f, benford):>10.4f} "
                f"{tvd(f, ns_freqs):>9.4f}")
        print(line)
        summary.append(line)

    # Per-digit frequencies.
    print(f"\nPer-digit frequency (× 10^4):")
    header = '  d  ' + ''.join(f'{name:>14}' for name, _ in seqs)
    print(header)
    summary += ['', 'Per-digit frequency (× 10^4):', header]
    for d in range(9):
        row = f'  {d + 1}  '
        for name, _ in seqs:
            row += f"{by_seq[name]['freqs'][d] * 1e4:>14.1f}"
        print(row)
        summary.append(row)

    # Reference rows.
    summary += ['', 'Reference (× 10^4):',
                '  d  ' + f"{'uniform':>14}{'Benford':>14}"]
    for d in range(9):
        summary.append(f'  {d + 1}  ' + f'{1 / 9 * 1e4:>14.1f}'
                       + f'{benford[d] * 1e4:>14.1f}')

    out_dir = HERE
    summary_path = os.path.join(out_dir, 'first_digit_summary.txt')
    with open(summary_path, 'w') as f:
        f.write('\n'.join(summary) + '\n')
    print(f"\nSaved {summary_path}")

    # Five-panel plot.
    print("Plotting ...")
    fig, axes = plt.subplots(1, 5, figsize=(22, 5), sharey=True)
    fig.patch.set_facecolor('#0a0a0a')
    x = np.arange(1, 10)

    for ax, (name, _) in zip(axes, seqs):
        ax.set_facecolor('#0a0a0a')
        f = by_seq[name]['freqs']
        n = sum(by_seq[name]['agg'])
        ax.bar(x, f, color='#ffcc5c', alpha=0.85, width=0.7,
               label='observed')
        ax.plot(x, uniform, color='#6ec6ff', linewidth=1.6, marker='o',
                markersize=4, label='uniform 1/9')
        ax.plot(x, benford, color='#ff6f61', linewidth=1.6, marker='s',
                markersize=4, label='Benford')
        ax.set_title(f'{name}   (n = {n:,})', color='white', fontsize=11)
        ax.set_xlabel('leading digit', color='white')
        ax.set_xticks(x)
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#333')
        if ax is axes[0]:
            ax.set_ylabel('frequency', color='white')
            ax.legend(fontsize=9, framealpha=0.3, labelcolor='white',
                      facecolor='#1a1a1a', loc='upper right')

    plt.suptitle(
        f'First-digit distribution: A_⟨3,5⟩ vs primes vs M_n   '
        f'(atoms ≤ {N:,})',
        color='white', fontsize=13
    )
    plt.tight_layout()
    plot_path = os.path.join(out_dir, 'first_digit.png')
    plt.savefig(plot_path, dpi=120, facecolor='#0a0a0a',
                bbox_inches='tight')
    print(f"Saved {plot_path}")


if __name__ == "__main__":
    main()
