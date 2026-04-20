# F1-HYPO-PLAN

Working plan for SECOND-PROOF §3 (F1): which polynomial-tail
induced-operator framework matches BS(1,2), and what it takes
to instantiate its hypotheses.

This is a disposable doc. Once we have enough clarity, the
useful bits fold back into SECOND-PROOF §3 (F1) and the
framework-reference list in SECOND-PROOF's §References. The
archival record of why we picked one citation over another
stays here.

Date: 2026-04-20. Based on reading the three candidates:

- `sources/Melbourne-Terhesiu-2012-operator-renewal-infinite-measure.pdf`
- `sources/Gouezel-2004-sharp-polynomial-decay-correlations.pdf`
- `sources/Young-1999-recurrence-times-rates-of-mixing.pdf`

(Sarig 2002 not downloaded because M–T and Gouëzel together
cover his content — he's cited as the predecessor that they
generalize. If we need him later we pull him then.)

---

## 1. The three frameworks at a glance

Exponent β is the return-tail exponent: P(τ > n) ~ C/n^β.

| Paper          | tail range        | Invariant measure              | Main output                                                           |
|----------------|-------------------|--------------------------------|-----------------------------------------------------------------------|
| Young 1999     | uses m{R̂ > n}, not the base-return tail m{R > n}; still needs ∫R dm < ∞ | Probability | ‖F^n_* λ − ν‖ = O(n^{−α}) when m{R̂ > n} = O(n^{−α})                 |
| Gouëzel 2004   | β > 1             | Probability                    | Cor(f, g ∘ T^n) ~ (Σ_{k>n} m[φ > k]) ∫f ∫g + sharp error              |
| Melbourne–Terhesiu 2012 | β ∈ (0, 1]   | σ-finite (infinite)           | Theorem 2.1 for β ∈ (1/2, 1]; weaker boundary/subsequence statements for β ≤ 1/2 |

**Our case:** empirically P(τ_R > n) ~ n^{−0.495}. That is β = 1/2,
which is the boundary between infinite-mean (β ≤ 1) and
finite-mean (β > 1) return time.

Consequences for the three papers:

- **Young 1999 does not apply off-the-shelf.** His Theorem 1
  (existence of invariant probability) requires ∫R dm < ∞,
  which needs the base-return tail to be summable. At β = 1/2
  the total tower measure Σ_ℓ m(Δ_ℓ) = Σ_ℓ P(R > ℓ) ~
  Σ_ℓ ℓ^{−1/2} diverges. Also, his convergence theorem is stated
  in terms of m{R̂ > n}, not directly in terms of the base-return
  tail m{R > n}, so his exponent bookkeeping is not on the same
  axis as M–T's.
- **Gouëzel 2004 does not apply.** His Theorem 1.1 assumes
  β > 1 explicitly. At β = 1/2 his machinery gives nothing.
- **Melbourne–Terhesiu 2012 applies.** β = 1/2 is inside their
  range, but at the boundary case. Their clean operator
  asymptotic (Theorem 2.1) is for β ∈ (1/2, 1]. At β = 1/2 they
  give Theorem 2.2(a), an upper bound with a log correction, and
  Theorem 2.3, which recovers a density-zero subsequence limit
  and a liminf statement for positive observables.

So the short answer is: M–T is the primary framework. Young and
Gouëzel are out of range at β = 1/2.

---

## 2. What M–T gives us at β = 1/2

Theorem 2.2(a) at β = 1/2 gives

    T_n ≪ ℓ(n) · n^{−1/2} ∫_{1/n}^π ℓ(1/θ)^{−2} θ^{−1} dθ.

If the slowly varying factor ℓ is asymptotically constant (the
natural reading of our measured tail), the integral is
(log n)(1 + o(1)) and we get

    T_n ≪ n^{−1/2} log n.

That is the baseline full-sequence upper bound.

M–T also gives more than that at the boundary. Theorem 2.3 says:

- for each y ∈ Y and v ∈ B, there is a density-zero set E such
  that along n ∉ E,

      ℓ(n) n^{1/2} (T_n v)(y) → d_{1/2} ∫_Y v dμ;

