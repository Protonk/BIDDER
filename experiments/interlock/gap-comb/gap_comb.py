"""
Mantissa-spectrum gap-comb experiment for multiplicative atoms of
numerical semigroups.

The first interlock experiment collapses each atom to one leading digit.
This one keeps log-mantissa phase.  For a finite sequence X, compute

    C_X(k) = mean_{x in X} exp(2π i k frac(log_10 x)),   k = 1..K.

If A_S is well approximated by primes plus gap-times-prime layers, then
the ratio C_A(k) / C_prime(k) should carry a phase comb whose teeth sit
near log_10(g) for g in the gap set G.

Outputs:
- gap_comb.txt — spectral distances and phase-comb peaks.
- gap_comb.png — spectra, phase periodogram, and cross-semigroup scores.
"""

import os
import sys
import time
from math import log10

import numpy as np
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'interlock'))

from ns_atoms import numerical_semigroup, gap_set, frobenius_number  # noqa: E402


N = 1_000_000
K_MAX = 64
PHASE_GRID = 1024
BASE = 10
PRIME_AMP_FLOOR = 2e-3

SEMIGROUPS = [
    ("<3,5>", (3, 5)),
    ("<3,7>", (3, 7)),
    ("<4,5>", (4, 5)),
    ("<5,7>", (5, 7)),
    ("<3,5,7>", (3, 5, 7)),
]

PALETTE = {
    "yellow": "#ffcc5c",
    "blue": "#6ec6ff",
    "red": "#ff6f61",
    "green": "#88d8b0",
    "bg": "#0a0a0a",
    "fg": "white",
    "grid": "#333333",
}


