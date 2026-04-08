"""
tree_signatures.py — substrate cache for the Valuation Forest expedition.

For each monoid n in 1..N_ANALYTIC, generate the binary ACM stream,
truncate to an exact TARGET_BITS prefix, and cache the per-monoid
statistics V1/V2/V3 read. The cache is the source of truth: no viz
script ever recomputes a stream.

Stored fields:

  ns                int   (N,)        monoid index
  v2                int   (N,)        2-adic valuation
  odd_part          int   (N,)        m, where n = m * 2^v2
  bits_used         int   (N,)        exact prefix length used (= TARGET_BITS)
  entries_used      int   (N,)        # ACM entries needed to reach TARGET_BITS
  mean_rle0         float (N,)        mean zero-run length on the prefix
  mean_rle1         float (N,)        mean one-run length on the prefix
  mean_rle0_audit   float (N,)        mean zero-run length on first AUDIT_BITS
  mean_rle0_delta   float (N,)        mean_rle0 - mean_rle0_audit
  rle0_block_means  float (N, BLOCKS) per-block mean zero-run length
  entropy_def       float (N,)        1 - H_8 / 8 on the prefix
  rle0_hist         float (N, 16)     normalized zero-run-length histogram;
                                      bins are lengths 1..16, with bin 16
                                      absorbing runs >= 16, so each row sums to 1
  walsh_t1          float (N,)        walsh tier-1 brightness (NaN outside 2..32)
"""

import sys
import os
import math
import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_here, '..', '..'))                                 # base2/
sys.path.insert(0, os.path.join(_here, '..', '..', '..', '..', '..', 'core'))       # core/

from acm_core import acm_n_primes


# ── Parameters ───────────────────────────────────────────────────────

N_RENDER = 512
N_ANALYTIC = 4096
TARGET_BITS = 100_000
AUDIT_BITS = 10_000
BLOCKS = 8
BLOCK_BITS = TARGET_BITS // BLOCKS    # 12_500
HIST_MAX = 16
ENTROPY_K = 8

# Tier-1 cells from forest/walsh/WALSH.md
WALSH_TIER1 = (30, 69, 71, 143, 162, 163, 180, 246, 255)


# ── Bit-packing helper ───────────────────────────────────────────────
# bin(p)[2:].encode('ascii').translate(_TRANSLATE) -> bytes of 0/1

_TRANSLATE_BUF = bytearray(256)
_TRANSLATE_BUF[ord('0')] = 0
_TRANSLATE_BUF[ord('1')] = 1
_TRANSLATE = bytes(_TRANSLATE_BUF)


def _bits_of(p):
    return bin(p)[2:].encode('ascii').translate(_TRANSLATE)


# ── Number-theoretic helpers ─────────────────────────────────────────

def v2_of(n):
    v = 0
    while n % 2 == 0:
        v += 1
        n //= 2
    return v


def odd_part_of(n):
    while n % 2 == 0:
        n //= 2
    return n


