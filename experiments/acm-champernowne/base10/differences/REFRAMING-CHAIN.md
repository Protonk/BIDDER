# The reframing chain — a meta-note on EXP01-07

The seven experiments in this directory were not a sequence of
hypothesis-driven probes. They were a **reframing chain**: each null
or walked-back result triggered an external reframing, and each
reframing made invisible findings visible in the next experiment,
which then produced its own walked-back result, driving the next
reframing.

This is worth naming because it's a pattern that doesn't work
internally — the reframings each came from *outside* the empirical
loop (a user's pushback, a theoretical conjecture, a structural
intuition). The agent layer's experiments pile up nulls until a
reframing arrives. This note records the chain so future
differencing-flavoured work can recognise the pattern early.

## The chain

```
EXP01 (digit frequency)         → null + tail-leak artifact
EXP02 (continued fraction)      → null (generic by every CF metric)
                                  ↓
                          REFRAMING 1: differencing as transducer
                          (DIFFERENCING-AS-TRANSDUCER.md)
                                  ↓
EXP03 (digit-pair correlations) → weak residual (χ² 110)
EXP04 (random subset control)   → panel-specific signal (z = +2.21)
EXP05 (parameter sweep)         → walks back EXP04: signal panel-specific
                                  ↓
                          REFRAMING 2: optimizer / multiplicity
                          (in conversation, not yet documented)
                                  ↓
EXP06 (multi-tongue)            → falsifies "preservation" claim;
                                   each multiplicity has its shape
                                  ↓
                          REFRAMING 3: source-stream stratification
                          (in conversation, not yet documented)
                                  ↓
EXP07 (source-stream)           → digit-3 spike is finite-k
                                   truncation artifact in d ∈ {8,9,10}
```

Three reframings, each followed by 1–2 experiments that produced
findings the previous frame could not have detected.

## What each reframing made visible

### Reframing 1: differencing as transducer

**Frame before**: δ = C_Bundle − C_Surv is a real number with
properties to measure. EXP01-02 measured digit frequency and
continued fraction, both came back null.

**Frame after**: differencing on digit-concatenated streams of
*different lengths* aligns them by digit position rather than by
atom. After the first divergence, every digit-position subtraction
compares unrelated atoms' digits. The output is generic by
construction.

**What became visible**: the random-subset baseline (EXP04). Once
we knew that *any* subtraction of two digit-misaligned streams
produces the borrow signature, comparing survivor's δ to random
subsets' δ became the relevant question — not comparing δ to
uniform.

### Reframing 2: optimizer / multiplicity

**Frame before**: the survivor filter has a "specific" signature
(EXP04). EXP05 asked whether this specificity holds across panels
and found it didn't.

**Frame after**: survivors are the output of an information-theoretic
optimizer (`H(stream | integer) = 0`). Higher multiplicities
(`m = 2, 3, ...`) have `H > 0`. The selection criterion is
parameter-invariant; the question is whether the selection's
*output property* (leading-digit content) is.

**What became visible**: the multi-tongue plot (EXP06). Once
multiplicity was the axis, partitioning the bundle by `m ∈ {1, 2,
3, ≥4}` revealed that each multiplicity has its own characteristic
leading-digit shape — and that the L1 tracking observed in Two
Tongues is at the *magnitude* level only, with shape differences
hidden underneath.

### Reframing 3: source-stream stratification

**Frame before**: each multiplicity has its shape (EXP06). Survivors
specifically over-represent digit 3 (20.4% vs bundle's 12.4%). Why?

**Frame after**: every survivor has a unique source stream `d`. If
the digit-3 spike comes from a specific subset of source streams,
the spike is localizable.

**What became visible**: EXP07's astonishingly clean stratification.
`P_d(3)` per source stream: 0–8% for `d ∈ [2..6]`, 16% for `d=7`,
36/41/49% for `d ∈ {8, 9, 10}`. Plus a structural argument: there
are no *true* `d=10`-only survivors at all (the constraints force
`160 | m` AND `10 ∤ m`, which is impossible). The 136 apparent
`d=10` survivors are *finite-k truncation artifacts* — integers
`c = 10m` whose alternative-stream atom (typically `n=5`) had rank
> `k=400` and was excluded from the bundle.

## The walking-back, in summary

Each reframing also *walked back* the previous reading:

```
EXP04: "survivor is special at z = +2.21"
EXP05 walked back to: "special only at this panel"
                                  ↓
EXP06: "each multiplicity has its shape, richness is at shape level"
EXP07 walked back to: "the shape difference is finite-k truncation
                       in 3 source streams; in the k → ∞ limit,
                       the spike disappears"
```

The walkbacks aren't failures. Each one *sharpens* the structural
claim. The current state, after EXP07: the bundle/survivor relation
is **more tightly constrained** than EXP04 suggested — what looked
like survivor-specific richness was mostly the imprint of the
truncation parameter `k`, projected through specific source streams.
The L1 tracking in Two Tongues is real, but at the magnitude level,
and what appeared to be perpendicular richness was largely
truncation imprint.

## What this implies

1. **For this work**: the cabinet's Two Tongues curiosity entry
   needs revising. The "rich and persistent" framing should become
   something more like "L1-magnitude tracking persistent; perpendicular
   richness mostly k-truncation artifact." The curiosity stays a
   curiosity; its provocations sharpen.

2. **For other differencing-flavoured questions**: the pattern is a
   warning. If the first 2-3 experiments come back null and the
   transducer note is the diagnosis, that's not a setback — it's
   the project asking for a structural reframing. Don't burn cycles
   on a fourth digit-frequency probe; instead, look for the next
   external frame to apply.

3. **For the agent layer**: the experiments alone could not generate
   the reframings. The "external" reframings — transducer (user),
   optimizer (user), source-stream (agent under prompting) — were
   the ones that drove discovery. The agent's empirical work
   verified, refined, and walked back, but did not initiate. This
   is structural, not a deficit. Designs that expect the agent to
   self-direct here will under-perform; designs that pair empirical
   capacity with external framing land much better.

   *Editorial caveat:* the "came from outside the empirical loop"
   claim is editorial — it reflects the conversational record but
   isn't strictly verifiable from file timestamps and contents
   alone. A future audit pass with access to the chat record could
   verify; from artifacts alone, the chronology is consistent with
   this reading but doesn't prove it.

## Cross-references

- `EXP01-FINDINGS.md`, `EXP02-FINDINGS.md` — the initial nulls.
- `DIFFERENCING-AS-TRANSDUCER.md` — Reframing 1.
- `EXP03-FINDINGS.md` — first weak residual after Reframing 1.
- `EXP04-FINDINGS.md`, `EXP05-FINDINGS.md` — random-control
  observation and walkback.
- `EXP06-FINDINGS.md` — first finding after Reframing 2.
- `EXP07-FINDINGS.md` — finding after Reframing 3, walks back EXP06.
- `wonders/curiosity-two-tongues.md` — cabinet entry that the
  whole chain has been refining; due for an audit.
