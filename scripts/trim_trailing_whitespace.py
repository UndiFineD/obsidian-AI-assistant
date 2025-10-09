#!/usr/bin/env python3
"""
Trim trailing whitespace across the repository.

Rules:
- For non-Markdown text files (.py, .ts, .css, .json, .ps1, .sh, .txt, .yml, .yaml): remove all trailing spaces/tabs.
- For Markdown (.md):
    - If a line ends with 3+ spaces, reduce to exactly 2 spaces (explicit line break).
    - If a line ends with 1-2 spaces, leave as-is.
    - Remove trailing tabs.
- Ensure files end with a single newline when appropriate.

Skips: .git/, node_modules/, models/, vector_db/, cache/, __pycache__/, .venv/, venv/
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Iterable, Tuple

TEXT_EXTS_STRICT = {".py", ".ts", ".css", ".json", ".ps1", ".sh", ".txt", ".yml", ".yaml"}
MD_EXT = ".md"
SKIP_DIRS = {".git", "node_modules", "models", "vector_db", "cache", "__pycache__", ".venv", "venv", "nodejs"}


def should_skip_dir(p: Path) -> bool:
    return any(part in SKIP_DIRS for part in p.parts)


def iter_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*"):
        if p.is_dir():
            if should_skip_dir(p):
                # Skip walking into this directory by clearing its iterator
                # rglob can't be pruned mid-iteration, so just rely on parts check above for files
                pass
            continue
        if should_skip_dir(p):
            continue
        if p.suffix.lower() in TEXT_EXTS_STRICT or p.suffix.lower() == MD_EXT:
            yield p


def process_md_line(line: str) -> str:
    # Normalize line endings handling: remove trailing CR/LF for analysis
    raw = line.rstrip("\n\r")
    # Remove trailing tabs entirely
    while raw.endswith("\t"):
        raw = raw[:-1]
    # Count trailing spaces
    i = len(raw)
    while i > 0 and raw[i-1] == " ":
        i -= 1
    trailing_spaces = len(raw) - i
    content = raw[:i]
    if trailing_spaces >= 3:
        # Reduce to exactly 2 spaces
        raw = content + "  "
    # Re-attach single newline (use platform-independent "\n"; git will normalize by .gitattributes if needed)
    return raw + "\n"


def process_text_line(line: str) -> str:
    # Remove all trailing whitespace for non-MD files
    return line.rstrip() + "\n"


def trim_file(path: Path) -> Tuple[bool, int]:
    changed = False
    changes = 0
    try:
        data = path.read_text(encoding="utf-8")
    except Exception:
        # Skip non-UTF8 or unreadable files
        return False, 0

    lines = data.splitlines(True)  # keepends
    new_lines = []
    if path.suffix.lower() == MD_EXT:
        for ln in lines:
            new_ln = process_md_line(ln)
            if new_ln != ln:
                changed = True
                changes += 1
            new_lines.append(new_ln)
    else:
        for ln in lines:
            new_ln = process_text_line(ln)
            if new_ln != ln:
                changed = True
                changes += 1
            new_lines.append(new_ln)

    # Ensure single trailing newline at EOF
    if new_lines and not new_lines[-1].endswith("\n"):
        new_lines[-1] = new_lines[-1] + "\n"
        changed = True

    if changed:
        path.write_text("".join(new_lines), encoding="utf-8", newline="\n")
    return changed, changes


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    total_files = 0
    total_changed = 0
    total_line_changes = 0

    for f in iter_files(root):
        total_files += 1
        ch, cnt = trim_file(f)
        if ch:
            total_changed += 1
            total_line_changes += cnt
            print(f"Trimmed: {f} ({cnt} lines)")

    print("---")
    print(f"Files scanned: {total_files}")
    print(f"Files changed: {total_changed}")
    print(f"Line edits: {total_line_changes}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
