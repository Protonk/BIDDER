# Deep Trouble No. 4

## ⚠️ STATUS UPDATE (Hardy is a bijection)

The "deep-field microscope" framing below was the right *instrument*
framing for order-dependent observables (Mode 2: digit-position
oracle; Mode 3: block-boundary probe; Mode 4: tail destroyer for
position-anchored claims). It was the **wrong** framing for
substrate-only Q_n / depth-invariance questions, because for prime n,

    c(K, n) := p_K(n) / n  =  qn + r + 1,  (q,r) = divmod(K-1, n-1)

is just the order-preserving bijection from `Z_{≥1}` to
`{c : n ∤ c}`. Sampling cofactors via Hardy at any K is the same as
sampling the K-th integer coprime to n in magnitude order — there is
no "deep" axis to vary that the substrate hasn't already collapsed.

See `experiments/math/hardy/SURPRISING-DEEP-KEY.md` for the full
write-up: the depth-invariance experiments did not test depth, they
verified the bijection. The genuine number-theoretic content the
experiments did surface is the multiplicative-divisor correlation
`E[d(c_1 c_2)]` for cofactors at growing magnitude — Erdős /
Tenenbaum territory on integers coprime to n.

Modes 2/3/4 below are still the right framing for **order-dependent**
questions: digit-position into the concatenated real, radix-block
counts, position-anchored prefix-era visuals. Mode 1 (atom-only deep
windows) and any "deep Q_n at atoms" reading are substrate-only and
should be read through `SURPRISING-DEEP-KEY.md` rather than as a
deep-field instrument. The atoms-only caveat at the end of this doc
already flags that nontrivial-rank Q-tests need composite m and
recommends the right deep-Q sanity loop.

For the local algebra see `algebra/Q-FORMULAS.md` and
`algebra/FINITE-RANK-EXPANSION.md`.

---

Hardy Sidestep changes the experimental posture. We do not have to
stand at the start of an ACM-Champernowne stream and watch prefixes
grow. For `n >= 2`, the K-th n-prime is closed form:

    p_K(n) = n * (q*n + r + 1),
    q, r = divmod(K - 1, n - 1).

That means we can sample deep in the dark: jump to an index, digit
depth, or block boundary far beyond enumeration, open a small window,
and ask whether the same structures echo there.

The goal is one unified tool with four modes, not four independent
one-offs.


## The Instrument

Working name:

    hardy_echo.py

Core primitive:

    window(n, K0, W) = p_K0(n), p_{K0+1}(n), ..., p_{K0+W-1}(n)

computed by Hardy random access, not prefix enumeration. Every mode
then renders or summarizes that local window.

Shared outputs:

- window metadata: `n`, `K0`, `W`, base `b`, digit-depth or block if
  relevant;
- entry table: K, n-prime, cofactor, digit length, boundary position;
- bit/digit stream over the window;
- local observables: running mean, RLE, Hamming, boundary stitch,
  Walsh/entropy if requested;
- destroyer controls: shuffle entries inside the same window,
  preserve lengths when needed, compare to matched early-prefix view.

The question is always the same: does a structure seen near the origin
reappear deep in the stream once the obvious local background is
matched?


## BQN Annotation

This is exact-math annotation for the shared window object. It mirrors `experiments/math/hardy/hardy_echo.py`
and the closed form in `core/HARDY-SIDESTEP.md`. The `n = 1` ordinary
prime branch is out of scope.

```bqn
NthNPn2 ← {
  k ← 𝕩-1
  q ← ⌊ k ÷ (𝕨-1)
  r ← (𝕨-1)|k
  𝕨 × 1 + r + 𝕨 × q
}

HWindow ← {
  k0‿w ← 𝕩
  𝕨 NthNPn2¨ k0+↕w
}
```

`NthNPn2` is the Hardy sidestep: left argument `𝕨` is `n >= 2`,
right argument `𝕩` is the one-indexed entry `K`. `HWindow` is Mode 1:
given `n` and `(K0,W)`, return the local run of n-primes without
enumerating the prefix.

Digit streams are a separate layer on the same window:

```bqn
DigitsB ← {𝕩<𝕨 ? ⟨𝕩⟩ ; (𝕨 𝕊 ⌊𝕩÷𝕨)∾⟨𝕨|𝕩⟩}
DLenB   ← {≠ 𝕨 DigitsB 𝕩}
DStream ← {⥊ 𝕨 DigitsB¨ 𝕩}
V2      ← {0=2|𝕩 ? 1+𝕊⌊𝕩÷2 ; 0}
```