- if v ≥ 0, then

      lim inf ℓ(n) n^{1/2} T_n v = d_{1/2} ∫_Y v dμ

  pointwise on Y.

So β = 1/2 is not just an upper-bound desert. M–T still recovers
the n^{−1/2} scale along a density-one subsequence and in a
pointwise-liminf sense. What it does *not* give, without extra
hypotheses, is the clean full-sequence operator asymptotic of
Theorem 2.1.

For our purposes, that creates three levels of output:

1. **Accept the log as the proof-grade full-sequence bound at
   the renewal-operator level.** If the rest of the proof
   pipeline (return-to-full-walk translation + identification of
   the mantissa marginal) closes without additional losses, the
   theorem-scale statement would become O(n^{−1/2} log n)
   instead of ∼ B(ν)·n^{−1/2}. Weaker statement but still
   Benford convergence, still paper-grade.
2. **Record Theorem 2.3 as partial boundary-case structure.**
   Useful for fairness and for intuition about the right scale,
   but not by itself the paper's clean theorem statement.
3. **Drop the log via Gouëzel's private-communication extension.**
   M–T Remark 2.4: Gouëzel [20] (private comm., not the 2004
   paper) extends Theorem 2.1 to all β ∈ (0, 1) under the
   additional hypothesis μ(φ = n) = O(ℓ(n) · n^{−(β+1)}),
   which at β = 1/2 means μ(φ = n) = O(ℓ(n) n^{−3/2}). This is a
   density-level condition, one derivative stronger than the
   tail condition P(τ > n) ~ n^{−1/2}.

Option 3 is the cleaner statement for the paper, but it adds
an F2-adjacent empirical verification step: we measured the
survival function, not the point-mass density. Whether μ(φ = n)
has the upper bound O(ℓ(n) n^{−3/2}) for BS(1,2) is a separate
check.

**Recommendation for the plan:** Carry the three-tier picture.
The paper can ship with the log if Gouëzel's extension can't be
verified; Theorem 2.3 should be mentioned for fairness, but it
is not the clean full-sequence statement we want to draft
around.

---

## 3. The Markov-chain-to-deterministic translation

All three frameworks are phrased for deterministic dynamical
systems f : X → X with a Perron–Frobenius transfer operator L
on some function space. BS(1,2) is a Markov kernel K on X =
T × ℤ, not a single deterministic map. Something has to give.

### Option A: Bernoulli-shift skew product

Let Ω = {a, a^{−1}, b, b^{−1}}^ℕ with the symmetric product
measure P_sym. Define F : Ω × (T × ℤ) → Ω × (T × ℤ) by

    F(ω, x) = (σω, ω_0 · x),

where σ is the shift and ω_0 is the first-coordinate generator
acting on x. F is deterministic. The natural invariant measure
is P_sym × μ_walker (if the walker has a σ-finite invariant).

The transfer operator L for F averages over the single
pre-image (σ^{−1} on Ω is multi-valued, but with measure-
preserving weights). On the walker-marginal side, L reproduces
the Markov kernel K. On the full skew product, L is genuinely
Perron–Frobenius.

This is the standard trick: random dynamics → deterministic on
a product space. But the skew product only translates the random
dynamics into deterministic language. It does **not** by itself
supply the measure-preserving / conservative / Markov /
Gibbs-Markov hypotheses of the three papers, and it still leans
on having an appropriate invariant measure on the walker side.

### Option B: Stay in Markov-chain language

There is a Meyn–Tweedie-adjacent literature on polynomial
ergodicity for Markov chains (Tuominen–Tweedie 1994, Jarner–
Roberts, and others) that works directly with Markov kernels
and "drift conditions." This is arguably more natural for our
setting but gives different function-space output (typically
f-modulated total variation). Not cited in any of the three
papers we pulled, because they are dynamical-systems papers.

### Recommendation

**Go with Option A for SECOND-PROOF §3.** Build the Bernoulli
skew product, verify M–T's (H1)(H2) on it, then ask whether
Theorem 2.2(a) / 2.3 can be transported back through the
return-to-full-walk and identification steps to the actual
Benford statement. This keeps us in the citation family we've
already scoped.

Option B is a plausible alternative route if Option A turns out
to be technically heavy. Flag as fallback; don't pursue now.

