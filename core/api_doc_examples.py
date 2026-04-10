"""
api_doc_examples.py — Verifier for core/API.md.

For each Python code block in core/API.md, classifies it as either a
signature block (skipped) or an example block (run), then rewrites
every `EXPR # LITERAL` line in example blocks into an assertion
before executing. If any assertion fires the block fails.

Run: python3 core/api_doc_examples.py
"""

import ast
import os
import re
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(HERE, 'API.md')

# Match the convention in core/api.py and tests/test_api.py
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'generator'))


# ---------------------------------------------------------------------------
# Block extraction
# ---------------------------------------------------------------------------

FENCE = re.compile(r"```python\n(.*?)\n```", re.DOTALL)


def extract_blocks(text):
    """Yield (block_text, doc_line_no) for every ```python fence."""
    for m in FENCE.finditer(text):
        line_no = text[:m.start()].count('\n') + 2  # first content line
        yield m.group(1), line_no


def is_example(block):
    """A block is an example (runnable) iff it contains an import."""
    return any(
        ln.strip().startswith(('from ', 'import '))
        for ln in block.splitlines()
    )


# ---------------------------------------------------------------------------
# Per-line transformation
# ---------------------------------------------------------------------------

# `<expression>  # <comment>` — non-greedy on the expression so that the
# leftmost `\s+#` boundary wins. Doc convention is two-or-more spaces
# before the `#`, which avoids collisions with `#` inside strings (none
# in the doc anyway).
COMMENT_LINE = re.compile(r'^(\s*)(.+?)\s\s+#\s*(.*)$')

# `print(<expr>)` → unwrap to compare the inner expression rather than
# the always-None return value of print.
PRINT_WRAP = re.compile(r'^print\((.*)\)$')


def extract_literal(comment_text):
    """Try to parse a Python literal from the start of a comment.

    Walks prefixes of the (whitespace-normalized) comment from longest
    to shortest, returning the first one ast.literal_eval accepts. This
    handles trailing annotations like `   — both at index 0` or
    `  ( = 2**32 - 1)` without needing per-separator special cases.
    """
    parts = comment_text.strip().split()
    for n in range(len(parts), 0, -1):
        candidate = ' '.join(parts[:n])
        try:
            return ast.literal_eval(candidate), True
        except (ValueError, SyntaxError):
            continue
    return None, False


def transform_line(line):
    """Rewrite `EXPR # LITERAL` to an assertion. Otherwise return as-is."""
    m = COMMENT_LINE.match(line)
    if not m:
        return line
    indent, expr, comment = m.group(1), m.group(2).rstrip(), m.group(3)
    pm = PRINT_WRAP.match(expr.strip())
    check_expr = pm.group(1) if pm else expr
    value, ok = extract_literal(comment)
    if not ok:
        return line
    msg = line.strip().replace('"', "'")
    return f'{indent}assert ({check_expr}) == {value!r}, "{msg}"'


def transform_block(block):
    return '\n'.join(transform_line(ln) for ln in block.splitlines())


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_block(block, label):
    transformed = transform_block(block)
    ns = {'__name__': '__main__'}
    try:
        exec(compile(transformed, label, 'exec'), ns)
        return True, None
    except AssertionError as e:
        return False, f"assertion: {e}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def main():
    with open(DOC) as f:
        text = f.read()

    examples = []
    skipped = 0
    for block, line_no in extract_blocks(text):
        if is_example(block):
            examples.append((block, line_no))
        else:
            skipped += 1

    print(f"core/API.md: {len(examples)} example blocks, {skipped} signature blocks")
    print()

    failures = 0
    for i, (block, line_no) in enumerate(examples, start=1):
        label = f"example #{i:2d} (API.md line {line_no:3d})"
        ok, err = run_block(block, label)
        if ok:
            print(f"  OK    {label}")
        else:
            print(f"  FAIL  {label}: {err}")
            failures += 1

    print()
    if failures:
        print(f"FAILED: {failures}/{len(examples)} example blocks")
        sys.exit(1)
    else:
        print(f"All {len(examples)} example blocks verified.")


if __name__ == '__main__':
    main()