`DStream` gives the exact base-`b` digit stream of a Hardy window.
`V2` names the binary trailing-zero invariant used by boundary stitch;
entry-shuffling preserves it because it is per entry, not per position.

Block and digit-position modes use the same inverse. For a lower value
bound `L`, first compute the least multiplier `k >= ceil(L/n)` not
divisible by `n`, then convert that multiplier to its one-indexed
n-prime position.

```bqn
CeilDiv  ← {⌈𝕩÷𝕨}
NextGood ← {0=𝕨|𝕩 ? 𝕩+1 ; 𝕩}

KOfMult ← {
  q ← ⌊𝕩÷𝕨
  r ← 𝕨|𝕩
  r + q × 𝕨-1
}

KFirstGE ← {
  c ← 𝕨 CeilDiv 𝕩
  k ← 𝕨 NextGood c
  𝕨 KOfMult k
}

KLastLT ← {¯1 + 𝕨 KFirstGE 𝕩}

BlockK ← {
  b‿d ← 𝕩
  lo ← b⋆d-1
  hi ← b⋆d
  (𝕨 KFirstGE lo)‿(𝕨 KLastLT hi)
}
```

`BlockK` is Mode 3: it gives the inclusive K-range for entries in the
radix block `[b^(d-1), b^d)`. Mode 2 subtracts whole digit-length
blocks using `BlockK`, then divides the residual digit offset by `d`.
Destroyer controls are not BQN objects here; they are experimental
protocols applied to the same `HWindow` payload.


## Mode 1 — Deep Window

Pick `(n, K0, W)` and build the local n-prime window directly.

Use it for:

- RLE spectroscopy at large K;
- boundary stitch far from the origin;
- Hamming / bit-balance windows after the early digit-length regime;
- Walsh cells on deep chunks.

This is the first tail-destroyer for the visual forest. A structure
that survives at `K0 = 10^12`, `10^50`, or `2^4096` is not an
early-prefix artifact. A structure that vanishes was probably local
startup geometry.

A particularly sharp test of the boundary-stitch claim from
`experiments/acm-champernowne/base2/forest/boundary_stitch/`:
the trailing-zero `v_2(n)` barcode is closed-form arithmetic, so
it should persist verbatim at `K0 = 10^50`. The right-side
bit-length-class gradient depends on the local digit-length regime
of `p_K`, which evolves with `K`. A clean separation — algebra-side
persists, position-side either persists, shifts, or dies — is itself
a finding.


## Mode 2 — Digit-Position Oracle

Given a stream digit position `i`, locate the entry containing that
position, then open a small Hardy window around it.

The inverse can be exact by digit-length blocks. Use Mode 3's
`K_for_block(n,b,d)` to count how many n-primes have base-`b` digit
length `d`; subtract whole blocks until the target digit position lands
inside one block; then divide the residual by `d` to recover the entry
index and offset.

Use it for:

- asking what the ACM-Champernowne real looks like at digit depth
  `10^100`;
- sampling local digit fabrics without materializing the prefix;
- separating digit-depth effects from entry-index effects.

This is the natural bridge from "K-th n-prime" to "digit at position
i of the real."


## Mode 3 — Block Boundary Probe

Given `(b, n, d)`, jump to n-primes near the radix block

    [b^(d-1), b^d).

Instead of generating all earlier entries, estimate the relevant K
from the closed form and refine locally. Then inspect the entries
just before, inside, and after the block.

Use it for:

- testing `core/BLOCK-UNIFORMITY.md` far beyond small d;
- probing the CF-spike boundary mechanism directly;
- checking whether the `(n - 1)/n^2` density factor emerges from
  actual block-local counts;
- comparing smooth, Family E, and uncertified blocks at absurd size.

This mode is where Hardy Sidestep touches the base-10 spike work
most directly. It is the verification harness that
`experiments/acm/flow/STRUCTURE-HUNT.md` Phase 3.1 needs: derive
the CF-spike formula from `Q_n` (`algebra/Q-FORMULAS.md`,
`algebra/FINITE-RANK-EXPANSION.md`) at small `d`, then check the
prediction at `d = 50` or `d = 100` via Mode 3 without
materializing the Champernowne real to that depth.


