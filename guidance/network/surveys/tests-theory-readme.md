# tests/theory/README.md — Theorem Index

source: [`tests/theory/README.md`](../../../tests/theory/README.md)  
cited in: [`COLLECTION.md` — The Generator](../../../COLLECTION.md#chapter-2-the-generator)  
last reviewed: 2026-04-10

---

**Bridges.** Proved claims to the executable pass/fail tests
that would falsify them, and to the experiment-side visual
witnesses that show the behavior. One table, one row per
theorem, four columns: *Result* (the claim), *Proof* (the doc
under `core/`), *Theory test* (the file under `tests/theory/`
that attacks the claim), *Experiment* (the script under
`experiments/bidder/` that renders it).

**Presents.** Tabular. The rows are the structural
permutation-invariance theorem, the Euler–Maclaurin rate rows,
the finite-population correction, the cipher coupling gap, the
integer-block and sieved-block lemmas, the spread bound, the
Hardy closed form, and the abductive key. Each row pins
exactly one falsification criterion to exactly one test file.
The doc is the authoritative map between the prose in `core/`
and the tests in `tests/theory/`; if the two disagree, this
table is where the disagreement surfaces.

**Excludes.** The tests themselves (they live in the test
files). The experiments (they live under `experiments/`). The
red-team posture that the tests embody — that lives in
[`red-team-theory.md`](red-team-theory.md), to which this doc
defers for the four-layer decomposition and the "isolate
permutation facts from cipher-quality facts" discipline. The
"honest gaps" row is the distinctive move: `ABDUCTIVE-KEY.md`
has no theory test, and the absence is named as a gap rather
than papered over.

**See also.** [`red-team-theory.md`](red-team-theory.md) —
the organizing document for the four-layer decomposition.
[`riemann-sum.md`](riemann-sum.md) — the theorem with the
densest test coverage (three files).
[`block-uniformity.md`](block-uniformity.md) — the lemma
whose four test names are indexed here
(`test_block_uniformity_sieved_*`).
[`hardy-sidestep.md`](hardy-sidestep.md) — the closed form
verified by `test_sawtooth.py` and the companion
`core/hardy_sidestep.py` harness.