def primes_up_to(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for p in range(2, int(limit ** 0.5) + 1):
        if sieve[p]:
            sieve[p * p::p] = bytearray(len(sieve[p * p::p]))
    return [i for i in range(limit + 1) if sieve[i]]


def atoms_fast(generators, limit):
    """A_S ∩ [2, limit] via product marking."""
    S = numerical_semigroup(generators, limit)
    s_list = sorted(s for s in S if s >= 2)
    reducible = bytearray(limit + 1)
    for i, a in enumerate(s_list):
        if a * a > limit:
            break
        for b in s_list[i:]:
            prod = a * b
            if prod > limit:
                break
            reducible[prod] = 1
    return [m for m in range(2, limit + 1) if m in S and not reducible[m]], S


def gap_prime_model(gaps, S, primes, limit):
    """Leading-order set model: primes in S plus g·prime layers."""
    model = {p for p in primes if p in S}
    for g in gaps:
        if g <= 1:
            continue
        for p in primes:
            value = g * p
            if value > limit:
                break
            if value in S:
                model.add(value)
    return sorted(model)


def coefficients(seq, k_max=K_MAX, base=BASE):
    theta = np.mod(np.log(np.asarray(seq, dtype=float)) / np.log(base), 1.0)
    out = np.empty(k_max, dtype=np.complex128)
    for k in range(1, k_max + 1):
        out[k - 1] = np.exp(2j * np.pi * k * theta).mean()
    return out


def spectral_distance(a, b):
    return float(np.sqrt(np.mean(np.abs(a - b) ** 2)))


def coherence(a, b):
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(abs(np.vdot(a, b)) / (na * nb))


def ratio_residual_periodogram(c_atoms, c_primes, k_values, phase_grid):
    stable = np.abs(c_primes) > PRIME_AMP_FLOOR
    ks = k_values[stable]
    if len(ks) == 0:
        phases = np.linspace(0.0, 1.0, phase_grid, endpoint=False)
        return phases, np.zeros_like(phases), stable
    ratio = c_atoms[stable] / c_primes[stable] - 1.0
    phases = np.linspace(0.0, 1.0, phase_grid, endpoint=False)
    waves = np.exp(-2j * np.pi * np.outer(ks, phases))
    score = np.abs(ratio @ waves)
    if score.max() > 0:
        score = score / score.max()
    return phases, score, stable


def top_phase_peaks(phases, score, count=5, exclusion=0.025):
    order = np.argsort(score)[::-1]
    peaks = []
    for idx in order:
        phase = float(phases[idx])
        if all(abs(((phase - p + 0.5) % 1.0) - 0.5) >= exclusion for p, _ in peaks):
            peaks.append((phase, float(score[idx])))
        if len(peaks) == count:
            break
    return peaks


def nearest_gap_distance(phase, gap_phases):
    if not gap_phases:
        return None
    return min(abs(((phase - gp + 0.5) % 1.0) - 0.5) for gp in gap_phases)


def draw_figure(rows, prime_coeffs, k_values):
    focus = rows[0]
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.patch.set_facecolor(PALETTE["bg"])
    axes = axes.ravel()

    for ax in axes:
        ax.set_facecolor(PALETTE["bg"])
        ax.tick_params(colors=PALETTE["fg"])
        for spine in ax.spines.values():
            spine.set_color(PALETTE["grid"])
        ax.grid(color=PALETTE["grid"], linewidth=0.45, alpha=0.6)

    ax = axes[0]
    ax.plot(k_values, np.abs(focus["c_atoms"]), color=PALETTE["yellow"],
            linewidth=1.6, label="atoms")
    ax.plot(k_values, np.abs(prime_coeffs), color=PALETTE["blue"],
            linewidth=1.4, label="primes")
    ax.plot(k_values, np.abs(focus["c_model"]), color=PALETTE["green"],
            linewidth=1.4, label="gap-prime model")
    ax.set_title("|C(k)| for A_<3,5>", color=PALETTE["fg"])
    ax.set_xlabel("harmonic k", color=PALETTE["fg"])
    ax.set_ylabel("magnitude", color=PALETTE["fg"])
    ax.legend(facecolor="#1a1a1a", labelcolor=PALETTE["fg"], framealpha=0.35)

    ax = axes[1]
    ax.plot(k_values, np.abs(focus["c_atoms"] - prime_coeffs),
            color=PALETTE["red"], linewidth=1.5, label="atoms - primes")
    ax.plot(k_values, np.abs(focus["c_model"] - prime_coeffs),
            color=PALETTE["green"], linewidth=1.5, label="model - primes")
    ax.set_title("Residual spectrum for A_<3,5>", color=PALETTE["fg"])
    ax.set_xlabel("harmonic k", color=PALETTE["fg"])
    ax.set_ylabel("residual magnitude", color=PALETTE["fg"])
    ax.legend(facecolor="#1a1a1a", labelcolor=PALETTE["fg"], framealpha=0.35)

    ax = axes[2]
    ax.plot(focus["phases"], focus["periodogram"], color=PALETTE["yellow"],
            linewidth=1.6, label="ratio residual")
    ax.plot(focus["phases"], focus["model_periodogram"], color=PALETTE["green"],
            linewidth=1.4, linestyle="--", label="gap-prime model")
    for gp, g in zip(focus["gap_phases"], focus["nonunit_gaps"]):
        ax.axvline(gp, color=PALETTE["blue"], linewidth=1.0, alpha=0.65)
        ax.text(gp, 1.03, str(g), color=PALETTE["blue"], ha="center",
                va="bottom", fontsize=9)
    ax.set_ylim(0, 1.12)
    ax.set_title("Phase-comb scan for A_<3,5>", color=PALETTE["fg"])
    ax.set_xlabel("mantissa phase φ", color=PALETTE["fg"])
    ax.set_ylabel("normalised score", color=PALETTE["fg"])
    ax.legend(facecolor="#1a1a1a", labelcolor=PALETTE["fg"], framealpha=0.35)

    ax = axes[3]
    labels = [r["name"] for r in rows]
    x = np.arange(len(rows))
    width = 0.35
    ax.bar(x - width / 2, [r["dist_prime"] for r in rows], width,
           color=PALETTE["red"], label="dist(atoms, primes)")
    ax.bar(x + width / 2, [r["dist_model"] for r in rows], width,
           color=PALETTE["green"], label="dist(atoms, model)")
    for i, r in enumerate(rows):
        ax.text(i, max(r["dist_prime"], r["dist_model"]) * 1.04,
                f'coh {r["residual_coherence"]:.2f}', color=PALETTE["fg"],
                ha="center", va="bottom", fontsize=8)
    ax.set_title("Gap-prime model fit across semigroups", color=PALETTE["fg"])
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right", color=PALETTE["fg"])
    ax.set_ylabel("spectral L2 distance", color=PALETTE["fg"])
    ax.legend(facecolor="#1a1a1a", labelcolor=PALETTE["fg"], framealpha=0.35)

    plt.suptitle(
        f"Gap-comb mantissa spectroscopy, atoms <= {N:,}, k <= {K_MAX}",
        color=PALETTE["fg"],
        fontsize=14,
    )
    plt.tight_layout()
    out_png = os.path.join(HERE, "gap_comb.png")
    plt.savefig(out_png, dpi=130, facecolor=PALETTE["bg"], bbox_inches="tight")
    return out_png


def main():
    print(f"Gap-comb spectrum: N={N:,}, K={K_MAX}")
    t0 = time.perf_counter()
    primes = primes_up_to(N)
    c_primes = coefficients(primes)
    print(f"  primes: {len(primes):,} ({time.perf_counter() - t0:.2f}s)")

    k_values = np.arange(1, K_MAX + 1)
    rows = []
    for name, generators in SEMIGROUPS:
        t0 = time.perf_counter()
        atom_seq, S = atoms_fast(generators, N)
        gaps = gap_set(S, N)
        nonunit_gaps = [g for g in gaps if g > 1]
        model_seq = gap_prime_model(gaps, S, primes, N)
        atom_set = set(atom_seq)
        model_set = set(model_seq)
        c_atoms = coefficients(atom_seq)
        c_model = coefficients(model_seq)
        phases, periodogram, stable = ratio_residual_periodogram(
            c_atoms, c_primes, k_values, PHASE_GRID
        )
        _, model_periodogram, _ = ratio_residual_periodogram(
            c_model, c_primes, k_values, PHASE_GRID
        )
        gap_phases = [log10(g) % 1.0 for g in nonunit_gaps]
        peaks = top_phase_peaks(phases, periodogram)
        model_peaks = top_phase_peaks(phases, model_periodogram)
        dist_prime = spectral_distance(c_atoms, c_primes)
        dist_model = spectral_distance(c_atoms, c_model)
        residual_coh = coherence(c_atoms - c_primes, c_model - c_primes)
        rows.append({
            "name": name,
            "generators": generators,
            "gaps": gaps,
            "nonunit_gaps": nonunit_gaps,
            "gap_phases": gap_phases,
            "frobenius": frobenius_number(S, N),
            "atom_count": len(atom_seq),
            "model_count": len(model_seq),
            "missing_from_model": len(atom_set - model_set),
            "extra_in_model": len(model_set - atom_set),
            "symdiff": len(atom_set ^ model_set),
            "c_atoms": c_atoms,
            "c_model": c_model,
            "dist_prime": dist_prime,
            "dist_model": dist_model,
            "model_gain": dist_prime / dist_model if dist_model else float("inf"),
            "residual_coherence": residual_coh,
            "phases": phases,
            "periodogram": periodogram,
            "model_periodogram": model_periodogram,
            "stable_harmonics": int(stable.sum()),
            "peaks": peaks,
            "model_peaks": model_peaks,
            "time": time.perf_counter() - t0,
        })
        print(
            f"  {name:<9} atoms={len(atom_seq):>8,} model={len(model_seq):>8,} "
            f"symdiff={rows[-1]['symdiff']:>4} "
            f"distP={dist_prime:.5f} distM={dist_model:.5f} "
            f"coh={residual_coh:.3f} ({rows[-1]['time']:.2f}s)"
        )

    out_png = draw_figure(rows, c_primes, k_values)
    out_txt = os.path.join(HERE, "gap_comb.txt")
    lines = [
        "Gap-comb mantissa spectroscopy",
        f"N = {N}",
        f"K_MAX = {K_MAX}",
        f"prime amplitude floor for ratio residual = {PRIME_AMP_FLOOR}",
        "",
        "Spectral distances over k = 1..K_MAX.",
        "distP = L2(C_atoms, C_primes). distM = L2(C_atoms, C_gap_model).",
        "",
        f"{'S':<10} {'F':>4} {'|G|':>4} {'|A|':>9} {'|model|':>9} "
        f"{'A-M':>5} {'M-A':>5} {'distP':>9} {'distM':>9} "
        f"{'gain':>7} {'coh':>7} {'stable':>6}",
        "-" * 98,
    ]
    for r in rows:
        lines.append(
            f"{r['name']:<10} {r['frobenius']:>4} {len(r['gaps']):>4} "
            f"{r['atom_count']:>9,} {r['model_count']:>9,} "
            f"{r['missing_from_model']:>5} {r['extra_in_model']:>5} "
            f"{r['dist_prime']:>9.5f} {r['dist_model']:>9.5f} "
            f"{r['model_gain']:>7.2f} {r['residual_coherence']:>7.3f} "
            f"{r['stable_harmonics']:>6}"
        )

    lines += ["", "Phase-comb peaks from C_atoms / C_primes - 1."]
    for r in rows:
        lines += [
            "",
            f"{r['name']}  generators={r['generators']}",
            f"G = {r['gaps']}",
            "nonunit gap phases log10(g) mod 1:",
            "  " + ", ".join(f"{g}:{phase:.4f}" for g, phase in zip(r["nonunit_gaps"], r["gap_phases"])),
            "top data peaks:",
        ]
        for phase, score in r["peaks"]:
            distance = nearest_gap_distance(phase, r["gap_phases"])
            distance_text = "NA" if distance is None else f"{distance:.4f}"
            lines.append(f"  phase={phase:.4f} score={score:.3f} nearest_gap={distance_text}")
        lines.append("top gap-prime-model peaks:")
        for phase, score in r["model_peaks"]:
            distance = nearest_gap_distance(phase, r["gap_phases"])
            distance_text = "NA" if distance is None else f"{distance:.4f}"
            lines.append(f"  phase={phase:.4f} score={score:.3f} nearest_gap={distance_text}")

    with open(out_txt, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Saved {out_txt}")
    print(f"Saved {out_png}")


if __name__ == "__main__":
    main()
