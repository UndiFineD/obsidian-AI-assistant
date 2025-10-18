#!/usr/bin/env python3
"""
Simple Markdown TODO validator for OpenSpec TODO files.
Checks:
- Top-level heading starts with 'TODO:'
- Contains '## Workflow Progress'
- Contains at least one markdown checkbox line
- No trailing whitespace
- Ends with a trailing newline

Usage:
  python scripts/check_markdown_todos.py [paths...]
If no paths are provided, scans openspec/changes/*/todo.md and openspec/templates/todo.md
"""
from __future__ import annotations
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKBOX_RE = re.compile(r"^- \[\s?[x ]\s?\]", re.IGNORECASE)


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"{path}: cannot read file: {e}"]

    # Heading
    if not re.search(r"^#\s+TODO:\s*", text, re.MULTILINE):
        errors.append(f"{path}: missing top-level 'TODO' heading")

    # Section and checkbox
    if "## Workflow Progress" not in text:
        errors.append(f"{path}: missing '## Workflow Progress' section")
    if not any(CHECKBOX_RE.search(line) for line in text.splitlines()):
        errors.append(f"{path}: no markdown checkboxes found")

    # Trailing whitespace
    for i, line in enumerate(text.splitlines()):
        if re.search(r"\s+$", line):
            errors.append(f"{path}: trailing whitespace on line {i+1}")
            break

    # Must end with newline
    if not text.endswith("\n"):
        errors.append(f"{path}: file must end with a trailing newline (MD047)")

    return errors


def collect_targets(paths: list[str]) -> list[Path]:
    if paths:
        return [Path(p) for p in paths]
    return list(ROOT.glob("openspec/changes/*/todo.md")) + [
        ROOT / "openspec" / "templates" / "todo.md",
    ]


def main(argv: list[str]) -> int:
    targets = collect_targets(argv)
    all_errors: list[str] = []
    for p in targets:
        if not p.exists():
            continue
        all_errors.extend(validate_file(p))

    if all_errors:
        print("\n".join(all_errors))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
