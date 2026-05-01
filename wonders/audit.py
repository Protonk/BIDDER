"""
audit.py — accuracy audit for wonders/ entries.

This script is the sensitizer and the audit at once. Run it; read its
output; do the reading it asks for; reply in chat with what you find.

WHAT WONDERS IS

The cabinet at wonders/ is a working catalogue of the things this
project has been struck by. Six categories — marvel, prodigy, sport,
curiosity, monster, wonder — are *modes of being struck*, not
database keys. Each entry leaves room for an aesthetic note that only
a human can write. The README.md and INDEX.md explain the form; read
those before you go further.

WHAT THIS AUDIT IS FOR

The three seed entries (marvel-row-ogf-cliff, prodigy-L1-cliff-n2-h8,
wonder-cost-ladder) were drafted from the algebra/ docs and the
arguments/ files. The drafts are the agent's; the aesthetic notes
will be the human's. Before the human writes those notes, the drafts
need to be *fair to the source material* — accurate citations,
unembellished discovery contexts, descriptions that do not over-claim.
That is what this audit checks.

WHAT THIS AUDIT IS NOT FOR

It is not for re-classifying entries. If you find yourself thinking
"this wonder is too speculative; it should be a curiosity" — stop.
The category was a deliberate choice. Wonders are *supposed* to be
under-articulated and citation-thin; that is the category's whole
point. Resistance to classification is a feature.

It is not for filling in aesthetic notes. Those are the human's;
leave the TODO markers alone.

It is not for adding citations or evidence beyond what the entry
already has. The entry's evidence section is what the human chose
to anchor on. If a claim in the entry is not supported by the cited
evidence, flag it. Don't go find better evidence yourself.

It is not for catching every minor wording quibble. Be a reader, not
a copyeditor.

HOW TO REPLY

Read the three entries against their citations. Check the specific
worries listed below per entry. Reply in chat — not in a file —
with three short blocks (one per entry) covering: claims that hold
up, claims that don't, and anything important the entries miss.
A few hundred words total is plenty.

================================================================
"""

from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def _exists(path):
    return os.path.exists(os.path.join(REPO, path))


def auto_check_citations():
    """Check the cited file paths exist and that file:line citations
    fall within their files. Failures here are bit-rot, not the audit."""
    print('--- auto-checks ---')
    paths = [
        'algebra/ROW-OGF.md',
        'algebra/KERNEL-ZEROS.md',
        'algebra/tests/test_anchors.py',
        'algebra/predict_q.py',
        'algebra/predict_correlation.py',
        'algebra/WITHIN-ROW-PARITY.md',
        'algebra/tests/integration/test_within_row_lattice_summary.txt',
        'arguments/ATTRACTOR-AND-MIRAGE.md',
        'arguments/THE-WHOLE-MACHINE.md',
        'experiments/acm-champernowne/base10/q_distillery/q_lattice_4000_h_regen.py',
        'experiments/acm-champernowne/base10/q_distillery/HIGHER-H-EXPECTATIONS.md',
    ]
    missing = [p for p in paths if not _exists(p)]
    if missing:
        print('  CITED FILE MISSING:')
        for p in missing:
            print(f'    - {p}')
    else:
        print('  all cited files present')

    # Spot-check the ATTRACTOR line range cited in the prodigy entry.
    am = os.path.join(REPO, 'arguments/ATTRACTOR-AND-MIRAGE.md')
    if os.path.exists(am):
        with open(am) as f:
            lines = f.readlines()
        if len(lines) < 615:
            print(f'  ATTRACTOR-AND-MIRAGE.md has {len(lines)} lines; '
                  f'prodigy cites :612-615')
        else:
            print(f'  ATTRACTOR-AND-MIRAGE.md:612-615 in range '
                  f'(file has {len(lines)} lines)')

    # Anchor A10 should appear in test_anchors.py.
    ta = os.path.join(REPO, 'algebra/tests/test_anchors.py')
    if os.path.exists(ta):
        with open(ta) as f:
            content = f.read()
        for tag in ('A10a', 'A10b', 'A10c', 'A10d'):
            if tag not in content:
                print(f'  WARN  {tag} not found in test_anchors.py')
    print()