## Mode 4 — Tail Destroyer

Take any existing prefix-era claim and re-run it in matched deep
windows.

Default protocol:

1. choose an early-prefix artifact and its local observable;
2. choose deep windows with matched local digit length / bit length;
3. compute the same observable;
4. shuffle entries within each deep window as the null;
5. report whether the signal survives, weakens, reverses, or dies.

Candidate claims:

- binary RLE ridges by `v_2(n)`;
- boundary-stitch trailing-zero barcode and right-side gradient;
- Walsh robust cells and their shuffle death;
- Morlet/RDS notches;
- base-10 CF spike neighborhood structure.

This mode is deliberately destructive. It tells us which visuals
were origin effects and which are stream laws.

This mode is the "destroyer" half of
`experiments/VISUAL-REDUCTION-DISCIPLINE.md`. The Phase 1 destroyers
in `experiments/acm/flow/phase1_destroyers.py` shuffled prefix data
within fixed-size cells; Mode 4 generalises that to arbitrary
prefix-era visuals re-run at arbitrary depth, with the same
shuffle-null discipline.


## Unified Read

The four modes are one experiment if they share the same local-window
object. The difference is only how the window is chosen:

| mode | choose window by | asks |
|---|---|---|
| Deep Window | entry index K | does the structure persist in the tail? |
| Digit Oracle | digit position i | what lives at this depth in the real? |
| Block Probe | radix block `(b,d)` | what happens at a positional boundary? |
| Tail Destroyer | matched old claim | was the old signal a prefix artifact? |

If these cohere, Hardy Sidestep becomes the dark-field microscope for
ACM-Champernowne: it does not prove the structure by itself, but it
lets us interrogate arbitrarily distant places where prefix methods
cannot go.

**Out of scope for v1.** Walsh-Hadamard spectra, Morlet / wavelet
scalograms, continued-fraction expansions, and any other observable
that requires a coherent global frame (rather than just a local
window) are *not* in the first build. They can be added later as
post-processors on the unified window object; v1 is the window
primitive plus simple per-window observables (RLE, boundary stitch,
Hamming, bit/digit balance) and the entry-shuffle null.


## First Pass

Build the minimal tool in this order:

1. implement `window(n, K0, W)` using the Hardy closed form;
2. **smoke check**: assert `window(n, 1, W)` matches the existing
   enumerator `acm_n_primes(n, W)` from `core/acm_core.py` for
   `n ∈ {2, 3, 4, 5, 6, 10}` and `W ≤ 200`. The closed form is
   one-line arithmetic; the smoke check pins it against the working
   pipeline before any visualisation runs on top.
3. emit base-2 and base-10 digit streams for the window;
4. add RLE and boundary stitch summaries;
5. add entry-shuffle destroyer;
6. add digit-position inversion;
7. add block-boundary inversion.

Do not start with Walsh, Morlet, or CF. Start with the observables
whose prefix versions already have clear destroyers.


## Speculation

If the finite-rank expansion is the local arithmetic closure, Hardy
windows are the global sampling mechanism. Together they suggest a
two-part near-closure:

    local arithmetic closes by rank;
    global stream evidence is tested by deep random access.

The first tells us what the local object is. The second tells us
whether the object keeps echoing after the origin is gone.

`algebra/FINITE-RANK-EXPANSION.md` gives the local side; `algebra/Q-FORMULAS.md`
specialises it into explicit closed forms per `(h, n_type)`. Hardy
echo gives the global side.

**Caveat — atoms only.** Hardy random access returns *atoms* of
`M_n` (n-primes), all of which have height `ν_n(p_K(n)) = 1` and
trivially `Q_n(atom) = 1`. Nontrivial-rank Q-tests at depth therefore
require *composite* `M_n` elements: products `m = p_{K_1}(n) · p_{K_2}(n)`
or higher, sampled by Hardy on each factor. The right deep-Q
sanity loop is:

1. choose `(K_1, K_2)` deep (or any tuple);
2. compute `m = ∏ p_{K_i}(n)` and `h = ν_n(m)` (here equals the
   tuple length);
3. evaluate the closed form from `algebra/Q-FORMULAS.md` and assert
   exact `Fraction` agreement with the master expansion's direct
   evaluation.

If those agree at `K_i = 10^50`, the finite-rank lemma is checked
at scales no prefix method can reach.