---

## 4. What verifying M–T's (H1)(H2) on BS(1,2) looks like

M–T's abstract hypotheses (§2):

- **(H1):** There exists a Banach space 𝓑 ⊂ L^∞(Y), containing
  constants, with |v|_∞ ≤ ‖v‖, such that R_n : 𝓑 → 𝓑 is
  bounded with ‖R_n‖ ≤ C · μ(φ = n) for all n ≥ 1.
- **(H2)(i):** The eigenvalue 1 is simple and isolated in the
  spectrum of R(1).
- **(H2)(ii):** For z ∈ 𝔻̄ \ {1}, the spectrum of R(z) does not
  contain 1.

M–T §11.1 gives a standard approach to (H2)(i) and (H2)(ii):

- **(H2)(i):** ergodicity of the induced return map F on Y
  (which for our skew product means ergodicity of the first-
  return dynamics on Ω × R).
- **(H2)(ii):** essential spectral radius of R(z) < 1 for every
  z ∈ 𝔻̄, plus aperiodicity — no nontrivial L² solutions to
  v ∘ F = e^{iθφ} · v for θ ∈ (0, 2π).

M–T's two worked example classes (§11):

- **§11.2 Gibbs–Markov first return.** Banach space 𝓑 = Lip(Y)
  with the dynamical metric d_τ(x, y) = τ^{s(x,y)}, where s
  is the separation time under F. Requires countable Markov
  partition of Y with uniformly piecewise Lipschitz
  distortion and the "big images" property (inf_a μ(Fa) > 0).
- **§11.3 AFN maps.** Non-Markovian interval maps with
  indifferent fixed points. Banach space 𝓑 = BV(Y).

### Which template for BS(1,2)?

The Gibbs–Markov template (§11.2) is closer. A candidate induced
return map F on Ω × R would need:

- A countable partition by actual return branches. "Generator
  sequence up to combinatorial equivalence" is too coarse by
  itself unless it really determines a branch of the return map.
- Dynamical distortion controlled by the b-step's ε-coordinate
  behavior (BINADE-WHITECAPS supplies the Fourier side of this).
- Nontrivial image structure under F. But "big images" in M–T is
  a structural lower bound inf_a μ(Fa) > 0 on partition-element
  images; Mess #2's σ̃ concentration does not verify that by
  itself.

Open question: does the induced map on Ω × R actually satisfy
the *uniform* piecewise Lipschitz distortion plus big images
property? Mess #2's finding at E₀ = 10 gives information about
where return mass lands, but it should not be cited as evidence
that the Gibbs–Markov big-images hypothesis already holds. The
uniformity of the distortion on the walker's T-coordinate is
also unchecked.

The upstream risk, separate from uniformity, is the existence of
a countable Markov partition in the first place — (GM-1) in
`paper/MESSES.md` Mess #6. On the natural excursion-type
partition F appears to smear cells across a continuum of return
states rather than mapping onto a union of cells, which would
block §11.2 before uniformity even comes up. Mess #6 carries the
explicit falsification protocol; this plan defers to it for the
first structural test.