def estimate_count(n, target_bits):
    """How many entries to ask acm_n_primes for, before doubling."""
    if n == 1:
        # i-th prime ~ i ln i; bit length ~ log2(i ln i) ~ 13 for first ~10k.
        return max(int(target_bits / 13) + 200, 500)
    avg = math.log2(max(n, 2)) + math.log2(max(target_bits // 20, 4))
    return int(target_bits / max(avg, 4)) + 200


def gen_exact_bits(n, target_bits):
    """Generate exactly target_bits bits of the binary ACM stream for monoid n.

    Returns (bits_uint8_array, entries_used).
    """
    count = estimate_count(n, target_bits)
    while True:
        primes = acm_n_primes(n, count)
        chunks = []
        running = 0
        entries_used = 0
        for p in primes:
            b = _bits_of(p)
            chunks.append(b)
            running += len(b)
            entries_used += 1
            if running >= target_bits:
                buf = b''.join(chunks)[:target_bits]
                return np.frombuffer(buf, dtype=np.uint8), entries_used
        count *= 2


# ── RLE / entropy primitives ─────────────────────────────────────────

def rle_runs(bits):
    """Return (values, lengths) arrays for runs in a 0/1 sequence."""
    if bits.size == 0:
        return np.zeros(0, dtype=np.uint8), np.zeros(0, dtype=np.int64)
    diff = np.diff(bits.astype(np.int16))
    change_idx = np.flatnonzero(diff) + 1
    starts = np.concatenate(([0], change_idx))
    ends = np.concatenate((change_idx, [bits.size]))
    lengths = (ends - starts).astype(np.int64)
    values = bits[starts]
    return values, lengths


def mean_run_length(bits, target_value):
    values, lengths = rle_runs(bits)
    sel = lengths[values == target_value]
    if sel.size == 0:
        return 0.0
    return float(sel.mean())


def block_mean_rle0(bits):
    out = np.zeros(BLOCKS, dtype=np.float64)
    for b in range(BLOCKS):
        chunk = bits[b * BLOCK_BITS:(b + 1) * BLOCK_BITS]
        out[b] = mean_run_length(chunk, 0)
    return out


def rle0_histogram(bits):
    """Bins are lengths 1..HIST_MAX. Runs of length >= HIST_MAX are folded
    into the last bin so the returned row sums to 1.0 whenever any
    zero-run exists."""
    values, lengths = rle_runs(bits)
    zlens = lengths[values == 0]
    if zlens.size == 0:
        return np.zeros(HIST_MAX, dtype=np.float64)
    capped = np.clip(zlens, 1, HIST_MAX)
    counts = np.bincount(capped, minlength=HIST_MAX + 1)
    return counts[1:HIST_MAX + 1].astype(np.float64) / zlens.size


def entropy_deficit_k8(bits):
    n = bits.size
    if n < ENTROPY_K:
        return 0.0
    bits32 = bits.astype(np.int32)
    n_windows = n - ENTROPY_K + 1
    windows = np.zeros(n_windows, dtype=np.int32)
    for j in range(ENTROPY_K):
        windows = (windows << 1) | bits32[j:j + n_windows]
    counts = np.bincount(windows, minlength=256)
    p = counts[counts > 0] / counts.sum()
    H = -float(np.sum(p * np.log2(p)))
    return 1.0 - H / ENTROPY_K


# ── Main ─────────────────────────────────────────────────────────────

print(f"Computing per-monoid signatures for n = 1..{N_ANALYTIC}")
print(f"  target {TARGET_BITS} bits, audit {AUDIT_BITS} bits, "
      f"{BLOCKS} blocks of {BLOCK_BITS} bits, k={ENTROPY_K}")

ns = np.arange(1, N_ANALYTIC + 1, dtype=np.int64)
v2_arr = np.empty(N_ANALYTIC, dtype=np.int32)
odd_arr = np.empty(N_ANALYTIC, dtype=np.int64)
bits_used = np.empty(N_ANALYTIC, dtype=np.int64)
entries_used = np.empty(N_ANALYTIC, dtype=np.int64)
mean_rle0 = np.empty(N_ANALYTIC, dtype=np.float64)
mean_rle1 = np.empty(N_ANALYTIC, dtype=np.float64)
mean_rle0_audit = np.empty(N_ANALYTIC, dtype=np.float64)
rle0_block_means = np.empty((N_ANALYTIC, BLOCKS), dtype=np.float64)
entropy_def = np.empty(N_ANALYTIC, dtype=np.float64)
rle0_hist = np.empty((N_ANALYTIC, HIST_MAX), dtype=np.float64)

for i in range(N_ANALYTIC):
    n = i + 1
    v2_arr[i] = v2_of(n)
    odd_arr[i] = odd_part_of(n)
    bits, ent = gen_exact_bits(n, TARGET_BITS)
    bits_used[i] = bits.size
    entries_used[i] = ent
    mean_rle0[i] = mean_run_length(bits, 0)
    mean_rle1[i] = mean_run_length(bits, 1)
    mean_rle0_audit[i] = mean_run_length(bits[:AUDIT_BITS], 0)
    rle0_block_means[i] = block_mean_rle0(bits)
    entropy_def[i] = entropy_deficit_k8(bits)
    rle0_hist[i] = rle0_histogram(bits)
    if i == 0 or (i + 1) % 256 == 0:
        print(f"  {i+1:5d}/{N_ANALYTIC}  n={n}  v2={int(v2_arr[i])}  "
              f"mean_rle0={mean_rle0[i]:7.3f}  ent_def={entropy_def[i]:.4f}")

mean_rle0_delta = mean_rle0 - mean_rle0_audit


# ── Walsh tier-1 brightness (NaN outside 2..32) ──────────────────────

walsh_t1 = np.full(N_ANALYTIC, np.nan, dtype=np.float64)
walsh_npz_path = os.path.join(_here, '..', 'walsh', 'walsh_spectra.npz')
if os.path.exists(walsh_npz_path):
    walsh = np.load(walsh_npz_path)
    walsh_ns = walsh['ns']
    walsh_spectra = walsh['spectra']
    tier1_idx = list(WALSH_TIER1)
    for w_i, w_n in enumerate(walsh_ns):
        nn = int(w_n)
        if 1 <= nn <= N_ANALYTIC:
            walsh_t1[nn - 1] = float(walsh_spectra[w_i, tier1_idx].sum())
    valid = np.isfinite(walsh_t1)
    rng = (int(np.where(valid)[0].min()) + 1, int(np.where(valid)[0].max()) + 1)
    print(f"\nWalsh tier-1 brightness populated for n in {rng[0]}..{rng[1]}")
else:
    print(f"\nWalsh spectra not found at {walsh_npz_path} — walsh_t1 will be NaN")


out_path = os.path.join(_here, 'tree_signatures.npz')
np.savez(
    out_path,
    ns=ns,
    v2=v2_arr,
    odd_part=odd_arr,
    bits_used=bits_used,
    entries_used=entries_used,
    mean_rle0=mean_rle0,
    mean_rle1=mean_rle1,
    mean_rle0_audit=mean_rle0_audit,
    mean_rle0_delta=mean_rle0_delta,
    rle0_block_means=rle0_block_means,
    entropy_def=entropy_def,
    rle0_hist=rle0_hist,
    walsh_t1=walsh_t1,
)
print(f"\nWrote {out_path}")


# ── Quick sanity check ──────────────────────────────────────────────

print("\n=== Sanity check ===")
print(f"  N = {N_ANALYTIC}")
print(f"  exact bits per monoid: {int(bits_used.min())}..{int(bits_used.max())}")
print(f"  entries used: {int(entries_used.min())}..{int(entries_used.max())}")
print(f"  mean_rle0 range: {mean_rle0.min():.3f} .. {mean_rle0.max():.3f}")
print(f"  mean_rle0 by v_2:")
for t in range(int(v2_arr.max()) + 1):
    mask = (v2_arr == t)
    cnt = int(mask.sum())
    if cnt == 0:
        continue
    print(f"    v_2={t:2d}  n={cnt:4d}  "
          f"mean={mean_rle0[mask].mean():7.3f}  "
          f"std={mean_rle0[mask].std():7.3f}")
abs_delta = np.abs(mean_rle0_delta)
print(f"  |mean_rle0 - audit| max={abs_delta.max():.4f}  "
      f"mean={abs_delta.mean():.4f}")
print("Done.")
