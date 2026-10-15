"""Builds every diagram of the AI Agent Bootcamp as diagrams/<name>.html (an inline SVG <figure>).

Pages include them with

    ```{raw} html
    :file: ../diagrams/<name>.html
    ```

Edit a function in part_*.py, then run:  python course_content/ai-agent-bootcamp/diagrams/make_diagrams.py
"""
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _dg

for mod in ("part_day1a", "part_day1b", "part_day2a", "part_day2b"):
    if (Path(__file__).resolve().parent / f"{mod}.py").exists():
        importlib.import_module(mod)

if __name__ == "__main__":
    for fn in _dg.ALL:
        fn()
    print(f"{len(_dg.ALL)} diagrams written")