This is the main piece of technical work under Option A.
Translation: the §4 walker-level identification problem
(Mess #2) and the F1 framework-regularity problem partially
interlock through the same return-state structure.

### Banach space candidates, ranked

1. **Lip(Y, d_τ) with d_τ = τ^{s(·,·)}**, Gibbs–Markov style.
   Analog of M–T §11.2. First choice.
2. **BV(Y)**, AFN style. Cruder but more forgiving of branch/
   carry discontinuities in the b-step. Fallback.
3. **Fourier-weighted L²** on T-coordinate, mixed with Lip on
   Ω-coordinate. The "natural" choice from the archived
   FIRST-PROOF R3 norm discussion, but not a standard M–T
   framework choice. Would need custom verification; ambitious.

SECOND-PROOF §3 (F3)'s spectral-gap step is the one place
where the norm choice bites. If F3 is easier in Fourier-L² but
F1 is easier in Lip(Y, d_τ), we may end up with a two-norm
argument.

---

## 5. Open questions

Three substantive things the reading didn't settle:

1. **Does BS(1,2) satisfy Gouëzel's density condition
   μ(φ = n) = O(ℓ(n) n^{−3/2})?** One empirical sim would pin this:
   measure the *point mass* of τ_R at each n and check whether an
   ℓ(n) n^{−3/2} upper envelope is plausible. The source only
   needs this upper bound, not a sharp asymptotic slope. If yes,
   we get clean n^{−1/2} at the renewal-operator level. If no,
   we accept the log as the full-sequence bound there and retain
   Theorem 2.3 as partial support at the right scale.
2. **Is the induced return map on the skew product Ω × R
   Gibbs–Markov?** This is the (H1) verification via M–T §11.2.
   Needs (a) a countable partition of Ω × R under which F maps
   cells to unions of cells (Markov property, GM-1), (b)
   piecewise Lipschitz distortion of F on that partition under
   d_τ (GM-3), (c) the big-images condition inf_a μ(Fa) > 0
   (GM-2). The load-bearing worry is (GM-1): on our present
   reading, the natural excursion-type partition is not Markov
   because F smears cells across a continuum of return states.
   This is tracked in `paper/MESSES.md` Mess #6, which carries
   the falsification protocol (small-example calculation on the
   minimal two-step excursion). Not empirical — it's a
   structural check on the kernel. If Mess #6 is falsified on
   the small example and the behavior generalizes, (GM-3) and
   (GM-2) become the next checks. If confirmed, escalate to
   Option B in §3.
3. **What's the aperiodicity input (H2)(ii)?** Essential
   spectral radius < 1 is usually proved by a Lasota–Yorke
   inequality on Lip-norm. No nontrivial cocycle solutions
   v ∘ F = e^{iθφ} v comes from a topological-mixing argument.
   Both are standard once the Gibbs–Markov structure of (H1)
   is established, but neither is free.

---

## 6. Best-guess summary

Committing on priors before the technical work:

- **Primary citation for SECOND-PROOF §3 (F1): Melbourne–Terhesiu
  2012.** It's the only paper of the three whose β-range
  covers our case.
- **Renewal-operator rate delivered: n^{−1/2} log n**
  (Theorem 2.2(a)) in the default reading; **n^{−1/2}** if
  Gouëzel's density condition μ(φ = n) = O(ℓ(n) n^{−3/2})
  holds (extension in M–T's Remark 2.4).
- **Boundary-case fairness:** even without the extra density
  condition, Theorem 2.3 still recovers the n^{−1/2} scale along
  a density-one subsequence and via a liminf statement for
  positive observables.
- **Translation layer: Bernoulli skew product** Ω × (T × ℤ).
  F1 verifies M–T's (H1)(H2) on this deterministic system;
  the original BS(1,2) Markov chain is the walker-marginal
  of the skew product.
- **Banach space: Lip(Y, d_τ)** by analogy with M–T §11.2
  Gibbs–Markov template. BV fallback.
- **Young 1999 and Gouëzel 2004 stay in the reference list**
  for context (Young for tower-construction language, Gouëzel
  for the zero-mean observable improvement and for the β > 1
  picture that explains why the β → 1/2 case needs M–T in the
  first place), but neither is load-bearing.

---

## 7. What folds where when we're done

When F1-HYPO-PLAN dissolves, its content redistributes:

- **SECOND-PROOF §3 (F1)** gets: primary citation pinned to
  M–T 2012; Banach space pinned to Lip(Y, d_τ); rate statement
  with log correction by default, clean n^{−1/2} as an
  extension under Gouëzel's density condition. Add one sentence
  noting M–T Theorem 2.3 as the partial boundary-case result.
- **SECOND-PROOF §3 (F2)** gets a second bullet: besides
  uniform-in-x 1/√n tail, also verify μ(φ = n) =
  O(ℓ(n) n^{−3/2}) at the density level if we want to remove
  the log. Small but logically separate addition.
- **SECOND-PROOF §References** drops the four-way listing.
  M–T 2012 becomes the primary; Young 1999 and Gouëzel 2004
  stay as supporting context.
- **A short note in SECOND-PROOF §References** pointing at the
  resolved F1 so the audit trail survives this doc's removal.

This plan itself gets deleted after SECOND-PROOF is updated.
