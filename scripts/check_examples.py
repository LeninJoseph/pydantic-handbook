"""Execute every ```python block in the docs.

Blocks in the same page run in order in one shared namespace; each page gets a
fresh namespace. Indented blocks (inside admonitions) are supported.

Usage: python scripts/check_examples.py [docs_dir]
"""
import contextlib
import io
import pathlib
import re
import sys
import textwrap
import traceback

docs = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "docs")
fence = re.compile(r"^([ \t]*)```python\n(.*?)^\1```", re.S | re.M)

total = failures = 0
for page in sorted(docs.rglob("*.md")):
    ns = {"__name__": "__main__"}
    for i, m in enumerate(fence.finditer(page.read_text(encoding="utf-8")), 1):
        total += 1
        code = textwrap.dedent(m.group(2))
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile(code, f"{page}:block{i}", "exec"), ns)
        except Exception:
            failures += 1
            print(f"FAILED {page} block {i}:\n{code}")
            traceback.print_exc()

print(f"{total} blocks checked, {failures} failed")
sys.exit(1 if failures else 0)