def per_entry_targets():
    print('--- where I want help, per entry ---\n')

    print('=== marvel-row-ogf-cliff.md ===')
    print("""
This entry is the strongest-anchored of the three. The risks are
subtle, not structural.

  1. Description says "the same multinomial number reappears at the
     same place in two derivations that look different." Is that fair?
     Read algebra/ROW-OGF.md and algebra/KERNEL-ZEROS.md side by side.
     If the row-OGF leading coefficient *is derived from* the
     kernel-zero boundary theorem rather than independently produced,
     the "two derivations that look different" framing is over-stated
     and should be softened. If the two derivations are genuinely
     independent, the framing stands.

  2. The discovery-context paragraph claims:
     "row_polynomial_qe_closed was added before row_polynomial because
      the closed form was easier to write than the general row."
     I drafted this for texture. Run `git log --follow --diff-filter=A
     algebra/predict_q.py` (or grep the commit history for those
     symbols) and either confirm or correct the order. If you can't
     find clear evidence either way, flag the sentence as unsupported
     and recommend it be cut or hedged.

  3. The closed form (1 - (1-x)^e)/e and the row sum 1/e or 0 — verify
     these match the implementation in algebra/predict_q.py:row_sum and
     :row_polynomial_qe_closed. If the implementation says something
     different, the entry is wrong.
""")

    print('=== prodigy-L1-cliff-n2-h8.md ===')
    print("""
This entry has the most synthesised material. The bug-hunt narrative is
a place to look hard.

  1. The numbers "+5.95e-06" (n=2) and "≈ +0.115" (n=13) at h=6.
     The first number is the per-lag L=1 value (per-lag profile for n=2
     is in the integration summary). The second number — +0.115 for
     n=13 — appears in the summary as the *odd-L mean* across
     L = 1, 3, 5, ..., 19, NOT specifically L=1. The entry presents both
     as L=1 values. Is that misleading? Read
     algebra/tests/integration/test_within_row_lattice_summary.txt and
     decide. If the framing is sloppy, recommend an exact correction
     (the L=1 value for n=13 specifically, or a re-framing of "lag
     profile" rather than "L=1 floor").

  2. Discovery-context paragraph claims:
     "The bug-hunt phase took the better part of a working session."
     I made this up. There is no source for the duration. Flag it.

  3. The resolution is described as "traced to the (-1)^j factor in
     the master expansion routing through the off-diagonal class
     pairs." Read algebra/WITHIN-ROW-PARITY.md and the
     class_decomposition function in algebra/predict_correlation.py
     and decide whether that description is fair to what those sources
     actually say. If WITHIN-ROW-PARITY.md attributes the sign flip
     to a different mechanism, the entry should be corrected to match.

  4. The line-number citation arguments/ATTRACTOR-AND-MIRAGE.md:612-615.
     Read those lines. The entry summarises them as "vertical L=1 ≈
     +0.25 at odd h, ≈ -0.14 at even h." Verify the summary is faithful
     to the source.
""")

    print('=== wonder-cost-ladder.md ===')
    print("""
The wonder is the loosest-anchored of the three on purpose. Read
"WHAT THIS AUDIT IS NOT FOR" again before you start. The entry
explicitly says the framing is not yet documented; that is honest.

The audit questions:

  1. The three coordinates (combinatorial, numerical, cognitive). The
     pitch that prompted this entry mentioned only an order-of-magnitude
     observation. The three-coordinate decomposition is the agent's
     synthesis. The entry says "These three coordinates may or may not
     be aspects of one rate. Whether they are is part of what the
     wonder is" — does that wording make the synthesis explicit
     enough? Or does the entry slip into presenting the three-coord
     framing as observed rather than proposed?

  2. The numerical-coordinate evidence cites the q_lattice_4000_h_regen.py
     docstring for "alternating terms reach 10^5, cancel to 10^-1, ULP
     error of 10^-12 on boundary cells." Read that docstring. Are the
     numbers right? Are they being used in a way that is fair to what
     the docstring is actually saying?

  3. The phrase "the 8 × 6 matrices in KERNEL-ZEROS.md exhaust the load
     at h = 5; at h = 8 the same matrix shape carries values from 1/8
     to 151200." Open KERNEL-ZEROS.md and check that 1/8 and 151200
     are real values from the h=8 table.

  4. The cost-ledger §9 of arguments/THE-WHOLE-MACHINE.md is cited
     as "the closest existing framing." Read that section. Is the
     entry's claim — that those are *path coordinates* and the cost
     ladder asks about *height coordinates* — a fair distinction, or
     is it manufacturing a contrast that isn't there?

  Note: do NOT recommend that this entry be moved to curiosity, or
  that it be deleted because the citations are thin. The wonder is
  performing its function as a wonder. The audit asks only whether
  the entry is *fair* to its sources, not whether it is well-anchored.
""")


def closing():
    print('--- how to reply ---\n')
    print("""Reply in chat with three blocks (one per entry). For each, cover:

  - Claims that hold up under the citation check.
  - Claims that don't — be specific about which sentence and what
    the source actually says.
  - Anything important the entry misses or mis-frames.

A few hundred words total. Do not write a report file. Do not edit
the entries themselves; the human decides what to change.

If something feels off but doesn't fit any of those buckets, say so
in plain language at the end. Especially: if you found yourself
wanting to do something this audit told you not to do (re-classify,
add citations, fill an aesthetic note, copyedit), name the
temptation. That is data about the form.
""")


def main():
    print(__doc__)
    auto_check_citations()
    per_entry_targets()
    closing()


if __name__ == '__main__':
    sys.exit(main())
