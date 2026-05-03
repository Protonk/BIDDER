"""
Does A_⟨3,5⟩ inherit the prime tilt at every N, not just at 10⁶?

Follow-up to first_digit.py. Sweeps N ∈ {10³, 10⁴, 10⁵, 10⁶, 10⁷} and
records, for each scale, the leading-digit residual against uniform
1/9 for both primes and A_⟨3,5⟩, plus the TVD between them.

Output:
- tilt_decay.txt — table at every N.
- tilt_decay.png — per-digit signed deviation (freq − 1/9) overlaid
  for both sequences across all N.
"""

import os
import sys
import time

import numpy as np
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'interlock'))

from cham_ns import leading_digit_histogram                # noqa: E402
from ns_atoms import numerical_semigroup                   # noqa: E402

K_VALUES = [3, 4, 5, 6, 7]


def sieve_primes(N):
    s = bytearray([1]) * (N + 1)
    s[0] = s[1] = 0
    for p in range(2, int(N ** 0.5) + 1):
        if s[p]:
            s[p * p::p] = bytearray(len(s[p * p::p]))
    return [i for i in range(N + 1) if s[i]]


def atoms_fast(generators, N):
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


def freqs(seq):
    h = leading_digit_histogram(seq)
    total = sum(h)
    return total, np.array([c / total for c in h])


def tvd(p, q):
    return float(0.5 * np.sum(np.abs(np.asarray(p) - np.asarray(q))))


def main():
    uniform = np.full(9, 1 / 9)
    rows = []

    print(f"{'N':>6} {'|P|':>10} {'|A|':>10}  "
          f"{'TVD_P(u)':>9} {'TVD_A(u)':>9}  {'TVD(A,P)':>9}  "
          f"{'P:d1':>7} {'A:d1':>7}  {'time':>10}")
    print('-' * 100)

    for k in K_VALUES:
        N = 10 ** k
        t0 = time.perf_counter()
        P = sieve_primes(N)
        nP, fP = freqs(P)
        tP = time.perf_counter() - t0

        t0 = time.perf_counter()
        A = atoms_fast([3, 5], N)
        nA, fA = freqs(A)
        tA = time.perf_counter() - t0

        tvd_P = tvd(fP, uniform)
        tvd_A = tvd(fA, uniform)
        tvd_AP = tvd(fA, fP)

        rows.append({'k': k, 'N': N, 'nP': nP, 'nA': nA,
                     'fP': fP, 'fA': fA,
                     'tvd_P': tvd_P, 'tvd_A': tvd_A, 'tvd_AP': tvd_AP})
        print(f"10^{k} {nP:>10,} {nA:>10,}  "
              f"{tvd_P:>9.4f} {tvd_A:>9.4f}  {tvd_AP:>9.4f}  "
              f"{fP[0]:>7.4f} {fA[0]:>7.4f}  ({tP:.1f}s+{tA:.1f}s)")

    # Save table.
    lines = [
        "Tilt decay of A_⟨3,5⟩ vs primes across N",
        "",
        f"{'N':>6} {'|P|':>10} {'|A|':>10}  "
        f"{'TVD_P(u)':>9} {'TVD_A(u)':>9}  {'TVD(A,P)':>9}",
        '-' * 70,
    ]
    for r in rows:
        lines.append(f"10^{r['k']} {r['nP']:>10,} {r['nA']:>10,}  "
                     f"{r['tvd_P']:>9.4f} {r['tvd_A']:>9.4f}  "
                     f"{r['tvd_AP']:>9.4f}")
    lines += [
        "",
        "Per-digit frequency × 10⁴ at each N. P = primes, A = A_⟨3,5⟩.",
        "  d  " + ''.join(f"   P/10^{r['k']:<2}    A/10^{r['k']:<2}" for r in rows),
    ]
    for d in range(9):
        row = f"  {d + 1}  "
        for r in rows:
            row += f"  {r['fP'][d] * 1e4:>8.1f}  {r['fA'][d] * 1e4:>8.1f}"
        lines.append(row)

    out_txt = os.path.join(HERE, 'tilt_decay.txt')
    with open(out_txt, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"\nSaved {out_txt}")

    # Plot signed deviation freq − 1/9 per leading digit, both sequences,
    # one line per N.
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), sharey=True)
    fig.patch.set_facecolor('#0a0a0a')
    x = np.arange(1, 10)
    cmap = plt.cm.viridis(np.linspace(0.15, 0.95, len(rows)))

    for ax, key, title in [
        (axes[0], 'fP', 'primes ≤ N'),
        (axes[1], 'fA', 'A_⟨3,5⟩ ≤ N'),
    ]:
        ax.set_facecolor('#0a0a0a')
        for r, color in zip(rows, cmap):
            dev = r[key] - 1 / 9
            ax.plot(x, dev, color=color, linewidth=2, marker='o',
                    markersize=6, label=f'N = 10^{r["k"]}')
        ax.axhline(0, color='#888', linewidth=0.8, linestyle='--')
        ax.set_title(title, color='white', fontsize=12)
        ax.set_xlabel('leading digit', color='white')
        ax.set_xticks(x)
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#333')
        ax.legend(fontsize=10, framealpha=0.3, labelcolor='white',
                  facecolor='#1a1a1a', loc='upper right')
        if ax is axes[0]:
            ax.set_ylabel('frequency − 1/9', color='white')

    plt.suptitle(
        'Leading-digit residual against uniform: shape of decay '
        'with N for primes and A_⟨3,5⟩',
        color='white', fontsize=13
    )
    plt.tight_layout()
    out_png = os.path.join(HERE, 'tilt_decay.png')
    plt.savefig(out_png, dpi=120, facecolor='#0a0a0a',
                bbox_inches='tight')
    print(f"Saved {out_png}")


if __name__ == "__main__":
    main()
