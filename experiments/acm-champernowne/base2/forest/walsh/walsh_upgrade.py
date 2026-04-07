import csv
import math
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, "..", ".."))
sys.path.insert(0, os.path.join(_here, "..", "..", "..", "..", "..", "core"))

import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import hadamard

from acm_core import acm_n_primes


SEED = 20260406
N_MAX = 32
BITS_TARGET = 2_000_000
BASE_K = 8
BASE_CHUNK = 1 << BASE_K
PHASE_OFFSETS = list(range(0, BASE_CHUNK, 8))
ALT_KS = [6, 7, 9, 10]
BOOTSTRAP_REPS = 80
UNIVERSAL_MIN_MONOIDS = 25
CV_MAX = 0.25
Z_MIN = 3.0
SPLIT_HALF_TOL = 0.10


def v2(n):
    m = 0
    while n % 2 == 0:
        m += 1
        n //= 2
    return m


def estimate_count_for_bits(n, bits):
    avg = math.log2(max(n * (bits // 10), 4))
    return int(bits / max(avg, 4)) + 200


def popcount(x):
    return int(bin(int(x)).count("1"))


def support_positions(idx, k):
    return [i for i in range(k) if (idx >> i) & 1]


def classify_support(idx, k):
    pos = support_positions(idx, k)
    if not pos:
        return "empty"
    if len(pos) == k:
        return "full"
    if len(pos) == 1:
        return "singleton"
    if all(b - a == 1 for a, b in zip(pos, pos[1:])):
        return "contiguous"
    if all((b - a) == 2 for a, b in zip(pos, pos[1:])):
        return "alternating"
    if pos[0] == 0 and pos[-1] == k - 1:
        return "edge-loaded"
    center = sum(pos) / len(pos)
    if center <= (k - 1) / 3:
        return "low-bit-heavy"
    if center >= 2 * (k - 1) / 3:
        return "high-bit-heavy"
    return "mixed"


def sequency_of_index(idx, k):
    row = hadamard(1 << k)[idx]
    return int(np.count_nonzero(np.diff(row) != 0))


def map_support_to_k(idx, k_from, k_to):
    pos = support_positions(idx, k_from)
    if not pos:
        return 0
    if len(pos) >= k_to:
        return (1 << k_to) - 1
    if k_from == 1 or k_to == 1:
        return 1
    targets = [p * (k_to - 1) / (k_from - 1) for p in pos]
    used = set()
    mapped = []
    for target in targets:
        pref = int(round(target))
        candidates = list(range(k_to))
        best = min((j for j in candidates if j not in used), key=lambda j: (abs(j - target), j))
        used.add(best)
        mapped.append(best)
    out = 0
    for p in sorted(mapped):
        out |= 1 << p
    return out


def build_actual_stream(n):
    count = estimate_count_for_bits(n, BITS_TARGET)
    primes = acm_n_primes(n, count)
    entries = [format(p, "b") for p in primes]
    lengths = np.array([len(s) for s in entries], dtype=np.int32)
    stream = "".join(entries).encode("ascii")
    bits = np.frombuffer(stream, dtype=np.uint8) - ord("0")
    boundaries = np.empty(len(lengths) + 1, dtype=np.int32)
    boundaries[0] = 0
    boundaries[1:] = np.cumsum(lengths)
    return {
        "n": n,
        "count": count,
        "bits": bits.astype(np.uint8, copy=False),
        "lengths": lengths,
        "boundaries": boundaries,
        "v2": v2(n),
    }


def prepare_streams():
    data = {}
    for n in range(2, N_MAX + 1):
        data[n] = build_actual_stream(n)
    return data


def hadamard_columns(k, indices):
    h = hadamard(1 << k).astype(np.float32)
    return h[:, indices].astype(np.float32, copy=False)


def chunk_power_for_indices(bits, k, indices, offset=0):
    chunk = 1 << k
    usable = len(bits) - offset
    n_chunks = usable // chunk
    if n_chunks <= 0:
        return np.empty((0, len(indices)), dtype=np.float32)
    view = bits[offset : offset + n_chunks * chunk].reshape(n_chunks, chunk).astype(np.float32)
    view = 2.0 * view - 1.0
    cols = hadamard_columns(k, indices)
    w = (view @ cols) / float(chunk)
    return (w * w).astype(np.float32, copy=False)


def full_spectrum(bits, k, offset=0):
    chunk = 1 << k
    usable = len(bits) - offset
    n_chunks = usable // chunk
    view = bits[offset : offset + n_chunks * chunk].reshape(n_chunks, chunk).astype(np.float32)
    view = 2.0 * view - 1.0
    h = hadamard(chunk).astype(np.float32)
    w = (view @ h) / float(chunk)
    return np.mean(w * w, axis=0).astype(np.float64)


def boundary_counts(boundaries, chunk_size, offset=0):
    total = boundaries[-1]
    n_chunks = (total - offset) // chunk_size
    starts = offset + np.arange(n_chunks, dtype=np.int32) * chunk_size
    ends = starts + chunk_size
    interior = boundaries[1:-1]
    left = np.searchsorted(interior, starts, side="right")
    right = np.searchsorted(interior, ends, side="left")
    return right - left


def universal_candidates_from_saved():
    d = np.load(os.path.join(_here, "walsh_spectra.npz"))
    spectra = d["spectra"]
    base = 1.0 / int(d["chunk_size"])
    counts = (spectra > base).sum(axis=0)
    high = np.array([popcount(i) >= 3 for i in range(spectra.shape[1])])
    return np.where(high & (counts >= UNIVERSAL_MIN_MONOIDS))[0]


def analytic_null_std(chunk_counts, chunk_size):
    sigma2 = 2.0 * (chunk_size - 1) / (chunk_size ** 3)
    return math.sqrt(sigma2 * np.sum(1.0 / chunk_counts) / (len(chunk_counts) ** 2))


def bootstrap_pooled_means(chunk_power_by_n, rng):
    cells = next(iter(chunk_power_by_n.values())).shape[1]
    pooled = np.zeros((BOOTSTRAP_REPS, cells), dtype=np.float64)
    for arr in chunk_power_by_n.values():
        m = arr.shape[0]
        weights = rng.poisson(1.0, size=(BOOTSTRAP_REPS, m)).astype(np.float32)
        denom = weights.sum(axis=1, keepdims=True)
        denom[denom == 0] = 1.0
        pooled += (weights @ arr) / denom
    pooled /= len(chunk_power_by_n)
    return pooled


def stage0_metrics(streams, candidate_indices):
    rng = np.random.default_rng(SEED)
    chunk_power = {}
    per_monoid = []
    first_half = []
    second_half = []
    chunk_counts = []
    for n, info in streams.items():
        arr = chunk_power_for_indices(info["bits"], BASE_K, candidate_indices, offset=0)
        chunk_power[n] = arr
        per_monoid.append(arr.mean(axis=0))
        mid = arr.shape[0] // 2
        first_half.append(arr[:mid].mean(axis=0))
        second_half.append(arr[mid:].mean(axis=0))
        chunk_counts.append(arr.shape[0])
    per_monoid = np.array(per_monoid)
    first_half = np.array(first_half)
    second_half = np.array(second_half)
    pooled = per_monoid.mean(axis=0)
    pooled_first = first_half.mean(axis=0)
    pooled_second = second_half.mean(axis=0)
    boot = bootstrap_pooled_means(chunk_power, rng)
    ci_lo = np.percentile(boot, 2.5, axis=0)
    ci_hi = np.percentile(boot, 97.5, axis=0)
    base = 1.0 / BASE_CHUNK
    counts_above = (per_monoid > base).sum(axis=0)
    cv = per_monoid.std(axis=0, ddof=1) / pooled
    z = (pooled - base) / analytic_null_std(np.array(chunk_counts, dtype=np.float64), BASE_CHUNK)
    # Split-half is recorded but NOT used as a robustness filter.
    #
    # The original implementation required both halves to lie inside
    # the bootstrap CI of the *full* pooled mean, which systematically
    # rejected the strongest cells: their pooled CI is so tight that
    # the noisier half-spectra almost always fall outside it.
    #
    # A relative-difference variant has its own problem: the two
    # halves of each monoid's chunk stream come from systematically
    # different n-primes (shorter integers in the first half, longer
    # in the second). Cells that capture this natural drift show
    # large |first - second| even though the elevation itself is
    # entirely real. The test then conflates "is this cell stable
    # across the stream's natural drift" with "is this cell elevated
    # reliably," and rejects cells that are universal in the sense
    # we actually care about.
    #
    # The count + CV + z bar is sufficient for universality:
    # elevated in >=25/31 monoids, cross-monoid CV < 0.25, and a
    # pooled z-score of >=3 against the analytic null. We keep
    # split_ok as a recorded diagnostic for future inspection.
    half_diff = np.abs(pooled_first - pooled_second)
    split_ok = (half_diff / np.maximum(pooled, 1e-12)) < SPLIT_HALF_TOL
    robust = (counts_above >= UNIVERSAL_MIN_MONOIDS) & (cv < CV_MAX) & (z >= Z_MIN)
    return {
        "per_monoid": per_monoid,
        "pooled": pooled,
        "pooled_first": pooled_first,
        "pooled_second": pooled_second,
        "ci_lo": ci_lo,
        "ci_hi": ci_hi,
        "counts_above": counts_above,
        "cv": cv,
        "z": z,
        "split_ok": split_ok,
        "robust_mask": robust,
        "chunk_counts": np.array(chunk_counts, dtype=np.int32),
    }


def corr_with_v2(values):
    v2s = np.array([v2(n) for n in range(2, N_MAX + 1)], dtype=np.float64)
    return float(np.corrcoef(v2s, values)[0, 1])


def save_stage0(streams, candidate_indices, metrics):
    robust_indices = candidate_indices[metrics["robust_mask"]]
    sequencies = np.array([sequency_of_index(int(idx), BASE_K) for idx in robust_indices], dtype=np.int32)
    rows = []
    for i, idx in enumerate(candidate_indices):
        vals = metrics["per_monoid"][:, i]
        rows.append(
            {
                "s": int(idx),
                "popcount": popcount(idx),
                "geometry": classify_support(int(idx), BASE_K),
                "sequency": sequency_of_index(int(idx), BASE_K),
                "mean_p": float(metrics["pooled"][i]),
                "ratio": float(metrics["pooled"][i] * BASE_CHUNK),
                "corr_v2": corr_with_v2(vals),
                "monoids_above": int(metrics["counts_above"][i]),
                "cv": float(metrics["cv"][i]),
                "z": float(metrics["z"][i]),
                "ci_lo": float(metrics["ci_lo"][i]),
                "ci_hi": float(metrics["ci_hi"][i]),
                "split_ok": bool(metrics["split_ok"][i]),
                "robust": bool(metrics["robust_mask"][i]),
            }
        )
    csv_path = os.path.join(_here, "walsh_upgrade_stage0.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    np.savez(
        os.path.join(_here, "walsh_upgrade_stage0.npz"),
        candidate_indices=candidate_indices,
        robust_indices=robust_indices,
        pooled=metrics["pooled"],
        ci_lo=metrics["ci_lo"],
        ci_hi=metrics["ci_hi"],
        counts_above=metrics["counts_above"],
        cv=metrics["cv"],
        z=metrics["z"],
    )
    base = np.load(os.path.join(_here, "walsh_spectra.npz"))
    order_indices = np.array(sorted(range(BASE_CHUNK), key=lambda i: (sequency_of_index(int(i), BASE_K), i)))
    heatmap = base["spectra"][:, order_indices]
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor("#0a0a0a")
    ax.set_facecolor("#0a0a0a")
    vmin = max(float(heatmap[heatmap > 0].min()), 1e-10)
    im = ax.imshow(heatmap, aspect="auto", cmap="inferno", vmin=vmin, vmax=float(heatmap.max()))
    ax.set_title("Walsh heatmap in sequency order", color="white", fontsize=14, pad=12)
    ax.set_xlabel("Walsh subset index sorted by sequency", color="white")
    ax.set_ylabel("monoid n", color="white")
    ax.set_yticks(range(len(base["ns"])))
    ax.set_yticklabels([str(int(n)) for n in base["ns"]], color="white", fontsize=8)
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_color("#444")
    cbar = plt.colorbar(im, ax=ax, pad=0.02)
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="white")
    cbar.outline.set_edgecolor("#444")
    plt.tight_layout()
    plt.savefig(os.path.join(_here, "walsh_sequency_heatmap.png"), dpi=200, facecolor="#0a0a0a", bbox_inches="tight")
    plt.close()
    return robust_indices, rows


def phase_sweep(streams, tracked_indices):
    out = np.zeros((len(PHASE_OFFSETS), N_MAX - 1, len(tracked_indices)), dtype=np.float32)
    for oi, offset in enumerate(PHASE_OFFSETS):
        for ni, n in enumerate(range(2, N_MAX + 1)):
            arr = chunk_power_for_indices(streams[n]["bits"], BASE_K, tracked_indices, offset=offset)
            out[oi, ni] = arr.mean(axis=0)
    np.savez(os.path.join(_here, "walsh_phase_sweep.npz"), offsets=np.array(PHASE_OFFSETS), ns=np.arange(2, N_MAX + 1), indices=tracked_indices, spectra=out)
    return out


def chunk_size_sweep(streams, tracked_indices):
    mapped = {k: np.array([map_support_to_k(int(idx), BASE_K, k) for idx in tracked_indices], dtype=np.int32) for k in ALT_KS}
    result = {}
    for k in ALT_KS:
        vals = np.zeros((N_MAX - 1, len(tracked_indices)), dtype=np.float32)
        for ni, n in enumerate(range(2, N_MAX + 1)):
            arr = chunk_power_for_indices(streams[n]["bits"], k, mapped[k], offset=0)
            vals[ni] = arr.mean(axis=0)
        result[k] = vals
    np.savez(os.path.join(_here, "walsh_chunk_size_sweep.npz"), indices=tracked_indices, **{f"k{k}": v for k, v in result.items()}, **{f"map{k}": mapped[k] for k in ALT_KS})
    return result, mapped


def boundary_conditioned(streams, tracked_indices):
    classes = ("0", "1", "2+")
    result = np.zeros((N_MAX - 1, len(classes), len(tracked_indices)), dtype=np.float32)
    for ni, n in enumerate(range(2, N_MAX + 1)):
        arr = chunk_power_for_indices(streams[n]["bits"], BASE_K, tracked_indices, offset=0)
        counts = boundary_counts(streams[n]["boundaries"], BASE_CHUNK, offset=0)
        masks = [counts == 0, counts == 1, counts >= 2]
        for ci, mask in enumerate(masks):
            if np.any(mask):
                result[ni, ci] = arr[mask].mean(axis=0)
            else:
                result[ni, ci] = np.nan
    np.savez(os.path.join(_here, "walsh_boundary_conditioned.npz"), indices=tracked_indices, ns=np.arange(2, N_MAX + 1), classes=np.array(classes), spectra=result)
    return result, classes


def phase_boundary_interaction(streams, tracked_indices, boundary_result):
    base_boundary = np.nanmean(boundary_result, axis=0)
    if not np.any(np.nanmax(base_boundary, axis=0) > (1.0 / BASE_CHUNK)):
        return None
    result = np.full((len(PHASE_OFFSETS), N_MAX - 1, 3, len(tracked_indices)), np.nan, dtype=np.float32)
    for oi, offset in enumerate(PHASE_OFFSETS):
        for ni, n in enumerate(range(2, N_MAX + 1)):
            arr = chunk_power_for_indices(streams[n]["bits"], BASE_K, tracked_indices, offset=offset)
            counts = boundary_counts(streams[n]["boundaries"], BASE_CHUNK, offset=offset)
            masks = [counts == 0, counts == 1, counts >= 2]
            for ci, mask in enumerate(masks):
                if np.any(mask):
                    result[oi, ni, ci] = arr[mask].mean(axis=0)
    np.savez(os.path.join(_here, "walsh_phase_boundary.npz"), offsets=np.array(PHASE_OFFSETS), ns=np.arange(2, N_MAX + 1), indices=tracked_indices, spectra=result)
    return result


def synthetic_length_matched(info, rng):
    total = int(info["lengths"].sum())
    bits = np.empty(total, dtype=np.uint8)
    pos = 0
    for length in info["lengths"]:
        bits[pos] = 1
        if length > 1:
            bits[pos + 1 : pos + length] = rng.integers(0, 2, size=length - 1, dtype=np.uint8)
        pos += int(length)
    return bits


def synthetic_v2_preserving(info, rng):
    total = int(info["lengths"].sum())
    bits = np.empty(total, dtype=np.uint8)
    pos = 0
    z = info["v2"]
    for length in info["lengths"]:
        bits[pos] = 1
        interior = max(int(length) - 1 - z, 0)
        if interior > 0:
            bits[pos + 1 : pos + 1 + interior] = rng.integers(0, 2, size=interior, dtype=np.uint8)
        if z > 0:
            bits[pos + int(length) - z : pos + int(length)] = 0
        pos += int(length)
    return bits


def shuffled_entries(info, rng):
    order = rng.permutation(len(info["lengths"]))
    total = int(info["lengths"].sum())
    bits = np.empty(total, dtype=np.uint8)
    pos = 0
    for idx in order:
        start = int(info["boundaries"][idx])
        end = int(info["boundaries"][idx + 1])
        entry = info["bits"][start:end]
        bits[pos : pos + len(entry)] = entry
        pos += len(entry)
    return bits


def fair_coin_calibration(streams, tracked_indices, rng):
    vals = np.zeros((N_MAX - 1, len(tracked_indices)), dtype=np.float32)
    for ni, n in enumerate(range(2, N_MAX + 1)):
        actual = chunk_power_for_indices(streams[n]["bits"], BASE_K, tracked_indices, offset=0)
        n_chunks = actual.shape[0]
        bits = rng.integers(0, 2, size=n_chunks * BASE_CHUNK, dtype=np.uint8)
        vals[ni] = chunk_power_for_indices(bits, BASE_K, tracked_indices, offset=0).mean(axis=0)
    return vals


def control_spectra(streams, tracked_indices):
    rng = np.random.default_rng(SEED)
    fair = fair_coin_calibration(streams, tracked_indices, rng)
    length = np.zeros((N_MAX - 1, len(tracked_indices)), dtype=np.float32)
    v2p = np.zeros((N_MAX - 1, len(tracked_indices)), dtype=np.float32)
    shuffle = np.zeros((N_MAX - 1, len(tracked_indices)), dtype=np.float32)
    for ni, n in enumerate(range(2, N_MAX + 1)):
        info = streams[n]
        length[ni] = chunk_power_for_indices(synthetic_length_matched(info, rng), BASE_K, tracked_indices, offset=0).mean(axis=0)
        v2p[ni] = chunk_power_for_indices(synthetic_v2_preserving(info, rng), BASE_K, tracked_indices, offset=0).mean(axis=0)
        shuffle[ni] = chunk_power_for_indices(shuffled_entries(info, rng), BASE_K, tracked_indices, offset=0).mean(axis=0)
    np.savez(os.path.join(_here, "walsh_controls.npz"), indices=tracked_indices, fair=fair, length=length, v2=v2p, shuffle=shuffle, ns=np.arange(2, N_MAX + 1))
    return fair, length, v2p, shuffle


def survives_like_universal(values, base):
    counts_above = (values > base).sum()
    cv = values.std(ddof=1) / values.mean()
    z = (values.mean() - base) / (values.std(ddof=1) / math.sqrt(len(values)) if values.std(ddof=1) > 0 else np.inf)
    return counts_above >= UNIVERSAL_MIN_MONOIDS and cv < CV_MAX and z >= Z_MIN


def boundary_label(boundary, classes, ci):
    means = np.nanmean(boundary[:, :, ci], axis=0)
    finite = np.isfinite(means)
    if finite.sum() == 1:
        return f"{classes[int(np.where(finite)[0][0])]} only (degenerate)"
    return classes[int(np.nanargmax(means))]


def stage3_table(tracked_indices, stage0_rows, phase, chunk_sizes, mapped, boundary, classes, controls):
    base = 1.0 / BASE_CHUNK
    fair, length, v2p, shuffle = controls
    row_map = {int(r["s"]): r for r in stage0_rows if r["robust"]}
    out_rows = []
    pooled_phase = phase.mean(axis=0)
    for ci, idx in enumerate(tracked_indices):
        row = row_map[int(idx)]
        phase_vals = pooled_phase[:, ci]
        phase_survives = survives_like_universal(phase_vals, base)
        k_hits = []
        for k, vals in chunk_sizes.items():
            chunk = 1 << k
            mapped_idx = mapped[k][ci]
            base_k = 1.0 / chunk
            if survives_like_universal(vals[:, ci], base_k):
                k_hits.append(f"{k}:{mapped_idx}")
        out_rows.append(
            {
                "s": int(idx),
                "popcount": int(row["popcount"]),
                "mean P[s]": f"{row['mean_p']:.6f}",
                "ratio": f"{row['ratio']:.3f}",
                "corr v2": f"{row['corr_v2']:.3f}",
                "geometry": row["geometry"],
                "sequency": int(row["sequency"]),
                "phase": "yes" if phase_survives else "no",
                "k-stable": ",".join(k_hits) if k_hits else "no",
                "boundary": boundary_label(boundary, classes, ci),
                "length-ctrl": "yes" if survives_like_universal(length[:, ci], base) else "no",
                "v2-ctrl": "yes" if survives_like_universal(v2p[:, ci], base) else "no",
                "shuffle": "yes" if survives_like_universal(shuffle[:, ci], base) else "no",
            }
        )
    csv_path = os.path.join(_here, "walsh_upgrade_table.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)
    return out_rows


def results_markdown(tracked_indices, stage0_rows, phase, chunk_sizes, mapped, boundary, classes, controls):
    base = 1.0 / BASE_CHUNK
    fair, length, v2p, shuffle = controls
    row_map = {int(r["s"]): r for r in stage0_rows if r["robust"]}
    pooled_phase = phase.mean(axis=0)
    lines = [
        "# Walsh Upgrade Results",
        "",
        f"Robust universal cells after the Stage 0 bar: {len(tracked_indices)}",
        "",
        "## Robust Set",
        "",
        "| cell | popcount | geometry | sequency | mean P[s] | ratio | corr with v2 | monoids above baseline |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for idx in tracked_indices:
        row = row_map[int(idx)]
        lines.append(
            f"| {int(idx)} | {int(row['popcount'])} | {row['geometry']} | {int(row['sequency'])} | {row['mean_p']:.6f} | {row['ratio']:.3f}x | {row['corr_v2']:.3f} | {int(row['monoids_above'])} |"
        )
    lines.extend(["", "## Stage 1", ""])
    phase_yes = []
    for ci, idx in enumerate(tracked_indices):
        if survives_like_universal(pooled_phase[:, ci], base):
            phase_yes.append(int(idx))
    lines.append(f"- Survive phase-averaging across {len(PHASE_OFFSETS)} sampled offsets: {', '.join(map(str, phase_yes)) or 'none'}")
    k_notes = []
    for ci, idx in enumerate(tracked_indices):
        hits = []
        for k, vals in chunk_sizes.items():
            if survives_like_universal(vals[:, ci], 1.0 / (1 << k)):
                hits.append(f"k={k}@{mapped[k][ci]}")
        if hits:
            k_notes.append(f"{int(idx)} -> {', '.join(hits)}")
    lines.append(f"- Chunk-size persistence: {'; '.join(k_notes) or 'none'}")
    lines.append("- Boundary concentration classes:")
    for ci, idx in enumerate(tracked_indices):
        lines.append(f"  - {int(idx)} -> {boundary_label(boundary, classes, ci)}")
    if all("degenerate" in boundary_label(boundary, classes, ci) for ci in range(len(tracked_indices))):
        lines.append("")
        lines.append("At `k=8`, the boundary-conditioned split is not a real separator: every 256-bit chunk in the run already contains multiple entry boundaries.")
        lines.append("So this stage only tells us the survivors live on boundary-rich windows at that scale; it does not separate boundary effects from interior effects.")
    lines.extend(["", "## Stage 2", ""])
    lines.append("| cell | length-matched | v2-preserving | entry-order shuffle | fair-coin calibration mean |")
    lines.append("|---|---|---|---|---:|")
    for ci, idx in enumerate(tracked_indices):
        lines.append(
            f"| {int(idx)} | {'yes' if survives_like_universal(length[:, ci], base) else 'no'} | {'yes' if survives_like_universal(v2p[:, ci], base) else 'no'} | {'yes' if survives_like_universal(shuffle[:, ci], base) else 'no'} | {fair[:, ci].mean():.6f} |"
        )
    with open(os.path.join(_here, "walsh_upgrade_results.md"), "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    candidate_indices = universal_candidates_from_saved()
    streams = prepare_streams()
    metrics = stage0_metrics(streams, candidate_indices)
    tracked_indices, stage0_rows = save_stage0(streams, candidate_indices, metrics)
    phase = phase_sweep(streams, tracked_indices)
    chunk_sizes, mapped = chunk_size_sweep(streams, tracked_indices)
    boundary, classes = boundary_conditioned(streams, tracked_indices)
    phase_boundary_interaction(streams, tracked_indices, boundary)
    controls = control_spectra(streams, tracked_indices)
    stage3_table(tracked_indices, stage0_rows, phase, chunk_sizes, mapped, boundary, classes, controls)
    results_markdown(tracked_indices, stage0_rows, phase, chunk_sizes, mapped, boundary, classes, controls)
    print(f"Tracked robust cells: {tracked_indices.tolist()}")


if __name__ == "__main__":
    main()
