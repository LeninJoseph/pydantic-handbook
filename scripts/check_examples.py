"""Execute every ```python block in HANDBOOK.md in order, in one shared namespace.

Usage: python scripts/check_examples.py [HANDBOOK.md]
"""
import contextlib
import io
import re
import sys
import textwrap
import traceback

path = sys.argv[1] if len(sys.argv) > 1 else "HANDBOOK.md"
blocks = re.findall(r"```python\n(.*?)```", open(path, encoding="utf-8").read(), re.S)
ns = {"__name__": "__main__"}
failures = 0
for i, block in enumerate(blocks, 1):
    code = textwrap.dedent(block)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(code, f"{path}:block{i}", "exec"), ns)
    except Exception:
        failures += 1
        print(f"FAILED block {i}:\n{code}")
        traceback.print_exc()
print(f"{len(blocks)} blocks checked, {failures} failed")
sys.exit(1 if failures else 0)
